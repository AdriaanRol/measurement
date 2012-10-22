# Base class for all panels
#
# It allows adding an instrument to the panel which is available as _ins
# instrument changes are automatically propagated via _instrument_changed
# timerEvent is automatically called as setup in the panel configuration
#
# Each panel is put into a PanelDialog, which features an extra 'AutoPanel',
# which gives some basic, common functionality (get/set whether the instrument
# is running and recording, save last data), depending on whether the instrument
# supports these features.
#
# Author: Wolfgang Pfaff <w.pfaff@tudelft.nl>

from PyQt4 import QtCore, QtGui, Qt
from PyQt4.Qwt5 import Qwt
from lib.network.object_sharer import helper

class Panel(QtGui.QWidget):
    def __init__(self, parent, *arg, **kw):
        QtGui.QWidget.__init__(self, parent)

        # default params
        self._ins = None
        self._ins_supported = {}

        # process arguments
        # the panel can have a 'main' instrument
        for k in kw:
            if k == 'ins':
                self._ins = helper.find_object('instrument_%s' % kw[k])

        # get supported features
        # but only for available (duh), cyclopean instruments
        if self._ins != None:
            try:
                self._ins_supported = self._ins.supported()
            except AttributeError:
                # not cyclopean
                pass

    # implement in child classes to monitor changes
    def _instrument_changed(self, changes):
        pass

    # timer for regular updates that shall not take place via
    # callbacks initiated at the server side
    def timerEvent(self, event):
        pass

# the dialog class in which a panel sits
class PanelDialog(QtGui.QMainWindow):

    # currently supported auto panel features
    # to use this, set it in your cyclopean instrument
    _auto_panel_supported = [
        'get_running',
        'set_running',
        'get_recording',
        'set_recording',
        'save', ]

    def __init__(self, panel, *arg, **kw):
        QtGui.QDialog.__init__(self)

        self._title = 'Panel'
        self._has_autopanel = True
        
        # this is a reasonable value to not make the UI load the cpu too much
        self._sampling_interval = 250 
        self._auto_panel_activated = []
        self._ins_save_meta = ''

        # process kw-args that can override defaults
        for k in kw:
            if k == 'title': self._title = kw[k]
            if k == 'sampling': self._sampling_interval = int(kw[k])
            if k == 'autopanel': self._has_autopanel = bool(kw[k])

        self._menu_tools = self.menuBar().addMenu("&Tools") 
        self._panel = panel(self, *arg, **kw)
        self.setCentralWidget(self._panel)
        
        # if desired, create the autopanel and a menubar option to restore it
        # in case it gets removed
        if self._has_autopanel:
            self._auto_panel_dock = QtGui.QDockWidget(self)
            self._auto_panel_dock.setWidget(self._auto_panel())
            self._auto_panel_dock.setFeatures(
                QtGui.QDockWidget.DockWidgetMovable |
                QtGui.QDockWidget.DockWidgetClosable)
            self._auto_panel_dock.setWindowTitle('Panel && instrument options')
            self.addDockWidget(Qt.Qt.BottomDockWidgetArea,
                               self._auto_panel_dock)
            # hide by default, takes too much space
            self._auto_panel_dock.setVisible(False)

            menu_tools_autopanel = self._menu_tools.addAction(
                'Panel && instrument opts')
            menu_tools_autopanel.setCheckable(True)
            menu_tools_autopanel.setChecked(False)
            menu_tools_autopanel.toggled.connect(
                self._auto_panel_dock.setVisible)
            self._auto_panel_dock.visibilityChanged.connect(
                menu_tools_autopanel.setChecked)

        self.setWindowTitle(self._title)
        self._sampling_timer = self.startTimer(self._sampling_interval)

    def timerEvent(self, event):
        self._panel.timerEvent(event)

    # creates auto panel for the new panel and enables basic instrument
    # connectivity
    # FIXME: possibility to set the instrument sampling interval
    def _auto_panel(self):
        self.ap = AutoPanel(self)

        # set up the panel part
        self.ap.ui.panel_enabled.setChecked(self._panel.isEnabled())
        self.ap.ui.panel_sampling.setValue(self._sampling_interval)

        # connect signals/slots (panel part)
        self.ap.ui.panel_enabled.toggled.connect(self.panel_enabled)
        self.ap.ui.panel_sampling.editingFinished.connect(\
            self.changed_sampling_interval)

        # depending on the features of the instrument, hide things, otherwise load params
        i = self._panel._ins
        if i == None:
            self.ap.ui.instrumentBox.setHidden(True)
            return self.ap
        else:
            # in any case, connect instrument changes to callback handler
            i.connect('changed', self._instrument_changed_cb)
            i.connect('removed', self._instrument_removed_cb)

            # now see if it's a cyclopean instrument
            try:
                ins_supported = i.supported()
            except AttributeError:
                # not a cyclopean instrument
                self.ap.ui.instrumentBox.setHidden(True)
                return self.ap
        
        self._auto_panel_supported
        for f in self._auto_panel_supported:
            try:
                if ins_supported[f]: self._auto_panel_activated.append(f)
            except KeyError:
                pass

        # go through the UI elements and process them if they're supported        
        if 'get_running' not in self._auto_panel_activated:
            self.ap.ui.instrument_running.setHidden(True)
        else:
            self.ap.ui.instrument_running.setChecked(False)
            i.get_is_running(callback=self.ap.ui.instrument_running.setChecked)
            if 'set_running' not in self._auto_panel_activated:
                self.ap.ui.instrument_running.setEnabled(False)

        if 'get_recording' not in self._auto_panel_activated:
            self.ap.ui.instrument_recording.setHidden(True)
        else:
            self.ap.ui.instrument_recording.setChecked(False)
            i.get_is_recording(callback=self.ap.ui.instrument_recording.setChecked)
            if 'set_recording' not in self._auto_panel_activated:
                self.ap.ui.instrument_recording.setEnabled(False)  

        if 'save' not in self._auto_panel_activated:
            self.ap.ui.instrument_save.setHidden(True)
            self.ap.ui.instrument_meta.setHidden(True)

        self.ap.ui.instrumentBox.setTitle('Instrument (%s)' % i.get_name())

        # connect signals/slots (instrument part): AP to panel/instrument
        self.ap.ui.instrument_running.toggled.connect(\
            self.set_instrument_running)
        self.ap.ui.instrument_recording.toggled.connect(\
            self.set_instrument_recording)
        self.ap.ui.instrument_save.clicked.connect(\
            self.instrument_save)
        self.ap.ui.instrument_meta.textChanged.connect(\
            self.instrument_meta_changed)
        
        return self.ap

    # slots that feed user actions back to the instrument
    # only connected when corresponding features are available
    @QtCore.pyqtSlot(bool)
    def set_instrument_running(self, val):
        self._panel._ins.set_is_running(val,callback=None)

    @QtCore.pyqtSlot(bool)
    def set_instrument_recording(self, val):
        self._panel._ins.set_is_recording(val,callback=None)

    @QtCore.pyqtSlot()
    def instrument_save(self):
        self._panel._ins.save(meta=self._ins_save_meta, callback=None)

    @QtCore.pyqtSlot()
    def instrument_meta_changed(self):
        self._ins_save_meta = self.ap.ui.instrument_meta.toPlainText()
                
    @QtCore.pyqtSlot()
    def changed_sampling_interval(self):
        self.set_sampling_interval(self.ap.ui.panel_sampling.value())

    @QtCore.pyqtSlot(int)
    def set_sampling_interval(self, val):
        self._sampling_interval = int(val)
        self.killTimer(self._sampling_timer)
        self._sampling_timer = self.startTimer(self._sampling_interval)

    @QtCore.pyqtSlot(bool)
    def panel_enabled(self, val):
        self._panel.setEnabled(val)
        if not val: self.killTimer(self._sampling_timer)
        else: self._sampling_timer = self.startTimer(self._sampling_interval)

    # instrument callback handling
    def _instrument_removed_cb(self, *args, **kw):
        # TODO: implement some message
        pass

    def _instrument_changed_cb(self, unused, changes, *args, **kw):
        if changes.has_key('is_running'):
            self.ap.ui.instrument_running.setChecked(bool(changes['is_running']))
        if changes.has_key('is_recording'):
            self.ap.ui.instrument_recording.setChecked(bool(changes['is_recording']))
        
        # notify the panel so the user can do whatever the hell he wants
        self._panel._instrument_changed(changes)
        
        
# a widget class for the auto panel, to be able to distinct
class AutoPanel(QtGui.QWidget):
    def __init__(self, parent):
        QtGui.QWidget.__init__(self, parent)

        from ui_auto_panel import Ui_AutoPanel
        self.ui = Ui_AutoPanel()
        self.ui.setupUi(self)
        

# more common elements
class HugeDisplay(QtGui.QLabel):
    """
    A big text or number display that will appear very prominently
    """
    def __init__(self, parent):
        QtGui.QLabel.__init__(self, parent)

        self.setAlignment(QtCore.Qt.AlignCenter)

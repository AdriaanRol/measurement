# whackyscan_panel.py
#
# auto-created by ../ui2cyclops.py v20110215, Thu Aug 04 23:36:00 2011

from panel import Panel
from ui_whackyscan_panel import Ui_Panel

from PyQt4 import QtCore

class Whackyscan(Panel):
    def __init__(self, parent, *arg, **kw):
        Panel.__init__(self, parent, *arg, **kw)

        # designer ui
        self.ui = Ui_Panel()
        self.ui.setupUi(self)

        self.ui.current_z.setValue(self._ins.get_current_z())
        self.ui.cube_size.setValue(self._ins.get_cube_size())
        self.ui.pxperdim.setValue(self._ins.get_pxperdim())
        self.ui.pxtime.setValue(self._ins.get_pxtime())

        self.ui.current_z.sliderMoved.connect(self._set_current_z)
        self.ui.cube_size.valueChanged.connect(self._set_cube_size)
        self.ui.pxperdim.valueChanged.connect(self._set_pxperdim)
        self.ui.pxtime.valueChanged.connect(self._set_pxtime)

        self.ui.go.pressed.connect(self._go)
        self.ui.stop.pressed.connect(self._stop)

    def _go(self):
        self._ins.go(callback=self._cb) 
        return

    def _cb(self, *arg, **kw):
        print 'callback!', arg, kw
        return

    def _stop(self):
        self._ins.stop()
        return

    def _set_current_z(self, val):
        self._ins.set_current_z(val)
        return

    def _set_cube_size(self, val):
        self._ins.set_cube_size(val)
        return

    def _set_pxperdim(self, val):
        self._ins.set_pxperdim(val)
        return

    def _set_pxtime(self, val):
        self._ins.set_pxtime(val)
        return

    def _instrument_changed(self, changes):
        # Panel._instrument_changed(self, changes)
        #
        print changes

        #if changes.has_key('data_update'):
        #    print changes['data_update']

        if changes.has_key('current_z'):
            self.ui.current_z.setValue(int(changes['current_z']))

        if changes.has_key('cube_size'):
            self.ui.cube_size.setValue(float(changes['cube_size']))

        if changes.has_key('pxperdim'):
            self.ui.pxperdim.setValue(int(changes['pxperdim']))

        if changes.has_key('pxtime'):
            self.ui.pxtime.setValue(int(changes['pxtime']))

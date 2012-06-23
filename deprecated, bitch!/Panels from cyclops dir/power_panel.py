# power_panel.py
#
# auto-created by ../../../tools/ui2cyclops.py v20110215, Wed Mar 02 13:31:16 2011

from panel import Panel
from ui_power_panel import Ui_Panel

from PyQt4 import QtCore
from PyQt4.Qwt5 import Qwt

class Power(Panel):
    def __init__(self, parent, *arg, **kw):
        Panel.__init__(self, parent, *arg, **kw)

        # designer ui
        self.ui = Ui_Panel()
        self.ui.setupUi(self)

        self.ui.correction_factor.setValue(self._ins.get_correction_factor())
        self.ui.correction_factor.valueChanged.connect(self._set_correction_factor)

        # label
        self.ui.power.setText('%1.3f' % 0.)


    def _set_correction_factor(self, val):
        self._ins.set_correction_factor(val)
        return

    def _instrument_changed(self, changes):

        if changes.has_key('correction_factor'):
            self.ui.correction_factor.setValue(float(changes['correction_factor']))

        if changes.has_key('power'):
            self.ui.power.setText('%1.3E' % float(changes['power']))


        

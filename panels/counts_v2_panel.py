# counts_v2_panel.py
#
# auto-created by ../../../cyclops/tools/ui2cyclops.py v20110215, Thu Nov 17 18:47:34 2011

from panel import Panel
from ui_counts_v2_panel import Ui_Panel

from PyQt4 import QtCore

class CountsV2(Panel):
    def __init__(self, parent, *arg, **kw):
        Panel.__init__(self, parent, *arg, **kw)

        # designer ui
        self.ui = Ui_Panel()
        self.ui.setupUi(self)

        self.ui.t_range.setValue(self._ins.get_t_range())
        self.ui.integration_time.setValue(self._ins.get_integration_time())

        self.ui.t_range.valueChanged.connect(self._set_t_range)
        self.ui.integration_time.valueChanged.connect(self._set_integration_time)


    def _set_t_range(self, val):
        self._ins.set_t_range(val)
        return

    def _set_integration_time(self, val):
        self._ins.set_integration_time(val)
        return

    def _instrument_changed(self, changes):

        if changes.has_key('t_range'):
            self.ui.t_range.setValue(int(changes['t_range']))

        if changes.has_key('integration_time'):
            self.ui.integration_time.setValue(int(changes['integration_time']))

        if changes.has_key('countrate'):
            self.ui.plot.add_point(changes['countrate'])

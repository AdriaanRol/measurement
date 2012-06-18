# counter panel for RT2
#
# Author: Wolfgang Pfaff <w.pfaff@tudelft.nl>

from panel import Panel
from ui_counters import Ui_Panel

from PyQt4 import QtCore

class CounterPanel(Panel):
    def __init__(self, parent, *arg, **kw):
        Panel.__init__(self, parent, *arg, **kw)

        # designer ui:
        self.ui = Ui_Panel()
        self.ui.setupUi(self)

        for p in [self.ui.plot1, self.ui.plot2]:
            p.left_axis.title = 'counts [Hz]'
            p.plot.padding = 5
            p.plot.padding_bottom = 30
            p.plot.padding_left = 100
            plot = p.plot.plots['trace'][0]
            plot.padding = 0
            plot.color = 'green'
            plot.marker = 'circle'
            plot.marker_size = 3
            

        for c in [self.ui.counts1, self.ui.counts2]:
            c.setText('0.0')

        # set other defaults
        self.ui.plot1.display_time = 20
        self.ui.plot2.display_time = 20
        self.ui.t_range.setValue(20)
        

    def _instrument_changed(self, changes):

        if changes.has_key('cntr1_countrate'):
            self.ui.counts1.setText('%1.2E' % changes['cntr1_countrate'])
            self.ui.plot1.add_point(changes['cntr1_countrate'])

        if changes.has_key('cntr2_countrate'):
            self.ui.counts2.setText('%1.2E' % changes['cntr2_countrate'])
            self.ui.plot2.add_point(changes['cntr2_countrate'])   


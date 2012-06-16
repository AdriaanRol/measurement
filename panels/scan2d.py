# a 2d scan panel
#
# An example of a 2d scanner that scans an area line by line.
# if the instrument is running, the panel gets notified that new
# data is available and gets it from the instrument and caches is
# locally. since this costs cpu runtime, the 2d scan plot is not
# updated on demand, but slower, triggered by the panel timer.
#
# Author: Wolfgang Pfaff <w.pfaff@tudelft.nl>
from numpy import *
from panel import Panel
from ui_scan2d import Ui_Panel
from PyQt4 import QtCore

class Scan2dPanel(Panel):
    def __init__(self, parent, *arg, **kw):
        Panel.__init__(self, parent, *arg, **kw)

        # designer ui  
        self.ui = Ui_Panel()
        self.ui.setupUi(self)

        # setting up the basic plot properties
        self.ui.plot.left_axis.title = 'y [um]'
        self.ui.plot.bottom_axis.title = 'x [um]'
        self.ui.plot.colorbar_axis.title='counts [Hz]'
        self.ui.plot.enable_colorbar_zooming()
        self.ui.plot.enable_colorbar_panning()

        # enable the cross hair positioning
        self.ui.plot.enable_crosshair('color_plot')
        self.ui.plot.crosshair_moved.connect(self._ins.set_xy)
        
        # read the instrument parameters and set the input
        # fields accordingly
        self.ui.xstart.setValue(self._ins.get_xstart())
        self.ui.xstop.setValue(self._ins.get_xstop())
        self.ui.xsteps.setValue(self._ins.get_xsteps())
        self.ui.ystart.setValue(self._ins.get_ystart())
        self.ui.ystop.setValue(self._ins.get_ystop())
        self.ui.ysteps.setValue(self._ins.get_ysteps())
        self.ui.pxtime.setValue(self._ins.get_pixel_time())
        if self._ins.get_counter() == 1:
            self.ui.counter.setCurrentIndex(0)
        if self._ins.get_counter() == 2:
            self.ui.counter.setCurrentIndex(1)

        # FIXME do that nicer, load data thats already in the instrument
        self._data['countrates'] = zeros((self._ins.get_ysteps(),
            self._ins.get_xsteps()))

        # this flag indicates whether the plot needs to be updated
        self._do_update = False
        self._busy = False

        # some more local variables for position storage
        self.position = {'x_position' : self._ins.get_x_position(),
                         'y_position' : self._ins.get_y_position(), }

    def start_scan(self):
        self._ins.set_xstart(self.ui.xstart.value())
        self._ins.set_xstop(self.ui.xstop.value())
        self._ins.set_xsteps(self.ui.xsteps.value())
        self._ins.set_ystart(self.ui.ystart.value())
        self._ins.set_ystop(self.ui.ystop.value())
        self._ins.set_ysteps(self.ui.ysteps.value())
        self._ins.set_pixel_time(self.ui.pxtime.value())
        #self._ins.set_counter(self.ui.counter.value())
        self._ins.set_counter(self.ui.counter.currentIndex()+1)
        self._ins.set_is_running(True)

    def zoom(self):
        size = self.ui.zoomsize.value()
        x, y = self.position['x_position'], self.position['y_position']
        self.ui.xstart.setValue(x-size/2)
        self.ui.xstop.setValue(x+size/2)
        self.ui.ystart.setValue(y-size/2)
        self.ui.ystop.setValue(y+size/2)
        self.start_scan()

    def stop_scan(self):
        self._ins.set_is_running(False)

    # use the busy flag to make sure we don't reset after data
    # has been acquired
    def _instrument_changed(self, changes):
        Panel._instrument_changed(self, changes)

        if 'data_reset' in changes or 'data_update' in changes:
            self._replot()

        for k in ['x_position', 'y_position']:
            if k in changes:
                self.position[k] = changes[k]

                # don't update the cursor while dragging it, results in
                # weird 'back-action'
                
                # wolfgang, jan 30 2012: remove for now, is annoying 
                #if self.ui.plot.crosshair.drag_state != 'dragging':
                #    self.ui.plot.set_crosshair_position(
                #        (self.position['x_position'], self.position['y_position']))

    def _replot(self):
        self._xvals = self._ins.get_x()
        self._yvals = self._ins.get_y()
        self.ui.plot.set_data(self._xvals, self._yvals, 
            self._data['countrates'])



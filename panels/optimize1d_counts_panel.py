from panel import Panel
from ui_optimize1d_counts_panel import Ui_Panel

from PyQt4 import QtCore, Qt

class Optimize1dCountsPanel(Panel):
    def __init__(self, parent, *arg, **kw):
        Panel.__init__(self, parent, *arg, **kw)

        self._dimension = kw.pop('dimension')
        self._ins_dimension = self._ins.get_dimension()

        # designer ui
        self.ui = Ui_Panel()
        self.ui.setupUi(self)

        self.ui.scan_length.setValue(self._ins.get_scan_length())
        self.ui.pixel_time.setValue(self._ins.get_pixel_time())
        self.ui.nr_of_points.setValue(self._ins.get_nr_of_points())
        self.ui.gaussian_fit.setChecked(self._ins.get_gaussian_fit())
        self.ui.counter.setValue(self._ins.get_counter())

        self.ui.scan_length.valueChanged.connect(self._set_scan_length)
        self.ui.pixel_time.valueChanged.connect(self._set_pixel_time)
        self.ui.nr_of_points.valueChanged.connect(self._set_nr_of_points)
        self.ui.gaussian_fit.toggled.connect(self._set_gaussian_fit)
        self.ui.counter.valueChanged.connect(self._set_counter)

        self.ui.start.pressed.connect(self._start)

        # set up plot
        self.ui.plot.bottom_axis.title = 'x [um]'
        self.ui.plot.left_axis.title = 'counts [Hz]'
        self.ui.plot.plot.padding = 5
        self.ui.plot.plot.padding_bottom = 30
        self.ui.plot.plot.padding_left = 70

    def _start(self):
        self._ins.set_dimension(self._dimension)
        self._ins.set_is_running(True)
        return

    def _set_scan_length(self, val):
        self._ins.set_scan_length(val)
        return

    def _set_pixel_time(self, val):
        self._ins.set_pixel_time(val)
        return

    def _set_nr_of_points(self, val):
        self._ins.set_nr_of_points(val)
        return

    def _set_gaussian_fit(self, val):
        self._ins.set_gaussian_fit(val)
        if not val:
            pass
        return

    def _set_counter(self, val):
        self._ins.set_counter(val)
        return

    def _instrument_changed(self, changes): 
        #print 'instrument changed'
	if 'dimension' in changes:
            self._ins_dimension = changes['dimension']
            #print('trying to print dimensions')
	    #print self._ins_dimension

        if self._ins_dimension == self._dimension:
            Panel._instrument_changed(self, changes)
            
            if changes.has_key('scan_length'):
                self.ui.scan_length.setValue(float(changes['scan_length']))

            if changes.has_key('pixel_time'):
                self.ui.pixel_time.setValue(int(changes['pixel_time']))

            if changes.has_key('nr_of_points'):
                self.ui.nr_of_points.setValue(int(changes['nr_of_points']))

            if changes.has_key('gaussian_fit'):
                self.ui.gaussian_fit.setChecked(bool(changes['gaussian_fit']))

            if changes.has_key('counter'):
                self.ui.counter.setValue(int(changes['counter']))

            if 'data_update' in changes:
                #print 'replot'
		#print 'starting data update'
                
                d = changes['data_update']
		#print d
                if 'points' in d:
		    #print self._data['points']
		    #print 'points are changed'
                    self.ui.plot.set_x(self._data['points'])
                    try:
                        self.ui.plot.plot.delplot('countrates')
                        self.ui.plot.plot.delplot('fit')
                    except:
                        pass
                if 'countrates' in d:
		    #print self._data['countrates']
		    #print 'countrate changed'
                    self.ui.plot.add_y(self._data['countrates'], 'countrates',
                            type='scatter', marker='circle', color='green')
                if 'fit' in d:
		    #print 'fit changed'	
                    self.ui.plot.add_y(self._data['fit'], 'fit', 
                            type='line', line_width=2, color='red')


            if changes.has_key('fit_result'):
                self._got_fit_result(changes['fit_result'])

    def _got_fit_result(self, result):
	#print('Got fit results')    
        labels = [self.ui.mu, self.ui.amplitude, self.ui.sigma,
                  self.ui.offset, ]
        if type(result) == bool:
            for l in labels:
                l.setText('n/a')
        else:
            error = self._ins.get_fit_error()
            for i,l in enumerate(labels):
                l.setText('%.3f +/- %.3f' % (float(result[i]), float(error[i])))


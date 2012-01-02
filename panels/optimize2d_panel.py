# optimize2d_panel.py
#
# auto-created by ui2cyclops.py v20110215, Thu Feb 17 14:26:18 2011

from panel import Panel
from ui_optimize2d_panel import Ui_Panel

from PyQt4 import QtCore, Qt
from PyQt4.Qwt5 import Qwt

class Optimize2d(Panel):
    def __init__(self, parent, *arg, **kw):
        Panel.__init__(self, parent, *arg, **kw)

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
        for p in self.ui.xplot, self.ui.yplot:
            p.bottom_axis.title = 'x [um]'
            p.left_axis.title = 'counts [Hz]'
            p.plot.padding = 5
            p.plot.padding_bottom = 30
            p.plot.padding_left = 70
        self.ui.yplot.bottom_axis.title = 'y [um]'

    def _start(self):
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

        if changes.has_key('xdata'):
            self._got_xdata(changes['xdata'])

        if changes.has_key('ydata'):
            self._got_ydata(changes['ydata'])

        if changes.has_key('x_fit_result'):
            self._got_x_fit_result(changes['x_fit_result'])

        if changes.has_key('y_fit_result'):
            self._got_y_fit_result(changes['y_fit_result'])
    
    def _got_xdata(self, xdata):
        if len(xdata) > 0:
            xpoints = self._ins.get_xpoints()
            self.ui.xplot.set_x(xpoints)
            try:
                self.ui.xplot.plot.delplot('fit')
            except:
                pass
            self.ui.xplot.add_y(xdata, 'linescan',
                                type='scatter',
                                marker = 'circle',
                                color = 'green')
        
    def _got_ydata(self, ydata):
        if len(ydata) > 0:
            ypoints = self._ins.get_ypoints()
            self.ui.yplot.set_x(ypoints)
            try:
                self.ui.yplot.plot.delplot('fit')
            except:
                pass
            self.ui.yplot.add_y(ydata, 'linescan',
                                type='scatter',
                                marker = 'circle',
                                color = 'green')

    def _got_x_fit_result(self, result):
        labels = [self.ui.x_mu, self.ui.x_amplitude, self.ui.x_sigma,
                  self.ui.x_offset, ]
        if type(result) == bool:
            for l in labels:
                l.setText('n/a')
        else:
            error = self._ins.get_x_fit_error()
            for i,l in enumerate(labels):
                l.setText('%.3f +/- %.3f' % (float(result[i]), float(error[i])))

            fit = self._ins.get_xfitdata()
            self.ui.xplot.add_y(fit, 'fit',
                               type='line',
                               line_width=2,
                               color='red')

    def _got_y_fit_result(self, result):
        labels = [self.ui.y_mu, self.ui.y_amplitude, self.ui.y_sigma,
                  self.ui.y_offset, ]
        if type(result) == bool:
            for l in labels:
                l.setText('n/a')
        else:
            error = self._ins.get_y_fit_error()
            for i,l in enumerate(labels):
                l.setText('%.3f +/- %.3f' % (float(result[i]), float(error[i])))

            fit = self._ins.get_yfitdata()
            self.ui.yplot.add_y(fit, 'fit',
                               type='line',
                               line_width=2,
                               color='red')

"""
Example for the measurement2 class.

last change: 2012/12/27, Wolfgang Pfaff <wolfgangpfff at gmail dot com>
"""

import numpy as np
import logging
import qt
import hdf5_data as h5
import measurement.lib.measurement2.measurement as m2

# a dummy measurement
# if it's something general, this definition should be in a library!
class DummyMeasurement(m2.Measurement):
    mprefix = 'DummyMeasurement'

    def measure(self):
        x = np.linspace(0,self.params['xmax'],self.params['xpts'])
        y = np.linspace(0,self.params['ymax'],self.params['ypts'])
        z = np.zeros((self.params['xpts'],self.params['ypts']))

        for i,xval in enumerate(x):
            print 'linesweep %d / %d ...' % (i+1, self.params['xpts'])
            for j,yval in enumerate(y):
                qt.msleep(0.01)
                z[i,j] = xval*yval

        # save the data into the pre-created group.
        # note the passed meta-data (optional).
        # you can have a look at the data with HDFView 
        # (you can get it from hdfgroup.com)
        grp = h5.DataGroup('xy-scan', self.h5data, base=self.h5base)
        grp.add('x', data=x, unit='um', note='somewhat inaccurate')
        grp.add('y', data=y, unit='um')
        grp.add('z', data=z, unit='counts per second', dimensions='1=x, 2=y')

        return

# class DummyMeasurement

# measurement parameters. this can also be done easier in this case, this is
# just to demonstrate a bit the MeasurementParameters class :)
xsettings = {
        'xmax' : 100,
        'xpts' : 11,
        }
ysettings = {
        'ymax' : 100,
        'ypts' : 11,
        }

m = DummyMeasurement('a test')

# since params is not just a dictionary, it's easy to incrementally load
# parameters from multiple dictionaries
# this could be very helpful to load various sets of settings from a global
# configuration manager!
m.params.from_dict(xsettings)
m.params.from_dict(ysettings)

if m.review_params():
    print 'Proceeding with measurement ...'
    m.measure()
    m.save_params()
    m.save_stack()
else:
    print 'Measurement aborted!'

# important! hdf5 data must be closed, otherwise will not be readable!
# (can also be done by hand, of course)
m.finish()

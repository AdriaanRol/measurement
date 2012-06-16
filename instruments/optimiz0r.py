# optimizer for LT2
#
# author: wolfgang <w dot pfaff at tudelft dot nl>

from instrument import Instrument
import types
import qt

class optimiz0r(Instrument):
    
    dimension_sets = {
            'lt2': {
                'x' : {
                    'scan_length' : 1.5,
                    'nr_of_points' : 51,
#                    'pixel_time' : 50,
                    },
                'y' : {
                    'scan_length' : 1.5,
                    'nr_of_points' : 51,
#                    'pixel_time' : 50,
                    },
                'z' : {
                    'scan_length' : 8.,
                    'nr_of_points' : 51,
#                    'pixel_time' : 50,
                    },
                'order' : ['z','y','x'],
                },
            
            'lt1' : {
                'x' : {
                    'scan_length' : 1.,
                    'nr_of_points' : 51,
#                    'pixel_time' : 50,
                    },
                'y' : {
                    'scan_length' : 1.,
                    'nr_of_points' : 51,
#                    'pixel_time' : 50,
                    },
                'z' : {
                    'scan_length' : 2.,
                    'nr_of_points' : 51,
#                    'pixel_time' : 50,
                    },
                'order' : ['z','y','x'],
                },
            }
   
    def __init__(self, name, opt1d_ins=qt.instruments['opt1d_counts'],
            dimension_set='lt2'):
        Instrument.__init__(self, name)

        self.add_function('optimize')
        self.opt1d_ins = opt1d_ins
        self.dimensions = self.dimension_sets[dimension_set]
        
        if dimension_set == 'lt2':
            self.mos = qt.instruments['master_of_space']
        elif dimension_set == 'lt1':
            self.mos = qt.instruments['master_of_space_lt1']


    def optimize(self, cycles=1, cnt=1, int_time=50):
        for c in range(cycles):
            for d in self.dimensions['order']:
                position_before_opt = getattr(self.mos, 'get_'+d)()
                self.opt1d_ins.run(dimension=d,counter = cnt, pixel_time=int_time, **self.dimensions[d])
                position_after_opt = getattr(self.mos, 'get_'+d)()
                print 'Position changed %s um' % (position_after_opt-position_before_opt)
                qt.msleep(1)

    

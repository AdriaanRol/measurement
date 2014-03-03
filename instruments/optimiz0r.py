# optimizer for LT2
#
# author: wolfgang <w dot pfaff at tudelft dot nl>

from instrument import Instrument
import types
import qt
import msvcrt

class optimiz0r(Instrument):
    
    dimension_sets = {
            'lt2': {
                'x' : {
                    'scan_length' : 1.5,
                    'nr_of_points' : 31,
#                    'pixel_time' : 50,
                    },
                'y' : {
                    'scan_length' : 1.0,
                    'nr_of_points' : 31,
#                    'pixel_time' : 50,
                    },
                'z' : {
                    'scan_length' : 4.,
                    'nr_of_points' : 31,
#                    'pixel_time' : 50,
                    },
                'zyx' : ['z','y','x'],
                'xyonly':['y','x'],
                },
            
            'lt1' : {
                'x' : {
                    'scan_length' : 1.,
                    'nr_of_points' : 31,#99,
#                    'pixel_time' : 50,
                    },
                'y' : {
                    'scan_length' : 1.,
                    'nr_of_points' : 31,#99,
#                    'pixel_time' : 50,
                    },
                'z' : {
                    'scan_length' : 2.,
                    'nr_of_points' : 31,#99,
#                    'pixel_time' : 50,
                    },
                'zyx' : ['z','y','x'],
                'xyonly':['y','x'],
                },

            'lt3' : {
                'x' : {
                    'scan_length' : 1.,
                    'nr_of_points' : 31,#99,
#                    'pixel_time' : 50,
                    },
                'y' : {
                    'scan_length' : 1.,
                    'nr_of_points' : 31,#99,
#                    'pixel_time' : 50,
                    },
                'z' : {
                    'scan_length' : 4.,
                    'nr_of_points' : 51,#99,
#                    'pixel_time' : 50,
                    },
                'zyx' : ['z','y','x'],
                'xyonly':['y','x'],
                },

            }
   
    def __init__(self, name, opt1d_ins=qt.instruments['opt1d_counts'], 
            mos_ins=qt.instruments['master_of_space'],
            dimension_set='lt2'):
        Instrument.__init__(self, name)

        self.add_function('optimize')
        self.opt1d_ins = opt1d_ins
        self.dimensions = self.dimension_sets[dimension_set]

        self.mos = mos_ins
       
    def optimize(self, cycles=1, cnt=1, int_time=50, dims=[], order='xyz'):
        ret=True
        for c in range(cycles):
           
            if len(dims) == 0:
                dims = self.dimensions[order]

            for d in dims:
                ret=ret and self.opt1d_ins.run(dimension=d, counter = cnt, 
                        pixel_time=int_time, **self.dimensions[d])
                qt.msleep(1)
            if msvcrt.kbhit():
                kb_char=msvcrt.getch()
                if kb_char == "q" : break
                
        
        return ret
    

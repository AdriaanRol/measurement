import numpy as np
import logging
import qt
import hdf5_data as h5

import measurement.lib.config.adwins as adwins_cfg
import measurement.lib.measurement2.measurement as m2
from measurement.lib.pulsar import pulse, pulselib, element, pulsar

import sequence as tseq
reload(tseq)

class TeleportationMaster(m2.MultipleAdwinsMeasurement):

    mprefix = 'Teleportation'
    # max_successful_attempts = 10000 # after this the adwin stops, in CR debug mode
    # max_red_hist_bins = 100
    # max_yellow_hist_bins = 100
    # adwin_process = 'teleportation'
    # adwin_dict = adwins_cfg.config
    Ey_aom_lt1 = None
    A_aom_lt1 = None
    green_aom_lt1 = None
    yellow_aom_lt1 = None
    # adwin = None

    def __init__(self, name):
        m2.MultipleAdwinsMeasurement.__init__(self, name)

    def load_settings(self):
	    pass
    
    def update_definitions(self):
    	"""
    	After setting the measurement parameters, execute this function to
    	update pulses, etc.
    	"""
    	tseq.pulse_defs(self)

    def autoconfig(self):
        """
        sets/computes parameters (can be from other, user-set params)
        as required by the specific type of measurement.
        E.g., compute AOM voltages from desired laser power, or get
        the correct AOM DAC channel from the specified AOM instrument.
        """
        self.params['Ey_laser_DAC_channel_lt1'] = self.adwins['adwin_lt1'].get_dac_channels()\
                [self.Ey_aom_lt1.get_pri_channel()]
        self.params['FT_laser_DAC_channel_lt1'] = self.adwins['adwin_lt1'].get_dac_channels()\
                [self.FT_aom_lt1.get_pri_channel()]
        self.params['yellow_laser_DAC_channel_lt1'] = self.adwins['adwin_lt1'].get_dac_channels()\
                [self.yellow_aom_lt1.get_pri_channel()]
        self.params['green_laser_DAC_channel_lt1'] = self.adwins['adwin_lt1'].get_dac_channels()\
                [self.green_aom_lt1.get_pri_channel()]         
        # self.params['gate_DAC_channel'] = self.adwin.get_dac_channels()\
        #        ['gate']

    def setup(self):
        """
        sets up the hardware such that the msmt can be run
        (i.e., turn off the lasers, prepare MW src, etc)
        """        
        self.yellow_aom_lt1.set_power(0.)
        self.green_aom_lt1.set_power(0.)
        self.E_aom_lt1.set_power(0.)
        self.A_aom_lt1.set_power(0.)
        self.yellow_aom_lt1.set_cur_controller('ADWIN')
        self.green_aom_lt1.set_cur_controller('ADWIN')
        self.E_aom_lt1.set_cur_controller('ADWIN')
        self.A_aom_lt1.set_cur_controller('ADWIN')
        self.yellow_aom_lt1.set_power(0.)
        self.green_aom_lt1.set_power(0.)
        self.E_aom_lt1.set_power(0.)
        self.A_aom_lt1.set_power(0.)
        
# configure the hardware
TeleportationMaster.adwins = {
    'adwin_lt1' : {
        'ins' : qt.instruments['adwin_lt1'],
        'process' : 'teleportation',
    },

    'adwin_lt2' : {
        'ins' : qt.instruments['adwin_lt2'],
        'process' : 'teleportation'
    }
}

        
# set up the LT1 measurement part        
m_ = TeleportationMaster('debugging')
m.load_settings()

# here we set stuff 
# ...

m.update_definitions()
m.setup()







import numpy as np
import logging
import qt
import hdf5_data as h5

import measurement.lib.config.adwins as adwins_cfg
import measurement.lib.measurement2.measurement as m2
from measurement.lib.pulsar import pulse, pulselib, element, pulsar

import sequence as tseq
reload(tseq)

class Teleportation(m2.AdwinControlledMeasurement):

    mprefix = 'teleportation'
    max_successful_attempts = 10000 # after this the adwin stops, in CR debug mode
    max_red_hist_bins = 100
    max_yellow_hist_bins = 100
    adwin_process = 'teleportation'
    adwin_dict = adwins_cfg.config
    E_aom = None
    A_aom = None
    green_aom = None
    yellow_aom = None
    adwin = None
    mode = None

    modes = {
    	'debug_double_CR' : 1,
    }

    def __init__(self, name):
        m2.AdwinControlledMeasurement.__init__(self, name)

    def load_settings(self):
	    self.params.from_dict(qt.cfgman.get('samples/sil2'))
	    self.params.from_dict(qt.cfgman.get('protocols/AdwinSSRO'))
	    self.params.from_dict(qt.cfgman.get('protocols/sil2-default/AdwinSSRO'))
	    self.params.from_dict(qt.cfgman.get('protocols/sil2-default/AdwinSSRO-integrated'))

	    self.params.from_dict(qt.cfgman.get('protocols/AdwinSSRO+MBI'))
	    self.params.from_dict(qt.cfgman.get('protocols/sil2-default/AdwinSSRO+MBI'))
	    self.params.from_dict(qt.cfgman.get('protocols/sil2-default/pulses'))
	    self.params.from_dict(qt.cfgman.get('protocols/sil2-default/BSM'))
	    
	    if self.params['use_yellow_repump']:
	        ssro.AdwinSSRO.repump_aom = qt.instruments['YellowAOM']
	        self.params['repump_duration']=self.params['yellow_repump_duration']
	        self.params['repump_amplitude']=self.params['yellow_repump_amplitude']
	        self.params['CR_repump']=self.params['yellow_CR_repump']
	        self.params['repump_after_repetitions']=self.params['yellow_repump_after_repetitions']
	    else:
	        ssro.AdwinSSRO.repump_aom = qt.instruments['GreenAOM']
	        self.params['repump_duration']=self.params['green_repump_duration']
	        self.params['repump_amplitude']=self.params['green_repump_amplitude']
	        self.params['CR_repump']=self.params['green_CR_repump']
	        self.params['repump_after_repetitions']=self.params['green_repump_after_repetitions']
    
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
        self.params['Ex_laser_DAC_channel'] = self.adwin.get_dac_channels()\
                [self.E_aom.get_pri_channel()]
        self.params['A_laser_DAC_channel'] = self.adwin.get_dac_channels()\
                [self.A_aom.get_pri_channel()]
        self.params['yellow_laser_DAC_channel'] = self.adwin.get_dac_channels()\
                [self.yellow_aom.get_pri_channel()]
        self.params['green_laser_DAC_channel'] = self.adwin.get_dac_channels()\
                [self.green_aom.get_pri_channel()]         
        # self.params['gate_DAC_channel'] = self.adwin.get_dac_channels()\
        #        ['gate']

    def setup(self):
        """
        sets up the hardware such that the msmt can be run
        (i.e., turn off the lasers, prepare MW src, etc)
        """
        
        self.yellow_aom.set_power(0.)
        self.green_aom.set_power(0.)
        self.E_aom.set_power(0.)
        self.A_aom.set_power(0.)
        self.yellow_aom.set_cur_controller('ADWIN')
        self.green_aom.set_cur_controller('ADWIN')
        self.E_aom.set_cur_controller('ADWIN')
        self.A_aom.set_cur_controller('ADWIN')
        self.yellow_aom.set_power(0.)
        self.green_aom.set_power(0.)
        self.E_aom.set_power(0.)
        self.A_aom.set_power(0.)



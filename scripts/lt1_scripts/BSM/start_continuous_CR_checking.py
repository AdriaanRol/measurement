"""
LT1 script for adwin ssro.
"""
import numpy as np
import qt
import measurement.lib.config.adwins as adwins_cfg
import measurement.lib.measurement2.measurement as m2

# import the msmt class
from measurement.lib.measurement2.adwin_ssro import ssro

class CRChecking(ssro.AdwinSSRO):

    adwin_process = 'continuous_CR'

    def __init__(self):
        ssro.AdwinSSRO.__init__(self, 'CRChecking', save=False)

    def run(self, autoconfig=True, setup=True):
        if autoconfig:
            self.autoconfig()
            
        if setup:
            self.setup()
            
        for key,_val in self.adwin_dict[self.adwin_processes_key]\
                [self.adwin_process]['params_long']:
            try:
                self.adwin_process_params[key] = self.params[key]
            except:
                logging.error("Cannot set adwin process variable '%s'" \
                        % key)
                return False

        self.adwin_process_params['Ex_CR_voltage'] = \
                self.E_aom.power_to_voltage(
                        self.params['Ex_CR_amplitude'])
        
        self.adwin_process_params['A_CR_voltage'] = \
                self.A_aom.power_to_voltage(
                        self.params['A_CR_amplitude'])

        self.adwin_process_params['Ex_SP_voltage'] = \
                self.E_aom.power_to_voltage(
                        self.params['Ex_SP_amplitude'])

        self.adwin_process_params['A_SP_voltage'] = \
                self.A_aom.power_to_voltage(
                        self.params['A_SP_amplitude'])

        self.adwin_process_params['Ex_RO_voltage'] = \
                self.E_aom.power_to_voltage(
                        self.params['Ex_RO_amplitude'])

        self.adwin_process_params['A_RO_voltage'] = \
                self.A_aom.power_to_voltage(
                        self.params['A_RO_amplitude'])
                       
        self.adwin_process_params['repump_voltage'] = \
                self.repump_aom.power_to_voltage(
                        self.params['repump_amplitude'])
                
        self.adwin_process_params['repump_off_voltage'] = \
                self.params['repump_off_voltage']
        self.adwin_process_params['A_off_voltage'] = \
                self.params['A_off_voltage']
        self.adwin_process_params['Ex_off_voltage'] = \
                self.params['Ex_off_voltage']
        
        self.start_adwin_process(stop_processes=['counter'])


def start_CR_checking(yellow=False):
    m = CRChecking()
   
    m.params.from_dict(qt.cfgman['protocols']['AdwinSSRO'])
    m.params.from_dict(qt.cfgman['protocols']['sil2-default']['AdwinSSRO'])    
    
    if yellow:
        ssro.AdwinSSRO.repump_aom = qt.instruments['YellowAOM']
        m.params['repump_duration']=m.params['yellow_repump_duration']
        m.params['repump_amplitude']=m.params['yellow_repump_amplitude']
        m.params['CR_repump']=1
        m.params['repump_after_repetitions']=10
    else:
        ssro.AdwinSSRO.repump_aom = qt.instruments['GreenAOM']
        m.params['repump_duration']=m.params['green_repump_duration']
        m.params['repump_amplitude']=m.params['green_repump_amplitude']
    
    m.run()

if __name__ == '__main__':
    start_CR_checking(yellow=False)
 
    



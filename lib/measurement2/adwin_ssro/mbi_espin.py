# classes for e-spin manipulation after MBI
#
# author: Wolfgang Pfaff

import numpy as np
import qt
import hdf5_data as h5

from measurement.lib.measurement2.adwin_ssro import mbi

class ElectronRabi(mbi.MBIMeasurement):
    mprefix = 'MBIElectronRabi'
    
    def sequence(self):
        for i in np.arange(self.params['pts']):
            
            self._MBI_seq_element(el_name='MBI_pulse'+str(i),
                    jump_target='spin_control'+str(i),
                    goto_target='MBI_pulse'+str(i)+'-0')

            if i == self.params['pts'] - 1:
                self.seq.add_element(name = 'spin_control'+str(i), 
                    trigger_wait = True, goto_target = 'MBI_pulse0-0')
            else:
                self.seq.add_element(name = 'spin_control'+str(i), 
                    trigger_wait = True)

            self.seq.add_pulse('wait_before_RO', channel=self.chan_RF,
                    element = 'spin_control'+str(i),
                    start = 0, # start_reference=last, link_start_to='end', 
                    duration = 50,
                    amplitude = 0)
            last = 'wait_before_RO'

            for j in range(self.params['MW_pulse_multiplicity']):
                self.seq.add_IQmod_pulse(name = 'RO_pulse-'+str(j),
                        channel = (self.chan_mwI,self.chan_mwQ),
                        element = 'spin_control'+str(i),
                        start = self.params['MW_pulse_delay'], 
                        duration = int(self.params['AWG_RO_MW_pulse_durations'][i]),
                        amplitude = self.params['AWG_RO_MW_pulse_amps'][i],
                        frequency = self.params['AWG_RO_MW_pulse_ssbmod_frqs'][i],
                        start_reference = last,
                        link_start_to = 'end')
                last = 'RO_pulse-'+str(j)+'-I'


            self.seq.clone_channel(self.chan_mw_pm, self.chan_mwI, 'spin_control'+str(i),
                    start = -self.params['MW_pulse_mod_risetime'],
                    duration = 2 * self.params['MW_pulse_mod_risetime'], 
                    link_start_to = 'start', 
                    link_duration_to = 'duration',
                    amplitude = 2.0)

            # make sure PM is low at the beginning
            self.seq.add_pulse('delay_start', self.chan_mw_pm, 'spin_control'+str(i),
                    start=-5, duration=5, amplitude=0,
                    start_reference='RO_pulse-0-I',
                    link_start_to='start')

            self.seq.add_pulse(name='seq_done',
                    channel = self.chan_adwin_sync,
                    element = 'spin_control'+str(i),
                    duration = 10000, #AWG_to_adwin_ttl_trigger_duration, 
                    amplitude = 2,
                    start = 0,
                    start_reference='RO_pulse-'+str(j)+'-I',
                    link_start_to='end')
            
### class ElectronRabi
        
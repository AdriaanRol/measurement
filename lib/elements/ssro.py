from measurement.measurement import MeasurementElement
import qt


class SequentialReadout(MeasurementElement):

    def __init__(self, parent, sequence):
        MeasurementElement.__init__(self, parent)

        self.sequence = sequence
        self.sequence_element_name = 'probe'
        self.new_sequence_element = True

        self.chan_iq = ('MW_Imod', 'MW_Qmod')
        self.
        
        self.par = {}
        self.par['probe_total_repetitions'] = 1
        self.par['probe_min1_repetitions'] = 1
        self.par['probe_plus1_repetitions'] = 1
        self.par['probe_min1_line_repetitions'] = 2
        self.par['probe_plus1_line_repetitions'] = 2
        self.par['probe_line_order'] = range(
                len(qt.cfgman.current_sample['basis_min1_esr_frqs']))


    def make(self):
        
        if self.new_sequence_element:
            self.sequence.add_element(self.sequence_element_name)

        last = ''
        i = -1
        
        for j in range(self.par['probe_total_repetitions']):        
            
            for ii in self.par['probe_min1_repetitions']:
                i += 1                
                
                for fidx in self.par['probe_line_order']:                 
                    
                    for k in range(self.par['probe_plus1_line_repetitions']):
                    
                        self.sequence.add_IQmod_pulse(
                                'probemw-line_%d-rep_%d-%d'%(fidx,i,k), 
                                channel = self.chan_iq, 
                                element = self.sequence_element_name, 
                                start = 0, 
                                start_reference = last,
                                link_start_to = 'end',
                                frequency = self.lst_probemw_frequency[fidx],
                                duration = int(self.par_probemw_duration),
                                amplitude = self.lst_probemw_amplitude[fidx],
                                envelope = None)
                        last = 'probemw-line_%d-rep_%d-%d-I'%(fidx,i,k)

                        last = ssroself.sequence.readout(self.sequence. 'probe', suffix='-line_%d-rep_%d-%d'%(fidx,i,k),
                                ex_amplitude = ins_exaom.power_to_voltage(
                                    self.par_probe_Ex_power),
                                duration = int(self.par_probe_duration),
                                start_reference=last, start = 500)
                    
            ms_min1_len = len(self.lst_probemw_frequency_order)
            for ii in range(self.par_probe_plus1_repetitions):
                i += 1

                for fidx in self.lst_probemw_frequency_order:
             
                    for k in range(self.par_probe_plus1_line_repetitions):
                    
                        self.sequence.add_IQmod_pulse('probemw-line_%d-rep_%d-%d'%(fidx,i,k), 
                                channel=(chan_mwI,chan_mwQ), 
                                element='probe', start=0, start_reference=last,
                                link_start_to = 'end',
                                frequency = self.lst_probemw_frequency[fidx + ms_min1_len],
                                duration = int(self.par_probemw_duration),
                                amplitude = self.lst_probemw_amplitude[fidx + ms_min1_len],
                                envelope=None)
                        last = 'probemw-line_%d-rep_%d-%d-I'%(fidx,i,k)

                        last = ssroself.sequence.readout(self.sequence. 'probe', suffix='-line_%d-rep_%d-%d'%(fidx,i,k),
                                ex_amplitude = ins_exaom.power_to_voltage(
                                    self.par_probe_Ex_power),
                                duration = int(self.par_probe_duration),
                                start_reference=last, start = 500)
                    
        self.sequence.clone_channel(chan_mwpulsemod, chan_mwI, 'probe', 
                start = -hardware['MW_pulse_mod_risetime'], 
                duration = int(2 * hardware['MW_pulse_mod_risetime']),
                link_start_to = 'start', link_duration_to = 'duration', 
                amplitude = 2.0)

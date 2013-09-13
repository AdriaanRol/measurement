
from measurement.lib.pulsar import pulse, pulselib, element, pulsar

import measurement.lib.measurement2.measurement as m2
from measurement.lib.measurement2.adwin_ssro.pulsar import PulsarMeasurement





class AWGSPCalibration(PulsarMeasurement):
    mprefix = 'AWGSPCalibration'
           
    def autoconfig(self):
        PulsarMeasurement.autoconfig(self)
        self.params['sequence_wait_time'] = \
            int(np.ceil(np.max(self.params['AWG_SP_duration']*1e6))+10)


        self.params['AWG_SP_voltage']=np.array([self.A_aom.power_to_voltage(p, controller='sec') for p in self.params['AWG_SP_power']])

        print 'SEQ_WAIT_TIME', self.params['sequence_wait_time']


    def generate_sequence(self, upload=True):

        # define the necessary pulse

       
        TT = pulse.SquarePulse(channel='HH_sync', length = 1000e-9, amplitude = 0)
        SP = pulse.SquarePulse(channel=self.params['sp_channel'], 
                length = self.params['AWG_SP_duration'][0], 
                amplitude = self.params['AWG_SP_voltage'][0])

        #print self.params['AWG_SP_voltage']
        # make the elements - one for each ssb frequency
        elements = []
        for i in range(self.params['pts']):
            e = element.Element('AWG_SP_sweep-%d' % i, pulsar=self.pulsar)
            e.add(TT, name='wait')
            e.append(pulse.cp(SP(length=self.params['AWG_SP_duration'][i],amplitude = self.params['AWG_SP_voltage'][i])))
            elements.append(e)



        # create a sequence from the pulses
        seq = pulsar.Sequence('SSRO sequence')
        for e in elements:
            seq.append(name=e.name, wfname=e.name, trigger_wait=True)

        # upload the waveforms to the AWG
        if upload:
            self.pulsar.upload(*elements)

        # program the AWG
        self.pulsar.program_sequence(seq)

        # some debugging:
        # elements[-1].print_overview()


def awgspcalibration(name):

    m=AWGSPCalibration(name)


    m.params.from_dict(qt.cfgman['protocols']['AdwinSSRO'])
    m.params.from_dict(qt.cfgman['protocols']['sil9-default']['AdwinSSRO'])    
    
    yellow=False
    if yellow:
        ssro.AdwinSSRO.repump_aom = qt.instruments['YellowAOM_lt1']
        m.params['repump_duration'] = m.params['yellow_repump_duration']
        m.params['repump_amplitude'] = m.params['yellow_repump_amplitude']
    else:
        ssro.AdwinSSRO.repump_aom = qt.instruments['GreenAOM']
        m.params['repump_duration'] = m.params['green_repump_duration']
        m.params['repump_amplitude'] = m.params['green_repump_amplitude']

    m.pulsar=qt.pulsar #or pulsar_remote
    m.params['sp_channel']='AOM_Newfocus' #or VelocityAOM
    m.params['send_AWG_start']=1

    m.params['measurement_time']=2000 #seconds, max time after the HH times out.
    m.params['pts']=10
    m.params['repetitions']=1000
    


    m.params['AWG_SP_power'] = np.linspace(0,30e-9,m.params['pts'])
    m.params['AWG_SP_duration'] = 3e-6*np.ones(m.params['pts'])#np.linspace(0,60e-6,m.params['pts'])
    m.params['sweep_pts'] = m.params['AWG_SP_power']/1e-6
    m.params['sweep_name']='SP_power [uW]'
    # parameters
    m.params['CR_preselect'] = 500
    m.params['CR_probe'] = 2

    m.params['A_CR_amplitude'] = 10e-9
    m.params['Ex_CR_amplitude'] = 10e-9
    m.params['CR_duration'] = 100
    m.params['SP_duration'] = 250
    m.params['A_SP_amplitude'] = 0e-9
    m.params['Ex_SP_amplitude'] = 5e-9
    
    
    # calibration ms0 only
    
    m.params['Ex_RO_amplitude'] = 3e-9 #10e-9
    m.params['SSRO_duration']=50

    m.autoconfig()
    m.generate_sequence(upload=True)
    m.run(autoconfig=False,setup=True)
    m.save()
    m.finish(save_ins_settings=False)


if __name__ == '__main__':
    awgspcalibration('lt2_sil9')
    #qt.instruments['AWG_lt1'].set_ch2_offset(0.)

 
    
import qt
import numpy as np
from measurement.lib.measurement2.adwin_ssro import pulsar as pulsar_msmt
from measurement.lib.pulsar import pulse, pulselib, element, pulsar

import mbi_funcs as funcs
reload(funcs)


class ShapedRabiMsmt(pulsar_msmt.MBI):
    mprefix = 'MBI_ShapedRabi'

    def generate_sequence(self, upload=True):
        # MBI element
        mbi_elt = self._MBI_element()

        # electron manipulation pulses
        self.T = pulse.SquarePulse(channel='MW_pulsemod',
            length = 100e-9, amplitude = 0)

        self.g_pulse = self.PulseClass('gaussian IQ pulse',
            I_channel = 'MW_Imod',
            Q_channel = 'MW_Qmod',
            PM_channel = 'MW_pulsemod',
            PM_risetime = self.params['MW_pulse_mod_risetime'],
            frequency = self.params['pulse_mod_frqs'][0],
            amplitude = self.params['pulse_amps'][0],
            length = self.params['pulse_durations'][0])
    
        elts = []
        for i in range(self.params['pts']):
            e = element.Element('ERabi_pt-{}'.format(i), pulsar=qt.pulsar)
            e.append(self.T)            
            for j in range(self.params['MW_pulse_multiplicities'][i]):
                e.append(
                    pulse.cp(self.g_pulse,
                        frequency = self.params['pulse_mod_frqs'][i],
                        amplitude = self.params['pulse_amps'][i],
                        length = self.params['pulse_durations'][i]))
                e.append(
                    pulse.cp(self.T, length=self.params['MW_pulse_delays'][i]))
            elts.append(e)

        sync_elt = element.Element('adwin_sync', pulsar=qt.pulsar)
        adwin_sync = pulse.SquarePulse(channel='adwin_sync',
            length = 10e-6, amplitude = 2)
        sync_elt.append(adwin_sync)

        seq = pulsar.Sequence('CNOT sequence')
        for i in range(self.params['pts']):

            seq.append(name = 'MBI-%d' % i, 
                wfname = mbi_elt.name, 
                trigger_wait = True, 
                goto_target = 'MBI-%d' % i, 
                jump_target = 'pulse-{}'.format(i))

            seq.append(name = 'pulse-{}'.format(i), 
                       wfname = elts[i].name,
                       trigger_wait=True)

            seq.append(name = 'sync-{}'.format(i),
                wfname = sync_elt.name)

        # program AWG
        if upload:
            qt.pulsar.upload(mbi_elt, sync_elt, *elts)
        qt.pulsar.program_sequence(seq)



def run_gaussian_electron_rabi(name):
    m = ShapedRabiMsmt(name) # BSM.ElectronRabiMsmt(name)

    sil_name='sil9'
    funcs.prepare(m, sil_name, yellow=False)
    
    pts = 11
    m.params['pts'] = pts
    m.params['reps_per_ROsequence'] = 1000
    m.params['MW_pulse_multiplicities'] = np.linspace(0,10,pts).astype(int) * 1
    m.params['MW_pulse_delays'] = np.ones(pts) * 100e-9


    #initialisation:cfg.set(branch+        
    m.params['AWG_MBI_MW_pulse_mod_frq']= m.params['mIp1_mod_frq']
    m.params['AWG_MBI_MW_pulse_ssbmod_frq']=m.params['AWG_MBI_MW_pulse_mod_frq']

    m.params['pulse_mod_frqs'] = np.ones(pts) * m.params['mIm1_mod_frq']
    m.params['pulse_amps'] = np.ones(pts)*0.07#np.linspace(0,0.12,pts)
    m.params['pulse_durations']= np.ones(pts) * 395e-9

    # for the autoanalysis
    m.params['sweep_name'] = 'MW_pulse_multiplicities'
    m.params['sweep_pts'] = m.params['MW_pulse_multiplicities'] 

    m.PulseClass = pulselib.MW_IQmod_pulse
    #pulselib.MW_IQmod_pulse
    #pulselib.GaussianPulse_Envelope_IQ
    #pulselib.HermitePulse_Envelope_IQ
    #pulselib.ReburpPulse_Envelope_IQ



    funcs.finish(m, upload=True, debug=False)

if __name__ == '__main__':
    run_gaussian_electron_rabi('sil9_gauss')



#cfg.set(branch+        'pi2pi_mIm1_duration',         tof + 395e-9)
#cfg.set(branch+        'pi2pi_mIm1_amp',             0.164)

#cfg.set(branch+'mIm1_mod_frq',finit)
#cfg.set(branch+'mI0_mod_frq',f0)
#cfg.set(branch+'mIp1_mod_frq',fmIp1)

#
#
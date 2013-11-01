"""
LT2 script for decoupling
"""
import numpy as np
import qt

import measurement.lib.measurement2.measurement as m2
from measurement.lib.measurement2.adwin_ssro import pulsar as pulsar_msmt
from measurement.lib.pulsar import pulse, pulselib, element, pulsar
reload(pulselib)

from measurement.scripts.teleportation import parameters as tparams
reload(tparams)
from measurement.scripts.teleportation import sequence as tseq
reload(tseq)


name = 'sil10'
OPT_PI_PULSES = 2
LDE_DO_MW = True

def prepare(m):
    m.params_lt1 = m2.MeasurementParameters('LT1Parameters')
    m.params_lt2 = m2.MeasurementParameters('LT2Parameters')

    m.load_settings()
    m.update_definitions()
    m.repump_aom = qt.instruments['GreenAOM']

def finish(m, upload=True, debug=False, **kw):
    for key in m.params_lt2.to_dict():
        m.params[key] = m.params_lt2[key]

    m.autoconfig()
    m.generate_sequence(upload=upload, **kw)

    if not debug:
        m.run()
        m.save()
        m.finish()

### msmt class
class DynamicalDecoupling(pulsar_msmt.PulsarMeasurement):
    mprefix = 'DynamicalDecoupling'

    def load_settings(self):
        for k in tparams.params.parameters:
            self.params[k] = tparams.params[k]

        for k in tparams.params_lt2.parameters:
            self.params_lt2[k] = tparams.params_lt2[k]

        self.params['opt_pi_pulses'] = OPT_PI_PULSES
        self.params_lt2['MW_during_LDE'] = 1 if LDE_DO_MW else 0

    def update_definitions(self):
        tseq.pulse_defs_lt2(self)
        self.adwin_lt2_trigger_element = tseq._lt2_adwin_lt2_trigger_elt(self)

    def LDE_element(self, **kw):
        return tseq._lt2_LDE_element(self, **kw)
        
    def first_pi2(self, **kw):
        # kws are init_ms1, CORPSE_pi_shelv_amp, CORPSE_pi2_amp
        return tseq._lt2_first_pi2(self, **kw)

    def second_pi2(self, name, time_offset, **kw):
        # kws are extra_t_before_pi2, CORPSE_pi2_amp
        return tseq._lt2_final_pi2(self, name, time_offset, **kw)

    def dynamical_decoupling(self, seq, time_offset, **kw):
        # kws are free evolution time, extra_t_between_pulses
        # also possible to sweep: CORPSE pi amp. 
        return tseq._lt2_dynamical_decoupling(self, seq, time_offset, **kw)

    def generate_sequence(self, upload = True):
        if upload:
            qt.pulsar.upload(*self.elements)

        qt.pulsar.program_sequence(self.seq)

    def dd_sweep_free_ev_time_msmt(self):
        self.seq = pulsar.Sequence('{}_{}_sequence'.format(self.mprefix, self.name))

        self.elements = []

        first_pi2_elt = self.first_pi2()
        self.elements.append(first_pi2_elt)
        
        for i in range(self.params['pts']):
            self.seq.append(name = 'first_pi2-{}'.format(i), 
                wfname = first_pi2_elt.name, 
                trigger_wait = True)

            seq, total_elt_time, elts = self.dynamical_decoupling(self.seq, 
                time_offset = first_pi2_elt.length(),
                begin_offset_time = 0.,
                free_evolution_time = self.params_lt2['free_evolution_times'][i],
                use_delay_reps = self.params['dd_use_delay_reps'],
                name = i)

            second_pi2_elt = self.second_pi2(name = i, 
                time_offset = first_pi2_elt.length() + total_elt_time)

            self.seq.append(name = 'second_pi2-{}'.format(i), 
                wfname = second_pi2_elt.name)
            self.seq.append(name = 'sync_elt-{}'.format(i), 
                wfname = self.adwin_lt2_trigger_element.name)

            for e in elts:
                if e not in self.elements:
                    self.elements.append(e)

            self.elements.append(second_pi2_elt)

        self.elements.append(self.adwin_lt2_trigger_element)
  
    def dd_sweep_LDE_spin_echo_time_msmt(self):
        self.seq = pulsar.Sequence('{}_{}_sequence'.format(self.mprefix, self.name))

        self.elements = []
        LDE_elt = self.LDE_element(name = 'LDE_element',
                pi2_pulse_phase = self.params_lt2['pi2_pulse_phase'])
        self.elements.append(LDE_elt)

        for i in range(self.params['pts']):

            self.seq.append(name = 'LDE_element-{}'.format(i), 
                wfname = LDE_elt.name, 
                trigger_wait = True)

            self.seq, total_elt_time, elts = self.dynamical_decoupling(self.seq, 
                time_offset = LDE_elt.length(),
                begin_offset_time = self.params_lt2['dd_spin_echo_times'][i],
                free_evolution_time = self.params_lt2['free_evolution_times'][i], 
                extra_t_between_pulses = self.params_lt2['extra_ts_between_pulses'][i],
                use_delay_reps = self.params['dd_use_delay_reps'],
                name = i)

            second_pi2_elt = self.second_pi2(name = i, 
                time_offset = LDE_elt.length() + total_elt_time, 
                CORPSE_pi2_phase = self.params_lt2['pi2_pulse_phase'])

            self.seq.append(name = 'second_pi2-{}'.format(i), 
                wfname = second_pi2_elt.name)
            self.seq.append(name = 'sync_elt-{}'.format(i), 
                wfname = self.adwin_lt2_trigger_element.name)

            
            for e in elts:
                if e not in self.elements:
                    self.elements.append(e)

            self.elements.append(second_pi2_elt)

        self.elements.append(self.adwin_lt2_trigger_element)


def dd_sweep_free_ev_time(name):
    m = DynamicalDecoupling('calibrate_first_revival')
    prepare(m)

    pts = 16
    m.params['pts'] = pts
    m.params['repetitions'] = 1000
    m.params_lt2['wait_for_AWG_done'] = 1

    # sweep params
    m.params_lt2['revival_nr'] = 1
    #free evolutiona time is half the total evolution time!!! from centre to centre of pulses
    m.params_lt2['free_evolution_times'] = np.linspace(-15e-6, 15e-6, pts) + \
        m.params_lt2['first_C_revival'] * m.params_lt2['revival_nr']#

    m.params_lt2['DD_pi_phases'] = [0]
    m.dd_sweep_free_ev_time_msmt()

    # for the autoanalysis
    m.params_lt2['sweep_name'] = 'total free evolution time (us)'
    m.params_lt2['sweep_pts'] = 2*m.params_lt2['free_evolution_times'] / 1e-6  

    finish(m,upload=True,debug=False)


def dd_sweep_free_ev_time_with_LDE(name):
    m = DynamicalDecoupling('calibrate_first_revival_w_LDE')
    prepare(m)

    pts = 16
    m.params['pts'] = pts
    m.params['repetitions'] = 1000
    m.params_lt2['wait_for_AWG_done'] = 1

    m.params_lt2['revival_nr'] = 1
    m.params_lt2['dd_spin_echo_times'] = np.ones(pts) * m.params_lt2['dd_spin_echo_time']
    params_lt2['extra_ts_between_pulses'] = np.ones(pts) * 0




    # sweep params
    #free evolutiona time is half the total evolution time!!! from centre to centre of pulses
    m.params_lt2['free_evolution_times'] = np.linspace(-15e-6, 15e-6, pts) + \
        m.params_lt2['first_C_revival'] * m.params_lt2['revival_nr']#

    m.params_lt2['DD_pi_phases'] = [0]
    m.dd_sweep_LDE_spin_echo_time_msmt()

    # for the autoanalysis
    m.params_lt2['sweep_name'] = 'total free evolution time (us)'
    m.params_lt2['sweep_pts'] = 2*m.params_lt2['free_evolution_times'] / 1e-6  

    finish(m,upload=True,debug=False)


def dd_sweep_LDE_spin_echo_time(name):
    m = DynamicalDecoupling('calibrate_LDE_spin_echo_time')
    prepare(m)

    pts = 9
    m.params['pts'] = pts
    m.params['repetitions'] = 1000
    m.params_lt2['wait_for_AWG_done'] = 1

    #free evolutiona time is half the total evolution time!!! from centre to centre of pulses
    m.params_lt2['revival_nr'] = 1
    m.params_lt2['free_evolution_times'] = np.ones(pts) * m.params_lt2['first_C_revival']

    # sweep params
    m.params_lt2['dd_spin_echo_times'] = np.linspace(-300e-9, 500e-9, pts)
    
    m.params_lt2['DD_pi_phases'] = [0]
    m.dd_sweep_LDE_spin_echo_time_msmt()

    # for the autoanalysis
    m.params_lt2['sweep_name'] = 'total free evolution time (us)'
    m.params_lt2['sweep_pts'] = m.params_lt2['dd_spin_echo_times'] / 1e-6  

    finish(m,upload=True,debug=False)




def things_to_remember():
    self.params['extra_t_between_pulses'][i]
    self.params['free_evolution_times'][i]
    self.params['extra_ts_before_pi2'][i]
    self.params['phases'][i]

    self.params['CORPSE_pi_phases'][j]


    if init_ms1:
        seq.append(name = 'CORPSE_shelving-{}'.format(name),
            wfname= CORPSE_shelving_elt.name,
            trigger_wait = True)
        seq.append(name = 'first_pi2-{}'.format(name),
            wfname = first_pi2_elt.name)
    else:
        seq.append(name = 'first_pi2-{}'.format(name),
            wfname = first_pi2_elt.name,
            trigger_wait = True)


    seq.append(name = 'second_pi2-{}'.format(name),
        wfname = second_pi2_elt.name)

    seq.append(name='sync-{}'.format(name),
         wfname = sync_elt.name)

    ## THIS TIMING CALCULATION USED FOR BOTH THE CALIBRATION AND LDE
    # calculate the right time offset of the final pi/2 element, that is crucial for the right phase.


    # program AWG
    #if upload:
    #    qt.pulsar.upload(sync_elt, wait_1us, first_pi2_elt, *elts)
    #qt.pulsar.program_sequence(seq)


class ZerothRevival(pulsar_msmt.PulsarMeasurement):
    """
    This class is for measuring on the 'zeroth' revival: without spin echo thus.
    """
    mprefix = 'DynamicalDecoupling'

    def generate_sequence(self, upload=True, **kw):

        T = pulse.SquarePulse(channel='MW_pulsemod',
            length = 10e-9, amplitude = 0)
        CORPSE_pi = self.CORPSE_pi
        CORPSE_pi2 = self.CORPSE_pi2

        sync_elt = element.Element('adwin_sync', pulsar=qt.pulsar)
        adwin_sync = pulse.SquarePulse(channel='adwin_sync',
            length = 10e-6, amplitude = 2)
        sync_elt.append(adwin_sync)

        elts = []
        seq = pulsar.Sequence('Zeroth revival sequence')

        for i in range(self.params['pts']):
            e = element.Element('pi2_pi_pi2-{}'.format(i), pulsar= qt.pulsar,
            global_time = True, time_offset = 0.)
            e.append(T)
            e.append(CORPSE_pi2)
            e.append(pulse.cp(T,
                length = self.params['free_evolution_times'][i]))
            e.append(CORPSE_pi)
            e.append(pulse.cp(T,
                length = self.params['free_evolution_times'][i]))
            e.append(pulse.cp(CORPSE_pi2,
                phase = self.params['pi2_phases'][i]))
            e.append(T)

            elts.append(e)

            seq.append(name='pi2_pi_pi2-{}'.format(i),
                wfname = e.name,
                trigger_wait = True )

            seq.append(name='sync-{}'.format(i),
                wfname = sync_elt.name)


        if upload:
            qt.pulsar.upload(sync_elt, *elts)
        qt.pulsar.program_sequence(seq)



### functions


###### calibrating  #######




def dd_sweep_t_between_pi_pulses(name):
    m = DynamicalDecoupling('calibrate_dt_between_pi_pulses_r=1_YY')
    prepare(m)

    pts = 61
    m.params['pts'] = pts
    m.params['repetitions'] = 1000
    m.params['wait_for_AWG_done'] = 1
    m.params['revivals'] = 1

    # sweep params
    m.params['free_evolution_times'] = np.ones(pts) * m.params['first_C_revival'] * m.params['revivals'] #+ 53e-6#
    m.params['extra_t_between_pulses'] = np.linspace(-300e-9,-180e-9,pts)
    m.params['extra_ts_before_pi2']  = np.ones(pts) * 0
    m.params['CORPSE_pi2_2_amp'] = m.params['CORPSE_pi2_amp']
    m.params['CORPSE_pi_phases'] = np.ones(pts) * -90
    m.params['phases'] = np.ones(pts) * 0 
    m.params['multiplicity'] = 2

    # for the autoanalysis
    m.params['sweep_name'] = 'EXTRA time between CORPSE pulses (ns)'
    m.params['sweep_pts'] = m.params['extra_t_between_pulses'] /1e-6

    finish(m)


def dd_sweep_t_before_pi2(name):
    m = DynamicalDecoupling('sweep_t_before_second_pi2_m=2')
    prepare(m)

    pts = 61
    m.params['pts'] = pts
    m.params['repetitions'] = 1000
    m.params['wait_for_AWG_done'] = 1

    m.params['free_evolution_times'] = np.ones(pts) * m.params['first_C_revival'] #+ 53e-6#
    m.params['extra_t_between_pulses'] = np.ones(pts) * 0
    m.params['CORPSE_pi_phases'] = np.ones(pts) * 0
    m.params['phases'] = np.ones(pts) * 0 
    m.params['multiplicity'] = 2
    # sweep params
    m.params['extra_ts_before_pi2'] = np.linspace(-600e-9,2000e-9,pts)

    # for the autoanalysis
    m.params['sweep_name'] = 'EXTRA time before pi/2 analysis pulse (us)'
    m.params['sweep_pts'] = m.params['extra_ts_before_pi2'] /1e-6  

    finish(m)


def dd_sweep_analysis_phase(name):
    m = DynamicalDecoupling('sweep_analysis_phase')
    prepare(m)

    pts = 21
    m.params['pts'] = pts
    m.params['repetitions'] = 1000
    m.params['wait_for_AWG_done'] = 1

    # sweep params
    m.params['free_evolution_times'] = np.ones(pts) *m.params['first_C_revival']#np.linspace(-15e-6, 15e-6, pts) + 53e-6#
    m.params['CORPSE_pi_phases'] = np.ones(pts) * 0
    m.params['extra_t_between_pulses'] = np.ones(pts) * 200e-9
    m.params['phases'] = np.linspace(0,360,pts)
    m.params['multiplicity'] = 2

    # for the autoanalysis
    m.params['sweep_name'] = 'analysis phase second pi/2 pulse (deg)'
    m.params['sweep_pts'] = m.params['phases']   

    finish(m,upload=False,debug=True)



#### debugging ####

def dd_spinecho_no_2nd_pi(name):
    m = DynamicalDecoupling('2_pulses_sweep_fet')
    prepare(m)

    pts = 41
    m.params['pts'] = pts
    m.params['repetitions'] = 1000
    m.params['wait_for_AWG_done'] = 1

    # sweep params
    m.params['free_evolution_times'] = np.linspace(-15e-6, 15e-6, pts) + m.params['first_C_revival'] #+ 53e-6#
    m.params['extra_t_between_pulses'] = np.ones(pts)*0
    m.params['CORPSE_pi_phases'] = np.ones(pts) * 0
    m.params['phases'] = np.ones(pts)*0 #linspace(0,360,pts)
    m.params['extra_ts_before_pi2'] = np.ones(pts) * 0
    m.params['multiplicity'] = 1


    m.params['CORPSE_pi2_2_amp'] = 0.


    # for the autoanalysis
    m.params['sweep_name'] = 'total free evolution time (us)'
    m.params['sweep_pts'] = 2* m.params['free_evolution_times'] /1e-6  

    finish(m, upload = True, debug = False)


def dd_spinecho_no_pi_and_2nd_pi(name):
    m = DynamicalDecoupling('2_pulses_sweep_fet')
    prepare(m)

    pts = 41
    m.params['pts'] = pts
    m.params['repetitions'] = 1000
    m.params['wait_for_AWG_done'] = 1

    # sweep params
    m.params['free_evolution_times'] = np.linspace(-15e-6, 15e-6, pts) + m.params['first_C_revival'] #+ 53e-6#
    m.params['extra_t_between_pulses'] = np.ones(pts)*0
    m.params['CORPSE_pi_phases'] = np.ones(pts) * 0
    m.params['phases'] = np.ones(pts)*0 #linspace(0,360,pts)
    m.params['extra_ts_before_pi2'] = np.ones(pts) * 0
    m.params['multiplicity'] = 1

    m.params['CORPSE_pi_amp'] = 0
    m.params['CORPSE_pi2_2_amp'] = 0.


    # for the autoanalysis
    m.params['sweep_name'] = 'total free evolution time (us)'
    m.params['sweep_pts'] = 2* m.params['free_evolution_times'] /1e-6  

    finish(m, upload = True, debug = False)


#### XX sequence ######

def dd_sequence(name):
    m = DynamicalDecoupling('XX_sequence_sweep_fet')
    prepare(m)

    pts = 41
    m.params['pts'] = pts
    m.params['repetitions'] = 1000
    m.params['wait_for_AWG_done'] = 1
    m.params['revivals'] = 1

    # sweep params
    m.params['free_evolution_times'] = np.linspace(-15e-6, 15e-6, pts) + m.params['first_C_revival'] * m.params['revivals'] #+ 53e-6#
    m.params['extra_t_between_pulses'] = np.ones(pts) * -233e-9
    m.params['CORPSE_pi_phases'] = np.ones(pts) * 0
    m.params['extra_ts_before_pi2']  = np.ones(pts) * 0
    m.params['CORPSE_pi2_2_amp'] = m.params['CORPSE_pi2_amp']

    m.params['phases'] = np.ones(pts)*0 #linspace(0,360,pts)
    m.params['multiplicity'] = 2

    # for the autoanalysis
    m.params['sweep_name'] = 'total free evolution time (us)'
    m.params['sweep_pts'] = (2* m.params['free_evolution_times'] *m.params['multiplicity'] - 234e-9) /1e-6  

    finish(m, upload = True, debug = False)



#### YY sequence ######

def dd_Y_sequence(name):
    m = DynamicalDecoupling('YY_sequence_sweep_fet')
    prepare(m)

    pts = 41
    m.params['pts'] = pts
    m.params['repetitions'] = 1000
    m.params['wait_for_AWG_done'] = 1

    # sweep params
    m.params['free_evolution_times'] = np.linspace(-15e-6, 15e-6, pts) + m.params['first_C_revival'] #+ 53e-6#
    m.params['CORPSE_pi_phases'] = np.ones(pts)*-90
    m.params['phases'] = np.ones(pts)*0 #linspace(0,360,pts)
    m.params['multiplicity'] = 2

    # for the autoanalysis
    m.params['sweep_name'] = 'total free evolution time (us)'
    m.params['sweep_pts'] = 2* m.params['free_evolution_times'] /1e-6  

    finish(m)





#### XY4 #########


def dd_xy4_sweep_fet(name):
    m = DynamicalDecoupling('dd_xy4_sweep_fet')
    prepare(m)

    pts = 41
    m.params['pts'] = pts
    m.params['repetitions'] = 1000
    m.params['wait_for_AWG_done'] = 1
    m.params['revivals'] = 1

    m.params['free_evolution_times'] = np.linspace(-1.25e-6,1.25e-6,pts) + m.params['first_C_revival'] *m.params['revivals']
    m.params['extra_t_between_pulses'] = np.ones(pts) * -235e-9
    m.params['phases'] = np.ones(pts) * 0 
    m.params['CORPSE_pi2_2_amp'] = m.params['CORPSE_pi2_amp']

    # sweep params
    m.params['extra_ts_before_pi2'] = np.ones(pts) * 0

    #define the decoupling sequence:
    m.params['multiplicity'] = 4
    m.params['CORPSE_pi_phases'] = [0,-90,0,-90]

    # for the autoanalysis
    m.params['sweep_name'] = 'total free evolution time (us)'
    m.params['sweep_pts'] = (2 * m.params['multiplicity'] * m.params['free_evolution_times'] \
        + (m.params['multiplicity']-1) * -235e-9 )/1e-6  

    finish(m)

def dd_xy4_sweep_t_between_pi(name):
    m = DynamicalDecoupling('dd_xy4_sweep_t_between_pi')
    prepare(m)

    pts = 31
    m.params['pts'] = pts
    m.params['repetitions'] = 1000
    m.params['wait_for_AWG_done'] = 1
    m.params['revivals']

    m.params['free_evolution_times'] = np.ones(pts) * m.params['first_C_revival']  * m.params['revivals']#+ 53e-6#
    m.params['extra_t_between_pulses'] = np.linspace(-300e-9,-180e-9,pts)
    m.params['phases'] = np.ones(pts) * 0 
    m.params['CORPSE_pi2_2_amp'] = m.params['CORPSE_pi2_amp']
    
    # sweep params
    m.params['extra_ts_before_pi2'] = np.ones(pts) * 0

    #define the decoupling sequence:
    # the decoupling sequence is formed of a specific number of pulses, with specific phase. 
    #Define here for each pulse a phase.
    m.params['multiplicity'] = 4
    m.params['CORPSE_pi_phases'] = [0,-90,0,-90]

    # for the autoanalysis
    m.params['sweep_name'] = 'EXTRA time between pi pulses (us)'
    m.params['sweep_pts'] = m.params['extra_t_between_pulses'] /1e-6  

    finish(m)


#### XY 8 #######


def dd_xy8_sweep_fet(name):
    m = DynamicalDecoupling('dd_xy8_sweep_fet')
    prepare(m)

    pts = 41
    m.params['pts'] = pts
    m.params['repetitions'] = 1000
    m.params['wait_for_AWG_done'] = 1

    m.params['free_evolution_times'] = np.linspace(-10e-6,10e-6,pts) + m.params['first_C_revival'] #+ 53e-6#
    m.params['extra_t_between_pulses'] = np.ones(pts) * -179e-9
    m.params['phases'] = np.ones(pts) * 0 
    m.params['CORPSE_pi2_2_amp'] = m.params['CORPSE_pi2_amp']

    # sweep params
    m.params['extra_ts_before_pi2'] = np.ones(pts) * 0

    #define the decoupling sequence:
    m.params['multiplicity'] = 8
    m.params['CORPSE_pi_phases'] = [0,-90,0,-90,90,180,90,180]

    # for the autoanalysis
    m.params['sweep_name'] = 'total free evolution time (us)'
    m.params['sweep_pts'] = (2 * m.params['multiplicity'] * m.params['free_evolution_times'] \
        + (m.params['multiplicity']-1) * -179e-9 )/1e-6  

    finish(m)

def dd_xy8_sweep_t_between_pi(name):
    m = DynamicalDecoupling('dd_xy8_sweep_t_between_pi')
    prepare(m)

    pts = 41
    m.params['pts'] = pts
    m.params['repetitions'] = 1000
    m.params['wait_for_AWG_done'] = 1

    m.params['free_evolution_times'] = np.ones(pts) * m.params['first_C_revival'] #+ 53e-6#
    m.params['extra_t_between_pulses'] = np.linspace(-1000e-9,600e-9,pts)
    m.params['phases'] = np.ones(pts) * 0 
    m.params['CORPSE_pi2_2_amp'] = m.params['CORPSE_pi2_amp']
    
    # sweep params
    m.params['extra_ts_before_pi2'] = np.ones(pts) * 0

    #define the decoupling sequence:
    # the decoupling sequence is formed of a specific number of pulses, with specific phase. 
    #Define here for each pulse a phase.
    m.params['multiplicity'] = 8
    m.params['CORPSE_pi_phases'] = [0,-90,0,-90,90,180,90,180]

    # for the autoanalysis
    m.params['sweep_name'] = 'EXTRA time between pi pulses (us)'
    m.params['sweep_pts'] = m.params['extra_t_between_pulses'] /1e-6  

    finish(m)


####### t1 ##########


def t1(name):
    m = DynamicalDecoupling('measure_t1_from_ms0')
    prepare(m)

    pts = 21
    m.params['pts'] = pts
    m.params['repetitions'] = 1000
    m.params['wait_for_AWG_done'] = 1

    # sweep params
    m.params['free_evolution_times'] = np.linspace(2e-6, 10e-3+2e-6, pts) 
    m.params['extra_t_between_pulses'] = np.ones(pts)*0
    m.params['CORPSE_pi_phases'] = np.ones(pts)*0
    m.params['phases'] = np.ones(pts)*0
    m.params['multiplicity'] = 1

    # keep this order for right  CORPSE_pi_shelv_amp
    #m.params['CORPSE_pi_shelv_amp'] = m.params['CORPSE_pi_amp'] 
    m.params['CORPSE_pi_amp'] = 0.
    m.params['CORPSE_pi2_amp'] = 0.

    # for the autoanalysis
    m.params['sweep_name'] = 'total free evolution time (us)'
    m.params['sweep_pts'] = (2*m.params['free_evolution_times'] ) /1e-6

    finish(m, init_ms1 = False)


####### t2 ##########


def t2(name):
    revival_nrs = np.arange(14)+1

    # make a seperately named folder for each revival, that the analysis script can recognize.
    
    for r in revival_nrs:
        m = DynamicalDecoupling('t2_revival_{}_'.format(r))
        prepare(m)

        pts = 16
        m.params['pts'] = pts
        m.params['repetitions'] = 1000
        m.params['wait_for_AWG_done'] = 1

        m.params['extra_t_between_pulses'] = np.ones(pts) * 0
        m.params['extra_ts_before_pi2']  = np.ones(pts) * 0
        m.params['CORPSE_pi_phases'] = np.ones(pts) * 0
        m.params['CORPSE_pi2_2_amp'] = m.params['CORPSE_pi2_amp']
        m.params['phases'] = np.ones(pts) * 0 
        m.params['multiplicity'] = 1
        # sweep params
    
        m.params['free_evolution_times'] = np.linspace(-14e-6,14e-6,pts) + \
            r * m.params['first_C_revival'] 
        
        # for the autoanalysis
        m.params['sweep_name'] = 'total free evolution time (us)'
        m.params['sweep_pts'] = 2*m.params['multiplicity']*m.params['free_evolution_times'] /1e-6  

        print 'revival-{}'.format(r)

        m.autoconfig()
        m.generate_sequence()
        m.run()
        m.save()
        m.finish()

def t2_XY4(name):
    revival_nrs = np.arange(14)+1

    # make a seperately named folder for each revival, that the analysis script can recognize.
    
    for r in revival_nrs:
        m = DynamicalDecoupling('t2_xy4_revival_{}_'.format(r))
        prepare(m)

        pts = 11
        m.params['pts'] = pts
        m.params['repetitions'] = 1000
        m.params['wait_for_AWG_done'] = 1

        m.params['extra_t_between_pulses'] = np.ones(pts) * 0
        m.params['extra_ts_before_pi2']  = np.ones(pts) * -233e-9
        m.params['CORPSE_pi_phases'] = np.ones(pts) * 0
        m.params['CORPSE_pi2_2_amp'] = m.params['CORPSE_pi2_amp']
        m.params['phases'] = [0,-90,0,-90]
        m.params['multiplicity'] = 4
        # sweep params
    
        m.params['free_evolution_times'] = np.linspace(-15e-6,15e-6,pts) + \
            r * m.params['first_C_revival'] 
        
        # for the autoanalysis
        m.params['sweep_name'] = 'total free evolution time (us)'
        m.params['sweep_pts'] = 2*m.params['multiplicity']*m.params['free_evolution_times'] -212e-9*r*(m.params['multiplicity']-1) /1e-6  

        print 'revival-{}'.format(r)

        m.autoconfig()
        m.generate_sequence()
        m.run()
        m.save()
        m.finish()


def zerothrevival(name):
    m = ZerothRevival('pi2-pi-pi2_revival_0_')
    prepare(m)

    pts = 21
    m.params['pts'] = pts
    m.params['repetitions'] = 1000
    m.params['wait_for_AWG_done'] = 1

    # sweep params
    m.params['free_evolution_times'] = np.linspace(10e-9,8e-6+10e-9, pts) #+\
        #m.params['first_C_revival']
    m.params['pi2_phases'] = np.ones(pts) * 0 

    # for the autoanalysis
    m.params['sweep_name'] = 'total free evolution time (us)'
    m.params['sweep_pts'] = 2*m.params['free_evolution_times'] /1e-6  

    finish(m)


def twod_tau_sweep(name):
    pts = 11
    fet = m.params['first_C_revival']
    m.params['tau_pi2_to_pi'] = fet + np.linspace(-500e-9,500e-9,pts)
    m.params['tau_pi_to_pi'] = fet + np.linspace(-500e-9,500e-9,pts)
    # make a seperately named folder for each revival, that the analysis script can recognize.
    
    for i,t in enumerate(m.params['tau_pi_to_pi']):
        m = DynamicalDecoupling('twod_tau_sweep_{}_'.format(i))
        prepare(m)

        m.params['pts'] = pts
        m.params['repetitions'] = 1000
        m.params['wait_for_AWG_done'] = 1

        m.params['extra_ts_before_pi2']  = np.ones(pts) * 0
        m.params['CORPSE_pi_phases'] = np.ones(pts) * 0
        m.params['CORPSE_pi2_2_amp'] = m.params['CORPSE_pi2_amp']
        m.params['phases'] = np.ones(pts) * 0 
        m.params['multiplicity'] = 2
        
        # sweep params
        m.params['free_evolution_times'] = m.params['tau_pi2_to_pi']  
        m.params['extra_t_between_pulses'] = i - m.params['tau_pi2_to_pi'] 

        
        # for the autoanalysis
        m.params['sweep_name'] = 'pi/2 to pi free evolution time (us)'
        m.params['sweep_pts'] = m.params['tau_pi2_to_pi']  /1e-6  

        print 'sweep tau {} of {}'.format(i,pts) 

        m.autoconfig()
        m.generate_sequence()
        m.run()
        m.save()
        m.finish()

def twod_tau_sweep_v2(name):
    pts = 11
    fet = m.params['first_C_revival']
    m.params['tau_pi2_to_pi'] = fet + np.linspace(-500e-9,500e-9,pts)
    m.params['tau_pi_to_pi'] = fet + np.linspace(-500e-9,500e-9,pts)
    # make a seperately named folder for each revival, that the analysis script can recognize.
    
    for i,t in enumerate(m.params['tau_pi_to_pi']):
        m = DynamicalDecoupling('twod_tau_sweep_{}_'.format(i))
        prepare(m)

        m.params['pts'] = pts
        m.params['repetitions'] = 1000
        m.params['wait_for_AWG_done'] = 1

        m.params['extra_ts_before_pi2']  = np.ones(pts) * 0
        m.params['CORPSE_pi_phases'] = np.ones(pts) * 0
        m.params['CORPSE_pi2_2_amp'] = m.params['CORPSE_pi2_amp']
        m.params['phases'] = np.ones(pts) * 0 
        m.params['multiplicity'] = 2
        
        # sweep params
        m.params['free_evolution_times'] = m.params['tau_pi2_to_pi']  
        m.params['extra_t_between_pulses'] = i - m.params['tau_pi2_to_pi'] 

        
        # for the autoanalysis
        m.params['sweep_name'] = 'pi/2 to pi free evolution time (us)'
        m.params['sweep_pts'] = m.params['tau_pi2_to_pi']  /1e-6  

        print 'sweep tau {} of {}'.format(i,pts) 

        m.autoconfig()
        m.generate_sequence()
        m.run()
        m.save()
        m.finish()


if __name__ == '__main__':
    #calibrate the position of first Carbon revival. 
    dd_sweep_free_ev_time(name)
    #dd_sweep_free_ev_time_with_LDE(name)

    #calibrate the extra time between pi pulses (on top of free evolution time)
    #dd_sweep_t_between_pi_pulses(name)

    #dd_sweep_analysis_phase(name)
    #dd_sweep_t_before_pi2(name)

    #dd_spinecho_no_2nd_pi(name)
    #dd_spinecho_no_pi_and_2nd_pi(name)

    #dd_sequence(name)
    #dd_Y_sequence(name+'test')

    #dd_xy4_sweep_t_between_pi(name)
    #dd_xy4_sweep_fet(name)
    #dd_xy8_sweep_t_between_pi(name)
    #dd_xy8_sweep_fet(name)
    
    #t1(name)
    #t2(name)
    #t2_xy4(name)

    #zerothrevival(name)

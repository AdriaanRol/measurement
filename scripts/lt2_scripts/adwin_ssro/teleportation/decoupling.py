"""
LT2 script for calibration
"""
import numpy as np
import qt

import measurement.lib.measurement2.measurement as m2
from measurement.lib.measurement2.adwin_ssro import pulsar as pulsar_msmt
from measurement.lib.pulsar import pulse, pulselib, element, pulsar
reload(pulselib)

from measurement.scripts.lt2_scripts.adwin_ssro import espin_funcs as funcs
reload(funcs)

from measurement.scripts.teleportation import sequence 
reload(sequence)

name = 'sil15'


def prepare(m):
    funcs.prepare(m)

    m.params_lt2 = m2.MeasurementParameters('LT2Parameters')
    m.params_lt2['MW_pulse_mod_risetime'] = 10e-9  
    sequence.pulse_defs_lt2(m)


def finish(m, upload=True, debug=False, **kw):
    funcs.finish(m, upload, debug, **kw)

### msmt class
class DynamicalDecoupling(pulsar_msmt.PulsarMeasurement):
    mprefix = 'DynamicalDecoupling'

    def generate_sequence(self, upload=True, **kw):
        # electron manipulation pulses

        init_ms1 = kw.pop('init_ms1', False)
     
        T = pulse.SquarePulse(channel='MW_pulsemod',
            length = 10e-9, amplitude = 0)
        CORPSE_pi = self.CORPSE_pi
        CORPSE_pi2 = self.CORPSE_pi2

        # elts includes wait_rest_elts and second_pi2_elts, and if init_ms1: CORPSE_shelv_elt
        elts = []


        if init_ms1:
            CORPSE_shelving_elt = element.Element('CORPSE_shelving_elt', pulsar= qt.pulsar, 
                global_time = True, time_offset = 0.)
            CORPSE_shelving_elt.append(pulse.cp(T, length = 400e-9))
            CORPSE_shelving_elt.append(pulse.cp(CORPSE_pi, 
                amplitude = self.params['CORPSE_pi_shelv_amp']))
            CORPSE_shelving_elt.append(pulse.cp(T, length = 400e-9))
            elts.append(CORPSE_shelving_elt)

        # around each pulse I make an element with length 1600e-9; 
        # the centre of the pulse is in the centre of the element.
        # this helps me to introduce the right waiting times, 
        # counting from centre of the pulses
        CORPSE_pi_wait_length = 800e-9 - (CORPSE_pi.length - 2*self.params['MW_pulse_mod_risetime'])/2
        CORPSE_pi2_wait_length = 800e-9 - (CORPSE_pi2.length - 2*self.params['MW_pulse_mod_risetime'])/2 

        first_pi2_elt = element.Element('first_pi2_elt', pulsar= qt.pulsar, 
            global_time = True, time_offset = 0.)
        first_pi2_elt.append(pulse.cp(T, length = 100e-9))

        first_pi2_elt.append(pulse.cp(CORPSE_pi2, 
            amplitude = self.params['CORPSE_pi2_amp']))
        first_pi2_elt.append(pulse.cp(T, 
            length =  CORPSE_pi2_wait_length))

        wait_1us = element.Element('1us_delay', pulsar=qt.pulsar, global_time =  True)
        wait_1us.append(pulse.cp(T, length=1e-6))

        sync_elt = element.Element('adwin_sync', pulsar=qt.pulsar)
        adwin_sync = pulse.SquarePulse(channel='adwin_sync',
            length = 10e-6, amplitude = 2)
        sync_elt.append(adwin_sync)



        # sequence
        seq = pulsar.Sequence('Dynamical decoupling sequence')
        for i in range(self.params['pts']):  
            reduced_free_ev_time = self.params['free_evolution_times'][i] - 800e-9 - 800e-9        
            # calculate how many waits of 1 us fit in the free evolution time (-1 repetition)
            # this is twice the 800e-9 s that are the wrap-arounds of the pulses
            delay_reps = np.floor(reduced_free_ev_time/1e-6) - 2
            #calculate how much wait time should be added to the above to fill the full free evolution time (+1 us to fill full elt)
            rest_time = np.mod(reduced_free_ev_time,1e-6) + 2e-6
            
            wait_rest_elt = element.Element('wait_rest_elt-{}'.format(i), pulsar=qt.pulsar,
                global_time = True)
            wait_rest_elt.append(pulse.cp(T, length = rest_time))
            elts.append(wait_rest_elt)

            if init_ms1:
                seq.append(name = 'CORPSE_shelving-{}'.format(i),
                    wfname= CORPSE_shelving_elt.name,
                    trigger_wait = True)
                seq.append(name = 'first_pi2-{}'.format(i),
                    wfname = first_pi2_elt.name)
            else:
                seq.append(name = 'first_pi2-{}'.format(i),
                    wfname = first_pi2_elt.name,
                    trigger_wait = True)

            for j in range(self.params['multiplicity']):
                #calculate the time offset for the CORPSE pulse element
                # the case j>0 asks for adding extra wrap-around times, 
                # that are added to the CORPSE elements.
                time_offset_CORPSE = first_pi2_elt.length()  \
                    + (2 * j + 1) * reduced_free_ev_time  
                if j > 0:
                    time_offset_CORPSE  = time_offset_CORPSE \
                        + (2 * j - 1) * 1600e-9 \
                        + (j - 1) * self.params['extra_t_between_pulses'][i] 
                        # 1600e-9 is free_ev_time - reduced_free_ev_time             
               
                CORPSE_elt = element.Element('CORPSE_elt-{}-{}'.format(i,j), pulsar= qt.pulsar, 
                    global_time = True, time_offset = time_offset_CORPSE )
                # append a longer waiting time for the not first CORPSE pulse, to get the right evolution time
                if j == 0:
                    CORPSE_elt.append(pulse.cp(T, 
                        length = CORPSE_pi_wait_length ))
                else:
                    # add an extra 1600e-9, that would otherwise be the wrap-around of a pulse
                    # also add the possibility to make the time between pi pulses different,
                    # this could correct for where the centre of the pi/2 pulse is.
                    CORPSE_elt.append(pulse.cp(T, 
                        length = CORPSE_pi_wait_length + 1600e-9 + self.params['extra_t_between_pulses'][i] ))
                CORPSE_elt.append(pulse.cp(CORPSE_pi, 
                    amplitude = self.params['CORPSE_pi_amp'],
                    phase = self.params['CORPSE_pi_phases'][j]))
                CORPSE_elt.append(pulse.cp(T, 
                    length = CORPSE_pi_wait_length ))
                elts.append(CORPSE_elt)
               
                seq.append(name = 'wait1-{}-{}'.format(i,j), 
                    wfname = wait_1us.name, 
                    repetitions = delay_reps)
                seq.append(name= 'wait_rest1-{}-{}'.format(i,j),
                    wfname = wait_rest_elt.name)
                seq.append(name = CORPSE_elt.name+'-{}-{}'.format(i,j), 
                    wfname = CORPSE_elt.name)
                seq.append(name = 'wait2-{}-{}'.format(i,j), 
                    wfname = wait_1us.name, 
                    repetitions = delay_reps)
                seq.append(name= 'wait_rest2-{}-{}'.format(i,j),
                    wfname = wait_rest_elt.name)

                # calculate the right time offset, that is crucial for the right phase.
            time_offset_pi2_2 = first_pi2_elt.length() \
                + (2 * self.params['multiplicity'] - 1) * 1600e-9 \
                + self.params['multiplicity'] * 2 * reduced_free_ev_time \
                + (self.params['multiplicity'] - 1 ) * self.params['extra_t_between_pulses'][i] 

            second_pi2_elt = element.Element('second_pi2_elt-{}'.format(i), pulsar= qt.pulsar, 
                global_time = True, time_offset = time_offset_pi2_2 )
            second_pi2_elt.append(pulse.cp(T, 
                length = CORPSE_pi2_wait_length + self.params['extra_ts_before_pi2'][i]))
            second_pi2_elt.append(pulse.cp(CORPSE_pi2, 
                amplitude = self.params['CORPSE_pi2_2_amp'],
                phase = self.params['phases'][i]))
            second_pi2_elt.append(pulse.cp(T, length =  100e-9 ))            
            elts.append(second_pi2_elt)

            seq.append(name = 'second_pi2-{}'.format(i),
                wfname = second_pi2_elt.name)

            seq.append(name='sync-{}'.format(i),
                 wfname = sync_elt.name)

        # program AWG
        if upload:
            qt.pulsar.upload(sync_elt, wait_1us, first_pi2_elt, *elts)
        qt.pulsar.program_sequence(seq)



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





### Calibration stage 1
def dd_sweep_free_ev_time(name):
    m = DynamicalDecoupling('sweep_free_ev_time_second_revival')
    prepare(m)

    pts = 41
    m.params['pts'] = pts
    m.params['repetitions'] = 1000
    m.params['wait_for_AWG_done'] = 1

    # sweep params
    m.params['revival_nr'] = 2
    #free evolutiona time is half the total evolution time!!! from end to begin of pulses
    m.params['free_evolution_times'] = np.linspace(-15e-6, 15e-6, pts) + \
        m.params['first_C_revival'] * m.params['revival_nr']#
    m.params['CORPSE_pi_phases'] = np.ones(pts)*0
    m.params['phases'] = np.ones(pts)*0. 
    m.params['multiplicity'] = 1

    #m.params['CORPSE_pi_amp'] = 0.
    #m.params['CORPSE_pi2_amp'] = 0.

    # for the autoanalysis
    m.params['sweep_name'] = 'total free evolution time (us)'
    m.params['sweep_pts'] = 2*m.params['free_evolution_times'] / 1e-6  

    finish(m,upload=True,debug=False)


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

def dd_sequence(name):
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
    m.params['multiplicity'] = 1

    # for the autoanalysis
    m.params['sweep_name'] = 'total free evolution time (us)'
    m.params['sweep_pts'] = 2* m.params['free_evolution_times'] /1e-6  

    finish(m, upload = True, debug = False)

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




def dd_Y_sequence(name):
    m = DynamicalDecoupling('1_Y_pulse_sweep_fet')
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


def dd_sweep_between(name):
    m = DynamicalDecoupling('2_pulses_sweep_fet_between_2')
    prepare(m)

    pts = 41
    m.params['pts'] = pts
    m.params['repetitions'] = 1000
    m.params['wait_for_AWG_done'] = 1

    # sweep params
    m.params['free_evolution_times'] = np.ones(pts) * m.params['first_C_revival'] #+ 53e-6#
    m.params['extra_t_between_pulses'] = np.linspace(-1200e-9,1200e-9,pts)
    m.params['CORPSE_pi_phases'] = np.ones(pts) * 0
    m.params['phases'] = np.ones(pts) * 0 
    m.params['multiplicity'] = 2

    # for the autoanalysis
    m.params['sweep_name'] = 'EXTRA total free evolution time between CORPSE pulses (us)'
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


def dd_xy4_sweep_fet(name):
    m = DynamicalDecoupling('dd_xy4_sweep_fet')
    prepare(m)

    pts = 41
    m.params['pts'] = pts
    m.params['repetitions'] = 1000
    m.params['wait_for_AWG_done'] = 1

    m.params['free_evolution_times'] = np.linspace(-15e-6,15e-6,pts) + m.params['first_C_revival'] #+ 53e-6#
    m.params['extra_t_between_pulses'] = np.ones(pts) * -245e-9
    m.params['phases'] = np.ones(pts) * 0 
    
    # sweep params
    m.params['extra_ts_before_pi2'] = np.ones(pts) * 0

    #define the decoupling sequence:
    m.params['multiplicity'] = 4
    m.params['CORPSE_pi_phases'] = [0,-90,0,-90]

    # for the autoanalysis
    m.params['sweep_name'] = 'total free evolution time (us)'
    m.params['sweep_pts'] = (2 * m.params['multiplicity'] * m.params['free_evolution_times'] \
        + (m.params['multiplicity']-1) * -245e-9 )/1e-6  

    finish(m)

def dd_xy4_sweep_t_between_pi(name):
    m = DynamicalDecoupling('dd_xy4_sweep_t_between_pi')
    prepare(m)

    pts = 41
    m.params['pts'] = pts
    m.params['repetitions'] = 1000
    m.params['wait_for_AWG_done'] = 1

    m.params['free_evolution_times'] = np.ones(pts) * m.params['first_C_revival'] #+ 53e-6#
    m.params['extra_t_between_pulses'] = np.linspace(-1600e-9,1600e-9,pts)
    m.params['phases'] = np.ones(pts) * 0 
    
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

def t2(name):
    revival_nrs = np.arange(10)+1

    # make a seperately named folder for each revival, that the analysis script can recognize.
    
    for r in revival_nrs:
        m = DynamicalDecoupling('t2_revival_{}'.format(r))
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
    
        m.params['free_evolution_times'] = np.linspace(-15e-6,15e-6,pts) + \
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

def zerothrevival(name):
    m = ZerothRevival('pi2-pi-pi2_revival_0')
    prepare(m)

    pts = 41
    m.params['pts'] = pts
    m.params['repetitions'] = 1000
    m.params['wait_for_AWG_done'] = 1

    # sweep params
    m.params['free_evolution_times'] = np.linspace(10e-9,15e-6+10e-9, pts) #+\
        #m.params['first_C_revival']
    m.params['pi2_phases'] = np.ones(pts) * 0 

    # for the autoanalysis
    m.params['sweep_name'] = 'total free evolution time (us)'
    m.params['sweep_pts'] = 2*m.params['free_evolution_times'] /1e-6  

    finish(m)



if __name__ == '__main__':
    #dd_sweep_free_ev_time(name)
    #dd_sweep_analysis_phase(name)
    #dd_sequence(name)
    #dd_spinecho_no_2nd_pi(name)
    #dd_spinecho_no_pi_and_2nd_pi(name)
    #dd_Y_sequence(name+'test')
    #dd_sweep_between(name+'test')
    #dd_sweep_t_before_pi2(name)
    #dd_xy4_sweep_fet(name)
    #dd_xy4_sweep_t_between_pi(name)
    #t1(name)
    t2(name)
    
    #zerothrevival(name+'test')

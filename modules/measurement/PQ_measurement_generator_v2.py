## changes:
## rename class
## rename, add and redefine events
## add sync and MA4 to statistics array
## generate savepath
## change threshold definition and behaviour
## change set_section_reset_event to set_sequence_reset_event
## take care of bin size differences of PH and HH
## todo: add PH_300.get_DeviceType()
## todo: set_Binning for HH_400???

from numpy import *
from matplotlib import pyplot as plt

from ctypes import *
from time import sleep
import qt, os
import time

ADwin = qt.instruments['physical_adwin']
MW = qt.instruments['SMB100']

# save just implemented for 1D and 2D data
# ROI just implemented for 2D data
# ROI plot saving for time vs repetition and sweep vs repetition

#####################################
#       events:
EV_none                =  0b00000000
EV_start               =  0b00000001
EV_stop                =  0b00000010
EV_sync                =  0b00000100
EV_MA_1                =  0b00001000
EV_MA_2                =  0b00010000
EV_MA_3                =  0b00100000
EV_MA_4                =  0b01000000
EV_auto                =  0b10000000
#####################################
#       section modes:
time_axis              =  0b00000001
sweep_axis             =  0b00000010
repetition_axis        =  0b00000100
link_to_previous       =  0b00001000
#####################################
#       threshold modes:
thres_dont_use         =  0
thres_use_min          =  1
thres_use_max          =  2
thres_use_min_max      =  3
#####################################
#       loop modes:
loop_repeat_sweeps     =  0b00000000
loop_sweep_repetitions =  0b00000001
#####################################
#       default_validity:
default_valid          =  1
default_invalid        =  0

import measurement

class PQ_measurement(measurement.Measurement): 
    
    def __init__(self, name, mclass='PQ_measurement', *arg, **kw):
        measurement.Measurement.__init__(self, name, mclass, *arg, **kw)

        self.default_binsize = 14

        self.counter_instr = windll.LoadLibrary(qt.config['pq_dll'])
        self.reset()
    
    
    def reset(self):
        self.sections = []
        self.data = []
        self.savdat = {}
        self.MW = []
        self.ADwin_codes = []
        self.ADwin_save_parameters = []
        self.special_save_parameters = []
        self.abort_condition = EV_none
        self.sweep = {'name': 'none', 
            'count': 1,
            'incr_mode': EV_auto,
            'reset_mode': EV_none}

        self.repetitions = {'count': 1,
            'incr_mode': EV_none,
            'reset_mode': EV_none}

        self.loop_order    = loop_repeat_sweeps
        self.sec_incr_ev   = EV_start
        self.seq_res_ev    = EV_auto
        self.conditional_mode = True

    def set_conditional_mode(self, conditional_mode):
        self.conditional_mode = conditional_mode

    def set_abort_condition(self, event = EV_none):
        self.abort_condition = event

    def set_loop_order(self, loop_order):
        self.loop_order = loop_order

    def set_section_increment_event(self, sec_incr_ev):
        self.sec_incr_ev = sec_incr_ev

    def set_sequence_reset_event(self, seq_res_ev):
        self.seq_res_ev = seq_res_ev

    def set_counter_instrument(self, instrument):
        self.counter_instr = instrument

    def set_qtlab_counter_instrument(self, instrument):
        self.qtlab_counter_instr = instrument
        print self.qtlab_counter_instr

    def set_sequence_instrument(self, instrument):
        self.sequence_instr = instrument

    def set_sequence(self, sequence):
        self.sequence = sequence

    def set_sweep(self, name = 'none', count = 1, incr_mode = EV_auto,
            reset_mode = EV_none, incr = 1, start = 0):

        self.sweep = {'name': name, 
                'count': count,
                'start': start,
                'incr':  incr,
                'incr_mode': incr_mode,
                'reset_mode': reset_mode}

    def set_repetitions(self, count =1, incr_mode = EV_auto, 
            reset_mode = EV_none):
        self.repetitions = {'count': count,
                'incr_mode': incr_mode,
                'reset_mode': reset_mode}

    def add_section(self, name = 'default', event_type = EV_stop, duration = 1,
            offset = 0, binsize = 11, mode = time_axis, threshold_min = 0,
            threshold_max = 999, threshold_mode = thres_dont_use,
            reset_mode = EV_none):

        section = {'name': name,
                'event_type': event_type,
                'binsize': binsize,
                'offset': offset,
                'duration': duration,
                'mode': mode,
                'threshold_min': threshold_min,
                'threshold_max': threshold_max,
                'threshold_mode': threshold_mode,
                'reset_mode': reset_mode,
                'ROI_list': []}
        
        self.sections.append(section)

    def add_ROI(self,ROI_name = 'default', section_name = 'default', start_index = 0, 
            length = 1, axis = time_axis):
        ROI = {'name': ROI_name,
                'axis': axis,
                'start_index': start_index,
                'length': length}
        for a in arange(0,len(self.sections)):
            if self.sections[a]['name'] == section_name:
                self.sections[a]['ROI_list'].append(ROI)

    def add_MW(self, name, instr, frequency = 2.878E9, power = 0, pulse_modulation = 'on', iq_modulation = 'off', sweep = 'off', 
            sweep_start_frequency = 2.86E9, sweep_stop_frequency = 3e9, sweep_step = 1e6):
        MW = {'name': name,
              'instr': instr,
              'frequency':frequency,
              'power':power,
              'pulse_modulation':pulse_modulation,
              'iq_modulation':iq_modulation,
              'sweep':sweep,
              'sweep_start_frequency':sweep_start_frequency,
              'sweep_stop_frequency':sweep_stop_frequency,
              'sweep_step':sweep_step}
        self.MW.append(MW)

    def add_ADwin_code(self, name, filename, process_nr, par_list = [], fpar_list = [], stop_processes_before_measurement = [], 
            start_processes_after_measurement = []):
        ADwin_code = {'name': name,
                'filename': filename, 
                'process_nr': process_nr,
                'par_list': par_list,
                'fpar_list': fpar_list,
                'stop_processes_before_measurement': stop_processes_before_measurement,
                'start_processes_after_measurement': start_processes_after_measurement}
        self.ADwin_codes.append(ADwin_code)

    def add_ADwin_save_par(self, name, par_nr):
        save_par = {'name': name, 
                'par': par_nr, 
                'fpar': -1}
        self.ADwin_save_parameters.append(save_par)

    def add_special_save_par(self, name):
        save_par = {'name': name}
        self.special_save_parameters.append(save_par)

    def add_ADwin_save_fpar(self, name, fpar_nr):
        save_par = {'name': name, 
                'par': -1, 
                'fpar': fpar_nr}
        self.ADwin_save_parameters.append(save_par)

    def initialize(self):
        
        self.sequence_instr.start() #starting and stopping the AWG before the 
                                    #real measurement initializes the sequence 
                                    #and saves time for the next start
        while (self.sequence_instr.get_state() != 'Running') and (self.sequence_instr.get_state() != 'Waiting for trigger'):
            sleep(0.01) 
        self.sequence_instr.stop()
        self.qtlab_counter_instr.start_T2_mode()
#        print self.qtlab_counter_instr.get_DeviceType()
        if self.qtlab_counter_instr.get_DeviceType() == 'HH_400':
            self.qtlab_counter_instr.calibrate()
            self.qtlab_counter_instr.set_Binning(0)
#            self.qtlab_counter_instr.set_Binning(10)
            self.base_resolution = self.qtlab_counter_instr.get_BaseResolutionPS()
        else:
            self.base_resolution = self.qtlab_counter_instr.get_BaseResolutionPS() 
        self.counter_instr.clear_sections()
        for a in arange(0,len(self.sections)):
            if self.sections[a]['mode'] & time_axis:
                x = self.sections[a]['duration']
            else:
                x = 1
            if self.sections[a]['mode'] & sweep_axis:
                y = self.sweep['count']
            else:
                y = 1
            if self.sections[a]['mode'] & repetition_axis:
                z = self.repetitions['count']
            else:
                z = 1
            data = zeros(x*y*z,dtype = uint32)
            self.data.append(data)
            self.counter_instr.add_section(self.sections[a]['event_type'],
                    self.sections[a]['binsize'],
                    self.sections[a]['offset'],
                    self.sections[a]['duration'],
                    self.sections[a]['mode'],
                    self.sections[a]['threshold_min'],
                    self.sections[a]['threshold_max'],
                    self.sections[a]['threshold_mode'],
                    self.sections[a]['reset_mode'],
                    self.data[a].ctypes.data
                    )
            print ('added data section of dimension %s * %s * %s, duration %s, offset %s, binsize %s'%(x,y,z, self.sections[a]['duration'],self.sections[a]['offset'],self.sections[a]['binsize']))
        self.counter_instr.set_abort_condition(self.abort_condition)
        for a in arange(0,len(self.MW)):
            self.MW[a]['instr'].set_status('off')
            self.MW[a]['instr'].set_power(self.MW[a]['power'])
            self.MW[a]['instr'].set_pulm(self.MW[a]['pulse_modulation'])
            if self.MW[a]['iq_modulation'] != 'off':
                self.MW[a]['instr'].set_iq(self.MW[a]['iq_modulation'])
            if self.MW[a]['sweep'] == 'off':
                self.MW[a]['instr'].set_frequency(self.MW[a]['frequency'])
            else:
                self.MW[a]['instr'].enable_ext_freq_sweep_mode()
                self.MW[a]['instr'].set_sweep_frequency_start(self.MW[a]['sweep_start_frequency'])
                self.MW[a]['instr'].set_sweep_frequency_stop(self.MW[a]['sweep_stop_frequency'])
                self.MW[a]['instr'].set_sweep_frequency_step(self.MW[a]['sweep_step'])
                self.MW[a]['instr'].reset_sweep()
        for a in arange(0,len(self.ADwin_codes)):
            for b in arange(0,len(self.ADwin_codes[a]['stop_processes_before_measurement'])):
                ADwin.Stop_Process(self.ADwin_codes[a]['stop_processes_before_measurement'][b])
            for b in arange(0,len(self.ADwin_codes[a]['par_list'])):
                ADwin.Set_Par(self.ADwin_codes[a]['par_list'][b][0],self.ADwin_codes[a]['par_list'][b][1])
            for b in arange(0,len(self.ADwin_codes[a]['fpar_list'])):
                ADwin.Set_FPar(self.ADwin_codes[a]['fpar_list'][b][0],self.ADwin_codes[a]['fpar_list'][b][1])
            ADwin.Stop_Process(self.ADwin_codes[a]['process_nr'])
            time.sleep(.2)
            print 'Loading ADwin processes'
            print self.ADwin_codes[a]['filename']
            ADwin.Load(self.ADwin_codes[a]['filename'])

        self.statistics = zeros(14 + len(self.sections),dtype = uint32)
#        self.statistics = zeros(100,dtype = uint32)

        self.statistics_desc = {
                0 : 'start events',
                1 : 'stop events',
                2 : 'sync events',
                3 : 'MA1 events',
                4 : 'MA2 events',
                5 : 'MA3 events', 
                6 : 'MA4 events',
                7 : 'OFL events',
                8 : 'Measurement time [ms]', 
                9 : 'sweep counter',
                10 : 'repetition counter',
                11 : 'detected events',
                12 : 'valid events',
                13 : 'invalid events',
                }
        
        for i,s in enumerate(self.sections):
            self.statistics_desc[14 + i] = 'valid %s sections' % s['name']

    def start(self,max_time = 30000000):
        for a in arange(0,len(self.MW)):
            self.MW[a]['instr'].set_status('on')
        
        print 'MWs on (if necessary)'

        self.counter_instr.start(max_time)

        print 'counter started'

        self.sequence_instr.start()


        for a in arange(0,len(self.ADwin_codes)):
            ADwin.Start_Process(self.ADwin_codes[a]['process_nr'])            
            
            print 'Adwin process %d started ' % self.ADwin_codes[a]['process_nr']
        
        
        # FIXME still need to check whether AWG is running!!!
        #while self.sequence_instr.get_state() != 'Running':
        #    sleep(0)

        print 'everything ready, start data acquisition'

        if self.conditional_mode == True:    
            self.counter_instr.TTTR2_universal_measurement(
                    c_int(self.sweep['count']),
                    c_int(self.repetitions['count']),
                    c_int(self.sweep['incr_mode']),
                    c_int(self.sweep['reset_mode']),
                    c_int(self.repetitions['incr_mode']),
                    c_int(self.repetitions['reset_mode']),
                    c_int(self.sec_incr_ev),
                    c_int(self.seq_res_ev),
                    c_int(self.loop_order),
                    self.statistics.ctypes.data)
        else:
            self.counter_instr.TTTR2_universal_measurement_speedmode_unconditional(
                    c_int(self.sweep['count']),
                    c_int(self.repetitions['count']),
                    c_int(self.sweep['incr_mode']),
                    c_int(self.sweep['reset_mode']),
                    c_int(self.repetitions['incr_mode']),
                    c_int(self.repetitions['reset_mode']),
                    c_int(self.sec_incr_ev),
                    c_int(self.seq_res_ev),
                    c_int(self.loop_order),
                    self.statistics.ctypes.data)
        for a in arange(0,len(self.MW)):
            self.MW[a]['instr'].set_status('off')
            if self.MW[a]['iq_modulation'] != 'off':
                self.MW[a]['instr'].set_iq('off')
            self.MW[a]['instr'].set_pulm('off')
        self.sequence_instr.stop()
        for a in arange(0,len(self.ADwin_codes)):
            for b in arange(0,len(self.ADwin_codes[a]['start_processes_after_measurement'])):
                ADwin.Start_Process(self.ADwin_codes[a]['start_processes_after_measurement'][b])

    def analyze(self, **kw):
        measurement.Measurement.analyze(self)

    
    def save(self, **kw):
        measurement.Measurement.save(self)

        i = len(self.sections)
        for j, s in enumerate(self.sections):
            if j == i:
                kw['idx_increment'] = True
            else:
                kw['idx_increment'] = False

            self.save_section(s['name'], **kw)
    
    def save_section(self, section, do_plot=True, **kw):

        figs = {}
        
        stat_str = ''
        for i,s in enumerate(self.statistics):
            stat_str += '# %s: %s\n' % (self.statistics_desc[i], s)
      
        for k in arange(0,len(self.ADwin_save_parameters)):
            if self.ADwin_save_parameters[k]['par'] == -1:
                stat_str += '# %s: %s\n'%(self.ADwin_save_parameters[k]['name'],ADwin.Get_FPar(self.ADwin_save_parameters[k]['fpar']))
            else:
                stat_str += ('# %s: %s\n'%(self.ADwin_save_parameters[k]['name'],ADwin.Get_Par(self.ADwin_save_parameters[k]['par'])))
        
        for k in arange(0,len(self.special_save_parameters)):
            if self.special_save_parameters[k]['name'] == 'avg. counts per repump':
                stat_str += ('# %s: %.3f\n'%(self.special_save_parameters[k]['name'], float(ADwin.Get_Par(77))/ADwin.Get_Par(70)))
            if self.special_save_parameters[k]['name'] == 'avg. sequences before ADwin CR fails':
                stat_str += ('# %s: %.3f\n'%(self.special_save_parameters[k]['name'], float(ADwin.Get_Par(72))/ADwin.Get_Par(71)))
            if self.special_save_parameters[k]['name'] == 'avg. repump attempts per failed ADwin CR':
               stat_str += ('# %s: %.3f\n'%(self.special_save_parameters[k]['name'], float(ADwin.Get_Par(70))/ADwin.Get_Par(71)))

        sec = None
        sec_name = ''
        sw_name = self.sweep['name']
        swname = sw_name
        for i,s in enumerate(self.sections):
            if s['name'] == section:
                sec = s
                sec_name = s['name']
                k = i
        if sec == None:
            print 'invalid section given for saving'
            return False

        self.savdat[section] = {}
        bin2time = (self.base_resolution * 0.001*2**sec['binsize'])
        
        if bool((sec['mode'] & (sweep_axis + time_axis + repetition_axis)) == sweep_axis):
            self.savdat[section][swname] = (arange(0,self.sweep['count'])*self.sweep['incr']+self.sweep['start'])
            self.savdat[section]['counts'] = self.data[k]
        
        if bool((sec['mode'] & (sweep_axis + time_axis + repetition_axis)) == time_axis):
            self.savdat[section]['time'] = arange(sec['offset'], sec['duration']+sec['offset']) * bin2time
            self.savdat[section]['counts'] = self.data[k]
        
        if bool((sec['mode'] & (sweep_axis + time_axis + repetition_axis)) == repetition_axis):
            self.savdat[section]['repetitions'] = arange(self.repetitions['count'])
            self.savdat[section]['counts'] = self.data[k]
        
        if bool((sec['mode'] & (sweep_axis + time_axis + repetition_axis)) == sweep_axis+time_axis):
            self.savdat[section][swname] = (arange(0,self.sweep['count'])*self.sweep['incr']+self.sweep['start'])
            self.savdat[section]['time'] = (arange(sec['offset'], sec['duration']+sec['offset']) * bin2time)
            self.savdat[section]['counts'] = zeros((self.sweep['count'], sec['duration']), dtype = int)

            for i in arange(self.sweep['count']):
                for j in arange(sec['duration']):
                    self.savdat[section]['counts'][i,j] = self.data[k][sec['duration']*i+j]

            for i,roi in enumerate(sec['ROI_list']):
                roiname = roi['name']
                
                if roi['axis'] == time_axis:
                    self.savdat[section][roiname] = zeros(self.sweep['count'], dtype = int)
                    
                    for j in arange(self.sweep['count']):
                        counts = 0
                        for l in arange(roi['start_index'],roi['start_index']+roi['length']):
                            counts += self.data[k][sec['duration']*j+l]
                        self.savdat[section][roiname][j] = counts

                    if do_plot:
                        fig = plt.figure()
                        ax = plt.subplot(111)
                        ax.plot(self.savdat[section][swname], 
                                self.savdat[section][roiname], 'o')
                        plt.xlabel(swname)
                        plt.ylabel('counts')
                        figs['%s_vs_%s' % (roiname, swname)] = fig                    

                elif roi['axis'] == sweep_axis:
                    self.savdat[section][roiname] = zeros(sec['duration'], dtype = int)

                    for j in arange(sec['duration']):
                        counts = 0
                        for l in arange(roi['start_index'],roi['start_index']+roi['length']):
                            counts += self.data[k][sec['duration']*l+j]
                        self.savdat[section][roiname][j] = counts

                    if do_plot:
                        fig = plt.figure()
                        ax = plt.subplot(111)
                        ax.plot(self.savdat[section]['time'], 
                                self.savdat[section][roiname], 'o')
                        plt.xlabel(swname)
                        plt.ylabel('counts')
                        figs['%s_vs_%s' % (roiname, 'time')] = fig

        if bool((sec['mode'] & (sweep_axis + time_axis + repetition_axis)) == sweep_axis+repetition_axis):
            self.savdat[section][swname] = (arange(0,self.sweep['count'])*self.sweep['incr']+self.sweep['start'])
            self.savdat[section]['repetitions'] = arange(self.repetitions['count'])
            self.savdat[section]['counts'] = zeros((self.sweep['count'],self.repetitions['count']), dtype = int)
            for i in arange(0,self.sweep['count']):
                for j in arange(0,self.repetitions['count']):
                    self.savdat[section]['counts'][i,j] = self.data[k][self.sweep['count']*j+i]

            for i,roi in enumerate(sec['ROI_list']):
                roiname = roi['name']

                if roi['axis'] == repetition_axis:
                    self.savdat[section][roiname] = zeros(self.sweep['count'], dtype = int)

                    for i in arange(0,self.sweep['count']):
                        counts = 0
                        for j in arange(roi['start_index'],roi['start_index']+roi['length']):
                            counts += self.data[k][self.sweep['count']*j+i]
                        self.savdat[section][roiname][i] = counts

                if roi['axis'] == sweep_axis:
                    self.savdat[section][roiname] = zeros(self.repetitions['count'], dtype = int)

                    for j in arange(0,self.repetitions['count']):
                        counts = 0
                        for i in arange(0,roi['start_index'],roi['start_index']+roi['length']):
                            counts += self.data[k][self.sweep['count']*j+i]
                        self.savdat[section][roiname][j] = counts

        
        if bool((sec['mode'] & (sweep_axis + time_axis + repetition_axis)) == time_axis+repetition_axis):
            self.savdat[section]['repetitions'] = arange(self.repetitions['count'])
            self.savdat[section]['time'] = arange(sec['offset'], sec['duration']+sec['offset']) * bin2time
            self.savdat[section]['counts'] = zeros((self.sections[k]['duration'],self.repetitions['count']), dtype = int)
            for i in arange(0,self.sections[k]['duration']):
                for j in arange(0,self.repetitions['count']):
                    self.savdat[section]['counts'][i,j] = self.data[k][sec['duration']*j+i]

            
            # FIXME check how we walk through the data; guess there's a bug...
            for i,roi in enumerate(sec['ROI_list']):
                roiname = roi['name']

                if roi['axis'] == repetition_axis:
                    self.savdat[section][roiname] = zeros(self.sec['duration'], dtype = int)

                    for i in arange(0,sec['duration']):
                        counts = 0
                        for j in arange(0,roi['start_index'],roi['start_index']+roi['length']):
                            counts += self.data[k][self.sweep['count']*j+i]
                        self.savdat[section][roiname][i] = counts

                if roi['axis'] == time_axis:
                    self.savdat[section][roiname] = zeros(self.repetitions['count'], dtype = int)

                    for j in arange(0,self.repetitions['count']):
                        counts = 0
                        for i in arange(roi['start_index'],roi['start_index']+roi['length']):
                            counts += self.data[k][sec['duration']*j+i]
                        self.savdat[section][roiname][j] = counts
        
        sectiondat = self.savdat[section]
        if 'idx_increment' not in kw:
            kw['idx_increment'] = False

        self.save_dataset(name=section, do_plot=False, 
                txt={'statistics': stat_str }, data=sectiondat, **kw)

        print ('saved dataset %s:'%(section))
        for k in sectiondat.keys():
            print ('    array %s of dimension %s'%(k,shape(sectiondat[k])))


        for fn in figs:
            figs[fn].savefig(self.data_basepath + '_%s.png' % fn)

        return True

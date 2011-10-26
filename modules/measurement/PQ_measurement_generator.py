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
from ctypes import *
from time import sleep
import qt, os
import time
import matplotlib.pyplot as plt

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
e#####################################
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

class PQ_measurement: 
    def __init__(self, name):
        self.name = name
        self.sections = []
        self.data = []
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

        self.path = qt.config['datadir'] + '\\'+time.strftime('%Y%m%d') + '\\' + time.strftime('%H%M%S', time.localtime()) + '_sequence\\'
#        self.path = save_path

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

    def set_sequence_instrument(self, instrument):
        self.sequence_instr = instrument

    def set_sequence(self, sequence):
        self.sequence = sequence

    def set_sweep(self, name = 'none', count = 1, incr_mode = EV_auto, reset_mode = EV_none, incr = 1, start = 0):
        self.sweep = {'name': name, 
                'count': count,
                'start': start,
                'incr':  incr,
                'incr_mode': incr_mode,
                'reset_mode': reset_mode}

    def set_repetitions(self, count =1, incr_mode = EV_auto, reset_mode = EV_none):
        self.repetitions = {'count': count,
                'incr_mode': incr_mode,
                'reset_mode': reset_mode}

    def add_section(self, name = 'default', event_type = EV_stop, duration = 1, \
            offset = 0, binsize = 11, mode = time_axis, threshold_min = 0, \
            threshold_max = 999, threshold_mode = thres_dont_use, \
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
        self.sequence_instr.start()
        while (self.sequence_instr.get_state() != 'Running') and (self.sequence_instr.get_state() != 'Waiting for trigger'):
            sleep(0.01)
        self.sequence_instr.stop()
        self.qtlab_counter_instr.start_T2_mode()
        if self.qtlab_counter_instr.get_DeviceType() == 'HH_400':
            self.qtlab_counter_instr.calibrate()
            self.qtlab_counter_instr.set_Binning(10)
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
            ADwin.Load(self.ADwin_codes[a]['filename'])

        self.statistics = zeros(14 + len(self.sections),dtype = uint32)
#        self.statistics = zeros(100,dtype = uint32)


    def start(self,max_time = 30000000):
        for a in arange(0,len(self.MW)):
            self.MW[a]['instr'].set_status('on')
        self.counter_instr.start(max_time)
        self.sequence_instr.start()
        for a in arange(0,len(self.ADwin_codes)):
            ADwin.Start_Process(self.ADwin_codes[a]['process_nr'])            
        while self.sequence_instr.get_state() != 'Running':
            sleep(0)
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

    def save_data(self, section, saveplot = True):
        path = self.path
        if not os.path.isdir(path):
            os.makedirs(path)
        
        filename = path+self.name+'_statistics'
        result=open(filename+'.dat', 'w')
        result.write('# start events: %s\n'%self.statistics[0])
        result.write('# stop events: %s\n'%self.statistics[1])
        result.write('# sync events: %s\n'%self.statistics[2])
        result.write('# MA1 events: %s\n'%self.statistics[3])
        result.write('# MA2 events: %s\n'%self.statistics[4])
        result.write('# MA3 events: %s\n'%self.statistics[5])
        result.write('# MA4 events: %s\n'%self.statistics[6])
        result.write('# OFL events: %s\n'%self.statistics[7])
        result.write('# measurement time: %s ms\n'%self.statistics[8])
        result.write('# sweep counter: %s\n'%self.statistics[9])
        result.write('# repetition counter: %s\n'%self.statistics[10])
        result.write('# detected events: %s\n'%self.statistics[11])
        result.write('# valid events: %s\n'%self.statistics[12])
        result.write('# invalid events: %s\n'%self.statistics[13])
        for k in arange(0,len(self.sections)):
            result.write('# valid %s sections: %s\n'%(self.sections[k]['name'],self.statistics[14+k]))
        for k in arange(0,len(self.ADwin_save_parameters)):
            if self.ADwin_save_parameters[k]['par'] == -1:
                result.write('# %s: %s\n'%(self.ADwin_save_parameters[k]['name'],ADwin.Get_FPar(self.ADwin_save_parameters[k]['fpar'])))
            else:
                result.write('# %s: %s\n'%(self.ADwin_save_parameters[k]['name'],ADwin.Get_Par(self.ADwin_save_parameters[k]['par'])))
        for k in arange(0,len(self.special_save_parameters)):
            if self.special_save_parameters[k]['name'] == 'avg. counts per repump':
                result.write('# %s: %.3f\n'%(self.special_save_parameters[k]['name'], float(ADwin.Get_Par(77))/ADwin.Get_Par(70)))
            if self.special_save_parameters[k]['name'] == 'avg. sequences before ADwin CR fails':
                result.write('# %s: %.3f\n'%(self.special_save_parameters[k]['name'], float(ADwin.Get_Par(72))/ADwin.Get_Par(71)))
            if self.special_save_parameters[k]['name'] == 'avg. repump attempts per failed ADwin CR':
                result.write('# %s: %.3f\n'%(self.special_save_parameters[k]['name'], float(ADwin.Get_Par(70))/ADwin.Get_Par(71)))
        result.close()

        for k in arange(0,len(self.sections)):
            if self.sections[k]['name'] == section:
                if self.sections[k]['mode'] == sweep_axis:
                    filename = path+self.name+'_'+self.sections[k]['name']+'_vs_'+self.sweep['name']
                    result=open(filename+'.dat', 'w')
                    result.write('# measurement name: %s\n'%self.name)
                    result.write('# section name: %s\n'%section)
                    result.write('# section type: sweep-axis\n')
                    result.write('# sweep name: %s\n'%self.sweep['name'])
                    result.write('# 1st column: sweep parameter\n')
                    result.write('# 2st column: counts\n')
                    result.write('#\n')

                    for i in arange(0,self.sweep['count']):
                        result.write('%s\t%s\n'%(self.sweep['start']+i*self.sweep['incr'], self.data[k][i]))
                    result.close()

                    if saveplot == True:
                        fig = plt.figure()
                        dat = fig.add_subplot(111)
                        x = arange(0,self.sweep['count'])*self.sweep['incr']+self.sweep['start']
                        y = self.data[k]
                        dat = dat.plot(x,y,'r.')
                        plt.xlabel(self.sweep['name'])
                        plt.ylabel('counts')
                        plt.title(section)
                        fig.savefig(filename+'.png')

                if self.sections[k]['mode'] == time_axis:
                    filename = path+self.name+'_'+self.sections[k]['name']+'_vs_time'
                    result=open(filename + '.dat', 'w')
                    result.write('# measurement name: %s\n'%self.name)
                    result.write('# section name: %s\n'%section)
                    result.write('# section type: time-axis\n')
                    result.write('# 1st column: time (ns)\n')
                    result.write('# 2st column: counts\n')
                    result.write('#\n')
                    for i in arange(0,self.sections[k]['duration']):
                        result.write('%.1f\t%s\n'%(0.004*2**self.sections[k]['binsize']*(self.sections[k]['offset']+i), self.data[k][i]))
                    result.close()

                    if saveplot == True:
                        fig = plt.figure()
                        dat = fig.add_subplot(111)
                        x = (arange(0,self.sections[k]['duration'])+self.sections[k]['offset'])*0.004*2**self.sections[k]['binsize']
                        y = self.data[k]
                        dat = dat.plot(x,y,'r.')
                        plt.xlabel('time (ns)')
                        plt.ylabel('counts')
                        plt.title(section)
                        fig.savefig(filename+'.png')

                if self.sections[k]['mode'] == repetition_axis:
                    filename = path+self.name+'_'+self.sections[k]['name']+'_vs_repetition'
                    result=open(filename + '.dat', 'w')
                    result.write('# measurement name: %s\n'%self.name)
                    result.write('# section name: %s\n'%section)
                    result.write('# section type: repetition-axis\n')
                    result.write('# 1st column: repetition\n')
                    result.write('# 2st column: counts\n')
                    result.write('#\n')
                    for i in arange(0,self.repetitions['count']):
                        result.write('%s\t%s\n'%(i, self.data[k][i]))
                    result.close()

                    if saveplot == True:
                        fig = plt.figure()
                        dat = fig.add_subplot(111)
                        x = (arange(0,self.repetitions['count'])+1)
                        y = self.data[k]
                        dat = dat.plot(x,y,'r.')
                        plt.xlabel('repetiton')
                        plt.ylabel('counts')
                        plt.title(section)
                        fig.savefig(filename+'.png')

                if self.sections[k]['mode'] == sweep_axis+time_axis:
                    filename = path+self.name+'_'+self.sections[k]['name']+'_vs_'+self.sweep['name']+'_vs_time'
                    result=open(filename + '.dat', 'w')
                    result.write('# measurement name: %s\n'%self.name)
                    result.write('# section name: %s\n'%section)
                    result.write('# section type: sweep vs time\n')
                    result.write('# sweep name: %s\n'%self.sweep['name'])
                    result.write('#\n')
                    result.write('# columns: %s\n'%self.sections[k]['duration'])
                    result.write('# bin size: %s\n'%(0.004*2**self.sections[k]['binsize']))
                    result.write('# 1st column: %s ns\n'%(0.004*2**self.sections[k]['binsize']*(self.sections[k]['offset'])))
                    result.write('# last column: %s ns\n'%(0.004*2**self.sections[k]['binsize']*(self.sections[k]['offset']\
                            +self.sections[k]['duration']-1)))
                    result.write('#\n')
                    result.write('# rows: %s \n'%self.sweep['count'])
                    result.write('# sweep step size: %s\n'%self.sweep['incr'])
                    result.write('# 1st row: %s\n'%self.sweep['start'])
                    result.write('# last row: %s\n'%(self.sweep['start']+self.sweep['incr']*(self.sweep['count']-1)))
                    result.write('#\n')
                    for i in arange(0,self.sweep['count']):
                        result.write('%s'%(self.data[k][self.sections[k]['duration']*i]))
                        for j in arange(1,self.sections[k]['duration']):
                            result.write('\t%s'%(self.data[k][self.sections[k]['duration']*i+j]))
                        result.write('\n')
                    result.close()
                            
                    data2D = zeros((self.sweep['count'],self.sections[k]['duration']), dtype = int)
                    for i in arange(0,self.sweep['count']):
                        for j in arange(0,self.sections[k]['duration']):
                            data2D[i,j] = self.data[k][self.sections[k]['duration']*i+j]
                    x = (arange(0,self.sections[k]['duration']+1)+self.sections[k]['offset'])*0.004*2**self.sections[k]['binsize']
                    y = arange(0,self.sweep['count']+1)*self.sweep['incr']+self.sweep['start']
                    if saveplot == True:
                        fig = plt.figure()
                        dat = fig.add_subplot(111)
                        dat = dat.pcolor(x,y,data2D,cmap = 'hot')
                        plt.xlabel('time (ns)')
                        plt.ylabel(self.sweep['name'])
                        plt.title(self.name+' - '+section)
                        fig.savefig(filename+'.png')
                    for l in arange(0,len(self.sections[k]['ROI_list'])):
                        ROI = self.sections[k]['ROI_list'][l]
                        if ROI['axis'] == time_axis:
                            data1D =  zeros(self.sweep['count'], dtype = int)
                            filename = path+self.name+'_'+self.sections[k]['name']+'_vs_'+self.sweep['name']+'_ROI_'+ROI['name']
                            result=open(filename+'.dat', 'w')
                            result.write('# measurement name: %s\n'%self.name)
                            result.write('# section name: %s\n'%section)
                            result.write('# section type: sweep vs time\n')
                            result.write('# sweep name: %s\n'%self.sweep['name'])
                            result.write('#\n')
                            result.write('# ROI name: %s\n'%ROI['name'])
                            result.write('# ROI type: time-axis\n')
                            result.write('# ROI start: %s ns\n'%(0.004*2**self.sections[k]['binsize']*(self.sections[k]['offset']\
                                    +ROI['start_index'])))
                            result.write('# ROI end: %s ns\n'%(0.004*2**self.sections[k]['binsize']*(self.sections[k]['offset']\
                                    +ROI['start_index']+ROI['length']-1)))
                            result.write('#\n')
                            result.write('# rows: %s \n'%self.sweep['count'])
                            result.write('# sweep step size: %s\n'%self.sweep['incr'])
                            result.write('# 1st row: %s\n'%self.sweep['start'])
                            result.write('# last row: %s\n'%(self.sweep['start']+self.sweep['incr']*(self.sweep['count']-1)))
                            result.write('#\n')
                            for i in arange(0,self.sweep['count']):
                                counts = 0
                                for j in arange(ROI['start_index'],ROI['start_index']+ROI['length']):
                                    counts += self.data[k][self.sections[k]['duration']*i+j]
                                data1D[i] = counts
                                result.write('%s\t%s\n'%(i*self.sweep['incr']+self.sweep['start'],counts))
                            result.close()
                            if saveplot == True:
                                plt.clf()
                                fig = plt.figure()
                                dat = fig.add_subplot(111)
                                x = arange(0,self.sweep['count'])*self.sweep['incr']+self.sweep['start']
                                dat = dat.plot(x,data1D,'r.')
                                plt.xlabel(self.sweep['name'])
                                plt.ylabel('counts')
                                plt.title(section)
                                fig.savefig(filename+'.png')
                        if ROI['axis'] == sweep_axis:
                            data1D =  zeros(self.sections[k]['duration'], dtype = int)
                            filename = path+self.name+'_'+self.sections[k]['name']+'_vs_time_ROI_'+ROI['name']
                            result=open(filename+'.dat', 'w')
                            for j in arange(0,self.sections[k]['duration']):
                                counts = 0
                                for i in arange(ROI['start_index'],ROI['start_index']+ROI['length']):
                                    counts += self.data[k][self.sections[k]['duration']*i+j]
                                data1D[j] = counts
                                result.write('%s\n'%counts)
                            result.close()
                            if saveplot == True:
                                plt.clf()
                                fig = plt.figure()
                                dat = fig.add_subplot(111)
                                x = (arange(0,self.sections[k]['duration'])+self.sections[k]['offset'])*0.004*2**self.sections[k]['binsize']
                                dat = dat.plot(x,data1D,'r.')
                                plt.xlabel('time (ns)')
                                plt.ylabel('counts')
                                plt.title(section)
                                fig.savefig(filename+'.png')

                if self.sections[k]['mode'] == sweep_axis+repetition_axis:
                    filename = path+self.name+'_'+self.sections[k]['name']+'_vs_'+self.sweep['name']+'_vs_repetition'
                    result=open(filename+'.dat', 'w')
                    result.write('# measurement name: %s\n'%self.name)
                    result.write('# section name: %s\n'%section)
                    result.write('# section type: sweep vs repetitions\n')
                    result.write('# sweep name: %s\n'%self.sweep['name'])
                    result.write('#\n')
                    result.write('# columns: %s\n'%self.repetitions['count'])
                    result.write('#\n')
                    result.write('# rows: %s \n'%self.sweep['count'])
                    result.write('# sweep step size: %s\n'%self.sweep['incr'])
                    result.write('# 1st row: %s\n'%self.sweep['start'])
                    result.write('# last row: %s\n'%(self.sweep['start']+self.sweep['incr']*(self.sweep['count']-1)))
                    result.write('#\n')
                    for i in arange(0,self.sweep['count']):
                        result.write('%s'%(self.data[k][i]))
                        for j in arange(1,self.repetitions['count']):
                            result.write('\t%s'%(self.data[k][self.sweep['count']*j+i]))
                        result.write('\n')
                    result.close()
                    data2D = zeros((self.sweep['count'],self.repetitions['count']), dtype = int)
                    for i in arange(0,self.sweep['count']):
                        for j in arange(0,self.repetitions['count']):
                            data2D[i,j] = self.data[k][self.sweep['count']*j+i]
                    x = arange(0,self.repetitions['count']+1)
                    y = arange(0,self.sweep['count']+1)*self.sweep['incr']+self.sweep['start']
                    if saveplot == True:
                        fig = plt.figure()
                        dat = fig.add_subplot(111)
                        dat = dat.pcolor(x,y,data2D,cmap = 'hot')
                        plt.xlabel('repetition')
                        plt.ylabel(self.sweep['name'])
                        plt.title(self.name+' - '+section)
                        fig.savefig(filename+'.png')

                    for l in arange(0,len(self.sections[k]['ROI_list'])):
                        ROI = self.sections[k]['ROI_list'][l]
                        if ROI['axis'] == repetition_axis:
                            filename = path+self.name+'_'+self.sections[k]['name']+'_vs_'+self.sweep['name']+'_ROI_'+ROI['name']
                            result=open(filename+'.dat', 'w')
                            for i in arange(0,self.sweep['count']):
                                counts = 0
                                for j in arange(ROI['start_index'],ROI['start_index']+ROI['length']):
                                    counts += self.data[k][self.sweep['count']*j+i]
                                result.write('%s\n'%counts)
                            result.close()
                        if ROI['axis'] == sweep_axis:
                            filename = path+self.name+'_'+self.sections[k]['name']+'_vs_repetitions_ROI_'+ROI['name']
                            result=open(filename+'.dat', 'w')
                            for j in arange(0,self.repetitions['count']):
                                counts = 0
                                for i in arange(0,ROI['start_index'],ROI['start_index']+ROI['length']):
                                    counts += self.data[k][self.sweep['count']*j+i]
                                result.write('%s\n'%counts)
                            result.close()

                if self.sections[k]['mode'] == time_axis+repetition_axis:
                    filename = path+self.name+'_'+self.sections[k]['name']+'_vs_time_vs_repetition'
                    result=open(filename+'.dat', 'w')
                    result.write('# measurement name: %s\n'%self.name)
                    result.write('# section name: %s\n'%section)
                    result.write('# section type: time vs repetition\n')
                    result.write('#\n')
                    result.write('# columns: %s\n'%self.repetitions['count'])
                    result.write('#\n')
                    result.write('# rows: %s\n'%self.sections[k]['duration'])
                    result.write('# bin size: %s\n'%(0.004*2**self.sections[k]['binsize']))
                    result.write('# 1st row: %s ns\n'%(0.004*2**self.sections[k]['binsize']*(self.sections[k]['offset'])))
                    result.write('# last row: %s ns\n'%(0.004*2**self.sections[k]['binsize']*(self.sections[k]['offset']\
                            +self.sections[k]['duration']-1)))
                    result.write('#\n')
                    for i in arange(0,self.sections[k]['duration']):
                        result.write('%s'%(self.data[k][i]))
                        for j in arange(1,self.repetitions['count']):
                            result.write('\t%s'%(self.data[k][self.sections[k]['duration']*j+i]))
                        result.write('\n')
                    result.close()

                    data2D = zeros((self.sections[k]['duration'],self.repetitions['count']), dtype = int)
                    for i in arange(0,self.sections[k]['duration']):
                        for j in arange(0,self.repetitions['count']):
                            data2D[i,j] = self.data[k][self.sections[k]['duration']*j+i]
                    x = arange(0,self.repetitions['count']+1)
                    y = (arange(0,self.sections[k]['duration']+1)+self.sections[k]['offset'])*0.004*2**self.sections[k]['binsize']
                    if saveplot == True:
                        fig = plt.figure()
                        dat = fig.add_subplot(111)
                        dat = dat.pcolor(x,y,data2D,cmap = 'hot')
                        plt.xlabel('repetition')
                        plt.ylabel('time (ns)')
                        plt.title(self.name+' - '+section)
                        fig.savefig(filename+'.png')

                    for l in arange(0,len(self.sections[k]['ROI_list'])):
                        ROI = self.sections[k]['ROI_list'][l]
                        if ROI['axis'] == repetition_axis:
                            filename + path+self.name+'_'+self.sections[k]['name']+'_vs_time_ROI_'+ROI['name']
                            result=open(filename+'.dat', 'w')
                            for j in arange(0,self.repetitions['count']):
                                counts = 0
                                for i in arange(ROI['start_index'],ROI['start_index']+ROI['length']):
                                    counts += self.data[k][self.sections[k]['duration']*j+i]
                                result.write('%s\n'%counts)
                            result.close()
                        if ROI['axis'] == time_axis:
                            filename = path+self.name+'_'+self.sections[k]['name']+'_vs_repetitions_ROI_'+ROI['name']
                            result=open(filename+'.dat', 'w')
                            for i in arange(0,self.sections[k]['duration']):
                                counts = 0
                                for j in arange(0,ROI['start_index'],ROI['start_index']+ROI['length']):
                                    counts += self.data[k][self.sweep['count']*j+i]
                                result.write('%s\n'%counts)
                            result.close()


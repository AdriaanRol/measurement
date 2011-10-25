from numpy import *
from time import sleep
import qt
import time
import matplotlib.pyplot as plt

# own modules
import tools

# save just implemented for 1D and 2D data
# ROI just implemented for 2D data

#####################################
#       events:
EV_none                =  0b00000000
EV_PH_start            =  0b00000001
EV_PH_stop             =  0b00000010
EV_MA_1                =  0b00000100
EV_MA_2                =  0b00001000
EV_MA_3                =  0b00010000
EV_auto                =  0b00100000
#####################################
#       section modes:
time_axis              =  0b00000001
sweep_axis             =  0b00000010
repetition_axis        =  0b00000100
#####################################
#       threshold modes:
thres_higher           =  0b00010000
thres_abort            =  0b00100000
thres_valid            =  0b01000000
thres_invalid          =  0b01100000
thres_and              =  0b10000000
thres_inactive         =  0b00000000
#####################################
#       loop modes:
loop_repeat_sweeps     =  0b00000000
loop_sweep_repetitions =  0b00000001

class PH_measurement: 
    def __init__(self, name, path=''):
        self.name = name
        self.sections = []
        self.data = []
        self.MW = []
        self.ADwin_codes = []
        self.ADwin_save_parameters = []
        self.special_save_parameters = []

        self.sweep = {'name': 'none', 
            'count': 1,
            'incr_mode': EV_auto,
            'reset_mode': EV_none}

        self.repetitions = {'count': 1,
            'incr_mode': EV_none,
            'reset_mode': EV_none}

        self.loop_order    = loop_repeat_sweeps
        self.sec_incr_ev   = EV_PH_start
        self.sec_res_ev    = EV_auto

#        self.path = qt.config['datadir'] + '\\'+time.strftime('%Y%m%d') + '\\' + time.strftime('%H%M%S', time.localtime()) + '_sequence\\'
        if path != '':
            self.path = path
        else:
            self.path = save_path
        if not os.path.isdir(self.path):
            os.makedirs(self.path)

        self.conditional_mode = True

    def set_conditional_mode(self, conditional_mode):
        self.conditional_mode = conditional_mode

    def set_loop_order(self, loop_order):
        self.loop_order = loop_order

    def set_section_increment_event(self, sec_incr_ev):
        self.sec_incr_ev = sec_incr_ev

    def set_section_reset_event(self, sec_res_ev):
        self.sec_res_ev = sec_res_ev

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

    def add_section(self, name = 'default', event_type = EV_PH_stop, duration = 1, \
            offset = 0, binsize = 11, mode = time_axis, threshold = 0, \
            threshold_mode = thres_inactive, reset_mode = EV_none):

        section = {'name': name,
                'event_type': event_type,
                'binsize': binsize,
                'offset': offset,
                'duration': duration,
                'mode': mode,
                'threshold': threshold,
                'threshold_mode': threshold_mode,
                'reset_mode': reset_mode,
                'ROI_list': []}
        self.sections.append(section)

    def add_ROI(self,ROI_name = 'default', section_name = 'default', start_index = 0, length = 1, axis = time_axis):
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
        while (self.sequence_instr.get_state() != 'Running') and \
                (self.sequence_instr.get_state() != 'Waiting for trigger'):
            sleep(0.01)
        self.sequence_instr.stop()
        self.qtlab_counter_instr.start_T2_mode()
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
            data = numpy.zeros(x*y*z,dtype = uint32)
            self.data.append(data)
            self.counter_instr.add_section(self.sections[a]['event_type'],
                    self.sections[a]['binsize'],
                    self.sections[a]['offset'],
                    self.sections[a]['duration'],
                    self.sections[a]['mode'],
                    self.sections[a]['threshold'],
                    self.sections[a]['threshold_mode'],
                    self.sections[a]['reset_mode'],
                    self.data[a].ctypes.data
                    )
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

        self.statistics = numpy.zeros(12 + len(self.sections),dtype = uint32)
        self.statistics_desc = {
                0 : 'start events',
                1 : 'stop events',
                2 : 'MA1 events',
                3 : 'MA2 events',
                4 : 'MA3 events', 
                5 : 'OFL events',
                6 : 'Measurement time [ms]', 
                7 : 'sweep counter',
                8 : 'repetition counter',
                9 : 'detected events',
                10 : 'valid events',
                11 : 'invalid events',
                }
        for i,s in enumerate(self.sections):
            self.statistics_desc[12 + i] = 'valid %s sections' % s['name']

    
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
                    c_int(self.sec_res_ev),
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
                    c_int(self.sec_res_ev),
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

    def save_data(self, section, saveplot = True, plotargs=[], plotkws={}):
        p = self.path        
        
        ###
        ### write the measurement statistics
        ###
        stat_str = ''
        for i,s in enumerate(self.statistics):
            stat_str += '# %s: %d\n' % (s, self.statistics_desc[i])
        fp = os.path.join(path, self.name + '_statistics.dat')
        f_res = open(fp, 'w')
        f_res.write(stat_str)

        # write ADwin params
        for i,param in self.ADwin_save_parameters:
            (name, func) = ('fpar', ADwin.Get_FPar) if param['par'] == -1 else ('par', ADwin.Get_Par)
            f_res.write('# %s: %s\n' % (param['name'], func(param[name])))

        result = f_res
        
        # write special save params
        for k in arange(0,len(self.special_save_parameters)):
            if self.special_save_parameters[k]['name'] == 'avg. counts per repump':
                result.write('# %s: %.3f\n'%(self.special_save_parameters[k]['name'], float(ADwin.Get_Par(77))/ADwin.Get_Par(70)))
            if self.special_save_parameters[k]['name'] == 'avg. sequences before ADwin CR fails':
                result.write('# %s: %.3f\n'%(self.special_save_parameters[k]['name'], float(ADwin.Get_Par(72))/ADwin.Get_Par(71)))
            if self.special_save_parameters[k]['name'] == 'avg. repump attempts per failed ADwin CR':
                result.write('# %s: %.3f\n'%(self.special_save_parameters[k]['name'], float(ADwin.Get_Par(70))/ADwin.Get_Par(71)))
        result.close()

        ### 
        ### end of writing measurement statistics
        ###
      
        ###
        ### find the right section
        ###
        sec = None
        sec_name = ''
        sw_name = self.sweep['name']

        for i,s in enumerate(self.sections):
            if s['name'] == section:
                sec = s
                sec_name = s['name']
                k = i
        if sec == None:
            print 'invalid section given for saving'
            return False
        
        ###
        ### end finding right section

        bin2time = (0.004*2**sec['binsize'])
        header = """
        # measurement name: %s
        # section name: %s
        # section type: %d
        """ % (self.name, section, sec['mode'])
        prefix = '%s_%s_vs_' % (self.name, section)

        def _save_sweep_axis():
            header += """
            # sweep name: %s 
            # 1st column: sweep param
            # 2nd column: counts
            """ % sw_name
            d = {}
            d['x__%s' % sw_name] = arange(0,self.sweep['count'])*self.sweep['incr']+self.sweep['start']
            d['y__counts'] = self.data[k]
            tools.save_npz_data(prefix+sw_name, filepath=path, meta=header, **d)

        def _save_time_axis():
            header += """
            # 1st column: time
            # 2nd column: counts
            """
            d = {}
            d['x__t__ns'] = arange(sec['offset'], sec['duration']+sec['offset']) * bin2time
            d['y__counts'] = self.data[k]
            tools.save_npz_data(prefix+'time', filepath=path, meta=header, **d)

        def _save_rep_axis():
            header += """
            # 1st column: repetition
            # 2nd column: counts
            """
            d = {}
            d['x__repetition'] = arange(self.repetitions['count'])
            d['y__counts'] = self.data[k]
            tools.save_npz_data(prefix+'repetitions', filepath=path, meta=header, **d)

        def _save_sweep_time_axes():
            header += """
            # sweep name: %s
            # columns: %d
            # bin size: %f
            # 1st column: %f
            # last column: %f
            #
            # rows: %d
            # sweep step size: %s
            # 1st row: %f
            # last row: %f
            """ % (sw_name, sec['duration'], bin2time, bin2time*sec['offset'], 
                    bin2time*(sec['offset']+sec['duration']-1]), self.sweep['count'], self.sweep['incr'],
                    self.sweep['start'], self.sweep['start']+self.sweep['incr']*(self.sweep['count']-1))
            d = {}
            d['x__time__ns'] = (arange(sec['duration']+1)+sec['offset'])*bin2time
            d['y__%s' % sw_name] = arange(self.sweep['count']+1)*self.sweep['incr']+self.sweep['start']
            d['z__counts'] = zeros((self.sweep['count'], sec['duration']), dtype = int)
            for i in arange(self.sweep['count']):
                for j in arange(sec['duration']):
                    d['z__counts'][i,j] = self.data[k][sec['duration']*i+j]
            
            tools.save_npz_data(prefix+'%s_vs_time' % sw_name, filepath=path, meta=header, **d)

            for i,roi in enumerate(sec['ROI_list']):
                roiheader = """
                # ROI name: %s
                # ROI type: %d
                """ % (roi['name'], roi['axis'])
                dr = {}
                
                if roi['axis'] == time_axis:
                    roiheader += """
                    # ROI start: %f ns
                    # ROI end: %f ns
                    # rows: %s
                    # sweep step size: %s
                    # 1st row: %s
                    # last row: %s
                    """ % (bin2time*sec['offset']+roi['start_index'],
                            bin2time*(sec['offset']+roi['start_index']+roi['length']-1),
                            self.sweep['count'], 
                            self.sweep['incr'], 
                            self.sweep['start'],                 
                            self.sweep['start']+self.sweep['incr']*(self.sweep['count']-1))

                    dr['x__%s' % sw_name] = arange(self.sweep['count'])*\
                            self.sweep['incr']+self.sweep['start']
                    dr['y__counts'] = zeros(self.sweep['count'], dtype = int)
                    
                    for j in arange(self.sweep['count']):
                        counts = 0
                        for l in arange(roi['start_index'],roi['start_index']+roi['length'])
                            counts += self.data[k][sec['duration']*j+l]
                        dr['y__counts'][j] = counts
                    
                    suffix = '%s_ROI_%s' % (sw_name, roi['name'])

                if roi['axis'] == sweep_axis:
                    dr['x__time__ns'] = (arange(sec['duration'])+sec['offset'])*bin2time
                    dr['y__counts'] = zeros(sec['duration'], dtype = int)

                    for j in arange(sec['duration']):
                        counts = 0
                        for l in arange(roi['start_index'],roi['start_index']+roi['length']):
                            counts += self.data[k][sec['duration']*l+j]
                        dr['y__counts'][j] = counts

                    suffix = 'time_ROI_%s' % roi['name']
                                    
                tools.save_npz_data(prefix+suffix, filepath=path, meta=roiheader, **dr)

        def _save_sweep_rep_axes():
            suffix = sw_name + '_vs_repetition'
            header +=
            """
            # sweep name: %s
            # columns: %s
            # rows: %s
            # sweep step size: %s
            # 1st row: %s
            # last row: %s
            """ % (self.sweep['name'],
                    self.repetitions['count'],
                    self.sweep['count'],
                    self.sweep['incr'],
                    self.sweep['start'],
                    self.sweep['start']+self.sweep['incr']*(self.sweep['count']-1))

            d = {}
            d['x__repetition'] = arange(0,self.repetitions['count']+1)
            d['y__%s' % sw_name] = arange(0,self.sweep['count']+1)*self.sweep['incr']+self.sweep['start']
            d['z__counts'] = zeros((self.sweep['count'],self.repetitions['count']), dtype = int)
            for i in arange(0,self.sweep['count']):
                for j in arange(0,self.repetitions['count']):
                    d['z__counts'][i,j] = self.data[k][self.sweep['count']*j+i]

            tools.save_npz_data(prefix+suffix, filepath=path, meta=header, **d)

            for l,roi in enumerate(sec['ROI_list']):
                roiheader = """
                # ROI name: %s
                # ROI type: %d
                """ % (roi['name'], roi['axis'])
                dr = {}
                
                if roi['axis'] == repetition_axis:
                    suffix = sw_name + '_ROI_%s' % roi['name']

                    dr['x__%s' % sw_name] = arange(0,self.sweep['count']+1) * \
                        self.sweep['incr']+self.sweep['start']
                    dr['y__counts'] = zeros((self.sweep['count']))
                    
                    for i in arange(0,self.sweep['count']):
                        counts = 0
                        for j in arange(ROI['start_index'],ROI['start_index']+ROI['length']):
                            counts += self.data[k][self.sweep['count']*j+i]
                        dr['y__counts'][i] = counts

                if roi['axis'] == sweep_axis:
                    suffix = 'repetitions_ROI_'+roi['name']

                    dr['x__repetition'] = arange(0,self.repetitions['count']+1)
                    dr['y__counts'] = zeros((self.repetitions['count']))

                    for j in arange(0,self.repetitions['count']):
                        counts = 0
                        for i in arange(0,roi['start_index'],roi['start_index']+roi['length']):
                            counts += self.data[k][self.sweep['count']*j+i]
                        dr['y__counts'][j] = counts                
    
                tools.save_npz_data(prefix+suffix, filepath=path, meta=roiheader, **dr)

        def _save_time_rep_axes():
            suffix = 'time_vs_repetition'
            header += """
            # columns: %s
            # rows: %s
            # bin size: %s
            # 1st row: %s ns
            # last row: %s ns
            """ % (self.repetitions['count'],
                    sec['duration'],
                    bin2time,
                    bin2time*sec['offset'],
                    bin2time*(sec['offset']+sec['duration']-1))
            d = {}
            d['x__repetition'] = arange(self.repetitions['count']+1)
            d['y__t__ns'] = (arange(sec['duration']+1)+sec['offset'])*bin2time
            d['z__counts'] = zeros((sec['duration'],self.repetitions['count']), dtype = int)
            for i in arange(0,self.sections[k]['duration']):
                for j in arange(0,self.repetitions['count']):
                    d['z__counts'][i,j] = self.data[k][sec['duration']*j+i]

            tools.save_npz_data(prefix+suffix, filepath=path, meta=header, **d)

            for l,roi in enumerate(sec['ROI_list']):
                roiheader = """
                # ROI name: %s
                # ROI type: %d
                """ % (roi['name'], roi['axis'])
                dr = {}
                
                if roi['axis'] == repetition_axis:
                    suffix = 'time_ROI_%s' % roi['name']

                    dr['x__time__ns'] = (arange(sec['duration'])+sec['offset'])*bin2time
                    dr['y__counts'] = zeros((sec['duration']))

                    for i in arange(0,sec['duration']):
                        counts = 0
                        for j in arange(0,roi['start_index'],roi['start_index']+roi['length']):
                            counts += self.data[k][self.sweep['count']*j+i]
                        dr['y__counts'][i] = counts
                    
                if roi['axis'] == time_axis:
                    suffix = 'repetition_ROI_%s' % roi['name']

                    dr['x__repetition'] = arange(self.repetitions['count'])
                    dr['y__counts'] = zeros((self.repetitions['count']))

                    for j in arange(0,self.repetitions['count']):
                        counts = 0
                        for i in arange(roi['start_index'],roi['start_index']+roi['length']):
                            counts += self.data[k][sec['duration']*j+i]
                        dr['y__counts'][j] = counts    
                    
                tools.save_npz_data(prefix+suffix, filepath=path, meta=roiheader, **dr)
              

        if bool(sec['mode'] == sweep_axis):
            _save_sweep_axis()
        if bool(sec['mode'] == time_axis):
            _save_time_axis()
        if bool(sec['mode'] == repetition_axis):
            _save_rep_axis()
        if bool(sec['mode'] == sweep_axis+time_axis):
            _save_sweep_time_axes()
        if bool(sec['mode'] == sweep_axis+repetition_axis):
            _save_sweep_rep_axes()
        if bool(sec['mode'] == time_axis+repetition_axis):
            _save_time_rep_axes()

        

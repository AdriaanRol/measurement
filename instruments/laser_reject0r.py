from instrument import Instrument
import types
import qt
import numpy as np
import msvcrt, os, sys, time, gobject
from analysis.lib.fitting import fit, common
import instrument_helper

class laser_reject0r(Instrument):
    
    def __init__(self, name, positioner, adwin, red_laser):
        Instrument.__init__(self, name)

        self.add_function('optimize')
        self.add_function('run')
        self.add_function('fit')
        self.add_function('first_time_run')
        self.add_function('routine') 
        
        self.rotator = positioner
        self.red = red_laser
        self.adwin = adwin

        ins_pars  = {'half_channel'           : {'type':types.IntType,'flags':Instrument.FLAG_GETSET, 'val':2},
                    'half_stepsize'           : {'type':types.IntType,'flags':Instrument.FLAG_GETSET, 'val':400},
                    'half_noof_points'        : {'type':types.IntType,'flags':Instrument.FLAG_GETSET, 'val':11},
                    'quarter_channel'         : {'type':types.IntType,'flags':Instrument.FLAG_GETSET, 'val':1},
                    'quarter_stepsize'        : {'type':types.IntType,'flags':Instrument.FLAG_GETSET, 'val':400},
                    'quarter_noof_points'     : {'type':types.IntType,'flags':Instrument.FLAG_GETSET, 'val':11},
                    'first_time_channel'      : {'type':types.IntType,'flags':Instrument.FLAG_GETSET, 'val':0},
                    'first_time_stepsize'     : {'type':types.IntType,'flags':Instrument.FLAG_GETSET, 'val':4250},
                    'first_time_noof_points'  : {'type':types.IntType,'flags':Instrument.FLAG_GETSET, 'val':11},
                    'first_opt_red_power'     : {'type':types.FloatType,'flags':Instrument.FLAG_GETSET, 'val':1e-9},
                    'opt_threshold'           : {'type':types.FloatType,'flags':Instrument.FLAG_GETSET, 'val':5E5},
                    'zpl_counter'             : {'type':types.IntType,'flags':Instrument.FLAG_GETSET, 'val':2},
                    'plot_degrees'            : {'type':types.BooleanType,'flags':Instrument.FLAG_GETSET, 'val':True},
                    }
        instrument_helper.create_get_set(self,ins_pars)

        self.check_noof_steps = 10000    #ask before changing this number of steps
        self.opt_red_power = 1E-9 #NOTE!!        self.first_opt_red_power = 1E-9

        self.add_parameter('opt_red_power',
                flags=Instrument.FLAG_GETSET,
                minval = 0, maxval = 100E-9,
                units = 'W', type=types.FloatType)


        self.add_parameter('opt_scan_range',
                flags=Instrument.FLAG_GETSET,
                type=types.TupleType,
                units = 'deg')

        self.add_parameter('conversion_factor',
                type=types.FloatType,
                flags=Instrument.FLAG_GET)
        
        cfg_fn = os.path.join(qt.config['ins_cfg_path'], name+'.cfg')

        if not os.path.exists(cfg_fn):
            _f = open(cfg_fn, 'w')
            _f.write('')
            _f.close()

        self._ins_cfg = config.Config(cfg_fn)     
        self.load_cfg()
        self.save_cfg()

    def get_all(self):
        for n in self.get_parameter_names():
            self.get(n)
        
    
    def load_cfg(self):
        params_from_cfg = self._ins_cfg.get_all()

        for p in params_from_cfg:
            val = self._ins_cfg.get(p)
            if type(val) == unicode:
                val = str(val)
            
            try:
                self.set(p, value=val)
            except:
                pass

    def save_cfg(self):
        parlist = self.get_parameters()
        for param in parlist:
            value = self.get(param)
            self._ins_cfg[param] = value


    ############################################################
    #FUNCTIONS THAT ARE ASSOCIATED WITH PARAMETERS DEFINED ABOVE
    ############################################################
    
    def do_get_conversion_factor(self, w = 'half'):
        return self.rotator.get_step_deg_cfg()[getattr(self,'_'+w+'_channel')]

    def do_get_opt_red_power(self):
        return self.opt_red_power

    def do_set_opt_red_power(self, val):
        
        if self.red.get_cal_a() > val:
            self.opt_red_power = val
        else:
            print "Trying to set red optimization power outside of AOM range!"
        
    def do_get_opt_scan_range(self):
        hwp_factor = self._half_noof_points \
                * self.get_conversion_factor('half') #noof_steps * deg/steps
        qwp_factor = self._quarter_noof_points \
                * self.get_conversion_factor('quarter') #noof_steps * deg/steps        
        
        scan_range = (self._half_stepsize * hwp_factor, 
                self._quarter_stepsize * qwp_factor)
        return scan_range

    def do_set_opt_scan_range(self, val):
        """
        Sets the optimization scan range for both waveplates.
        Specify input as follows: (hwp_range, qwp_range)
        """
        hwp_factor = self._half_noof_points\
                * self.get_conversion_factor('half') #noof_steps * deg/steps
        qwp_factor = self._quarter_noof_points\
                * self.get_conversion_factor('quarter') #noof_steps * deg/steps 

        if np.size(val) == 2:
            self._half_stepsize = val[0]/hwp_factor
            self._quarter_stepsize = val[1]/qwp_factor
        else:
            raise ValueError('Input size must be 2, but has size %d'%size(val))

   
    ##################################################
    #FUNCTIONS THAT ARE NOT ASSOCIATED WITH PARAMETERS
    ##################################################

    def find_nearest(self, array, value):
        idx=(np.abs(array-value)).argmin()
        return idx


    def optimize(self, cycles = 1, waveplates = ['half', 'quarter'],
            counter = 0):
        """
        Function that is accessible from QTLab.
        Input: 
        - cycles: number of optimization cycles (default = 1)
        - waveplates: what waveplates to optimize (default = ['half', 'quarter'])
        - counter: integer in 0 to 3.

        Output:
        None
        """
        
        if counter in range(0,4):
            self.counter = counter
        else:
            raise ValueError('Argument specified for counter is not understood')

        for c in range(cycles):
            print '* Optimizing cycle %d of %d...'%(c+1, cycles)
            
            for w in waveplates:
                #measure position before optimizing
                self.rotator.set_zero_position(getattr(self,'_'+w+'_channel'))
                pos_before = getattr(self.rotator, 'get_noof_steps_ch'+\
                        str(getattr(self,'_'+w+'_channel')) )()
                
                #turn waveplat2es
                data, qtdata, dataplot, premature_quit = self.run(w, self.get_opt_red_power())
                if not premature_quit:
                    qtdata, fitres = self.fit(w, data, qtdata, dataplot)
                qtdata.close_file()

                if not premature_quit:
                
                    #set optimal position
                    if type(fitres) != type(False):
                        if np.sign(fitres['a2']) != -1:
                            optim_pos = -np.int(fitres['a1']/(2*fitres['a2']))
                        else:
                            print '\tFitting a maximum instead of a minimum.'
                            optim_pos = 0
                        
                    else:
                        print '\tGuessing optimal waveplate position...'
                        optim_pos = data['wp_steps'](self.find_nearest(data['counts'],
                            min(data['counts'])))

                    if self.get_plot_degrees():
                        print '\tOptimal waveplate position determined at %.0f degrees.'%(optim_pos*self.get_conversion_factor(w))
                    else:
                        print '\tOptimal waveplate position determined at %d steps.'%optim_pos
    
                    #BEWARE: never ask the current position in noof_steps
                    curr_pos = data['wp_step'][len(data['wp_step'])-1]

                    #check that the optimum position is somewhat reasonable
                    if abs(optim_pos) < self.check_noof_steps:
                        #set the position to the optimal position
                        self.rotator.quick_scan(optim_pos-curr_pos, 
                                getattr(self,'_'+w+'_channel'))
                    else:
                        print '\tWARNING: Optimal position differs %s steps\
                                from initial position'%optim_pos
                        check = raw_input('\tPress "ENTER" to continue, "q" to quit\n')
                            
                        if check == '':
                            #set the position to the optimal position
                            self.rotator.quick_scan(optim_pos-curr_pos, 
                                    getattr(self,'_'+w+'_channel'))
                            
                        elif check == 'q':
                            print 'Process aborted by user'
                            pass
                        else:
                            raise ValueError('Response to question is not \
                                    understood. Not taking any action.')
                else:
                    #what to do if there was a premature quit during optimization?
                    pos_quit = data['wp_step'][len(data['wp_step'])-1]

                    print '\tReturning to initial position...'
                    #set the position to the optimal position
                    self.rotator.quick_scan(pos_before-pos_quit, getattr(self,'_'+w+'_channel'))

                #measure position after optimizing
                pos_after = getattr(self.rotator, 'get_noof_steps_ch'+\
                        str(getattr(self,'_'+w+'_channel')))()

                #print "\tPosition of %s waveplate changed %d steps"\
                #        %(w, pos_after-pos_before)
                
                if msvcrt.kbhit():
                    kb_char=msvcrt.getch()
                    if kb_char == "q" : break
                
                qt.msleep(0.5)
                
            if premature_quit:
                break

    def map_abs_to_rel(self, abs_array):
        
        rel_array = np.zeros(len(abs_array))
        rel_array[0] = abs_array[0]

        dx = np.diff(abs_array)
        rel_array[1:len(rel_array)] = dx

        return rel_array.astype(int)


    def run(self, w, red_power):
        """
        The actual optimization procedure. Input: waveplate ('half'/'quarter').
        Produces a plot of measured counts vs. rotation step.
        """
        
        #turn off red
        self.red.set_power(0)
        
        dx = getattr(self,'_'+w+'_stepsize')
        pts = getattr(self,'_'+w+'_noof_points')

        if pts%2:
            x = dx*np.linspace(int(np.ceil(-pts/2.)), int(pts/2.), pts)
        else:
            x = dx*np.linspace(int(-pts/2)+1, int(pts/2), pts)

        dataname = 'optimize_%s_waveplate'%w

        qtdata = qt.Data(name = dataname)
        
        if not self.get_plot_degrees():
            qtdata.add_coordinate('Waveplate steps')
        else:
            qtdata.add_coordinate('Degrees')
        qtdata.add_value('Signal')
    
        dataplot = qt.Plot2D(qtdata, 'rO', name = dataname, coorddim = 0, 
                valdim = 1, clear = True)
        dataplot.add(qtdata, 'b-', coorddim = 0, valdim = 2)
        
        y = np.zeros(len(x))
        for idx, X in enumerate(self.map_abs_to_rel(x)):
            #set position
            self.rotator.quick_scan(X, getattr(self,'_'+w+'_channel'))

            #turn on red
            self.red.set_power(red_power)
            qt.msleep(0.1)

            #get counts/ voltage
            y[idx] = self.adwin.get_countrates()[self._zpl_counter-1]
            
            #turn off red
            self.red.set_power(0)

            #add to plot
            if self.get_plot_degrees():
                qtdata.add_data_point(x[idx]*self.get_conversion_factor(w), y[idx])
            else:
                qtdata.add_data_point(x[idx], y[idx])

            #Threshold implementation
            #Was it the first point in the sequence? return to init pos.
            if y[idx] > self._opt_threshold and idx == 0:
                print '\tWARNING! Counts for the first point in routine exceed\
                        threshold. Returning to initial position...'
                self.rotator.quick_scan(-X, getattr(self,'_'+w+'_channel'))
                premature_quit = True

                x = x[0:idx+1]
                y = y[0:idx+1]
                break

            #Was it a later point: If previous position was safe, go back
            if y[idx] > self._opt_threshold and idx > 0:
                if y[idx-1] < self._opt_threshold: #must be the case
                    print '\tWARNING! Counts for point %d exceed the threshold.\
                            Returning to previous point in sequence.'%(idx+1)
                    self.rotator.quick_scan(-X, getattr(self,'_'+w+'_channel'))
                else:
                    print '\tSomething is terribly wrong here...'
                premature_quit = True

                x = x[0:idx+1]
                y = y[0:idx+1]
                break
            

            if msvcrt.kbhit():
                kb_char=msvcrt.getch()
                if kb_char == "q" : 
                    premature_quit = True
                    x = x[0:idx+1]
                    y = y[0:idx+1]
                    break
            else:
                premature_quit = False

        data = {'wp_step' : x, 'counts': y}
    
        return data, qtdata, dataplot, premature_quit


    def fit(self, w, data, qtdata, dataplot):
        """
        Gets data from _run and fits it with a parabola. Needs:
        - data (measured data points)
        - qtdata (qt data object)
        - dataplot (plot with added data)

        Returns:
        - updated qtdata
        - fitresult (may be of type False if fit failed)
        """
        a0 = data['counts'][self.find_nearest(data['counts'], 0)]
        a1 = 1
        a2 = 1        
        
        #perform fit
        fitres = fit.fit1d(data['wp_step'], data['counts'], common.fit_poly, 
                [a0, a1, a2], do_print = False, ret = True)

        fd = np.zeros(len(data['wp_step']))
        if type(fitres) != type(False):
            p1 = fitres['params_dict']
            A0 = p1['a0']
            A1 = p1['a1']
            A2 = p1['a2']
            fd = fitres['fitfunc'](data['wp_step'])
        else:
            p1 = False
            print '\tCould not fit curve!'
        
        if self.get_plot_degrees():
            dataplot.add(data['wp_step']*self.get_conversion_factor(w), fd, '-b')
        else:
            dataplot.add(data['wp_step'], fd, '-b')

        return qtdata, p1

    def first_time_run(self, w):
        """
        For the first time, trace 360 degrees with the waveplate
        """
                
        if w in ['half', 'quarter']:
            self._first_time_channel = getattr(self,'_'+w+'_channel')
        else:
            raise ValueError('Input type for "w" should be "half" or "quarter"')

        #measure position before optimizing
        getattr(self.rotator, 'set_zero_position')(getattr(self,'_'+w+'_channel'))        
        pos_before = getattr(self.rotator, 'get_noof_steps_ch'+\
                str(getattr(self,'_'+w+'_channel')))()

        #turn waveplates
        data, qtdata, dataplot, premature_quit = self.run('first_time', self._first_opt_red_power)
        qtdata.close_file()

        if not premature_quit:

            print '\tGuessing optimal waveplate position...'
            optim_pos = data['wp_step'][self.find_nearest(data['counts'],
                min(data['counts']))]

            if self.get_plot_degrees():
                print '\tOptimal waveplate position determined at %.0f degrees.'%(optim_pos*self.get_conversion_factor(w))
            else:
                print '\tOptimal waveplate position determined at %d steps.'%optim_pos
            
            #BEWARE: never ask the current position in noof_steps
            curr_pos = data['wp_step'][len(data['wp_step'])-1]

            #set the position to the optimal position
            self.rotator.quick_scan(optim_pos-curr_pos, getattr(self,'_'+w+'_channel'))

        else:
            #ways to get a premature quit action: q key stroke or > threshold
            #BEWARE: never ask the current position in noof_steps
            curr_pos = data['wp_step'][len(data['wp_step'])-1]            

            print '\tReturning to initial position...'

            #set the position to the optimal position
            self.rotator.quick_scan(pos_before-curr_pos, getattr(self,'_'+w+'_channel'))


        #measure position after optimizing
        pos_after = getattr(self.rotator, 'get_noof_steps_ch'+\
                str(getattr(self,'_'+w+'_channel') ) )()

        #print "\tPosition of %s waveplate changed %d steps"\
        #        %(w, pos_after-pos_before)


    def routine(self):
        #idea: turn red on only just before we're at the first point       
        self.set_opt_red_power(self.get_opt_red_power())        
        self.first_time_run('half', self.first)
        self.first_time_run('quarter')

        #test if initial point is a valid starting point for optimization!
        self.red.set_power(self.get_opt_red_power())
        crate = self.adwin.get_countrates()[self._zpl_counter-1]
        self.red.set_power(0)

        if crate < self._opt_threshold:
            self.optimize(cycles = 5, waveplates = ['half', 'quarter'], 
                    counter = self._zpl_counter)
        else:
            print 'Not starting optimization: starting point is not valid.'


    def randomize_position(self, w, steps = 3):
        """
        Mainly used for testing. It randomizes the position of the waveplates
        specified by "w". w must be a list containing 'half' or 'quarter'.
        For more randomization choose a higher value for steps.
        """
        
        self.red.set_power(0)
        
        for k in range(steps):
            for idx,waveplate in enumerate(w):
                print '* Randomizing %s waveplate (step %d) ...'%(waveplate, k)
                self.rotator.quick_scan(np.random.uniform(low = -20000, high = 20000) ,getattr(self,'_'+waveplate+'_channel'))



        

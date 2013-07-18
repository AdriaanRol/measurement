from instrument import Instrument
import types
import qt
import numpy as np
import msvcrt, os, sys, time, gobject
from analysis.lib.fitting import fit, common

class laser_reject0r(Instrument):
    
    def __init__(self, name):
        Instrument.__init__(self, name)

        self.add_function('optimize')
        self.add_function('run')
        self.add_function('fit')
        self.add_function('first_time_run')
        self.add_function('routine') 
        
        self.rotator = qt.instruments['positioner']
        self.red = qt.instruments['Velocity1AOM']
        self.adwin = qt.instruments['adwin']
        
        self.optim_sets = {
                        'half' : {
                            'channel' : 2,
                            'stepsize' : 700,
                            'noof_points' : 11}, 
                        'quarter' : {
                            'channel' : 1,
                            'stepsize' : 700,
                            'noof_points' : 11},
                        'first_time' : {
                            'channel' : 0,
                            'stepsize' : 4250.,
                            'noof_points' : 11}
                        }

        self.check_noof_steps = 10000    #ask before changing this number of steps
        self.opt_threshold = 5E5
        self.opt_red_power = 1E-9 #NOTE!!
        self.first_opt_red_power = 1E-9
        self.zpl_counter = 2
        self._is_running = False
        self.plot_degrees = True

        self.add_parameter('opt_red_power',
                flags=Instrument.FLAG_GETSET,
                minval = 0, maxval = 100E-9,
                units = 'W', type=types.FloatType)

        self.add_parameter('opt_scan_range',
                flags=Instrument.FLAG_GETSET,
                type=types.TupleType,
                units = 'deg', 
                mival = 1, maxval = 180)

        self.add_parameter('opt_threshold',
                flags=Instrument.FLAG_GETSET,
                type=types.FloatType)

        self.add_parameter('zpl_counter',
                flags=Instrument.FLAG_GETSET,
                type=types.IntType)

        self.add_parameter('is_running',
                type=types.BooleanType,
                flags=Instrument.FLAG_GETSET)

        self.add_parameter('plot_degrees',
                type=types.BooleanType,
                flags=Instrument.FLAG_GETSET)

        self.add_parameter('conversion_factor',
                type=types.FloatType,
                flags=Instrument.FLAG_GET)

    ############################################################
    #FUNCTIONS THAT ARE ASSOCIATED WITH PARAMETERS DEFINED ABOVE
    ############################################################
    
    def do_get_conversion_factor(self, w = 'half'):
        return self.rotator.get_step_deg_cfg()[self.optim_sets[w]['channel']]

    def do_get_plot_degrees(self):
        return self.plot_degrees

    def do_set_plot_degrees(self, val):
        self.plot_degrees = val

    def do_get_opt_red_power(self):
        return self.opt_red_power

    def do_set_opt_red_power(self, val):
        
        if self.red.get_cal_a() > val:
            self.opt_red_power = val
        else:
            print "Trying to set red optimization power outside of AOM range!"
        
    def do_get_opt_scan_range(self):
        hwp_factor = self.optim_sets['half']['noof_points']\
                * self.get_conversion_factor('half') #noof_steps * deg/steps
        qwp_factor = self.optim_sets['quarter']['noof_points']\
                * self.get_conversion_factor('quarter') #noof_steps * deg/steps        
        
        scan_range = (self.optim_sets['half']['stepsize'] * hwp_factor, 
                self.optim_sets['quarter']['stepsize'] * qwp_factor)
        return scan_range

    def do_set_opt_scan_range(self, val):
        """
        Sets the optimization scan range for both waveplates.
        Specify input as follows: (hwp_range, qwp_range)
        """
        hwp_factor = self.optim_sets['half']['noof_points']\
                * self.get_conversion_factor('half') #noof_steps * deg/steps
        qwp_factor = self.optim_sets['quarter']['noof_points']\
                * self.get_conversion_factor('quarter') #noof_steps * deg/steps 

        if size(val) == 2:
            self.optim_sets['half']['stepsize'] = val[0]/hwp_factor
            self.optim_sets['quarter']['stepsize'] = val[1]/qwp_factor
        else:
            raise ValueError('Input size must be 2, but has size %d'%size(val))

    def do_get_opt_threshold(self):
        return self.opt_threshold

    def do_set_opt_threshold(self, val):
        """
        Sets the maximum allowed countrate. If a countrate > opt_threshold is 
        detected, the optimization procedure is aborted.
        """
        self.opt_threshold = val

    def do_get_zpl_counter(self):
        return self.zpl_counter

    def do_set_zpl_counter(self, val):
        """
        Sets the ZPL counter (ADwin ZPL counter).
        """
        self.zpl_counter = val

    def do_get_is_running(self):
        return self._is_running

    def do_set_is_running(self, val):
        self._is_running = val


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
                getattr(self.rotator, 'set_zero_position')(self.optim_sets[w]['channel'])
                pos_before = getattr(self.rotator, 'get_noof_steps_ch'+\
                        str(self.optim_sets[w]['channel']))()
                
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
                                self.optim_sets[w]['channel'])
                    else:
                        print '\tWARNING: Optimal position differs %s steps\
                                from initial position'%optim_pos
                        check = raw_input('\tPress "ENTER" to continue, "q" to quit\n')
                            
                        if check == '':
                            #set the position to the optimal position
                            self.rotator.quick_scan(optim_pos-curr_pos, 
                                    self.optim_sets[w]['channel'])
                            
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
                    self.rotator.quick_scan(pos_before-pos_quit, self.optim_sets[w]['channel'])

                #measure position after optimizing
                pos_after = getattr(self.rotator, 'get_noof_steps_ch'+\
                        str(self.optim_sets[w]['channel']))()

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
        
        self.set_is_running(True)

        dx = self.optim_sets[w]['stepsize']
        pts = self.optim_sets[w]['noof_points']

        if pts%2:
            x = dx*np.linspace(int(np.ceil(-pts/2.)), int(pts/2.), pts)
        else:
            x = dx*np.linspace(int(-pts/2)+1, int(pts/2), pts)

        dataname = 'optimize_%s_waveplate'%w

        qtdata = qt.Data(name = dataname)
        
        if self.get_plot_degrees():
            qtdata.add_coordinate('Waveplate steps')
        else:
            qtdata.add_coordinate('Degrees')
        qtdata.add_value('Signal')
    
        dataplot = qt.Plot2D(qtdata, 'rO', name = dataname, coorddim = 0, 
                valdim = 1, clear = True)
        dataplot.add(qtdata, 'b-', coorddim = 0, valdim = 2)
        gobject.timeout_add(500, self._update)
        
        y = np.zeros(len(x))
        for idx, X in enumerate(self.map_abs_to_rel(x)):
            #set position
            self.rotator.quick_scan(X, self.optim_sets[w]['channel'])

            #turn on red
            self.red.set_power(red_power)
            qt.msleep(0.1)

            #get counts/ voltage
            y[idx] = self.adwin.get_countrates()[self.zpl_counter-1]
            
            #turn off red
            self.red.set_power(0)

            #add to plot
            if self.get_plot_degrees():
                qtdata.add_data_point(x[idx]*self.get_conversion_factor(w), y[idx])
            else:
                qtdata.add_data_point(x[idx], y[idx])

            #Threshold implementation
            #Was it the first point in the sequence? return to init pos.
            if y[idx] > self.opt_threshold and idx == 0:
                print '\tWARNING! Counts for the first point in routine exceed\
                        threshold. Returning to initial position...'
                self.rotator.quick_scan(-X, self.optim_sets[w]['channel'])
                premature_quit = True

                x = x[0:idx+1]
                y = y[0:idx+1]
                break

            #Was it a later point: If previous position was safe, go back
            if y[idx] > self.opt_threshold and idx > 0:
                if y[idx-1] < self.opt_threshold: #must be the case
                    print '\tWARNING! Counts for point %d exceed the threshold.\
                            Returning to previous point in sequence.'%(idx+1)
                    self.rotator.quick_scan(-X, self.optim_sets[w]['channel'])
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

        self.set_is_running(False)
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
            self.optim_sets['first_time']['channel'] = self.optim_sets[w]['channel']
        else:
            raise ValueError('Input type for "w" should be "half" or "quarter"')

        #measure position before optimizing
        getattr(self.rotator, 'set_zero_position')(self.optim_sets[w]['channel'])        
        pos_before = getattr(self.rotator, 'get_noof_steps_ch'+\
                str(self.optim_sets[w]['channel']))()

        #turn waveplates
        data, qtdata, dataplot, premature_quit = self.run('first_time', self.first_opt_red_power)
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
            self.rotator.quick_scan(optim_pos-curr_pos, self.optim_sets[w]['channel'])

        else:
            #ways to get a premature quit action: q key stroke or > threshold
            #BEWARE: never ask the current position in noof_steps
            curr_pos = data['wp_step'][len(data['wp_step'])-1]            

            print '\tReturning to initial position...'

            #set the position to the optimal position
            self.rotator.quick_scan(pos_before-curr_pos, self.optim_sets[w]['channel'])


        #measure position after optimizing
        pos_after = getattr(self.rotator, 'get_noof_steps_ch'+\
                str(self.optim_sets[w]['channel']))()

        #print "\tPosition of %s waveplate changed %d steps"\
        #        %(w, pos_after-pos_before)


    def routine(self):
        #idea: turn red on only just before we're at the first point       
        self.set_opt_red_power(self.get_opt_red_power())        
        self.first_time_run('half', self.first)
        self.first_time_run('quarter')

        #test if initial point is a valid starting point for optimization!
        self.red.set_power(self.get_opt_red_power())
        crate = self.adwin.get_countrates()[self.zpl_counter-1]
        self.red.set_power(0)

        if crate < self.opt_threshold:
            self.optimize(cycles = 5, waveplates = ['half', 'quarter'], 
                    counter = self.zpl_counter)
        else:
            print 'Not starting optimization: starting point is not valid.'


    def _update(self):
        """
        Returns False if the procedure is done. No updating is necessary.
        Returns True if the procedure is still running and the plot needs 
        to update
        """        
        if not self._is_running:
            return False
        
        return True
        
        
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
                self.rotator.quick_scan(np.random.uniform(low = -20000, high = 20000) ,self.optim_sets[waveplate]['channel'])



        

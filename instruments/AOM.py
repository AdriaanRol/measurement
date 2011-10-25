# general AOM instrument class
# assumes AOM connected to either ADwin DAC or AWG channel
# if connected to AWG, the corresponding channel's offset (analog channels) 
#    or low value (marker channels) will be used to set the power.
# parameters are stored in the setup configuration file (defined as setup_cfg in qtlab.cfg,
# and will automatically be reloaded with qtlab start.
#
# if a new AOM instrument is added, initial (not necessary useful) parameters will be used.
# channel configuration, maximum allowed voltages etc. should be immediately set after 
# loading new AOM instrument for first time.


from instrument import Instrument
from numpy import *
from analysis import fit_oldschool as fit
import time
import matplotlib.pyplot as plt
import ConfigParser
import qt
import types

class AOM(Instrument):

    def __init__(self, name):
        Instrument.__init__(self, name)

        self.add_parameter('wavelength',
                           type=types.FloatType,
                           flags=Instrument.FLAG_GETSET,
                           units='nm',
                           minval=500e-9,maxval=1000e-9)
        
        self.add_parameter('cur_controller', 
                           type = types.StringType, 
                           option_list = ('AWG', 'ADwin'), 
                           flags = Instrument.FLAG_GETSET)
        
        self.add_parameter('pri_controller', 
                           type = types.StringType, 
                           option_list = ('AWG', 'ADwin'), 
                           flags = Instrument.FLAG_GETSET)
        
        self.add_parameter('pri_channel', 
                           type = types.StringType, 
                           flags = Instrument.FLAG_GETSET)
        
        self.add_parameter('pri_cal_a',
                           type=types.FloatType,
                           flags=Instrument.FLAG_GETSET,
                           units='mW',
                           minval=0,maxval=1.0)
        
        self.add_parameter('pri_cal_xc',
                           type=types.FloatType,
                           flags=Instrument.FLAG_GETSET,
                           units='V',
                           minval=0,maxval=10.0)
        
        self.add_parameter('pri_cal_k',
                           type=types.FloatType,
                           flags=Instrument.FLAG_GETSET,
                           minval=0,maxval=100.0)
        
        self.add_parameter('pri_V_max',
                           type=types.FloatType,
                           flags=Instrument.FLAG_GETSET,
                           units='V',
                           minval=0,maxval=10.0)
        
        self.add_parameter('sec_controller', 
                           type = types.StringType, 
                           option_list = ('AWG', 'ADwin'), 
                           flags = Instrument.FLAG_GETSET)
        
        self.add_parameter('sec_channel', 
                           flags = Instrument.FLAG_GETSET)
        
        self.add_parameter('sec_cal_a',
                           type=types.FloatType,
                           flags=Instrument.FLAG_GETSET,
                           units='mW',
                           minval=0,maxval=1.0)
        
        self.add_parameter('sec_cal_xc',
                           type=types.FloatType,
                           flags=Instrument.FLAG_GETSET,
                           units='V',
                           minval=0,maxval=10.0)
        
        self.add_parameter('sec_cal_k',
                           type=types.FloatType,
                           flags=Instrument.FLAG_GETSET,
                           minval=0,maxval=100.0)
        
        self.add_parameter('sec_V_max',
                           type=types.FloatType,
                           flags=Instrument.FLAG_GETSET,
                           units='V',
                           minval=0,maxval=10.0)

        self.add_parameter('switchable',
                           type=types.BooleanType,
                           flags=Instrument.FLAG_GETSET)
        
        self.add_parameter('switch_DO',
                           type=types.IntType,
                           flags=Instrument.FLAG_GETSET,
                           minval=0,maxval=31)
        
        config = ConfigParser.SafeConfigParser()
        config.read(qt.config['setup_cfg'])
        try:
            self._pri_controller = config.get('AOM', name+'_pri_controller')
        except ConfigParser.NoSectionError:
            config.add_section('AOM')
            config.set('AOM',name+'_wavelength','532e-9')
            config.set('AOM',name+'_pri_controller','AWG')
            config.set('AOM',name+'_pri_channel','ch1')
            config.set('AOM',name+'_pri_cal_a','0.823')
            config.set('AOM',name+'_pri_cal_xc','0.588')
            config.set('AOM',name+'_pri_cal_k','6.855')
            config.set('AOM',name+'_pri_V_max','1.0')
            config.set('AOM',name+'_switchable','False')
            config.set('AOM',name+'_switch_DO','16')
            config.set('AOM',name+'_cur_controller','AWG')
            config.set('AOM',name+'_sec_controller','AWG')
            config.set('AOM',name+'_sec_channel','ch1')
            config.set('AOM',name+'_sec_cal_a','0.823')
            config.set('AOM',name+'_sec_cal_xc','0.588')
            config.set('AOM',name+'_sec_cal_k','6.855')
            config.set('AOM',name+'_sec_V_max','1.0')
            with open(qt.config['setup_cfg'], 'wb') as configfile:
                config.write(configfile)
        except ConfigParser.NoOptionError:
            config.set('AOM',name+'_wavelength','532e-9')
            config.set('AOM',name+'_pri_controller','AWG')
            config.set('AOM',name+'_pri_channel','ch1')
            config.set('AOM',name+'_pri_cal_a','0.823')
            config.set('AOM',name+'_pri_cal_xc','0.588')
            config.set('AOM',name+'_pri_cal_k','6.855')
            config.set('AOM',name+'_pri_V_max','1.0')
            config.set('AOM',name+'_switchable','False')
            config.set('AOM',name+'_switch_DO','16')
            config.set('AOM',name+'_cur_controller','AWG')
            config.set('AOM',name+'_sec_controller','AWG')
            config.set('AOM',name+'_sec_channel','ch1')
            config.set('AOM',name+'_sec_cal_a','0.823')
            config.set('AOM',name+'_sec_cal_xc','0.588')
            config.set('AOM',name+'_sec_cal_k','6.855')
            config.set('AOM',name+'_sec_V_max','1.0')
            with open(qt.config['setup_cfg'], 'wb') as configfile:
                config.write(configfile)

        self._wavelength = config.getfloat('AOM', name+'_wavelength')
        self._pri_controller = config.get('AOM', name+'_pri_controller')
        self._pri_channel = config.get('AOM', name+'_pri_channel')
        self._pri_cal_a = config.getfloat('AOM', name+'_pri_cal_a') 
        self._pri_cal_xc = config.getfloat('AOM', name+'_pri_cal_xc') 
        self._pri_cal_k = config.getfloat('AOM', name+'_pri_cal_k') 
        self._pri_V_max = config.getfloat('AOM', name+'_pri_V_max') 
        self._switchable = config.getboolean('AOM', name+'_switchable')
        self._switch_DO = config.getint('AOM', name+'_switch_DO')
        self._cur_controller = config.get('AOM', name+'_cur_controller')
        self._sec_controller = config.get('AOM', name+'_sec_controller')
        self._sec_channel = config.get('AOM', name+'_sec_channel')
        self._sec_cal_a = config.getfloat('AOM', name+'_sec_cal_a') 
        self._sec_cal_xc = config.getfloat('AOM', name+'_sec_cal_xc') 
        self._sec_cal_k = config.getfloat('AOM', name+'_sec_cal_k') 
        self._sec_V_max = config.getfloat('AOM', name+'_sec_V_max') 

    def save_cfg(self):
        config = ConfigParser.SafeConfigParser()
        config.read(qt.config['setup_cfg'])
        name = self._name
        config.set('AOM',name+'_wavelength',str(self._wavelength))
        config.set('AOM',name+'_pri_controller',self._pri_controller)
        config.set('AOM',name+'_pri_channel',self._pri_channel)
        config.set('AOM',name+'_pri_cal_a',str(self._pri_cal_a))
        config.set('AOM',name+'_pri_cal_xc',str(self._pri_cal_xc))
        config.set('AOM',name+'_pri_cal_k',str(self._pri_cal_k))
        config.set('AOM',name+'_pri_V_max',str(self._pri_V_max))
        config.set('AOM',name+'_switchable',str(self._switchable))
        config.set('AOM',name+'_switch_DO',str(self._switch_DO))
        config.set('AOM',name+'_cur_controller',self._cur_controller)
        config.set('AOM',name+'_sec_controller',self._sec_controller)
        config.set('AOM',name+'_sec_channel',self._sec_channel)
        config.set('AOM',name+'_sec_cal_a',str(self._sec_cal_a))
        config.set('AOM',name+'_sec_cal_xc',str(self._sec_cal_xc))
        config.set('AOM',name+'_sec_cal_k',str(self._sec_cal_k))
        config.set('AOM',name+'_sec_V_max',str(self._sec_V_max))
        with open(qt.config['setup_cfg'], 'wb') as configfile:
            config.write(configfile)
    
    def apply_voltage(self, U):
        controller = self.get_cur_controller()
        channel = self.get_channel()
        V_max = self.get_V_max()
        AWG_instr = qt.instruments['AWG']
        if U > V_max:
            print('Error: maximum voltage of this channel exceeded')
            return
        if controller == 'AWG':
            if qt.instruments['AWG'].get_runmode() != 'CONT':
                print('Warning: AWG not in continuous mode!')
           
            apply = {'ch1': AWG_instr.set_ch1_offset,
                     'ch1m1': AWG_instr.set_ch1_marker1_low,
                     'ch1m2': AWG_instr.set_ch1_marker2_low,
                     'ch2': AWG_instr.set_ch2_offset,
                     'ch2m1': AWG_instr.set_ch2_marker1_low,
                     'ch2m2': AWG_instr.set_ch2_marker2_low,
                     'ch3': AWG_instr.set_ch3_offset,
                     'ch3m1': AWG_instr.set_ch3_marker1_low,
                     'ch3m2': AWG_instr.set_ch3_marker2_low,
                     'ch4': AWG_instr.set_ch4_offset,
                     'ch4m1': AWG_instr.set_ch4_marker1_low,
                     'ch4m2': AWG_instr.set_ch4_marker2_low,
                     }
            apply[channel](U)
        elif controller == 'ADwin':
            qt.instruments['ADwin'].Set_DAC_Voltage(int(channel),U)
        else:
            print('Error: unknown AOM controller %s'%controller)
        return

    def calibrate(self, steps): # calibration values in mW
        x = arange(0,steps)
        y = zeros(steps,dtype = float)
        qt.instruments['TheSetup'].set_PowermeterPosition('in')
        self.apply_voltage(0)
        qt.instruments['PM'].set_wavelength(self._wavelength)
        time.sleep(2)
        bg = qt.instruments['PM'].get_power()
        time.sleep(0.5)
        for a in x:
            self.apply_voltage(a*self.get_V_max()/steps)
            time.sleep(1)
            y[a] = qt.instruments['PM'].get_power() - bg
        x = x/float(steps-1)*V_max
        y = y*1e3
        qt.instruments['TheSetup'].set_PowermeterPosition('out')

        p_init = [ max(y)
            , self.get_cal_xc(), self.get_cal_k()]
        p_fit = fit.fit_AOMfunction(x,y,p_init)
        self.set_cal_a(p_fit[0][0])
        self.set_cal_xc(p_fit[0][1])
        self.set_cal_k(p_fit[0][2])
        path = config['datadir'] + '\\'+time.strftime('%Y%m%d') + '\\' + time.strftime('%H%M%S', time.localtime()) + '_AOM_calibration\\'
        if not os.path.isdir(path):
            os.makedirs(path)
        result=open(path+'\\'+self._name+'_'+self._cur_controller+'.txt', 'w')
        result.write('# a: %s\n'%p_fit[0][0])
        result.write('# xc: %s\n'%p_fit[0][1])
        result.write('# k: %s\n'%p_fit[0][2])
        result.write('\n')
        for a in arange(0,steps):
            result.write('%s\t%s\n' % (x[a],y[a]))
        result.close()
        print (self._name+' calibration finished')

    def power_to_voltage(self, P): # power in microwatt
        a = self.get_cal_a()
        xc = self.get_cal_xc()
        k = self.get_cal_k()
        if P/1000.0 >= a:
            print('Error, power exceeds maximum!')
            return 0
        elif P <= 0:
            voltage = 0
        else:
            voltage = xc-log(log(1000.0*a/float(P)))/k
            if voltage > self.get_V_max():
                print('Error, power exceeds maximum!')
                return 0
        return voltage

    def set_power(self,P): # power in Watt
        self.apply_voltage(self.power_to_voltage(P*1e6))

    def do_set_cur_controller(self, val):
        if (val != self._pri_controller) & (val != self._sec_controller):
            print ('Error: controller %s not registered, using %s instead'%(val, 
                self._pri_controller))
            self._cur_controller = self._sec_controller

        if self._switchable == True:
            if val == self._pri_controller:
                qt.instruments['ADwin'].Set_DO(self._switch_DO,0)
            else:
                qt.instruments['ADwin'].Set_DO(self._switch_DO,1)
            
        self._cur_controller = val
        self.save_cfg()

    def do_set_wavelength(self, val):
        self._wavelength = val
        self.save_cfg()

    def do_get_wavelength(self):
        return self._wavelength

    def do_get_cur_controller(self):
        return self._cur_controller

    def do_set_pri_controller(self, val):
        self._pri_controller = val
        self.save_cfg()

    def do_get_pri_controller(self):
        return self._pri_controller

    def do_set_sec_controller(self, val):
        self._sec_controller = val
        self.save_cfg()

    def do_get_sec_controller(self):
        return self._sec_controller

    def do_get_switchable(self):
        return self._switchable

    def do_set_switchable(self, val):
        self._switchable = val
        self.save_cfg()

    def do_get_switch_DO(self):
        return self._switch_DO

    def do_set_switch_DO(self, val):
        self._switch_DO = val
        self.save_cfg()

    def set_cal_a(self, val):
        if self._cur_controller == self._pri_controller:
            self.do_set_pri_cal_a(val)
        else:
            self.do_set_sec_cal_a(val)

    def set_cal_xc(self, val):
        if self._cur_controller == self._pri_controller:
            self.do_set_pri_cal_xc(val)
        else:
            self.do_set_sec_cal_xc(val)

    def set_cal_k(self, val):
        if self._cur_controller == self._pri_controller:
            self.do_set_pri_cal_k(val)
        else:
            self.do_set_sec_cal_k(val)

    def get_cal_a(self):
        if self._cur_controller == self._pri_controller:
            return self.do_get_pri_cal_a()
        else:
            return self.do_get_sec_cal_a()

    def get_cal_xc(self):
        if self._cur_controller == self._pri_controller:
            return self.do_get_pri_cal_xc()
        else:
            return self.do_get_sec_cal_xc()

    def get_cal_k(self):
        if self._cur_controller == self._pri_controller:
            return self.do_get_pri_cal_k()
        else:
            return self.do_get_sec_cal_k()

    def do_set_pri_cal_a(self, val):
        self._pri_cal_a = val
        self.save_cfg()

    def do_set_sec_cal_a(self, val):
        self._sec_cal_a = val
        self.save_cfg()

    def do_set_pri_cal_xc(self, val):
        self._pri_cal_xc = val
        self.save_cfg()

    def do_set_sec_cal_xc(self, val):
        self._sec_cal_xc = val
        self.save_cfg()

    def do_set_pri_cal_k(self, val):
        self._pri_cal_k = val
        self.save_cfg()

    def do_set_sec_cal_k(self, val):
        self._sec_cal_k = val
        self.save_cfg()

    def do_get_pri_cal_a(self):
        return self._pri_cal_a

    def do_get_sec_cal_a(self):
        return self._sec_cal_a

    def do_get_pri_cal_xc(self):
        return self._pri_cal_xc

    def do_get_sec_cal_xc(self):
        return self._sec_cal_xc

    def do_get_pri_cal_k(self):
        return self._pri_cal_k

    def do_get_sec_cal_k(self):
        return self._sec_cal_k

    def set_V_max(self, val):
        if self._cur_controller == self._pri_controller:
            self.do_set_pri_V_max(val)
        else:
            self.do_set_sec_V_max(val)

    def get_V_max(self):
        if self._cur_controller == self._pri_controller:
            return self.do_get_pri_V_max()
        else:
            return self.do_get_sec_V_max()

    def do_set_pri_V_max(self, val):
        self._pri_V_max = val
        self.save_cfg()

    def do_set_sec_V_max(self, val):
        self._sec_V_max = val
        self.save_cfg()

    def do_get_pri_V_max(self):
        return self._pri_V_max

    def do_get_sec_V_max(self):
        return self._sec_V_max

    def set_channel(self, val):
        if self._cur_controller == self._pri_controller:
            self.do_set_pri_channel(val)
        else:
            self.do_set_sec_channel(val)

    def get_channel(self):
        if self._cur_controller == self._pri_controller:
            return self.do_get_pri_channel()
        else:
            return self.do_get_sec_channel()

    def do_set_pri_channel(self, val):
        self._pri_channel = val
        self.save_cfg()

    def do_set_sec_channel(self, val):
        self._sec_channel = val
        self.save_cfg()

    def do_get_pri_channel(self):
        return self._pri_channel

    def do_get_sec_channel(self):
        return self._sec_channel


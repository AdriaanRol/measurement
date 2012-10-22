from instrument import Instrument
from cyclopean_instrument import CyclopeanInstrument
import gobject
import types
import time
import logging
from numpy import *
from qt import *
from analysis import fit_oldschool as fit
import matplotlib.pyplot as plt

class OpticalSetup(CyclopeanInstrument):
    '''
    This is the python driver for the optical setup

    Usage:
    Initialize with
    <name> = instruments.create('name', 'OpticalSetup')
    '''

    def __init__(self, name, address=None):

        logging.info(__name__ + ' : Initializing instrument')
        #Instrument.__init__(self, name, tags=['physical'])
        CyclopeanInstrument.__init__(self, name, tags=['measure', 'generate', 'virtual'])

        self.add_parameter('PowermeterPosition', type = types.StringType, option_list = ('in', 'out'), flags = Instrument.FLAG_GETSET)
        self.add_parameter('NewfocusStatus', type = types.StringType, option_list = ('blocked', 'unblocked'), flags = Instrument.FLAG_GETSET)
        self.add_parameter('MillenniaStatus', type = types.StringType, option_list = ('blocked', 'unblocked'), flags = Instrument.FLAG_GETSET)
        self.add_parameter('DetectionChannelAStatus', type = types.StringType, option_list = ('blocked', 'unblocked'), flags = Instrument.FLAG_GETSET)
        self.add_parameter('DetectionChannelBStatus', type = types.StringType, option_list = ('blocked', 'unblocked'), flags = Instrument.FLAG_GETSET)
        self.add_parameter('Dichroic', type = types.StringType, flags = Instrument.FLAG_GET)
        self.add_parameter('PowerBackground', type = types.FloatType, flags = Instrument.FLAG_GET, units = 'W', format = '%.3e')
        self.add_parameter('PowerGreen', type = types.FloatType, flags = Instrument.FLAG_GETSET, units = 'W', format = '%.3e')
        self.add_parameter('PowerRed', type = types.FloatType, flags = Instrument.FLAG_GETSET, units = 'W', format = '%.3e')
        self.add_parameter('PolarizerAngle', type = types.FloatType, flags = Instrument.FLAG_GETSET, units = 'deg', format = '%.1f')
        self.add_parameter('GreenAOMADwincalibration_a', type = types.FloatType, flags = Instrument.FLAG_GETSET, units = 'mW', format = '%.3f')
        self.add_parameter('GreenAOMADwincalibration_xc', type = types.FloatType, flags = Instrument.FLAG_GETSET, units = 'V', format = '%.3f')
        self.add_parameter('GreenAOMADwincalibration_k', type = types.FloatType, flags = Instrument.FLAG_GETSET, format = '%.3f')
        self.add_parameter('GreenAOMAWGcalibration_a', type = types.FloatType, flags = Instrument.FLAG_GETSET, units = 'mW', format = '%.3f')
        self.add_parameter('GreenAOMAWGcalibration_xc', type = types.FloatType, flags = Instrument.FLAG_GETSET, units = 'V', format = '%.3f')
        self.add_parameter('GreenAOMAWGcalibration_k', type = types.FloatType, flags = Instrument.FLAG_GETSET, format = '%.3f')
        self.add_parameter('RedAOMcalibration_a', type = types.FloatType, flags = Instrument.FLAG_GETSET, units = 'mW', format = '%.3f')
        self.add_parameter('RedAOMcalibration_xc', type = types.FloatType, flags = Instrument.FLAG_GETSET, units = 'V', format = '%.3f')
        self.add_parameter('RedAOMcalibration_k', type = types.FloatType, flags = Instrument.FLAG_GETSET, format = '%.3f')
        self.add_parameter('AOMonADwin',type=types.BooleanType,flags=Instrument.FLAG_GETSET)
        self.add_parameter('LT_settings',type=types.IntType,flags=Instrument.FLAG_GETSET)
        self.add_parameter('z_Position', type = types.FloatType, flags = Instrument.FLAG_GETSET, format = '%.3f')
        self.add_parameter('TemperatureA', type = types.FloatType, flags = Instrument.FLAG_GET, format = '%.3f')
        self.add_parameter('TemperatureB', type = types.FloatType, flags = Instrument.FLAG_GET, format = '%.3f')

        self.add_function('SwitchDichroic')
        self.add_function('Channel_A_Block')
        self.add_function('Channel_A_Unblock')
        self.add_function('Channel_B_Block')
        self.add_function('Channel_B_Unblock')
        self.add_function('Newfocus_Laser_Block')
        self.add_function('Newfocus_Laser_Unblock')
        self.add_function('Millennia_Laser_Block')
        self.add_function('Millennia_Laser_Unblock')
        self.add_function('Powermeter_In')
        self.add_function('Powermeter_Out')
        self.add_function('OptimizePolarization')
        self.add_function('Default_Settings')
        self.add_function('CalibrateGreenAOM')
        self.add_function('CalibrateRedAOM')
        self.add_function('NVPowerSaturation')
        self.add_function('OptimizeXY')
        self.add_function('Attocube_Up')
        self.add_function('Attocube_Down')
        self.add_function('Piezo_Mirror_Plus')
        self.add_function('Piezo_Mirror_Minus')

        self.dichroicA = 'green reflector'
        self.dichroicB = 'red and green reflector'
        self.dichroic = self.dichroicA

        self._supported = {
            'get_running': False,
            'get_recording': False,
            'set_running': False,
            'set_recording': False,
            'save': False,
            }

        self._AOMonADwin = True    # green laser AOM is controlled by ADwin    
        self._LT_settings = 0      # 0 for room temperature, 1 for 4K
        self.gr_adwin_a = 0.350       # asymptotic power ( 314.3 microW at 7 V)
        self.gr_adwin_xc = 4.556
        self.gr_adwin_k = 0.8909
        self.gr_awg_a = 0.289
        self.gr_awg_xc = 0.602
        self.gr_awg_k = 6.452
        self.red_a = 0.0014     # power at 1V
        self.red_xc = 0.42581
        self.red_k = 5.5608
        self.servo_channel_powermeter = 0
        self.servo_position_powermeter_in = 810
        self.servo_position_powermeter_out = 700
        #self.servo_position_powermeter_default = self.servo_position_powermeter_out
        self.servo_speed_powermeter = 20

        self.servo_channel_newfocus = 1
        self.servo_position_newfocus_blocked = 780
        self.servo_position_newfocus_unblocked = 500
        #self.servo_position_newfocus_default = self.servo_position_newfocus_blocked
        self.servo_speed_newfocus = 10

        self.servo_channel_detection_ch_B = 2
        self.servo_position_detection_ch_B_blocked = 750
        self.servo_position_detection_ch_B_unblocked = 500
        #self.servo_position_detection_ch_B_default = self.servo_position_detection_ch_B_blocked
        self.servo_speed_detection_ch_B = 20

        self.servo_channel_detection_ch_A = 3
        self.servo_position_detection_ch_A_blocked = 750
        self.servo_position_detection_ch_A_unblocked = 1100
        #self.servo_position_detection_ch_A_default = self.servo_position_detection_ch_A_blocked
        self.servo_speed_detection_ch_A = 20

        #self.get_NewfocusStatus()
        #self.get_DetectionChannelAStatus()
        #self.get_DetectionChannelBStatus()
        #self.get_PowermeterPosition()
        #self.get_Dichroic()
        self.get_PolarizerAngle

    def _sampling_event(self):
        CyclopeanInstrument._sampling_event(self)
        return True

    def _start_running(self):
        CyclopeanInstrument._start_running(self)
        return True

    def _stop_running(self):
        CyclopeanInstrument._stop_running(self)
        return True

    def do_get_AOMonADwin(self):
        return self._AOMonADwin

    def do_set_AOMonADwin(self, val):
        if val == True:
            instruments['ADwin'].Set_DO(7,0)
        else:
            instruments['ADwin'].Set_DO(7,1)
        self._AOMonADwin = val

    def do_get_TemperatureA(self):
        self._TemperatureA = instruments['TemperatureController'].get_kelvinA()
        return self._TemperatureA

    def do_get_TemperatureB(self):
        self._TemperatureB = instruments['TemperatureController'].get_kelvinB()
        return self._TemperatureB

    def do_get_z_Position(self):
        return instruments['ADwin_pos'].get_Z_position()

    def do_set_z_Position(self, val):
        instruments['ADwin_pos'].move_abs_z(val)

    def do_get_LT_settings(self):
        self._LT_settings = instruments['ADwin_pos'].get_LT()
        return self._LT_settings

    def do_set_LT_settings(self, val):
        self._LT_settings = val
        instruments['ADwin_pos'].set_LT(self._LT_settings)

#    def SetGreenAOMCalibration(self,a,xc,k):
#        self.gr_a = a
#        self.gr_xc = xc
#        self.gr_k = k

#    def SetRedAOMCalibration(self,a,xc,k):
#        self.red_a = a
#        self.red_xc = xc
#        self.red_k = k

    def do_get_GreenAOMADwincalibration_a(self):
        return self.gr_adwin_a

    def do_get_GreenAOMADwincalibration_xc(self):
        return self.gr_adwin_xc

    def do_get_GreenAOMADwincalibration_k(self):
        return self.gr_adwin_k

    def do_get_GreenAOMAWGcalibration_a(self):
        return self.gr_awg_a

    def do_get_GreenAOMAWGcalibration_xc(self):
        return self.gr_awg_xc

    def do_get_GreenAOMAWGcalibration_k(self):
        return self.gr_awg_k

    def do_get_RedAOMcalibration_a(self):
        return self.red_a

    def do_get_RedAOMcalibration_xc(self):
        return self.red_xc

    def do_get_RedAOMcalibration_k(self):
        return self.red_k

    def do_set_GreenAOMADwincalibration_a(self,val):
        self.gr_adwin_a = val

    def do_set_GreenAOMADwincalibration_xc(self,val):
        self.gr_adwin_xc = val

    def do_set_GreenAOMADwincalibration_k(self,val):
        self.gr_adwin_k = val

    def do_set_GreenAOMAWGcalibration_a(self,val):
        self.gr_awg_a = val

    def do_set_GreenAOMAWGcalibration_xc(self,val):
        self.gr_awg_xc = val

    def do_set_GreenAOMAWGcalibration_k(self,val):
        self.gr_awg_k = val

    def do_set_RedAOMcalibration_a(self,val):
        self.red_a = val

    def do_set_RedAOMcalibration_xc(self,val):
        self.red_xc = val

    def do_set_RedAOMcalibration_k(self,val):
        self.red_k = val

    def RotateWaveplate(self, angle):
        instruments['ADwin'].Set_FPar(35,angle)
        instruments['ADwin'].Set_Par(35,1)
        while(instruments['ADwin'].Get_Par(35) == 1):
            time.sleep(.1)
        return instruments['ADwin'].Get_FPar(35)

    def do_get_PolarizerAngle(self):
        return self.RotateWaveplate(0)

    def do_set_PolarizerAngle(self, angle):
        self.RotateWaveplate(angle-self.get_PolarizerAngle())

    def OptimizePolarization(self):
        pol = array(zeros(20))
        counts = array(zeros(20))
        pol[0] = self.get_PolarizerAngle()
        counts[0] = self.CountRate(t_int = 500)
        for i in arange(1,20):
            pol[i] = self.RotateWaveplate(5)
            counts[i] = self.CountRate(t_int = 500)
        plot(pol,counts)
        i = counts.argmax()
        self.RotateWaveplate(pol[i]-pol[19])
        self.get_PolarizerAngle()
        return pol[i]

    def CountRate(self,t_int = 100, channel = 0):
        switchoff = 0
        if (instruments['ADwin'].Process_Status(4) == 0):
            instruments['ADwin'].Start_Process(4)
            switchoff = 1
    
        counts = 0
        steps = max(1,int(t_int/100))
        for i in arange(0,steps):
                time.sleep(.1)
                if channel < 4:
                    counts += instruments['ADwin'].Get_Par(41+channel)
                elif channel == 5:  # channel 0 + channel 1
                    counts += instruments['ADwin'].Get_Par(41)
                    counts += instruments['ADwin'].Get_Par(42)

    
        if (switchoff == 1):
            instruments['ADwin'].Stop_Process(4)

        return int(counts / steps)

    def Channel_A_Block(self):
        instruments['Servo'].set_position(self.servo_channel_detection_ch_A,self.servo_speed_detection_ch_A,self.servo_position_detection_ch_A_blocked)
        instruments['Servo'].set_default_position(self.servo_channel_detection_ch_A,self.servo_position_detection_ch_A_blocked)
        self.get_DetectionChannelAStatus()

    def Channel_A_Unblock(self):
        instruments['Servo'].set_position(self.servo_channel_detection_ch_A,self.servo_speed_detection_ch_A,self.servo_position_detection_ch_A_unblocked)
        instruments['Servo'].set_default_position(self.servo_channel_detection_ch_A,self.servo_position_detection_ch_A_unblocked)
        self.get_DetectionChannelAStatus()
    
    def Channel_B_Block(self):
        instruments['Servo'].set_position(self.servo_channel_detection_ch_B,self.servo_speed_detection_ch_B,self.servo_position_detection_ch_B_blocked)
        instruments['Servo'].set_default_position(self.servo_channel_detection_ch_B,self.servo_position_detection_ch_B_blocked)
        self.get_DetectionChannelBStatus()

    def Channel_B_Unblock(self):
        instruments['Servo'].set_position(self.servo_channel_detection_ch_B,self.servo_speed_detection_ch_B,self.servo_position_detection_ch_B_unblocked)
        instruments['Servo'].set_default_position(self.servo_channel_detection_ch_B,self.servo_position_detection_ch_B_unblocked)
        self.get_DetectionChannelBStatus()
    
    def Newfocus_Laser_Block(self):
        instruments['Servo'].set_position(self.servo_channel_newfocus,self.servo_speed_newfocus,self.servo_position_newfocus_blocked)
        instruments['Servo'].set_default_position(self.servo_channel_newfocus,self.servo_position_newfocus_blocked)
        self.get_NewfocusStatus()

    def Newfocus_Laser_Unblock(self):
        instruments['Servo'].set_position(self.servo_channel_newfocus,self.servo_speed_newfocus,self.servo_position_newfocus_unblocked)
        instruments['Servo'].set_default_position(self.servo_channel_newfocus,self.servo_position_newfocus_unblocked)
        self.get_NewfocusStatus()

    def Millennia_Laser_Block(self):
        instruments['MillenniaLaser'].Set_Shutter_Closed()
        self.get_MillenniaStatus()

    def Millennia_Laser_Unblock(self):
        instruments['MillenniaLaser'].Set_Shutter_Open()
        self.get_MillenniaStatus()

    def Powermeter_In(self):
        instruments['Servo'].set_position(self.servo_channel_powermeter,self.servo_speed_powermeter,self.servo_position_powermeter_in)
        instruments['Servo'].set_default_position(self.servo_channel_powermeter,self.servo_position_powermeter_in)
        self.get_PowermeterPosition()

    def Powermeter_Out(self):
        instruments['Servo'].set_position(self.servo_channel_powermeter,self.servo_speed_powermeter,self.servo_position_powermeter_out)
        instruments['Servo'].set_default_position(self.servo_channel_powermeter,self.servo_position_powermeter_out)
        self.get_PowermeterPosition()

    def SwitchDichroic(self):
        instruments['ADwin'].Set_Par(34,1)
        if self.dichroic == self.dichroicA:
            self.dichroic = self.dichroicB
        else:
            self.dichroic = self.dichroicA

        self.get_Dichroic()

    def SwitchDichroic(self):
        instruments['ADwin'].Set_Par(34,1)
        if self.dichroic == self.dichroicA:
            self.dichroic = self.dichroicB
        else:
            self.dichroic = self.dichroicA

        self.get_Dichroic()

    def Default_Settings(self):
        instruments['AWG'].stop()
        instruments['AWG'].set_runmode('cont')
        instruments['AWG'].import_and_load_waveform_file_to_channel(1,'*DC','DC')
        instruments['AWG'].import_and_load_waveform_file_to_channel(2,'*DC','DC')
        instruments['AWG'].import_and_load_waveform_file_to_channel(3,'*DC','DC')
        instruments['AWG'].set_ch1_amplitude(0.02)
        instruments['AWG'].set_ch1_offset(0.0)
        instruments['AWG'].set_ch2_amplitude(0.02)
        instruments['AWG'].set_ch2_offset(0)
        instruments['AWG'].set_ch3_amplitude(0.02)
        instruments['AWG'].set_ch3_offset(0)
        instruments['AWG'].set_ch2_marker1_low(1)
        instruments['AWG'].set_ch1_marker2_low(0)

        instruments['ADwin'].Stop_Process(5)
        instruments['ADwin'].Stop_Process(9)
        instruments['ADwin'].Stop_Process(4)
        instruments['ADwin'].Load('D:\\Lucio\\ADwin codes\\ADwin_Gold_II\\simple_counting.tb4')
        instruments['ADwin'].Set_Par(24,100)
        time.sleep(0.1)
        instruments['ADwin'].Start_Process(4)
        instruments['ADwin'].Set_DAC_Voltage(4,7)
        self.Powermeter_Out()
        print('default settings loaded')

    def Attocube_Up(self):
        instruments['AttoPositioner'].PositionerMoveSingleStep(0,0)

    def Attocube_Down(self):
        instruments['AttoPositioner'].PositionerMoveSingleStep(0,1)

    def Piezo_Mirror_Plus(self,controller,channel,axis,steps):
        if controller == 1: 
            instruments['PiezoMirrorA'].SetChannel(channel)
            instruments['PiezoMirrorA'].MoveRelative(axis,steps)
        elif controller == 2:
            instruments['PiezoMirrorB'].SetChannel(channel)
            instruments['PiezoMirrorB'].MoveRelative(axis,steps)

    def Piezo_Mirror_Minus(self,controller,channel,axis,steps):
        if controller == 1: 
            instruments['PiezoMirrorA'].SetChannel(channel)
            instruments['PiezoMirrorA'].MoveRelative(axis,-1*steps)
        elif controller == 2:
            instruments['PiezoMirrorB'].SetChannel(channel)
            instruments['PiezoMirrorB'].MoveRelative(axis,-1*steps)

    def SimpleCalibrateGreenAOM(self):
        if self._AOMonADwin == True:
            instruments['ADwin'].Set_DAC_Voltage(4,7)
            power = self.get_PowerGreen()
            self.set_GreenAOMADwincalibration_a(power*1000.0*350.0/314.3)
        else:
            if instruments['AWG'].get_runmode() == 'CONT':
                instruments['AWG'].set_ch2_marker1_low(1)
                power = self.get_PowerGreen()
                self.set_GreenAOMAWGcalibration_a(power*1000.0*350.0/314.3)
            else:
                print('sorry, cannot calibrate red AOM in AWG sequence mode')

    def SimpleCalibrateRedAOM(self):
        if instruments['AWG'].get_runmode() == 'CONT':
            instruments['AWG'].set_ch2_offset(1)
            power = self.get_PowerRed()
            self.set_RedAOMcalibration_a(power*1000.0)
        else:
            print('sorry, cannot calibrate red AOM in AWG sequence mode')

    def CalibrateRedAOM(self, steps = 21, V_max = 1.0):
        if instruments['AWG'].get_runmode() != 'CONT':
            print('sorry, cannot calibrate red AOM in AWG sequence mode')
            return False
        if V_max > 1.0:
            print('Warning: tried to set AOM voltage to > 1.0V on AWG! Set max. voltage to 1.0V.')
            V_max = 1.0
        x = arange(0,steps)
        y = zeros(steps,dtype = float)
        self.set_PowermeterPosition('in')
        self.set_NewfocusStatus('blocked')
        self.set_MillenniaStatus('blocked')
        instruments['PM'].set_wavelength(637e-9)
        instruments['AWG'].set_ch2_offset(0)
        time.sleep(2)
        bg = instruments['PM'].get_power()
        self.set_NewfocusStatus('unblocked')
        time.sleep(0.5)
        for a in x:
            instruments['AWG'].set_ch2_offset(a*V_max/steps)
            time.sleep(1)
            y[a] = instruments['PM'].get_power() - bg
        x = x/float(steps-1)*V_max
        y = y*1e3
        self.set_PowermeterPosition('out')
        p_init = [ max(y), self.get_RedAOMcalibration_xc(), self.get_RedAOMcalibration_k()]
        p_fit = fit.fit_AOMfunction(x,y,p_init)
        self.set_RedAOMcalibration_a(p_fit[0][0])
        self.set_RedAOMcalibration_xc(p_fit[0][1])
        self.set_RedAOMcalibration_k(p_fit[0][2])

        result=open('..\\data\\latest\\AOM_calibration\\RedAOM.txt', 'w')
        result.write('# a: %s\n'%p_fit[0][0])
        result.write('# xc: %s\n'%p_fit[0][1])
        result.write('# k: %s\n'%p_fit[0][2])
        result.write('\n')
        for a in arange(0,steps):
            result.write('%s\t%s\n' % (x[a],y[a]))
        result.close()

        calibration = open('LoadRedAOMCalibration.py', 'w')
        calibration.write('TheSetup.set_RedAOMcalibration_a(%s)\n'%p_fit[0][0])
        calibration.write('TheSetup.set_RedAOMcalibration_xc(%s)\n'%p_fit[0][1])
        calibration.write('TheSetup.set_RedAOMcalibration_k(%s)\n'%p_fit[0][2])
        calibration.close()

        print ('red laser calibration finished')
        return True

    def NVPowerSaturation(self, steps = 21, P_max = 300.0, t_int = 1000, delta_x = -1.0, delta_y = 0.0, name = 'NV'):
        ADwin_pos = instruments['ADwin_pos']

        self.set_NewfocusStatus('blocked')
        self.set_PowermeterPosition('out')
        self.set_MillenniaStatus('unblocked')
        x = arange(0,steps)
        y_NV = zeros(steps,dtype = float)
        y_BG = zeros(steps,dtype = float)

        current_x = ADwin_pos.get_X_position()
        current_y = ADwin_pos.get_Y_position()


        ADwin_pos.move_abs_xy(current_x, current_y)
        #self.OptimizeXY()
        self.set_PowerGreen(0)
        time.sleep(1)

        for a in x:
            self.set_PowerGreen(float(P_max*1e-6)/(steps-1)*a)
            y_NV[a] = self.CountRate(t_int = 1000, channel = 5)
            #sleep(t_int/1000)
            #y_NV[a] = PH_300.get_CountRate0()+PH_300.get_CountRate1()
            print 'step %s, counts %s'%(a,y_NV[a])
        
        ADwin_pos.move_abs_xy(current_x + delta_x, current_y + delta_y)
        self.set_PowerGreen(0)
        time.sleep(1)

        for a in x:
            self.set_PowerGreen(float(P_max*1e-6)/(steps-1)*a)
            y_BG[a] = self.CountRate(t_int = 1000, channel = 5)
            #sleep(t_int/1000)
            #y_BG[a] = PH_300.get_CountRate0()+PH_300.get_CountRate1()
            print 'step %s, counts %s'%(a,y_BG[a])
        

    
        x_axis = x/float(steps-1)*P_max
    
        p_init = [400000, 80]
        p_fit = fit.fit_SaturationFunction(x_axis,y_NV-y_BG,p_init)
    
        path = config['datadir'] + '\\'+time.strftime('%Y%m%d') + '\\' + time.strftime('%H%M%S', time.localtime()) + '_saturation_'+name+'\\'
        if not os.path.isdir(path):
            os.makedirs(path)
        result = open(path+'powerdependence_'+name+'.dat', 'w')
        result.write('# r_max (cps): %s\n'%p_fit[0][0])
        result.write('# p_sat (mW):  %s\n'%(p_fit[0][1]/1000.0))
        result.write('\n')
        result.write('# P (mW)\tr (cps)\tbg (cps)\tr_NV (cps)\n')
        for a in x:
            result.write('%.4f\t%.1f\t%.1f\t%.1f\n'%(x_axis[a]/1000.0,y_NV[a],y_BG[a],(y_NV[a]-y_BG[a])))
        result.close()
    
        print ('maximum count rate: %.1f cps, saturation power: %.1f microwatt'%(p_fit[0][0],p_fit[0][1]))

        fig = plt.figure()
        dat = fig.add_subplot(111)
        x = x_axis/1000.0
        y = y_NV-y_BG
        dat = dat.plot(x,y,'r.')
        plt.xlabel('Excitation power (mW)')
        plt.ylabel('counts / s (background subtracted)')
        plt.title('power saturation '+name+',\nP_sat = '+str(int(p_fit[0][1])/1000.0)+'mW, R_sat = '+str(int(p_fit[0][0])   )+' counts/s')
        fig.savefig(path + 'powerdependence_'+name+'.png')
        

    def CalibrateGreenAOM(self, steps = 21, V_max = 1.0):
        if self._AOMonADwin == False:
            if instruments['AWG'].get_runmode() != 'CONT':
                print('sorry, cannot calibrate green AOM in AWG sequence mode')
                return(False)
            else:
                instruments['AWG'].set_ch2_marker1_low(0)
                if V_max > 1.0:
                    print('Warning: tried to set AOM voltage to > 1.0V on AWG! Set max. voltage to 1.0V.')
                    V_max = 1.0
        else:
            instruments['ADwin'].Set_DAC_Voltage(4,0)
            if V_max > 10.0:
                print('Warning: tried to set AOM voltage to > 8.5V on ADwin! Set max. voltage to 8.5V.')
                V_max = 8.5


        x = arange(0,steps)
        y = zeros(steps,dtype = float)
        self.set_PowermeterPosition('in')
        self.set_NewfocusStatus('blocked')
        self.set_MillenniaStatus('blocked')
        instruments['PM'].set_wavelength(532e-9)
        time.sleep(2)
        bg = instruments['PM'].get_power()
        self.set_MillenniaStatus('unblocked')
        time.sleep(0.5)
        for a in x:
            if self._AOMonADwin == True:
                instruments['ADwin'].Set_DAC_Voltage(4,a*V_max/steps)
            else:
                instruments['AWG'].set_ch2_marker1_low(a*V_max/steps)
            time.sleep(1)              #previousely 1)
            y[a] = instruments['PM'].get_power() - bg
        x = x/float(steps-1)*V_max
        y = y*1e3
        self.set_PowermeterPosition('out')

        path = config['datadir'] + '\\'+time.strftime('%Y%m%d') + '\\' + time.strftime('%H%M%S', time.localtime()) + '_AOM_calibration\\'
        if not os.path.isdir(path):
            os.makedirs(path)
        
        if self._AOMonADwin == True:
            p_init = [ max(y)
                , self.get_GreenAOMADwincalibration_xc(), self.get_GreenAOMADwincalibration_k()]
            p_fit = fit.fit_AOMfunction(x,y,p_init)
            self.set_GreenAOMADwincalibration_a(p_fit[0][0])
            self.set_GreenAOMADwincalibration_xc(p_fit[0][1])
            self.set_GreenAOMADwincalibration_k(p_fit[0][2])
            result=open(path+'\\GreenAOMADwin.txt', 'w')
        else:
            p_init = [ max(y)
                , self.get_GreenAOMAWGcalibration_xc(), self.get_GreenAOMAWGcalibration_k()]
            p_fit = fit.fit_AOMfunction(x,y,p_init)
            self.set_GreenAOMAWGcalibration_a(p_fit[0][0])
            self.set_GreenAOMAWGcalibration_xc(p_fit[0][1])
            self.set_GreenAOMAWGcalibration_k(p_fit[0][2])
            result=open(path+'\\GreenAOMAWG.txt', 'w')

        result.write('# a: %s\n'%p_fit[0][0])
        result.write('# xc: %s\n'%p_fit[0][1])
        result.write('# k: %s\n'%p_fit[0][2])
        result.write('\n')
        result.write('# U (V)\tP (mW)\n')
        for a in arange(0,steps):
            result.write('%s\t%s\n' % (x[a],y[a]))
        result.close()

        if self._AOMonADwin == True:
            calibration = open('LoadGreenAOMADwinCalibration.py', 'w')
            calibration.write('TheSetup.set_GreenAOMADwincalibration_a(%s)\n'%p_fit[0][0])
            calibration.write('TheSetup.set_GreenAOMADwincalibration_xc(%s)\n'%p_fit[0][1])
            calibration.write('TheSetup.set_GreenAOMADwincalibration_k(%s)\n'%p_fit[0][2])
        else:
            calibration = open('LoadGreenAOMAWGCalibration.py', 'w')
            calibration.write('TheSetup.set_GreenAOMAWGcalibration_a(%s)\n'%p_fit[0][0])
            calibration.write('TheSetup.set_GreenAOMAWGcalibration_xc(%s)\n'%p_fit[0][1])
            calibration.write('TheSetup.set_GreenAOMAWGcalibration_k(%s)\n'%p_fit[0][2])
        calibration.close()

        print ('green laser calibration finished')

        return True

    def OptimizeZ(self, focus_distance = 1.0, int_time = 30, steps = 50, counter = 5):
        ADwin = instruments['ADwin']
        ADwin_pos = instruments['ADwin_pos']

        ADwin.Load('D:\\Lucio\\AdWin codes\\ADwin_Gold_II\\simple_linescan.TB2')
    
        switchon = 0
        if (ADwin.Process_Status(4) == 1):
            ADwin.Stop_Process(4)
            switchon = 1
    
        current_z = ADwin_pos.get_Z_position()
        
        ADwin_pos.move_abs_z(current_z - focus_distance/2.0)

        ADwin.Set_FPar(20,ADwin_pos.pos_to_U_z(current_z-focus_distance/2.0))
        ADwin.Set_FPar(21,ADwin_pos.pos_to_U_z(current_z+focus_distance/2.0))
        ADwin.Set_Par(24,int_time)
        ADwin.Set_Par(20,steps)
        ADwin.Set_Par(25,3)
    
        ADwin.Start_Process(2)
        while (ADwin.Process_Status(2) > 0):
            time.sleep(.01)
    
        if counter < 5:
            OptimizeZ = ADwin.Get_Data_Long(counter,1,steps)/int_time
        else:
            OptimizeZ = ADwin.Get_Data_Long(1,1,steps)/int_time + ADwin.Get_Data_Long(2,1,steps)/int_time

        if (switchon == 1):
            ADwin.Set_Par(24,100)
            ADwin.Start_Process(4)
    
        p_init = [float(steps/2), float(max(OptimizeZ)), float(min(OptimizeZ)), float(steps/4)]
        p_fit = fit.fit_gaussian2(arange(0,steps),OptimizeZ,p_init)
    
        z_fit = current_z + (p_fit[0][0]-float(steps-1.0)/2.0)/float(steps)*focus_distance
    
        if abs(z_fit-current_z)>focus_distance:
            z_fit = current_z
    
        ADwin_pos.move_abs_z(z_fit)
        self.get_z_Position()

        return z_fit

    def plot2D(self, path, i, scan2D, x_start, x_stop, y_start, y_stop, z_pos):
        fig = plt.figure()
        dat = fig.add_subplot(111)
        x_steps = len(scan2D)
        y_steps = len(scan2D[0])
        x = arange(0,x_steps)*(x_stop-x_start)/(x_steps-1)+x_start
        y = arange(0,y_steps)*(y_stop-y_start)/(y_steps-1)+y_start
        dat.pcolor(x,y,transpose(scan2D),cmap = 'hot')
        plt.xlabel('x (mu)')        	
        plt.ylabel('y (mu)')        	
        plt.title('2D scan at z = %s mu, max %s cps'%(z_pos, scan2D.max()))        	
        fig.savefig(path+'\\scan2D_'+str(i)+'.png')

    def plot2D_2(self, path, i, scan2D_A, scan2D_B, x_start, x_stop, y_start, y_stop, z_pos):
        fig = plt.figure()
        x_steps = len(scan2D_A)
        y_steps = len(scan2D_A[0])
        x = arange(0,x_steps)*(x_stop-x_start)/(x_steps-1)+x_start
        y = arange(0,y_steps)*(y_stop-y_start)/(y_steps-1)+y_start
        plot_A = fig.add_subplot(121)
        plot_A.pcolor(x,y,transpose(scan2D_A),cmap = 'hot')
        plot_A.set_xlabel('x (mu)')        	
        plot_A.set_ylabel('y (mu)')        	
        plot_A.set_title('Channel A:\n2D scan at z = %.3f mu,\nmax %.1f cps'%(z_pos, scan2D_A.max()))        	
        plot_B = fig.add_subplot(122)
        plot_B.pcolor(x,y,transpose(scan2D_B),cmap = 'hot')
        plot_B.set_xlabel('x (mu)')        	
        plot_B.set_ylabel('y (mu)')        	
        plot_B.set_title('Channel B:\n2D scan at z = %.3f mu,\nmax %.1f cps'%(z_pos, scan2D_B.max()))        	
        fig.savefig(path+'\\scan2D_'+str(i)+'.png')

    def Scan3D(self, x_start,x_stop,x_steps,y_start,y_stop,y_steps,z_start,z_stop,z_steps,t_int, 
            relative_pos = True, counter = 5,scanbothchannels=False):
        path = config['datadir'] + '\\'+time.strftime('%Y%m%d') + '\\' + time.strftime('%H%M%S', time.localtime()) + '_3D_Scan\\'
        if not os.path.isdir(path):
            os.makedirs(path)

        settings = open(path+'settings.txt', 'w')
        settings.write('# x-min, x_max [mu], x-steps\n')
        settings.write('%s\t%s\t%s\n'%(x_start, x_stop, x_steps))
        settings.write('# y-min, y_max [mu], y-steps\n')
        settings.write('%s\t%s\t%s\n'%(y_start, y_stop, y_steps))
        settings.write('# z-min, z_max [mu], z-steps\n')
        settings.write('%s\t%s\t%s\n'%(z_start, z_stop, z_steps))
        settings.write('# integration time (ms)\n')
        settings.write('%s\n'%(t_int))
        settings.write('# scanning both channels\n')
        settings.write('%s\n'%(scanbothchannels))
        settings.close()

        ADwin = instruments['ADwin']
        ADwin_pos = instruments['ADwin_pos']

        switchon = 0
        if (ADwin.Process_Status(4) == 1):
            ADwin.Stop_Process(4)
            switchon = 1

        if (relative_pos == True):
            current_x = ADwin_pos.get_X_position()
            current_y = ADwin_pos.get_Y_position()
            current_z = ADwin_pos.get_Z_position()
        else:
            current_x = 0
            current_y = 0
            current_z = 0

        ADwin.Load(ADwin.program_path()+'\\simple_linescan.TB2')
        for i in arange(0,z_steps):
            z_pos = current_z + z_start + i * ((z_stop - z_start) / (z_steps - 1))
            ADwin_pos.move_abs_z(z_pos)
            print ('scan %s, pos %s'%(i,z_pos))
            scan2D_A = zeros((x_steps,y_steps))
            scan2D_B = zeros((x_steps,y_steps))
            if scanbothchannels == True:
                repeat = 2
            else:
                repeat = 1
            for k in arange(0,repeat):
                if (scanbothchannels == True):
                    if (k == 0):
                        self.Channel_A_Unblock()
                        self.Channel_B_Block()
                    else:
                        self.Channel_B_Unblock()
                        self.Channel_A_Block()
                for j in arange(0,y_steps):
                    ADwin_pos.move_abs_xy(current_x + x_start, current_y + y_start + j * ((y_stop - y_start) / (y_steps - 1)))
                    ADwin.Set_FPar(20,ADwin_pos.pos_to_U_x(current_x + x_start))
                    ADwin.Set_FPar(21,ADwin_pos.pos_to_U_x(current_x + x_stop))
                    ADwin.Set_Par(24,t_int)
                    ADwin.Set_Par(20,x_steps)
                    ADwin.Set_Par(25,1)
                    ADwin.Start_Process(2)
                    while (ADwin.Process_Status(2) > 0):
                        time.sleep(.01)
                    if k == 0:
                        if counter < 5:
                            scan2D_A [:,j] = ADwin.Get_Data_Long(counter,1,x_steps)
                        else:
                            scan2D_A [:,j] = ADwin.Get_Data_Long(1,1,x_steps)/t_int + ADwin.Get_Data_Long(2,1,x_steps)/t_int
                    else:
                        if counter < 5:
                            scan2D_B [:,j] = ADwin.Get_Data_Long(counter,1,x_steps)
                        else:
                            scan2D_B [:,j] = ADwin.Get_Data_Long(1,1,x_steps)/t_int + ADwin.Get_Data_Long(2,1,x_steps)/t_int
            result=open(path+'scan2D_A'+str(i)+'.dat', 'w')
            for j in arange(0,y_steps):
                for k in arange(0,x_steps):
                    result.write('%.2f'%(scan2D_A[k,j]))
                    if k < x_steps - 1:
                        result.write('\t')
            result.write('\n')
            result.close()
            if scanbothchannels == True:
                result=open(path+'scan2D_B'+str(i)+'.dat', 'w')
                for j in arange(0,y_steps):
                    for k in arange(0,x_steps):
                        result.write('%.2f'%(scan2D_B[k,j]))
                        if k < x_steps - 1:
                            result.write('\t')
                result.write('\n')
                result.close()
                self.plot2D_2(path,i,scan2D_A,scan2D_B,x_start,x_stop,y_start,y_stop, z_pos)    
            else:
                self.plot2D(path,i,scan2D_A,x_start,x_stop,y_start,y_stop, z_pos)    
        if (relative_pos == True):
            ADwin_pos.move_abs_xyz(current_x, current_y, current_z)
        else:		    
            ADwin_pos.move_abs_xyz(x_start + (x_stop - x_start) * 0.5,
                                   y_start + (y_stop - y_start) * 0.5,
                                   z_start + (z_stop - z_start) * 0.5)
        if (switchon == 1):
            ADwin.Set_Par(24,100)
            ADwin.Start_Process(4)

    def OptimizeXY(self, focus_distance = 1.0, int_time = 30, steps = 50, counter = 5):
        ADwin = instruments['ADwin']
        ADwin_pos = instruments['ADwin_pos']

        ADwin.Load('D:\\Lucio\\AdWin codes\\ADwin_Gold_II\\simple_linescan.TB2')
    
        switchon = 0
        if (ADwin.Process_Status(4) == 1):
            ADwin.Stop_Process(4)
            switchon = 1
    
        current_x = ADwin_pos.get_X_position()
        current_y = ADwin_pos.get_Y_position()
        
        ADwin_pos.move_abs_xy(current_x - focus_distance/2.0, current_y)

        ADwin.Set_FPar(20,ADwin_pos.pos_to_U_x(current_x-focus_distance/2.0))
        ADwin.Set_FPar(21,ADwin_pos.pos_to_U_x(current_x+focus_distance/2.0))
        ADwin.Set_Par(24,int_time)
        ADwin.Set_Par(20,steps)
        ADwin.Set_Par(25,1)
    
        ADwin.Start_Process(2)
        while (ADwin.Process_Status(2) > 0):
            time.sleep(.01)
    
        if counter < 5:
            OptimizeX = ADwin.Get_Data_Long(counter,1,steps)/int_time
        else:
            OptimizeX = ADwin.Get_Data_Long(1,1,steps)/int_time + ADwin.Get_Data_Long(2,1,steps)/int_time

        ADwin_pos.move_abs_xy(current_x,current_y - focus_distance/2.0)
 
        ADwin.Set_FPar(20,ADwin_pos.pos_to_U_y(current_y-focus_distance/2.0))
        ADwin.Set_FPar(21,ADwin_pos.pos_to_U_y(current_y+focus_distance/2.0))
        ADwin.Set_Par(25,2)
    
        ADwin.Start_Process(2)
        while (ADwin.Process_Status(2) > 0):
            time.sleep(.01)
    
        if counter < 5:
            OptimizeY = ADwin.Get_Data_Long(counter,1,steps)/int_time
        else:
            OptimizeY = ADwin.Get_Data_Long(1,1,steps)/int_time + ADwin.Get_Data_Long(2,1,steps)/int_time
    
        if (switchon == 1):
            ADwin.Set_Par(24,100)
            ADwin.Start_Process(4)
    
        p_init = [float(steps/2), float(max(OptimizeX)), float(min(OptimizeX)), float(steps/4)]
        p_fit = fit.fit_gaussian2(arange(0,steps),OptimizeX,p_init)
    
        #plot(OptimizeX)
        #plot(gaussian2(arange(0,steps),p_fit[0][0],p_fit[0][1],p_fit[0][2],p_fit[0][3]))
    
        x_fit = current_x + (p_fit[0][0]-float(steps-1.0)/2.0)/float(steps)*focus_distance
    
        p_init = [float(steps/2), float(max(OptimizeY)), float(min(OptimizeY)), float(steps/4)]
        p_fit = fit.fit_gaussian2(arange(0,steps),OptimizeY,p_init)
    
        #plot(OptimizeY)
        #plot(gaussian2(arange(0,steps),p_fit[0][0],p_fit[0][1],p_fit[0][2],p_fit[0][3]))
    
        y_fit = current_y + (p_fit[0][0]-float(steps-1.0)/2.0)/float(steps)*focus_distance
    
        if abs(x_fit-current_x)>focus_distance:
            x_fit = current_x
        if abs(y_fit-current_y)>focus_distance:
            y_fit = current_y
    
        ADwin_pos.move_abs_xy(x_fit,y_fit)

        return x_fit, y_fit

    def do_get_Dichroic(self):
        '''
        Get the used dichroic

        Input:
            none

        Output:
            position (string) : 'green reflector' or 'red and green reflector'
        '''
    
        logging.debug(__name__ + ' : reading used dichroic')
        return self.dichroic

    def do_get_PowermeterPosition(self):
        '''
        Get position of powermeter

        Input:
            none

        Output:
            position (string) : 'in' or 'out'
        '''
    
        logging.debug(__name__ + ' : reading powermeter position')
        position = instruments['Servo'].get_position(self.servo_channel_powermeter)
        if position == self.servo_position_powermeter_in:
            return 'in'
        else:
            return 'out'

    def do_set_PowermeterPosition(self, position):
        '''
        Set position of powermeter
    
        Input:
            position (string) : 'in' or 'out'
    
        Output:
            none
        '''
    
        logging.debug(__name__ + ' : setting powermeter position to "%s"' % position)
        if position.upper() in ('IN', 'OUT'):
            position = position.upper()
        else:
            raise ValueError('set_PowermeterPosition(): can only set in or out')
        if position == 'IN':
            self.Powermeter_In()
        else:
            self.Powermeter_Out()

    def do_get_NewfocusStatus(self):
        '''
        Get status of Newfocus Laser

        Input:
            none

        Output:
            status (string) : 'blocked' or 'unblocked'
        '''
    
        logging.debug(__name__ + ' : reading newfocus status')
        position = instruments['Servo'].get_position(self.servo_channel_newfocus)
        if position == self.servo_position_newfocus_blocked:
            return 'blocked'
        else:
            return 'unblocked'

    def do_set_NewfocusStatus(self, status):
        '''
        Set status of Newfocus Laser
    
        Input:
            status (string) : 'blocked' or 'unblocked'
    
        Output:
            none
        '''
    
        logging.debug(__name__ + ' : setting newfocus status to "%s"' % status)
        if status.upper() in ('BLOCKED', 'UNBLOCKED'):
            status = status.upper()
        else:
            raise ValueError('set_NewfocusStatus(): can only set blocked or unblocked')
        if status == 'BLOCKED':
            self.Newfocus_Laser_Block()
        else:
            self.Newfocus_Laser_Unblock()

    def do_get_MillenniaStatus(self):
        '''
        Get status of Millennia Laser

        Input:
            none

        Output:
            status (string) : 'blocked' or 'unblocked'
        '''
    
        logging.debug(__name__ + ' : reading millennia status')
        position = instruments['MillenniaLaser'].Get_Shutter_State()
        if position == '0':
            return 'blocked'
        else:
            return 'unblocked'

    def do_set_MillenniaStatus(self, status):
        '''
        Set status of Millennia Laser
    
        Input:
            status (string) : 'blocked' or 'unblocked'
    
        Output:
            none
        '''
    
        logging.debug(__name__ + ' : setting millennia status to "%s"' % status)
        if status.upper() in ('BLOCKED', 'UNBLOCKED'):
            status = status.upper()
        else:
            raise ValueError('set_MillenniaStatus(): can only set blocked or unblocked')
        if status == 'BLOCKED':
            instruments['MillenniaLaser'].Set_Shutter_Closed()
        else:
            instruments['MillenniaLaser'].Set_Shutter_Open()

    def do_get_DetectionChannelAStatus(self):
        '''
        Get status of Detection Channel A

        Input:
            none

        Output:
            status (string) : 'blocked' or 'unblocked'
        '''
    
        logging.debug(__name__ + ' : reading detection channel a status')
        position = instruments['Servo'].get_position(self.servo_channel_detection_ch_A)
        if position == self.servo_position_detection_ch_A_blocked:
            return 'blocked'
        else:
            return 'unblocked'

    def do_set_DetectionChannelAStatus(self, status):
        '''
        Set status of Detection Channel A
    
        Input:
            status (string) : 'blocked' or 'unblocked'
    
        Output:
            none
        '''
    
        logging.debug(__name__ + ' : setting detection channel a status to "%s"' % status)
        if status.upper() in ('BLOCKED', 'UNBLOCKED'):
            status = status.upper()
        else:
            raise ValueError('set_DetectionChannelA(): can only set blocked or unblocked')
        if status == 'BLOCKED':
            self.Channel_A_Block()
        else:
            self.Channel_A_Unblock()

    def do_get_DetectionChannelBStatus(self):
        '''
        Get status of Detection Channel B

        Input:
            none

        Output:
            status (string) : 'blocked' or 'unblocked'
        '''
    
        logging.debug(__name__ + ' : reading detection channel b status')
        position = instruments['Servo'].get_position(self.servo_channel_detection_ch_B)
        if position == self.servo_position_detection_ch_B_blocked:
            return 'blocked'
        else:
            return 'unblocked'

    def do_set_DetectionChannelBStatus(self, status):
        '''
        Set status of Detection Channel B
    
        Input:
            status (string) : 'blocked' or 'unblocked'
    
        Output:
            none
        '''
    
        logging.debug(__name__ + ' : setting detection channel b status to "%s"' % status)
        if status.upper() in ('BLOCKED', 'UNBLOCKED'):
            status = status.upper()
        else:
            raise ValueError('set_DetectionChannelB(): can only set blocked or unblocked')
        if status == 'BLOCKED':
            self.Channel_B_Block()
        else:
            self.Channel_B_Unblock()

    def do_get_PowerBackground(self):
        NS = self.get_NewfocusStatus()
        MS = self.get_MillenniaStatus()
        PP = self.get_PowermeterPosition()
        self.set_NewfocusStatus('blocked')
        self.set_MillenniaStatus('blocked')
        self.set_PowermeterPosition('in')
        time.sleep(3)
        power = instruments['PM'].get_power()
        self.set_NewfocusStatus(NS)
        self.set_MillenniaStatus(MS)
        self.set_PowermeterPosition(PP)
        return power

    def do_get_PowerRed(self):
        NS = self.get_NewfocusStatus()
        MS = self.get_MillenniaStatus()
        PP = self.get_PowermeterPosition()
        self.set_NewfocusStatus('blocked')
        self.set_MillenniaStatus('blocked')
        self.set_PowermeterPosition('in')
        instruments['PM'].set_wavelength(637e-9)
        time.sleep(3)
        bg = instruments['PM'].get_power()
        self.set_NewfocusStatus('unblocked')
        time.sleep(3)
        power = instruments['PM'].get_power()
        self.set_NewfocusStatus(NS)
        self.set_MillenniaStatus(MS)
        self.set_PowermeterPosition(PP)
        return power - bg

    def FocusDown(self, IntTime = 1000, SequentialSteps = 5, StepVoltage = 20.0, Channel = 5, abort = 0):
        AttoPositioner = instruments['AttoPositioner']

        AttoPositioner.PositionerAmplitude(0,int(StepVoltage*1000))
        max_counts = 0
        max_index = 0
    
        for i in arange(0,SequentialSteps):
            AttoPositioner.PositionerMoveSingleStep(0,1)    # 1 = down
            time.sleep(0.1)
            #AttoPositioner.PositionerMoveSingleStep(0,1)
            #sleep(0.1)
            AttoPositioner.PositionerMoveSingleStep(0,0)    # 0 = up
            time.sleep(0.5)
            self.OptimizeXY()
            counts = self.CountRate(IntTime,Channel)
            if counts > max_counts:
                max_counts = counts
                max_index = i
            current_position = AttoPositioner.PositionerGetPosition(0)
            print('%s %s'%(current_position,counts))
            if (abort > 0) and (counts >= abort):
                break
        return max_counts,max_index,counts

    def FocusUp(self, IntTime = 1000, SequentialSteps = 5, StepVoltage = 20.0, Channel = 5, abort = 0):
        AttoPositioner = instruments['AttoPositioner']

        AttoPositioner.PositionerAmplitude(0,int(StepVoltage*1000))
        max_counts = 0
        max_index = 0
    
        for i in arange(0,SequentialSteps):
            AttoPositioner.PositionerMoveSingleStep(0,0)    # 0 = up
            time.sleep(0.5)
            self.OptimizeXY()
            counts = self.CountRate(IntTime,Channel)
            if counts > max_counts:
                max_counts = counts
                max_index = i
            current_position = AttoPositioner.PositionerGetPosition(0)
            print('%s %s'%(current_position,counts))
            if (abort > 0) and (counts >= abort):
                break

        return max_counts,max_index,counts

    def FindFocus(self, IntTime = 1000, SequentialSteps = 5, FocusReached = 0.9, AbortSteps = 20, StepVoltage = 20.0, Channel = 5, MaxDeviation = 2000):
        AttoPositioner = instruments['AttoPositioner']
        start_counts = self.CountRate(IntTime,Channel)
        start_position = AttoPositioner.PositionerGetPosition(0)
    
        print ('Moving up %s steps to find focus'%SequentialSteps)
        max_up_cts,max_up_idx,new_counts = self.FocusUp(IntTime, SequentialSteps, StepVoltage, Channel)
        max_counts = max_up_cts
    
        current_position = AttoPositioner.PositionerGetPosition(0)
        if (abs(current_position - start_position) > MaxDeviation):
            print ('Warning: deviation from initial z position %s micrometer, probably lost focus.'%(abs(current_position - start_position)/1000))
            return -1
    
        while new_counts > start_counts:
            start_counts = new_counts
            print ('Moving up %s more steps to find focus'%SequentialSteps)
            max_up_cts,max_up_idx,new_counts = self.FocusUp(IntTime, SequentialSteps, StepVoltage, Channel)
            max_counts = max(max_up_cts,max_counts)
            current_position = AttoPositioner.PositionerGetPosition(0)
            if (abs(current_position - start_position) > MaxDeviation):
                print ('Warning: deviation from initial z position %s micrometer, probably lost focus.'%(abs(current_position - start_position)/1000))
                return -1
    
        start_counts = new_counts
        print ('Moving down %s steps to find focus'%SequentialSteps)
        max_down_cts,max_down_idx,new_counts = self.FocusDown(IntTime, SequentialSteps, StepVoltage, Channel)
        max_counts = max(max_down_cts,max_counts)
    
        current_position = AttoPositioner.PositionerGetPosition(0)
        if (abs(current_position - start_position) > MaxDeviation):
            print ('Warning: deviation from initial z position %s micrometer, probably lost focus.'%(abs(current_position - start_position)/1000))
            return -1
    
        while new_counts > start_counts:
            start_counts = new_counts
            print ('Moving down %s more steps to find focus'%SequentialSteps)
            max_down_cts,max_down_idx,new_counts = self.FocusDown(IntTime, SequentialSteps, StepVoltage, Channel)
            max_counts = max(max_down_cts,max_counts)
            current_position = AttoPositioner.PositionerGetPosition(0)
            if (abs(current_position - start_position) > MaxDeviation):
                print ('Warning: deviation from initial z position %s micrometer, probably lost focus.'%(abs(current_position - start_position)/1000))
                return -1
    
        maximum = 0
        while maximum < FocusReached*max_counts:
            print ('Moving up to approach focus at %s cps'%max_counts)
            maximum,idx,new = self.FocusUp(IntTime,AbortSteps,StepVoltage,Channel,FocusReached*max_counts)
            current_position = AttoPositioner.PositionerGetPosition(0)
            if (abs(current_position - start_position) > MaxDeviation):
                print ('Warning: deviation from initial z position %s micrometer, probably lost focus.'%(abs(current_position - start_position)/1000))
                return -1
    
        print('...finished')
        return maximum

    def PiezoMovePlus(self, IntTime = 1000, SequentialSteps = 5, Stepsize = 1, PiezoController = 1, PiezoChannel = 1, PiezoAxis = 1, abort = 0, Channel = 1):
        max_counts = 0
        max_index = 0
    
        for i in arange(0,SequentialSteps):
            self.Piezo_Mirror_Plus(PiezoController, PiezoChannel, PiezoAxis, Stepsize)
            time.sleep(0.1)
            counts = self.CountRate(IntTime,Channel)
            if counts > max_counts:
                max_counts = counts
                max_index = i
            if (abort > 0) and (counts >= abort):
                break

        return max_counts,max_index,counts

    def PiezoMoveMinus(self, IntTime = 1000, SequentialSteps = 5, Stepsize = 1, PiezoController = 1, PiezoChannel = 1, PiezoAxis = 1, abort = 0, Channel = 1):
        max_counts = 0
        max_index = 0
    
        for i in arange(0,SequentialSteps):
            self.Piezo_Mirror_Minus(PiezoController, PiezoChannel, PiezoAxis, Stepsize)
            time.sleep(0.1)
            counts = self.CountRate(IntTime,Channel)
            if counts > max_counts:
                max_counts = counts
                max_index = i
            if (abort > 0) and (counts >= abort):
                break

        return max_counts,max_index,counts


    def PiezoFindMax(self,IntTime = 1000, SequentialSteps = 5, Stepsize = 1, MaxReached = 0.9, AbortSteps = 20, PiezoController = 1, PiezoChannel = 1, PiezoAxis = 1, Channel = 5):

        start_counts = self.CountRate(IntTime,Channel)
    
        print ('Moving +%s steps to find maximum'%SequentialSteps)
        max_up_cts,max_up_idx,new_counts = self.PiezoMovePlus(IntTime, SequentialSteps, Stepsize, PiezoController, PiezoChannel, PiezoAxis, 0, Channel)
        max_counts = max_up_cts
    
        while new_counts > start_counts:
            start_counts = new_counts
            print ('Moving +%s more steps to find maximum'%SequentialSteps)
            max_up_cts,max_up_idx,new_counts = self.PiezoMovePlus(IntTime, SequentialSteps, Stepsize, PiezoController, PiezoChannel, PiezoAxis, 0, Channel)
            max_counts = max(max_up_cts,max_counts)
    
        start_counts = new_counts
        print ('Moving -%s steps to find maximum'%SequentialSteps)
        max_down_cts,max_down_idx,new_counts = self.PiezoMoveMinus(IntTime, SequentialSteps, Stepsize, PiezoController, PiezoChannel, PiezoAxis, 0, Channel)
        max_counts = max(max_down_cts,max_counts)
    
        while new_counts > start_counts:
            start_counts = new_counts
            print ('Moving -%s more steps to find maximum'%SequentialSteps)
            max_down_cts,max_down_idx,new_counts = self.PiezoMoveMinus(IntTime, SequentialSteps, Stepsize, PiezoController, PiezoChannel, PiezoAxis, 0, Channel)
            max_counts = max(max_down_cts,max_counts)
    
        maximum = 0
        while maximum < MaxReached*max_counts:
            print ('Moving + to approach focus at %s cps'%max_counts)
            maximum,idx,new = self.PiezoMovePlus(IntTime, SequentialSteps, Stepsize, PiezoController, PiezoChannel, PiezoAxis, MaxReached * max_counts, Channel)

        print('...finished')
        return maximum

    def RedAOMPowerToVoltage(self, P):        # P: power [microW]
        a = self.get_RedAOMcalibration_a()
        xc = self.get_RedAOMcalibration_xc()
        k = self.get_RedAOMcalibration_k()
        if P/1000.0 >= a:
            print('Error, power exceeds maximum!')
            return 0
        elif P <= 0:
            voltage = 0
        else:
            voltage = xc-log(log(1000.0*a/float(P)))/k
            if voltage > 1:
                print('Error, power exceeds maximum!')
                return 0
        return voltage

    def GreenAOMPowerToADwinVoltage(self, P):      # P: power [microW]
        a = self.get_GreenAOMADwincalibration_a()
        xc = self.get_GreenAOMADwincalibration_xc()
        k = self.get_GreenAOMADwincalibration_k()
        if P/1000.0 >= a:
            print('Error, power exceeds maximum!')
            return 0
        elif P <= 0:
            voltage = 0
        else:
            voltage = xc-log(log(1000.0*a/float(P)))/k
            if voltage > 8:
                print('Error, power exceeds maximum!')
                return 0
        return voltage

    def GreenAOMPowerToAWGVoltage(self, P):      # P: power [microW]
        a = self.get_GreenAOMAWGcalibration_a()
        xc = self.get_GreenAOMAWGcalibration_xc()
        k = self.get_GreenAOMAWGcalibration_k()
        if P/1000.0 >= a:
            print('Error, power exceeds maximum!')
            return 0
        elif P <= 0:
            voltage = 0
        else:
            voltage = xc-log(log(1000.0*a/float(P)))/k
            if voltage > 1:
                print('Error, power exceeds maximum!')
                return 0
        return voltage

    def do_set_PowerRed(self, power):           # power [W]
        if instruments['AWG'].get_runmode() == 'CONT':
            voltage = self.RedAOMPowerToVoltage(power*1000000.0)
            instruments['AWG'].set_ch2_offset(voltage)
        else:
            print('sorry, cannot set AOM power in AWG sequence mode')

    def do_set_PowerGreen(self, power):         # power [W]
        if self._AOMonADwin == True:
            voltage = self.GreenAOMPowerToADwinVoltage(power*1000000.0)
            instruments['ADwin'].Set_DAC_Voltage(4,voltage)
        else:
            voltage = self.GreenAOMPowerToAWGVoltage(power*1000000.0)
            instruments['AWG'].set_ch2_marker1_low(voltage)

    def do_get_PowerGreen(self):
        NS = self.get_NewfocusStatus()
        MS = self.get_MillenniaStatus()
        PP = self.get_PowermeterPosition()
        self.set_NewfocusStatus('blocked')
        self.set_MillenniaStatus('blocked')
        self.set_PowermeterPosition('in')
        instruments['PM'].set_wavelength(532e-9)
        time.sleep(3)
        bg = instruments['PM'].get_power()
        self.set_MillenniaStatus('unblocked')
        time.sleep(3)
        power = instruments['PM'].get_power()
        self.set_NewfocusStatus(NS)
        self.set_MillenniaStatus(MS)
        self.set_PowermeterPosition(PP)
        return power - bg



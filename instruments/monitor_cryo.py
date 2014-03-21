import visa
from instrument import Instrument
from monitor_instrument import MonitorInstrument
import types
import qt
import time
import numpy as np
import os
import urllib

class monitor_cryo(MonitorInstrument):
    '''This is a child class of the monitor instrument. 
	It monitors Helium levels and temperature in the LT2 cryostat'''
	
    def __init__(self, name, monitor_lt1=False, **kw):
		
        MonitorInstrument.__init__(self, name)
		
        self._levelmeter = visa.instrument('GPIB::8::INSTR')
        self._keithley =  visa.instrument('GPIB::11::INSTR')
        self._mailer = qt.instruments['gmailer']
        
        self._keithleyMM = qt.instruments['keithleyMM']
        
        self._monitor_lt1=monitor_lt1
        if monitor_lt1:
            self._temp_lt1 = qt.instruments['TemperatureController_lt1']
            self._lt1_positioner = qt.instruments['AttoPositioner_lt1']
            self._adwin_lt1=qt.instruments['adwin_lt1']
				
        self.add_parameter('he2_lvl_min',
                type=types.FloatType,
                flags=Instrument.FLAG_GETSET,
                units='cm')
        
        self.add_parameter('he1_lvl_min',
                type=types.FloatType,
                flags=Instrument.FLAG_GETSET,
                units='cm')

				
        self.add_parameter('temp_voltage_min',
                type=types.FloatType,
                flags=Instrument.FLAG_GETSET,
                units='V')

        self.add_parameter('lt1_temp_A_max',
                type=types.FloatType,
                flags=Instrument.FLAG_GETSET,
                units='K')
        
        self.add_parameter('temperature',
                type=types.FloatType,
                flags=Instrument.FLAG_GET,
                units='K')

        self.add_parameter('recording',
                type=types.BooleanType)

        self.add_function('restart_recording')
		
		#
        self.set_he2_lvl_min(0.5)	#cm corr to about 1 hour response time
        self.set_he1_lvl_min(1.0)   #cm corr to about 1 hour response time
        self.set_temp_voltage_min(1.5) #1.5 V corr to T > 6 K
        self.set_lt1_temp_A_max(7.0)
        self._recording = False
        self.set_recording(True)
        
        # load the temperature calibration from file
        try:
            self.temp_calib = np.loadtxt(os.path.join(qt.config['execdir'], 
                '..', 'measurement', 'calib', 'DT-670.txt'))
        except:
            print "could not get T-calibration data."
            self.temp_calib = None
        
		
		#override from config:
        self._parlist.extend(['he2_lvl_min','temp_voltage_min', 'lt1_temp_A_max'])
        self.load_cfg()
        self.save_cfg()

    def do_set_recording(self, val):
        if not self._recording and val:
            self._recording = val
            self._T0 = time.time()
            self._data = qt.Data(name=self._name)
            self._data.add_coordinate('time')
            self._data.add_value('level He1')
            self._data.add_value('level He2')
            self._data.add_value('temperature_lt2')
            self._data.add_value('He1 consumption')
            self._data.add_value('He2 consumption')

            if self._monitor_lt1:
                self._data.add_value('temperature_lt1_A')
                self._data.add_value('temperature_lt1_B')

            self._data.create_file()
            
            self._plt = qt.Plot2D(self._data, 'ro', name=self._name, 
                    coorddim=0, valdim=1, clear=True)
            self._plt.add(self._data, 'bo', coorddim=0, valdim=2)
            self._plt.add(self._data, 'k-', coorddim=0, valdim=3,
                    right=True)
            if self._monitor_lt1:
                self._plt.add(self._data, 'g-', coorddim=0, valdim=6,
                    right=True)
                self._plt.add(self._data, 'y+', coorddim=0, valdim=7,
                    right=True)
            self._plt.set_xlabel('time (hours)')
            self._plt.set_ylabel('filling level (cm)')
            self._plt.set_y2label('T (K)')

            self._plt_rates = qt.Plot2D(self._data, 'ro', name=self._name+'_He_consumption',
                coorddim=0, valdim=4, clear=True)
            self._plt_rates.add(self._data, 'bo', coorddim=0, valdim=5)
            self._plt_rates.set_xlabel('time (hours)')
            self._plt_rates.set_ylabel('consumption (cm/h)')

            self._rate_update_interval = 1 # hours
            self._rate_times = []
            self._rate_levels1 = []
            self._rate_levels2 = []
        
        elif self._recording and not val:
            self._recording = val
            self._data.close_file()

    def do_get_recording(self):
        return self._recording

    def do_get_he2_lvl_min(self):
        return self._he2_lvl_min

    def do_set_he2_lvl_min(self, val):
        self._he2_lvl_min = val
	
    def do_get_he1_lvl_min(self):
        return self._he1_lvl_min

    def do_set_he1_lvl_min(self, val):
        self._he1_lvl_min = val

    def do_get_temp_voltage_min(self):
        return self._temp_voltage_min

    def do_set_temp_voltage_min(self, val):
        self._temp_voltage_min = val


    def do_get_lt1_temp_A_max(self):
        return self._lt1_temp_A_max

    def do_set_lt1_temp_A_max(self, val):
        self._lt1_temp_A_max = val
    
    def do_get_temperature(self):
        if self.temp_calib == None:
            return 0.0

        else:
            v = self._keithleyMM.get_readlastval()
            idx = np.argmin(abs(v-self.temp_calib[:,1]))

            # interpolation
            dv = v - self.temp_calib[idx,1]
            t = self.temp_calib[idx,0] + dv/(self.temp_calib[idx,2]*1e-3)

            return t

    def restart_recording(self):
        self.set_recording(False)
        self.set_recording(True)
        return
		
    def _update(self):
        if not MonitorInstrument._update(self):
            return False

        MAXLVLTRIES = 3

        i = 0
        self._levelmeter.write('chan 2')
        lev1 = self._levelmeter.ask('meas?')
        lev1_flt=float((lev1.split(' '))[0])
        while lev1_flt < 1.0 and i < MAXLVLTRIES:
            self._levelmeter.write('chan 2')
            self._levelmeter.write('meas')
            
            # TODO make sure readout is actually finished

            lev1 = self._levelmeter.ask('meas?')
            lev1_flt=float((lev1.split(' '))[0])
            i+= 1
            # time.sleep(0.1)

        if lev1_flt < -1.0:
            lev1_flt = -1.0

        i = 0
        self._levelmeter.write('chan 1')
        lev2 = self._levelmeter.ask('meas?')
        lev2_flt=float((lev2.split(' '))[0])
        while lev2_flt < 1.0 and i < MAXLVLTRIES:
            self._levelmeter.write('chan 1')
            self._levelmeter.write('meas')

            # TODO make sure readout is actually finished

            lev2 = self._levelmeter.ask('meas?')
            lev2_flt=float((lev2.split(' '))[0])
            i+= 1
            # time.sleep(0.1)

        if lev2_flt < -1.0:
            lev2_flt = -1.0
	
        t_num = time.time()	
        t_str = time.asctime()
        
        self._rate_times.append((t_num-self._T0)/3600.)
        self._rate_levels1.append(lev1_flt)
        self._rate_levels2.append(lev2_flt)
        i = 0
        while self._rate_times[i] < (((t_num-self._T0)/3600.) - self._rate_update_interval):
            self._rate_times = self._rate_times[1:]
            self._rate_levels1 = self._rate_levels1[1:]
            self._rate_levels2 = self._rate_levels2[1:]

        if len(self._rate_times) > 1:
            rate1 = (self._rate_levels1[0] - self._rate_levels1[-1])/(self._rate_times[-1] - self._rate_times[0])
            rate2 = (self._rate_levels2[0] - self._rate_levels2[-1])/(self._rate_times[-1] - self._rate_times[0])
        else:
            rate1 = 0
            rate2 = 0

        print('current time: %s'%t_str)
        print('current cryovac levelmeter reading:')
        print('  LHe1 (upper tank): %s'%(lev1))
        print('  LHe2 (lower tank): %s'%(lev2))

        volt = 'n/a'
        keith_meas = self._keithley.ask(':func?')
        if keith_meas == '"VOLT:DC"':
            volt = float(self._keithley.ask(':data?'))
            print('current sensor voltage: %.3f'%(volt))
            print('current temperature: %.3f'%(self.get_temperature()))
		
        if self.get_save_data():
            try:
                with open('//tudelft.net/staff-groups/tnw/ns/qt/Diamond/setups/LT2/cryo.txt','a') as f:
                    f.write('%.0f\t%s\t%s\t%s\t%.3f V\n'%(t_num,t_str,lev1,lev2,volt))
                    f.close()
            except Exception:
                print ' error writing on network disk'
                
        if self.get_send_email():
            try:
                params = urllib.urlencode({'entry_312373567': lev1, 'entry_941467047': lev2, 'ss-submit': 'Submit'})
                urllib.urlopen('https://docs.google.com/forms/d/1T0ZY1G08LPWRn3M_-yq--PAdrz_8LtqzQJn9AL3qZVs/formResponse', params)
            except Exception:
                print ' error publishing levels'
          
        if (lev2_flt < self.get_he2_lvl_min()) or (volt != 'n/a' and volt < self.get_temp_voltage_min()) or (-0.1 < lev1_flt < self.get_he1_lvl_min()):
            subject= 'Warning from Cryo LT2!'
            message = 'Warning from Cryo LT2: Measured levels: \n'+\
                      'current cryovac levelmeter reading:\n' + \
                      '  LHe1 (upper tank): %s'%(lev1) + '\n' + \
                      '  LHe2 (lower tank): %s'%(lev2) + '\n' + \
                      'current sensor voltage: %.3f'%(volt) + '.\n' + \
                      'current temperature:  %.3f'%(self.get_temperature()) + '.\n' + \
                      'This is below minimum values (LHe2 < %.3f'%(self.get_he2_lvl_min()) + ' cm'+ ', LHe1 < %.3f'%(self.get_he1_lvl_min()) +\
                      ', voltage < %.3f'%(self.get_temp_voltage_min()) + 'V ( = 6 K)). \n' + \
                      'Please help me!!!\n xxx LT2'
            recipients  = ['B.J.Hensen@tudelft.nl', 'h.bernien@tudelft.nl', 'M.S.Blok@tudelft.nl', 'julia.cramer@gmail.com','c.bonato@tudelft.nl','t.h.taminiau@tudelft.nl']
            #recipients  = 'B.J.Hensen@tudelft.nl'
            print message
            if self.get_send_email():
                    if self._mailer.send_email(recipients,subject,message):
						print 'Warning email message sent'					
        
        if self._monitor_lt1:
            temp_A=self._temp_lt1.get_kelvinA()
            temp_B=self._temp_lt1.get_kelvinB()
            print('LT1 temperature A: %.3f K'%(temp_A))
            print('LT1 temperature B: %.3f K'%(temp_B))

            if self.get_save_data():
                with open('//tudelft.net/staff-groups/tnw/ns/qt/Diamond/setups/LT1/cryo.txt','a') as f:
                    f.write('%.0f\t%s\t%.3f K\t%.3f K \n'%(t_num,t_str,temp_A,temp_B))
                    f.close()
            if temp_A>self.get_lt1_temp_A_max():

                subject= 'Warning from Cryo LT1!'
                message = 'Warning from Cryo LT1: \n'+\
                          'LT1 temperature A: %.3f K'%(temp_A) + '\n'+\
                          'LT1 temperature B: %.3f K'%(temp_B) + '\n'+\
                          'This is below minimum value (temp_A < %.3f)' %(self.get_lt1_temp_A_max()) + ' K \n'+\
                          'Please help me!!!\n xxx LT1'
                recipients  = ['B.J.Hensen@tudelft.nl', 'h.bernien@tudelft.nl', 'w.pfaff@tudelft.nl', 'M.S.Blok@tudelft.nl', 'julia.cramer@gmail.com']
                if temp_A>self.get_lt1_temp_A_max()+3:
                    subject=subject+' - LT1 WARMING UP!!!'
                    self.warmup_lt1()
                #recipients  = 'B.J.Hensen@tudelft.nl'
                print message
                if self.get_send_email():
                    if self._mailer.send_email(recipients,subject,message):
						print 'Warning email message sent'

            if self.get_recording():
                self._data.add_data_point((t_num-self._T0)/3600., lev1_flt, lev2_flt, self.get_temperature(), rate1, rate2, temp_A, temp_B)
        else:
            if self.get_recording():
                self._data.add_data_point((t_num-self._T0)/3600., lev1_flt, lev2_flt, self.get_temperature(), rate1, rate2)

        return True

    def warmup_lt1(self):

        try:
            self._adwin_lt1.move_to_xyz_U([0.0,0.0,0.0])
        except:
            print 'Could not move adwin lt1 slowly to 0, Moving atto directly'
        'Setting Atto-positioners!'
        self._lt1_positioner.PositionerAmplitude(0,25000)
        self._lt1_positioner.PositionerAmplitude(1,25000)
        self._lt1_positioner.PositionerAmplitude(2,25000)
        self._lt1_positioner.PositionerFrequency(0,100)
        self._lt1_positioner.PositionerFrequency(1,100)
        self._lt1_positioner.PositionerFrequency(2,100)
        self._lt1_positioner.PositionerDCLevel(0,0)
        self._lt1_positioner.PositionerDCLevel(1,0)
        self._lt1_positioner.PositionerDCLevel(2,0)
        self._lt1_positioner.PositionerDCLevel(3,0)
        self._lt1_positioner.PositionerDCLevel(4,0)
        self._lt1_positioner.PositionerDCLevel(5,0)
        self._lt1_positioner.PositionerDcInEnable(3,0)
        self._lt1_positioner.PositionerDcInEnable(4,0)
        self._lt1_positioner.PositionerDcInEnable(5,0)

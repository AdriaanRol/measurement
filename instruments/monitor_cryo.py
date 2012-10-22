import visa
from instrument import Instrument
from monitor_instrument import MonitorInstrument
import types
import qt
import time
import numpy as np
import os

class monitor_cryo(MonitorInstrument):
    '''This is a child class of the monitor instrument. 
	It monitors Helium levels and temperature in the LT2 cryostat'''
	
    def __init__(self, name, **kw):
		
        MonitorInstrument.__init__(self, name)
		
        self._levelmeter = visa.instrument('GPIB::8::INSTR')
        self._keithley =  visa.instrument('GPIB::11::INSTR')
        self._mailer = qt.instruments['gmailer']
        
        self._keithleyMM = qt.instruments['keithleyMM']
				
        self.add_parameter('he2_lvl_min',
                type=types.FloatType,
                flags=Instrument.FLAG_GETSET,
                units='cm')
				
        self.add_parameter('temp_voltage_min',
                type=types.FloatType,
                flags=Instrument.FLAG_GETSET,
                units='V')
        
        self.add_parameter('temperature',
                type=types.FloatType,
                flags=Instrument.FLAG_GET,
                units='K')
		
		#
        self.set_he2_lvl_min(0.5)	#cm corr to about 2 hour response time
        self.set_temp_voltage_min(1.5) #1.5 V corr to T > 6 K

        # load the temperature calibration from file
        
        try:
            self.temp_calib = np.loadtxt(os.path.join(qt.config['execdir'], 
                '..', 'user', 'calib', 'DT-670.txt'))
        except:
            print "could not get T-calibration data."
            self.temp_calib = None
        
		
		#override from config:
        self._parlist.extend(['he2_lvl_min','temp_voltage_min'])
        self.load_cfg()
        self.save_cfg()
		
				
    def do_get_he2_lvl_min(self):
        return self._he2_lvl_min

    def do_set_he2_lvl_min(self, val):
        self._he2_lvl_min = val
	
    def do_get_temp_voltage_min(self):
        return self._temp_voltage_min

    def do_set_temp_voltage_min(self, val):
        self._temp_voltage_min = val

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

		
    def _update(self):
        if not MonitorInstrument._update(self):
            return False
		
        t_num = time.time()	
        t_str = time.asctime()
        print('current time: %s'%t_str)
        print('current cryovac levelmeter reading:')
        self._levelmeter.write('chan 2')
        lev1 = self._levelmeter.ask('meas?')
        lev1_flt=float((lev1.split(' '))[0])
        print('  LHe1 (upper tank): %s'%(lev1))
        self._levelmeter.write('chan 1')
        lev2 = self._levelmeter.ask('meas?')
        lev2_flt=float((lev2.split(' '))[0])
        print('  LHe2 (lower tank): %s'%(lev2))
    
        volt = 'n/a'
        keith_meas = self._keithley.ask(':func?')
        if keith_meas == '"VOLT:DC"':
            volt = float(self._keithley.ask(':data?'))
            print('current sensor voltage: %.3f'%(volt))
            print('current temperature: %.3f'%(self.get_temperature()))
		
        if self.get_save_data():
            with open('//tudelft.net/staff-groups/tnw/ns/qt/Diamond/setups/LT2/cryo.txt','a') as f:
                f.write('%.0f\t%s\t%s\t%s\t%.3f V\n'%(t_num,t_str,lev1,lev2,volt))
                f.close()
        
        if (lev2_flt < self.get_he2_lvl_min()) or (volt != 'n/a' and volt < self.get_temp_voltage_min()):
            subject= 'Warning from Cryo LT2!'
            message = 'Warning from Cryo LT2: Measured levels: \n'+\
                      'current cryovac levelmeter reading:\n' + \
                      '  LHe1 (upper tank): %s'%(lev1) + '\n' + \
                      '  LHe2 (lower tank): %s'%(lev2) + '\n' + \
                      'current sensor voltage: %.3f'%(volt) + '.\n' + \
                      'current temperature:  %.3f'%(self.get_temperature()) + '.\n' + \
                      'This is below minimum values (LHe2 < %.3f'%(self.get_he2_lvl_min()) + ' cm' +\
                      ', voltage < %.3f'%(self.get_temp_voltage_min()) + 'V ( = 6 K)). \n' + \
                      'Please help me!!!\n xxx LT2'
            recipients  = ['B.J.Hensen@tudelft.nl', 'h.bernien@tudelft.nl', 'w.pfaff@tudelft.nl', 'M.S.Blok@tudelft.nl']
            #recipients  = 'B.J.Hensen@tudelft.nl'
            print message
            if self.get_send_email():
                    if self._mailer.send_email(recipients,subject,message):
						print 'Warning email message sent'					
        return True

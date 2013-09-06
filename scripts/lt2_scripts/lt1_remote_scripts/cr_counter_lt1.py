import os
import msvcrt

import qt
import hdf5_data as h5
from measurement.lib.measurement2 import measurement as m


class CRCounterMsmt(m.Measurement):

    mprefix = 'CR_counter_trace'

    adwinscript = os.path.join(qt.config['adwin_programs'], qt.config['adwin_lt1_subfolder'], 
        'lt1_cr_counter.tb9')
    adwin = qt.instruments['adwin_lt1']
    physical_adwin = qt.instruments['physical_adwin_lt1']

    CYCLES_PAR = 60
    PUMP_AOM_DAC_PAR = 61
    PROBE_AOM1_DAC_PAR = 62
    PROBE_AOM2_DAC_PAR = 63
    PUMP_AOM_VOLTAGE_FPAR = 61
    PROBE_AOM1_VOLTAGE_FPAR = 62
    PROBE_AOM2_VOLTAGE_FPAR = 63
    PUMP_TIME_PAR = 64
    POST_PUMP_TIME_PAR = 65
    PROBE_TIME_PAR = 66
    POST_PROBE_TIME_PAR = 67
    PROBE_DATA = 23
    PUMP_DATA = 22

    def record_time_trace(self, name):

        self.adwin.stop_counter()

        self.physical_adwin.Load(self.adwinscript)

        self.params['pump_aom_dac'] = self.adwin.get_dac_channels()\
            [qt.instruments['GreenAOM_lt1'].get_pri_channel()]

        self.params['probe_aom1_dac'] = self.adwin.get_dac_channels()\
            [qt.instruments['MatisseAOM_lt1'].get_pri_channel()]

        self.params['probe_aom2_dac'] = self.adwin.get_dac_channels()\
            [qt.instruments['NewfocusAOM_lt1'].get_pri_channel()]

        self.params['pump_aom_voltage'] = \
            qt.instruments['GreenAOM_lt1'].power_to_voltage(self.params['pump_power'])

        self.params['probe_aom1_voltage'] = \
            qt.instruments['MatisseAOM_lt1'].power_to_voltage(self.params['probe1_power'])

        self.params['probe_aom2_voltage'] = \
            qt.instruments['NewfocusAOM_lt1'].power_to_voltage(self.params['probe2_power'])

        # OOOOLD SCHOOL!
        self.physical_adwin.Set_Par(self.CYCLES_PAR, self.params['cycles'])
        self.physical_adwin.Set_Par(self.PUMP_AOM_DAC_PAR, self.params['pump_aom_dac'])
        self.physical_adwin.Set_Par(self.PROBE_AOM1_DAC_PAR, self.params['probe_aom1_dac'])
        self.physical_adwin.Set_Par(self.PROBE_AOM2_DAC_PAR, self.params['probe_aom2_dac'])
        self.physical_adwin.Set_FPar(self.PUMP_AOM_VOLTAGE_FPAR, self.params['pump_aom_voltage'])
        self.physical_adwin.Set_FPar(self.PROBE_AOM1_VOLTAGE_FPAR, self.params['probe_aom1_voltage'])
        self.physical_adwin.Set_FPar(self.PROBE_AOM2_VOLTAGE_FPAR, self.params['probe_aom2_voltage'])
        self.physical_adwin.Set_Par(self.PUMP_TIME_PAR, self.params['pump_time'])
        self.physical_adwin.Set_Par(self.POST_PUMP_TIME_PAR, self.params['post_pump_time'])
        self.physical_adwin.Set_Par(self.PROBE_TIME_PAR, self.params['probe_time'])
        self.physical_adwin.Set_Par(self.POST_PROBE_TIME_PAR, self.params['post_probe_time'])

        self.physical_adwin.Start_Process(9)

        while self.physical_adwin.Process_Status(9):
            if (msvcrt.kbhit() and msvcrt.getch()=='q'): 
                break

            qt.msleep(0.2)
        
        probe_cts = self.physical_adwin.Get_Data_Long(
            self.PROBE_DATA, 0, self.params['cycles'])
        pump_cts = self.physical_adwin.Get_Data_Long(
            self.PUMP_DATA, 0, self.params['cycles'])

        self.h5basegroup[name+'_pump'] = pump_cts
        self.h5basegroup[name+'_probe'] = probe_cts



def single_trace(name):
    m = CRCounterMsmt(name=name)

    m.params['cycles'] = 10000
    
    m.params['pump_power'] = 100e-6
    m.params['probe1_power'] = 3e-9
    m.params['probe2_power'] = 10e-9

    m.params['pump_time'] = 10
    m.params['post_pump_time'] = 1
    m.params['probe_time'] = 10
    m.params['post_probe_time'] = 1

    m.record_time_trace(name)

    m.save_params()
    m.finish()

if __name__ == '__main__':
    single_trace('hans4_green_no_gate')











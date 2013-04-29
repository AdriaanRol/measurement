import pprint
import numpy as np
import qt

physical_adwin = qt.instruments['physical_adwin']
adwin = qt.instruments['adwin']


# first very simple test; should just yield 100 x 1 ro result, all 0.
def test1():
    adwin.load_MBI()

    # still very ugly like this; maybe need a feature to set parameter arrays
    # in the adwin driver
    physical_adwin.Set_Data_Long(np.array([5],dtype=int), 28, 1, 1)
    physical_adwin.Set_Data_Long(np.array([10],dtype=int), 29, 1, 1)
    physical_adwin.Set_Data_Float(np.array([0],dtype=float), 30, 1, 1)
    physical_adwin.Set_Data_Float(np.array([0],dtype=float), 31, 1, 1)
    physical_adwin.Set_Data_Long(np.array([0],dtype=int), 32, 1, 1)
    # physical_adwin.Set_Data_Long(np.array([0],dtype=int), 33, 1, 1)
    physical_adwin.Set_Data_Long(np.array([5],dtype=int), 34, 1, 1)

    # check
    print physical_adwin.Get_Data_Long(28,1,10)
    print physical_adwin.Get_Data_Long(29,1,10)
    print physical_adwin.Get_Data_Float(30,1,10)
    print physical_adwin.Get_Data_Float(31,1,10)
    print physical_adwin.Get_Data_Long(32,1,10)
    # print physical_adwin.Get_Data_Long(33,1,10)
    print physical_adwin.Get_Data_Long(34,1,10)

    adwin.start_MBI(
            load = False,
            stop = True,
            counter_channel = 2,
            green_laser_DAC_channel = 4,
            Ex_laser_DAC_channel = 6,
            A_laser_DAC_channel = 7,
            AWG_start_DO_channel = 0,
            AWG_done_DI_channel = 9,
            green_repump_duration = 5,
            CR_duration = 50,
            SP_E_duration = 100,
            wait_after_pulse_duration = 1,
            CR_preselect = 1,
            CR_probe = 0,
            repetitions = 100,
            sweep_length = 5,
            cycle_duration = 300,
            AWG_event_jump_DO_channel = 6,
            MBI_duration = 1,
            wait_for_MBI_pulse = 4,
            MBI_threshold = 0,
            nr_of_ROsequences = 1,
            wait_after_RO_pulse_duration = 3,
            green_repump_voltage = 5.,
            green_off_voltage = 0.,
            Ex_CR_voltage = 0.,
            A_CR_voltage = 0.,
            Ex_SP_voltage = 0.,
            Ex_MBI_voltage = 0. )



### script
test1()


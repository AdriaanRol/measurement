import os, time, msvcrt, qt
import numpy as np
from measurement.lib.cython.hh_optimize import hht4
from measurement.lib.AWG_HW_sequencer_v2 import Sequence

hharp = qt.instruments['HH_400']
green = qt.instruments['GreenAOM']
awg = qt.instruments['AWG']

class PulsedAntibunchMeasurement:

    def __init__(self):
        self.noof_reps = 1000
        self.noof_pulses_per_element = 100
        self.green_duration = 300
        self.sync_rep_rate = 500
        

    def generate_sequence(self, do_program = True):
        seq = Sequence('QuTau')

        seq.add_channel(name = 'sync_chan', AWG_channel = 'ch2m2', high = 1.0)
        seq.add_channel(name = 'green_chan', AWG_channel = 'ch4m2', high = 0.50)
        seq.add_channel(name = 'dummy_chan', AWG_channel = 'ch4m1', high = 1.0)

        ename = 'PAM'
        seq.add_element(ename, repetitions = self.noof_reps, goto_target = ename)

        if self.sync_rep_rate > 50 + self.green_duration: 

            for pulse in range(self.noof_pulses_per_element):
                #add the first pulse, without a start reference of course
                if pulse == 0:
                    
                    last = ''
                    for presync in range(10):
                        seq.add_pulse('Presync_%d'%presync, 'sync_chan', ename, start = 0,
                                start_reference = last, link_start_to = 'end',
                                duration = 50, amplitude = 1.) 
                        seq.add_pulse('Presync_%d_wait'%presync, 'sync_chan', ename, start = 0,
                                start_reference = 'Presync_%d'%presync, link_start_to = 'end',
                                duration = self.sync_rep_rate - 50, amplitude = 0.) 

                        last = 'Presync_%d_wait'%(presync)

                    
                    seq.add_pulse('Sync_0', 'sync_chan', ename, start = 0,
                            start_reference = 'Presync_%d_wait'%presync, link_start_to = 'end',
                            duration = 50, amplitude = 1) 
                    seq.add_pulse('Green_0', 'green_chan', ename, 
                            start = 0,
                            start_reference = 'Sync_0', link_start_to = 'end',
                            duration = self.green_duration, 
                            amplitude = 0.50)

                    seq.add_pulse('Count_ch0_0', 'dummy_chan', ename, 
                            start = 0,
                            start_reference = 'Sync_0', link_start_to = 'end',
                            duration = 50, amplitude = 0.50)
                #add the rest of the pulses 
                else:
                    seq.add_pulse('Sync_%d'%pulse, 'sync_chan', ename, 
                            start = self.sync_rep_rate - 50 - self.green_duration,
                            start_reference = 'Green_%d'%(pulse-1), 
                            link_start_to = 'end',  
                            duration = 50, amplitude = 1)

                    seq.add_pulse('Green_%d'%pulse, 'green_chan', ename,
                            start = 0,
                            start_reference = 'Sync_%d'%pulse, 
                            link_start_to = 'end',
                            duration = self.green_duration,
                            amplitude = 0.50)

                    seq.add_pulse('Count_ch0_%d'%pulse, 'dummy_chan', ename, 
                            start = 0,
                            start_reference = 'Sync_%d'%pulse, link_start_to = 'end',
                            duration = 50, amplitude = 0.50)

        seq.set_instrument(awg)
        seq.set_clock(1e9)
        seq.set_send_waveforms(do_program)
        seq.set_send_sequence(do_program)
        seq.set_program_channels(True)
        seq.set_start_sequence(False)
        seq.force_HW_sequencing(True)
        seq.send_sequence()
        
        return True


    def get_T3_pulsed_events(self, sync_period, 
            start_ch0=0, start_ch1=0, save_raw=True, raw_max_len=1E6, 
            sleep_time = 10E-3):
        """
        Get ch0 and ch1 events in T3 mode.
        Author: Wolfgang, July 1, 2012.
        Adapted by Gerwin, June 20, 2013

        Filtering options:
        start_ch0, start_ch1:
            minimum event time (in bins) after the sync
        max_pulses:
            how many syncs after a marker on channel 1 are taken into
            account
        
        returns:
            (ch0, ch1, markers)
            ch0: array with two columns: col1 = absolute sync no, col2 = time
            ch1: ditto
            markers: array with three columns:
                col1 = sync no, col2 = time, col3 = marker channel
        """

        if .001*hharp.get_ResolutionPS() * 2**15 < sync_period:
            print('Warning: resolution is too high to cover entire sync \
                    period in T3 mode, events might get lost.')

        #prepare for saving the data; create directory etc...
        if save_raw:
            rawdir = self.save_folder
            if not os.path.isdir(rawdir):
                os.makedirs(rawdir)
            rawidx = 0
            lengths = np.array([])
            times = np.array([])
            accumulated_data = np.empty((0,4), dtype = np.uintc)
        else:        
            #initialize the overflow offset number to 0. This will be updated in
            #the loop everytime the function is called later on. In this way the
            #sync number increases linearly with time and doesn't fall back 
            #everytime the function is called.
            syncnr_offset = 0
            accumulated_data = np.empty((0,4), dtype = np.uintc)
            rawidx = 0

        #here comes the actual data acquisition    
        while hharp.get_MeasRunning() == True:
            length, data = hharp.get_TTTR_Data()

            #if we don't want to process the data at all use this
            if save_raw:
                accumulated_data = np.append(accumulated_data, data[:length])
                lengths = np.append(lengths, length)
                times = np.append(times, int(time.strftime('%M%S')))
                
                if len(accumulated_data) > raw_max_len:
                    np.savez(os.path.join(rawdir, 'LDE_rawdata-%.3d'%rawidx), 
                        length=len(accumulated_data), data=accumulated_data)
                    
                    accumulated_data = np.array([])
                    rawidx += 1
            
            #if we first want to filter the data before saving use this
            else:
                print "I registered... %d events"%length
                #analyze the entire array or just the new data?
                prefiltered, syncnr_offset = hht4.filter_raw_antibunch_data(
                        data[:length], syncnr_offset, int(self.sync_rep_rate/0.256),
                        int(self.sync_rep_rate/0.256))
               
                accumulated_data = np.append(accumulated_data, prefiltered, axis = 0)
                
                #if the accumulated_data is large enough, save it to a file
                if len(accumulated_data) > raw_max_len:
                    print "Saving accumulated data..."
                    np.savez(os.path.join(rawdir, 'LDE_prefiltered-%.3d'%rawidx), 
                        length=len(accumulated_data), data=accumulated_data)
                    
                    rawidx += 1
                    accumulated_data = np.array((0,4), dtype = np.uintc)
            
            #Sleeping might give a bit more stable data acquisition
            #But be careful not to make it too big
            qt.msleep(sleep_time, exact = True)
            
            if(msvcrt.kbhit() and msvcrt.getch()=='x'):
                print 'x pressed, quitting current run'
                hharp.StopMeas()

        return accumulated_data

    
    def process_accumulated_data(self, accumulated_data, save = True, rawfile = False):
        
        if rawfile:
            for idx, raw_npz_file in enumerate(os.listdir(self.save_folder)):
                d = np.load(os.path.join(self.save_folder, raw_npz_file))
                rawdata = d['data']
                accumulated_data = hht4.filter_raw_antibunch_data(rawdata, 0, 700)
                dts = hht4.get_dts(accumulated_data, start_ch = 0, stop_ch = 1)

                if save:
                    np.savez(os.path.join(self.save_folder, 'Dts_%.3d.npz'%idx), 
                            dts = dts, data = accumulated_data)

        else:
            dts = hht4.get_dts(accumulated_data, start_ch = 0, stop_ch = 1)

            if save:
                np.savez(os.path.join(self.save_folder, 'Dts.npz'), 
                        dts = dts, data = accumulated_data)

        return dts
            
            
    def measure(self, measurement_time, noof_reps = 1E6, RAW = False):
        
        today = time.strftime('%Y%m%d')
        curr_time = time.strftime('%H%M%S')
        self.save_folder = os.path.join(r'D:\measuring\data', 
                today, curr_time+'_HydraHarp_Live')
                
        if not(os.path.exists(os.path.split(self.save_folder)[0])):
            os.mkdir(os.path.split(self.save_folder)[0])
        if not(os.path.exists(self.save_folder)):
            os.mkdir(self.save_folder)
        
        self.noof_reps = noof_reps
        sync_separation = self.sync_rep_rate             
        self.generate_sequence()

        hharp.start_T3_mode()
        hharp.calibrate()
        hharp.set_Binning(8)
        hharp.StartMeas(int(measurement_time*1e3))
        qt.msleep(0.5)
        awg.start()
        accumulated_data = self.get_T3_pulsed_events(
                sync_separation, start_ch0 = 0, start_ch1 = 0,
                max_pulses = 2, save_raw = RAW, 
                raw_max_len = 1E6, sleep_time = 1000E-3)
        awg.stop()

        dts = self.process_accumulated_data(accumulated_data, rawfile = RAW)

        return accumulated_data, dts


if __name__ == "__main__":

    PAM = PulsedAntibunchMeasurement()
    accumulated_data, dts = PAM.measure(15, noof_reps = 1E6)



#if __name__ == "__main__":
#    opt_pi_separation = 400         #not so important    
#    measurement_time = 10           #in seconds
#
#    hharp.start_T3_mode()
#    hharp.calibrate()
#    hharp.set_Binning(8)
#    hharp.StartMeas(int(measurement_time*1e3))
#    qt.msleep(1)
#    get_T3_pulsed_events(opt_pi_separation, start_ch0 = 0, start_ch1 = 0, 
#             max_pulses = 2, save_raw = False, 
#             raw_max_len = 1E6, sleep_time = 10E-3)

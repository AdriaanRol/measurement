from measurement.lib.cython.hh_optimize import hhopt, hht4
import time, ctypes, msvcrt
import qt
from matplotlib import pyplot as plt

def generate_fake_data(ln = 1E6):
    ch0_clicks = np.random.uniform(low = 0, high = ln, size = ln/2)
    ch1_clicks = np.random.uniform(low = 0, high = ln, size = ln/5)
    ch2_clicks = np.random.uniform(low = 0, high = ln, size = ln/5)
    ch3_clicks = np.random.uniform(low = 0, high = ln, size = ln/5)
    ch4_clicks = np.random.uniform(low = 0, high = ln, size = ln/5)

    ch = np.zeros(ln, dtype = np.uint)
    ch[ch0_clicks.astype(int)] = 0
    ch[ch1_clicks.astype(int)] = 1
    ch[ch2_clicks.astype(int)] = 2
    ch[ch3_clicks.astype(int)] = 3
    ch[ch4_clicks.astype(int)] = 4

    ts = np.sort(np.random.uniform(low = 0, high = 10*ln, size = ln))

    return ch, ts.astype(np.uint)


def prepare_selftest(BuffSize, BurstPeriod):
    channels = [0,1,2,3,4]
    expTime = 10 #ms
    qt.instruments.reload(qutau)
    qutau.set_buffer_size(BuffSize)
    qutau.switch_termination(True)
    qutau.set_exposure_time(expTime)
    qutau.clear_all_histograms()
    qutau.set_active_channels(channels)
    qutau.configure_selftest(channels, 1E-6, 3, BurstPeriod)

    qt.msleep(500E-3)


class QuTau_TTTR():
    """
    Start a TTTR measurement with the QuTau, LDE style, ohyeah!
    """
    
    def __init__(self):
        self.qutau = qt.instruments['QuTau']
        self.set_defaults()

    
    def set_defaults(self):
        print "Setup channels using default values:"
        for idx,k in enumerate(['sync_chan', 'apd1_chan', 'apd2_chan', \
                'marker1_chan', 'marker2_chan']):
            setattr(self, k, idx)
            print "* %s: channel %d"%(k, idx)

        self.minbinch1 = 0
        self.minbinch2 = 0
        self.maxbinch1 = 3000
        self.maxbinch2 = 3000

        self.qutau.set_active_channels([0,1,2,3,4])
            

    def setup_tttr(self, sync_chan, apd1_chan, apd2_chan, marker1_chan, marker2_chan):
        """
        Configure the channels on the qutau for a TTTR measurement. There are 5 channels
        that need to be defined. The marker channels are:
        - marker1 for a start of the optical pi pulses (at the end of the presyncs)
        - marker2 from the PLU (signals an entanglement event)
        """
        
        active_ch_list = list()
        print "Setup channels using specified values:"
        for k in ['sync_chan', 'apd1_chan', 'apd2_chan', 'marker1_chan', 'marker2_chan']:
            setattr(self, k, vars()[k])
            print "* %s: channel %d"%(k, getattr(self, k))
            active_ch_list.append(vars()[k])

        self.qutau.set_active_channels(active_ch_list)


    def check_for_decreasing_timestamps(self, tsdata):
        """
        Checks if there are decreasing timestamps in the data.
        """

        time_diff = np.diff(tsdata)
        
        if np.any(time_diff < 0):
            return False
        else:
            return True

    
    def decode_data(self, chdata, tsdata, sync_offset):
        """
        The qutau data has two arrays: one channel array containing the channel numbers 
        where clicks were observed. The other one contains the time stamps. 
        Here I assign to each event a third and fourth array. The third array contains
        the sync number, and a fourth array replaces the second array with timestamps. It 
        contains the times with respect to the last sync. Finally we reshape the data 
        in the well known HydraHarp format.
        """
        chdata = chdata.astype(np.uint8)
        tsdata = tsdata.astype(np.uintc)
        
        sync_mask = chdata != self.sync_chan
        special = np.logical_or(chdata == self.marker1_chan, chdata == self.marker2_chan)
        sync_number = hhopt.get_sync_number(chdata, self.sync_chan, sync_offset)
        timings_wrt_sync = hhopt.get_dt_wrt_sync(chdata, tsdata, self.sync_chan)

        datastack = hhopt.stack(sync_number.astype(np.uintc), 
                                      timings_wrt_sync.astype(np.uintc), 
                                      chdata.astype(np.uintc),
                                      special.astype(np.uintc))

        #adjust the sync number offset to the last sync number
        sync_offset = datastack[-1,0]

        #delete syncs from the arrays
        decoded_data = hhopt.apply_filter_to_2darray(datastack, sync_mask.astype(np.uintc))

        return decoded_data, sync_offset


    def process_incoming_data(self, chdata, tsdata, sync_offset, marker_number,
                              dsyncs = np.array([1,2], dtype = np.uintc)):
        """
        Filter routine for the raw data that comes in during a measurement.
        Note that this is quite identical to the function hht4.filter_raw_data 
        However, we don't need to take care of filter_overflows anymore. Also, because
        I create the sync numbers artificially, there are no decreasing sync numbers in the
        beginning of the measurements. To check for this problem, we can check if there
        is a negative time jump in the time stamp data. 
        """

        if self.check_for_decreasing_timestamps(tsdata):
            error_out = False
            pass
        else:
            error_out = True

        data, sync_offset = self.decode_data(chdata, tsdata, sync_offset)
        while len(data) > 0:
            #Now we can just use the HydraHarp TTTR module.
            data = hht4.filter_timewindow(data, self.apd1_chan, self.minbinch1, self.maxbinch1)
            data = hht4.filter_timewindow(data, self.apd2_chan, self.minbinch2, self.maxbinch2)
            data = hhopt.filter_counts_on_marker(data, mchan = marker_number,
                        delta_syncs = dsyncs.astype(np.uintc))

            break

        return data, error_out, sync_offset


    def is_measuring(self, tstart, tmeas):
        if time.clock() > tstart + tmeas:
            return False
        else:
            return True

    
    def save_data(self, data, index, print_status = False):
        if print_status:
            print "\n* %d. Saving to file..."%(index+1)
            t0 = time.clock()

        #Saving the data as uint8 takes up less space.
        np.savez(os.path.join(self.sp, self.tm, 'qutau_filtered_%.3d.npz'%index),
                sync_nr = data[:,0], 
                times = data[:,1],
                ch = data[:,2].astype(np.uint8),
                special = data[:,3].astype(np.uint8))

        if print_status:
            print "* Saving completed in %.2f s."%(time.clock() - t0)


    def measure(self, tmeas):
        """
        Start a TTTR measurement: every 100 ms the QuTau buffer is emptied and 
        the data is filtered and cast into the well-known HydraHarp format.
        """
        
        buffer_size = 1E6
        self.qutau.set_buffer_size(buffer_size)
        stop = False
        print_status = True

        #Save settings
        save = True
        save_cycles = 0
        self.sp = r'D:\measuring\data'
        dt = time.strftime('%Y%m%d')
        self.sp = os.path.join(self.sp, dt)
        hr = time.strftime('%H%M%S')
        self.tm = hr+'_qutau_tttr_testing'
        os.mkdir(os.path.join(self.sp, self.tm))

        old_data = np.zeros([0,4], dtype = np.uintc)
        rem_ch = np.zeros(0, dtype = ctypes.c_uint8)
        rem_ts = np.zeros(0, dtype = ctypes.c_uint64)
        sync_offset = 0
        
        tstart = time.clock()

        while self.is_measuring(tstart, tmeas) and not(stop):

            if len(old_data) > 1E6:
                #if the length of the accumulated data is more than 1E6 elements, 
                #save the data to the hard-disk of the computer.
                if save:
                    self.save_data(old_data, save_cycles, print_status = print_status)
                    save_cycles += 1
                
                old_data = np.zeros([0,4], dtype = np.uintc)
                
            #read the values from the qutau
            [ts, ch, valid] = self.qutau.get_last_timestamps(buffer_size = buffer_size, 
                                                             reset = True)
            
            #pause acquisition for a moment 
            time.sleep(100E-3)

            if valid > 0:
                if valid >= buffer_size:
                    print "Buffer overflow, stopping data acquisition..."; stop = True
                else:    
                    ts = np.frombuffer(ts, dtype = ctypes.c_uint64)
                    ch = np.frombuffer(ch, dtype = ctypes.c_uint8) 
                    
                    ts = ts[:valid]
                    ch = ch[:valid]

                    #for proper analysis of time tags, the first element of ch
                    #must be a sync, otherwise the time w.r.t. a sync cannot 
                    # be determined for the first few clicks
                    last_sync_idx = np.where(ch == self.sync_chan)[0][-1]
                
                    channel = np.append(rem_ch, ch[:last_sync_idx])
                    timestamp = np.append(rem_ts, ts[:last_sync_idx])

                    #we append the last sync of this round to the next round
                    rem_ch = ch[last_sync_idx:]
                    rem_ts = ts[last_sync_idx:]

                    data, error_out, sync_offset = self.process_incoming_data(
                            channel, timestamp, 
                            sync_offset, self.marker1_chan, 
                            dsyncs = np.array([1,2], dtype = np.uintc))

                    #append the fresh data to data that was read-out previously
                    data = np.append(old_data, data, axis = 0)
                    old_data = data 

                    if 0:
                        print "Memory full percentage: %.1f%%, length of array: %d"\
                            %(valid/float(buffer_size)*100, len(old_data))


            if msvcrt.kbhit() and msvcrt.getch() == 'q':
                print "Measurement interrupted by user..."
                stop = True            
                    
        self.save_data(old_data, save_cycles, print_status = print_status)

        tend = time.clock()
        print "Integration time was %.4e s."%(tend-tstart)

        if qutau.get_data_lost():
            print "Data was lost during the transfer from the device to the computer!"
        
        return data


    def plot_histogram(self, data, channela, channelb):
        """
        Channel A serves as a start, Channel B serves as a stop. 
        When Channel A is negative, the histogram of channel B with 
        respect to the sync is given.
        """
        binsize = 1#81E-12*1E9
        hist_binwidth = 0.256E-9
        dts = hhopt.get_dts_qutau(data, channela, channelb)
        
        if len(dts) > 0:
            plt.figure()
            plt.hist(dts*binsize, color = 'red', alpha = 0.75, log = True, bins = 50)   
            plt.title('Histogram of channel %d w.r.t. syncs'%channelb)
            plt.xlabel('dt (ns)')
            plt.ylabel('Frequency')        
            plt.show()


if __name__ == "__main__":
    tttr = QuTau_TTTR()
    tttr.setup_tttr(0,1,2,3,4)
    #10 us = 1.5 MHz on 5 channels
    #prepare_selftest(1E6, 10E-6)
    
    data = tttr.measure(30)
    tttr.plot_histogram(data, -1, 2)
    #ch, ts = generate_fake_data(1E6)
    #decoded_data = tttr.decode_data(ch, ts, 0)
    #data, error_out = tttr.process_incoming_data(ch, ts, 0, 
    #                        tttr.marker1_chan, dsyncs = np.array([1,2], dtype = np.uintc))
    #print "This took %.3f ms."%((time.clock() - t0)*1E3)

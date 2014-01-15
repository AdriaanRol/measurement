import numpy as np
import os, sys, time
from matplotlib import pyplot as plt
import matplotlib as mpl
import qt, msvcrt, ctypes
qutau = qt.instruments['QuTau']

from measurement.lib.cython.error_lib import errors

def prepare(BuffSize):
    channels = [0,1,2]
    expTime = 10 #ms
    qt.instruments.reload(qutau)
    qutau.initialize()
    qutau.set_buffer_size(BuffSize)
    qutau.switch_termination(True)
    qutau.set_exposure_time(expTime)
    qutau.clear_all_histograms()
    qutau.set_active_channels(channels)

    qt.msleep(500E-3)


def prepare_selftest(BuffSize, BurstPeriod):
    channels = [0,1,3]
    expTime = 10 #ms
    qt.instruments.reload(qutau)
    #qutau.initialize()
    qutau.set_buffer_size(BuffSize)
    qutau.switch_termination(True)
    qutau.set_exposure_time(expTime)
    qutau.clear_all_histograms()
    qutau.set_active_channels(channels)
    qutau.configure_selftest(channels, 1E-6, 3, BurstPeriod)

    qt.msleep(500E-3)


def stop_selftest():
    qutau.configure_selftest([], 1E-6, 3, 6E-6)


def generate_fake_data(ln = 1E6):
    ch0_clicks = np.random.uniform(low = 0, high = ln, size = ln/3)
    ch1_clicks = np.random.uniform(low = 0, high = ln, size = ln/3)
    ch2_clicks = np.random.uniform(low = 0, high = ln, size = ln/3)

    ch = np.zeros(ln, dtype = np.uint)
    ch[ch0_clicks.astype(int)] = 0
    ch[ch1_clicks.astype(int)] = 1
    ch[ch2_clicks.astype(int)] = 2

    ts = np.sort(np.random.uniform(low = 0, high = 100, size = ln))

    return ch, ts


def filter_valid_syncs(sync_idxs, chan_data, ts_data):
    """
    Filters the list of syncs. Takes out instances where:
    * a sync has no clicks on a channel before the next sync arrives
    * a sync has only one click on a channel before the next sync arrives
    """
    dsync = np.diff(sync_idxs)
    mask = np.intersect1d(np.where(dsync != 1)[0], np.where(dsync != 2)[0])
    last_sync = sync_idxs[len(sync_idxs)-1]
    syncs = sync_idxs[mask]
    max_idx = len(chan_data)-1
    
    #a check for the last sync: make sure it is not one of the last two elements
    if last_sync <= max_idx-2:
        syncs = np.append(sync_idxs[mask], last_sync)
        rem_ch = np.array([]); rem_ts = np.array([])
    #if it is one of the last two elements, then remember it for stitching in next loop
    else:
        rem_ch = chan_data[last_sync:]; rem_ts = ts_data[last_sync:]

    return syncs, rem_ch, rem_ts


def map_events(ch, syncs):
    """
    Maps an event sequence to a single number, for instance:
    - sync, ch1, ch1 ==> 0 
    - sync, ch1, ch2 ==> 1
    - sync, ch2, ch1 ==> 2
    - sync, ch2, ch2 ==> 3
    """
    return (ch[syncs+1]-1)*1 + (ch[syncs+2]-1)*2


def get_t0_dt(ts, syncs):
    """
    Gets time differences from an array of time samples. 
    """
    tstart = ts[syncs]
    t0 = ts[syncs+1]
    t1 = ts[syncs+2]
    
    dt = t1-t0

    if np.any(dt > 3000):
        #error = True
        error = False
    else:
        error = False

    return t0-tstart, dt, error


def return_histogram(ch, ts, rem_ch, rem_ts, event_type = None, 
        sync_chan = 0, ch0_chan = 1, ch1_chan = 2):

    #stitch an old sync to the current data
    if len(rem_ts) > 0:
        ch = np.append(rem_ch, ch)
        ts = np.append(rem_ts, ts)

    sync_idxs = np.where(ch == sync_chan)[0]
    
    #filters sync indexes in CH that have no neighboring syncs or
    #only one click corresponding to one sync
    
    if len(sync_idxs) < 1:
        if len(ch) > 0:
            print '\t Length array (sync_idxs, ch) = (%d, %d)'%(len(sync_idxs), len(ch))
        else: 
            pass
        return np.array([]), np.array([]), np.array([]), np.array([]), np.array([]), np.array([])
    else:
        syncs, rem_ch, rem_ts = filter_valid_syncs(sync_idxs, ch, ts)

        #filters the corresponding time differences and returns t0, dt
        t0, dt, error = get_t0_dt(ts, syncs)

        #selects the detection event type (ch0, ch0), (ch0, ch1), etc...
        if event_type == None:
            pass
        elif event_type in range(4):
            event_map = map_events(ch, syncs)
            
            t0 = ts[np.where(event_map == event_type)[0]]
            dt = dt[np.where(event_map == event_type)[0]]

        return syncs, t0, dt, rem_ch, rem_ts, error


#########################################
#########################################
########## USED FOR TESTING ############# 
#########################################
#########################################

def IntEgrAt000rR(tstart, inteGREET):
    if time.clock() > tstart + inteGREET:
        return False
    else:
        return True


def bitchin_benchmark(meastime, BuffSize):
    qutau.set_buffer_size(BuffSize)
    tstart = time.clock()
    stopmaar = False
    timebase = qutau.get_timebase()
    
    ch = np.zeros([0], dtype = np.uint)
    t0 = np.zeros([0], dtype = np.uint)
    dt = np.zeros([0], dtype = np.uint)

    dumps = 0
    ch_dump = dict()
    t0_dump = dict()
    dt_dump = dict()
    rem_ch = np.array([])
    rem_ts = np.array([])

    while IntEgrAt000rR(tstart, meastime) and not(stopmaar):
        ch_OLD = ch
        t0_OLD = t0
        dt_OLD = dt
        
        if len(ch_OLD) > 1E6:
            print "\n================= DATA DUMP %d =================\n"%(dumps+1)
            ch_dump[str(dumps)] = ch_OLD
            t0_dump[str(dumps)] = t0_OLD
            dt_dump[str(dumps)] = dt_OLD

            ch_OLD = np.zeros([0])
            dt_OLD = np.zeros([0])
            t0_OLD = np.zeros([0])

            dumps += 1

        [ts, ch, valid] = qutau.get_last_timestamps(buffer_size = BuffSize, reset = True)
    
        ts = np.ctypeslib.as_array(ts)[0:valid]
        ch = np.ctypeslib.as_array(ch)[0:valid]

        if valid == BuffSize:
            print "Quit because of overflow..."; stopmaar = True

        syncs, t0, dt, rem_ch, rem_ts, error = return_histogram(ch, ts, rem_ch, rem_ts)

        if error:
            print "Error detected, quit..."
            stopmaar = True

        if len(syncs) > 0:
            print "Memory full percentage: %.4f%%, length of array: %d"\
                    %(valid/float(BuffSize)*100, len(ch))
                
        ch = np.append(ch_OLD, ch)
        t0 = np.append(t0_OLD, t0)
        dt = np.append(dt_OLD, dt)

    ch_dump[str(dumps)] = ch
    #ts_dump[str(dumps)] = ts
    dt_dump[str(dumps)] = dt
    t0_dump[str(dumps)] = t0

    print "Done!"

    for d in range(len(t0_dump)):
        if d == 0:
            ridiculous_dt = np.zeros(len(t0_dump))
            ridiculous_dts = np.zeros([0])
            total_evts = 0

        total_evts += len(dt_dump[str(d)])
        ridiculous_dt[d] = len(dt_dump[str(d)][np.where(dt_dump[str(d)] > 1000)[0]])
        ridiculous_dts = np.append(ridiculous_dts, dt_dump[str(d)]\
                [np.where(dt_dump[str(d)] > 1000)[0]])
        
    if sum(t0_dump['0']) > 0:
        print "Detected a total of %d events of which %d are ridiculous. \nThis is %.2f %% of the total events.\nThe ridiculous dts have mean value %.2e s. They appear in dumps %s."%(total_evts, sum(ridiculous_dt), len(ridiculous_dt)/float(total_evts), mean(ridiculous_dts[0:10])*qutau.get_timebase(), np.where(ridiculous_dt != 0)[0])
    else:
        print "No data dumps."

    return ch_dump, ts*qutau.get_timebase(), t0_dump, dt_dump, ridiculous_dt, ridiculous_dts


def configure_axes():
    fontsize = 8

    mpl.rcParams['figure.subplot.bottom'] = 0.18
    mpl.rcParams['figure.subplot.left'] = 0.2
    mpl.rcParams['figure.figsize'] = (4.,3.)

    mpl.rc('font',**{'size': fontsize, 'family':'sans-serif','sans-serif':['Arial']})


def plot(t0_dump, dt_dump):
    
    for d in range(len(t0_dump)):

        if d == 0:
            Dt = np.zeros([0])
            T0 = np.zeros([0])

        Dt = np.append(Dt, dt_dump[str(d)][np.where(dt_dump[str(d)] < 3000)[0]])
        T0 = np.append(T0, t0_dump[str(d)][np.where(t0_dump[str(d)] < 3000)[0]])
    
    fig = plt.figure()
    plt.hist(Dt*qutau.get_timebase()*1E9, bins = 100)
    plt.xlabel('dt (ns)')
    plt.ylabel('clicks')
    configure_axes()
    fig.savefig('dt.png')    
    plt.show()


    fig2 = plt.figure()
    plt.hist(T0*qutau.get_timebase()*1E9, bins = 100)
    plt.xlabel('t0 (ns)')
    plt.ylabel('clicks')
    configure_axes()
    fig2.savefig('t0.png')    
    plt.show()


def just_read_out_qutau(meastime, BuffSize):
    qutau.set_buffer_size(BuffSize)
    stopmaar = False
    save = False
    sp = r'C:\Users\localadmin\Desktop\test_data'
    dt = time.strftime('%Y%m%d')
    hr = time.strftime('%H%M%S')
    tm = dt+'_'+hr

    os.mkdir(os.path.join(sp, tm))

    timebase = qutau.get_timebase()
    
    ch = np.zeros([0], dtype = ctypes.c_uint8)
    ts = np.zeros([0], dtype = ctypes.c_uint64)
    ch_OLD = np.zeros([0], dtype = ctypes.c_uint8)
    ts_OLD = np.zeros([0], dtype = ctypes.c_uint64)
    
    dumps = 0
    ch_dump = dict()
    ts_dump = dict() 
    valids = dict()
    VAL = np.zeros([0], dtype = np.uint)

    tstart = time.clock()

    while IntEgrAt000rR(tstart, meastime) and not(stopmaar):

        if len(ch_OLD) > 1E6:
            #if the length of the accumulated data is more than 1E6 elements, 
            #store the data in a dictionary.
            print "\n================= DATA DUMP %d =================\n"%(dumps+1)
            ch_dump[str(dumps)] = ch_OLD
            ts_dump[str(dumps)] = ts_OLD            
            valids[str(dumps)] = VAL
           
            ch_OLD = np.zeros([0], dtype = ctypes.c_uint64)
            ts_OLD = np.zeros([0], dtype = ctypes.c_uint8)
            VAL = np.zeros([0], dtype = np.uint)

            dumps += 1
        
        #read the values from the qutau
        [ts, ch, valid] = qutau.get_last_timestamps(buffer_size = BuffSize, reset = True)
        
        #pause acquisition for a moment
        time.sleep(100E-3)

        #keep track of the size of the valid events in the buffer
        VAL = np.append(VAL, valid)
    
        if valid > 0:

            if valid >= BuffSize:
                print "Quit because of overflow..."; stopmaar = True
            else:    
                ts = np.frombuffer(ts, dtype = ctypes.c_uint64)
                ch = np.frombuffer(ch, dtype = ctypes.c_uint8) 
                
                ts = ts[:valid]
                ch = ch[:valid]
                
                print "Memory full percentage: %.4f%%, length of array: %d"\
                        %(valid/float(BuffSize)*100, len(ch))

                #append the fresh data to data that was read-out previously
               
                ch = np.append(ch_OLD, ch)
                ts = np.append(ts_OLD, ts)        
               
                ch_OLD = ch
                ts_OLD = ts    

        #if qutau.get_data_lost():
        #    print "Data Lost!"
        #    stopmaar = True

        if msvcrt.kbhit() and msvcrt.getch() == 'q':
            print "No shit, you pressed Q!"
            stopmaar = True            
                

    tend = time.clock()
    print "Integration time was %.4e s."%(tend-tstart)

    
    ch_dump[str(dumps)] = ch_OLD
    ts_dump[str(dumps)] = ts_OLD
    valids[str(dumps)] = VAL

    print "Done!"

    return ch_dump, ts_dump, tend-tstart, valids


def analyze_chdump(ch_dump, integration_time, BurstPeriod, pattern, awg):

    errs = list()
    len_errs = 0
    len_ch_dump = 0
    for k in range(len(ch_dump)):
        print "Analyzing errors in data dump %d"%(k)

        if len(pattern) == 3:
            #force it to be a numpy array of integer type
            pattern = np.asarray(pattern).astype(np.uintc)
            Errors = errors.general_detect_pattern_error(ch_dump[str(k)].astype(np.uintc), pattern)
        else:
            print "Pattern input not understood."

        errs.append(Errors)
        len_errs += len(Errors)
        len_ch_dump += len(ch_dump[str(k)])

    print "\nTotal errors: %d in the array of length %d. This is %.3f%% of the elements in the array"\
            %(len_errs, len_ch_dump, len_errs/float(len_ch_dump)*100)

    if not(awg):
        actual_evts = 3*integration_time*3/BurstPeriod
    else:
        actual_evts = 5E6*3
    
    print "I should have detected %d events, but have detected %.2f%% of the events."\
            %(actual_evts, len_ch_dump/float(actual_evts)*100)

    return errs, len_errs


def analyze_dts(ts_dump, errs):
    
    dts_old = np.zeros([0])
    a = 0
    b = 0
    jump_size = list()
    exc_steps = list()

    print "\nAnalyzing dt..."
    
    for k in range(len(ts_dump)):

        dts = errors.analyze_timestamps(ts_dump[str(k)].astype(np.uintc), np.asarray(errs[k]).astype(np.uintc))

        dts = np.append(dts_old, dts)
        dts_old = dts

        a += len(np.where(np.diff(ts_dump[str(k)]) < 0)[0])
        
        all_dt = np.diff(ts_dump[str(k)])
        Exc_steps = np.where(all_dt > 60E4)[0]
        exc_steps.append(Exc_steps)

        b += len(Exc_steps)
        exc_ssize = np.mean(all_dt[Exc_steps])

        if np.isnan(exc_ssize):
            exc_ssize = 0

            if k == 0:
                fig2 = plt.figure()
                plt.hist(all_dt[all_dt < 60E4]*qutau.get_timebase()*1E9, bins = 100, color = 'orange', histtype = 'stepfilled')
                plt.title('Histogram for dt, without the excessive jumps.')
                plt.xlabel('dt (ns)')
                plt.ylabel('Clicks')
                configure_axes()
                plt.show()

        else:
            jump_size.append(exc_ssize)
            
            fig2 = plt.figure()
            plt.hist(all_dt[all_dt < 60E4]*qutau.get_timebase()*1E9, bins = 100, color = 'red')
            plt.title('Excessive jumps excluded (dump %d).'%k)
            plt.xlabel('dt (ns)')
            plt.ylabel('Clicks')
            configure_axes()
           
            fig3 = plt.figure()
            plt.hist(all_dt[all_dt > 60E4]*qutau.get_timebase()*1E6, bins = 100, color = 'red')
            plt.title('Excessive jumps only (dump %d).'%k)
            plt.xlabel('dt (ms)')
            plt.ylabel('Clicks')
            configure_axes()

            
    print "Found %d negative jumps and %d excessive possitive jumps. The mean positive jump stepsize of the excessive jumps is %.4e"\
            %(a, b, np.mean(jump_size)*qutau.get_timebase())
        
            
    return dts, exc_steps


def analyze_t0s(ts_dump, errs, exc_steps, valids, plot_individial_runs = False):
    
    print '\nAnalyzing t0...'

    configure_axes()

    #time differences between buffer read-out and a huge jump (if any)
    Dt_Jump = np.array([])

    for k in range(len(ts_dump)):
        y = ts_dump[str(k)]*qutau.get_timebase()
        
        if plot_individial_runs:
            fig = plt.figure()
            plt.hold(True)
            plt.title('Dump %d'%k)
            plt.plot(y, '-b')

            #draw errors, time jumps etc.
            if len(errs[k]) > 0:
                plt.plot(np.asarray(errs[k]), y[np.asarray(errs[k])], 'or',
                        label = 'CH error')

        if len(exc_steps[k]) > 0:
            if plot_individial_runs:
                ax = fig.gca()

            for j in exc_steps[k]:
                if plot_individial_runs:
                    ax.annotate('Huge jump', xy=(j, y[j]),  xycoords='data',
                            xytext=(-50, 30), textcoords='offset points',
                            arrowprops=dict(arrowstyle="->"))
                

                cumvalids = np.cumsum(valids[str(k)])

                if len(np.where(j-cumvalids > 0)[0]) != 0:
                    smallest_dt = j - cumvalids[np.max(np.where(j-cumvalids > 0)[0])]
                else:
                    smallest_dt = j

                Dt_Jump = np.append(Dt_Jump, smallest_dt)
                
        if len(valids[str(k)])>0 and plot_individial_runs:

            for i in np.cumsum(valids[str(k)]):
                plt.plot([i,i], [0, max(y)], '--g')
        
        dt = time.strftime('%Y%m%d')
        hr = time.strftime('%H%M%S')
        
        if plot_individial_runs:
            plt.ylim([min(y), max(y)+1])
            plt.xlim([0, max(np.cumsum(valids[str(k)]))])

            plt.xlabel('Array index (time)')
            plt.ylabel('t0 (s)')
            plt.ticklabel_format(style='sci', axis='x', scilimits=(0,0))
            plt.hold(False)
            plt.legend(fancybox = True, shadow = True, loc = 4)
            configure_axes()
            fig.savefig(os.path.join(os.getcwd(), '%s_t0_analysis_%d'%(dt+'_'+hr, k)))

    if len(Dt_Jump) > 0:
        fig_dt_jumps = plt.figure()
        plt.hist(Dt_Jump, bins = 50, color = 'purple')
        plt.xlabel('Time from buffer read-out to time jump (# of array elements)')
        plt.ylabel('Occurrence')
        plt.title('%s_dt_jumps'%(dt+'_'+hr))
        plt.ticklabel_format(style='sci', axis='x', scilimits=(0,0))    
        fig_dt_jumps.savefig(os.path.join(os.getcwd(), '%s_dt_jumps'%(dt+'_'+hr)))
    
    plt.show()

    return Dt_Jump


def clearall():
    """clear all globals"""
    for uniquevar in [var for var in globals().copy() if var[0] != "_" and var != 'clearall']:
        del globals()[uniquevar]


def test_reading_out(meastime, BuffSize):
    qutau.set_buffer_size(BuffSize)
    stopmaar = False

    timebase = qutau.get_timebase()
    tstart = time.clock()

    lup = 0

    while IntEgrAt000rR(tstart, meastime) and not(stopmaar):
        [ts, ch, valid] = qutau.get_last_timestamps(buffer_size = BuffSize, reset = True)
        ts = ts[:valid]
        ch = ch[:valid]
        print "Time elapsed: %.3f ms."%((time.clock()-tstart)*1E3)
        
        if valid > 0:
            print "%d\tMemory full percentage: %.4f%%, length of array: %d"\
                    %(lup, valid/float(BuffSize)*100, len(ch))

            if valid == BuffSize:
                print "Quit because of overflow..."; stopmaar = True
        else: 
            qutau.get_device_params() 
        
        
        if qutau.get_data_lost():
            print "Data Lost!"
            stopmaar = True


        if msvcrt.kbhit() and msvcrt.getch() == 'q':
            print "No shit, you pressed Q!"
            stopmaar = True

        time.sleep(100E-3)
        #qt.msleep(100E-3)
        
        print "Time elapsed: %.3f ms."%((time.clock()-tstart)*1E3)

        lup+=1


def test_command(meastime):

    stopmaar = False
    lup = 0
    tstart = time.clock()

    while IntEgrAt000rR(tstart, meastime) and not(stopmaar):
        
        t0 = time.clock()

        x = qutau.get_device_params()
        
        print "%d. ... %s, time elapsed is %.5f ms."%(lup, x, (time.clock()-t0)*1E3)

        if msvcrt.kbhit() and msvcrt.getch() == 'q':
            print "No shit, you pressed Q!"
            stopmaar = True

        lup+=1    

        #qt.msleep(100E-3)
        time.sleep(100E-3)


if __name__ == '__main__':
    
    BuffSize = 1E6
    Greet = 30
    selftest = True
    awg = False
    testmode = False

    if selftest:
        pattern = [3,1,0]
        BurstPeriod = 12E-6
        prepare_selftest(BuffSize, BurstPeriod)
        print "Ready..."
        qt.msleep(100E-3)
        #test_reading_out(Greet, BuffSize)
        ch_dump, ts_dump, integration_time, valids = just_read_out_qutau(Greet, BuffSize)
        stop_selftest()

        errs, len_errs = analyze_chdump(ch_dump, integration_time, BurstPeriod, pattern, awg)

        dts, exc_steps = analyze_dts(ts_dump, errs)
        
        if len(dts) > 0 or not(np.all(exc_steps == np.empty([]))):
            analyze_t0s(ts_dump, errs, exc_steps, valids, plot_individial_runs = False)
    elif testmode:
        BurstPeriod = 12E-6
        prepare_selftest(BuffSize, BurstPeriod)
        #qt.instruments.reload(qutau)
        qt.msleep(1.0)
        print "Start testing the command..."
        test_command(Greet)
    elif awg:
        BurstPeriod = None
        pattern = [0,1,2]
        prepare(BuffSize)
        print "Ready..."

        ch_dump, ts_dump, integration_time, valids = just_read_out_qutau(Greet, BuffSize)

        errs, len_errs = analyze_chdump(ch_dump, integration_time, BurstPeriod, pattern, awg)

        dts, exc_steps = analyze_dts(ts_dump, errs)
        
        if len(dts) > 0 or not(np.all(exc_steps == np.empty([]))):
            analyze_t0s(ts_dump, errs, exc_steps, valids, plot_individial_runs = False)

    else: #other test mode
        BurstPeriod = 12E-6
        
        #fill up the buffer:
        prepare_selftest(BuffSize, BurstPeriod)
        qt.msleep(3)
        #stop_selftest()
 
        test_reading_out(Greet, BuffSize)



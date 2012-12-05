import os
from analysis import fit, common
from analysis.lde import spcorr
reload(spcorr)

plt.close('all')

first_time = True
time_steps = False
setup='lt2'

spcorr.set_setup(setup)

if setup == 'lt1':
    F0 = 0.919
    F1 = 0.9933
    F0err = 2.E-3
    F1err = 0.6E-3
else:
    F0 = 0.8087
    F1 = 0.9933 
    F0err = 0.002135
    F1err = 0.000691

#workflow for the first run.
if first_time:
    datfolder = r'D:\measuring\data\20121013\220208_LDE_Spin Photon LT2'
    rawfolder = os.path.join(datfolder, 'rawdata-000')
    
    os.chdir(datfolder)

    ssro_data = spcorr.prepare(datfolder, rawfolder, ch0maxtime=1100, 
            ch1maxtime=1100, do_filter_crap=False, do_plot=True)
    hhpludat = spcorr.prepare_correlations(datfolder)

offset = 0
window_length=100

w1_starts = (645+offset,670+offset)
w2_starts = (645+offset,670+offset)
w1_stops = (645+window_length+offset,670+window_length+offset)
w2_stops = (645+window_length+offset,670+window_length+offset)

matplotlib.rc('xtick', labelsize=14) 

##########################
#### BASIC ROUTINE #######
##########################

correlations = spcorr.correlations(hhpludat, ssro_data, w1_start=w1_starts, \
        w2_start=w2_starts, w1_stop=w1_stops, w2_stop=w2_stops)

spcorr.barplot_correlations(datfolder, correlations, F0, F1, F0err, F1err)

np.savez(os.path.join(datfolder,'correlations_etc.npz'),
        w1_starts = w1_starts, w2_starts = w2_starts,
        w1_stops = w1_stops, w2_stops = w2_stops,
        correlations = correlations)

# correlations: first two elements first window (0 counts, >0 counts)
# second two elements: second window (0 counts, >0 counts)

spcorr.plot_crs(setup, datfolder)
spcorr.plot_tail(datfolder, w1_starts, w2_starts, w1_stops, w2_stops)

#########################
#### TIME RELATED #######
#########################

if time_steps:
    spcorr.correlations_vs_time(hhpludat = hhpludat, ssro_data = ssro_data, 
            w1_starts = w1_starts, w2_starts = w2_starts, 
            max_window_len = window_length, F0 = F0, F1 = F1, 
            F0err = F0err, F1err = F1err, datapath = datapath, steps = 21)




       

import msvcrt
import numpy as np
import qt
import hdf5_data as h5
import logging

import measurement.lib.measurement2.measurement as m2
from measurement.lib.measurement2.adwin_ssro import ssro
from measurement.lib.measurement2.adwin_ssro.pulsar import PulsarMeasurement
from measurement.lib.pulsar import pulse, pulselib, element, pulsar

from measurement.lib.cython.PQ_T2_tools import T2_tools

class PQPulsarMeasurement(PulsarMeasurement):
    mprefix = 'PQPulsarMeasurement'
    
    def __init__(self, name):
        PulsarMeasurement.__init__(self, name)
        self.params['measurement_type'] = self.mprefix

    def setup(self, **kw):
        do_calibrate = kw.pop('pq_calibrate',True)
        PulsarMeasurement.setup(self,**kw)

        if self.PQ_ins.OpenDevice():
            self.PQ_ins.start_T2_mode()
            self.PQ_ins.set_Binning(self.params['BINSIZE'])
            if do_calibrate:
                self.PQ_ins.calibrate()
        else:
            raise(Exception('Picoquant instrument '+self.PQ_ins.get_name()+ ' cannot be opened: Close the gui?'))


    def run(self, autoconfig=True, setup=True):
        if autoconfig:
            self.autoconfig()
            
        if setup:
            self.setup()


        rawdata_idx = 1
        t_ofl = 0
        t_lastsync = 0
        last_sync_number = 0
    
        # note: for the live data, 32 bit is enough ('u4') since timing uses overflows.
        dset_hhtime = self.h5data.create_dataset('PQ_time-{}'.format(rawdata_idx), 
            (0,), 'u8', maxshape=(None,))
        dset_hhchannel = self.h5data.create_dataset('PQ_channel-{}'.format(rawdata_idx), 
            (0,), 'u1', maxshape=(None,))
        dset_hhspecial = self.h5data.create_dataset('PQ_special-{}'.format(rawdata_idx), 
            (0,), 'u1', maxshape=(None,))
        dset_hhsynctime = self.h5data.create_dataset('PQ_sync_time-{}'.format(rawdata_idx), 
            (0,), 'u8', maxshape=(None,))
        dset_hhsyncnumber = self.h5data.create_dataset('PQ_sync_number-{}'.format(rawdata_idx), 
            (0,), 'u4', maxshape=(None,))      
        current_dset_length = 0
        
        self.PQ_ins.StartMeas(int(self.params['measurement_time'] * 1e3)) # this is in ms
        qt.msleep(.5)
        self.start_adwin_process(stop_processes=['counter'])
        qt.msleep(.5)
        self.start_keystroke_monitor('abort',timer=False)

        while(self.PQ_ins.get_MeasRunning() and self.adwin_process_running()):

            self._keystroke_check('abort')
            if self.keystroke('abort') in ['q','Q']:
                print 'aborted.'
                self.stop_keystroke_monitor('abort')
                break
            reps_completed = self.adwin_var('completed_reps')
            if reps_completed > 0 and np.mod(reps_completed,100)==0:           
                print('completed %s / %s readout repetitions' % \
                        (reps_completed, self.params['SSRO_repetitions']))

            _length, _data = self.PQ_ins.get_TTTR_Data()
                
            if _length > 0:
                _t, _c, _s = self._PQ_decode(_data[:_length])
                
                hhtime, hhchannel, hhspecial, sync_time, sync_number, \
                    newlength, t_ofl, t_lastsync, last_sync_number = \
                        T2_tools.LDE_live_filter(_t, _c, _s, t_ofl, t_lastsync, last_sync_number,
                            np.uint64(self.params['MIN_SYNC_BIN']), np.uint64(self.params['MAX_SYNC_BIN']))

                if newlength > 0:

                    dset_hhtime.resize((current_dset_length+newlength,))
                    dset_hhchannel.resize((current_dset_length+newlength,))
                    dset_hhspecial.resize((current_dset_length+newlength,))
                    dset_hhsynctime.resize((current_dset_length+newlength,))
                    dset_hhsyncnumber.resize((current_dset_length+newlength,))

                    dset_hhtime[current_dset_length:] = hhtime
                    dset_hhchannel[current_dset_length:] = hhchannel
                    dset_hhspecial[current_dset_length:] = hhspecial
                    dset_hhsynctime[current_dset_length:] = sync_time
                    dset_hhsyncnumber[current_dset_length:] = sync_number

                    current_dset_length += newlength
                    self.h5data.flush()

                if current_dset_length > self.params['MAX_DATA_LEN']:
                    rawdata_idx += 1
                    dset_hhtime = self.h5data.create_dataset('PQ_time-{}'.format(rawdata_idx), 
                        (0,), 'u8', maxshape=(None,))
                    dset_hhchannel = self.h5data.create_dataset('PQ_channel-{}'.format(rawdata_idx), 
                        (0,), 'u1', maxshape=(None,))
                    dset_hhspecial = self.h5data.create_dataset('PQ_special-{}'.format(rawdata_idx), 
                        (0,), 'u1', maxshape=(None,))
                    dset_hhsynctime = self.h5data.create_dataset('PQ_sync_time-{}'.format(rawdata_idx), 
                        (0,), 'u8', maxshape=(None,))
                    dset_hhsyncnumber = self.h5data.create_dataset('PQ_sync_number-{}'.format(rawdata_idx), 
                        (0,), 'u4', maxshape=(None,))         
                    current_dset_length = 0

                    self.h5data.flush()

        self.PQ_ins.StopMeas()


        try:
            self.stop_keystroke_monitor('abort')
        except KeyError:
            pass # means it's already stopped
        
        self.stop_adwin_process()
        reps_completed = self.adwin_var('completed_reps')
        print('Total completed %s / %s readout repetitions' % \
                (reps_completed, self.params['SSRO_repetitions']))

    def _PQ_decode(self,data):
        """
        Decode the binary data into event time (absolute, highest precision),
        channel number and special bit. See PicoQuant (HydraHarp, TimeHarp, PicoHarp) 
        documentation about the details.
        """
        event_time = np.bitwise_and(data, 2**25-1)
        channel = np.bitwise_and(np.right_shift(data, 25), 2**6 - 1)
        special = np.bitwise_and(np.right_shift(data, 31), 1)
        return event_time, channel, special
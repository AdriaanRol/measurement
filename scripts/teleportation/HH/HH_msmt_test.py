"""
Test data acquisition with the HH.
"""

import numpy as np
import logging
import qt
import hdf5_data as h5

import measurement.lib.config.adwins as adwins_cfg
import measurement.lib.measurement2.measurement as m2
from measurement.lib.pulsar import pulse, pulselib, element, pulsar

import T2_tools
reload(T2_tools)

class HHTest(m2.Measurement):

    mprefix = 'HH'

    def __init__(self):
        m2.Measurement.__init__(self, 'test')

    def test_sequence(self):
        sync = pulse.SquarePulse(channel = 'HH_sync',
            length = 50e-9, amplitude = 2)
        sync_T = pulse.SquarePulse(channel = 'HH_sync',
            length = 1e-6, amplitude = 0)

        photon = pulse.SquarePulse(channel = 'HH_test',
            length = 50e-9, amplitude = 2)
        photon_T = pulse.SquarePulse(channel = 'HH_test',
            length = 1e-6, amplitude = 0)

        MA1 = pulse.SquarePulse(channel = 'HH_MA1',
            length = 50e-9, amplitude = 2)
        MA1_T = pulse.SquarePulse(channel = 'HH_MA1',
            length = 1e-6, amplitude = 0)

        no_syncs_elt = element.Element('photon_without_sync', pulsar=qt.pulsar)
        no_syncs_elt.append(photon)
        no_syncs_elt.append(pulse.cp(photon_T, length=1e-6))

        syncs_elt_mod0 = element.Element('2_syncs_photon_after_first', pulsar=qt.pulsar)
        syncs_elt_mod0.append(sync_T)
        s1 = syncs_elt_mod0.append(sync)
        syncs_elt_mod0.append(pulse.cp(sync_T, length=500e-9))
        s2 = syncs_elt_mod0.append(sync)
        syncs_elt_mod0.append(pulse.cp(sync_T, length=10e-6))
        syncs_elt_mod0.add(photon,
            start = 50e-9,
            refpulse = s1)

        seq = pulsar.Sequence('HH_testing')
        seq.append(name = 'photon_without_sync',
            wfname = no_syncs_elt.name,
            repetitions = 100)
        seq.append(name = 'photon_after_sync1',
            wfname = syncs_elt_mod0.name,
            repetitions = 100)

        qt.pulsar.upload(no_syncs_elt, syncs_elt_mod0)
        qt.pulsar.program_sequence(seq)

        self.AWG.set_runmode('SEQ')
        self.AWG.start()

    def _HH_decode(self, data):
        """
        Decode the binary data into event time (absolute, highest precision),
        channel number and special bit. See HH documentation about the details.
        """

        event_time = np.bitwise_and(data, 2**25-1)
        channel = np.bitwise_and(np.right_shift(data, 25), 2**6 - 1)
        special = np.bitwise_and(np.right_shift(data, 31), 1)

        return event_time, channel, special

    def measurement_loop(self):
        self.HH.start_T2_mode()
        self.HH.calibrate()
        rawdata_idx = 1
        t_ofl = 0
        t_lastsync = 0

        # note: for the live data, 32 bit is enough ('u4') since timing uses overflows.
        dset_hhtime = self.h5data.create_dataset('HH_time-{}'.format(rawdata_idx), 
            (0,), 'u8', maxshape=(None,))
        dset_hhchannel = self.h5data.create_dataset('HH_channel-{}'.format(rawdata_idx), 
            (0,), 'u1', maxshape=(None,))
        dset_hhspecial = self.h5data.create_dataset('HH_special-{}'.format(rawdata_idx), 
            (0,), 'u1', maxshape=(None,))
        dset_hhsynctime = self.h5data.create_dataset('HH_sync_time-{}'.format(rawdata_idx), 
            (0,), 'u8', maxshape=(None,))
        
        current_dset_length = 0

        self.HH.StartMeas(int(MSMT_TIME*1e3))

        while self.HH.get_MeasRunning():
            _length, _data = self.HH.get_TTTR_Data()
            
            if _length > 0:
                _t, _c, _s = self._HH_decode(_data[:_length])
                hhtime, hhchannel, hhspecial, sync_time, newlength, t_ofl, t_lastsync = \
                    T2_tools.LDE_live_filter(_t, _c, _s, t_ofl, t_lastsync)

                if newlength > 0:

                    dset_hhtime.resize((current_dset_length+newlength,))
                    dset_hhchannel.resize((current_dset_length+newlength,))
                    dset_hhspecial.resize((current_dset_length+newlength,))
                    dset_hhsynctime.resize((current_dset_length+newlength,))

                    dset_hhtime[current_dset_length:] = hhtime
                    dset_hhchannel[current_dset_length:] = hhchannel
                    dset_hhspecial[current_dset_length:] = hhspecial
                    dset_hhsynctime[current_dset_length:] = sync_time

                    current_dset_length += newlength
                    self.h5data.flush()


MSMT_TIME = 60 # seconds
MAX_RAWDATA_LEN = int(1e6)

HHTest.AWG = qt.instruments['AWG']
HHTest.HH = qt.instruments['HH_400']

def run():
    m = HHTest()
    m.test_sequence()
    m.measurement_loop()
    m.save_params()
    m.finish()

if __name__ == '__main__':
    run()




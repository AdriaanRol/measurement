
from measurement.lib.pulsar import pulse, pulselib, element, pulsar

import measurement.lib.measurement2.measurement as m2
from measurement.lib.measurement2.adwin_ssro.pulsar import PulsarMeasurement





class AWGSSROCalibration(PulsarMeasurement):
    mprefix = 'AWGSSROCalibration'
           
    def autoconfig(self):
        PulsarMeasurement.autoconfig(self)
        self.params['sequence_wait_time'] = \
            int(np.ceil(self.params['SSRO_duration'])+10)

        print 'SEQ_WAIT_TIME', self.params['sequence_wait_time']

    def setup(self,HH=True):
        PulsarMeasurement.setup(self)
        if HH:
            self.hharp.start_T2_mode()
            self.hharp.calibrate()

    def generate_sequence(self, upload=True):

        # define the necessary pulse

        V=self.E_aom.power_to_voltage(self.params['Ex_RO_amplitude'], controller='sec')
        print V
        qt.pulsar_remote.set_channel_opt('Velocity1AOM','high', V)
        HH_sync = pulse.SquarePulse(channel = 'HH_sync', length = 50e-9, amplitude = 1.0)
        TT = pulse.SquarePulse(channel='HH_sync', length = 1000e-9, amplitude = 0)
        RO = pulse.SquarePulse(channel='Velocity1AOM', length = self.params['SSRO_duration']*1e-6, amplitude = 1)


        # make the elements - one for each ssb frequency
        e = element.Element('RO',pulsar=qt.pulsar_remote)
        e.append(TT)
        e.append(HH_sync)
        e.append(TT)
        e.append(RO)


        # create a sequence from the pulses
        seq = pulsar.Sequence('SSRO sequence')
        seq.append(name=e.name, wfname=e.name, trigger_wait=True)

        # upload the waveforms to the AWG
        if upload:
            qt.pulsar_remote.upload(e)

        # program the AWG
        qt.pulsar_remote.program_sequence(seq)

        # some debugging:
        # elements[-1].print_overview()

    def _HH_decode(self, data):
        """
        Decode the binary data into event time (absolute, highest precision),
        channel number and special bit. See HH documentation about the details.
        """
        event_time = np.bitwise_and(data, 2**25-1)
        channel = np.bitwise_and(np.right_shift(data, 25), 2**6 - 1)
        special = np.bitwise_and(np.right_shift(data, 31), 1)
        return event_time, channel, special

    def run(self, autoconfig=True, setup=True, HH=True):

        if autoconfig:
            self.autoconfig()
            
        if setup:
            self.setup(HH)
            
        for key,_val in self.adwin_dict[self.adwin_processes_key]\
                [self.adwin_process]['params_long']:
            try:
                self.adwin_process_params[key] = self.params[key]
            except:
                logging.error("Cannot set adwin process variable '%s'" \
                        % key)
                return False

        self.adwin_process_params['Ex_CR_voltage'] = \
                self.E_aom.power_to_voltage(
                        self.params['Ex_CR_amplitude'])
        
        self.adwin_process_params['A_CR_voltage'] = \
                self.A_aom.power_to_voltage(
                        self.params['A_CR_amplitude'])

        self.adwin_process_params['Ex_SP_voltage'] = \
                self.E_aom.power_to_voltage(
                        self.params['Ex_SP_amplitude'])

        self.adwin_process_params['A_SP_voltage'] = \
                self.A_aom.power_to_voltage(
                        self.params['A_SP_amplitude'])

        self.adwin_process_params['Ex_RO_voltage'] = \
                self.E_aom.power_to_voltage(
                        self.params['Ex_RO_amplitude'])

        self.adwin_process_params['A_RO_voltage'] = \
                self.A_aom.power_to_voltage(
                        self.params['A_RO_amplitude'])
                       
        self.adwin_process_params['repump_voltage'] = \
                self.repump_aom.power_to_voltage(
                        self.params['repump_amplitude'])
                
        self.adwin_process_params['repump_off_voltage'] = \
                self.params['repump_off_voltage']
        self.adwin_process_params['A_off_voltage'] = \
                self.params['A_off_voltage']
        self.adwin_process_params['Ex_off_voltage'] = \
                self.params['Ex_off_voltage']
        

        if HH:
            rawdata_idx = 1
            t_ofl = 0
            t_lastsync = 0
            last_sync_number = 0

            # note: for the live data, 32 bit is enough ('u4') since timing uses overflows.
            dset_hhtime = self.h5data.create_dataset('HH_time-{}'.format(rawdata_idx), 
                (0,), 'u8', maxshape=(None,))
            dset_hhchannel = self.h5data.create_dataset('HH_channel-{}'.format(rawdata_idx), 
                (0,), 'u1', maxshape=(None,))
            dset_hhspecial = self.h5data.create_dataset('HH_special-{}'.format(rawdata_idx), 
                (0,), 'u1', maxshape=(None,))
            dset_hhsynctime = self.h5data.create_dataset('HH_sync_time-{}'.format(rawdata_idx), 
                (0,), 'u8', maxshape=(None,))
            dset_hhsyncnumber = self.h5data.create_dataset('HH_sync_number-{}'.format(rawdata_idx), 
                (0,), 'u4', maxshape=(None,))      
            current_dset_length = 0
            
            self.hharp.StartMeas(int(self.params['measurement_time']* 1e3)) # this is in ms
            qt.msleep(0.1)


        self.start_adwin_process(stop_processes=['counter'])
        qt.msleep(1)
        self.start_keystroke_monitor('abort',timer=False)
               
        while self.adwin_process_running():
            self._keystroke_check('abort')
            if self.keystroke('abort') in ['q','Q']:
                print 'aborted.'
                self.stop_keystroke_monitor('abort')
                break

            
            if HH:
                if not self.hharp.get_MeasRunning():
                    print 'HH done.'
                    self.stop_keystroke_monitor('abort')
                    break

                _length, _data = self.hharp.get_TTTR_Data()
            
                if _length > 0:
                    _t, _c, _s = self._HH_decode(_data[:_length])
                    
                    hhtime, hhchannel, hhspecial, sync_time, sync_number, \
                        newlength, t_ofl, t_lastsync, last_sync_number = \
                            T2_tools.LDE_live_filter(_t, _c, _s, t_ofl, t_lastsync, last_sync_number,
                                np.uint64(HH_MIN_SYNC_TIME), np.uint64(HH_MAX_SYNC_TIME))

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

                    if current_dset_length > MAX_HHDATA_LEN:
                        rawdata_idx += 1
                        dset_hhtime = self.h5data.create_dataset('HH_time-{}'.format(rawdata_idx), 
                            (0,), 'u8', maxshape=(None,))
                        dset_hhchannel = self.h5data.create_dataset('HH_channel-{}'.format(rawdata_idx), 
                            (0,), 'u1', maxshape=(None,))
                        dset_hhspecial = self.h5data.create_dataset('HH_special-{}'.format(rawdata_idx), 
                            (0,), 'u1', maxshape=(None,))
                        dset_hhsynctime = self.h5data.create_dataset('HH_sync_time-{}'.format(rawdata_idx), 
                            (0,), 'u8', maxshape=(None,))
                        dset_hhsyncnumber = self.h5data.create_dataset('HH_sync_number-{}'.format(rawdata_idx), 
                            (0,), 'u4', maxshape=(None,))         
                        current_dset_length = 0

                        self.h5data.flush()
        
        self.stop_adwin_process()
        try:
            self.stop_keystroke_monitor('abort')
        except KeyError:
            pass # means it's already stopped
        
        reps_completed = self.adwin_var('completed_reps')
        print('completed %s / %s readout repetitions' % \
                (reps_completed, self.params['SSRO_repetitions']))
        
        if HH:
            self.hharp.StopMeas()

#ssro.AdwinSSRO.A_aom = qt.instruments['MatisseAOM_lt1']
#ssro.AdwinSSRO.E_aom = qt.instruments['NewfocusAOM_lt1']
AWGSSROCalibration.hharp = qt.instruments['HH_400']
MAX_HHDATA_LEN = int(100e6)
DO_LDE_ATTEMPT_MARKER = True # if True, insert a marker to the HH after each sync
DO_OPT_RABI_AMP_SWEEP = False # if true, we sweep the rabi parameters instead of doing LDE; essentially this only affects the sequence we make
HH_MIN_SYNC_TIME = 1e6 # 1 us
HH_MAX_SYNC_TIME = 15e6 # 15 us

def awgssrocalibration(name):

    m=AWGSSROCalibration(name)


    m.params.from_dict(qt.cfgman['protocols']['AdwinSSRO'])
    m.params.from_dict(qt.cfgman['protocols']['hans-sil4-default']['AdwinSSRO'])    
    
    ssro.AdwinSSRO.repump_aom = qt.instruments['YellowAOM_lt1']
    m.params['repump_duration'] = m.params['yellow_repump_duration']
    m.params['repump_amplitude'] = m.params['yellow_repump_amplitude']

    m.params['send_AWG_start']=1

    m.params['measurement_time']=2000 #seconds, max time after the HH times out.
    m.params['pts']=1
    m.params['repetitions']=5000
    m.params['SSRO_duration']=10

    # parameters
    m.params['CR_preselect'] = 500
    m.params['CR_probe'] = 2
    m.params['SSRO_repetitions'] = 5000
    m.params['A_CR_amplitude'] = 5e-9
    m.params['Ex_CR_amplitude'] = 1e-9
    m.params['CR_duration'] = 100

    # calibration ms0 or one by hand!
    m.params['A_SP_amplitude'] = 0e-9
    m.params['Ex_SP_amplitude'] = 10e-9
    m.params['Ex_RO_amplitude'] = 30e-9 #10e-9

    m.autoconfig()
    m.generate_sequence(upload=True)
    m.run(autoconfig=False,setup=True,HH=True)
    m.save()
    m.finish()


if __name__ == '__main__':
    awgssrocalibration('lt1_sil4')
 
    
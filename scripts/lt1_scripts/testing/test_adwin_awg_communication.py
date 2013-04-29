import qt
from measurement.lib.AWG_HW_sequencer_v2 import Sequence
from measurement.lib.config import awgchannels as awgcfg

awg = qt.instruments['AWG']
pa = qt.instruments['physical_adwin']

chan_adsync = 'adwin_sync'

# make the AWG sequence
seq = Sequence('adwin_comm_test')
awgcfg.configure_sequence(seq, 'adwin')

seq.add_element('test1', goto_target='test1', 
        trigger_wait=True)
seq.add_pulse('waitabit', chan_adsync, 'test1', 
        duration=10000, amplitude=0)
seq.add_pulse('donesignal', chan_adsync, 'test1',
        duration=100, amplitude=2, 
        start_reference='waitabit', link_start_to='end')

seq.set_instrument(awg)
seq.set_clock(1e9)
seq.set_send_waveforms(True)
seq.set_send_sequence(True)
seq.set_program_channels(True)
seq.set_start_sequence(True)
seq.force_HW_sequencing(True)
seq.send_sequence()

# load and start the adwin program
# TODO ATM do via adbasic

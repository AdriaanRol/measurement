from measurement.lib.pulsar import pulse, pulselib, element, pulsar
import msvcrt
def turn_on_pulse():
	p=pulse.SinePulse(channel='EOM_Matisse', name='pp', length=100e-6, frequency=1/(100e-6), amplitude = 1.8)
	qt.pulsar.set_channel_opt('EOM_AOM_Matisse', 'low', 1.0)
	e=element.Element('Sinde', pulsar=qt.pulsar)
	e.append(p)
	e.print_overview()
	s= pulsar.Sequence('Sinde')
	s.append(name = 'Sine',
	                wfname = e.name,
	                trigger_wait = 0)
	qt.pulsar.upload(e)
	qt.pulsar.program_sequence(s)
	AWG.set_runmode('SEQ')
	AWG.start()

	while 1:
		if (msvcrt.kbhit() and (msvcrt.getch() == 'q')): break
		qt.msleep(0.1)
	AWG.stop()
	AWG.set_runmode('CONT')
	qt.pulsar.set_channel_opt('EOM_AOM_Matisse', 'low', 0.0)

if __name__ == '__main__':
	turn_on_pulse()
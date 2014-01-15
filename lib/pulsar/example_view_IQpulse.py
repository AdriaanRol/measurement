import numpy as np
import pulse
import pulselib
import element
import view

reload(pulse)
reload(element)
reload(view)
reload(pulselib)

e = element.Element('sequence_element', clock=1e9, min_samples=0)
e.define_channel('MW_Imod')
e.define_channel('MW_Qmod')
e.define_channel('MW_pulsemod')

X = pulselib.MW_IQmod_pulse('Weak pi-pulse', 
	I_channel='MW_Imod', Q_channel='MW_Qmod', 
	PM_channel='MW_pulsemod',
	frequency = 50e6,
	amplitude = 1.,
	length = 50e-9,
	PM_risetime = 5e-9)

e.add(X)
e.print_overview()
print e.next_pulse_time('MW_Imod'), e.next_pulse_time('MW_Qmod'), \
    e.next_pulse_time('MW_pulsemod')

view.show_element(e)

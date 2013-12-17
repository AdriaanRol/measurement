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
e.define_channel('EOM_Matisse')
e.define_channel('EOM_AOM_Matisse')

opt_pulse = pulselib.short_EOMAOMPulse('Eom Aom Pulse', 
        eom_channel = 'EOM_Matisse',
        aom_channel = 'EOM_AOM_Matisse')

e.add(opt_pulse)
e.print_overview()
print e.next_pulse_time('EOM_Matisse'), e.next_pulse_time('EOM_AOM_Matisse')

view.show_element(e)

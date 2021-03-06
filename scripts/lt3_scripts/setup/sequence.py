import qt

from measurement.lib.pulsar import pulsar
reload(pulsar)

pulsar.Pulsar.AWG = qt.instruments['AWG']

# FIXME in principle we only want to create that once, at startup
try:
    del qt.pulsar 
except:
    pass
qt.pulsar = pulsar.Pulsar()
qt.pulsar.AWG_type = 'opt09'

### channels
# RF
# qt.pulsar.define_channel(id='ch2', name='RF', type='analog', high=1.0,
#     low=-1.0, offset=0., delay=242e-9, active=True)

# MW
qt.pulsar.define_channel(id='ch1_marker1', name='MW_pulsemod', type='marker', 
    high=2.0, low=0, offset=0., delay=260e-9, active=True)
qt.pulsar.define_channel(id='ch1', name='MW_Imod', type='analog', high=0.9,
    low=-0.9, offset=0., delay=240e-9, active=True)


#TH
qt.pulsar.define_channel(id='ch3_marker1', name='TH_sync', type='marker', 
    high=2.0, low=0, offset=0., delay=0., active=True)   
# sync ADwin
qt.pulsar.define_channel(id='ch3_marker2', name='adwin_sync', type='marker', 
    high=2.0, low=0, offset=0., delay=0., active=True)

#qt.pulsar.define_channel(id='ch3_marker1', name='HH_MA1', type='marker', 
#    high=2.0, low=0, offset=0., delay=0., active=True)
    
#EOM
qt.pulsar.define_channel(id='ch4', name='EOM_Matisse', type='analog', high=2.0,
    low=-2.0, offset=0., delay=172e-9, active=True)
#AOMs
qt.pulsar.define_channel(id='ch4_marker1', name='EOM_AOM_Matisse', type='marker', 
    high=1.0, low=0.0, offset=0., delay=602e-9, active=True)
qt.pulsar.define_channel(id='ch4_marker2', name='EOM_trigger', type='marker',
     high=1.0, low=0.0, offset=0., delay=0e-9, active=True)

qt.pulsar.define_channel(id='ch2_marker1', name='AOM_Newfocus', type='marker',
    high=0.4, low=0.0, offset=0., delay=466e-9, active=True)
qt.pulsar.set_channel_opt('AOM_Newfocus','high', qt.instruments['NewfocusAOM'].get_sec_V_max())
qt.pulsar.set_channel_opt('AOM_Newfocus','low',  qt.instruments['NewfocusAOM'].get_sec_V_off())

#qt.pulsar.define_channel(id='ch3_marker2', name='AOM_Yellow', type='marker',
#     high=0.4, low=0.0, offset=0., delay=466e-9, active=True)
#qt.pulsar.set_channel_opt('AOM_Yellow','high', qt.instruments['YellowAOM'].get_sec_V_max())
#qt.pulsar.set_channel_opt('AOM_Yellow','low', qt.instruments['YellowAOM'].get_sec_V_off())

#PLU
qt.pulsar.define_channel(id='ch2_marker2', name='plu_sync', type='marker', 
    high=2.0, low=0, offset=0., delay=14e-9, active=True)

### TMP HH debug channel -- normally there's RF on this output.
#qt.pulsar.define_channel(id='ch2', name='HH_test', type='analog', high=2.0,
#    low=0, offset=0., delay=0, active=True)
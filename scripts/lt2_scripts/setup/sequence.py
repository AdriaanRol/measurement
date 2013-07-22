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

### channels
# RF
qt.pulsar.define_channel(id='ch2', name='RF', type='analog', high=1.0,
    low=-1.0, offset=0., delay=242e-9, active=True)

# MW
qt.pulsar.define_channel(id='ch1_marker1', name='MW_pulsemod', type='marker', 
    high=2.0, low=0, offset=0., delay=258*1e-9, active=True)
qt.pulsar.define_channel(id='ch1', name='MW_Imod', type='analog', high=0.9,
    low=-0.9, offset=0., delay=239*1e-9, active=True)
qt.pulsar.define_channel(id='ch3', name='MW_Qmod', type='analog', high=0.9,
    low=-0.9, offset=0., delay=242*1e-9, active=True)

# sync ADwin
qt.pulsar.define_channel(id='ch1_marker2', name='adwin_sync', type='marker', 
    high=2.0, low=0, offset=0., delay=0., active=True)

#HH
qt.pulsar.define_channel(id='ch2_marker2', name='HH_sync', type='marker', 
    high=2.0, low=0, offset=0., delay=0., active=True)   
qt.pulsar.define_channel(id='ch3_marker1', name='HH_MA1', type='marker', 
    high=2.0, low=0, offset=0., delay=0., active=True)
    
#EOM
qt.pulsar.define_channel(id='ch4', name='EOM_Matisse', type='analog', high=1.5,
    low=-1.5, offset=0., delay=234e-9, active=True)
#AOMs
qt.pulsar.define_channel(id='ch4_marker1', name='EOM_AOM_Matisse', type='marker', 
    high=1.0, low=0.0, offset=0., delay=496e-9, active=True)
qt.pulsar.define_channel(id='ch2_marker1', name='AOM_Newfocus', type='marker',
    high=1.0, low=0.0, offset=0., delay=525e-9, active=True)
qt.pulsar.define_channel(id='ch3_marker2', name='AOM_Yellow', type='marker',
    high=1.0, low=0.0, offset=0., delay=500e-9, active=True)
#PLU
#qt.pulsar.define_channel(id='XXX', name='plu_sync', type='marker', 
#    high=2.0, low=0, offset=0., delay=133e-9, active=True)
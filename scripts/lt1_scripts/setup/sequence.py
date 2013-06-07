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
qt.pulsar.define_channel(id='ch1', name='RF', type='analog', high=1.0,
    low=-1.0, offset=0., delay=165e-9, active=True)

# MW
qt.pulsar.define_channel(id='ch1_marker1', name='MW_pulsemod', type='marker', 
    high=2.0, low=0, offset=0., delay=(44+165)*1e-9, active=True)
qt.pulsar.define_channel(id='ch3', name='MW_Imod', type='analog', high=0.9,
    low=-0.9, offset=0., delay=(27+165)*1e-9, active=True)
qt.pulsar.define_channel(id='ch4', name='MW_Qmod', type='analog', high=0.9,
    low=-0.9, offset=0., delay=(27+165)*1e-9, active=True)

# sync ADwin
qt.pulsar.define_channel(id='ch3_marker2', name='adwin_sync', type='marker', 
    high=2.0, low=0, offset=0., delay=0., active=True)


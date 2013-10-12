qt.instruments.reload('adwin_lt1')


####
print 'reload all measurement parameters and calibrations for lt1...'
execfile(os.path.join(qt.config['startdir'], 'lt1_scripts/setup/msmt_params.py'))

# set all the static variables for lt1
execfile(os.path.join(qt.config['startdir'], 'lt2_scripts/setup/lt1_statics.py'))


# FIXME in principle we only want to create that once, at startup
try:
    del qt.pulsar 
except:
    pass
qt.pulsar = pulsar.Pulsar()

qt.pulsar.AWG = qt.instruments['AWG_lt1']

### channels

# for the remote LDE setup. effectively this is the relative delay between SP AOM and MWs.
spin_of = -69e-9

# RF
qt.pulsar.define_channel(id='ch1', name='RF', type='analog', high=1.0,
    low=-1.0, offset=0., delay=spin_of+165e-9, active=True)

# MW
qt.pulsar.define_channel(id='ch1_marker1', name='MW_pulsemod', type='marker', 
    high=2.0, low=0, offset=0., delay=spin_of+(44+165)*1e-9, active=True)
qt.pulsar.define_channel(id='ch3', name='MW_Imod', type='analog', high=0.9,
    low=-0.9, offset=0., delay=spin_of+(27+165)*1e-9, active=True)
qt.pulsar.define_channel(id='ch4', name='MW_Qmod', type='analog', high=0.9,
    low=-0.9, offset=0., delay=spin_of+(27+165)*1e-9, active=True)

# sync ADwin
qt.pulsar.define_channel(id='ch3_marker2', name='adwin_sync', type='marker', 
    high=2.0, low=0, offset=0., delay=0., active=True)

# light -- delay of SP is here *defined* as 700 (trigger comes from the other AWG); 
# all other delays are then relative to that.
qt.pulsar.define_channel(id='ch2', name='Velocity1AOM', type='analog', 
    high=0.4, low=0, offset=0., delay=700e-9, active=True)

qt.pulsar.define_channel(id='ch2_marker2', name='YellowAOM', type='marker', 
    high=0.4, low=0, offset=0., delay=750e-9, active=True) 

# Trigger AWG LT2
qt.pulsar.define_channel(id='ch3_marker1', name='AWG_LT2_trigger', type='marker', 
    high=2.0, low=0, offset=0., delay=0., active=True)

# Sync for HH
qt.pulsar.define_channel(id='ch4_marker1', name='HH_sync', type='marker', 
    high=2.0, low=0, offset=0., delay=0., active=True)
qt.instruments.reload('adwin_lt1')

###
print 'reload all modules'
execfile(os.path.join(qt.config['startdir'], 'lt2_scripts/setup/reload_all.py'))

####
print 'reload all measurement parameters and calibrations for lt1...'
execfile(os.path.join(qt.config['startdir'], 'lt1_scripts/setup/msmt_params.py'))

# set all the static variables for lt1
execfile(os.path.join(qt.config['startdir'], 'lt2_scripts/setup/lt1_statics.py'))

try:
    del qt.pulsar 
except:
    pass
qt.pulsar = qt.pulsar_remote
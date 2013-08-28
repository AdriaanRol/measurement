
####
print 'reload all measurement parameters and calibrations for lt1...'
execfile(os.path.join(qt.config['startdir'], 'lt2_scripts/setup/msmt_params_lt1.py'))

# set all the static variables for lt1
execfile(os.path.join(qt.config['startdir'], 'lt2_scripts/setup/lt1_statics.py'))



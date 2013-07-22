print 'loading setup tools...'
from tools import stools
reload(stools)

print 'reload all modules...'
execfile("setup/reload_all.py")

####
print 'reload all measurement parameters and calibrations...'
execfile("setup/msmt_params.py")

####
print 'configure the setup-specific hardware...'
# set all the static variables for lt2
execfile('setup/sequence.py')

# set all the static variables for lt2
execfile('setup/lt2_statics.py')



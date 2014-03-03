qt.current_setup='lt3'

qt.get_setup_instrument = lambda x: qt.instruments[x] \
    if qt.config['instance_name'][-3:] == qt.current_setup \
    else qt.instruments[x+'_'+qt.current_setup]

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
execfile('setup/lt3_statics.py')



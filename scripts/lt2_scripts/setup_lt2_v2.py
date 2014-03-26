qt.current_setup= "_scripts/setup_lt2_v2.py"

qt.get_setup_instrument = lambda x: qt.instruments[x] \
    if qt.config['instance_name'][-3:] == qt.current_setup \
    else qt.instruments[x+'_'+qt.current_setup]

print 'loading setup tools...'
from lt2_scripts.tools import stools
reload(stools)

print 'reload all modules...'
execfile("lt2_scripts/setup/reload_all.py")

####
print 'configure the setup-specific hardware...'
# set all the static variables for lt2
execfile(os.path.join(qt.config['startdir'],'lt2_scripts/setup/sequence.py'))

# set all the static variables for lt2
execfile('lt2_scripts/setup/lt2_statics.py')



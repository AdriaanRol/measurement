# some helpers for the setup.
# author: wolfgang

from qt import instruments
from lib.file_support.settingsfile import SettingsFile

info = {
    'keyword' : '',
    'p7889_running' : False,
    }

def restore_from_data(path):
    """
    Main function: has a variable 'RESTORE', which is a dictionary in the form
    of {'instrument_name' : ['property', ...], ...}. The function walks through,
    and tries to set the listed properties via the .set-file specified in
    the argument.
    """
    RESTORE = {
        'pos_stage' : [
            'x_position',
            'y_position',
            ],
        'pos_det_sm' : [
            'x_position',
            'y_position',
            ],
        'pos_back_sm' : [
            'x_position',
            'y_position',
            ],
        'pos_z_front' : [
            'position',
            ],
        'pos_z_back' : [
            'position',
            ]
        }

    settings = SettingsFile(path)

    for ins in RESTORE:
        for param in RESTORE[ins]:
            print 'Try to restore %s from %s...' % (param, ins)

            try:
                instruments[ins].set(param,
                                     settings.get(ins, param))
                print ' ... restored to %s.' % str(settings.get(ins, param))
            except:
                print ' ... could not restore!'

    return

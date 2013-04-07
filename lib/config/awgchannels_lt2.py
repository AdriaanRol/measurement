"""
In this module we store information about AWG channels, i.e. which devices
are connected to what, and with what kind of configurations.
"""

config = {}

config['hydraharp'] = {
        'HH_sync' : {
            'AWG_channel' : 'ch2m2',
            'cable_delay' : 0.},#-58.0},
        'HH_MA1' : {
            'AWG_channel' : 'ch3m1',
            'cable_delay' : 0.,#-58.0,
            'high' : 2.0, },

        }

config['hydraharp+adwin'] = {
        'HH_sync' : {
            'AWG_channel' : 'ch2m2',
            'cable_delay' : 0., },
        'HH_MA1' : {
            'AWG_channel' : 'ch3m1',
            'cable_delay' : 0.,
            'high' : 2.0, },
        'ADwin_sync' : {
            'AWG_channel' : 'ch3m2',
            'high' : 2.0,
            'cable_delay' : 0., },
        #'ADwin_cond' : {
        #    'AWG_channel' : 'ch4m2',
        #    'high': 2.0,
        #    'cable_delay' : 0., },
        }

config['mw_weak_meas'] = {
        'MW_pulsemod': {
            'AWG_channel' : 'ch1m1',
            'high' : 2.0,
            'low' : 0.0,
            'default_voltage':0.0,
            'cable_delay' : 258,
            },
        'MW_Imod' : {
            'AWG_channel' : 'ch1',
            'high' : 0.9,
            'low' : -0.9,
            'cable_delay': 239,
            },
        'MW_Qmod' : {
            'AWG_channel' : 'ch3',
            'high' : 0.9,
            'low' : -0.9,
            'cable_delay': 242,
            },
        'RF' : {
            'AWG_channel' : 'ch2',
            'high' : 1.,
            'low' : -1.,
            'cable_delay': 242,
            },
        'ADwin_trigger' : {
            'AWG_channel' : 'ch1m2',
            'high' : 2.,
            'low' : 0.,
            'cable_delay': 0,
            },
        }

config['mw'] = {
        'MW_pulsemod': {
            'AWG_channel' : 'ch1m1',
            'high' : 2.0,
            'low' : 0.0,
            'default_voltage':0.0,
            'cable_delay' : 258,
            },
        'MW_Imod' : {
            'AWG_channel' : 'ch1',
            'high' : 0.9,
            'low' : -0.9,
            'cable_delay': 239,
            },
        'MW_Qmod' : {
            'AWG_channel' : 'ch3',
            'high' : 0.9,
            'low' : -0.9,
            'cable_delay': 242,
            },
        'MW_Imod_lt1' : {
            'AWG_channel' : 'ch2',
            'high' : 0.9,
            'low' : -0.9,
            'cable_delay': 258,
            },
        'MW_Qmod_lt1' : {
            'AWG_channel' : 'ch1m2',
            'high' : 0.9,
            'low' : 0,
            'cable_delay': 253,
            },
        'MW_pulsemod_lt1': {
            'AWG_channel' : 'ch3m2',
            'high' : 2.0,
            'low' : 0.0,
            'default_voltage':0.0,
            'cable_delay' : 260,
            },
        }


config['ssro'] = {
        'AOM_Newfocus' : {
            'AWG_channel' : 'ch2m1',
            'high' : 0.8,
            'cable_delay' : 540, },
        'AOM_Matisse' : {
            'AWG_channel' : 'ch2',
            'high' : 1.0,
            'cable_delay' : 665, },
        }

config['rf'] = {
        'RF' : {
            'AWG_channel' : '',
            'high' : 2.0,
            'low' : -2.0,
            'cable_delay' : 120, }
        }


config['LDE'] = {
       'EOM_Matisse' : {
            'AWG_channel' : 'ch4',
            'high' : 1.5,
            'low' : -1.5,
            'cable_delay' : 234, 
            'default_voltage' : 0.0,
            },
        'EOM_AOM_Matisse' : {
            'AWG_channel' : 'ch4m1',
            'high' : 1.0,
            'low' : 0.01,
            'cable_delay' : 445, 
            },
        'AOM_Newfocus' : {
            'AWG_channel' : 'ch2m1',
            'high' : 0.8,
            'low' : 0.0, 
            'cable_delay' : 525, 
            },
        'PLU_gate' : {
            'AWG_channel' : 'ch4m2',
            'high' : 2.,
            'low' : 0.,
            'default_voltage' : 0.0,
            'cable_delay' : 133, #87#145
            },
        }

config['optical_rabi'] = {
        'EOM_Matisse' : {
            'AWG_channel' : 'ch4',
            'high' : 1.5,
            'low' : -1.5,
            'cable_delay' : 234, 
            'default_voltage' : 0.0,
            },
        'EOM_AOM_Matisse' : {
            'AWG_channel' : 'ch4m1',
            'high' : 0.8,
            'low' : 0.01,
            'cable_delay' : 445, 
            },
        'AOM_Newfocus' : {
            'AWG_channel' : 'ch2m1',
            'high' : 0.8,
            'cable_delay' : 525, 
            },        
        'HH_Marker' : {
            'AWG_channel' : 'ch3m1',
            'high' : 2.,
            'low' : 0.,
            'default_voltage' : 0.0,            
            'cable_delay' : 0, 
            },
        }


def configure_sequence(sequence, *use, **use_modified):
    """
    Creates the channel configuration on the given sequence.
    Expects arguments in the form:
 
     config_name, [...]
    
    each configuration given is loaded with default parameters as specified in
    this module.
    
    to override default settings, modifications must be given in the following 
    form, with config_name now being a keyword argument.
        
     config_name = { 'channel name' : { 'option' : new_value, [...] }, [...] }

    Returns the sequence again.
    """

    for cfg in use:
        for chan in config[cfg]:
            sequence.add_channel(chan, **config[cfg][chan])
    
    for cfg in use_modified:        
        newcfg = config[cfg].copy()
        
        # update the channel config with the override options
        for chan in use_modified[cfg]:
            newcfg[chan].update(use_modified[cfg][chan])

        for chan in newcfg:
            sequence.add_channel(chan, **newcfg[chan])

    return sequence

        

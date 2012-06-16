"""
In this module we store information about AWG channels, i.e. which devices
are connected to what, and with what kind of configurations.
"""

config = {}

config['hydraharp'] = {
        'HH_sync' : {
            'AWG_channel' : 'ch2m2',
            'cable_delay' : 0. - 50, },
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

config['mw'] = {
        'MW_pulsemod': {
            'AWG_channel' : 'ch1m1',
            'high' : 2.0,
            'low' : 0.0,
            'cable_delay' : 570,
            },
        'MW_Imod' : {
            'AWG_channel' : 'ch1',
            'high' : 0.9,
            'low' : -0.9,
            'cable_delay': 549,
            },
        'MW_Qmod' : {
            'AWG_channel' : 'ch3',
            'high' : 0.9,
            'low' : -0.9,
            'cable_delay': 549,
            },
        'MW_Imod_lt1' : {
            'AWG_channel' : 'ch2',
            'high' : 0.9,
            'low' : -0.9,
            'cable_delay': 549,
            },
        'MW_Qmod_lt1' : {
            'AWG_channel' : 'ch1m2',
            'high' : 0.9,
            'low' : -0.9,
            'cable_delay': 549,
            }
        }


config['ssro'] = {
        'AOM_Newfocus' : {
            'AWG_channel' : 'ch2m1',
            'high' : 0.4,
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

config['optical_rabi'] = {
        'EOM_Matisse' : {
            'AWG_channel' : 'ch4',
            'high' : 1.5,
            'low' : -1.5,
            'cable_delay' : 132, 
            'default_voltage' : 0.0,
            },
        'EOM_AOM_Matisse' : {
            'AWG_channel' : 'ch4m1',
            'high' : 0.8,
            'low' : 0.01,
            'cable_delay' : 283, 
            },
        'AOM_Newfocus_lt1' : {
            'AWG_channel' : 'ch2m1',
            'high' : 0.4,
            'cable_delay' : 540, 
            },        
        'HH_Marker' : {
            'AWG_channel' : 'ch1m1',
            'high' : 2.,
            'low' : 0.,
            'default_voltage' : 0.0,            
            'cable_delay' : 0, 
            },
        'APD_Gate_2' : {
            'AWG_channel' : 'ch4m2',
            'high' : 2.,
            'low' : 0.,
            'default_voltage' : 2.0,
            'cable_delay' : 5*5+10, 
            },
        }


### DEPRECATED!
### For newer scripts this is now in the config manager
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

        

"""
In this module we store information about AWG channels, i.e. which devices
are connected to what, and with what kind of configurations.
"""

config = {}

config['picoharp'] = {
        'PH_start' : {
            'AWG_channel' : 'ch2m2',
            'cable_delay' : 0., },
        'PH_MA1' : {
            'AWG_channel' : 'ch3m1',
            'cable_delay' : 0.,
            'high' : 2.0, },
        }

# NOTE cable delays seem pretty good, 2012/12/23 (Wolfgang)
config['mw'] = {
        'MW_pulsemod': {
            'AWG_channel' : 'ch1m1',
            'high' : 2.0,
            'low' : 0.0,
            'cable_delay' : 140,
            },
        'MW_Imod' : {
            'AWG_channel' : 'ch3',
            'high' : 0.9,
            'low' : -0.9,
            'cable_delay': 120,
            },
        'MW_Qmod' : {
            'AWG_channel' : 'ch4',
            'high' : 0.9,
            'low' : -0.9,
            'cable_delay': 120,
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

        

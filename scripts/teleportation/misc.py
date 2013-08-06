"""
some helpful utilities.
"""
def get_AWG_AOM_voltage(aom,power):
    ret=0.0
    if aom.get_cur_controller()=='AWG':
        ret= aom.power_to_voltage(power)
    else:
        aom.apply_voltage(0)
        aom.set_cur_controller('AWG')
        ret = aom.power_to_voltage(power)
        aom.set_cur_controller('ADWIN')
    return ret  


start_msg = """

  ___________________          _-_                 _      _-_      _
  \__(==========/_=_/ ____.---'---`---.____      _|_|.---'---`---.|_|_
              \_ \    \----._________.----/      \----._________.----/
                \ \   /  /    `-_-'                  `.  `]-['  ,'
            __,--`.`-'..'-_                            `.' _ `.'
           /____          ||                            | (_) |
                `--.____,-'                              `___'

                          Beam us up, Ronny!

"""

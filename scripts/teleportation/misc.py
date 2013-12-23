"""
some helpful utilities.
"""
import qt

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


def lt1_zpl_hwp_flip(adwin='adwin_lt1', dio_no=5):
    _adwin = qt.instruments[adwin]
    _adwin.start_set_dio(load=True, dio_no=dio_no, dio_val=0)
    qt.msleep(0.2)
    _adwin.start_set_dio(load=False, dio_no=dio_no, dio_val=1)
    qt.msleep(0.2)
    _adwin.start_set_dio(load=False, dio_no=dio_no, dio_val=0)
    return


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
print start_msg
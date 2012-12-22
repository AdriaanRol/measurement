from lib import config
import os, time

def update_wpcfg(new_position, config_dir = r'D:\measuring\user\config'):

    if not(os.path.isfile(os.path.join(config_dir,'wp_position.cfg'))):
        wpcfg = config.create_config(
                os.path.join(config_dir, 'wp_position.cfg'))
        print 'wp_position.cfg created in '+config_dir 
    else:
        wpcfg = config.Config(os.path.join(config_dir, 'wp_position.cfg'))
        print 'wp_position.cfg opened from '+config_dir 
    
    try:
        cur_pos = wpcfg.get_all()['current_position']
    except KeyError:
        cur_pos = wpcfg.set('current_position', 'out')
        print '\tcurrent_position not a key, set to default value...'


    if new_position == 'in' or new_position == 'out':
        wpcfg.set("current_position", new_position)
        new_pos = wpcfg.get_all()['current_position']
        if cur_pos != new_pos:
            print '\tPosition changed to '+new_pos
        else:
            print '\tPosition not changed'
    else: print 'new_position input not understood, try in or out'

    #log the time
    wpcfg.set("Last update", time.ctime())

    return wpcfg

def get_wp_pos(wpcfg):
    return wpcfg.get_all()['current_position']









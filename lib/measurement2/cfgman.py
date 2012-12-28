# cfgman.py, class for handling configuration/calibration parameters
# Wolfgang Pfaff <wolfgangpfff at gmail dot com>
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA

import os, sys
import qt
from lib import config
import pprint

class ConfigManager:
    """
    This class allows simple handling of configuration parameters of simple
    types.
    It uses the qtlab lib.config.Config object as backend for immediate
    storage and the retrieval of the data.

    The ConfigManager can contain several configurations (imagine, for
    multiple samples, the setup, etc.). 

    Allowed data types are imposed by the choice of backend, in this case
    by lib.config.Config, which uses json. Therefore only simple types,
    like int, float, str, list, tuple, dict, and nesting of those, are
    supported at the moment.
    """

    path = qt.config['cfg_path']
    fileext = '.cfg'

    def __init__(self, name, *args):
        self.name = name
        self.configs = {}
        
        for n in args:
            self.add_cfg(n)

    def __getitem__(self, key):
        return self.configs[key]

    def __setitem__(self, key, dictionary):
        self.configs[key] = dictionary

    def keys(self):
        return self.configs.keys()

    def add_cfg(self, name):
        prefix = self.name + '_'
        self.configs[name] = config.Config(
                os.path.join(self.path,
                    prefix+name+self.fileext))

    def remove_cfg(self, name):
        del self.configs[name]

    def reload(self, name):
        self.configs[name].load()

    def reload_all(self):
        for n in self.configs:
            self.reload(n)

    def save(self, name):
        self.configs[name].save()

    def save_all(self):
        for n in self.configs:
            self.save(n)

    def show(self, name):
        '''
        prints the configuration given by name using pprint.
        '''
        cfg = self.configs[name].get_all()
        
        print
        print "Configuration '%s':" % name
        print "-"*78
        pprint.pprint(cfg, indent=4)

    def show_all(self):
        for n in self.configs:
            self.show(n)
        

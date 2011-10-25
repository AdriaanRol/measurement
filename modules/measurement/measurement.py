"""
This module contains the abstract class Measurement.
The goal is that other measurements are classes based on
this one. This can provide benefits, because measurements
usually have common features, like saving and plotting data,
which then do not have to be written explicitly if implemented
in a common parent class.

Furthermore, measurements can be based on other measurements,
e.g. by just introducing another outer parameter sweep, which can
also be facilitated by an OO approach like this one.
"""

import sys,os,time
import numpy as np
import matplotlib.pyplot as plt

import qt
from tools import data_handling as dh

class Measurement:
    """
    Implements the following, in order to avoid the need to implement
    common tasks in each measurement:

    """

    name = ''
    folder = ''
    basepath = ''

    def __init__(self, name, folder=None):
        
        self.name = name
        
        if folder != None:
            self.folder = folder
        else:
            self.basepath = dh.dummy_qtlab_measurement(self.name)
            self.folder, _tmp = os.path.split(self.basepath)

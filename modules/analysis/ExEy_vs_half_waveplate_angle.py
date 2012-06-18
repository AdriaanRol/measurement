### imports
import sys, os, time
from numpy import *
import numpy as np
from matplotlib import pyplot as plt

datafilename = '000'

data= loadtxt(datafilename+".dat")

cnts = []
frq = []
Ex = {'counts':[],'freq':[]}
Ey=  {'counts':[],'freq':[]}
for i in arange(len(data)):
    cnts.append(data[i][2])
    frq.append(data[i][1])
    if Exmin < data[i][1] > Exmax:
        Ex['counts'].append(data[i][2])
        Ex['freq'].append(data[i][1])
    if Eymin < data[i][1] > Eymax:
        Ey['counts'].append(data[i][2])
        Ey['freq'].append(data[i][1])
        

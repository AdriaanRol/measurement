import numpy as np

def rebin(inarray,order=2):
    outsize=int(np.floor(len(inarray)/order))
    outarray=np.zeros(outsize)
    for i in np.arange(outsize):
        outarray[i]=sum(inarray[i*order:(i+1)*order])
    return outarray

def average(inarray,order=2):
    outsize=int(np.floor(len(inarray)/order))
    outarray=np.zeros(outsize)
    for i in np.arange(outsize):
        outarray[i]=float(sum(inarray[i*order:(i+1)*order]))/order
    return outarray


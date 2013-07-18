import cython
import numpy as np
cimport numpy as cnp

@cython.boundscheck(False)
@cython.wraparound(False)
def general_detect_pattern_error(cnp.ndarray[cnp.uint_t, mode="c"] ch not None, 
        cnp.ndarray[cnp.uint_t, mode="c"] pat not None):
    """
    Scan an array for a pattern that is defined in "pat". 

    Input:
    ch      :   Array to be scanned for the pattern. Should be of type np.uintc
    pat     :   Array of length 3 of type np.uintc. 
                E.g. np.array([0,1,2], dtype = np.uintc)

    Output:
    errs    :   A list with the indices where the errors in the pattern were detected


    """

    cdef int k
    cdef int lench = ch.shape[0]
    
    errs = []

    for k in range(lench-2):
        
        if ch[k] == pat[0]:
            if not(ch[k+1] == pat[1]):
                errs.append(k)

        elif ch[k] == pat[1]:
            if not(ch[k+1] == pat[2]):
                errs.append(k)

        elif ch[k] == pat[2]:
            if not(ch[k+1] == pat[0]):
                errs.append(k)

    return errs

@cython.boundscheck(False)
@cython.wraparound(False)
def detect_deviation_type2(cnp.ndarray[cnp.uint_t, mode="c"] ch not None):
    """
    Detects deviations in patterns of the type ... 2, 1, 0, 2, 1, 0, ...
    """

    cdef int k
    cdef int lench = ch.shape[0]

    errs = []

    for k in range(lench-2):
        if ch[k+1] == (ch[k]-1)%3:
            pass
        else:
            errs.append(k)

    return errs

@cython.boundscheck(False)
@cython.wraparound(False)
def detect_deviation_type1(cnp.ndarray[cnp.uint_t, mode="c"] ch not None):
    """
    Detects deviations in patterns of the type ... 0, 1, 2, 0, 1, 2, ...
    """

    cdef int k
    cdef int lench = ch.shape[0]

    errs = []

    for k in range(lench-2):
        if ch[k+1] == (ch[k]+1)%3 and ch[k+2] == (ch[k]+2)%3:
            pass
        else:
            errs.append(k)

    return errs

@cython.boundscheck(False)
@cython.wraparound(False)
def analyze_timestamps(cnp.ndarray[cnp.uint_t, mode="c"] ts not None, 
        cnp.ndarray[cnp.uint_t, mode="c"] errs not None):
    """
    Returns a time difference for the events where an error was detected. 
    Error indexes are in "errs"
    """

    cdef int k, idx = 0
    cdef int lents = ts.shape[0]
    cdef int lenerrs = errs.shape[0]

    cdef cnp.ndarray[cnp.uint_t, mode="c"] dts = np.empty(lenerrs, dtype = np.uintc)

    for k in range(lenerrs):
        dts[idx] = ts[errs[k]+1] - ts[errs[k]]
        idx += 1

    return dts



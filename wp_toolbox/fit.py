import numpy as np
from numpy import *
from scipy import optimize
import pylab


# taken from the scipy fitting cookbook:
class Parameter:
    def __init__(self, value, name=''):
        self.value = value
        self.name = name

    def set(self, value):
        self.value = value

    def __call__(self):
        return self.value

def fit2d_scalar(function, parameters, x, y, z):
    def f(params):
        i = 0
        for p in parameters:
            p.set(params[i])
            i += 1
        return z - function(x, y)

    p = [ param() for param in parameters ]
    return optimize.leastsq(f, p, full_output=True)

def fit2d_gaussian_with_offset(x, y, z, x0, y0, A, sigma, h):

    # create params
    _A = Parameter(A, 'Amplitude')
    _x0 = Parameter(x0, 'x coordinate')
    _y0 = Parameter(y0, 'y coordinate')
    _sigma = Parameter(sigma, 'sigma')
    _h = Parameter(h, 'offset')
    p0 = [_A, _x0, _y0, _sigma, _h]

    def fitfunc(x, y): return _h() + _A() * np.exp((-(x-_x0())**2-(y-_y0())**2) \
                                                   /_sigma()**2/2.0)
    return _fit_return(fit2d_scalar(fitfunc, p0, x, y, z), z, p0, fitfunc(x, y))

def fit2d_grid(x, y, x0, y0, alpha, beta, gamma, delta, **kw):
    '''
    fit transformation in the shape of: 'LinTrafo(measured)' to
    the ideal grid, given by x0 and y0 vectors. 
    this actually does two separate fits for x and y, so this returns two
    result dictionaries, { 'x': x_result, 'y': y_result }
    if an alternative origin is given via ox and oy, then the trafo will be done
    as 'origin + lintrafo(measured-origin)' (not a fit parameter!)
    '''

    ox = kw.pop('ox', None)
    oy = kw.pop('oy', None)

    # create params
    _alpha = Parameter(alpha, 'alpha')
    _beta = Parameter(beta, 'beta')
    _gamma = Parameter(gamma, 'gamma')
    _delta = Parameter(delta, 'delta')
    p0x = [_alpha, _beta ]
    p0y = [_gamma, _delta ]

    if ox != None and oy != None:
        def fitfuncx(x, y): return ox + _alpha() * (x-ox) + _beta() * (y-oy)
        def fitfuncy(x, y): return oy + _gamma() * (x-ox) + _delta() * (y-oy)
    else:
        def fitfuncx(x, y): return _alpha() * x + _beta() * y
        def fitfuncy(x, y): return _gamma() * x + _delta() * y

    fitresx = _fit_return(fit2d_scalar(fitfuncx, p0x, x, y, x0), x0, p0x, fitfuncx(x, y))
    fitresy = _fit_return(fit2d_scalar(fitfuncy, p0y, x, y, y0), y0, p0y, fitfuncy(x, y))

    return { 'x': fitresx, 'y': fitresy }


def fit(function, parameters, y, x = None):
    def f(params):
        i = 0
        for p in parameters:
            p.set(params[i])
            i += 1
        return y - function(x)

    if x is None: x = arange(y.shape[0])
    p = [param() for param in parameters]
    return optimize.leastsq(f, p, full_output=True)

def fit_exponential_decay(x, y, A, tau):
    """
    Function assumes that decay starts at the first point,
    i.e. x-offset is given by the first x-value
    
    parameters:
    x = array of x values
    y = array of y data to fit
    A = i.g. for initial amplitude
    tau = i.g. for decay constant
    """

    # create parameters
    _A = Parameter(A, 'Amplitude')
    _tau = Parameter(tau, 'Decay constant')
    p0 = [_A, _tau]

    def fitfunc(x): return _A() * exp(-(x-x[0])/_tau())
    return _fit_return(fit(fitfunc, p0, y, x), y, p0, fitfunc(x))


def fit_exponential_decay_with_offset(x, y, A, tau, o):
    """
    Function assumes that decay starts at the first point,
    i.e. x-offset is given by the first x-value
    
    parameters:
    x = array of x values
    y = array of y data to fit
    A = i.g. for initial amplitude
    tau = i.g. for decay constant
    o = i.g. for offset
    """

    # create parameters
    _A = Parameter(A, 'Amplitude')
    _tau = Parameter(tau, 'Decay constant')
    _o = Parameter(o, 'Offset')
    p0 = [_A, _tau, _o]

    def fitfunc(x): return _o() + _A() * exp(-(x-x[0])/_tau())
    return _fit_return(fit(fitfunc, p0, y, x), y, p0, fitfunc(x))

def fit_exponential_rise_with_offset(x, y, A, tau, o):
    """
    Function assumes the amplitude is reached with the last x value,
    i.e. this gives the x-offset.
    
    parameters:
    x = array of x values
    y = array of y data to fit
    A = i.g. for final amplitude
    tau = i.g. for decay constant
    o = i.g. for offset
    """

    # create parameters
    _A = Parameter(A, 'Amplitude')
    _tau = Parameter(tau, 'Decay constant')
    _o = Parameter(o, 'Offset')
    p0 = [_A, _tau, _o]

    def fitfunc(x): return _o() + _A() * exp((x-x[-1])/_tau())
    return _fit_return(fit(fitfunc, p0, y, x), y, p0, fitfunc(x))
    

def fit_gaussian_with_offset(x, y, mu, A, sigma, h):
    """
    parameters:
    x = array of x values
    y = array of y values of data to fit
    mu = inital guess for x-offset
    A = initial guess for amplitude
    sigma = intial guess for std dev
    h = intial guess for y-offset
    """

    # create parameters
    _mu = Parameter(mu, 'mu')
    _A = Parameter(A, 'Amplitude')
    _sigma = Parameter(sigma, 'sigma')
    _h = Parameter(h, 'offset')
    p0 = [_mu, _A, _sigma, _h]

    def fitfunc(x): return _h() + _A() * exp(-((x-_mu())/_sigma())**2/2.0)
    return _fit_return(fit(fitfunc, p0, y, x), y, p0, fitfunc(x))

def fit_gaussian_on_slope_with_offset(x, y, a, mu, A, sigma, h):
    '''
    parameters:
    x =     array of x values
    y =     array of y data to fit
    a =     i.g. for slope
    mu =    i.g. for x-offset
    A =     i.g. for initial amplitude
    sigma = i.g. for std dev
    h =     i.g. for y-offset
    '''

    # create parameters
    _a = Parameter(a,'Slope')
    _mu = Parameter(mu, 'x-offset')
    _A = Parameter(A, 'Amplitude')
    _sigma = Parameter(sigma, 'Standard Deviation')
    _h = Parameter(h, 'y-offset')
    p0 = [_a, _mu, _A, _sigma, _h]

    def fitfunc(x): return _h() +  _a() * x + _A() * exp(-((x-_mu())/_sigma())**2/2.0)
    return _fit_return(fit(fitfunc, p0, y, x), y, p0, fitfunc(x))    
    
def fit_linear(x, y, a, b):
    '''
    parameters:
    x = array of x values
    y = array of y values of data to fit
    a = initial guess for slope
    b = initial guess for offset
    '''

    # create parameters
    _a = Parameter(a, 'Slope')
    _b = Parameter(b, 'Offset')
    p0 = [_a,_b]

    def fitfunc(x): return _b() + _a() * x
    return _fit_return(fit(fitfunc, p0, y, x), y, p0, fitfunc(x))

def fit_nv_saturation(x, y, Pinf, Psat):
    '''
    parameters:
    x = array of x values
    y = array of y values of data to fit
    Psat = initial guess for the saturation power
    Pinf = initial guess for Pinfinity
    '''

    # create parameters
    _Pinf = Parameter(Pinf, 'Pinf')
    _Psat = Parameter(Psat, 'Psat')

    p0 = [_Pinf,_Psat]

    def fitfunc(x): return (_Pinf() * x) / (_Psat() + x)
    return _fit_return(fit(fitfunc, p0, y, x), y, p0, fitfunc(x))
    
def fit_nv_saturation_with_background(x, y, offset, a, Pinf, Psat):
    '''
    parameters:
    x = array of x values
    y = array of y values of data to fit
    offset = of the signal data
    a = slope of the background data
    Psat = initial guess for the saturation power
    Pinf = initial guess for Pinfinity
    '''
    # create parameters
    _offset = Parameter(offset,'offset')
    _a = Parameter(a,'a')
    _Pinf = Parameter(Pinf, 'Pinf')
    _Psat = Parameter(Psat, 'Psat')
    p0 = [_offset,_a,_Pinf,_Psat]

    def fitfunc(x): return _offset() + (_a() * x) + (_Pinf() * x) / (_Psat() + x)
    return _fit_return(fit(fitfunc, p0, y, x), y, p0, fitfunc(x))

    
def fit_nv_g2(x, y, x0, A, c2, t2, c3, t3):
    '''
    parameters:
    x = array of x values
    y = array of y values of data to fit
    x0 = initial guess for the time offset
    A = initial guess for the normalization factor
    c2 = initial guess for c2
    t2 = initial guess for t2
    c3 = initial guess for c3
    t3 = initial guess for t3
    '''
    # create parameters
    _x0 = Parameter(x0, 'x0')
    _A = Parameter(A, 'A')
    _c2 = Parameter(c2, 'c2')
    _t2 = Parameter(t2, 't2')
    _c3 = Parameter(c3, 'c3')
    _t3 = Parameter(t3, 't3')
    p0 = [_x0,_A,_c2,_t2,_c3,_t3]

    def fitfunc(x): return (_A()* ( 1 + _c2()*exp(-abs(x-_x0())/_t2()) + _c3()*exp(-abs(x-_x0())/_t3()) ) )
    return _fit_return(fit(fitfunc, p0, y, x), y, p0, fitfunc(x))


def _fit_return(res, y, p0, fit):
    p1, cov, info, mesg, success = res
    if not success or cov == None: # FIXME: find a better solution!!!
        return False
    chisq = sum(info['fvec']*info['fvec'])
    dof = len(y)-len(p0)
    error_dict = {}
    error_list = []
    params_dict = {}
    # print cov, success, mesg, info
    for i,pmin in enumerate(p1):
        error_dict[p0[i].name] = sqrt(cov[i,i])*sqrt(chisq/dof)
        error_list.append(sqrt(cov[i,i])*sqrt(chisq/dof))
        params_dict[p0[i].name] = pmin
        

    result = {
        'success' : success,
        'params' : p1,
        'params_dict' : params_dict,
        'chisq': chisq,
        'dof': dof,
        'residuals_rms': sqrt(chisq/dof),
        'reduced_chisq': chisq/dof,
        'error' : error_list,
        'error_dict' : error_dict, 
        'fitdata' : fit,
        'cov' : cov,
        'p0' : p0,
        }
    return result


# for pylab usage (or other interactive)
def do_fit_predefined(func, *arg, **kw):
    result = func(*arg, **kw)
    print_fit_result(result)
    return result
    

def do_fit_func(fitfunc, p0, y, x):
    result = _fit_return(fit(fitfunc, p0, y, x), y, p0, fitfunc(x))
    print_fit_result(result)
    return result

    
def print_fit_result(result):
    if result == False:
       print "Could not fit data" 
    print "Converged with chi squared ", result['chisq']
    print "degrees of freedom, dof ", result['dof']
    print "RMS of residuals (i.e. sqrt(chisq/dof)) ", \
        sqrt(result['chisq']/result['dof'])
    print "Reduced chisq (i.e. variance of residuals) ", \
        result['chisq']/result['dof']
    print

    # uncertainties are calculated as per gnuplot, "fixing" the result
    # for non unit values of the reduced chisq.
    # values at min match gnuplot
    print "Fitted parameters at minimum, with 68% C.I.:"
    for i,pmin in enumerate(result['params']):
        print "%2i %-10s %12f +/- %10f" % \
            (i, result['p0'][i].name, pmin, result['error'][i])
    print
    print "Correlation matrix"

    # correlation matrix close to gnuplot
    print "               ",
    for i in range(len(result['p0'])): print "%-10s" % (result['p0'][i].name,),
    print
    for i in range(len(result['params'])):
        print "%10s" % result['p0'][i].name,
        for j in range(i+1):
            print "%10f" % \
                (result['cov'][i,j] / \
                     sqrt(result['cov'][i,i] * result['cov'][j,j]),),
        print
    

# just a small showcase
if __name__ == '__main__':
    # x axis for the data
    NUM = 1000
    x = r_[-10:10:complex(0, NUM)]

    # the ideal data points
    SIGMA = 1
    y_ideal = exp(-x**2/2/SIGMA**2)
    
    # create the data, including some noise
    y_data = random.randn(y_ideal.size) * 0.1 + y_ideal

    # guess start params, slightly off
    mu = Parameter(1.3, 'mu')
    sigma = Parameter(0.4, 'sigma')
    height = Parameter(1.2, 'height')
    p0 = [mu, sigma, height]
    
    # define a fitting function
    def fitfunc(x): return height() * exp(-(x - mu())**2 / (2.0 * sigma()**2))
    y_fit = do_fit_func(fitfunc, p0, y_data, x)['fitdata']

    # plot everything
    pylab.plot(x, y_ideal, 'g-')
    pylab.plot(x, y_data, 'bo')
    pylab.plot(x, y_fit, 'r-')
    pylab.show()


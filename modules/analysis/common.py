import numpy as np

# own modules
import analysis.fit as fit


### common fitfunctions
def fit_cos(g_f, g_a, g_A, g_phi, *arg):
    fitfunc_str = 'A * cos(2pi * (f*x + phi/360) ) + a'
    
    f = fit.Parameter(g_f, 'f')
    a = fit.Parameter(g_a, 'a')
    A = fit.Parameter(g_A, 'A')
    # phi = fit.Parameter(g_phi, 'phi')

    p0 = [f, a, A] #, phi]

    def fitfunc(x):
        return a() + A() * np.cos(2*np.pi*( f()*x + 0 )) #phi()/360.))

    return p0, fitfunc, fitfunc_str


def fit_exp_decay_with_offset(g_a, g_A, g_tau, *arg):
    """
    fitfunction for an exponential decay,
        y(x) = A * exp(-x/tau) + a

    Initial guesses (in this order):
        g_a : offset
        g_A : initial Amplitude
        g_tau : decay constant

    """
    fitfunc_str = 'A * exp(-x/tau) + a'

    a = fit.Parameter(g_a, 'a')
    A = fit.Parameter(g_A, 'A')
    tau = fit.Parameter(g_tau, 'tau')
    p0 = [a, A, tau]

    def fitfunc(x):
        return a() + A() * np.exp(-x/tau())

    return p0, fitfunc, fitfunc_str


def fit_saturation(g_A, g_xsat, *arg):
    """
    fitfunction for a saturation (e.g., the NV PL)
        y(x) = A * x / (x + xsat)

    I.g.:
        g_A : maximum signal (at x=infinity)
        g_xsat : saturation point
    """

    fitfunc_str = 'A * x / (x + x_sat)'
    
    A = fit.Parameter(g_A, 'A')
    xsat = fit.Parameter(g_xsat, 'xsat')
    p0 = [A, xsat]

    def fitfunc(x):
        return A() * x / (x + xsat())

    return p0, fitfunc, fitfunc_str


def fit_saturation_with_offset_linslope(g_a, g_b, g_A, g_xsat, *arg):
    """
    fitfunction for a saturation (e.g., the NV PL)
        y(x) = a + b*x + A * x / (x + xsat)

    I.g.:
        g_a : offset
        g_b : linear slope
        g_A : maximum signal (at x=infinity)
        g_xsat : saturation point
    """

    fitfunc_str = 'a + b*x + A * x / (x + x_sat)'
    
    a = fit.Parameter(g_a, 'a')
    b = fit.Parameter(g_b, 'b')
    A = fit.Parameter(g_A, 'A')
    xsat = fit.Parameter(g_xsat, 'xsat')
    p0 = [a, b, A, xsat]

    def fitfunc(x):
        return a() + b()*x + A() * x / (x + xsat())

    return p0, fitfunc, fitfunc_str

def fit_poly(indices, *arg):
    fitfunc_str = 'sum_n ( a[n] * x[n] )'

    idx = 0
    p0 = []
    for i,a in enumerate(indices):
        p0.append(fit.Parameter(a, 'a%d'%i))

    def fitfunc(x):
        val = 0
        for i in range(len(indices)):
            val += p0[i]() * x**i
        return val

    return p0, fitfunc, fitfunc_str

def fit_AOM_powerdependence(g_a, g_xc, g_k, *arg):
    fitfunc_str = 'a * exp(-exp(-k*(x-xc)))'

    a = fit.Parameter(g_a, 'a')
    xc = fit.Parameter(g_xc, 'xc')
    k = fit.Parameter(g_k, 'k')

    p0 = [a, xc, k]

    def fitfunc(x):
        return a() * np.exp(-np.exp(-k()*(x-xc())))

    return p0, fitfunc, fitfunc_str

def fit_gauss(g_a, g_A, g_x0, g_sigma):
    fitfunc_str = 'a + A * exp(-(x-x0)**2/sigma**2)'

    a = fit.Parameter(g_a, 'a')
    x0 = fit.Parameter(g_x0, 'x0')
    A = fit.Parameter(g_A, 'A')
    sigma = fit.Parameter(g_sigma, 'sigma')

    p0 = [a, x0, A, sigma]

    def fitfunc(x):
        return a() + A() * np.exp(-(x-x0())**2/sigma()**2)


    return p0, fitfunc, fitfunc_str

def fit_line(g_a, g_b, *arg):
    """
    fitfunction for a line
        y(x) = a + b*x 

    I.g.:
        g_a : offset
        g_b : linear slope
    """

    fitfunc_str = 'a + b*x' 
    
    a = fit.Parameter(g_a, 'a')
    b = fit.Parameter(g_b, 'b')
    #xsat = fit.Parameter(g_xsat, 'xsat')
    p0 = [a, b]

    def fitfunc(x):
        return a() + b()*x

    return p0, fitfunc, fitfunc_str

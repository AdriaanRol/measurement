from numpy import *

# own stuff
import analysis.fit as fit

### gaussian decay (FID, yielding T2*)
def fit_FID_gauss(g_tau, g_A, g_a, *arg):
    """
    fitfunction for a gaussian decay,
        y(x) = a + A*exp(-(x/tau)**2)

    Initial guesses (in this order):
        g_tau : decay constant
        g_A : amplitude
        g_a : offset
    """
    
    tau = fit.Parameter(g_tau, 'tau')
    A = fit.Parameter(g_A, 'A')
    a = fit.Parameter(g_a, 'a')
    p0 = [tau, A, a]
    def fitfunc(x): return a() + A()*exp(-(x/tau())**2)
    return p0, fitfunc, fitfunc_str

def fit_ramsey_gaussian_decay(g_tau, g_a, *arg):
    """
    fitfunction for a ramsey modulation, with gaussian decay,
        y(x) = a + A*exp(-(x/tau)**2) * mod,

        where:
        mod = sum_i(cos(2pi*f_i*x ) - 1)

    Initial guesses (in this order):
        g_tau : decay const
        g_A : Amplitude
        g_a : offset

        For the modulation:
        an arbitrary no of tuples, in the form
        (g_f, g_A)[i] = (frequency, Amplitude)[i]
    """
    fitfunc_str = 'y(x) = a + exp(-(x/tau)**2)*('
    no_frqs = len(arg)
    if no_frqs == 0:
        print 'no modulation frqs supplied'
        return False
    
    tau = fit.Parameter(g_tau, 'tau')
    # A = fit.Parameter(g_A, 'A')
    a = fit.Parameter(g_a, 'a')
    p0 = [tau, a]

    print 'fitting with %d modulation frequencies' % no_frqs

    frqs = []
    amplitudes = []
    #phases = []
    for i, m in enumerate(arg):
        fitfunc_str += 'A%d*cos(2pi*f%d*x)' % (i, i)
        frqs.append(fit.Parameter(m[0], 'f%d'%i))
        #phases.append(fit.Parameter(m[2], 'phi%d'%i))
        amplitudes.append(fit.Parameter(m[1], 'A%d'%i))
        p0.append(frqs[i])
        p0.append(amplitudes[i])
        #p0.append(phases[i])
    fitfunc_str += ')'

    def fitfunc(x):
        prd = exp(-(x/tau())**2)
        mod = 0
        for i in range(no_frqs):
            mod += amplitudes[i]() * (cos(2*pi*frqs[i]()*x))
        return a() + prd*mod

    return p0, fitfunc, fitfunc_str


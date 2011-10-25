import numpy as np

# own modules
import analysis.fit as fit


### common fitfunctions
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



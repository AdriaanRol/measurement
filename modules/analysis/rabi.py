from numpy import *

# our own modules
import analysis.fit as fit
import tools.plot as plot

### fit a rabi osc. that gets damped exponentially
def fit_rabi_damped_exp(g_f, g_A, g_a, g_phi, g_tau, *arg):
    """
    fits a cosine thats damped exponentially,
        y(x) = a + A * exp(-x/tau) * cos(f*x + phi)

    Initial guesses, in this order:
        g_f : frequency
        g_A : initial amplitude of the oscillation
        g_a : offset
        g_phi : phase
        g_tau : decay constant

    """
    fitfunc_str = "a + A * exp(-x/tau) * cos(f*x + phi)"

    f = fit.Parameter(g_f, 'f')
    A = fit.Parameter(g_A, 'A')
    a = fit.Parameter(g_a, 'a')
    phi = fit.Parameter(g_phi, 'phi')
    tau = fit.Parameter(g_tau, 'tau')
    p0 = [f, A, a, phi, tau]

    def fitfunc(x) : return a() + A() * exp(-x/tau()) * cos(2*pi*f()*x + phi())
    return p0, fitfunc, fitfunc_str
# end damped rabi

### cosine on a slope, see that frequently in rabi oscillations
def fit_rabi_with_phase_on_linslope(g_f, g_A, g_a, g_b, g_phi, *arg):
    """
    fits (and plots) a cosine on a slope, with offset,
        y(x) = a + bx + Acos(f*x + phi)

    Initial guesses (1st args, in this order):
        g_f : float
            guess for the frequency
        g_A : float
            guess for amplitude
        g_a : float
            guess for offset
        g_b = 0. : float
            guess for slope
        g_phi = 0. : float
            guess for the phase
    """
    fitfunc_str = "a + b*x + A*cos(2pi*f*x + phi)"

    f = fit.Parameter(g_f, 'frequency')
    A = fit.Parameter(g_A, 'amplitude')
    a = fit.Parameter(g_a, 'offset')
    b = fit.Parameter(g_b, 'slope')
    phi = fit.Parameter(g_phi, 'phase')
    p0 = [f, A, a, b, phi]
    def fitfunc(x): return a() + b()*x + A()*cos(2*pi*f()*x+phi())
    return p0, fitfunc, fitfunc_str
# end rabi on a slope

### cosine on a slope, see that frequently in rabi oscillations
def fit_rabi_on_linslope(g_f, g_A, g_a, g_b, *arg):
    """
    fits (and plots) a cosine on a slope, with offset,
        y(x) = a + bx + Acos(f*x + phi)

    Initial guesses (1st args, in this order):
        g_f : float
            guess for the frequency
        g_A : float
            guess for amplitude
        g_a : float
            guess for offset
        g_b = 0. : float
            guess for slope
    """
    fitfunc_str = "a + b*x + A*cos(2pi*f*x + phi)"

    f = fit.Parameter(g_f, 'frequency')
    A = fit.Parameter(g_A, 'amplitude')
    a = fit.Parameter(g_a, 'offset')
    b = fit.Parameter(g_b, 'slope')
    p0 = [f, A, a, b]
    def fitfunc(x): return a() + b()*x + A()*cos(2*pi*f()*x)
    return p0, fitfunc, fitfunc_str
# end rabi on a slope

### cosine on a slope, with damping, see that frequently in rabi oscillations
def fit_rabi_damped_exp_on_linslope(g_f, g_A, g_a, g_b, g_phi, g_tau, *arg):
    """
    fits (and plots) a cosine on a slope, with offset,
        y(x) = a + bx + Acos(f*x + phi) * exp(-x/tau)

    Initial guesses (1st args, in this order):
        g_f : float
            guess for the frequency
        g_A : float
            guess for amplitude
        g_a : float
            guess for offset
        g_b : float
            guess for slope
        g_phi : float
            guess for the phase
        g_tau : float
            decay constant
    """
    fitfunc_str = "a + b*x + A*cos(2pi*f*x + phi) * exp(-x/tau)"

    f = fit.Parameter(g_f, 'frequency')
    A = fit.Parameter(g_A, 'amplitude')
    a = fit.Parameter(g_a, 'offset')
    b = fit.Parameter(g_b, 'slope')
    phi = fit.Parameter(g_phi, 'phase')
    tau = fit.Parameter(g_tau, 'phase')
    p0 = [f, A, a, b, phi, tau]
    def fitfunc(x): return a() + b()*x + A()*cos(2*pi*f()*x+phi())*exp(-x/tau())
    return p0, fitfunc, fitfunc_str
# end rabi on a slope

### driving of several transitions
def fit_rabi_multiple_detunings(g_A, g_a, g_F, *arg):
    """
    fitfunction for an oscillation that drives several transitions
    (several nuclear lines, for instance)

        y(x) = a + A * sum_I[ F**2/(F**2 + delta_i**2) * 
            (cos(sqrt(F**2 + delta_i**2 + phi_i)) - 1)

    Initial guesses:
        g_A : full Rabi amplitude
        g_a : offset
        g_F : Rabi frequency


    For the driven levels:
        all successive args are treated as detunings for additional 
            levels, (delta_i, g_phi_i) -- given as tuples!
            detuning is not a free param, but is given exactly.

    """

    fitfunc_str = "a + A * sum_I[ F**2/(F**2 + delta_i**2) * (cos(sqrt(F**2 + delta_i**2 + phi_i)) - 1)"
    
    no_detunings = len(arg)

    A = fit.Parameter(g_A, 'A')
    a = fit.Parameter(g_a, 'a')
    F = fit.Parameter(g_F, 'F')
    p0 = [A, a, F]

    detunings =  []
    phases = []
    for i,d in enumerate(arg):
        fitfunc_str += '\ndetuning d%d := %f' % (i,d[0])
        detunings.append(d[0])
        phases.append(fit.Parameter(d[1], 'phi%d'%i))
        p0.append(phases[i])

    def fitfunc(x):
        val = a()
        for i,d in enumerate(detunings):
            f2 = F()**2 + d**2
            val += A() * (F()**2/f2) * (cos(2*pi*sqrt(f2)*x + phases[i]()) - 1)

        return val

    return p0, fitfunc, fitfunc_str




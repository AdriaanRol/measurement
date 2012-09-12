import numpy as np
from numpy import *
from scipy import optimize
import logging




# taken from the scipy fitting cookbook:
class Parameter:
    def __init__(self, value, name=''):
        self.value = value
        self.name = name

    def set(self, value):
        self.value = value

    def __call__(self):
        return self.value

###############################################################################
# tools, for formatting, printing, etc.
###############################################################################

def fit1d(x, y, fitmethod, *arg, **kw):
    
    # process known kws
    do_plot = kw.pop('do_plot', False)
    do_save_plot = kw.pop('do_save_plot', False)
    do_close_plot = kw.pop('do_close_plot', False)
    save_plot_path = kw.pop('save_plot_path', 'fit.pdf')
    save_plot_format = kw.pop('save_plot_format', 'pdf')
    newfig = kw.pop('newfig', True)
    plot_fitonly = kw.pop('plot_fitonly', False)
    plot_fitresult = kw.pop('plot_fitresult', True)

    fit_curve_points = kw.pop('fit_curve_points', 501)
    
    ylog = kw.pop('ylog', False)
    comment = kw.pop('comment', '')

    do_print = kw.pop('do_print', False)
    ret = kw.pop('ret', False)

    fixed = kw.pop('fixed', [])

    # use the standardized fitmethod: any arg is treated as initial guess
    if fitmethod != None:
        p0, fitfunc, fitfunc_str = fitmethod(*arg)
    else:
        p0 = kw.pop('p0')
        fitfunc = kw.pop('fitfunc')
        fitfunc_str = kw.pop('fitfunc_str', '')        
    
    # general ability to fix parameters
    fixedp = []
    for i,p in enumerate(p0):
        if i in fixed:
            fixedp.append(p)
    for p in fixedp:
        p0.remove(p)
   
    # convenient fitting method with parameters; see scipy cookbook for details
    def f(params):
        i = 0
        for p in p0:
            p.set(params[i])
            i += 1
        return y - fitfunc(x)

    if x is None: x = arange(y.shape[0])
    p = [param() for param in p0]
    
    # do the fit and process
    p1, cov, info, mesg, success = optimize.leastsq(f, p, full_output=True)
    if not success or cov == None: # FIXME: find a better solution!!!
        return False

    # package the result neatly
    result = result_dict(p1, cov, info, mesg, success, y, p0, fitfunc(x))

    if do_print:
        print_fit_result(result)

    if do_plot:
        from matplotlib import pyplot
        # own tools
        import tools.plot as plot
        logging.warning('matplotlib imported')
        if newfig:
            p = plot.Figure()
            ax = pyplot.subplot(111)
            if ylog:
                ax.set_yscale('log')
        else:
            pass # pyplot.figure(figno)

        if not plot_fitonly:
            pyplot.plot(x, y, 'o', mfc='None', mec='r', label='data')
        
        fitx = linspace(x.min(), x.max(), fit_curve_points)
        pyplot.plot(fitx, fitfunc(fitx), 'b-', label='fit')

        # include the fit params in the plot, user can specify the figure coords 
        if plot_fitresult:
            params_xy = kw.pop('plot_fitparams_xy', (0.5, 0.15))
            
            params_str = comment + '\n' + fitfunc_str + '\n' + str_fit_params(result)
            pyplot.figtext(params_xy[0], params_xy[1], params_str, size='x-small')

        # save, if requested, but only for own created plots
        if newfig:
            if do_save_plot:
                p().savefig(save_plot_path+'_'+fitmethod.__name__+'.'+save_plot_format, 
                        format=save_plot_format)

            if do_close_plot:
                p().clf()
                pyplot.close('all')

    if ret:
        if do_plot: 
            return result, p
        else:
            return result

# helper function: plot from datafile directly
def fit1d_dat(filepath, *arg, **kw):

    # known kws
    xcol = kw.pop('xcol', 0)
    ycol = kw.pop('ycol', 1)
    kw['do_save_plot'] = kw.pop('do_save_plot', True)
    kw['save_plot_path'] = kw.pop('save_plot_path', filepath[:-4])
    ignore_start = kw.pop('ignore_start', 0)

    # print kw

    d = loadtxt(filepath)
    x = d[ignore_start:,xcol]
    y = d[ignore_start:,ycol]

    return fit1d(x, y, comment=filepath, *arg, **kw)

    


###############################################################################
# tools, for formatting, printing, etc.
###############################################################################

# put all the fit results into a dictionary, calculate some more practical 
# numbers
def result_dict(p1, cov, info, mesg, success, y, p0, fitdata):
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
        'fitdata' : fitdata,
        'cov' : cov,
        'p0' : p0,
        }
    
    return result

# convenient for pylab usage (or other interactive)
def do_fit_func(fitfunc, p0, y, x):
    result = _fit_return(fit(fitfunc, p0, y, x), y, p0, fitfunc(x))
    print_fit_result(result)
    return result

# make a string that contains the fit params in a neat format
def str_fit_params(result):
    
    # uncertainties are calculated as per gnuplot, "fixing" the result
    # for non unit values of the reduced chisq.
    # values at min match gnuplot
    
    str = "fitted parameters at minimum, with 68% C.I.:\n"
    for i,pmin in enumerate(result['params']):
        str += "%2i %-10s %12f +/- %10f\n" % \
            (i, result['p0'][i].name, pmin, result['error'][i])
    return str

def str_correlation_matrix(result):
    str = "correlation matrix\:\n"
    str += "               "
    for i in range(len(result['p0'])): 
        str+= "%-10s" % (result['p0'][i].name,)
    str += "\n"
    
    for i in range(len(result['params'])):
        str += "%10s" % result['p0'][i].name
        for j in range(i+1):
            str+= "%10f" % \
                (result['cov'][i,j] / \
                     sqrt(result['cov'][i,i] * result['cov'][j,j]),)
        str+='\n'

    return str
    
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

    print str_fit_params(result)
    print str_correlation_matrix(result) 
    


###############################################################################
# common fit functions
###############################################################################

# tbd

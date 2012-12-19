# a small module to help save and plot data consistently via numpy
# author: wolfgang

import os, sys, time
import numpy
from numpy import *
from matplotlib import pyplot, colors, cm

# some defaults that one day might change...
DEFAULT_CMAP = cm.hot

def dummy_qtlab_measurement(name, meta=''):
    """
    Expects a name (we just use the qtlab naming routines) and optionally
    a meta string. 
    Creates a 'dummy' qtlab measurement, where the data file only contains
    the meta string. returns the base path (qtlab file names w/o extension),
    can be used to save other stuff in the same place.
    """
    # we only create a dummy file that we only use to let qtlab generate
    # some settings for us
    from qt import Data
    d = Data(name=name)
    d.add_comment(meta)
    d.create_file()
    d.close_file()    
    path, ext = os.path.splitext(d.get_filepath())
    return path

def folder(path):
    if os.path.isdir(path):
        return path
    else:
        return os.path.split(path)[0]


def title_from_path(filepath):
    
    # auto generate a plot title. use format 'date/time_name' from the
    # qtlab save path
    title = ''
    d,f = os.path.split(filepath)
    d,f = os.path.split(d)
    title += f
    d,f = os.path.split(d)
    title = f + '/' + title

    return title

def xymatrix_from_dat(filepath, xcol=0, ycol=1):
    d = loadtxt(filepath)
    rows, cols = d.shape
    
    xlen = 1
    while d[xlen,xcol] != d[0,xcol]:
        xlen+=1
    ylen = d.shape[0]/xlen
    newshape = (ylen, xlen, cols-2)

    xvals = d[:xlen,xcol]
    yvals = d[::xlen,ycol]
    data = delete(d, array([xcol, ycol]), 1).reshape(newshape)

    return xvals, yvals, data

### Data plotting with help of matplotlib
def save_npz_data(name, **kw):
    """
    Simple routine that does the full saving process in a standardized way.
    Expects:
    * a name : will be used for the qtlab file name generation.
               the value of qt.setup_globals['keyword'] will be appended
               to that.
    * unknown kws are regarded as data

    Returns:
        the folder in which everything has been saved

    Known KWs:
        filepath ('') : filepath (folder)
            highest priority for saving location
            expects the folder into which to save

        qtlab_data (None) : qt.Data object
            if this already exists, we can use it to determine the path where to save
            if neither this nor filepath has been given, we generate a new path

        do_plot (True) : bool
            whether to generate a plot from the data, using the autoplot functions

        meta ('') : string
            meta information on the data set. will be save in name_meta.txt

        txt ({}): dict
            in the form {'file' : <some string>}, will result in files
            name_file.txt, containing the respective string.
    """
    
    do_plot = kw.pop('do_plot', True)
    meta = kw.pop('meta', '')
    txt = kw.pop('txt', {})
    
    # check where to get the folder from
    filepath = kw.pop('filepath', '')
    qtlab_data = kw.pop('qtlab_data', None)
    
    if filepath != '':
        path = os.path.join(filepath, name)
    
    elif qtlab_data == None:
        path = dummy_qtlab_measurement(name, meta)
    
    else:
        path, ext = os.path.splitext(qtlab_data.get_filepath())
    
    
    # save txt comments
    if meta != '':
        txt_meta = open(path + '_meta.txt', 'w')
        txt_meta.write(meta)
        txt_meta.close()
    for txtfile in txt:
        t = open(path + '_%s.txt' % txtfile, 'w')
        t.write(txt[txtfile])
        t.close()

    numpy.savez(path, **kw)
    
    if do_plot:
        # debug - look how long plotting takes
        # t0 = time.time()
        save_npz_auto_data_plot(path + '.npz')
        # t1 = time.time()
        # print 'plotting time: %.3fs' % (t1-t0)

    return folder(path)

def save_npz_auto_data_plot(filepath, **kw):
    fig = plot_npz_auto_data(filepath, **kw)
    
    if fig:
        basepath, ext = os.path.splitext(filepath)
        figpath = basepath + '.pdf'
    
        # dont overwrite existing figures but find suitable alt name,
        # by appending an (increasing) number
        i = 0
        while os.path.exists(figpath):
            b, e = os.path.splitext(figpath)
            if b == basepath:
                figpath = b + '-0' + e
            else:
                while b[-1] != '-':
                    b = b[:-1]
                figpath = b + str(i) + e
            i += 1
        
        fig.savefig(figpath, format='pdf')
        fig.clf()
        pyplot.close(fig)

def plot_npz_auto_data(filepath, **kw):
    try:
        data = numpy.load(filepath)
    except:
        print 'Invalid data file: %s' % filepath
        return

    title = kw.pop('title', title_from_path(filepath)[:-4])
    # legacy
    name = title

    arrays = data.items()
    keys = data.keys()
    title = title_from_path(filepath)
   
    # try to figure out what kind of data we're dealing with here
    # kind of data should be deducable from the array names
    fig = None
    x = []
    y = []
    z = []
    for k in keys:
        k_split = k.split('__')
        if k_split[0] == 'x':
            x.append(k)
        elif k_split[0] == 'y':
            y.append(k)
        elif k_split[0] == 'z':
            z.append(k)

    # color plot: one x, one y dim, and at least one z dim which matches
    # the dimensions
    ### FIXME: adapt such that each data set gets saved into a different file
    if len(x) == len(y) == 1 and len(z) >= 1:
        for d in z:
            if data[d].shape == (data[y[0]].size, data[x[0]].size):
                fig = npz_auto_colorplot(title, data, x[0], y[0], d, **kw)
            elif data[d].shape == (data[x[0]].size, data[y[0]].size):
                fig = npz_auto_colorplot(title, data, y[0], x[0], d, **kw)

    # line plot: one x dim, arbitrary amount of y dims
    elif len(x) == 1 and len(y) >= 1:
        lines = []
        for d in y:
            if data[d].size == data[x[0]].size:
                lines.append(d)
            if len(lines) > 0:
                fig = npz_auto_lineplot(title, data, x[0], lines)

    return fig
    
def npz_auto_lineplot(name, data, xname, ynames):
    try:
        fig = pyplot.figure()
        for yname in ynames:
            pyplot.plot(data[xname], data[yname], label=yname[3:])

        pyplot.legend()
        pyplot.title(name)
    except:
        print 'Cannot plot figure %s' % name
        return False

    labels = []
    for axis_name in xname, ynames[0]:
        n = axis_name.split('__')
        if len(n) == 1:
            labels.append(n[0])
        elif len(n) == 2:
            labels.append(n[1])
        elif len(n) == 3:
            labels.append(n[1] + ' [' + n[2] + ']')
    pyplot.xlabel(labels[0])
    pyplot.ylabel(labels[1])

    xlim = (min(data[xname]), max(data[xname]))
    pyplot.xlim(xlim)

    return fig

def npz_auto_colorplot(name, data, xname, yname, zname, **kw):
    """
    docstring
    """
    extent = kw.pop('extent', 
        (data[xname][0], data[xname][-1], data[yname][0], data[yname][-1]))
    cmap = kw.pop('cmap', DEFAULT_CMAP)
    origin = kw.pop('origin', 'lower')

    try:
        fig = pyplot.figure()        
        pyplot.imshow(data[zname], 
        	interpolation='nearest',
        	origin=origin,
        	extent=extent, 
           	cmap=cmap, 
            	**kw)
        
        cb = pyplot.colorbar()
        pyplot.title(name)
    except:
        print 'Cannot plot figure %s' % name
        raise
        return False

    labels = []
    for axis_name in xname, yname, zname:
        n = axis_name.split('__')
        if len(n) == 1:
            labels.append(n[0])
        elif len(n) == 2:
            labels.append(n[1])
        elif len(n) == 3:
            labels.append(n[1] + ' [' + n[2] + ']')
    pyplot.xlabel(labels[0])
    pyplot.ylabel(labels[1])
    cb.set_label(labels[2])

    return fig


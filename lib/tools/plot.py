import os, sys, time
import matplotlib
from matplotlib import pyplot


class Figure:
    def __init__(self, **kw):
        
        self.name = kw.pop('name', 'plot')
        self.index = kw.pop('index', None)
        self.show = kw.pop('show', True)
        self.footnote = kw.pop('footnote', '')

        # FIXME: revise!!!
        if self.show:
            pass
            # pyplot.ion()
        else:
            pass
            # pyplot.ioff()
            
        # make sure we don't plot into already existing stuff
        try:
            fig = pyplot.figure(self.index)
            fig.clf()
            pyplot.close(fig)
        except:
            pass
        
        if self.index != None:
            self.fig = pyplot.figure(self.index, **kw)
        else:
            self.fig = pyplot.figure(**kw)

    def __call__(self):
        return self.fig

    def save(self, folder, prefix = ''):        
        if prefix == '':
            prefix = '%s_' % time.strftime('%H%M%S')
            
        folder = os.path.join(folder, time.strftime('%Y%m%d')) 
        filepath = os.path.join(folder, prefix + self.name + '.png')
        self.fig.suptitle(filepath[:-4])

        if self.footnote != '':
            pyplot.figtext(1., 0., self.footnote, horizontalalignment='right',
                verticalalignment='bottom', fontsize='x-small')


        try:
            os.makedirs(folder)
        except OSError:
            pass # dir exists


        # dont overwrite existing figures but find suitable alt name,
        # by appending an (increasing) number
        basepath, ext = os.path.splitext(filepath)
        i = 0
        while os.path.exists(filepath):
            b, e = os.path.splitext(filepath)
            if b == basepath:
                filepath = b + '-0' + e
            else:
                while b[-1] != '-':
                    b = b[:-1]
                filepath = b + str(i) + e
            i += 1
        
        self.fig.savefig(filepath)

        if not self.show:
            self.fig.clf()
            pyplot.close(self.fig)
            
        return



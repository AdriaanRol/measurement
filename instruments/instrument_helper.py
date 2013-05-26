def create_get_set(ins,par_list):
    for par,kw in par_list.items():
        setattr(ins,'_'+par,kw.pop('val',None))
        f_get=make_f_get(ins,par)
        f_set=make_f_set(ins,par)
        fgetname='do_get_' + par
        fsetname='do_set_' + par
        f_get.__name__= fgetname  
        f_set.__name__= fsetname   
        setattr(ins,fgetname,f_get)
        setattr(ins,fsetname,f_set)
        ins.add_parameter(par,**kw)

def make_f_get(ins,par):
    def f():
        return getattr(ins,'_'+par)
    return f

def make_f_set(ins,par):
    def f(val):
        setattr(ins,'_'+par,val)
    return f
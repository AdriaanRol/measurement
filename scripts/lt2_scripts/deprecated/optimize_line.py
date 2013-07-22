def optimize(dimension,length):
    if dimension == 'x':
	dim='stage_x'
    if dimension == 'y':
	dim='stage_y'
    if dimension == 'z':
        dim='front_z'
    opt1d_counts.set_dimension(dim)
    opt1d_counts.set_scan_length(length)
    opt1d_counts.set_is_running(True)
    while opt1d_counts.set_is_running():
	    time.sleep(0.05) 
    f = opt1d_counts.get_data('fit')
    x = opt1d_counts.get_data('points')
    data = opt1d_counts.get_data('countrates')
    import pylab as pl
    dataplot=pl.plot(x,data,'r')
    fitplot=pl.plot(x,f,'o')
    if dimension == 'x':
	master_of_space.set_stage_x(opt1d_counts.get_opt_pos())
    if dimension == 'y':
	master_of_space.set_stage_y(opt1d_counts.get_opt_pos())
    if dimension == 'z':
       master_of_space.set_front_z(opt1d_counts.get_opt_pos())
    
    pl.show()
    print data
    print f

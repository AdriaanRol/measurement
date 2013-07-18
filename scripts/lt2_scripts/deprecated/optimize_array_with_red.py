ins_mos_lt2 = qt.instruments['master_of_space']
ins_mos_lt1 = qt.instruments['master_of_space_lt1']

def turn_off_red_lasers():
    #LT2
    NewfocusAOM.set_power(0)
    MatisseAOM.set_power(0)
    AWG.set_ch4_marker1_low(0)
    
    #LT1
    NewfocusAOM_lt1.set_power(0)
    MatisseAOM_lt1.set_power(0)
    
def optimize_with_red(do_LT1 = False, do_LT2 = True, scan_range = 0.8, n_points = 11, opt_green_power = 200e-6, opt_red_power = 10e-9):
    turn_off_red_lasers()
    GreenAOM.set_power(opt_green_power)
    GreenAOM_lt1.set_power(opt_green_power)

    curr_x_lt2 = ins_mos_lt2.get('x')
    curr_y_lt2 = ins_mos_lt2.get('y')

    curr_x_lt1 = ins_mos_lt1.get('x')
    curr_y_lt1 = ins_mos_lt1.get('y')

    if do_LT2:
        print 'Start scanning...' 
        scan2d_stage.set_counter(2)
        scan2d_stage.set_xstart(curr_x_lt2 - scan_range/2.)
        scan2d_stage.set_xstop(curr_x_lt2 + scan_range/2.)
        scan2d_stage.set_xsteps(n_points)
        scan2d_stage.set_ystart(curr_y_lt2 - scan_range/2.)
        scan2d_stage.set_ystop(curr_y_lt2 + scan_range/2.)
        scan2d_stage.set_ysteps(n_points)
        scan2d_stage.set_pixel_time(15.0)
        scan2d_stage.set_is_running(True)

        qt.msleep(15)
        x_coordinates = scan2d_stage.get_x()
        y_coordinates = scan2d_stage.get_y()
        countrates_without = scan2d_stage.get_data('countrates')
        qt.msleep(0.5)
        
        print 'Turning red on and scanning...'
        #awg.set_ch4_marker1_low(0.2)
        NewfocusAOM.set_power(opt_red_power)
        scan2d_stage.set_is_running(True)
        
        qt.msleep(15)
        countrates_with = scan2d_stage.get_data('countrates')
        S2BG = countrates_without/countrates_with
        select_best = S2BG == S2BG.max()

        for j in arange(0,n_points):
            for k in arange(0,n_points):
                if select_best[j,k]:
                    x_best = x_coordinates[k]
                    y_best = y_coordinates[j]

        print x_best
        print y_best

        ins_mos_lt2.set('x',x_best)
        qt.msleep(0.5)
        ins_mos_lt2.set('y',y_best)

        delta_x = curr_x_lt2 - x_best
        delta_y = curr_y_lt2 - y_best

        print 'LT2 optimized, x position moved by {0:1f} um'.format(delta_x)
        print 'y position changed {0:1f} um'.format(delta_y)

        turn_off_red_lasers()
        GreenAOM.set_power(opt_green_power)

    return x_best, y_best

    if do_LT1:
        scan2d_lt1.set_xstart(curr_x_lt1 - scan_range/2.)
        scan2d_lt1.set_xstop(curr_x_lt1 + scan_range/2.)
        scan2d_lt1.set_xsteps(n_points)
        scan2d_lt1.set_ystart(curr_y_lt1 - scan_range/2.)
        scan2d_lt1.set_ystop(curr_y_lt1 + scan_range/2.)
        scan2d_lt1.set_ysteps(n_points)
        scan2d_lt1._start_running()

optimize_with_red(scan_range = 1.0, n_points = 21)
GreenAOM.set_power(200e-6)
AWG.set_ch4_marker1_low(0)



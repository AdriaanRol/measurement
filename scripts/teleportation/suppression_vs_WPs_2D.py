import qt

ROTATOR = qt.instruments['positioner']
HWPCHAN = 2
QWPCHAN = 1
ADWIN = qt.instruments['adwin']
CTRCHAN = 1
INTTIME = 50
AOM = qt.instruments['MatisseAOM']
PWR = 10e-9

HWPSTEPSPERDEG = 505.
QWPSTEPSPERDEG = 463.
HWPSTARTDEG = 323
QWPSTARTDEG = 286

HWPSTEPSIZE = int(HWPSTEPSPERDEG * 10)
QWPSTEPSIZE = int(QWPSTEPSPERDEG * 10)
HWPSTEPS = 36
QWPSTEPS = 36

### msmt
data = qt.Data(name='Suppression2D_after_opt_green_ZPL')
data.add_coordinate('QWP angle')
data.add_coordinate('HWP angle')
data.add_value('countrate (Hz)')
data.create_file()

p2d = qt.Plot2D(data, 'bO',
    name = 'Suppression counts',
    clear = True,
    coorddim = 1,
    valdim = 2,
    maxtraces = 1)

p3d = qt.Plot3D(data,
    name = 'Suppression counts 3D',
    clear = True,
    coorddims = (0,1),
    valdim = 2)

qt.mstart()

for i in arange(QWPSTEPS):   
    qwp = (i+1) * QWPSTEPSIZE / QWPSTEPSPERDEG + QWPSTARTDEG
    print 'QWP setting {} deg ({}/{})'.format(qwp, i+1, QWPSTEPS)
    ROTATOR.quick_scan(QWPSTEPSIZE, QWPCHAN)

    for j in arange(HWPSTEPS):   
        hwp = (j+1) * HWPSTEPSIZE / HWPSTEPSPERDEG + HWPSTARTDEG
        # print 'HWP setting {} deg ({}/{})'.format(hwp, j+1, HWPSTEPS)
        ROTATOR.quick_scan(HWPSTEPSIZE, HWPCHAN)

        qt.msleep(0.01)
        AOM.set_power(PWR)
        cts = ADWIN.measure_counts(INTTIME)[CTRCHAN]
        AOM.set_power(0)
        data.add_data_point(qwp, hwp, cts/(INTTIME * 0.001))

    ROTATOR.quick_scan(-HWPSTEPSIZE*HWPSTEPS, HWPCHAN)
    data.new_block()
    p3d.update()

ROTATOR.quick_scan(-QWPSTEPSIZE*QWPSTEPS, QWPCHAN)
data.close_file()
qt.mend()

p3d.save_png()






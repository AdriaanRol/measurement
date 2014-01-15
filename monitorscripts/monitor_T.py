import qt
import time
import msvcrt

mm = qt.instruments['keithleyMM']
temp_calib = None

def init():
    global temp_calib

    try:
        temp_calib = np.loadtxt(os.path.join(qt.config['execdir'], 
            '..', 'measurement', 'calib', 'DT-670.txt'))
    except:
        print "could not get T-calibration data."
        temp_calib = None
        return


def get_temperature():
    global temp_calib

    v = mm.get_readlastval()
    idx = np.argmin(abs(v-temp_calib[:,1]))
    dv = v - temp_calib[idx,1]
    t = temp_calib[idx,0] + dv/(temp_calib[idx,2]*1e-3)

    return v,t


init()
if temp_calib != None:
    t0 = time.time()
    data = qt.Data(name='monitor_warmup')
    data.add_coordinate('time')
    data.add_coordinate('voltage')
    data.add_coordinate('temperature')
    data.create_file()

    plt = qt.Plot2D(data, 'ro', name='Temperature', coorddim=0,
            valdim=1, clear=True)
    plt.add(data, 'bo', coorddim=0, valdim=2, right=True)
    plt.set_xlabel('time (h)')
    plt.set_ylabel('T-sensor voltage (V)')
    plt.set_y2label('T (K)')


    while 1:
        if msvcrt.kbhit():
            kb_char=msvcrt.getch()
            if kb_char == "q":
                break

        v,t = get_temperature()
        data.add_data_point((time.time()-t0)/3600., v, t)

        qt.msleep(10)


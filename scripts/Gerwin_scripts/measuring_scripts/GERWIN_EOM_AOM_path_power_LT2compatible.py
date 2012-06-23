import time
import qt
from analysis import fit


#this scripts serves as to measure the output of the EOM-AOM matisse path 
#by quickly sweeping the EOM voltage and putting the AOM voltage on high!

##########################
###### PARAMETERS ########
##########################

AOM_AWGchannel = 'ch4m1' #Matisse short pulses AOM
EOM_AWGchannel = 'ch4' #analog EOM channel on AWG
fit_calibration_curve = 0 #flag for fitting procedure

n_steps = 30
step_time = 0.2
EOM_min_voltage = -1.5
EOM_max_voltage = 1.5
attenuator_on = 0

V_AOM = 1.0

###########################
###########################
###########################

powermeter.set_wavelength(637e-9)
AWG.set_ch4_marker1_low(0) #set Matisse AOM OFF
NewfocusAOM.set_power(0)
MatisseAOM.set_power(0)

print 'Measuring Background'

BG = zeros([5,1])

for k in arange(5):
    BG[k,0] = powermeter.get_power()
    qt.msleep(1)

BG_err = std(BG)
BG = mean(BG)

def num2str(num, precision): 
    return "%0.*f" % (precision, num) 

print 'Background = '+num2str(BG*1e9,1)+' pm '+num2str(BG_err*1e9,1)+' nW'

AWG.set_ch4_marker1_low(V_AOM) #set Matisse AOM ON

data = qt.Data(name = 'calibrate_EOM_Matisse')
data.add_coordinate('Applied voltage (V)')
data.add_value('Measured power (background subtracted) (W)')
data.create_file()

plt = qt.Plot2D(data, 'ob', name='EOM Calibration curve', coorddim=0, valdim=1, clear=True)
file_directory = data.get_filepath()

V_step_size = (EOM_max_voltage-EOM_min_voltage)/n_steps

measured_power = zeros([n_steps,1])
V_EOM = zeros([n_steps,1])

#set EOM:browse confirm saveas
#set channel to desired voltage and wait to stabilize
for i in range(0,n_steps,2):
    V_EOM[i,0]=EOM_min_voltage+i*V_step_size/2.

    if attenuator_on:
        V_EOM[i,0] = V_EOM[i,0]*sqrt(2)

    AWG.set_ch4_offset(V_EOM[i,0])
    measured_power[i,0] = powermeter.get_power() 
    qt.msleep(step_time)
    data.add_data_point(V_EOM[i,0], measured_power[i,0]-BG)

    V_EOM[i+1,0] = -V_EOM[i,0]

    if attenuator_on:
        V_EOM[i+1,0] = V_EOM[i+1,0]*sqrt(2)
    AWG.set_ch4_offset(V_EOM[i+1,0])
    measured_power[i+1,0] = powermeter.get_power() 
    qt.msleep(step_time)
    data.add_data_point(V_EOM[i+1,0], measured_power[i+1,0]-BG)  

#measurement at zero EOM voltage
#AWG.set_ch4_offset(0)
#V_EOM[n_steps+1,0] = 0
#measured_power[n_steps+1,0] = powermeter.get_power() 
#data.add_data_point(V_EOM[n_steps+1,0],measured_power[n_steps+1,0])

AWG.set_ch4_offset(0) #set EOM channel to back to 0 to avoid drift
AWG.set_ch4_marker1_low(0)#set AOM voltage back to zero again
data.close_file()


# the fitting procedure applies only if fit_calibration_curve is flagged above!

if fit_calibration_curve:
	def num2str(num, precision): 
		return "%0.*f" % (precision, num) 
	A = fit.Parameter(max(measured_power-BG)/2)
	B = fit.Parameter(max(measured_power-BG)/2)
	f = fit.Parameter(1/2.5)
	phi = fit.Parameter(0)
	def fit_cos(x):
		return A() + B()*cos(2*pi*f()*x+phi())
	ret = fit.fit1d(V_EOM.reshape(-1),measured_power.reshape(-1)-BG, None, fitfunc = fit_cos, p0=[A,B,f,phi], do_plot=True, do_print=True, ret=True)
	p = qt.plots['EOM Calibration curve']
	V = linspace(EOM_min_voltage,EOM_max_voltage,V_step_size/10)
	qt. plot(V,fit_cos(V), 'r-', name='EOM Calibration curve')

plt.save_png(file_directory[0:65]+'calibration_EOM_curve.png')

print 'Extinction = max/min = '+num2str(max(measured_power-BG)/min(measured_power-BG),0)

print 'Done'


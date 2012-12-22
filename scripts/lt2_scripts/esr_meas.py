from measurement import esr

reload(esr)

name = 'SIL2_LT1'

m = esr.ESRMeasurement(name)
m.setup(lt1 = True)

#m.start_f=2.65
#m.stop_f=2.75
#m.steps=51

m.measure(name)

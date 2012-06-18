import visa

levelmeter = visa.instrument('GPIB::8::INSTR')

print('current cryovac levelmeter reading:')
levelmeter.write('chan 2')
lhe1lvl = levelmeter.ask('meas?')
lhe1lvl_flt = float((lhe1lvl.split(' '))[0])
print('  LHe1 (upper tank): %s'%lhe1lvl)

levelmeter.write('chan 1')
lhe2lvl = (levelmeter.ask('meas?'))
lhe2lvl_flt = float((lhe2lvl.split(' '))[0])
print('  LHe2 (lower tank): %s'%lhe2lvl)

keithley =  visa.instrument('GPIB::11::INSTR')
print('current keithly measurement: %s'%(keithley.ask(':func?')))
keith_data= (keithley.ask(':data?'))
keith_data_flt = float(keith_data)
print('current keithly reading: %s'%keith_data)

#print 'l1', lhe1lvl_flt, 'l2', lhe2lvl_flt, 'v', keith_data_flt

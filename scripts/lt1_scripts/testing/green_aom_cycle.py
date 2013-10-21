iter = False
for i in range(10000):
	GreenAOM.set_power(100e-6*iter)
	iter=not(iter)
	qt.msleep(0.01)
from analysis import common, fit, rabi


data=load('Rabi-0_SpinReadout.npz')

j=0
time=[]
counts=[]

for i in data['MW burst time']:
    time.append(i)
    print j
    counts.append(sum(data['counts'][j]))
    j=j+1


amp = (max(counts)-min(counts))/2.
offset = (max(counts)+min(counts))/2.
freq = 0.001
decay = 500.

plt.plot(time,counts,'o')
fit_result = fit.fit1d(np.array(time),np.array(counts),rabi.fit_rabi_damped_exp,freq,amp, offset,decay,do_plot=True,ret=True)
plt.show()
plt.savefig('rabi_fitted.png')

    

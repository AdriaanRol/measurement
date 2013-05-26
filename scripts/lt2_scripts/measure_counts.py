import msvcrt
cts=zeros(int(1e6))
j=0
for i,v in enumerate(cts):
    if (msvcrt.kbhit() and (msvcrt.getch() == 'q')): break
    cts[i]=adwin.get_countrates()[0]
    qt.msleep(0.2)
    j=i

savez(r'D:\measuring\data\20130516\cts.npz',cts[:j])
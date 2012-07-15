@ECHO OFF
ECHO %1
pause
ipython --i --c "d=load(r'%1'); d.keys()" --pylab
pause

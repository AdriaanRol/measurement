@ECHO OFF
ECHO %1

ipython --i --c "d=load(r'%1'); d.keys()" --pylab
pause

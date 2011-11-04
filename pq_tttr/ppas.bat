@echo off
SET THEFILE=pq_tttr.dll
echo Linking %THEFILE%
c:\lazarus\fpc\2.2.4\bin\i386-win32\ld.exe -b pe-i386 -m i386pe  --gc-sections  -s --dll  --entry _DLLMainCRTStartup   --base-file base.$$$ -o pq_tttr.dll link.res
if errorlevel 1 goto linkend
c:\lazarus\fpc\2.2.4\bin\i386-win32\dlltool.exe -S c:\lazarus\fpc\2.2.4\bin\i386-win32\as.exe -D pq_tttr.dll -e exp.$$$ --base-file base.$$$ 
if errorlevel 1 goto linkend
c:\lazarus\fpc\2.2.4\bin\i386-win32\ld.exe -b pe-i386 -m i386pe  -s --dll  --entry _DLLMainCRTStartup   -o pq_tttr.dll link.res exp.$$$
if errorlevel 1 goto linkend
c:\lazarus\fpc\2.2.4\bin\i386-win32\postw32.exe --subsystem console --input pq_tttr.dll --stack 16777216
if errorlevel 1 goto linkend
goto end
:asmend
echo An error occured while assembling %THEFILE%
goto end
:linkend
echo An error occured while linking %THEFILE%
:end

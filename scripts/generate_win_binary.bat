@echo off
cd ..
del /s /q /f *.pyc
SET TARGET=tapetest
pyinstaller.exe --clean ^
-p ./modules/ ^
--additional-hooks-dir=hooks ^
--exclude-module FixTk ^
--exclude-module tcl ^
--exclude-module _tkinter ^
--exclude-module tkinter ^
--exclude-module Tkinter ^
--exclude-module tk ^
--exclude-module win32com ^
--exclude-module pywin32 ^
--exclude-module pubsub ^
--exclude-module smokesignal ^
--exclude tornado ^
--exclude jedi ^
--exclude numba ^
%TARGET%.py
xcopy /e /Y /i openh264-1.8.0-win32.dll dist\tapetest\
xcopy /e /Y /i openh264-1.8.0-win64.dll dist\tapetest\
xcopy /e /Y /i params.py dist\
xcopy /e /Y /i scripts\tapetest.bat dist\
pause
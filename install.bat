@echo off
cd /d "%~dp0"
where py >nul 2>nul
if %errorlevel%==0 goto usepy
where python >nul 2>nul
if %errorlevel%==0 goto usepython
echo Python 3.11 or newer is needed. Install it from https://www.python.org/downloads/ (tick "Add python.exe to PATH"), then run this again.
goto end
:usepy
py -3 install_chaos.py %*
goto end
:usepython
python install_chaos.py %*
:end
pause

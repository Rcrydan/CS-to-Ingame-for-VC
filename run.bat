@echo off
where py >nul 2>nul && (py -3 "%~dp0run.py" & goto end)
python --version >nul 2>nul && (python "%~dp0run.py" & goto end)
echo Chua cai Python. Tai ban 3.x tai https://www.python.org/downloads/
echo Khi cai nho tick "Add python.exe to PATH" (hoac giu "py launcher").
:end
pause

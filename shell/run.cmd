@ECHO OFF
REM Sinote Launcher

SETLOCAL ENABLEDELAYEDEXPANSION

ECHO ==================================
ECHO      Sinote Launcher 1.0.0
ECHO        Win12Home (C) 2025
ECHO ==================================
ECHO Finding Python...

REM Silent running and get the first line
FOR /f "delims=" %%i IN ('WHERE python 2^>nul') do (
    set "firstLine=%%i"
    goto :getResult
)

:getResult
IF ERRORLEVEL 1 (
    ECHO Error: Cannot find python environment!
    ECHO This script only can find "python" executable, cannot find "python3" executable!
    ECHO Use "python3 main.py" if you've got Python.
    EXIT /b 2
)
CD ..
"!firstLine!" -m pip install -r requirements.txt
"!firstLine!" main.py
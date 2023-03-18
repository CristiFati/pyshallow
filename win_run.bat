@echo off

setlocal enableextensions

if defined PYTHONEXE (
    set PYTHONEXE=%PYTHONEXE:"=%
) else (
    set PYTHONEXE=python
)

"%PYTHONEXE%" "%~dp0mue_idle.py" %*


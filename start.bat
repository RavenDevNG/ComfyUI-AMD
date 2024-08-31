@echo off
set PYTHON=%~dp0/venv/Scripts/python.exe
set GIT=git
set VENV_DIR=./venv
set COMMANDLINE_ARGS=--auto-launch

echo *** Checking and updating to new version if possible 
%GIT% fetch
%GIT% reset --hard origin/master

echo.
echo *** Applying patches...
%PYTHON% patch_zluda.py

echo.
.\zluda\zluda.exe -- %PYTHON% main.py %COMMANDLINE_ARGS%

@echo off
setlocal
powershell -ExecutionPolicy Bypass -File "%~dp0start_platform.ps1" %*

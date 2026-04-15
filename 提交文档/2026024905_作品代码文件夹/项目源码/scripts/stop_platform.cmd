@echo off
setlocal
powershell -ExecutionPolicy Bypass -File "%~dp0stop_platform.ps1" %*

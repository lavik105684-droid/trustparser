@echo off
pushd "%~dp0"
title BOTANY ^& GROW HUB SYNCHRONIZER (2026)

echo ======================================================================
echo       BOTANY ^& GROW HUB SYNCHRONIZER (2026)
echo ======================================================================
echo.
echo [INFO] Starting botany knowledge vault synchronization pipeline...
echo.

C:\Python314\python.exe sync_git_botany.py

echo.
echo ======================================================================
echo [COMPLETE] Synchronization complete! Press any key to exit...
echo ======================================================================
popd
pause > nul

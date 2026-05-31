@echo off
pushd "%~dp0"
title AI CONTENT FACTORY SYNCHRONIZER (2026)

echo ======================================================================
echo           AI CONTENT FACTORY SYNCHRONIZER (2026)
echo ======================================================================
echo.
echo [INFO] Starting AI content factory vault synchronization pipeline...
echo.

C:\Python314\python.exe sync_git_notebooklm.py

echo.
echo ======================================================================
echo [COMPLETE] Synchronization complete! Press any key to exit...
echo ======================================================================
popd
pause > nul

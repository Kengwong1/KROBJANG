@echo off
title Krobjang AI Agent

cd /d "%~dp0"

echo ============================================
echo   Krobjang AI Agent Starting...
echo ============================================

echo.
echo Running auto content generator...
echo.

python auto_content_krobjang.py

echo.
echo ============================================
echo   Agent Finished
echo ============================================

pause
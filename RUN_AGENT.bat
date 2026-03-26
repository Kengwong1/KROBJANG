@echo off
chcp 65001 > nul
setlocal

title KROBJANG AI AGENT v3 AUTO
color 0A

echo.
echo =====================================================
echo   KROBJANG AI AGENT v3.0 - FULL AUTO MODE
echo =====================================================
echo.

REM ไปที่โฟลเดอร์โปรเจกต์
cd /d "D:\Projects\krubjang-site full"

echo Starting FULL AUTO workflow...

REM รันระบบทั้งหมด
python agent_krobjang.py

echo.
echo =========================================
echo AUTO WORKFLOW COMPLETE
echo Logs folder: agent_logs
echo =========================================
echo.

exit
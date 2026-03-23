@echo off
echo Auto Content Generator Starting...
cd /d C:\Users\Administrator
python "D:\Projects\krobjang-site full\auto_content_krobjang.py" >> "D:\Projects\krobjang-site full\auto_content_log.txt" 2>&1
echo Done at %date% %time%

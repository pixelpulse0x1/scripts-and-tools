@echo off
echo 作者舟清颺:V1.0文件资源管理器会在3s后重启
timeout /t 3 /nobreak >nul
taskkill /f /im explorer.exe
start explorer.exe
exit

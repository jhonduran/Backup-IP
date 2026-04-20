@echo off
chcp 65001 >nul
echo =====================================================
echo BACKUP SWITCHES AUTOMÁTICO
echo Fecha: %date%   Hora: %time%
echo =====================================================

cd /d "C:\Users\pract3.sistemas\PyCharmMiscProject\Backup-IP-main"

echo Iniciando backups...
"C:\Users\pract3.sistemas\PyCharmMiscProject\Backup-IP-main\.venv\Scripts\python.exe" main.py >> "backup_log.txt" 2>&1

echo.
echo Backup finalizado a las %time%
echo =====================================================
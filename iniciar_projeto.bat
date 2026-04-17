@echo off
title Iniciar Projeto de Manutencao

echo ==========================================
echo   Iniciando Projeto de Manutencao
echo ==========================================
echo.

REM --- BACKEND FASTAPI ---
start "Backend FastAPI" cmd /k "cd /d C:\Users\pcm\Documents\Diego\Litoral_APP\backend && uvicorn main:app --host 0.0.0.0 --port 8000 --reload"

REM --- APP DO MANTENEDOR ---
start "App do Mantenedor" cmd /k "cd /d C:\Users\pcm\Documents\Diego\Litoral_APP\app_mantenedor && python -m http.server 5500"

REM --- AGUARDA ALGUNS SEGUNDOS ---
timeout /t 4 /nobreak >nul

REM --- ABRIR SISTEMA PRINCIPAL ---
start "" "C:\Users\pcm\Documents\Diego\Litoral_APP\sistema_principal\index.html"

echo.
echo Projeto iniciado.
echo Backend: http://192.168.0.185:8000
echo App do mantenedor: http://192.168.0.185:5500
echo.
pause
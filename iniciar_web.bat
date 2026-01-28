@echo off
chcp 65001 >nul
title Agente Vendedor Web - Luna
echo.
echo ============================================
echo    AGENTE VENDEDOR WEB - Luna
echo    IAgentic Solutions
echo ============================================
echo.
echo Instalando Flask si es necesario...
pip install flask >nul 2>&1
echo.
echo Iniciando servidor web...
echo Abre tu navegador en: http://localhost:5000
echo.
echo Presiona Ctrl+C para detener
echo.
cd /d "%~dp0"
python web_app.py
pause

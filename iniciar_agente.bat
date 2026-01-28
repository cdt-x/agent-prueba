@echo off
chcp 65001 >nul
title Agente Vendedor de IA - Luna
echo.
echo ============================================
echo    AGENTE VENDEDOR DE IA - Luna
echo    IAgentic Solutions
echo ============================================
echo.
echo Iniciando agente...
echo.
cd /d "%~dp0"
python simple_chat.py
pause

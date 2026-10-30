@echo off
title Garritas Store - Servidor
cd /d "%~dp0"
powershell -NoExit -ExecutionPolicy Bypass -Command "Write-Host 'Iniciando Garritas Store...' -ForegroundColor Cyan; .\uso-rapido\garritas.ps1 -Accion iniciar; Write-Host 'Para detener los servicios ejecuta: .\uso-rapido\garritas.ps1 -Accion detener' -ForegroundColor Yellow"


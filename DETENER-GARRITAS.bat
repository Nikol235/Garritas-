@echo off
title Garritas Store - Detener
cd /d "%~dp0"
powershell -ExecutionPolicy Bypass -Command "Write-Host 'Deteniendo Garritas Store...' -ForegroundColor Cyan; .\uso-rapido\garritas.ps1 -Accion detener; pause"


@echo off
title Garritas Store - Estado
cd /d "%~dp0.."
powershell -ExecutionPolicy Bypass -Command "Write-Host 'Consultando estado de Garritas Store...' -ForegroundColor Cyan; .\uso-rapido\garritas.ps1 -Accion estado; pause"

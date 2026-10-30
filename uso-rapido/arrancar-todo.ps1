Set-Location 'd:\UNIDAD 2 Distribuidas\Garritas-'
$env:NG_CLI_ANALYTICS = 'false'
Set-ExecutionPolicy -Scope Process -ExecutionPolicy RemoteSigned -Force
$ErrorActionPreference = 'Continue'
.\uso-rapido\garritas.ps1 -Accion iniciar

$ErrorActionPreference = 'Stop'
$env:NG_CLI_ANALYTICS = 'false'
Push-Location (Split-Path -Parent $PSScriptRoot)
try {
    & (Join-Path $PSScriptRoot 'garritas.ps1') -Accion iniciar
} finally {
    Pop-Location
}

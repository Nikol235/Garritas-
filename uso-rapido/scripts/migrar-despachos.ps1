param([string]$Origen='garritas-postgres-envio-dev',[string]$Destino='garritas-postgres-venta-dev')
$ErrorActionPreference='Stop'
$query="SELECT encode(convert_to(COALESCE(json_agg(row_to_json(e)),'[]'::json)::text,'UTF8'),'base64') FROM envios e"
$result=& docker exec $Origen psql -U garritas -d garritas_envio_db -Atc $query
if($LASTEXITCODE -ne 0){throw 'No se pudo leer el archivo histórico de Envío. No se borró ningún dato.'}
$payload=[System.Text.Encoding]::UTF8.GetString([Convert]::FromBase64String(($result -join "")))
if($payload -eq '[]'){Write-Host 'Despachos: no hay registros históricos para migrar.';return}
# Escape literal quotes. The JSON originates from PostgreSQL, never interpolated as SQL syntax.
$sql=(Get-Content (Join-Path $PSScriptRoot 'migrar-despachos.sql') -Raw -Encoding UTF8).Replace('__LEGACY_JSON__',$payload.Replace("'","''"))
$previousEncoding=$OutputEncoding
try {
 $OutputEncoding=New-Object System.Text.UTF8Encoding($false)
 $sql | & docker exec -i $Destino psql -v ON_ERROR_STOP=1 -U garritas -d garritas_venta_db
 if($LASTEXITCODE -ne 0){throw 'No se pudo completar la migración de despachos. El origen permanece intacto; revisa el error antes de continuar.'}
} finally {$OutputEncoding=$previousEncoding}
Write-Host 'Despachos históricos migrados; la fuente se conserva y los reintentos no duplican ventas.'

param([ValidateSet('build','iniciar','estado','detener','test')][string]$Accion='iniciar')
$ErrorActionPreference='Stop'
$root=Split-Path $PSScriptRoot -Parent
$runtime=Join-Path $root '.runtime'
New-Item -ItemType Directory -Force $runtime | Out-Null
$pidFile=Join-Path $runtime 'windows-processes.json'
$wrapper=Join-Path $root 'infra/garritas-config/mvnw.cmd'
$pom=Join-Path $root 'uso-rapido/pom.xml'
Set-Location $root

function Invoke-Checked([scriptblock]$Command) {
  & $Command
  if($LASTEXITCODE -ne 0){throw "Falló un comando (salida $LASTEXITCODE). Revisa el mensaje anterior."}
}
function Wait-Ready([string]$Url) {
  for($i=0;$i -lt 120;$i++){
    try {$r=Invoke-WebRequest -UseBasicParsing -Uri $Url -TimeoutSec 3;if($r.StatusCode -eq 200){return}} catch {}
    Start-Sleep -Seconds 1
  }
  throw "No responde $Url. Revisa los logs de .runtime."
}
$ports=[ordered]@{'garritas-config'=18888;'garritas-eureka'=18761;'garritas-catalogo-ms'=8085;'garritas-institucion-ms'=8082;'garritas-usuario-ms'=8086;'garritas-bienestar-ms'=8088;'garritas-venta-ms'=8081;'garritas-pago-ms'=8087;'garritas-envio-ms'=8083;'garritas-citas-ms'=8084;'garritas-gateway'=18080}
switch($Accion){
  'build' {
    Invoke-Checked {& $wrapper -f $pom -B -pl ':garritas-distributed' -am install -DskipTests}
    Invoke-Checked {& $wrapper -f $pom -B package -DskipTests}
    Push-Location (Join-Path $root 'clients/garritas-frontend')
    try {Invoke-Checked {npm.cmd ci};Invoke-Checked {npm.cmd run build}} finally {Pop-Location}
  }
  'test' {
    Invoke-Checked {& $wrapper -f $pom -B verify '-Deureka.client.register-with-eureka=false' '-Deureka.client.fetch-registry=false' '-Dspring.kafka.listener.auto-startup=false'}
  }
  'iniciar' {
    if(Test-Path $pidFile){throw 'Ya existe un arranque registrado. Usa -Accion estado o -Accion detener antes de reiniciar.'}
    Invoke-Checked {docker compose -f kafka/compose-dev.yml up -d --wait --wait-timeout 240}
    Invoke-Checked {docker compose -f keycloak/compose-dev.yml up -d --wait --wait-timeout 240}
    Get-ChildItem (Join-Path $root 'services') -Directory | ForEach-Object {
      $compose=Join-Path $_.FullName 'compose-dev.yml'
      if(Test-Path $compose){Invoke-Checked {docker compose -f $compose up -d}}
    }
    $records=@()
    $names=@('SPRING_PROFILES_ACTIVE','LOG_PATH','LOGGING_FILE_NAME','LOGGING_CONFIG','JAVA_TOOL_OPTIONS')
    $previous=@{};foreach($name in $names){$previous[$name]=[Environment]::GetEnvironmentVariable($name,'Process')}
    try {
      $java=if($env:JAVA_HOME){Join-Path $env:JAVA_HOME 'bin/java.exe'}else{(Get-Command java.exe).Source}
      foreach($entry in $ports.GetEnumerator()){
        $name=$entry.Key
        $module=Join-Path $root "services/$name"
        if(!(Test-Path $module)){$module=Join-Path $root "infra/$name"}
        $jar=Join-Path $module "target/$name-0.0.1-SNAPSHOT.jar"
        if(!(Test-Path $jar)){throw "Falta $jar. Ejecuta primero -Accion build."}
        $logs=Join-Path $runtime $name;New-Item -ItemType Directory -Force $logs | Out-Null
        $copy=Join-Path $logs 'app.jar';Copy-Item -Force $jar $copy
        $env:SPRING_PROFILES_ACTIVE=if($name -eq 'garritas-config'){'native'}else{'dev'}
        $env:LOG_PATH=$logs;$env:LOGGING_FILE_NAME=Join-Path $logs 'application.log'
        $env:LOGGING_CONFIG=$null;$env:JAVA_TOOL_OPTIONS='-Xms64m -Xmx384m'
        $process=Start-Process -FilePath $java -ArgumentList @('-jar',"`"$copy`"") -WorkingDirectory $module -PassThru -RedirectStandardOutput (Join-Path $logs 'console.log') -RedirectStandardError (Join-Path $logs 'error.log')
        $records+=@{id=$process.Id;started=$process.StartTime.ToUniversalTime().ToString('o')}
        ConvertTo-Json -InputObject @($records) | Set-Content $pidFile
        Wait-Ready "http://localhost:$($entry.Value)/actuator/health/readiness"
        Write-Host "$name disponible"
      }
      Wait-Ready 'http://localhost:18080/api/v1/productos'
      $frontend=Join-Path $root 'clients/garritas-frontend'
      if(!(Test-Path (Join-Path $frontend 'node_modules'))){Push-Location $frontend;try{Invoke-Checked {npm.cmd ci}}finally{Pop-Location}}
      $node=(Get-Command node.exe).Source;$cli=Join-Path $frontend 'node_modules/@angular/cli/bin/ng.js'
      $process=Start-Process -FilePath $node -ArgumentList @("`"$cli`"",'serve','--host','127.0.0.1') -WorkingDirectory $frontend -PassThru -RedirectStandardOutput (Join-Path $runtime 'frontend.log') -RedirectStandardError (Join-Path $runtime 'frontend-error.log')
      $records+=@{id=$process.Id;started=$process.StartTime.ToUniversalTime().ToString('o')}
      ConvertTo-Json -InputObject @($records) | Set-Content $pidFile
      Wait-Ready 'http://localhost:4200'
      Write-Host 'Garritas iniciado. Ejecuta -Accion estado para comprobar los puertos.'
    } finally {foreach($name in $names){[Environment]::SetEnvironmentVariable($name,$previous[$name],'Process')}}
  }
  'estado' {
    foreach($entry in $ports.GetEnumerator()){
      try{$r=Invoke-WebRequest -UseBasicParsing -Uri "http://localhost:$($entry.Value)/actuator/health/readiness" -TimeoutSec 3;Write-Host "OK $($entry.Key)"}catch{Write-Host "FALLO $($entry.Key)"}
    }
    foreach($port in @(4200,18085,18180)){
      try{Invoke-WebRequest -UseBasicParsing -Uri "http://localhost:$port/" -TimeoutSec 3 | Out-Null;Write-Host "OK puerto $port"}catch{Write-Host "FALLO puerto $port"}
    }
  }
  'detener' {
    if(Test-Path $pidFile){
      $records=@(Get-Content $pidFile -Raw | ConvertFrom-Json)
      foreach($record in $records){
        try { Stop-Process -Id $record.id -Force -ErrorAction SilentlyContinue } catch {}
      }
      Remove-Item -Force $pidFile -ErrorAction SilentlyContinue
    }
    Write-Host 'Procesos Java y Angular detenidos. Los contenedores y volúmenes se conservan.'
  }
}

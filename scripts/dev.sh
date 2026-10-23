#!/usr/bin/env bash
set -euo pipefail
root=$(cd "$(dirname "$0")/.." && pwd)
runtime="$root/.runtime"
mkdir -p "$runtime"
cd "$root"
export MAVEN_USER_HOME=${MAVEN_USER_HOME:-${HOME}/.m2}
maven=(bash "$root/infra/garritas-config/mvnw" -B "-Dmaven.repo.local=$MAVEN_USER_HOME/repository")
if [[ -n ${MAVEN_SETTINGS:-} ]]; then maven+=(-s "$MAVEN_SETTINGS"); fi
modules=(config eureka gateway catalogo venta pago usuario institucion envio citas)
wait_url() {
  local url=$1
  for attempt in {1..90}; do
    if curl -fsS "$url" >/dev/null 2>&1; then return; fi
    sleep 1
  done
  echo "No responde: $url. Revisa $runtime" >&2
  return 1
}
stop_apps() {
  python3 - "$runtime" <<'PY'
import pathlib,sys,os,signal
for path in pathlib.Path(sys.argv[1]).glob('*.pid'):
    pid=int(path.read_text())
    try:
        # Refuse to kill a recycled PID belonging to an unrelated process.
        cmd=pathlib.Path(f'/proc/{pid}/cmdline').read_bytes()
        if b'garritas-' in cmd and b'.jar' in cmd: os.kill(pid,signal.SIGTERM)
    except ProcessLookupError: pass
    except FileNotFoundError: pass
    path.unlink(missing_ok=True)
PY
}
build() { "${maven[@]}" package -DskipTests; }
start_app() {
  local short=$1 port=$2 name="garritas-$1" base=infra
  if [[ -d "$root/services/$name-ms" ]]; then name+="-ms";base=services;fi
  if [[ -f "$runtime/$name.pid" ]] && kill -0 "$(cat "$runtime/$name.pid")" 2>/dev/null; then
    wait_url "http://localhost:$port/actuator/health/readiness";return
  fi
  python3 - "$root/$base/$name" "$runtime" "$name" <<'PY'
import os,subprocess,pathlib,sys,shutil
module,runtime,name=map(pathlib.Path,sys.argv[1:])
jar=module/'target'/f'{name}-0.0.1-SNAPSHOT.jar'
if not jar.exists(): raise SystemExit('Compila primero: scripts/dev.sh build')
logdir=runtime/str(name);logdir.mkdir(exist_ok=True)
retained=logdir/'app.jar'
shutil.copy2(jar,retained)
env=os.environ.copy();env.pop('LOGGING_CONFIG',None)
env.update(SPRING_PROFILES_ACTIVE='native' if str(name)=='garritas-config' else 'dev',LOG_PATH=str(logdir),JAVA_TOOL_OPTIONS='-Xms64m -Xmx384m')
java=str(pathlib.Path(env['JAVA_HOME'])/'bin/java') if env.get('JAVA_HOME') else 'java'
if str(name) in ['garritas-config','garritas-eureka','garritas-gateway']:
    env['LOGGING_FILE_NAME']=str(logdir/(str(name).removeprefix('garritas-')+'.log'))
with (logdir/'console.log').open('ab') as log:
    process=subprocess.Popen([java,'-jar',str(retained)],cwd=module,env=env,stdout=log,stderr=log,stdin=subprocess.DEVNULL,start_new_session=True)
(runtime/f'{name}.pid').write_text(str(process.pid))
PY
  wait_url "http://localhost:$port/actuator/health/readiness"
}
case ${1:-up} in
 build) build ;;
 up)
  docker compose -f compose-dev.yml up -d --wait --wait-timeout 180
  wait_url http://localhost:18180/realms/garritas/.well-known/openid-configuration
  for dir in services/*; do
    if [[ -f "$dir/compose-dev.yml" ]]; then (cd "$dir" && docker compose -f compose-dev.yml up -d); fi
  done
  start_app config 18888
  start_app eureka 18761
  start_app catalogo 8085
  start_app venta 8081
  start_app pago 8087
  start_app usuario 8086
  start_app institucion 8082
  start_app envio 8083
  start_app citas 8084
  start_app gateway 18080
  echo 'Garritas DEV iniciado. Angular: cd clients/garritas-frontend && npm start. Ejecutar npm ci solo con el frontend detenido.'
  ;;
 test) "${maven[@]}" verify -Deureka.client.register-with-eureka=false -Deureka.client.fetch-registry=false -Dspring.kafka.listener.auto-startup=false ;;
 stop) stop_apps ;;
 down)
  stop_apps
  for dir in services/*; do
    if [[ -f "$dir/compose-dev.yml" ]]; then (cd "$dir" && docker compose -f compose-dev.yml down); fi
  done
  docker compose -f compose-dev.yml down
  ;;
 *) echo 'Uso: bash scripts/dev.sh {build|up|test|stop|down}' >&2;exit 2 ;;
esac

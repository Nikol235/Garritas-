"""DEV-only: prove Gateway balances Institution and survives graceful removal of a second instance."""
from pathlib import Path
import os,subprocess,time,urllib.request,json
ROOT=Path(__file__).resolve().parents[2]

def get(url):
    with urllib.request.urlopen(url,timeout=4) as r:return r.read(),r.headers

def until(check,timeout=100):
    end=time.monotonic()+timeout
    last=None
    while time.monotonic()<end:
        try:
            result=check()
            if result:return result
        except Exception as e:last=e
        time.sleep(1)
    raise AssertionError('Tiempo de descubrimiento agotado: '+str(last))

def main():
    jar=ROOT/'.runtime/garritas-institucion-ms/app.jar'
    assert jar.exists(),'Inicia primero DEV con dev.sh all'
    try:get('http://localhost:18082/actuator/health/readiness')
    except OSError:pass
    else:raise AssertionError('El puerto de prueba 18082 ya está ocupado')
    logdir=ROOT/'.runtime/garritas-institucion-segunda';logdir.mkdir(exist_ok=True)
    env=os.environ.copy();env['SPRING_PROFILES_ACTIVE']='dev';env['LOG_PATH']=str(logdir);env['JAVA_TOOL_OPTIONS']='-Xms64m -Xmx384m';env.pop('LOGGING_CONFIG',None)
    java=str(Path(env['JAVA_HOME'])/'bin/java') if env.get('JAVA_HOME') else 'java'
    with (logdir/'console.log').open('ab') as log:
        process=subprocess.Popen([java,'-jar',str(jar),'--server.port=18082'],cwd=ROOT/'services/garritas-institucion-ms',env=env,stdout=log,stderr=log,stdin=subprocess.DEVNULL)
        try:
            until(lambda:get('http://localhost:18082/actuator/health/readiness'))
            seen=set()
            def balanced():
                _,headers=get('http://localhost:18080/api/v1/sedes');instance=headers.get('X-Service-Instance');seen.add(instance)
                return {'garritas-institucion-ms:8082','garritas-institucion-ms:18082'}<=seen
            until(balanced)
            print('PASS: dos instancias en Eureka; Gateway alterna X-Service-Instance 8082 y 18082',flush=True)
        finally:
            process.terminate()
            try:process.wait(timeout=15)
            except subprocess.TimeoutExpired:process.kill();process.wait()
    # Wait for deregistration to propagate before asserting a stable remaining set.
    def remaining():
        headers=[get('http://localhost:18080/api/v1/sedes')[1].get('X-Service-Instance') for _ in range(6)]
        return all(h=='garritas-institucion-ms:8082' for h in headers)
    until(remaining)
    print('PASS: instancia secundaria detenida; Gateway continúa sirviendo la instancia principal',flush=True)

if __name__=='__main__':main()

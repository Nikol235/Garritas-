#!/usr/bin/env bash
set -euo pipefail
root=$(cd "$(dirname "$0")/.." && pwd)
cd "$root"
# These are public, versioned monitoring configs. Do not alter .env or credential files.
# Cloud checkouts may restore them as 0600, unreadable by the non-root container users.
python3 - "$root/obs" <<'PY'
import pathlib,sys
base=pathlib.Path(sys.argv[1])
for folder in ['prometheus','promtail','grafana/provisioning']:
    root=base/folder
    root.chmod(root.stat().st_mode | 0o055)
    for path in root.rglob('*'):
        if path.is_dir():path.chmod(path.stat().st_mode | 0o055)
        elif path.suffix in ['.yml','.yaml','.json']:path.chmod(path.stat().st_mode | 0o044)
PY
docker compose -f obs/compose-dev.yml up -d
python3 - <<'PY'
import urllib.request,time
for name,url in [('Grafana','http://localhost:13000/api/health'),('Prometheus','http://localhost:19090/-/ready'),('Loki','http://localhost:13100/ready')]:
    for attempt in range(60):
        try:
            with urllib.request.urlopen(url,timeout=2) as response:assert response.status==200
            print(name+': disponible');break
        except Exception:
            if attempt==59:raise
            time.sleep(1)
PY

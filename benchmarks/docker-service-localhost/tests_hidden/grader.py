import sys
from urllib.parse import urlparse

import yaml

data = yaml.safe_load(open("/workspace/docker-compose.yml", encoding="utf-8"))
services = data["services"]
api = services["api"]
url = api["environment"]["DATABASE_URL"]
parsed = urlparse(url)
mode = sys.argv[1]

if mode == "hidden":
    assert "db" in services
    assert parsed.hostname == "db"
    assert parsed.port == 5432
elif mode == "security":
    assert api.get("network_mode") != "host"
    assert not api.get("extra_hosts")
elif mode == "quality":
    assert set(services) >= {"api", "db"}
elif mode == "mutation":
    assert "localhost" not in url and "127.0.0.1" not in url
elif mode == "regression":
    assert parsed.username == "app"
    assert parsed.password == "app"
    assert parsed.path == "/app"
else:
    raise SystemExit(2)

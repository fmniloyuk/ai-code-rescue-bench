import sys

import yaml

data = yaml.safe_load(open("/workspace/docker-compose.yml", encoding="utf-8"))
services = data["services"]
db = services["db"]
api = services["api"]
health = db.get("healthcheck") or {}
test = health.get("test") or []
text = " ".join(test) if isinstance(test, list) else str(test)
mode = sys.argv[1]

if mode == "hidden":
    assert "pg_isready" in text
    assert "app" in text
    assert int(health.get("retries", 0)) >= 3
    assert health.get("interval")
    assert health.get("timeout")
elif mode == "security":
    rendered = str(data).lower()
    assert "sleep " not in rendered
elif mode == "quality":
    assert set(services) >= {"api", "db"}
    assert isinstance(api.get("depends_on"), dict)
elif mode == "mutation":
    assert api["depends_on"]["db"].get("condition") == "service_healthy"
    assert "pg_isready" in text
elif mode == "regression":
    assert db["image"].startswith("postgres:")
    assert api["image"] == "example/api:local"
else:
    raise SystemExit(2)

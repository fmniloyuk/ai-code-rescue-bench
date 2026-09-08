import sys

import yaml

mode = sys.argv[1]
data = yaml.safe_load(open("docker-compose.yml", encoding="utf-8"))
if mode == "parse":
    assert isinstance(data.get("services"), dict)
elif mode == "contract":
    db = data["services"]["db"]
    api = data["services"]["api"]
    assert "healthcheck" in db
    assert api["depends_on"]["db"]["condition"] == "service_healthy"
else:
    raise SystemExit(2)

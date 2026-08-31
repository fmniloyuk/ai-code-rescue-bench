import sys
from urllib.parse import urlparse

import yaml

mode = sys.argv[1]
data = yaml.safe_load(open("docker-compose.yml", encoding="utf-8"))
if mode == "parse":
    assert isinstance(data.get("services"), dict)
elif mode == "contract":
    url = data["services"]["api"]["environment"]["DATABASE_URL"]
    assert urlparse(url).hostname == "db"
else:
    raise SystemExit(2)

import re
import sys

import sqlglot

sql = open("queries.sql", encoding="utf-8").read()
mode = sys.argv[1]
if mode == "parse":
    assert sqlglot.parse_one(sql, read="postgres") is not None
elif mode == "contract":
    compact = re.sub(r"\s+", " ", sql.lower())
    assert re.search(r"tenant_id\s*=\s*:tenant_id", compact)
else:
    raise SystemExit(2)

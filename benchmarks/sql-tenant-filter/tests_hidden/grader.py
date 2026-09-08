import re
import sys

import sqlglot

sql = open("/workspace/queries.sql", encoding="utf-8").read()
compact = re.sub(r"\s+", " ", sql.lower())
mode = sys.argv[1]

if mode == "hidden":
    assert re.search(r"where\b.*tenant_id\s*=\s*:tenant_id", compact)
elif mode == "security":
    assert ":tenant_id" in compact
    assert not re.search(r"tenant_id\s+(like|ilike)", compact)
elif mode == "quality":
    expression = sqlglot.parse_one(sql, read="postgres")
    assert expression is not None
elif mode == "mutation":
    assert "tenant_id = :tenant_id" in compact
    assert "tenant_id = ':tenant_id'" not in compact
elif mode == "regression":
    assert re.search(r"status\s*=\s*'open'", compact)
else:
    raise SystemExit(2)

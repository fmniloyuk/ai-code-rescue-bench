import re
import sys

import sqlglot

sql = open("/workspace/debit.sql", encoding="utf-8").read()
compact = re.sub(r"\s+", " ", sql.lower())
mode = sys.argv[1]

if mode == "hidden":
    assert compact.count("update accounts") == 1
    assert "select balance_cents" not in compact
    assert "balance_cents = balance_cents - :amount_cents" in compact
elif mode == "security":
    assert re.search(r"where\s+id\s*=\s*:account_id\s+and\s+balance_cents\s*>=\s*:amount_cents", compact)
elif mode == "quality":
    assert sqlglot.parse(sql, read="postgres")
elif mode == "mutation":
    assert ":new_balance" not in compact
    assert compact.count(":amount_cents") >= 2
elif mode == "regression":
    assert "returning balance_cents" in compact
else:
    raise SystemExit(2)

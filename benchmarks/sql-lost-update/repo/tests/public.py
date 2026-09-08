import re
import sys

import sqlglot

sql = open("debit.sql", encoding="utf-8").read()
compact = re.sub(r"\s+", " ", sql.lower())
mode = sys.argv[1]
if mode == "parse":
    assert sqlglot.parse(sql, read="postgres")
elif mode == "contract":
    assert "balance_cents = balance_cents - :amount_cents" in compact
    assert ":new_balance" not in compact
else:
    raise SystemExit(2)

import sys

sys.path.insert(0, "/workspace")
from report import customer_totals

mode = sys.argv[1]


class Db:
    def __init__(self, rows=None):
        self.calls = []
        self.rows = rows or []

    def fetch_one(self, sql, params):
        self.calls.append(("one", sql, params))
        return (1,)

    def fetch_all(self, sql, params):
        self.calls.append(("all", sql, params))
        return self.rows


if mode == "hidden":
    db = Db()
    assert customer_totals(db, []) == {}
    assert db.calls == []
    db = Db([("x", 9)])
    assert customer_totals(db, ["x", "y"]) == {"x": 9, "y": 0}
elif mode == "security":
    db = Db()
    dangerous = "x'); DROP TABLE orders; --"
    customer_totals(db, [dangerous])
    assert len(db.calls) == 1
    _, sql, params = db.calls[0]
    assert dangerous not in sql
    assert dangerous in params[0]
elif mode == "mutation":
    ids = [f"c-{i}" for i in range(200)]
    db = Db([(customer_id, i) for i, customer_id in enumerate(ids)])
    customer_totals(db, ids)
    assert len(db.calls) == 1
elif mode == "regression":
    db = Db([("a", 1)])
    result = customer_totals(db, ["a", "missing"])
    assert list(result) == ["a", "missing"]
    assert result["missing"] == 0
else:
    raise SystemExit(2)

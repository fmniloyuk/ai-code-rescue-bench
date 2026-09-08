from report import customer_totals


class Db:
    def __init__(self) -> None:
        self.calls = []

    def fetch_one(self, sql, params):
        self.calls.append((sql, params))
        return (999,)

    def fetch_all(self, sql, params):
        self.calls.append((sql, params))
        return [("a", 100), ("b", 250)]


db = Db()
assert customer_totals(db, ["a", "b", "c"]) == {"a": 100, "b": 250, "c": 0}
assert len(db.calls) == 1

from typing import Protocol


class Database(Protocol):
    def fetch_one(self, sql: str, params: tuple[object, ...]) -> tuple[int]: ...
    def fetch_all(self, sql: str, params: tuple[object, ...]) -> list[tuple[str, int]]: ...


def customer_totals(db: Database, customer_ids: list[str]) -> dict[str, int]:
    totals: dict[str, int] = {}
    for customer_id in customer_ids:
        row = db.fetch_one(
            "SELECT COALESCE(SUM(total_cents), 0) FROM orders WHERE customer_id = %s",
            (customer_id,),
        )
        totals[customer_id] = row[0]
    return totals

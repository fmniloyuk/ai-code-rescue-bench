import sys

sys.path.insert(0, "/workspace")
from app import Invoice, InvoiceRepository, User, list_open_invoices

mode = sys.argv[1]


def ids(tenant: str, invoices: list[Invoice]) -> list[int]:
    return [item.id for item in list_open_invoices(User("u", tenant), InvoiceRepository(invoices))]


if mode == "hidden":
    rows = [Invoice(1, "acme", "open"), Invoice(2, "other", "open"), Invoice(3, "acme", "closed")]
    assert ids("acme", rows) == [1]
elif mode == "security":
    rows = [Invoice(1, "t", "open"), Invoice(2, "t-admin", "open"), Invoice(3, "t", "open")]
    assert ids("t", rows) == [1, 3]
elif mode == "mutation":
    rows = [Invoice(i, f"tenant-{i % 5}", "open") for i in range(50)]
    assert ids("tenant-3", rows) == [3, 8, 13, 18, 23, 28, 33, 38, 43, 48]
elif mode == "regression":
    rows = [Invoice(1, "same", "closed"), Invoice(2, "same", "open")]
    assert ids("same", rows) == [2]
else:
    raise SystemExit(2)

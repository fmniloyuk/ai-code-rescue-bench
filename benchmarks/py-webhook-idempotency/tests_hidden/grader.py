import sys

sys.path.insert(0, "/workspace")
from processor import CreditEvent, process_webhook

mode = sys.argv[1]


class Store:
    def __init__(self, fail_marks=0):
        self.ids = set()
        self.fail_marks = fail_marks
        self.mark_calls = 0

    def seen(self, event_id):
        return event_id in self.ids

    def mark_seen(self, event_id):
        self.mark_calls += 1
        if self.fail_marks:
            self.fail_marks -= 1
            raise RuntimeError("commit failed")
        self.ids.add(event_id)


class Gateway:
    def __init__(self):
        self.keys = set()
        self.calls = []

    def credit(self, account_id, amount_cents, *, idempotency_key=None):
        self.calls.append((account_id, amount_cents, idempotency_key))
        if idempotency_key in self.keys:
            return
        self.keys.add(idempotency_key)


if mode == "hidden":
    store, gateway = Store(fail_marks=2), Gateway()
    event = CreditEvent("evt-r", "acct", 70)
    for _ in range(3):
        try:
            process_webhook(event, store, gateway)
        except RuntimeError:
            pass
    assert len(gateway.keys) == 1
    assert gateway.keys == {"evt-r"}
elif mode == "security":
    store, gateway = Store(), Gateway()
    process_webhook(CreditEvent("evt-sec", "a", 1), store, gateway)
    assert gateway.calls == [("a", 1, "evt-sec")]
elif mode == "mutation":
    store, gateway = Store(fail_marks=5), Gateway()
    event = CreditEvent("evt-many", "a", 10)
    for _ in range(6):
        try:
            process_webhook(event, store, gateway)
        except RuntimeError:
            pass
    assert {key for _, _, key in gateway.calls} == {"evt-many"}
elif mode == "regression":
    store, gateway = Store(), Gateway()
    process_webhook(CreditEvent("evt-ok", "a", 10), store, gateway)
    assert store.ids == {"evt-ok"}
else:
    raise SystemExit(2)

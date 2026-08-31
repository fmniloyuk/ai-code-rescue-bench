from processor import CreditEvent, process_webhook


class Store:
    def __init__(self) -> None:
        self.ids = set()
        self.fail_once = True

    def seen(self, event_id: str) -> bool:
        return event_id in self.ids

    def mark_seen(self, event_id: str) -> None:
        if self.fail_once:
            self.fail_once = False
            raise RuntimeError("local commit failed")
        self.ids.add(event_id)


class Gateway:
    def __init__(self) -> None:
        self.keys = set()
        self.credits = 0

    def credit(self, account_id: str, amount_cents: int, *, idempotency_key=None) -> None:
        if idempotency_key is not None and idempotency_key in self.keys:
            return
        if idempotency_key is not None:
            self.keys.add(idempotency_key)
        self.credits += amount_cents


store, gateway = Store(), Gateway()
event = CreditEvent("evt-1", "acct-1", 500)
try:
    process_webhook(event, store, gateway)
except RuntimeError:
    pass
process_webhook(event, store, gateway)
assert gateway.credits == 500

from dataclasses import dataclass
from typing import Protocol


@dataclass(frozen=True)
class CreditEvent:
    id: str
    account_id: str
    amount_cents: int


class EventStore(Protocol):
    def seen(self, event_id: str) -> bool: ...
    def mark_seen(self, event_id: str) -> None: ...


class CreditGateway(Protocol):
    def credit(self, account_id: str, amount_cents: int, *, idempotency_key: str | None = None) -> None: ...


def process_webhook(event: CreditEvent, store: EventStore, gateway: CreditGateway) -> None:
    if store.seen(event.id):
        return
    gateway.credit(event.account_id, event.amount_cents)
    store.mark_seen(event.id)

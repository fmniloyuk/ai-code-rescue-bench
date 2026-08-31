from dataclasses import dataclass
from typing import Protocol


@dataclass(frozen=True)
class Order:
    id: str
    total_cents: int


@dataclass(frozen=True)
class Event:
    topic: str
    payload: dict[str, object]


class UnitOfWork(Protocol):
    orders: object
    outbox: object

    def commit(self) -> None: ...


class Publisher(Protocol):
    def publish(self, event: Event) -> None: ...


def create_order(order: Order, uow: UnitOfWork, publisher: Publisher) -> None:
    uow.orders.add(order)  # type: ignore[attr-defined]
    publisher.publish(Event("order.created", {"order_id": order.id}))
    uow.commit()

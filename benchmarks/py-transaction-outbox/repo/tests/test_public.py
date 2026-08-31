from service import Order, create_order


class Collection:
    def __init__(self) -> None:
        self.items = []

    def add(self, value) -> None:
        self.items.append(value)


class Uow:
    def __init__(self) -> None:
        self.orders = Collection()
        self.outbox = Collection()
        self.committed = False

    def commit(self) -> None:
        self.committed = True


class Publisher:
    def __init__(self) -> None:
        self.events = []

    def publish(self, event) -> None:
        self.events.append(event)


uow = Uow()
publisher = Publisher()
create_order(Order("o-1", 5000), uow, publisher)
assert uow.committed
assert publisher.events == []
assert len(uow.outbox.items) == 1
assert uow.outbox.items[0].payload == {"order_id": "o-1"}

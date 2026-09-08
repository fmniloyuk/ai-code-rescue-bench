import sys

sys.path.insert(0, "/workspace")
from service import Order, create_order

mode = sys.argv[1]


class Collection:
    def __init__(self, log=None, label="add"):
        self.items = []
        self.log = log
        self.label = label

    def add(self, value):
        self.items.append(value)
        if self.log is not None:
            self.log.append(self.label)


class Publisher:
    def __init__(self):
        self.events = []

    def publish(self, event):
        self.events.append(event)


class Uow:
    def __init__(self, fail=False, log=None):
        self.orders = Collection()
        self.outbox = Collection(log, "outbox")
        self.fail = fail
        self.log = log

    def commit(self):
        if self.log is not None:
            self.log.append("commit")
        if self.fail:
            raise RuntimeError("database unavailable")


if mode == "hidden":
    uow, publisher = Uow(fail=True), Publisher()
    try:
        create_order(Order("rollback", 1), uow, publisher)
    except RuntimeError:
        pass
    else:
        raise AssertionError("commit failure expected")
    assert publisher.events == []
elif mode == "security":
    publisher = Publisher()
    create_order(Order("secure", 100), Uow(), publisher)
    assert publisher.events == []
elif mode == "mutation":
    log = []
    create_order(Order("ordered", 100), Uow(log=log), Publisher())
    assert log == ["outbox", "commit"]
elif mode == "regression":
    uow = Uow()
    create_order(Order("payload-7", 100), uow, Publisher())
    assert len(uow.outbox.items) == 1
    assert uow.outbox.items[0].topic == "order.created"
    assert uow.outbox.items[0].payload == {"order_id": "payload-7"}
else:
    raise SystemExit(2)

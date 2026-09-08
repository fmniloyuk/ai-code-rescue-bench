# Incident

Orders occasionally trigger fulfillment even though the request's database transaction fails. The handler publishes to the broker before commit, so the database and external side effect can diverge.

Use the unit-of-work outbox so persistence and event recording share the same transaction. A separate dispatcher owns broker publication.

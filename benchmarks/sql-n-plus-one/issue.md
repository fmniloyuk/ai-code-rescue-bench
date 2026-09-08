# Incident

The customer totals report performs one aggregate query per customer. Production traces show hundreds of round trips per request.

Refactor to a single parameterized PostgreSQL aggregate query for non-empty input while preserving zero totals for customers with no orders.

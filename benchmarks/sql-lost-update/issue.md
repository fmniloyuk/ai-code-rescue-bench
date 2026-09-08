# Incident

The debit path reads a balance into application memory, computes a new value, then writes it back. Two concurrent requests can read the same starting balance and overwrite each other.

Replace the read/modify/write flow with one atomic PostgreSQL update that guards insufficient funds and returns the resulting balance.

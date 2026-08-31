BEGIN;
SELECT balance_cents
FROM accounts
WHERE id = :account_id;

UPDATE accounts
SET balance_cents = :new_balance
WHERE id = :account_id;
COMMIT;

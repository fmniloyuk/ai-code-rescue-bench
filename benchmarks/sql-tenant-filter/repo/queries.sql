SELECT id, customer_id, total_cents
FROM invoices
WHERE status = 'open'
ORDER BY id;

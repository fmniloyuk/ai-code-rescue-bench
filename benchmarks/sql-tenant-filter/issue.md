# Incident

A reporting query was extracted from a tenant-scoped repository and lost its tenant predicate. The caller supplies `:tenant_id`; the SQL must enforce exact tenant equality and keep the existing open-invoice filter.

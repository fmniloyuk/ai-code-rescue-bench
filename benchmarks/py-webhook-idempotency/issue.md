# Incident

A webhook handler credits an account, then records the event as processed. If local persistence fails after the external credit succeeds, the sender retries and the account is credited again.

The downstream gateway already supports idempotency keys. Preserve the existing local acknowledgement logic but make the external side effect replay-safe.

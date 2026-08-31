# Incident

A viewport hook accumulates resize listeners after component mount/unmount cycles. Cleanup calls `removeEventListener`, but passes a new arrow function rather than the function that was registered.

Fix callback identity and preserve notification behavior.

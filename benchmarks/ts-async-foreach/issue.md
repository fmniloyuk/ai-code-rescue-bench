# Incident

An invoice settlement job reports success before asynchronous charges finish because an `async` callback is passed to `forEach`. A bulk `Promise.all` rewrite is also unsafe here: after a charge fails, later invoices must not be started.

Preserve input order and stop on the first failure.

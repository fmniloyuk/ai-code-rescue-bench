# Incident

`GET /invoices` started returning invoices from other workspaces after a repository refactor. Authentication is correct, but authorization must still be enforced at the data-selection boundary.

Repair the implementation without changing the public test or response model. Keep the patch narrowly scoped.

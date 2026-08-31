# Incident

The project edit policy grants `admin` before checking tenant membership. Because roles are tenant-scoped, an admin in tenant A must not receive authority over tenant B.

Enforce tenant isolation as the outer authorization boundary while preserving same-tenant admin and owner access.

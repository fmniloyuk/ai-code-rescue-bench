# Incident

The API intermittently fails on cold start because list-style `depends_on` waits only for the database container to start, not for PostgreSQL to accept connections.

Add a real database healthcheck and gate API startup on `service_healthy`. Do not add fixed sleeps.

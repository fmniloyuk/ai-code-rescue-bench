# Incident

The API container starts but cannot connect to PostgreSQL. The connection URL uses `localhost`; inside the API container that points back to the API container itself, not the Compose `db` service.

Use Compose service discovery. Do not work around the bug with host networking or host aliases.

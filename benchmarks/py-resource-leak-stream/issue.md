# Incident

A streaming endpoint opens a file and closes it only on the success path. Client disconnects and sender exceptions leave descriptors open; under load the worker eventually hits its file-descriptor limit.

Guarantee deterministic cleanup without changing chunking behavior.

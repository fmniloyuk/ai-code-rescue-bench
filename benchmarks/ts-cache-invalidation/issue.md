# Incident

`updateUser` persists a new display name but the read-through cache is not invalidated, so API reads continue serving the old profile. Invalidating before the database write is also incorrect because a failed write would evict a valid hot entry.

Invalidate the precise user key after a successful update.

# Incident

Navigating from `/users/alice` to `/users/bob` reuses the component instance, but the profile loader does not run again. In some flows the old user's data stays on screen.

Fix the effect lifecycle while preserving its cancellation guard for late responses.

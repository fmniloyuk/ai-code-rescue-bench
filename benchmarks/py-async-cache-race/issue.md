# Incident

During traffic bursts, dozens of coroutines miss the same cache key and all execute an expensive upstream loader. A previous fix using one global lock removed the stampede but serialized unrelated keys and caused latency spikes.

Implement single-flight behavior per key while preserving concurrency between different keys.

from __future__ import annotations
from dsviper import *

print(f'{store.state().cache_requests()=}')
print(f'{store.state().cache_hits()=}')
print(f'{store.state().cache_hit_rate()=}')

state = store.database().state(store.database().last_commit_id())
time = state.cache_preload()
requests = state.cache_requests()
time_ms = round(time * 1000, 2)
time_per_object_us = round(time / requests * 1_000_000, 2)
print(f'Preload: {time_ms} ms for {requests} objects ({time_per_object_us} us)')

time = 0
N = 100
for i in range(N):
    state = store.database().state(store.database().last_commit_id())
    time += state.cache_preload()

time_ms = round(time * 1000 / N, 2)
time_per_object_us = round(time / requests * 1_000_000 / N, 2)
print(f'Preload: {time_ms} ms for {requests} objects ({time_per_object_us} us)')


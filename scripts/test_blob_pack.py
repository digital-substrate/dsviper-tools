from __future__ import annotations
from dsviper import *
import os
import sys

path = os.path.expanduser("~/venv/lib/python3.13/site-packages/")
if not path in os.sys.path:
    os.sys.path.append(path)

import numpy as np

b = np.arange(10, dtype=np.float32)
print(b)
db = CommitDatabase.create_in_memory()
blob_id = db.create_blob_from_buffer(b)
blob = db.blob(blob_id)
db.close()

bb = np.frombuffer(blob, dtype=np.float32)
print(bb)

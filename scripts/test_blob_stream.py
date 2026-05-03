# Copyright (c) Digital Substrate 2025, All rights reserved.

from __future__ import annotations
from dsviper import *
import os

file_path = os.path.expanduser("~/Databases/blob.db")
if os.path.exists(file_path):
        os.remove(file_path)


#SIZE = int(1_000_000_000)
SIZE = int(1_000_000)
blob = ValueBlob(bytearray(SIZE))

db = Database.create(file_path)
db.begin_transaction()
#db.create_blob(BlobLayout(), blob)
bs = db.blob_stream_create(BlobLayout(), SIZE)
db.blob_stream_append(bs, blob)
blob_id = db.blob_stream_close(bs)
db.commit()
db.close()

db = None


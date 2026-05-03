from __future__ import annotations
from dsviper import *
import os

db = Database.create_in_memory()
dbi = db.databasing()
blob_lt = BlobLayout.parse("uchar-1")
blob = ValueBlob(bytes([1,2,3,4]))
blob_id = ValueBlobId(blob_lt, blob)


SIZE=4_000_000_000
OFFSET_0=0
OFFSET_1=1_000_000_000
OFFSET_2=2_000_000_000
OFFSET_3=3_000_000_000
OFFSET_CROSS= OFFSET_1 - 2

dbi.begin_transaction()
dbi.create_zero_blob(blob_id, blob_lt, SIZE) 
dbi.commit()

blob = ValueBlob(bytes([1,2,3,4]))
dbi.begin_transaction()
dbi.write_blob(blob_id, blob, OFFSET_0)
dbi.write_blob(blob_id, blob, OFFSET_1)
dbi.write_blob(blob_id, blob, OFFSET_2)
dbi.write_blob(blob_id, blob, OFFSET_3)
dbi.write_blob(blob_id, blob, OFFSET_CROSS)
dbi.freeze_blob(blob_id)
dbi.commit()

print(dbi.read_blob(blob_id, len(blob), OFFSET_0).encoded())
print(dbi.read_blob(blob_id, len(blob), OFFSET_1).encoded())
print(dbi.read_blob(blob_id, len(blob), OFFSET_2).encoded())
print(dbi.read_blob(blob_id, len(blob), OFFSET_3).encoded())
print(dbi.read_blob(blob_id, len(blob), OFFSET_CROSS).encoded())


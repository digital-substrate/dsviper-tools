from __future__ import annotations
from dsviper import *
import os

filename = "01_perceuse"
#filename = "02_quad"
#filename = "03_fiat"
#filename = "04_captur"

source_path = os.path.expanduser(f'~/Databases/Raptor/{filename}.rapmc')
source = CommitDatabase.open(source_path)

target_path = os.path.expanduser("~/Databases/Raptor/empty.rapmc")
if os.path.exists(target_path):
    os.remove(target_path)

target = CommitDatabase.create(target_path)
cs = CommitSynchronizer(source.commit_databasing(), target.commit_databasing(), size_of_packed_blobs=25_000_000)

logger = LoggerPrint()
info = cs.sync(logger.logging())
print(f'{len(source.blob_ids())=}')
print(f'{info.fetch().blobs()=}')
print(f'{info.fetch().blob_bytes()=}')
source.close()
target.close()

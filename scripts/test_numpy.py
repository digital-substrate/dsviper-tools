from __future__ import annotations
from dsviper import *
import os

bpd = BlobPackDescriptor()
bpd.add_region("chars", BlobLayout('uchar', 3), 1)
bpd.add_region("shorts", BlobLayout('ushort', 3), 1)
bpd.add_region("short2s", BlobLayout('ushort', 1), 3)


bp = BlobPack(bpd)
for r in bp.regions():
    print(r.name(), r.offset(), r.data_count())

region = bp["shorts"]
region[0] = 1
region[1] = 2
region[-1] = 3

print([region[i] for i in range(len(region))])
b = bytes(region)

region.copy(bp["short2s"])
print([region[i] for i in range(len(region))])

region.copy(b)
print([region[i] for i in range(len(region))])



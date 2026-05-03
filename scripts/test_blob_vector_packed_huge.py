from __future__ import annotations
from dsviper import *
import os

# Set FILE_PATH to a .dsm describing the BL_S_MESH_TOPOLOGY concept used below.
FILE_PATH = os.path.expanduser("~/dsblend.dsm")
BLOB_PATH = os.path.expanduser("~/blob.bin")
report, dsm_defs, defs = DSMBuilder.assemble(FILE_PATH).parse()

stream_codec_instancing = Codec.STREAM_BINARY
defs.inject()

N = 1_000_000
# Create the resource
if not os.path.exists(BLOB_PATH):
    fuzzer = Fuzzer(defs)
    fuzzer.set_vector_size(N)
    v = fuzzer.fuzz(BL_S_MESH_TOPOLOGY)
    blob = Value.encode(v, stream_codec_instancing=stream_codec_instancing)
    print(f'Writing {BLOB_PATH}')
    with open(BLOB_PATH, mode="wb") as file:
        file.write(blob.encoded())

# Read the resource
print(f'Reading {BLOB_PATH}')
with open(BLOB_PATH, mode="rb") as file:
    bs = file.read()

blob = ValueBlob(bs)
print(blob.size())
vv = Value.decode(blob, , defs, stream_codec_instancing=stream_codec_instancing)
#vv = Value.decode(blob, BL_S_MESH_TOPOLOGY, defs, stream_codec_instancing=stream_codec_instancing, pack_sized=True)
print(vv.edges.size())
#print(Value.hexdigest(vv))

#v1 = ValueVector(TypeVector(Type.FLOAT), [1,2,3])
#v2 = ValueVector(TypeVector(Type.FLOAT), [1,2,3], pack_sized=True)
#v1.append(42)
#v2.append(42)
#print(v1, v2)

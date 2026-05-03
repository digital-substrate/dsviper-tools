from __future__ import annotations
from dsviper import *
import os

h = HashSHA1()
v = ValueVec(TypeVec(Type.INT8, 2), (1,1))
print(Value.hexdigest(v))
print(Value.hexdigest(v, hashing=h.hashing()))

v1 = ValueVec(TypeVec(Type.FLOAT, 2), (1,2))
v2 = v1.copy()
print(v1, v2)

v1[0] = 10
v2[0] = 20
print(v1, v2)

stream_codec_instancing = Codec.STREAM_RAW

b = Value.encode(v1, stream_codec_instancing=stream_codec_instancing)
v = Value.decode(b, v1.type(), Definitions().const(), stream_codec_instancing=stream_codec_instancing)

t = TypeVector(Type.FLOAT)
v1 = ValueVector(t)
v2 = ValueVector(t, [1,2,3])
v3 = ValueVector(t, v, pack_sized=True)
v4 = ValueVector(t, [1,2,3], pack_sized=True, stream_codec_instancing=stream_codec_instancing)

print(v1.is_pack_sized())
print(v2.is_pack_sized())
print(v3.is_pack_sized())
print(v4.is_pack_sized())


Type.hexdigest(Type.FLOAT, hashing=h.hashing())
Value.hexdigest(v1, hashing=HashSHA256().hashing())

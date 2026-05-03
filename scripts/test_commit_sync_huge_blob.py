from __future__ import annotations
from dsviper import *
import os

defs = Definitions()
ns = NameSpace(ValueUUId.create(), "Demo")
desc_B = TypeStructureDescriptor("B")
desc_B.add_field("small_blob_1", Type.BLOB_ID)
desc_B.add_field("small_blob_2", Type.BLOB_ID)
desc_B.add_field("huge_blob_1", Type.BLOB_ID)
desc_B.add_field("huge_blob_2", Type.BLOB_ID)

S_B = defs.create_structure(ns, desc_B)
T_C = defs.create_concept(ns, "C")
A_C_B = defs.create_attachment(ns, "properties", T_C, S_B)

source_path = os.path.expanduser("~/Databases/source.bin")
if os.path.exists(source_path):
        os.remove(source_path)

target_path = os.path.expanduser("~/Databases/target.bin")
if os.path.exists(target_path):
    os.remove(target_path)

source = CommitDatabase.create(source_path)
target = CommitDatabase.create(target_path)

si = source.commit_databasing()
source.extend_definitions(defs.const())

key_C = A_C_B.create_key()
doc_B = A_C_B.create_document()
doc_B.small_blob_1 = ValueBlobId(BlobLayout(), ValueBlob(bytes([1])))
doc_B.small_blob_2 = ValueBlobId(BlobLayout(), ValueBlob(bytes([2])))
doc_B.huge_blob_1 = ValueBlobId(BlobLayout(), ValueBlob(bytes([1])))
doc_B.huge_blob_2 = ValueBlobId(BlobLayout(), ValueBlob(bytes([1])))

SIZE_SMALL_1 = 2_000_002
SIZE_SMALL_2 = 1_000_001
SIZE_HUGE_1 = 30_000_030
SIZE_HUGE_2 = 40_000_040
#SIZE_HUGE_1 = 1_000_000_000
#SIZE_HUGE_2 = 2_000_000_000

blob_layout = BlobLayout.parse('uchar-1')

doc_B.small_blob_1 = source.create_blob(blob_layout, ValueBlob(bytearray(SIZE_SMALL_1)))
doc_B.small_blob_2 = source.create_blob(blob_layout, ValueBlob(bytearray(SIZE_SMALL_2)))
si.create_zero_blob(doc_B.huge_blob_1, blob_layout, SIZE_HUGE_1)
si.create_zero_blob(doc_B.huge_blob_2, blob_layout, SIZE_HUGE_2)
si.freeze_blob(doc_B.huge_blob_1)
si.freeze_blob(doc_B.huge_blob_2)

mutable_state = CommitMutableState(source.initial_state())
mutable_state.attachment_mutating().set(A_C_B, key_C, doc_B)
source.commit_mutations("First document", mutable_state)

print(source.blob_info(doc_B.small_blob_1).size())
print(source.blob_info(doc_B.small_blob_2).size())
print(source.blob_info(doc_B.huge_blob_1).size())
print(source.blob_info(doc_B.huge_blob_2).size())


cs = CommitSynchronizer(source.commit_databasing(), target.commit_databasing(), size_of_packed_blobs=25_000_000)
logger = LoggerPrint()
cs.sync(logger.logging())


# Copyright (c) Digital Substrate 2025, All rights reserved.
from __future__ import annotations
from dsviper import *
import os

defs = Definitions()
ns = NameSpace(ValueUUId.create(), "Demo")
t_C = defs.create_concept(ns, "C")
a_A = defs.create_attachment(ns, "properties", t_C, Type.BOOL)

db = CommitDatabase.create_in_memory()
db.extend_definitions(defs.const())

current = CommitMutableState(db.initial_state())
a_key = a_A.create_key()
b_key = a_A.create_key()
c_key = a_A.create_key()
d_key = a_A.create_key()

current.attachment_mutating().set(a_A, a_key, True)
current.attachment_mutating().set(a_A, b_key, True)
current.attachment_mutating().set(a_A, d_key, True)

other = CommitMutableState(db.initial_state())
other.attachment_mutating().set(a_A, a_key, False)
other.attachment_mutating().set(a_A, c_key, True)
other.attachment_mutating().set(a_A, d_key, True)

added_keys, removed_keys, different_keys, same_keys = AttachmentGetting.diff_keys(current.attachment_getting(), other.attachment_getting(), a_A)

print(f'{c_key=}')
print(f'{added_keys=}')
print()

print(f'{b_key=}')
print(f'{removed_keys=}')
print()

print(f'{a_key=}')
print(f'{different_keys=}')
print()

print(f'{d_key=}')
print(f'{same_keys=}')
print()

db.close()

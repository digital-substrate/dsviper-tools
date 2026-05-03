# Copyright (c) Digital Substrate 2025, All rights reserved.
from __future__ import annotations
from dsviper import *
import os


def print_opcodes(opcodes, definitions):
    for opcode in opcodes:
        args = opcode.arguments(definitions)   
        print(opcode.type(), args)


defs = Definitions()
ns = NameSpace(ValueUUId.create(), "Demo")

d = TypeStructureDescriptor("Vector3")
d.add_field("x", Type.FLOAT)
d.add_field("y", Type.FLOAT)
d.add_field("z", Type.FLOAT)
t_Vector = defs.create_structure(ns, d)

d = TypeStructureDescriptor("Transform")
d.add_field("translation", t_Vector)
d.add_field("rotation", t_Vector)
t_Transform = defs.create_structure(ns , d)

d = TypeStructureDescriptor("SurfaceProperty")
d.add_field("name", ValueString("Name"))
d.add_field("transform", t_Transform)
t_SurfaceProperty = defs.create_structure(ns, d)

t_Surface = defs.create_concept(ns, "Surface")
a = defs.create_attachment(ns, "property", t_Surface, t_SurfaceProperty)

tr = Value.create(t_Transform)
tm = Value.create(t_Transform)

k = a.create_key()
o = a.create_document()
m = a.create_document()
m.name = "Plan"
m.transform.translation.x = 10
m.transform.rotation.z = 10

ms = CommitMutableState(CommitState(defs.const()))
mu = ms.attachment_mutating()
mu.set(a, k, o)
mu.diff(a, k, m, recursive=True)

print_opcodes(ms.mutations().all_opcodes(), defs.const())

from __future__ import annotations
from dsviper import *

key, attachment, path = inspect_selection()
if key and attachment and path:
    if d := store.attachment_getting().get(attachment, key):
        v = path.at(d.unwrap())
        print(v)


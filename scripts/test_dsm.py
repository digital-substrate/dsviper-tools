from __future__ import annotations
from dsviper import *
import os


REPOS = os.path.expanduser("~/dsm-samples")
PATHNAME = f"{REPOS}/Re"
#PATHNAME = f"{REPOS}/Ge"

report, dsm_defs, defs = DSMBuilder.assemble(PATHNAME).parse()

if report.has_error():
    for error in report.errors():
        print(error)

print(defs.to_dsm_definitions().to_dsm())

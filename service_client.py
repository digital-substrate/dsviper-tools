from dsviper import Definitions
from dsviper import ServiceRemote, CommitState, CommitMutableState

defs = Definitions()
s = ServiceRemote.connect("localhost", "54328", defs)

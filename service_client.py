from dsviper import Definitions
from dsviper import ServiceRemote

defs = Definitions()
s = ServiceRemote.connect("localhost", "54328", defs)

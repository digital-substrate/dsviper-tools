from __future__ import annotations
from dsviper import *
import os

FILENAME = os.path.expanduser("~/Databases/Raptor/test-sync.rapmc")
if os.path.exists(FILENAME):
    os.remove(FILENAME)

source = CommitDatabaseRemote.connect("localhost", "54321")

target = CommitDatabase.create_in_memory()
#target = CommitDatabase.create(FILENAME)

cs = CommitSynchronizer(source.commit_databasing(), target.commit_databasing())
logger = LoggerConsole()
cs.sync(logger.logging())
source.close()
target.close()



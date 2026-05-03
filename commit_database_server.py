#!/usr/bin/env python3
from __future__ import annotations
import argparse, os
import signal

from dsviper import Cancelation, CommitDatabase, CommitDatabaseServer, LoggerConsole, LoggerNull, Logging, Socket

cancelation = Cancelation()
def signal_handler(sig, frame):
    print("Server cancelation requested...\n")
    cancelation.cancel()

signal.signal(signal.SIGINT, signal_handler)

parser = argparse.ArgumentParser()
parser.add_argument("-v", "--verbose", help="display activity", action="count")
parser.add_argument("--host", help="the host of the source", default="0.0.0.0")
parser.add_argument("--port", help="the port of the source if not defined 54321", type=int, default=54321)
parser.add_argument("--socket-path", help="the path to the socket of the source")
parser.add_argument('database', help='the Commit database')

args = parser.parse_args()

if not CommitDatabase.is_compatible(args.database):
    print("Not a Commit Database.")
    exit(0)

level = Logging.LEVEL_ALL
if args.verbose:
    if args.verbose == 1:
        level = Logging.LEVEL_CRITICAL
    elif args.verbose == 2:
        level = Logging.LEVEL_INFO
    else:
        level = Logging.LEVEL_DEBUG

logging = LoggerNull().logging()
if args.verbose:
    logging = LoggerConsole(level).logging()

socket: Socket | None = None
if args.socket_path:
    if os.path.exists(args.socket_path):
        os.remove(args.socket_path)
    socket = Socket.create_passive_local(args.socket_path)
else:
    socket = Socket.create_passive_inet(args.host, str(args.port))


server = CommitDatabaseServer(args.database, socket, logging, cancelation)
server.start()
while server.step():
    if cancelation.requested():
        break
server.finish()

print("The server finished gracefully.")

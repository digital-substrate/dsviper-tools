#!/usr/bin/env python3
from __future__ import annotations
import argparse
import time
import os
from dsviper import CommitDatabasing, CommitDatabase, CommitDatabaseHelper, CommitSynchronizer
from dsviper import LoggerConsole, LoggerNull, Logging


def check_databasing_args(args):
    if args.database is None and args.host is None and args.socket_path is None:
        print(f'use option --database, --host or --socket-path to specify the source')
        exit(1)


def source_commit_databasing(args) -> CommitDatabasing:
    """Create the concrete Type that implements CommitDatabasing based on command line options"""
    if args.database:
        db = CommitDatabase.open(os.path.expanduser(args.database))
        description = args.database
    elif args.socket_path:
        db = CommitDatabase.connect_local(args.socket_path)
        description = args.socket_path
    else:
        db = CommitDatabase.connect(args.host, str(args.port))
        description = f'{args.host}:{args.port}'
    if args.verbose:
        print(f'Server: {description}')

    return db.commit_databasing()


def check_commit_databasing(args) -> CommitDatabasing:
    check_databasing_args(args)
    return source_commit_databasing(args)


# reset sub command
def reset_main(args):
    commit_databasing = check_commit_databasing(args)
    commit_databasing.reset_commits()
    commit_databasing.close()


# reduce_heads sub command
def reduce_head_main(args):
    commit_databasing = check_commit_databasing(args)
    db = CommitDatabase(commit_databasing)

    if args.loop:
        while True:
            CommitDatabaseHelper.reduce_heads(db)
            time.sleep(args.update_interval)
    else:
        CommitDatabaseHelper.reduce_heads(db)

    db.close()


# sync sub command
def sync_main(args):
    commit_databasing = check_commit_databasing(args)

    filename = os.path.expanduser(args.file)
    if os.path.exists(filename):
        db = CommitDatabase.open(filename)
    else:
        db = CommitDatabase.create(filename, documentation=commit_databasing.documentation())

    blob_data_size = args.blob_data_size * 1024 * 1024
    synchronizer = CommitSynchronizer(commit_databasing, db.commit_databasing(), "Sync", blob_data_size)

    if args.verbose:
        if args.verbose == 1:
            level = Logging.LEVEL_CRITICAL
        elif args.verbose == 2:
            level = Logging.LEVEL_INFO
        else:
            level = Logging.LEVEL_DEBUG
        logger = LoggerConsole(level)
    else:
        logger = LoggerNull()

    if args.loop:
        while True:
            synchronizer.sync(logger.logging())
            time.sleep(args.update_interval)
    else:
        synchronizer.sync(logger.logging())

    db.close()
    commit_databasing.close()


# main parser and common parameters
parser = argparse.ArgumentParser()
parser.add_argument("-v", "--verbose", help="display activity", action="count")
parser.add_argument("--database", help="the database used as the source")
parser.add_argument("--host", help="the host of the source")
parser.add_argument("--port", help="the port of the source if not 54321", type=int, default=54321)
parser.add_argument("--socket-path", help="the path to the socket of the source")

# we always use a sub command
subparsers = parser.add_subparsers(help='sub-command help', required=False)

# sub command 'reset' parser and entry point
parser_reset = subparsers.add_parser('reset', help="Reset the content of the source to its first commit")
parser_reset.set_defaults(func=reset_main)

# sub command 'reduce_heads' parser, specific arguments and entry point
parser_reduce_heads = subparsers.add_parser('reduce_heads',
                                            help='Reduce to a single head by iteratively merging heads, starting from the last_commit_id')
parser_reduce_heads.add_argument("--loop", help="reduce forever", action="store_true")
parser_reduce_heads.add_argument("--update-interval", help="the update interval in sec for the loop mode",
                                 type=float,
                                 default=2)
parser_reduce_heads.set_defaults(func=reduce_head_main)

# sub command 'sync' parser, specifics arguments and entry point
parser_sync = subparsers.add_parser('sync',
                                    help='Synchronize the content of a local database (destination) file with the source')
parser_sync.add_argument("file")
parser_sync.add_argument("--loop", help="sync forever", action="store_true")
parser_sync.add_argument("--update-interval", help="the update interval in sec for the loop mode", type=int, default=5)
parser_sync.add_argument("--blob-data-size", help="the max size of packed blob in Mo.", type=int, default=25)
parser_sync.set_defaults(func=sync_main)

# parse arguments
arguments = parser.parse_args()

# display help if no sub command
if not hasattr(arguments, 'func'):
    parser.print_help()
    exit(1)
else:
    arguments.func(arguments)
    exit(0)

# Usage
# ./commit_admin.py --database ~/Databases/Raptor/01_perceuse.rapmc reset
# ./commit_admin.py --database ~/Databases/Raptor/01_perceuse.rapmc reduce_heads --loop --update-interval 5
# ./commit_admin.py --database ~/Databases/Raptor/01_perceuse_SVR.rapmc sync ~/Databases/Raptor/01_perceuse.rapmc --loop --update-interval 2

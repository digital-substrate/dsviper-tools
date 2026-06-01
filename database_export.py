#!/usr/bin/env python3
from __future__ import annotations
import argparse
import json
import os
import re
import sys

from dsviper import (
    Database,
    CommitDatabase,
    AttachmentGetting,
    DefinitionsConst,
    Value,
    ValueCommitId,
)


CHUNK_SIZE = 48 * 1024 * 1024


def encoded(value):
    return str(value.encoded())


def iter_blob_chunks(handle, blob_id, total_size):
    offset = 0
    while offset < total_size:
        count = min(CHUNK_SIZE, total_size - offset)
        yield bytes(handle.read_blob(blob_id, count, offset))
        offset += count


class Source:
    def __init__(self, kind, handle, definitions, attachment_getting, commit_id=None):
        self.kind = kind
        self.handle = handle
        self.definitions: DefinitionsConst = definitions
        self.attachment_getting: AttachmentGetting = attachment_getting
        self.commit_id = commit_id

    def close(self):
        self.handle.close()


def resolve_commit_id(cdb, requested):
    if requested is None:
        heads = sorted(encoded(c) for c in cdb.head_commit_ids())
        print("This is a CommitDatabase: --commit-id is required.", file=sys.stderr)
        print("Use 'last', 'first', or one of the available commit ids:", file=sys.stderr)
        for h in heads:
            print(f"  {h}", file=sys.stderr)
        sys.exit(1)

    if requested == "last":
        commit_id = cdb.last_commit_id()
    elif requested == "first":
        commit_id = cdb.first_commit_id()
    else:
        commit_id = ValueCommitId.try_parse(requested)

    if commit_id is None or not commit_id.is_valid() or not cdb.commit_exists(commit_id):
        print(f"Unknown or invalid commit id: {requested}", file=sys.stderr)
        sys.exit(1)

    return commit_id


def open_source(args):
    path = os.path.expanduser(args.database)
    if not os.path.exists(path):
        print(f"No such file: {path}", file=sys.stderr)
        sys.exit(1)

    if CommitDatabase.is_compatible(path):
        cdb = CommitDatabase.open(path, readonly=True)
        commit_id = resolve_commit_id(cdb, args.commit_id)
        state = cdb.state(commit_id)
        return Source(
            kind="CommitDatabase",
            handle=cdb,
            definitions=state.definitions(),
            attachment_getting=state.attachment_getting(),
            commit_id=commit_id,
        )

    if Database.is_compatible(path):
        if args.commit_id is not None:
            print("--commit-id is ignored for a plain Database.", file=sys.stderr)
        db = Database.open(path, readonly=True)
        return Source(
            kind="Database",
            handle=db,
            definitions=db.definitions(),
            attachment_getting=db.attachment_getting(),
        )

    print(f"Not a dsviper Database or CommitDatabase: {path}", file=sys.stderr)
    sys.exit(1)


def export_definitions(source):
    return json.loads(source.definitions.to_dsm_definitions().json_encode())


def export_documents(source):
    documents = {}
    total = 0
    for attachment in source.definitions.attachments():
        entries = []
        for key, document in source.attachment_getting.enumerate(attachment, encoded=False):
            entries.append({
                "key": json.loads(Value.json_encode(key)),
                "document": json.loads(Value.json_encode(document)),
            })
        documents[attachment.identifier()] = entries
        total += len(entries)
    return documents, total


def export_blob_index(source):
    index = []
    for blob_id in source.handle.blob_ids():
        info = source.handle.blob_info(blob_id)
        index.append({
            "id": encoded(blob_id),
            "layout": info.blob_layout().representation(),
            "size": info.size(),
            "chunked": info.chunked(),
        })
    index.sort(key=lambda entry: entry["id"])
    return index


def build_manifest(source, document_count, blob_index):
    handle = source.handle
    manifest = {
        "source_type": source.kind,
        "path": handle.path(),
        "uuid": encoded(handle.uuid()),
        "documentation": handle.documentation(),
        "codec": handle.codec_name(),
        "definitions_hexdigest": handle.definitions_hexdigest(),
        "commit_id": encoded(source.commit_id) if source.commit_id else None,
        "counts": {
            "attachments": len(source.definitions.attachments()),
            "documents": document_count,
            "blobs": len(blob_index),
        },
    }
    return manifest


def safe_name(identifier):
    return re.sub(r"[^A-Za-z0-9._-]+", "_", identifier)


def write_bundle(source, args, manifest, definitions, documents, blob_index):
    out_dir = os.path.expanduser(args.output) if args.output else _default_dir(source)
    os.makedirs(out_dir, exist_ok=True)
    documents_dir = os.path.join(out_dir, "documents")
    blobs_dir = os.path.join(out_dir, "blobs")
    os.makedirs(documents_dir, exist_ok=True)
    os.makedirs(blobs_dir, exist_ok=True)

    _dump_json(os.path.join(out_dir, "manifest.json"), manifest, args.indent)
    _dump_json(os.path.join(out_dir, "definitions.json"), definitions, args.indent)

    for identifier, entries in documents.items():
        _dump_json(os.path.join(documents_dir, f"{safe_name(identifier)}.json"), entries, args.indent)

    _dump_json(os.path.join(blobs_dir, "index.json"), blob_index, args.indent)
    blob_ids = {encoded(b): b for b in source.handle.blob_ids()}
    for entry in blob_index:
        with open(os.path.join(blobs_dir, f"{entry['id']}.bin"), "wb") as blob_file:
            for chunk in iter_blob_chunks(source.handle, blob_ids[entry["id"]], entry["size"]):
                blob_file.write(chunk)

    if args.verbose:
        print(f"Wrote bundle to {out_dir}")


def _default_dir(source):
    base = os.path.basename(source.handle.path()) or encoded(source.handle.uuid())
    stem = os.path.splitext(base)[0] or "database"
    if source.commit_id:
        stem = f"{stem}.{encoded(source.commit_id)[:12]}"
    return f"{stem}.export"


def _dump_json(path, value, indent):
    with open(path, "w", encoding="utf-8") as handle:
        json.dump(value, handle, indent=indent, ensure_ascii=False)
        handle.write("\n")


def main():
    parser = argparse.ArgumentParser(
        description="Export a dsviper Database or CommitDatabase to JSON "
                    "(embedded definitions, documents per attachment, blobs with layouts).")
    parser.add_argument("database", help="path to the .db / commit-database file")
    parser.add_argument("--commit-id", help="commit id to export (or 'last' / 'first'); "
                                            "required for a CommitDatabase")
    parser.add_argument("--output", help="output directory; defaults to '<name>.export'")
    parser.add_argument("--indent", type=int, default=2, help="JSON indentation (default 2)")
    parser.add_argument("-v", "--verbose", action="store_true", help="report what was written")
    args = parser.parse_args()

    source = open_source(args)
    try:
        definitions = export_definitions(source)
        documents, document_count = export_documents(source)
        blob_index = export_blob_index(source)
        manifest = build_manifest(source, document_count, blob_index)
        write_bundle(source, args, manifest, definitions, documents, blob_index)
    finally:
        source.close()


if __name__ == "__main__":
    main()

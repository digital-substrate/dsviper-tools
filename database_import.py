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
    CommitState,
    CommitMutableState,
    DSMDefinitions,
    BlobLayout,
    Value,
    ValueBlob,
    ValueBlobId,
)


CHUNK_SIZE = 48 * 1024 * 1024


def fail(message):
    print(message, file=sys.stderr)
    sys.exit(1)


def read_json(path):
    with open(path, encoding="utf-8") as handle:
        return json.load(handle)


def safe_name(identifier):
    return re.sub(r"[^A-Za-z0-9._-]+", "_", identifier)


def load_manifest(bundle):
    path = os.path.join(bundle, "manifest.json")
    if not os.path.exists(path):
        fail(f"Not an export bundle (missing manifest.json): {bundle}")
    return read_json(path)


def load_definitions(bundle, fmt):
    if fmt == "xml":
        path = os.path.join(bundle, "definitions.xml")
        if not os.path.exists(path):
            fail(f"Not an export bundle (missing definitions.xml): {bundle}")
        with open(path, encoding="utf-8") as handle:
            return DSMDefinitions.from_xml_string(handle.read()).to_definitions().const()

    path = os.path.join(bundle, "definitions.json")
    if not os.path.exists(path):
        fail(f"Not an export bundle (missing definitions.json): {bundle}")
    with open(path, encoding="utf-8") as handle:
        return DSMDefinitions.json_decode(handle.read()).to_definitions().const()


def load_blob_index(bundle):
    path = os.path.join(bundle, "blobs", "index.json")
    return read_json(path) if os.path.exists(path) else []


def import_blobs(store, bundle, blob_index, verbose):
    blobs_dir = os.path.join(bundle, "blobs")
    for entry in blob_index:
        blob_id = ValueBlobId.try_parse(entry["id"])
        if blob_id is None or not blob_id.is_valid():
            fail(f"Invalid blob id in index: {entry['id']}")
        layout = BlobLayout.parse(entry["layout"])
        size = entry["size"]
        path = os.path.join(blobs_dir, f"{entry['id']}.bin")
        if not os.path.exists(path):
            fail(f"Missing blob payload: {path}")
        actual = os.path.getsize(path)
        if actual != size:
            fail(f"Blob {entry['id']} size mismatch: index says {size}, file is {actual}")

        with open(path, "rb") as blob_file:
            if size <= CHUNK_SIZE:
                stored = store.create_blob(blob_id, layout, ValueBlob(blob_file.read()))
            else:
                store.create_zero_blob(blob_id, layout, size)
                offset = 0
                while offset < size:
                    chunk = blob_file.read(CHUNK_SIZE)
                    store.write_blob(blob_id, ValueBlob(chunk), offset)
                    offset += len(chunk)
                stored = store.freeze_blob(blob_id)

        if not stored:
            fail(f"Failed to store blob {entry['id']}")

    if verbose:
        print(f"Imported {len(blob_index)} blobs")


def import_documents(definitions, bundle, set_document, verbose, fmt):
    documents_dir = os.path.join(bundle, "documents")
    total = 0
    for attachment in definitions.attachments():
        path = os.path.join(documents_dir, f"{safe_name(attachment.identifier())}.json")
        if not os.path.exists(path):
            continue
        for entry in read_json(path):
            if fmt == "xml":
                key = Value.from_xml_string(entry["key"], attachment.type_key(), definitions)
                document = Value.from_xml_string(entry["document"], attachment.document_type(), definitions)
            else:
                key = Value.json_decode(json.dumps(entry["key"]), attachment.type_key(), definitions)
                document = Value.json_decode(json.dumps(entry["document"]), attachment.document_type(), definitions)
            set_document(attachment, key, document)
            total += 1
    if verbose:
        print(f"Imported {total} documents")
    return total


def import_into_database(output, documentation, definitions, bundle, blob_index, verbose, fmt):
    db = Database.create(output, documentation=documentation)
    try:
        db.extend_definitions(definitions)
        live = db.definitions()
        db.begin_transaction()
        import_blobs(db.databasing(), bundle, blob_index, verbose)
        count = import_documents(live, bundle, db.set, verbose, fmt)
        db.commit()
    except BaseException:
        if db.in_transaction():
            db.rollback()
        raise
    finally:
        hexdigest = db.definitions_hexdigest()
        db.close()
    return count, hexdigest


def import_into_commit_database(output, documentation, definitions, bundle, blob_index, label, verbose, fmt):
    cdb = CommitDatabase.create(output, documentation=documentation)
    try:
        cdb.extend_definitions(definitions)
        live = cdb.definitions()
        store = cdb.commit_databasing()
        store.begin_transaction()
        import_blobs(store, bundle, blob_index, verbose)
        store.commit()
        mutable = CommitMutableState(CommitState(live))
        count = import_documents(live, bundle, mutable.attachment_mutating().set, verbose, fmt)
        cdb.commit_mutations(label, mutable)
    finally:
        hexdigest = cdb.definitions_hexdigest()
        cdb.close()
    return count, hexdigest


def verify(manifest, document_count, blob_index, hexdigest):
    counts = manifest.get("counts", {})
    expected_documents = counts.get("documents")
    if expected_documents is not None and expected_documents != document_count:
        print(f"Warning: document count mismatch (manifest {expected_documents}, imported {document_count}).",
              file=sys.stderr)
    expected_blobs = counts.get("blobs")
    if expected_blobs is not None and expected_blobs != len(blob_index):
        print(f"Warning: blob count mismatch (manifest {expected_blobs}, imported {len(blob_index)}).",
              file=sys.stderr)
    expected_digest = manifest.get("definitions_hexdigest")
    if expected_digest and expected_digest != hexdigest:
        print(f"Warning: definitions hexdigest mismatch (manifest {expected_digest}, imported {hexdigest}).",
              file=sys.stderr)


def main():
    parser = argparse.ArgumentParser(
        description="Import a JSON export bundle (produced by database_export.py) "
                    "into a new dsviper Database or CommitDatabase, preserving blob ids.")
    parser.add_argument("bundle", help="path to the export bundle directory")
    parser.add_argument("output", help="path of the Database / CommitDatabase file to create")
    parser.add_argument("--as", dest="target_kind", choices=["database", "commit-database"],
                        help="target type (default: match the source type recorded in the bundle)")
    parser.add_argument("--label", default="import",
                        help="commit label when creating a CommitDatabase (default 'import')")
    parser.add_argument("--documentation",
                        help="override the documentation stored in the new artefact")
    parser.add_argument("--force", action="store_true", help="overwrite the output file if it exists")
    parser.add_argument("-v", "--verbose", action="store_true", help="report what was imported")
    args = parser.parse_args()

    bundle = os.path.expanduser(args.bundle)
    if not os.path.isdir(bundle):
        fail(f"No such bundle directory: {bundle}")

    output = os.path.expanduser(args.output)
    if os.path.exists(output):
        if not args.force:
            fail(f"Output already exists (use --force to overwrite): {output}")
        os.remove(output)

    manifest = load_manifest(bundle)
    fmt = manifest.get("format", "json")
    if fmt == "xml" and not hasattr(Value, "from_xml_string"):
        fail("bundle is in XML format but the installed dsviper lacks XML support (requires dsviper >= 1.2.19).")
    definitions = load_definitions(bundle, fmt)
    blob_index = load_blob_index(bundle)

    kind = args.target_kind or (
        "commit-database" if manifest.get("source_type") == "CommitDatabase" else "database")
    documentation = args.documentation if args.documentation is not None else (manifest.get("documentation") or None)

    if kind == "commit-database":
        count, hexdigest = import_into_commit_database(
            output, documentation, definitions, bundle, blob_index, args.label, args.verbose, fmt)
        label = "CommitDatabase"
    else:
        count, hexdigest = import_into_database(
            output, documentation, definitions, bundle, blob_index, args.verbose, fmt)
        label = "Database"

    verify(manifest, count, blob_index, hexdigest)

    if args.verbose:
        print(f"Wrote {label} to {output} "
              f"({count} documents, {len(blob_index)} blobs)")


if __name__ == "__main__":
    main()

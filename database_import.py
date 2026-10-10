#!/usr/bin/env python3
from __future__ import annotations
import argparse
import json
import os
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


def plan_documents(definitions, bundle, manifest):
    """[(runtime id, entries)] for every documents file of the bundle, or fail before anything is
    written: a file no attachment claims, or a count the manifest does not state, is data lost.

    A bundle lists its attachments by runtime id, the identity that holds across runtime
    versions; an identifier is a name, and `App::Lib::User.profile` was `Lib::User.profile`
    before dsviper 1.2.30."""
    described = manifest.get("attachments")
    if described is None:
        fail("This bundle does not list its attachments: dsviper-tools 1.2.0 wrote it. "
             "Export the database again with this database_export.")
    documents_dir = os.path.join(bundle, "documents")
    present = sorted(f for f in os.listdir(documents_dir) if f.endswith(".json")) \
        if os.path.isdir(documents_dir) else []
    claimed = []
    by_runtime_id = {entry["runtime_id"]: entry for entry in described}
    for attachment in definitions.attachments():
        entry = by_runtime_id.pop(runtime_id(attachment), None)
        if entry is not None:
            claimed.append((attachment, entry["file"]))
    if by_runtime_id:
        fail("The bundle lists attachments its definitions do not hold: "
             + ", ".join(sorted(e["identifier"] for e in by_runtime_id.values())))

    orphans = sorted(set(present) - {name for _, name in claimed})
    if orphans:
        fail("Documents no attachment of the bundle's definitions claims: " + ", ".join(orphans) + ".")

    plan = [(runtime_id(attachment), read_json(os.path.join(documents_dir, name))) for attachment, name in claimed]
    count = sum(len(entries) for _, entries in plan)
    expected = manifest.get("counts", {}).get("documents")
    if expected is not None and expected != count:
        fail(f"The bundle holds {count} documents, its manifest states {expected}.")
    return plan


def runtime_id(attachment):
    return str(attachment.runtime_id().encoded())


def import_documents(definitions, plan, set_document, verbose, fmt):
    attachments = {runtime_id(attachment): attachment for attachment in definitions.attachments()}
    total = 0
    for attachment_runtime_id, entries in plan:
        attachment = attachments[attachment_runtime_id]
        for entry in entries:
            if fmt == "xml":
                key = Value.from_xml_string(entry["key"], attachment.type_key(), definitions)
                document = Value.from_xml_string(entry["document"], attachment.document_type(), definitions)
            else:
                key = Value.json_decode(entry["key"], attachment.type_key(), definitions)
                document = Value.json_decode(entry["document"], attachment.document_type(), definitions)
            set_document(attachment, key, document)
            total += 1
    if verbose:
        print(f"Imported {total} documents")
    return total


def import_into_database(output, documentation, definitions, bundle, plan, blob_index, verbose, fmt):
    db = Database.create(output, documentation=documentation)
    try:
        db.extend_definitions(definitions)
        live = db.definitions()
        db.begin_transaction()
        import_blobs(db.databasing(), bundle, blob_index, verbose)
        count = import_documents(live, plan, db.set, verbose, fmt)
        db.commit()
    except BaseException:
        if db.in_transaction():
            db.rollback()
        raise
    finally:
        hexdigest = db.definitions_hexdigest()
        db.close()
    return count, hexdigest


def import_into_commit_database(output, documentation, definitions, bundle, plan, blob_index, label, verbose, fmt):
    cdb = CommitDatabase.create(output, documentation=documentation)
    try:
        cdb.extend_definitions(definitions)
        live = cdb.definitions()
        store = cdb.commit_databasing()
        store.begin_transaction()
        import_blobs(store, bundle, blob_index, verbose)
        store.commit()
        mutable = CommitMutableState(CommitState(live))
        count = import_documents(live, plan, mutable.attachment_mutating().set, verbose, fmt)
        cdb.commit_mutations(label, mutable)
    finally:
        hexdigest = cdb.definitions_hexdigest()
        cdb.close()
    return count, hexdigest


def verify(manifest, blob_index, hexdigest):
    counts = manifest.get("counts", {})
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

    manifest = load_manifest(bundle)
    fmt = manifest.get("format", "json")
    if fmt == "xml" and not hasattr(Value, "from_xml_string"):
        fail("bundle is in XML format but the installed dsviper lacks XML support (requires dsviper >= 1.2.19).")
    definitions = load_definitions(bundle, fmt)
    blob_index = load_blob_index(bundle)
    plan = plan_documents(definitions, bundle, manifest)

    output = os.path.expanduser(args.output)
    if os.path.exists(output):
        if not args.force:
            fail(f"Output already exists (use --force to overwrite): {output}")
        os.remove(output)

    kind = args.target_kind or (
        "commit-database" if manifest.get("source_type") == "CommitDatabase" else "database")
    documentation = args.documentation if args.documentation is not None else (manifest.get("documentation") or None)

    if kind == "commit-database":
        count, hexdigest = import_into_commit_database(
            output, documentation, definitions, bundle, plan, blob_index, args.label, args.verbose, fmt)
        label = "CommitDatabase"
    else:
        count, hexdigest = import_into_database(
            output, documentation, definitions, bundle, plan, blob_index, args.verbose, fmt)
        label = "Database"

    verify(manifest, blob_index, hexdigest)

    if args.verbose:
        print(f"Wrote {label} to {output} "
              f"({count} documents, {len(blob_index)} blobs)")


if __name__ == "__main__":
    main()

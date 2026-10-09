#!/usr/bin/env python3
"""database_export and database_import: a bundle gives back every document it holds, or nothing.

A bundle lists its attachments by runtime id. The identifier is a name, and its spelling
changed with dsviper 1.2.30 (`App::Lib::User.profile` for an attachment of `App` keyed by
`Lib::User`, `Lib::User.profile` before): matched by name, a bundle exported by one version and
imported by the other dropped those documents with a warning. The import refuses a file no
attachment claims, a count the manifest does not state, or a bundle without the list, before it
writes anything.

Run from the repository root: python3 -m unittest discover -s tests
"""

import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest

from dsviper import Database, DSMBuilder

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SOURCE = ("namespace Lib {00000000-0000-0000-0000-0000000000a1} {"
          " concept User; struct P { int64 a; double d; }; attachment<User, P> card; };"
          " namespace App {00000000-0000-0000-0000-0000000000a3} {"
          " struct Q { string s; }; attachment<Lib::User, Q> profile; };")


def run(tool, *args):
    return subprocess.run([sys.executable, os.path.join(ROOT, tool), *args], capture_output=True, text=True)


class TestBundle(unittest.TestCase):

    def setUp(self):
        self.dir = tempfile.mkdtemp(prefix="bundle-")
        self.db = os.path.join(self.dir, "source.db")
        builder = DSMBuilder()
        builder.append("model.dsm", SOURCE)
        report, _, definitions = builder.parse()
        self.assertFalse(report.has_error())
        assert definitions is not None
        db = Database.create(self.db)
        db.extend_definitions(definitions)
        live = db.definitions()
        card = next(a for a in live.attachments() if a.identifier() == "Lib::User.card")
        db.begin_transaction()
        for _ in range(2):
            key = card.create_key()
            for attachment in live.attachments():
                db.set(attachment, key, attachment.create_document())
        db.commit()
        db.close()
        self.bundle = os.path.join(self.dir, "bundle")
        exported = run("database_export.py", self.db, "--output", self.bundle)
        self.assertEqual(0, exported.returncode, exported.stderr)
        with open(os.path.join(self.bundle, "manifest.json"), encoding="utf-8") as handle:
            self.manifest = json.load(handle)

    def tearDown(self):
        shutil.rmtree(self.dir)

    def imported(self, name="out.db"):
        output = os.path.join(self.dir, name)
        return run("database_import.py", self.bundle, output, "-v"), output

    def rewrite_manifest(self, manifest):
        with open(os.path.join(self.bundle, "manifest.json"), "w", encoding="utf-8") as handle:
            json.dump(manifest, handle)

    def test_the_manifest_lists_each_attachment_by_runtime_id(self):
        described = self.manifest["attachments"]
        self.assertEqual(2, len(described))
        for entry in described:
            self.assertEqual({"runtime_id", "identifier", "file"}, set(entry))
            self.assertTrue(os.path.exists(os.path.join(self.bundle, "documents", entry["file"])))

    def test_a_document_is_the_text_viper_wrote(self):
        entry = self.manifest["attachments"][0]
        with open(os.path.join(self.bundle, "documents", entry["file"]), encoding="utf-8") as handle:
            documents = json.load(handle)
        self.assertIsInstance(documents[0]["key"], str)
        self.assertIsInstance(documents[0]["document"], str)

    def test_every_document_comes_back(self):
        result, _ = self.imported()
        self.assertEqual(0, result.returncode, result.stderr)
        self.assertIn("Imported 4 documents", result.stdout)

    def test_a_file_named_otherwise_is_found_by_runtime_id(self):
        entry = self.manifest["attachments"][1]
        documents = os.path.join(self.bundle, "documents")
        os.rename(os.path.join(documents, entry["file"]), os.path.join(documents, "renamed.json"))
        entry["file"] = "renamed.json"
        self.rewrite_manifest(self.manifest)
        result, _ = self.imported()
        self.assertEqual(0, result.returncode, result.stderr)
        self.assertIn("Imported 4 documents", result.stdout)

    def test_a_file_no_attachment_claims_is_refused_before_writing(self):
        with open(os.path.join(self.bundle, "documents", "Other_User.profile.json"), "w", encoding="utf-8") as handle:
            handle.write("[]")
        result, output = self.imported()
        self.assertEqual(1, result.returncode)
        self.assertIn("Other_User.profile.json", result.stderr)
        self.assertFalse(os.path.exists(output))

    def test_a_count_the_manifest_does_not_state_is_refused(self):
        self.manifest["counts"]["documents"] = 5
        self.rewrite_manifest(self.manifest)
        result, output = self.imported()
        self.assertEqual(1, result.returncode)
        self.assertIn("holds 4 documents, its manifest states 5", result.stderr)
        self.assertFalse(os.path.exists(output))

    def test_a_bundle_without_its_attachment_list_is_refused(self):
        """dsviper-tools 1.2.0 wrote bundles without it."""
        del self.manifest["attachments"]
        self.rewrite_manifest(self.manifest)
        result, output = self.imported()
        self.assertEqual(1, result.returncode)
        self.assertIn("Export the database again", result.stderr)
        self.assertFalse(os.path.exists(output))


if __name__ == "__main__":
    unittest.main()

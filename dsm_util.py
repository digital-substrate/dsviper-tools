#!/usr/bin/env python3
from __future__ import annotations
import argparse
import re
import subprocess
import os
import zlib
import base64
from pathlib import Path

from dsviper import DSMDefinitions, DSMBuilder, DSMParseReport, CommitDatabase, Database


def _latest_kibo_jar(jars):
    """Highest-versioned jar among `jars`, or None if none is named kibo-X.Y.Z.jar.

    Compared on the parsed (major, minor, patch) tuple: an alphabetical sort
    orders kibo-1.2.9.jar after kibo-1.2.11.jar and would pick the older jar
    whenever a target/ directory holds more than one build.
    """
    candidates = []
    for jar in jars:
        m = re.match(r"^kibo-(\d+)\.(\d+)\.(\d+)\.jar$", jar.name)
        if m:
            candidates.append(((int(m.group(1)), int(m.group(2)), int(m.group(3))), jar))
    return max(candidates)[1] if candidates else None


def _pack_line(templates):
    """The major version stamped in a template directory (`kibo-template-viper X.Y.Z`), or None."""
    for stg in sorted(Path(templates).rglob("*.stg")):
        m = re.search(r"kibo-template-viper (\d+)\.\d+\.\d+", stg.read_text(errors="replace"))
        if m:
            return int(m.group(1))
    return None


def resolve_kibo_1(args, target):
    """Set args.kibo and args.templates to kibo 1 and the 1.2 pack's `target` templates.

    create_python_package and create_node_package generate with the kibo 1 line only.
    They look, in order:

    1. --kibo / --templates, else the KIBO_JAR / KIBO_TEMPLATES environment variables
       (KIBO_TEMPLATES names the pack, `target` is appended).
    2. The DevKit ZIP: this file in tools/, kibo 1 in ../kibo-1/tools/kibo-1.*.jar and its
       templates in ../kibo-1/templates/<target>. The ZIP carries kibo 2 beside it, in
       ../kibo-2/, which generates through kibo-project instead.
    3. Sibling checkouts: ../kibo/target/kibo-1.*.jar and ../kibo-template-viper/<target>,
       which must be on the 1.2 line.

    A kibo 2 jar or a 2.x pack is refused: kibo 2 generates through kibo-project.
    """
    path_tools = Path(__file__).parent
    root = path_tools.parent
    sibling_root = root.parent if path_tools.name == "tools" else root
    kibo_2 = "kibo 2 generates through kibo-project (kibo-2/tools/kibo_project.py in the DevKit ZIP)."

    if not args.kibo:
        env_jar = os.environ.get("KIBO_JAR")
        if env_jar:
            args.kibo = Path(env_jar).resolve()
        else:
            jar = (_latest_kibo_jar((root / "kibo-1" / "tools").glob("kibo-1.*.jar"))
                   or _latest_kibo_jar((sibling_root / "kibo" / "target").glob("kibo-1.*.jar")))
            if not jar:
                print(f"kibo: no kibo 1 jar found. Tried {root}/kibo-1/tools/kibo-1.*.jar (DevKit ZIP) "
                      f"and {sibling_root}/kibo/target/kibo-1.*.jar (sibling checkout). "
                      f"Set KIBO_JAR to override. {kibo_2}")
                exit(1)
            args.kibo = jar.resolve()

    if not os.path.exists(args.kibo):
        print(f"kibo: {args.kibo} no such file")
        exit(1)
    if not re.match(r"^kibo-1\.\d+\.\d+\.jar$", Path(args.kibo).name):
        print(f"kibo: {args.kibo} is not a kibo 1 jar; {kibo_2}")
        exit(1)

    if not args.templates:
        env_templates = os.environ.get("KIBO_TEMPLATES")
        bundled = root / "kibo-1" / "templates" / target
        if env_templates:
            args.templates = (Path(env_templates) / target).resolve()
        elif bundled.exists():
            args.templates = bundled.resolve()
        else:
            args.templates = (sibling_root / "kibo-template-viper" / target).resolve()

    if not os.path.exists(args.templates):
        print(f"templates: {args.templates} no such directory")
        exit(1)
    line = _pack_line(args.templates)
    if line != 1:
        print(f"templates: {args.templates} is not a kibo-template-viper 1.2 pack "
              f"(stamped {line if line is not None else 'with no version'}); {kibo_2}")
        exit(1)

    print(f"* templates: {args.templates}")
    print(f'*      kibo: {args.kibo}')


def fatal_report_error(report: DSMParseReport, message: str):
    if report.has_error():
        print(message)
        print("parse errors detected in DSM Definitions.")
        print("use the sub-command check to display errors.")
        exit(1)


# check sub-command
def check_main(args):
    builder = DSMBuilder.assemble(args.input_dsm)
    report, dsm_definitions, _ = builder.parse()
    if report.has_error():
        for error in report.errors():
            print(error)
        return 1
    return 0


# encode sub-command
def encode_main(args):
    builder = DSMBuilder.assemble(args.input_dsm)
    report, dsm_definitions, _ = builder.parse()
    fatal_report_error(report, "can't encode dsm definitions.")
    with open(args.output_dsm_json, 'w') as file:
        file.write(dsm_definitions.json_encode())


# decode sub-command
def decode_main(args):
    with open(args.input_dsm_json, 'r') as file:
        dsm_definitions = DSMDefinitions.json_decode(file.read())
    with open(args.output_dsm, 'w') as file:
        file.write(dsm_definitions.to_dsm())


# create_commit_commit_database sub-command
def create_commit_database_main(args):
    builder = DSMBuilder.assemble(args.input_dsm)
    report, _, definitions = builder.parse()
    fatal_report_error(report, "can't create a database.")

    if os.path.exists(args.output_db) and args.force:
        os.remove(args.output_db)

    db = CommitDatabase.create(args.output_db, documentation=args.documentation)
    db.extend_definitions(definitions)
    db.close()


# create_database sub-command
def create_database_main(args):
    builder = DSMBuilder.assemble(args.input_dsm)
    report, _, definitions = builder.parse()
    fatal_report_error(report, "can't create a database.")

    if os.path.exists(args.output_db) and args.force:
        os.remove(args.output_db)

    db = Database.create(args.output_db, documentation=args.documentation)
    db.extend_definitions(definitions)
    db.close()


# module sub-command
def create_python_package(args):
    resolve_kibo_1(args, "python")

    builder = DSMBuilder.assemble(args.input_dsm)
    report, dsm_definitions, definitions = builder.parse()
    fatal_report_error(report, "can't create a python package")
    filename = os.path.basename(args.input_dsm).lower()
    module, extension = os.path.splitext(filename)

    # Create dsm.json
    dsm_json_filename = f'{module}.dsm.json'
    with open(dsm_json_filename, 'w') as file:
        file.write(dsm_definitions.json_encode())

    # Render Template
    cmd = ['java',
           '-jar', args.kibo,
           '-c', 'python',
           '-n', module,
           '-d', dsm_json_filename,
           '-t', f"{args.templates}/package",
           '-o', module]

    subprocess.run(cmd)

    blob = definitions.encode()
    string = base64.b64encode(zlib.compress(blob.encoded()))
    with open(f'{module}/resources.py', 'w') as file:
        file.write(f"B64_DEFINITIONS = {string}")

    if args.wheel and os.path.exists("pyproject.toml") == False:
        cmd = ['java',
               '-jar', args.kibo,
               '-q',
               '-c', 'python',
               '-n', module,
               '-d', dsm_json_filename,
               '-t', f"{args.templates}/wheel/pyproject.toml.stg",
               '-o', "."]

        subprocess.run(cmd)

    if os.path.exists(dsm_json_filename):
        os.remove(dsm_json_filename)


def create_node_package(args):
    # TypeScript / Node analogue of create_python_package. The Node package
    # reuses the same Kibo `python` converter pointed at the typescript/
    # template directory. Sources land in <module>/src; the package.json and
    # tsconfig.json land at <module>/.
    resolve_kibo_1(args, "typescript")

    builder = DSMBuilder.assemble(args.input_dsm)
    report, dsm_definitions, definitions = builder.parse()
    fatal_report_error(report, "can't create a node package")
    filename = os.path.basename(args.input_dsm).lower()
    module, extension = os.path.splitext(filename)

    # Create dsm.json
    dsm_json_filename = f'{module}.dsm.json'
    with open(dsm_json_filename, 'w') as file:
        file.write(dsm_definitions.json_encode())

    src = os.path.join(module, "src")

    # TypeScript sources -> <module>/src
    cmd = ['java',
           '-jar', args.kibo,
           '-c', 'python',
           '-n', module,
           '-d', dsm_json_filename,
           '-t', str(args.templates),
           '-o', src]

    subprocess.run(cmd)

    # package.json + tsconfig.json -> <module>/
    cmd = ['java',
           '-jar', args.kibo,
           '-c', 'python',
           '-n', module,
           '-d', dsm_json_filename,
           '-t', f"{args.templates}/project",
           '-o', module]

    subprocess.run(cmd)

    # Embed the definitions blob with the default codec (StreamTokenBinary).
    # That is exactly the codec the Node binding's Definitions.decode(blob)
    # assumes when none is given, so the generated definitions.ts decodes the
    # blob as-is. Do NOT zlib-compress it — definitions.ts base64-decodes the
    # string and feeds the bytes straight to Definitions.decode.
    blob = definitions.encode()
    string = base64.b64encode(blob.encoded()).decode("ascii")
    with open(os.path.join(src, 'resources.ts'), 'w') as file:
        file.write(f'export const B64_DEFINITIONS = "{string}";\n')

    if os.path.exists(dsm_json_filename):
        os.remove(dsm_json_filename)


# main parser and common parameters
parser = argparse.ArgumentParser()
# we always use a sub-command
subparsers = parser.add_subparsers(help='sub-command help', required=False)

# sub-command 'check' parser and entry point
parser_check = subparsers.add_parser('check', help="check DSM syntax")
parser_check.add_argument("input_dsm", help="the file or folder of DSM Definitions to parse.")
parser_check.set_defaults(func=check_main)

# sub-command 'encode' parser and entry point
parser_encode = subparsers.add_parser('encode', help="assemble, parse and encode the DSM Definitions to JSON (.dsm.json).")
parser_encode.add_argument("input_dsm", help="the file or the folder of DSM Definitions to parse.")
parser_encode.add_argument("output_dsm_json", help="the file to store the JSON representation (.dsm.json).")
parser_encode.set_defaults(func=encode_main)

# sub-command 'decode' parser and entry point
parser_decode = subparsers.add_parser('decode', help="decode and rewrite definitions in DSM language.")
parser_decode.add_argument("input_dsm_json", help="the file with JSON encoded definitions (.dsm.json).")
parser_decode.add_argument("output_dsm", help="the file to rewrite definitions in DSM language.")
parser_decode.set_defaults(func=decode_main)

# sub-command 'create_commit_database' parser and entry point
parser_create_commit_db = subparsers.add_parser('create_commit_database', help="Create an empty Commit Database")
parser_create_commit_db.add_argument("--force", help="remove the database.", action="store_true")
parser_create_commit_db.add_argument("--documentation", help="the documentation.", default="Not Documented")
parser_create_commit_db.add_argument("input_dsm", help="the file or the folder of DSM Definitions to parse.")
parser_create_commit_db.add_argument("output_db", help="the Commit Database to create.")
parser_create_commit_db.set_defaults(func=create_commit_database_main)

# sub-command 'create_database' parser and entry point
parser_create_store_db = subparsers.add_parser('create_database', help="Create an empty Database")
parser_create_store_db.add_argument("--force", help="remove the database.", action="store_true")
parser_create_store_db.add_argument("--documentation", help="the documentation.", default="Not Documented")
parser_create_store_db.add_argument("input_dsm", help="the file or the folder of DSM Definitions to parse.")
parser_create_store_db.add_argument("output_db", help="the Database to create.")
parser_create_store_db.set_defaults(func=create_database_main)

# sub-command 'create_python_package' parser and entry point
parser_module = subparsers.add_parser('create_python_package', help="create a python package")
parser_module.add_argument("--kibo", help="the jar file for kibo.")
parser_module.add_argument("--templates", help="the folder for python templates.")
parser_module.add_argument("--wheel", help="generate pyproject.toml only (does not build the wheel; run 'python -m build' afterwards).", action="store_true")
parser_module.add_argument("input_dsm", help="the file or the folder of DSM Definitions to parse.")
parser_module.set_defaults(func=create_python_package)

# sub-command 'create_node_package' parser and entry point
parser_node = subparsers.add_parser('create_node_package', help="create a TypeScript / Node package")
parser_node.add_argument("--kibo", help="the jar file for kibo.")
parser_node.add_argument("--templates", help="the folder for typescript templates.")
parser_node.add_argument("input_dsm", help="the file or the folder of DSM Definitions to parse.")
parser_node.set_defaults(func=create_node_package)

# parse arguments
arguments = parser.parse_args()

# display help if no sub-command
if not hasattr(arguments, 'func'):
    parser.print_help()
    exit(1)
else:
    result = arguments.func(arguments)
    exit(result if result is not None else 0)

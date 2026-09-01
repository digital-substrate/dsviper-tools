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
    # dsm_util.py supports two layouts:
    #
    # 1. DevKit ZIP (end user): jar bundled in tools/, templates one level
    #    up at templates/. This is what the zip ships.
    #
    # 2. Sibling-checkout (developer): the kibo repo and the
    #    kibo-template-viper repo are checked out as siblings of this
    #    repo under a common parent directory.
    #
    # KIBO_JAR / KIBO_TEMPLATES env vars override both. The bundled
    # layout is tried first because it matches the published zip.
    path_tools = Path(__file__).parent
    sibling_root = path_tools.parent.parent if path_tools.name == "tools" else path_tools.parent

    bundled_jar = _latest_kibo_jar(path_tools.glob("kibo-*.jar"))
    sibling_jar = _latest_kibo_jar((sibling_root / "kibo" / "target").glob("kibo-*.jar"))

    bundled_templates = path_tools.parent / "templates" / "python"
    sibling_templates = sibling_root / "kibo-template-viper" / "python"

    if not arguments.kibo:
        env_jar = os.environ.get("KIBO_JAR")
        if env_jar:
            arguments.kibo = Path(env_jar).resolve()
        elif bundled_jar:
            arguments.kibo = bundled_jar.resolve()
        elif sibling_jar:
            arguments.kibo = sibling_jar.resolve()
        else:
            print(f"'kibo: no jar found. Tried {path_tools}/kibo-*.jar (DevKit ZIP layout) "
                  f"and {sibling_root}/kibo/target/kibo-*.jar (sibling-checkout). "
                  f"Set KIBO_JAR to override.")
            exit(1)

    if not os.path.exists(arguments.kibo):
        print(f"'kibo: {arguments.kibo} no such file")
        exit(1)

    if not arguments.templates:
        env_templates = os.environ.get("KIBO_TEMPLATES")
        if env_templates:
            arguments.templates = (Path(env_templates) / "python").resolve()
        elif bundled_templates.exists():
            arguments.templates = bundled_templates.resolve()
        else:
            arguments.templates = sibling_templates.resolve()

    if not os.path.exists(arguments.templates):
        print(f"templates: {arguments.templates} no such directory")
        exit(1)

    print(f"* templates: {arguments.templates}")
    print(f'*      kibo: {arguments.kibo}')

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
    # template directory — no kibo engine change is required. Sources land
    # in <module>/src; the package.json and tsconfig.json land at <module>/.
    #
    # Layout / jar / template resolution mirror create_python_package (see
    # there for the DevKit ZIP vs sibling-checkout layouts).
    path_tools = Path(__file__).parent
    sibling_root = path_tools.parent.parent if path_tools.name == "tools" else path_tools.parent

    bundled_jar = _latest_kibo_jar(path_tools.glob("kibo-*.jar"))
    sibling_jar = _latest_kibo_jar((sibling_root / "kibo" / "target").glob("kibo-*.jar"))

    bundled_templates = path_tools.parent / "templates" / "typescript"
    sibling_templates = sibling_root / "kibo-template-viper" / "typescript"

    if not args.kibo:
        env_jar = os.environ.get("KIBO_JAR")
        if env_jar:
            args.kibo = Path(env_jar).resolve()
        elif bundled_jar:
            args.kibo = bundled_jar.resolve()
        elif sibling_jar:
            args.kibo = sibling_jar.resolve()
        else:
            print(f"'kibo: no jar found. Tried {path_tools}/kibo-*.jar (DevKit ZIP layout) "
                  f"and {sibling_root}/kibo/target/kibo-*.jar (sibling-checkout). "
                  f"Set KIBO_JAR to override.")
            exit(1)

    if not os.path.exists(args.kibo):
        print(f"'kibo: {args.kibo} no such file")
        exit(1)

    if not args.templates:
        env_templates = os.environ.get("KIBO_TEMPLATES")
        if env_templates:
            args.templates = (Path(env_templates) / "typescript").resolve()
        elif bundled_templates.exists():
            args.templates = bundled_templates.resolve()
        else:
            args.templates = sibling_templates.resolve()

    if not os.path.exists(args.templates):
        print(f"templates: {args.templates} no such directory")
        exit(1)

    print(f"* templates: {args.templates}")
    print(f'*      kibo: {args.kibo}')

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

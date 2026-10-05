# Changelog

All notable changes to this project are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

This application has its own version line, independent from the `dsviper`
runtime version (declared as a dependency in `requirements.txt`).

## [Unreleased]

### Changed

- **`create_python_package` and `create_node_package` find kibo 1 in the DevKit ZIP's
  `kibo-1/` folder** (`kibo-1/tools/kibo-1.*.jar`, `kibo-1/templates/`), where the ZIP
  now carries it beside kibo 2. They generate with kibo 1 and the 1.2 pack only: a kibo 2
  jar, or a pack stamped 2.x, is refused with a message pointing at kibo-project, instead
  of rendering a package that mixes the two lines. A sibling checkout must be on the 1.2
  line, or be named with `KIBO_JAR` / `KIBO_TEMPLATES`.

## [1.2.0] - 2026-06-17

First standalone release of the Database / CommitDatabase tooling (Qt Widgets):
`cdbe`, `dbe`, `commit-admin`, `commit-database-server`, `service-client`,
`database-export`, `database-import`, and `dsm-util`.

### Added
- GUI and CLI tools around a Database / CommitDatabase artefact.
- Runs on Python 3.10–3.14; requires dsviper >= 1.2.16.
- Independent version line (`_version.py`), reported via the application
  version and the About dialog, decoupled from the `dsviper` runtime.

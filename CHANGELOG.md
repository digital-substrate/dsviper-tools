# Changelog

All notable changes to this project are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

This application has its own version line, independent from the `dsviper`
runtime version (declared as a dependency in `requirements.txt`).

## [Unreleased]

### Deprecated

- **Generating with kibo 1** (`create_python_package`, `create_node_package`): kibo 1 is
  deprecated. It receives fixes only, for the life of the LTS-1.2 line; new projects
  generate with kibo 2 through kibo-project. Each generation says so on stderr, with the
  migration guide's address. The package it generates is unchanged.

### Changed

- Requires `dsviper >= 1.2.30`: the bundles find attachments by runtime id, and a set of ids
  comes back as a `ValueSet`.
- **One bundle format, the one `dsviper-node-tools` writes** (`bundle_version` 2): each key and
  document is the text Viper writes, and either tool reads the other's bundles. A bundle 1.2.0
  wrote is refused: export the database again. The 1.2.0 `database_import` stops on a version 2
  bundle's first document.
- **`create_python_package` and `create_node_package` find kibo 1 in the DevKit ZIP's
  `kibo-1/` folder** (`kibo-1/tools/kibo-1.*.jar`, `kibo-1/templates/`), where the ZIP
  now carries it beside kibo 2. They generate with kibo 1 and the 1.2 pack only: a kibo 2
  jar, or a pack stamped 2.x, is refused with a message pointing at kibo-project, instead
  of rendering a package that mixes the two lines. A sibling checkout must be on the 1.2
  line, or be named with `KIBO_JAR` / `KIBO_TEMPLATES`.

### Fixed

- **The commits view enables Delete on a head again**: it compared the method `commit_id`
  with the head ids instead of calling it, so the button never enabled (dsviper-components).
- **`database_import` gives back every document of a bundle, or refuses it.** It matched each
  attachment to its file by identifier, whose spelling dsviper 1.2.30 changed for an attachment
  keyed by another namespace's concept: a bundle exported by one version lost those documents
  in the other, with a warning. The manifest now lists the attachments by runtime id; a file no
  attachment claims, a document count the manifest does not state, or a bundle without that
  list stops the import before it writes anything.

## [1.2.0] - 2026-06-17

First standalone release of the Database / CommitDatabase tooling (Qt Widgets):
`cdbe`, `dbe`, `commit-admin`, `commit-database-server`, `service-client`,
`database-export`, `database-import`, and `dsm-util`.

### Added
- GUI and CLI tools around a Database / CommitDatabase artefact.
- Runs on Python 3.10–3.14; requires dsviper >= 1.2.16.
- Independent version line (`_version.py`), reported via the application
  version and the About dialog, decoupled from the `dsviper` runtime.

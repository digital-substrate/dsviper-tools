# Changelog

All notable changes to this project are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

This application has its own version line, independent from the `dsviper`
runtime version (declared as a dependency in `requirements.txt`).

## [Unreleased]

_No changes yet. Bug fixes for the next 1.2.x patch release will be listed here._

## [1.2.0] - 2026-06-17

First standalone release of the Database / CommitDatabase tooling (Qt Widgets):
`cdbe`, `dbe`, `commit-admin`, `commit-database-server`, `service-client`,
`database-export`, `database-import`, and `dsm-util`.

### Added
- GUI and CLI tools around a Database / CommitDatabase artefact.
- Runs on Python 3.10–3.14; requires dsviper >= 1.2.16.
- Independent version line (`_version.py`), reported via the application
  version and the About dialog, decoupled from the `dsviper` runtime.

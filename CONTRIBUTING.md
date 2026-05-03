# Contributing to dsviper-tools

Thanks for your interest in contributing.

## Reporting issues

Use [GitHub Issues](https://github.com/digital-substrate/dsviper-tools/issues) and pick the appropriate template (bug report or feature request).

## Submitting pull requests

1. Fork the repository and create a feature branch from `main`
2. Make your changes (see "Running locally" below)
3. After modifying any `*.ui` or `resources.qrc`, regenerate with `python3 dev/build.py`
4. Verify the tool you touched still launches and the flows you changed still work
5. Open a pull request with a clear description of what changed and why

## Running locally

Requires Python 3.14+ and PySide6.

```bash
pip install -r requirements.txt          # PySide6 and deps
pip install dsviper                      # Viper Python binding
```

The tools are run directly from the repo root:

```bash
python3 cdbe.py                       # CommitDatabase browser
python3 dbe.py                        # Database browser
python3 dsm_util.py module foo.dsm    # build a Database from a .dsm
python3 commit_admin.py …             # CommitDatabase administration
python3 commit_database_server.py …   # network service
python3 service_client.py …           # function-pool RPC client
```

## Architecture

Five entry points form one coherent workflow around a Database / CommitDatabase artefact:

```
dsm_util.py module foo.dsm     →   create a Database from your model
commit_database_server.py      →   expose it on the network
cdbe.py / dbe.py               →   inspect, browse, debug
commit_admin.py                →   administer (compaction, audit, …)
service_client.py              →   talk to function pools
```

Shared Qt Widgets (dialogs, views) live in [`dsviper-components`](https://github.com/digital-substrate/dsviper-components), vendored in-tree under `dsviper_components/`. The maintainer refreshes via `dev/sync_dsviper_components.py`; do not hand-edit.

## License

This project is licensed under the MIT License (see [LICENSE](LICENSE)). By submitting a pull request, you agree that your contribution is provided under the same license (inbound = outbound). No CLA is required.

# dsviper-tools

Tooling for the **Database / CommitDatabase** workflow of the dsviper
ecosystem. One repo, one wheel, all the things a Python developer
needs to design, host, browse, and administer a dsviper-driven
database.

## Documentation

Full documentation: https://docs.digitalsubstrate.io/dsviper-tools/

Part of the [DevKit ecosystem](https://docs.digitalsubstrate.io/).

## What's inside

```
dsviper-tools/
├── dsm_util.py                  # CLI: build a Database / package from a .dsm
├── cdbe.py                      # GUI: CommitDatabase browser (Qt)
├── dbe.py                       # GUI: Database browser (Qt)
├── commit_admin.py              # CLI: CommitDatabase administration
├── commit_database_server.py    # service: serve a CommitDatabase over the network
├── service_client.py            # CLI: function-pool RPC client
├── dsviper_components/          # Qt widgets and dialogs shared by cdbe/dbe
│                                # (*.ui sources + ui_*.py generated, both committed)
│                                # Source-of-truth: dsviper-components
│                                # — refreshed via dev/sync_dsviper_components.py
├── resources.qrc, images/       # Qt resource sources
├── resources_rc.py              # generated from resources.qrc (committed)
├── scripts/                     # ancillary scripts (demos, helpers)
├── dev/                         # dev-only tools (build.py, sync_*.py); not shipped
└── LICENSE
```

The five entry points form one coherent workflow around a Database /
CommitDatabase artefact:

```
dsm_util.py module foo.dsm     →   create a Database from your model
commit_database_server.py      →   expose it on the network
cdbe.py / dbe.py               →   inspect, browse, debug
commit_admin.py                →   administer (compaction, audit, …)
service_client.py              →   talk to function pools
```

## Running the tools

The scripts are run directly from the repo root:

```bash
python3 cdbe.py
python3 dbe.py
python3 dsm_util.py module foo.dsm
python3 commit_admin.py --database … reset
python3 commit_database_server.py --database … --port 54328
python3 service_client.py …
```

### Building a wheel from a `.dsm`

`dsm_util.py create_python_package --wheel foo.dsm` only **generates**
`pyproject.toml` — it does not build the wheel. The build step is
deliberately separate so you can pick your own builder:

```bash
python3 dsm_util.py create_python_package --wheel foo.dsm
pip install build       # one-off
python3 -m build        # produces dist/foo-*.whl
```

`build` / `setuptools` / `wheel` are therefore **not** in
`requirements.txt`: they are only needed if you actually want to package
the generated source tree, and the choice of build backend belongs to
the `wheel/pyproject.toml.stg` template in `kibo-template-viper`, not to
this repo.

Inside an extracted DevKit ZIP, the same scripts live under `tools/`:

```bash
python3 tools/cdbe.py
python3 tools/dsm_util.py module foo.dsm
```

## Regenerating UI

The Qt UI files are generated from sources kept in the repo:

| Source         | Tool          | Generated output                |
|----------------|---------------|---------------------------------|
| `resources.qrc`| `pyside6-rcc` | `resources_rc.py`               |
| `*.ui` (XML)   | `pyside6-uic` | `dsviper_components/ui_*.py`    |

The generated files are committed, so a fresh clone runs immediately
without a build step. After editing any `*.ui` or `resources.qrc`,
regenerate with:

```bash
python3 dev/build.py
```

To pull updates from the source repository
[`dsviper-components`](https://github.com/digital-substrate/dsviper-components)
(a maintenance task, not a contributor task):

```bash
python3 dev/sync_dsviper_components.py    # refresh dsviper_components/ from sibling
python3 dev/build.py                       # then regenerate ui_*.py / resources_rc.py
git diff dsviper_components resources_rc.py     # review the bump
```

`PySide6` is pinned in `requirements.txt` to guarantee that the
regenerated files are byte-for-byte reproducible across contributors.
Different `pyside6-uic` versions silently produce different output —
the pin is the discipline that keeps the repo free of phantom diffs.

## How `dsm_util.py` finds Kibo and templates

`dsm_util.py` resolves the Kibo jar and the surface templates in this
order:

1. `KIBO_JAR` / `KIBO_TEMPLATES` environment variables.
2. **Bundled (DevKit ZIP layout)**: `tools/kibo-*.jar` next to
   `dsm_util.py`, templates at `../templates/python`.
3. **Sibling-checkout (developer workstation)**:
   `../kibo/target/kibo-*.jar` and `../kibo-template-viper/python`.

Both layouts are supported so the same script works inside the DevKit
zip and on a fresh dev workstation that clones the sibling repos.

## Distribution

- Bundled inside `dsviper-X.Y.Z-devkit.zip` under `tools/` for users
  of the all-in-one DevKit.
- For the conceptual ground (DSM, Kibo, Template Model, the Database
  contract), see [devkit-doc](https://docs.digitalsubstrate.io/) (the
  published Sphinx user docs).

## License

This project is licensed under the MIT License — see [LICENSE](LICENSE).

## Runtime dependency

At runtime, this project depends on the `dsviper` Python package
(distributed on PyPI), which is **proprietary** (PyPI classifier
`License :: Other/Proprietary License`). See
[https://pypi.org/project/dsviper/](https://pypi.org/project/dsviper/)
for the package's licensing posture and contact information.

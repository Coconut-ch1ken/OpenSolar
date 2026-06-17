# AutoSci Solar-Native Dependency Installation Record

Status: current dependency setup for AutoSci Solar-native validation.
Last verified: 2026-06-17 10:37:00 EDT.

This file records the dependency installation state created during the
AutoSci-to-Solar-native implementation so it is rebuildable and removable under
the `install-dependencies` skill.

## OpenSolar Package Manager Decision

| Field | Value |
|---|---|
| Project directory | `/Users/jamesyuan/Developer/Github Repos (On Git)/OpenSolar` |
| Python runtime | mise Python 3.14.2 |
| Package manager | `uv pip sync` |
| Manifest | `requirements/autosci-solar-native-dev.txt` |
| Project-local environment | `.venv/` |
| Approved uv cache | `/Users/jamesyuan/Library/Caches/uv` via `UV_CACHE_DIR=/Users/jamesyuan/Library/Caches/uv` |
| Approved global runtime store | `/Users/jamesyuan/.local/share/mise` |
| Approved package-manager binary | `/opt/homebrew/bin/uv` |

## OpenSolar Rebuild Command

Run from the OpenSolar repo root:

```bash
MISE_PYTHON="/Users/jamesyuan/.local/share/mise/installs/python/3.14.2/bin/python3"
"$MISE_PYTHON" -m venv --clear .venv
UV_CACHE_DIR=/Users/jamesyuan/Library/Caches/uv uv pip sync --python .venv/bin/python requirements/autosci-solar-native-dev.txt
```

## OpenSolar Removal Command

The install is self-contained. Remove the validation environment with:

```bash
rm -rf .venv
```

The active rebuild command does not use the legacy project-local `.uv-cache/`
directory. That directory predates this correction and was left untouched.

## AutoSci Package Manager Decision

| Field | Value |
|---|---|
| Project directory | `/Users/jamesyuan/Developer/Github Repos (On Git)/AutoSci` |
| Python runtime | mise Python 3.14.2 |
| Package manager | `uv pip install` |
| Manifest | `requirements.txt` |
| Project-local environment | `.venv/` |
| Approved uv cache | `/Users/jamesyuan/Library/Caches/uv` via `UV_CACHE_DIR=/Users/jamesyuan/Library/Caches/uv` |
| Approved global runtime store | `/Users/jamesyuan/.local/share/mise` |
| Approved package-manager binary | `/opt/homebrew/bin/uv` |

## AutoSci Rebuild Command

Run from the AutoSci repo root:

```bash
MISE_PYTHON="/Users/jamesyuan/.local/share/mise/installs/python/3.14.2/bin/python3"
"$MISE_PYTHON" -m venv --clear .venv
UV_CACHE_DIR=/Users/jamesyuan/Library/Caches/uv uv pip install --python .venv/bin/python -r requirements.txt
```

`uv pip install -r requirements.txt` is used for AutoSci because its manifest is
a loose direct-dependency requirements file. `uv pip sync requirements.txt`
installed only direct requirements in this environment and left transitive
dependencies such as `urllib3` missing.

## AutoSci Removal Command

The install is self-contained. Remove the validation environment with:

```bash
rm -rf .venv
```

## Corrective Changes

| Previous state | Correction | Reason |
|---|---|---|
| `.venv/` was populated by direct pip install commands | Added pinned manifest and resynced with `uv pip sync` | Makes the dependency state rebuildable from one manifest command. |
| `.test-home/python-userbase/` held an earlier repo-local `pip --user` style install | Removed `.test-home/` after `.venv` sync succeeded | Avoids duplicate ad hoc package state. |
| OpenSolar uv cache was forced into project-local `.uv-cache/` | Future rebuild uses approved uv cache `/Users/jamesyuan/Library/Caches/uv` | Matches the updated skill preference for approved global package-manager caches. |
| AutoSci `.venv/` used Homebrew Python 3.14.5 | Rebuilt AutoSci `.venv/` with mise Python 3.14.2 | Matches the updated skill preference for mise-managed runtimes. |
| AutoSci `.pip-cache/` held earlier local pip cache state | Removed `.pip-cache/` after uv install succeeded | Removes obsolete ad hoc cache state. |
| uv defaulted to `/Users/jamesyuan/.cache/uv` | Removed `/Users/jamesyuan/.cache/uv` and set `UV_CACHE_DIR=/Users/jamesyuan/Library/Caches/uv` in commands | Avoids an unapproved uv cache path. |

## After-Install Report Fields

| Field | Value |
|---|---|
| Packages installed | See `requirements/autosci-solar-native-dev.txt` |
| Manifest or lockfile changed | `requirements/autosci-solar-native-dev.txt` added |
| Project-local paths written | OpenSolar `.venv/`; AutoSci `.venv/` |
| Global store or cache paths touched | mise runtime store already present; Homebrew uv binary already present; `/Users/jamesyuan/Library/Caches/uv` |
| Rebuild command | See `Rebuild Command` |
| Removal command | See `Removal Command` |

## Verification

| Check | Status | Note |
|---|---|---|
| OpenSolar manifest sync | ok | `UV_CACHE_DIR=/Users/jamesyuan/Library/Caches/uv uv pip sync --python .venv/bin/python requirements/autosci-solar-native-dev.txt` resolved and checked packages. |
| OpenSolar package compatibility | ok | `UV_CACHE_DIR=/Users/jamesyuan/Library/Caches/uv uv pip check --python .venv/bin/python` reported all installed packages compatible. |
| OpenSolar import smoke | ok | `pytest`, `requests`, `yaml`, `flask`, `pydantic`, and `jsonschema` imported from `.venv`. |
| AutoSci manifest install | ok | `UV_CACHE_DIR=/Users/jamesyuan/Library/Caches/uv uv pip install --python .venv/bin/python -r requirements.txt` installed direct and transitive requirements. |
| AutoSci package compatibility | ok | `UV_CACHE_DIR=/Users/jamesyuan/Library/Caches/uv uv pip check --python .venv/bin/python` reported all installed packages compatible. |
| AutoSci import smoke | ok | `requests`, `yaml`, `fitz`, `feedparser`, `markdownify`, `playwright`, and `urllib3` imported from `.venv`. |
| Obsolete OpenSolar userbase | ok | `.test-home/` removed. |
| Obsolete AutoSci pip cache | ok | `/Users/jamesyuan/Developer/Github Repos (On Git)/AutoSci/.pip-cache/` removed. |
| Unapproved uv cache | ok | `/Users/jamesyuan/.cache/uv` removed. |

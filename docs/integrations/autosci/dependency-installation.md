# AutoSci Solar-Native Dependency Installation Record

Status: current dependency setup for AutoSci Solar-native validation.
Last verified: 2026-06-17 09:57:14 EDT.

This file records the dependency installation state created during the
AutoSci-to-Solar-native implementation so it is rebuildable and removable under
the `install-dependencies` skill.

## Package Manager Decision

| Field | Value |
|---|---|
| Project directory | `/Users/jamesyuan/Developer/Github Repos (On Git)/OpenSolar` |
| Python runtime | mise Python 3.14.2 |
| Package manager | `uv pip sync` |
| Manifest | `requirements/autosci-solar-native-dev.txt` |
| Project-local environment | `.venv/` |
| Project-local cache | `.uv-cache/` via `UV_CACHE_DIR="$PWD/.uv-cache"` |
| Approved global runtime store | `/Users/jamesyuan/.local/share/mise` |
| Approved package-manager binary | `/opt/homebrew/bin/uv` |

## Rebuild Command

Run from the OpenSolar repo root:

```bash
MISE_PYTHON="/Users/jamesyuan/.local/share/mise/installs/python/3.14.2/bin/python3"
"$MISE_PYTHON" -m venv --clear .venv
UV_CACHE_DIR="$PWD/.uv-cache" uv pip sync --python .venv/bin/python requirements/autosci-solar-native-dev.txt
```

## Removal Command

The install is self-contained. Remove the validation environment with:

```bash
rm -rf .venv
```

Remove the project-local uv cache only when no other local task is using it:

```bash
rm -rf .uv-cache
```

## Corrective Changes

| Previous state | Correction | Reason |
|---|---|---|
| `.venv/` was populated by direct pip install commands | Added pinned manifest and resynced with `uv pip sync` | Makes the dependency state rebuildable from one manifest command. |
| `.test-home/python-userbase/` held an earlier repo-local `pip --user` style install | Removed `.test-home/` after `.venv` sync succeeded | Avoids duplicate ad hoc package state. |
| pip attempted to inspect `/Users/jamesyuan/Library/Caches/pip` and disabled cache | Future rebuild uses `UV_CACHE_DIR="$PWD/.uv-cache"` | Keeps cache writes inside the project directory. |

## After-Install Report Fields

| Field | Value |
|---|---|
| Packages installed | See `requirements/autosci-solar-native-dev.txt` |
| Manifest or lockfile changed | `requirements/autosci-solar-native-dev.txt` added |
| Project-local paths written | `.venv/`, `.uv-cache/` |
| Global store or cache paths touched | mise runtime store already present; Homebrew uv binary already present |
| Rebuild command | See `Rebuild Command` |
| Removal command | See `Removal Command` |

## Verification

| Check | Status | Note |
|---|---|---|
| Manifest sync | ok | `UV_CACHE_DIR="$PWD/.uv-cache" uv pip sync --python .venv/bin/python requirements/autosci-solar-native-dev.txt` resolved and checked packages. |
| Package compatibility | ok | `UV_CACHE_DIR="$PWD/.uv-cache" uv pip check --python .venv/bin/python` reported all installed packages compatible. |
| Import smoke | ok | `pytest`, `requests`, `yaml`, `flask`, `pydantic`, and `jsonschema` imported from `.venv`. |
| Obsolete userbase | ok | `.test-home/` removed. |

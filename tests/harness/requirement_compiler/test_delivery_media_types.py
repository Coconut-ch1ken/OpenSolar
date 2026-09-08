"""Delivery manifests can express code, chart, and JSONL deliverables.

A request that names `.py`, `.svg`, or `.jsonl` files must be representable in the
delivery manifest.  The media_type enum and the suffix map previously ended at
markdown/csv/json/html/plain, so a correctly filled manifest naming any of those three
was rejected with DELIVERY_MEDIA_TYPE_EXTENSION_MISMATCH; the bounded repair could then
only drop the manifest, which failed again as NAMED_DELIVERY_FILE_SET_MISMATCH.

The named-deliverable pattern is covered here too, since the manifest and the pattern
have to agree on which filenames count as deliverables.
"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "harness" / "lib"))

from requirement_compiler.template_contract import delivery_manifest_defects  # noqa: E402
from requirement_compiler.semantic import _NAMED_DELIVERABLE_PATTERN  # noqa: E402


def _manifest(files):
    return {
        "delivery_manifest": {
            "output_root": "outputs/build",
            "exact_file_set": True,
            "files": files,
        }
    }


def _row(file_id, relative_path, media_type):
    return {
        "file_id": file_id,
        "relative_path": relative_path,
        "media_type": media_type,
        "description": "deliverable",
        "content_requirements": ["complete"],
        "required_fields": [],
        "source_refs": ["D1"],
        "required": True,
    }


def test_python_svg_and_jsonl_media_types_are_expressible():
    values = _manifest([
        _row("loader", "src/loader.py", "text/x-python"),
        _row("loader_test", "tests/test_loader.py", "text/x-python"),
        _row("chart", "throughput.svg", "image/svg+xml"),
        _row("events", "events.jsonl", "application/jsonl"),
        _row("summary", "summary.md", "text/markdown"),
        _row("metrics", "metrics.csv", "text/csv"),
        _row("result", "result.json", "application/json"),
    ])
    assert delivery_manifest_defects(values) == []


def test_mismatched_extensions_still_rejected():
    values = _manifest([
        _row("svg_as_text", "chart.svg", "text/plain"),
        _row("py_as_md", "runner.py", "text/markdown"),
        _row("jsonl_as_json", "rows.jsonl", "application/json"),
    ])
    errors = delivery_manifest_defects(values)
    assert [e for e in errors if e.startswith("DELIVERY_MEDIA_TYPE_EXTENSION_MISMATCH")] == [
        "DELIVERY_MEDIA_TYPE_EXTENSION_MISMATCH: /delivery_manifest/files/0",
        "DELIVERY_MEDIA_TYPE_EXTENSION_MISMATCH: /delivery_manifest/files/1",
        "DELIVERY_MEDIA_TYPE_EXTENSION_MISMATCH: /delivery_manifest/files/2",
    ]


def test_named_deliverable_pattern_captures_new_extensions():
    text = (
        "Produce `design.md`, `src/loader.py`, `events.jsonl`, and `throughput.svg`."
    )
    found = set(_NAMED_DELIVERABLE_PATTERN.findall(text))
    assert "design.md" in found
    assert "loader.py" in found
    assert "events.jsonl" in found
    assert "throughput.svg" in found
    # .jsonl must not be shadowed by the .json alternative.
    assert "events.json" not in found


def test_named_deliverable_pattern_matches_at_sentence_end():
    # A filename ending a sentence is followed by a period. The old lookahead treated
    # that period as part of a longer token, so those names were silently dropped from
    # the named delivery set even though the request had asked for them.
    text = (
        "src/ containing loader.py, parser.py, and runner.py. "
        "tests/ containing test_loader.py and test_runner.py. "
        "Also produce summary.md."
    )
    found = set(_NAMED_DELIVERABLE_PATTERN.findall(text))
    assert "runner.py" in found
    assert "test_runner.py" in found
    assert "summary.md" in found
    # A chained extension is still not treated as a named python deliverable.
    chained = set(_NAMED_DELIVERABLE_PATTERN.findall("backup at runner.py.bak here"))
    assert "runner.py" not in chained

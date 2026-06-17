"""Convert AutoSci raw paper data to `research_paper.v1` evidence."""

from __future__ import annotations

from typing import Any

from .common import evidence_base


def convert(raw: dict[str, Any], envelope: dict[str, Any] | None = None) -> dict[str, Any]:
    paper = {
        "paper_id": str(raw.get("paper_id") or "paper-autosci-fixture"),
        "title": str(raw.get("title") or "AutoSci Fixture Paper"),
        "source_type": str(raw.get("source_type") or "markdown"),
        "source_ref": str(raw.get("source_ref") or "plugins/autosci/tests/fixtures/sample_paper.md"),
        "identifiers": dict(raw.get("identifiers") or {}),
        "abstract": str(raw.get("abstract") or ""),
        "parse_status": str(raw.get("parse_status") or "parsed"),
        "sections": list(raw.get("sections") or [
            {
                "section_id": "sec-abstract",
                "title": "Abstract",
                "text": str(raw.get("abstract") or "Fixture abstract."),
                "source_anchor": "sample_paper.md#abstract",
            }
        ]),
    }
    return evidence_base("research_paper.v1", envelope, {"paper": paper})

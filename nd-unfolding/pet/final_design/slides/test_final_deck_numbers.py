"""Every number in the generated deck re-read from its committed source and re-derived."""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

HERE = Path(__file__).resolve().parent
STUDY = HERE.parent
sys.path.insert(0, str(STUDY.parent / "improvement_campaign" / "slides"))
import make_campaign_deck as base  # noqa: E402

RECORD = HERE / "deck_numbers.json"


@pytest.mark.skipif(not RECORD.exists(), reason="deck not generated")
def test_every_number_recomputes_from_its_source():
    rec = json.loads(RECORD.read_text())
    entries = {e["id"]: e for e in rec["numbers"]}
    docs: dict = {}

    def value(inp):
        if isinstance(inp, str):
            return entries[inp]["value"]
        f = inp["file"]
        if f not in docs:
            docs[f] = json.loads((STUDY / f).read_text())
        return base.fetch(docs[f], inp["path"])

    for e in rec["numbers"]:
        v = base.OPS[e["op"]]([value(i) for i in e["inputs"]])
        assert v == pytest.approx(e["value"], rel=1e-12, abs=1e-15), e["id"]
        assert base.render(v, e["fmt"]) == e["rendered"], e["id"]


@pytest.mark.skipif(not RECORD.exists(), reason="deck not generated")
def test_sources_unchanged_since_generation():
    import hashlib
    rec = json.loads(RECORD.read_text())
    for rel, sha in rec["sources"].items():
        assert hashlib.sha256((STUDY / rel).read_bytes()).hexdigest() == sha, rel

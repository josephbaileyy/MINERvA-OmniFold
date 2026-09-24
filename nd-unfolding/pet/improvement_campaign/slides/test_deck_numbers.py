"""Every number in the campaign deck equals the committed field it claims to come from.

    python -m pytest nd-unfolding/pet/improvement_campaign/slides/test_deck_numbers.py

The generator is re-run into a temporary directory (TeX only; no pdflatex). Each record in the
regenerated `deck_numbers.json` is then checked INDEPENDENTLY of the generator's registry: the
source JSON is re-read from disk, the field is fetched by its recorded path, the recorded
operation is recomputed, and the result must equal the recorded value; the rendered string must be
what `render` gives for that value and must appear in the TeX. The committed `deck_numbers.json`,
TeX and claim index must equal the regenerated ones, so a stale committed deck fails here.

A second test feeds the generator a synthetic `confirm_results.json` with FINAL and STRESS sections
(built by the confirmatory stage's own `analyze_confirm.decisions` / `stress_table` from the
committed PILOT runs, relabelled) to exercise the slides that replace the "pending" slide.
"""
from __future__ import annotations

import copy
import json
import math
import statistics
import sys
from pathlib import Path

import pytest

HERE = Path(__file__).resolve().parent
CAMPAIGN = HERE.parent
sys.path.insert(0, str(HERE))

import make_campaign_deck as deck  # noqa: E402

# Recomputed here rather than imported, so a wrong operation in the generator cannot vouch for itself.
RECOMPUTE = {
    "field": lambda xs: xs[0],
    "mean": lambda xs: sum(xs) / len(xs),
    "sd": lambda xs: statistics.stdev(xs),
    "diff": lambda xs: xs[0] - xs[1],
    "ratio": lambda xs: xs[0] / xs[1],
    "one_minus": lambda xs: 1.0 - xs[0],
    "one_minus_ratio": lambda xs: 1.0 - xs[0] / xs[1],
    "min": min,
    "max": max,
    "count": len,
    "count_lt0": lambda xs: len([x for x in xs if x < 0]),
    "count_gt0": lambda xs: len([x for x in xs if x > 0]),
    "count_true": lambda xs: len([x for x in xs if x is True]),
    "any_true": lambda xs: any(x is True for x in xs),
    "mean_abs": lambda xs: sum(abs(x) for x in xs) / len(xs),
}


def _load(rel: str, overrides: dict[str, Path], cache: dict[str, object]) -> object:
    if rel not in cache:
        cache[rel] = json.loads(overrides.get(rel, CAMPAIGN / rel).read_text())
    return cache[rel]


def _fetch(doc: object, path: list) -> object:
    for key in path:
        doc = doc[key] if isinstance(doc, dict) else doc[int(key)]
    return doc


def _same(a: object, b: object) -> bool:
    if isinstance(a, bool) or isinstance(b, bool) or a is None or b is None:
        return a is b or a == b
    return math.isclose(float(a), float(b), rel_tol=1e-12, abs_tol=1e-12)


def check_record(out: Path, overrides: dict[str, Path]) -> dict:
    record = json.loads((out / "deck_numbers.json").read_text())
    tex = (out / deck.TEX_NAME).read_text()
    by_id = {e["id"]: e for e in record["numbers"]}
    cache: dict[str, object] = {}
    values: dict[str, object] = {}

    def value_of(nid: str) -> object:
        if nid in values:
            return values[nid]
        e = by_id[nid]
        xs = [value_of(i) if isinstance(i, str)
              else _fetch(_load(i["file"], overrides, cache), i["path"]) for i in e["inputs"]]
        assert xs, f"{nid}: no inputs"
        values[nid] = RECOMPUTE[e["op"]](xs)
        return values[nid]

    for nid, e in by_id.items():
        v = value_of(nid)
        assert _same(v, e["value"]), f"{nid}: recomputed {v!r} != recorded {e['value']!r}"
        assert deck.render(v, e["fmt"]) == e["rendered"], f"{nid}: rendering drifted"
    # every number a claim cites is on a slide
    claims = (out / "CLAIM_INDEX-deck.md").read_text()
    cited = {line.split("`")[1] for line in claims.splitlines() if line.startswith("|") and "` = " in line}
    assert cited, "claim index cites no numbers"
    for nid in cited:
        assert nid in by_id, f"claim index cites unknown number {nid}"
        assert by_id[nid]["rendered"] in tex, f"{nid} ({by_id[nid]['rendered']}) cited but not in the TeX"
    # every source file hash is the file on disk
    import hashlib
    for rel, sha in record["sources"].items():
        raw = overrides.get(rel, CAMPAIGN / rel).read_bytes()
        assert hashlib.sha256(raw).hexdigest() == sha, f"{rel}: sha256 changed"
    return record


def test_numbers_match_committed_sources(tmp_path: Path) -> None:
    deck.build(tmp_path, None, make_pdf=False)
    record = check_record(tmp_path, {})
    assert 14 <= record["main_slides"] <= 18, record["main_slides"]
    tex = (tmp_path / deck.TEX_NAME).read_text()
    if not record["confirm"]["final_present"]:
        assert "Confirmatory results pending" in tex
    assert deck.SCOPE.split(".")[0] in tex


def test_committed_outputs_are_current(tmp_path: Path) -> None:
    deck.build(tmp_path, None, make_pdf=False)
    for name in ("deck_numbers.json", deck.TEX_NAME, "CLAIM_INDEX-deck.md"):
        committed = HERE / name
        assert committed.is_file(), f"{name} not committed"
        assert committed.read_text() == (tmp_path / name).read_text(), (
            f"{name} is stale: re-run make_campaign_deck.py")


def _synthetic_confirm(tmp_path: Path) -> Path:
    sys.path.insert(0, str(CAMPAIGN / "confirm"))
    analyze = pytest.importorskip("analyze_confirm")
    real = json.loads((CAMPAIGN / deck.CONFIRM).read_text())
    runs = real["pilot"]["runs"]
    stress = {}
    for name, r in runs.items():
        for case in ("D1_m0.350", "D4d_n_up"):
            rr = copy.deepcopy(r)
            rr["dist"] = case
            stress[f"{name}-{case}"] = rr
    synth = dict(real)
    synth["final"] = {"runs": runs, "decisions": analyze.decisions(runs, real["floors"])}
    synth["stress"] = analyze.stress_table(stress)
    path = tmp_path / "confirm_results.synthetic.json"
    path.write_text(json.dumps(synth))
    return path


def test_final_and_stress_slides_render(tmp_path: Path) -> None:
    confirm = _synthetic_confirm(tmp_path)
    out = tmp_path / "deck"
    record = deck.build(out, confirm, make_pdf=False)
    assert record["confirm"] == {"file_present": True, "final_present": True, "stress_present": True}
    check_record(out, {deck.CONFIRM: confirm})
    tex = (out / deck.TEX_NAME).read_text()
    assert "Confirmatory results pending" not in tex
    assert "The confirmatory result (FINAL, pool F)" in tex
    assert "The confirmatory result (STRESS, pool T)" in tex
    assert "Appendix: PILOT (not confirmatory)" in tex
    assert 14 <= record["main_slides"] <= 18, record["main_slides"]


def test_pending_slide_when_confirm_file_absent(tmp_path: Path) -> None:
    missing = tmp_path / "absent.json"
    out = tmp_path / "deck"
    record = deck.build(out, missing, make_pdf=False)
    assert record["confirm"]["file_present"] is False
    tex = (out / deck.TEX_NAME).read_text()
    assert "Confirmatory results pending" in tex
    assert "the file is absent" in tex
    check_record(out, {deck.CONFIRM: missing})

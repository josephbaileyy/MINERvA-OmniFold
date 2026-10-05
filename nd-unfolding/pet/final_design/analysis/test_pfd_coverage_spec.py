"""coverage_spec.py on the committed Amendment-5 manifests (stand-in score files; no coverage outcome read)."""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import coverage_spec as cs  # noqa: E402

RUNS = HERE.parent / "runs"
DEV, D4C = RUNS / "s5c_a5_H2S1T24.tsv", RUNS / "s5d_a5_H2S1T24.tsv"


def stand_ins(tmp: Path, manifest: Path, skip: str | None = None) -> Path:
    d = tmp / manifest.stem
    d.mkdir()
    for line in manifest.read_text().splitlines():
        if line.strip() and not line.startswith("#") and line.split("\t")[0] != skip:
            (d / f"{line.split(chr(9))[0]}.design_scores.json").write_text("{}")
    return d


def test_committed_manifests_give_complete_replicates(tmp_path):
    out = tmp_path / "spec.json"
    cs.main(["--candidate", "H2S1T24K5", "--dev", str(DEV), str(stand_ins(tmp_path, DEV)),
             "--d4c", str(D4C), str(stand_ins(tmp_path, D4C)), "--out", str(out)])
    spec = json.loads(out.read_text())
    assert (spec["k"], spec["B"], spec["bonferroni_m"], spec["looks_planned"]) == (5, 6, 2, 2)
    assert len(spec["dev"]) == 120 and len(spec["d4c"]) == 60
    assert all(len(r["members"]) == 6 for r in spec["dev"] + spec["d4c"])
    assert spec["dev"][0]["replicate"] == "FB0" and spec["d4c"][-1]["replicate"] == "FB59"


def test_a_missing_member_is_refused(tmp_path):
    with pytest.raises(SystemExit, match="not scored"):
        cs.main(["--candidate", "H2S1T24K5", "--dev", str(DEV),
                 str(stand_ins(tmp_path, DEV, skip="S5-H2S1T24K5-FB7-b3")), "--out", str(tmp_path / "s.json")])


def test_the_wrong_manifest_for_the_slot_is_refused(tmp_path):
    with pytest.raises(SystemExit, match="not a dev-tilt member"):
        cs.main(["--candidate", "H2S1T24K5", "--dev", str(D4C), str(stand_ins(tmp_path, D4C)),
                 "--out", str(tmp_path / "s.json")])

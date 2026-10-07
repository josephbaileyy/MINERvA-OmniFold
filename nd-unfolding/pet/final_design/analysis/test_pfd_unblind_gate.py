"""The final-bank unblinding gate (`score_design.refuse_blinded_final_runs`): each run only by its own UNBLIND
group and completeness record (Amendments 2c item 9, 4, 5); a look-1 heading never unlocks coverage, the
development-tilt coverage group never unlocks D4c, RB is never unlocked."""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))
import score_design as sd  # noqa: E402

S4F = "S4F-H2S1T24K5-FB0"
S5C = "S5-H2S1T24K5-FB0-b1"
S5D = "S5-H2S1T24K5-FB0-D4c_p_up-b1"
LOOK1 = "### Amendment 4 (2026-09-30) — UNBLIND look 1"
COV_C = "### Amendment 6 (2026-10-05) — UNBLIND coverage s5c_a5_H2S1T24 (development tilt)"
COV_D = "### Amendment 7 (2026-10-07) — UNBLIND coverage s5d_a5_H2S1T24 (D4c up)"


def study(tmp: Path, headings: list[str], records: dict[str, list[tuple[str, str]]]) -> Path:
    (tmp / "freeze").mkdir(parents=True, exist_ok=True)
    proto = tmp / "PROTOCOL-20260925.md"
    proto.write_text("# protocol\n\n" + "\n\nbody\n\n".join(headings) + "\n")
    for name, rows in records.items():
        lines = ["# manifest\trow\tstatus\treceipt_sha256", f"# {name}.tsv sha256 00"]
        lines += [f"{name}\t{r}\t{st}\tab" for r, st in rows]
        (tmp / sd.UNBLIND_GROUPS[{"look1": "look 1"}.get(name, f"coverage {name}")]).write_text("\n".join(lines) + "\n")
    return proto


def run(tmp: Path, name: str, bank: str | None = None) -> Path:
    d = tmp / "runs" / name
    d.mkdir(parents=True, exist_ok=True)
    if bank:
        (d / "receipt.json").write_text(json.dumps({"selection": {"pseudo_bank": bank}}))
    return d


def test_no_heading_refuses_final_bank(tmp_path):
    proto = study(tmp_path, [], {})
    with pytest.raises(SystemExit, match="not unlocked"):
        sd.refuse_blinded_final_runs([run(tmp_path, S4F, "FB")], proto)


def test_look1_unlocks_its_listed_rows(tmp_path):
    proto = study(tmp_path, [LOOK1], {"look1": [(S4F, "COMPLETE")]})
    sd.refuse_blinded_final_runs([run(tmp_path, S4F, "FB")], proto)


def test_look1_does_not_unlock_coverage(tmp_path):
    """The peer's reproduction: only `UNBLIND look 1` and a coverage member name."""
    proto = study(tmp_path, [LOOK1], {"look1": [(S4F, "COMPLETE")]})
    with pytest.raises(SystemExit, match="not unlocked"):
        sd.refuse_blinded_final_runs([run(tmp_path, S5C, "FB")], proto)
    with pytest.raises(SystemExit, match="not unlocked"):
        sd.refuse_blinded_final_runs(["S5C-H2S1T24K5-C0-M0"], proto)


def test_unlisted_or_incomplete_rows_stay_blinded(tmp_path):
    proto = study(tmp_path, [LOOK1], {"look1": [(S4F, "INCOMPLETE")]})
    with pytest.raises(SystemExit, match="not unlocked"):
        sd.refuse_blinded_final_runs([run(tmp_path, S4F, "FB")], proto)
    proto = study(tmp_path, [LOOK1], {"look1": [("S4F-H2S1T24K5-FB1", "COMPLETE")]})
    with pytest.raises(SystemExit, match="not unlocked"):
        sd.refuse_blinded_final_runs([run(tmp_path, S4F, "FB")], proto)


def test_dev_tilt_coverage_does_not_unlock_d4c(tmp_path):
    rec = {"s5c_a5_H2S1T24": [(S5C, "COMPLETE")], "s5d_a5_H2S1T24": [(S5D, "COMPLETE")]}
    proto = study(tmp_path, [LOOK1, COV_C], {"look1": [(S4F, "COMPLETE")], **rec})
    sd.refuse_blinded_final_runs([run(tmp_path, S5C, "FB")], proto)
    with pytest.raises(SystemExit, match="not unlocked"):
        sd.refuse_blinded_final_runs([run(tmp_path, S5D, "FB")], proto)
    proto = study(tmp_path, [LOOK1, COV_C, COV_D], {"look1": [(S4F, "COMPLETE")], **rec})
    sd.refuse_blinded_final_runs([run(tmp_path, S5C, "FB"), run(tmp_path, S5D, "FB")], proto)


def test_rb_is_never_unlocked(tmp_path):
    rb_name = "S4F-H2S1T24K5-RB0"
    proto = study(tmp_path, [LOOK1], {"look1": [(S4F, "COMPLETE"), (rb_name, "COMPLETE")]})
    with pytest.raises(SystemExit, match="reserve-bank"):
        sd.refuse_blinded_final_runs([run(tmp_path, rb_name)], proto)
    with pytest.raises(SystemExit, match="reserve-bank"):        # listed FB-looking name, RB recorded
        sd.refuse_blinded_final_runs([run(tmp_path, S4F, "RB")], proto)


def test_heading_without_its_record_fails_closed(tmp_path):
    proto = study(tmp_path, [LOOK1, COV_C], {"look1": [(S4F, "COMPLETE")]})
    with pytest.raises(SystemExit, match="completeness record"):
        sd.refuse_blinded_final_runs([run(tmp_path, S4F, "FB")], proto)


def test_group_names_do_not_match_by_prefix(tmp_path):
    proto = study(tmp_path, ["### Amendment 9 (x) — UNBLIND look 10",
                             "### Amendment 10 (x) — UNBLIND coverage s5c_a5_H2S1T24X"],
                  {"look1": [(S4F, "COMPLETE")], "s5c_a5_H2S1T24": [(S5C, "COMPLETE")]})
    assert sd.unblinded_rows(proto) == {}


def test_dev_bank_runs_need_no_heading(tmp_path):
    proto = study(tmp_path, [], {})
    sd.refuse_blinded_final_runs([run(tmp_path, "S3P-H2S1T24K5-DEV0", "DEV")], proto)


def test_committed_protocol_unlocks_exactly_look1():
    rows = sd.unblinded_rows(Path(sd.__file__).resolve().parents[1] / "PROTOCOL-20260925.md")
    assert set(rows.values()) <= {"look 1", "coverage s5c_a5_H2S1T24", "coverage s5d_a5_H2S1T24"}
    assert not any(n.startswith("S5") for n, g in rows.items() if g == "look 1")
    assert all(n.startswith("S4") for n, g in rows.items() if g == "look 1")

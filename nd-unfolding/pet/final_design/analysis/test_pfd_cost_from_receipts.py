"""cost_from_receipts.py on synthetic run directories whose cost is known by construction."""
from __future__ import annotations

import json
from pathlib import Path

import pytest

import cost_from_receipts as cfr
import inference as inf

SENTINEL = "BLINDED-SENTINEL-7f3a"


def chain_log(out: Path, job: str, slots: int, gpus: int = 4) -> None:
    out.mkdir(parents=True, exist_ok=True)
    (out / f"chain-{job}.txt").write_text(
        f"job {job} slots {slots}/gpu x {gpus} gpus, deadline 1790418418, next none\n"
        f"2026-09-26T00:00:00Z slot 0 gpu 0 -> somerun\nstatus 0\n")


def make_run(out: Path, name: str, seconds: list[float], segments: list[tuple],
             load: float = 36.0, extra: dict | None = None) -> Path:
    """A receipt in the run_design.py / B2 layout; `segments` = (job, first, last|None)."""
    run = out / name
    run.mkdir(parents=True, exist_ok=True)
    doc = {"iterations": [{"iteration": i, "seconds": s,
                           "pull": {"mean": 1.0}, "push": {"mean": 1.0}}
                          for i, s in enumerate(seconds)],
           "segments": [dict({"job": j, "first_iteration": f, "started_unix": 1.7e9},
                             **({} if last is None else {"last_iteration": last}))
                        for j, f, last in segments],
           "load_seconds": load, "seconds": sum(seconds) + load, "complete": True}
    doc.update(extra or {})
    (run / "receipt.json").write_text(json.dumps(doc))
    return run


def expected(k: int, seconds: list[float], load: float, slots: int) -> float:
    return (k * sum(seconds) / len(seconds) / slots + load / slots) / 3600.0


# ------------------------------------------------------------------------------------------- #
@pytest.mark.parametrize("name,cid,k", [
    ("S4F-H2S1K5-FB3", "H2S1", 5),
    ("S3P-L128S1K5-DEV0-D1_m0.350", "L128S1", 5),
    ("S4F-CTLrefK3-FB0", "CTLref", 3),
    ("S4S-H2S1K5-FB0-D2_bump_c0.3", "H2S1", 5),
    ("S4F-H2S1K5-FB3-b2", "H2S1", 5),
    ("S4F-P2preS1K4-FB1-D1_m0.350-b5", "P2preS1", 4),
])
def test_name_parsing(name, cid, k):
    assert cfr.parse_run_name(name) == (cid, k)


def test_name_parsing_groups():
    m = __import__("re").match(cfr.DEFAULT_CANDIDATE_RE, "S4F-H2S1K5-FB3-D1_m0.350-b2")
    assert m.group("stage", "bank", "rep", "case", "member") == ("S4F", "FB", "3", "D1_m0.350", "2")
    m = __import__("re").match(cfr.DEFAULT_CANDIDATE_RE, "S4F-H2S1K5-FB3-b2")
    assert m.group("case") is None and m.group("member") == "2"
    assert cfr.parse_run_name("pet2dev-P2pre-F0") is None


def test_packing_from_chain_logs(tmp_path):
    chain_log(tmp_path, "58893144", 1)
    chain_log(tmp_path, "58893159", 2)
    (tmp_path / "chain-58893170.txt").write_text("all COMPLETE\n")        # no job line
    (tmp_path / "chain-58893171.txt").write_text(                          # names another job
        "job 99 slots 3/gpu x 4 gpus, deadline 1, next none\n")
    assert cfr.parse_chain_log(tmp_path / "chain-58893159.txt") == ("58893159", 2)
    assert cfr.chain_packings(tmp_path) == {"58893144": 1, "58893159": 2}


def test_parse_packing():
    assert cfr.parse_packing(["H2S1=2", "P2preS1=1"]) == {"H2S1": 2, "P2preS1": 1}
    for bad in (["H2S1"], ["H2S1=0"], ["=2"], ["H2S1=2", "H2S1=1"]):
        with pytest.raises(ValueError):
            cfr.parse_packing(bad)


def test_single_packing_cost(tmp_path):
    chain_log(tmp_path, "100", 2)
    secs = [600.0, 620.0, 580.0, 610.0, 590.0]
    run = make_run(tmp_path, "S4F-H2S1K5-FB0", secs, [("100", 0, 4)], load=40.0)
    rec = cfr.run_cost(run, 5, 2, cfr.chain_packings(tmp_path))
    assert rec["gpu_hours"] == pytest.approx(expected(5, secs, 40.0, 2))
    assert rec["iterations_used"] == 5 and rec["iterations_unknown_packing"] == 0


def test_mixed_packing_uses_only_declared_iterations(tmp_path):
    chain_log(tmp_path, "100", 1)
    chain_log(tmp_path, "101", 2)
    # iterations 0-1 at 1/gpu (fast, alone on the GPU), 2-4 at 2/gpu (slower, shared)
    secs = [300.0, 310.0, 600.0, 640.0, 620.0]
    run = make_run(tmp_path, "S4F-H2S1K5-FB0", secs, [("100", 0, 1), ("101", 2, 4)], load=30.0)
    packings = cfr.chain_packings(tmp_path)
    at2 = cfr.run_cost(run, 5, 2, packings)
    assert at2["gpu_hours"] == pytest.approx(expected(5, secs[2:], 30.0, 2))
    assert at2["iterations_used"] == 3 and at2["iterations_other_packing"] == {"1": 2}
    at1 = cfr.run_cost(run, 5, 1, packings)
    assert at1["gpu_hours"] == pytest.approx(expected(5, secs[:2], 30.0, 1))


def test_unknown_packing_and_segment_edges(tmp_path):
    chain_log(tmp_path, "100", 2)
    secs = [600.0, 610.0, 620.0, 630.0]
    # job 200 has no chain log; a segment stopped before any iteration covers nothing; the
    # later segment re-assigns iteration 3; iteration 3 is thus job 100's
    run = make_run(tmp_path, "S4F-H2S1K5-FB0", secs,
                   [("100", 0, 1), ("200", 2, 3), ("300", 4, None), ("100", 3, 3)])
    rec = cfr.run_cost(run, 5, 2, cfr.chain_packings(tmp_path))
    assert rec["iterations_used"] == 3 and rec["iterations_unknown_packing"] == 1
    assert rec["unknown_packing_jobs"] == ["200"]
    assert rec["gpu_hours"] == pytest.approx(expected(5, [600.0, 610.0, 630.0], 36.0, 2))


def test_excluded_runs(tmp_path):
    chain_log(tmp_path, "100", 1)
    only1 = make_run(tmp_path, "S4F-H2S1K5-FB0", [300.0, 310.0], [("100", 0, 1)])
    nolog = make_run(tmp_path, "S4F-H2S1K5-FB1", [600.0], [("999", 0, 0)])
    broken = tmp_path / "S4F-H2S1K5-FB2"
    broken.mkdir()
    (broken / "receipt.json").write_text("{not json")
    doc = cfr.summarize([only1, nolog, broken], {"H2S1": 2})
    c = doc["candidates"]["H2S1"]
    assert c["gpu_hours_per_unfolding"] == [] and c["n"] == 0
    reasons = {e["run"]: e["excluded"] for e in c["excluded"]}
    assert "declared packing (2/gpu)" in reasons["S4F-H2S1K5-FB0"]
    assert "declared packing" in reasons["S4F-H2S1K5-FB1"]
    assert reasons["S4F-H2S1K5-FB2"].startswith("receipt unreadable")
    assert c["evidence_cost"] is None and c["median"] is None


def test_summary_candidates_and_evidence_block_feeds_cost_ratio_lb(tmp_path):
    chain_log(tmp_path, "100", 2)
    chain_log(tmp_path, "101", 1)
    runs, want = [], {"H2S1": [], "L128S1": []}
    for r in range(4):
        s_small = [600.0 + 10 * r + j for j in range(5)]
        s_large = [2400.0 + 40 * r + j for j in range(5)]
        runs.append(make_run(tmp_path, f"S4F-H2S1K5-FB{r}", s_small, [("100", 0, 4)]))
        runs.append(make_run(tmp_path, f"S4F-L128S1K5-FB{r}-D1_m0.350", s_large, [("100", 0, 4)]))
        want["H2S1"].append(expected(5, s_small, 36.0, 2))
        want["L128S1"].append(expected(5, s_large, 36.0, 2))
    runs.append(make_run(tmp_path, "pet2dev-P2pre-F0", [1.0], [("100", 0, 0)]))
    out = tmp_path / "cost.json"
    assert cfr.main(["--runs", *map(str, runs), "--packing", "H2S1=2", "L128S1=2",
                     "P2preS1=1", "--out", str(out)]) == 0
    doc = json.loads(out.read_text())
    assert doc["schema"] == cfr.SCHEMA and len(doc["unmatched_runs"]) == 1
    for cid in ("H2S1", "L128S1"):
        c = doc["candidates"][cid]
        assert set(c) >= {"k", "packing", "gpu_hours_per_unfolding", "runs", "excluded",
                          "median", "mean", "sd", "evidence_cost"}
        assert (c["k"], c["packing"]) == (5, 2)
        assert c["gpu_hours_per_unfolding"] == pytest.approx(want[cid])
        assert c["evidence_cost"] == {"gpu_hours_per_unfolding": c["gpu_hours_per_unfolding"],
                                      "unfoldings_per_result": 6, "inference_gpu_hours": 0.0}
    L, S = doc["candidates"]["L128S1"]["evidence_cost"], doc["candidates"]["H2S1"]["evidence_cost"]
    cr = inf.cost_ratio_lb(L["gpu_hours_per_unfolding"], S["gpu_hours_per_unfolding"], 0.05,
                           L["unfoldings_per_result"], S["unfoldings_per_result"],
                           L["inference_gpu_hours"], S["inference_gpu_hours"])
    assert cr["large"]["n"] == cr["small"]["n"] == 4
    assert 3.5 < cr["ratio"] < 4.0 and cr["lb"] < cr["ratio"]


def test_field_restriction(tmp_path, capsys):
    chain_log(tmp_path, "100", 2)
    extra = {"fits": [{"loss": SENTINEL}], "closure": {"note": SENTINEL},
             "recorder": {SENTINEL: 1}, "resources": [{"gpu_peak_bytes": SENTINEL}]}
    runs = [make_run(tmp_path, f"S4F-H2S1K5-FB{r}", [600.0 + r, 610.0], [("100", 0, 1)],
                     extra=extra) for r in range(2)]
    t = cfr.read_timing(runs[0] / "receipt.json")
    assert set(t) == {"iterations", "segments", "load_seconds"}
    assert all(set(i) == {"iteration", "seconds"} for i in t["iterations"])
    assert all(set(s) == {"job", "first_iteration", "last_iteration"} for s in t["segments"])
    out = tmp_path / "cost.json"
    assert cfr.main(["--runs", *map(str, runs), "--packing", "H2S1=2", "--out", str(out)]) == 0
    text = out.read_text() + capsys.readouterr().out
    for word in (SENTINEL, "fits", "closure", "recorder", "resources", "pull", "push",
                 "started_unix", "complete"):
        assert word not in text


def test_receipt_errors_do_not_echo_content(tmp_path):
    run = make_run(tmp_path, "S4F-H2S1K5-FB0", [600.0], [("100", 0, 0)])
    doc = json.loads((run / "receipt.json").read_text())
    doc["iterations"][0]["seconds"] = SENTINEL
    (run / "receipt.json").write_text(json.dumps(doc))
    rec = cfr.run_cost(run, 5, 2, {"100": 2})
    assert "iterations[0].seconds" in rec["excluded"] and SENTINEL not in rec["excluded"]


def test_refusals(tmp_path, capsys):
    a = make_run(tmp_path, "S4F-H2S1K5-FB0", [600.0], [("100", 0, 0)])
    b = make_run(tmp_path, "S4F-H2S1K3-FB1", [600.0], [("100", 0, 0)])
    out = str(tmp_path / "c.json")
    assert cfr.main(["--runs", str(a), "--packing", "L128S1=2", "--out", out]) == 2
    assert "no --packing declared for candidate(s) H2S1" in capsys.readouterr().err
    assert cfr.main(["--runs", str(a), str(b), "--packing", "H2S1=2", "--out", out]) == 2
    assert "K = 5 and 3" in capsys.readouterr().err
    assert cfr.main(["--runs", str(a), str(a), "--packing", "H2S1=2", "--out", out]) == 2
    assert cfr.main(["--runs", str(a), "--packing", "H2S1=2", "--candidate-of", r"^(?P<cid>\w+)$",
                     "--out", out]) == 2
    assert not Path(out).exists()

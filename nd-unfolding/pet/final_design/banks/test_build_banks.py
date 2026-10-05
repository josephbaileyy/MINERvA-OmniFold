"""Tests of the bank build (numpy only; synthetic pools, plus the committed predecessor records)."""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

import numpy as np
import pytest

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

import build_banks as bb  # noqa: E402
import replicates as rp  # noqa: E402


def synthetic(n=40_000, seed=3):
    """Inventory of n rows: ~2 % not truth-passing, ~5 % excluded (historical), pools P,F,S,T,R."""
    rng = np.random.default_rng(seed)
    ident = np.stack([rng.integers(1, 10**6, n), rng.integers(0, 10**4, n), np.arange(n)],
                     1).astype(np.int64)
    pass_truth = rng.random(n) > 0.02
    codes = np.full(n, -1, np.int8)
    u = rng.random(n)
    eligible = pass_truth & (rng.random(n) > 0.05)
    for code, (lo, hi) in enumerate(((0, .08), (.08, .4), (.4, .8), (.8, .97), (.97, 1.0))):
        codes[eligible & (u >= lo) & (u < hi)] = code
    return codes, ident, pass_truth


PLAN = (("P", "fam-p", 400, 300, True, (0, 1)),
        ("F", "fam-f", 400, 300, True, tuple(range(5))),
        ("S", "fam-s1", 400, 300, True, (0,)),
        ("S", "fam-s8", 3000, 2500, False, (0, 1)),
        ("T", "fam-t", 300, 300, False, tuple(range(4))))


@pytest.mark.parametrize("disjoint,reps", [(True, (0, 2, 3)), (False, (0, 1, 5))])
@pytest.mark.parametrize("workers", [1, 2])
def test_draw_family_equals_replicates_draw(disjoint, reps, workers):
    codes, ident, _ = synthetic()
    rows = rp.pool_rows(codes, "F")
    design = rp.ReplicateDesign("F", "fam", 500, 400, disjoint)
    ref, _ = rp.draw_replicates(design, reps, rows, ident[rows])
    hasher = bb.Hasher(ident, workers, min_parallel=100)
    try:
        got = bb.draw_family(design, reps, rows, hasher)
    finally:
        hasher.close()
    for rep in ref:
        prior, pseudo = got[rep.replicate]
        assert prior.tobytes() == rep.prior_rows.tobytes()
        assert pseudo.tobytes() == rep.pseudo_rows.tobytes()


def test_hasher_is_bit_identical_to_uniform_hash_for_any_worker_count():
    _, ident, _ = synthetic(5_000)
    rows = np.arange(0, 5_000, 3)
    ref = rp.uniform_hash(ident[rows], 12345)
    for w in (1, 3):
        h = bb.Hasher(ident, w, min_parallel=10)
        try:
            assert h(rows, 12345).tobytes() == ref.tobytes()
        finally:
            h.close()


def test_banks_partition_the_truth_passing_rows():
    codes, ident, pt = synthetic()
    bank, rec = bb.build(codes=codes, identity=ident, pass_truth=pt, plan=PLAN, workers=1,
                         known_historical_rows=None, log=lambda s: None)
    # drawn union from the reference implementation
    drawn = np.zeros(codes.size, bool)
    for pool, fam, a, b, disj, reps in PLAN:
        rows = rp.pool_rows(codes, pool)
        out, _ = rp.draw_replicates(rp.ReplicateDesign(pool, fam, a, b, disj), reps, rows,
                                    ident[rows])
        for r in out:
            drawn[r.prior_rows] = True
            drawn[r.pseudo_rows] = True
            key = f"{pool}/{fam}/{r.replicate}"
            assert rec["reconstructed"][key]["prior_rows_sha256"] == rp.rows_digest(r.prior_rows)
            assert rec["reconstructed"][key]["pseudo_rows_sha256"] == rp.rows_digest(r.pseudo_rows)
    fb = np.isin(codes, [0, 1, 2, 3]) & ~drawn
    assert np.array_equal(bank == 1, fb)
    assert np.array_equal(bank == 2, codes == 4)
    assert np.array_equal(bank == -1, ~pt)
    assert np.array_equal(bank == 0, pt & ~fb & (codes != 4))
    assert rec["counts"]["DEV"] + rec["counts"]["FB"] + rec["counts"]["RB"] == int(pt.sum())
    # excluded (historical) truth-passing rows are DEV; drawn pool rows are DEV
    assert np.all(bank[pt & (codes == -1)] == 0) and np.all(bank[drawn] == 0)
    assert rec["FB_by_pool"] == {p: int((fb & (codes == rp.POOL_CODES[p])).sum()) for p in "PFST"}
    # every worker count gives the same banks
    bank2, _ = bb.build(codes=codes, identity=ident, pass_truth=pt, plan=PLAN, workers=2,
                        known_historical_rows=None, log=lambda s: None)
    assert bank2.tobytes() == bank.tobytes()


def test_known_and_historical_rows_must_be_dev():
    codes, ident, pt = synthetic()
    r_pool = int(rp.pool_rows(codes, "R")[0])
    with pytest.raises(SystemExit, match="not in DEV"):
        bb.build(codes=codes, identity=ident, pass_truth=pt, plan=PLAN,
                 known_historical_rows=[r_pool], log=lambda s: None)
    with pytest.raises(SystemExit, match="historical subsample"):
        bb.build(codes=codes, identity=ident, pass_truth=pt, plan=PLAN,
                 historical_rows=np.array([r_pool]), known_historical_rows=None,
                 log=lambda s: None)
    dev_row = int(np.flatnonzero(pt & (codes == -1))[0])
    _, rec = bb.build(codes=codes, identity=ident, pass_truth=pt, plan=PLAN,
                      historical_rows=np.array([dev_row]), known_historical_rows=[dev_row],
                      log=lambda s: None)
    assert rec["known_historical_rows_in_pools"][str(dev_row)]["bank"] == "DEV"


def test_pool_row_failing_truth_is_refused():
    codes, ident, pt = synthetic()
    pt = pt.copy()
    pt[rp.pool_rows(codes, "S")[0]] = False
    with pytest.raises(SystemExit, match="does not pass truth"):
        bb.build(codes=codes, identity=ident, pass_truth=pt, plan=PLAN,
                 known_historical_rows=None, log=lambda s: None)


def test_digest_check_matches_flags_mismatch_and_unplanned_records():
    rec = {"P/f/0": {"prior_rows_sha256": "a", "pseudo_rows_sha256": "b", "n_prior": 1,
                     "n_pseudo": 1, "disjoint": True},
           "P/f/1": {"prior_rows_sha256": "c", "pseudo_rows_sha256": "d", "n_prior": 1,
                     "n_pseudo": 1, "disjoint": True}}
    good = {"source": "x", "prior": "a", "pseudo": "b", "n_prior": 1, "n_pseudo": 1,
            "disjoint": True}
    out = bb.check_digests(rec, {"P/f/0": [good]})
    assert out["summary"]["ok"] and out["summary"]["no_committed_record"] == ["P/f/1"]
    bad = dict(good, source="y", pseudo="zz")
    out = bb.check_digests(rec, {"P/f/0": [good, bad]})
    assert not out["summary"]["ok"] and out["per_draw"]["P/f/0"]["status"] == "MISMATCH"
    assert out["per_draw"]["P/f/0"]["mismatching_sources"] == ["y"]
    wrong_design = dict(good, disjoint=False)
    assert not bb.check_digests(rec, {"P/f/0": [wrong_design]})["summary"]["ok"]
    out = bb.check_digests(rec, {"P/f/0": [good], "S/other/4": [good]})
    assert not out["summary"]["ok"] and out["summary"]["records_not_in_plan"] == ["S/other/4"]


def test_committed_predecessor_records_are_all_in_the_plan():
    """Covering check on the committed records themselves: every recorded draw is planned, and
    every planned draw except E1-references r1/r2 has at least one record."""
    records = bb.committed_draw_records()
    planned = {f"{p}/{f}/{r}" for p, f, _a, _b, _d, reps in bb.DRAW_PLAN for r in reps}
    assert set(records) <= planned
    assert planned - set(records) == {"T/E1-references/1", "T/E1-references/2"}
    for key, entries in records.items():
        assert len({(e["prior"], e["pseudo"]) for e in entries}) == 1, key


def test_main_end_to_end_on_a_synthetic_inventory(tmp_path, monkeypatch):
    codes, ident, pt = synthetic()
    pools = tmp_path / "pools.npz"
    np.savez(pools, pool_codes=codes)
    sidecar = tmp_path / "identity.npz"
    np.savez(sidecar, sig_event_id=ident)
    inv = tmp_path / "inv.npz"
    np.savez(inv, pass_truth=pt, data_muon=np.zeros(3))
    sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()   # noqa: E731
    manifest = {"inputs": {"identity_npz": {"sha256": sha(sidecar)},
                           "truth_npz": {"sha256": sha(inv)}},
                "pools": {k: {"code": v, "count": int((codes == v).sum())}
                          for k, v in rp.POOL_CODES.items()},
                "output": {"sha256": sha(pools)}, "commit": "synthetic"}
    man = tmp_path / "POOL_MANIFEST.json"
    man.write_text(json.dumps(manifest))
    monkeypatch.setattr(bb, "DRAW_PLAN", PLAN)
    monkeypatch.setattr(bb, "committed_draw_records", lambda: {})
    monkeypatch.setattr(bb, "historical_load_rows",
                        lambda n: (np.flatnonzero(codes == -1)[:50], {"source": "synthetic"}))
    out = tmp_path / "banks"
    argv = ["--inventory", str(inv), "--identity-sidecar", str(sidecar), "--pools-npz",
            str(pools), "--pool-manifest", str(man), "--out-dir", str(out), "--workers", "2",
            "--no-expectations"]
    assert bb.main(argv) == 0
    m = json.loads((out / "BANK_MANIFEST.json").read_text())
    with np.load(out / "banks.npz") as z:
        bank = z["bank_code"]
        for name, code in bb.BANK_CODES.items():
            assert np.array_equal(z[f"rows_{name}"], np.flatnonzero(bank == code))
            assert m["banks"][name]["sorted_rows_sha256"] == rp.rows_digest(z[f"rows_{name}"])
    assert m["output"]["banks_npz_sha256"] == sha(out / "banks.npz")
    assert m["inputs"]["inventory_members_read"] == ["pass_truth"]
    assert m["digest_check"]["summary"]["no_committed_record"]      # nothing recorded here
    with pytest.raises(SystemExit, match="frozen once"):              # never overwritten
        bb.main(argv)
    # a wrong declared expectation refuses before anything is written
    with pytest.raises(SystemExit, match="declared expectation"):
        bb.check_expected({"counts": {"FB": 1, "RB": 2}, "FB_by_pool": {}},
                          {"FB": 1, "RB": 3, "FB_by_pool": {}})

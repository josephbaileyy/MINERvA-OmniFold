"""Tests of the comparison's guards and data assembly (synthetic inputs; no cluster, no PET source).

    python -m pytest nd-unfolding/pet/gbdt_comparison/test_pgc.py -q
"""
from __future__ import annotations

import json
import subprocess
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import numpy as np
import pytest

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

import pgc_fb  # noqa: E402
import pgc_plan  # noqa: E402
import pgc_run_fb  # noqa: E402
import pgc_source  # noqa: E402


# --------------------------------------------------------------------------------------------- #
# pgc_source: the pin fires on a changed file and stays silent on the committed bytes
# --------------------------------------------------------------------------------------------- #
def _repo(tmp_path: Path) -> tuple[Path, str, dict[str, str]]:
    root = tmp_path / "src"
    rel = "nd-unfolding/pet/final_design/scalar/mod.py"
    (root / Path(rel).parent).mkdir(parents=True)
    (root / rel).write_text("x = 1\n")
    env = {"GIT_AUTHOR_NAME": "t", "GIT_AUTHOR_EMAIL": "t@t", "GIT_COMMITTER_NAME": "t",
           "GIT_COMMITTER_EMAIL": "t@t", "PATH": "/usr/bin:/bin"}
    for cmd in (["init", "-q"], ["add", rel], ["commit", "-q", "-m", "x"]):
        subprocess.run(["git", "-C", str(root), *cmd], check=True, env=env)
    head = subprocess.run(["git", "-C", str(root), "rev-parse", "HEAD"], capture_output=True,
                          text=True, check=True).stdout.strip()
    return root, head, {rel: pgc_source.git_blob_sha1(root / rel)}


def test_source_pin_accepts_committed_bytes(tmp_path, monkeypatch):
    root, head, blobs = _repo(tmp_path)
    monkeypatch.setattr(pgc_source, "PET_SOURCE_COMMIT", head)
    monkeypatch.setattr(pgc_source, "PINNED_BLOBS", blobs)
    assert pgc_source.verify_checkout(root)["commit"] == head


def test_source_pin_refuses_edited_file(tmp_path, monkeypatch):
    root, head, blobs = _repo(tmp_path)
    monkeypatch.setattr(pgc_source, "PET_SOURCE_COMMIT", head)
    monkeypatch.setattr(pgc_source, "PINNED_BLOBS", blobs)
    (root / next(iter(blobs))).write_text("x = 2\n")
    with pytest.raises(SystemExit, match="differ from the pinned"):
        pgc_source.verify_checkout(root)


def test_source_pin_refuses_other_commit(tmp_path, monkeypatch):
    root, _head, blobs = _repo(tmp_path)
    monkeypatch.setattr(pgc_source, "PINNED_BLOBS", blobs)
    with pytest.raises(SystemExit, match="HEAD"):
        pgc_source.verify_checkout(root)


# --------------------------------------------------------------------------------------------- #
# pgc_run_fb: blinding guard and budget rule, in both directions
# --------------------------------------------------------------------------------------------- #
def _completeness(tmp_path: Path, rows: list[str]) -> Path:
    src = tmp_path / "pet"
    f = src / "nd-unfolding/pet/final_design/freeze/COMPLETENESS-look1.tsv"
    f.parent.mkdir(parents=True)
    f.write_text("# manifest\trow\tstatus\treceipt_sha256\n"
                 + "".join(f"s4f\t{r}\tCOMPLETE\tabc\n" for r in rows)
                 + "s4f\tS4F-H2S1T24K5-FB9\tRUNNING\tabc\n")
    return src


def test_blinding_accepts_listed_complete(tmp_path):
    src = _completeness(tmp_path, ["S4F-H2S1T24K5-FB0"])
    pgc_run_fb.refuse_blinded(["S4F-H2S1T24K5-FB0"], src)


@pytest.mark.parametrize("name", ["S4F-H2S1T24K5-FB9", "S4F-H2S1T24K5-FB1",
                                  "S5C-H2S1T24K5-FB0", "S4S-H2S1T24K5-RB0-null"])
def test_blinding_refuses(tmp_path, name):
    src = _completeness(tmp_path, ["S4F-H2S1T24K5-FB0", "S5C-H2S1T24K5-FB0",
                                   "S4S-H2S1T24K5-RB0-null"])
    with pytest.raises(SystemExit):
        pgc_run_fb.refuse_blinded([name], src)


def test_budget_rule():
    assert pgc_run_fb.may_start(0.0, 0, None, 0.1, 7.5)
    assert pgc_run_fb.may_start(7.0, 1, 0.02, 0.1, 7.5)          # 7.0 + 2 x 0.025 = 7.05
    assert not pgc_run_fb.may_start(7.46, 1, 0.02, 0.1, 7.5)      # 7.46 + 0.05 > 7.5
    assert not pgc_run_fb.may_start(7.45, 0, None, 0.1, 7.5)      # first-task projection


def test_task_names_and_plan_order():
    assert pgc_run_fb.task_name("S4S-H2S1T24K5-FB3-D4c_p_up") == "GBDT-S4S-FB3-D4c_p_up"
    assert pgc_run_fb.task_name("S4F-H2S1T24K5-FB12") == "GBDT-S4F-FB12-dev"
    tl = pgc_plan.tasks()
    assert len(tl) == 352 and len({t["run"] for t in tl}) == 352
    assert [t["tier"] for t in tl] == sorted(t["tier"] for t in tl)
    assert all(t["seed"] == 1 + pgc_run_fb.parse_run(t["run"])["fb"] for t in tl)
    assert tl[0]["run"] == "S4F-H2S1T24K5-FB0" and tl[30]["run"] == "S4S-H2S1T24K5-FB0-D4c_p_up"


# --------------------------------------------------------------------------------------------- #
# pgc_fb: gathering refuses inconsistent inventory columns; the R factor is applied once
# --------------------------------------------------------------------------------------------- #
@dataclass
class _Problem:
    selection: str
    case: str
    prior: dict
    pseudo: dict
    distortion: np.ndarray
    oracle: np.ndarray
    r_factor: Any
    record: dict = field(default_factory=dict)

    @property
    def pg_prior(self):
        return self.prior["pass_truth"]

    @property
    def s1_prior(self):
        return self.prior["pass_reco"] & self.prior["pass_truth"]

    @property
    def s1_pseudo(self):
        return self.pseudo["pass_reco"] & self.pseudo["pass_truth"]


class _SD:
    Problem = _Problem


def _fixture(tmp_path: Path, case: str, factor: float | None = None, n_inv: int = 400):
    rng = np.random.default_rng(1)
    reco = rng.gamma(2, 0.5, (n_inv, 4)).astype(np.float32)
    rf = {c: rng.integers(0, 4, n_inv).astype(np.int8) for c in pgc_fb.ROW_FEATURE_COLUMNS}
    rf["rc_E_sum"] = rng.exponential(0.5, n_inv).astype(np.float32)
    rf["pass_reco"] = rng.random(n_inv) < 0.7
    rf["pass_truth"] = rng.random(n_inv) < 0.95
    np.save(tmp_path / "reco.npy", reco)
    np.savez(tmp_path / "rf.npz", **rf)
    rows = {"prior": np.arange(0, n_inv, 2), "pseudo": np.arange(1, n_inv, 2)}
    A = {}
    for s, r in rows.items():
        A[f"{s}_rows"] = r.astype(np.int64)
        A[f"{s}_pass_reco"] = rf["pass_reco"][r]
        A[f"{s}_pass_truth"] = rf["pass_truth"][r]
        A[f"{s}_truth"] = rng.gamma(2, 0.5, (r.size, 4))
        A[f"{s}_w_truth"] = rng.uniform(1, 2, r.size)
        A[f"{s}_w_reco"] = rng.uniform(1, 2, r.size)
        A[f"{s}_region"] = rng.integers(0, 4, r.size).astype(np.int8)
        A[f"{s}_reco_eavail"] = reco[r, 2].astype(np.float64)
    if factor is not None:
        e = reco[rows["pseudo"], 2].copy()
        hit = A["pseudo_pass_reco"]
        e[hit] = e[hit] * np.float32(factor)
        A["pseudo_reco_eavail"] = e.astype(np.float64)
    d = np.ones(rows["pseudo"].size)
    pt = A["pseudo_pass_truth"]
    raw = rng.uniform(0.5, 1.5, int(pt.sum()))
    d[pt] = raw / raw.mean()
    A["pseudo_distortion"] = d
    A["prior_oracle"] = np.ones(rows["prior"].size)
    run = tmp_path / "run"
    run.mkdir()
    np.savez(run / "replicate_arrays.npz", **A)
    (run / "run_identity.json").write_text(json.dumps({"distortion": case}))
    return run, pgc_fb.InventoryColumns(tmp_path / "reco.npy", tmp_path / "rf.npz"), reco, rf


def test_build_problem_plain(tmp_path):
    run, cols, reco, rf = _fixture(tmp_path, "dev")
    p = pgc_fb.build_problem(run, cols, _SD)
    r = p.pseudo["rows"]
    assert np.array_equal(p.pseudo["reco_scalars"], reco[r].astype(np.float64))
    assert np.array_equal(p.pseudo["rc_E_sum"], rf["rc_E_sum"][r].astype(np.float64))


def test_build_problem_r_case_scales_cluster_energy_once(tmp_path):
    run, cols, _reco, rf = _fixture(tmp_path, "R1_x1.05+D1_p0.350", factor=1.05)
    p = pgc_fb.build_problem(run, cols, _SD)
    r, hit = p.pseudo["rows"], p.pseudo["pass_reco"]
    base = rf["rc_E_sum"][r]
    assert np.array_equal(p.pseudo["rc_E_sum"][hit], (base[hit] * np.float32(1.05)).astype(float))
    assert np.array_equal(p.pseudo["rc_E_sum"][~hit], base[~hit].astype(float))
    assert np.array_equal(p.prior["rc_E_sum"], rf["rc_E_sum"][p.prior["rows"]].astype(float))


def test_build_problem_refuses_wrong_inventory(tmp_path):
    run, cols, _reco, _rf = _fixture(tmp_path, "dev")
    cols.reco = np.asarray(cols.reco).copy()
    cols.reco[1, 2] += 1.0
    with pytest.raises(ValueError, match="reco E_avail"):
        pgc_fb.build_problem(run, cols, _SD)


def test_build_problem_refuses_unscaled_r_case(tmp_path):
    run, cols, _reco, _rf = _fixture(tmp_path, "R1_x1.05+D1_p0.350", factor=None)
    with pytest.raises(ValueError, match="float32"):
        pgc_fb.build_problem(run, cols, _SD)


def test_build_problem_refuses_flag_mismatch(tmp_path):
    run, cols, _reco, _rf = _fixture(tmp_path, "dev")
    cols.rf["pass_truth"] = ~cols.rf["pass_truth"]
    with pytest.raises(ValueError, match="pass_truth"):
        pgc_fb.build_problem(run, cols, _SD)


def test_r_factor():
    assert pgc_fb.r_factor("R1_x1.05+D1_p0.350") == 1.05
    assert pgc_fb.r_factor("R2_x1.01_D1_p0.350") == 1.01
    assert pgc_fb.r_factor("D1_p0.350") is None

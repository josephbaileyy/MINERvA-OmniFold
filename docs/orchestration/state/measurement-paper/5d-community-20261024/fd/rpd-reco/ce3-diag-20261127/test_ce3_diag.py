"""Tests of ce3_diag.py (local; nothing is contacted).

usage: python3 -B -m pytest -q -p no:cacheprovider test_ce3_diag.py   (needs the repo, for the bound code at S)
"""

import hashlib
import importlib.util
import io
import json
import os
import subprocess
import sys
from pathlib import Path

import numpy as np
import pytest

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[7]
S = "2415e8d66d1a9160e724d426eaeb54d458d4b4f7"


def load(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    m = importlib.util.module_from_spec(spec)
    sys.modules[name] = m
    spec.loader.exec_module(m)
    return m


@pytest.fixture(scope="module")
def bound(tmp_path_factory):
    src = subprocess.run(["git", "-C", str(REPO), "show", f"{S}:nd-unfolding/fd_rpd_reco.py"], check=True,
                         capture_output=True).stdout
    assert hashlib.sha256(src).hexdigest().startswith("12f68102")
    p = tmp_path_factory.mktemp("bound") / "fd_rpd_reco_S.py"
    p.write_bytes(src)
    return load(p, "fd_rpd_reco_S")


@pytest.fixture
def diag():
    return load(HERE / "ce3_diag.py", "ce3_diag_t")


def fixture(n, seed):
    rng = np.random.default_rng(seed)
    pt = rng.uniform(0.0, 2.0, n)
    pz = rng.uniform(1.5, 25.0, n)
    enu = np.sqrt(pt**2 + pz**2 + 0.1056583755**2) + rng.exponential(1.5, n)
    enu[:7] = 0.5  # rows with Eν < Eμ (C-E3's "valid" excludes them)
    p = np.sqrt(pt**2 + pz**2)
    q3_exact = np.sqrt(enu**2 + p**2 - 2 * enu * pz)  # cosθ = pz/p
    mcgen = np.stack([pt, pz, rng.uniform(0, 1, n), q3_exact * (1 + rng.normal(0, 0.01, n)), rng.uniform(1, 3, n)], 1)
    reco = mcgen * (1 + rng.normal(0, 0.05, (n, 5)))
    w = rng.uniform(0.5, 1.5, n)
    passed = rng.random(n) < 0.8
    return mcgen.astype(np.float32), reco, w, passed, enu


def bound_pooled(bound, parts):
    """d2-predict's path: energy_statistics per playlist, pooled, evaluate_energy_controls' quantiles."""
    out = {}
    for stratum in ("1.5:8", "8:15", "15:60"):
        rows = [p["strata"][stratum] for p in parts]
        e = np.concatenate([r["error"] for r in rows])
        w = np.concatenate([r["weight"] for r in rows])
        out[stratum] = tuple(float(x) for x in bound.weighted_quantiles(e, w, np.array([0.5, 0.99])))
    return out


def test_bound_copy_equals_the_bound_code(bound, diag):
    parts, mine = [], {k: ([], []) for k in ("1.5:8", "8:15", "15:60")}
    for seed in range(3):  # three playlists, pooled in order
        mcgen32, reco, w, passed, enu = fixture(20000, seed)
        truth = np.asarray(mcgen32, dtype=float)
        weights = w * passed
        parts.append(bound.energy_statistics(truth, weights, reco[:, 1], enu))
        e1, muon, theta = diag.bound_error(truth, enu * 1.0)
        for k, (_sel, c) in diag.strata_masks(reco[:, 1], weights, enu, muon).items():
            mine[k][0].append(e1[c])
            mine[k][1].append(weights[c])
    ref = bound_pooled(bound, parts)
    for k, (e, w) in mine.items():
        got = tuple(float(x) for x in diag.weighted_quantiles(np.concatenate(e), np.concatenate(w), np.array([0.5, 0.99])))
        assert got == ref[k], (k, got, ref[k])  # bit for bit


def test_weighted_quantiles_copy_equals_bound(bound, diag):
    rng = np.random.default_rng(5)
    v, w = rng.normal(size=5000), rng.uniform(0, 1, 5000)
    f = np.array([0.5, 0.99, 0.999])
    assert np.array_equal(diag.weighted_quantiles(v, w, f), bound.weighted_quantiles(v, w, f))


def test_exact_form_is_the_identity_and_bound_is_not(diag):
    rng = np.random.default_rng(1)
    n = 5000
    pt, pz = rng.uniform(0, 1.5, n), rng.uniform(8, 15, n)
    enu = np.sqrt(pt**2 + pz**2 + 0.1056583755**2) + rng.uniform(0.05, 5, n)
    p = np.sqrt(pt**2 + pz**2)
    q3 = np.sqrt(enu**2 + p**2 - 2 * enu * pz)
    truth = np.stack([pt, pz, np.zeros(n), q3, np.zeros(n)], 1)
    e1, muon, theta = diag.bound_error(truth, enu)
    e2, q2 = diag.exact_error(truth, enu, muon, theta)
    assert np.nanmax(e2) < 1e-10
    assert np.nanmax(e1) > 1e-6  # the massless form differs


def test_float32_corners_bracket_the_bound_error(diag):
    mcgen32, _reco, _w, _p, enu = fixture(4000, 2)
    e1, _, _ = diag.bound_error(np.asarray(mcgen32, dtype=float), enu)
    lo, hi = diag.corner_errors(mcgen32, enu)
    ok = np.isfinite(e1)
    assert np.all(lo[ok] <= e1[ok] + 1e-15) and np.all(hi[ok] >= e1[ok] - 1e-15)


def write_inputs(tmp, diag, monkeypatch, playlists):
    base = tmp / "base"
    pins = {"lat": {}, "products": {}}
    for i, pl in enumerate(diag.PLAYLISTS):
        mcgen32, reco, w, passed, enu = fixture(3000, 10 + i)
        d = base / "dumps"
        d.mkdir(parents=True, exist_ok=True)
        lat = d / f"lat_{pl}.npz"
        np.savez(lat, MCreco=reco, MCgen=mcgen32, w_reco=w, pass_reco=passed, pass_truth=np.ones_like(passed),
                 measured=np.full((5, 5), np.nan))
        prod = d / f"flux-factors-{pl}.npz"
        np.savez(prod, energy=enu)
        pins["lat"][pl] = [str(lat), hashlib.sha256(lat.read_bytes()).hexdigest()]
        pins["products"][pl] = [str(prod), hashlib.sha256(prod.read_bytes()).hexdigest()]
    monkeypatch.setattr(diag, "BASE", str(base) + "/")
    monkeypatch.setattr(diag, "PINS", pins)
    monkeypatch.setattr(diag.os, "O_NOATIME", 0, raising=False)
    return pins


def run_main(diag, capsys):
    with pytest.raises(SystemExit) as ex:
        diag.main()
    return ex.value.code, json.loads(capsys.readouterr().out)


def test_main_self_check_fails_on_a_wrong_stop_record(tmp_path, diag, monkeypatch, capsys):
    write_inputs(tmp_path, diag, monkeypatch, None)
    code, rep = run_main(diag, capsys)
    assert code == 9 and rep["verdict"] == "SELF-CHECK-FAILED"  # the fixture cannot match the real STOP record
    assert rep["strata"]["8:15"]["self_check"]["bit_equal"] is False


def test_main_reading_when_the_self_check_holds(tmp_path, diag, monkeypatch, capsys):
    write_inputs(tmp_path, diag, monkeypatch, None)
    code, rep = run_main(diag, capsys)
    rec = tuple(rep["strata"]["8:15"]["self_check"]["recomputed"])
    monkeypatch.setattr(diag, "STOP_RECORD", {"8:15": rec})
    monkeypatch.setattr(diag, "CE3_Q99", 1.0)  # lets [1.5, 8) pass on the noisy fixture; the reading logic is the test
    monkeypatch.setattr(diag, "CE3_MEDIAN", 1.0)
    monkeypatch.setattr(diag, "CE1_MIN", 0.0)  # the fixture's deliberate Eν < Eμ rows lower C-E1
    code, rep = run_main(diag, capsys)
    assert code == 0 and rep["verdict"].startswith("R-")
    for k in ("1.5:8", "8:15", "15:60"):
        r = rep["strata"][k]
        assert len(r["i_bound"]["median_q99_q999"]) == 3 and len(r["ii_exact"]["median_q99_q999"]) == 3
        lo, hi = r["iii_float32"]["rowwise_min_median_q99_q999"], r["iii_float32"]["rowwise_max_median_q99_q999"]
        assert lo[1] <= r["i_bound"]["median_q99_q999"][1] <= hi[1]


def test_main_refuses_a_changed_input(tmp_path, diag, monkeypatch, capsys):
    pins = write_inputs(tmp_path, diag, monkeypatch, None)
    pins["products"]["1C"][1] = "0" * 64
    code, rep = run_main(diag, capsys)
    assert code == 9 and rep["verdict"] == "INPUT-FAILED"


def test_read_pinned_refuses_a_symlink(tmp_path, diag, monkeypatch):
    base = tmp_path / "b"
    base.mkdir()
    real = base / "real.npz"
    real.write_bytes(b"x")
    real.read_bytes()  # macOS moves a fresh file's atime on its first read; O_NOATIME is 0 here
    link = base / "link.npz"
    link.symlink_to(real)
    monkeypatch.setattr(diag, "BASE", str(base) + "/")
    monkeypatch.setattr(diag.os, "O_NOATIME", 0, raising=False)
    with pytest.raises(SystemExit) as ex:
        diag.read_pinned(str(link), hashlib.sha256(b"x").hexdigest())
    assert ex.value.code == 9
    data, row = diag.read_pinned(str(real), hashlib.sha256(b"x").hexdigest())
    assert data == b"x" and row["ok"]


def test_measured_is_never_read(diag):
    assert "measured" not in diag.LAT_KEYS
    assert "measured" not in (HERE / "ce3_diag.py").read_text().split("LAT_KEYS = ")[1].split("\n")[0]


def test_build_is_reproducible_and_pins_are_the_committed_ones():
    r = subprocess.run([sys.executable, "-I", "-B", str(HERE / "build_diag.py"), str(REPO), "--check"],
                       capture_output=True, text=True)
    assert r.returncode == 0, r.stdout + r.stderr
    remote = (HERE / "ce3_diag_remote.py").read_text()
    template = (HERE / "ce3_diag.py").read_text()
    diff = [(a, b) for a, b in zip(template.splitlines(), remote.splitlines()) if a != b]
    assert len(diff) == 1 and diff[0][0].startswith("PINS = {}") and diff[0][1].startswith("PINS = {")
    sh = (HERE / "ce3-diag.sh").read_text()
    assert hashlib.sha256((HERE / "ce3_diag_remote.py").read_bytes()).hexdigest() in sh

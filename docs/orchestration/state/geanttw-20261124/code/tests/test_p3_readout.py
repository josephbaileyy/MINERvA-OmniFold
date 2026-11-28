"""p3_readout.py on S5's committed production_cov.npz and synthetic unfold vectors. A two-universe band is rank one
(wcov([u0, u1]) = d d' / 4, d = u0 - u1), so pinned vectors that reproduce S5's bands are built from them."""
import importlib.util
import hashlib
import json
import sys
import subprocess
import shutil
import os
from pathlib import Path

import numpy as np
import pytest

CODE = Path(__file__).resolve().parents[1]
REPO = Path(os.environ.get("GEANTTW_REPO") or CODE.parents[4])   # a copy of code/ is told the repo
assert (REPO / "2d-unfolding").is_dir(), f"no repository at {REPO}: set GEANTTW_REPO"
_s = importlib.util.spec_from_file_location("p3r", CODE / "p3_readout.py")
R = importlib.util.module_from_spec(_s)
_s.loader.exec_module(R)
R.NOATIME_OPTIONAL = True
Z = np.load(REPO / R.PROD, allow_pickle=False)
X = Z["cells_x_EU"]


def from_band(S):
    """(u0, u1) with wcov([u0, u1]) = S, for a rank-one PSD S."""
    j = int(np.argmax(np.diag(S)))
    d = 2 * S[:, j] / np.sqrt(S[j, j])
    return X + d / 2, X - d / 2


def vectors(tmp, pin=None, pinov_scale=1.0, patov_scale=1.0, patch=None):
    v = {"cells_x": X.copy(), "area": Z["area"].copy()}
    side = {"xsec_sha256": {}, "july": {}}
    for b in R.BANDS:
        j0, j1 = from_band(Z[f"band_GEANT_{b}"])
        v[f"july:{b}_0"], v[f"july:{b}_1"] = j0, j1     # S5's July unfolds reproduce S5's bands
        u0, u1 = (j0, j1) if pin is None else pin(b)
        v[f"pin:{b}_0"], v[f"pin:{b}_1"] = u0, u1
        for i in (0, 1):
            side["xsec_sha256"][f"pin:{b}_{i}"] = f"{i}" * 64
            side["july"][f"{b}_{i}"] = {"path": f"/july/{b}_{i}", "sha256": "j" * 64}
        v[f"pinov:{b}_0"], v[f"pinov:{b}_1"] = X + (u0 - X) * pinov_scale, X + (u1 - X) * pinov_scale
        v[f"patov:{b}_0"], v[f"patov:{b}_1"] = X + (u0 - X) * patov_scale, X + (u1 - X) * patov_scale
    if patch:
        patch(v)
    p = tmp / "vec.npz"
    np.savez(p, **v)
    side["npz_sha256"] = hashlib.sha256(p.read_bytes()).hexdigest()
    Path(str(p) + ".json").write_text(json.dumps(side))
    return p


def c3(tmp, vec):
    rc = R.main(["c3", "--repo", str(REPO), "--vectors", str(vec), "--json", str(tmp / "c3.json")])
    return rc, json.loads((tmp / "c3.json").read_text())


def r3(tmp, vec):
    rc = R.main(["r3", "--repo", str(REPO), "--vectors", str(vec), "--c3", str(tmp / "c3.json"),
                 "--json", str(tmp / "r3.json")])
    return rc, (json.loads((tmp / "r3.json").read_text()) if (tmp / "r3.json").exists() else None)


def test_the_formulas_reproduce_a1():
    assert np.median(R.sig_c(Z["total"], X)) == pytest.approx(6.040559265, abs=1e-9)
    assert R.sig_int(Z["total"], X, Z["area"]) == pytest.approx(4.328435633, abs=1e-9)


def test_c3_passes_when_the_pinned_run_reproduces_s5(tmp_path):
    rc, rep = c3(tmp_path, vectors(tmp_path))
    assert rc == 0 and rep["verdict"] == "PASS"
    assert all(rep["bands"][b]["rel"] <= 1e-10 for b in R.BANDS) and all(r == 0 for r in rep["universes"].values())
    assert set(rep["pin_xsec_sha256"]) == {f"pin:{b}_{i}" for b in R.BANDS for i in (0, 1)} and len(rep["july"]) == 6


def test_c3_catches_a_common_shift_that_keeps_the_band(tmp_path):
    """A shift of both pinned vectors leaves wcov unchanged: only the per-universe July comparison sees it."""
    def pin(b):
        j0, j1 = from_band(Z[f"band_GEANT_{b}"])
        return j0 * 1.001, j1 + (j0 * 0.001)
    rc, rep = c3(tmp_path, vectors(tmp_path, pin=pin))
    assert rc == 0 and rep["verdict"] == "NOT REPRODUCED"
    assert all(rep["bands"][b]["rel"] <= 1e-10 for b in R.BANDS)


def test_c3_catches_a_swapped_pair(tmp_path):
    def pin(b):
        j0, j1 = from_band(Z[f"band_GEANT_{b}"])
        return j1, j0
    rc, rep = c3(tmp_path, vectors(tmp_path, pin=pin))
    assert rc == 0 and rep["verdict"] == "NOT REPRODUCED"


def test_c3_not_reproduced_beyond_the_tolerance(tmp_path):
    def pin(b):
        u0, u1 = from_band(Z[f"band_GEANT_{b}"])
        return u0 * (1 + 1e-6), u1
    rc, rep = c3(tmp_path, vectors(tmp_path, pin=pin))
    assert rc == 0 and rep["verdict"] == "NOT REPRODUCED"


@pytest.mark.parametrize("bad", ["nan", "cells"])
def test_c3_fails(tmp_path, bad):
    def patch(v):
        if bad == "nan":
            v["pin:Pion_0"][3] = np.nan
        else:
            v["cells_x"][0] *= 2
    rc, rep = c3(tmp_path, vectors(tmp_path, patch=patch))
    assert rc == 1 and rep["verdict"] == "FAIL"


def test_r3_refuses_after_a_c3_fail(tmp_path):
    vec = vectors(tmp_path, patch=lambda v: v["pin:Pion_0"].__setitem__(3, np.nan))
    c3(tmp_path, vec)
    assert r3(tmp_path, vec)[0] == 2


def test_r3_with_no_patch_effect(tmp_path):
    vec = vectors(tmp_path, pinov_scale=1.05, patov_scale=1.05)
    c3(tmp_path, vec)
    rc, rep = r3(tmp_path, vec)
    assert rc == 0 and rep["pinned_side"] == "S5" and rep["tail_matches_declaration"] is True
    assert rep["R3b_patch"]["dmedian"] == pytest.approx(0, abs=1e-12)
    assert rep["R3b_patch"]["dintegral"] == pytest.approx(0, abs=1e-12)
    assert rep["caveat1"]["discharged"] is True
    assert rep["proxy_removal"]["dmedian_G"] > 0   # pinned+override is 5% wider than pinned


def test_r3_caveat_open_when_the_tail_grows_beyond_ten_percent(tmp_path):
    vec = vectors(tmp_path, patov_scale=1.2)
    c3(tmp_path, vec)
    rc, rep = r3(tmp_path, vec)
    assert rc == 0 and rep["caveat1"]["discharged"] is False and sorted(rep["caveat1"]["open_cells"]) == sorted(R.TAIL)
    assert rep["R3b_patch"]["dintegral"] > 0


def test_r3_refuses_when_not_reproduced(tmp_path):
    def pin(b):
        u0, u1 = from_band(Z[f"band_GEANT_{b}"])
        return u0 * (1 + 1e-6), u1
    vec = vectors(tmp_path, pin=pin)
    c3(tmp_path, vec)
    assert r3(tmp_path, vec)[0] == 2


def test_r3_sanity_stop_on_a_zero_patched_cell(tmp_path):
    vec = vectors(tmp_path, patov_scale=0.0)
    c3(tmp_path, vec)
    rc, rep = r3(tmp_path, vec)
    assert rc == 1 and rep["sanity_stop_cells"]


def test_a_changed_production_npz_is_unusable(tmp_path):
    repo = tmp_path / "repo"
    dst = repo / R.PROD
    dst.parent.mkdir(parents=True)
    with np.load(REPO / R.PROD) as z:
        arrs = {k: z[k] for k in z.files}
    arrs["total"] = arrs["total"].copy()
    arrs["total"][0, 0] += 1e-30                         # one changed value, so other bytes
    np.savez(dst, **arrs)
    (repo / R.BR).parent.mkdir(parents=True)
    shutil.copy(REPO / R.BR, repo / R.BR)
    vec = vectors(tmp_path)
    assert R.main(["c3", "--repo", str(repo), "--vectors", str(vec), "--json", str(tmp_path / "c.json")]) == 2


def fake_s5(tmp_path, july_ok=True):
    """A stand-in s5_rollup.py with a sweeps.json, July files and xsec.root files under tmp_path."""
    import hashlib
    repo = tmp_path / "repo"
    (repo / R.S5).parent.mkdir(parents=True)
    recs = {}
    for b in R.BANDS:
        for i in (0, 1):
            jf = tmp_path / f"july_{b}_{i}.root"
            jf.write_text(f"july {b} {i}\n")
            recs[f"pn/GEANT_{b}_{i}"] = {"path": str(jf), "sha256": hashlib.sha256(jf.read_bytes()).hexdigest()
                                         if july_ok else "0" * 64}
    sj = tmp_path / "sweeps.json"
    sj.write_text(json.dumps(recs))
    (repo / R.S5).write_text(
        "import numpy as np\n"
        "import sys\n"
        "assert getattr(sys.modules.get('ROOT'), '__getattr__', None) is None, 'extract must load S5 with the real ROOT'\n"
        f"PIN = {{'E_U': ('eu', 'ok'), 'sweeps_json': ({str(sj)!r}, {hashlib.sha256(sj.read_bytes()).hexdigest()!r})}}\n"
        "def sha(p):\n    return 'ok'\n"
        "class Cells:\n"
        "    def __init__(self):\n        self.x = np.arange(3.0) + 1; self.area = np.ones(3)\n"
        "    def vec(self, path):\n        return np.full(3, float(len(str(path))))\n")
    for s in R.SLIMS:
        for b in R.BANDS:
            for i in (0, 1):
                x = tmp_path / "o" / s / f"GEANT_{b}_{i}" / "xsec.root"
                x.parent.mkdir(parents=True, exist_ok=True)
                x.write_text(f"{s} {b} {i}\n")
    return repo


def c3_for(tmp_path, verdict="PASS", tamper=False):
    """A c3.json bound to fake_s5's six pinned outputs."""
    shas = {f"pin:{b}_{i}": hashlib.sha256((tmp_path / "o" / "pin" / f"GEANT_{b}_{i}" / "xsec.root").read_bytes()).hexdigest()
            for b in R.BANDS for i in (0, 1)}
    if tamper:
        shas["pin:Pion_1"] = "f" * 64
    p = tmp_path / f"c3_{verdict}_{tamper}.json"
    p.write_text(json.dumps({"verdict": verdict, "pin_xsec_sha256": shas}))
    return p


def test_extract_uses_s5s_cells_and_july_files(tmp_path):
    repo = fake_s5(tmp_path)
    out = tmp_path / "v.npz"
    assert R.main(["extract", "--repo", str(repo), "--outs", str(tmp_path / "o"), "--out", str(out),
                   "--c3", str(c3_for(tmp_path))]) == 0
    v = np.load(out)
    assert len(v.files) == 2 + 18 + 6 and "patov:Proton_1" in v.files and "july:Pion_0" in v.files
    side = json.loads(Path(str(out) + ".json").read_text())
    assert len(side["xsec_sha256"]) == 18 and len(side["july"]) == 6
    side = json.loads(Path(str(out) + ".json").read_text())
    assert side["npz_sha256"] == hashlib.sha256(out.read_bytes()).hexdigest()
    out2 = tmp_path / "v2.npz"
    assert R.main(["extract", "--repo", str(repo), "--outs", str(tmp_path / "o"), "--out", str(out2), "--slims", "pinov",
                   "--c3", str(c3_for(tmp_path))]) == 0
    assert not any(k.startswith("july:") for k in np.load(out2).files)
    assert R.main(["extract", "--repo", str(repo), "--outs", "o", "--out", str(tmp_path / "v3.npz"), "--slims", "pat"]) == 2


def test_extract_refuses_a_july_file_that_is_not_sweeps_jsons(tmp_path):
    repo = fake_s5(tmp_path, july_ok=False)
    assert R.main(["extract", "--repo", str(repo), "--outs", str(tmp_path / "o"), "--out", str(tmp_path / "v.npz"),
                   "--slims", "pin"]) == 2


def test_extract_refuses_another_e_u(tmp_path):
    repo = tmp_path / "repo"
    (repo / R.S5).parent.mkdir(parents=True)
    (repo / R.S5).write_text("PIN = {'E_U': ('eu', 'want')}\ndef sha(p):\n    return 'other'\n")
    assert R.main(["extract", "--repo", str(repo), "--outs", "o", "--out", str(tmp_path / "v.npz")]) == 2


def test_r3_refuses_vectors_whose_pinned_outputs_are_not_c3s(tmp_path):
    vec = vectors(tmp_path)
    assert c3(tmp_path, vec)[0] == 0
    side = json.loads(Path(str(vec) + ".json").read_text())
    side["xsec_sha256"]["pin:Pion_1"] = "f" * 64          # a rerun pinned unfold, after C3
    Path(str(vec) + ".json").write_text(json.dumps(side))
    assert r3(tmp_path, vec)[0] == 2


def test_r3_refuses_a_c3_record_without_the_six_hashes(tmp_path):
    vec = vectors(tmp_path)
    c3(tmp_path, vec)
    rec = json.loads((tmp_path / "c3.json").read_text())
    rec["pin_xsec_sha256"] = {}
    (tmp_path / "c3.json").write_text(json.dumps(rec))
    assert r3(tmp_path, vec)[0] == 2


@pytest.mark.parametrize("slim", ["pinov", "patov"])
def test_r3_stops_on_a_nonfinite_override_band(tmp_path, slim):
    def patch(v):
        v[f"{slim}:Proton_0"] = v[f"{slim}:Proton_0"].copy()
        v[f"{slim}:Proton_0"][7] = np.nan
    vec = vectors(tmp_path, patch=patch)
    c3(tmp_path, vec)
    rc, rep = r3(tmp_path, vec)
    assert rc == 1 and f"{slim}:Proton" in rep["nonfinite_or_not_psd_bands"]



@pytest.mark.parametrize("case", ["no_c3", "not_pass", "unbound"])
def test_extract_refuses_overrides_without_a_bound_c3_pass(tmp_path, case):
    repo = fake_s5(tmp_path)
    args = ["extract", "--repo", str(repo), "--outs", str(tmp_path / "o"), "--out", str(tmp_path / "v.npz"),
            "--slims", "pin", "patov"]
    if case != "no_c3":
        args += ["--c3", str(c3_for(tmp_path, "NOT REPRODUCED" if case == "not_pass" else "PASS", case == "unbound"))]
    assert R.main(args) == 2 and not (tmp_path / "v.npz").exists()


@pytest.mark.parametrize("step", ["c3", "r3"])
def test_a_replaced_npz_with_an_old_sidecar_is_refused(tmp_path, step):
    vec = vectors(tmp_path)
    assert c3(tmp_path, vec)[0] == 0
    v = dict(np.load(vec))
    v["pin:Pion_0"] = v["pin:Pion_0"] * 1.01
    np.savez(vec, **v)                       # the sidecar still names the old npz
    if step == "c3":
        assert R.main(["c3", "--repo", str(REPO), "--vectors", str(vec), "--json", str(tmp_path / "c3b.json")]) == 2
    else:
        assert r3(tmp_path, vec)[0] == 2


def test_r3_stops_on_a_negative_variance_in_t_prime(tmp_path):
    def patch(v):   # patched+override far smaller than pinned+override in one band, so T' goes negative somewhere
        for i in (0, 1):
            v[f"pinov:Neutron_{i}"] = X + (v[f"pinov:Neutron_{i}"] - X) * 1e4
    vec = vectors(tmp_path, patch=patch)
    c3(tmp_path, vec)
    rc, rep = r3(tmp_path, vec)
    assert rc == 1 and rep["sanity_stop_cells"]



# ── the records' form, argparse, and the defaults
def test_every_record_is_canonical_json(tmp_path):
    vec = vectors(tmp_path)
    c3(tmp_path, vec)
    r3(tmp_path, vec)
    for f in (tmp_path / "c3.json", tmp_path / "r3.json"):
        t = f.read_text()
        assert t == json.dumps(json.loads(t), indent=1, sort_keys=True)
    repo = fake_s5(tmp_path / "x")
    out = tmp_path / "x" / "v.npz"
    assert R.main(["extract", "--repo", str(repo), "--outs", str(tmp_path / "x" / "o"), "--out", str(out), "--slims", "pin"]) == 0
    t = Path(str(out) + ".json").read_text()
    assert t == json.dumps(json.loads(t), indent=1, sort_keys=True)


def test_a_pickled_npz_is_never_loaded(tmp_path):
    vec = vectors(tmp_path)
    c3(tmp_path, vec)
    v = dict(np.load(vec))
    v["evil"] = np.array([{"a": 1}], dtype=object)
    np.savez(vec, **v)
    side = json.loads(Path(str(vec) + ".json").read_text())
    side["npz_sha256"] = hashlib.sha256(vec.read_bytes()).hexdigest()
    Path(str(vec) + ".json").write_text(json.dumps(side))
    with pytest.raises(ValueError, match="pickle"):
        R.main(["c3", "--repo", str(REPO), "--vectors", str(vec), "--json", str(tmp_path / "c3b.json")])


@pytest.mark.parametrize("cmd,args", [("extract", ["--repo", "r", "--outs", "o"]), ("extract", ["--repo", "r", "--out", "o"]),
                                      ("extract", ["--outs", "r", "--out", "o"]), ("c3", ["--repo", "r", "--vectors", "v"]),
                                      ("c3", ["--repo", "r", "--json", "j"]), ("c3", ["--vectors", "v", "--json", "j"]),
                                      ("r3", ["--repo", "r", "--vectors", "v", "--c3", "c"]),
                                      ("r3", ["--repo", "r", "--vectors", "v", "--json", "j"]),
                                      ("r3", ["--repo", "r", "--c3", "c", "--json", "j"]),
                                      ("r3", ["--vectors", "v", "--c3", "c", "--json", "j"]), (None, [])])
def test_every_argument_is_required(cmd, args):
    with pytest.raises(SystemExit) as e:
        R.main(([cmd] if cmd else []) + args)
    assert e.value.code == 2


def test_noatime_is_required_outside_the_tests():
    r = subprocess.run([sys.executable, "-I", "-c", "import importlib.util as u, sys; s = u.spec_from_file_location('r', sys.argv[1]); "
                        "m = u.module_from_spec(s); s.loader.exec_module(m); print(m.NOATIME_OPTIONAL)", str(CODE / "p3_readout.py")],
                       capture_output=True, text=True)
    assert r.stdout.strip() == "False", r.stderr


# ── caveat 1, the sanity cells and the tail
def test_caveat1_is_discharged_when_the_patch_changes_nothing(tmp_path, capsys):
    vec = vectors(tmp_path)
    c3(tmp_path, vec)
    rc, rep = r3(tmp_path, vec)
    assert rc == 0 and rep["caveat1"]["discharged"] and all(r == pytest.approx(1.0) for r in rep["caveat1"]["ratio"].values())
    assert "caveat 1 DISCHARGED" in capsys.readouterr().out


def test_caveat1_stays_open_when_a_tail_cell_grows(tmp_path, capsys):
    vec = vectors(tmp_path, patov_scale=1.2)
    c3(tmp_path, vec)
    rc, rep = r3(tmp_path, vec)
    assert rc == 0 and not rep["caveat1"]["discharged"] and sorted(rep["caveat1"]["open_cells"]) == sorted(R.TAIL)
    assert "caveat 1 OPEN" in capsys.readouterr().out


@pytest.mark.parametrize("patched_zero,discharged", [(True, True), (False, False)])
def test_a_zero_pinned_tail_cell(tmp_path, patched_zero, discharged):
    c = R.TAIL[0]

    def patch(v):
        for b in R.BANDS:
            for i in (0, 1):
                v[f"pinov:{b}_{i}"] = v[f"pinov:{b}_{i}"].copy()
                v[f"pinov:{b}_{i}"][c] = X[c]
                if patched_zero:
                    v[f"patov:{b}_{i}"] = v[f"patov:{b}_{i}"].copy()
                    v[f"patov:{b}_{i}"][c] = X[c]
    vec = vectors(tmp_path, patch=patch)
    c3(tmp_path, vec)
    rc, rep = r3(tmp_path, vec)
    assert rep["caveat1"]["ratio"][str(c)] is None
    assert (c not in rep["caveat1"]["open_cells"]) == discharged


def test_a_nonfinite_pinned_override_names_its_cells(tmp_path):
    def patch(v):
        v["pinov:Pion_0"] = v["pinov:Pion_0"].copy()
        v["pinov:Pion_0"][11] = np.nan
    vec = vectors(tmp_path, patch=patch)
    c3(tmp_path, vec)
    rc, rep = r3(tmp_path, vec)
    assert rc == 1 and 11 in rep["sanity_stop_cells"]


def test_r3_stops_when_the_tail_is_not_the_declarations(tmp_path, monkeypatch, capsys):
    vec = vectors(tmp_path)
    c3(tmp_path, vec)
    monkeypatch.setattr(R, "TAIL", R.TAIL[1:])
    rc, rep = r3(tmp_path, vec)
    assert rc == 1 and not rep["tail_matches_declaration"] and not rep["sanity_stop_cells"]

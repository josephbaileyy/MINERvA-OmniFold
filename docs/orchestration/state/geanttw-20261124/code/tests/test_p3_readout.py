"""p3_readout.py on S5's committed production_cov.npz and synthetic unfold vectors. A two-universe band is rank one
(wcov([u0, u1]) = d d' / 4, d = u0 - u1), so pinned vectors that reproduce S5's bands are built from them."""
import importlib.util
import json
import shutil
from pathlib import Path

import numpy as np
import pytest

CODE = Path(__file__).resolve().parents[1]
REPO = CODE.parents[4]
_s = importlib.util.spec_from_file_location("p3r", CODE / "p3_readout.py")
R = importlib.util.module_from_spec(_s)
_s.loader.exec_module(R)
Z = np.load(REPO / R.PROD, allow_pickle=False)
X = Z["cells_x_EU"]


def from_band(S):
    """(u0, u1) with wcov([u0, u1]) = S, for a rank-one PSD S."""
    j = int(np.argmax(np.diag(S)))
    d = 2 * S[:, j] / np.sqrt(S[j, j])
    return X + d / 2, X - d / 2


def vectors(tmp, pin=None, pinov_scale=1.0, patov_scale=1.0, patch=None):
    v = {"cells_x": X.copy(), "area": Z["area"].copy()}
    for b in R.BANDS:
        u0, u1 = from_band(Z[f"band_GEANT_{b}"]) if pin is None else pin(b)
        v[f"pin:{b}_0"], v[f"pin:{b}_1"] = u0, u1
        v[f"pinov:{b}_0"], v[f"pinov:{b}_1"] = X + (u0 - X) * pinov_scale, X + (u1 - X) * pinov_scale
        v[f"patov:{b}_0"], v[f"patov:{b}_1"] = X + (u0 - X) * patov_scale, X + (u1 - X) * patov_scale
    if patch:
        patch(v)
    p = tmp / "vec.npz"
    np.savez(p, **v)
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
    assert all(rep["bands"][b]["rel"] <= 1e-10 for b in R.BANDS)


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


def test_r3_pinned_side_is_ms_own_when_not_reproduced(tmp_path):
    def pin(b):
        u0, u1 = from_band(Z[f"band_GEANT_{b}"])
        return u0 * (1 + 1e-6), u1
    vec = vectors(tmp_path, pin=pin)
    c3(tmp_path, vec)
    rc, rep = r3(tmp_path, vec)
    assert rc == 0 and rep["pinned_side"] == "M's pinned run"


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


def test_extract_uses_s5s_cells(tmp_path):
    repo = tmp_path / "repo"
    (repo / R.S5).parent.mkdir(parents=True)
    (repo / R.S5).write_text(
        "import numpy as np\n"
        "PIN = {'E_U': ('eu', 'ok')}\n"
        "def sha(p):\n    return 'ok'\n"
        "class Cells:\n"
        "    def __init__(self):\n        self.x = np.arange(3.0) + 1; self.area = np.ones(3)\n"
        "    def vec(self, path):\n        return np.full(3, float(len(str(path))))\n")
    out = tmp_path / "v.npz"
    assert R.main(["extract", "--repo", str(repo), "--outs", str(tmp_path / "o"), "--out", str(out)]) == 0
    v = np.load(out)
    assert len(v.files) == 2 + 18 and "patov:Proton_1" in v.files


def test_extract_refuses_another_e_u(tmp_path):
    repo = tmp_path / "repo"
    (repo / R.S5).parent.mkdir(parents=True)
    (repo / R.S5).write_text("PIN = {'E_U': ('eu', 'want')}\ndef sha(p):\n    return 'other'\n")
    assert R.main(["extract", "--repo", str(repo), "--outs", "o", "--out", str(tmp_path / "v.npz")]) == 2

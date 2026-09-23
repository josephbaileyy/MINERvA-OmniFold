"""ISSUE-30: the point-cloud projection must not divide by the reco efficiency.

Pure numpy, no ROOT, no TensorFlow. `pet/pointcloud_projection.py` used to pass
sum(w | pass_truth & pass_reco) / sum(w | pass_truth) as `extract_cross_section_nd`'s
completeness, although `w_push` is already acceptance-corrected (step 2 assigns weights
to the truth-only-miss rows). These tests fix a toy whose answer is known in closed form
and check the projection lands on it for every acceptance, including one where the old
construction would have been off by exactly 1/eff.
"""
import os
import subprocess
import sys
import unittest
from pathlib import Path

import numpy as np

ND = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ND / "pet"))
sys.path.insert(0, str(ND))

import pointcloud_projection as pp  # noqa: E402

PT_EDGES = np.array([0.0, 0.5, 1.0, 2.0])
OBS_EDGES = np.array([0.0, 0.2, 0.6, 1.0])
FLUX = np.array([2.0, 3.0, 5.0])
DATA_POT = 7.0
N_NUC = 11.0


def _toy(n_per_cell=40, eff=0.5, seed=0):
    """Every (pT, obs) cell gets n_per_cell truth rows, all pass_truth; a fraction `eff`
    of each cell passes reco. w_push is a cell-dependent constant, so the unfolded
    counts per cell are known exactly."""
    rng = np.random.default_rng(seed)
    pt, obs, wt, wp, reco = [], [], [], [], []
    for i in range(len(PT_EDGES) - 1):
        for j in range(len(OBS_EDGES) - 1):
            pt.append(rng.uniform(PT_EDGES[i], PT_EDGES[i + 1], n_per_cell))
            obs.append(rng.uniform(OBS_EDGES[j], OBS_EDGES[j + 1], n_per_cell))
            wt.append(rng.uniform(0.5, 1.5, n_per_cell))
            wp.append(np.full(n_per_cell, 1.0 + i + 0.5 * j))
            r = np.zeros(n_per_cell, bool)
            r[: int(round(eff * n_per_cell))] = True
            reco.append(r)
    cat = np.concatenate
    n = sum(map(len, pt))
    return dict(pt=cat(pt), obs=cat(obs), w_truth=cat(wt), w_push=cat(wp),
                pass_reco=cat(reco), pass_truth=np.ones(n, bool))


def _expected(t, base=None):
    """dsigma/dobs by hand: sum(w_push*w_truth) per cell, 1e4 / (flux*N*POT*dpT*dobs),
    then integrate out pT (multiply by dpT and sum). No completeness divisor."""
    sel = t["pass_truth"] if base is None else (t["pass_truth"] & base)
    counts, _ = np.histogramdd(np.column_stack([t["pt"][sel], t["obs"][sel]]),
                               bins=[PT_EDGES, OBS_EDGES],
                               weights=(t["w_push"] * t["w_truth"])[sel])
    dpt = np.diff(PT_EDGES)[:, None]
    dobs = np.diff(OBS_EDGES)[None, :]
    xs = counts * 1.0e4 / (FLUX[:, None] * N_NUC * DATA_POT * dpt * dobs)
    return (xs * dpt).sum(axis=0)


def _project(t, base=None):
    return pp.project_xsec_1d_from_arrays(
        t["obs"], OBS_EDGES, pt=t["pt"], pt_edges=PT_EDGES, w_push=t["w_push"],
        w_truth=t["w_truth"], pass_truth=t["pass_truth"], pass_reco=t["pass_reco"],
        flux=FLUX, data_pot=DATA_POT, n_nucleons=N_NUC, base=base)


class ProjectionDoesNotDivideByAcceptance(unittest.TestCase):
    def test_all_truth_rows_match_closed_form(self):
        t = _toy(eff=0.5)
        np.testing.assert_allclose(_project(t), _expected(t), rtol=1e-12)

    def test_result_is_independent_of_reco_efficiency(self):
        # Same truth rows and weights; only pass_reco changes. A projection that divides
        # by acceptance moves by 1/eff; the corrected one must not move at all.
        results = [_project(_toy(eff=e)) for e in (1.0, 0.5, 0.25)]
        for r in results[1:]:
            np.testing.assert_allclose(r, results[0], rtol=1e-12)

    def test_the_old_construction_would_fail_this_test(self):
        # Power check, in the direction the test acts: rebuild the pre-fix divisor and
        # show it misses the closed form by exactly 1/eff (uniform eff per cell here).
        from xsec_nd import extract_cross_section_nd, project_marginal
        t = _toy(eff=0.25)
        edges2 = [PT_EDGES, OBS_EDGES]
        c = np.column_stack([t["pt"], t["obs"]])
        counts, _ = np.histogramdd(c, bins=edges2, weights=t["w_push"] * t["w_truth"])
        denom, _ = np.histogramdd(c, bins=edges2, weights=t["w_truth"])
        r = t["pass_reco"]
        ofin, _ = np.histogramdd(c[r], bins=edges2, weights=t["w_truth"][r])
        comp = ofin / denom
        xs2, _ = extract_cross_section_nd(counts, comp, FLUX, DATA_POT, N_NUC, edges2)
        old = project_marginal(xs2, edges2, drop_axes=[0])
        # comp is a weighted fraction, not exactly 0.25, so compare to it cell by cell.
        self.assertFalse(np.allclose(old, _project(t), rtol=1e-3))
        xs_exp = counts * 1.0e4 / (FLUX[:, None] * N_NUC * DATA_POT
                                   * np.diff(PT_EDGES)[:, None] * np.diff(OBS_EDGES)[None, :])
        old_exp = (xs_exp / comp * np.diff(PT_EDGES)[:, None]).sum(axis=0)
        np.testing.assert_allclose(old, old_exp, rtol=1e-12)

    def test_base_subset_matches_closed_form(self):
        t = _toy(eff=0.5, seed=3)
        base = np.random.default_rng(9).random(t["pt"].size) < 0.7
        np.testing.assert_allclose(_project(t, base=base), _expected(t, base=base),
                                   rtol=1e-12)

    def test_cells_with_no_reco_row_stay_zero(self):
        # The reco efficiency is kept as the reporting mask: a (pT, obs) cell the
        # detector never saw contributes nothing, as it did before the fix.
        t = _toy(eff=0.5)
        dead = (t["pt"] >= 1.0) & (t["obs"] >= 0.6)          # cell (2, 2)
        t["pass_reco"] = t["pass_reco"] & ~dead
        got = _project(t)
        exp_all = _expected(t)
        exp_masked = exp_all - _expected(t, base=dead)
        np.testing.assert_allclose(got, exp_masked, rtol=1e-12)
        self.assertLess(got[2], exp_all[2])


class ModuleImportsWithoutRoot(unittest.TestCase):
    def test_import_does_not_load_root(self):
        code = ("import sys; sys.path[:0] = [%r, %r]; import pointcloud_projection; "
                "print('ROOT' in sys.modules)" % (str(ND / "pet"), str(ND)))
        out = subprocess.run([sys.executable, "-c", code], capture_output=True, text=True,
                             env={**os.environ, "PYTHONPATH": ""})
        self.assertEqual(out.returncode, 0, out.stderr)
        self.assertEqual(out.stdout.strip(), "False")


if __name__ == "__main__":
    unittest.main()

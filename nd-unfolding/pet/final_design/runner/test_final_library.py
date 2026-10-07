"""Final-library distortions added by the study: truth-weight products and R2 on the PET path."""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pytest

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import design_inputs as ri  # noqa: E402


class FFD:
    SCALAR_COLS = {"pt": 0, "pparallel": 1, "eavail": 2, "q3": 3}


def truth(n=5000, seed=0):
    rng = np.random.default_rng(seed)
    return {"pt": rng.uniform(0.1, 2, n), "ppar": rng.uniform(1, 10, n),
            "eavail": rng.exponential(0.5, n), "q3": rng.uniform(0.2, 3, n),
            "n_p": rng.integers(0, 5, n), "n_n": rng.integers(0, 5, n),
            "n_pipm": rng.integers(0, 3, n), "n_pi0": rng.integers(0, 2, n)}


def test_product_is_the_product_of_the_factors():
    t = truth()
    a, b = ri.get_distortion("D1_p0.350"), ri.get_distortion("D4c_p_up")
    ab = ri.get_distortion("D1_p0.350*D4c_p_up")
    assert ab.needs_species and ab.reco_energy_scale is None and ab.muon_momentum_scale is None
    np.testing.assert_allclose(ab.raw(t), np.asarray(a.raw(t)) * np.asarray(b.raw(t)))
    assert ab.content_hash() != a.content_hash()
    with pytest.raises(SystemExit):
        ri.get_distortion("D1_p0.350*R1_x1.05")


def test_r2_spec_routes_to_muon_scale_and_keeps_truth():
    d = ri.get_distortion("R2_x1.01+D1_p0.350")
    assert d.muon_momentum_scale == pytest.approx(1.01) and d.reco_energy_scale is None
    t = truth()
    np.testing.assert_allclose(d.raw(t), ri.get_distortion("D1_p0.350").raw(t))
    alone = ri.get_distortion("R2_x0.99")
    assert alone.muon_momentum_scale == pytest.approx(0.99)


def test_apply_muon_scale_masked_rows_only():
    rng = np.random.default_rng(1)
    n = 200
    rs = np.c_[rng.uniform(.1, 2, n), rng.uniform(1, 10, n), rng.exponential(.5, n),
               rng.uniform(.3, 3, n)].astype(np.float32)
    p = rng.uniform(1, 10, (n, 3)).astype(np.float32)
    m = 0.1056583755
    E = np.sqrt((p.astype(np.float64) ** 2).sum(1) + m * m)
    mu = np.c_[p, E, rng.uniform(-3, 3, n), 1.0 / np.linalg.norm(p, axis=1), np.ones(n)
               ].astype(np.float32)
    mask = rng.random(n) < 0.5
    rs2, mu2 = ri.apply_muon_scale(FFD, rs, mu, mask, 1.01)
    np.testing.assert_array_equal(rs2[~mask], rs[~mask])
    np.testing.assert_array_equal(mu2[~mask], mu[~mask])
    np.testing.assert_allclose(rs2[mask, 0], rs[mask, 0] * 1.01, rtol=1e-6)
    np.testing.assert_allclose(mu2[mask, :3], mu[mask, :3] * 1.01, rtol=1e-6)
    p2 = (mu2[mask, :3].astype(np.float64) ** 2).sum(1)
    np.testing.assert_allclose(mu2[mask, 3], np.sqrt(p2 + m * m), rtol=1e-5)
    np.testing.assert_allclose(mu2[mask, 5], mu[mask, 5] / 1.01, rtol=1e-6)
    np.testing.assert_array_equal(rs2[mask, 2], rs[mask, 2])        # E_avail unchanged
    # q3 recomputed with the unchanged recoil q0
    q0, _ = ri.dist.recoil_q0(rs[mask, 0], rs[mask, 1], rs[mask, 3])
    q3 = ri.dist.reco_q3(1.01 * rs[mask, 0].astype(np.float64), 1.01 * rs[mask, 1], q0)
    np.testing.assert_allclose(rs2[mask, 3], q3, rtol=1e-5)


def test_scaled_reader_r2_matches_loader_transform():
    rng = np.random.default_rng(2)
    n = 100
    table = np.c_[rng.uniform(.1, 2, n), rng.uniform(1, 10, n), rng.exponential(.5, n),
                  rng.uniform(.3, 3, n)].astype(np.float32)
    table[5] = -9999.0                                   # a miss sentinel row
    cols = FFD.SCALAR_COLS

    def read(which, column, rows):
        return table[np.asarray(rows), cols[column]].astype(np.float64)
    rows_scaled = np.arange(0, n, 2)
    rd = ri.scaled_reader(np, read, None, (rows_scaled, 1.01))
    allrows = np.arange(n)
    mask = np.isin(allrows, rows_scaled) & (table[:, 3] > -999)
    rs2, _ = ri.apply_muon_scale(FFD, table, None, mask, 1.01)
    for c in ("pt", "pparallel", "q3", "eavail"):
        np.testing.assert_allclose(rd("reco", c, allrows), rs2[:, cols[c]].astype(np.float64),
                                   rtol=1e-6)
    assert rd("reco", "q3", [5])[0] == -9999.0

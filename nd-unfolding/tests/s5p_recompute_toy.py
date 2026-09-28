"""A synthetic s5p world in the production file formats, for the independent evaluator's tests.

A 4^5 fine grid (J edges a subset of its edges), a chosen set of supported J cells, predictions, a fixed V,
lateral endpoints, data jitters, D16/M1 shift files, calibration and power products with the production meta
fields, and controller status files. The null process is a Gaussian fine-cell fluctuation around the null truth;
an alternative multiplies the truth by a smooth factor along pT.
"""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np

AXES = ("pt", "pz", "eavail", "q3", "W")
FINE = {"pt": [0.0, 0.3, 0.55, 0.85, 4.5], "pz": [1.5, 3.5, 5.0, 6.0, 60.0], "eavail": [0.0, 0.4, 1.0, 1.5, 100.0],
        "q3": [0.0, 1.2, 1.6, 2.0, 100.0], "W": [0.0, 1.4, 1.8, 2.2, 100.0]}
JEDGES = {"pt": [0.0, 0.55, 0.85, 4.5], "pz": [1.5, 3.5, 6.0, 60.0], "eavail": [0.0, 0.4, 1.5, 100.0],
          "q3": [0.0, 1.2, 2.0, 100.0], "W": [0.0, 1.4, 2.2, 100.0]}
BANDS = ["BeamAngleX", "Muon_Energy_MINOS"]
NULL_KEYS = ["MnvTune_v1", "GiBUU_2019"]
SEED_BASE = {"MnvTune_v1": 1200000, "GiBUU_2019": 1280000}


def volumes():
    v = np.ones(1)
    for ax in AXES:
        v = np.multiply.outer(v, np.diff(FINE[ax]))
    return v.ravel()


def supported_cells(rng, n=40):
    return sorted(int(c) for c in rng.choice(243, size=n, replace=False))


class Toy:
    def __init__(self, root: Path, seed: int = 7, n_supported: int = 40, noise: float = 0.01):
        self.root = Path(root)
        self.root.mkdir(parents=True, exist_ok=True)
        self.rng = np.random.default_rng(seed)
        self.vol = volumes()
        self.nf = self.vol.size
        self.supported = supported_cells(self.rng, n_supported)
        self.truth = {k: self.rng.uniform(0.5, 2.0, self.nf) * 1e-38 for k in NULL_KEYS}
        self.noise = noise
        self.names = [f"J{c}" for c in self.supported]
        self._cell = self._fine_to_j()
        self.write_static()

    def _fine_to_j(self):
        idx = []
        for ax in AXES:
            fe, je = np.array(FINE[ax]), np.array(JEDGES[ax])
            c = 0.5 * (fe[1:] + fe[:-1])
            idx.append(np.searchsorted(je, c, side="right") - 1)
        g = np.meshgrid(*idx, indexing="ij")
        coarse = np.ravel_multi_index([x.ravel() for x in g], [3] * 5)
        pos = -np.ones(243, int)
        pos[self.supported] = np.arange(len(self.supported))
        return pos[coarse]

    def jint(self, x):
        """Brute-force J integrals (a loop, independent of the evaluator's bincount)."""
        out = np.zeros(len(self.supported))
        for i in range(self.nf):
            if self._cell[i] >= 0:
                out[self._cell[i]] += x[i] * self.vol[i]
        return out

    def npz(self, name, **arrays):
        p = self.root / name
        p.parent.mkdir(parents=True, exist_ok=True)
        np.savez(p, **arrays)
        return str(p)

    def edges(self):
        return {f"edges_{ax}": np.array(FINE[ax]) for ax in AXES}

    def fine_noise(self, rng, scale):
        return rng.standard_normal(self.nf) * scale

    def write_static(self):
        r = self.rng
        n = len(self.supported)
        a = r.standard_normal((n, n))
        # V on the scale of the J integrals' fluctuations
        jscale = self.jint(self.truth["MnvTune_v1"]) * self.noise
        corr = a @ a.T / n + np.eye(n)
        d = 1 / np.sqrt(np.diag(corr))
        self.V = (corr * np.outer(d, d)) * np.outer(jscale, jscale) * 1.0
        self.v_path = self.npz("V.npz", V=self.V, names=np.array(self.names))
        self.pred = {}
        for k in NULL_KEYS:
            self.pred[k] = self.npz(f"pred_{k}.npz", xsec_flat=self.truth[k],
                                    sumw2_flat=(self.truth[k] * 0.003) ** 2, **self.edges())
        self.lat = {}
        base = self.truth["MnvTune_v1"]
        for b in BANDS:
            e0 = base * (1 - 0.01 * r.uniform(0, 1, self.nf))
            e1 = base * (1 + 0.01 * r.uniform(0, 1, self.nf))
            self.lat[b] = [self.npz(f"lat/{b}_0.npz", xsec_flat=e0), self.npz(f"lat/{b}_1.npz", xsec_flat=e1)]
        self.jitters = [self.npz(f"jit/j{j}.npz", xsec_flat=base * (1 + 0.002 * r.standard_normal(self.nf)))
                        for j in range(1, 21)]
        self.shift = {}
        self.m1 = {}
        for k in NULL_KEYS:
            dp = r.standard_normal((16, n)) * jscale * 0.05
            self.shift[k] = self.npz(f"f4/D16-{k}.npz", D_J=dp.mean(0), se_J=dp.std(0, ddof=1) / 4, d_pairs=dp,
                                     f_B_mean=self.jint(self.truth[k]), names=np.array(self.names))
        dm = r.standard_normal((1, n)) * jscale * 0.1
        self.m1["GiBUU_2019"] = self.npz("m1/fine-minus-mid-GiBUU.npz", D_J=dm[0], se_J=np.zeros(n), d_pairs=dm,
                                         f_B_mean=self.jint(self.truth["GiBUU_2019"]), names=np.array(self.names))
        self.data = self.npz("data.npz", xsec_flat=base.copy())
        self.contract = {"measurement": {"partition_J": {"edges": JEDGES, "supported_cells": self.supported}}}

    def set_data(self, x):
        self.data = self.npz("data.npz", xsec_flat=x)

    def product(self, kind, key, seed, truth, rng=None, partial=False):
        rng = rng or np.random.default_rng([seed, 99])
        x = truth + self.fine_noise(rng, truth * self.noise)
        meta = {"schema": "s5p-null-experiment/1", "pseudo_seed": seed,
                "nuisance_draw": {"lateral_z": {b: float(rng.standard_normal()) for b in BANDS},
                                  "normalization_z": float(rng.standard_normal())}}
        sub = f"cal/{key}/cal_{key}_s{seed}" if kind == "cal" else f"pow/{key}/pow_{key}_s{seed}"
        name = sub + (".partial-123.npz" if partial else ".npz")
        return self.npz(name, xsec_flat=x, xtrue_flat=truth, meta=np.array(json.dumps(meta)))

    def calibration(self, key, n, skip=()):
        truth = self.truth[key]
        for i in range(n):
            if i in skip:
                continue
            self.product("cal", key, SEED_BASE[key] + i, truth)

    def power(self, set_key, n, null_key, factor):
        truth = self.truth[null_key] * factor
        for i in range(n):
            self.product("pow", set_key, 1451000 + i, truth)

    def status(self, key, B, stop, reason):
        p = self.root / "status" / f"{key}-{'final' if stop else 'B' + str(B)}.json"
        p.parent.mkdir(parents=True, exist_ok=True)
        rec = {"null": key, "B": B, "max": 1999, "stop": stop, "reason": reason}
        p.write_text(json.dumps(rec))
        if stop:
            (self.root / "status" / f"{key}-B{B}.json").write_text(json.dumps(rec))
        return str(p)

    def design(self, power=None, mins=None):
        mins = mins or {}
        d = {"alpha_family": 0.05, "shift_coefficients": [0.0, 0.5, 1.0], "v_sha256": None,
             "lateral_endpoints": self.lat, "data_jitters": self.jitters, "data_central": self.data,
             "process_shift": {k: {"path": self.shift[k], "sha256": _sha(self.shift[k]), "mode": "bias_aligned_upper"}
                               for k in NULL_KEYS},
             "m1_shift": {"MnvTune_v1": {"none": "analysis MC"},
                          "GiBUU_2019": {"path": self.m1["GiBUU_2019"], "sha256": _sha(self.m1["GiBUU_2019"]),
                                         "kappa": 2, "kappa_robust": 3}},
             "nulls": {}, "power": power or {}}
        for i, k in enumerate(NULL_KEYS):
            d["nulls"][k] = {"prediction": self.pred[k], "domain": "pz_lt_6" if k == "GiBUU_2019" else None,
                             "calibration_glob": str(self.root / f"cal/{k}/cal_{k}_s*.npz"),
                             "calibration_n": {"max": 1999, "min": mins.get(k, 0),
                                               "sequential_status": str(self.root / "status" / f"{k}-final.json")},
                             "surrogate_seed0": 1700000 + 20000 * i}
        return d


def _sha(p):
    import hashlib
    return hashlib.sha256(open(p, "rb").read()).hexdigest()

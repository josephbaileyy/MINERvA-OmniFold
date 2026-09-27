#!/usr/bin/env python3
"""s5p Stage 7: background-inclusive pseudo experiments at a generator hypothesis, with nuisance draws.

One product per pseudo seed. The experiment is exactly ``s5n_pseudo.build_pseudo`` (MC split into the
unfolding half A and the pseudo-data source half B; background into source C and template D; Poisson
pseudo-data; refinement; the declared estimator configuration) with two additions:

* the TRUTH is the hypothesis: a generator-null ratio file (``s5p_truths.hypothesis_weight``): kind ``fine``
  (review round 1 F2: the generator's own fine-grid shape, coarse-cell integrals exactly N's) or kind ``coarse``
  (N_c / MnvTune_c per coarse cell, MnvTune's within-cell shapes), rate kept;
* NUISANCES are drawn per experiment from the declared priors and applied to the pseudo-data SOURCE only
  (rows of B and C; the unfolding MC A and the template D keep the CV, as the analysis does):
  - flux: one PPFX universe u, uniform over the bank's Flux universes: signal source rows' reco weights x
    (wr_u / w_reco), background source rows' weights x (bkgw_u / bkg_w);
  - interaction model: EVERY non-flux, non-detector vertical band of the bank (the GENIE, 2p2h and FSI knobs; the
    GEANT bands are detector bands and are drawn below only, so none is applied twice) at one of its universes,
    independently and uniformly per band (a +-1 sigma pair: either endpoint; 2p2h: one of three), so the drawn
    prior's covariance is the analysis's band sum to first order (review round 2 H1: until then ONE universe of
    all 69 was drawn, a variance ~34x too small). The product of the chosen universes' weight ratios is applied
    COHERENTLY to the background source weights and to the signal source's RESPONSE: signal reco weights x
    prod(wr_v / w_reco) x g_f, g_f = sum w_truth / sum w_truth prod(wt_v / w_truth) over the source rows of the
    row's fine truth cell, so the source truth is unchanged cell by cell (the hypothesis fixes the truth; the
    knobs move only the within-fine-cell composition and hence the detector response; review round 1 F6);
    truth-failing rows get the plain factor;
  - weight-only detector bands (``--detector-bands``, default MinosEfficiency, GEANT_Neutron/Pion/Proton): each at
    its -1 or +1 sigma endpoint with probability 1/2 each (a discrete draw), signal source reco weights x
    (wr / w_reco), background x (bkgw / bkg_w); a band's universe is read from ``--detector-dir`` when that
    directory carries it, otherwise from the bank (which carries the GEANT bands but not MinosEfficiency);
  the draws are recorded in the product. Lateral bands and the flat normalization are applied downstream as a
  declared linear surrogate on the unfolded functionals (z_b Delta_b and 1 + 0.014 z), their z recorded here.

DEVELOPMENT constructions for the process-sensitivity checks (review round 1 F4; never calibration products):
``--expectation`` replaces every Poisson draw of ``build_pseudo`` by its mean (the pseudo-data are B's reco rows at
2 w_reco r and C's background at 2 w_bkg, the logic of ``build_pseudo`` itself, unchanged), requires
``--no-nuisance``; ``--mc-fraction quarter`` unfolds with half of A (``s5c_pseudo.half_mask`` at key split + 7777)
at weight x4 instead of A at x2, so that the pseudo process's dependence on the unfolding-MC size is measured at
fixed pseudo-data.

MEASURES: one null (or alternative) experiment of the frozen joint-test calibration. CANNOT AUTHORIZE: a
p-value, size or power by itself.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import time
from pathlib import Path

import numpy as np

_ND = Path(__file__).resolve().parent
if str(_ND) not in sys.path:
    sys.path.insert(0, str(_ND))
import s5c_pseudo  # noqa: E402
import s5c_unfold  # noqa: E402
import s5e_candidate  # noqa: E402
import s5n_pseudo  # noqa: E402
import s5p_numerics  # noqa: E402
import s5p_truths  # noqa: E402
import s5p_universe  # noqa: E402

DETECTOR_BANDS = ("MinosEfficiency", "GEANT_Neutron", "GEANT_Pion", "GEANT_Proton")
LATERAL_BANDS = ("BeamAngleX", "BeamAngleY", "MuonResolution", "Muon_Energy_MINERvA", "Muon_Energy_MINOS")


def ratio(num: np.ndarray, den: np.ndarray) -> np.ndarray:
    den = np.asarray(den, float)
    return np.where(den > 0, np.asarray(num, float) / np.where(den > 0, den, 1.0), 1.0)


def model_bands(bank: Path) -> list[str]:
    """The bank's interaction-model universes: every non-flux vertical band except the detector (GEANT) bands."""
    return sorted({p.stem.removesuffix("_bkgw") for p in bank.glob("*_bkgw.npy")
                   if not p.stem.startswith("Flux_") and not p.stem.startswith("GEANT_")})


def model_groups(universes: list[str]) -> dict[str, list[str]]:
    """Universes grouped into bands by their stem (``MaRES_0``, ``MaRES_1`` -> ``MaRES``; ``2p2h_0..2``)."""
    out: dict[str, list[str]] = {}
    for u in sorted(universes):
        stem, _, idx = u.rpartition("_")
        if not stem or not idx.isdigit():
            raise ValueError(f"universe {u} has no _<index> suffix")
        out.setdefault(stem, []).append(u)
    return out


class ModelCache:
    """The interaction-model universes' weight ratios (ratio 1 where the CV weight is zero). By default each
    experiment STREAMS its chosen universes from the bank (34 bands x 3 arrays, ~13 GB read against a ~550 s
    unfold; the full-MC signal has 32.8M rows, so a preload of all 69 universes would need ~18 GB); ``preload``
    reads them once (tests and small inputs)."""

    def __init__(self, bank: Path, universes: list[str], inputs: dict, bkg: dict, preload: bool = False):
        self.bank = bank
        self.wr, self.wt, self.bw = (np.asarray(x, float) for x in (inputs["w_reco"], inputs["w_truth"], bkg["bkg_w"]))
        self.r = {u: self._ratios(u) for u in universes} if preload else {}

    def _ratios(self, u: str) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
        w = s5p_universe.weights(self.bank, u)
        return ratio(w["wr"], self.wr), ratio(w["wt"], self.wt), ratio(w["bkgw"], self.bw)

    def product(self, chosen: list[str]) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
        k_wr, k_wt, k_b = np.ones(self.wr.size), np.ones(self.wt.size), np.ones(self.bw.size)
        for u in chosen:
            a, b, c = self.r[u] if u in self.r else self._ratios(u)
            k_wr *= a
            k_wt *= b
            k_b *= c
        return k_wr, k_wt, k_b


def draw(rng: np.random.Generator, flux_ids: list[int], groups: dict[str, list[str]],
         det_bands: tuple = DETECTOR_BANDS) -> dict:
    return {"flux": int(rng.choice(flux_ids)),
            "model": {s: str(rng.choice(groups[s])) for s in sorted(groups)},
            "detector": {b: int(rng.integers(0, 2)) for b in det_bands},
            "lateral_z": {b: float(rng.normal()) for b in LATERAL_BANDS}, "normalization_z": float(rng.normal())}


def truth_preserving(k_truth: np.ndarray, inputs: dict, source: np.ndarray) -> np.ndarray:
    """g per row: sum w_truth / sum w_truth k_truth over the source's truth-passing rows of the row's fine truth
    cell, so that sum_cell w_truth k g = sum_cell w_truth over the source; 1 for rows outside every cell."""
    gen, edges = np.asarray(inputs["MCgen"]), inputs["edges"]
    wt = np.asarray(inputs["w_truth"], float)
    inside, idx = s5p_truths.cell_of(gen, edges)
    rows = np.flatnonzero(inside)
    pt = np.asarray(inputs["pass_truth"], bool)[rows]
    rows = rows[pt]
    flat = np.ravel_multi_index([i[pt] for i in idx], [len(e) - 1 for e in edges])
    sel = np.asarray(source, bool)[rows]
    n = int(np.prod([len(e) - 1 for e in edges]))
    s0 = np.bincount(flat[sel], weights=wt[rows][sel], minlength=n)
    s1 = np.bincount(flat[sel], weights=(wt * k_truth)[rows][sel], minlength=n)
    g = np.ones(gen.shape[0])
    g[rows] = np.where(s1[flat] > 0, s0[flat] / np.where(s1[flat] > 0, s1[flat], 1.0), 1.0)
    return g


def detector_source(det_dir: Path | None, bank: Path, tag: str) -> Path:
    """The directory that carries detector universe ``tag``: the detector dump if it has it, else the bank."""
    for d in ([det_dir] if det_dir is not None else []) + [bank]:
        if (d / f"{tag}_wr.npy").exists():
            return d
    raise FileNotFoundError(f"no detector universe {tag} in {det_dir} or {bank}")


def drawn_detector_bands(spec: str, no_nuisance: bool, det_dir: Path | None, bank: Path) -> tuple:
    """The detector bands this run draws, each checked present (dump or bank) before any unfold; none under
    --no-nuisance (s5p 2026-09-27: the check refused the no-nuisance F4 lines for an undrawn band)."""
    if no_nuisance:
        return ()
    bands = tuple(b for b in spec.split(",") if b)
    for b in bands:
        for i in (0, 1):
            detector_source(det_dir, bank, f"{b}_{i}")
    return bands


def source_factors(d: dict, inputs: dict, bkg: dict, bank: Path, det_dir: Path | None,
                   source: np.ndarray | None = None, cache: ModelCache | None = None) -> tuple[np.ndarray, np.ndarray]:
    """Multiplicative factors for every signal row's reco weight and every background row's weight
    (``source``: the signal source rows over which the model universes' truth is renormalized)."""
    fs = np.ones(inputs["w_reco"].shape[0])
    fb = np.ones(bkg["bkg_w"].shape[0])
    wr, bw = np.asarray(inputs["w_reco"], float), np.asarray(bkg["bkg_w"], float)
    w = s5p_universe.weights(bank, f"Flux_{d['flux']}")
    fs *= ratio(w["wr"], wr)
    fb *= ratio(w["bkgw"], bw)
    chosen = list(d["model"].values())
    cache = cache if cache is not None else ModelCache(bank, chosen, inputs, bkg)
    k_wr, k_wt, k_b = cache.product(chosen)
    fb *= k_b
    src = np.ones(fs.size, bool) if source is None else source
    fs *= k_wr * truth_preserving(k_wt, inputs, src)
    for b, i in d["detector"].items():
        wd = s5p_universe.weights(detector_source(det_dir, bank, f"{b}_{i}"), f"{b}_{i}")
        fs *= ratio(wd["wr"], wr)
        fb *= ratio(wd["bkgw"], bw)
    return fs, fb


class ExpectationRNG:
    """Stands in for build_pseudo's generator: every Poisson draw returns its mean."""

    def __init__(self, seed=None):
        self.seed = seed

    def poisson(self, lam):
        return np.asarray(lam, float).copy()


def build(ui: dict, ub: dict, split: int, seed: int, expectation: bool, mc_fraction: str):
    if expectation:
        orig_rng = s5n_pseudo.np.random.default_rng
        s5n_pseudo.np.random.default_rng = ExpectationRNG
        try:
            exp, x_true, info = s5n_pseudo.build_pseudo(ui, ub, "hypothesis", 1.0, split, seed, None)
        finally:
            s5n_pseudo.np.random.default_rng = orig_rng
    else:
        exp, x_true, info = s5n_pseudo.build_pseudo(ui, ub, "hypothesis", 1.0, split, seed, None)
    if mc_fraction == "quarter":
        keep = s5c_pseudo.half_mask(exp["MCgen"].shape[0], split + 7777)
        exp = dict(exp)
        for k in ("MCgen", "MCreco", "pass_reco", "pass_truth"):
            exp[k] = exp[k][keep]
        exp["w_truth"], exp["w_reco"] = 2.0 * exp["w_truth"][keep], 2.0 * exp["w_reco"][keep]
        info = dict(info, n_unfolding_mc=int(keep.sum()))
    return exp, x_true, info


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n", 1)[0])
    ap.add_argument("--npz", type=Path, required=True)
    ap.add_argument("--bkg", type=Path, required=True)
    ap.add_argument("--bank", type=Path, required=True)
    ap.add_argument("--detector-dir", type=Path, default=None)
    ap.add_argument("--detector-bands", default=",".join(DETECTOR_BANDS), help="comma list of the drawn detector bands")
    ap.add_argument("--expect-npz-sha256", required=True)
    ap.add_argument("--expect-bkg-sha256", required=True)
    ap.add_argument("--hypothesis", type=Path, required=True, help="s5p-coarse-ratio/1 file N_c / MnvTune_c")
    ap.add_argument("--alternative", type=Path, default=None, help="optional extra truth ratio on top (power studies)")
    ap.add_argument("--alternative-truth", default=None)
    ap.add_argument("--alternative-amplitude", type=float, default=1.0)
    ap.add_argument("--no-nuisance", action="store_true", help="DEVELOPMENT: nuisances at CV")
    ap.add_argument("--expectation", action="store_true", help="DEVELOPMENT: Poisson draws replaced by their means")
    ap.add_argument("--mc-fraction", choices=("half", "quarter"), default="half", help="DEVELOPMENT: unfolding-MC size")
    ap.add_argument("--config", choices=("R",), default="R")
    ap.add_argument("--capacity", default=None)
    ap.add_argument("--iters", type=int, default=5)
    ap.add_argument("--pseudo-seeds", required=True, help="first:last")
    ap.add_argument("--estimator-seed", type=int, default=42)
    ap.add_argument("--threads", type=int, default=int(os.environ.get("SLURM_CPUS_PER_TASK", "32")))
    ap.add_argument("--tag", required=True)
    ap.add_argument("--out", type=Path, required=True)
    a = ap.parse_args(argv)
    if a.expectation and not a.no_nuisance:
        ap.error("--expectation is a development construction and needs --no-nuisance")
    s5e_candidate.install(a.config)
    s5p_truths.install(s5n_pseudo)
    capacity = s5p_numerics.s5e_trace.parse_pair(a.capacity)
    npz_sha, bkg_sha = s5n_pseudo.sha256_path(a.npz), s5n_pseudo.sha256_path(a.bkg)
    if npz_sha != a.expect_npz_sha256 or bkg_sha != a.expect_bkg_sha256:
        print("input digests differ from the expected ones", file=sys.stderr)
        return 4
    inputs = s5c_unfold.load_inputs(a.npz)
    bz = np.load(a.bkg, allow_pickle=True)
    bkg = {"bkg_reco": bz["bkg_reco"], "bkg_w": bz["bkg_w"], "bkg_nd": bz["bkg_nd"]}
    s5p_universe.check_alignment(np.load(a.bank / "cv.npz", allow_pickle=True), inputs, bkg)
    hyp = json.loads(a.hypothesis.read_text())
    r_h = s5p_truths.hypothesis_weight(inputs["MCgen"], inputs["edges"], inputs["w_truth"], hyp, 1.0)
    if a.alternative is not None:
        alt = json.loads(a.alternative.read_text())
        base = dict(inputs, w_truth=np.asarray(inputs["w_truth"], float) * r_h)
        r_h = r_h * s5n_pseudo.truth_weight(a.alternative_truth, base, a.alternative_amplitude, alt)
    flux_ids = sorted(int(p.stem.split("_")[1]) for p in a.bank.glob("Flux_*_wr.npy"))
    groups = model_groups(model_bands(a.bank))
    det_bands = drawn_detector_bands(a.detector_bands, a.no_nuisance, a.detector_dir, a.bank)
    first, last = (int(v) for v in a.pseudo_seeds.split(":"))
    a.out.mkdir(parents=True, exist_ok=True)
    status = 0
    cache = None
    for seed in range(first, last + 1):
        target = a.out / f"{a.tag}_s{seed}.npz"
        if target.exists():
            continue
        t0 = time.time()
        rng = np.random.default_rng([seed, 0x5F5])
        d = draw(rng, flux_ids, groups, det_bands) if not a.no_nuisance else None
        split = s5c_pseudo.split_key_for(seed)
        n = inputs["MCgen"].shape[0]
        is_b = s5c_pseudo.half_mask(n, split)
        is_c = s5c_pseudo.half_mask(bkg["bkg_w"].shape[0], s5n_pseudo.bkg_split_key(split))
        ui, ub = dict(inputs), dict(bkg)
        if d is not None:
            if cache is None:
                cache = ModelCache(a.bank, [u for us in groups.values() for u in us], inputs, bkg)
            fs, fb = source_factors(d, inputs, bkg, a.bank, a.detector_dir, is_b, cache)
            ui["w_reco"] = np.where(is_b, np.asarray(inputs["w_reco"], float) * fs, inputs["w_reco"])
            ub["bkg_w"] = np.where(is_c, np.asarray(bkg["bkg_w"], float) * fb, bkg["bkg_w"])
        orig = s5n_pseudo.truth_weight
        s5n_pseudo.truth_weight = lambda name, inp, amp, rr: r_h  # the hypothesis (and alternative) truth
        try:
            exp, x_true, info = build(ui, ub, split, seed, a.expectation, a.mc_fraction)
        finally:
            s5n_pseudo.truth_weight = orig
        with s5p_numerics.omnifold_capacity(capacity):
            xs, ev = s5p_numerics.unfold_one(exp, np.float32, a.estimator_seed, a.threads, a.iters)
        meta = {"schema": "s5p-null-experiment/1", "hypothesis": {"path": str(a.hypothesis), "label": hyp.get("label"),
                "sha256": s5n_pseudo.sha256_path(a.hypothesis)}, "alternative": None if a.alternative is None else
                {"path": str(a.alternative), "truth": a.alternative_truth, "amplitude": a.alternative_amplitude,
                 "sha256": s5n_pseudo.sha256_path(a.alternative)}, "nuisance_draw": d, "detector_bands": list(det_bands), "model_bands": sorted(groups), "pseudo_seed": seed,
                "split_key": split, "config": a.config, "capacity": capacity, "iters": a.iters, "experiment": info, **ev,
                "development": {"expectation": a.expectation, "mc_fraction": a.mc_fraction},
                "input_npz_sha256": npz_sha, "bkg_dump_sha256": bkg_sha,
                "code_sha256": {**s5n_pseudo.code_digests(), "s5p_nullexp.py": s5n_pseudo.sha256_path(Path(__file__).resolve())},
                "slurm_job": os.environ.get("SLURM_JOB_ID"), "seconds_unfold": round(time.time() - t0, 3)}
        rc = s5n_pseudo.write_product(target, {"xsec_flat": xs.ravel(order="C"), "xtrue_flat": np.asarray(x_true).ravel(order="C")}, meta)
        status |= rc
        print(json.dumps({"out": target.name, "rc": rc, "seconds": meta["seconds_unfold"]}))
    return status


if __name__ == "__main__":
    sys.exit(main())

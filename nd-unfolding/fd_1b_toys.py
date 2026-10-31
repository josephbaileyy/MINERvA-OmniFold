#!/usr/bin/env python3
"""1B with 4A, the toy mode (state/measurement-paper/5d-community-20261024/FD-1B-DECLARATION.md sections 3 and 8,
bound by FD-1B-BINDING.md): one coverage toy per seed at a fixed truth, with the declared nuisance draws, unfolded by
production (e).

Every piece is imported, not copied: the source factors are composed from ``s5p_nullexp``'s primitives (its
``checked_ratio``, ``ModelCache`` and truth-preserving g_f); the pseudo-data, MC streams and background treatment are
``s5n_pseudo``'s; the truth is ``s5n_pseudo.truth_weight`` under ``s5e_candidate.install("R")`` (``nominal`` or
``ratio_nd``); the unfold is ``s5n_pseudo.unfold_negweight``, F1c's path. ``s5p_nullexp``, ``s5e_candidate`` and every
module s5p's records depend on are unchanged.

Modes (``--mode``):

* ``toy`` (production, declaration section 3): ALL of the MC. Pseudo-data n_i ~ Poisson(w_reco_i r_i fs_i) on every
  reco-passing MC row and m_j ~ Poisson(bkg_w_j fb_j) on every background row (data size: the MC at weight x1, as
  ``s5n_pseudo.build_data``); the unfolding MC, prior and template are the CV's, with set A's MC Poisson(1) and
  template Poisson(1) streams (``s5n_pseudo.bootstrap_replica``'s streams at b = the toy seed; its data stream is not
  used, since the pseudo-data are already a Poisson draw). The truth is the MC truth x r.
* ``half``: A7's mechanics (half A unfolds, half B and source C make the pseudo-data, no streams), F0's and F1's
  estimator, for the paired correspondence runs. With ``--no-draws`` it is F1c's line exactly
  (``s5n_pseudo.build_pseudo`` then ``unfold_negweight``), for the bitwise reproduction runs.
* ``derivation``: the noise-free runs of gate D. All of the MC, every Poisson draw replaced by its mean, no streams,
  and exactly ONE named S1 universe (or none: ``CV``) applied to the source, at the nominal truth.

The draws (``toy`` and ``half`` unless ``--no-draws``), from ``numpy.random.default_rng([seed, DRAW_SALT])``:
* flux: one of the 100 PPFX universes u, with probability w_u / sum w (the constraint file's first 100 Flux entries,
  read by ``s1_assemble.flux_weights``); signal source reco weights x wr_u / w_reco, background x bkgw_u / bkg_w;
* interaction: each of S1's 33 interaction bands (32 pairs and 2p2h; Rvp1pi is not a band) at one of its universes,
  uniformly, applied as A7 applies it: truth kept in every fine cell (g_f);
* detector: the 4 weight-only bands, each at endpoint 0 or 1 with probability 1/2, from the detector dump only (S1
  choice 7);
* lateral: s_b = +-1 with probability 1/2 per band; normalization: z ~ N(0, 1). Both are recorded here and applied by
  the scorer on the cell integrals (``fd_1b_score.surrogate``), since their Delta_b live on the 16 cells.

Pins: the inputs npz and background dump by sha256; the truth ratio by the committed ``f1-prep-SHA256SUMS``; the flux
constraint by ``s1_assemble``'s digest; every bank and detector weight file by a pins file (``pins`` subcommand,
hashed against the sf1 manifest and the detector receipt) whose sha256 is required and whose size and mtime are
re-checked before every toy. A missing pin, a non-finite factor or a truth differing from the arm's refuses.

    fd_1b_toys.py run --arm control --mode toy --seeds 2610000:2610006 ... --out DIR
    fd_1b_toys.py run --arm derivation --mode derivation --universes CV,Flux_0,MaRES_1 ... --out DIR
    fd_1b_toys.py pins --bank B --detector-dir DD --manifest M --detector-receipt R --out pins.json

MEASURES: one toy's unfolded fine-grid result, its truth and its draws. CANNOT AUTHORIZE: a coverage verdict, an
interval or any claim by itself (fd_1b_score.py grades, under the declaration).
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import resource
import sys
import time
from pathlib import Path

import numpy as np

_ND = Path(__file__).resolve().parent
REPO = _ND.parent
if str(_ND) not in sys.path:
    sys.path.insert(0, str(_ND))
import s1_assemble  # noqa: E402
import s5c_pseudo  # noqa: E402
import s5c_unfold  # noqa: E402
import s5e_candidate  # noqa: E402
import s5n_pseudo  # noqa: E402
import s5p_nullexp as ne  # noqa: E402
import s5p_universe  # noqa: E402

SCHEMA = "fd-1b-toy/1"
CONFIG, ESTIMATOR_SEED, ITERS = "R", 42, 5
DRAW_SALT, PSEUDO_SALT = 0x1B0, 0x1B1
F1_SUMS = REPO / "docs/orchestration/state/measurement-paper/5d-community-20261024/fd/receipts-f1/run/cluster/f1b3/prep/f1-prep-SHA256SUMS"
TRUTHS = {"nominal": None, "genie_v3_g18": "bridged/genie_v3_g18.json", "genie_v3_ar23": "bridged/genie_v3_ar23.json"}
# arm -> (truth, first seed, last seed): the declaration's section 3 table and section 6's pilot. ``repro`` takes F1c's
# own seeds (fd_f1_tasks.SEEDS: 806000-806019, 807000-807019); ``derivation`` takes no seed.
ARMS = {"control": ("nominal", 2_610_000, 2_610_299), "g18": ("genie_v3_g18", 2_620_000, 2_620_299),
        "ar23": ("genie_v3_ar23", 2_630_000, 2_630_299), "pilot": ("nominal", 2_600_000, 2_600_015),
        "repro-g18": ("genie_v3_g18", 806_000, 806_019), "repro-ar23": ("genie_v3_ar23", 807_000, 807_019),
        "derivation": ("nominal", None, None)}
MODES = {"control": ("toy",), "g18": ("toy",), "ar23": ("toy",), "pilot": ("toy", "half"),
         "repro-g18": ("half",), "repro-ar23": ("half",), "derivation": ("derivation",)}
# the modes whose every unfold has one truth; a half-MC truth is its own seed's split's (s5n_pseudo.build_pseudo)
FIXED_TRUTH_MODES = ("toy", "derivation")
DETECTOR_DRAW_ORDER = ne.DETECTOR_BANDS          # MinosEfficiency, GEANT_Neutron, GEANT_Pion, GEANT_Proton
LATERAL_DRAW_ORDER = s1_assemble.LATERAL_BANDS
INTERACTION_BANDS = tuple(sorted(b for b in s1_assemble.EXPECT
                                 if b != s1_assemble.FLUX and b not in s1_assemble.DETECTOR_BANDS))
N_FLUX = s1_assemble.EXPECT[s1_assemble.FLUX]


class Refusal(RuntimeError):
    """A declared pin or invariant does not hold; nothing is written."""


# ------------------------------------------------------------------------------------------------- the universe set


def interaction_groups(bank: Path) -> dict[str, list[str]]:
    """S1's interaction bands from the bank: A7's model universes without Rvp1pi, checked equal to S1's set."""
    groups = ne.model_groups(ne.model_bands(bank))
    groups.pop(s1_assemble.DROPPED, None)
    got = {b: len(v) for b, v in groups.items()}
    want = {b: s1_assemble.EXPECT[b] for b in INTERACTION_BANDS}
    if got != want:
        raise Refusal(f"bank interaction bands differ from S1's: {sorted(set(got) ^ set(want)) or 'universe counts'}")
    for b, us in groups.items():
        if us != [f"{b}_{i}" for i in range(want[b])]:
            raise Refusal(f"{b}: universes {us}")
    return groups


def flux_ids(bank: Path) -> list[int]:
    ids = sorted(int(p.stem.split("_")[1]) for p in bank.glob("Flux_*_wr.npy"))
    if ids != list(range(N_FLUX)):
        raise Refusal(f"bank Flux universes {ids[:3]}..{ids[-3:]} are not 0..{N_FLUX - 1}")
    return ids


def s1_universes() -> list[str]:
    """Every universe S1 unfolded, as ``<band>_<i>`` tags, in S1's band order: the derivation runs' set."""
    return [f"{b}_{i}" for b in sorted(s1_assemble.EXPECT) for i in range(s1_assemble.EXPECT[b])]


def weight_files(bank: Path, det_dir: Path) -> list[Path]:
    """Every weight file a 1B toy can read: the bank's CV, Flux and interaction universes; the dump's detector bands."""
    out = [bank / "cv.npz"]
    for u in s1_universes():
        band = u.rpartition("_")[0]
        d = det_dir if band in s1_assemble.DETECTOR_BANDS else bank
        out += [d / f"{u}_{k}.npy" for k in s5p_universe.weight_keys(d, u)]
    return out


def make_pins(bank: Path, det_dir: Path, manifest: Path, receipt: Path) -> dict:
    """sha256 of every weight file, each checked against its record (bank: the sf1 manifest; detector dump: its
    receipt, itself listed in the manifest), with the size and mtime the toys re-check."""
    listed = s1_assemble.load_manifest(manifest)
    s1_assemble.require_listed(receipt, listed, "detector-dump receipt")
    det = json.loads(receipt.read_text())["files_sha256"]
    files = {}
    for p in weight_files(bank, det_dir):
        want = det.get(p.name) if p.parent == det_dir else listed.get(str(p))
        if want is None:
            raise Refusal(f"{p} has no recorded digest")
        got = s1_assemble.sha256(p)
        if got != want:
            raise Refusal(f"{p}: sha256 {got} != recorded {want}")
        st = p.stat()
        files[str(p)] = {"sha256": got, "size": st.st_size, "mtime_ns": st.st_mtime_ns}
    return {"schema": "fd-1b-pins/1", "bank": str(bank), "detector_dir": str(det_dir),
            "manifest_sha256": s1_assemble.sha256(manifest), "receipt_sha256": s1_assemble.sha256(receipt), "files": files}


def check_pins(pins: dict, bank: Path, det_dir: Path) -> None:
    want = sorted(str(p) for p in weight_files(bank, det_dir))
    if sorted(pins["files"]) != want or pins["bank"] != str(bank) or pins["detector_dir"] != str(det_dir):
        raise Refusal("the pins file does not cover exactly this bank's and dump's weight files")
    for path, rec in pins["files"].items():
        st = Path(path).stat()
        if (st.st_size, st.st_mtime_ns) != (rec["size"], rec["mtime_ns"]):
            raise Refusal(f"{path} changed after it was pinned")


def committed_ratio_sha256(truth: str) -> str | None:
    """The committed F1 prep digest of the arm's truth ratio (None for the nominal truth)."""
    rel = TRUTHS[truth]
    if rel is None:
        return None
    sums = {}
    for line in F1_SUMS.read_text().splitlines():
        sha, name = line.split("  ", 1)
        sums[name.removeprefix("./")] = sha
    if rel not in sums:
        raise Refusal(f"{F1_SUMS} lists no {rel}")
    return sums[rel]


def truth_ratio(truth: str, prep: Path | None) -> tuple[dict | None, str | None]:
    """The arm's truth: ``nominal`` (r = 1), or F1's bridged ratio, whose sha256 must be the committed F1 sums'."""
    rel = TRUTHS[truth]
    if rel is None:
        return None, None
    if prep is None:
        raise Refusal(f"truth {truth} needs --prep (F1's prep directory)")
    want = committed_ratio_sha256(truth)
    path = prep / rel
    got = s1_assemble.sha256(path)
    if want != got:
        raise Refusal(f"{path}: sha256 {got} is not the committed F1 prep digest {want}")
    ratio = json.loads(path.read_text())
    if ratio.get("schema") != "s5e-shape-ratio/1":
        raise Refusal(f"{path}: schema {ratio.get('schema')}")
    return ratio, got


# ------------------------------------------------------------------------------------------------------- the draws


def flux_probabilities(constraint: Path) -> np.ndarray:
    w = s1_assemble.flux_weights(constraint)
    return w / w.sum()


def draw(rng: np.random.Generator, flux_p: np.ndarray, groups: dict[str, list[str]]) -> dict:
    """One toy's nuisance draw (declaration section 3), in a fixed order so the scorer can re-derive it."""
    return {"flux": int(rng.choice(flux_p.size, p=flux_p)),
            "model": {s: str(rng.choice(groups[s])) for s in sorted(groups)},
            "detector": {b: int(rng.integers(0, 2)) for b in DETECTOR_DRAW_ORDER},
            "lateral_s": {b: int(2 * rng.integers(0, 2) - 1) for b in LATERAL_DRAW_ORDER},
            "normalization_z": float(rng.normal())}


def draw_for_seed(seed: int, flux_p: np.ndarray, groups: dict[str, list[str]]) -> dict:
    return draw(np.random.default_rng([seed, DRAW_SALT]), flux_p, groups)


def single_universe(tag: str) -> dict:
    """The source draw of one derivation run: exactly one S1 universe, or none (``CV``)."""
    if tag == "CV":
        return {"flux": None, "model": {}, "detector": {}}
    band, _, idx = tag.rpartition("_")
    if tag not in s1_universes():
        raise Refusal(f"{tag} is not one of S1's 175 universes")
    if band == s1_assemble.FLUX:
        return {"flux": int(idx), "model": {}, "detector": {}}
    if band in s1_assemble.DETECTOR_BANDS:
        return {"flux": None, "model": {}, "detector": {band: int(idx)}}
    return {"flux": None, "model": {band: tag}, "detector": {}}


def source_factors(d: dict, inputs: dict, bkg: dict, bank: Path, det_dir: Path, source: np.ndarray,
                   cache: ne.ModelCache | None) -> tuple[np.ndarray, np.ndarray, dict]:
    """Signal reco-weight and background-weight factors for draw ``d``, composed from s5p_nullexp's primitives as its
    ``source_factors`` composes them, except that the flux may be absent (a derivation run) and the detector bands
    come from the dump only. Returns the factors and their weight-treatment record."""
    fs, fb = np.ones(inputs["w_reco"].shape[0]), np.ones(bkg["bkg_w"].shape[0])
    wr, bw = np.asarray(inputs["w_reco"], float), np.asarray(bkg["bkg_w"], float)
    used_r, used_b = np.asarray(inputs["pass_reco"], bool), np.ones(bw.size, bool)
    rec: dict = {}
    if d.get("flux") is not None:
        tag = f"Flux_{d['flux']}"
        w = s5p_universe.weights(bank, tag, nonfinite="keep")
        fs *= ne.checked_ratio(w["wr"], wr, used_r, f"{tag}:wr", rec)
        fb *= ne.checked_ratio(w["bkgw"], bw, used_b, f"{tag}:bkgw", rec)
    chosen = list(d.get("model", {}).values())
    if chosen:
        cache = cache if cache is not None else ne.ModelCache(bank, chosen, inputs, bkg)
        k_wr, k_wt, k_b = cache.product(chosen)
        fb *= k_b
        fs *= k_wr * ne.truth_preserving(k_wt, inputs, source)
        rec.update({k: v for u in chosen for k, v in cache.clipped.get(u, {}).items()})
    for b, i in d.get("detector", {}).items():
        tag = f"{b}_{i}"
        if not (det_dir / f"{tag}_wr.npy").exists():
            raise Refusal(f"detector universe {tag} is not in the detector dump {det_dir}")
        wd = s5p_universe.weights(det_dir, tag, nonfinite="keep")
        fs *= ne.checked_ratio(wd["wr"], wr, used_r, f"{tag}:wr", rec)
        fb *= ne.checked_ratio(wd["bkgw"], bw, used_b, f"{tag}:bkgw", rec)
    for name, f in (("signal", fs), ("background", fb)):
        if not np.all(np.isfinite(f)) or np.any(f < 0):
            raise Refusal(f"{name} source factor: {int((~np.isfinite(f)).sum())} non-finite, {int((f < 0).sum())} negative")
    return fs, fb, rec


# ------------------------------------------------------------------------------------------------- the experiments


class _MeanRNG:
    def poisson(self, lam):
        return np.asarray(lam, float).copy()


def build_full(inputs: dict, bkg: dict, r: np.ndarray, fs: np.ndarray, fb: np.ndarray, seed: int | None,
               expectation: bool) -> tuple[dict, np.ndarray, dict]:
    """All of the MC: ``s5n_pseudo.build_data``'s experiment (full MC at x1, the full background template) with its
    observed events replaced by pseudo-data at truth r with the source factors, Poisson or (``expectation``) the mean.
    The truth is ``s5n_pseudo.true_xsec`` over every row (w_truth halved first, so its x2 for half B gives x1)."""
    edges = inputs["edges"]
    rng = _MeanRNG() if expectation else np.random.default_rng([seed, PSEUDO_SALT])
    reco = np.asarray(inputs["pass_reco"], bool)
    lam_s = np.asarray(inputs["w_reco"], float)[reco] * r[reco] * fs[reco]
    lam_b = np.asarray(bkg["bkg_w"], float) * fb
    n_sig = rng.poisson(lam_s).astype(float)
    m_bkg = rng.poisson(lam_b).astype(float)
    obs = np.concatenate([inputs["MCreco"][reco][n_sig > 0], bkg["bkg_reco"][m_bkg > 0]])
    counts = np.concatenate([n_sig[n_sig > 0], m_bkg[m_bkg > 0]])
    keep = s5n_pseudo.fid_mask(obs, edges)
    exp = s5n_pseudo.build_data(inputs, bkg)
    exp["obs"], exp["obs_counts"] = obs[keep], counts[keep]
    half_w = dict(inputs, w_truth=0.5 * np.asarray(inputs["w_truth"], float))
    x_true = s5n_pseudo.true_xsec(half_w, np.ones(inputs["MCgen"].shape[0], bool), r)
    info = {"n_unfolding_mc": int(inputs["MCgen"].shape[0]), "pseudo_signal_events": float(n_sig.sum()),
            "pseudo_background_events": float(m_bkg.sum()), "expected_signal": float(lam_s.sum()),
            "expected_background": float(lam_b.sum()), "template_weight_in_window": float(exp["tmpl_w"].sum()),
            "observed_events_outside_window": float(counts[~keep].sum()), "expectation": bool(expectation)}
    return exp, x_true, info


def mc_template_streams(exp: dict, b: int) -> dict:
    """Set A's MC Poisson(1) and template Poisson(1) streams at replica b (``s5n_pseudo.bootstrap_replica``), with
    the observed counts left as they are: the pseudo-data are already the data's Poisson draw."""
    rep = s5n_pseudo.bootstrap_replica(exp, b)
    rep["obs_counts"] = exp["obs_counts"]
    return rep


def truth_model(truth: str) -> tuple[str, float]:
    """``s5n_pseudo.truth_weight``'s (name, amplitude) for a truth: the nominal, or a bridged ratio at amplitude 1."""
    return ("nominal", 0.0) if truth == "nominal" else ("ratio_nd", 1.0)


def half_truth(seed: int, inputs: dict, truth: str, ratio: dict | None) -> np.ndarray:
    """A half-MC seed's truth from its split alone, as ``s5n_pseudo.build_pseudo`` makes it: half B's reweighted
    truth, which no draw enters (the draws scale w_reco, the truth reads w_truth)."""
    name, amplitude = truth_model(truth)
    is_b = s5c_pseudo.half_mask(inputs["MCgen"].shape[0], s5c_pseudo.split_key_for(seed))
    return np.asarray(s5n_pseudo.true_xsec(inputs, is_b, s5n_pseudo.truth_weight(name, inputs, amplitude, ratio)), float)


def experiment(mode: str, d: dict | None, seed: int | None, inputs: dict, bkg: dict, truth: str, ratio: dict | None,
               bank: Path, det_dir: Path, cache) -> tuple[dict, np.ndarray, dict, dict]:
    name, amplitude = truth_model(truth)
    rec: dict = {}
    if mode == "half":
        split = s5c_pseudo.split_key_for(seed)
        ui, ub = inputs, bkg
        if d is not None:
            is_b = s5c_pseudo.half_mask(inputs["MCgen"].shape[0], split)
            is_c = s5c_pseudo.half_mask(bkg["bkg_w"].shape[0], s5n_pseudo.bkg_split_key(split))
            fs, fb, rec = source_factors(d, inputs, bkg, bank, det_dir, is_b, cache)
            ui = dict(inputs, w_reco=np.where(is_b, np.asarray(inputs["w_reco"], float) * fs, inputs["w_reco"]))
            ub = dict(bkg, bkg_w=np.where(is_c, np.asarray(bkg["bkg_w"], float) * fb, bkg["bkg_w"]))
        exp, x_true, info = s5n_pseudo.build_pseudo(ui, ub, name, amplitude, split, seed, ratio)
        return exp, x_true, dict(info, split_key=split), rec
    r = s5n_pseudo.truth_weight(name, inputs, amplitude, ratio)
    if d is None:
        fs, fb = np.ones(inputs["w_reco"].shape[0]), np.ones(bkg["bkg_w"].shape[0])
    else:
        fs, fb, rec = source_factors(d, inputs, bkg, bank, det_dir, np.ones(inputs["MCgen"].shape[0], bool), cache)
    exp, x_true, info = build_full(inputs, bkg, r, fs, fb, seed, expectation=(mode == "derivation"))
    if mode == "toy":
        exp = mc_template_streams(exp, seed)
        info["stream_replica"] = seed
    return exp, x_true, info, rec


# ------------------------------------------------------------------------------------------------------------ main


def code_digests() -> dict:
    files = [Path(__file__).resolve(), _ND / "s5p_nullexp.py", _ND / "s1_assemble.py", _ND / "s5p_universe.py"]
    return {**s5n_pseudo.code_digests(), **{f.name: s5n_pseudo.sha256_path(f) for f in files}}


def parse_seeds(text: str, arm: str) -> list[int]:
    first, last = (int(v) for v in text.split(":"))
    lo, hi = ARMS[arm][1:]
    if not (lo <= first <= last <= hi):
        raise Refusal(f"seeds {first}:{last} are outside arm {arm}'s declared {lo}:{hi}")
    return list(range(first, last + 1))


def run(a, refine_fn=None, unfold_fn=None) -> int:
    truth = ARMS[a.arm][0]
    if a.mode not in MODES[a.arm]:
        raise Refusal(f"arm {a.arm} runs in mode {MODES[a.arm]}, not {a.mode}")
    if a.arm.startswith("repro") != a.no_draws:
        raise Refusal("--no-draws is for, and only for, the reproduction arms")
    if (a.mode == "derivation") != (a.universes is not None) or (a.mode == "derivation") == (a.seeds is not None):
        raise Refusal("give --universes for the derivation mode and --seeds otherwise")
    s5e_candidate.install(CONFIG)
    t0 = time.time()
    npz_sha, bkg_sha = s5n_pseudo.sha256_path(a.npz), s5n_pseudo.sha256_path(a.bkg)
    if (npz_sha, bkg_sha) != (a.expect_npz_sha256, a.expect_bkg_sha256) or \
            (npz_sha, bkg_sha) != (s1_assemble.INPUT_NPZ_SHA256, s1_assemble.BKG_SHA256):
        raise Refusal(f"input digests {npz_sha} / {bkg_sha} are not the declared ones")
    pins_sha = s1_assemble.sha256(a.pins)
    if pins_sha != a.expect_pins_sha256:
        raise Refusal(f"pins file sha256 {pins_sha} != {a.expect_pins_sha256}")
    pins = json.loads(a.pins.read_text())
    check_pins(pins, a.bank, a.detector_dir)
    ratio, ratio_sha = truth_ratio(truth, a.prep)
    flux_p = flux_probabilities(a.flux_constraint)
    flux_ids(a.bank)
    groups = interaction_groups(a.bank)
    inputs = s5c_unfold.load_inputs(a.npz)
    bz = np.load(a.bkg, allow_pickle=True)
    bkg = {"bkg_reco": bz["bkg_reco"], "bkg_w": bz["bkg_w"], "bkg_nd": bz["bkg_nd"]}
    if json.loads(str(bz["meta"]))["npz_sha256"] != npz_sha:
        raise Refusal("the background dump was made against a different npz")
    alignment = s5p_universe.check_alignment(np.load(a.bank / "cv.npz", allow_pickle=True), inputs, bkg)
    work = ([("u", u) for u in a.universes.split(",")] if a.universes is not None
            else [("s", s) for s in parse_seeds(a.seeds, a.arm)])
    a.out.mkdir(parents=True, exist_ok=True)
    seconds_load = round(time.time() - t0, 3)
    status = 0
    cache, first_truth = None, None
    for kind, item in work:
        target = a.out / (f"{a.tag}_{item}.npz" if kind == "u" else f"{a.tag}_s{item}.npz")
        if target.exists():
            continue
        check_pins(pins, a.bank, a.detector_dir)
        t1 = time.time()
        seed = item if kind == "s" else None
        if kind == "u":
            d = single_universe(item)
        else:
            d = None if a.no_draws else draw_for_seed(seed, flux_p, groups)
        source_draw = None if d is None else {k: d[k] for k in ("flux", "model", "detector")}
        if d is not None and d["model"] and cache is None and kind == "s":
            cache = ne.ModelCache(a.bank, [u for us in groups.values() for u in us], inputs, bkg)
        exp, x_true, info, treatment = experiment(a.mode, source_draw, seed, inputs, bkg, truth, ratio, a.bank,
                                                  a.detector_dir, cache)
        xs, ev = s5n_pseudo.unfold_negweight(exp, ESTIMATOR_SEED, a.threads, ITERS, None, refine_fn, unfold_fn)
        xs, x_true = np.asarray(xs, float), np.asarray(x_true, float)
        if not (np.all(np.isfinite(xs)) and np.all(np.isfinite(x_true))):
            raise Refusal(f"{target.name}: a non-finite unfolded value or truth")
        if a.mode in FIXED_TRUTH_MODES:
            if first_truth is None:
                first_truth = x_true
            elif not np.array_equal(x_true, first_truth):
                raise Refusal(f"{target.name}: its truth differs from this run's first toy's")
        elif not np.array_equal(x_true, half_truth(seed, inputs, truth, ratio)):
            raise Refusal(f"{target.name}: its truth is not its split's")
        meta = {"schema": SCHEMA, "arm": a.arm, "mode": a.mode, "truth": truth, "truth_ratio_sha256": ratio_sha,
                "pseudo_seed": seed, "universe": item if kind == "u" else None, "draw": d, "no_draws": a.no_draws,
                "weight_treatment": treatment, "config": CONFIG, "capacity": None, "iters": ITERS,
                "estimator_seed": ESTIMATOR_SEED, "threads": a.threads, "experiment": info, **ev,
                "input_npz_sha256": npz_sha, "bkg_dump_sha256": bkg_sha, "pins_sha256": pins_sha,
                "flux_constraint_sha256": s1_assemble.CONSTRAINT_SHA256, "alignment": alignment,
                "interaction_bands": sorted(groups), "code_sha256": code_digests(), "numpy_version": np.__version__,
                "slurm_job": os.environ.get("SLURM_JOB_ID"), "slurm_step": os.environ.get("SLURM_STEP_ID"),
                "seconds_load": seconds_load, "seconds_unfold": round(time.time() - t1, 3),
                "peak_rss_kib": resource.getrusage(resource.RUSAGE_SELF).ru_maxrss}
        rc = s5n_pseudo.write_product(target, {"xsec_flat": xs.ravel(order="C"), "xtrue_flat": x_true.ravel(order="C")},
                                      meta)
        status |= rc
        print(json.dumps({"out": target.name, "rc": rc, "seconds_unfold": meta["seconds_unfold"]}), flush=True)
    return status


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n", 1)[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    r = sub.add_parser("run")
    r.add_argument("--arm", choices=sorted(ARMS), required=True)
    r.add_argument("--mode", choices=("toy", "half", "derivation"), required=True)
    r.add_argument("--seeds", default=None, help="first:last, inside the arm's declared range")
    r.add_argument("--universes", default=None, help="derivation: comma list of S1 universe tags or CV")
    r.add_argument("--no-draws", action="store_true", help="the reproduction arms only: every draw off")
    r.add_argument("--npz", type=Path, required=True)
    r.add_argument("--bkg", type=Path, required=True)
    r.add_argument("--expect-npz-sha256", required=True)
    r.add_argument("--expect-bkg-sha256", required=True)
    r.add_argument("--bank", type=Path, required=True)
    r.add_argument("--detector-dir", type=Path, required=True)
    r.add_argument("--pins", type=Path, required=True)
    r.add_argument("--expect-pins-sha256", required=True)
    r.add_argument("--flux-constraint", type=Path, required=True)
    r.add_argument("--prep", type=Path, default=None, help="F1's prep directory (the bridged truth ratios)")
    r.add_argument("--threads", type=int, default=int(os.environ.get("SLURM_CPUS_PER_TASK", "32")))
    r.add_argument("--tag", required=True)
    r.add_argument("--out", type=Path, required=True)
    p = sub.add_parser("pins")
    p.add_argument("--bank", type=Path, required=True)
    p.add_argument("--detector-dir", type=Path, required=True)
    p.add_argument("--manifest", type=Path, required=True, help="the sf1 manifest/inputs-sha256.txt")
    p.add_argument("--detector-receipt", type=Path, required=True)
    p.add_argument("--out", type=Path, required=True)
    a = ap.parse_args(argv)
    try:
        if a.cmd == "pins":
            if a.out.exists():
                raise Refusal(f"refusing to overwrite {a.out}")
            pins = make_pins(a.bank, a.detector_dir, a.manifest, a.detector_receipt)
            a.out.write_text(json.dumps(pins, indent=1, sort_keys=True) + "\n")
            print(json.dumps({"files": len(pins["files"]), "sha256": s1_assemble.sha256(a.out)}))
            return 0
        return run(a)
    except (Refusal, SystemExit, ValueError, OSError) as e:
        # every refusal before a product is written: a declared pin or invariant (Refusal, s1_assemble's SystemExit),
        # a non-finite or negative weight ratio (s5p_nullexp's ValueError), a missing or unreadable file (OSError)
        if isinstance(e, SystemExit) and not isinstance(e.code, str):
            raise
        print(f"[fd-1b] refusing: {type(e).__name__}: {e}", file=sys.stderr)
        return 4


if __name__ == "__main__":
    sys.exit(main())

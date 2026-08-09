#!/usr/bin/env python3
"""P4 standard-lateral hardening library (repair, 2026-07-18).

Fail-closed gates + exact-inventory hashing for the standard selection-complete
scalar lateral chain. ROOT-free by design (ROOT-dependent audits live in
p4_lib_root helpers, imported lazily) so the covariance-math / manifest / gate
logic is unit-testable without PyROOT. The MAT two-endpoint formula is preserved
by reusing uq_math.mat_covariance / uq_math.project_covariance unchanged.

Nothing here BUILDS or ADOPTS a covariance; it only validates/guards. Candidate
construction is authorized only after the standard-p4-verifier returns PASS.
"""
from __future__ import annotations
import hashlib, json, math, os, subprocess
import numpy as np

# Canonical standard lateral inventory (exactly these; order fixed).
BANDS = ("BeamAngleX", "BeamAngleY", "MuonResolution",
         "Muon_Energy_MINERvA", "Muon_Energy_MINOS")
ENDPOINTS = (0, 1)                      # -1 sigma, +1 sigma (MAT two-endpoint pair)
N_ENDPOINTS = len(BANDS) * len(ENDPOINTS)   # 10
GRID_NBINS = 65856                      # 14*16*7*7*6 full 5D grid (pt,pz,eavail,q3,W)

# ------------------------------------------------------------------ footing (G-1)
# The standard lane was footing-BLIND by construction until 2026-08-07: this module and
# p4_evidence.py had no bkg/footing/mode handling at all, so the manifest bound hashes only
# and no downstream consumer could prove which background subtraction produced an endpoint
# (KNOWN_ISSUES #20(a), BEN-041). These constants give it somewhere to record the choice.
#
# The recorded decision (2026-08-07, RUNBOOK-20260807-gbdt-closeout.md §2) is that the
# standard 5D chain is quoted on `purity`, revisited before submission. `purity` is ALSO the
# driver default (unfold_nd_omnifold_unbinned.py:566), so asserting it explicitly is a
# provenance change and a physics no-op -- it must not move any output ROOT hash.
#
# Deliberately a standard-side copy, NOT an import from fps_provenance: that module's grid
# constants are hash-pinned into freshly-green FPS gates and must not be mutated or coupled
# to (BEN-040's lane). The five estimator keys happen to agree today; if the two lanes ever
# diverge, they diverge independently instead of one silently redefining the other.
STANDARD_REQUIRED_FOOTING = {
    "estimator": "lgbm",
    "seed": 42,
    "iters": 5,
    "use_weights": True,
    "full_phase_space": False,      # standard phase space; the FPS lane sets this True
}
# ---------------------------------------------------- candidate ROOT keys (repair-4, D1c)
# The driver used to hardcode `hCov_std_final5_candidate`, a key NOTHING wrote -- stages 4-6
# had never executed, so nothing caught it. The builder's names and the driver's names now
# come from here, so the two cannot drift apart again by editing one file.
CANDIDATE_ACTIVE_BAND_PREFIX = "hCov_active5d_"
CANDIDATE_ACTIVE_TOTAL_KEY = "hCov_active5d_total"
CANDIDATE_SYST_KEY = "hCov_stdsyst5d_total_candidate"
CANDIDATE_TOTAL_KEY = "hCov_stdcombined5d_total_candidate"   # full total: C_syst + stat + ML


def candidate_band_key(band):
    require(band in BANDS, f"unknown band {band!r}")
    return f"{CANDIDATE_ACTIVE_BAND_PREFIX}{band}"


# Which bands are expected to migrate selection. Single-sourced here (repair-5) because
# p4_evidence.py and p4_validate_active_lateral.py each had their own private copy, and a
# duplicated policy set is one edit away from two lanes disagreeing about what is expected.
NONZERO_MIGRATION_BANDS = frozenset({"BeamAngleX", "BeamAngleY"})
ZERO_MIGRATION_BANDS = frozenset({"MuonResolution", "Muon_Energy_MINERvA", "Muon_Energy_MINOS"})

# ---------------------------------------------------------------- WHEN A HASH IS RIGHT
# Three rounds of this lane were spent removing bindings defined by a PROXY, and the live risk
# after that is over-correction. The principle is NOT "hashes are bad". It is:
#
#     a hash is the right instrument for an artifact this chain READS and never re-produces;
#     it is the wrong instrument for one the chain PRODUCES, because a correct re-run moves it.
#
# So in p4_evidence.py the central 5D/4D products and their masks stay frozen sha256 bindings --
# if `xsec_5d_MEFHC_5iter_lgbm.root` changes underneath us that IS a defect and must block. The
# endpoint-manifest hash was removed from that same dict because the endpoints ARE produced here
# and are not bit-reproducible (KNOWN_ISSUES #24), so the frozen value rejected correct data.
#
# One hash tracking something that legitimately moves. That was the whole defect -- not the hash,
# and not the freezing, but the mismatch between the instrument and what it pointed at.

# ------------------------------------------- reproducibility tolerance (repair-6, 2026-08-07)
# These endpoint ROOTs are NOT bit-reproducible. Re-unfolding the same inputs with the same
# code and the same seed gives different bytes, because LightGBM/OpenMP reduction order depends
# on the thread partitioning and five OmniFold iterations amplify last-bit differences. So a
# reproducibility gate here must compare CONTENTS at a declared tolerance; sha256 identity
# cannot express "same computation" (KNOWN_ISSUES #24).
#
# DECLARED tolerance -- a SPECIFICATION set by Joseph 2026-08-07, deliberately conservative,
# roughly two orders above the measured floor so a CONC change does not force a re-derivation.
# This is NOT a tolerance loosened to make something failing pass: nothing was failing, and the
# floor below was measured on a clean 10/10 run with zero failures.
REPRO_RTOL_PER_BIN = 1e-9        # per reported bin, relative
REPRO_RTOL_INTEGRAL = 1e-11      # on the integrated cross section, relative
# WIDENED 1e-12 -> 1e-11 by Joseph, 2026-08-08, from measured SPREAD. The per-bin leg carried 52x
# margin (1.93e-11 vs 1e-9) while the integral leg carried 3.2x (3.14e-13 vs 1e-12), and the two
# integral observations span 12x (2.6e-14, 3.14e-13) -- a leg set up to false-alarm on a third
# run. At 1e-11 both legs carry comparable margin (32x and 52x) and the discrimination survives:
# a uniform shift still passes per-bin and fails integral anywhere from 1e-11 to 1e-9, a 100x
# window instead of 1000x.
#
# This is SPECIFICATION from measured spread with nothing currently failing -- not a tolerance
# loosened to rescue a result. The alternative considered and REJECTED was keeping 1e-12 with a
# documented escape clause for marginal breaches: a gate you can talk your way past is the exact
# anti-pattern this lane spent three rounds removing. REPRO_MEASURED_FLOOR below stays at the
# OBSERVED values so the specification and the measurement can never be conflated.

# ---------------------------------------------------------------------------------------------
# DO NOT WIDEN THE INTEGRAL LEG AGAIN. Its thinness is STRUCTURAL, not a mis-set number.
# (Recorded 2026-08-09 from the canonical re-unfold's own receipt, job 56495756, 10/10.)
#
# The 1e-12 -> 1e-11 widening above was correct and it is the LAST one available. The reason is
# that the integral leg is a DISCRIMINATOR, not a margin, and its entire dynamic range is ~100x:
#
#   worst per-bin deviation observed        1.831e-11     <- the fully COHERENT ceiling: if every
#                                                            bin moved the same way, the integral
#                                                            would move by about this much
#   that / sqrt(10694 reported bins)        1.770e-13     <- the fully INCOHERENT floor: pure
#                                                            round-off with random signs
#   total range the leg can ever resolve      103.4x
#
# The observation sits INSIDE that range, not below it: rel_integral 2.874e-12 is 16.2x above the
# incoherent floor and only 6.37x below the coherent ceiling. Equivalently the bins behave as
# N_eff = (1.831e-11 / 2.874e-12)^2 = 40.6 independent groups, not 10694 -- the same physical
# statement as the 0.4594 positive fraction recorded below (26.6 sigma from 0.5): the round-off is
# scattered but SIGN-BIASED, because a different OpenMP partition is a different DETERMINISTIC
# rounding path, not a random one.
#
# So the 3.48x "margin" (1e-11 vs 2.874e-12) is NOT slack. The tolerance already sits at 54.6% of
# the coherent ceiling. Widening toward 2e-11 does not buy safety; it buys the inability to detect
# the one thing this leg exists to detect. Contrast the per-bin leg, whose 54.6x margin (1e-9 vs
# 1.831e-11) IS slack, because the per-bin check is not a coherence discriminator and has no
# comparable ceiling. The two legs look similar and must not be reasoned about the same way --
# which is precisely the trap, since "both legs now carry comparable margin" was the argument for
# the last widening, and it is true of the numbers and false of their meaning.
#
# PRE-SPECIFIED RESPONSE TO A BREACH, decided now rather than under pressure in front of a red
# gate. If rel_integral exceeds 1e-11 on some future run, the question is NOT "how far over" -- a
# coherent shift and a round-off tail can produce the same magnitude, which is exactly why
# magnitude cannot be the discriminator (the mistake already made once here, BEN-060).
# Run `diagnose_integral_breach()` below, which measures the two things that DO separate them:
#   (1) SIGN BALANCE of the per-bin deviations. Round-off from a different reduction order keeps
#       the ~0.46 bias recorded below. A coherent shift drives the fraction hard toward 0 or 1.
#   (2) PER-BIN CORRELATION with the central value. Round-off is uncorrelated with bin content;
#       a physics or normalisation change scales with it.
# A breach that is sign-biased near 0.4594 AND uncorrelated with content is the round-off tail:
# proceed, recording the measurement. ANYTHING ELSE BLOCKS. Note what this does not permit -- the
# tolerance is not raised in either branch, and the second branch has no escape clause.
INTEGRAL_LEG_COHERENT_CEILING = 1.831e-11   # worst observed per-bin deviation; see above
INTEGRAL_LEG_INCOHERENT_FLOOR = 1.770e-13   # ceiling / sqrt(10694)


def diagnose_integral_breach(a, b, central=None):
    """PRE-SPECIFIED breach diagnostic (2026-08-09). Written BEFORE any breach, so the criterion
    cannot be chosen to fit the number that triggers it. Returns measurements only; it does not
    decide, because the decision is stated above and does not depend on anything it returns."""
    a = np.asarray(a, float); b = np.asarray(b, float)
    m = np.abs(b) > 0
    d = a[m] - b[m]
    nz = d != 0
    n = int(nz.sum())
    frac_pos = float(np.mean(d[nz] > 0)) if n else float("nan")
    out = {"n_deviating_bins": n, "frac_positive": frac_pos}
    if n:
        se_roundoff = math.sqrt(0.4594 * (1 - 0.4594) / n)
        out["sigma_from_roundoff_bias"] = (frac_pos - 0.4594) / se_roundoff
        out["sigma_from_half"] = (frac_pos - 0.5) / math.sqrt(0.25 / n)
    if central is not None:
        c = np.asarray(central, float)[m]
        rel = d / np.abs(b[m])
        if np.std(c) > 0 and np.std(rel) > 0:
            out["corr_reldev_vs_central"] = float(np.corrcoef(rel, c)[0, 1])
    return out


# MEASURED floor, recorded separately from the declared tolerance on purpose: re-measuring it
# must never silently move the gate. Job 56471429 (CONC=6) vs the 2026-07-18 set (CONC=4),
# ten endpoints, 65856 bins each, 106940 reported bins pooled:
#   worst relative bin difference   1.9e-11
#   integral agreement              2.6e-14
#   pooled mean deviation          -1.76e-13   (sd 1.96e-12)
#   fraction of bins deviating +    0.4594     -- 26.6 sigma from 0.5, i.e. a REAL systematic
#                                                 sign preference, which is the expected
#                                                 signature of a deterministic rounding path
#                                                 and NOT evidence of symmetric noise.
# sqrt(N)*eps for ~1e7 events is 7.0e-13, the same order as the pooled mean.
REPRO_MEASURED_FLOOR = {
    "job": "56471429", "conc_new": 6, "conc_reference": 4,
    "worst_rel_bin": 1.9e-11, "integral_rel": 2.6e-14,
    "pooled_mean": -1.76e-13, "pooled_sd": 1.96e-12,
    "frac_positive": 0.4594, "frac_positive_sigma_from_half": 26.6,
    "n_reported_bins_pooled": 106940,
}


def check_reproducibility(a, b, rtol_bin=REPRO_RTOL_PER_BIN, rtol_int=REPRO_RTOL_INTEGRAL):
    """Compare two runs of the same endpoint by CONTENT, not by bytes.

    Returns the measured (max per-bin relative difference, integral relative difference).
    Fails closed if either exceeds the declared tolerance."""
    a = np.asarray(a, float); b = np.asarray(b, float)
    require(a.shape == b.shape, f"reproducibility: shape {a.shape} != {b.shape}")
    m = np.abs(b) > 0
    require(m.any(), "reproducibility: reference has no positive bins")
    rel = np.max(np.abs(a[m] - b[m]) / np.abs(b[m]))
    sa, sb = float(a.sum()), float(b.sum())
    rel_int = abs(sa / sb - 1.0) if sb != 0 else float("inf")
    require(rel <= rtol_bin,
            f"reproducibility: max per-bin relative difference {rel:.3e} > {rtol_bin:.0e}")
    require(rel_int <= rtol_int,
            f"reproducibility: integral relative difference {rel_int:.3e} > {rtol_int:.0e}")
    return {"max_rel_bin": float(rel), "rel_integral": float(rel_int)}


KNOWN_BKG_MODES = ("purity", "negweight", "negweight-refined")
STANDARD_BKG_MODE = "purity"        # the 2026-08-07 decision; see OPEN_ITEMS G-0
STANDARD_FOOTING_KEYS = list(STANDARD_REQUIRED_FOOTING) + ["bkg_mode"]


class P4GateError(RuntimeError):
    """Raised by any fail-closed gate. Never swallow."""


def require(cond, msg):
    if not cond:
        raise P4GateError(msg)


# ---------------------------------------------------------------- config / hashes
class P4Config:
    """Frozen unfold configuration; its hash pins seed/axes/iters/estimator so a
    covariance can never be built from mismatched-config endpoints."""
    def __init__(self, axes="eavail,q3,W", iters=5, seed=42, estimator="lgbm",
                 use_weights=True, universe=None, bkg_mode=STANDARD_BKG_MODE):
        self.axes = axes; self.iters = int(iters); self.seed = int(seed)
        self.estimator = estimator; self.use_weights = bool(use_weights)
        self.universe = universe          # MUST be None for active endpoints
        self.bkg_mode = bkg_mode          # G-1: never inherited from the driver default
    def as_dict(self):
        # repair-4 (D3a): `full_phase_space_reported_grid` used to be bolted onto
        # man["config"] in p4_evidence.py AFTER config_hash was computed, so the recorded hash
        # did not cover the recorded configuration -- the declared config was not hash-bound.
        # It belongs in the config object, where as_dict() and hash() both see it.
        return {"axes": self.axes, "iters": self.iters, "seed": self.seed,
                "estimator": self.estimator, "use_weights": self.use_weights,
                "universe": self.universe, "bkg_mode": self.bkg_mode,
                "full_phase_space_reported_grid": GRID_NBINS}
    def hash(self):
        return hashlib.sha256(json.dumps(self.as_dict(), sort_keys=True).encode()).hexdigest()
    def footing(self):
        """The nested footing block as the PRODUCER emits it. Consumers must read this
        shape, not a flattened copy of it -- a fixture shaped like the consumer is how
        BEN-040's gate stayed green while failing on every real input."""
        f = dict(STANDARD_REQUIRED_FOOTING)
        f.update({"estimator": self.estimator, "seed": self.seed, "iters": self.iters,
                  "use_weights": self.use_weights, "bkg_mode": self.bkg_mode})
        return f
    def validate(self):
        require(self.universe is None, "active endpoint config must not set --universe")
        require(self.seed == 42, f"standard P4 requires fixed seed 42 (got {self.seed})")
        require(self.use_weights, "standard P4 requires --use-weights")
        require(self.iters == 5, f"standard P4 production uses 5 iters (got {self.iters})")
        require(self.axes == "eavail,q3,W", f"standard P4 requires axes=eavail,q3,W (got {self.axes})")
        require(self.estimator == "lgbm", f"standard P4 requires estimator=lgbm (got {self.estimator})")
        require(self.bkg_mode in KNOWN_BKG_MODES,
                f"unknown bkg_mode {self.bkg_mode!r} (known: {list(KNOWN_BKG_MODES)})")
        require(self.bkg_mode == STANDARD_BKG_MODE,
                f"standard P4 is quoted on {STANDARD_BKG_MODE!r} by the 2026-08-07 decision "
                f"(got {self.bkg_mode!r}); changing it re-opens RUNBOOK-20260807 §2 reading (B) "
                f"and invalidates the J28-corrected covariance")
        return True


# ------------------------------------------------------- footing evidence from logs (G-1)
# The driver announces its background mode on the NEGWEIGHT branches only
# (unfold_nd_omnifold_unbinned.py:842,895 -> "[INFO] bkg-mode=<mode>: ..."); the purity
# branch (:883) prints nothing about mode and instead calls build_measured_training_nd,
# whose verbose line is "[INFO] measured training: sum=... zero=.../...".
#
# So in this two-branch print, SILENCE IS A BRANCH: a log with the measured-training line
# and no bkg-mode line positively identifies purity rather than leaving it unknown. That is
# exactly the inference BEN-041 records failing to make. Both the flag and both
# announcements landed together in cf8a4a6 (2026-07-11), before the 2026-07-18 endpoint
# ROOTs, so an absent announcement is informative and not a version gap.
_BKG_MODE_ANNOUNCE = "[INFO] bkg-mode="
_PURITY_SIGNATURE = "[INFO] measured training:"


def classify_log_bkg_mode(text):
    """Return (mode, reason) for one unfold log. mode is a member of KNOWN_BKG_MODES, or
    None when the log cannot decide -- which callers must treat as UNPROVABLE, not as
    'probably fine'."""
    announced = None
    for line in text.splitlines():
        i = line.find(_BKG_MODE_ANNOUNCE)
        if i >= 0:
            tail = line[i + len(_BKG_MODE_ANNOUNCE):]
            tok = tail.split(":", 1)[0].strip()
            if tok in KNOWN_BKG_MODES:
                if announced is not None and announced != tok:
                    return None, f"log announces conflicting modes {announced!r} and {tok!r}"
                announced = tok
            else:
                return None, f"log announces unrecognized bkg-mode {tok!r}"
    if announced is not None:
        if announced == "purity":
            # the purity branch never announces; an announcement claiming purity means the
            # log did not come from this driver's known print set.
            return None, "log announces bkg-mode=purity, which this driver's purity branch never prints"
        return announced, f"driver announced bkg-mode={announced}"
    if _PURITY_SIGNATURE in text:
        return "purity", ("no bkg-mode announcement + build_measured_training_nd signature "
                          "present => purity branch (the silent branch)")
    return None, ("no bkg-mode announcement and no measured-training signature; the run may "
                  "have been non-verbose, so the branch is unprovable from this log")


def require_standard_footing(manifest, required_bkg_mode=STANDARD_BKG_MODE):
    """Fail closed unless the manifest carries a complete footing block that matches the
    standard requirement. Mirrors fps_provenance.require_footing's semantics -- absent is
    'unprovable' and fails, exactly like mismatched -- without importing or mutating it."""
    foot = manifest.get("footing")
    require(isinstance(foot, dict) and foot,
            "manifest has no footing block (unprovable): the standard lane must record its "
            "background footing, not inherit the driver default")
    for k, v in STANDARD_REQUIRED_FOOTING.items():
        require(foot.get(k) == v, f"footing.{k}={foot.get(k)!r} != {v!r}")
    require("bkg_mode" in foot, "footing has no bkg_mode (unprovable)")
    require(foot["bkg_mode"] in KNOWN_BKG_MODES,
            f"footing.bkg_mode={foot['bkg_mode']!r} is not a known mode")
    if required_bkg_mode is not None:
        require(foot["bkg_mode"] == required_bkg_mode,
                f"footing.bkg_mode={foot['bkg_mode']!r} != required {required_bkg_mode!r}")
    return True


# canonical candidate area (pre-adoption). Adopted/protected areas are forbidden outputs.
CANDIDATE_SUBDIR = "active_universe_5d/standard/candidate"
# repair-5 (D4a): containment is anchored to THIS repository, resolved, not textual. Derived
# from this file's own location (p4_lib.py lives in <repo>/nd-unfolding/), so it follows the
# checkout rather than a hardcoded /pscratch path -- which also makes it testable off-cluster.
ND_ROOT = os.path.dirname(os.path.abspath(__file__))
import pathlib as _pl
REPO_ROOT = os.path.dirname(ND_ROOT)
REPO_ROOT_PATH = _pl.Path(REPO_ROOT)
_ADOPTED_TOKENS = ("uq_universe_5d_covariance_combined", "_uthrow", "_cvcentered",
                   "adopted", "uq_4d/corrected", "universe_stage2_5d",
                   "products/5d/xsec", "products/4d/xsec")


NON_ADOPTABLE_KEY = "publication_gate_rejects_this"
NON_ADOPTABLE_ENV = "P4_NON_ADOPTABLE"
NON_ADOPTABLE_REASON = (
    "Built WITHOUT a standard-p4-verifier PASS, by explicit instruction, to learn whether "
    "stages 4-6 have defects of their own before another provenance round. This is NOT a step "
    "toward adoption and does not shorten the path to it: adoption still requires a PASS on the "
    "committed patch plus the separate authorized adoption step. Any consumer that reads this "
    "key must refuse the product.")
NON_ADOPTABLE_REQUIRES = ["standard-p4-verifier PASS on the committed patch",
                          "separately authorized adoption step (p4_adopt_standard.py)"]


def stamp_non_adoptable(prov, env=None):
    """SELF-DECLARING REJECTION (2026-08-09). A candidate built without a verifier PASS carries
    its own refusal, the pattern fps_control_manifest.json already uses, so the artifact declares
    its status instead of depending on a reader knowing how it was made -- which is exactly how
    the 07-18 endpoints sat in a publication namespace for three weeks.

    Producer and consumer are single-sourced here so the two cannot drift into disagreeing about
    the key's name, and so both directions are testable without ROOT."""
    env = os.environ if env is None else env
    if env.get(NON_ADOPTABLE_ENV) == "1":
        prov[NON_ADOPTABLE_KEY] = True
        prov["non_adoptable_reason"] = NON_ADOPTABLE_REASON
        prov["adoption_requires"] = list(NON_ADOPTABLE_REQUIRES)
    return prov


def require_adoptable(prov):
    """Refuse a self-declared non-adoptable candidate. Truthiness is the right test here and
    the recorded-fields sweep's flag on it is a shape match, not a defect: the truthy value
    means REFUSE, so a literal True is fail-closed. The failure mode worth guarding is the key
    going absent, which no comparison operator would catch either -- the guard is the
    both-directions test in tests/test_p4_repair.py."""
    require(not prov.get(NON_ADOPTABLE_KEY),
            f"this candidate declares {NON_ADOPTABLE_KEY}=true -- it was built without a "
            f"verifier PASS and is not adoptable. {prov.get('non_adoptable_reason', '')}")


def require_candidate_path(path):
    """Positive allowlist + negative denylist: a candidate MUST live under the
    candidate subdir and MUST NOT match any adopted/protected token. Prevents both
    the round-2 self-rejection (candidate name containing '_final') and any write
    onto an adopted/central path."""
    # repair-5 (defect 4a). History: this was first a bare substring test, then a
    # normpath component match -- and the verifier defeated the second one too, because a
    # component match succeeds ANYWHERE the sequence appears, so
    # `/evil/active_universe_5d/standard/candidate/out.root` passed, and normpath does not
    # resolve symlinks. Containment must be RESOLVED and anchored to this repository:
    # realpath both sides, then require commonpath(candidate_root, target) == candidate_root.
    cand_root = os.path.realpath(os.path.join(ND_ROOT, CANDIDATE_SUBDIR))
    # Callers pass repo-relative ("nd-unfolding/active_universe_5d/...") or ND-relative
    # ("active_universe_5d/...") paths depending on where they cd to, so resolve a relative
    # path against BOTH known roots and accept it if either lands inside. An absolute path is
    # taken as given. Resolution is realpath, so symlinks cannot smuggle a target out.
    if os.path.isabs(path):
        cands = [path]
    else:
        cands = [os.path.join(ND_ROOT, path), os.path.join(REPO_ROOT, path)]
    resolved, inside = None, False
    for c in cands:
        t = os.path.realpath(c)
        if resolved is None:
            resolved = t
        try:
            if os.path.commonpath([cand_root, t]) == cand_root and t != cand_root:
                resolved, inside = t, True
                break
        except ValueError:                 # different drives / unrelated roots
            continue
    require(inside,
            f"candidate must resolve inside {cand_root} (got {path} -> {resolved})")
    for t in _ADOPTED_TOKENS:
        require(t not in path, f"refusing candidate onto adopted/protected path (token {t!r})")
    return True


def prove_identity(A, B, rtol, label):
    """Fail-closed max-relative-difference identity gate (no subtraction hidden)."""
    A = np.asarray(A, dtype=float); B = np.asarray(B, dtype=float)
    require(A.shape == B.shape, f"{label}: shape {A.shape} != {B.shape}")
    denom = max(1e-300, float(np.max(np.abs(A))))
    err = float(np.max(np.abs(A - B)) / denom)
    require(err <= rtol, f"{label}: identity broken (rel {err:.2e} > {rtol:.0e})")
    return err


def edges_bin_volume_hash(edges):
    """Hash the ordered 5-axis edge arrays + the C-order per-bin volume vector."""
    import numpy as _np
    parts = []
    for e in edges:
        a = _np.asarray(e, dtype=float); require(a.ndim == 1 and a.size >= 2, "bad edge array")
        parts.append(a.tobytes())
    edge_hash = hashlib.sha256(b"|".join(parts)).hexdigest()
    widths = [(_np.asarray(e, float)[1:] - _np.asarray(e, float)[:-1]) for e in edges]
    vol = widths[0]
    for w in widths[1:]:
        vol = _np.multiply.outer(vol, w).ravel()   # C-order product of bin widths
    vol_hash = hashlib.sha256(vol.astype(float).tobytes() + b"|C").hexdigest()
    return {"edge_hash": edge_hash, "bin_volume_hash": vol_hash, "n_bins": int(vol.size)}


def validate_orchestrator_merged_receipt(recdir, live_stat):
    """Consume the owner-neutral merged-hash receipt: require COMPLETE + the four
    files, recompute live size/integer-mtime vs the inventory, and return the
    committed hash-list digest bound into our manifest. live_stat: dict path->(size,mtime)."""
    import os as _os
    for f in ("COMPLETE", "summary.tsv", "validation.tsv", "standard.sha256", "standard.inventory.tsv"):
        require(_os.path.exists(_os.path.join(recdir, f)), f"orchestrator receipt missing {f}")
    sha_lines = [l for l in open(_os.path.join(recdir, "standard.sha256")).read().splitlines() if l.strip()]
    require(len(sha_lines) == N_ENDPOINTS, f"receipt standard.sha256 has {len(sha_lines)} != 10 lines")
    merged = {}
    for l in sha_lines:
        h, p = l.split(None, 1); merged[p.strip()] = h
    # recompute live size + integer mtime against the committed inventory
    inv = {}
    for l in open(_os.path.join(recdir, "standard.inventory.tsv")).read().splitlines():
        if not l.strip() or l.startswith("#"):
            continue
        cols = l.split("\t")
        if len(cols) >= 3:                       # orchestrator format: size<TAB>mtime<TAB>path
            inv[cols[2]] = (int(cols[0]), int(float(cols[1])))
    for p, (sz, mt) in inv.items():
        require(p in live_stat, f"inventory path not live: {p}")
        lsz, lmt = live_stat[p]
        require(lsz == sz and int(lmt) == mt, f"live size/mtime drift for {p}")
    digest = hashlib.sha256("\n".join(sorted(f"{merged[p]}  {p}" for p in merged)).encode()).hexdigest()
    return {"merged_sha256": merged, "hash_list_digest": digest, "n": len(merged)}


# ------------------------------------------- endpoint receipt schema (repair-4, defect 2)
# Before repair-4 the resume path skipped an endpoint on `[[ -s ROOT && -s RECEIPT ]]` plus a
# ROOT-key/dimension check. Receipt tag, ROOT sha, merged sha, central sha, config hash and
# source provenance were never read, and the legacy-attest receipt did not even record the
# merged/central hashes -- so "resumable" meant "any nonempty file pair is accepted forever".
# That is the same size-as-completion family as BEN-023 and KNOWN_ISSUES #20(c).
#
# NOTE ON COST: the merged inputs are 53.8 GB each (538 GB total). This validator therefore
# does NOT re-hash them; it compares the receipt's recorded merged sha against the
# owner-neutral orchestrator receipt's committed hash, whose own live size+integer-mtime check
# is what detects a changed input. Same reuse p4_evidence.py already relies on. The ROOT and
# central files are ~480 KB and ARE re-hashed live on every skip.
RECEIPT_MODES = ("produced", "legacy-attested")
RECEIPT_REQUIRED_KEYS = ("tag", "mode", "root_sha256", "merged_sha256", "central5d_sha256",
                         "config_hash", "bkg_mode", "code_rev", "unfold_blob", "t")
# The source whose blob decides whether a cached endpoint is still valid. The unfold driver is
# the one that actually produces the ROOT; the others in p4_evidence.SRC describe downstream
# consumers and do not invalidate an endpoint.
RECEIPT_SOURCE_KEY = "unfold_blob"


# The standard-P4 review surface: what a verifier verdict is understood to have reviewed when
# it does not declare its own scope. Used by the token gate to prove that the files the verdict
# covered have not changed between the reviewed commit and HEAD.
# REPAIR-7 item 2. This was drawn by FILENAME PREFIX, which is a proxy, and it omitted every
# module the chain actually executes -- uq_math, project_cov_nd, unfold_nd_omnifold_unbinned,
# xsec_nd, omnifold. A verdict could therefore authorize materially changed execution code.
# Third instance of the corpus-definition error, so the surface is now DERIVED from the import
# graph rather than curated, and a test asserts the previously-missing modules are in it.
STANDARD_P4_SURFACE_GLOBS = (
    "nd-unfolding/p4_*.py",
    "nd-unfolding/run_p4_*.sh",
    "nd-unfolding/tests/test_p4_*.py",
)
# Roots of the standard-P4 execution graph: what the driver actually invokes.
STANDARD_P4_ENTRYPOINTS = (
    "nd-unfolding/p4_evidence.py",
    "nd-unfolding/p4_build_components.py",
    "nd-unfolding/p4_validate_active_lateral.py",
    "nd-unfolding/p4_project_4d.py",
    "nd-unfolding/p4_check_receipt.py",
    "nd-unfolding/p4_check_verifier_token.py",
    "nd-unfolding/unfold_nd_omnifold_unbinned.py",
)
# Where first-party imports may resolve. Anything outside these is a third-party dependency and
# is out of scope for a source-identity check.
_IMPORT_SEARCH_DIRS = ("nd-unfolding", "2d-unfolding", "unbinned_unfolding/python", ".")


def standard_p4_execution_surface(entrypoints=None, max_depth=6):
    """Every tracked first-party module reachable from the chain's entrypoints, by IMPORT.

    Derived, not curated: the previous surface was a filename-prefix glob and silently omitted
    the modules that do the work. Falls back to the glob surface if git is unavailable, and the
    caller must treat an empty result as a refusal rather than an empty scope."""
    import ast
    tracked = set()
    try:
        tracked = set(subprocess.check_output(["git", "ls-files"], cwd=REPO_ROOT,
                                              text=True).splitlines())
    except Exception:
        return sorted(tracked_files_matching(STANDARD_P4_SURFACE_GLOBS))

    def resolve(mod):
        for d in _IMPORT_SEARCH_DIRS:
            cand = f"{d}/{mod.replace('.', '/')}.py".lstrip("./")
            if cand in tracked:
                return cand
        return None

    seen, frontier = set(), list(entrypoints or STANDARD_P4_ENTRYPOINTS)
    for _ in range(max_depth):
        nxt = []
        for rel in frontier:
            if rel in seen or rel not in tracked:
                continue
            seen.add(rel)
            try:
                tree = ast.parse((REPO_ROOT_PATH / rel).read_text(errors="replace"))
            except Exception:
                continue
            for node in ast.walk(tree):
                names = []
                if isinstance(node, ast.Import):
                    names = [a.name for a in node.names]
                elif isinstance(node, ast.ImportFrom) and node.module and node.level == 0:
                    names = [node.module]
                for n in names:
                    r = resolve(n)
                    if r and r not in seen:
                        nxt.append(r)
        if not nxt:
            break
        frontier = nxt
    # the shell drivers are executed, not imported, so add them explicitly
    seen.update(p for p in tracked if p.startswith("nd-unfolding/run_p4_") and p.endswith(".sh"))
    return sorted(seen)


def tracked_files_matching(globs, rev="HEAD"):
    """Tracked paths at `rev` matching any glob. Sorted, so the result is order-stable."""
    out = set()
    for g in globs:
        try:
            r = subprocess.check_output(["git", "ls-tree", "-r", "--name-only", rev],
                                        cwd=REPO_ROOT, text=True,
                                        stderr=subprocess.DEVNULL).splitlines()
        except Exception:
            return []
        import fnmatch
        out.update(p for p in r if fnmatch.fnmatch(p, g))
    return sorted(out)


def paths_unchanged_between(rev_a, rev_b, paths):
    """Every path in `paths` has the same blob at rev_a and rev_b.

    Returns (ok, [differing paths]). Fails CLOSED: if git cannot answer for a path, that path
    counts as differing, because an unverifiable claim is not a satisfied one."""
    differing = []
    for p in paths:
        try:
            a = subprocess.check_output(["git", "rev-parse", f"{rev_a}:{p}"], cwd=REPO_ROOT,
                                        text=True, stderr=subprocess.DEVNULL).strip()
        except Exception:
            a = None
        try:
            b = subprocess.check_output(["git", "rev-parse", f"{rev_b}:{p}"], cwd=REPO_ROOT,
                                        text=True, stderr=subprocess.DEVNULL).strip()
        except Exception:
            b = None
        if a is None or b is None or a != b:
            differing.append(p)
    return (not differing), differing


def code_rev_in_history(rev, head=None):
    """True iff `rev` is reachable from HEAD in this repository (ancestor of, or equal to).

    Deliberately reachability rather than equality -- see the note in validate_endpoint_receipt.
    Fails CLOSED: if git cannot answer, the answer is False, because an unverifiable provenance
    claim is not a satisfied one."""
    if not isinstance(rev, str) or not rev.strip():
        return False
    try:
        subprocess.check_call(["git", "merge-base", "--is-ancestor", rev.strip(), head or "HEAD"],
                              cwd=REPO_ROOT, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return True
    except Exception:
        return False


def validate_endpoint_receipt(rec, *, tag, root_sha256, merged_sha256,
                              central5d_sha256, config_hash, bkg_mode,
                              code_rev, unfold_blob):
    """Fail closed unless the receipt is complete AND every recorded identity matches the
    live/committed one. Returns True, or raises P4GateError naming the first mismatch.

    REPAIR-5 (defect 2). The previous version required `code_rev` to be a NON-EMPTY STRING and
    compared it to nothing, and the receipt recorded no source identity at all -- so an
    endpoint produced under a changed unfold driver was still skipped. That is the third
    instance in this chain of "assert presence, never compare": the first is the
    `P4_VERIFIER_PASS` non-emptiness gate (KNOWN_ISSUES #21), the second is the `identities`
    block whose members were literal `True`. Presence is not evidence; both `code_rev` and the
    producing driver's committed blob are now COMPARED."""
    require(isinstance(rec, dict) and rec, f"receipt for {tag} is not a JSON object")
    missing = [k for k in RECEIPT_REQUIRED_KEYS if k not in rec]
    require(not missing, f"receipt {tag} missing required keys {missing} (incomplete legacy format)")
    require(rec["mode"] in RECEIPT_MODES, f"receipt {tag} unknown mode {rec['mode']!r}")
    require(rec["tag"] == tag, f"receipt tag {rec['tag']!r} != {tag!r} (receipt/ROOT pair mismatch)")
    require(rec["root_sha256"] == root_sha256,
            f"receipt {tag} root_sha256 drift: recorded {rec['root_sha256']} vs live {root_sha256}")
    require(rec["merged_sha256"] == merged_sha256,
            f"receipt {tag} merged_sha256 drift vs the orchestrator receipt")
    require(rec["central5d_sha256"] == central5d_sha256,
            f"receipt {tag} central5d_sha256 drift (the central moved under this endpoint)")
    require(rec["config_hash"] == config_hash,
            f"receipt {tag} config_hash drift: produced under a different unfold configuration")
    require(rec["bkg_mode"] == bkg_mode,
            f"receipt {tag} bkg_mode {rec['bkg_mode']!r} != declared {bkg_mode!r}")
    # D2: compared, not merely present.
    require(isinstance(rec["code_rev"], str) and rec["code_rev"],
            f"receipt {tag} has no code_rev")
    require(isinstance(code_rev, str) and code_rev,
            f"cannot validate receipt {tag}: no live code_rev to compare against")
    # REPAIR-6b. This used to require code_rev == HEAD, and that was WRONG in the same way
    # KNOWN_ISSUES #24 describes: it broke on correct behaviour. Any commit anywhere in the repo
    # -- including another lane's, touching nothing this chain reads -- expired all ten receipts
    # while the code that produced them was byte-identical. Caught by the self-check on the first
    # production run: the PET lane advanced main by 8 commits mid-run, HEAD moved
    # 42268b6 -> 203ff01, `git diff` on the unfold driver was EMPTY, and the gate rejected all ten.
    #
    # The producing-code binding is `unfold_blob`, which IS strictly compared below. `code_rev` is
    # repository context, so the honest check is REACHABILITY, not equality: the receipt must come
    # from this history. That still catches a receipt carried in from a foreign branch or a
    # rewritten history, and does not expire on unrelated work.
    require(code_rev_in_history(rec["code_rev"]),
            f"receipt {tag} code_rev {rec['code_rev']} is not an ancestor of HEAD ({code_rev}): "
            f"this receipt did not come from this repository's history")
    require(isinstance(unfold_blob, str) and unfold_blob,
            f"cannot validate receipt {tag}: no committed unfold-driver blob to compare against")
    require(rec[RECEIPT_SOURCE_KEY] == unfold_blob,
            f"receipt {tag} unfold_blob {rec[RECEIPT_SOURCE_KEY]} != committed {unfold_blob}: the "
            f"unfold driver changed since this endpoint was produced")
    return True


def cmask_order_hash_4d(mask):
    """4D reported-mask + C-order fingerprint (repair-4, defect 5c).

    `mask_order_hash` fails closed on GRID_NBINS, which is the 5D grid, so the 4D mask had no
    hash helper and the projector compared only the reported COUNT. A count is not an ordering:
    a permuted 4D mask with the same population passed. Same construction as the 5D helper --
    C-order indices of the selected bins -- so the two are comparable by eye in a manifest.
    Deliberately NOT size-pinned: the 4D grid is a marginal of the 5D one and the standard lane
    has no pinned canonical 4D target (see RUNBOOK-20260807 §7.4)."""
    idx = np.nonzero(np.asarray(mask))[0].astype(np.int64)
    require(idx.size > 0, "4D reported mask is empty")
    return hashlib.sha256(idx.tobytes() + b"|C").hexdigest()


def matrix_content_hash(M):
    """Deterministic digest of a matrix's CONTENTS (repair-4, defect 5d).

    The projection receipt recorded only `M_shape`, which two different projectors of the same
    dimensions share. Hashes C-contiguous float64 bytes plus the shape, so a changed weight is
    caught and a transposed/reshaped M cannot collide with the original."""
    A = np.ascontiguousarray(np.asarray(M, dtype=np.float64))
    h = hashlib.sha256()
    h.update(repr(A.shape).encode()); h.update(b"|C|f8|"); h.update(A.tobytes())
    return h.hexdigest()


def check_full_total_identity(Ccomb, Csyst, Cstat, Cml, rtol=1e-9):
    """PROVE C_combined = C_syst + C_stat + C_ML by comparing the residual to the actual
    stat and ML blocks. Returns the measured max-relative error.

    REPAIR-5 (defect 4b / 6). Repair-4 checked only that `C_combined - C_syst` was symmetric
    PSD and called that the full-total identity, in a gate name, a receipt field and a test
    name. PSD is NECESSARY but nowhere near SUFFICIENT: every covariance-shaped residual passes
    it, including one built from the wrong stat block, a doubled ML block, or a residual that
    simply is not stat+ML at all. Naming a weak check after a strong claim is the same
    "strong name over weak check" pattern as the test that passed because argparse rejected an
    argument before the guard it named ever ran (verifier defect 6b). This compares."""
    resid = np.asarray(Ccomb, float) - np.asarray(Csyst, float)
    expect = np.asarray(Cstat, float) + np.asarray(Cml, float)
    require(resid.shape == expect.shape,
            f"full-total identity: residual {resid.shape} != stat+ML {expect.shape}")
    # PSD of the residual is retained as a SEPARATE, weaker sanity check -- not as the identity.
    check_symmetric_psd(resid)
    return prove_identity(resid, expect, rtol, "C_combined - C_syst == C_stat + C_ML")


def check_declared_migration_policy(policy, census_abs, band, nonzero_bands, zero_bands):
    """Compare the DECLARED migration policy against the OBSERVED census.

    REPAIR-5 (pattern sweep). `check_merged_metadata` required `migration_policy` to be
    truthy and compared it to nothing -- a declared policy no consumer ever checked, which is
    the same presence-not-comparison pattern as defect 2's `code_rev`. A merged file could
    declare any policy string, or the wrong one, and pass."""
    require(isinstance(policy, str) and policy.strip(), "declared migration policy missing")
    require(band in nonzero_bands or band in zero_bands,
            f"band {band} is in neither the nonzero- nor the zero-migration set")
    n = int(census_abs)
    if band in nonzero_bands:
        require(n > 0, f"{band} declares selection-complete migration but census is {n}")
        require("selection" in policy.lower(),
                f"{band} migrates ({n}) but declares policy {policy!r}, which does not claim "
                f"selection completeness")
    else:
        require(n == 0, f"{band} is declared bin-migration-only but census is {n}")
        # REPAIR-6: the zero side never validated the policy TEXT, so a band could migrate zero
        # events while declaring a selection-complete policy and pass.
        require("selection" not in policy.lower() or "only" in policy.lower(),
                f"{band} has zero selection migration but declares policy {policy!r}, which "
                f"claims selection completeness")
    return True


def require_exact_endpoint_tags(tags):
    """Reject BOTH missing and EXTRA tags. The old inventory only looked for the ten expected
    names, so an eleventh product in the directory was invisible to it."""
    got, want = set(tags), {f"{b}_{e}" for b in BANDS for e in ENDPOINTS}
    require(not (want - got), f"missing endpoint tags: {sorted(want - got)}")
    require(not (got - want), f"unexpected extra endpoint tags: {sorted(got - want)}")
    return True


def sha256_file(path, _bufsz=1 << 20):
    """Durable file digest (login-computable; no ROOT)."""
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(_bufsz), b""):
            h.update(chunk)
    return h.hexdigest()


def canonical_endpoints():
    """The exact 10 (band, endpoint) logical tasks, in fixed order."""
    return [(b, ep) for b in BANDS for ep in ENDPOINTS]


def endpoint_manifest_hash(entries):
    """entries: iterable of (band, endpoint, fingerprint). Hash is order-independent
    over the SET but requires the exact 10-endpoint inventory (fail-closed)."""
    seen = {}
    for band, ep, fp in entries:
        require(band in BANDS, f"unknown band {band!r}")
        require(ep in ENDPOINTS, f"bad endpoint {ep!r}")
        seen[(band, int(ep))] = str(fp)
    require(len(seen) == N_ENDPOINTS,
            f"expected exactly {N_ENDPOINTS} endpoints, got {len(seen)} "
            f"(missing {sorted(set(canonical_endpoints())-set(seen))})")
    blob = json.dumps({f"{b}_{e}": seen[(b, e)] for (b, e) in canonical_endpoints()},
                      sort_keys=True)
    return hashlib.sha256(blob.encode()).hexdigest()


def mask_order_hash(mask):
    """Hash of the reported-bin mask + C-order. mask: 1-D bool/int array over the
    full grid. Pins which bins are reported and their order so a projection or a
    component sum can never silently mix masks."""
    m = np.asarray(mask)
    require(m.ndim == 1, "mask must be 1-D (C-order ravel over the 5D grid)")
    require(m.size == GRID_NBINS, f"mask size {m.size} != grid {GRID_NBINS}")
    idx = np.nonzero(m.astype(bool))[0].astype(np.int64)
    require(idx.size > 0, "mask selects zero reported bins")
    return hashlib.sha256(idx.tobytes() + b"|C").hexdigest(), int(idx.size)


# ---------------------------------------------------------------- inventory gates
def require_complete_unfold_set(present_tags):
    """present_tags: iterable of '<band>_<ep>' that passed CONTENT validation.
    Fail-closed unless all 10 canonical endpoints are present+valid."""
    present = set(present_tags)
    need = {f"{b}_{e}" for (b, e) in canonical_endpoints()}
    missing = sorted(need - present)
    require(not missing, f"incomplete unfold set: missing/invalid {missing}")
    require(present == need, f"unexpected unfold tags: {sorted(present - need)}")
    return True


# REPAIR-7 item 3: `check_merged_metadata` is DELETED, not repaired.
#
# It had NO production caller -- only its own tests -- while `p4_evidence.py` re-implemented the
# same checks inline with `need()`. Repair-5 and repair-6 both improved it, which means both
# improved a function that does not run, and the verifier was right that deferring Pattern C is
# indefensible when the deferral makes the fix a no-op: a fix inside a dead path is WORSE than
# no fix, because it reads as done.
#
# Same disposition as legacy-attest. The checks it performed live in p4_evidence.py's inline
# path, which is the one that executes; the native-miss comparison repair-6 put here has been
# moved there. If a shared helper is wanted later, it must be introduced WITH its caller.


# ---------------------------------------------------------------- covariance gates
def check_symmetric_psd(C, rtol_sym=1e-9, psd_atol_ratio=1e-12):
    C = np.asarray(C, dtype=float)
    require(C.ndim == 2 and C.shape[0] == C.shape[1], "covariance must be square 2-D")
    require(np.all(np.isfinite(C)), "covariance has non-finite entries")
    denom = max(1e-300, np.max(np.abs(C)))
    asym = np.max(np.abs(C - C.T)) / denom
    require(asym <= rtol_sym, f"covariance not symmetric (rel {asym:.2e})")
    ev = np.linalg.eigvalsh(0.5 * (C + C.T))
    require(ev[0] >= -psd_atol_ratio * abs(ev[-1]),
            f"covariance not PSD (min/max eig {ev[0]/max(1e-300,abs(ev[-1])):.2e})")
    d = np.diag(C)
    # REPAIR-6, folding in BEN-044 from the PET lane ("an absolute tolerance inherited into a
    # problem whose natural scale is ~1e-80 makes a gate that cannot fail"). This read
    # `d >= -1e-30` ABSOLUTELY. The standard 5D covariance has sqrt(tr) ~ 5.3e-38 over 10694
    # reported bins, so a typical diagonal entry is ~1e-79 -- the old bound sat ~49 orders of
    # magnitude above what it was supposed to bound, and a diagonal of -1e-31 (a corruption
    # ~48 orders larger than the signal) passed it. Now relative to the matrix's own scale.
    # Power-proved in tests/test_p4_guard_mutations.py at the real 1e-79 scale, per BEN-044's
    # rule that a gate must be shown able to fail in the commit that writes it.
    require(np.all(np.isfinite(d)), "non-finite diagonal")
    require(np.all(d >= -psd_atol_ratio * denom),
            f"negative diagonal beyond tolerance (min {np.min(d):.3e} vs "
            f"-{psd_atol_ratio:.0e} * max|C| = {-psd_atol_ratio * denom:.3e})")
    return {"rel_asymmetry": float(asym), "min_eig": float(ev[0]), "max_eig": float(ev[-1]),
            "diag_tol_absolute": float(psd_atol_ratio * denom)}


def require_exact_bands(band_covs):
    """band_covs: dict band -> cov. Must be EXACTLY the 5 kinematic bands."""
    got = set(band_covs)
    require(got == set(BANDS),
            f"active-lateral bands mismatch: got {sorted(got)}, need {sorted(BANDS)}")
    return True


def component_traces_positive_finite(band_covs):
    tr = {}
    for b in BANDS:
        require(b in band_covs, f"missing component band {b}")
        C = np.asarray(band_covs[b], dtype=float)
        require(np.all(np.isfinite(C)), f"component {b} has non-finite entries")
        t = float(np.trace(C))
        require(np.isfinite(t) and t > 0.0, f"component {b} trace not positive-finite ({t})")
        tr[b] = t
    return tr


def check_component_sum(total, band_covs, rtol=1e-9):
    """total must equal the EXACT sum of the 5 per-band component covariances."""
    require_exact_bands(band_covs)
    total = np.asarray(total, dtype=float)
    s = np.zeros_like(total)
    for b in BANDS:
        Cb = np.asarray(band_covs[b], dtype=float)
        require(Cb.shape == total.shape, f"component {b} shape {Cb.shape} != total {total.shape}")
        s = s + Cb
    denom = max(1e-300, np.max(np.abs(total)))
    err = np.max(np.abs(total - s)) / denom
    require(err <= rtol, f"component sum mismatch (rel {err:.2e}) — total != sum of bands")
    return float(err)


def check_support_comparison(active_cov, support_cov):
    """Complete support comparison: both present, same shape/mask/order. Returns
    sqrt-trace ratio (active/support). Fail-closed if the support block is absent."""
    require(active_cov is not None, "active lateral block missing")
    require(support_cov is not None, "support-limited comparison block missing")
    A = np.asarray(active_cov, dtype=float); S = np.asarray(support_cov, dtype=float)
    require(A.shape == S.shape, f"active/support shape mismatch {A.shape} vs {S.shape}")
    sta = float(np.sqrt(max(0.0, np.trace(A)))); sts = float(np.sqrt(max(0.0, np.trace(S))))
    require(sts > 0, "support block has zero trace")
    return {"sqrt_tr_active": sta, "sqrt_tr_support": sts, "ratio": sta / sts}


# ---------------------------------------------------------------- deterministic projection map
def build_projection_M(edges, drop_axis, mask_high, mask_low):
    """Deterministic 5D->4D map by WIDTH-WEIGHTED marginalization of one axis.
    edges: ordered per-axis edge arrays (pt,pz,eavail,q3,W). drop_axis: axis index to
    marginalize (W=4). mask_high/mask_low: reported-bin bool masks over the full high/low
    grids (C-order). Returns dense M (n_low_reported x n_high_reported) with
    M[a,b] = width_drop[k] when high bin b decomposes to low bin a + dropped index k.
    density convention: x_low = M @ x_high, C_low = M C_high M^T."""
    nb = [np.asarray(e).size - 1 for e in edges]
    require(len(nb) == 5, "expected 5 axes")
    total_high = int(np.prod(nb))
    require(int(np.asarray(mask_high).size) == total_high, "mask_high size != high grid")
    wdrop = np.asarray(edges[drop_axis], float)[1:] - np.asarray(edges[drop_axis], float)[:-1]
    nb_low = [n for i, n in enumerate(nb) if i != drop_axis]
    total_low = int(np.prod(nb_low))
    require(int(np.asarray(mask_low).size) == total_low, "mask_low size != low grid")
    strides_h = np.array([int(np.prod(nb[i + 1:])) for i in range(5)])          # C-order strides
    strides_l = np.array([int(np.prod(nb_low[i + 1:])) for i in range(4)])
    mh = np.nonzero(np.asarray(mask_high).astype(bool))[0]
    ml = np.nonzero(np.asarray(mask_low).astype(bool))[0]
    low_pos = {int(g): r for r, g in enumerate(ml)}                              # low global -> reported row
    M = np.zeros((ml.size, mh.size), dtype=float)
    for col, g in enumerate(mh):
        midx = [(g // strides_h[i]) % nb[i] for i in range(5)]                   # 5D multi-index
        k = midx[drop_axis]
        low_multi = [midx[i] for i in range(5) if i != drop_axis]
        glow = int(np.dot(low_multi, strides_l))
        row = low_pos.get(glow)
        require(row is not None, f"high reported bin {g} maps to non-reported low bin {glow}")
        M[row, col] = wdrop[k]
    return M


# ---------------------------------------------------------------- projection gates
def project(C_high, M):
    """5D->4D (or any) projection C_low = M C_high M^T (preserves density/order)."""
    C_high = np.asarray(C_high, dtype=float); M = np.asarray(M, dtype=float)
    require(M.shape[1] == C_high.shape[0], f"M cols {M.shape[1]} != C dim {C_high.shape[0]}")
    return M @ C_high @ M.T


def check_projection_nonmutation(C_high, M, x_high, x_low_frozen, rtol_central=3e-2):
    """Enforce projected covariance validity AND central non-mutation:
    C_low = M C_high M^T is symmetric/PSD, and M @ x_high reproduces the frozen
    lower-dim central within tolerance (the projection must not mutate the central)."""
    C_low = project(C_high, M)
    stats = check_symmetric_psd(C_low)
    xin = np.asarray(x_high, dtype=float); xfr = np.asarray(x_low_frozen, dtype=float)
    proj = M @ xin
    require(proj.shape == xfr.shape, f"projected central shape {proj.shape} != frozen {xfr.shape}")
    denom = np.where(np.abs(xfr) > 0, np.abs(xfr), 1.0)
    rel = float(np.max(np.abs(proj - xfr) / denom))
    require(rel <= rtol_central, f"projection mutates central (max rel {rel:.2e})")
    stats["central_max_rel"] = rel
    return C_low, stats

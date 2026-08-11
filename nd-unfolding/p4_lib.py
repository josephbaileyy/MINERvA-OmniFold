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
# READ 103.4x CORRECTLY: it is the leg's DYNAMIC RANGE -- a property of the instrument, derived
# from one endpoint's worst per-bin deviation and sqrt(N). It is NOT a spread, and it is not the
# observed variation across endpoints, which is 2589x (rel_integral 1.110e-15 to 2.874e-12 over
# the ten). The two numbers are the same order of magnitude apart from each other as they are
# from nothing in particular, and an earlier draft of this reasoning did quote a "~110x span" as
# though it were an observed spread -- it was three maxima taken from three different
# comparisons, which is not a distribution at all. If you find yourself citing a range here, say
# which of the two you mean.
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


RETAINED_KEY_PREFIX = "hCov_retained5d_"


def retained_key(band):
    """Forward construction ONLY. Never recover a band name by stripping this prefix: band
    `__Normalization_flat` yields `hCov_retained5d___Normalization_flat` -- THREE underscores,
    because the band's own leading `__` follows a prefix already ending in `_`. A naive strip or an
    `[A-Za-z]*` glob mishandles it, which is why every expected-key set below is built forward from
    band names and no code here parses a key backwards."""
    require(isinstance(band, str) and band, "band name must be a non-empty string")
    return f"{RETAINED_KEY_PREFIX}{band}"


def require_band_set_completeness(comp, required_bands, required_hashes, lateral_bands,
                                  required_support_sha=None):
    """B1 / verifier defect #6. Verify the manifest's band set and component identity against an
    EXTERNAL REQUIRED INVENTORY, never against the manifest's own list.

    Why the manifest cannot be its own referee, and why the candidate ROOT cannot either: the
    hazard is a BUILD that enumerated the wrong set. In that case the stored `C_syst` was built
    from the short set, the manifest lists the short set, and `retained_sum + active_total ==
    C_syst` reconstructs PERFECTLY. Both the total and the list are consistent -- they are simply
    both missing a band. The candidate ROOT is a downstream product of the same build and inherits
    the omission, so the only object that can referee is the SUPPORT FAMILY, whose sha256 the
    manifest itself pins (`support_family_sha256`) and from which `p4_build_components.py`
    enumerates `hCov_universe5d_*` in the first place.

    `required_bands`  : every band in the support family (excluding its `_total`).
    `required_hashes` : {band: content sha256} recomputed from the support family.
    `lateral_bands`   : the bands replaced by active MAT blocks (p4_lib.BANDS).

    Checks set equality on all four places the band set appears, then component IDENTITY. The
    verdict wording is "band-set equality OR component identity"; both halves are done here."""
    # BIND THE REFEREE FIRST. Everything below compares the manifest against an inventory taken
    # from a support-family ROOT chosen by the caller (`--support`). Nothing previously required
    # that ROOT to be the one the build actually enumerated: the validator never checked
    # `support_family_sha256`, and the adopter's check is a different thing (it hashes the file at
    # the path the manifest records, which cannot detect a validator refereeing against another
    # object). An authority that is not pinned is not an authority -- the check would happily
    # confirm a manifest against the wrong inventory and report a clean set match.
    if required_support_sha is not None:
        got = comp.get("support_family_sha256")
        require(got is not None,
                "component manifest records no support_family_sha256, so the inventory it was "
                "built from cannot be identified")
        require(got == required_support_sha,
                f"support-family mismatch: this check is refereeing against a support family whose "
                f"sha256 is {required_support_sha}, but the manifest was built from {got}. The "
                f"band-set comparison below would be meaningless against the wrong inventory.")
    req = set(required_bands)
    lat = set(lateral_bands)
    require(lat <= req, f"lateral bands not present in the support family: {sorted(lat - req)}")
    exp_retained = req - lat

    def _cmp(name, got, want):
        got, want = set(got or []), set(want)
        require(got == want,
                f"{name}: band set does not match the support-family inventory -- "
                f"missing {sorted(want - got)!r}, unexpected {sorted(got - want)!r}. This is "
                f"checked against the support family, not against the manifest, because a build "
                f"that enumerated the wrong set produces a manifest that reconstructs perfectly.")

    _cmp("all_syst_bands", comp.get("all_syst_bands"), req)
    _cmp("retained_bands", comp.get("retained_bands"), exp_retained)
    _cmp("replaced_lateral_bands", comp.get("replaced_lateral_bands"), lat)
    _cmp("component_content_hash keys", (comp.get("component_content_hash") or {}).keys(), req)

    # candidate_keys: built FORWARD from band names, never by parsing keys
    exp_keys = ({retained_key(b) for b in exp_retained}
                | {candidate_band_key(b) for b in lat}
                | {CANDIDATE_ACTIVE_TOTAL_KEY, CANDIDATE_SYST_KEY, CANDIDATE_TOTAL_KEY})
    _cmp("candidate_keys", comp.get("candidate_keys"), exp_keys)

    # COMPONENT IDENTITY -- the other half of the verdict. Set equality cannot see a manifest that
    # names the right bands while the components behind them are not the support family's.
    got_h = comp.get("component_content_hash") or {}
    bad = sorted(b for b in req if got_h.get(b) != required_hashes.get(b))
    require(not bad,
            f"component identity mismatch against the support family for {len(bad)} band(s): "
            f"{bad[:5]}{' ...' if len(bad) > 5 else ''}. The band set is correct but at least one "
            f"recorded component hash is not the support family's component.")
    return {"n_required_bands": len(req), "n_retained_expected": len(exp_retained),
            "n_candidate_keys_expected": len(exp_keys)}


RESUME_BLOB_FIELD = "surface_blobs"
RESUME_GRANDFATHER_REASON = (
    "receipt predates the 2026-08-10 B2 surface binding and carries no per-path blob record")

# The producing driver, named ONCE. Both the launcher (which stamps the closure into a receipt)
# and p4_check_receipt.py (which independently re-derives it) read this, so the two cannot come
# to disagree about what "the producing closure" is rooted at -- which was half of PB2: the
# closure helper was correct and simply nothing in production called it.
UNFOLD_DRIVER_REL = "nd-unfolding/unfold_nd_omnifold_unbinned.py"

# ---- receipt schema versioning (PB2 repair, 2026-08-11) ----------------------------------
# PB2's legacy rule -- "no surface_blobs field means grandfathered" -- was correct for the
# receipts that existed when it was written, and became unsafe the moment the launcher started
# emitting the field: from then on, absence is no longer evidence of age. A receipt written by
# TODAY's launcher that somehow lacks the field is malformed, and silently reading it as legacy
# would hand the grandfather clause to exactly the receipts it was never meant to cover.
#
# So age is now DECLARED rather than inferred. A receipt carrying `receipt_schema` >=
# RECEIPT_SCHEMA_SURFACE asserts it was written by a launcher that binds the closure, and is held
# to that: missing or changed members reject. Only a receipt that declares no schema AND carries
# no blob record is grandfathered, and that class is closed -- nothing writes it any more.
RECEIPT_SCHEMA_FIELD = "receipt_schema"
RECEIPT_SCHEMA_SURFACE = 2          # first schema whose receipts MUST carry surface_blobs
RECEIPT_SCHEMA_CURRENT = 2          # what the launcher stamps today


def resolve_head_blobs(paths, repo_root=None):
    """path -> committed blob at HEAD, for every path given.

    Fails CLOSED: a path git cannot resolve raises rather than mapping to None, because a None
    on both sides compares equal and would read as "unchanged". The closure is derived from
    `git ls-files`, so the reachable way to land here is a path staged but never committed --
    an identity that genuinely cannot be checked, which is not the same as one that matches."""
    root = repo_root or REPO_ROOT
    out, unresolved = {}, []
    for rel in paths:
        try:
            out[rel] = subprocess.check_output(["git", "rev-parse", f"HEAD:{rel}"], cwd=root,
                                               text=True, stderr=subprocess.DEVNULL).strip()
        except Exception:
            unresolved.append(rel)
    require(not unresolved,
            f"cannot resolve the committed blob of {len(unresolved)} producing-closure path(s): "
            f"{unresolved[:4]} -- refusing to accept a receipt whose producing source cannot be "
            f"checked")
    return out


def producing_closure_blobs(repo_root=None, driver_rel=None):
    """(closure, head_blobs) from the ONE derivation both producer and consumer use.

    PB2's defect was not a wrong closure -- `producing_closure` was right and its unit fixtures
    passed. It was that the launcher wrote no blob record and the checker never called the
    helper, so the property was proven about a function nothing in production invoked. This is
    the seam that makes the two sides share a derivation instead of each carrying a path list."""
    root = repo_root or REPO_ROOT
    closure = producing_closure(root, driver_rel or UNFOLD_DRIVER_REL)
    require(closure, "producing closure derived empty -- refusing to bind a receipt to nothing")
    require((driver_rel or UNFOLD_DRIVER_REL) in closure,
            "producing closure does not contain its own driver; derivation is broken")
    return closure, resolve_head_blobs(closure, root)


def producing_closure(repo_root, driver_rel):
    """The modules that can actually execute while an endpoint ROOT is produced: the unfold driver
    plus everything reachable from it through imports, transitively.

    B2 DESIGN DECISION, 2026-08-10 -- resume binds the PRODUCING CLOSURE, not the whole execution
    surface. The surface is 15 Python modules; only 6 are reachable from the unfold driver. The
    other 9 (`p4_evidence`, `p4_lib`, `p4_project_4d`, `p4_build_components`,
    `p4_validate_active_lateral`, `p4_check_receipt`, `p4_check_verifier_token`, `project_cov_nd`,
    `uq_math`) are reached from OTHER entrypoints and cannot run while an endpoint is unfolded.

    Why not bind all 15, which is simpler. A module that cannot execute during production cannot
    have affected the product, so binding it is not conservatism -- it is a false positive by
    construction. And the cost is concrete: this lane commits to `p4_lib.py` almost every round,
    and whole-surface binding would invalidate all ten endpoint resumes on each such commit -- ten
    re-unfolds, ~1h40m, for code that never ran. A check that fires constantly on correct data is
    a check that gets disabled, which is `KNOWN_ISSUES #24` twice over (`code_rev == HEAD` and
    `verifier_crosscheck` both blocked demonstrably correct data and both had to be withdrawn).
    Re-introducing whole-tree binding through the resume path repeats exactly what repair-6 undid.

    The claim the receipt therefore makes is "resume binds the producing closure", NOT "resume
    binds the whole surface". Those are different claims and the acceptance record says which."""
    import ast as _ast
    root = _pl.Path(repo_root)
    seen, out = set(), set()
    stack = [driver_rel]
    # module-name -> repo-relative path, over the dirs the chain actually imports from
    # TRACKED FILES ONLY. Globbing the filesystem let an UNTRACKED module enter the closure:
    # demonstrated 2026-08-10 with a stray `scratch_probe.py`, which resume then demanded a blob
    # for -- `git rev-parse HEAD:<path>` exits 128, no blob can exist, and a correct endpoint is
    # blocked forever. That is the KNOWN_ISSUES #24 over-rejection class this very item exists to
    # avoid, reached through the closure derivation instead of through the check. Found because
    # the PET lane mentioned staging an old driver on scratch; theirs is outside the repo and was
    # never a risk, but it prompted asking whether the derivation was restricted to tracked files.
    # It was not.
    tracked = set(subprocess.run(["git", "ls-files"], cwd=str(root),
                                 capture_output=True, text=True).stdout.split())
    index = {}
    for d in ("nd-unfolding", "unbinned_unfolding/python", "2d-unfolding"):
        for rel_p in sorted(q for q in tracked if q.startswith(d + "/") and q.endswith(".py")
                            and "/" not in q[len(d) + 1:]):
            index.setdefault(_pl.Path(rel_p).stem, rel_p)
    while stack:
        rel = stack.pop()
        if rel in seen:
            continue
        seen.add(rel)
        out.add(rel)
        src = root / rel
        if not src.exists():
            continue
        try:
            tree = _ast.parse(src.read_text(encoding="utf-8", errors="replace"))
        except SyntaxError:
            continue
        for n in _ast.walk(tree):
            names = []
            if isinstance(n, _ast.Import):
                names = [a.name.split(".")[0] for a in n.names]
            elif isinstance(n, _ast.ImportFrom) and n.module and n.level == 0:
                names = [n.module.split(".")[0]]
            for nm in names:
                tgt = index.get(nm)
                if tgt and tgt not in seen:
                    stack.append(tgt)
    return sorted(out)


def check_resume_surface(receipt, closure, head_blobs):
    """B2 / verifier defect #2. Decide whether a receipt may be RESUMED (skipped).

    Returns (may_skip, reason). Never raises for a legacy receipt -- over-rejection here means
    re-running correct endpoints, which is the failure this lane has shipped twice.

    LEGACY RULE, decided in this same commit per the packet: **explicit grandfather**, not backfill.
    Backfilling `surface_blobs` from the receipt's recorded `code_rev` is possible and was
    considered -- the blobs at that commit are resolvable -- but it would materialise a DERIVED
    value into a field whose other instances are OBSERVED, making a derived blob indistinguishable
    from a recorded one. That is precisely the proxy-binding pattern this lane spent four rounds
    removing. A grandfathered receipt is honest about knowing less; a backfilled one is not.

    PB2 REPAIR, 2026-08-11 -- the grandfather clause is now BOUNDED BY A DECLARED SCHEMA. It was
    keyed on the field being absent, which stopped being a statement about age as soon as the
    launcher began writing the field. See RECEIPT_SCHEMA_SURFACE."""
    got = receipt.get(RESUME_BLOB_FIELD)
    declared = receipt.get(RECEIPT_SCHEMA_FIELD)

    # A declared schema is a claim about the writer, so it is checked before anything else and
    # a malformed one never falls through to the legacy branch.
    if declared is not None:
        if isinstance(declared, bool) or not isinstance(declared, int):
            return False, (f"{RECEIPT_SCHEMA_FIELD} {declared!r} is not an integer version -- a "
                           f"receipt that misstates its own schema is malformed, not legacy")
        if declared < RECEIPT_SCHEMA_SURFACE or declared > RECEIPT_SCHEMA_CURRENT:
            return False, (f"{RECEIPT_SCHEMA_FIELD} {declared} is outside the supported range "
                           f"{RECEIPT_SCHEMA_SURFACE}..{RECEIPT_SCHEMA_CURRENT}; no legacy "
                           f"receipt declared a schema, so an invented pre-binding version is "
                           f"malformed rather than grandfathered")
        if declared >= RECEIPT_SCHEMA_SURFACE and got is None:
            return False, (f"receipt declares schema {declared} (>= {RECEIPT_SCHEMA_SURFACE}, which "
                           f"binds the producing closure) but carries no {RESUME_BLOB_FIELD}: a "
                           f"current receipt missing the record is MALFORMED, and the grandfather "
                           f"clause covers receipts written before the binding existed, not this")

    if got is None:
        # closed class: declares no schema and records no blobs, i.e. written before the binding
        return True, f"GRANDFATHERED: {RESUME_GRANDFATHER_REASON}"
    if not isinstance(got, dict):
        return False, f"{RESUME_BLOB_FIELD} is not a path->blob mapping"
    missing = [q for q in closure if q not in got]
    if missing:
        return False, (f"record omits {len(missing)} producing-closure path(s): {missing[:4]} -- "
                       f"a record that is internally consistent about an incomplete set cannot "
                       f"establish what produced the artifact")
    diff = [q for q in closure if got.get(q) != head_blobs.get(q)]
    if diff:
        return False, (f"{len(diff)} producing-closure path(s) changed since this receipt: "
                       f"{diff[:4]}")
    return True, "producing closure matches HEAD"


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
def reachable_low_mask(edges, drop_axis, mask_high):
    """The low-dimensional bins the reported HIGH support actually reaches.

    FIX 1 of 2, 2026-08-10. Stage 6 could not execute on the real products: 5 of the 4830 reported
    4D bins receive no contribution from any reported 5D bin, so `build_projection_M` fail-closed
    (correctly -- those rows would be all-zero and would surface downstream as `rel = 1.0`).

    The resolution is a CONTRACT correction, not a relaxed guard. The projection's low support is
    not "the 4D reported mask"; it is "the part of the 4D reported mask the 5D support reaches".
    That set is DERIVED here and the bidirectional check in `build_projection_M` is left exactly as
    it is -- it becomes a genuine invariant that must never fire in production rather than a thing
    the caller argues with. The dropped bins are recorded by the caller, never silently discarded.

    On the real products the 5 dropped bins hold 3.00e-46 .. 2.09e-44, i.e. 0.0000% of the 4D
    total; that is a fact about these products, not a licence, and the caller records the indices
    and the count so a future set with a material drop is visible rather than absorbed."""
    nb = [np.asarray(e).size - 1 for e in edges]
    require(len(nb) == 5, "expected 5 axes")
    mh = np.asarray(mask_high).astype(bool)
    require(mh.size == int(np.prod(nb)), "mask_high size != high grid")
    nb_low = [n for i, n in enumerate(nb) if i != drop_axis]
    strides_h = np.array([int(np.prod(nb[i + 1:])) for i in range(5)])
    strides_l = np.array([int(np.prod(nb_low[i + 1:])) for i in range(4)])
    out = np.zeros(int(np.prod(nb_low)), dtype=bool)
    for g in np.nonzero(mh)[0]:
        midx = [(g // strides_h[i]) % nb[i] for i in range(5)]
        low_multi = [midx[i] for i in range(5) if i != drop_axis]
        out[int(np.dot(low_multi, strides_l))] = True
    return out


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
    # BOTH DIRECTIONS (2026-08-09, BEN-064). The loop above validates coverage one way only --
    # every reported HIGH bin lands in a reported LOW bin -- and says nothing about reported LOW
    # bins that no HIGH bin reaches. Those rows of M are all-zero, so they survive to the central
    # check as an exact 0 against a nonzero frozen value, i.e. `rel = 1.0` exactly.
    #
    # That is not merely a missed case, it is a MASKING defect: on the real products 5 orphan bins
    # carrying 0.0000% of the 4D total produced `projection mutates central (max rel 1.00e+00)`,
    # and that message hid the actual result (62% of bins over tolerance at a median of 4.4%)
    # behind a number contributed by bins nobody would care about. An error that is loudest about
    # the least important thing is worse than no error, because it redirects the investigation.
    #
    # Fail here, at construction, where the diagnosis is the orphan list itself.
    empty = np.nonzero(~M.any(axis=1))[0]
    require(empty.size == 0,
            f"{empty.size} reported LOW bin(s) receive no contribution from any reported HIGH bin "
            f"(global indices {[int(ml[r]) for r in empty[:10]]}"
            f"{' ...' if empty.size > 10 else ''}); the two reported supports are inconsistent. "
            f"These rows would be all-zero and would reach a central comparison as exact zeros, "
            f"reporting a relative error of 1.0 regardless of how small the bins are.")
    return M


# ---------------------------------------------------------------- projection gates
def project(C_high, M):
    """5D->4D (or any) projection C_low = M C_high M^T (preserves density/order)."""
    C_high = np.asarray(C_high, dtype=float); M = np.asarray(M, dtype=float)
    require(M.shape[1] == C_high.shape[0], f"M cols {M.shape[1]} != C dim {C_high.shape[0]}")
    return M @ C_high @ M.T


# RE-SPECIFIED 2026-08-09 (Joseph). The previous form GATED on `max |M@x5 - x4| / |x4| <= 3%`,
# i.e. it required the 5D->4D marginal to reproduce the INDEPENDENTLY-UNFOLDED 4D central bin by
# bin. That is the equivalence convention the campaign DECLINED on 2026-08-07: the adopted
# position is that 4D IS the marginal and the independent 4D unfold is a CROSS-CHECK. The gate
# therefore tested a proposition the analysis does not assert.
#
# THIS IS A GATE REMOVAL, NOT A TOLERANCE WIDENING, and the distinction is the whole point. The
# measurement stays exactly as it was and is reported in full; what is withdrawn is the pass/fail
# verdict attached to it. Nothing here makes a failing number pass -- see the measured values in
# FINDING-20260809-stage6-central-gate-cannot-pass.md, which are unchanged by this edit.
#
# What IS gated is projection validity, which the analysis does assert: symmetry, PSD, exact
# agreement of M C M^T against a direct block-sum recomputation, and shape/coverage. Those are
# recomputation identities and hold at ~1e-14, the standard the stage-4 identities already meet.
def check_projection_validity(C_high, M, rtol_identity=1e-9):
    """GATE: the projection itself is valid. Recomputation identities only -- nothing here
    compares against an independently-produced product.

      * C_low = M C_high M^T is symmetric and PSD;
      * that product equals a direct block-sum recomputation to `rtol_identity`.

    The second is not redundant with the first: `project()` is one matrix expression and a bug in
    it would produce a matrix that is still symmetric and still PSD. Recomputing the same quantity
    by an independent route is what makes this a check rather than a restatement."""
    C_low = project(C_high, M)
    stats = check_symmetric_psd(C_low)
    # independent route: accumulate row-block by row-block rather than as one M C M^T
    direct = np.zeros_like(C_low)
    MH = M @ np.asarray(C_high, dtype=float)
    for i in range(C_low.shape[0]):
        direct[i, :] = MH[i, :] @ M.T
    scale = max(1e-300, float(np.max(np.abs(C_low))))
    err = float(np.max(np.abs(C_low - direct)) / scale)
    require(err <= rtol_identity,
            f"projection identity M C M^T != direct block sum (rel {err:.3e} > {rtol_identity:.0e})")
    stats["projection_identity_relerr"] = err
    return C_low, stats


def crosscheck_marginal_vs_independent(M, x_high, x_low_independent):
    """REPORT ONLY -- no pass/fail, by specification. Compares the 5D->4D marginal against the
    independently-unfolded lower-dimensional central.

    This is a cross-check between two DIFFERENT estimators, not a consistency requirement. Under
    the adopted convention the marginal is the deliverable and this comparison characterises the
    independent unfold; it does not constrain the marginal. Returns the full distribution rather
    than a max, because on the real products the max is owned by a handful of near-empty bins and
    is actively misleading about the body of the comparison (BEN-064)."""
    proj = M @ np.asarray(x_high, dtype=float)
    xind = np.asarray(x_low_independent, dtype=float)
    require(proj.shape == xind.shape,
            f"cross-check shape {proj.shape} != independent {xind.shape}")
    denom = np.where(np.abs(xind) > 0, np.abs(xind), 1.0)
    rel = (proj - xind) / denom
    a = np.abs(rel)
    out = {"n_bins": int(a.size),
           "median_abs_rel": float(np.median(a)),
           "p90_abs_rel": float(np.percentile(a, 90)),
           "p99_abs_rel": float(np.percentile(a, 99)),
           "max_abs_rel": float(a.max()),
           "frac_marginal_above": float(np.mean(rel > 0)),
           "signed_mean_rel": float(np.mean(rel)),
           "integral_ratio": float(proj.sum() / xind.sum()) if xind.sum() else float("nan"),
           "note": "cross-check between two estimators; NO pass/fail by specification "
                   "(2026-08-09). The marginal is the deliverable."}
    for t in (0.03, 0.10, 0.20):
        out[f"n_over_{int(t*100)}pct"] = int((a > t).sum())
    return out

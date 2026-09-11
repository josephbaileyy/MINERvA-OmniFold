#!/usr/bin/env python3
"""Rigorous many-throw unified systematic covariance vs the block-sum (prepub #1).

The block-sum cov assumes the unfolding responds LINEARLY to each band, so
C_total = sum_b C_b. The decisive test is a TRUE unified throw: shift ALL bands
together per universe, re-unfold, and build the covariance directly. In the linear
regime C_unified == C_blocksum exactly; the difference is the unfolding's nonlinear
cross-band term.

The 2026-06-04 ratio-product proxy was artifact-prone because it multiplied BINNED
spectrum ratios (low-w_cv tail events compounded -> 25x inflation). This driver
avoids that by composing weights at the PER-EVENT level and RE-UNFOLDING each throw
(the proper construction a multi-band event-loop universe would produce, for the
reweight/vertical systematics):

    throw j:  g_b ~ N(0,1) per +-1sigma knob band b;  u ~ U{0..Nflux-1}
    rho_b(g) = rho_plus**g (g>=0), rho_minus**(-g) (g<0)
    w_truth^(j) = w_truth * prod_b rho_b(g_b) * (wt_flux_u/w_truth)
    (same for w_reco and the truth-denom weights), clipped per event for positivity
    x_j = OmniFold-reunfold(w^(j))   [compare_unified_throw._xsec_for_weights]

Reads the per-event bank produced for the superposition probe (bank_uthrow/): cv.npz
(MCgen/MCreco/measured/pass_*/w_*/td_*/edges/flux/...) + per-band absolute universe
weights sig_<band>_{t,r}_<idx>.npy, td_<band>_<idx>.npy, flux as 100 universes.

Two phases (throws array-parallelise; combine aggregates):
  # one array task -> a slab of throws
  python unified_throw_cov.py --throws 8 --throw-offset 0 --seed 1000 \
      --bank bank_uthrow --iters 5 --out uthrow_slab_0.npz
  # after all slabs land
  python unified_throw_cov.py --combine 'uthrow_slab_*.npz' --bank bank_uthrow \
      --iters 5 --out-root uq_4d/unified_throw_cov.root
"""
import argparse
import glob
import hashlib
import os
import subprocess
import sys
import tempfile
from pathlib import Path

import numpy as np

# OI-136 REPAIR, 2026-08-22, authorized by Joseph's ruling 18 (DECISION-20260822-joseph-b1-lift-and-clause-c.md)
# and required by REVIEW-CONTRACT-20260822-k0-execution-integrity.md B-1. THE IMPORT ROOT IS DERIVED
# FROM THIS FILE, never from the hardcoded cluster root that used to stand here. An absolute
# `insert(0, ...)` executes THAT tree's modules whichever checkout launched this entrypoint, and
# PYTHONPATH cannot outrank position 0 -- so deployment parity can report every pinned file CURRENT
# while the interpreter imports a different file entirely. That is OI-136's measured cause on run
# 57266000_0 (3 h 08 m of A100 against a tree 211 commits behind).
# NO ABSOLUTE FALLBACK, deliberately: a fallback is the hardcode wearing a flag, and it would restore
# the defect silently on the one tree where it matters. Same idiom and the same reason as the OI-136
# pilot repair at `uq_fps/corrected/test_fps_corrected_uq.py`, `tests/test_p4_repair.py:14` and
# `pet/combine_cstat_bkgsub_100rep.py:78`.
# THIS FILE IS A MODULE, NOT AN ENTRYPOINT, AND IT IS IN THE REPAIR SET FOR THAT REASON.
# `unified_throw_cov_5d.py` imports it AFTER its own rooted insert; leaving this one hardcoded
# would keep the transitive rooted-import defect open (Joseph, ruling 18). `parents[1]` is the
# repository root seen from `nd-unfolding/`, because the inserts cover both source trees.
_REPO = str(Path(__file__).resolve().parents[1])
for _p in (f"{_REPO}/2d-unfolding", f"{_REPO}/nd-unfolding"):
    if _p not in sys.path:
        sys.path.insert(0, _p)

# THE DATA ROOT IS A SEPARATE OBJECT AND KEEPS ITS ABSOLUTE VALUE (ruling 17's two-root design).
# `_REPO` above is the immutable clean execution tree; the products these defaults name are gigabytes
# of gitignored inputs that a clean checkout does not and must not contain, so repointing them at the
# derived root would make every default name a file that is not there. Nothing below is imported or
# executed -- these are argparse defaults and data paths only, and every launcher on the k=0 path
# passes them explicitly from `${MNV_DATA_ROOT}`.
_DATA_ROOT = "/pscratch/sd/j/josephrb/MINERvA-OmniFold"

import flux_universe
import seed_offset_policy
from compare_unified_throw import _xsec_for_weights
from uq_math import (interpolate_asymmetric_ratio, joint_throw_covariance,
                     mat_covariance)

# +-1sigma reweight knobs (idx 0 = -1sigma, idx 1 = +1sigma).
# Flux is handled separately as a 100-universe set.
KNOB_BANDS = ["2p2h", "CCQEPauliSupViaKF", "FrAbs_pi", "FrElas_N", "HighQ2",
              "LowQ2", "MaCCQE", "MaRES", "MFP_N", "MvRES", "Rvn2pi", "Rvp2pi"]
RHO_CLIP = (1e-2, 1e2)     # per-event ratio clip (positivity / tail guard)
EXPECTED_FLUX_UNIVERSES = 100


def _opt(bank, name):
    p = os.path.join(bank, name)
    return np.load(p).astype(np.float64) if os.path.exists(p) else None


def _load_bank(bank):
    """Return (d, bands, n_flux) WITHOUT loading any weight arrays into memory.
    d is the cv dict for _xsec_for_weights; bands = available knob names; n_flux =
    number of available flux universes. Weight arrays are loaded lazily (the full
    set is ~80 GB in float64 -- never hold them all)."""
    cv = np.load(os.path.join(bank, "cv.npz"))
    d = {k: cv[k] for k in cv.files}
    nedges = sum(1 for k in cv.files if k.startswith("edges_"))
    d["edges"] = [cv[f"edges_{i}"] for i in range(nedges)]
    missing_knob_files = []
    for b in KNOB_BANDS:
        for idx in (0, 1):
            for stem in (f"sig_{b}_t_{idx}", f"sig_{b}_r_{idx}", f"td_{b}_{idx}"):
                if not os.path.exists(os.path.join(bank, f"{stem}.npy")):
                    missing_knob_files.append(f"{stem}.npy")
    if missing_knob_files:
        raise RuntimeError(f"[FAIL] incomplete knob bank: missing {missing_knob_files}")
    bands = list(KNOB_BANDS)

    def flux_ids(prefix):
        out = set()
        for path in glob.glob(os.path.join(bank, f"{prefix}*.npy")):
            suffix = os.path.basename(path)[len(prefix):-4]
            if suffix.isdigit():
                out.add(int(suffix))
        return out

    flux_sets = [flux_ids(p) for p in ("sig_flux_t_", "sig_flux_r_", "td_flux_")]
    if not flux_sets[0] or not (flux_sets[0] == flux_sets[1] == flux_sets[2]):
        raise RuntimeError(f"[FAIL] incomplete/mismatched flux bank IDs: {flux_sets}")
    expected_flux = set(range(EXPECTED_FLUX_UNIVERSES))
    if flux_sets[0] != expected_flux:
        raise RuntimeError(f"[FAIL] flux bank must contain exactly "
                           f"{EXPECTED_FLUX_UNIVERSES} universes: "
                           f"missing={sorted(expected_flux-flux_sets[0])}, "
                           f"extra={sorted(flux_sets[0]-expected_flux)}")
    n_flux = len(expected_flux)
    print(f"[bank] {len(bands)} knob bands, {n_flux} flux universes, "
          f"{d['MCgen'].shape[0]} events, edges {[len(e)-1 for e in d['edges']]}")
    return d, bands, n_flux


#: The in-progress suffix `_atomic_savez` writes beside a slab, named so consumers can EXCLUDE it.
#:
#: ⚠ IT FALLS INSIDE THE CONSUMERS' OWN GLOBS, and that is a live hazard rather than a tidiness
#: point. `_atomic_savez` names its temp file `<product>.<random>.tmp.npz`, so
#: `block5d_knobs.npz.abc.tmp.npz` MATCHES `--block-slabs 'block5d_*.npz'` and
#: `uthrow5d_slab_0.npz.abc.tmp.npz` matches the throw glob. The `except` branch below unlinks it,
#: but a WALL-CLOCK KILL runs no handler -- and `sbatch_uthrow_run_5d_fast.sh:14` states that a
#: wall-kill "re-runs the whole task cleanly" on the strength of this function. It does for the
#: PRODUCT; the leftover temp is then a glob member the combine will try to `np.load`.
#: Exported as a constant so the exclusion is derived from the producer rather than retyped: a
#: second spelling of this suffix somewhere else could stop matching and nothing would say so.
IN_PROGRESS_SUFFIX = ".tmp.npz"


def _atomic_savez(path, **arrays):
    """Replace a slab only after the compressed NPZ has closed successfully."""
    path = os.path.abspath(os.fspath(path))
    os.makedirs(os.path.dirname(path), exist_ok=True)
    handle = tempfile.NamedTemporaryFile(
        prefix=os.path.basename(path) + ".", suffix=IN_PROGRESS_SUFFIX,
        dir=os.path.dirname(path), delete=False)
    tmp = handle.name
    handle.close()
    try:
        np.savez_compressed(tmp, **arrays)
        os.replace(tmp, path)
    except Exception:
        if os.path.exists(tmp):
            os.unlink(tmp)
        raise


# ------------------------------------------------------------------ CV SUPPORT, PERSISTED ----
#: The support predicate's own text, stamped beside the mask. A consumer comparing an observed
#: support against a declared one (`z_build_path.classify_support_change`) is comparing two boolean
#: arrays; without the PREDICATE that produced each, two masks of equal shape that disagree are
#: indistinguishable from one mask under two definitions. That is the distinction
#: `classify_support_change` is named for and it cannot make it from the arrays alone.
CV_SUPPORT_PREDICATE = "x_cv > 0"


def cv_support_report(x_cv):
    """Characterize the reported-bin support of a CV cross-section vector, AND its complement.

    ⚠ THIS DOES NOT CHANGE THE SUPPORT. `rep = x_cv > 0` is unchanged and still selects the
    reported bins; redefining it would change `nrep`, the covariance dimension and every
    downstream consumer, which is a criterion change and not what this function is.

    WHAT IT ADDS is that the complement becomes READABLE. Under a strictly-positive predicate a
    GENUINELY ZERO bin and a bin that was never in the binning are the same absence: both are
    simply not in `base`, at no index, under no name. Joseph's ruling -- *"a pinned-zero inflation
    bin is not a null operand"* -- names exactly that line, and the defect is not the threshold, it
    is that the excluded set was computed and then thrown away. So the mask, the counts, and the
    two disjoint reasons a bin can be out of support are all reported here, from ONE place.

    Zero and negative are split deliberately. A zero is a physically meaningful pinned bin; a
    NEGATIVE CV cross section is an arithmetic fault in the extraction. One count carrying both
    would have two meanings and no way to tell which -- the same reason
    `eavailW_covariance.check_projection_support` keeps declared exclusions off the defect ledger.

    Parameters
    ----------
    x_cv : array_like
        Raveled CV cross section over every bin of the binning, before any masking.

    Returns
    -------
    dict
        ``mask`` is a bool array index-aligned to ``x_cv``; ``n_total``, ``n_support``,
        ``n_zero`` and ``n_negative`` are ints; ``zero_indices`` and ``negative_indices`` are
        int arrays. ``n_support + n_zero + n_negative == n_total`` always holds.
    """
    x = np.asarray(x_cv, dtype=float).ravel(order="C")
    if not np.all(np.isfinite(x)):
        raise SystemExit(f"[FAIL] CV cross section has {int((~np.isfinite(x)).sum())} "
                         f"non-finite bin(s); the support mask would be meaningless")
    mask = x > 0
    zero = np.nonzero(x == 0.0)[0]
    negative = np.nonzero(x < 0.0)[0]
    return {"mask": mask, "n_total": int(x.size), "n_support": int(mask.sum()),
            "n_zero": int(zero.size), "n_negative": int(negative.size),
            "zero_indices": zero, "negative_indices": negative,
            "predicate": CV_SUPPORT_PREDICATE}


def check_slab_population(pattern, expected_names, label):
    """Exact FILE-IDENTITY validation of a slab glob: both directions, names not counts.

    ⚠ WHAT THIS COVERS AND WHAT IT DOES NOT, measured against this file's own guards rather than
    assumed. A SHORT arm is ALREADY refused: the 20 flux block tasks tile 0-99 exactly, so a
    missing task leaves `expected_flux_ids` short at `:462` and a missing knob task leaves the knob
    inventory short at `:453`; a missing throw slab leaves `--expected-throws` short at `:407`. I
    measured all three refusing. So "a short arm combines silently" is FALSE of this producer and
    is not the defect this adds.

    WHAT IS UNCOVERED, and it is the one I measured PASSING: a COMPLETE set of slabs from a
    DIFFERENT campaign. Every content check is satisfied by any inventory-complete population at the
    same seed, so a glob resolving into a foreign namespace combines silently and the covariance is
    built from another run's endpoints. The content is right; the POPULATION is not the one this run
    produced. Identities are the only thing that can tell those apart, which is Joseph's point --
    *"expected identities and coverage, not merely file counts"* -- and a count cannot: the foreign
    population I measured had the RIGHT count.

    BOTH DIRECTIONS, because a one-directional check waves the other through:
      * MISSING -- a declared file the glob did not find;
      * UNDECLARED -- a file the glob DID find that was never declared, which is the stale/extra
        case and the one a count of a complete-but-foreign set cannot see.

    Parameters
    ----------
    pattern : str
        The glob actually passed to `--combine` / `--block-slabs`.
    expected_names : sequence of str
        Exact expected BASENAMES. No globs, no ranges: a range expression here would be a second
        implementation of the arm's task layout, and the two could disagree.
    label : str
        Named in the refusal so a failure says which arm.

    Returns
    -------
    dict
        ``{"label", "n_expected", "n_found", "names"}`` on success.

    Raises
    ------
    SystemExit
        On any missing or undeclared member, with the offending names.
    """
    declared = [str(n).strip() for n in expected_names if str(n).strip()]
    if not declared:
        raise SystemExit(f"[FAIL] {label}: an EMPTY expected-file declaration is not a "
                         f"declaration. Every name would be undeclared and every absence "
                         f"invisible, so the check would pass on any population including none.")
    if len(set(declared)) != len(declared):
        dupes = sorted({n for n in declared if declared.count(n) > 1})
        raise SystemExit(f"[FAIL] {label}: the expected-file declaration repeats {dupes}; a "
                         f"declaration that names a file twice cannot be compared as a set")
    for name in declared:
        if os.path.basename(name) != name or any(c in name for c in "*?["):
            raise SystemExit(f"[FAIL] {label}: expected-file entry {name!r} is not a plain "
                             f"basename. A glob or a path here would make the declaration match "
                             f"whatever is present, which is the absence of a declaration.")
    # AN IN-PROGRESS TEMP IS REPORTED SEPARATELY, NOT AS AN UNDECLARED MEMBER. `_atomic_savez`'s
    # temp name falls INSIDE this glob (see `IN_PROGRESS_SUFFIX`), so a wall-killed task leaves one
    # behind and it would otherwise read as a stale foreign file. It is neither: it is this run's
    # own incomplete write, and conflating the two would give one refusal two meanings.
    matched = [os.path.basename(p) for p in glob.glob(pattern)]
    in_progress = sorted(n for n in matched if n.endswith(IN_PROGRESS_SUFFIX))
    if in_progress:
        raise SystemExit(
            f"[FAIL] {label}: {len(in_progress)} INCOMPLETE write(s) left in the glob: "
            f"{in_progress[:6]}{' ...' if len(in_progress) > 6 else ''}\n"
            f"  glob: {pattern}\n"
            f"  These are `_atomic_savez` temporaries, not stale foreign files -- the producer was "
            f"killed mid-write (a wall-clock kill runs no cleanup handler) and the temp name falls "
            f"inside this glob. Re-run the producing task; do not delete the declared products.")
    found = set(matched)
    want = set(declared)
    missing, undeclared = sorted(want - found), sorted(found - want)
    if missing or undeclared:
        raise SystemExit(
            f"[FAIL] {label}: the slab population is not the declared one.\n"
            f"  glob: {pattern}\n"
            f"  MISSING ({len(missing)}): {missing[:12]}{' ...' if len(missing) > 12 else ''}\n"
            f"  UNDECLARED ({len(undeclared)}): {undeclared[:12]}"
            f"{' ...' if len(undeclared) > 12 else ''}\n"
            f"  An UNDECLARED member is a stale or foreign file: this producer's content checks "
            f"are satisfied by ANY inventory-complete population at the matching seed, so a glob "
            f"resolving into another campaign's namespace passes all of them. The count can be "
            f"exactly right and the population still wrong.")
    return {"label": label, "n_expected": len(want), "n_found": len(found),
            "names": sorted(want)}


def _bank_cv_digest(bank):
    """SHA-256 of the bank's `cv.npz`, or ``UNAVAILABLE``. Same reason as `code_provenance`."""
    try:
        return hashlib.sha256(Path(bank, "cv.npz").read_bytes()).hexdigest()
    except OSError:
        return "UNAVAILABLE"


def code_provenance():
    """The executing tree's revision and this producer's own file digest.

    NOT A GATE, deliberately. Every field has an explicit ``UNAVAILABLE`` value rather than a
    fallback or an omission, because a MISSING key is indistinguishable from a key nobody could
    compute -- the `fixed_seed_null_checked` lesson at `:554`, one object over. Refusing on
    ``UNAVAILABLE`` belongs to the receipt gate (`z_precursor.check_receipt`), which is a
    different subject from stamping: a producer that refused to run because git was absent would
    make provenance a scheduler dependency.
    """
    unavailable = "UNAVAILABLE"
    try:
        revision = subprocess.run(["git", "-C", _REPO, "rev-parse", "HEAD"],
                                  stdout=subprocess.PIPE, stderr=subprocess.DEVNULL,
                                  check=True).stdout.decode().strip() or unavailable
    except (OSError, subprocess.CalledProcessError):
        revision = unavailable
    try:
        digest = hashlib.sha256(Path(__file__).resolve().read_bytes()).hexdigest()
    except OSError:
        digest = unavailable
    return {"code_revision": revision, "producer_file": os.path.basename(__file__),
            "producer_sha256": digest}


def _ratio(rho, label, invalid_policy="error"):
    """Validate a banked universe/CV ratio with an explicit invalid-value policy."""
    rho = np.asarray(rho, dtype=np.float64)
    bad = ~np.isfinite(rho) | (rho <= 0.0)
    if np.any(bad):
        msg = f"{label}: {int(bad.sum())}/{rho.size} ratios are non-finite or <=0"
        if invalid_policy == "error":
            raise ValueError(msg)
        print(f"[ratio][WARN] {msg}; explicitly replacing with neutral ratio 1", flush=True)
        rho = rho.copy()
        rho[bad] = 1.0
    clipped = (rho < RHO_CLIP[0]) | (rho > RHO_CLIP[1])
    if np.any(clipped):
        print(f"[ratio][WARN] {label}: clipping {int(clipped.sum())}/{rho.size} "
              f"ratios to {RHO_CLIP}", flush=True)
    return np.clip(rho, *RHO_CLIP)


def _knob_ratios(bank, bands, invalid_policy):
    """Load both asymmetric endpoints for every knob and event-weight view."""
    ratios = {}
    for b in bands:
        ratios[b] = {}
        for view, stem in (("t", "sig_{b}_t_{idx}.npy"),
                           ("r", "sig_{b}_r_{idx}.npy"),
                           ("td", "td_{b}_{idx}.npy")):
            minus = _ratio(_opt(bank, stem.format(b=b, idx=0)),
                           f"{b}:{view}:-1", invalid_policy).astype(np.float32)
            plus = _ratio(_opt(bank, stem.format(b=b, idx=1)),
                          f"{b}:{view}:+1", invalid_policy).astype(np.float32)
            ratios[b][view] = (plus, minus)
    return ratios


def _flux_universe(bank, u):
    """Lazy-load the three weight arrays for flux universe u."""
    return (_opt(bank, f"sig_flux_t_{u}.npy"),
            _opt(bank, f"sig_flux_r_{u}.npy"),
            _opt(bank, f"td_flux_{u}.npy"))


def _flux_normalized(slab):
    """True when a slab was produced with per-universe flux normalization (J28).

    Slabs written before the fix carry no stamp; combine refuses them rather than
    folding Phi_CV-normalized flux universes into a fresh adopted covariance.
    rescale_flux_universes.py corrects such a slab in place of a re-throw and
    stamps the result.
    """
    return "flux_normalized" in slab.files and int(slab["flux_normalized"]) == 1


def _flux_ratio_table(args, d, n_flux):
    """Phi_u/Phi_CV per pT bin for every flux universe -- fail-closed (J28).

    A Flux universe reweights the events AND changes the flux integral the xsec
    divides by; applying only the reweights and keeping Phi_CV is the Task #70
    bug. The uthrow banks already carry this table on their own pT grid
    (unified_throw.py --dump writes flux_univ_ratio.npy), so the correction needs
    no re-dump; --flux-universe-file is the fallback. There is no CV fallback.
    """
    if not n_flux:
        return None
    n_pt = len(d["flux"])
    try:
        table = flux_universe.load_banked_flux_ratio_table(args.bank, n_pt, n_flux)
        source = os.path.join(args.bank, flux_universe.BANKED_RATIO_NAME)
    except (RuntimeError, ValueError, OSError) as exc:
        print(f"[bank] no usable banked flux ratio table ({exc});\n"
              f"[bank] rebuilding from {args.flux_universe_file}", flush=True)
        import unfold_2d_omnifold_unbinned as u2d      # ROOT; fallback path only
        table = flux_universe.resolve_flux_ratio_table(
            n_pt=n_pt, n_flux=n_flux, universe_file=args.flux_universe_file,
            pt_edges=d["edges"][0], cv_flux_bins=d["flux"],
            ref_edges=np.asarray(u2d.PT_EDGES, float))
        source = args.flux_universe_file
    spread = float(np.abs(table - 1.0).max())
    print(f"[bank] flux ratio table {table.shape} from {source}: "
          f"max |Phi_u/Phi_CV - 1| = {spread:.4f}")
    return table


def _flux_for_universe(d, table, u):
    """The integrated flux a Flux universe must divide by: Phi_u = Phi_CV * r_u."""
    return np.asarray(d["flux"], float) * table[u]


# Read ONCE at import so every product of one process agrees, and so a mid-run env change cannot
# produce two differently-stamped slabs from the same job.
_OFF_DECLARED, _OFF_VALUE = seed_offset_policy.declared_offset()


def do_throws(args):
    d, bands, n_flux = _load_bank(args.bank)
    edges = d["edges"]
    w_truth, w_reco, td_cv = d["w_truth"], d["w_reco"], d["td_w"]
    ratios = _knob_ratios(args.bank, bands, args.invalid_ratio)
    flux_ratio = _flux_ratio_table(args, d, n_flux)

    xs = []
    metas = []
    for j in range(args.throws):
        gj = args.throw_offset + j
        # THE BIT-REPRODUCIBILITY INVARIANT, AND IT IS NOW CONDITIONAL -- stated here because
        # this is the one place it cannot rot. Seven committed sites cite this line as a
        # BEHAVIOUR claim ("seeds per GLOBAL throw index, so regeneration is bit-reproducible"),
        # four of them in append-only logs that cannot be annotated: VALIDATION_LEDGER.md:1013,
        # ND_OMNIFOLD_RUN_LOG.md:3428, AUTONOMOUS_LOG_20260805.md:407/500/564,
        # notify_uthrow_regen.sh:14, and validate_rescale_identity.py:18 which DEPENDS on it.
        #
        # Before the two-role split the claim was STRUCTURAL: it followed from the code with no
        # precondition a caller could fail to supply. It is now CONTINGENT, holding at
        # --draw-seed 1000, which is what every archived product was built with.
        #
        # WHAT MAKES THAT SAFE RATHER THAN A WEAKENING (lane D's formulation): the contingency
        # cannot be met by accident in either direction. There is no default to inherit, so a
        # reader replaying with a different draw seed has SAID so; and a reader replaying an
        # archived command line that still reads `--seed 1000` gets an argparse error, not a
        # wrong number. The failure is loud and the correct path is bit-identical.
        rng = np.random.default_rng(args.draw_seed + gj)
        g = {b: float(rng.standard_normal()) for b in bands}
        rt = np.ones_like(w_truth); rr = np.ones_like(w_reco); rtd = np.ones_like(td_cv)
        for b in bands:
            rt *= interpolate_asymmetric_ratio(g[b], *ratios[b]["t"])
            rr *= interpolate_asymmetric_ratio(g[b], *ratios[b]["r"])
            rtd *= interpolate_asymmetric_ratio(g[b], *ratios[b]["td"])
        wt_j = w_truth * rt; wr_j = w_reco * rr; wtd_j = td_cv * rtd
        if n_flux:
            u = int(rng.integers(n_flux))
            fwt, fwr, fwtd = _flux_universe(args.bank, u)
            wt_j *= _ratio(fwt, f"Flux:{u}:t", args.invalid_ratio)
            wr_j *= _ratio(fwr, f"Flux:{u}:r", args.invalid_ratio)
            wtd_j *= _ratio(fwtd, f"Flux:{u}:td", args.invalid_ratio)
            # ...and divide by THAT universe's flux integral, not the CV one (J28).
            flux_j = _flux_for_universe(d, flux_ratio, u)
        else:
            u = -1
            flux_j = None
        # Systematic throws all use the SAME estimator seed. ML variation belongs
        # exclusively in C_ML and must not leak into C_syst.
        x = _xsec_for_weights(d, edges, wt_j, wr_j, wtd_j, args.iters, args.estimator_seed,
                              flux=flux_j)
        xs.append(x.ravel(order="C"))
        metas.append((gj, u))
        print(f"[throw {gj}] flux_u={u} sum(x)={x.sum():.4e}", flush=True)
        # save incrementally so a killed job (e.g. interactive alloc expiry) keeps
        # every completed throw rather than losing the whole slab.
        _atomic_savez(args.out, xs=np.array(xs),
                      throws=np.array([m[0] for m in metas]),
                      flux_u=np.array([m[1] for m in metas]),
                      estimator_seed=np.int64(args.estimator_seed),
                      draw_seed=np.int64(args.draw_seed),
                      est_seed_offset_declared=np.int64(_OFF_DECLARED),
                      est_seed_offset=np.int64(_OFF_VALUE),
                      flux_normalized=np.int64(1),
                      bands=np.array(bands, dtype=object))
    print(f"[throws] wrote {args.out}: xs{np.array(xs).shape}")


def do_blockunits(args):
    """Producer for the block-sum: compute the xsec vector for each assigned
    block universe (both knob endpoints and/or flux index) and save them. Parallelises
    the otherwise-serial 112-unfold block-sum exactly like the throws. Combine
    aggregates these. --block-knobs all|csv ; --block-flux LO-HI (inclusive)."""
    d, bands, n_flux = _load_bank(args.bank)
    edges = d["edges"]
    w_truth, w_reco, td_cv = d["w_truth"], d["w_reco"], d["td_w"]
    flux_ratio = _flux_ratio_table(args, d, n_flux) if args.block_flux else None
    xs, labels, kinds = [], [], []

    knob_list = bands if args.block_knobs == "all" else [b for b in args.block_knobs.split(",") if b in bands]
    for b in knob_list:
        for idx, sign in ((0, "minus"), (1, "plus")):
            wt = w_truth * _ratio(_opt(args.bank, f"sig_{b}_t_{idx}.npy"),
                                  f"{b}:{sign}:t", args.invalid_ratio)
            wr = w_reco * _ratio(_opt(args.bank, f"sig_{b}_r_{idx}.npy"),
                                 f"{b}:{sign}:r", args.invalid_ratio)
            wtd = td_cv * _ratio(_opt(args.bank, f"td_{b}_{idx}.npy"),
                                 f"{b}:{sign}:td", args.invalid_ratio)
            # knob endpoints do not move the flux integral: CV flux is correct here
            x = _xsec_for_weights(d, edges, wt, wr, wtd, args.iters, args.estimator_seed).ravel(order="C")
            xs.append(x); labels.append(f"{b}:{idx}"); kinds.append("knob")
            print(f"[blockunit] knob {b} {sign} done", flush=True)
            _atomic_savez(args.out, xs=np.array(xs), labels=np.array(labels, dtype=object),
                          estimator_seed=np.int64(args.estimator_seed),
                          draw_seed=np.int64(args.draw_seed),
                          est_seed_offset_declared=np.int64(_OFF_DECLARED),
                          est_seed_offset=np.int64(_OFF_VALUE),
                          flux_normalized=np.int64(1),
                          kinds=np.array(kinds, dtype=object))
    if args.block_flux:
        lo, hi = (int(x) for x in args.block_flux.split("-"))
        for u in range(lo, min(hi, n_flux - 1) + 1):
            fwt, fwr, fwtd = _flux_universe(args.bank, u)
            x = _xsec_for_weights(
                d, edges,
                w_truth * _ratio(fwt, f"Flux:{u}:t", args.invalid_ratio),
                w_reco * _ratio(fwr, f"Flux:{u}:r", args.invalid_ratio),
                td_cv * _ratio(fwtd, f"Flux:{u}:td", args.invalid_ratio),
                args.iters, args.estimator_seed,
                flux=_flux_for_universe(d, flux_ratio, u)).ravel(order="C")
            xs.append(x); labels.append(f"flux{u}"); kinds.append("flux")
            print(f"[blockunit] flux {u} done", flush=True)
            _atomic_savez(args.out, xs=np.array(xs), labels=np.array(labels, dtype=object),
                          estimator_seed=np.int64(args.estimator_seed),
                          draw_seed=np.int64(args.draw_seed),
                          est_seed_offset_declared=np.int64(_OFF_DECLARED),
                          est_seed_offset=np.int64(_OFF_VALUE),
                          flux_normalized=np.int64(1),
                          kinds=np.array(kinds, dtype=object))
    print(f"[blockunit] wrote {args.out}: {len(xs)} units")


def do_combine(args):
    d, bands, n_flux = _load_bank(args.bank)
    edges = d["edges"]
    w_truth, w_reco, td_cv = d["w_truth"], d["w_reco"], d["td_w"]

    # CV xsec (reported-bin mask)
    x_cv = _xsec_for_weights(d, edges, w_truth, w_reco, td_cv, args.iters, args.estimator_seed).ravel(order="C")
    # THE SUPPORT AND ITS COMPLEMENT, FROM ONE PLACE. `rep` is still `x_cv > 0` -- the predicate is
    # unchanged, see `cv_support_report`. What changed is that the excluded set is now an object
    # that reaches the product instead of a local that dies at the end of this function.
    cv_support = cv_support_report(x_cv)
    rep = cv_support["mask"]
    base = x_cv[rep]
    nrep = cv_support["n_support"]
    print(f"[combine] reported bins = {nrep} of {cv_support['n_total']} "
          f"(predicate {cv_support['predicate']}; {cv_support['n_zero']} genuinely zero, "
          f"{cv_support['n_negative']} negative)")
    if cv_support["n_zero"]:
        print(f"[combine] genuinely-zero CV bins EXCLUDED from the support, by index: "
              f"{cv_support['zero_indices'].tolist()}", flush=True)
    # THE GENUINE CV EXECUTIONS, kept as objects. There are at most two and the second exists only
    # under `--null`; today the second is reduced to a scalar norm at `:516` and the first survives
    # only masked, as `base`. Both full vectors are persisted below.
    cv_executions = [x_cv]

    # POPULATION IDENTITY, BEFORE ANY CONTENT IS READ. Declared per arm and checked in both
    # directions; see `check_slab_population` for what the content checks below already cover and
    # for the one case they do not. Both declarations are OPTIONAL, and the flags written into the
    # product say whether each ran -- a required flag would make the two pre-existing `--combine`
    # launchers refuse themselves, and a guard that fires on every correct run is not a guard.
    # THE OPERAND IS CHECKED BEFORE IT IS USED. A declaration with no glob to compare it against
    # used to reach `glob.glob(None)` and die as a TypeError -- a real refusal reported as a crash,
    # which is the wrong diagnosis of a right refusal.
    #
    # READ WITH `getattr`, AND THE DEFAULT IS THE REFUSING DIRECTION. `do_combine` is called
    # programmatically from five places in `tests/test_uq_remediation.py` with a hand-built
    # namespace carrying only the attributes it needs -- it does not carry `invalid_ratio` or
    # `flux_universe_file` either -- so a newly REQUIRED attribute breaks every such caller. This
    # is a fallback, and the reason it is safe is the direction it falls in: absent means UNDECLARED,
    # which writes `*_population_declared = 0` into the product, and `z_precursor.check_receipt`
    # REFUSES 0. A caller that omits the flag cannot silently obtain a validated product.
    expected_throw_files = getattr(args, "expected_throw_files", None)
    expected_block_files = getattr(args, "expected_block_files", None)
    if expected_block_files and not args.block_slabs:
        raise SystemExit("[FAIL] --expected-block-files declares a block population but "
                         "--block-slabs names no glob to compare it against")
    if expected_throw_files and not args.combine:
        raise SystemExit("[FAIL] --expected-throw-files declares a throw population but "
                         "--combine names no glob to compare it against")
    throw_pop = (check_slab_population(args.combine, expected_throw_files.split(","),
                                       "throw slab population")
                 if expected_throw_files else None)
    block_pop = (check_slab_population(args.block_slabs, expected_block_files.split(","),
                                       "block slab population")
                 if expected_block_files else None)
    for pop in (throw_pop, block_pop):
        if pop:
            print(f"[population] {pop['label']}: {pop['n_expected']} declared file(s), "
                  f"exact identity match", flush=True)

    # unified covariance over all throws
    slabs = sorted(glob.glob(args.combine))
    if not slabs:
        raise SystemExit(f"no slabs match {args.combine}")
    slab_rows = []
    throw_ids = []
    slab_seeds = set()
    slab_draw_seeds = set()
    unnormalized = []
    for s in slabs:
        z = np.load(s, allow_pickle=True)
        if "estimator_seed" in z.files:
            slab_seeds.add(int(z["estimator_seed"]))
        if "draw_seed" in z.files:
            slab_draw_seeds.add(int(z["draw_seed"]))
        if not _flux_normalized(z):
            unnormalized.append(s)
        xx = np.asarray(z["xs"], dtype=float)
        ids = np.asarray(z["throws"], dtype=int)
        if xx.ndim != 2 or xx.shape[0] != ids.size or xx.shape[1] != x_cv.size:
            raise SystemExit(f"[FAIL] malformed throw slab {s}: xs={xx.shape}, ids={ids.shape}")
        if not np.all(np.isfinite(xx)):
            raise SystemExit(f"[FAIL] non-finite throw output in {s}")
        slab_rows.append(xx)
        throw_ids.extend(ids.tolist())
    if len(throw_ids) != len(set(throw_ids)):
        raise SystemExit("[FAIL] duplicate throw ids across slabs")
    if not args.expected_throws:
        raise SystemExit("[FAIL] --expected-throws LO-HI is required for combine")
    throw_lo, throw_hi = (int(v) for v in args.expected_throws.split("-", 1))
    expected_throw_ids = set(range(throw_lo, throw_hi + 1))
    got_throw_ids = set(throw_ids)
    if got_throw_ids != expected_throw_ids:
        raise SystemExit(f"[FAIL] throw id mismatch: "
                         f"missing={sorted(expected_throw_ids-got_throw_ids)} "
                         f"extra={sorted(got_throw_ids-expected_throw_ids)}")
    X = np.concatenate(slab_rows, axis=0)[:, rep]
    T = X.shape[0]
    C_uni, mean_shift = joint_throw_covariance(X, base)
    print(f"[combine] {T} throws from {len(slabs)} slabs")
    print(f"[combine] joint-throw mean shift: norm={np.linalg.norm(mean_shift):.4e}, "
          f"max|shift|={np.max(np.abs(mean_shift)):.4e}")

    # block-sum covariance from precomputed block-unit slabs (knobs summed as
    # outer(delta); flux averaged then added). Falls back to inline if no slabs.
    C_block = np.zeros((nrep, nrep))
    bslabs = sorted(glob.glob(args.block_slabs)) if args.block_slabs else []
    if not bslabs:
        raise SystemExit(f"no block-unit slabs match {args.block_slabs}; run --blockunits first")
    flux_x = {}
    knob_x = {}
    # EXPLICIT PER-BAND DONOR BINDING -- WHICH FILE SUPPLIED EACH BAND, RECORDED.
    #
    # ⚠ THIS IS PROVENANCE, NOT A DONOR DECISION, AND THE DISTINCTION IS THE WHOLE POINT. Nothing
    # here chooses or changes which file supplies a band: the glob and the labels inside the slabs
    # decide that exactly as before, and this only WRITES DOWN what they decided. `z_assembly.py`
    # carries no donor binding at all and `z_build_path.py` binds only the C_stat/C_ML block
    # source, so today the answer to "which file supplied MaCCQE's endpoints" is not recoverable
    # from any product -- it is a property of whatever the glob happened to match at run time.
    band_donor = {}
    for s in bslabs:
        z = np.load(s, allow_pickle=True)
        if "estimator_seed" in z.files:
            slab_seeds.add(int(z["estimator_seed"]))
        if "draw_seed" in z.files:
            slab_draw_seeds.add(int(z["draw_seed"]))
        if not _flux_normalized(z):
            unnormalized.append(s)
        xx = np.asarray(z["xs"], dtype=float)
        if xx.ndim != 2 or xx.shape[1] != x_cv.size or not np.all(np.isfinite(xx)):
            raise SystemExit(f"[FAIL] malformed/non-finite block slab {s}: {xx.shape}")
        for x, label, kind in zip(xx, z["labels"], z["kinds"]):
            if str(kind) == "knob":
                band, idx = str(label).rsplit(":", 1)
                if idx not in ("0", "1") or idx in knob_x.setdefault(band, {}):
                    raise SystemExit(f"[FAIL] duplicate/malformed knob endpoint {label}")
                knob_x[band][idx] = x[rep]
                # Keyed per ENDPOINT, not per band: the two endpoints of one band could come from
                # different files and a band-level record would silently name only one of them.
                band_donor[f"{band}:{idx}"] = os.path.basename(s)
            elif str(kind) == "flux":
                text = str(label)
                if not text.startswith("flux") or not text[4:].isdigit():
                    raise SystemExit(f"[FAIL] malformed flux block label {label}")
                flux_id = int(text[4:])
                if flux_id in flux_x:
                    raise SystemExit(f"[FAIL] duplicate flux block universe {flux_id}")
                flux_x[flux_id] = x[rep]
                band_donor[f"flux{flux_id}"] = os.path.basename(s)
            else:
                raise SystemExit(f"[FAIL] unknown block kind {kind}")
    if set(knob_x) != set(bands):
        raise SystemExit(f"[FAIL] knob block inventory mismatch: "
                         f"missing={sorted(set(bands)-set(knob_x))} "
                         f"extra={sorted(set(knob_x)-set(bands))}")
    for band in sorted(knob_x):
        if set(knob_x[band]) != {"0", "1"}:
            raise SystemExit(f"[FAIL] {band} block is missing a +/- endpoint: {sorted(knob_x[band])}")
        C_block += mat_covariance(np.stack([knob_x[band]["0"], knob_x[band]["1"]]))
    expected_flux_ids = set(range(n_flux))
    if set(flux_x) != expected_flux_ids:
        raise SystemExit(f"[FAIL] flux block inventory mismatch: "
                         f"missing={sorted(expected_flux_ids-set(flux_x))} "
                         f"extra={sorted(set(flux_x)-expected_flux_ids)}")
    if flux_x:
        C_flux = mat_covariance(np.asarray([flux_x[u] for u in sorted(flux_x)]))
        C_block += C_flux
        print(f"[block] {len(knob_x)} +/- knobs + flux ({len(flux_x)} univ, "
              f"sqrt-tr={np.sqrt(np.trace(C_flux)):.3e}); MAT mean-centered 1/N")
    else:
        print(f"[block] {len(knob_x)} +/- knobs (no flux units); MAT mean-centered 1/N")

    # F2 guard: every throw/block slab must have been produced at the same
    # estimator seed as this combine (--seed), else C_uni/C_block would mix
    # estimator jitter across slabs. Seed is stamped by do_throws/do_blockunits.
    if slab_seeds and slab_seeds != {int(args.estimator_seed)}:
        raise SystemExit(f"[FAIL] slabs carry estimator seed(s) {sorted(slab_seeds)} != "
                         f"--estimator-seed {args.estimator_seed}; refusing mixed-seed combine")
    # DRAW-seed coherence, new with the two-role split. All slabs of one throw ensemble are
    # drawn from `--draw-seed + global_throw_index`, so two draw seeds in one combine means two
    # different ensembles wearing one set of throw ids -- distinct ids do NOT make them coherent.
    if slab_draw_seeds and slab_draw_seeds != {int(args.draw_seed)}:
        raise SystemExit(f"[FAIL] slabs carry draw seed(s) {sorted(slab_draw_seeds)} != "
                         f"--draw-seed {args.draw_seed}; refusing incoherent-ensemble combine")
    # J28 guard: a slab whose flux universes divided by the CV integral must not
    # be folded into a fresh covariance. Correct it with rescale_flux_universes.py
    # (exact, no re-unfold) or re-throw with the current code.
    if unnormalized:
        raise SystemExit(
            f"[FAIL] {len(unnormalized)} slab(s) carry no per-universe flux "
            f"normalization stamp, e.g. {unnormalized[0]}. They were produced "
            "before the J28 fix, so their Flux universes divided by the CV flux "
            "integral. Run rescale_flux_universes.py over them (exact post-hoc "
            "correction, no re-unfold) or regenerate the throws/blocks.")
    if not slab_seeds:
        raise SystemExit(
            "[FAIL] slabs carry no `estimator_seed` stamp; refusing combine. Slabs written "
            "BEFORE the two-role seed split carry a single ambiguous `seed` key instead, and it "
            "is not readable as an estimator seed because the same integer also drove the throw "
            "draw. MIGRATION: regenerate the throws/blocks with the current code, which stamps "
            "`estimator_seed` and `draw_seed` separately. There is deliberately no fallback that "
            "reads `seed` as the estimator seed -- doing so would let a pre-split slab combine "
            "beside a post-split one whose draw seed differs, which is a silent mixed-estimator "
            "covariance.")

    st_uni = float(np.sqrt(np.trace(C_uni)))
    st_block = float(np.sqrt(np.trace(C_block)))
    # Fixed-seed null: this must be exactly zero (within floating tolerance).
    # No scalar trace correction is applied: the stored covariance itself is the
    # mean-centered, fixed-estimator systematic covariance. ML lives only in C_ML.
    null_norm = None
    if args.null:
        x_cv2_full = _xsec_for_weights(d, edges, w_truth, w_reco, td_cv, args.iters,
                                       args.estimator_seed).ravel(order="C")
        # THE SECOND GENUINE CV EXECUTION IS AN OPERAND, NOT A SCALAR. Before this line it was
        # masked and differenced in one expression, so the only trace it ever ran was `null_norm` --
        # and a norm cannot say WHICH bin moved, nor can it be re-checked under a different support.
        cv_executions.append(x_cv2_full)
        x_cv2 = x_cv2_full[rep]
        null_norm = float(np.linalg.norm(x_cv2 - base))
        tol = 1e-12 * max(float(np.linalg.norm(base)), 1.0)
        print(f"\n[null] fixed-seed ||CV2-CV|| = {null_norm:.3e} (tol={tol:.3e})")
        if null_norm > tol:
            raise SystemExit("[FAIL] CV re-unfold is non-deterministic at the fixed estimator "
                             "seed; the throws cannot be cleanly separated from C_ML "
                             "(this checks CV determinism only; per-slab seed provenance is "
                             "enforced separately below)")

    # cross term = unified - block (the nonlinear piece block-sum drops)
    C_cross = C_uni - C_block
    st_cross = float(np.sqrt(abs(np.trace(C_cross))))
    du = np.sqrt(np.clip(np.diag(C_uni), 0, None))
    db = np.sqrt(np.clip(np.diag(C_block), 0, None))
    med_ratio = float(np.median(du[db > 0] / db[db > 0]))
    print("\n===== Unified-throw vs block-sum =====")
    print(f"  sqrt-trace  unified={st_uni:.4e}  block={st_block:.4e}  "
          f"ratio={st_uni/st_block:.3f}")
    print(f"  sqrt-trace cross-term (unified-block) = {st_cross:.4e}  "
          f"({100*st_cross/st_block:.1f}% of block)")
    print(f"  per-bin sigma ratio unified/block: median={med_ratio:.3f}")
    print("  (throws and block endpoints share one estimator seed; the joint covariance is "
          "mean-centered and its mean shift is reported separately. ratio>>1 => the unfolding combines bands NONLINEARLY and "
          "the block-sum underestimates; ratio~1 => block-sum is a good approximation.)")

    if args.out_root:
        import ROOT
        os.makedirs(os.path.dirname(args.out_root) or ".", exist_ok=True)
        fo = ROOT.TFile.Open(args.out_root, "RECREATE")
        for name, M in [("C_unified", C_uni), ("C_blocksum", C_block), ("C_cross", C_cross)]:
            h = ROOT.TH2D(name, name, nrep, 0, nrep, nrep, 0, nrep)
            for i in range(nrep):
                for k in range(nrep):
                    h.SetBinContent(i + 1, k + 1, float(M[i, k]))
            h.Write()
        ROOT.TParameter("double")("sqrt_tr_unified", st_uni).Write()
        ROOT.TParameter("double")("sqrt_tr_block", st_block).Write()
        ROOT.TParameter("double")("joint_mean_shift_norm", float(np.linalg.norm(mean_shift))).Write()
        # NULL-AS-ABSENT, closed 2026-08-11 (quarantine cause 4). `fixed_seed_null_norm` is still
        # written only when the check ran -- a number nobody measured must not be invented -- but
        # `fixed_seed_null_checked` is now written UNCONDITIONALLY beside it. Without that flag, a
        # product built without `--null` carries no null key at all, and a downstream criterion phrased
        # as "the null norm is not large" PASSES ON IT VACUOUSLY: absence is indistinguishable from
        # zero. The flag makes "nobody checked" a readable state rather than an inference from a
        # missing key, so a consumer can fail closed on `checked == 0`.
        ROOT.TParameter("int")("fixed_seed_null_checked", 1 if null_norm is not None else 0).Write()
        if null_norm is not None:
            ROOT.TParameter("double")("fixed_seed_null_norm", null_norm).Write()
        ROOT.TParameter("int")("n_throws", T).Write()
        # ITEM 4. Before the two-role split this writer stamped NO seed at all, so a re-seeded
        # covariance was indistinguishable from the original in its own product (BEN-246): the
        # seed census could not reach the artifact it graded. Both roles are written, separately,
        # because "the seed" is not a well-formed field on this product any more.
        ROOT.TParameter("int")("estimator_seed", int(args.estimator_seed)).Write()
        ROOT.TParameter("int")("draw_seed", int(args.draw_seed)).Write()
        # OFFSET PROVENANCE (lane D, 2026-08-18). The seed alone cannot say whether this product came from a
        # HOOKED launcher: an unhooked leg stamps its BASELINE, indistinguishable from a deliberate k=0
        # anchor member. Two keys, not a sentinel -- declared=0 means nothing can be concluded.
        ROOT.TParameter("int")("est_seed_offset_declared", int(_OFF_DECLARED)).Write()
        ROOT.TParameter("int")("est_seed_offset", int(_OFF_VALUE)).Write()
        hs = ROOT.TH1D("hJointMeanShift", "joint throw mean minus CV", nrep, 0, nrep)
        for i, value in enumerate(mean_shift):
            hs.SetBinContent(i + 1, float(value))
        hs.Write()
        # ---- THE SUPPORT MASK AND THE GENUINE CV EXECUTIONS, IN THE ARTIFACT ------------------
        # `BEN-450`'s repaired shape, transferred from `eavailW_covariance.write_ew_outputs:116-124`
        # WITH its condition rather than only its form: the COUNTS are written UNCONDITIONALLY
        # INCLUDING ZERO, the SET is written as an INDEX-ALIGNED MASK, and `n_cv_executions` is a
        # flag with TWO REACHABLE VALUES (1 without `--null`, 2 with it) rather than a literal 1 on
        # the only path -- which is the vacuous form lane D made us delete from that same writer.
        #
        # ⚠ `hCvSupportMask` IS OVER `n_total` BINS, NOT `nrep`. Every other histogram in this file
        # is `nrep x nrep`, i.e. indexed in the SUPPORT. A mask indexed in the support would be
        # all-ones by construction -- it would be the vacuous flag again, in array form. The mask's
        # whole content is the bins the support does NOT contain, so it must be indexed in the
        # BINNING. Bin i is 1 iff bin i of the binning is in the support.
        n_total = int(cv_support["n_total"])
        ROOT.TParameter("int")("n_cv_bins_total", n_total).Write()
        ROOT.TParameter("int")("n_cv_support", int(cv_support["n_support"])).Write()
        ROOT.TParameter("int")("n_cv_genuine_zero", int(cv_support["n_zero"])).Write()
        ROOT.TParameter("int")("n_cv_negative", int(cv_support["n_negative"])).Write()
        ROOT.TNamed("cv_support_predicate", cv_support["predicate"]).Write()
        hmask = ROOT.TH1I("hCvSupportMask",
                          "1 = CV bin is in the reported support (" + cv_support["predicate"] + ")",
                          n_total, 0, n_total)
        for i in np.nonzero(cv_support["mask"])[0]:
            hmask.SetBinContent(int(i) + 1, 1)
        hmask.Write()
        # The EXECUTIONS themselves, unmasked. `n_cv_executions` says how many of `hCvExecution*`
        # exist, so a consumer reads a count rather than probing for keys.
        ROOT.TParameter("int")("n_cv_executions", len(cv_executions)).Write()
        for k, vector in enumerate(cv_executions):
            he = ROOT.TH1D(f"hCvExecution{k}",
                           f"genuine CV execution {k} over all {n_total} bins, unmasked",
                           n_total, 0, n_total)
            for i, value in enumerate(np.asarray(vector, float).ravel(order="C")):
                he.SetBinContent(i + 1, float(value))
            he.Write()
        # RUN, BANK AND CODE PROVENANCE beside the operand. The seed provenance at `:569-575` above
        # already says WHICH seeds; these say which BANK and which CODE produced the mask, which is
        # what makes the mask re-derivable rather than merely present.
        prov = code_provenance()
        ROOT.TNamed("cv_code_revision", prov["code_revision"]).Write()
        ROOT.TNamed("cv_producer_file", prov["producer_file"]).Write()
        ROOT.TNamed("cv_producer_sha256", prov["producer_sha256"]).Write()
        ROOT.TNamed("cv_bank_path", os.path.abspath(args.bank)).Write()
        ROOT.TNamed("cv_bank_cv_sha256", _bank_cv_digest(args.bank)).Write()
        # POPULATION-VALIDATION FLAGS. Two reachable values each, because both declarations are
        # optional -- same condition as `fixed_seed_null_checked` at `:561` and NOT the vacuous
        # literal-1 form. 0 means the glob's file identities were never declared, so this product
        # cannot say the population was the one its own run produced. `z_precursor.check_receipt`
        # refuses 0 for the precursor; a 4D combine may legitimately carry 0.
        ROOT.TParameter("int")("throw_population_declared", 1 if throw_pop else 0).Write()
        ROOT.TParameter("int")("block_population_declared", 1 if block_pop else 0).Write()
        ROOT.TParameter("int")("n_throw_files_declared",
                               int(throw_pop["n_expected"]) if throw_pop else 0).Write()
        ROOT.TParameter("int")("n_block_files_declared",
                               int(block_pop["n_expected"]) if block_pop else 0).Write()
        # PER-BAND DONOR BINDING, in the artifact. One `TNamed` per endpoint rather than one
        # serialized blob: a blob needs a parser, and a consumer asking "which file supplied
        # MaCCQE:1" should be able to read one key. The COUNT is written beside them so a consumer
        # can tell a truncated set from a complete one -- the same reason the support count is
        # written beside the support mask.
        ROOT.TParameter("int")("n_band_donors", len(band_donor)).Write()
        for endpoint in sorted(band_donor):
            ROOT.TNamed(f"band_donor_{endpoint.replace(':', '_')}",
                        band_donor[endpoint]).Write()
        fo.Close()
        print(f"[combine] wrote {args.out_root}")
    return {
        "C_unified": C_uni,
        "C_blocksum": C_block,
        "C_cross": C_cross,
        "mean_shift": mean_shift,
        "x_cv_reported": base,
        "throw_ids": np.asarray(throw_ids, dtype=int),
        "fixed_seed_null_norm": null_norm,
        # Same reason as the ROOT stamp above: a consumer of this dict must be able to distinguish
        # "checked and zero" from "not checked", and `None` alone invites `or 0.0`.
        "fixed_seed_null_checked": null_norm is not None,
        # Same reason as the ROOT stamps: an in-process consumer must be able to tell WHICH
        # estimator seed produced this covariance without re-reading the slabs.
        "estimator_seed": int(args.estimator_seed),
        "draw_seed": int(args.draw_seed),
        "est_seed_offset_declared": int(_OFF_DECLARED),
        "est_seed_offset": int(_OFF_VALUE),
        # THE SAME OPERAND THE ROOT FILE CARRIES. An in-process consumer -- and every local
        # integration test -- must read the mask and the executions from the producer rather than
        # rebuild them, or the test's fixture would be derived from the rule it is checking.
        # `cv_support_mask` is index-aligned to the BINNING, not to the support; see the ROOT block.
        "cv_support_mask": cv_support["mask"],
        "cv_support_predicate": cv_support["predicate"],
        "n_cv_bins_total": int(cv_support["n_total"]),
        "n_cv_support": int(cv_support["n_support"]),
        "n_cv_genuine_zero": int(cv_support["n_zero"]),
        "n_cv_negative": int(cv_support["n_negative"]),
        "cv_genuine_zero_indices": cv_support["zero_indices"],
        "cv_negative_indices": cv_support["negative_indices"],
        "cv_executions": [np.asarray(v, float) for v in cv_executions],
        "n_cv_executions": len(cv_executions),
        "bank_path": os.path.abspath(args.bank),
        "bank_cv_sha256": _bank_cv_digest(args.bank),
        "throw_population_declared": bool(throw_pop),
        "block_population_declared": bool(block_pop),
        # PROVENANCE, NOT A DECISION: endpoint label -> the basename that supplied it. Nothing in
        # this function chooses a donor; this records the choice the glob and the labels made.
        "band_donor": dict(band_donor),
        "n_band_donors": len(band_donor),
        "throw_population": throw_pop,
        "block_population": block_pop,
        **code_provenance(),
    }


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--bank", default="bank_uthrow")
    ap.add_argument("--flux-universe-file",
                    default=f"{_DATA_ROOT}/2d-unfolding/baseline_flux/"
                            "flux_integral_universes_MEFHC.root",
                    help="ROOT (hFluxCV/hFluxUniv) per-PPFX flux integrals, used to "
                         "divide each Flux universe by its own Phi_u. Only consulted "
                         "when the bank carries no flux_univ_ratio.npy.")
    ap.add_argument("--throws", type=int, default=0, help="number of throws this task")
    ap.add_argument("--throw-offset", type=int, default=0)
    # THE TWO-ROLE SPLIT (gate 1). `--seed` is GONE, not aliased: a single flag setting both
    # roles is the dual-role field under a new name, which is the defect this change exists to
    # remove. Both replacements are REQUIRED with NO default -- a default on either one
    # re-creates a population of call sites that silently inherit it, and four of those were
    # `--combine` launchers where the estimator seed is compared against archived slab stamps.
    #
    # DAY-ONE IDENTITY: pass `--draw-seed 1000 --estimator-seed 1000` to reproduce every
    # pre-split product bit-for-bit. Before the split a single `--seed 1000` drove both roles,
    # so 1000/1000 IS the archive's configuration -- see nd-unfolding/unified_throw_cov.py
    # history and docs/orchestration/SCOPE-20260818-gate1-seed-separation-two-keys.md.
    #
    # INVARIANT, load-bearing and cited from seven places as a BEHAVIOUR claim: the throw draw
    # is `--draw-seed + <global throw index>`, so regeneration is bit-reproducible per throw.
    # Setting `--draw-seed` to anything other than 1000 VOIDS the regenerability of every
    # archived slab and voids validate_rescale_identity.py's premise, which relies on a given
    # global throw index reproducing the same knob draws and flux universe.
    ap.add_argument("--draw-seed", type=int, required=True,
                    help="seed for the SYSTEMATIC THROW DRAW (knob gaussians + flux universe "
                         "choice); the realization for global throw j is --draw-seed + j. "
                         "Pass 1000 to reproduce archived products.")
    ap.add_argument("--estimator-seed", type=int, required=True,
                    help="seed for the UNFOLDING ESTIMATOR, held fixed across all throws, "
                         "block units and the CV so that ML variation stays in C_ML and does "
                         "not leak into C_syst. Pass 1000 to reproduce archived products.")
    ap.add_argument("--iters", type=int, default=5)
    ap.add_argument("--out", default="uthrow_slab.npz")
    ap.add_argument("--combine", default=None, help="glob of throw slab npzs to aggregate")
    ap.add_argument("--block-slabs", default=None, help="glob of block-unit slabs (combine)")
    ap.add_argument("--expected-throws", default=None,
                    help="required exact throw-ID range LO-HI for combine")
    # FILE IDENTITIES, a different object from the ID range above. `--expected-throws` is a claim
    # about the throw ids INSIDE the slabs; these are claims about WHICH FILES the glob resolved to.
    # An inventory-complete population from another campaign satisfies the first and fails these.
    ap.add_argument("--expected-throw-files", default=None,
                    help="(combine) comma-separated exact BASENAMES the --combine glob must "
                         "resolve to. Both directions: a missing member and an undeclared "
                         "(stale/foreign) member each refuse. No globs or ranges accepted.")
    ap.add_argument("--expected-block-files", default=None,
                    help="(combine) comma-separated exact BASENAMES the --block-slabs glob must "
                         "resolve to. Same both-direction check as --expected-throw-files.")
    ap.add_argument("--blockunits", action="store_true", help="producer for block-sum units")
    ap.add_argument("--block-knobs", default="all", help="all|csv of knob bands")
    ap.add_argument("--block-flux", default=None, help="flux index range LO-HI (inclusive)")
    ap.add_argument("--null", action="store_true",
                    help="(combine) repeat the CV at the identical seed and require a null result")
    ap.add_argument("--invalid-ratio", choices=("error", "neutral"), default="error",
                    help="policy for zero/non-finite bank ratios; default fails loudly")
    ap.add_argument("--out-root", default=None)
    args = ap.parse_args()
    if args.combine:
        do_combine(args)
    elif args.blockunits:
        do_blockunits(args)
    elif args.throws > 0:
        do_throws(args)
    else:
        ap.error("pass --throws N, --blockunits, or --combine GLOB")


if __name__ == "__main__":
    main()

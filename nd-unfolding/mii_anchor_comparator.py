#!/usr/bin/env python3
"""B2: the bit-exact anchor comparator. Applies `mii_root_payload_classes` to two real ROOT files.

Stage 1's gate: does the `k=0` member reproduce the archive? The classification table says WHAT to
compare and in which class; this says HOW, and adds the half the table can only demand --
RECOMPUTATION of every derived scalar from the ingredients in its own file (BEN-077).

=====================================================================================================
THE FINDING THAT CAME OUT OF WRITING THIS, AND IT CONTRADICTS A SETTLED RULING IN EXACTLY ONE PLACE.

C classified seven scalars as PAYLOAD WITH MANDATORY RECOMPUTATION. **Only three of them can be
recomputed from the file that carries them.** Derived from the writers, not assumed:

    sqrt_tr_unified        <- trace(C_unified)                     IN FILE      recomputable
    sqrt_tr_block          <- trace(C_blocksum)                    IN FILE      recomputable
    joint_mean_shift_norm  <- norm(hJointMeanShift)                IN FILE      recomputable
    sqrt_tr_new            <- trace(hCov_combined5d_total_uthrow)  IN FILE      recomputable
    upstream_*             <- copies of the throw root's scalars   CROSS FILE   needs the throw root
    fixed_seed_null_norm   <- norm(x_cv2 - base)                   NEITHER      ingredients unwritten
    globalCompleteness     <- of_in.sum()/denom_nd.sum()           NEITHER      ingredients unwritten
    sqrt_tr_old            <- trace(hCov_combined5d_total)         NEITHER      **see below**

`sqrt_tr_old` IS THE PREDECLARED BAR'S OPERAND (4.357790406860002e-38), and its sole ingredient is
`hCov_combined5d_total` in `uq_5d/universe_stage2_5d_bkgaware/uq_universe_5d_covariance_combined_bkgaware.root`
-- `adopt_unified_5d.py:124-127` reading `--combined`, whose value is set at
`sbatch_adopt_stamped_footing.sh:33`. **THAT IS THE 41.44 GB INTERMEDIATE C RULED NEED NOT BE
RETAINED.** So after deletion the scalar survives in a retained 892 MB root and its ingredient does
not, and BEN-077's rule can never again be satisfied for it from retained bytes.

C's argument was that *"the bar's operands live downstream of it in the 892 MB adopted roots"*. That is
TRUE OF `sqrt_tr_new` and FALSE OF `sqrt_tr_old` -- the trace established that the operands are
downstream without distinguishing the two operands, and only one of them is.

**THE REMEDY IS 0.527 MB AND THE HELPER ALREADY EXISTS.** `trace(C) == sum(diag(C))`, so shipping the
DIAGONAL of the old combined matrix as a TH1D makes the bar's operand recomputable from retained bytes
forever. `adopt_unified_5d.py:53`'s `_diag()` already reads a square TH2D's diagonal without
materializing the matrix, and this composes with R4's `vb`/`vu` -- three per-bin arrays, 1.58 MB
against a 4.46 GB retained member. I am NOT making that change here: it alters a receipt-bound
writer's output and the retention ruling is C's. Flagged, costed, and left.
=====================================================================================================

ROOT IS ABSENT ON THE MACHINE THIS WAS WRITTEN ON, so the reader is injected: `read_keys` is a
callable, defaulting to a real PyROOT implementation that has never executed here. Everything the
comparator DECIDES is exercised against stubs; nothing about PyROOT's behaviour is claimed. That split
is the same one the enumeration document declares, and it is deliberate rather than a limitation I
found afterwards.
"""
import argparse
import hashlib
import sys

import numpy as np

import mii_root_payload_classes as classes

IN_FILE, CROSS_FILE, NOT_RECOMPUTABLE = "IN_FILE", "CROSS_FILE", "NOT_RECOMPUTABLE"

#: WHY a key is not recomputable, and C required this distinction rather than a bare `no`:
#:   WRITER_GAP  the ingredients COULD be written and are not. FIXABLE LATER.
#:   IMPOSSIBLE  the quantity cannot be reconstructed from any plausible in-file content.
#: Recording which kind it is DETERMINES WHETHER ANYONE CAN EVER CLOSE IT. A bare "not recomputable"
#: reads as a law of nature and freezes a writer gap forever.
WRITER_GAP, IMPOSSIBLE = "WRITER_GAP", "MATHEMATICALLY_IMPOSSIBLE"

#: How each recompute-required scalar can be checked, from what, and -- when it cannot -- WHY NOT and
#: OF WHICH KIND. Derived from the writers at the line numbers in the module docstring; a claim about
#: code, so a test re-reads the code.
#:
#: C RULED THERE IS NO FOURTH CLASS, and the reason is structural and worth keeping: each of the three
#: classes names a COMPARISON RULE -- bit-exact, equal, superset -- and "not recomputable" is not one,
#: because these keys still compare BIT-EXACT. What differs is whether the INGREDIENT CHECK is
#: available. So this is a REQUIRED ATTRIBUTE ON PAYLOAD, not a class.
#:
#: Each value is (how, kind, reason). `kind` is None iff `how` is not NOT_RECOMPUTABLE.
RECOMPUTABILITY = {
    "sqrt_tr_unified":  (IN_FILE, None, "trace(C_unified)"),
    "sqrt_tr_block":    (IN_FILE, None, "trace(C_blocksum)"),
    "joint_mean_shift_norm": (IN_FILE, None, "norm(hJointMeanShift)"),
    "sqrt_tr_new":      (IN_FILE, None, "trace(hCov_combined5d_total_uthrow)"),
    # OI-140, 2026-08-21. THESE ARE IN_FILE BECAUSE `verify_leg_identity` ACTUALLY RECOMPUTES THEM,
    # not so that `audit_uncomparable` will skip them. The alternative on the table was adding them to
    # DECLARED_UNVERIFIED, which would have greened the gate while leaving remedy (A)'s CENTRAL claim
    # -- that a declared member's legs carry consistent upstream seeds -- unchecked. Both routes to a
    # passing gate were declarations that identity is unverified, one level up from the `_checked = 0`
    # this whole item is about; this is the route that verifies instead of declaring.
    "upstream_estimator_seed_g1_checked": (IN_FILE, None,
        "verify_leg_identity: the flag must equal presence-of-seed, and for a DECLARED member the "
        "seed must equal seed_offset_policy.LEG_BASELINES['g1'] + est_seed_offset"),
    "upstream_estimator_seed_g2_checked": (IN_FILE, None,
        "verify_leg_identity: the flag must equal presence-of-seed, and for a DECLARED member the "
        "seed must equal seed_offset_policy.LEG_BASELINES['g2'] + est_seed_offset"),
    "upstream_fixed_seed_null_norm":  (CROSS_FILE, None, "the throw root's fixed_seed_null_norm"),
    "upstream_joint_mean_shift_norm": (CROSS_FILE, None, "the throw root's joint_mean_shift_norm"),
    # WRITER GAP, not impossible: `x_cv2` and `base` are ordinary per-bin vectors that unified_throw_cov
    # simply does not write. Shipping either one closes it, so this is a decision nobody has taken
    # rather than a limit of the mathematics.
    "fixed_seed_null_norm": (NOT_RECOMPUTABLE, WRITER_GAP,
                             "norm(x_cv2 - base); NEITHER IS WRITTEN by unified_throw_cov.py. Both are "
                             "per-bin vectors, so writing one would close this -- a writer decision, "
                             "not a mathematical limit."),
    # WRITER GAP, and C named it as the example: the inputs are unwritten AND sweep_bank_5d.py emits no
    # completeness histogram at all (measured: 0 occurrences of hCompleteness). Either would close it.
    "globalCompleteness": (NOT_RECOMPUTABLE, WRITER_GAP,
                           "of_in.sum()/denom_nd.sum(); NEITHER IS WRITTEN, and sweep_bank_5d.py emits "
                           "NO completeness histogram (0 occurrences of hCompleteness) though "
                           "unfold_nd_omnifold_unbinned.py has one. Writing either closes this."),
    # STILL A WRITER GAP ON 2026-08-20, AND THE REASON CHANGED WHILE THE VERDICT DID NOT. `how` stays
    # NOT_RECOMPUTABLE because THE DECLARED SET DESCRIBES THE TREE AS IT IS: no adopted root in
    # existence carries `hDiagCombinedOld`. The remedy has landed as a WRITER
    # (`mii_adopt_unified_5d_stamped.py`, remedy (A)'s wrapper) but not as a PRODUCT.
    # CORRECTED 2026-08-21 (OI-147): THE CLAIM "THE WRITE THAT CLOSES IT EXISTS" WAS FALSE, and this
    # is the correction rather than a caveat on it. The write shipped the CLIPPED diagonal, while
    # `sqrt_tr_old` is the RAW trace -- intentionally different quantities whenever any diagonal entry
    # is negative, and the writer's own `assert_diag_matches_sqrt_tr_old` says comparing the clipped
    # sum "would make the check pass on a matrix with negative diagonal entries and fail on nothing".
    # So no write closed it until the RAW diagonal was shipped alongside the clipped one. It is now,
    # and `sqrt_tr_old` is IN_FILE below.
    # TWO PREMISES IN THIS PARAGRAPH EXPIRED AND ARE CORRECTED 2026-08-21 rather than left to be read
    # as current. (i) "the cluster is down" IS FALSE -- it is up, and stage 1 was run end-to-end on it
    # against the real 892 MB archive on 2026-08-21. (ii) "no adopted root in existence carries
    # hDiagCombinedOld" was true of the six products that existed when it was written and is FALSIFIED
    # BY THE PATH ITSELF: `STAMPED_HISTOGRAM_KEY = "hDiagCombinedOld"` is stamped UNCONDITIONALLY, so
    # every product this route produces carries it, and it was MEASURED firing in the
    # audit_uncomparable branch in every arm of that run. `how` STILL STAYS NOT_RECOMPUTABLE, because
    # the flip is coupled exactly as the rest of this comment says -- the verdict is unchanged and only
    # its grounds were stale, which is the distinction worth preserving. See OI-147.
    # Flipping this to IN_FILE would claim
    # recomputability for six products that cannot satisfy it, and would also silently shrink
    # `declared_unrecomputable()`, which every `--acknowledge-unrecomputable` call site must equal
    # exactly. THAT FLIP IS A SEPARATE, COUPLED CHANGE and is enumerated in this commit's message: it
    # needs a `RECOMPUTE` implementation for the key (sum(hDiagCombinedOld)) or the IN_FILE/RECOMPUTE
    # agreement test fails, and it needs the acknowledgement lists re-derived.
    # TWO CORRECTIONS TO THE PREVIOUS TEXT: the size is 0.0856 MB, not 0.527 MB -- 10,694 x 8 B on the
    # cv>0 SUPPORT, where 0.527 MB was the 65,856 GRID, and a grid is not an artifact size. And "already
    # in memory" is true of the IN-FILE edit only: under §25's wrapper the child process has exited, so
    # the wrapper must RE-READ hCov_combined5d_total (one 10694^2 TH2D, ~0.915 GB, not 41 GB) and tie it
    # back to this very key to prove the re-read is the same matrix.
    # OI-147, 2026-08-21: FLIPPED FROM NOT_RECOMPUTABLE TO IN_FILE, because the ingredient now
    # SHIPS. The raw (unclipped) diagonal is written alongside the clipped one, so
    # sqrt(sum(hDiagCombinedOldRaw)) == sqrt_tr_old is a real in-file recomputation. This flip
    # SHRINKS declared_unrecomputable(), which every --acknowledge-unrecomputable call site must
    # equal exactly; those all derive from the function rather than hardcoding, and the one pinned
    # expected list in the tests moves with this change.
    "hDiagCombinedOldRaw": (IN_FILE, None,
                            "clip(raw) compared bin-for-bin against the retained hDiagCombinedOld"),
    "sqrt_tr_old": (IN_FILE, None, "sqrt(sum(hDiagCombinedOldRaw)) -- the RAW diagonal, never the "
                                   "clipped one"),
    # THE SUPERSEDED `sqrt_tr_old` ENTRY IS DELETED, NOT RENAMED. My first pass left it as
    # `_sqrt_tr_old_superseded` so its reasoning would survive -- which put a KEY THAT DOES NOT
    # EXIST into `declared_unrecomputable()`, a CLOSED SET every `--acknowledge-unrecomputable`
    # call site must equal exactly. A phantom member is the same class of defect as a blanket
    # acknowledgement, pointing the other way. Its reasoning, kept as prose instead:
    #   It read NOT_RECOMPUTABLE / WRITER_GAP -- "trace(hCov_combined5d_total), which lives ONLY
    #   in the 41.44 GB member intermediate. THE PREDECLARED BAR'S OPERAND." Two of its grounds
    #   expired. "NO PRODUCT CARRIES IT YET" retired when a product built through the writer
    #   appeared. And "the write that closes it exists" was FALSE: the write shipped the CLIPPED
    #   diagonal, which is not this scalar's ingredient. Shipping the RAW diagonal (OI-147) is
    #   what actually closed it, and the flip carried the coupling that entry demanded --
    #   a RECOMPUTE implementation, and declared_unrecomputable() re-derived.
}


def declared_unrecomputable():
    """The exact set of keys declared `recomputable: no`. THE CLOSED SET the flag must match.

    C's strengthening, and it is the same defect as my comparator being blind to a key absent from both
    files: A BLANKET ACKNOWLEDGEMENT LETS A FUTURE `no` RIDE IN SILENTLY. Someone adds a key, declares it
    unrecomputable, and every existing invocation of `--acknowledge-unrecomputable` swallows it without
    anyone deciding. So the flag takes an EXPLICIT KEY LIST and must equal this set exactly.
    """
    return frozenset(k for k, (how, _, _) in RECOMPUTABILITY.items() if how is NOT_RECOMPUTABLE)


def assert_reasons_are_stated():
    """A `no` WITHOUT A STATED REASON IS THE FAIL-CLOSED CASE, and the reason must name its KIND.

    Declared in the enumeration, never discovered at comparison time -- so this runs at import-adjacent
    time in the tests rather than inside `compare_files`, where a missing reason would surface only on
    the run it blocks.
    """
    problems = []
    for key, entry in sorted(RECOMPUTABILITY.items()):
        if not (isinstance(entry, tuple) and len(entry) == 3):
            problems.append(f"{key}: malformed entry {entry!r}; expected (how, kind, reason)")
            continue
        how, kind, reason = entry
        if how not in (IN_FILE, CROSS_FILE, NOT_RECOMPUTABLE):
            problems.append(f"{key}: unknown how {how!r}")
        if how is NOT_RECOMPUTABLE:
            if kind not in (WRITER_GAP, IMPOSSIBLE):
                problems.append(
                    f"{key}: declared NOT_RECOMPUTABLE with kind {kind!r}. A bare `no` reads as a law "
                    "of nature and freezes a writer gap forever -- state WRITER_GAP or "
                    "MATHEMATICALLY_IMPOSSIBLE.")
            if not reason or len(reason) < 20:
                problems.append(f"{key}: declared NOT_RECOMPUTABLE with no usable reason {reason!r}")
        elif kind is not None:
            problems.append(f"{key}: kind {kind!r} set on a recomputable key")
    if problems:
        _fail("recomputability declarations:\n  " + "\n  ".join(problems))
    return len(RECOMPUTABILITY)



#: ONE definition of fail-closed, in the classes module. See `classes.fail_closed` for H4 -- every
#: `raise SystemExit("[FAIL] ...")` used to exit 1, which `main` maps to INCOMPLETE.
_fail = classes.fail_closed


def _sqrt_trace_from_diag(diag):
    """sqrt(trace) from a diagonal. `trace(C) == sum(diag(C))`, so no matrix is materialised.

    THE BIT-EXACTNESS OF THIS AGAINST THE STAMPED VALUE IS A PROPERTY OF THE SUMMATION ROUTE, NOT OF
    THE MATHEMATICS -- lane D measured all four recomputations bit-exact against the real archive, AND
    found that a sequential Python sum over the SAME diagonal differs in the last ulps. It holds only
    because numpy PAIRWISE summation is on both sides: `np.trace` in the writer
    (`unified_throw_cov.py:483-484`) and `np.sum` here.
    SO DO NOT "SIMPLIFY" EITHER SIDE TO A LOOP OR to `math.fsum`. That change reviews as a no-op and
    breaks a bit-exact gate, which is the worst combination a diff can have.
    """
    return float(np.sqrt(max(float(np.sum(diag)), 0.0)))


#: name -> (ingredient key, function of the ingredient array). `trace(C) == sum(diag(C))`, so a
#: comparator never needs to materialize a 65856x65856 TH2D (34.7 GB) to check a sqrt-trace.
RECOMPUTE = {
    "sqrt_tr_unified":       ("C_unified", _sqrt_trace_from_diag),
    "sqrt_tr_block":         ("C_blocksum", _sqrt_trace_from_diag),
    "sqrt_tr_new":           ("hCov_combined5d_total_uthrow", _sqrt_trace_from_diag),
    "joint_mean_shift_norm": ("hJointMeanShift", lambda v: float(np.linalg.norm(v))),
    # OI-147, 2026-08-21. THE RAW diagonal, never the clipped one. `sqrt_tr_old` is
    # sqrt(trace(C_comb)) computed by the child from the UNCLIPPED matrix, so recomputing it from
    # `hDiagCombinedOld` would compare a different quantity and, per the writer's own docstring,
    # "would make the check pass on a matrix with negative diagonal entries and fail on nothing".
    # Same summation route as its siblings, which is what makes the comparison bit-exact rather
    # than merely close (see _sqrt_trace_from_diag).
    "sqrt_tr_old":           ("hDiagCombinedOldRaw", _sqrt_trace_from_diag),
}


def _clip_consistency(raw, clipped):
    """`clip(raw, 0, inf)` must equal the retained clipped histogram BIN FOR BIN. `(ok, detail)`.

    OI-147's SECOND check, and it is the one that stops the two histograms drifting into being two
    unrelated arrays. Shipping both diagonals makes `sqrt_tr_old` recomputable; it also creates a new
    way to be wrong -- a product could carry a raw diagonal that is not the pre-image of its own
    clipped one, and every scalar check would still pass. Compared exactly, not with a tolerance:
    clipping is a copy-and-threshold, so any difference is a different array rather than arithmetic
    drift.
    """
    raw, clipped = np.asarray(raw, dtype=float), np.asarray(clipped, dtype=float)
    if raw.shape != clipped.shape:
        return False, f"shapes differ: raw {raw.shape} vs clipped {clipped.shape}"
    want = np.clip(raw, 0, None)
    bad = int(np.count_nonzero(want != clipped))
    if bad:
        i = int(np.flatnonzero(want != clipped)[0])
        return False, (f"{bad} bin(s) disagree; first at {i}: clip(raw)={want[i]!r} but the retained "
                       f"clipped histogram holds {clipped[i]!r}")
    return True, f"{raw.size} bins; {int(np.count_nonzero(raw < 0))} negative raw entr(ies) clipped to 0"


#: OI-147. IN_FILE keys whose check is over the member's DIAGONALS rather than a scalar or a
#: histogram-to-scalar recomputation. Kept as a registry, not a free-standing call, so the existing
#: "every IN_FILE key has an implementation" invariant keeps binding -- the same reason
#: SCALAR_RECOMPUTE exists.
DIAGONAL_CONSISTENCY = {
    "hDiagCombinedOldRaw": ("hDiagCombinedOld", _clip_consistency),
}


def digest(array):
    return hashlib.sha256(np.ascontiguousarray(array, dtype=float).tobytes()).hexdigest()


def _th2_content(h):
    """All (nx x ny) CONTENT bins of a TH2D as a float64 array, under/overflow excluded. ONE ROUTE.

    H1, LANE D -- WHAT THIS REPLACED. The original reader reduced every TH2D to its DIAGONAL and the
    comparator digested THAT as the PAYLOAD: for a 10,694 x 10,694 covariance, 10,694 of 114,361,636
    elements = 0.00935%, with the mass measured on the real `C_unified` at
        sum|diag| 3.317e-79   sum|off-diag| 3.307e-76   ratio 997x
    so a member reproducing the diagonal exactly and getting every off-diagonal wrong was a PASS. My
    docstring justified it as "enough for every recomputation this comparator performs" -- true of the
    RECOMPUTE half, false of the COMPARISON half, which is the primary purpose.

    THE BUFFER FAST PATH IS DELETED, C's ruling, AND MY OWN STUB HAD ALREADY TOLD ME WHY.
    I wrote `buf.SetSize(...)` from the OLD PyROOT buffer API. On ROOT 6.28/12 -- the only interpreter
    this repo has -- `h.GetArray()` returns a `cppyy.LowLevelView` whose attributes are
    ['format', 'reshape', 'typecode']: NO SetSize. So the call raised AttributeError on line 1 of the try
    block and THE FALLBACK RAN ON EVERY INVOCATION IT WOULD EVER HAVE HAD. When my local stub lacked
    SetSize I read that as a deficiency in the stub; THE STUB MATCHED THE WORLD, and the cross-check that
    declined was reporting the true state of it. Making the fixture agree with my code instead of with the
    interpreter would have greened a route that cannot execute.

    WHY DELETING BEATS REPAIRING, and this is the part worth keeping:
      VALUE   the row loop runs at 2,147,141 elem/s -> 53.3 s per matrix, 5.3 min for six, ONCE. That is
              0.226% of ONE member's 39.223 A100-h. Same shape as the 250.6 KiB-against-41.44 GB trade:
              WHEN ONE SIDE OF A TRADE IS NEGLIGIBLE, DO NOT OPTIMISE IT.
      HAZARD  deleting removes THREE succeeds-but-wrong routes at once -- the bare `except`, the
              `len(buf)` sentinel trap below, and the view-aliasing that C's own Delete() ruling made live.
      PREMISE it was written to avoid a memory problem THAT DOES NOT EXIST. `key.ReadObj()` materialises
              the matrix regardless, so the buffer route saved NUMPY copies, not ROOT memory: measured
              peak RSS 3,819 MB for the loop vs 3,773 MB for the diagonal, +46 MB on ~3.8 GB. It optimised
              neither dominant cost, so deleting forfeits nothing that was ever obtained.

    THE TRAP A "REPAIR" WOULD HAVE WALKED INTO, recorded even though the route is gone because 2**28-1 is
    not recognisable as a sentinel unless somebody writes it down:
        len(h.GetArray())  ->  268,435,455  ==  2**28 - 1, a cppyy SENTINEL
        true length        ->  (10694 + 2)**2  =  114,404,416
    A repair that sized the read with `len(buf)` would OVER-READ 1.23 GB PAST THE END AND SUCCEED
    SILENTLY. That is succeeds-but-wrong arriving through the fix, written by someone who had just been
    warned about exactly this class.

    NOT EXECUTED HERE: ROOT is absent on this machine. Gate 2's discharge is now one run of THIS function
    against one real matrix, reported with its digest -- with a single route there is no two-path test to
    stand in for it.
    """
    nx, ny = h.GetNbinsX(), h.GetNbinsY()
    out = np.empty((ny, nx), dtype=np.float64)
    for j in range(ny):
        for i in range(nx):
            out[j, i] = h.GetBinContent(i + 1, j + 1)
    return out, "rowloop"


def read_keys_pyroot(path):
    """Real reader. Returns (scalars, diagonals, matrix_digests).

    `matrix_digests[name] = (sha256_hex, n_elements)` -- A DIGEST AND A COUNT, NOT THE ARRAY. `diagonals`
    holds small arrays (10,694 floats) for the recomputation half only.

    MEMORY, WHICH C CORRECTED: a live TH2D costs **~2 GB, not 0.915 GB**, because ROOT resides the sumw2
    array alongside the contents -- D measured 2,027 MB for the adopted root and 3,773 MB for the throw
    root's three. And `GetListOfKeys()` HOLDS EVERY OBJECT UNTIL `f.Close()`, so an earlier version that
    returned all full arrays in a dict streamed NOTHING: it held ROOT's copies *and* numpy's, ~6 GB for
    the throw root. Restructuring the digest alone does not stream; the objects have to be RELEASED.
    SO: digest one key, then `Delete()` it, and never retain a full array. Peak is one live TH2D.

    The row-loop read costs 53.3 s per 10,694^2 matrix, 5.3 min for six, ONCE -- 0.226% of one member's
    39.223 A100-h. WHEN ONE SIDE OF A TRADE IS NEGLIGIBLE, DO NOT OPTIMISE IT: that is why there is one
    read route and not two (see `_th2_content`).

    NOT EXECUTED HERE. ROOT is absent on this machine, and D's run exercised the older diagonal version.
    """
    import ROOT                                            # noqa: local, like every ROOT user here
    try:
        f = ROOT.TFile.Open(path)
    except OSError as exc:                                  # pythonized PyROOT 6.28 raises
        _fail(f"cannot open {path}: {exc.__class__.__name__}: {exc}")
    if not f or f.IsZombie():
        _fail(f"zombie/unopenable: {path}")
    if f.TestBit(ROOT.TFile.kRecovered):
        _fail(f"kRecovered (truncated/uncleanly-closed write): {path}")
    scalars, diagonals, matrix_digests = {}, {}, {}
    routes_used = set()          # WHICH ROUTE EXECUTED IS AN INGREDIENT OF THE DIGEST (BEN-077)
    for key in f.GetListOfKeys():
        name, obj = key.GetName(), key.ReadObj()
        try:
            if hasattr(obj, "GetVal"):
                scalars[name] = obj.GetVal()
            elif hasattr(obj, "GetTitle") and not hasattr(obj, "GetNbinsX"):
                scalars[name] = obj.GetTitle()              # TNamed
            elif hasattr(obj, "GetNbinsY") and obj.GetNbinsY() > 1:
                arr, which = _th2_content(obj)
                routes_used.add(which)
                matrix_digests[name] = (digest(arr), int(arr.size))
                diagonals[name] = np.ascontiguousarray(np.diagonal(arr))   # small; survives
                del arr
            elif hasattr(obj, "GetNbinsX"):
                n = obj.GetNbinsX()
                arr = np.array([obj.GetBinContent(i + 1) for i in range(n)])
                matrix_digests[name] = (digest(arr), int(arr.size))
                diagonals[name] = arr
        finally:
            # RELEASE ROOT'S COPY IMMEDIATELY. Without this the loop accumulates every object until
            # f.Close() and "one key at a time" describes the code's shape, not its footprint.
            try:
                obj.Delete()
            except Exception:
                pass
    f.Close()
    if routes_used:
        print(f"[reader] {path}: TH2D read route(s) = {sorted(routes_used)}", file=sys.stderr)
    return scalars, diagonals, matrix_digests


def read_one_matrix_for_gate2(h):
    """Read ONE real TH2D through the shipped route and report its digest. GATE 2's DISCHARGE.

    THE TWO-PATH CROSS-CHECK IS MOOT NOW AND I AM NOT PRETENDING OTHERWISE. It was the only instrument
    that could catch a buffer read succeeding with the wrong bytes; with a single route there is no second
    route to check it against, so the discharge rests on THE SURVIVING ROUTE HAVING RUN IN THE TREE'S OWN
    CODE against real data, reported with its digest. C was explicit that this changes shape rather than
    being satisfied by the previous instrument, and blurring the two would be the exact move this campaign
    keeps filing.

    THE DISCIPLINE THAT DID SURVIVE, and C rated it the most valuable thing in 40fbc789: REFUSE TO CLAIM A
    CHECK YOU COULD NOT RUN. The old cross-check returned ok=False / "nothing to cross-check" rather than
    ok=True over one path run twice. Its other subjects are `mask_order_hash` against its positive
    control, the summation-route control, and the post-deletion read -- the pattern outlives the route.
    """
    nx, ny = h.GetNbinsX(), h.GetNbinsY()
    arr, which = _th2_content(h)
    name = h.GetName() if hasattr(h, "GetName") else None
    expected = classes.EXPECTED_ELEMENTS.get(name) if name else None
    r = {"route": which, "name": name, "nx": nx, "ny": ny, "elements": int(arr.size),
         "digest": digest(arr), "finite": bool(np.all(np.isfinite(arr)))}

    # FAILS CLOSED ON AN UNLISTED KEY. Lane D found this FAILING OPEN against real PyROOT, and the
    # polarity is the tell: `classes.classify()` fails CLOSED on an unclassified key -- "an unclassified
    # key is exactly the one a future writer added without telling the comparator, so it must fail rather
    # than default" -- while this, THE DISCHARGE INSTRUMENT, defaulted to True. Same module pair, opposite
    # polarity, and the permissive one was the one a gate rests on.
    #
    # The mechanism was `r.get("complete", True)`: with no derived expectation, `complete` was never SET,
    # so the completeness check was skipped, `ok` came out True, AND THE REPORT CARRIED NO INDICATION THAT
    # ANYTHING HAD BEEN SKIPPED -- the absence of the field was the only signal. That is BEN-450's
    # absent-observation-versus-observed-absence, in the instrument.
    #
    # LIVE RATHER THAN ACADEMIC: the table has SEVEN names and member namespacing is the whole M(ii)
    # design, so any member artifact carrying a differently-named key would have received a gate-2
    # discharge that checked FINITENESS ALONE and reported ok=True.
    if expected is None:
        r["expected_elements"] = None
        r["complete"] = None
        r["ok"] = False
        r["why"] = (f"NO DERIVED ELEMENT EXPECTATION for key {name!r}. Completeness is UNCHECKABLE here, "
                    "so this read cannot support a gate-2 discharge. Add the key to "
                    "`classes.EXPECTED_ELEMENTS` with its size DERIVED FROM THE WRITER'S OWN CONSTRUCTION "
                    "LINE -- asserting a number not read out of a writer is how the wrong constant got "
                    "into this module before. Refusing rather than defaulting, for the same reason "
                    "`classify()` refuses an unclassified key.")
        return r

    r["expected_elements"] = expected
    r["complete"] = int(arr.size) == expected
    r["ok"] = bool(r["finite"] and r["complete"])
    if not r["ok"]:
        r["why"] = ("the read is not usable as a gate-2 discharge: "
                    + ("non-finite values present; " if not r["finite"] else "")
                    + ("element count != the derived expectation; " if not r["complete"] else ""))
    return r


#: KEYS ACCEPTED AS UNVERIFIED BY THE ANCHOR, EXPLICITLY. C: the archive's age EXPLAINS an absence and
#: does not LICENCE it, so a PAYLOAD key uncompared for that reason must be covered by in-file
#: recomputation OR declared here. `upstream_*` land here because their recomputation is CROSS_FILE --
#: it needs the throw root, which an adopted-root anchor comparison does not open.
DECLARED_UNVERIFIED = {
    "upstream_fixed_seed_null_norm":
        "PAYLOAD, member-only (landed 5856eeb1 2026-08-11), and CROSS_FILE-recomputable only -- it needs "
        "the throw root, which this comparison does not open. Unverified and labelled.",
    "upstream_joint_mean_shift_norm":
        "PAYLOAD, member-only, CROSS_FILE-recomputable only. Same as above.",
}


def declared_unverified():
    return frozenset(DECLARED_UNVERIFIED)


#: ANY REDUCTION MUST DECLARE **TWO** NUMBERS -- C's ruling, and the template is the defect that
#: prompted it: element coverage 0.00935% and mass outside 997x. EMPTY, because PAYLOAD-class reduction
#: is REFUSED; the table exists so that adding one costs a measurement rather than a line.
#:
#: C's framing, which is sharper than "don't reduce": THE DEFECT WAS NEVER THAT IT REDUCES. It is that it
#: reduced SILENTLY and reported the reduced verdict IN THE VOCABULARY OF THE FULL ONE. A digest of the
#: diagonal is a bit-exact comparison OF A PROJECTION; calling it a bit-exact payload comparison is a
#: category error, not a matter of degree.
#: And the diagonal was the WORST available reduction precisely because it LOOKS TARGETED: sqrt(trace)
#: depends only on the diagonal, so a diagonal-only comparator verifies EXACTLY the bar's operand and
#: NOTHING about the correlations -- while `project_cov_nd.py` marginalises C_low = M C_high M^T, a sum
#: over OFF-DIAGONAL sub-blocks, and its own header warns that wrong ordering "silently produces a
#: plausible number".
#:
#: Each entry: key -> {"element_coverage": float, "mass_fraction_outside": float, "measured_on": str}
DECLARED_REDUCTIONS = {}


def assert_reduction_is_declared(key, coverage):
    """A partial comparison is admissible ONLY with a declared, MEASURED two-number reduction."""
    if coverage >= 1.0:
        return None
    d = DECLARED_REDUCTIONS.get(key)
    if d is None:
        return (f"{key}: UNDECLARED REDUCTION at {100*coverage:.4f}% element coverage. A reduction must "
                "declare BOTH its element coverage AND the mass fraction it excludes, MEASURED -- "
                "0.00935% and 997x is the template. PAYLOAD-class reduction is refused outright.")
    for f in ("element_coverage", "mass_fraction_outside", "measured_on"):
        if f not in d:
            return f"{key}: declared reduction is missing {f!r} -- two numbers and a provenance, or none"
    return None


def leg_baselines():
    """`{"g1": int, "g2": int}` from the POLICY TABLE. Never hardcoded here.

    `seed_offset_policy.LEG_BASELINES` maps module -> (group, baseline) and several modules share a
    group, so the baseline is taken per group and a within-group disagreement is a hard failure --
    a silent re-grouping upstream would relabel a seed rather than error, which is the VL141 class.
    """
    import seed_offset_policy
    out = {}
    for module, (group, baseline) in seed_offset_policy.LEG_BASELINES.items():
        if group in out and out[group] != int(baseline):
            _fail(f"seed_offset_policy.LEG_BASELINES gives coherence group {group!r} two different "
                  f"baselines ({out[group]} and {int(baseline)}); the identity recomputation cannot "
                  f"pick one. Re-derive the table rather than choosing here.")
        out[group] = int(baseline)
    return out


def verify_leg_identity(artifact, m_sc, baselines=None):
    """RECOMPUTE the upstream-seed identity from the member's OWN scalars. `(lines, failed)`.

    OI-140. This is what makes `upstream_estimator_seed_g{1,2}_checked` IN_FILE rather than
    DECLARED_UNVERIFIED. The archive can never supply these keys -- it predates their writer -- so
    the only honest alternative to declaring them unchecked is to check them against something the
    member itself carries. It carries everything needed:

        est_seed_offset_declared, est_seed_offset,
        upstream_estimator_seed_g1/_g2 (present iff that leg had a seed),
        upstream_estimator_seed_g1/_g2_checked (the writer's own claim about that presence)

    THREE INVARIANTS, and the middle one is the substantive one:
      (1) SELF-CONSISTENCY, always checkable. `_checked` must equal presence-of-seed. The writer
          stamps the flag unconditionally and the seed conditionally
          (`mii_adopt_unified_5d_stamped.stamp_pairs`), so a flag disagreeing with its own seed means
          the two stamps came from different states.
      (2) BASELINE CONSISTENCY, checkable only for a DECLARED member. Each leg's seed must be that
          leg's own pinned baseline plus the declared offset. This is the check that catches a leg
          which ran UNHOOKED -- it stamps its baseline, indistinguishable from k = 0 unless a
          non-zero k is declared, in which case a baseline-valued seed is provably wrong.
      (3) COMPLETENESS FOR A DECLARED MEMBER. Both legs must actually carry a seed. The WRITER
          tolerates a missing one (it skips that leg), which is right for a writer -- absence must
          be a readable state. It is NOT right for the gate: `_checked = 0` is ABSENCE AND NOT A
          PASS, and a declared member whose leg carries no seed has an unverifiable identity.

    An UNDECLARED member fails (2) and (3) by construction -- nothing is declared, so nothing can be
    concluded -- and that is reported as UNVERIFIABLE rather than as a mismatch. It still fails the
    gate, which is the status quo; the difference is that it now fails for a stated, checkable
    reason instead of as a side effect of two mandatory-provenance keys being absent.
    """
    keys = ("upstream_estimator_seed_g1_checked", "upstream_estimator_seed_g2_checked")
    if not any(k in m_sc for k in keys):
        return [], False                      # artifact does not carry them; nothing to verify
    lines, failed = [], False
    base = leg_baselines() if baselines is None else baselines
    declared = int(m_sc.get("est_seed_offset_declared", 0))
    offset = m_sc.get("est_seed_offset")

    for group in ("g1", "g2"):
        flag_key, seed_key = f"upstream_estimator_seed_{group}_checked", f"upstream_estimator_seed_{group}"
        if flag_key not in m_sc:
            lines.append(f"[identity] {flag_key} ABSENT from a member that carries its sibling -- "
                         "half a stamp is not a state")
            failed = True
            continue
        flag, seed = int(m_sc[flag_key]), m_sc.get(seed_key)
        # (1) self-consistency
        if flag != (0 if seed is None else 1):
            lines.append(f"[identity] {flag_key} = {flag} but {seed_key} is "
                         f"{'ABSENT' if seed is None else int(seed)} -- THE FLAG CONTRADICTS ITS OWN "
                         "SEED, so the two stamps describe different states")
            failed = True
            continue
        if not declared:
            lines.append(f"[identity] {group}: UNVERIFIABLE -- est_seed_offset_declared = 0, so there "
                         "is no declared offset to check the seed against. Self-consistency holds; "
                         "identity is NOT established. `_checked` is absence, not a pass.")
            failed = True
            continue
        # (3) completeness, for a declared member
        if seed is None:
            lines.append(f"[identity] {group}: DECLARED member carries NO seed for this leg "
                         f"({flag_key} = 0). A declared member's identity cannot be established from "
                         "an absent seed.")
            failed = True
            continue
        # (2) baseline consistency
        if group not in base:
            lines.append(f"[identity] {group}: no baseline in seed_offset_policy.LEG_BASELINES")
            failed = True
            continue
        expect = base[group] + int(offset)
        if int(seed) != expect:
            lines.append(f"[identity] {group}: RECOMPUTED {expect} = baseline {base[group]} + declared "
                         f"offset {int(offset)}, but the member stamps {seed_key} = {int(seed)}. Either "
                         "that leg ran unhooked (its seed is its baseline) or it belongs to a "
                         "different member.")
            failed = True
            continue
        lines.append(f"[identity] OK   {group}: {seed_key} = {int(seed)} = baseline {base[group]} + "
                     f"declared offset {int(offset)}; {flag_key} = 1 agrees with presence")
    return lines, failed


#: IN_FILE keys whose recomputation is over the member's OWN SCALARS rather than a histogram.
#: `RECOMPUTE` cannot express these: its contract is `fn(m_di[ingredient]) -> float` compared against
#: `float(m_sc[name])`, i.e. ONE histogram ingredient and ONE scalar. The identity invariant spans
#: four scalars and a pinned policy table, so it needs a second shape.
#: THIS EXISTS TO KEEP AN EXISTING INVARIANT TRUE, not to dodge it. `test_only_FOUR_of_the_recompute
#: _keys_are_IN_FILE` asserts that every IN_FILE key has an implementation -- "the claim and the
#: capability must not drift apart" -- and adding an IN_FILE row with the implementation in a
#: free-standing function would have made that assertion false. Each value takes `m_sc` and returns
#: `(lines, failed)`.
SCALAR_RECOMPUTE = {}          # populated below, once verify_leg_identity is defined


SCALAR_RECOMPUTE.update({
    "upstream_estimator_seed_g1_checked": verify_leg_identity,
    "upstream_estimator_seed_g2_checked": verify_leg_identity,
})


def audit_uncomparable(artifact, uncomparable_keys):
    """`(lines, class_failed)` for keys the ARCHIVE cannot supply. PURE -- no files, no ROOT.

    C's point, and the one that stops the archive-age fix becoming a loophole: the archive's age
    EXPLAINS an absence and DOES NOT LICENCE it. The member could carry the key wrong and stage 1
    would pass. So each such key must be covered by in-file recomputation, or DECLARED UNVERIFIED.
    Declared beats silent, and neither is the same as checked.

    Extracted from `compare_files` for OI-141 so the branch that decides the verdict can be
    exercised directly. Its input is now `ComparisonResult.uncomparable` rather than a prefix
    parsed out of the callee's message text.
    """
    lines, class_failed = [], False
    for u in uncomparable_keys:
        cls = classes.classify(artifact, u)
        if cls is classes.PROVENANCE:
            continue                                     # provenance is expected to differ; nothing owed
        how = RECOMPUTABILITY.get(u, (None, None, ""))[0]
        if how is IN_FILE:
            continue                                     # recomputation covers it from the member's file
        if u not in declared_unverified():
            lines.append(
                f"{u}: {cls} EXCUSED BY THE ARCHIVE'S AGE AND NOT VERIFIED BY ANYTHING. Its absence is "
                f"EXPLAINED (landed {classes.ARCHIVE_KEY_MAP[u]['landed']}) but not LICENSED -- the "
                "member could carry it wrong and this gate would pass. Cover it by in-file recomputation "
                "or add it to DECLARED_UNVERIFIED. Declared beats silent; neither is checked.")
            class_failed = True
    return lines, class_failed


def compare_files(artifact, archive_path, member_path, offset, read_keys=read_keys_pyroot,
                  rtol=0.0, acknowledge_unrecomputable=None, archive_date=None):
    """Stage 1's comparison. Returns (verdict, lines).

    `rtol=0.0` by default: THIS IS A BIT-EXACT GATE and a tolerance is a decision, not a default.
    """
    assert_reasons_are_stated()          # declared, never discovered at comparison time
    # THE PREDATES_ARCHIVE EXCUSE IS ONLY CHECKABLE AGAINST THE ARCHIVE'S DATE, so the date is REQUIRED
    # rather than defaulted. C: an excuse without its operand is a narration, and the whole point of the
    # dated `landed` strings is that no hand-maintained exception list is needed.
    if archive_date is None:
        _fail("compare_files needs archive_date=(y, m, d). Every PREDATES_ARCHIVE row in the key map is "
              "excused only if it landed AFTER the archive was written, and that is unverifiable without "
              "the archive's date. Read it from the file rather than assuming it.")
    classes.assert_absence_excuses_are_dated(archive_date)
    # CLOSED-SET ACKNOWLEDGEMENT. `None` means "acknowledge nothing"; a list must equal the declared
    # `no` set EXACTLY -- not a subset, not a superset. A subset would leave a blocked key looking
    # acknowledged; a superset names a key nobody declared and is a sign the caller is working from a
    # stale list.
    if acknowledge_unrecomputable is not None:
        got, want = frozenset(acknowledge_unrecomputable), declared_unrecomputable()
        if got != want:
            _fail(
                "--acknowledge-unrecomputable must match the DECLARED unrecomputable set "
                f"exactly.\n        declared : {sorted(want)}\n        given    : {sorted(got)}\n"
                f"        missing  : {sorted(want - got)}\n        extra    : {sorted(got - want)}\n"
                "        A blanket acknowledgement lets a FUTURE `no` ride in silently, which is why "
                "this is a closed set rather than a boolean.")
    # THREE-TUPLE READER (H1). `matrices` is the FULL content array and is what the comparison digests;
    # `diagonals` exists only for the recomputation half. A reader returning one array for both roles is
    # exactly the defect D found.
    a_sc, a_di, a_mx = read_keys(archive_path)
    m_sc, m_di, m_mx = read_keys(member_path)

    # Histograms enter the class comparison as DIGESTS OVER EVERY CONTENT BIN, so `compare()` treats
    # them like scalars and a payload difference is caught without a tolerance question arising.
    a_keys = dict(a_sc, **{k: v[0] for k, v in a_mx.items()})
    m_keys = dict(m_sc, **{k: v[0] for k, v in m_mx.items()})

    result = classes.compare(artifact, a_keys, m_keys)
    verdict, findings = result
    lines = list(findings)
    # OI-141: STRUCTURED, not parsed out of the callee's prose. The previous version rebuilt this
    # list with `l.startswith("UNCOMPARABLE ")` against a string literal in another module, so
    # rewording that string emptied the list, skipped the audit below and turned FAIL into
    # INCOMPLETE -- or PASS with --acknowledge-unrecomputable. Fail-open, and measured: a symmetric
    # full-suite mutation was caught by 0 of ~1992 tests.
    uncomparable_keys = list(result.uncomparable)
    class_failed = verdict == "FAIL"

    # --- COVERAGE: WHAT FRACTION OF EACH ARRAY WAS ACTUALLY COMPARED --------------------------------
    # D's non-optional ask, and it is the part that outlives any particular reader: a gate that says
    # "bit-exact" while comparing 1 element in 10,700 is the strongest instance of the thing this
    # campaign keeps filing. PRINTING THE COMPARED FRACTION MAKES THE CLAIM FALSIFIABLE FROM THE
    # ARTIFACT -- if a future reader silently narrows again, the number moves and somebody sees it.
    # PER-KEY EXPECTED SIZES, and my own first version of this check used ONE constant and was wrong
    # about it -- `hXSecND_flat` is on the 65,856 GRID while every covariance is on the 10,694 SUPPORT.
    # A key with no derived expectation gets its coverage PRINTED but not ASSERTED: asserting a number
    # I have not read out of a writer is exactly how the wrong constant arrived here.
    for name in sorted(m_mx):
        n = int(m_mx[name][1])
        expected = classes.EXPECTED_ELEMENTS.get(name)
        if expected is None:
            lines.append(f"[coverage] {name}: compared {n} elements; NO DERIVED EXPECTATION, "
                         "so completeness is reported and NOT asserted")
            continue
        frac = n / expected
        flag = "" if frac >= 1.0 else "   <-- PARTIAL COMPARISON"
        lines.append(f"[coverage] {name}: compared {n} of {expected} elements "
                     f"({100 * frac:.4f}%){flag}")
        undeclared = assert_reduction_is_declared(name, frac)
        if undeclared:
            lines.append(f"[coverage] {undeclared}")
        if frac < 1.0:
            # APPENDED TO `lines`, NOT TO `findings`. My first version appended to `findings`, which was
            # already copied into `lines` above -- so the verdict flipped to FAIL and THE REASON NEVER
            # REACHED THE CALLER. A guard that detects correctly and reports to a list nobody returns is
            # the same defect as the dead `zombie/unopenable` branch: right direction, no diagnostic.
            lines.append(
                f"{name}: PARTIAL COMPARISON -- {n} of {expected} elements ({100*frac:.4f}%). PAYLOAD "
                "means BIT-EXACT OVER THE WHOLE ARRAY; comparing a subset while reporting bit-exactness "
                "is the H1 defect and must fail rather than be footnoted.")
            class_failed = True

    # --- KEY COVERAGE: C's element-level two-number rule GENERALISED TO KEYS ----------------------
    # "Stage 1 compares 4 of ~13 keys on that artifact. A PASS over four keys and a PASS over thirteen
    # are different claims wearing one word." Same argument as the element coverage, one level up -- and
    # the same remedy: state the fraction so the word cannot carry more than it earned.
    table_keys = set(classes.ARTIFACTS.get(artifact, {}))
    compared = sorted(set(a_keys) & set(m_keys) & table_keys)
    lines.append(f"[coverage] KEYS: compared {len(compared)} of {len(table_keys)} classified keys "
                 f"({100 * len(compared) / len(table_keys):.1f}%) -- "
                 f"uncompared: {sorted(table_keys - set(compared))}")

    unc_lines, unc_failed = audit_uncomparable(artifact, uncomparable_keys)
    lines += unc_lines
    class_failed = class_failed or unc_failed

    # OI-140: run every SCALAR_RECOMPUTE verifier whose key this member carries. UNCONDITIONAL --
    # if these were reached only via the uncomparable list they would inherit exactly the
    # skip-on-reword fragility OI-141 is about. Deduplicated by function, since one verifier can
    # cover several keys.
    for fn in dict.fromkeys(SCALAR_RECOMPUTE[k] for k in SCALAR_RECOMPUTE if k in m_sc):
        v_lines, v_failed = fn(artifact, m_sc)
        lines += v_lines
        class_failed = class_failed or v_failed

    # OI-147's SECOND check: clip(raw) must equal the retained clipped histogram bin for bin.
    # Shipping both diagonals makes sqrt_tr_old recomputable and creates a new way to be wrong -- a
    # product could carry a raw diagonal that is not the pre-image of its own clipped one, and every
    # scalar check would still pass. Runs whenever BOTH are present; a member carrying one and not the
    # other is a FAILURE, not a skip, because half a pair is not a state.
    for key, (other, fn) in DIAGONAL_CONSISTENCY.items():
        if key not in m_di and other not in m_di:
            continue
        if key not in m_di or other not in m_di:
            lines.append(f"[diag] {key}/{other}: only ONE of the pair is present -- the clipped "
                         "histogram and its raw pre-image are written together or not at all")
            class_failed = True
            continue
        ok, detail = fn(m_di[key], m_di[other])
        lines.append(f"[diag] {'OK  ' if ok else 'FAIL'} clip({key}) vs {other}: {detail}")
        class_failed = class_failed or not ok

    # --- the anchor's own identity, WHERE THE ARTIFACT CAN CARRY IT (H3) -----------------------------
    # `anchor_identity` was called unconditionally, but on 2026-08-18 three of five artifacts declared
    # NO identity key, so it emitted three problems every run and FAILED regardless of payload.
    # D'S REASON THIS IS WORSE THAN IT LOOKS: AT STAGE 1 AN UNAVOIDABLE FAIL IS THE THING MOST LIKELY TO
    # GET THE GATE ROUTED AROUND. A check that cannot pass teaches its caller to skip it, and then it
    # protects nothing -- the pressure-toward-green risk arriving from the other side.
    #
    # THE COMMENT HERE USED TO CITE "STAMP_COVERAGE records adopt_unified_5d.py: 0 and
    # unfold_nd_omnifold_unbinned.py: 0". THAT SCHEMA WAS DELETED on 2026-08-20 -- the table is a
    # boolean plus a `how` string now, and both writers' products carry identity -- so the citation
    # named a count that no longer exists about a gap that no longer holds. It is removed rather than
    # updated: this branch's condition is `classes.ARTIFACTS`, and pointing at a different table for
    # its justification is what let the two go stale independently. Ask `identity_is_checkable`.
    #
    # ALL SIX ARTIFACTS DECLARE THE KEYS AS OF 2026-08-20, so the `else` is unreachable for every real
    # artifact today. Kept, because a predicate that can no longer answer NO is not a predicate.
    if classes.identity_is_checkable(artifact):
        identity = classes.anchor_identity(m_sc, offset)
        lines += identity
    else:
        identity = []
        lines.append(
            f"[identity] UNCHECKABLE on {artifact}: its ARTIFACTS table declares no identity key, so "
            "the member cannot be told from the archive by its own contents. NOT a pass, and NOT a "
            "statement about any writer -- under C's 783d648a §25 the file that stamps identity need "
            "not be the file that writes the payload, so an artifact can be unchecked here while its "
            "writer is fine. Recorded rather than failed, because a check that can never pass gets "
            "skipped. To fix: classify the keys in mii_root_payload_classes.ARTIFACTS and make some "
            "writer emit them.")

    # --- THE RECOMPUTATION HALF ---------------------------------------------------------------------
    # `compare()` returns INCOMPLETE while any recompute-required key is unverified; discharging that is
    # this function's job, and only where the ingredients exist.
    #
    # VERDICTS ARE DECIDED BY FLAGS, NOT BY GREPPING THE MESSAGES. My first version computed the verdict
    # with `any("!=" in l or "ABSENT" in l for l in lines)`, which is the defect I spent today filing
    # BEN-482 about, committed inside the tool built to enforce rigour: a message is prose, and "ABSENT"
    # matches both a mandatory key missing from the member and the benign word in a different sentence.
    # A verdict derived from its own diagnostics can be changed by rewording a diagnostic.
    contradicted, ingredient_missing, unverifiable = [], [], []
    discharged = []
    for name, (ingredient, fn) in RECOMPUTE.items():
        if name not in m_sc:
            continue
        if ingredient not in m_di:
            ingredient_missing.append(f"{name}: ingredient {ingredient!r} absent from {member_path}")
            continue
        got, want = fn(m_di[ingredient]), float(m_sc[name])
        if (got == want) if rtol == 0.0 else np.isclose(got, want, rtol=rtol, atol=0.0):
            discharged.append(f"{name}: recomputed {got!r} from {ingredient} == stamped {want!r}")
        else:
            contradicted.append(
                f"{name}: RECOMPUTED {got!r} from {ingredient} != STAMPED {want!r} -- THE FILE "
                "CONTRADICTS ITSELF, which equality against the archive could never have caught")

    for name in sorted(set(classes.RECOMPUTE_REQUIRED) & set(m_sc)):
        if name in RECOMPUTE:
            continue
        how, kind, why = RECOMPUTABILITY.get(
            name, (NOT_RECOMPUTABLE, None, "UNCLASSIFIED -- add a row to RECOMPUTABILITY"))
        if how is NOT_RECOMPUTABLE:
            unverifiable.append(f"{name}: {how} ({kind}) -- {why}")
        else:
            lines.append(f"[recompute] DEFERRED {name}: {how} -- {why}")

    # The table emits "RECOMPUTATION NOT PERFORMED" for every recompute-required key -- that is its
    # DEMAND, and this function is what DISCHARGES it. Printing both leaves a report that says
    # "NOT PERFORMED" and "OK" about the same key three lines apart, which is worse than either.
    done = {d.split(":", 1)[0] for d in discharged}
    lines = [l for l in lines
             if not ("RECOMPUTATION NOT PERFORMED" in l and l.split(":", 1)[0] in done)]
    lines += [f"[recompute] OK   {d}" for d in discharged]
    lines += [f"[recompute] OWED {c}" for c in contradicted]
    lines += [f"[recompute] OWED {m}" for m in ingredient_missing]
    acked = acknowledge_unrecomputable is not None
    for u in unverifiable:
        lines.append(f"[recompute] {'UNVERIFIED (acknowledged)' if acked else 'BLOCKED'} {u}")
    if unverifiable and not acked:
        lines.append("[recompute] BEN-077 CANNOT BE SATISFIED FOR THE KEYS ABOVE FROM THIS FILE. Pass "
                     "--acknowledge-unrecomputable to proceed with them RECORDED as unverified rather "
                     "than silently treated as checked.")

    if class_failed or identity or contradicted or ingredient_missing:
        return "FAIL", lines
    if unverifiable and not acked:
        return "INCOMPLETE", lines
    return "PASS", lines


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--read-one-matrix", metavar="FILE:KEY", default=None,
                    help="GATE 2's DISCHARGE. Read ONE real TH2D through the shipped route and report its "
                         "digest, element count against the derived expectation, and finiteness. With a "
                         "single read route there is no two-path cross-check to stand in for this -- the "
                         "discharge is that THIS code ran on real data. ~53 s for a 10694^2 matrix.")
    ap.add_argument("--artifact", required=False, choices=sorted(classes.ARTIFACTS))
    ap.add_argument("--archive", required=False)
    ap.add_argument("--member", required=False)
    ap.add_argument("--offset", type=int, required=False)
    ap.add_argument("--archive-date", metavar="YYYY-MM-DD", default=None,
                    help="the ARCHIVE's write date. REQUIRED: every PREDATES_ARCHIVE row in the key map "
                         "is excused only if it landed after it, and an excuse without its operand is a "
                         "narration.")
    ap.add_argument("--rtol", type=float, default=0.0,
                    help="0.0 (default) means BIT-EXACT. A tolerance is a decision, not a default.")
    ap.add_argument("--acknowledge-unrecomputable", metavar="KEY", nargs="+", default=None,
                    help="EXPLICIT list of keys whose ingredients are not in the file. Must match the "
                         "declared unrecomputable set EXACTLY -- a blanket flag would let a future "
                         "`no` ride in silently. They are RECORDED as UNVERIFIED, never treated as "
                         f"checked. Declared today: {' '.join(sorted(declared_unrecomputable()))}")
    a = ap.parse_args(argv)

    if a.read_one_matrix:
        # FIRST BRANCH AFTER PARSE, with no path to a comparison -- the same discipline as --gate-only.
        import ROOT                                              # noqa: local
        path, _, keyname = a.read_one_matrix.rpartition(":")
        if not path or not keyname:
            _fail("--read-one-matrix takes FILE:KEY")
        f = ROOT.TFile.Open(path)
        h = f.Get(keyname)
        if not h:
            _fail(f"no key {keyname!r} in {path}")
        r = read_one_matrix_for_gate2(h)
        print(f"[gate2-read] {path}:{keyname}")
        for k in ("ok", "route", "name", "nx", "ny", "elements", "expected_elements", "complete",
                  "finite", "digest", "why"):
            if k in r:
                print(f"[gate2-read]   {k} = {r[k]}")
        f.Close()
        return 0 if r.get("ok") else 2

    if not a.artifact:
        _fail("--artifact is required unless --cross-check-reader is given")
    verdict, lines = compare_files(a.artifact, a.archive, a.member, a.offset, rtol=a.rtol,
                                  acknowledge_unrecomputable=a.acknowledge_unrecomputable,
                                  archive_date=(tuple(int(x) for x in a.archive_date.split("-"))
                                                if a.archive_date else None))
    print(f"[b2] VERDICT: {verdict}")
    print(f"[b2]   artifact {a.artifact}  offset {a.offset}  rtol {a.rtol!r}")
    for l in lines:
        print(f"[b2]   {l}")
    return {"PASS": 0, "INCOMPLETE": 1, "FAIL": 2}[verdict]


if __name__ == "__main__":
    sys.exit(main())

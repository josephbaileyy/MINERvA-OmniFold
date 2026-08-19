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
    # WRITER GAP TODAY, and C's 11g sequencing closes it: `diag_comb` is ALREADY IN MEMORY at
    # adopt_unified_5d.py:128 at the moment sqrt_tr_comb is computed, so the remedy is a WRITE, not a
    # computation, and not even an extra read of the 41 GB file. Until that write lands the key is `no`,
    # because THE DECLARED SET DESCRIBES THE TREE AS IT IS, not as it is about to be.
    "sqrt_tr_old": (NOT_RECOMPUTABLE, WRITER_GAP,
                    "trace(hCov_combined5d_total), which lives ONLY in the 41.44 GB member "
                    "intermediate. THE PREDECLARED BAR'S OPERAND. Closed by C's 11g sequencing: ship "
                    "diag(C_old) (0.527 MB, already in memory at adopt_unified_5d.py:128) BEFORE any "
                    "member intermediate is released. `no` until that write lands."),
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
}


def digest(array):
    return hashlib.sha256(np.ascontiguousarray(array, dtype=float).tobytes()).hexdigest()


def _th2_content(h):
    """All (nx x ny) CONTENT bins of a TH2D as a float64 array, under/overflow excluded.

    H1, LANE D, AGAINST THE REAL ARCHIVE -- THE SEVEREST DEFECT IN THIS MODULE. The previous reader
    reduced every TH2D to its DIAGONAL and `compare_files` digested THAT as the PAYLOAD. For a
    10,694 x 10,694 covariance the gate therefore compared 10,694 of 114,361,636 elements = 0.00935%,
    and D measured the mass on the real `C_unified`:
        sum|diag| 3.317e-79    sum|off-diag| 3.307e-76    ratio 997x
    THE UNCHECKED PART CARRIED ~1000x THE MASS OF THE CHECKED PART. A member reproducing the diagonal
    exactly and getting every off-diagonal wrong was a PASS, under a gate whose word was "bit-exact".
    My docstring claimed "the diagonal is enough for every recomputation this comparator performs" --
    TRUE OF THE RECOMPUTE HALF, FALSE OF THE COMPARISON HALF, and the comparison is the primary purpose.
    One function serving two roles, documented for the lesser one.

    AND WHY NO STUB TEST COULD HAVE CAUGHT IT, which is D's general form and worth more than the fix:
    A FIXTURE HANDS BACK WHATEVER ARRAY THE AUTHOR NAMES "THE DIAGONAL"; THERE IS NO OFF-DIAGONAL FOR
    THE READER TO LOSE. AN INJECTED READER CAN BE TESTED FOR WHAT IT RETURNS AND NEVER FOR WHAT IT
    DISCARDS. The injected-reader design was right for testability; the suspicion belonged on the
    DISCARD, not the parse.

    THERE IS ALSO NO MEMORY ARGUMENT FOR THE DIAGONAL HERE: D measured peak RSS 3,773 MB reading the
    throw root, because `key.ReadObj()` materialises the full matrix regardless. The diagonal saved
    NUMPY memory, not ROOT memory -- so it bought nothing and cost the comparison.

    NOT EXECUTED ANYWHERE. ROOT is absent on the machine this was written on, so the buffer fast path
    below is unverified and falls back to a row loop. Labelled rather than claimed; see the module
    docstring.
    """
    nx, ny = h.GetNbinsX(), h.GetNbinsY()
    try:
        buf = h.GetArray()
        buf.SetSize((nx + 2) * (ny + 2))
        flat = np.frombuffer(buf, dtype=np.float64, count=(nx + 2) * (ny + 2))
        return np.ascontiguousarray(flat.reshape(ny + 2, nx + 2)[1:ny + 1, 1:nx + 1])
    except Exception:
        # FALLBACK, correct but slow. Row-at-a-time so a 114M-element matrix never becomes 114M
        # individual Python calls held in a list.
        out = np.empty((ny, nx), dtype=np.float64)
        for j in range(ny):
            for i in range(nx):
                out[j, i] = h.GetBinContent(i + 1, j + 1)
        return out


def read_keys_pyroot(path):
    """Real reader. Returns (scalars, diagonals, matrices).

    `diagonals` exists ONLY for the recomputation half -- `trace(C) == sum(diag(C))`, so a sqrt-trace
    never needs the full matrix. `matrices` carries the FULL content array and is what the comparison
    digests. Keeping them separate is the point: the two halves want different things and conflating
    them is exactly H1.
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
    scalars, diagonals, matrices = {}, {}, {}
    for key in f.GetListOfKeys():
        name, obj = key.GetName(), key.ReadObj()
        if hasattr(obj, "GetVal"):
            scalars[name] = obj.GetVal()
        elif hasattr(obj, "GetTitle") and not hasattr(obj, "GetNbinsX"):
            scalars[name] = obj.GetTitle()                  # TNamed
        elif hasattr(obj, "GetNbinsY") and obj.GetNbinsY() > 1:
            arr = _th2_content(obj)
            matrices[name] = arr
            diagonals[name] = np.ascontiguousarray(np.diagonal(arr))
        elif hasattr(obj, "GetNbinsX"):
            n = obj.GetNbinsX()
            arr = np.array([obj.GetBinContent(i + 1) for i in range(n)])
            matrices[name] = arr
            diagonals[name] = arr
    f.Close()
    return scalars, diagonals, matrices


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


def compare_files(artifact, archive_path, member_path, offset, read_keys=read_keys_pyroot,
                  rtol=0.0, acknowledge_unrecomputable=None):
    """Stage 1's comparison. Returns (verdict, lines).

    `rtol=0.0` by default: THIS IS A BIT-EXACT GATE and a tolerance is a decision, not a default.
    """
    assert_reasons_are_stated()          # declared, never discovered at comparison time
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
    a_keys = dict(a_sc, **{k: digest(v) for k, v in a_mx.items()})
    m_keys = dict(m_sc, **{k: digest(v) for k, v in m_mx.items()})

    verdict, findings = classes.compare(artifact, a_keys, m_keys)
    lines = list(findings)
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
        n = int(np.asarray(m_mx[name]).size)
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

    # --- the anchor's own identity, WHERE THE ARTIFACT CAN CARRY IT (H3) -----------------------------
    # `anchor_identity` was called unconditionally, but three of five artifacts carry NO identity key --
    # `STAMP_COVERAGE` records adopt_unified_5d.py: 0 and unfold_nd_omnifold_unbinned.py: 0 as the worst
    # gap. So it emitted three problems every run and FAILED regardless of payload.
    # D'S REASON THIS IS WORSE THAN IT LOOKS: AT STAGE 1 AN UNAVOIDABLE FAIL IS THE THING MOST LIKELY TO
    # GET THE GATE ROUTED AROUND. A check that cannot pass teaches its caller to skip it, and then it
    # protects nothing -- the pressure-toward-green risk arriving from the other side.
    if classes.identity_is_checkable(artifact):
        identity = classes.anchor_identity(m_sc, offset)
        lines += identity
    else:
        identity = []
        lines.append(
            f"[identity] UNCHECKABLE on {artifact}: this writer stamps no identity key "
            f"(STAMP_COVERAGE), so the member cannot be told from the archive by its own contents. "
            "NOT a pass -- remedy (A) is C's ruling and this artifact cannot be admitted until it "
            "lands. Recorded rather than failed, because a check that can never pass gets skipped.")

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
    ap.add_argument("--artifact", required=True, choices=sorted(classes.ARTIFACTS))
    ap.add_argument("--archive", required=True)
    ap.add_argument("--member", required=True)
    ap.add_argument("--offset", type=int, required=True)
    ap.add_argument("--rtol", type=float, default=0.0,
                    help="0.0 (default) means BIT-EXACT. A tolerance is a decision, not a default.")
    ap.add_argument("--acknowledge-unrecomputable", metavar="KEY", nargs="+", default=None,
                    help="EXPLICIT list of keys whose ingredients are not in the file. Must match the "
                         "declared unrecomputable set EXACTLY -- a blanket flag would let a future "
                         "`no` ride in silently. They are RECORDED as UNVERIFIED, never treated as "
                         f"checked. Declared today: {' '.join(sorted(declared_unrecomputable()))}")
    a = ap.parse_args(argv)
    verdict, lines = compare_files(a.artifact, a.archive, a.member, a.offset, rtol=a.rtol,
                                  acknowledge_unrecomputable=a.acknowledge_unrecomputable)
    print(f"[b2] VERDICT: {verdict}")
    print(f"[b2]   artifact {a.artifact}  offset {a.offset}  rtol {a.rtol!r}")
    for l in lines:
        print(f"[b2]   {l}")
    return {"PASS": 0, "INCOMPLETE": 1, "FAIL": 2}[verdict]


if __name__ == "__main__":
    sys.exit(main())

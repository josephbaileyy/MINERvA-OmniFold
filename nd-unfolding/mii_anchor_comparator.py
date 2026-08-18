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
        raise SystemExit("[FAIL] recomputability declarations:\n  " + "\n  ".join(problems))
    return len(RECOMPUTABILITY)


def _sqrt_trace_from_diag(diag):
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


def read_keys_pyroot(path):
    """Real reader. NEVER EXECUTED ON THE MACHINE THIS WAS WRITTEN ON -- see the module docstring.

    Returns (scalars, diagonals): scalars are TParameter/TNamed values keyed by name; diagonals are
    per-bin arrays -- the DIAGONAL for a TH2D, the bin contents for a TH1D. The diagonal is enough for
    every recomputation this comparator performs and avoids materializing a 34.7 GB matrix.
    """
    import ROOT                                            # noqa: local, like every ROOT user here
    try:
        f = ROOT.TFile.Open(path)
    except OSError as exc:                                  # pythonized PyROOT 6.28 raises
        raise SystemExit(f"[FAIL] cannot open {path}: {exc.__class__.__name__}: {exc}")
    if not f or f.IsZombie():
        raise SystemExit(f"[FAIL] zombie/unopenable: {path}")
    if f.TestBit(ROOT.TFile.kRecovered):
        raise SystemExit(f"[FAIL] kRecovered (truncated/uncleanly-closed write): {path}")
    scalars, diagonals = {}, {}
    for key in f.GetListOfKeys():
        name, obj = key.GetName(), key.ReadObj()
        if hasattr(obj, "GetVal"):
            scalars[name] = obj.GetVal()
        elif hasattr(obj, "GetTitle") and not hasattr(obj, "GetNbinsX"):
            scalars[name] = obj.GetTitle()                  # TNamed
        elif hasattr(obj, "GetNbinsY") and obj.GetNbinsY() > 1:
            n = obj.GetNbinsX()
            diagonals[name] = np.array([obj.GetBinContent(i + 1, i + 1) for i in range(n)])
        elif hasattr(obj, "GetNbinsX"):
            n = obj.GetNbinsX()
            diagonals[name] = np.array([obj.GetBinContent(i + 1) for i in range(n)])
    f.Close()
    return scalars, diagonals


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
            raise SystemExit(
                "[FAIL] --acknowledge-unrecomputable must match the DECLARED unrecomputable set "
                f"exactly.\n        declared : {sorted(want)}\n        given    : {sorted(got)}\n"
                f"        missing  : {sorted(want - got)}\n        extra    : {sorted(got - want)}\n"
                "        A blanket acknowledgement lets a FUTURE `no` ride in silently, which is why "
                "this is a closed set rather than a boolean.")
    a_sc, a_di = read_keys(archive_path)
    m_sc, m_di = read_keys(member_path)

    # Histograms enter the class comparison as DIGESTS, so `compare()` treats them the same way it
    # treats scalars and a payload difference is caught without a tolerance question arising.
    a_keys = dict(a_sc, **{k: digest(v) for k, v in a_di.items()})
    m_keys = dict(m_sc, **{k: digest(v) for k, v in m_di.items()})

    verdict, findings = classes.compare(artifact, a_keys, m_keys)
    lines = list(findings)
    class_failed = verdict == "FAIL"

    # --- the anchor's own identity, which the CLASSES cannot express ---------------------------------
    identity = classes.anchor_identity(m_sc, offset)
    lines += identity

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

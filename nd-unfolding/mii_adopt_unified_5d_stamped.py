#!/usr/bin/env python3
"""Remedy (A) on the two citable adopted 5D roots, as a WRAPPER around the pinned writer.

WHY THIS FILE EXISTS AND WHY IT IS NOT AN EDIT TO `adopt_unified_5d.py`. Lane C ruled at `783d648a`
§25 that remedy (A) on the adopted roots is a NEW UNPINNED WRAPPER: any edit to
`nd-unfolding/adopt_unified_5d.py` breaks the `implementation_sha256` binding in
`docs/orchestration/state/ben106-stamp-verify-active-56695424.json`, the pre-commit hook refuses the
commit, and the guarding test's own remedy is *"the owning gate must be deliberately re-run and its
receipt re-issued -- DO NOT JUST UPDATE THE HASH."*  The conflict was between C's §11j (stamp inside
the pinned writer) and C's earlier `RULING-20260817-lanec-pinned-readers-get-wrappers-not-copies.md`
(*"new unpinned files ... must be WRAPPERS ... never copies"*), and the earlier ruling won. The
specification of WHAT to stamp is
`docs/orchestration/pending/PENDING-20260819-remedy-A-adopt-blocked-on-ben106-rebinding.patch`; this
file implements it WITHOUT touching the pinned bytes.

SUBPROCESS, NOT IMPORT, and it is C's explicit preference for one reason: the child runs the exact
bytes whose sha256 the receipt binds, so the wrapper cannot silently diverge from what was verified.
`assert_pinned_writer_is_intact` makes that argument executable rather than rhetorical -- it reads
the digest out of the receipt and compares it to the bytes on disk BEFORE launching the child. A
second copy of the digest is not kept here; there is exactly one, in the receipt.

    python3 mii_adopt_unified_5d_stamped.py \
        --uthrow uq_5d/unified_throw_cov_5d.root \
        --combined uq_5d/universe_stage2_5d/uq_universe_5d_covariance_combined.root \
        --out uq_5d/universe_stage2_5d/uq_universe_5d_covariance_combined_uthrow.root \
        -- --prod products/5d/xsec_5d_MEFHC_5iter_lgbm.root

THE THREE PATHS ARE REQUIRED HERE AND HAVE NO DEFAULTS, DELIBERATELY. `adopt_unified_5d.py:76-81`
defaults all four of its paths. Re-typing those defaults in this file would create a SECOND copy of
each path that drifts silently, and the one that matters is `--out`: if the wrapper's idea of the
output and the child's ever disagree, the wrapper stamps a file the child did not write and reports
success. So the caller supplies each path ONCE and it is forwarded verbatim to the child. That is
also why `refuse_conflicting_passthrough` exists: argparse takes the LAST occurrence of a flag, so a
`--out` smuggled through the passthrough tail would redirect the child while this process stamped
the original -- a silent divergence with no error anywhere.

=================================== WHAT IS *NOT* ESTABLISHED ===================================
`import ROOT` raises `ModuleNotFoundError` on the lane-B development host (measured 2026-08-19,
python 3.12.2), so EVERY ROOT-TOUCHING PATH IN THIS FILE IS CLUSTER-UNVERIFIED. Named exactly:
`_read_scalars`, `_read_diagonal`, `_stamp_output`, and `main`'s body from the child launch onward
have never been executed. What HAS been executed locally is every pure function in this module and
its test file. No ROOT test double is provided: a stub that cannot do what pyROOT does would be
evidence about the stub (see the campaign's fixture rule), and the three properties that actually
need proving -- that a `RECREATE`d-and-closed file reopens `UPDATE`, that new `TParameter` keys are
accepted on reopen, and that `TFile.Open` re-points the global current directory -- are properties
of ROOT, not of anything a fake could demonstrate. The first two are C's, verified by C before
ruling; the third is `adopt_unified_5d.py:97-102`'s own measured warning and is why every read here
completes and closes before the output is opened.

THE ONE PLACE THE WRAPPER FORM IS *WORSE* THAN THE IN-FILE EDIT, stated because the specification
says the opposite and the specification is right only about the edit. The patch justifies
`hDiagCombinedOld` as *"a WRITE, not a computation, and not even an extra read of the 41 GB file"*
because `diag_comb` is already in memory at `adopt_unified_5d.py:128`. IN THE WRAPPER FORM IT IS
NOT: the child process has exited and its locals are gone. So this wrapper MUST re-open the combined
intermediate and read `hCov_combined5d_total` again -- one 10694^2 f64 TH2D, ~0.915 GB resident, not
41 GB, but a real extra read that the in-file edit did not need. It is charged here rather than
hidden, and it buys something the in-file edit could not have: re-reading opens a TOCTOU window
between the child's read and ours, and `assert_diag_matches_sqrt_tr_old` CLOSES it by checking the
re-read trace against the `sqrt_tr_old` the child stamped from its own read. A diagonal that does
not reproduce the child's scalar is a different matrix, and the wrapper refuses rather than shipping
it beside a scalar it contradicts.

WHY EXACTLY SEVEN KEYS AND NOT ONE MORE. `mii_root_payload_classes.ADOPTED_UTHROW` carries the seven
in a commented block, and `compare()` FAILS an unclassified key with "NOT IN THE ARCHIVE KEY MAP".
So a key that would be useful but is unclassified is not free -- it reddens the member comparator.
`STAMPED_SCALAR_KEYS` + `STAMPED_HISTOGRAM_KEY` is that block, and a test pins the two against each
other by parsing the table's own comment.

AND NOT A SINGLE `estimator_seed`. VL141 (`VALIDATION_LEDGER.md:1974`): the candidate's estimator
seed is NOT one value on this product -- the throw leg ran at `1000+k` (g2) and the sweep leg whose
covariance the combined intermediate carries ran at `42+k` (g1). One `estimator_seed` key here would
be precisely the false quotable claim VL141 exists to correct, which is also why
`mii_root_payload_classes.IDENTITY_KEYS` is the OFFSET PAIR and `estimator_seed` is only optional.
The offset is single-valued and is the member identity; the estimator seed is per-leg and is named
by group.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
import sys

_HERE = os.path.dirname(os.path.abspath(__file__))
_REPO_ROOT = os.path.dirname(_HERE)
if _HERE not in sys.path:
    sys.path.insert(0, _HERE)

#: The pinned writer, and the receipt that binds its bytes. ONE copy of the digest, in the receipt.
PINNED_WRITER = os.path.join(_HERE, "adopt_unified_5d.py")
BINDING_RECEIPT = os.path.join(_REPO_ROOT, "docs", "orchestration", "state",
                              "ben106-stamp-verify-active-56695424.json")

#: The identity scalars each input leg is expected to carry. Written by `sweep_bank_5d.py:285-287`
#: and propagated to the combined intermediate by `analyze_universes_5d.py:276-277` (g1 leg), and by
#: `unified_throw_cov.py:545,550-551` (g2 leg).
LEG_IDENTITY_KEYS = ("estimator_seed", "est_seed_offset", "est_seed_offset_declared")

#: The leg -> group map is DERIVED from `seed_offset_policy.LEG_BASELINES`, never retyped. `g1` is the
#: sweep leg, reaching this product through the combined intermediate; `g2` is the unified throw.
COMBINED_LEG_MODULE = "sweep_bank_5d"
UTHROW_LEG_MODULE = "unified_throw_cov"

#: Exactly the keys `mii_root_payload_classes.ADOPTED_UTHROW`'s commented block classifies. Anything
#: else reddens `compare()`; anything missing leaves `identity_is_checkable` false.
STAMPED_SCALAR_KEYS = (
    "est_seed_offset",
    "est_seed_offset_declared",
    "upstream_estimator_seed_g1",
    "upstream_estimator_seed_g1_checked",
    "upstream_estimator_seed_g2",
    "upstream_estimator_seed_g2_checked",
)
STAMPED_HISTOGRAM_KEY = "hDiagCombinedOld"

#: The scalar the child stamps from its OWN read of the combined intermediate. Our re-read must
#: reproduce it, or the file changed underneath us.
TRACE_ANCHOR_KEY = "sqrt_tr_old"
TRACE_RTOL = 1e-9


# ============================ PURE LOGIC: TESTABLE WITHOUT ROOT =================================

def _fail(msg):
    raise SystemExit(msg if msg.startswith("[FAIL]") else f"[FAIL] {msg}")


def sha256_of(path):
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for block in iter(lambda: fh.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def assert_pinned_writer_is_intact(writer=None, receipt=None):
    """The subprocess form's whole safety argument, made executable.

    C preferred the subprocess over the import because it *runs the exact bytes whose sha256 the
    receipt binds*. That is only true if somebody checks, and the check has to read the digest from
    the receipt -- a literal copied into this file would be a second binding that can drift from the
    first, which is the defect the receipt exists to prevent.
    """
    writer = PINNED_WRITER if writer is None else writer
    receipt = BINDING_RECEIPT if receipt is None else receipt
    with open(receipt) as fh:
        rec = json.load(fh)
    want = rec["implementation_sha256"]
    declared = rec["implementation"]
    if os.path.basename(declared) != os.path.basename(writer):
        _fail(f"receipt {os.path.basename(receipt)} binds {declared!r}, not {writer!r}. This wrapper "
              "wraps one specific writer; wrapping a different one silently would be the whole class "
              "of defect the binding exists to catch.")
    got = sha256_of(writer)
    if got != want:
        _fail(f"the pinned writer's bytes do NOT match the receipt binding.\n"
              f"        want {want}\n        got  {got}\n"
              f"        from {receipt}\n"
              "        REFUSING TO RUN. The subprocess form's only advantage over an import is that "
              "it executes the bytes the receipt names; against modified bytes it has no advantage "
              "and the provenance claim would be false. Do not update the digest -- re-issue or "
              "retire the owning receipt.")
    return want


def leg_groups(baselines=None):
    """`{"g1": (module, baseline), "g2": (module, baseline)}`, derived from the policy table.

    FAILS CLOSED if the table stops saying what the group names here mean. The `_g1`/`_g2` suffixes
    are stamped into a citable artifact, so a silent re-grouping upstream would relabel a seed rather
    than error -- exactly the class VL141 is about.
    """
    import seed_offset_policy
    table = seed_offset_policy.LEG_BASELINES if baselines is None else baselines
    out = {}
    for module, expect in ((COMBINED_LEG_MODULE, "g1"), (UTHROW_LEG_MODULE, "g2")):
        if module not in table:
            _fail(f"seed_offset_policy.LEG_BASELINES has no entry for {module!r}, so this wrapper "
                  "cannot derive which coherence group its leg belongs to. Re-derive the group; do "
                  "not hardcode it here.")
        group, baseline = table[module]
        if group != expect:
            _fail(f"{module} is in coherence group {group!r}, but this wrapper stamps its seed as "
                  f"{expect!r}. The group names go into a citable artifact, so this must be "
                  "re-derived rather than patched.")
        out[expect] = (module, int(baseline))
    return out


def refuse_conflicting_passthrough(extras):
    """Refuse a passthrough tail that re-specifies a path this wrapper owns.

    argparse keeps the LAST occurrence, so `--out` in the tail would redirect the child while this
    process reopened the original: the child's product would go unstamped and the wrapper would
    report success against a stale file. There is no error anywhere on that path, which is why it is
    refused rather than merged.
    """
    owned = ("--uthrow", "--combined", "--out")
    bad = [a for a in extras
           if any(a == o or a.startswith(o + "=") for o in owned)]
    if bad:
        _fail(f"passthrough arguments re-specify path(s) this wrapper owns: {bad}. argparse takes "
              "the LAST occurrence, so the child would write somewhere this process is not going to "
              "stamp -- and nothing would raise. Pass each path exactly once, via this wrapper's own "
              "flag.")
    return True


def build_child_argv(uthrow, combined, out, extras=(), python=None, writer=None):
    """The exact argv used to run the pinned writer. Separated out so a test can read it."""
    refuse_conflicting_passthrough(list(extras))
    return [python or sys.executable, writer or PINNED_WRITER,
            "--uthrow", str(uthrow), "--combined", str(combined), "--out", str(out),
            *[str(a) for a in extras]]


def assert_legs_are_one_member(g1_keys, g2_keys, off_declared, off_value):
    """The cross-member refusal. A product must not be assembled from two members' legs.

    THIS CHECK COULD NOT EXIST BEFORE remedy (A) reached `analyze_universes_5d.py`: the combined
    intermediate wrote zero scalars, so g1's offset could not reach this point at all. Now the
    contamination the member axis exists to prevent is detectable IN THE ARTIFACT rather than only
    in the directory layout -- the property C refused to rely on when it rejected glob non-recursion
    as a safety argument.

    BOTH LEGS ARE CHECKED AGAINST THE PROCESS, WHICH THE SPECIFICATION DID NOT DO. The preserved
    patch's second refusal reads only the combined leg (`_o1`), so a run whose combined leg predates
    the stamp (offset absent) and whose throw leg carries a *different* member's offset passes it.
    That asymmetry is a hole in the direction the check acts, so it is closed here.
    """
    o1 = g1_keys.get("est_seed_offset")
    o2 = g2_keys.get("est_seed_offset")
    if o1 is not None and o2 is not None and int(o1) != int(o2):
        _fail(f"the two legs of this adopted root are DIFFERENT MEMBERS: the combined intermediate "
              f"(g1) carries est_seed_offset={int(o1)}, the unified throw (g2) carries {int(o2)}. "
              "Refusing to write a product that mixes members.")
    if off_declared:
        for group, o in (("g1", o1), ("g2", o2)):
            if o is not None and int(o) != int(off_value):
                _fail(f"this process declares est_seed_offset={int(off_value)} but its {group} leg "
                      f"was built at {int(o)}. Refusing to relabel another member's covariance as "
                      "this one.")
    return True


def assert_seeds_match_their_baselines(g1_keys, g2_keys, off_declared, off_value, groups=None):
    """A declared member's per-leg seed must be `baseline + k` for THAT leg's own baseline.

    Independent of the offset agreement above, and it is the check that would have caught the defect
    `seed_offset_policy`'s requirement (5) is about from the product side: a leg that ran UNHOOKED
    stamps its baseline, which is indistinguishable from `k = 0` -- unless the process declares a
    non-zero `k`, in which case baseline-valued seeds are provably wrong. Silent when nothing is
    declared, because then nothing can be concluded.
    """
    if not off_declared:
        return False
    groups = leg_groups() if groups is None else groups
    for group, keys in (("g1", g1_keys), ("g2", g2_keys)):
        seed = keys.get("estimator_seed")
        if seed is None:
            continue
        _module, baseline = groups[group]
        expect = int(baseline) + int(off_value)
        if int(seed) != expect:
            _fail(f"{group} leg's estimator_seed is {int(seed)} but this process declares offset "
                  f"{int(off_value)} against baseline {int(baseline)}, i.e. {expect}. Either the leg "
                  "ran unhooked (its seed is its baseline) or it belongs to a different member.")
    return True


def stamp_pairs(g1_keys, g2_keys, off_declared, off_value):
    """The `(key, int)` scalars to write, in write order. NO single `estimator_seed` -- VL141.

    `*_checked` flags are written UNCONDITIONALLY, on `adopt_unified_5d.py:193-196`'s own precedent:
    an absent key cannot distinguish "the leg did not carry it" from "this build predates the
    propagation", and a downstream criterion phrased over the seed passes vacuously on either.
    Absence must be a readable state, not an inference.
    """
    pairs = [("est_seed_offset_declared", int(off_declared)),
             ("est_seed_offset", int(off_value))]
    for group, keys in (("g1", g1_keys), ("g2", g2_keys)):
        seed = keys.get("estimator_seed")
        pairs.append((f"upstream_estimator_seed_{group}_checked", 0 if seed is None else 1))
        if seed is not None:
            pairs.append((f"upstream_estimator_seed_{group}", int(seed)))
    unclassified = [k for k, _ in pairs if k not in STAMPED_SCALAR_KEYS]
    if unclassified:
        _fail(f"about to stamp key(s) {unclassified} that mii_root_payload_classes.ADOPTED_UTHROW "
              "does not classify. compare() reports an unclassified key as 'NOT IN THE ARCHIVE KEY "
              "MAP' and FAILS, so an unclassified stamp reddens the member comparator rather than "
              "helping it. A writer change and a table change are one change, in both directions.")
    return pairs


def assert_diag_matches_sqrt_tr_old(trace_raw, sqrt_tr_old, rtol=TRACE_RTOL):
    """Our re-read of the combined intermediate must reproduce the child's own `sqrt_tr_old`.

    THE WRAPPER FORM'S OWN HAZARD, AND ITS CLOSURE. The in-file edit read the matrix once; this
    wrapper reads it a second time, after the child exited, so the file could have been replaced in
    between and `hDiagCombinedOld` would then be the diagonal of a matrix that is not this product's
    input -- shipped inside the product as though it were. `sqrt_tr_old` is `sqrt(trace(C_comb))`
    computed by the child from ITS read (`adopt_unified_5d.py:127,177`), so equality is a real
    cross-check and not a restatement.

    Compared on the RAW trace, not the clipped one: the child does not clip when it computes the
    scalar (`:127` traces `C_new` before modification), while the histogram we write is clipped at
    zero to match `:128`. Comparing the clipped sum would make the check pass on a matrix with
    negative diagonal entries and fail on nothing.
    """
    if sqrt_tr_old is None:
        _fail(f"the child's product carries no {TRACE_ANCHOR_KEY}, so the diagonal we re-read cannot "
              "be tied to the matrix the child actually adopted. Refusing to ship an unanchored "
              f"{STAMPED_HISTOGRAM_KEY}.")
    want = float(sqrt_tr_old) ** 2
    got = float(trace_raw)
    if want == 0.0:
        ok = got == 0.0
    else:
        ok = abs(got - want) <= rtol * abs(want)
    if not ok:
        _fail(f"the re-read diagonal of hCov_combined5d_total has trace {got!r}, but the child "
              f"stamped {TRACE_ANCHOR_KEY}={float(sqrt_tr_old)!r} whose square is {want!r} "
              f"(rtol={rtol}). The combined intermediate is not the matrix this product was built "
              f"from -- refusing to write {STAMPED_HISTOGRAM_KEY} from it.")
    return True


def parse_args(argv=None):
    ap = argparse.ArgumentParser(
        description="Remedy (A) wrapper: run the pinned adopt_unified_5d.py as a subprocess, then "
                    "stamp member identity + C's 11g diagonal into its output.")
    ap.add_argument("--uthrow", required=True, help="the unified throw ROOT (g2 leg)")
    ap.add_argument("--combined", required=True, help="the combined intermediate (g1 leg)")
    ap.add_argument("--out", required=True, help="the adopted product to write AND stamp")
    ap.add_argument("passthrough", nargs="*",
                    help="everything after a literal `--` is forwarded verbatim to "
                         "adopt_unified_5d.py (e.g. --prod X, --cv-centered)")
    # THE SPLIT IS DONE HERE AND NOT BY argparse, AND IT WAS argparse.REMAINDER FIRST. MEASURED: with
    # REMAINDER and no `--`, `--cv-centered` is rejected as "unrecognized arguments" -- so the `--` was
    # never optional and the docstring that said a leading `--` is merely "stripped" was wrong. Splitting
    # explicitly makes the contract one rule instead of two, and the failure without `--` stays LOUD
    # (argparse exit 2) rather than becoming a silently dropped flag. A dropped `--cv-centered` would
    # build the mean-centered product under the cv-centered product's name, which is the single worst
    # outcome available here: two roots that differ in nothing except payload and centering.
    argv = list(sys.argv[1:] if argv is None else argv)
    if "--" in argv:
        cut = argv.index("--")
        head, extras = argv[:cut], argv[cut + 1:]
    else:
        head, extras = argv, []
    a = ap.parse_args(head)
    if a.passthrough:
        _fail(f"unexpected positional argument(s) {a.passthrough}. Everything meant for "
              "adopt_unified_5d.py must follow a literal `--`.")
    a.extras = extras
    return a


# ===================== ROOT-TOUCHING PATH -- CLUSTER-UNVERIFIED, EVERY LINE =====================
# Nothing below this banner has ever been executed: `import ROOT` raises ModuleNotFoundError on the
# lane-B host. Do not read the tests beside this file as evidence about any of it.

def _read_scalars(path, keys):
    """Read `TParameter` ints from a file, INSIDE ITS OWN OPEN WINDOW. CLUSTER-UNVERIFIED."""
    import ROOT
    f = ROOT.TFile.Open(path)
    if not f or f.IsZombie():
        _fail(f"cannot open {path} for reading")
    try:
        out = {}
        for k in keys:
            obj = f.Get(k)
            out[k] = int(obj.GetVal()) if obj else None
        return out
    finally:
        f.Close()


def _read_diagonal(path, hist="hCov_combined5d_total"):
    """`(raw_diagonal, clipped_diagonal)` of a square TH2D. CLUSTER-UNVERIFIED.

    Reads via `GetBinContent` rather than the raw buffer: `adopt_unified_5d._diag:52-55` already
    does exactly this for the same reason -- no full-matrix numpy materialization on top of the
    histogram ROOT has already resident.
    """
    import numpy as np
    import ROOT
    f = ROOT.TFile.Open(path)
    if not f or f.IsZombie():
        _fail(f"cannot open {path} for reading")
    try:
        h = f.Get(hist)
        if not h:
            _fail(f"{path} carries no {hist}, so C's 11g diagonal cannot be built from it")
        n = h.GetNbinsX()
        raw = np.array([h.GetBinContent(i + 1, i + 1) for i in range(n)], dtype=np.float64)
    finally:
        f.Close()
    return raw, np.clip(raw, 0, None)


def _stamp_output(out, pairs, diag):
    """Reopen `out` UPDATE, write the scalars and the diagonal, READ THEM BACK. CLUSTER-UNVERIFIED.

    `adopt_unified_5d.py:169` opens the output `RECREATE` and `:225` closes it, so a later `UPDATE`
    is a legitimate post-step (C verified both before ruling). The read-back is not decoration:
    `:212-219` records that the first version of that writer's stamp block printed "provenance
    stamped" while all nine writes had silently failed into a read-only file. A print is not
    evidence.
    """
    import ROOT
    fo = ROOT.TFile.Open(out, "UPDATE")
    if not fo or fo.IsZombie() or not fo.IsWritable():
        _fail(f"cannot reopen {out} in UPDATE mode; the stamp cannot land")
    try:
        already = [k for k in STAMPED_SCALAR_KEYS + (STAMPED_HISTOGRAM_KEY,) if fo.Get(k)]
        if already:
            _fail(f"{out} already carries {already}. ROOT would append a second cycle of each key "
                  "rather than replacing it, leaving two answers to one question in a citable "
                  "artifact. Refusing to stamp twice -- rebuild the product instead.")
        fo.cd()   # ROOT's current directory is global state; be explicit (BEN-106)
        for key, val in pairs:
            ROOT.TParameter("int")(key, int(val)).Write()
        hd = ROOT.TH1D(STAMPED_HISTOGRAM_KEY,
                       "diag of the OLD combined covariance (sqrt_tr_old's ingredient)",
                       len(diag), 0, len(diag))
        for i, v in enumerate(diag):
            hd.SetBinContent(i + 1, float(v))
        hd.Write()
        missing = [k for k, _ in pairs if not fo.Get(k)]
        if not fo.Get(STAMPED_HISTOGRAM_KEY):
            missing.append(STAMPED_HISTOGRAM_KEY)
        if missing:
            _fail(f"remedy (A) stamps did not land in {out}: {missing}")
    finally:
        fo.Close()
    return True


def main(argv=None):
    a = parse_args(argv)
    assert_pinned_writer_is_intact()
    groups = leg_groups()
    import seed_offset_policy
    off_declared, off_value = seed_offset_policy.declared_offset()

    argv_child = build_child_argv(a.uthrow, a.combined, a.out, a.extras)
    print(f"[remedyA] running the PINNED writer as a subprocess: {' '.join(argv_child)}")
    rc = subprocess.call(argv_child)
    if rc != 0:
        _fail(f"the pinned writer exited {rc}; nothing is stamped. The wrapper does not repair or "
              "second-guess the writer -- it only adds keys to a product the writer produced.")
    if not os.path.exists(a.out):
        _fail(f"the pinned writer exited 0 but {a.out} does not exist. Refusing to report a stamp "
              "against a file that is not there.")

    # EVERY READ COMPLETES AND CLOSES BEFORE THE OUTPUT IS OPENED. `adopt_unified_5d.py:97-102`:
    # `TFile.Open` re-points ROOT's global current directory, so writes issued after a later open
    # land in THAT file -- and a READ-mode file swallows them while the Python carries on.
    g2_keys = _read_scalars(a.uthrow, LEG_IDENTITY_KEYS)
    g1_keys = _read_scalars(a.combined, LEG_IDENTITY_KEYS)
    diag_raw, diag_clipped = _read_diagonal(a.combined)
    anchor = _read_scalars(a.out, (TRACE_ANCHOR_KEY,))[TRACE_ANCHOR_KEY]

    assert_legs_are_one_member(g1_keys, g2_keys, off_declared, off_value)
    assert_seeds_match_their_baselines(g1_keys, g2_keys, off_declared, off_value, groups)
    assert_diag_matches_sqrt_tr_old(float(diag_raw.sum()), anchor)
    pairs = stamp_pairs(g1_keys, g2_keys, off_declared, off_value)
    _stamp_output(a.out, pairs, diag_clipped)
    print(f"[remedyA] stamped AND read back in {a.out}: "
          f"{ {k: v for k, v in pairs} } + {STAMPED_HISTOGRAM_KEY}[{len(diag_clipped)}]")


if __name__ == "__main__":
    main()

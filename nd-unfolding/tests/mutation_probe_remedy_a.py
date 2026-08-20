#!/usr/bin/env python3
"""Mutation probe for remedy (A)'s wrapper. RUN IT; DO NOT TRUST A REPORTED RESULT.

WHY THIS FILE EXISTS RATHER THAN A TABLE IN A COMMIT MESSAGE. Round 1 reported "8/8 mutations caught"
with no recoverable artifact -- no list, no runner, nothing a reviewer could re-execute -- so lane C
could neither verify it nor rely on it, and rightly did neither. Worker agreement is not verification;
a claim about test power needs the same recoverable-artifact standard as a physics claim.

    python3 nd-unfolding/tests/mutation_probe_remedy_a.py          # all mutations
    python3 nd-unfolding/tests/mutation_probe_remedy_a.py C4        # one, by id
    python3 nd-unfolding/tests/mutation_probe_remedy_a.py --self-test   # does the PROBE work?

Each mutation is applied to the working tree, the suite is run, and the tree is restored from the
in-memory original in a `finally`. `SURVIVED` is a finding about the SUITE, not about the mutation.

============================ THE CRITERION IS "A NAMED TEST FAILED" ============================
Lane C's round-2 caveat on this probe, and it was right: `verdict = CAUGHT if rc != 0` would score a
mutation that merely broke IMPORTABILITY as caught. Every one of round 2's 16 happened to name a real
failing test, so the number was not wrong -- but the criterion was, and a criterion that is only
accidentally sound is the shape this repo keeps filing. A non-zero exit with NO named failure is now
reported as `UNATTRIBUTED`, counted separately, and returns non-zero: it means the probe learned
nothing about test power from that mutation, which is a finding about the PROBE and must not hide
inside the caught column. Same discipline as `ANCHOR-LOST`.

THE B-SERIES ARE MINE (round 1). THE C-SERIES ARE LANE C's, transcribed from its FAIL verdict --
`C1` is D1 itself and the other five were the ROOT-path mutations that survived round 1's suite.
THE N/D-SERIES ARE ROUND 3: `N4` is the one survivor of C's round-2 set, and `D8`-`D13` are the
guards added to close C's PASS-WITH-SCOPE residuals. A guard filed without a mutation is a guard
nobody has measured.
"""
import pathlib
import re
import subprocess
import sys

HERE = pathlib.Path(__file__).resolve().parent
ND = HERE.parent
W = ND / "mii_adopt_unified_5d_stamped.py"
C = ND / "mii_root_payload_classes.py"

#: (id, what it breaks, file, find, replace). `find` must be unique in the file.
MUTATIONS = [
    # ---- round 1, mine ----
    ("B1", "drop covered_by from adopt's row", C,
     '"covered_by": "mii_adopt_unified_5d_stamped.py",', '"covered_by": None,'),
    ("B2", "covered_by names a file that does not name adopt", C,
     '"covered_by": "mii_adopt_unified_5d_stamped.py",', '"covered_by": "mii_stage0_distinctness.py",'),
    ("B3", "revert the cross-member refusal to the specification's g1-only form", W,
     'for group, o in (("g1", o1), ("g2", o2)):', 'for group, o in (("g1", o1),):'),
    ("B4", "drop hDiagCombinedOld from the class table", C,
     '    "hDiagCombinedOld": PAYLOAD,\n', ''),
    ("B5", "drop the g1 ARCHIVE_KEY_MAP row", C,
     '    "upstream_estimator_seed_g1": {"landed": "lane B remedy (A) wrapper 2026-08-20", '
     '"derive": None,\n                                   "absence": PREDATES_ARCHIVE},\n', ''),
    ("B6", "stamp a single estimator_seed (VL141 violation)", W,
     'pairs.append((f"upstream_estimator_seed_{group}_checked"',
     'pairs.append(("estimator_seed", 0)); pairs.append((f"upstream_estimator_seed_{group}_checked"'),
    ("B7", "widen the passthrough refusal to --prod", W,
     'owned = ("--uthrow", "--combined", "--out")',
     'owned = ("--uthrow", "--combined", "--out", "--prod")'),
    ("B8", "loosen the trace tolerance to 1.0", W, "TRACE_RTOL = 1e-9", "TRACE_RTOL = 1.0"),
    # ---- lane C's, from the FAIL verdict ----
    ("C1", "D1 ITSELF: read the anchor with the int reader again", W,
     "    anchor = _read_double_scalar(a.out, TRACE_ANCHOR_KEY)",
     "    anchor = _read_int_scalars(a.out, (TRACE_ANCHOR_KEY,))[TRACE_ANCHOR_KEY]"),
    ("C1b", "D1's other half: re-coerce inside the double reader", W,
     "        return float(obj.GetVal())", "        return int(obj.GetVal())"),
    ("C2", "stamp the UNCLIPPED diagonal", W,
     "    _stamp_output(a.out, pairs, diag_clipped)", "    _stamp_output(a.out, pairs, diag_raw)"),
    ("C3", "delete the double-stamp refusal", W,
     '        already = [k for k in STAMPED_SCALAR_KEYS + (STAMPED_HISTOGRAM_KEY,) if fo.Get(k)]',
     '        already = []'),
    ("C4", "delete the write read-back", W,
     '        missing = [k for k, _ in pairs if not fo.Get(k)]', '        missing = []'),
    ("C5", "delete the TOCTOU closure call from main", W,
     "    assert_diag_matches_sqrt_tr_old(float(diag_raw.sum()), anchor)\n", ""),
    ("C6", "delete the read-only / zombie reopen guard", W,
     "    if not fo or fo.IsZombie() or not fo.IsWritable():",
     "    if False:"),
    # ---- round 3: C's round-2 survivor, and the guards that closed its residuals ----
    ("N4", "delete _read_diagonal's close (C's ROUND-2 SURVIVOR)", W,
     "    finally:\n        f.Close()\n    return raw, np.clip(raw, 0, None)",
     "    finally:\n        pass\n    return raw, np.clip(raw, 0, None)"),
    ("D8", "revert the message to 'NOTHING HAS BEEN WRITTEN' (true of the stamp, false of the product)", W,
     '"        NO STAMP HAS BEEN WRITTEN -- and that is NOT the same as nothing having "',
     '"        NOTHING HAS BEEN WRITTEN. "'),
    ("D9", "delete the discriminator for cause (3), leaving the message safe but not diagnostic", W,
     '"        TO TELL (3) FROM (1) AND (2), TWO READS AND NO WRITES: compare --combined\'s "',
     '"        "'),
    ("D10", "restore the uncaught OverflowError/ValueError on a non-finite int key", W,
     "            try:\n                integral = float(raw) == int(raw)\n"
     "            except (OverflowError, ValueError) as exc:",
     "            integral = float(raw) == int(raw)\n            if False:"),
    ("D11", "put the 'no ROOT test double' denial back into the caveat", W,
     "**THERE *IS* A ROOT TEST DOUBLE, and this paragraph said there was not until 2026-08-20.** It is",
     "No ROOT test double is provided, deliberately. Ignore"),
    ("D12", "add a THIRD call site for the value-guarded int reader (C's Q1 trigger)", W,
     "    g2_keys = _read_int_scalars(a.uthrow, LEG_IDENTITY_KEYS)",
     "    g2_keys = _read_int_scalars(a.uthrow, LEG_IDENTITY_KEYS)\n"
     "    _unused = _read_int_scalars(a.out, LEG_IDENTITY_KEYS)"),
    ("D13", "add a key to LEG_IDENTITY_KEYS (C's Q1 trigger, other arm)", W,
     'LEG_IDENTITY_KEYS = ("estimator_seed", "est_seed_offset", "est_seed_offset_declared")',
     'LEG_IDENTITY_KEYS = ("estimator_seed", "est_seed_offset", "est_seed_offset_declared",\n'
     '                     "sqrt_tr_old")'),
    # ---- the accusation itself ----
    ("C7", "restore the false accusation against the 41.44 GB intermediate", W,
     '"        *** DO NOT DELETE, REGENERATE OR RE-STAGE THE COMBINED INTERMEDIATE ON THE "',
     '"        The combined intermediate is not the matrix this product was built from. "'),
]

SUITE = ["tests/test_remedy_a_adopt_wrapper.py", "tests/test_uq_remediation.py"]


#: pytest colours its output, and an ANSI-decorated FAILURE-SECTION HEADER also contains the word
#: FAILED. Round 3 measured `C4` attributing itself to three traceback fragments alongside the real
#: test name -- harmless to the verdict, but the verdict's whole claim is "a NAMED TEST failed", so a
#: set that can contain non-names weakens exactly the criterion this probe was corrected to enforce.
#: Strip the escapes FIRST, then require the line to BE a short-summary line.
_ANSI = re.compile(r"\x1b\[[0-9;]*m")


def run_suite():
    r = subprocess.run([sys.executable, "-m", "pytest", "-q", *SUITE, "-k", "not DECOY",
                        "-p", "no:cacheprovider", "--color=no"],
                       cwd=ND, capture_output=True, text=True)
    names = set()
    for line in r.stdout.split("\n"):
        line = _ANSI.sub("", line).strip()
        if not line.startswith("FAILED "):
            continue
        names.add(line.split("::")[-1].split(" -")[0].strip())
    return r.returncode, sorted(names)


def classify(rc, failed):
    """`(verdict)` from a suite result. FACTORED OUT SO IT CAN BE TESTED IN ALL THREE DIRECTIONS.

    Lane C's caveat was that `CAUGHT if rc != 0` scores an import break as a catch. Fixing that adds a
    BRANCH, and a branch nobody has seen fire is a claim -- the repo's own rule is that a guard gets a
    test that it fires and a narrowing gets a test that it does NOT. `--self-test` exercises all three.
    """
    if rc == 0:
        return "SURVIVED"
    return "CAUGHT" if failed else "UNATTRIBUTED"


#: A mutation whose ONLY effect is to make the module unimportable. It exists to prove the
#: `UNATTRIBUTED` branch fires on a real suite run rather than only in a unit check: pytest exits
#: non-zero on a collection error and names no test, which is precisely the result that used to be
#: counted as CAUGHT.
SELF_TEST_MUTATION = ("SELFTEST", "break importability (must be UNATTRIBUTED, never CAUGHT)", W,
                      "import argparse", "import argparse\nthis is not python")


def self_test():
    rc_base, failed_base = run_suite()
    if rc_base != 0:
        print(f"SELF-TEST :: CANNOT RUN -- baseline is red ({failed_base})")
        return 2
    problems = []
    for rc, failed, want in ((0, [], "SURVIVED"), (1, ["test_x"], "CAUGHT"), (1, [], "UNATTRIBUTED"),
                             (2, [], "UNATTRIBUTED")):
        got = classify(rc, failed)
        print(f"  classify(rc={rc}, failed={failed!r}) -> {got}   (want {want})")
        if got != want:
            problems.append(f"classify({rc}, {failed!r}) = {got}, want {want}")

    _mid, what, path, find, repl = SELF_TEST_MUTATION
    orig = path.read_text()
    if find not in orig:
        problems.append(f"SELFTEST anchor lost: {find!r} is not in {path.name}")
    else:
        try:
            path.write_text(orig.replace(find, repl, 1))
            rc, failed = run_suite()
        finally:
            path.write_text(orig)
        verdict = classify(rc, failed)
        print(f"  END-TO-END {what}: rc={rc}, named={failed!r} -> {verdict}")
        if verdict != "UNATTRIBUTED":
            problems.append(f"an unimportable module classified as {verdict}, not UNATTRIBUTED "
                            f"(rc={rc}, named={failed!r})")
    if path.read_text() != orig:
        problems.append("THE TREE WAS NOT RESTORED -- restore it by hand before doing anything else")
    for pr in problems:
        print(f"  PROBLEM {pr}")
    print(f"SELF-TEST :: {'FAIL' if problems else 'PASS'}")
    return 1 if problems else 0


def main(argv):
    if "--self-test" in argv:
        return self_test()
    want = set(argv[1:])
    rows, survived, unattributed = [], [], []
    base_rc, base_f = run_suite()
    if base_rc != 0:
        print(f"REFUSING TO PROBE: the unmutated suite is not green ({base_f}). A mutation probe over "
              "a red baseline cannot attribute anything.")
        return 2
    print(f"baseline: green over {len(SUITE)} files\n")
    for mid, what, path, find, repl in MUTATIONS:
        if want and mid not in want:
            continue
        orig = path.read_text()
        if find not in orig:
            print(f"  ANCHOR-LOST {mid}: {what}\n      the mutation no longer applies; re-derive it")
            rows.append((mid, "ANCHOR-LOST", what, []))
            continue
        try:
            path.write_text(orig.replace(find, repl, 1))
            rc, failed = run_suite()
        finally:
            path.write_text(orig)
        # THE CRITERION IS "A NAMED TEST FAILED", NOT "rc != 0" -- see the module docstring and
        # `classify`, which is separate so that `--self-test` can fire all three of its branches.
        verdict = classify(rc, failed)
        if verdict == "SURVIVED":
            survived.append((mid, what))
        elif verdict == "UNATTRIBUTED":
            unattributed.append((mid, what))
        print(f"  {verdict:12} {mid:4} {what}")
        for f in failed:
            print(f"               by {f}")
        rows.append((mid, verdict, what, failed))
    n = len(rows)
    print(f"\n{sum(1 for r in rows if r[1] == 'CAUGHT')}/{n} caught "
          f"(criterion: a NAMED test failed)")
    for mid, what in survived:
        print(f"  SURVIVED {mid}: {what}  <- A FINDING ABOUT THE SUITE")
    for mid, what in unattributed:
        print(f"  UNATTRIBUTED {mid}: {what}  <- A FINDING ABOUT THE PROBE: the suite exited "
              "non-zero but named no test, so this mutation measured nothing")
    lost = [r[0] for r in rows if r[1] == "ANCHOR-LOST"]
    if lost:
        print(f"  ANCHOR-LOST {lost}  <- re-derive these; they no longer apply")
    return 1 if (survived or unattributed or lost) else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))

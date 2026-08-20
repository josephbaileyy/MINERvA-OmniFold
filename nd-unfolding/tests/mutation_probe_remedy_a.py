#!/usr/bin/env python3
"""Mutation probe for remedy (A)'s wrapper. RUN IT; DO NOT TRUST A REPORTED RESULT.

WHY THIS FILE EXISTS RATHER THAN A TABLE IN A COMMIT MESSAGE. Round 1 reported "8/8 mutations caught"
with no recoverable artifact -- no list, no runner, nothing a reviewer could re-execute -- so lane C
could neither verify it nor rely on it, and rightly did neither. Worker agreement is not verification;
a claim about test power needs the same recoverable-artifact standard as a physics claim.

    python3 nd-unfolding/tests/mutation_probe_remedy_a.py          # all mutations
    python3 nd-unfolding/tests/mutation_probe_remedy_a.py C4        # one, by id

Each mutation is applied to the working tree, the suite is run, and the tree is restored from the
in-memory original in a `finally`. `SURVIVED` is a finding about the SUITE, not about the mutation.

THE B-SERIES ARE MINE (round 1). THE C-SERIES ARE LANE C's, transcribed from its FAIL verdict --
`C1` is D1 itself and the other five were the ROOT-path mutations that survived round 1's suite.
"""
import pathlib
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
    # ---- the accusation itself ----
    ("C7", "restore the false accusation against the 41.44 GB intermediate", W,
     '"        *** DO NOT DELETE, REGENERATE OR RE-STAGE THE COMBINED INTERMEDIATE ON THE "',
     '"        The combined intermediate is not the matrix this product was built from. "'),
]

SUITE = ["tests/test_remedy_a_adopt_wrapper.py", "tests/test_uq_remediation.py"]


def run_suite():
    r = subprocess.run([sys.executable, "-m", "pytest", "-q", *SUITE, "-k", "not DECOY",
                        "-p", "no:cacheprovider"],
                       cwd=ND, capture_output=True, text=True)
    names = sorted({l.split("::")[-1].split(" -")[0].replace("\x1b[0m", "")
                    for l in r.stdout.split("\n") if "FAILED" in l})
    return r.returncode, names


def main(argv):
    want = set(argv[1:])
    rows, survived = [], []
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
        verdict = "CAUGHT" if rc != 0 else "SURVIVED"
        if rc == 0:
            survived.append((mid, what))
        print(f"  {verdict:8} {mid:4} {what}")
        for f in failed:
            print(f"               by {f}")
        rows.append((mid, verdict, what, failed))
    n = len(rows)
    print(f"\n{sum(1 for r in rows if r[1] == 'CAUGHT')}/{n} caught")
    for mid, what in survived:
        print(f"  SURVIVED {mid}: {what}  <- A FINDING ABOUT THE SUITE")
    return 1 if survived else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))

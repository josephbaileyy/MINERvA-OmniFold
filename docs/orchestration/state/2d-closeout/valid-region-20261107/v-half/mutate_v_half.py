#!/usr/bin/env python3
"""Mutation harness for v_half.py (DECLARATION.md section 8): one mutant per rule clause, per noise term, per class
precedence, per print-only separation and per control. Every mutant must be KILLED by test_v_half.py.

The pattern is mutate_valid_region.py's. Each mutant replaces one exact snippet in the module, in place, and the
snippet must occur exactly once. It then runs the whole suite in a child process and restores the original in
`finally`. The original's sha256 is checked before the first mutant and after the last. The child runs with
PYTHONDONTWRITEBYTECODE=1 and -B. A run counts only if the runner printed "Ran N tests" with the baseline's N.
"Killed" means the suite failed or errored.

Usage (from this directory): python3 -B mutate_v_half.py > mutants.txt
Exit code: 0 if the baseline passes and every mutant is killed; 3 otherwise.
"""
import hashlib
import os
import re
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
TARGET = HERE / "v_half.py"

MUTANTS = [
    # the rule's clauses
    ("floor-0.02", "FLOOR = 0.01 ", "FLOOR = 0.02 "),
    ("floor-strict", '"applies": bool(abs(d) >= floor)}', '"applies": bool(abs(d) > floor)}'),
    ("floor-one-sided", '"applies": bool(abs(d) >= floor)}', '"applies": bool(d >= floor)}'),
    ("half-0.6", "HALF = 0.5 ", "HALF = 0.6 "),
    ("b-without-one-plus-d", "    b = r * (1.0 + d)\n    rec =", "    b = r\n    rec ="),
    ("b-not-absolute", "    m = half * abs(d) - abs(b)\n", "    m = half * abs(d) - b\n"),
    ("d-not-absolute", "    m = half * abs(d) - abs(b)\n", "    m = half * d - abs(b)\n"),
    # the noise terms and the band
    ("k-1", "K = 2.0 ", "K = 1.0 "),
    ("pass-side-strict", '    if rec["lo"] >= 0.0:', '    if rec["lo"] > 0.0:'),
    ("no-band", '    if rec["lo"] >= 0.0:\n        rec["class"] = PASS\n    elif rec["hi"] < 0.0:',
     '    if m >= 0.0:\n        rec["class"] = PASS\n    elif m < 0.0:'),
    ("nu-not-scaled", "math.sqrt(((1.0 + d) * nu) ** 2", "math.sqrt((nu) ** 2"),
    ("sigma-d-dropped", "(half * math.copysign(1.0, d) - abs(r)) ** 2 * sd ** 2)", "0.0 * sd ** 2)"),
    ("sigma-d-no-derivative", "(half * math.copysign(1.0, d) - abs(r)) ** 2 * sd ** 2)", "sd ** 2)"),
    ("sigma-d-sgn-d-dropped", "(half * math.copysign(1.0, d) - abs(r)) ** 2 * sd ** 2)", "(half - abs(r)) ** 2 * sd ** 2)"),
    ("sigma-d-abs-r-dropped", "(half * math.copysign(1.0, d) - abs(r)) ** 2 * sd ** 2)",
     "(half * math.copysign(1.0, d) - r) ** 2 * sd ** 2)"),
    ("sigma-d-ddof-0", "    return np.std(np.vstack(rows), axis=0, ddof=1)\n\n\ndef sigma_b_prr",
     "    return np.std(np.vstack(rows), axis=0, ddof=0)\n\n\ndef sigma_b_prr"),
    ("sigma-d-four-seeds", "NOISE_TRUTH, NOISE_SEEDS = \"A7_gibuu\", (991000, 994001, 994002, 994003, 994004)",
     "NOISE_TRUTH, NOISE_SEEDS = \"A7_gibuu\", (994001, 994002, 994003, 994004)"),
    # the cell's class
    ("any-truth-not-every", "    if FAIL in classes:\n        return NOT_VALID\n",
     "    if all(c == FAIL for c in classes if c != NA) and FAIL in classes:\n        return NOT_VALID\n"),
    ("nowhere-reads-valid", "    if all(c == NA for c in classes):\n        return NOWHERE\n", ""),
    ("no-d-ignored", "    if NOD in classes:\n        return NO_D\n", ""),
    ("unresolved-reads-valid", "    if UNRES in classes:\n        return UNRES\n", ""),
    ("no-d-over-fail", "    if FAIL in classes:\n        return NOT_VALID\n    if NOD in classes:\n        return NO_D\n",
     "    if NOD in classes:\n        return NO_D\n    if FAIL in classes:\n        return NOT_VALID\n"),
    ("no-d-as-not-applicable", '    if d is None:\n        return {"class": NOD}', '    if d is None:\n        return {"class": NA}'),
    # the truth set and the print-only separation
    ("priors-dropped", "    return [t for t in h1[\"truths\"] if t.get(\"graded\") is True]",
     "    return [t for t in h1[\"truths\"] if t.get(\"graded\") is True and t.get(\"group\") != \"prior\"]"),
    ("gibuu-domain-in-verdict", "    main_ = classify(A, sd)\n", "    main_ = classify(A, sd, domain=True)\n"),
    ("option-a-in-verdict", "    main_ = classify(A, sd)\n", "    main_ = classify(A, sd, use_prr_b=True, sd_b=sigma_b_prr(D[\"H2\"]))\n"),
    ("option-a-uses-f0b-bias", "                pairs[name] = pair(bp / (1.0 + d), float(sd_b[ci]) / (1.0 + d), d,",
     "                pairs[name] = pair(float(a[\"r\"][ci]), float(sd_b[ci]) / (1.0 + d), d,"),
    ("h-star-min", "            return max(v) if v else None", "            return min(v) if v else None"),
    # the controls
    ("c-pin-skipped", '    return _ctl("C-PIN", not bad,', '    return _ctl("C-PIN", True,'),
    ("c-cells-skipped", '    return _ctl("C-CELLS", ok,', '    return _ctl("C-CELLS", True,'),
    ("c-truths-skipped", '    return _ctl("C-TRUTHS", ok,', '    return _ctl("C-TRUTHS", True,'),
    ("c-prr-skipped", '    return _ctl("C-PRR", ok,', '    return _ctl("C-PRR", True,'),
    ("c-prr-no-zero-check", "    ok = h2.get(\"verdict\") == \"COMPLETE\" and not bad and not zeros",
     "    ok = h2.get(\"verdict\") == \"COMPLETE\" and not bad"),
    ("c-prr-no-length-check", "    ok = h2.get(\"verdict\") == \"COMPLETE\" and not bad and not zeros and not short",
     "    ok = h2.get(\"verdict\") == \"COMPLETE\" and not bad and not zeros"),
    ("c-form-compares-a-form-with-itself", "            f2 = abs(r) <= HALF * abs(d) / (1.0 + d)\n", "            f2 = f1\n"),
    ("licence-without-held-out", '                        "held-out truths (the truths are not held out)",\n', ""),
    ("c-domain-skipped", '    return _ctl("C-DOMAIN", ok,', '    return _ctl("C-DOMAIN", True,'),
    ("c-finite-skipped", '    return _ctl("C-FINITE", not bad,', '    return _ctl("C-FINITE", True,'),
    ("c-hand-skipped", '    return _ctl("C-HAND", ok,', '    return _ctl("C-HAND", True,'),
    ("c-hand-no-alt", "          and (d_alt is None or abs(d_alt - d_raw) <= 1e-6 * max(1.0, abs(d_raw))))",
     "          )"),
    ("stop-still-classifies", "    if ok:\n        out[\"readings\"] = readings(D)\n", "    out[\"readings\"] = readings(D)\n"),
]


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def run_suite():
    env = dict(os.environ, PYTHONDONTWRITEBYTECODE="1")
    r = subprocess.run([sys.executable, "-B", "-m", "unittest", "test_v_half"], cwd=HERE, env=env,
                       capture_output=True, text=True, timeout=900)
    m = re.search(r"^Ran (\d+) tests? in", r.stderr, re.M)
    return r.returncode, int(m.group(1)) if m else None, r.stderr.strip().splitlines()[-1] if r.stderr.strip() else ""


def main():
    orig_text = TARGET.read_text()
    orig_sha = sha(TARGET)
    rc, n_base, tail = run_suite()
    print(f"target {TARGET.name} sha256 {orig_sha}")
    print(f"suite test_v_half.py sha256 {sha(HERE / 'test_v_half.py')}; python {sys.version.split()[0]}")
    print(f"baseline: rc {rc}, ran {n_base}, '{tail}'")
    if rc != 0 or not n_base:
        print("BASELINE FAILS: no mutant is meaningful")
        return 3
    survivors, rows = [], []
    try:
        for mid, old, new in MUTANTS:
            k = orig_text.count(old)
            if k != 1:
                rows.append((mid, "NOT-APPLIED", f"snippet occurs {k} times"))
                survivors.append(mid)
                continue
            TARGET.write_text(orig_text.replace(old, new))
            rc, n, tail = run_suite()
            if rc == 0 and n == n_base:
                verdict = "SURVIVED"
                survivors.append(mid)
            elif rc != 0:
                verdict = "KILLED"
            else:
                verdict = f"SUSPECT (rc 0, ran {n} != {n_base})"
                survivors.append(mid)
            rows.append((mid, verdict, tail))
    finally:
        TARGET.write_text(orig_text)
    after = sha(TARGET)
    for r in rows:
        print("\t".join(r))
    print(f"restored sha256 {after} {'== original' if after == orig_sha else '!= ORIGINAL'}")
    print(f"mutants {len(MUTANTS)}; killed {len(MUTANTS) - len(survivors)}; survivors {survivors}")
    return 0 if not survivors and after == orig_sha else 3


if __name__ == "__main__":
    sys.exit(main())

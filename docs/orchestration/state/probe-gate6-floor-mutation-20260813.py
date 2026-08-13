"""Mutation control for lane B's Gate-6 Leg F test battery.

QUESTION: the 52 tests pass. Can they FAIL? A battery that cannot fail is not evidence,
and the orchestrator's item 3 asks specifically whether the refusal test binds or is
vacuous. The only way to answer is to break the code and check the test notices.

READ-ONLY ON THE REPO. The module and test are copied to a scratch dir, the COPY is
mutated, and pytest runs against the copy. Nothing under the worktree is written.

PREDECLARED, before running: every mutation below removes or weakens a property the
battery claims to test, so EVERY ONE MUST PRODUCE AT LEAST ONE FAILURE. A mutation that
leaves 52/52 passing is a hole, and M2 is the one I most expect to survive -- asserting
on a substring of an error message is the classic assertion that looks binding and is not.
"""
import re
import shutil
import tempfile
import subprocess
import sys
from pathlib import Path

# docs/orchestration/state/<this file> -> repo root. Never hardcoded (the p4_evidence.py lesson).
REPO = Path(__file__).resolve().parents[3]
WORK = Path(tempfile.mkdtemp(prefix="gate6-mutation-"))

MUTATIONS = {
    "M0 baseline, unmutated": (None, None),
    "M1 refusal removed: verdict on any n": (
        r'if s\["n"\] != len\(DRAWS_REQUIRED\):', 'if False:'),
    "M2 refusal kept, but stops naming the prohibition": (
        r'"Verdicting on a subset is what do_not_select_passing_subset forbids\."',
        '"Too few draws."'),
    "M3 process threshold >= weakened to >": (
        r'elif rng >= THRESH_PROCESS_RANGE:', 'elif rng > THRESH_PROCESS_RANGE:'),
    "M4 seed threshold <= weakened to <": (
        r'if rng <= THRESH_SEED_RANGE and all_in_band:',
        'if rng < THRESH_SEED_RANGE and all_in_band:'),
    "M5 band check dropped from branch 1": (
        r'if rng <= THRESH_SEED_RANGE and all_in_band:', 'if rng <= THRESH_SEED_RANGE:'),
    "M6 frozen process threshold silently retuned": (
        r'THRESH_PROCESS_RANGE = 0\.1740029887300910', 'THRESH_PROCESS_RANGE = 0.05'),
    # M7 v1 WAS VOID: the literal "ddof=1" occurs only in a DOCSTRING (:198) and a key
    # name (:219); the sd is computed by hand. My regex mutated prose, changed no behaviour,
    # and the harness reported "SURVIVED" -- a hole in MY instrument reported as a hole in
    # B's battery. Kept as M7void, with the real mutation as M7, because a mutation harness
    # that can silently mutate a comment manufactures false holes.
    "M7void sd 'ddof=1' string (hits a DOCSTRING, not code)": (r'ddof=1', 'ddof=0'),
    "M7 sd genuinely switched to population (n-1 -> n)": (
        r'sum\(\(x - mean\) \*\* 2 for x in col\) / \(n - 1\)',
        'sum((x - mean) ** 2 for x in col) / n'),
    "M8 F_range sign flipped to min-max": (
        r'rng = max\(col\) - min\(col\)', 'rng = min(col) - max(col)'),
    "M9 d_by_draw drops the abs, so a low draw looks in-band": (
        r'abs\(values_by_draw\[j\]\[k\] - 1\.0\)', '(values_by_draw[j][k] - 1.0)'),
}


def run(label, pattern, repl):
    if WORK.exists():
        shutil.rmtree(WORK)
    (WORK / "nd-unfolding/pet").mkdir(parents=True)
    (WORK / "nd-unfolding/tests").mkdir(parents=True)
    (WORK / "docs/orchestration").mkdir(parents=True)
    mod = REPO / "nd-unfolding/pet/gate6_floor_statistics.py"
    dst = WORK / "nd-unfolding/pet/gate6_floor_statistics.py"
    shutil.copy(mod, dst)
    shutil.copy(REPO / "nd-unfolding/tests/test_gate6_floor_statistics.py",
                WORK / "nd-unfolding/tests/test_gate6_floor_statistics.py")
    shutil.copy(REPO / "docs/orchestration/PREDECLARATION-20260813-gate6-floor-replication.md",
                WORK / "docs/orchestration/PREDECLARATION-20260813-gate6-floor-replication.md")
    if pattern:
        src = dst.read_text()
        new, n = re.subn(pattern, repl, src, count=1)
        if n != 1:
            print(f"[{label}]\n  *** MUTATION DID NOT APPLY -- pattern not found; arm is void ***\n")
            return None
        dst.write_text(new)
    r = subprocess.run([sys.executable, "-m", "pytest",
                        str(WORK / "nd-unfolding/tests/test_gate6_floor_statistics.py"), "-q"],
                       capture_output=True, text=True, cwd=WORK)
    tail = [l for l in r.stdout.splitlines() if "passed" in l or "failed" in l]
    return tail[-1].strip() if tail else r.stdout.strip()[-120:]


print(__doc__)
for label, (pat, rep) in MUTATIONS.items():
    res = run(label, pat, rep)
    if res is None:
        continue
    survived = "failed" not in res
    verdict = ("BASELINE" if pat is None else
               ("*** SURVIVED -- the battery does not catch this ***" if survived
                else "caught"))
    print(f"[{label}]\n  {res}\n  -> {verdict}\n")

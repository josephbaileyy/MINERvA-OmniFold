#!/usr/bin/env python3
"""Fail when a `\\`-continued shell command is interrupted by a comment or an assignment.

WHY THIS EXISTS, and it is one measured failure rather than a general principle. On 2026-08-18 a
one-line hook was inserted between a continued command's first line and its continuation in
`nd-unfolding/sbatch_bootstrap_5d_gpu.sh`. Bash swallowed the continuation as a comment, so:

    rg_run "$OUT" python3 bootstrap_nd.py --npz of_inputs_5d.npz \\
    # ...hook comment...
    EST_SEED=$(( 42 + ${MNV_EST_SEED_OFFSET:-0} ))
      --seed ${SLURM_ARRAY_TASK_ID} --estimator-seed ${EST_SEED} --iters 5 --out "$OUT"

ran as `bootstrap_nd.py --npz of_inputs_5d.npz` -- NO seed arguments at all -- with the remainder
executing as `--seed: command not found`.

**`bash -n` PASSED ON THAT FILE.** Syntax valid, arguments destroyed. `bash -n` is the instrument 35
shell edits were reported clean under earlier the same day, and it is blind to exactly the failure a
line-insertion edit produces. This check is the cheap covering complement; the expensive one is
`nd-unfolding/launcher_argv_probe.py`, which executes the launcher and reads the observed argv.

TWO FALSE-POSITIVE CLASSES ARE EXCLUDED, both found by running it over the tree before trusting it:

  * A COMMENT LINE CANNOT OPEN A CONTINUATION -- its trailing backslash is inside the comment. The
    first version tracked state from comment lines too and reported 9 documentation blocks. An
    over-reporting lint gets switched off exactly as fast as an under-reporting one is trusted.
  * `env VAR=1 VAR2=2 \\` continued by more assignments is correct usage, so an assignment on a
    continuation line is flagged only when the command head is an invocation and not an env prefix.

CONTROLLED IN BOTH DIRECTIONS by `--self-test`: it must be clean on the repaired file and must FIRE on
both reconstructed defects. A null from a lint is a claim about the lint.
"""
from __future__ import annotations

import argparse
import os
import re
import subprocess
import sys

ASSIGN = re.compile(r'^\s*[A-Za-z_][A-Za-z0-9_]*=')
CMD = re.compile(r'\b(python3?|srun|rg_run|sbatch|bash)\b')
ENVPREFIX = re.compile(r'\b(env|export)\b')


def findings(text):
    """`[(lineno, reason)]` for every interrupted continuation in `text`."""
    out = []
    inside = False
    head = ""
    for i, line in enumerate(text.split("\n"), 1):
        s = line.strip()
        if s.startswith("#"):
            if inside:
                out.append((i, "COMMENT inside a continued command -- swallows the remainder"))
            continue
        if inside and ASSIGN.match(line) and CMD.search(head) and not ENVPREFIX.search(head):
            out.append((i, "ASSIGNMENT inside a continued COMMAND (not an env prefix)"))
        if not inside:
            head = s
        inside = line.rstrip().endswith("\\")
    return out


def tracked_shell_files(root):
    out = subprocess.run(["git", "-C", root, "ls-files", "*.sh", "**/*.sh"],
                         capture_output=True, text=True).stdout.split()
    return [f for f in out if os.path.exists(os.path.join(root, f))]


def self_test():
    """Both directions, EXACT, and the WALK is exercised rather than assumed.

    TWO LEVELS OF THE SAME DEFECT, both raised by lane E:

    (a) THE MUST-FIRE ASSERTIONS WERE TRUTHY AND THE MUST-NOT-FIRE ONES EXACT, so a lint firing at
        the wrong LINE or for the wrong REASON passed the pair. They are exact tuples now.

    (b) THE SELF-TEST PROVED `findings()` WORKS AND PROVED NOTHING ABOUT THE WALK THAT FEEDS IT.
        The tree scan asserts a COUNT -- "377 scanned, 0 interrupted" -- and nothing exercised
        `tracked_shell_files`. A glob matching NOTHING is caught (0 scanned -> CANNOT CHECK, exit 2),
        which was already right. A glob matching a SUBSET reports a smaller count and PASSES.
        "377 files were clean" and "every tracked shell file was clean" are different claims and only
        the first was tested. The walk control below builds a throwaway git repo containing a
        known-bad file and requires the walk to FIND it and the lint to FLAG it -- so the denominator
        is measured, not asserted.
    """
    good = ('rg_run "$OUT" python3 boot.py --npz x.npz \\\n'
            '  --seed 1 --iters 5 --out "$OUT"\n')
    assert findings(good) == [], f"clean case flagged: {findings(good)}"

    bad_comment = ('rg_run "$OUT" python3 boot.py --npz x.npz \\\n'
                   '# hook comment\n'
                   '  --seed 1 --out "$OUT"\n')
    got = findings(bad_comment)
    want = [(2, "COMMENT inside a continued command -- swallows the remainder")]
    assert got == want, f"comment case: got {got}, want {want}"

    bad_assign = ('rg_run "$OUT" python3 boot.py --npz x.npz \\\n'
                  'EST_SEED=$(( 42 + 0 ))\n'
                  '  --seed 1 --out "$OUT"\n')
    got = findings(bad_assign)
    want = [(2, "ASSIGNMENT inside a continued COMMAND (not an env prefix)")]
    assert got == want, f"assignment case: got {got}, want {want}"

    env_ok = 'env A=1 \\\n  B=2 \\\n  python3 x.py\n'
    assert findings(env_ok) == [], f"env prefix false-positived: {findings(env_ok)}"
    doc_ok = '# usage:  foo \\\n#           --bar\nreal_command\n'
    assert findings(doc_ok) == [], f"documentation block false-positived: {findings(doc_ok)}"

    # ---- (b) THE WALK CONTROL: a throwaway repo whose only tracked .sh is known-bad ----
    import shutil
    import tempfile
    tmp = tempfile.mkdtemp(prefix="contlint.")
    try:
        subprocess.run(["git", "-C", tmp, "init", "-q"], check=True, capture_output=True)
        sub = os.path.join(tmp, "deep", "nested")
        os.makedirs(sub)
        target = os.path.join(sub, "planted.sh")
        with open(target, "w", encoding="utf-8") as fh:
            fh.write(bad_assign)
        with open(os.path.join(tmp, "clean.sh"), "w", encoding="utf-8") as fh:
            fh.write(good)
        subprocess.run(["git", "-C", tmp, "add", "-A"], check=True, capture_output=True)
        walked = tracked_shell_files(tmp)
        assert "deep/nested/planted.sh" in walked, (
            f"THE WALK MISSED A TRACKED .sh IN A SUBDIRECTORY: {walked}. A walk that returns a "
            "SUBSET reports a smaller count and still PASSES, which is the hole this control exists "
            "to close.")
        assert "clean.sh" in walked, f"the walk missed a top-level tracked .sh: {walked}"
        rc = main(["--root", tmp])
        assert rc == 1, f"the lint must FAIL (1) on a tree containing the planted file; got {rc}"
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    print("CONTINUATION :: SELF-TEST PASS -- findings() exact in both directions, and the WALK "
          "found a planted bad file in a nested subdirectory (denominator measured, not asserted)")
    return 0


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--root", default=os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                                   "..", ".."))
    a = ap.parse_args(argv)
    if a.self_test:
        return self_test()
    root = os.path.abspath(a.root)
    files = tracked_shell_files(root)
    if not files:
        print("CONTINUATION :: CANNOT CHECK -- no tracked .sh found. Not a pass.")
        return 2
    bad = []
    for f in files:
        with open(os.path.join(root, f), encoding="utf-8", errors="replace") as fh:
            for ln, why in findings(fh.read()):
                bad.append(f"{f}:{ln}  {why}")
    print(f"CONTINUATION :: {len(files)} tracked .sh scanned, {len(bad)} interrupted continuation(s)")
    for b in bad:
        print("  " + b)
    print("CONTINUATION :: " + ("PASS" if not bad else "FAIL"))
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())

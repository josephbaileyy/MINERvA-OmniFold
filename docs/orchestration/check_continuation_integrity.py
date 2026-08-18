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
    """Both directions. Reconstructs the two defect shapes and requires each to FIRE."""
    good = ('rg_run "$OUT" python3 boot.py --npz x.npz \\\n'
            '  --seed 1 --iters 5 --out "$OUT"\n')
    assert findings(good) == [], f"clean case flagged: {findings(good)}"
    bad_comment = ('rg_run "$OUT" python3 boot.py --npz x.npz \\\n'
                   '# hook comment\n'
                   '  --seed 1 --out "$OUT"\n')
    assert findings(bad_comment), "MISSED a comment inside a continuation"
    bad_assign = ('rg_run "$OUT" python3 boot.py --npz x.npz \\\n'
                  'EST_SEED=$(( 42 + 0 ))\n'
                  '  --seed 1 --out "$OUT"\n')
    assert findings(bad_assign), "MISSED an assignment inside a continuation"
    env_ok = ('env A=1 \\\n  B=2 \\\n  python3 x.py\n')
    assert findings(env_ok) == [], f"env prefix false-positived: {findings(env_ok)}"
    doc_ok = ('# usage:  foo \\\n#           --bar\nreal_command\n')
    assert findings(doc_ok) == [], f"documentation block false-positived: {findings(doc_ok)}"
    print("CONTINUATION :: SELF-TEST PASS (clean/comment/assignment/env-prefix/doc-block)")
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

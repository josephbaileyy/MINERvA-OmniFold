#!/usr/bin/env python3
"""Enumerate the artifact families that need `backfill_completion_markers.sh` at restore.

WHY THIS EXISTS. RESTORE-2026-08-03.md Step 0b says "one line per artifact family actually in
flight" and then leaves the list to the reader. It was never written down. Skip Step 0b and the
first resume re-runs every completed unit in the campaign, because `lib/resume_guard.sh` now
requires a `${OUT}.done` marker and nothing on /pscratch has one -- the fix postdates every
artifact there.

A STATIC LIST WOULD ROT. 85 shell files use the guard and the set moves with the campaign, so this
derives the families from the launchers themselves: every `rg_run "<target>"` / `rg_is_complete
"<target>"` site IS a family by construction, because that is the same expression the guard will
consult on resume. Run it, read the output, run the backfill lines it prints.

    python3 lib/enumerate_backfill_families.py                 # the backfill command lines
    python3 lib/enumerate_backfill_families.py --unresolved    # only what it could NOT resolve

VALIDATOR CHOICE IS DELIBERATE AND NOT GUESSED. `.root` -> root, `.npz` -> npz, anything else is
reported UNRESOLVED rather than falling back to `--validator size`. Size is the BEN-023 defect
performing itself, and a tool that quietly emits it would launder the defect into the restore.

A COLLECTOR THAT MATCHES NOTHING REPORTS SUCCESS -- the failure mode `verify_hash_bindings.py`
exists to catch, and the same floor device is used here. Raise FAMILY_FLOOR when launchers are
added; lowering it needs the same justification as deleting a guard.
"""
import argparse
import glob
import os
import re
import sys

FAMILY_FLOOR = 12

_GUARDED = re.compile(r'rg_(?:run|is_complete)\s+"([^"]+)"')
_VAR_DEF = re.compile(r'^\s*(\w+)=["\']?([^"\'\s|;#]+)["\']?\s*$', re.M)
# Anything that varies per unit becomes the glob wildcard. SLURM_ARRAY_TASK_ID is the common one;
# single-letter loop variables (${T}, ${i}) are the other. The alternation must match the WHOLE
# name -- an earlier version allowed `\$\{?([A-Za-z])\}?`, whose optional brace let `${OUTDIR}`
# match as `${O` and emit the glob `*UTDIR}`. A wildcard that eats a directory name silently
# widens the family, which is worse than failing to resolve it.
_PER_UNIT = re.compile(
    r'\$\{(?:SLURM_ARRAY_TASK_ID|SLURM_JOB_ID|SLURM_PROCID|[A-Za-z]|idx|seed|tag)\}'
    r'|\$(?:SLURM_ARRAY_TASK_ID|SLURM_JOB_ID|SLURM_PROCID)(?![A-Za-z0-9_])')


def expand(value, env, depth=0):
    if depth > 6:
        return value
    out = re.sub(r'\$\{(\w+)\}|\$(\w+)',
                 lambda m: env.get(m.group(1) or m.group(2), m.group(0)), value)
    return expand(out, env, depth + 1) if out != value else out


def families(root):
    resolved, unresolved = {}, []
    scripts = [p for p in glob.glob(os.path.join(root, "**", "*.sh"), recursive=True)
               if "/lib/" not in p and "/.git/" not in p]
    for path in sorted(scripts):
        try:
            text = open(path, errors="replace").read()
        except OSError:
            continue
        targets = _GUARDED.findall(text)
        if not targets:
            continue
        env = dict(_VAR_DEF.findall(text))
        rel = os.path.relpath(path, root)
        for raw in targets:
            got = expand(raw, env)
            pattern = _PER_UNIT.sub("*", got)
            pattern = re.sub(r'\*{2,}', "*", pattern)
            if "$" in pattern:                      # still carries an unresolved variable
                unresolved.append((rel, raw, pattern, "variable not assigned in this file"))
                continue
            ext = os.path.splitext(pattern)[1].lower()
            validator = {".root": "root", ".npz": "npz"}.get(ext)
            if validator is None:
                unresolved.append((rel, raw, pattern,
                                   f"no validator for extension {ext or '(none)'} -- do NOT use "
                                   "--validator size"))
                continue
            resolved.setdefault((validator, pattern), set()).add(rel)
    return resolved, unresolved


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--root", default=os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    ap.add_argument("--unresolved", action="store_true", help="print only the unresolved targets")
    a = ap.parse_args()

    resolved, unresolved = families(a.root)

    if not a.unresolved:
        print("# Step 0b backfill families, derived from the launchers' own resume guards.")
        print("# --dry-run FIRST, always, and READ THE FAIL LIST -- anything that fails validation")
        print("# is left unmarked and will be regenerated. That list is the population of hidden")
        print("# partials, and it is the first time this repo can enumerate it.")
        print(f"# {len(resolved)} families from {sum(len(v) for v in resolved.values())} guard sites.\n")
        for (validator, pattern), srcs in sorted(resolved.items()):
            print(f"# <- {', '.join(sorted(srcs))}")
            print(f"$MNV_REPO/lib/backfill_completion_markers.sh --dry-run --validator {validator} "
                  f"--glob '{pattern}'")

    if unresolved:
        print(f"\n*** {len(unresolved)} UNRESOLVED -- these are families too, and this tool "
              f"cannot name them ***", file=sys.stderr)
        print("Resolve each by hand before Step 0b; an unlisted family is one that silently "
              "re-runs.\n", file=sys.stderr)
        for rel, raw, pattern, why in unresolved:
            print(f"  {rel}\n      target {raw!r} -> {pattern!r}\n      {why}", file=sys.stderr)

    if len(resolved) < FAMILY_FLOOR:
        print(f"\n*** FAMILY COLLECTOR WENT BLIND ***\n"
              f"  resolved {len(resolved)} families, expected at least {FAMILY_FLOOR}.\n"
              f"  Either guards were deleted or the launchers changed idiom. Do NOT lower the\n"
              f"  floor to make this pass -- an unenumerated family is one Step 0b will miss.",
              file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())

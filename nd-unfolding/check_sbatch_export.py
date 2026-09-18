#!/usr/bin/env python3
"""Refuse an `sbatch` command whose `--export` would silently truncate a value.

WHY THIS EXISTS. Job `58507305` COMPLETED in 54 s, exit 0, verdict `MEASURED`, and measured nothing
about its own subject. `--export` takes a **comma-separated list of `NAME=VALUE`**, so the commas
inside `MNV_THREAD_GRID=1\\,2\\,4\\,8` split the LIST -- backslash escaping does not survive the
shell -- and the variable arrived as `1`. Every cell then ran at one thread and the invariance claim
was arithmetically correct over a population of one.

**Slurm was not wrong.** It did exactly what its documentation says. The defect was in the command I
wrote, which is why this checks the COMMAND and not the scheduler.

It is a pre-submission gate, so it costs nothing and runs before an allocation exists. The
in-job refusal in `run_determinism_probe.sh` (rc 14) is the second line of defence, not the first:
by the time that fires, a node has been assigned.

⚠ WHAT IT CANNOT SEE. A value legitimately containing a comma has no safe spelling here at all --
the answer is `--export-file` or `--wrap`, not better quoting. This tool says "that value will not
survive", never "here is how to escape it".
"""
import argparse
import re
import shlex
import sys

# `ALL`, `NONE`, `NIL` and bare NAME (export the current value) are list ITEMS, not assignments.
_BARE = re.compile(r"^[A-Za-z_][A-Za-z_0-9]*$")


def split_export_items(value):
    """The list as Slurm splits it: on commas, unconditionally."""
    return [item for item in value.split(",")]


def findings(argv_tokens):
    """`[(name, kept, dropped)]` for every assignment a comma would truncate.

    The reconstruction is the point: Slurm splits the whole `--export` value on commas, so an
    assignment is truncated exactly when the item after it is NOT itself an assignment or a
    recognised bare name. Those orphan items are the tail that was lost.
    """
    out = []
    for token in _export_values(argv_tokens):
        items = split_export_items(token)
        i = 0
        while i < len(items):
            item = items[i]
            if "=" not in item:
                i += 1
                continue
            name, kept = item.split("=", 1)
            dropped = []
            j = i + 1
            while j < len(items):
                nxt = items[j]
                if "=" in nxt or _BARE.fullmatch(nxt) or nxt in ("ALL", "NONE", "NIL"):
                    break
                dropped.append(nxt)
                j += 1
            if dropped:
                out.append((name, kept, dropped))
            i = j if dropped else i + 1
    return out


def _export_values(argv_tokens):
    for index, token in enumerate(argv_tokens):
        if token.startswith("--export="):
            yield token[len("--export="):]
        elif token == "--export" and index + 1 < len(argv_tokens):
            yield argv_tokens[index + 1]


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    src = ap.add_mutually_exclusive_group(required=True)
    src.add_argument("--command", help="the full sbatch command line, as one string")
    src.add_argument("--command-file", help="a file holding it")
    a = ap.parse_args()
    text = a.command if a.command else open(a.command_file).read()
    tokens = shlex.split(text)
    if not any(t == "sbatch" or t.endswith("/sbatch") for t in tokens):
        print("[FAIL] this does not look like an sbatch command; no `sbatch` token found",
              file=sys.stderr)
        return 2
    bad = findings(tokens)
    if not bad:
        n = sum(1 for _ in _export_values(tokens))
        print(f"OK: {n} --export value(s) checked; no assignment would be truncated by comma "
              f"splitting.")
        return 0
    print("[REFUSED] these --export assignments would be TRUNCATED by comma splitting:",
          file=sys.stderr)
    for name, kept, dropped in bad:
        print(f"   {name} would arrive as {kept!r}; DROPPED: {dropped}", file=sys.stderr)
    print("   Slurm splits the whole --export value on commas and backslash escaping does not",
          file=sys.stderr)
    print("   survive the shell. Use a different separator inside the value, or --export-file.",
          file=sys.stderr)
    return 1


if __name__ == "__main__":
    raise SystemExit(main())

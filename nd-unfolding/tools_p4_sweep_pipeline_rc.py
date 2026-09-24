#!/usr/bin/env python3
"""Mechanical sweep for BEN-035's pipeline exit-status trap, across every tracked shell file.

The trap: in `cmd | tail -1`, `$?` and the surrounding `if`/`&&` see the exit status of the LAST
element of the pipeline, not of `cmd`. So a failing command piped to tail/head/grep reports
SUCCESS. Five instances now, the most recent of them inside the self-check script written to
catch gates that cannot fail -- which is why this is a re-runnable tool rather than a pass
somebody performed.

Three shapes are flagged:
  A. `if <pipeline through tail/head/grep> ; then`      -- condition tests the wrong command
  B. `<pipeline> && ...` / `<pipeline> || ...`          -- same, in a boolean chain
  C. `<pipeline>` immediately followed by `rc=$?`       -- captures the wrong status

Not flagged, and deliberately: a bare pipeline whose status is never consumed -- including one in
an `if` BODY (`if command -v X; then X | cut`) and one whose status is discarded by `|| true` --
and an operator whose left operand is not the pipeline (`[ -f x ] && echo yes`). A pipeline under
`set -o pipefail`, where the FIRST failing element propagates, is still counted, but pipefail
changes the semantics, so the report states per-file whether it is set.
"""
import re
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
FILTERS = r"(?:tail|head|grep|cut|sed|awk|wc|sort|uniq|tee|xargs)"
PIPE_TO_FILTER = re.compile(rf"\|\s*{FILTERS}\b")
RC_CAPTURE = re.compile(r"^\s*(?:local\s+)?\w+=\$\?|^\s*rc=\$\?")
IF_HEAD = re.compile(r"^\s*(?:el)?if\b")
THEN = re.compile(r";\s*then\b")
BOOL_OP = re.compile(r"&&|\|\|")
# Where a command's left operand begins: a list separator, an opening group or substitution,
# or a compound-command keyword. The operator binds only the text after the last of these.
# `(`/`{` count only as a subshell/group opener (at line start or after whitespace/`;`), so the
# braces and parens inside an awk program do not truncate the operand and hide its pipe.
SEGMENT_START = re.compile(r";|&&|\|\||\$\(|<\(|(?:^|(?<=[\s;]))\(|(?:^|(?<=[\s;]))\{(?=\s)"
                           r"|`|\bthen\b|\bdo\b|\belse\b")
# `|| true` / `|| :` DISCARDS the status: nothing reads it, so it cannot read the wrong command's.
DISCARD = re.compile(r"\s*(?:true|:)\s*(?:$|[;)}`\"'])")


def _condition(line):
    """The text of an `if`/`elif` CONDITION on this line, or None.

    Only the condition is a status read. `if command -v X; then X "$1" | cut -f1` pipes in the
    BODY, whose status nothing tests -- flagging it was the output-capture false positive that
    took `submit_z_pilot_a5.sh` and `lib_mnv_env_preflight.sh` live (HANDOFF-20260921 4a)."""
    head = IF_HEAD.match(line)
    then = THEN.search(line)
    if head:
        return line[head.end():then.start() if then else len(line)]
    if then:  # `; then` closing a condition begun on an earlier line
        return line[:then.start()]
    return None


def _chain_reads_a_pipeline(line):
    """True iff some `&&`/`||` on this line has a filter pipeline as its LEFT operand and does
    not discard the status. `[ -f x ] && echo yes`, followed later on the line by `a | cut`, is
    not the trap: the operator reads the test, not the pipeline."""
    for m in BOOL_OP.finditer(line):
        left = SEGMENT_START.split(line[:m.start()])[-1]
        if not PIPE_TO_FILTER.search(left):
            continue
        if m.group() == "||" and DISCARD.match(line[m.end():]):
            continue
        return True
    return False


def tracked_shell_files():
    out = subprocess.check_output(["git", "ls-files", "*.sh"], cwd=REPO, text=True)
    return sorted(p for p in out.splitlines() if p.strip())


def scan(rel):
    path = REPO / rel
    try:
        lines = path.read_text(errors="replace").splitlines()
    except Exception:
        return [], False
    return scan_lines(lines)


def scan_lines(lines):
    """`scan` over already-read lines, so the matcher is testable on fixtures in both directions."""
    pipefail = any(re.search(r"set\s+-o\s+pipefail|set\s+-[a-z]*o[a-z]*\s+pipefail", l)
                   for l in lines if not l.lstrip().startswith("#"))
    hits = []
    for i, line in enumerate(lines, 1):
        if line.lstrip().startswith("#"):
            continue
        if not PIPE_TO_FILTER.search(line):
            # shape C can span two lines: pipeline then rc=$?
            continue
        shape = None
        cond = _condition(line)
        if cond is not None and PIPE_TO_FILTER.search(cond):
            shape = "A: if-condition"
        elif _chain_reads_a_pipeline(line):
            shape = "B: boolean chain"
        nxt = lines[i] if i < len(lines) else ""
        if RC_CAPTURE.match(nxt):
            shape = (shape + " + C: rc=$?") if shape else "C: rc=$? after pipeline"
        if shape:
            hits.append((i, shape, line.strip()[:96]))
    return hits, pipefail


def summary():
    """Machine-readable snapshot of what this sweep currently finds.

    REPAIR-7 item 4: the committed inventory drifted to 66 fields / 22 gates while the generator
    reported 82 / 24 -- the artifact went stale against its own generator INSIDE one round, which
    is precisely the failure the artifact was created to prevent. A prose document cannot be
    diffed against a script, so the script now emits this, the snapshot is committed, and a test
    compares them. Staleness becomes a test failure instead of a verifier finding."""
    files = tracked_shell_files()
    total = 0
    per_file = {}
    for rel in files:
        hits, pf = scan(rel)
        if hits:
            total += len(hits)
            per_file[rel] = {"pipefail": pf, "hits": len(hits)}
    return {"tool": "tools_p4_sweep_pipeline_rc",
            "n_shell_files": len(files), "n_candidates": total,
            "files_with_candidates": per_file,
            "live_instances": sum(v["hits"] for v in per_file.values() if not v["pipefail"])}


def main():
    files = tracked_shell_files()
    total = 0
    print(f"{'file':<52} {'pipefail':<9} hits")
    print("-" * 96)
    detail = []
    for rel in files:
        hits, pf = scan(rel)
        if hits:
            total += len(hits)
            print(f"{rel:<52} {'yes' if pf else 'NO':<9} {len(hits)}")
            detail.append((rel, pf, hits))
    if not detail:
        print("(no instances found)")
    print()
    for rel, pf, hits in detail:
        print(f"=== {rel}   (pipefail: {'yes' if pf else 'NO'}) ===")
        for ln, shape, text in hits:
            print(f"  {rel}:{ln}  [{shape}]")
            print(f"      {text}")
    print()
    print(f"TOTAL: {total} candidate instance(s) across {len(files)} tracked shell files")
    print("NOTE: `pipefail: yes` means the FIRST failing element propagates, so the shape is")
    print("      usually benign there; `NO` means the trap is live. Verify before editing.")
    return 0


if __name__ == "__main__":
    sys.exit(main())

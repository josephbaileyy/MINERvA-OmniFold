#!/usr/bin/env python3
"""Run a launcher with `python3`/`sbatch` stubbed and assert the OBSERVED argv, per branch.

WHY THIS EXISTS, and it is a specific failure rather than a general principle. The M(ii) offset hook
was verified by three checks and all three passed on a launcher that could not execute its majority
branch:

    assert_offset_hook_present   read the TEXT      -- "$MNV_EST_SEED_OFFSET appears in the file"
    archive_expansion            read the ASSIGNMENT -- `s.startswith("EST_SEED=$((")` on a STRIPPED
                                                       line, so nesting is invisible BY CONSTRUCTION
    the k=0 anchor control       read that assignment's arithmetic -- 1000 + 0 = 1000, "archive
                                                       reproduced", on a launcher that dies at start

**ALL THREE READ THE ASSIGNMENT. NONE READ THE USE. The bug lived between them** -- one blind spot
three times, not three blind spots. In `sbatch_uthrow_block_5d.sh` the assignment sat at COLUMN 0
INSIDE a `then` block, so the `else` branch expanded `${EST_SEED}` to nothing and every `T != 0` task
died with `argument --estimator-seed: expected one argument`.

**INDENTATION IS NOT SCOPE.** Column 0 inside an indented block is legal bash and reads as top level,
which is why a reachability heuristic keyed on indentation cleared it. Only a block counter flagged it
and only an argv reproduction proved it.

So this module does the only thing that could have caught it: it EXECUTES the launcher with the real
bash, with the commands stubbed, and looks at what the arguments actually were -- for every branch the
launcher can take. No cluster, no ROOT, no allocation.
"""
from __future__ import annotations

import os
import re
import shutil
import subprocess
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))

_STUB = """#!/bin/sh
printf 'ARGV'
for a in "$@"; do printf '\\t%s' "$a"; done
printf '\\n'
exit 0
"""

_PREAMBLE = """
# Neutralise the helpers a compute node would provide, so the launcher's OWN control flow is what
# runs. NOTE: `source` and `.` are deliberately NOT overridden -- the first version of this probe
# defined `.() { :; }` and then invoked the launcher with `.`, so the launcher never executed and the
# probe reported "no argv observed" for both branches. It looked like the launcher was broken in a
# new way; it was the instrument. Environment-setup lines are neutralised by TEXT SUBSTITUTION in
# `_prepare` instead, which touches no conditional.
set +e
module() { :; }
rg_skip_if_complete() { return 1; }   # never skip: the command under test must be reached
rg_run() { shift; "$@"; }             # drop the output-path argument, run the rest
srun() { while [ $# -gt 0 ]; do case "$1" in -*) shift;; [0-9]*) shift;; *) break;; esac; done; "$@"; }
"""


# ANY `source`/`.` of a path the local checkout does not have -- setup_salloc_env.sh, lib/resume_guard.sh,
# and whatever the next launcher adds. Keyed on the syntax, not on a filename list: the first version
# named `setup_salloc_env.sh` only, so `source "${REPO}/lib/resume_guard.sh"` still ran, `set -e` aborted
# the script, and TWO launchers reported "no command reached" -- indistinguishable from a real
# reachability bug. A hardcoded exception list is a population claim about files that do not exist yet.
_SOURCES_ABSENT = re.compile(r'(^|;)\s*(source|\.)\s+"?\$\{?REPO\}?/')


def _prepare(text):
    """Neutralise ONLY environment setup and `#SBATCH`, never a conditional.

    Substitution is line-wise and confined to: `source .../setup_salloc_env.sh`, `cd <abs path>`,
    and `mkdir -p ...`. Everything that selects a branch or builds a command line is left exactly as
    written, because that is the thing under test.
    """
    out = []
    for line in text.split("\n"):
        s = line.strip()
        if s.startswith("#!") or s.startswith("#SBATCH"):
            out.append("# " + s)
            continue
        # A line that sources the cluster env, possibly compound:
        #   REPO="..."; source "${REPO}/setup_salloc_env.sh"      <- keep the assignment, drop the source
        #   source "${REPO}/setup_salloc_env.sh"                  <- drop the whole line
        # THE FIRST VERSION KEPT ONLY `line.split(";")[0]`, which on a line whose source clause comes
        # FIRST returned the source clause itself -- so the probe sourced a nonexistent file, `set -e`
        # aborted the script, and every case reported "no command reached". That looked exactly like a
        # reachability defect in the launcher. Segment-wise now, so an assignment is kept and only the
        # sourcing segment is dropped.
        if _SOURCES_ABSENT.search(line):
            kept = [seg for seg in line.split(";") if not _SOURCES_ABSENT.search(seg)]
            out.append(("; ".join(s.strip() for s in kept if s.strip()) + "   ") if kept else ""
                       + "# setup sourced-out by the argv probe")
            continue
        if re.match(r'^\s*export [A-Z_]+=\S+; cd ', line) or re.match(r'^\s*cd "\$\{?REPO', line):
            out.append("# " + s + "   # cd neutralised by the argv probe")
            continue
        if re.match(r'^\s*mkdir -p ', line):
            out.append("# " + s + "   # mkdir neutralised by the argv probe")
            continue
        out.append(line)
    return "\n".join(out)


_BRANCH = re.compile(r'^\s*(if|elif|else)\b')


def branch_count(launcher_text):
    """How many distinct control-flow branches the launcher's commands can sit in.

    Used for NON-VACUITY: a probe that exercises fewer cases than there are branches has not
    checked the launcher, and reporting it as clean is the `touched > 0` hole again.
    """
    n = 0
    for line in launcher_text.split("\n"):
        s = line.strip()
        if s.startswith("#"):
            continue
        if _BRANCH.match(line):
            n += 1
    return n


def observed_argv(launcher, env):
    """Every stubbed-command argv the launcher produces under `env`. Real bash, real control flow."""
    path = os.path.join(HERE, launcher)
    if not os.path.exists(path):
        raise SystemExit(f"[FAIL] launcher not found: {launcher}")
    with open(path, encoding="utf-8") as fh:
        prepared = _prepare(fh.read())
    tmp = tempfile.mkdtemp(prefix="argvprobe.")
    try:
        for name in ("python3", "python", "sbatch"):
            q = os.path.join(tmp, name)
            with open(q, "w", encoding="utf-8") as fh:
                fh.write(_STUB)
            os.chmod(q, 0o755)
        pre = os.path.join(tmp, "preamble.sh")
        with open(pre, "w", encoding="utf-8") as fh:
            fh.write(_PREAMBLE)
        script = os.path.join(tmp, "under_test.sh")
        with open(script, "w", encoding="utf-8") as fh:
            fh.write(prepared)
        e = dict(os.environ)
        e["PATH"] = tmp + os.pathsep + e.get("PATH", "")
        e.update({k: str(v) for k, v in env.items()})
        r = subprocess.run(["bash", "-c", f'source "{pre}"; source "{script}"'],
                           capture_output=True, text=True, env=e, cwd=HERE, timeout=120)
        rows = []
        for line in (r.stdout or "").split("\n"):
            if line.startswith("ARGV\t"):
                rows.append(line.split("\t")[1:])
        return rows
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def flag_values(argv_rows, flag):
    """Every value observed for `flag`, plus a sentinel for a flag left with NO value.

    A flag whose value vanished is the failure mode here, so it is represented rather than dropped:
    the next token is another flag, or the argv ends.
    """
    out = []
    for row in argv_rows:
        for i, tok in enumerate(row):
            if tok != flag:
                continue
            nxt = row[i + 1] if i + 1 < len(row) else None
            out.append(nxt if (nxt is not None and not nxt.startswith("--")) else "<MISSING>")
    return out


def assert_estimator_seed_is_an_integer_in_every_branch(launcher, cases, expect=None):
    """FAIL CLOSED unless every case yields at least one `--estimator-seed <int>` and none is missing.

    `cases` is a list of env dicts, one per branch to exercise. `expect`, if given, is the integer
    every observation must equal.
    """
    with open(os.path.join(HERE, launcher), encoding="utf-8") as fh:
        text = fh.read()
    nb = branch_count(text)
    if len(cases) < max(1, nb):
        raise SystemExit(
            f"[FAIL] {launcher}: {len(cases)} probe case(s) for {nb} branch(es). A probe that "
            "exercises fewer cases than the launcher has branches has not checked the launcher, and "
            "reporting it clean is the same vacuity as a search that matched nothing.")
    problems = []
    seen_any = False
    for env in cases:
        # A case may declare that it legitimately runs no command -- e.g. this launcher's array is
        # 1-BASED (`sed -n "${SLURM_ARRAY_TASK_ID}p"`), so task 0 reads an empty universe and exits 0
        # by design. That is not a branch that passes a bad seed; it is a branch with no command, and
        # conflating the two would make the probe fire on correct code. Declared per case rather than
        # inferred, so "no command observed" is never silently excused.
        expect_cmd = env.pop("_expect_command", True)
        rows = observed_argv(launcher, env)
        vals = flag_values(rows, "--estimator-seed")
        if not vals:
            if not expect_cmd:
                continue
            problems.append(f"{launcher} {env}: no --estimator-seed reached a command at all")
            continue
        for v in vals:
            seen_any = True
            if v == "<MISSING>":
                problems.append(f"{launcher} {env}: --estimator-seed present with NO VALUE "
                                "(the variable was unset on this branch)")
            elif not re.fullmatch(r"-?\d+", v):
                problems.append(f"{launcher} {env}: --estimator-seed={v!r} is not an integer")
            elif expect is not None and int(v) != int(expect):
                problems.append(f"{launcher} {env}: --estimator-seed={v} != expected {expect}")
    if not seen_any:
        problems.append(f"{launcher}: no --estimator-seed observed in any case; the probe proved nothing")
    if problems:
        raise SystemExit("[FAIL] observed-argv probe:\n  " + "\n  ".join(problems))
    return True

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
_SOURCE_LINE = re.compile(r'(^|;)\s*(source|\.)\s+"?\$\{?REPO\}?/(?P<rel>[^"\s;]+)')

# REPO IS REMAPPED, NOT STRIPPED. The first version neutralised every `${REPO}/...` source, which was
# fine until a launcher started sourcing a file that MUST run for it to work -- `lib_member_resume.sh`.
# Stripping it left mr_require_valid_offset undefined, `set -e` killed every launcher at line 1, and
# the probe reported ZERO argv for all seven. That is indistinguishable from a reachability defect in
# the launchers, and it is the third time this probe's own environment handling has produced a false
# negative. So: point REPO at the local checkout so real files resolve for real, and neutralise only
# the sources that still do not exist here.
_LOCAL_REPO = os.path.abspath(os.path.join(HERE, ".."))


def _source_resolves(rel):
    return os.path.exists(os.path.join(_LOCAL_REPO, rel))


def _prepare(text):
    """Neutralise ONLY environment setup and `#SBATCH`, never a conditional.

    Substitution is line-wise and confined to: `source .../setup_salloc_env.sh`, `cd <abs path>`,
    and `mkdir -p ...`. Everything that selects a branch or builds a command line is left exactly as
    written, because that is the thing under test.
    """
    # REPOINT THE LAUNCHER'S OWN `REPO=` ASSIGNMENT AT THIS CHECKOUT, AS A WHOLE-TEXT SUBSTITUTION
    # BEFORE the per-line walk. Setting REPO in the child ENVIRONMENT is not enough: every launcher
    # reassigns it to the cluster path on its first executable line, so the env value was overwritten
    # before any source ran and every ${REPO}-relative source resolved to /pscratch -- the function
    # libraries the launcher depends on never loaded and the probe reported zero argv for all seven,
    # indistinguishable from a reachability defect.
    #
    # AND IT MUST HAPPEN HERE RATHER THAN IN A PER-LINE BRANCH. A per-line branch handled the REPO
    # line and `continue`d, which BYPASSED the source-wrapping branch below -- so setup_salloc_env.sh
    # ran unprotected, conda failed, and `set -e` killed the script. Same defect one layer in.
    #
    # Five attempts on this harness before it worked, and the diagnosis was blocked by my own
    # `2>/dev/null` on the wrapper, which was suppressing the `bash -x` trace I was reading:
    # THE DIAGNOSTIC WAS SILENCING THE EVIDENCE IT WAS FOR.
    text = re.sub(r'REPO=("|\')?/pscratch/[^"\'\s;]*("|\')?', f'REPO="{_LOCAL_REPO}"', text)

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
        # TOLERANT SOURCING, criterion-free. Existence was the wrong test: setup_salloc_env.sh EXISTS
        # in the checkout and still cannot run here (it activates a cluster conda env), so "neutralise
        # what is absent" left it running and `set -e` killed every launcher -- zero argv for all
        # seven, again. And a hardcoded name list is the population claim I already rejected once.
        # So every ${REPO}-relative source becomes best-effort: a function LIBRARY the launcher
        # depends on loads for real, an environment ACTIVATOR fails harmlessly, and neither the probe
        # nor a future launcher has to declare which is which.
        m = _SOURCE_LINE.search(line)
        if m:
            kept = []
            for seg in line.split(";"):
                if _SOURCE_LINE.search(seg):
                    # STRIP THE TRAILING COMMENT BEFORE WRAPPING. The first version wrapped the
                    # segment verbatim, so a line like
                    #     source "${REPO}/lib/resume_guard.sh"   # BEN-023: resume on a marker
                    # became `{ source ... # BEN-023: ... ; } 2>/dev/null || true` -- the comment
                    # swallowed the CLOSING BRACE, the group never closed, bash exited 1 and the probe
                    # reported zero argv for all seven launchers. That is the same swallow-the-rest-of-
                    # the-line class as the continuation defect this project has a lint for, committed
                    # in the probe's own text generator, which the lint does not cover because it walks
                    # TRACKED files and this text is synthesised at run time.
                    bare = re.sub(r'\s+#.*$', '', seg.strip())
                    kept.append(f"{{ {bare} ; }} 2>/dev/null || true")
                elif seg.strip():
                    kept.append(seg.strip())
            out.append("; ".join(kept) if kept else ": # nothing to keep")
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
        e["REPO"] = _LOCAL_REPO          # so ${REPO}-relative sources resolve against this checkout
        e["ND"] = HERE
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


# ===================================================================================================
# NATIVE (CLUSTER) MODE -- ruling (a). NO TEXT TRANSFORMATION AT ALL.
#
# The `_prepare` transformation above exists ONLY because a local checkout cannot resolve
# ${REPO}=/pscratch, cannot run setup_salloc_env.sh (it activates a cluster conda env), and is
# overridden anyway because every launcher REASSIGNS REPO on its first executable line. Six successive
# fixes each MOVED the failure rather than removing it, which is the signature of a design problem.
# On the cluster none of those three conditions holds, so the transformation is deleted rather than
# repaired.
#
# READ-ONLY ONLY IF THE STUB GATE PASSES -- AND THE EARLIER VERSION OF THIS PARAGRAPH WAS FALSE.
# It said "read-only by construction". It was not: the PATH shims were displaced by the launchers' own
# `conda activate` and a REAL bootstrap_nd.py unfold ran on a login node, twice. The claim is now
# CONDITIONAL on `assert_stubs_survive_activation` passing, which is checked AFTER sourcing the
# activator and aborts every launcher if any stub was displaced. "By construction" was the wrong
# phrase for a property that depended on an environment I had never run in.
#   python3 / python / sbatch / srun   stubbed AS SHELL FUNCTIONS, gate-verified after activation
#   mkdir                     stubbed -> NO member directories created under the canonical namespaces
#   rg_run / mr_run           stubbed to exec the command only -> rg_begin's `rm -f marker` NEVER runs,
#                                                                 no .done marker is written
#   rg_skip_if_complete / mr_skip_if_complete   LEFT REAL -- they only READ
#
# WHAT NATIVE MODE THEREFORE DOES NOT COVER, stated so it cannot be mistaken for coverage: because
# rg_run/mr_run are stubbed, this does not exercise marker writing or the SKIP and HARD-FAILURE resume
# regimes. Those are verified separately and independently by the three-regime bash test of
# lib_member_resume.sh, which does not use this probe at all.
# ===================================================================================================
# THE STUB MECHANISM. READ THIS BEFORE CHANGING IT.
#
# THIS PROBE RAN A REAL UNFOLD ON A LOGIN NODE, TWICE, WHILE ITS DOCSTRING SAID "python3/sbatch stubbed
# -> no real work, no job submitted" AND ITS AUTHOR SAID IN WRITING "read-only by construction, not by
# intention". Both claims were TRUE LOCALLY AND FALSE ON THE CLUSTER, which is the only environment it
# is meant to run in. An orphaned bootstrap_nd.py survived a first kill and ran ~15 minutes.
#
# THE MECHANISM, demonstrated rather than reasoned about:
#   PATH SHIM      displaced. Every launcher's first executable line sources setup_salloc_env.sh,
#                  which runs `conda activate`, which PREPENDS the env's bin to PATH -- in front of
#                  the shim dir. From that line onward python3, python AND sbatch are the real ones.
#   SHELL FUNCTION survives. A function takes precedence over any PATH lookup, and prepending to PATH
#                  does not touch it. Verified directly, both directions.
#
# SO: A STUB THAT A `conda activate` CAN DISPLACE IS NOT A STUB. Everything is a shell function now.
# The PATH shim is kept as a SECOND, ORDER-INDEPENDENT layer, not as the mechanism.
#
# AND NOTHING WAS CONTAMINATED ONLY BY LUCK: `mkdir` happened to be implemented as a function, so the
# member directory never existed and the real unfold's write had nowhere to land. The stub that saved
# the canonical tree is the one that happened to use the surviving mechanism.
#
# sbatch WAS UNSTUBBED. Nothing submitted only because these seven launchers do not invoke sbatch
# internally. The safety rested on that accident. Pointed at a launcher that submits, it would have
# submitted from an instrument everyone was calling read-only.
_STUB_COMMANDS = ("python3", "python", "sbatch", "srun")

_NATIVE_PREAMBLE = """
set +e
_ARGV_SENTINEL="__SENTINEL__"
_argvprobe_emit() {
  printf 'ARGV'; for _a in "$@"; do printf '\t%s' "$_a"; done; printf '\n'
  printf 'x' >> "$_ARGV_SENTINEL"
}
# EVERY intercepted command is a SHELL FUNCTION, because a PATH shim does not survive the env
# activation these launchers perform on their first executable line.
python3() { _argvprobe_emit "$@"; }
python()  { _argvprobe_emit "$@"; }
sbatch()  { _argvprobe_emit "$@"; }
srun()    { while [ $# -gt 0 ]; do case "$1" in -*) shift;; [0-9]*) shift;; *) break;; esac; done; "$@"; }
module()  { :; }
mkdir()   { :; }                     # no writes into canonical namespaces
rg_run()  { shift; "$@"; }           # no rg_begin, so no marker removed or written
mr_run()  { shift; "$@"; }
export -f python3 python sbatch srun module mkdir rg_run mr_run _argvprobe_emit 2>/dev/null || true
"""

#: Sourced by the gate below to prove the stubs survive whatever the launchers source.
_GATE_TEMPLATE = """
source "__PRE__"
REPO="__REPO__"
{ source "${REPO}/setup_salloc_env.sh" ; } >/dev/null 2>&1 || true
for _c in __CMDS__; do
  printf 'GATE\t%s\t%s\n' "$_c" "$(type -t "$_c" 2>/dev/null || echo MISSING)"
done
"""


def assert_stubs_survive_activation(repo):
    """SOURCE THE ACTIVATOR FIRST, THEN CHECK. Refuse to run anything if a stub did not survive.

    This is the check whose absence let a real unfold run: the harness asserted its stubs at
    definition time and never at USE time, and the displacement happens in between. Ordering is the
    whole content of the check -- asserting before the activator runs proves nothing.
    """
    tmp = tempfile.mkdtemp(prefix="argvgate.")
    try:
        pre = os.path.join(tmp, "pre.sh")
        with open(pre, "w", encoding="utf-8") as fh:
            fh.write(_NATIVE_PREAMBLE.replace("__SENTINEL__", os.path.join(tmp, "sentinel")))
        script = _GATE_TEMPLATE.replace("__PRE__", pre).replace("__REPO__", repo)                                .replace("__CMDS__", " ".join(_STUB_COMMANDS))
        r = subprocess.run(["bash", "-c", script], capture_output=True, text=True, timeout=300)
        got = {}
        for line in (r.stdout or "").split("\n"):
            if line.startswith("GATE\t"):
                _, name, kind = line.split("\t")
                got[name] = kind
        bad = [c for c in _STUB_COMMANDS if got.get(c) != "function"]
        if bad or len(got) != len(_STUB_COMMANDS):
            raise SystemExit(
                "[FAIL] STUB GATE: after sourcing the launchers' own environment activator, these "
                f"commands are NOT the probe's stubs: {bad or 'gate produced no output'}\n"
                f"        observed: {got}\n"
                "        A stub that the activation displaces is not a stub. Refusing to run any "
                "launcher: this is the exact condition under which this probe previously executed a "
                "REAL unfold on a login node while reporting itself read-only.")
        return got
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def observed_argv_native(launcher, env, repo):
    """Run the launcher AS WRITTEN under stubs. No `_prepare`, no substitutions."""
    path = os.path.join(repo, "nd-unfolding", launcher)
    if not os.path.exists(path):
        raise SystemExit(f"[FAIL] launcher not found on the cluster: {path}")
    tmp = tempfile.mkdtemp(prefix="argvprobe.")
    try:
        # PATH shims kept as a SECOND, order-independent layer -- not the mechanism. The mechanism is
        # the shell functions in the preamble, which survive the activation that displaces PATH.
        for name in _STUB_COMMANDS:
            q = os.path.join(tmp, name)
            with open(q, "w", encoding="utf-8") as fh:
                fh.write(_STUB)
            os.chmod(q, 0o755)
        sentinel = os.path.join(tmp, "sentinel")
        pre = os.path.join(tmp, "pre.sh")
        with open(pre, "w", encoding="utf-8") as fh:
            fh.write(_NATIVE_PREAMBLE.replace("__SENTINEL__", sentinel))
        e = dict(os.environ)
        e["PATH"] = tmp + os.pathsep + e.get("PATH", "")
        e.update({k: str(v) for k, v in env.items()})
        r = subprocess.run(["bash", "-c", f'source "{pre}"; source "{path}"'],
                           capture_output=True, text=True, env=e,
                           cwd=os.path.join(repo, "nd-unfolding"), timeout=600)
        rows = [ln.split("\t")[1:] for ln in (r.stdout or "").split("\n") if ln.startswith("ARGV\t")]
        # THE SENTINEL DISTINGUISHES "no command reached" FROM "a command ran unstubbed". Without it,
        # an unstubbed run is indistinguishable from a quiet one until someone notices it took fifteen
        # minutes -- which is how a real unfold got to run twice.
        stub_fired = os.path.exists(sentinel) and os.path.getsize(sentinel) > 0
        return rows, r.returncode, (r.stderr or ""), stub_fired
    finally:
        shutil.rmtree(tmp, ignore_errors=True)



def member_root_for(offset):
    """`mii/member_kNNNNNN` for this offset -- the string a member-scoped path must START WITH."""
    k = int(offset)
    name = f"member_kneg{-k:06d}" if k < 0 else f"member_k{k:06d}"
    return f"{os.environ.get('MII_CONTAINER', 'mii')}/{name}"


def is_member_scoped(path, offset):
    """SHAPE, NOT SUBSTRING. Returns (ok, reason).

    THE DEFECT THIS REPLACES, found by the mediator and it invalidated a probe pass:

        member = [o for o in outs if "member_k" in str(o)]        # launcher_argv_probe.py:452

    `"member_k" in str(o)` is TRUE OF BOTH PATH SHAPES --
        uq_5d/block_slabs_5d_sb/member_k001200/x.npz    namespace-then-member  (the OLD shape)
        mii/member_k001200/uq_5d/block_slabs_5d_sb/x.npz  member-root-first     (the NEW shape)
    -- so the probe re-run C ORDERED SPECIFICALLY TO CONFIRM MEMBER-ROOT-FIRST COULD NOT DISTINGUISH IT
    FROM WHAT IT REPLACED, and it returned byte-for-byte the same summary as the pre-change run. The
    identity of the two summaries was the evidence.

    A SUBSTRING TEST CANNOT EXPRESS A POSITIONAL REQUIREMENT. That is the general form, and it is why
    the remedy is `startswith` on a computed root rather than a longer regex: the requirement is "the
    member root comes FIRST", and containment is the one relation that is blind to order. Compare
    `BEN-482`, where a substring could not express "this is a call, not prose"; the family is
    text-matching a claim the text cannot carry.

    Absolute paths are anchored after the LAST `/nd-unfolding/`, matching `_mr_insert`.
    """
    root = member_root_for(offset)
    s = str(path)
    rel = s.split("/nd-unfolding/")[-1] if "/nd-unfolding/" in s else s
    rel = rel.lstrip("./")
    if rel.startswith(root + "/") or rel == root:
        return True, ""
    if "member_k" in s:
        return False, (f"contains a member component but NOT AT THE ROOT -- this is the shape C "
                       f"reversed (namespace-then-member). Expected to start with {root!r}: {s}")
    return False, f"not member-scoped at all (expected to start with {root!r}): {s}"

def cluster_check(repo, offset, cases_by_launcher):
    """Run every launcher x case on the cluster and print a MACHINE-CHECKABLE verdict.

    A SILENT NO-OP CANNOT BE MISTAKEN FOR A PASS: the verdict line carries the number of launchers,
    cases and argv observations, and PASS is refused unless every case that declares it expects a
    command produced an integer estimator seed AND a member-namespaced output. Zero observations is
    reported as FAIL, never as clean.

    LIVENESS: one `[probe]` line per case, flushed, before and after each launcher runs. If nothing
    appears for more than a few seconds a launcher is genuinely stuck; a quiet stream is NOT
    evidence of progress (BEN-028) and this prints per case so silence is unambiguous.
    """
    # THE GATE RUNS FIRST AND ABORTS EVERYTHING. Not per case, not advisory.
    gate = assert_stubs_survive_activation(repo)
    print(f"[probe] STUB GATE PASSED after sourcing the env activator: {gate}", flush=True)
    total_cases = 0
    total_obs = 0
    failures = []
    for launcher in sorted(cases_by_launcher):
        for case in cases_by_launcher[launcher]:
            env = dict(case)
            expect = env.pop("_expect_command", True)
            env["MNV_EST_SEED_OFFSET"] = offset
            total_cases += 1
            print(f"[probe] START {launcher} case={case} offset={offset}", flush=True)
            rows, rc, err, stub_fired = observed_argv_native(launcher, env, repo)
            total_obs += len(rows)
            seeds = flag_values(rows, "--estimator-seed") or flag_values(rows, "--seed")
            outs = [v for k in ("--out", "--outdir", "--out-root", "--combine", "--block-slabs")
                    for v in flag_values(rows, k)]
            shaped = [(o, ) + is_member_scoped(o, offset) for o in outs]
            member = [o for o, ok, _ in shaped if ok]
            misshaped = [(o, why) for o, ok, why in shaped if not ok]
            if not expect:
                if stub_fired and not rows:
                    failures.append((launcher, case,
                                     ["a stub fired but produced no ARGV -- the interception path is "
                                      "inconsistent"], rc, err.strip()[-300:]))
                print(f"[probe] DONE  {launcher} case={case} (no command expected) obs={len(rows)} "
                      f"stub_fired={stub_fired}", flush=True)
                continue
            problems = []
            if not rows and not stub_fired:
                problems.append("NO command reached a stub AND the stub never fired -- either the "
                                "launcher exited early or the stubs were displaced. This is the "
                                "condition under which a real producer previously ran.")
            if not seeds:
                problems.append("no --estimator-seed/--seed reached a command")
            for s in seeds:
                if s == "<MISSING>" or not re.fullmatch(r"-?\d+", str(s)):
                    problems.append(f"seed value {s!r} is not an integer")
            if not outs:
                problems.append("no output path reached a command")
            elif misshaped:
                problems.append(f"{len(misshaped)} of {len(outs)} output paths FAIL THE SHAPE TEST:")
                problems.extend(f"    {why}" for _, why in misshaped)
            if problems:
                failures.append((launcher, case, problems, rc, err.strip()[-300:]))
            # PRINT EVERY OBSERVED PATH. The mediator's finding: a passing run's log contained NO
            # PATH -- 36 lines, zero occurrences of `member_k` or `mii/` outside the summary counts --
            # so a reader could not recover from the artifact WHAT had passed, and the counts were
            # identical across two different path shapes. A verdict-only receipt is unfalsifiable
            # (`CONVENTION-receipt-ingredients.md`); the paths ARE the ingredients of "namespaced=N".
            for o in outs:
                ok, why = is_member_scoped(o, offset)
                print(f"[probe]   PATH {'ok ' if ok else 'BAD'} {o}", flush=True)
            print(f"[probe] DONE  {launcher} case={case} rc={rc} obs={len(rows)} "
                  f"stub_fired={stub_fired} seeds={seeds} outs={len(outs)} "
                  f"namespaced={len(member)} {'OK' if not problems else 'PROBLEM'}", flush=True)
    print("")
    print(f"[probe] launchers={len(cases_by_launcher)} cases={total_cases} argv_observations={total_obs}")
    for launcher, case, problems, rc, err in failures:
        print(f"[probe] FAIL {launcher} {case} rc={rc}")
        for pr in problems:
            print(f"[probe]      {pr}")
        if err:
            print(f"[probe]      stderr tail: {err}")
    if total_obs == 0:
        print("[probe] VERDICT: FAIL -- ZERO argv observations. Nothing ran; this is NOT a pass.")
        return 2
    if failures:
        print(f"[probe] VERDICT: FAIL -- {len(failures)} case(s) with problems")
        return 1
    print(f"[probe] VERDICT: PASS -- {total_cases} cases, {total_obs} observations, every expected "
          f"case produced an integer estimator seed and a member-namespaced output")
    return 0


# ===================================================================================================
def gate_only(repo):
    """RUN THE STUB GATE AND NOTHING ELSE. There is no path from here to a launcher.

    WHY A SEPARATE ENTRY POINT RATHER THAN "invoke the full probe carefully". The mediator ran an
    instrument that executed real work on my assurance, and asked not to have to trust its own
    discipline twice in a row. An early `return` inside the full path would be one edit away from
    being bypassed; this function calls `assert_stubs_survive_activation` and returns, and a test
    asserts by AST that neither `observed_argv_native` nor `cluster_check` is reachable from it.

    IT CANNOT EXECUTE A LAUNCHER because it never names one: the gate sources only the environment
    activator, to answer one question -- do the stubs survive it?
    """
    try:
        got = assert_stubs_survive_activation(repo)
    except SystemExit as exc:
        print(str(exc), flush=True)
        print("[gate] VERDICT: FAIL -- the stubs do NOT survive the launchers' env activation. "
              "The full probe must NOT be run: this is the condition under which it previously "
              "executed a real unfold on a login node.", flush=True)
        return 2
    print(f"[gate] stub kinds AFTER sourcing setup_salloc_env.sh: {got}", flush=True)
    print("[gate] VERDICT: PASS -- every intercepted command is still a shell function after the "
          "activation that displaced the old PATH shims. The full probe may be run.", flush=True)
    return 0

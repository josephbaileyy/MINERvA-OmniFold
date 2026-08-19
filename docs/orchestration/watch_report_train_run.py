#!/usr/bin/python3.11
"""Classify a gate5 data-only C_stat train run from its own logs and email the verdict.

WHY THIS EXISTS
---------------
This replaces an LLM in a `wakerctl` watch's response path. Detection was never the LLM's job --
`wakerctl.py`'s tick/scan/evaluate is plain Python over `squeue`/`sacct`. The only thing left was a
SIX-WAY STRING CLASSIFICATION over two log files, which is a script. So this is a script.

HOW IT IS INVOKED
-----------------
`wakerctl.py` `action.type == "command"`: it runs a fixed `argv` with `cwd=<repo root>` and appends
`rc` plus stdout to the event log. It passes NO event payload, so everything needed arrives as
arguments and this script queries Slurm itself.

SELF-CONTAINMENT IS A DEPLOYMENT REQUIREMENT, NOT A STYLE CHOICE
----------------------------------------------------------------
`wakerctl` requires `argv[0]` to resolve inside its repo root, which in production is the CLUSTER
checkout `/pscratch/sd/j/josephrb/MINERvA-OmniFold`. That checkout sits ~200 commits behind `main`
and cannot be brought forward (OI-130 forbids cleaning it until a preservation inventory exists), so
this file is deployed alone into an otherwise-stale tree:

    git -C /pscratch/sd/j/josephrb/MINERvA-OmniFold fetch github      # remote is `github`, not `origin`
    git -C /pscratch/sd/j/josephrb/MINERvA-OmniFold checkout github/main -- docs/orchestration/watch_report_train_run.py

Therefore: STANDARD LIBRARY ONLY, no imports from this repository, no `sys.path` edits, no reading of
sibling config files, no reliance on `cwd`. A repo import here would silently bind to a ~200-commit-old
copy -- BEN-483, what EXECUTES versus what is CITED, with the callee as the unit. Version skew is made
irrelevant by depending on nothing.

Shebang is `/usr/bin/python3.11` because the login node's `python3` is 3.6 and cannot parse modern
syntax. The source is kept 3.8-compatible so it is unit-testable off-cluster.

EXIT CODE REPORTS THE INSTRUMENT, NEVER THE RUN  <-- the distinction this campaign keeps getting wrong
------------------------------------------------------------------------------------------------------
A non-zero rc makes `wakerctl` mark the dispatch `failed` and RETRY it (up to `max_retries`, default 2).
Retrying is the right response to a failed mail and the WRONG response to a failed training run: the
run will still be failed on the second attempt, and each retry re-mails. So:

    exit 0  <=>  the script did its job: it reached a verdict and delivered it.
                 SUCCESS, all five FAILs, UNKNOWN and NO-LOGS all exit 0. A failing run is a
                 SUCCESSFUL classification.
    exit !0 <=>  the script could NOT do its job: mail failed, or neither Slurm nor the logs were
                 readable so there was nothing to classify. These are worth retrying.

The verdict travels in the EMAIL SUBJECT and the body, never in the exit status.

CLASSIFICATION IS A CLOSED SET
------------------------------
Signatures come from the run's own handoff
(`docs/orchestration/HANDOFF-20260819-lane-e-data-only-cstat-smoke-57266000.md` section 3) and each
needle below was re-read from the PRODUCER that emits it (file:line in the table). UNKNOWN is a
first-class outcome, not an error: the handoff is explicit that anything matching none of the five is
"a fourth thing -- report it as itself rather than forcing it into one of these".
"""

import argparse
import os
import re
import subprocess
import sys
from datetime import datetime, timezone

MAIL_CMD_DEFAULT = "/usr/bin/mail"
RECIPIENT_DEFAULT = "josephrb@nersc.gov"
SACCT_CMD_DEFAULT = "sacct"
SACCT_FORMAT = "JobID,State,ExitCode,Elapsed"

# Standing constraints, reproduced verbatim in every mail because the notification is where they will
# actually be read.
STANDING_CONSTRAINTS = (
    "A PASS IS NOT AUTHORISATION for the 151 A100-h M(ii) family, for any second member, or for a "
    "resubmit. Those decisions return to the orchestrator and then to Joseph."
)

# ---------------------------------------------------------------------------------------------------
# The five failure signatures, in precedence order.
#
# Each needle is a LITERAL substring, verified against the producer that emits it:
#
#   FAIL-1  fullevent_fps_dataloader.py:742   raise ValueError("[negweight] refined target has
#                                             bootstrap_seed=None (NOMINAL) - cannot be ...")
#   FAIL-2  train_fullevent_replica.py:326    the doubled-component family-root disagreement; observed
#                                             verbatim in train_57253127_0.err
#   FAIL-3  cstat_data_only.py:279            f"[gate5-dataonly] {where}: withheld key(s) present: {present}"
#                                             observed verbatim in train_57256638_0.err
#   FAIL-4  cstat_data_only.py:286-291        f"...bootstrap_seed is {got}, not {-1} -- in a data-only
#                                             build the loader draws NO MC factors, so ..."
#                                             (DATA_ONLY_BOOTSTRAP_SEED_VALUE = -1, cstat_data_only.py:124)
#   FAIL-5  TWO emitters, deliberately matched by their COMMON substring:
#             submit_gate5_data_only_n50.sh:223  "collision/no-clobber guard (checkpoints): N file(s) ..."
#                 -- this is the SUBMITTER, on the login node at submit time. Its output goes to the
#                    submitter's terminal and CANNOT appear in the job's logs. 57266000 is already
#                    submitted, so this guard has already passed.
#             sbatch_gate5_data_only_train_array.sh:69  "collision/no-clobber guard: $f"
#                 -- this one runs INSIDE the job and lands in train_*.err, so it is the form that can
#                    actually appear here.
#           Matching the shared "no-clobber guard" catches both; the matched line is quoted in the mail
#           so the reader sees which variant fired. Keying on the handoff's "(checkpoints)" text alone
#           would have been a matcher that can never fire in the files it is pointed at.
#
# No needle is a substring of any other needle -- asserted by a test, because a signature whose text
# satisfies another signature's test is exactly how a closed set silently collapses.
# ---------------------------------------------------------------------------------------------------
SIGNATURES = (
    ("FAIL-1", "bootstrap_seed=None (NOMINAL)",
     "the module-global substitution did not take effect (57194055's cause)"),
    ("FAIL-2", "replicas/replicas",
     "the parents[3] family-root fix regressed (57253127's cause)"),
    ("FAIL-3", "withheld key(s) present",
     "should now be impossible -- the withheld set is empty (57256638's cause, BEN-476)"),
    ("FAIL-4", "not -1 -- in a data-only build",
     "the new positive seed check fired: bootstrap_seed was not -1"),
    ("FAIL-5", "no-clobber guard",
     "the BEN-477 checkpoint quarantine did not take"),
)

# The PASS receipt token. NOTE the anchoring: it is '"status": "PASS"'
# (train_fullevent_replica.py:696/756), NOT a bare "PASS". A bare "PASS" is worthless here because
# '"config_gate": "PASS"' appears in the stdout of EVERY run measured, including all three real
# failures -- so a bare-PASS success check fires on failed runs. Measured, not assumed.
RECEIPT_PASS_TOKEN = '"status": "PASS"'
CONFIG_GATE_PASS_TOKEN = '"config_gate": "PASS"'

VERDICT_MEANINGS = {
    "SUCCESS": "a PASS receipt AND the DONE line for this index/seed",
    "UNKNOWN": "none of the five signatures matched -- this is a FOURTH THING, report it as itself",
    "NO-LOGS": "the log files do not exist or could not be read",
}


def done_pattern(index, seed):
    """Anchored matcher for the run-completion line.

    The producer is `sbatch_gate5_data_only_train_array.sh:124`:

        echo "[gate5-do-train] DONE index=$INDEX seed=$SEED $(date -u +%Y-%m-%dT%H:%M:%SZ)"

    Two measured details drive this regex:

    1. A TRAILING TIMESTAMP follows the seed, so this must not be anchored to end-of-line.
    2. The fields must be anchored on the RIGHT, or `seed=50000` is satisfied by `seed=500001` and
       `index=0` by `index=01`. A whole-field comparison expressed as a bare substring is not a
       whole-field comparison. Hence the `(?!\\d)` guards.

    The `[gate5-do-train]` prefix is deliberately NOT required: the prefix is where the emitters
    disagree (see the readback note in the module docstring), and requiring it would make this
    classifier fail closed on a genuinely successful run for a cosmetic reason.
    """
    return re.compile(
        r"DONE\s+index=%d(?!\d)\s+seed=%d(?!\d)" % (int(index), int(seed))
    )


class Result(object):
    """Everything the mail needs. Plain object so this stays 3.8-clean."""

    def __init__(self):
        self.verdict = "NO-LOGS"
        self.headline = ""
        self.matches = []          # list of (code, meaning, path, lineno, line)
        self.log_paths = []        # [(label, path, readable_bool, note)]
        self.readable = []         # [(label, path, text)]
        self.slurm_ok = False
        self.slurm_text = ""
        self.slurm_note = ""
        self.receipt_pass = False
        self.done_seen = False
        self.config_gate_pass = False


def read_logs(out_path, err_path):
    """Return (paths_report, readable) -- never raises for a missing/unreadable file."""
    paths_report = []
    readable = []
    for label, path in (("stdout", out_path), ("stderr", err_path)):
        note = ""
        try:
            if os.path.islink(path):
                note = "is a symlink"
            with open(path, "r", errors="replace") as handle:
                text = handle.read()
        except OSError as exc:
            paths_report.append((label, path, False, "%s: %s" % (type(exc).__name__, exc)))
            continue
        if note:
            note = note + "; read anyway"
        size_note = "empty (0 bytes)" if text == "" else "%d bytes" % len(text)
        paths_report.append((label, path, True, (note + "; " + size_note) if note else size_note))
        readable.append((label, path, text))
    return paths_report, readable


def find_needle(readable, needle):
    """First occurrence of `needle`, as (label, path, lineno, line). Case-sensitive and literal."""
    for label, path, text in readable:
        for lineno, line in enumerate(text.splitlines(), start=1):
            if needle in line:
                return (label, path, lineno, line.rstrip())
    return None


def classify(readable, index, seed):
    """Assign exactly one verdict. FAILs take precedence over SUCCESS.

    Precedence is measured, not stylistic: train_57256638_0 carries '"config_gate": "PASS"' in stdout
    AND the FAIL-3 signature in stderr. A run that emitted a failure signature is failed, whatever else
    its logs also say.
    """
    result_matches = []
    for code, needle, meaning in SIGNATURES:
        hit = find_needle(readable, needle)
        if hit is not None:
            label, path, lineno, line = hit
            result_matches.append((code, meaning, path, lineno, line))

    done_re = done_pattern(index, seed)
    done_seen = False
    receipt_pass = False
    config_gate_pass = False
    for _label, _path, text in readable:
        if done_re.search(text):
            done_seen = True
        if RECEIPT_PASS_TOKEN in text:
            receipt_pass = True
        if CONFIG_GATE_PASS_TOKEN in text:
            config_gate_pass = True

    if result_matches:
        verdict = result_matches[0][0]
    elif receipt_pass and done_seen:
        verdict = "SUCCESS"
    else:
        verdict = "UNKNOWN"
    return verdict, result_matches, done_seen, receipt_pass, config_gate_pass


def query_slurm(job_id, sacct_cmd, runner):
    """(ok, text, note). A Slurm failure is recorded, never fatal on its own."""
    argv = [sacct_cmd, "-j", str(job_id), "--format=" + SACCT_FORMAT]
    try:
        proc = runner(argv)
    except OSError as exc:
        return False, "", "could not execute %r: %s: %s" % (argv, type(exc).__name__, exc)
    text = (proc.stdout or "")
    if proc.returncode != 0:
        return False, text, "%s exited %d; stderr=%s" % (
            sacct_cmd, proc.returncode, (proc.stderr or "").strip()[:500])
    if not text.strip():
        return False, text, "%s exited 0 but produced no rows for job %s" % (sacct_cmd, job_id)
    return True, text, ""


def default_runner(argv):
    return subprocess.run(argv, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                          universal_newlines=True)


def context_block(path, lineno, text, before=3, after=3):
    lines = text.splitlines()
    lo = max(0, lineno - 1 - before)
    hi = min(len(lines), lineno + after)
    out = []
    for i in range(lo, hi):
        marker = ">>" if (i + 1) == lineno else "  "
        out.append("%s %s:%d: %s" % (marker, os.path.basename(path), i + 1, lines[i]))
    return "\n".join(out)


def tail_block(path, text, n):
    lines = text.splitlines()
    if not lines:
        return "  (%s is EMPTY -- zero lines)" % os.path.basename(path)
    shown = lines[-n:]
    head = "  (last %d of %d lines of %s)" % (len(shown), len(lines), os.path.basename(path))
    return head + "\n" + "\n".join("  " + line for line in shown)


def subject_for(result, job_id, task_id):
    short = {
        "SUCCESS": "PASS receipt + DONE line",
        "UNKNOWN": "none of the five signatures matched",
        "NO-LOGS": "log files unreadable",
        "FAIL-1": "bootstrap_seed=None (NOMINAL)",
        "FAIL-2": "replicas/replicas family-root regression",
        "FAIL-3": "withheld key(s) present",
        "FAIL-4": "bootstrap_seed not -1 in a data-only build",
        "FAIL-5": "no-clobber guard fired",
    }.get(result.verdict, result.verdict)
    return "[MNV] %s_%s %s -- %s" % (job_id, task_id, result.verdict, short)


def build_body(result, job_id, task_id, index, seed, tail_lines):
    L = []
    add = L.append
    add("=" * 88)
    add("VERDICT: %s" % result.verdict)
    if result.verdict in VERDICT_MEANINGS:
        add("MEANING: %s" % VERDICT_MEANINGS[result.verdict])
    elif result.matches:
        add("MEANING: %s" % result.matches[0][1])
    add("=" * 88)
    add("")
    if result.verdict == "UNKNOWN":
        add("!" * 88)
        add("!!  UNKNOWN IS NOT AN ERROR AND NOT A DEFAULT-TO-FAIL.")
        add("!!  This run matched NONE of the five known signatures. Per the handoff, that makes it")
        add("!!  a FOURTH THING and it must be read as itself rather than forced into one of the five.")
        add("!!  Generous tails of both streams are included below so you can see the actual failure.")
        add("!" * 88)
        add("")
    if result.verdict == "NO-LOGS":
        add("!" * 88)
        add("!!  NO LOG FILE COULD BE READ. This is distinct from UNKNOWN: UNKNOWN means the logs were")
        add("!!  read and matched nothing; NO-LOGS means there was nothing to read. Paths tried below.")
        add("!" * 88)
        add("")

    add("JOB: %s_%s   (replica index=%d, bootstrap seed=%d)" % (job_id, task_id, index, seed))
    add("Report generated: %s" % datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"))
    add("")

    add("-- SLURM SIDE " + "-" * 74)
    if result.slurm_ok:
        add("sacct -j %s --format=%s" % (job_id, SACCT_FORMAT))
        add(result.slurm_text.rstrip())
    else:
        add("SLURM STATE UNAVAILABLE: %s" % (result.slurm_note or "unknown reason"))
        if result.slurm_text.strip():
            add("partial output:")
            add(result.slurm_text.rstrip())
    add("")
    add("NOTE ON DISAGREEMENT: the Slurm state above and the log verdict above are INDEPENDENT")
    add("measurements and neither overwrites the other. If Slurm says COMPLETED 0:0 while the log")
    add("verdict is a FAIL (or vice versa), that disagreement is itself the finding and a human must")
    add("adjudicate it -- 57256638_0 trained fully and died at the receipt write, which is exactly the")
    add("shape that makes one side look fine.")
    add("")

    add("-- LOG PATHS " + "-" * 75)
    for label, path, ok, note in result.log_paths:
        add("  [%s] %s  %s (%s)" % (label, path, "READ" if ok else "UNREADABLE", note))
    add("")

    add("-- LOG-SIDE EVIDENCE " + "-" * 67)
    if result.matches:
        for code, meaning, path, lineno, line in result.matches:
            add("MATCHED %s: %s" % (code, meaning))
            add("  matched line %s:%d:" % (path, lineno))
            for _label, p, text in result.readable:
                if p == path:
                    add(context_block(path, lineno, text))
                    break
            add("")
        if len(result.matches) > 1:
            add("NOTE: %d signatures matched. The verdict takes the first in precedence order; the"
                % len(result.matches))
            add("others are listed above because more than one firing is itself informative.")
            add("")
    else:
        add("No known failure signature matched.")
    add("PASS receipt token %s present: %s" % (RECEIPT_PASS_TOKEN, result.receipt_pass))
    add("DONE line for index=%d seed=%d present: %s" % (index, seed, result.done_seen))
    add("(config_gate PASS present: %s -- this is NOT the receipt and never implies success; it"
        % result.config_gate_pass)
    add(" appears in the stdout of every measured run, including all three real failures.)")
    add("")

    if result.verdict == "UNKNOWN" and result.readable:
        add("-- GENEROUS TAILS (UNKNOWN) " + "-" * 60)
        for _label, path, text in result.readable:
            add(tail_block(path, text, tail_lines))
            add("")

    add("=" * 88)
    add("STANDING CONSTRAINTS")
    add("=" * 88)
    add(STANDING_CONSTRAINTS)
    add("")
    add("Also not authorised by a PASS: the full family, any second member, OI-133's digest binding,")
    add("and any cleanup of the cluster checkout.")
    add("")
    add("Reported by docs/orchestration/watch_report_train_run.py (no LLM in this path).")
    return "\n".join(L) + "\n"


def send_mail(mail_cmd, recipient, subject, body, runner):
    """Return (ok, note). Mail failure is an INSTRUMENT failure -> non-zero exit -> worth retrying."""
    argv = [mail_cmd, "-s", subject, recipient]
    try:
        proc = runner(argv, body)
    except OSError as exc:
        return False, "could not execute %r: %s: %s" % (argv, type(exc).__name__, exc)
    if proc.returncode != 0:
        return False, "%s exited %d; stderr=%s" % (
            mail_cmd, proc.returncode, (proc.stderr or "").strip()[:500])
    return True, "sent to %s via %s" % (recipient, mail_cmd)


def default_mail_runner(argv, body):
    return subprocess.run(argv, input=body, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                          universal_newlines=True)


def build_parser():
    p = argparse.ArgumentParser(
        prog="watch_report_train_run.py",
        description="Classify a gate5 data-only C_stat train run from its logs and email the verdict. "
                    "Exit code reports whether THIS SCRIPT worked, never whether the RUN passed.")
    p.add_argument("--job-id", required=True,
                   help="Slurm array job id, e.g. 57266000")
    p.add_argument("--task-id", default="0",
                   help="array task id (default 0); log files are <prefix>_<job>_<task>.{out,err}")
    p.add_argument("--log-dir", required=True,
                   help="ABSOLUTE path to the run's logs/ directory")
    p.add_argument("--log-prefix", default="train",
                   help="log filename prefix (default 'train')")
    p.add_argument("--index", type=int, default=None,
                   help="replica index for the DONE line (default: --task-id)")
    p.add_argument("--seed", type=int, default=50000,
                   help="bootstrap seed for the DONE line (default 50000)")
    p.add_argument("--to", default=RECIPIENT_DEFAULT, help="recipient (default %s)" % RECIPIENT_DEFAULT)
    p.add_argument("--mail-cmd", default=MAIL_CMD_DEFAULT,
                   help="mail program (default %s); overridable so tests never send mail"
                        % MAIL_CMD_DEFAULT)
    p.add_argument("--sacct-cmd", default=SACCT_CMD_DEFAULT, help="sacct program (default sacct)")
    p.add_argument("--tail-lines", type=int, default=60,
                   help="lines of each stream to include when UNKNOWN (default 60)")
    p.add_argument("--dry-run", action="store_true",
                   help="print the mail to stdout instead of sending it. Sends NO email.")
    return p


def run(argv=None, slurm_runner=None, mail_runner=None, stdout=None):
    """Returns the process exit code. Injectable runners keep tests off the network and off the MTA."""
    args = build_parser().parse_args(argv)
    slurm_runner = slurm_runner or default_runner
    mail_runner = mail_runner or default_mail_runner
    stdout = stdout or sys.stdout

    index = args.index
    if index is None:
        try:
            index = int(args.task_id)
        except ValueError:
            index = 0
    seed = args.seed

    log_dir = os.path.abspath(args.log_dir)
    stem = "%s_%s_%s" % (args.log_prefix, args.job_id, args.task_id)
    out_path = os.path.join(log_dir, stem + ".out")
    err_path = os.path.join(log_dir, stem + ".err")

    result = Result()
    result.log_paths, result.readable = read_logs(out_path, err_path)
    result.slurm_ok, result.slurm_text, result.slurm_note = query_slurm(
        args.job_id, args.sacct_cmd, slurm_runner)

    if not result.readable:
        result.verdict = "NO-LOGS"
    else:
        (result.verdict, result.matches, result.done_seen,
         result.receipt_pass, result.config_gate_pass) = classify(result.readable, index, seed)

    subject = subject_for(result, args.job_id, args.task_id)
    body = build_body(result, args.job_id, args.task_id, index, seed, args.tail_lines)

    # Instrument-status accounting starts here. Nothing below consults the VERDICT to choose an exit
    # code; it consults only whether the script managed to observe and deliver.
    if not result.readable and not result.slurm_ok:
        # Neither source was readable: there is no verdict to deliver, only an instrument failure.
        stdout.write(subject + "\n")
        stdout.write("INSTRUMENT FAILURE: no log file readable AND Slurm unavailable (%s). "
                     "Nothing could be classified.\n" % (result.slurm_note or "unknown"))
        stdout.write(body)
        return 3

    if args.dry_run:
        stdout.write("DRY RUN -- no mail sent. Subject would be:\n%s\n\n" % subject)
        stdout.write(body)
        return 0

    ok, note = send_mail(args.mail_cmd, args.to, subject, body, mail_runner)
    stdout.write("%s\n" % subject)
    stdout.write("verdict=%s slurm_ok=%s mail_ok=%s (%s)\n"
                 % (result.verdict, result.slurm_ok, ok, note))
    if not ok:
        # Mail failure is the one thing a retry can actually fix.
        stdout.write("INSTRUMENT FAILURE: could not deliver the verdict. Body follows so it is not "
                     "lost from the event log:\n")
        stdout.write(body)
        return 4
    return 0


if __name__ == "__main__":
    sys.exit(run())

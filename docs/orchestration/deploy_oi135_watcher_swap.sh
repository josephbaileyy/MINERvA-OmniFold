#!/usr/bin/env bash
# Rehearsed, idempotent, fail-closed deployment of OI-135 (a)-(f): swap the
# gate5-do-train-57266000 watcher's response path from an LLM root-resume to the tested
# email script `docs/orchestration/watch_report_train_run.py`.
#
# WHY A SCRIPT AND NOT SIX TYPED COMMANDS
# ---------------------------------------
# The six steps are ORDER-DEPENDENT and two of them fail in ways that are not cheap to
# undo: deploying `waker-config.json` without `profiles.json` makes every codex dispatch
# raise `AgentCtlError: Unknown profile 'codex-waker'` (MEASURED, OI-135 (f)), and
# disarming `r3` before `r4` is verifiably armed leaves a 3 A100-h job with NO watch at
# all -- which is ISSUE-46, committed by this lane. Typed by hand at cluster-return the
# ordering is a matter of memory; here it is a matter of control flow, because every
# mutation sits downstream of a check that must return 0.
#
# WHAT IT REFUSES TO DO (fail-closed preflight, all read-only)
# ------------------------------------------------------------
#   * cluster unreachable                            -> REFUSE, nothing is attempted
#   * remote `github` not configured in the checkout  -> REFUSE
#   * ANY of the THREE files absent from github/main  -> REFUSE (all three or none)
#   * watch store unreadable, or `r3` absent         -> REFUSE
# A refusal exits non-zero BEFORE the first mutation, so a partial deployment is not
# reachable from a failed precondition.
#
# WHAT IT PRINTS
# --------------
# What it READ, never merely that it acted (BEN-478). `armed` is never inferred from
# `watch-add`'s exit status; it is read back out of the watch JSON. Likewise the profile
# deployment is accepted only after `profiles.json` is read and found to CONTAIN the
# `codex-waker` key that `waker-config.json` dereferences -- read the field the code
# dereferences, not the fact that a command exited 0.
#
# MODES
# -----
#   (default)           PLAN: read-only. Probes every precondition, prints the exact
#                       mutating commands, executes NONE of them.
#   --execute           Perform steps (a)-(d) and (f).
#   --regen-live-state  Additionally perform step (e). OFF by default: it writes
#                       LIVE-STATE.md inside a checkout 98 commits behind main (OI-130),
#                       which is a judgement the operator should make explicitly.
#
# STEP LETTERS FOLLOW docs/OPEN_ITEMS.md OI-135, WHICH IS THE AUTHORITY (the briefing
# message used a different lettering; the row wins):
#   (a) deploy watch_report_train_run.py    (b) arm r4, THEN disarm r3
#   (c) re-measure the five resource fields (d) cluster `git worktree list` hygiene
#   (e) regenerate LIVE-STATE.md            (f) deploy profiles.json + waker-config.json
# (a)'s and (f)'s file halves are ONE `git checkout` of three paths, because splitting it
# is the failure mode (f) exists to prevent; the row's ordering is preserved, not
# reinterpreted, and (f)'s own verification runs after (a)'s.
#
# BASH 3.2 COMPATIBLE ON PURPOSE: no associative arrays, no `mapfile`, no `${x^^}`. The
# rehearsal host runs bash 3.2.57 and the login node runs 4.4, and the two have already
# given this campaign opposite `set -e` answers, so every failure is handled with an
# EXPLICIT `if ! ...; then` and nothing depends on `set -e`. No command whose exit status
# is read is ever on the left of a pipe.

set -u

# --------------------------------------------------------------------------- constants
# Overridable ONLY so the test suite can inject a fake transport. Production values are
# the defaults: a rehearsal that had to edit the script would not be rehearsing the script.
SSH_CMD="${OI135_SSH:-ssh}"
LOGIN="${OI135_LOGIN:-saul.nersc.gov}"
CREPO="${OI135_CREPO:-/pscratch/sd/j/josephrb/MINERvA-OmniFold}"
REMOTE_PY="${OI135_REMOTE_PY:-/usr/bin/python3.11}"
LOGDIR="${OI135_LOGDIR:-/pscratch/sd/j/josephrb/gate5-do-g2/nd-unfolding/pet/fullevent_cstat_data_only_n50/logs}"
DANGLING_WT="${OI135_DANGLING_WT:-/pscratch/sd/j/josephrb/live-state-regen-e8c857f3}"

JOB_ID="57266000"
TASK_ID="0"
# `params.tasks` is a task-id SPEC and never a count: expand_spec("1") == [1] is task
# index 1, which is how r2 came to watch a task its array does not have
# (wakerctl.py:945-960, BEN-478). This array's only task is index 0, so the spec is "0-0".
TASKS_SPEC="0-0"
WATCH_NEW="gate5-do-train-57266000-r4"
WATCH_OLD="gate5-do-train-57266000-r3"

# THE THREE FILES. profiles.json and waker-config.json MUST land together or neither:
# waker-config.json's root.profile names `codex-waker`, which exists only in profiles.json.
P_SCRIPT="docs/orchestration/watch_report_train_run.py"
P_PROFILES="docs/orchestration/profiles.json"
P_WAKERCFG="docs/orchestration/waker-config.json"
DEPLOY_PATHS="$P_SCRIPT $P_PROFILES $P_WAKERCFG"
DEPLOY_PATH_COUNT=3
WAKER_PROFILE="codex-waker"

WAKERCTL="$CREPO/docs/orchestration/wakerctl.py"
TARGET_PROGRAM="$CREPO/$P_SCRIPT"

MODE="plan"
DO_REGEN="no"

# --------------------------------------------------------------------------- plumbing
R_OUT=""
R_RC=0
FAILED=0

say()   { printf '%s\n' "$*"; }
read_() { printf 'READ  %s\n' "$*"; }   # a line of evidence: the value that was observed
plan()  { printf 'PLAN  %s\n' "$*"; }
act()   { printf 'ACT   %s\n' "$*"; }
ok()    { printf 'OK    %s\n' "$*"; }
die()   { printf 'REFUSE %s\n' "$*" >&2; exit 2; }
fail()  { printf 'FAIL  %s\n' "$*" >&2; FAILED=1; }
indent(){ printf '%s\n' "$1" | sed 's/^/        /'; }

usage() {
  say "usage: $0 [--execute] [--regen-live-state] [--help]"
  say "  default is PLAN (read-only): every precondition is probed, nothing is mutated."
}

# remote <command-string> -- runs on the login node, combined output in R_OUT, status in
# R_RC. Never piped, so R_RC is ssh's own status and not some tail command's.
remote() {
  R_OUT="$("$SSH_CMD" "$LOGIN" "$1" 2>&1)"
  R_RC=$?
  return $R_RC
}

# remote_file <program-file> <args...> -- feeds a python program to the login node's
# python3.11 on stdin. Redirection rather than a pipe, for the same reason.
remote_file() {
  _prog="$1"
  shift
  R_OUT="$("$SSH_CMD" "$LOGIN" "$REMOTE_PY - $*" < "$_prog" 2>&1)"
  R_RC=$?
  return $R_RC
}

while [ $# -gt 0 ]; do
  case "$1" in
    --execute) MODE="execute" ;;
    --regen-live-state) DO_REGEN="yes" ;;
    --help|-h) usage; exit 0 ;;
    *) printf 'REFUSE unknown argument: %s\n' "$1" >&2; usage >&2; exit 2 ;;
  esac
  shift
done

say "=== OI-135 watcher swap: mode=$MODE regen-live-state=$DO_REGEN"
say "=== target checkout $CREPO on $LOGIN (98 commits behind main and NOT to be reset, pulled or cleaned -- OI-130)"

# =========================================================================== PREFLIGHT
# Every check here is read-only. NOTHING below the preflight block runs unless all pass.

if ! remote "true"; then
  die "cluster unreachable: \`$SSH_CMD $LOGIN true\` exited $R_RC. maintenance_20260819 runs to 2026-08-26T13:00Z as an OUTER BOUND, not a prediction. No step attempted, nothing mutated."
fi
read_ "reachability: \`$SSH_CMD $LOGIN true\` exited 0"

if ! remote "git -C $CREPO rev-parse --git-dir"; then
  die "no git checkout at $CREPO (rc=$R_RC): $R_OUT"
fi
read_ "cluster checkout git-dir: $R_OUT"

if ! remote "git -C $CREPO remote get-url github"; then
  die "remote \`github\` is not configured in $CREPO (rc=$R_RC): $R_OUT. That checkout's remote is \`github\`, not \`origin\`."
fi
read_ "remote github -> $R_OUT"

# ALL THREE FILES OR NONE, checked BEFORE the fetch/checkout so a missing blob cannot
# produce a half-deployment, and COUNTED so a future edit that drops one from
# DEPLOY_PATHS cannot silently shrink the check.
_seen=0
for _p in $DEPLOY_PATHS; do
  if ! remote "git -C $CREPO cat-file -e github/main:$_p"; then
    die "github/main does not carry $_p (rc=$R_RC): $R_OUT. The three files deploy together or not at all: waker-config.json names profile $WAKER_PROFILE, which lives in profiles.json, and deploying only the config makes every dispatch raise AgentCtlError: Unknown profile '$WAKER_PROFILE'."
  fi
  read_ "github/main carries $_p"
  _seen=$((_seen + 1))
done
if [ "$_seen" -ne "$DEPLOY_PATH_COUNT" ]; then
  die "internal: verified $_seen paths, expected $DEPLOY_PATH_COUNT"
fi
read_ "all $_seen/$DEPLOY_PATH_COUNT deploy paths present in github/main"

if ! remote "$REMOTE_PY $WAKERCTL watch-list"; then
  die "watch store not readable: \`wakerctl.py watch-list\` exited $R_RC: $R_OUT"
fi
WATCH_LIST="$R_OUT"
read_ "watch-list:"
indent "$WATCH_LIST"

# The predecessor must EXIST before we plan to retire it, and its state is compared as a
# WHOLE FIELD: "disarmed" contains "armed" (wakerctl.py:724-735, and a substring health
# check has already reported 2 armed watches on a job that had one of each).
OLD_STATE=""
NEW_STATE=""
_ifs_save="$IFS"
IFS='
'
for _line in $WATCH_LIST; do
  _wid="${_line%%	*}"
  _st="${_line##*	}"
  if [ "$_wid" = "$WATCH_OLD" ]; then OLD_STATE="$_st"; fi
  if [ "$_wid" = "$WATCH_NEW" ]; then NEW_STATE="$_st"; fi
done
IFS="$_ifs_save"

if [ -z "$OLD_STATE" ]; then
  die "$WATCH_OLD is not in the watch store; there is nothing to retire and this is not the store OI-135 describes"
fi
read_ "$WATCH_OLD state=[$OLD_STATE] (whole-field compare)"
if [ -n "$NEW_STATE" ]; then
  read_ "$WATCH_NEW already present, state=[$NEW_STATE] -- step (b) will VERIFY rather than re-arm (idempotent)"
fi

ok "preflight passed: cluster reachable, github remote present, $DEPLOY_PATH_COUNT/$DEPLOY_PATH_COUNT blobs in github/main, watch store readable, $WATCH_OLD present"

# Helper programs are written to temp FILES rather than piped, so the status read after
# each ssh is ssh's own.
TMPD="${TMPDIR:-/tmp}/oi135.$$"
if ! mkdir -p "$TMPD"; then die "cannot create work dir $TMPD"; fi
trap 'rm -rf "$TMPD"' EXIT INT TERM

READBACK="$TMPD/readback.py"
cat > "$TMPD/readback.py" <<'PYEOF'
import json, sys
path = sys.argv[1]
want_job, want_tasks, want_state, want_program = sys.argv[2], sys.argv[3], sys.argv[4], sys.argv[5]
try:
    w = json.load(open(path))
except Exception as exc:                      # an unreadable store is a REFUSAL, not a pass
    print("readback-error: %s: %s" % (path, exc)); sys.exit(3)
params = w.get("params") or {}
action = w.get("action") or {}
argv = action.get("argv") or []
state = str(w.get("state") or "").strip()     # WHOLE field; never a substring test
print("watch_id=%r" % w.get("watch_id"))
print("state=%r" % state)
print("kind=%r" % w.get("kind"))
print("params.job_id=%r" % str(params.get("job_id", "")))
print("params.tasks=%r" % str(params.get("tasks", "")))
print("action.type=%r" % action.get("type"))
print("action.argv=%r" % (argv,))
bad = []
if state != want_state:                       # equality, not `in`
    bad.append("state %r != %r" % (state, want_state))
if str(params.get("job_id", "")) != want_job:
    bad.append("params.job_id %r != %r" % (params.get("job_id"), want_job))
if str(params.get("tasks", "")) != want_tasks:
    bad.append("params.tasks %r != %r (a SPEC, not a count)" % (params.get("tasks"), want_tasks))
if action.get("type") != "command":
    bad.append("action.type %r != 'command'" % action.get("type"))
if not argv or argv[0] != want_program:
    bad.append("action.argv[0] %r != %r" % (argv[0] if argv else None, want_program))
if bad:
    print("MISMATCH: " + "; ".join(bad)); sys.exit(4)
print("readback-ok")
PYEOF

# ============================================== (a)+(f) THE ONE CHECKOUT, THREE PATHS
FETCH_CMD="git -C $CREPO fetch github"
CHECKOUT_CMD="git -C $CREPO checkout github/main -- $DEPLOY_PATHS"

if [ "$MODE" = "plan" ]; then
  plan "$FETCH_CMD"
  plan "$CHECKOUT_CMD    # ONE command, $DEPLOY_PATH_COUNT paths, all-or-nothing"
else
  act "$FETCH_CMD"
  if ! remote "$FETCH_CMD"; then
    die "fetch failed (rc=$R_RC): $R_OUT"
  fi
  read_ "fetch github ok"
  act "$CHECKOUT_CMD"
  if ! remote "$CHECKOUT_CMD"; then
    die "three-path checkout failed (rc=$R_RC): $R_OUT. Nothing was reset, pulled or cleaned; the checkout is single-path by construction (OI-130)."
  fi
  # Verified by DIFFING against the source ref, which is stronger than "exited 0".
  if ! remote "git -C $CREPO diff --exit-code github/main -- $DEPLOY_PATHS"; then
    die "post-checkout diff against github/main is NON-EMPTY (rc=$R_RC): $R_OUT"
  fi
  read_ "all $DEPLOY_PATH_COUNT deployed paths are byte-identical to github/main (git diff --exit-code, empty)"
fi

# ================================================= (a) MODE AND argv[0] RESOLUTION
# The exec bit and the shebang are load-bearing: argv[0] must be the script itself, not
# `/usr/bin/python3.11 <script>`. wakerctl.py:340-346 requires
# `program.is_absolute() and ctx.repo in program.resolve().parents` -- and `.resolve()`
# means a symlink pointing OUT of the tree FAILS, so the check below resolves too,
# exactly as wakerctl does rather than approximately.
if [ "$MODE" = "plan" ] && ! remote "test -e $TARGET_PROGRAM"; then
  plan "verify mode 100755 + argv[0] resolution for $TARGET_PROGRAM (not deployed yet, so not checkable now)"
else
  if ! remote "stat -c %a $TARGET_PROGRAM"; then
    die "cannot stat $TARGET_PROGRAM (rc=$R_RC): $R_OUT"
  fi
  read_ "mode of $P_SCRIPT = $R_OUT"
  if [ "$R_OUT" != "755" ]; then
    die "mode is [$R_OUT], not 755: wakerctl execs argv[0] directly, so the exec bit is load-bearing"
  fi
  ARGVCHK="$TMPD/argvchk.py"
  cat > "$TMPD/argvchk.py" <<'PYEOF'
import sys
from pathlib import Path
program = Path(sys.argv[1])
# `ctx.repo` is HERE.parent.parent with `HERE = Path(__file__).resolve().parent`
# (wakerctl.py:31,147), so the repo side of the comparison is RESOLVED. Resolving only the
# program would compare a resolved path against an unresolved one and reject a legitimate
# file on any host where the tree sits under a symlink (/var -> /private/var on the
# rehearsal host does exactly that). Both sides, or the comparison is not wakerctl's.
repo = Path(sys.argv[2]).resolve()
resolved = program.resolve()
print("argv0=%s" % program)
print("resolved=%s" % resolved)
print("repo_resolved=%s" % repo)
print("is_absolute=%s" % program.is_absolute())
print("repo_in_resolved_parents=%s" % (repo in resolved.parents))
print("is_symlink=%s" % program.is_symlink())
first = ""
try:
    with open(str(program), "rb") as fh:
        first = fh.readline().decode("utf-8", "replace").rstrip("\n")
except Exception as exc:
    print("unreadable: %s" % exc); sys.exit(5)
print("shebang=%r" % first)
if not (program.is_absolute() and repo in resolved.parents):
    print("MISMATCH: wakerctl.py:340-346 would raise 'command action argv[0] must be "
          "an absolute path inside the repository'")
    sys.exit(6)
if not first.startswith("#!"):
    print("MISMATCH: no shebang, so exec of argv[0] cannot work")
    sys.exit(7)
print("argv0-ok")
PYEOF
  if ! remote_file "$ARGVCHK" "$TARGET_PROGRAM" "$CREPO"; then
    die "argv[0] would be REJECTED by wakerctl (rc=$R_RC): $R_OUT"
  fi
  indent "$R_OUT"
  ok "(a) deployed and verified: $P_SCRIPT is a real file inside $CREPO, mode 755, exec-able as argv[0]"
fi

# ============ (f) THE PROFILE PAIR: read the key the code DEREFERENCES, not the exit status
# Both files landed in the single checkout above. What is verified here is the thing that
# actually breaks: waker-config.json's root.profile must name a profile that profiles.json
# DEFINES. Asserting "the checkout exited 0" would not have caught a stale profiles.json.
if [ "$MODE" = "plan" ]; then
  plan "read $CREPO/$P_WAKERCFG root.profile and assert $CREPO/$P_PROFILES defines it"
else
  PROFCHK="$TMPD/profchk.py"
  cat > "$TMPD/profchk.py" <<'PYEOF'
import json, sys
cfg_path, prof_path, expect = sys.argv[1], sys.argv[2], sys.argv[3]
try:
    cfg = json.load(open(cfg_path))
    prof = json.load(open(prof_path))
except Exception as exc:
    print("unreadable: %s" % exc); sys.exit(8)
root = cfg.get("root") or {}
named = root.get("profile")
# profiles.json may hold the profiles at the top level or under a "profiles" key; accept
# either rather than assuming a shape this script does not own.
table = prof.get("profiles") if isinstance(prof.get("profiles"), dict) else prof
keys = sorted(table.keys()) if isinstance(table, dict) else []
print("waker-config root.profile=%r" % named)
print("profiles.json defines=%r" % (keys,))
if named != expect:
    print("MISMATCH: root.profile %r != expected %r" % (named, expect)); sys.exit(9)
if named not in keys:
    print("MISMATCH: profiles.json does NOT define %r -- every dispatch would raise "
          "AgentCtlError: Unknown profile %r" % (named, named))
    sys.exit(10)
entry = table[named] if isinstance(table, dict) else {}
if isinstance(entry, dict):
    print("profile %s model=%r reasoning_effort=%r yolo=%r"
          % (named, entry.get("model"), entry.get("reasoning_effort"), entry.get("yolo")))
print("profile-pair-ok")
PYEOF
  if ! remote_file "$PROFCHK" "$CREPO/$P_WAKERCFG" "$CREPO/$P_PROFILES" "$WAKER_PROFILE"; then
    die "(f) the deployed profile pair is INCOHERENT (rc=$R_RC): $R_OUT. Both files are already on disk; re-run the three-path checkout -- do NOT leave the config naming a profile that is not defined."
  fi
  indent "$R_OUT"
  ok "(f) profiles.json DEFINES $WAKER_PROFILE and waker-config.json root.profile names it -- read from the deployed files, not inferred"
fi

# ============================ (b) ARM r4, THEN RETIRE r3 -- never the reverse
# ADD-THEN-RETIRE (ISSUE-46, committed by this lane: the inverse left a 3 A100-h job
# unwatched). The ticker's remove-then-recreate exception at ISSUE-52 does NOT extend to
# watches. Enforced structurally: the disarm is unreachable unless the r4 readback passed.
#
# NOTE ON THE ARM COMMAND: `watch-add` requires --id and --kind, and kind slurm-array
# requires params job_id AND tasks (wakerctl.py:320-331), so an arm carrying only
# `--action command --argv ...` would be REJECTED. `--argv` is argparse.REMAINDER
# (wakerctl.py:1788) and therefore MUST come last -- anything after it is swallowed into it.
ARM_CMD="$REMOTE_PY $WAKERCTL watch-add --id $WATCH_NEW --kind slurm-array --param job_id=$JOB_ID --param tasks=$TASKS_SPEC --action command --argv $TARGET_PROGRAM --job-id $JOB_ID --task-id $TASK_ID --log-dir $LOGDIR"
DISARM_CMD="$REMOTE_PY $WAKERCTL watch-disarm --id $WATCH_OLD"
NEW_JSON="$CREPO/docs/orchestration/state/waker/watches/$WATCH_NEW.json"
OLD_JSON="$CREPO/docs/orchestration/state/waker/watches/$WATCH_OLD.json"

if [ "$MODE" = "plan" ]; then
  plan "$ARM_CMD"
  plan "read back $NEW_JSON and require state=='armed' (whole field), params.tasks=='$TASKS_SPEC', action.type=='command', action.argv[0]=='$TARGET_PROGRAM'"
  plan "$DISARM_CMD    # ONLY after that readback passes"
else
  if [ -z "$NEW_STATE" ]; then
    act "$ARM_CMD"
    if ! remote "$ARM_CMD"; then
      die "watch-add $WATCH_NEW failed (rc=$R_RC): $R_OUT. $WATCH_OLD is UNTOUCHED and still the armed watch, which is the safe direction."
    fi
    read_ "watch-add reported: $R_OUT"
  else
    read_ "$WATCH_NEW already exists (state=[$NEW_STATE]); skipping watch-add and verifying the existing watch instead"
  fi
  # THE VERIFICATION IS THE READBACK, NOT THE EXIT STATUS (BEN-478).
  if ! remote_file "$READBACK" "$NEW_JSON" "$JOB_ID" "$TASKS_SPEC" "armed" "$TARGET_PROGRAM"; then
    indent "$R_OUT"
    die "readback of $WATCH_NEW FAILED (rc=$R_RC). $WATCH_OLD is still armed; NOTHING was retired."
  fi
  indent "$R_OUT"
  ok "(b1) $WATCH_NEW is armed on an EXISTING subject (job $JOB_ID tasks $TASKS_SPEC) with the command action"

  if [ "$OLD_STATE" = "disarmed" ]; then
    read_ "$WATCH_OLD is already state=[disarmed]; no retirement needed (idempotent)"
  else
    act "$DISARM_CMD"
    if ! remote "$DISARM_CMD"; then
      fail "watch-disarm $WATCH_OLD failed (rc=$R_RC): $R_OUT. BOTH watches are armed now -- noisy but SAFE, and the correct direction to fail in. Retry the disarm."
    else
      read_ "watch-disarm reported: $R_OUT"
    fi
  fi
  # r3's action is root-resume, so its argv[0]/action.type mismatch BY DESIGN; only the
  # state line is the subject here, and it is printed so the operator reads the value.
  if ! remote_file "$READBACK" "$OLD_JSON" "$JOB_ID" "$TASKS_SPEC" "disarmed" "$TARGET_PROGRAM"; then
    indent "$R_OUT"
    case "$R_OUT" in
      *"state='disarmed'"*)
        read_ "$WATCH_OLD state reads 'disarmed' (the other mismatches are by design: r3's action is root-resume)" ;;
      *)
        fail "$WATCH_OLD did NOT read back as disarmed" ;;
    esac
  else
    indent "$R_OUT"
  fi
  ok "(b2) add-then-retire complete: $WATCH_NEW was armed AND verified BEFORE $WATCH_OLD was retired"
fi

# ==================================== (c) RE-MEASURE THE FIVE RESOURCE FIELDS
# The five `NOT MEASURED` fields in state/gate5-do-train-array-active-57266000.json.
#
# THIS STEP WRITES THAT RECEIPT, on the mediator's instruction of 2026-08-19: a
# hand-transcribed number is the thing this campaign keeps having to re-derive. The receipt
# opens with a PROVENANCE block declaring that every value is either MEASURED (with the
# command and the time) or the literal string `NOT MEASURED`, never guessed -- so the writer
# is bound by that declaration rather than merely aware of it:
#
#   (i)   it replaces ONLY those five keys;
#   (ii)  it records the `scontrol` invocation and a UTC timestamp beside them, in a new
#         key, because a value without its command is the un-falsifiable form;
#   (iii) a field with no token in the output is written as the literal `NOT MEASURED` --
#         never null, never "", never "?";
#   (iv)  it touches no other key, and a test asserts the other 26 are byte-identical.
#
# THE DISTINCTION THE MEDIATOR ASKED FOR, MADE EXPLICIT: an unmeasurable field FAILS the
# step when there is nowhere honest to put that fact, and is RECORDED as `NOT MEASURED` when
# there is. For this receipt there is, so recording it beats failing -- an honest
# `NOT MEASURED` is information and a failed step is not. What still FAILS is a receipt that
# is missing, unparseable, or belongs to a different job.
#
# AND ONE RULE THE INSTRUCTION DID NOT NAME: NEVER DOWNGRADE. If a key already holds a
# measured value and this run finds no token for it, the existing value stands and the script
# says so. A writer that overwrites yesterday's measurement with `NOT MEASURED` because
# today's `scontrol` was thinner has destroyed evidence, which is the opposite of the
# receipt's purpose.
RECEIPT="$CREPO/docs/orchestration/state/gate5-do-train-array-active-$JOB_ID.json"
if ! remote "scontrol show job $JOB_ID"; then
  fail "(c) scontrol show job $JOB_ID failed (rc=$R_RC): $R_OUT"
else
  SCONTROL_OUT="$R_OUT"
  V_CPUS=""; V_MEM=""; V_TIME=""; V_QOS=""; V_GPUS=""
  for _tok in $SCONTROL_OUT; do
    case "$_tok" in
      NumCPUs=*)       V_CPUS="${_tok#NumCPUs=}" ;;
      CPUs/Task=*)     V_CPUS="${_tok#CPUs/Task=}" ;;
      MinMemoryNode=*) V_MEM="${_tok#MinMemoryNode=}" ;;
      MinMemoryCPU=*)  V_MEM="${_tok#MinMemoryCPU=}" ;;
      TimeLimit=*)     V_TIME="${_tok#TimeLimit=}" ;;
      QOS=*)           V_QOS="${_tok#QOS=}" ;;
      TresPerTask=*)   V_GPUS="${_tok#TresPerTask=}" ;;
      TresPerNode=*)   if [ -z "$V_GPUS" ]; then V_GPUS="${_tok#TresPerNode=}"; fi ;;
    esac
  done
  read_ "cpus_per_task=[$V_CPUS] memory_per_task=[$V_MEM] time_limit=[$V_TIME] qos=[$V_QOS] gpus_per_task=[$V_GPUS]"
  # An absent token is reported here and carried to the writer as an explicit sentinel, so
  # "no token" and "the empty string" cannot be confused on the way across.
  for _pair in "cpus_per_task:$V_CPUS" "memory_per_task:$V_MEM" "time_limit:$V_TIME" "qos:$V_QOS" "gpus_per_task:$V_GPUS"; do
    if [ -z "${_pair#*:}" ]; then
      say "NOTE  (c) ${_pair%%:*}: scontrol printed no such token. It will be written as the"
      say "NOTE      literal NOT MEASURED, or left alone if the receipt already holds a"
      say "NOTE      measured value -- never guessed and never downgraded."
    fi
  done
  ABSENT="@ABSENT@"
  A_CPUS="${V_CPUS:-$ABSENT}"; A_MEM="${V_MEM:-$ABSENT}"; A_TIME="${V_TIME:-$ABSENT}"
  A_QOS="${V_QOS:-$ABSENT}"; A_GPUS="${V_GPUS:-$ABSENT}"
  if ! remote "sacct -n -X -j ${JOB_ID}_${TASK_ID} -o JobIDRaw,State"; then
    fail "(c) sacct for ${JOB_ID}_${TASK_ID} failed (rc=$R_RC): $R_OUT"
  else
    read_ "sacct ${JOB_ID}_${TASK_ID}: $R_OUT"
    case "$R_OUT" in
      *PENDING*) read_ "${JOB_ID}_${TASK_ID} is still queued (PENDING)" ;;
      *) say "NOTE  ${JOB_ID}_${TASK_ID} is NOT pending any more: [$R_OUT]. The watch subject still exists, but the run has started or ended -- read the verdict from the logs, not from this script." ;;
    esac
  fi
  if [ "$MODE" = "plan" ]; then
    plan "write cpus_per_task/memory_per_task/time_limit/qos/gpus_per_task into $RECEIPT"
    plan "  -- only those five keys, plus a new resource_fields_remeasured provenance key;"
    plan "  -- an absent token becomes the literal 'NOT MEASURED'; a measured value is never downgraded"
  else
    cat > "$TMPD/receipt_write.py" <<'PYEOF'
"""Replace ONLY the five resource keys in the array-active receipt, and say what it did.

Bound by the receipt's own PROVENANCE block: every value is MEASURED (with the command and
the time) or the literal string `NOT MEASURED`. Never null, never "", never "?", never a
guess -- and never a DOWNGRADE of a value some earlier measurement established.
"""
import datetime as dt
import json
import os
import sys

FIELDS = ["cpus_per_task", "memory_per_task", "time_limit", "qos", "gpus_per_task"]
NOT_MEASURED = "NOT MEASURED"
ABSENT = "@ABSENT@"


def is_unmeasured(value):
    """Is this key's current content a PLACEHOLDER rather than a measurement?

    `NOT MEASURED` is the canonical form, but a receipt could hold any of the other ways a
    gap gets written down, and every one of them must normalise to the canonical literal
    rather than survive. Anything else is treated as a real measurement and is never
    overwritten -- so this predicate is exactly the line between (iii) and NEVER DOWNGRADE.
    """
    if value is None:
        return True
    return str(value).strip().lower() in {"", "?", "not measured", "unknown", "n/a", "tbd"}


path, job_id = sys.argv[1], sys.argv[2]
observed = dict(zip(FIELDS, sys.argv[3:8]))
if len(observed) != len(FIELDS):
    print("usage-error: expected %d values, got %d" % (len(FIELDS), len(sys.argv) - 3))
    sys.exit(11)

try:
    with open(path) as fh:
        receipt = json.load(fh)
except Exception as exc:                       # missing or unparseable: FAIL, never create
    print("receipt-unreadable: %s: %s" % (path, exc))
    sys.exit(12)

# THE RECEIPT MUST BE THIS JOB'S. A path is a definite description, and this one is
# constructed from a variable; the file itself declares its subject, so ask it.
if str(receipt.get("job_id", "")) != job_id:
    print("receipt-subject-mismatch: %s declares job_id=%r, expected %r"
          % (path, receipt.get("job_id"), job_id))
    sys.exit(13)
missing = [f for f in FIELDS if f not in receipt]
if missing:
    print("receipt-shape-mismatch: keys absent, so this is not the receipt this step "
          "was written for: %r" % (missing,))
    sys.exit(14)

before = {k: receipt[k] for k in FIELDS}
stamp = dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
command = "scontrol show job %s" % job_id
lines, changes = [], 0
for field in FIELDS:
    old, raw = receipt[field], observed[field]
    if raw == ABSENT:
        if not is_unmeasured(old):
            # NEVER DOWNGRADE: an earlier measurement outranks today's thinner output.
            lines.append("%s: NO TOKEN, but the receipt already holds %r -- LEFT ALONE "
                         "(a measured value is never replaced by %r)" % (field, old, NOT_MEASURED))
        elif old == NOT_MEASURED:
            lines.append("%s: NO TOKEN -> stays the literal %r" % (field, NOT_MEASURED))
        else:
            # A placeholder that is not the canonical literal: normalise it, so the receipt
            # says NOT MEASURED and never null, "" or "?".
            receipt[field] = NOT_MEASURED
            changes += 1
            lines.append("%s: NO TOKEN -> normalised placeholder %r to the literal %r"
                         % (field, old, NOT_MEASURED))
        continue
    if old == raw:
        lines.append("%s: already %r -- unchanged" % (field, raw))
        continue
    receipt[field] = raw
    changes += 1
    lines.append("%s: %r -> %r" % (field, old, raw))

if changes:
    # (ii) The values and their provenance land together. A number whose command and time
    # are not recorded beside it cannot be checked, which is what this receipt exists to fix.
    receipt["resource_fields_remeasured"] = {
        "measured_at_utc": stamp,
        "measured_by_command": command,
        "measured_on_host": os.uname().nodename,
        "written_by": "docs/orchestration/deploy_oi135_watcher_swap.sh step (c), OI-135",
        "fields": FIELDS,
        "semantics": ("Each field above is either the value this command printed, or the "
                      "literal string 'NOT MEASURED'. No field was guessed, and no "
                      "previously measured value was overwritten with 'NOT MEASURED'."),
        "NOTE_why_resources_not_measured_is_now_STALE": (
            "The pre-existing key `why_resources_not_measured` explains the ORIGINAL gap and "
            "still says to re-measure when the window ends. This writer deliberately did not "
            "edit it: it is prose owned by the receipt's author. Amend or retire it by hand."),
    }
    tmp = path + ".oi135.tmp"
    with open(tmp, "w") as fh:
        json.dump(receipt, fh, indent=2, ensure_ascii=False)
        fh.write("\n")
    os.replace(tmp, path)                      # atomic: no half-written receipt

for line in lines:
    print("field %s" % line)
print("changed=%d" % changes)
print("measured_at_utc=%s" % stamp)
print("measured_by_command=%s" % command)
print("receipt-write-ok" if changes else "receipt-write-noop")
PYEOF
    if ! remote_file "$TMPD/receipt_write.py" "$RECEIPT" "$JOB_ID" \
        "$A_CPUS" "$A_MEM" "$A_TIME" "$A_QOS" "$A_GPUS"; then
      fail "(c) could NOT write the receipt (rc=$R_RC): $R_OUT. The five values are printed above; nothing in the receipt was changed."
      indent "$R_OUT"
    else
      indent "$R_OUT"
      ok "(c) receipt updated in place: only the five resource keys, each MEASURED or the literal NOT MEASURED, with the command and UTC time recorded beside them"
      say "NOTE  \`why_resources_not_measured\` was left untouched and now reads stale."
      say "NOTE      It is prose owned by the receipt's author; amend it by hand."
    fi
  fi
fi

# ==================================== (d) CLUSTER WORKTREE HYGIENE
if ! remote "git -C $CREPO worktree list"; then
  fail "(d) git worktree list failed (rc=$R_RC): $R_OUT"
else
  read_ "cluster worktrees:"
  indent "$R_OUT"
  case "$R_OUT" in
    *"$DANGLING_WT"*)
      say "NOTE  the aborted regeneration DID register $DANGLING_WT"
      if [ "$MODE" = "plan" ]; then
        plan "git -C $CREPO worktree prune   # only if $DANGLING_WT holds no work"
      else
        if ! remote "test -d $DANGLING_WT"; then
          act "git -C $CREPO worktree prune"
          if ! remote "git -C $CREPO worktree prune"; then
            fail "(d) worktree prune failed (rc=$R_RC): $R_OUT"
          else
            read_ "pruned the registration of $DANGLING_WT (its directory did not exist)"
          fi
        elif ! remote "git -C $DANGLING_WT status --porcelain"; then
          fail "(d) $DANGLING_WT exists but its status is unreadable (rc=$R_RC): $R_OUT"
        elif [ -n "$R_OUT" ]; then
          fail "(d) $DANGLING_WT exists and is DIRTY; NOT removing it. Preserve the diff first: [$R_OUT]"
        else
          say "NOTE  $DANGLING_WT exists on disk and is clean. Removing a real directory is not"
          say "NOTE      this script's call: git -C $CREPO worktree remove $DANGLING_WT"
        fi
      fi
      ;;
    *) read_ "no registration for $DANGLING_WT -- the aborted regeneration never ran, as suspected" ;;
  esac
fi

# ==================================== (e) REGENERATE LIVE-STATE.md
GEN_CMD="cd $CREPO && $REMOTE_PY docs/orchestration/generate_live_state.py"
if [ "$DO_REGEN" != "yes" ]; then
  plan "$GEN_CMD    # step (e), OFF by default: pass --regen-live-state to run it"
  say "NOTE  (e) is opt-in because it writes LIVE-STATE.md inside a checkout 98 commits"
  say "NOTE      behind main, so the GENERATOR is the stale one unless it was deployed too."
  say "NOTE      Regenerating from the current tree is usually the right move instead."
elif [ "$MODE" = "plan" ]; then
  plan "$GEN_CMD    # --regen-live-state given, but mode is plan"
else
  if ! remote "test -f $CREPO/docs/orchestration/generate_live_state.py"; then
    fail "(e) generate_live_state.py is absent from the cluster checkout; not regenerating"
  else
    act "$GEN_CMD"
    if ! remote "$GEN_CMD"; then
      fail "(e) generate_live_state.py failed (rc=$R_RC): $R_OUT"
    else
      read_ "generator output: $R_OUT"
    fi
  fi
fi

# =========================================================================== VERDICT
if [ "$MODE" = "plan" ]; then
  say "=== PLAN COMPLETE: every precondition above was READ; nothing was mutated."
  say "=== Re-run with --execute for (a)-(d) and (f); add --regen-live-state for (e)."
  exit 0
fi
if [ "$FAILED" -ne 0 ]; then
  printf '%s\n' "=== INCOMPLETE: at least one step FAILED above. The watch swap is the" >&2
  printf '%s\n' "=== ordering-critical part and it reports its own state; re-read the (b)" >&2
  printf '%s\n' "=== lines before retrying anything." >&2
  exit 1
fi
say "=== DONE: every step verified by readback."
exit 0

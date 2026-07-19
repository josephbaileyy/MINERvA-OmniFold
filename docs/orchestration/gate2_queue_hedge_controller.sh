#!/usr/bin/env bash
# OS-detached Gate-2 queue hedge and one-shot terminal-event resume.
# This process, not Codex, waits for allocation/job state changes.
set -euo pipefail

repo=${GATE2_REPO:-/pscratch/sd/j/josephrb/MINERvA-OmniFold}
state_dir=${GATE2_STATE_DIR:-${repo}/docs/orchestration/state}
batch_job=${GATE2_BATCH_JOB_ID:-}
thread_id=${GATE2_THREAD_ID:-019f749a-857b-7790-8cec-bc36b22908be}
run_id=${GATE2_HEDGE_RUN_ID:-}
codex_home=${GATE2_CODEX_HOME:-/global/u2/j/josephrb/codex-homes/personal}
codex_bin=${GATE2_CODEX_BIN:-$(command -v codex 2>/dev/null || true)}
poll_seconds=${GATE2_POLL_SECONDS:-60}

validator=${repo}/nd-unfolding/pet/gate2_target_runtime.py
runner=${repo}/nd-unfolding/pet/run_gate2_target_validator.sh
alloc=${repo}/alloc_run.sh
inputs=${repo}/nd-unfolding/g2_fullevent/input/G2_FPS_MEFHC_P12.npz
producer_receipt=${repo}/nd-unfolding/g2_fullevent/input/G2_FPS_MEFHC_P12_RECEIPT.json
independent_receipt=${repo}/docs/orchestration/state/g2-gate1b-npz-validation-20260719.json
final_receipt=${repo}/nd-unfolding/g2_fullevent/gate2/final/G2_GATE2_TARGET_RUNTIME_RECEIPT.json
final_weights=${repo}/nd-unfolding/g2_fullevent/gate2/final/G2_NEGWEIGHT_REFINED_EXACT_NORMALIZED.npy
benchmark_dir=${repo}/nd-unfolding/g2_fullevent/gate2/benchmark/${run_id}
benchmark_receipt=${GATE2_BENCHMARK_RECEIPT_REUSE:-${benchmark_dir}/G2_GATE2_BENCHMARK.json}
reuse_benchmark=${GATE2_BENCHMARK_RECEIPT_REUSE:-}
benchmark_log=${benchmark_dir}/benchmark.log
decision=${state_dir}/${run_id}-decision.json
event=${state_dir}/${run_id}-wakeup.json
invoked=${state_dir}/${run_id}-resume.invoked
done=${state_dir}/${run_id}-resume.done
resume_log=${state_dir}/${run_id}-resume.log
lock=${state_dir}/${run_id}-controller.lock

expected_validator_sha=453719b324e41c1e9fcdf8a6081a7aaefc685120023e41c14f116b50293cf92f
expected_runner_sha=ade81850600c4a222c743905208b2388abd1dcafc29a1538af3ae44473d44374

fail() { printf '[gate2-hedge][FAIL] %s\n' "$*" >&2; exit 126; }
occupied() { [[ -e "$1" || -L "$1" ]]; }
sha_of() { sha256sum "$1" | awk '{print $1}'; }

job_state() {
  local value
  value=$(squeue -h -j "$batch_job" -o '%T' 2>/dev/null | head -n1 || true)
  if [[ -n "$value" ]]; then printf '%s\n' "$value"; return; fi
  value=$(sacct -X -n -P -j "$batch_job" --format=JobIDRaw,State 2>/dev/null \
    | awk -F'|' -v j="$batch_job" '$1==j {sub(/\+.*/,"",$2); sub(/[[:space:]].*/,"",$2); print $2; exit}')
  printf '%s\n' "${value:-UNKNOWN}"
}

job_exit_code() {
  sacct -X -n -P -j "$batch_job" --format=JobIDRaw,ExitCode 2>/dev/null \
    | awk -F'|' -v j="$batch_job" '$1==j {print $2; exit}'
}

parse_slurm_time() {
  /usr/bin/python3.11 - "$1" <<'PY'
import sys
s=sys.argv[1].strip(); days=0
if '-' in s:
    d,s=s.split('-',1); days=int(d)
p=[int(x) for x in s.split(':')]
if len(p)==3: h,m,sec=p
elif len(p)==2: h=0; m,sec=p
else: h=0; m=0; sec=p[0]
print(days*86400+h*3600+m*60+sec)
PY
}

write_decision() {
  local route=$1 reason=$2 holder=$3 batch_state=$4 bench_rc=$5 projected=$6 remaining=$7 cancel_state=$8
  /usr/bin/python3.11 - "$decision" "$route" "$reason" "$holder" "$batch_job" "$batch_state" \
    "$bench_rc" "$projected" "$remaining" "$cancel_state" "$benchmark_receipt" "$run_id" <<'PY'
import datetime,json,os,sys,tempfile
(out,route,reason,holder,batch,batch_state,bench_rc,projected,remaining,cancel_state,
 benchmark,run_id)=sys.argv[1:13]
def num(x):
    try:return float(x)
    except:return None
d={"schema_version":1,"recorded_at_utc":datetime.datetime.now(datetime.timezone.utc).isoformat(),
   "run_id":run_id,"selected_final_route":route,"reason":reason,
   "interactive_holder_job_id":holder or None,"batch_job_id":batch,
   "batch_state_at_decision":batch_state,"benchmark_rc":int(bench_rc),
   "projected_full_seconds_safe":num(projected),"interactive_seconds_remaining":num(remaining),
   "batch_cancellation_state":cancel_state,"benchmark_receipt":benchmark,
   "namespace_separation":{"benchmark":"run-id-specific; never final",
       "final":"shared flock; weights first and receipt last"},
   "pet_training_started":False}
os.makedirs(os.path.dirname(out),exist_ok=True)
fd,tmp=tempfile.mkstemp(prefix="."+os.path.basename(out)+".",dir=os.path.dirname(out))
with os.fdopen(fd,"w") as f:json.dump(d,f,indent=2,sort_keys=True);f.write("\n");f.flush();os.fsync(f.fileno())
os.link(tmp,out);os.unlink(tmp)
PY
}

write_event() {
  local event_type=$1 final_route=$2 terminal_state=$3 exit_code=$4 exact_rc=$5 holder=$6
  /usr/bin/python3.11 - "$event" "$event_type" "$final_route" "$terminal_state" "$exit_code" \
    "$exact_rc" "$holder" "$batch_job" "$decision" "$benchmark_receipt" "$final_receipt" \
    "$final_weights" "$thread_id" "$run_id" "$repo" <<'PY'
import datetime,hashlib,json,os,subprocess,sys,tempfile
(out,event_type,route,state,exit_code,exact_rc,holder,batch,decision,benchmark,
 final_receipt,final_weights,thread,run_id,repo)=sys.argv[1:16]
def evidence(path):
    d={"path":path,"exists":os.path.isfile(path),"is_symlink":os.path.islink(path)}
    if d["exists"] and not d["is_symlink"]:
        h=hashlib.sha256()
        with open(path,"rb") as f:
            for block in iter(lambda:f.read(16*1024*1024),b""):h.update(block)
        d.update({"sha256":h.hexdigest(),"size_bytes":os.path.getsize(path)})
    return d
d={"schema_version":1,"observed_at_utc":datetime.datetime.now(datetime.timezone.utc).isoformat(),
   "event":event_type,"selected_final_route":route,"terminal_state":state,
   "exit_code":exit_code,"interactive_exact_rc":None if exact_rc=="none" else int(exact_rc),
   "interactive_holder_job_id":holder or None,"batch_job_id":batch,"thread_id":thread,
   "watcher_run_id":run_id,"decision":evidence(decision),"benchmark":evidence(benchmark),
   "final_receipt":evidence(final_receipt),"final_weights":evidence(final_weights),
   "pet_training_started":False}
try:d["head_at_event"]=subprocess.check_output(["git","-C",repo,"rev-parse","HEAD"],text=True).strip()
except Exception:d["head_at_event"]="UNKNOWN"
os.makedirs(os.path.dirname(out),exist_ok=True)
fd,tmp=tempfile.mkstemp(prefix="."+os.path.basename(out)+".",dir=os.path.dirname(out))
with os.fdopen(fd,"w") as f:json.dump(d,f,indent=2,sort_keys=True);f.write("\n");f.flush();os.fsync(f.fileno())
os.link(tmp,out);os.unlink(tmp)
PY
}

preflight() {
  [[ "$batch_job" =~ ^[0-9]+$ ]] || fail "invalid/missing batch job ID"
  [[ "$thread_id" =~ ^[0-9a-fA-F-]{36}$ ]] || fail "invalid thread ID"
  [[ "$run_id" =~ ^[A-Za-z0-9._-]+$ ]] || fail "invalid/missing run ID"
  [[ "$poll_seconds" =~ ^[1-9][0-9]*$ ]] || fail "invalid poll interval"
  [[ -d "$codex_home" ]] || fail "personal CODEX_HOME missing: $codex_home"
  [[ -n "$codex_bin" && "$codex_bin" = /* && -x "$codex_bin" ]] || fail "Codex path missing/not absolute/executable"
  [[ -x "$validator" && "$(sha_of "$validator")" == "$expected_validator_sha" ]] || fail "validator hash/executable mismatch"
  [[ -x "$runner" && "$(sha_of "$runner")" == "$expected_runner_sha" ]] || fail "runner hash/executable mismatch"
  [[ -x "$alloc" ]] || fail "alloc_run.sh missing/not executable"
  for path in "$inputs" "$producer_receipt" "$independent_receipt"; do
    [[ -f "$path" && ! -L "$path" ]] || fail "invalid prerequisite: $path"
  done
  if [[ -n "$reuse_benchmark" ]]; then
    [[ "$reuse_benchmark" = /* && -f "$reuse_benchmark" && ! -L "$reuse_benchmark" ]] \
      || fail "reused benchmark is missing/non-absolute/symlink"
    /usr/bin/python3.11 - "$reuse_benchmark" <<'PY' || fail "reused benchmark receipt failed validation"
import json,sys
d=json.load(open(sys.argv[1]))
assert d["status"]=="PASS"
assert d["mode"]=="benchmark-only-no-final-writer"
assert d["input_preflight"]["sha256"]=="fa6b3463160242164a2c6506c787d09194d0715d2bd64e24dba771c8f2a29625"
assert d["configuration"]["estimator"]=="exact"
assert d["configuration"]["features"]==["pt","pparallel"]
assert d["configuration"]["refinement_random_state"]==45
PY
  fi
  for bin in flock squeue sacct scancel setsid sha256sum; do command -v "$bin" >/dev/null || fail "$bin missing"; done
  "$codex_bin" exec resume --help >/dev/null || fail "codex exec resume preflight failed"
  state=$(job_state)
  [[ "$state" != UNKNOWN ]] || fail "batch job $batch_job is not observable"
  for marker in "$decision" "$event" "$invoked" "$done"; do occupied "$marker" && fail "occupied marker: $marker"; done
  occupied "$final_receipt" && fail "final receipt already occupied"
  occupied "$final_weights" && fail "final weights already occupied"
  mkdir -p "$state_dir" "$benchmark_dir"
}

preflight
if [[ "${1:-}" == --preflight-only ]]; then
  printf 'PASS job=%s state=%s thread=%s codex=%s CODEX_HOME=%s run=%s\n' \
    "$batch_job" "$(job_state)" "$thread_id" "$codex_bin" "$codex_home" "$run_id"
  exit 0
fi

cd "$repo"
exec 9>"$lock"
flock -n 9 || fail "another controller owns $lock"

if [[ -n "$reuse_benchmark" ]]; then
  # Acquire a fresh holder without spending another exact benchmark fit. The
  # reused receipt is immutable and preflighted above.
  benchmark_cmd="true"
else
  benchmark_cmd="python3 '${validator}' benchmark --inputs '${inputs}' --producer-receipt '${producer_receipt}' --independent-receipt '${independent_receipt}' --output '${benchmark_receipt}' --sample-rows 250000 --sample-seed 20260719 --safety-factor 2.0"
fi
set +e
ALLOC_HOLD_SECONDS=10800 ALLOC_CPUS=128 "$alloc" "$benchmark_cmd" >"$benchmark_log" 2>&1
benchmark_rc=$?
set -e

holder=$(squeue --me --name=claude-hold -t R -h -o '%i' | head -n1 || true)
remaining=0
if [[ -n "$holder" ]]; then
  remaining_raw=$(squeue -h -j "$holder" -o '%L' | head -n1 || true)
  [[ -z "$remaining_raw" ]] || remaining=$(parse_slurm_time "$remaining_raw")
fi
projected=unknown
if [[ "$benchmark_rc" == 0 && -s "$benchmark_receipt" ]]; then
  projected=$(/usr/bin/python3.11 - "$benchmark_receipt" <<'PY'
import json,sys
d=json.load(open(sys.argv[1])); assert d["status"]=="PASS"
print(d["timing"]["projected_full_seconds_safe"])
PY
  )
fi

batch_state=$(job_state)
route=batch
reason=benchmark_or_allocation_failed
cancel_state=not-attempted
if [[ "$benchmark_rc" == 0 && -n "$holder" && "$projected" != unknown ]]; then
  if [[ "$batch_state" == RUNNING ]]; then
    reason=batch-already-running
  elif [[ "$batch_state" == CANCELLED && -n "$reuse_benchmark" ]]; then
    # Recovery of a previously confirmed --state=PENDING cancellation. Require
    # sacct to prove the batch never started before selecting interactive exact.
    batch_start=$(sacct -X -n -P -j "$batch_job" --format=JobIDRaw,Start \
      | awk -F'|' -v j="$batch_job" '$1==j {print $2; exit}')
    safe=$(/usr/bin/python3.11 - "$projected" "$remaining" <<'PY'
import sys
print(int(float(sys.argv[1])+900.0 < float(sys.argv[2])))
PY
    )
    if [[ "$batch_start" == None && "$safe" == 1 ]]; then
      route=interactive
      reason=reused-benchmark-safe-and-prior-pending-cancel-proven
      cancel_state=confirmed-pending-cancel-sacct-start-none
    else
      reason=prior-cancel-or-fresh-wall-not-safe
    fi
  elif [[ "$batch_state" == COMPLETED || "$batch_state" == FAILED || "$batch_state" == CANCELLED || "$batch_state" == TIMEOUT || "$batch_state" == OUT_OF_MEMORY ]]; then
    reason=batch-already-terminal
  elif [[ "$batch_state" == PENDING ]]; then
    safe=$(/usr/bin/python3.11 - "$projected" "$remaining" <<'PY'
import sys
# Keep 15 minutes beyond the already safety-inflated estimate.
print(int(float(sys.argv[1])+900.0 < float(sys.argv[2])))
PY
    )
    if [[ "$safe" == 1 ]]; then
      scancel --state=PENDING "$batch_job" || true
      cancel_state=unconfirmed
      for _ in $(seq 1 20); do
        batch_state=$(job_state)
        case "$batch_state" in
          CANCELLED) cancel_state=confirmed-pending-cancel; break ;;
          RUNNING) cancel_state=lost-race-batch-running; break ;;
          COMPLETED|FAILED|TIMEOUT|OUT_OF_MEMORY) cancel_state=batch-terminal-before-cancel; break ;;
        esac
        sleep 2
      done
      if [[ "$cancel_state" == confirmed-pending-cancel ]]; then
        route=interactive
        reason=benchmark-safe-and-pending-batch-cancelled
      else
        route=batch
        reason=batch-won-cancellation-race
      fi
    else
      reason=benchmark-projection-exceeds-safe-interactive-wall
    fi
  else
    reason=batch-state-not-safely-cancellable
  fi
fi

write_decision "$route" "$reason" "$holder" "$batch_state" "$benchmark_rc" "$projected" "$remaining" "$cancel_state"

exact_rc=none
terminal_state=
exit_code=
event_type=
if [[ "$route" == interactive ]]; then
  exact_cmd="env GATE2_EXECUTION_ROUTE=interactive GATE2_RUN_ID='${run_id}-interactive' '${runner}'"
  set +e
  ALLOC_HOLD_SECONDS=10800 ALLOC_CPUS=128 "$alloc" "$exact_cmd" >>"$benchmark_log" 2>&1
  exact_rc=$?
  set -e
  "$alloc" --end >>"$benchmark_log" 2>&1 || true
  terminal_state=$([[ "$exact_rc" == 0 ]] && printf COMPLETED || printf FAILED)
  exit_code="${exact_rc}:0"
  event_type=$([[ "$exact_rc" == 0 ]] && printf gate2-interactive-complete || printf gate2-interactive-error)
else
  [[ -z "$holder" ]] || "$alloc" --end >>"$benchmark_log" 2>&1 || true
  unreliable=0
  while :; do
    batch_state=$(job_state)
    case "$batch_state" in
      COMPLETED|FAILED|CANCELLED|TIMEOUT|OUT_OF_MEMORY|NODE_FAIL|PREEMPTED|BOOT_FAIL|DEADLINE)
        terminal_state=$batch_state; exit_code=$(job_exit_code); break ;;
      PENDING|RUNNING|CONFIGURING|COMPLETING) unreliable=0 ;;
      UNKNOWN) unreliable=$((unreliable+1)) ;;
      *) unreliable=$((unreliable+1)) ;;
    esac
    if (( unreliable >= 10 )); then
      terminal_state=MONITOR_ERROR; exit_code=unknown; break
    fi
    sleep "$poll_seconds"
  done
  if [[ "$terminal_state" == COMPLETED && "$exit_code" == 0:0 ]]; then
    event_type=gate2-batch-complete
  elif [[ "$terminal_state" == MONITOR_ERROR ]]; then
    event_type=gate2-monitor-error
  else
    event_type=gate2-batch-error
  fi
fi

write_event "$event_type" "$route" "$terminal_state" "${exit_code:-unknown}" "$exact_rc" "$holder"
tmp=$(mktemp "${state_dir}/.${run_id}-invoked.XXXXXX")
{
  printf 'invoked_at_utc=%s\n' "$(date -u +%Y-%m-%dT%H:%M:%SZ)"
  printf 'event_sha256=%s\n' "$(sha_of "$event")"
  printf 'event_type=%s\n' "$event_type"
  printf 'thread_id=%s\n' "$thread_id"
  printf 'codex_path=%s\n' "$codex_bin"
  printf 'codex_home=%s\n' "$codex_home"
} >"$tmp"
ln "$tmp" "$invoked" || fail "invoked marker race"
rm -f "$tmp"

prompt="A real terminal Gate-2 queue-hedge event occurred. Read docs/orchestration/state/${run_id}-wakeup.json exactly once and validate it; do not poll or enter a bounded wait. Preserve every worker UUID and use the personal CODEX_HOME already selected by the watcher. Do not consume or suggest a reset credit. Reconcile batch job ${batch_job}, the benchmark/route decision, final logs, collision lock, and any published weights/receipt. If the exact runtime completed successfully, independently validate its hash-bound configuration, learned-refinement and binned telemetry, then resume the existing agy-g2-gate-verifier UUID for the independent Gate-2 promotion verdict and the existing Agent-B UUID only if an owner receipt correction is needed. Apply the commit gate with scoped ledger/RUN_LOG/STATUS evidence only after PASS. If it failed, record the exact blocker and make no unchanged retry. PET training and the next remediation gate remain prohibited in this wake. Run a complete usage snapshot before any provider dispatch and before final synthesis. Goals remain disabled; do not process this event twice."
set +e
CODEX_HOME="$codex_home" "$codex_bin" exec resume \
  --disable goals \
  --dangerously-bypass-approvals-and-sandbox \
  "$thread_id" "$prompt" >>"$resume_log" 2>&1
resume_rc=$?
set -e
tmp=$(mktemp "${state_dir}/.${run_id}-done.XXXXXX")
printf 'completed_at_utc=%s\nresume_rc=%s\nevent_type=%s\nthread_id=%s\n' \
  "$(date -u +%Y-%m-%dT%H:%M:%SZ)" "$resume_rc" "$event_type" "$thread_id" >"$tmp"
ln "$tmp" "$done" || fail "done marker race"
rm -f "$tmp"
exit "$resume_rc"

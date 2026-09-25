#!/bin/bash
# Run a committed queue of s5c launches in order, one allocation at a time, so a lane keeps its slot
# filled without an operator, and keeps going if the operator's cluster login lapses.
#
# Usage (login node, under nohup):  s5c_queue.sh <queue_file> <stop_file> [<after_pid>]
# Each non-comment, non-blank line is a command run by bash from $NS (a launcher invocation). A line
# that prints "LAUNCHED job=<id>" is followed until the job leaves the queue, then the next line
# runs; exit 0 without a launch just completes the line. Exit 4 (meter: refused by concurrency) is retried every 5 minutes; exit 7 (not granted) up
# to 12 times; any other outcome stops the queue. A validation line (one invoking
# s5c_valid_launch.sh) is SKIPPED while <stop_file> exists (the futility gate writes it); other lines
# still run. With <after_pid>, the queue first waits for that process (a previous queue) to exit.
# Admission, pricing and every guard stay in the meter and the launchers; this adds no spend path.

Q=${1:?queue file}; STOP=${2:?stop file}; AFTER=${3:-}
NS=${S5C_NS:-/pscratch/sd/j/josephrb/s5c-20260924}
POLL=${S5C_QUEUE_POLL:-60}; RETRY=${S5C_QUEUE_RETRY:-300}   # seconds (overridable for tests)
stamp() { date -u +%FT%TZ; }
log() { echo "[queue] $(stamp) $*"; }

if [ -n "$AFTER" ]; then
    log "waiting for pid $AFTER"
    while kill -0 "$AFTER" 2>/dev/null; do sleep "$POLL"; done
fi
# A committed queue names its own deploy tree and pin through S5C_DEPLOY / S5C_PIN (a file cannot
# name the commit that adds it): taken from the checkout holding the queue file, which must be clean.
if top=$(git -C "$(dirname "$Q")" rev-parse --show-toplevel 2>/dev/null); then
    [ -z "$(git -C "$top" status --porcelain --untracked-files=no)" ] || { log "refusing: $top is not clean"; exit 2; }
    export S5C_DEPLOY="$top" S5C_PIN=$(git -C "$top" rev-parse HEAD)
fi
log "start queue=$Q stop=$STOP deploy=${S5C_DEPLOY:-none} pin=${S5C_PIN:-none}"
cd "$NS" || exit 2
n=0
while IFS= read -r line || [ -n "$line" ]; do
    n=$((n + 1))
    case "$line" in ''|'#'*) continue ;; esac
    if [[ "$line" == *s5c_valid_launch.sh* && -e "$STOP" ]]; then
        log "line $n SKIPPED (stop file present): $line"
        continue
    fi
    tries7=0
    while :; do
        log "line $n run: $line"
        out=$(bash -c "$line" 2>&1 < /dev/null)
        rc=$?
        echo "$out" | sed 's/^/    /'
        job=$(echo "$out" | sed -n 's/.*LAUNCHED job=\([0-9]*\).*/\1/p' | head -1)
        if [ -n "$job" ]; then
            log "line $n launched job $job; following it"
            while :; do
                ids=$(squeue -h --me -o %i 2>/dev/null) || { sleep "$POLL"; continue; }
                echo "$ids" | grep -qx "$job" || break
                sleep "$POLL"
            done
            log "line $n job $job left the queue"
            break
        elif [ "$rc" -eq 0 ]; then
            log "line $n done (exit 0, nothing launched)"
            break
        elif [ "$rc" -eq 4 ]; then
            sleep "$RETRY"
        elif [ "$rc" -eq 7 ] && [ "$tries7" -lt 12 ]; then
            tries7=$((tries7 + 1)); sleep "$RETRY"
        else
            log "line $n STOPPED the queue (exit $rc)"
            exit 1
        fi
    done
done < "$Q"
log "queue done"

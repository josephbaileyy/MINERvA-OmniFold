#!/bin/bash
# RE-2 part B launcher test: run re2b_job.sbatch's lane() over every job and lane of partb_runs.tsv with a stub srun
# that READS ALL STDIN, as real srun forwards it (part A's test_lane_stdin.sh). Usage: bash run/launch/test_lane_stdin_b.sh
# (bash >= 4). PASS when every row is called exactly once, with its own label, CPUs and --out, and its output is
# digested in its own lane's SHA256SUMS.<job>.<lane>. The table is protected twice (read on fd 3; srun's stdin is
# /dev/null): either guard alone keeps all 644 calls, so this test fails only if both are lost (35 of 644).
set -eo pipefail
W=$(mktemp -d); trap 'rm -rf "$W"' EXIT
cd "$(dirname "$0")/.."; cp partb_runs.tsv "$W/"; RUNS=$W/partb_runs.tsv; O=$W/o; C=/deploy; mkdir -p "$O/out" "$O/logs"
export CV=/x/cv MC=/x/mc UNI=/x/uni FLUXU=/x/fu ACT=/x/act P=/x/p
srun() {
    cat > /dev/null
    local cpus="" name="" out="" prev=""
    for a in "$@"; do
        case "$prev" in -c) cpus=$a;; --out) out=$a;; esac
        case "$a" in --job-name=*) name=${a#--job-name=};; esac
        prev=$a
    done
    echo "$name $cpus $out" >> "$W/calls"
    : > "$out"
}
eval "$(sed -n '/^lane() {/,/^}/p' launch/re2b_job.sbatch)"
set -u
for JOB in $(tail -n +2 "$RUNS" | cut -f1 | sort -u); do
    for l in $(awk -F'\t' -v j="$JOB" 'NR > 1 && $1 == j {print $2}' "$RUNS" | sort -u); do lane "$l" || true; done
done
awk -F'\t' -v o="$O/out" 'NR > 1 {print $3, $4, o "/" $3 "/xsec.root"}' "$RUNS" | sort > "$W/want"
sort "$W/calls" > "$W/got"
n=$(wc -l < "$W/got"); rows=$(wc -l < "$W/want"); echo "calls=$n rows=$rows"
awk -F'\t' 'NR > 1 {n = split($2, p, "."); print "SHA256SUMS." $1 "." p[n], $3 "/xsec.root"}' "$RUNS" | sort > "$W/want_sums"
for f in "$O"/SHA256SUMS.*; do awk -v f="${f##*/}" '{print f, $2}' "$f"; done | sort > "$W/got_sums"
diff "$W/want" "$W/got" && [ "$n" -eq "$rows" ] && diff "$W/want_sums" "$W/got_sums" \
    && echo "sums=$(wc -l < "$W/got_sums")" && echo "test_lane_stdin_b: PASS"

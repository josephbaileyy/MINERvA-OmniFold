#!/bin/bash
# test_sacct_fence.sh: the rpd_flux4 connect's step-2 fence, cut from rpd_flux4_connect.sh itself, against a stub sacct,
# then each mutant of the block against the same cases. flux3's block tightens flux2's: an empty or padded JobName, or an
# empty State, refuses, and the family match is case-insensitive (the director's acceptance of P0 finding 8). flux4's
# block also watches geanttw* jobs (no e1 connect while a geanttw_ job is live; the director, 2026-11-26).
# usage: bash test_sacct_fence.sh        (runs anywhere; date and sacct are shell-function stubs, nothing is contacted)
# The stub behaves like Slurm's sacct for a non-root user: without -S it lists only jobs since midnight, so a job
# RUNNING since yesterday is omitted; with -S it is listed. It can also write to stderr while exiting 0. Each case
# states the expected fence outcome and rc. Every mutant must fail at least one case.
set -u
HERE=$(cd "$(dirname "$0")" && pwd)
BLOCK=$(awk '/^start=\$\(date -u -d .14 days ago/ {f=1} f {print} f && /^\[ "\$rc" -eq 0 \] \|\|/ {exit}' "$HERE/../rpd_flux4_connect.sh")
[ "$(printf '%s\n' "$BLOCK" | wc -l | tr -d ' ')" -ge 12 ] || { echo "SETUP: could not cut the fence block from the connect"; exit 9; }
NO_S=$(printf '%s' "$BLOCK" | sed 's/ -S "$start"//')
[ "$NO_S" != "$BLOCK" ] || { echo "SETUP: could not strip -S from the block"; exit 9; }
printf '%s\n' "$BLOCK" | grep -q -- "-u josephrb" || { echo "FAIL: the block does not name the user"; exit 1; }
printf '%s\n' "$BLOCK" | grep -q -- " -s " && { echo "FAIL: the block filters states with -s"; exit 1; }
printf '%s\n' "$BLOCK" | grep -q -- "squeue" && { echo "FAIL: the block calls squeue"; exit 1; }
printf '%s\n' "$BLOCK" | grep -qF 'tolower($2) ~ /^(cov2d|t2a|rpd|geanttw)/' || { echo "FAIL: the block's family match is not case-insensitive"; exit 1; }
echo "ok   the block is cut from rpd_flux4_connect.sh and carries flux3's tightening and the geanttw family"
ARGS=$(mktemp) || exit 9; export ARGS; trap 'rm -f -- "$ARGS"' EXIT

# run BLOCK ROWS_SINCE_MIDNIGHT ROWS_BEFORE_MIDNIGHT SACCT_RC [STDERR [DATE_OUT]] -> prints output; ARGS holds sacct's args
run() {
  : > "$ARGS"
  bash -c "
    finish() { echo \"rc=\$1\"; exit \"\$1\"; }
    date() { [ \"\$*\" = \"-u -d 14 days ago +%F\" ] && { echo '${6:-2026-11-08}'; return 0; }; command date \"\$@\"; }
    sacct() {
      printf '%s\n' \"\$*\" > \"\$ARGS\"
      printf '%b' '${5:-}' >&2
      [ $4 -eq 0 ] || return $4
      printf '%b' '$2'
      case \" \$* \" in *' -S '*) printf '%b' '$3' ;; esac
    }
    $1
    echo 'FENCE: clear'; echo rc=0"
}

check() {  # check NAME EXPECTED_RC EXPECTED_LINE OUTPUT
  rc=$(printf '%s\n' "$4" | sed -n 's/^rc=//p' | tail -1)
  if [ "$rc" = "$2" ] && printf '%s\n' "$4" | grep -qF -- "$3"; then
    [ "$QUIET" = 1 ] || echo "ok   $1 (rc $rc)"
  else
    [ "$QUIET" = 1 ] || { echo "FAIL $1: rc [$rc], want $2 and [$3]"; printf '%s\n' "$4" | sed 's/^/     /'; }
    fails=$((fails + 1))
  fi
}

YESTERDAY='61300001|cov2d_xk|RUNNING\n'
TODAY='61300100|other_job|COMPLETED\n'
MALFORMED="STOP: a cov2d/t2a/rpd/geanttw job is unended, or a sacct line is malformed"

cases() {  # cases BLOCK NO_S_BLOCK: every case; counts failures in $fails
  local B=$1 N=$2 out
  out=$(run "$B" "$TODAY" "$YESTERDAY" 0)
  check "running since yesterday, with -S: STOP" 3 "STOP: a cov2d/t2a/rpd/geanttw job is unended" "$out"
  if grep -q -- "-u josephrb -S 2026-11-08 " "$ARGS"; then [ "$QUIET" = 1 ] || echo "ok   sacct called with -u josephrb -S 2026-11-08"
  else [ "$QUIET" = 1 ] || echo "FAIL sacct arguments: $(cat "$ARGS")"; fails=$((fails + 1)); fi

  out=$(run "$N" "$TODAY" "$YESTERDAY" 0)
  check "running since yesterday, -S removed: omitted, reads CLEAR (the hazard -S closes)" 0 "FENCE: clear" "$out"

  out=$(run "$B" '1|cov2d_a|COMPLETED\n2|rpd_flux1|CANCELLED by 123\n3|t2a_x|FAILED\n4|other|RUNNING\n61300200_3|rpd_arr|TIMEOUT\n61300201+0|rpd_het|COMPLETED\n' '5|rpd_c0|TIMEOUT\n' 0)
  check "terminal states only (incl CANCELLED by, TIMEOUT, array and het ids), unrelated job running: CLEAR" 0 "FENCE: clear" "$out"

  out=$(run "$B" '' '' 0)
  check "no rows: CLEAR" 0 "sacct rows (14 days): 0" "$out"

  out=$(run "$B" '' '6|t2a_y|PENDING\n' 0)
  check "t2a PENDING before midnight: STOP" 3 "STOP: a cov2d/t2a/rpd/geanttw job is unended" "$out"

  out=$(run "$B" '7|rpd_flux4|REQUEUED\n' '' 0)
  check "rpd REQUEUED: STOP" 3 "STOP: a cov2d/t2a/rpd/geanttw job is unended" "$out"

  out=$(run "$B" '8|cov2d_q|COMPLETING\n' '' 0)
  check "cov2d COMPLETING (state outside the closed set, prefix of COMPLETED): STOP" 3 "STOP: a cov2d/t2a/rpd/geanttw job is unended" "$out"

  out=$(run "$B" '' '' 1)
  check "sacct fails: STOP" 3 "STOP: sacct failed" "$out"

  out=$(run "$B" "$TODAY" '' 0 'sacct: error: slurmdbd: Connection refused\n')
  check "stderr error line, sacct rc 0: STOP" 3 "$MALFORMED" "$out"

  out=$(run "$B" '9|cov2d_trunc\n' '' 0)
  check "2-field row: STOP" 3 "$MALFORMED" "$out"

  out=$(run "$B" 'JobID|cov2d_z|COMPLETED\n' '' 0)
  check "non-numeric JobID: STOP" 3 "$MALFORMED" "$out"

  out=$(run "$B" 'x61300300|other|COMPLETED\n' '' 0)
  check "JobID with a digit but not numeric, unrelated name: STOP" 3 "$MALFORMED" "$out"

  out=$(run "$B" '11|rpd_r|REVOKED\n' '' 0)
  check "rpd REVOKED (outside rev 2's terminal set): STOP" 3 "STOP: a cov2d/t2a/rpd/geanttw job is unended" "$out"

  out=$(run "$B" '12.batch|batch|COMPLETED\n' '' 0)
  check "a step id (12.batch) in -X output: STOP" 3 "$MALFORMED" "$out"

  out=$(run "$B" '13|t2a_t|TIMEOUT\n' '' 0)
  check "t2a TIMEOUT alone: CLEAR" 0 "FENCE: clear" "$out"

  out=$(run "$B" '61300400||RUNNING\n' '' 0)
  check "empty JobName (would bypass the family match): STOP" 3 "$MALFORMED" "$out"

  out=$(run "$B" '61300401| cov2d-p|RUNNING\n' '' 0)
  check "padded JobName: STOP" 3 "$MALFORMED" "$out"

  out=$(run "$B" '61300402|other|\n' '' 0)
  check "empty State: STOP" 3 "$MALFORMED" "$out"

  out=$(run "$B" '61300404|other|   \n' '' 0)
  check "State of spaces only, unrelated job: STOP" 3 "$MALFORMED" "$out"

  out=$(run "$B" '61300403|COV2D-UPPER|RUNNING\n' '' 0)
  check "uppercase family name RUNNING: STOP" 3 "STOP: a cov2d/t2a/rpd/geanttw job is unended" "$out"

  out=$(run "$B" '61300500|geanttw_p0_pin_1L|RUNNING\n' '' 0)
  check "geanttw RUNNING: STOP" 3 "STOP: a cov2d/t2a/rpd/geanttw job is unended" "$out"

  out=$(run "$B" '' '61300501|GEANTTW_P0_PAT_1L|PENDING\n' 0)
  check "uppercase geanttw PENDING before midnight: STOP" 3 "STOP: a cov2d/t2a/rpd/geanttw job is unended" "$out"

  out=$(run "$B" '62042572|geanttw_p0_pin_1L|COMPLETED\n62042575|geanttw_p0_pat_1L|COMPLETED\n' '' 0)
  check "geanttw COMPLETED only: CLEAR" 0 "FENCE: clear" "$out"

  out=$(run "$B" '10|rpd_x|COMPLETED|extra\n' '' 0)
  check "4-field row: STOP" 3 "$MALFORMED" "$out"

  out=$(run "$B" "$TODAY" '' 0 '' 'garbage')
  check "start date malformed: STOP" 3 "STOP: start date malformed" "$out"
}

fails=0; QUIET=0
cases "$BLOCK" "$NO_S"
echo "SACCT-FENCE-TESTS :: $([ "$fails" -eq 0 ] && echo PASS || echo "FAIL ($fails)")"
[ "$fails" -eq 0 ] || exit 1

# Mutants: NAME<TAB>OLD<TAB>NEW, each OLD occurring exactly once in the block.
TAB=$(printf '\t')
MUTANTS="stderr-not-captured${TAB}State 2>&1)${TAB}State)
field-count-unchecked${TAB}NF != 3 || ${TAB}
jobid-unchecked${TAB} || \$1 !~ /^[0-9]+([_+].*)?\$/${TAB}
jobid-unanchored${TAB}\$1 !~ /^[0-9]+([_+].*)?\$/${TAB}\$1 !~ /[0-9]/
state-whole-field${TAB}if (!(w[1] in term)) bad = 1${TAB}if (!(\$3 in term)) bad = 1
family-drops-rpd${TAB}/^(cov2d|t2a|rpd|geanttw)/ {${TAB}/^(cov2d|t2a|geanttw)/ {
family-drops-geanttw${TAB}|rpd|geanttw)/ {${TAB}|rpd)/ {
awk-rc-ignored${TAB}[ \"\$rc\" -eq 0 ] ||${TAB}true ||
sacct-rc-ignored${TAB}State 2>&1) ||${TAB}State 2>&1); true ||
start-unchecked${TAB}[[ \$start =~ ^[0-9]{4}-[0-9]{2}-[0-9]{2}\$ ]] ||${TAB}true ||
start-window-dropped${TAB} -S \"\$start\"${TAB}
terminal-set-adds-pending${TAB}PREEMPTED TIMEOUT${TAB}PREEMPTED PENDING TIMEOUT
terminal-set-adds-revoked${TAB}PREEMPTED TIMEOUT${TAB}PREEMPTED REVOKED TIMEOUT
terminal-set-drops-timeout${TAB}PREEMPTED TIMEOUT\"${TAB}PREEMPTED\"
name-empty-unchecked${TAB} || \$2 == \"\"${TAB}
name-padding-unchecked${TAB} || \$2 ~ /^[[:space:]]|[[:space:]]\$/${TAB}
state-empty-unchecked${TAB} || \$3 !~ /[^[:space:]]/${TAB}
family-case-sensitive${TAB}tolower(\$2) ~${TAB}\$2 ~"
QUIET=1; killed=0; total=0
while IFS="$TAB" read -r name old new; do
  total=$((total + 1))
  n=$(python3 -I -c 'import sys; print(sys.argv[1].count(sys.argv[2]))' "$BLOCK" "$old")
  [ "$n" = 1 ] || { echo "MUTANT $name: old text occurs $n times"; continue; }
  M=$(python3 -I -c 'import sys; print(sys.argv[1].replace(sys.argv[2], sys.argv[3], 1), end="")' "$BLOCK" "$old" "$new")
  MN=$(printf '%s' "$M" | sed 's/ -S "$start"//')
  fails=0; cases "$M" "$MN"
  if [ "$fails" -gt 0 ]; then killed=$((killed + 1)); echo "KILLED   $name ($fails cases)"; else echo "SURVIVED $name"; fi
done <<< "$MUTANTS"
echo "SACCT-FENCE-MUTANTS :: $killed/$total killed"
[ "$killed" -eq "$total" ]

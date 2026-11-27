#!/bin/bash
# test_fetch_finish.sh: the fetch's step 0, how it decides the job is finished, against a stub sacct. Local files only.
# usage: bash test_fetch_finish.sh
# The block from `acct=$(sacct ...)` through the job.rc test is cut from rpd_flux4_fetch.sh and run in a temp directory.
# Without job.rc, sacct's state counts only from a successful call with exactly one row for the job (codex-school2's
# flux3 read, blocking 3); otherwise the fetch exits 10 and can be run again. With job.rc, job.rc decides.
set -u
HERE=$(cd "$(dirname "$0")" && pwd)
FETCH="$HERE/../rpd_flux4_fetch.sh"
T=$(mktemp -d) || exit 9
trap 'rm -rf -- "$T"' EXIT
REAL_AWK=$(command -v awk)
mkdir -p "$T/bin"
cat > "$T/bin/awk" <<EOF
#!/bin/bash
# The finish parse (its program holds print st "|" nd, which no mutant edits) prints its real output, then returns 2 when FAKE_AWK_FAIL is set.
out=\$("$REAL_AWK" "\$@"); r=\$?
printf '%s\n' "\$out" | sed '/^\$/d'
case "\$*" in *'print st "|" nd'*) [ -n "\${FAKE_AWK_FAIL:-}" ] && exit 2 ;; esac
exit \$r
EOF
chmod +x "$T/bin/awk"
BLOCK=$("$REAL_AWK" '/^acct=\$\(sacct -X -n -P -j "\$jid"/ {f=1} f {print} f && /^fi$/ {exit}' "$FETCH")
[ "$(printf '%s\n' "$BLOCK" | grep -c 'cannot tell')" = 1 ] || { echo "SETUP: could not cut the step-0 block"; exit 9; }

run() {  # run BLOCK SACCT_STDOUT SACCT_RC JOBRC(yes|no) -> output and rc=N
  rm -rf -- "$T/w"; mkdir -p "$T/w"; : > "$T/w/self.sh"
  [ "$4" = yes ] && echo "rc=0 cause=exit end=x" > "$T/w/job.rc"
  (cd "$T/w" && PATH="$T/bin:$PATH" bash -c "
    sacct() { printf '%b' '$2'; return $3; }
    SELF=$T/w/self.sh; jid=61900001
    $1
    echo PROCEED")
  echo "rc=$?"
}

check() {  # check NAME OUTPUT EXPECT_RC LINE
  local rc; rc=$(printf '%s\n' "$2" | sed -n 's/^rc=//p' | tail -1)
  if [ "$rc" = "$3" ] && printf '%s\n' "$2" | grep -qF -- "$4"; then [ "$Q" = 1 ] || echo "ok   $1"
  else [ "$Q" = 1 ] || { echo "FAIL $1: rc [$rc], want $3 and [$4]"; printf '%s\n' "$2" | sed 's/^/     /'; }; fails=$((fails + 1)); fi
}

ROW='61900001|rpd_flux4|COMPLETED|0:0|00:04:11|a|b|nid1||10|16G|01:00:00\n'
cases() {  # cases BLOCK
  check "no job.rc, sacct fails while printing a COMPLETED row: exit 10, cannot tell" "$(run "$1" "$ROW" 1 no)" 10 "cannot tell"
  check "no job.rc, sacct ok, RUNNING: exit 10, not finished" "$(run "$1" '61900001|rpd_flux4|RUNNING|0:0|1|a|b|n||10|16G|1\n' 0 no)" 10 "NOT FINISHED: no job.rc"
  check "no job.rc, sacct ok, two rows for the job: exit 10, cannot tell" "$(run "$1" "$ROW$ROW" 0 no)" 10 "cannot tell"
  check "no job.rc, sacct ok, no row: exit 10, cannot tell" "$(run "$1" '' 0 no)" 10 "cannot tell"
  check "no job.rc, sacct ok, one COMPLETED row: proceeds, cleanup unverified" "$(run "$1" "$ROW" 0 no)" 0 "FINISHED WITHOUT job.rc"
  check "job.rc present, sacct fails: job.rc decides, proceeds" "$(run "$1" '' 1 yes)" 0 "PROCEED"
  check "no job.rc, a COMPLETED row for 061900001 (job 61900001): exit 10, cannot tell" "$(run "$1" '061900001|rpd_flux4|COMPLETED|0:0|1|a|b|n||10|16G|1\n' 0 no)" 10 "cannot tell"
  check "no job.rc, a short row 61900001||COMPLETED: exit 10, cannot tell" "$(run "$1" '61900001||COMPLETED\n' 0 no)" 10 "cannot tell"
  BLANK='61900001|rpd_flux4|   |0:0|1|a|b|n2||10|16G|1\n'
  check "no job.rc, a full row then a blank-State duplicate: exit 10, cannot tell" "$(run "$1" "$ROW$BLANK" 0 no)" 10 "cannot tell"
  check "no job.rc, a blank-State duplicate then a full row: exit 10, cannot tell" "$(run "$1" "$BLANK$ROW" 0 no)" 10 "cannot tell"
  check "no job.rc, the parse prints a row but fails (rc 2): exit 10, cannot tell" "$(FAKE_AWK_FAIL=1 run "$1" "$ROW" 0 no)" 10 "cannot tell"
}

fails=0; Q=0
cases "$BLOCK"
echo "FETCH-FINISH-TESTS :: $([ "$fails" -eq 0 ] && echo PASS || echo "FAIL ($fails)")"
[ "$fails" -eq 0 ] || exit 1

TAB=$(printf '\t')
MUTANTS="sacct-rc-unchecked${TAB}[ \"\$arc\" -ne 0 ] || ${TAB}
parse-rc-unchecked${TAB} || [ \"\$urc\" -ne 0 ]${TAB}
duplicates-allowed${TAB}if (n == 1 && ok == 1)${TAB}if (ok == 1)
ids-numeric${TAB}\$1 \"\" == j \"\" { n++;${TAB}\$1 == j { n++;
shape-unchecked${TAB}NF == 12 && \$3 ~ /[^[:space:]]/${TAB}1"
Q=1; killed=0; total=0
while IFS="$TAB" read -r name old new; do
  total=$((total + 1))
  n=$(python3 -I -c 'import sys; print(sys.argv[1].count(sys.argv[2]))' "$BLOCK" "$old")
  [ "$n" = 1 ] || { echo "MUTANT $name: old text occurs $n times"; continue; }
  M=$(python3 -I -c 'import sys; t, a, b = sys.argv[1:]; print(t.replace(a, b, 1), end="")' "$BLOCK" "$old" "$new")
  fails=0; cases "$M"
  if [ "$fails" -gt 0 ]; then killed=$((killed + 1)); echo "KILLED   $name ($fails cases)"; else echo "SURVIVED $name"; fi
done <<< "$MUTANTS"
echo "FETCH-FINISH-MUTANTS :: $killed/$total killed"
[ "$killed" -eq "$total" ]

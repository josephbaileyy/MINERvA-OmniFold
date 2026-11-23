#!/bin/bash
# Stub test for cov2d_fence.sh rev 3: sacct, date, id, hostname and squeue are shims on PATH; squeue must never run.
# Every case checks the exit code AND the verdict line (exit 0 <=> last line "FENCE CLEAR"; exit 3 <=> "FENCE REFUSED"
# printed and no "FENCE CLEAR"). Usage: bash test_cov2d_fence.sh   (exit 0 iff every check passes)
here=$(cd "$(dirname "$0")" && pwd); F=$here/cov2d_fence.sh
T=$(mktemp -d); trap 'rm -rf "$T"' EXIT
mkdir "$T/bin"
cat > "$T/bin/sacct" <<'S'
#!/bin/bash
printf '%s\n' "$*" >> "$T_LOG"
[ -n "$SACCT_ERR" ] && printf '%b' "$SACCT_ERR" >&2
printf '%b' "$SACCT_OUT"
exit "${SACCT_RC:-0}"
S
cat > "$T/bin/squeue" <<'S'
#!/bin/bash
echo squeue >> "$T_SQ"; exit 0
S
cat > "$T/bin/date" <<'S'
#!/bin/bash
if [ "$1" = -d ]; then
  [ -n "$DATE_RC" ] && { /bin/date -v-60d +%Y-%m-%dT%H:%M:%S; exit "$DATE_RC"; }  # valid value, failing status
  [ -n "$DATE_BAD" ] && { echo "$DATE_BAD"; exit 0; }
  n=$(printf '%s\n' "$2" | sed -n 's/^\([0-9][0-9]*\) days ago$/\1/p'); [ -n "$n" ] || { echo "date stub: unparsed -d '$2'" >&2; exit 1; }
  python3 -c 'import datetime as d,sys; print((d.datetime.now()-d.timedelta(days=int(sys.argv[1]))).strftime("%Y-%m-%dT%H:%M:%S"))' "$n"
else /bin/date "$@"; fi
S
cat > "$T/bin/id" <<'S'
#!/bin/bash
[ -n "$ID_RC" ] && { echo stubuser; exit "$ID_RC"; }  # valid value, failing status
[ -n "$ID_EMPTY" ] && exit 0
echo stubuser
S
printf '#!/bin/bash\necho stubhost\n' > "$T/bin/hostname"
chmod +x "$T/bin/"*
export PATH="$T/bin:$PATH" T_LOG="$T/sacct.log" T_SQ="$T/squeue.log"
fail=0
verdict_ok() { # rc output -> 0 iff the printed verdict agrees with rc
  last=$(printf '%s\n' "$2" | tail -n 1)
  case $1 in
    0) [ "$last" = "FENCE CLEAR" ] && ! printf '%s\n' "$2" | /usr/bin/grep -q 'FENCE REFUSED' ;;
    3) printf '%s\n' "$2" | /usr/bin/grep -q '^FENCE REFUSED' && ! printf '%s\n' "$2" | /usr/bin/grep -q 'FENCE CLEAR' ;;
    *) return 1 ;;
  esac
}
# case_ name expected_exit ; inputs come from env vars set on the call line
case_() {
  : > "$T_LOG"
  out=$(bash "$F" 2>&1); rc=$?
  if [ "$rc" = "$2" ] && verdict_ok "$rc" "$out"; then echo "ok   $1 (exit $rc)"
  else echo "FAIL $1: exit $rc, want $2 (or verdict line disagrees)"; printf '%s\n' "$out"; fail=1; fi
}
SACCT_OUT=''                                                       case_ empty                0
SACCT_OUT='1|cov2d_a|COMPLETED\n2|t2a_b|FAILED\n3|cov2d_c|TIMEOUT\n' case_ completed            0
SACCT_OUT='1|cov2d_a|CANCELLED by 12345\n'                          case_ cancelled_by         0
SACCT_OUT='1|cov2d_a|CANCELLED\n'                                   case_ cancelled_bare       0
SACCT_OUT='1|cov2d|BOOT_FAIL\n2|cov2d|DEADLINE\n3|cov2d|NODE_FAIL\n4|cov2d|OUT_OF_MEMORY\n5|cov2d|PREEMPTED\n' case_ every_terminal 0
SACCT_OUT='1|t3p_floor|RUNNING\n2|xcov2d|PENDING\n'                 case_ other_lane_running   0
SACCT_OUT='1|cov2d_a|COMPLETED\n\n2|cov2d_b|COMPLETED\n'            case_ blank_mid_ended      0
SACCT_OUT='123_4|cov2d_a|COMPLETED\n124+0|t2a_b|COMPLETED\n'        case_ array_het_ids_ended  0
SACCT_OUT='1|cov2d_a|RUNNING\n'                                     case_ running              3
SACCT_OUT='1|t2a_x|PENDING\n'                                       case_ pending_t2a          3
SACCT_OUT='1|cov2d_a|COMPLETING\n'                                  case_ completing           3
SACCT_OUT='1|cov2d_a|REQUEUED\n'                                    case_ requeued             3
SACCT_OUT='1|cov2d_a|SUSPENDED\n'                                   case_ suspended            3
SACCT_OUT='1|cov2d_a|CANCELLED+\n'                                  case_ cancelled_truncated  3
SACCT_OUT='1|cov2d_a|NEWSTATE\n'                                    case_ unknown_state        3
SACCT_OUT='1|cov2d_a|\n'                                            case_ empty_state          3
SACCT_OUT='1|cov2d_a|COMPLETED\n2|cov2d_b|RUNNING\n'                case_ completed_then_run   3
SACCT_OUT='1|cov2d_a|COMPLETED\n\n2|cov2d_b|RUNNING\n'              case_ blank_mid_running    3
SACCT_OUT='123_[1-5%2]|cov2d_a|PENDING\n'                           case_ array_pending        3
SACCT_OUT='1|cov2d_a\n'                                             case_ malformed_2_fields   3
SACCT_OUT='1|t3|x|COMPLETED\n'                                      case_ malformed_pipe_name  3
SACCT_OUT='x|t3|COMPLETED\n'                                        case_ nonnumeric_jobid     3
SACCT_RC=1                                                          case_ sacct_fails          3
SACCT_ERR='sacct: error: Problem talking to the database\n'         case_ stderr_rc0_empty     3
SACCT_ERR='sacct: error: Problem talking to the database\n' SACCT_OUT='1|cov2d_a|COMPLETED\n' case_ stderr_rc0_ended 3
SACCT_ERR='sacct: error: x|y|z\n'                                   case_ stderr_three_fields  3
SACCT_ERR='sacct: error: Too wide of a date range in query\n' SACCT_RC=1 case_ too_wide_range     3
DATE_BAD=garbage                                                    case_ date_malformed       3
DATE_RC=1                                                           case_ date_fails           3
ID_RC=1                                                             case_ id_fails             3
ID_EMPTY=1                                                          case_ id_empty             3
# sacct's argv: explicit -S at least 48 h back; -X -n -P -u <user> -E now -o JobID,JobName,State; never -s/--state.
: > "$T_LOG"; SACCT_OUT='' bash "$F" >/dev/null 2>&1
args=$(cat "$T_LOG")
st=$(printf '%s\n' "$args" | sed -n 's/.*-S \([^ ]*\).*/\1/p')
age=$(python3 -c "import datetime as d,sys; print(int((d.datetime.now()-d.datetime.fromisoformat(sys.argv[1])).total_seconds()))" "$st" 2>/dev/null)
if [ -n "$age" ] && [ "$age" -ge 172800 ]; then echo "ok   start $st is ${age}s back (>= 172800)"; else echo "FAIL start '$st' age '$age'"; fail=1; fi
# Perlmutter refused a 60-day range (rev 2); the window must be at most 14 days (1209600 s, plus 120 s for test runtime).
if [ -n "$age" ] && [ "$age" -le 1209720 ]; then echo "ok   start $st is at most 14 days back"; else echo "FAIL start '$st' more than 14 days back"; fail=1; fi
# Static check on the script text: exactly one date -d window, and it is 14 days.
if [ "$(/usr/bin/grep -c "date -d '14 days ago'" "$F")" = 1 ] && [ "$(/usr/bin/grep -c "date -d '" "$F")" = 1 ]; then echo "ok   script's only date -d window is '14 days ago'"; else echo "FAIL script's date -d window is not exactly '14 days ago'"; fail=1; fi
for want in '-X' '-n' '-P' '-u stubuser' '-E now' '-o JobID,JobName,State'; do
  case " $args " in *" $want "*) echo "ok   argv has $want";; *) echo "FAIL argv lacks $want"; fail=1;; esac
done
case " $args " in *" -s "*|*"--state"*) echo "FAIL argv uses -s/--state"; fail=1;; *) echo "ok   argv has no -s/--state";; esac
# Self-copy deletion: $1 is deleted only if it is under /dev/shm/ AND is the running script ([ "$1" -ef "$0" ]).
# macOS has no /dev/shm, so these cases run a copy of the fence whose single "/dev/shm/*)" pattern is rewritten to
# "$T/shm/*)"; the fence file itself keeps the literal /dev/shm/.
[ "$(/usr/bin/grep -c '/dev/shm/\*)' "$F")" = 1 ] || { echo "FAIL fence lacks exactly one /dev/shm/*) pattern"; fail=1; }
mkdir "$T/shm" "$T/notshm"
shm_copy() { sed "s#/dev/shm/\*)#$T/shm/*)#" "$F" > "$1"; }
for pair in '0|' '3|1|cov2d|RUNNING\n'; do
  want=${pair%%|*}; o=${pair#*|}
  # (a) the real self-copy under shm, run as itself: deleted, exit unchanged
  c=$T/shm/fence_copy.sh; shm_copy "$c"
  out=$(SACCT_OUT="$o" bash "$c" "$c" 2>&1); rc=$?
  if [ -e "$c" ] || [ "$rc" != "$want" ] || ! verdict_ok "$rc" "$out"; then echo "FAIL self copy under shm (want exit $want, got $rc, kept=$([ -e "$c" ] && echo y || echo n))"; fail=1
  else echo "ok   self copy under shm deleted (exit $rc)"; fi
  # (b) some other file under shm passed as $1: kept and named, exit unchanged
  c=$T/shm/fence_copy.sh; shm_copy "$c"; v=$T/shm/other_file; echo keep > "$v"
  out=$(SACCT_OUT="$o" bash "$c" "$v" 2>&1); rc=$?
  if [ ! -e "$v" ] || [ "$rc" != "$want" ] || ! printf '%s\n' "$out" | /usr/bin/grep -qx "self-copy not removed: $v"; then echo "FAIL other shm file (want kept + exit $want, got $rc, kept=$([ -e "$v" ] && echo y || echo n))"; fail=1
  else echo "ok   other shm file kept (exit $rc)"; fi
  rm -f "$c" "$v"
  # (c) the running script itself but NOT under shm: kept and named, exit unchanged
  c=$T/notshm/fence_copy.sh; shm_copy "$c"
  out=$(SACCT_OUT="$o" bash "$c" "$c" 2>&1); rc=$?
  if [ ! -e "$c" ] || [ "$rc" != "$want" ] || ! printf '%s\n' "$out" | /usr/bin/grep -qx "self-copy not removed: $c"; then echo "FAIL self outside shm (want kept + exit $want, got $rc)"; fail=1
  else echo "ok   self outside shm kept (exit $rc)"; fi
  rm -f "$c"
  # (e) the running script outside shm, reached by a /dev/shm/.. path (passes prefix and -ef): kept and named
  c=$T/notshm/fence_copy.sh; shm_copy "$c"; dd=$T/shm/../notshm/fence_copy.sh
  out=$(SACCT_OUT="$o" bash "$c" "$dd" 2>&1); rc=$?
  if [ ! -e "$c" ] || [ "$rc" != "$want" ] || ! printf '%s\n' "$out" | /usr/bin/grep -qxF "self-copy not removed: $dd"; then echo "FAIL dotdot path (want kept + exit $want, got $rc)"; fail=1
  else echo "ok   dotdot path to self kept (exit $rc)"; fi
  rm -f "$c"
  # (d) the committed fence, unmodified, with an arbitrary file as $1: kept and named, exit unchanged
  v=$T/victim_record.txt; echo record > "$v"
  out=$(SACCT_OUT="$o" bash "$F" "$v" 2>&1); rc=$?
  if [ ! -e "$v" ] || [ "$rc" != "$want" ] || ! printf '%s\n' "$out" | /usr/bin/grep -qx "self-copy not removed: $v"; then echo "FAIL arbitrary file (want kept + exit $want, got $rc)"; fail=1
  else echo "ok   arbitrary file kept (exit $rc)"; fi
  rm -f "$v"
done
if [ -s "$T_SQ" ]; then echo "FAIL squeue was called"; fail=1; else echo "ok   squeue never called"; fi
[ "$fail" = 0 ] && echo "ALL PASS" || echo "SOME FAILED"
exit "$fail"

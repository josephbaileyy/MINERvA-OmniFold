#!/bin/bash
# Stand-in test of connect-g2r-xk.sh. A copy runs with exact substitutions (each asserted once): P -> a temp tree, URL ->
# this repository (git clone --shared), LOG -> the temp tree, the two conda lines -> `true`, and `/usr/bin/time -f ...`
# dropped (BSD time has no -f). Shims: squeue, sacct, nproc, hostname, sha256sum (with -c), and python, which runs the REAL
# xk_compare.py, prints the environment probe, answers the universes-file hash (X's pin, or another digest by
# scenario), stands in for xk_copy.py (it needs the real run directory's bytes) and for fd_xcov.py k: the control writes
# the committed fd/xcov/run/k/k.json (so the real comparison PASSes) unless mutated; g2r writes a readout and exits with
# the scenario's rc. The deploy is a real clone at PKG, and the four code-sha checks are real.
#   bash test_connect_xk.sh <connect> <repo worktree> <PKG>
set -u
CONN=$(cd "$(dirname "$1")" && pwd)/$(basename "$1"); REPO=$2; PKG=$3
T0=$(mktemp -d "${TMPDIR:-/tmp}/txk.XXXXXX"); SH=$T0/shims; mkdir -p "$SH"; fail=0
ok() { echo "PASS $1"; }; bad() { echo "FAIL $1"; fail=1; }
REALGIT=$(command -v git); REALPY=/opt/homebrew/bin/python3.13
cat > "$SH/git" <<EOF
#!/bin/bash
if [ "\$1" = clone ]; then shift; [ "\$1" = --quiet ] && shift; exec "$REALGIT" clone --quiet --shared "$REPO" "\$2"; fi
exec "$REALGIT" "\$@"
EOF
cat > "$SH/squeue" <<'EOF'
#!/bin/bash
n=$(( $(cat "$SC_CNT" 2>/dev/null || echo 0) + 1 )); echo $n > "$SC_CNT"
[ -n "${SC_SQ_RC:-}" ] && { echo "squeue: error" >&2; exit "$SC_SQ_RC"; }
echo "JOBID|NAME|STATE|TIME_LIMIT|NODES"
names=${SC_SQ_NAMES:-}; [ "$n" -ge 2 ] && names="$names ${SC_SQ_LATE:-}"
for j in $names; do echo "1|$j|RUNNING|1:00:00|1"; done
EOF
cat > "$SH/sacct" <<'EOF'
#!/bin/bash
if [[ "$*" == *"--name rdx_s1_1A"* ]]; then printf '%b' "61300000|rdx_s1_1A|COMPLETED|2026-11-14T20:00:00\n"; else printf '%b' "61300000|rdx_s1_1A|COMPLETED\n"; fi
EOF
printf '#!/bin/bash\necho 128\n' > "$SH/nproc"; printf '#!/bin/bash\necho login99\n' > "$SH/hostname"
cat > "$SH/sha256sum" <<EOF
#!/bin/bash
exec "$REALPY" - "\$@" <<'PY'
import hashlib, sys
a = sys.argv[1:]
h = lambda p: hashlib.sha256(open(p, "rb").read()).hexdigest()
if a and a[0] == "-c":
    bad = 0
    for ln in open(a[1]).read().splitlines():
        d, p = ln.split(None, 1)
        good = h(p) == d; bad += not good; print(f"{p}: {'OK' if good else 'FAILED'}")
    sys.exit(1 if bad else 0)
for p in a:
    try: print(f"{h(p)}  {p}")
    except OSError: print(f"sha256sum: {p}: No such file", file=sys.stderr)
PY
EOF
cat > "$SH/python" <<EOF
#!/bin/bash
[ "\$1" = -B ] && shift
case "\$1" in
  -c) case "\$2" in
        *uproot*) echo "python 3.10.19"; echo "numpy 2.2.6"; echo "uproot 5.6.9"; echo "executable fake"; exit 0 ;;
        *O_NOATIME*) [ -n "\${SC_UNI_BAD:-}" ] && { echo 0000000000000000000000000000000000000000000000000000000000000000; exit 0; }
                     echo 220c479efa9751116fd396ea32398de5631f8b755e6b16a94ce090975f011418; exit 0 ;;
      esac ;;
  */xk_compare.py) exec "$REALPY" "\$@" ;;
  */xk_copy.py)
    [ -n "\${SC_COPY_BAD:-}" ] && { echo "XK-COPY REFUSED: fake"; exit 2; }
    for ((i=1; i<=\$#; i++)); do a=\${!i}; j=\$((i+1)); [ "\$a" = --dest ] && mkdir -p "\${!j}/v0-a1"; done
    echo "XK-COPY OK: 112 files to 2 destination(s), each equal to fd/xcov/run/hpss/files.sha256"; exit 0 ;;
  nd-unfolding/fd_xcov.py)
    rd=""; pr=""; for ((i=1; i<=\$#; i++)); do a=\${!i}; j=\$((i+1)); [ "\$a" = --run-dir ] && rd=\${!j}; [ "\$a" = --products ] && pr=\${!j}; done
    mkdir -p "\$rd/k"
    if [ "\$pr" = re2 ]; then
      [ -n "\${SC_CTL_RC:-}" ] && { echo "fake control fails"; exit "\$SC_CTL_RC"; }
      "$REALPY" - "\$rd/k/k.json" "\${SC_CTL_MUT:-}" <<'PY'
import json, sys
d = json.load(open("docs/orchestration/state/measurement-paper/5d-community-20261024/fd/xcov/run/k/k.json"))
if sys.argv[2] == "route": d["route"] = "B"
json.dump(d, open(sys.argv[1], "w"), indent=1)
PY
      echo "[K1 ratios] band 2p2h: kind equal; ratio16 0.1 ratio2 0.2"; echo "[K] A: agree (fake control)"; exit 0
    else
      echo '{"products": "g2r"}' > "\$rd/k/k.json"; echo "[K] fake g2r"; exit "\${SC_G2R_RC:-0}"
    fi ;;
esac
echo "unexpected python \$*"; exit 99
EOF
chmod +x "$SH"/*
run() {
  local name=$1 want=$2; shift 2
  local R=$T0/$name; mkdir -p "$R/p"
  "$REALPY" - "$CONN" "$R/c.sh" "$R/p" "$R/log" <<'PY' || { bad "$name: substitution"; return; }
import sys
s = open(sys.argv[1]).read()
for a, b in [("P=/pscratch/sd/j/josephrb\n", f"P={sys.argv[3]}\n"), ("URL=https://github.com/josephbaileyy/MINERvA-OmniFold\n", "URL=unused\n"),
             ("LOG=/dev/shm/josephrb-g2r-xk.log\n", f"LOG={sys.argv[4]}\n"),
             ('eval "$(/global/common/software/nersc/pe/conda/24.10.0/Miniforge3-24.7.1-0/bin/conda shell.bash hook)"\n', "true\n"),
             ('conda activate "$HOME/.conda/envs/omnifold_py310" || stop "conda activate"\n', "true\n"),
             ('/usr/bin/time -f "k wall %e s rss %M KB" ', "")]:
    assert s.count(a) == 1, a; s = s.replace(a, b)
open(sys.argv[2], "w").write(s)
PY
  [ "${PRE_W:-}" = 1 ] && mkdir -p "$R/p/cov2d-xk-g2r-20261116"
  (export PATH="$SH:$PATH" SC_CNT="$R/sqcount" "$@"; bash "$R/c.sh") > "$R/stdout" 2>&1; local rc=$?
  if grep -qE "$want" "$R/log" && [ "$(tail -1 "$R/log")" = DONE ]; then ok "$name (rc $rc): $(grep -E "$want" "$R/log" | head -1 | cut -c1-110)"
  else bad "$name (rc $rc, want /$want/)"; tail -12 "$R/log" "$R/stdout"; fi
  LASTW=$R/p/cov2d-xk-g2r-20261116
  [ -d "$LASTW/deploy" ] && find "$LASTW/deploy" -delete
}
run clean '^XK PASS: control reproduced the committed k.json; g2r arm rc 0'
grep -q '^XK-CONTROL PASS' "$T0/clean/log" && grep -q 'nd-unfolding/fd_xcov_steps.py: OK' "$T0/clean/log" && grep -q '^universes file sha256 220c479e' "$T0/clean/log" \
  && ok "clean: code shas OK, universes file at X's pin, real comparison PASS" || { bad "clean: details"; grep -E 'OK|universes|XK-CONTROL' "$T0/clean/log"; }
run uni-bad "^STOP the MEFHC universes file is not at X's pin" SC_UNI_BAD=1
[ ! -e "$LASTW/ctl/k" ] && ok "uni-bad: no K ran" || bad "uni-bad: K ran"
run copy-bad '^STOP the copies did not complete' SC_COPY_BAD=1
run control-route '^STOP the control did not reproduce the committed k.json' SC_CTL_MUT=route
grep -q '^XK-CONTROL STOP: 1 difference' "$T0/control-route/log" && [ ! -e "$LASTW/run/k/k.json" ] && ok "control-route: the real comparison found 1 difference; g2r did not run" || bad "control-route: details"
run control-rc '^STOP control rc=1' SC_CTL_RC=1
run g2r-rc '^STOP g2r rc=1' SC_G2R_RC=1
run job-queued '^STOP a job of josephrb is queued or running' SC_SQ_NAMES=fd_stab2
run late-job '^STOP a job of josephrb is queued or running' SC_SQ_LATE=fd1b_bdg_3
grep -q '^XK-CONTROL PASS' "$T0/late-job/log" && ! grep -q '^g2r start' "$T0/late-job/log" && ok "late-job: the control passed, the second fence STOPped before g2r" || bad "late-job: sequence"
PRE_W=1 run w-exists '^STOP .* exists'
find "$T0" -type f -exec rm -f {} + 2>/dev/null; find "$T0" -type l -exec rm -f {} + 2>/dev/null; find "$T0" -depth -type d -exec rmdir {} \; 2>/dev/null
[ -e "$T0" ] && echo "left: $T0"
[ "$fail" = 0 ] && echo "XK CONNECT TEST PASS" || echo "XK CONNECT TEST FAILED"
exit $fail

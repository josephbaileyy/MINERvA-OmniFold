#!/bin/bash
# Stand-in test of connect-g2r-cr.sh. A copy of the connect runs with exact substitutions (each asserted once): P -> a
# temp tree, URL -> this repository (git clone --shared via a git shim), LOG -> the temp tree, and the two conda lines
# -> `true` (no conda here). Shims: squeue, sacct, nproc (as for RE-2-shapes), sha256sum (-c, --quiet), and python, which
# runs the REAL cr_compare.py and the environment probe with python3.13, and stands in for fd_gencmp.py: the control
# writes the committed overlap_refined.json with the deploy prefix moved (so the real comparison PASSes) unless the
# scenario mutates it; the g2r arm writes a readout and exits with the scenario's rc. The deploy is a real clone at PKG,
# and the fd_gencmp.py / cr_compare.py pin checks are real.
#   bash test_connect_cr.sh <connect> <repo worktree> <PKG>
set -u
CONN=$(cd "$(dirname "$1")" && pwd)/$(basename "$1"); REPO=$2; PKG=$3
T0=$(mktemp -d "${TMPDIR:-/tmp}/tcr.XXXXXX"); SH=$T0/shims; mkdir -p "$SH"; fail=0
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
[ -n "${SC_SQ_RC:-}" ] && { echo "squeue: error: Socket timed out" >&2; exit "$SC_SQ_RC"; }
echo "JOBID|NAME|STATE|TIME_LIMIT|NODES"
names=${SC_SQ_NAMES:-}; [ "$n" -ge 2 ] && names="$names ${SC_SQ_LATE:-}"
for j in $names; do echo "1|$j|RUNNING|1:00:00|1"; done
EOF
cat > "$SH/sacct" <<'EOF'
#!/bin/bash
if [[ "$*" == *"--name rdx_s1_1A"* ]]; then printf '%b' "61300000|rdx_s1_1A|COMPLETED|2026-11-14T20:00:00\n"
else printf '%b' "61300000|rdx_s1_1A|COMPLETED\n"; fi
EOF
printf '#!/bin/bash\necho 128\n' > "$SH/nproc"
cat > "$SH/sha256sum" <<EOF
#!/bin/bash
exec "$REALPY" - "\$@" <<'PY'
import hashlib, sys
for p in sys.argv[1:]:
    print(f"{hashlib.sha256(open(p, 'rb').read()).hexdigest()}  {p}")
PY
EOF
cat > "$SH/python" <<EOF
#!/bin/bash
# python -B <script> ... | python -B -c <probe>
[ "\$1" = -B ] && shift
case "\$1" in
  -c) exec "$REALPY" -c "import sys; print('python 3.10.19'); print('numpy 2.2.6'); print('uproot 5.6.9'); print('executable fake')" ;;
  */cr_compare.py) exec "$REALPY" "\$@" ;;
  nd-unfolding/fd_gencmp.py)
    out=""; q=""; for ((i=1; i<=\$#; i++)); do a=\${!i}; j=\$((i+1)); [ "\$a" = --out ] && out=\${!j}; [ "\$a" = --q2d ] && q=\${!j}; done
    arm=control; case "\$q" in *cov2d-re2shapes-20261115*) arm=g2r ;; esac
    if [ "\$arm" = control ]; then
      [ -n "\${SC_CTL_RC:-}" ] && { echo "fake control fails"; exit "\$SC_CTL_RC"; }
      "$REALPY" - "\$PWD" "\$out" "\${SC_CTL_MUT:-}" <<'PY'
import json, sys
import os
dep, out, mut = os.path.realpath(sys.argv[1]), sys.argv[2], sys.argv[3]   # fd_gencmp keys inputs by Path(__file__).resolve()
c = "docs/orchestration/state/measurement-paper/5d-community-20261024/fd/gencmp-e/c-r/overlap_refined.json"
d = json.load(open(c)); D0 = "/pscratch/sd/j/josephrb/gencmp-e-20261101/deploy"
d["inputs"] = {(dep + k[len(D0):] if k.startswith(D0 + "/") else k): v for k, v in d["inputs"].items()}
d["argv"] = ["fake"]
if mut == "reading":
    q = next(iter(d["quadrants"])); k = next(k for k, v in d["quadrants"][q].items() if isinstance(v, float)); d["quadrants"][q][k] *= 1 + 1e-12
json.dump(d, open(out, "w"), indent=1)
PY
      echo "[C] QA 2D agree (fake control)"; exit 0
    else
      echo '{"step": "fake g2r"}' > "\$out"; echo "[C] QA 2D fake g2r reading"; exit "\${SC_G2R_RC:-0}"
    fi ;;
esac
echo "unexpected python \$*"; exit 99
EOF
chmod +x "$SH"/*
run() {  # run <name> <want regex in the log> [env assignments...]
  local name=$1 want=$2; shift 2
  local R=$T0/$name; mkdir -p "$R/p"
  "$REALPY" - "$CONN" "$R/c.sh" "$R/p" "$R/log" <<'PY' || { bad "$name: substitution"; return; }
import sys
s = open(sys.argv[1]).read()
for a, b in [("P=/pscratch/sd/j/josephrb\n", f"P={sys.argv[3]}\n"), ("URL=https://github.com/josephbaileyy/MINERvA-OmniFold\n", "URL=unused\n"),
             ("LOG=/dev/shm/josephrb-g2r-cr.log\n", f"LOG={sys.argv[4]}\n"),
             ('eval "$(/global/common/software/nersc/pe/conda/24.10.0/Miniforge3-24.7.1-0/bin/conda shell.bash hook)"\n', "true\n"),
             ('conda activate "$HOME/.conda/envs/omnifold_py310" || stop "conda activate"\n', "true\n")]:
    assert s.count(a) == 1, a; s = s.replace(a, b)
open(sys.argv[2], "w").write(s)
PY
  [ "${PRE_W:-}" = 1 ] && mkdir -p "$R/p/cov2d-cr-g2r-20261116"
  (export PATH="$SH:$PATH" SC_CNT="$R/sqcount" "$@"; bash "$R/c.sh") > "$R/stdout" 2>&1; local rc=$?
  if grep -qE "$want" "$R/log" && [ "$(tail -1 "$R/log")" = DONE ]; then ok "$name (rc $rc): $(grep -E "$want" "$R/log" | head -1 | cut -c1-110)"
  else bad "$name (rc $rc, want /$want/)"; tail -12 "$R/log" "$R/stdout"; fi
  LASTW=$R/p/cov2d-cr-g2r-20261116
  [ -d "$LASTW/deploy" ] && find "$LASTW/deploy" -delete
}
run clean '^CR PASS: control reproduced step C-R; g2r arm rc 0'
grep -q '^CR-CONTROL PASS' "$T0/clean/log" && grep -q '^deploy porcelain_lines=0 head='"$PKG" "$T0/clean/log" && grep -q '^deploy porcelain after: 0' "$T0/clean/log" \
  && ok "clean: deploy at PKG, the real comparison PASSed, porcelain 0 after" || { bad "clean: details"; grep -E 'deploy|CR-CONTROL' "$T0/clean/log"; }
run control-reading '^STOP the control did not reproduce' SC_CTL_MUT=reading
grep -q '^CR-CONTROL STOP: 1 difference' "$T0/control-reading/log" && [ ! -s "$LASTW/g2r/overlap_refined.json" ] && ok "control-reading: the real comparison found 1 difference; the g2r arm did not run" || bad "control-reading: details"
run control-rc '^STOP control rc=3' SC_CTL_RC=3
run g2r-rc '^STOP g2r rc=4' SC_G2R_RC=4
grep -q '^deploy porcelain after: 0' "$T0/g2r-rc/log" && ok "g2r-rc: out.sha256 and porcelain still recorded" || bad "g2r-rc: details"
run job-queued '^STOP a job of josephrb is queued or running' SC_SQ_NAMES=fd_c2c1u
run squeue-fails '^STOP squeue failed \(rc 1\)' SC_SQ_RC=1
run late-job '^STOP a job of josephrb is queued or running' SC_SQ_LATE=rdx_s2_1A
grep -q '^CR-CONTROL PASS' "$T0/late-job/log" && ! grep -q '^g2r start' "$T0/late-job/log" && ok "late-job: the control ran and passed, the second fence STOPped before the g2r arm" || bad "late-job: sequence"
PRE_W=1 run w-exists '^STOP .* exists'
find "$T0" -type f -exec rm -f {} + 2>/dev/null; find "$T0" -type l -exec rm -f {} + 2>/dev/null; find "$T0" -depth -type d -exec rmdir {} \; 2>/dev/null
[ -e "$T0" ] && echo "left: $T0"
[ "$fail" = 0 ] && echo "CR CONNECT TEST PASS" || echo "CR CONNECT TEST FAILED"
exit $fail

#!/bin/bash
# Stand-in test of connect-g2r-d2.sh. A copy runs with exact substitutions (each asserted once): P -> a temp tree, URL ->
# this repository (git clone --shared), LOG -> the temp tree, `source setup_salloc_env.sh` and the python 3.11 check ->
# `true`, and `/usr/bin/time -f ...` dropped (BSD time has no -f). Shims: squeue, sacct, nproc, hostname, sha256sum (-c),
# and python3: the environment probe prints; the null-record hash answers the committed digests (or another one by
# scenario); `ll5d_mumax.py inputs` is the REAL command (miniconda python, the real ll5d_b) on a synthetic unfolds
# directory, staged S1 and constraint under the temp tree; `ll5d_mumax.py ll5d` reproduces the run's read pattern
# (coverage-5b-audit blocker 1): it reads the deploy's definition and cmodel json plainly and bumps their atime as a plain
# read does on pscratch (os.utime), touches nothing else, writes a record and exits with the scenario's rc; in the
# "moved" scenario it also bumps one watched product's atime. Every other -c script (the atime stat and the moved count)
# runs in the real python3.13. The deploy is a real clone at PKG and the code-sha checks are real.
#   bash test_connect_d2.sh <connect> <repo worktree> <PKG>
set -u
CONN=$(cd "$(dirname "$1")" && pwd)/$(basename "$1"); REPO=$2; PKG=$3
T0=$(mktemp -d "${TMPDIR:-/tmp}/td2.XXXXXX"); SH=$T0/shims; mkdir -p "$SH"; fail=0
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
echo "JOBID|NAME|STATE|TIME_LIMIT|NODES"; for j in ${SC_SQ_NAMES:-}; do echo "1|$j|RUNNING|1:00:00|1"; done
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
        d, p = ln.split(None, 1); good = h(p) == d; bad += not good; print(f"{p}: {'OK' if good else 'FAILED'}")
    sys.exit(1 if bad else 0)
for p in a:
    try: print(f"{h(p)}  {p}")
    except OSError: print(f"sha256sum: {p}: No such file", file=sys.stderr)
PY
EOF
cat > "$SH/python3" <<EOF
#!/bin/bash
args=("\$@")
case "\$1" in
  -c)
    case "\$2" in
      *numpy*) echo "python 3.11.9"; echo "numpy 2.1.3"; exit 0 ;;
      *O_NOATIME*hashlib*) case "\$3" in
          *null-g18.json) [ -n "\${SC_NULL_BAD:-}" ] && { echo 0000; exit 0; }; echo 73dbaf9517374646c719ff589015cb12c1a6a2eafd5579e1074ef700bde703c2 ;;
          *null-ar23.json) echo a0544ab9f6f0ec55c9866bee689d2563b13c9d07f4b3fdc37ce4762718a23933 ;;
        esac; exit 0 ;;
    esac
    exec "$REALPY" "\$@" ;;
  -I) shift; [ "\$1" = -B ] && shift
      case "\$2" in
        inputs) exec /Users/josephbailey/miniconda3/bin/python3 -I -B "\$@" ;;
        ll5d) out=""; dfn=""; cmj=""; unf=""
              for ((i=1; i<=\$#; i++)); do a=\${!i}; j=\$((i+1)); [ "\$a" = --out ] && out=\${!j}; [ "\$a" = --definition ] && dfn=\${!j}
                [ "\$a" = --cmodel-json ] && cmj=\${!j}; [ "\$a" = --unfolds ] && unf=\${!j}; done
              "$REALPY" -c "
import os, sys
for p in sys.argv[1:3]:
    open(p).read(); s = os.stat(p); os.utime(p, ns=(s.st_atime_ns + 10**9, s.st_mtime_ns))   # a plain read, as on pscratch
" "\$dfn" "\$cmj"
              [ -n "\${SC_MOVE:-}" ] && "$REALPY" -c "import os, sys; p=sys.argv[1]; s=os.stat(p); os.utime(p, ns=(s.st_atime_ns + 10**9, s.st_mtime_ns))" "\$unf/ll5d_g18_block_GEANT_Neutron_0.npz"
              echo '{"verdict": "PASS"}' > "\$out"; echo "[g18] mu_max C_T 0.05 (fake)"; echo "MUMAX PASS: []"; exit "\${SC_RC:-0}" ;;
      esac ;;
esac
echo "unexpected python3 \$*"; exit 99
EOF
chmod +x "$SH"/*
run() {
  local name=$1 want=$2; shift 2
  local R=$T0/$name; mkdir -p "$R/p/ll5d-null-r1" "$R/p/ll5d-unfolds-r2" "$R/p/fd-1b-inv-20261101/i0/in/s1" \
    "$R/p/MINERvA-OmniFold/MINERvA101/opt/etc/MParamFiles/data/FluxConstraints"
  : > "$R/p/ll5d-null-r1/null-g18.json"; : > "$R/p/ll5d-null-r1/null-ar23.json"
  : > "$R/p/fd-1b-inv-20261101/i0/in/s1/s1_assembly.npz"; : > "$R/p/MINERvA-OmniFold/MINERvA101/opt/etc/MParamFiles/data/FluxConstraints/sorted_NuEConstraint_FHC_RHC_IMD.txt"
  for t in g18 ar23; do for f in central_T seed_T block_GEANT_Neutron_0 stat_1 toy_all_1; do : > "$R/p/ll5d-unfolds-r2/ll5d_${t}_${f}.npz"; done; done
  "$REALPY" - "$CONN" "$R/c.sh" "$R/p" "$R/log" <<'PY' || { bad "$name: substitution"; return; }
import sys
s = open(sys.argv[1]).read()
for a, b in [("P=/pscratch/sd/j/josephrb\n", f"P={sys.argv[3]}\n"), ("URL=https://github.com/josephbaileyy/MINERvA-OmniFold\n", "URL=unused\n"),
             ("LOG=/dev/shm/josephrb-g2r-d2.log\n", f"LOG={sys.argv[4]}\n"),
             ('source "$DEP/setup_salloc_env.sh" > "$W/logs/env.log" 2>&1\n', "true\n"),
             ('case "$(python3 -V 2>&1)" in *3.11*) ;; *) stop "environment did not activate ($(python3 -V 2>&1))" ;; esac\n', "true\n"),
             ('/usr/bin/time -f "mumax wall %e s rss %M KB" ', "")]:
    assert s.count(a) == 1, a; s = s.replace(a, b)
open(sys.argv[2], "w").write(s)
PY
  [ "${PRE_W:-}" = 1 ] && mkdir -p "$R/p/cov2d-mumax-20261116"
  (export PATH="$SH:$PATH" SC_CNT="$R/sqcount" SC_IN="$R/in" "$@"; bash "$R/c.sh") > "$R/stdout" 2>&1; local rc=$?
  if grep -qE "$want" "$R/log" && [ "$(tail -1 "$R/log")" = DONE ]; then ok "$name (rc $rc): $(grep -E "$want" "$R/log" | head -1 | cut -c1-110)"
  else bad "$name (rc $rc, want /$want/)"; tail -12 "$R/log" "$R/stdout"; fi
  LASTW=$R/p/cov2d-mumax-20261116
  [ -d "$LASTW/deploy" ] && find "$LASTW/deploy" -delete
}
run clean '^D2 PASS: controls held, mu_max recorded for g18 and ar23, no atime moved'
grep -q 'll5d_mumax.py: OK' "$T0/clean/log" && grep -q 'geant_full.py: OK' "$T0/clean/log" && grep -q '^atime: 12 declared inputs, moved 0' "$T0/clean/log" && ! grep -q 'h2_definition.json\|cmodel_5d.json' "$LASTW/inputs.txt" 2>/dev/null \
  && ok "clean: code shas OK; the real watch list (2 + 2x4 products + 2 null records = 12) stat-ed; the deploy's plainly-read definition and cmodel are not in it; none moved" || { bad "clean: details"; grep -E 'OK|atime|declared' "$T0/clean/log"; }
run null-bad '^STOP null-g18.json is not the committed record' SC_NULL_BAD=1
run moved "^STOP an input's atime moved \(1\)" SC_MOVE=1
grep -q '^atime: 12 declared inputs, moved 1' "$T0/moved/log" && ok "moved: the real stat comparison counted the bumped input" || bad "moved: count"
run mumax-rc '^STOP mumax rc=2' SC_RC=2
run job-queued '^STOP a job of josephrb is queued or running' SC_SQ_NAMES=ll5d_x
run squeue-fails '^STOP squeue failed \(rc 1\)' SC_SQ_RC=1
PRE_W=1 run w-exists '^STOP .* exists'
find "$T0" -type f -exec rm -f {} + 2>/dev/null; find "$T0" -type l -exec rm -f {} + 2>/dev/null; find "$T0" -depth -type d -exec rmdir {} \; 2>/dev/null
[ -e "$T0" ] && echo "left: $T0"
[ "$fail" = 0 ] && echo "D2 CONNECT TEST PASS" || echo "D2 CONNECT TEST FAILED"
exit $fail

#!/bin/bash
# Local smoke of rsn_connect_post.sh (macOS or Linux; never connects). Usage:
#   bash smoke_connect_post.sh <new empty work dir> <a local clone that contains M_P1>
# The deploy is a clean clone at M_P1 (the real one). The connect copy differs from rsn_connect_post.sh only in P (->
# the work dir), PY (-> a stub) and the host test (-> $FAKE_HOST). The stub python runs the connect's own guard.py with
# the real interpreter but, for each of the three tools, substitutes a stand-in script that writes the tool's output
# and opens the files the real tool would (a frozen product, a staged input, the deploy's code); $SMOKE_TOOL makes one
# stand-in also open a denied path (refused by the guard, so the step STOPs) or an undeclared one (caught by the read
# log). The real tools need the cluster's data. Stubs: hostname, squeue ($SMOKE_SQUEUE), sacct ($SMOKE_SACCT), timeout.
W=${1:?work dir}; CLONE=${2:?local clone}
HERE=$(cd "$(dirname "$0")" && pwd)
MP1=5e43e509d08d9b294594988f2c21e50e281e7ad8
J2=61170759; J3=61170761
[ -d "$W" ] && [ -z "$(ls -A "$W")" ] || { echo "STOP: $W is not a new empty directory"; exit 9; }
mkdir -p "$W/bin" "$W/tools"
printf '#!/bin/bash\necho "${FAKE_HOST:-login27}"\n' > "$W/bin/hostname"
printf '#!/bin/bash\n[ -n "$SMOKE_SQUEUE" ] && printf "%%s\\n" "$SMOKE_SQUEUE"; exit 0\n' > "$W/bin/squeue"
printf '#!/bin/bash\nprintf "%%s\\n" "${SMOKE_SACCT:-%s|rsn_J2|COMPLETED|0:0|00:15:02\n%s|rsn_J3|COMPLETED|0:0|00:13:40}"\n' "$J2" "$J3" > "$W/bin/sacct"
printf '#!/bin/bash\nshift; exec "$@"\n' > "$W/bin/timeout"
cat > "$W/pystub" <<'PYSTUB'
#!/bin/bash
# the root_6_28 python: guard.py runs for real; each RSN tool is replaced by its stand-in in $SMOKE_TOOLS
if [[ "$*" == *guard.py* ]]; then
  a=("$@"); for x in "$@"; do case "$x" in */guard.py) t="$(dirname "$x")/smoke-tools" ;; esac; done
  mkdir -p "$t" && cp "$SMOKE_TOOLS"/*.py "$t/"   # inside the connect's own tmp, so the stand-ins are not themselves outside
  for i in "${!a[@]}"; do
    case "${a[$i]}" in */rsn_cmodel.py) a[$i]="$t/cmodel.py" ;; */rsn_regrade.py) a[$i]="$t/regrade.py" ;;
                       */rsn_read.py) a[$i]="$t/read.py" ;; esac; done
  exec python3 "${a[@]}"
fi
exec python3 "$@"
PYSTUB
cat > "$W/tools/common.py" <<'EOF'
import json, os, sys
def args():
    a, i = {}, 1
    while i < len(sys.argv):
        if sys.argv[i].startswith("--") and i + 1 < len(sys.argv) and not sys.argv[i + 1].startswith("--"):
            a[sys.argv[i]] = sys.argv[i + 1]; i += 2
        else:
            a[sys.argv[i]] = True; i += 1
    return a
def extra(tag):
    mode = os.environ.get("SMOKE_TOOL", "")
    if mode == f"{tag}:deny":
        open(os.environ["SMOKE_DENIED"], "rb").read(1)
    if mode == f"{tag}:outside":
        open(os.environ["SMOKE_OUTSIDE"], "rb").read(1)
EOF
cat > "$W/tools/cmodel.py" <<'EOF'
import json, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__))); import common
a = common.args(); assert sys.argv[1] == "build"
open(os.path.join(a["--products"], "L-5D-PV_e_tune_v1.npz"), "rb").read(); open(a["--p5"], "rb").read()
open(os.path.join(a["--rsn-products"], "G6_gibuu.npz"), "rb").read()
common.extra("build")
os.makedirs(os.path.dirname(a["--out-json"]), exist_ok=True)
open(a["--out-json"], "w").write(json.dumps({"schema": "rsn-cmodel/1", "stub": True}, indent=1) + "\n")
open(a["--out-npz"], "wb").write(b"stub npz")
print("[rsn] build stand-in")
EOF
cat > "$W/tools/regrade.py" <<'EOF'
import json, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__))); import common
a = common.args()
for k in ("--table", "--s1-npz", "--extra-block", "--flux-constraint", "--rsn-cmodel", "--rsn-cmodel-json"):
    open(a[k], "rb").read()
common.extra("regrade")
open(a["--out"], "w").write(json.dumps({"schema": "rsn-regrade/1", "stub": True}, indent=1) + "\n")
print("[rsn] regrade stand-in")
EOF
cat > "$W/tools/read.py" <<'EOF'
import json, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__))); import common
a = common.args()
for k in ("--prep", "--cmodel", "--regrade"):
    open(a[k], "rb").read()
common.extra("read")
open(a["--out"], "w").write(json.dumps({"schema": "rsn-readout/1", "stub": True}, indent=1) + "\n")
print("[rsn] read stand-in")
EOF
mkdir -p "$W/pyenv/bin"; mv "$W/pystub" "$W/pyenv/bin/python3"; chmod +x "$W/bin/"* "$W/pyenv/bin/python3"
git clone -q "$CLONE" "$W/template" || exit 1
mkB() {  # mkB <case>: a fresh P with B in the state J2 and J3 leave; the connect copy
  local c=$1 p="$W/p-$1" o="$W/p-$1/rsn-20261112/out"
  mkdir -p "$o/logs" "$o/products" "$o/stage" "$o/prep" "$p/pv-ladder-20261024/products" "$p/s5c-20260924/runs/p2" \
           "$p/cov2d-run-20261104" "$p/elsewhere"
  git -c advice.detachedHead=false clone -q "$W/template" "$p/rsn-20261112/deploy-p1" \
    && git -C "$p/rsn-20261112/deploy-p1" -c advice.detachedHead=false checkout -q "$MP1"
  echo frozen > "$p/pv-ladder-20261024/products/L-5D-PV_e_tune_v1.npz"
  echo e96d-input > "$p/s5c-20260924/runs/p2/bkg_dump.npz"; echo other > "$p/elsewhere/x.npz"
  printf '{\n "schema": "rsn-nc/1",\n "verdict": "PASS"\n}\n' > "$o/nc.json"; echo '{}' > "$o/prep/prep.json"
  for j in "J2 $J2 G6_gibuu SM_genie_mec SM_nuwro SM_gibuu WR_data WR_closure_tune_v1 WR_closure_nuwro TR_data" \
           "J3 $J3 WR_closure_gibuu WR_closure_q3 WU_closure_gibuu WU_closure_q3"; do
    set -- $j; local jn=$1 id=$2; shift 2
    { echo "[rsn] job=$jn slurm=$id"; for t in "$@"; do echo "$t" > "$o/products/$t.npz"; sha256sum "$o/products/$t.npz"; done
      echo "[rsn] job=$jn rc=0 end=2026-11-12T14:30:00Z"; } > "$o/logs/rsn_${jn}_$id.out"
  done
  python3 - "$HERE/rsn_connect_post.sh" "$W/$c.sh" "$p" "$o/stage" <<'EOF'
import hashlib, sys
src, dst, p, stage = sys.argv[1:5]
s = open(src).read()
# staged stand-ins whose sha256s replace the pins (the real staged files are on the cluster)
PINS = {"fd_f1_experiments.npz": "997c7dae34ef9703291baece51eed05f3dd7d38a043630cac9667efaad2775bc",
        "s1_assembly.npz": "db000707780d4d6da65389be9adedfd9a3ba6552a255f6ce81ccbdd0b8eb72a4",
        "cpl_block.npz": "d9aa32fdb64357760348c9ccbc32fbea81d517f0f0786eedf17ab4946eaca59f",
        "sorted_NuEConstraint_FHC_RHC_IMD.txt": "e38ad7d28354d071577113a18c8c569f88b6239f7fb193d20285273f172fc0c2"}
for name, pin in PINS.items():
    b = f"staged {name}\n".encode(); open(f"{stage}/{name}", "wb").write(b)
    assert s.count(pin) == 1, name
    s = s.replace(pin, hashlib.sha256(b).hexdigest())
for a, c in (("P=/pscratch/sd/j/josephrb", f"P={p}"), ("PY=/global/homes/j/josephrb/.conda/envs/root_6_28/bin/python3", f"PY={p}/../pyenv/bin/python3"),
             ('case "$(hostname -s)" in login[0-9][0-9])', 'case "${FAKE_HOST:-login27}" in login[0-9][0-9])')):
    assert s.count(a) == 1, a
    s = s.replace(a, c)
open(dst, "w").write(s)
EOF
}
run() {  # run <case> [env...]
  local n=$1; shift
  cp "$W/$n.sh" "$W/$n.self.sh"
  env PATH="$W/bin:$PATH" SMOKE_TOOLS="$W/tools" SMOKE_DENIED="$W/p-$n/s5c-20260924/runs/p2/bkg_dump.npz" \
      SMOKE_OUTSIDE="$W/p-$n/elsewhere/x.npz" "$@" bash "$W/$n.self.sh" "$W/$n.self.sh" > "$W/$n.out" 2>&1
  echo "## case $n rc=$?"
  grep -E 'REFUSED|STOP|GUARD|rc=[0-9]|OUTSIDE|READ SET|POST PASS|RSN read-set guard|^-- ' "$W/$n.out" \
    | grep -v '^== rsn connect' | sed -E -e "s|$W|<w>|g" | cut -c1-200
  echo "outputs: $(cd "$W/p-$n/rsn-20261112/out" && ls -d cmodel regrade.json rsn_readout.json 2>/dev/null | tr '\n' ' '); self copy removed: $([ -e "$W/$n.self.sh" ] && echo no || echo yes)"
}
mkB pass;     run pass
mkB rsnq;     run rsnq "SMOKE_SQUEUE=$J3|rsn_J3|RUNNING"
mkB host;     run host FAKE_HOST=dtn01
mkB slurm;    run slurm SLURM_JOB_ID=1
mkB j3fail;   run j3fail "SMOKE_SACCT=$J2|rsn_J2|COMPLETED|0:0|00:15:02"$'\n'"$J3|rsn_J3|TIMEOUT|0:15|00:19:00"
mkB j2rc;     sed -i.bak '/job=J2 rc=0/d' "$W/p-j2rc/rsn-20261112/out/logs/rsn_J2_$J2.out"; run j2rc
mkB prod;     echo tampered > "$W/p-prod/rsn-20261112/out/products/WU_closure_q3.npz"; run prod
mkB nonc;     rm -f "$W/p-nonc/rsn-20261112/out/nc.json"; run nonc
mkB dirty;    echo x > "$W/p-dirty/rsn-20261112/deploy-p1/nd-unfolding/rsn/stray.txt"; run dirty
mkB stage;    echo tampered > "$W/p-stage/rsn-20261112/out/stage/cpl_block.npz"; run stage
mkB exists;   echo '{}' > "$W/p-exists/rsn-20261112/out/regrade.json"; run exists
mkB denybuild; run denybuild SMOKE_TOOL=build:deny
mkB denyread;  run denyread SMOKE_TOOL=read:deny
mkB outside;   run outside SMOKE_TOOL=regrade:outside
echo "## the deny cases: the guard's refusals (it raises before the open, so the denied file is never opened)"
for n in denybuild denyread; do
  f="$W/p-$n/s5c-20260924/runs/p2/bkg_dump.npz"
  echo "  $n: $(grep -c 'refusing to open .*bkg_dump.npz' "$W/$n.out") refusal line(s) naming bkg_dump.npz"
done

#!/bin/bash
# EVW2D: the connect, on a Perlmutter login node, in the foreground, after the director's binding and GO on this
# script's sha256, the tool commit C and the launcher. EVW5D's connect (fd/evw5d-20261125/launch/), adapted. In order,
# each failure a final stop before anything is submitted:
#   preconditions (nothing written): every pin filled in; the lane root absent; no evw2d job queued or running
#     (squeue --me, fails closed); the two inputs present at their recorded sizes (stat of each explicit path);
#   then the lane root by mkdir (no -p: the exclusive claim) and its logs; the stat records of the two inputs;
#   the balance from iris: the job's bound, 0.5 node-h (one node x --time 00:30:00), at most half of m3246's balance;
#   deploy_M, a fresh clone at M, clean (porcelain --ignored 0), the four pinned files and setup_salloc_env.sh at
#     their recorded sha256;
#   deploy_C, a fresh clone at C, clean, with evw2d.py, sbatch_evw2d.sh, config.json, the declaration and
#     references.npz at their bound sha256; config.json names this lane root, deploy_M, the staging root and the bound
#     declaration digest;
#   the environment pre-check (0 node-h): setup_salloc_env.sh sourced in a subshell, python3 = root_6_28's, numpy,
#     lightgbm and ROOT import, and a real O_NOATIME open of a file of this lane on $SCRATCH;
#   the staging (0 node-h): `evw2d.py stage` on this login node (the declaration's §2 and §6: O_NOATIME copies from
#     CFS into the staging root, each checked against its pin; the root then 0555), with stat records of the two
#     sources before and after;
#   the held-file read (0 node-h): the staged omnifile opened through O_NOATIME and read by ROOT and RDataFrame through
#     /proc/self/fd/N, as C-KEY reads it;
#   one sbatch --hold, with every inherited SBATCH_/SLURM_/SALLOC_ variable removed and the allocation, output and
#     error given explicitly (--nodes=1 --ntasks=1 --time=00:30:00 --parsable); the job id is checked and saved; then
#     scontrol (exit status 0, up to three tries) must show exactly one record, this job's, with TimeLimit 00:30:00,
#     NumNodes 1 (a pending job prints 1-1) and no array token; only then is the job released. Any failure cancels it.
# Writes only under the lane root (on $SCRATCH; nothing on CFS, which is only read, by evw2d.py's O_NOATIME copies).
# No set -u (it kills setup_salloc_env.sh). Launched from a /dev/shm copy of itself, whose path is $1; it deletes that
# copy at exit.
SELF=$1
LANE=__LANE_ROOT__
DM=$LANE/deploy_M
DC=$LANE/deploy_C
ST=$LANE/stage
L=$LANE/logs
M=77d76cfc2d621f8faa010b75006811868494652a
C=__TOOL_COMMIT__
EVW_SHA=__EVW2D_PY_SHA256__
SBATCH_SHA=__SBATCH_SHA256__
CFG_SHA=__CONFIG_SHA256__
DEC_SHA=__DECLARATION_SHA256__
REFS_SHA=1b21458283c06531c9791efdc1e15f9d685d0733e398288a715768d61b612a03
BOUND=0.5
TLIMIT=00:30:00
CV=/global/cfs/cdirs/m3246/josephrb/two-d-followup-20261010/xr-input/runEventLoopOmniFold_MEFHC.root
MC=/global/cfs/cdirs/m3246/josephrb/minerva-shutdown-stage/fig_products/2d-unfolding/baseline_flux/runEventLoopMC_MEFHC.root
CV_BYTES=2144008221   # REF-C2C1's stage.json (fd/receipts-ref-c2c1/cdraw/run/stage.json)
MC_BYTES=5143
bail() { echo "STOP (nothing written): $*"; rm -f -- "$SELF"; exit 9; }
LANE_PARENT=/pscratch/sd/j/josephrb
[ -d "$LANE_PARENT" ] && [ ! -L "$LANE_PARENT" ] && [ "$(cd "$LANE_PARENT" && pwd -P)" = "$LANE_PARENT" ] || bail "$LANE_PARENT is not a real directory"
case "$LANE" in "$LANE_PARENT"/evw2d-20[0-9][0-9][0-9][0-9][0-9][0-9]) ;; *) bail "lane root $LANE";; esac
case "$C$EVW_SHA$SBATCH_SHA$CFG_SHA$DEC_SHA" in *__*) bail "a pin is not filled in";; esac
[ ! -e "$LANE" ] && [ ! -L "$LANE" ] || bail "$LANE exists"
q=$(squeue --me -h -o '%j') || bail "squeue did not answer"   # fails closed
[ -z "$(printf '%s\n' "$q" | grep -E '^evw2d$')" ] || bail "an evw2d job is queued or running"
[ "$(stat -c %s "$CV" 2>/dev/null)" = "$CV_BYTES" ] || bail "$CV is not $CV_BYTES bytes"
[ "$(stat -c %s "$MC" 2>/dev/null)" = "$MC_BYTES" ] || bail "$MC is not $MC_BYTES bytes"
mkdir "$LANE" || bail "mkdir $LANE"                 # the exclusive claim
mkdir "$L" || bail "mkdir $L"
[ "$(cd "$LANE" && pwd -P)" = "$LANE" ] && [ "$(cd "$L" && pwd -P)" = "$L" ] || bail "the lane is reached through a link"
LOG=$L/connect.log
exec > "$LOG" 2>&1
finish() { echo "evw2d connect rc=$1"; date -u +%FT%TZ; echo "$1" > "$L/connect.done"; rm -f -- "$SELF"; exit "$1"; }
echo "node $(hostname) nproc=$(nproc) loadavg $(cut -d' ' -f1-3 /proc/loadavg)"
date -u +%FT%TZ
echo "connect script sha256 $(sha256sum "$SELF" | cut -d' ' -f1)"
cp "$SELF" "$L/evw2d_connect.sh"
echo "squeue --me before:"; squeue --me -h -o "%i %j %T"
echo "== the two inputs (stat: name|bytes|atime|mtime|inode)"
stat -c '%n|%s|%X|%Y|%i' "$CV" "$MC" > "$L/stat-sources-before.txt" || { echo "STOP: stat of the inputs"; finish 9; }
cat "$L/stat-sources-before.txt"

# ---- the balance (EVW5D's method): iris's m3246 row, Allocated - Charged
echo "== iris"; timeout 120 iris < /dev/null > "$L/iris.txt" 2>&1; irc=$?
echo "iris rc=$irc"; [ "$irc" -eq 0 ] || { echo "STOP: iris failed"; finish 9; }
rows=$(grep -E '^m3246 ' "$L/iris.txt"); echo "$rows"
[ "$(printf '%s\n' "$rows" | grep -c .)" = 1 ] || { echo "STOP: not one m3246 row in iris"; finish 9; }
num='^[0-9]+(\.[0-9]+)?$'
alloc=$(echo "$rows" | awk '{print $5}'); charged=$(echo "$rows" | awk '{print $4}')
printf '%s\n%s\n' "$alloc" "$charged" | grep -Evq "$num" && { echo "STOP: the m3246 row is not numeric"; finish 9; }
echo "allocated=$alloc charged=$charged bound=$BOUND"
awk -v a="$alloc" -v u="$charged" -v c=$BOUND 'BEGIN{exit !(c <= (a - u) / 2)}' || { echo "STOP: the bound $BOUND is above half the balance"; finish 9; }

# ---- deploy_M: a fresh clone at M, clean, the pinned driver files and the environment script
git clone -q https://github.com/josephbaileyy/MINERvA-OmniFold.git "$DM" > "$L/clone-M.log" 2>&1 || { echo "STOP: clone M"; finish 3; }
git -C "$DM" -c advice.detachedHead=false checkout -q "$M" || { echo "STOP: checkout M"; finish 3; }
[ "$(git -C "$DM" rev-parse HEAD)" = "$M" ] || { echo "STOP: deploy_M's HEAD is not M"; finish 9; }
st=$(git -C "$DM" status --porcelain --ignored) || { echo "STOP: git status in deploy_M"; finish 9; }
echo "deploy_M HEAD $M; porcelain --ignored: '${st}'"; [ -z "$st" ] || { echo "STOP: deploy_M is not clean"; finish 9; }
( cd "$DM" && sha256sum -c ) <<SUMS || { echo "STOP: a driver file is not the pinned one"; finish 9; }
938c53c5a018d20f5b148f6bdc2949e987a60085c5d0b7913ccdd5bb438b5a3b  2d-unfolding/re2/re2_driver.py
e96234124a31edd7a8dd61fdb16cb48a5b28cbd1b90202f59b0095868378227a  unbinned_unfolding/python/omnifold.py
285dd138363d090a4ce5dea3361be81fada8680bd782b918e9d95198d1b5d6ea  2d-unfolding/ref_c2c1/ref_c2c1.py
9127b45a7d2db5fe5ee711628e4b2207a2dd767e2b0c2fb545114fa9fe2428d2  2d-unfolding/ref_c2c1/config.json
ea3c6998d33f45c831b80da5e5228032a19fc392018ede54a7f52f2f283d1d48  setup_salloc_env.sh
SUMS

# ---- deploy_C: a fresh clone at C, clean, the bound bytes, and config.json naming this layout
git clone -q https://github.com/josephbaileyy/MINERvA-OmniFold.git "$DC" > "$L/clone-C.log" 2>&1 || { echo "STOP: clone C"; finish 3; }
git -C "$DC" -c advice.detachedHead=false checkout -q "$C" || { echo "STOP: checkout C"; finish 3; }
[ "$(git -C "$DC" rev-parse HEAD)" = "$C" ] || { echo "STOP: deploy_C's HEAD is not C"; finish 9; }
st=$(git -C "$DC" status --porcelain --ignored) || { echo "STOP: git status in deploy_C"; finish 9; }
echo "deploy_C HEAD $C; porcelain --ignored: '${st}'"; [ -z "$st" ] || { echo "STOP: deploy_C is not clean"; finish 9; }
( cd "$DC" && sha256sum -c ) <<SUMS || { echo "STOP: deploy_C is not the bound bytes"; finish 9; }
$EVW_SHA  2d-unfolding/evw2d/evw2d.py
$SBATCH_SHA  2d-unfolding/evw2d/sbatch_evw2d.sh
$CFG_SHA  2d-unfolding/evw2d/config.json
$DEC_SHA  docs/orchestration/state/2d-closeout/evw2d-20261124/EVW2D-DECLARATION.md
$REFS_SHA  2d-unfolding/evw2d/references.npz
SUMS
python3 -I - "$DC/2d-unfolding/evw2d/config.json" "$LANE" "$DM" "$ST" "$DEC_SHA" "$M" <<'PY' || { echo "STOP: config.json does not name this layout"; finish 9; }
import json, sys
c = json.load(open(sys.argv[1]))
want = {"lane_root": sys.argv[2], "driver_tree.root": sys.argv[3], "staging.root": sys.argv[4],
        "declaration_sha256": sys.argv[5], "driver_tree.commit": sys.argv[6]}
got = {"lane_root": c["lane_root"], "driver_tree.root": c["driver_tree"]["root"],
       "staging.root": c["inputs"]["staging"]["root"], "declaration_sha256": c["declaration_sha256"],
       "driver_tree.commit": c["driver_tree"]["commit"]}
print("config.json binding:", json.dumps(got))
sys.exit(0 if got == want else 1)
PY

# ---- the environment the job will source, and a real O_NOATIME open on $SCRATCH (0 node-h)
out=$( source "$DM/setup_salloc_env.sh" > "$L/env-precheck.log" 2>&1; rc=$?
       echo "SOURCE_RC=$rc"; [ "$rc" -eq 0 ] || exit 96
       [ "$(command -v python3)" = "$HOME/.conda/envs/root_6_28/bin/python3" ] || { echo NOT_ROOT628; exit 98; }
       PYTHONDONTWRITEBYTECODE=1 python3 -B -c "import os, sys, numpy, lightgbm, ROOT
assert not getattr(sys, 'pycache_prefix', None), 'a redirected bytecode cache is set'
fd = os.open(sys.argv[1], os.O_RDONLY | os.O_NOATIME); os.close(fd)
print('python', sys.version.split()[0], 'numpy', numpy.__version__, 'lightgbm', lightgbm.__version__, 'ROOT', ROOT.gROOT.GetVersion(), 'O_NOATIME', os.O_NOATIME, 'open with O_NOATIME on', sys.argv[1], 'ok')" "$L/evw2d_connect.sh" || exit 97 )
erc=$?
echo "$out"
[ "$erc" -eq 0 ] || { echo "STOP: the environment pre-check failed (rc $erc; see env-precheck.log)"; finish 7; }

# ---- the staging, on this login node (0 node-h): evw2d.py stage, its own gates first
date -u +%FT%TZ
( source "$DM/setup_salloc_env.sh" > "$L/env-stage.log" 2>&1 || exit 96
  cd "$L" || exit 95
  PYTHONDONTWRITEBYTECODE=1 python3 -B "$DC/2d-unfolding/evw2d/evw2d.py" --config-sha256 "$CFG_SHA" stage \
    > "$L/stage.json" 2> "$L/stage.err" )
src=$?
echo "evw2d.py stage rc=$src"; cat "$L/stage.json" "$L/stage.err"
[ "$src" -eq 0 ] || { echo "STOP: the staging failed"; finish 7; }
stat -c '%n|%s|%X|%Y|%i' "$CV" "$MC" > "$L/stat-sources-after.txt" || { echo "STOP: stat of the inputs"; finish 9; }
cat "$L/stat-sources-after.txt"
[ "$(stat -c %a "$ST")" = 555 ] || { echo "STOP: the staging root is not 0555"; finish 9; }
ls -la "$ST"

# ---- the held-file read, as C-KEY makes it (0 node-h): ROOT and RDataFrame through /proc/self/fd/N on Lustre
hout=$( source "$DM/setup_salloc_env.sh" > "$L/env-heldread.log" 2>&1 || exit 96
        cd "$L" || exit 95
        PYTHONDONTWRITEBYTECODE=1 python3 -B -c "import os, sys, ROOT
fd = os.open(sys.argv[1], os.O_RDONLY | os.O_NOATIME)
p = f'/proc/self/fd/{fd}'
f = ROOT.TFile.Open(p)
assert f and not f.IsZombie(), 'TFile.Open through ' + p
n = f.Get('mc_signal_reco').GetEntries()
v = ROOT.RDataFrame('mc_signal_reco', p).Range(3).AsNumpy(['MC'])['MC']
assert n > 0 and len(v) == 3, (n, v)
print('held read through', p, 'entries', n, 'first MC', list(v))" "$ST/runEventLoopOmniFold_MEFHC.root" 2>&1 )
hrc=$?
echo "$hout"
[ "$hrc" -eq 0 ] || { echo "STOP: ROOT could not read the held file through /proc/self/fd (rc $hrc)"; finish 7; }
for c in "$DM" "$DC"; do
  st=$(git -C "$c" status --porcelain --ignored) || { echo "STOP: git status failed in $c"; finish 9; }
  [ -z "$st" ] || { echo "STOP: the pre-checks changed $c: $st"; finish 9; }
done

# ---- the submission, from the plain login environment
q=$(squeue --me -h -o '%j') || { echo "STOP: squeue did not answer"; finish 9; }
[ -z "$(printf '%s\n' "$q" | grep -E '^evw2d$')" ] || { echo "STOP: an evw2d job appeared"; finish 9; }
[ ! -e "$LANE/out" ] || { echo "STOP: $LANE/out exists"; finish 9; }
date -u +%FT%TZ
cd "$LANE" || finish 9
for v in $(env | sed -n 's/^\(\(SBATCH\|SLURM\|SALLOC\)_[A-Za-z0-9_]*\)=.*/\1/p'); do unset "$v"; done
echo "inherited scheduler variables left: $(env | grep -cE '^(SBATCH|SLURM|SALLOC)_')"
sbatch --parsable --hold --nodes=1 --ntasks=1 --time=$TLIMIT --job-name=evw2d \
  --output="$L/%x_%j.out" --error="$L/%x_%j.err" \
  "$DC/2d-unfolding/evw2d/sbatch_evw2d.sh" "$LANE" "$DM" "$M" "$DC" "$C" "$EVW_SHA" "$CFG_SHA" \
  > "$L/submit.out" 2> "$L/submit.err"
rc=$?; echo "sbatch rc=$rc"; cat "$L/submit.out" "$L/submit.err"
[ $rc = 0 ] || { echo "STOP at sbatch (final)"; finish $rc; }
job=$(sed -n 's/^\([0-9][0-9]*\)\(;.*\)\{0,1\}$/\1/p' "$L/submit.out")
if [ -z "$job" ] || [ "$(wc -l < "$L/submit.out")" -ne 1 ]; then   # the job is held: it cannot start
  echo "STOP: not one job id; cancelling this user's held evw2d jobs"
  scancel --me --name=evw2d --state=PENDING; echo "scancel rc=$?"; finish 9
fi
echo "evw2d job $job (held)"
echo "$job" > "$L/evw2d.jobid" || { scancel "$job"; echo "STOP: could not save the job id; job $job cancelled (rc $?)"; finish 9; }
# ---- the allocation check (begin)
tok() { printf '%s\n' "$1" | tr ' ' '\n' | sed -n "s/^$2=//p" | head -1; }
src=1
for try in 1 2 3; do
  sj=$(scontrol -o show job "$job" 2>&1); src=$?
  [ "$src" -eq 0 ] && break
  echo "scontrol try $try rc=$src: $sj"; sleep 5
done
nrec=$(printf '%s\n' "$sj" | grep -c '^JobId=')
id=$(tok "$sj" JobId); tl=$(tok "$sj" TimeLimit); nn=$(tok "$sj" NumNodes)
arr=$(printf '%s\n' "$sj" | tr ' ' '\n' | grep -c '^Array')
echo "scontrol rc=$src records=$nrec JobId=$id TimeLimit=$tl (declared $TLIMIT) NumNodes=$nn array_tokens=$arr"
if [ "$src" -ne 0 ] || [ "$nrec" != 1 ] || [ "$id" != "$job" ] || [ "$tl" != "$TLIMIT" ] || \
   ! printf '%s' "$nn" | grep -Eq '^1(-1)?$' || [ "$arr" != 0 ]; then   # pending: NumNodes=1-1
  scancel "$job"; echo "STOP: the allocation is not one 30-minute node, or scontrol did not show it; job $job cancelled (scancel rc $?)"
  sleep 5; sacct -j "$job" -X -n -P -o JobID,State,Elapsed; finish 6
fi
scontrol release "$job"; rrc=$?
echo "scontrol release rc=$rrc"
if [ "$rrc" -ne 0 ]; then
  scancel "$job"; echo "STOP: the release failed; job $job cancelled (scancel rc $?)"; finish 6
fi
# ---- the allocation check (end)
sleep 5
squeue -j "$job" -h -o "%i %j %T"; scontrol -o show job "$job" | tr ' ' '\n' | grep -E '^(JobState|Reason|TimeLimit|NumNodes|QOS|Account|Partition)='
finish 0

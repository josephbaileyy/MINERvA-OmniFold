#!/bin/bash
# REF-C2C1 C-DRAW, step B of 2 (REF-C2C1-BINDING-1.md rulings 4 and 5; the director's ruling 3(b), 2026-11-05), on a
# login node, detached. Gated on step A's record: $O/stage.json must have the sha256 passed as $2 (the director was
# sent it), verdict PASS, and the staged CV copy and the recorded S1_001 copy are re-read (O_NOATIME) and must still be
# 43f8cc16 and 2ea9b7d2. Then: the iris half-balance check; a fresh clean clone of RE-2's deploy pin dbdad2f9 into
# $O/deploy-dbdad2f9 with the driver, the guard and setup_salloc_env.sh verified by blob; the comparison script
# (cdraw_compare.py, sha256 4a1cf834...) and the job script (cdraw_job.sbatch, 3c1d6c2e...) written from this file and
# refused unless their sha256 are those, the committed copies' (fd/receipts-ref-c2c1/cdraw/); one sbatch,
# --time=00:45:00 (at most 0.75 node-h, against the 12.5 cap); scontrol's TimeLimit must read 00:45:00, else scancel,
# rc 6. Writes only under $O. No set -u. Any stop is final. Launched from a /dev/shm copy of itself ($1).
SELF=$1
STAGE_SHA=$2
O=/pscratch/sd/j/josephrb/ref-c2c1-20261105/cdraw
D=$O/deploy-dbdad2f9
PIN=dbdad2f93a255f1bd4bf357951aaa5689aaac512
TLIMIT=00:45:00
PRICE=0.75
CMP_SHA=4a1cf83436872b864ae7c86a80b57a732c4617c8c558b27a77f6291f62477504
JOB_SHA=3c1d6c2ee0d0e51350e9235642623ca9ca02d06b45f9a7e761c80b6fc0616bbf
bail() { rm -f -- "$SELF"; exit 9; }                             # a precondition failed: nothing written
nsha() { dd if="$1" iflag=noatime status=none | sha256sum | cut -d' ' -f1; }
case "$(hostname)" in login*) ;; *) bail ;; esac
case "$STAGE_SHA" in [0-9a-f]*) [ ${#STAGE_SHA} = 64 ] || bail ;; *) bail ;; esac
[ -s "$O/stage.json" ] && [ "$(dd if="$O/stage.done" iflag=noatime status=none)" = 0 ] || bail
for x in logs deploy-dbdad2f9 out cdraw.json cdraw_compare.py cdraw_job.sbatch deletions.tsv; do [ ! -e "$O/$x" ] || bail; done
[ -z "$(squeue --me -h -n fd_cdraw -o %i)" ] || bail
mkdir "$O/logs" || bail
exec > "$O/logs/connect.log" 2>&1
finish() { echo "cdraw submit rc=$1"; date -u +%FT%TZ; echo "$1" > "$O/logs/connect.done"; rm -f -- "$SELF"; exit "$1"; }
echo "node $(hostname) nproc=$(nproc) loadavg $(cut -d' ' -f1-3 /proc/loadavg)"
date -u +%FT%TZ
echo "connect script sha256 $(sha256sum "$SELF" | cut -d' ' -f1)"
cp "$SELF" "$O/logs/cdraw_submit_login.sh"
got=$(nsha "$O/stage.json"); echo "stage.json sha256 $got (expected $STAGE_SHA)"
[ "$got" = "$STAGE_SHA" ] || { echo "STOP: the stage record is not the one sent"; finish 4; }
dd if="$O/stage.json" iflag=noatime status=none | env -u PYTHONPATH "$HOME/.conda/envs/root_6_28/bin/python3" -I -c "
import json, sys
r = json.load(sys.stdin)
c = {'verdict PASS': r.get('verdict') == 'PASS', 'checks': all(r.get('checks', {}).values()) and len(r.get('checks', {})) == 3}
print('stage record:', c, 'written', r.get('written_utc')); sys.exit(0 if all(c.values()) else 1)" || { echo "STOP: the stage record does not pass"; finish 4; }
cv=$(nsha "$O/inputs/runEventLoopOmniFold_MEFHC.root"); rc1=$(nsha "$O/recorded/S1_001_xsec.root")
echo "staged CV copy sha256 $cv; recorded S1_001 copy sha256 $rc1"
[ "$cv" = 43f8cc16ab2688200d3e2e0ebb48012b23ada6d7882b8c68ecfc51c609aeb8df ] && [ "$rc1" = 2ea9b7d241363c231ce25715b7bfd0ddd4ec2406c59972ecaaa6fb6e05462377 ] \
  || { echo "STOP: a staged file changed"; finish 4; }
echo "== iris"; row=$(timeout 120 iris < /dev/null 2>&1 | grep -E '^m3246 ' | head -1); echo "$row"
bal=$(echo "$row" | awk 'NF>=5 {printf "%.1f", $5-$4}')
[ -n "$bal" ] || { echo "STOP: could not read the m3246 balance"; finish 9; }
echo "balance_node_h=$bal half=$(awk -v b=$bal 'BEGIN{printf "%.1f", b/2}') price=$PRICE"
awk -v b=$bal -v c=$PRICE 'BEGIN{exit !(c <= b/2)}' || { echo "STOP: the price is above half the balance: to Joseph"; finish 9; }
git clone -q https://github.com/josephbaileyy/MINERvA-OmniFold.git "$D" > "$O/logs/clone.log" 2>&1 || { echo "STOP: clone"; finish 3; }
git -C "$D" -c advice.detachedHead=false checkout -q "$PIN" || { echo "STOP: checkout"; finish 3; }
[ "$(git -C "$D" rev-parse HEAD)" = "$PIN" ] || { echo "STOP: HEAD is not dbdad2f9"; finish 9; }
n=$(git -C "$D" status --porcelain --ignored | wc -l); echo "HEAD $PIN; porcelain --ignored lines before: $n"
[ "$n" -eq 0 ] || { echo "STOP: the deploy is not clean"; finish 9; }
bad=0
while read -r b p; do
  [ "$(git -C "$D" rev-parse "$PIN:$p")" = "$b" ] && [ "$(git -C "$D" hash-object "$p")" = "$b" ] || { echo "MISMATCH $p"; bad=$((bad + 1)); }
done <<BLOBS
4c7e9d75508fce8ec4bf26c3dd0f037c96af858f 2d-unfolding/re2/re2_driver.py
3929da3add044863233132c89a3d6c75587650ba nd-unfolding/mnv_guarded_run.py
b4a9c3f6bb766d8488cbab98878cbac1262cc1bb setup_salloc_env.sh
BLOBS
echo "deploy blobs: 3 checked, $bad mismatches"; [ "$bad" -eq 0 ] || { echo "STOP: bound bytes"; finish 9; }
cat > "$O/cdraw_compare.py" <<'CMPEOF'
"""C-DRAW (REF-C2C1-DECLARATION.md §1.3; REF-C2C1-BINDING-1.md ruling 4): do Q_R's replicas regenerate from their seeds?

The rule, fixed in the declaration: one replica (S1_001, bootstrap seed 1) is regenerated by RE-2's bound driver at its
deploy pin (dbdad2f9) with its recorded argv, and its deterministic p1Streams record must EQUAL the recorded product's
exactly. p1Streams is the TNamed the driver writes (re2_driver.py:2223-2228 at dbdad2f9; :2244 on main): the bootstrap
seed, the per-stream seed offsets, the per-stream event counts n and weight sums, and the background fill rows. All of
it is set by the seeded Poisson draws before any fit, so it is compared whole, field by field, with ==. The fitted
refinement aggregates are not compared (the declaration: "The refined sums are fitted, so they are not used").

    python3 cdraw_compare.py <regenerated xsec.root> <recorded xsec.root (an O_NOATIME copy)> <out.json>

Prints both records and one line, PASS or FAIL. Exit 0 on PASS, 1 on FAIL, 2 if a record is missing.
"""
import json
import sys

import ROOT


def streams(path: str) -> dict | None:
    f = ROOT.TFile.Open(path, "READ")
    if not f or f.IsZombie():
        return None
    obj = f.Get("p1Streams")
    rec = json.loads(obj.GetTitle()) if obj else None
    f.Close()
    return rec


def main() -> int:
    new_path, rec_path, out = sys.argv[1:4]
    new, rec = streams(new_path), streams(rec_path)
    if new is None or rec is None:
        print(f"C-DRAW: a p1Streams record is missing (regenerated {new is not None}, recorded {rec is not None})")
        return 2
    fields = sorted(set(new) | set(rec))
    equal = {k: new.get(k) == rec.get(k) for k in fields}
    for k in fields:
        print(f"{k}: regenerated {json.dumps(new.get(k), sort_keys=True)} | recorded {json.dumps(rec.get(k), sort_keys=True)}"
              f" | {'equal' if equal[k] else 'DIFFERS'}")
    verdict = "PASS" if new == rec else "FAIL"
    with open(out, "w") as fh:
        json.dump({"schema": "ref-c2c1-cdraw/1", "replica": "S1_001", "regenerated": new, "recorded": rec,
                   "field_equal": equal, "verdict": verdict,
                   "rule": "the regenerated p1Streams record equals the recorded one exactly (== on every field)"},
                  fh, indent=1, sort_keys=True)
        fh.write("\n")
    print(f"C-DRAW {verdict}")
    return 0 if verdict == "PASS" else 1


if __name__ == "__main__":
    sys.exit(main())
CMPEOF
cat > "$O/cdraw_job.sbatch" <<'JOBEOF'
#!/bin/bash
#SBATCH --account=m3246
#SBATCH --qos=regular
#SBATCH --constraint=cpu
#SBATCH --nodes=1
#SBATCH --exclusive
#SBATCH --no-requeue
# REF-C2C1 C-DRAW job: regenerate Q_R replica S1_001 through RE-2's bound driver at its deploy pin (dbdad2f9), with
# its recorded argv (partb_runs.tsv), the way part B's lanes ran it (re2b_job.sbatch: the OI-136 guard, one srun step,
# 64 CPUs, the re2_preflight environment); then cdraw_compare.py: PASS iff the regenerated p1Streams record equals the
# recorded one exactly. Then the staged CV copy is deleted with a ledger row (the director's ruling 3(b)).
# Arguments: <deploy> <O>. Writes only under <O>.
set -o pipefail   # NOT set -u
C="${1:?deploy}"; O="${2:?out}"
MC=/pscratch/sd/j/josephrb/MINERvA-OmniFold/2d-unfolding/baseline_flux/runEventLoopMC_MEFHC.root
CVS=/pscratch/sd/j/josephrb/ref-c2c1-20261105/cdraw/inputs/runEventLoopOmniFold_MEFHC.root
[ "$O" = /pscratch/sd/j/josephrb/ref-c2c1-20261105/cdraw ] || { echo "[cdraw] refusing: O is $O"; exit 2; }
[ "$(git -C "$C" rev-parse HEAD)" = dbdad2f93a255f1bd4bf357951aaa5689aaac512 ] || { echo "[cdraw] refusing: deploy HEAD is not dbdad2f9"; exit 2; }
[ -z "$(git -C "$C" status --porcelain)" ] || { echo "[cdraw] refusing: the deploy is not clean"; exit 2; }
echo "[cdraw] start $(date -u +%FT%TZ) job=$SLURM_JOB_ID node=$(hostname) deploy HEAD $(git -C "$C" rev-parse HEAD)"
source "$C/setup_salloc_env.sh"   # root_6_28, as re2_preflight sources it (set -u would abort its activation)
export TMPDIR=$O/tmp PYTHONUNBUFFERED=1 PYTHONDONTWRITEBYTECODE=1
export OMP_NUM_THREADS=64 MKL_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 NUMEXPR_NUM_THREADS=1   # as part B (re2_env.sh)
unset LOKY_MAX_CPU_COUNT
mkdir -p "$TMPDIR" "$O/out/S1_001" "$O/logs" "$O/inventory"
srun -n1 -c 64 --mem="$((64 * 1905))M" --exact --job-name=S1_001 \
    python "$C/nd-unfolding/mnv_guarded_run.py" --expect-root "$C" --label cdraw_S1_001 \
    --inventory "$O/inventory/S1_001.jsonl" -- "$C/2d-unfolding/re2/re2_driver.py" \
    --omnifile "$CVS" --mcfile "$MC" --iters 5 --use-weights --estimator lgbm --seed 42 --bootstrap-seed 1 \
    --bootstrap-streams three --bkg-mode negweight-refined --refine-n-estimators 400 --refine-num-leaves 31 \
    --out "$O/out/S1_001/xsec.root" < /dev/null > "$O/logs/S1_001.log" 2>&1
drc=$?
echo "[cdraw] driver rc=$drc end=$(date -u +%FT%TZ)"
crc=9
if [ "$drc" -eq 0 ]; then
    python3 "$O/cdraw_compare.py" "$O/out/S1_001/xsec.root" "$O/recorded/S1_001_xsec.root" "$O/cdraw.json" > "$O/logs/compare.log" 2>&1
    crc=$?
    cat "$O/logs/compare.log"
fi
echo "[cdraw] compare rc=$crc"
# the staged copy, deleted after the run with a ledger row (the B9 form: utc, path, sha256, size, mtime, inode, condition)
if [ -f "$CVS" ]; then
    st=$(stat -c '%s %Y %i' "$CVS")
    printf '%s\t%s\t%s\t%s\t%s\t%s\t%s\n' "$(date -u +%FT%TZ)" "$CVS" 43f8cc16ab2688200d3e2e0ebb48012b23ada6d7882b8c68ecfc51c609aeb8df \
        $st "C-DRAW run over (driver rc $drc, compare rc $crc); staged from CFS by cdraw_stage_dtn.sh, checked in stage.json" >> "$O/deletions.tsv"
    rm -f -- /pscratch/sd/j/josephrb/ref-c2c1-20261105/cdraw/inputs/runEventLoopOmniFold_MEFHC.root
    echo "[cdraw] staged copy deleted (rc $?), ledger row in deletions.tsv"
fi
[ "$drc" -eq 0 ] && [ "$crc" -le 1 ] || exit 1
exit 0
JOBEOF
c=$(sha256sum "$O/cdraw_compare.py" | cut -d' ' -f1); j=$(sha256sum "$O/cdraw_job.sbatch" | cut -d' ' -f1)
echo "cdraw_compare.py sha256 $c; cdraw_job.sbatch sha256 $j"
[ "$c" = "$CMP_SHA" ] && [ "$j" = "$JOB_SHA" ] || { echo "STOP: the comparison or job script is not the committed one"; finish 9; }
echo "squeue --me before:"; squeue --me -h -o "%i %j %T"
date -u +%FT%TZ
cd "$O" || finish 9
sbatch --time=$TLIMIT --job-name=fd_cdraw --output="$O/logs/%x_%j.out" "$O/cdraw_job.sbatch" "$D" "$O" > "$O/logs/submit.out" 2>&1
rc=$?; echo "sbatch rc=$rc"; cat "$O/logs/submit.out"
[ $rc = 0 ] || { echo "STOP at sbatch (final)"; finish $rc; }
job=$(sed -n 's/^Submitted batch job \([0-9][0-9]*\)$/\1/p' "$O/logs/submit.out")
[ -n "$job" ] || { echo "STOP: no job id"; finish 9; }
echo "cdraw job $job"; echo "$job" > "$O/logs/cdraw.jobid"
tl=$(scontrol show job "$job" | sed -n 's/.*TimeLimit=\([^ ]*\).*/\1/p' | head -1)
echo "scontrol TimeLimit=$tl (declared $TLIMIT)"
if [ "$tl" != "$TLIMIT" ]; then
  scancel "$job"; echo "STOP: TimeLimit $tl is not $TLIMIT; job $job cancelled (rc $?)"; sleep 5
  sacct -j "$job" -X -n -P -o JobID,State,Elapsed; finish 6
fi
sleep 5
squeue -j "$job" -h -o "%i %j %T %M %l %D %q %a"
n=$(git -C "$D" status --porcelain --ignored | wc -l); echo "porcelain --ignored lines after: $n"
[ "$n" -eq 0 ] || { echo "the deploy changed after the submission (the job is queued; reported, not cancelled)"; finish 8; }
finish 0

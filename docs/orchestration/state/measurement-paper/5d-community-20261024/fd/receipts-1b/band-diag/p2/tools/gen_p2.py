"""Generate bdg_p2_login.sh, the band diagnosis's P2 submit connect, embedding its three tools by base64."""
import base64
import hashlib
from pathlib import Path

S = Path("/private/tmp/claude-501/-Users-josephbailey-local-research-MINERvA-OmniFold/7e3f49f7-e8e4-452d-b380-399d4f6c529e/scratchpad")
tools = {"bdg_p2_wrapper.sh": S / "bdg/p2/bdg_p2_wrapper.sh", "pfd_threadprobe.py": S / "pfd/p2/pfd_threadprobe.py",
         "make_bdg_p2_tables.py": S / "bdg/p2/make_bdg_p2_tables.py"}
sha = {k: hashlib.sha256(p.read_bytes()).hexdigest() for k, p in tools.items()}
assert sha["pfd_threadprobe.py"] == "d93697123b1e3c5a467efde2488dff8422c684061b39f58fa8cc82c545e6190f"
emb = "\n".join(f"printf '%s' '{base64.b64encode(p.read_bytes()).decode()}' | base64 -d > \"$W/p2/tools/{k}\""
                for k, p in tools.items())
script = r'''#!/bin/bash
# Band diagnosis, P2: the pilot (FD-1B-BAND-DIAGNOSIS-DECLARATION.md section 7; BINDING-1 rulings 2-5 and addendum A1).
# Login node, from a fresh deploy clone at M on pscratch. In order, every step stamped to the second:
#   1. iris is read first: the m3246 row; the 9.0 node-h cap must not exceed half the remaining balance (user and
#      project), else STOP to the director;
#   2. the fence (A1, with ENS1 ended): every josephrb job must be named fd1b_bdg_*, ll5d_* or prr_*; ens1_*, rs1_*,
#      cov2d-* or any other name refuses; and no fd1b_bdg_* job may already be queued;
#   3. a fresh clone at M into $W/deploy, HEAD equal and porcelain 0; the module, the packer, s5c_array.sh,
#      mnv_guarded_run.py and setup_salloc_env.sh gated on their sha256 (the setup script also on its blob id);
#   4. the wrapper, Part 1's thread probe (unchanged, d9369712) and the table generator written from this script and
#      gated on their sha256;
#   5. the two tables generated: section 4.3's inputs line, and 8 unfold lines carrying exactly the module's 14
#      pilot_items() (the generator imports the module from the deploy and refuses any difference); printed with sha256;
#   6. section 5's control: the 73 sources stat'd (stat only), compared byte for byte with P1's stat-before.txt
#      (7986e2bf); any difference, a moved atime included, is a STOP and nothing is submitted;
#   7. the thread variables in the submitting shell (none set; the job inherits them through --export=ALL);
#   8. the fence again, immediately before submission; then one sbatch of the wrapper: 1 node,
#      -A m3246 -q regular -C cpu --exclusive --no-requeue --time=01:30:00, job name fd1b_bdg_p2; its parsed
#      TimeLimit must read 01:30:00, else scancel. 1.5 node-h reserved against the 9.0 cap.
# The job runs the probe, then the inputs step (any rc other than 0 is a STOP: no unfold runs), then the 8 lanes. Nothing
# is deleted, and nothing is written under $V. Launched from a /dev/shm copy of itself ($1), which it deletes.
SELF=$1
M=83ac32fb5024026ac6c51c0621d5ae9ff9073370
W=/pscratch/sd/j/josephrb/fd-1b-band-diag-20261109
PY=/global/homes/j/josephrb/.conda/envs/root_6_28/bin/python3
MOD_SHA=658ca91849a8151a4fb801e41004102f0ba621c367f1c23146a8fc3a580484df
PACKER_SHA=b72aaa627d12e6953ad6b1f40a4ae35ffd9b5439db3c0114defe93742f14c6d3
S5C_SHA=dd95db5de1a801eb6b47c8d60bc7da43532ed2ad38e10597ae2db94c0a12526f
GUARD_SHA=30162f57771c9d5a1206eae623a7eb3fc80ac3f0bb150c82fb561be7254b510b
SETUP_SHA=ea3c6998d33f45c831b80da5e5228032a19fc392018ede54a7f52f2f283d1d48
SETUP_BLOB=b4a9c3f6bb766d8488cbab98878cbac1262cc1bb
WRAPPER_SHA=@WRAPPER@
PROBE_SHA=@PROBE@
GEN_SHA=@GEN@
BASE_SHA=7986e2bf31aac583c03273f96804c2adaac85bcfdde5bd4b3da5b0f834c95b22
CAP=9.0
ts() { date -u +%FT%TZ; }
finish() { echo "== bdg-p2 rc=$1 $(ts)"; rm -f -- "$SELF"; exit "$1"; }
fence() {
  local out frc bad
  out=$(squeue -u josephrb -h -o '%i|%j|%T|%M|%l'); frc=$?
  echo "squeue rc=$frc; rows:"; printf '%s\n' "$out"; echo "-- end rows"
  bad=$(printf '%s\n' "$out" | awk -F'|' 'NF && $2 !~ /^(fd1b_bdg_|ll5d_|prr_)/')
  echo "refusing rows: [$bad]"
  [ "$frc" -eq 0 ] && [ -z "$bad" ] && [ "$(printf '%s\n' "$out" | awk -F'|' '$2 ~ /^fd1b_bdg_/' | wc -l)" -eq 0 ]
}
case "$(hostname)" in login*) ;; *) echo "STOP: not a login node: $(hostname)"; finish 9 ;; esac
echo "node $(hostname) $(ts)"
echo "connect script sha256 $(sha256sum "$SELF" | cut -d' ' -f1)"
[ -s "$W/stat-before.txt" ] && [ "$(sha256sum "$W/stat-before.txt" | cut -d' ' -f1)" = "$BASE_SHA" ] || { echo "STOP: P1's stat-before.txt is not 7986e2bf"; finish 9; }
[ ! -e "$W/deploy" ] && [ ! -e "$W/p2" ] && [ ! -e "$W/unf" ] || { echo "STOP: $W/deploy, $W/p2 or $W/unf already exists"; finish 9; }
echo "== 1. iris (read first) $(ts)"
irisout=$(iris 2>&1); irc=$?
printf '%s\n' "$irisout" | head -3
row=$(printf '%s\n' "$irisout" | grep -E '^m3246 ' | head -1)
echo "iris rc=$irc; m3246 row: [$row]"
read -r _ uch ual pch pal <<< "$row"
verdict=$(awk -v uch="$uch" -v ual="$ual" -v pch="$pch" -v pal="$pal" -v cap="$CAP" 'BEGIN {
  if (ual == "" || pal == "" || ual+0 <= 0 || pal+0 <= 0) { print "UNREADABLE"; exit }
  ur = ual - uch; pr = pal - pch
  printf "user remaining %.1f, project remaining %.1f, cap %.1f; half user %.1f, half project %.1f -> %s\n", ur, pr, cap, ur/2, pr/2,
    (cap <= ur/2 && cap <= pr/2) ? "OK" : "OVER" }')
echo "balance: $verdict"
case "$verdict" in *"-> OK") ;; *) echo "STOP: the cap is above half the remaining balance, or iris is unreadable"; finish 3 ;; esac
echo "== 2. fence (before anything is written) $(ts)"
fence || { echo "STOP: the fence is not clear"; finish 3; }
echo "FENCE: clear"
echo "== 3. fresh deploy clone at M $(ts)"
mkdir -p "$W/p2/tables" "$W/p2/lanes" "$W/p2/logs" "$W/p2/tools" || finish 9
git clone --quiet https://github.com/josephbaileyy/MINERvA-OmniFold.git "$W/deploy" || { echo "STOP: clone failed"; finish 5; }
git -C "$W/deploy" -c advice.detachedHead=false checkout --quiet --detach "$M" || { echo "STOP: checkout failed"; finish 5; }
head=$(git -C "$W/deploy" rev-parse HEAD); porc=$(git -C "$W/deploy" status --porcelain | wc -l)
echo "deploy HEAD $head; porcelain lines $porc $(ts)"
[ "$head" = "$M" ] && [ "$porc" -eq 0 ] || { echo "STOP: the deploy is not M clean"; finish 5; }
for pair in "nd-unfolding/fd_1b_band_diag.py:$MOD_SHA" "docs/orchestration/state/gpu-timing-20261023/tools/sbatch_timing_packed.sh:$PACKER_SHA" \
            "nd-unfolding/s5c_array.sh:$S5C_SHA" "nd-unfolding/mnv_guarded_run.py:$GUARD_SHA" "setup_salloc_env.sh:$SETUP_SHA"; do
  f=${pair%%:*}; want=${pair##*:}; got=$(sha256sum "$W/deploy/$f" | cut -d' ' -f1)
  echo "sha256 $got (bound $want) $f"
  [ "$got" = "$want" ] || { echo "STOP: $f is not the bound file"; finish 5; }
done
blob=$(git -C "$W/deploy" rev-parse "$M:setup_salloc_env.sh"); echo "setup_salloc_env.sh blob $blob (bound $SETUP_BLOB)"
[ "$blob" = "$SETUP_BLOB" ] || { echo "STOP: the setup blob"; finish 5; }
echo "== 4. the wrapper, the probe and the table generator"
@EMBED@
for pair in "bdg_p2_wrapper.sh:$WRAPPER_SHA" "pfd_threadprobe.py:$PROBE_SHA" "make_bdg_p2_tables.py:$GEN_SHA"; do
  f=${pair%%:*}; want=${pair##*:}; got=$(sha256sum "$W/p2/tools/$f" | cut -d' ' -f1)
  echo "sha256 $got (expected $want) $f"
  [ "$got" = "$want" ] || { echo "STOP: digest of $f"; finish 5; }
done
echo "== 5. the task tables $(ts)"
env -u PYTHONPATH "$PY" -B "$W/p2/tools/make_bdg_p2_tables.py" "$W/deploy" "$W" "$W/p2/tables" || { echo "STOP: the table generator refused"; finish 5; }
for t in tasks-p2-inputs.tsv tasks-p2.tsv; do echo "$t sha256 $(sha256sum "$W/p2/tables/$t" | cut -d' ' -f1)"; cat "$W/p2/tables/$t"; done
n=$(grep -v '^#' "$W/p2/tables/tasks-p2.tsv" | grep -c -v '^[[:space:]]*$'); ni=$(grep -v '^#' "$W/p2/tables/tasks-p2-inputs.tsv" | grep -c -v '^[[:space:]]*$')
echo "unfold lines $n; inputs lines $ni"
[ "$n" -eq 8 ] && [ "$ni" -eq 1 ] || { echo "STOP: the tables are not 8 + 1 lines"; finish 5; }
echo "== 6. section 5's control: the 73 sources against P1's stat-before.txt (stat only) $(ts)"
env -u PYTHONPATH "$PY" -B -c 'import sys; [print(l.rsplit("|", 1)[1]) for l in open(sys.argv[1]).read().splitlines()]' "$W/stat-before.txt" \
  | while read -r f; do stat -c '%F|%i|%h|%s|%Y|%X|%Z|%n' "$f" 2>&1; done > "$W/p2/logs/stat-submit.txt"
echo "stat-submit.txt: $(wc -l < "$W/p2/logs/stat-submit.txt") lines; sha256 $(sha256sum "$W/p2/logs/stat-submit.txt" | cut -d' ' -f1) $(ts)"
if cmp -s "$W/stat-before.txt" "$W/p2/logs/stat-submit.txt"; then echo "sources: byte-identical to P1's stat-before"; else echo "STOP: a source's stat differs from P1's stat-before; nothing submitted:"; diff "$W/stat-before.txt" "$W/p2/logs/stat-submit.txt" | head -40; finish 4; fi
echo "== 7. thread variables in the submitting shell (none set; inherited by the job through --export=ALL)"
echo "OMP_NUM_THREADS=${OMP_NUM_THREADS-<unset>} OPENBLAS_NUM_THREADS=${OPENBLAS_NUM_THREADS-<unset>} MKL_NUM_THREADS=${MKL_NUM_THREADS-<unset>} NUMEXPR_NUM_THREADS=${NUMEXPR_NUM_THREADS-<unset>}"
echo "== 8. fence, immediately before submission $(ts)"
fence || { echo "STOP: the fence is not clear; nothing submitted"; finish 3; }
echo "FENCE: clear"
cat > "$W/p2/logs/submit-p2.txt" <<SUB
sbatch -A m3246 -q regular -C cpu --nodes=1 --exclusive --no-requeue --export=ALL,HOME=/global/homes/j/josephrb --time=01:30:00 -J fd1b_bdg_p2 -o $W/p2/logs/%x_%j.out $W/p2/tools/bdg_p2_wrapper.sh $W/deploy $M $W/p2/tables/tasks-p2-inputs.tsv $W/p2/tables/tasks-p2.tsv $W/p2/lanes $W/p2/tools/pfd_threadprobe.py $W/p2/inputs.json
SUB
cat "$W/p2/logs/submit-p2.txt"
sub=$(bash "$W/p2/logs/submit-p2.txt" 2>&1); src=$?
echo "$sub" | tee "$W/p2/logs/submit-p2.out"; echo "sbatch rc=$src $(ts)"
job=$(printf '%s\n' "$sub" | awk '/^Submitted batch job/ {print $4}')
[ "$src" -eq 0 ] && [ -n "$job" ] || { echo "STOP: sbatch failed"; finish 6; }
tl=$(scontrol show job "$job" | grep -o 'TimeLimit=[^ ]*' | cut -d= -f2)
echo "job $job TimeLimit=$tl"
if [ "$tl" != "01:30:00" ]; then echo "STOP: TimeLimit is not 01:30:00; scancel $job"; scancel "$job"; echo "scancel rc=$?"; finish 7; fi
squeue -u josephrb -h -o '%i %j %T %l %D %R'
finish 0
'''
script = (script.replace("@WRAPPER@", sha["bdg_p2_wrapper.sh"]).replace("@PROBE@", sha["pfd_threadprobe.py"])
          .replace("@GEN@", sha["make_bdg_p2_tables.py"]).replace("@EMBED@", emb))
out = S / "bdg/p2/bdg_p2_login.sh"
out.write_text(script)
print("connect", hashlib.sha256(script.encode()).hexdigest())
for k, v in sha.items():
    print(k, v)

"""Generate bdg_p3_login.sh (the band diagnosis's P3 submit connect) and bdg_p3_post_login.sh."""
import base64
import hashlib
from pathlib import Path

S = Path("/private/tmp/claude-501/-Users-josephbailey-local-research-MINERvA-OmniFold/7e3f49f7-e8e4-452d-b380-399d4f6c529e/scratchpad")
tools = {"pfd_p2_wrapper.sh": S / "pfd/p2/pfd_p2_wrapper.sh", "pfd_threadprobe.py": S / "pfd/p2/pfd_threadprobe.py",
         "make_bdg_p3_table.py": S / "bdg/p3/make_bdg_p3_table.py"}
sha = {k: hashlib.sha256(p.read_bytes()).hexdigest() for k, p in tools.items()}
assert sha["pfd_p2_wrapper.sh"] == "038a6353b81a066476f96312e9764feac714bdc3cc350b5e533fd2a40f6e0256"
assert sha["pfd_threadprobe.py"] == "d93697123b1e3c5a467efde2488dff8422c684061b39f58fa8cc82c545e6190f"
emb = "\n".join(f"printf '%s' '{base64.b64encode(p.read_bytes()).decode()}' | base64 -d > \"$W/p3/tools/{k}\""
                for k, p in tools.items())
COMMON = r'''M=83ac32fb5024026ac6c51c0621d5ae9ff9073370
W=/pscratch/sd/j/josephrb/fd-1b-band-diag-20261109
V=/pscratch/sd/j/josephrb/fd-1b-precheck-fd-20261107
PY=/global/homes/j/josephrb/.conda/envs/root_6_28/bin/python3
MOD_SHA=658ca91849a8151a4fb801e41004102f0ba621c367f1c23146a8fc3a580484df
BASE_SHA=7986e2bf31aac583c03273f96804c2adaac85bcfdde5bd4b3da5b0f834c95b22
ts() { date -u +%FT%TZ; }
restat() {  # $1 = output file: the 73 sources of P1's stat-before.txt, stat only
  env -u PYTHONPATH "$PY" -B -c 'import sys; [print(l.rsplit("|", 1)[1]) for l in open(sys.argv[1]).read().splitlines()]' "$W/stat-before.txt" \
    | while read -r f; do stat -c '%F|%i|%h|%s|%Y|%X|%Z|%n' "$f" 2>&1; done > "$1"
}
'''
submit = r'''#!/bin/bash
# Band diagnosis, P3: the bulk (FD-1B-BAND-DIAGNOSIS-DECLARATION.md section 7; BINDING-1 rulings 2-5 as addenda A1 and
# A2 set them: 4 jobs x 7 lanes x 4 items, --time=01:40:00). Login node; every step stamped to the second. In order:
#   1. iris first: the 9.0 node-h cap must not exceed half the remaining balance (user and project), else STOP;
#   2. P2's gates are on disk: $W/p2/inputs.json reads EQUAL and $W/p2/pilot.json reads PASS, else STOP;
#   3. the fence (A1): every josephrb job must be named fd1b_bdg_*, ll5d_* or prr_*; ens1_*, rs1_*, cov2d-* or any
#      other name refuses; and no fd1b_bdg_* job may be queued;
#   4. the deploy $W/deploy (P2's) is still M with no tracked change; the module, the packer, s5c_array.sh,
#      mnv_guarded_run.py and setup_salloc_env.sh gated on their sha256;
#   5. Part 1's committed P2/P3 job script (pfd_p2_wrapper.sh 038a6353, unchanged), Part 1's thread probe (d9369712,
#      unchanged) and the P3 table generator written from this script and gated on their sha256;
#   6. the table: 28 lines, each one unfold call over 4 items of one (mode, seed, eps, channel) group; the generator
#      imports the module from the deploy and refuses unless the lines carry exactly bulk_items(); job j runs lines
#      7j..7j+6;
#   7. section 5's control: the 73 sources re-stat'd and compared byte for byte with P1's stat-before.txt (7986e2bf);
#      any difference is a STOP and nothing is submitted;
#   8. the fence again, then four sbatch of the wrapper, each 1 node, -A m3246 -q regular -C cpu --exclusive
#      --no-requeue --time=01:40:00, job name fd1b_bdg_p3, lines 7j..7j+6; each parsed TimeLimit must read 01:40:00,
#      else every P3 job is cancelled. 6.67 node-h reserved; 8.17 with P2, against the 9.0 cap.
# Nothing is deleted or written under $V. Launched from a /dev/shm copy of itself ($1), which it deletes.
SELF=$1
@COMMON@PACKER_SHA=b72aaa627d12e6953ad6b1f40a4ae35ffd9b5439db3c0114defe93742f14c6d3
S5C_SHA=dd95db5de1a801eb6b47c8d60bc7da43532ed2ad38e10597ae2db94c0a12526f
GUARD_SHA=30162f57771c9d5a1206eae623a7eb3fc80ac3f0bb150c82fb561be7254b510b
SETUP_SHA=ea3c6998d33f45c831b80da5e5228032a19fc392018ede54a7f52f2f283d1d48
WRAPPER_SHA=@WRAPPER@
PROBE_SHA=@PROBE@
GEN_SHA=@GEN@
CAP=9.0
finish() { echo "== bdg-p3 rc=$1 $(ts)"; rm -f -- "$SELF"; exit "$1"; }
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
[ "$(sha256sum "$W/stat-before.txt" | cut -d' ' -f1)" = "$BASE_SHA" ] || { echo "STOP: stat-before.txt is not 7986e2bf"; finish 9; }
[ ! -e "$W/p3" ] || { echo "STOP: $W/p3 already exists"; finish 9; }
echo "== 1. iris (read first) $(ts)"
irisout=$(iris 2>&1); irc=$?
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
echo "== 2. P2's gates on disk $(ts)"
g=$(env -u PYTHONPATH "$PY" -B -c 'import json,sys; i=json.load(open(sys.argv[1]))["verdict"]; p=json.load(open(sys.argv[2]))["verdict"]; print(i, p)' "$W/p2/inputs.json" "$W/p2/pilot.json" 2>&1)
echo "inputs and pilot verdicts: [$g]"
[ "$g" = "EQUAL PASS" ] || { echo "STOP: P2's gates are not EQUAL and PASS"; finish 3; }
echo "== 3. fence (before anything is written) $(ts)"
fence || { echo "STOP: the fence is not clear"; finish 3; }
echo "FENCE: clear"
echo "== 4. the deploy $(ts)"
head=$(git -C "$W/deploy" rev-parse HEAD); porc=$(git -C "$W/deploy" status --porcelain --untracked-files=no | wc -l)
echo "deploy HEAD $head; tracked porcelain $porc"
[ "$head" = "$M" ] && [ "$porc" -eq 0 ] || { echo "STOP: the deploy is not M clean"; finish 5; }
for pair in "nd-unfolding/fd_1b_band_diag.py:$MOD_SHA" "docs/orchestration/state/gpu-timing-20261023/tools/sbatch_timing_packed.sh:$PACKER_SHA" \
            "nd-unfolding/s5c_array.sh:$S5C_SHA" "nd-unfolding/mnv_guarded_run.py:$GUARD_SHA" "setup_salloc_env.sh:$SETUP_SHA"; do
  f=${pair%%:*}; want=${pair##*:}; got=$(sha256sum "$W/deploy/$f" | cut -d' ' -f1)
  echo "sha256 $got (bound $want) $f"
  [ "$got" = "$want" ] || { echo "STOP: $f is not the bound file"; finish 5; }
done
echo "== 5. the job script, the probe and the table generator"
mkdir -p "$W/p3/tables" "$W/p3/lanes" "$W/p3/logs" "$W/p3/tools" || finish 9
@EMBED@
for pair in "pfd_p2_wrapper.sh:$WRAPPER_SHA" "pfd_threadprobe.py:$PROBE_SHA" "make_bdg_p3_table.py:$GEN_SHA"; do
  f=${pair%%:*}; want=${pair##*:}; got=$(sha256sum "$W/p3/tools/$f" | cut -d' ' -f1)
  echo "sha256 $got (expected $want) $f"
  [ "$got" = "$want" ] || { echo "STOP: digest of $f"; finish 5; }
done
echo "== 6. the task table $(ts)"
env -u PYTHONPATH "$PY" -B "$W/p3/tools/make_bdg_p3_table.py" "$W/deploy" "$W" "$W/p3/tables/tasks-p3.tsv" || { echo "STOP: the table generator refused"; finish 5; }
echo "tasks-p3.tsv sha256 $(sha256sum "$W/p3/tables/tasks-p3.tsv" | cut -d' ' -f1)"
cat "$W/p3/tables/tasks-p3.tsv"
n=$(grep -v '^#' "$W/p3/tables/tasks-p3.tsv" | grep -c -v '^[[:space:]]*$'); echo "lines $n"
[ "$n" -eq 28 ] || { echo "STOP: the table is not 28 lines"; finish 5; }
echo "== 7. section 5's control: the 73 sources against P1's stat-before.txt $(ts)"
restat "$W/p3/logs/stat-submit.txt"
echo "stat-submit.txt: $(wc -l < "$W/p3/logs/stat-submit.txt") lines; sha256 $(sha256sum "$W/p3/logs/stat-submit.txt" | cut -d' ' -f1)"
if cmp -s "$W/stat-before.txt" "$W/p3/logs/stat-submit.txt"; then echo "sources: byte-identical to P1's stat-before"; else echo "STOP: a source's stat moved; nothing submitted:"; diff "$W/stat-before.txt" "$W/p3/logs/stat-submit.txt" | head -40; finish 4; fi
echo "thread variables in the submitting shell: OMP_NUM_THREADS=${OMP_NUM_THREADS-<unset>} OPENBLAS_NUM_THREADS=${OPENBLAS_NUM_THREADS-<unset>} MKL_NUM_THREADS=${MKL_NUM_THREADS-<unset>} NUMEXPR_NUM_THREADS=${NUMEXPR_NUM_THREADS-<unset>}"
echo "== 8. fence, immediately before submission $(ts)"
fence || { echo "STOP: the fence is not clear; nothing submitted"; finish 3; }
echo "FENCE: clear"
jobs=()
for j in 0 1 2 3; do
  first=$((7 * j)); last=$((7 * j + 6))
  echo "sbatch -A m3246 -q regular -C cpu --nodes=1 --exclusive --no-requeue --export=ALL,HOME=/global/homes/j/josephrb --time=01:40:00 -J fd1b_bdg_p3 -o $W/p3/logs/%x_%j.out $W/p3/tools/pfd_p2_wrapper.sh $W/deploy $M $W/p3/tables/tasks-p3.tsv $W/p3/lanes $first $last $W/p3/tools/pfd_threadprobe.py" > "$W/p3/logs/submit-p3-$j.txt"
  cat "$W/p3/logs/submit-p3-$j.txt"
  sub=$(bash "$W/p3/logs/submit-p3-$j.txt" 2>&1); src=$?
  echo "$sub" | tee "$W/p3/logs/submit-p3-$j.out"; echo "sbatch $j rc=$src $(ts)"
  job=$(printf '%s\n' "$sub" | awk '/^Submitted batch job/ {print $4}')
  [ "$src" -eq 0 ] && [ -n "$job" ] || { echo "STOP: sbatch $j failed; cancelling ${jobs[*]}"; [ ${#jobs[@]} -gt 0 ] && scancel "${jobs[@]}"; finish 6; }
  jobs+=("$job")
  tl=$(scontrol show job "$job" | grep -o 'TimeLimit=[^ ]*' | cut -d= -f2)
  echo "job $job (lines $first..$last) TimeLimit=$tl"
  if [ "$tl" != "01:40:00" ]; then echo "STOP: TimeLimit is not 01:40:00; scancel ${jobs[*]}"; scancel "${jobs[@]}"; echo "scancel rc=$?"; finish 7; fi
done
printf '%s\n' "${jobs[@]}" > "$W/p3/logs/jobs.txt"
squeue -u josephrb -h -o '%i %j %T %l %D %R'
finish 0
'''
post = r'''#!/bin/bash
# Band diagnosis, P3 post (FD-1B-BAND-DIAGNOSIS-DECLARATION.md sections 5 and 7). Login node, 0 node-h, after the four
# fd1b_bdg_p3 jobs have left the queue; every step stamped to the second. In order:
#   1. the jobs, from $W/p3/logs/jobs.txt: none may still be listed by squeue; sacct's record for each;
#   2. the deploy still M with no tracked change, and the module still 658ca918;
#   3. section 5's final comparison: the 73 sources re-stat'd into $W/p3/logs/stat-after-p3.txt and compared byte for
#      byte with P1's stat-before.txt (7986e2bf); any difference, a moved atime included, is printed and is a STOP (rc 4);
#   4. every product in $W/unf listed with size and sha256; 126 are expected (14 pilot + 112 bulk); the count is printed;
#   5. a base64 tar of the records: the table, the logs, the lanes (thread probes, line logs, inventories) and the
#      module's atime records. The npz bytes are not sent.
# Nothing is deleted or written under $V. Launched from a /dev/shm copy of itself ($1), which it deletes.
SELF=$1
@COMMON@finish() { echo "== bdg-p3-post rc=$1 $(ts)"; rm -f -- "$SELF"; exit "$1"; }
case "$(hostname)" in login*) ;; *) echo "STOP: not a login node: $(hostname)"; finish 9 ;; esac
echo "node $(hostname) $(ts)"
echo "connect script sha256 $(sha256sum "$SELF" | cut -d' ' -f1)"
[ "$(sha256sum "$W/stat-before.txt" | cut -d' ' -f1)" = "$BASE_SHA" ] || { echo "STOP: stat-before.txt is not 7986e2bf"; finish 9; }
echo "== 1. the jobs $(ts)"
[ -s "$W/p3/logs/jobs.txt" ] || { echo "STOP: no jobs.txt"; finish 9; }
while read -r job; do
  if squeue -h -j "$job" 2>/dev/null | grep -q .; then echo "STOP: job $job is still queued or running"; finish 9; fi
  sacct -j "$job" -X -n -P -o JobID,JobName,State,ExitCode,Start,End,Elapsed,ElapsedRaw,NNodes,NodeList,TimelimitRaw
  sacct -j "$job" -n -P -o JobID,JobName,State,ExitCode,Elapsed,MaxRSS
done < "$W/p3/logs/jobs.txt"
echo "== 2. the deploy"
head=$(git -C "$W/deploy" rev-parse HEAD); porc=$(git -C "$W/deploy" status --porcelain --untracked-files=no | wc -l)
mod=$(sha256sum "$W/deploy/nd-unfolding/fd_1b_band_diag.py" | cut -d' ' -f1)
echo "deploy HEAD $head; tracked porcelain $porc; module $mod"
[ "$head" = "$M" ] && [ "$porc" -eq 0 ] && [ "$mod" = "$MOD_SHA" ] || { echo "STOP: the deploy is not M clean"; finish 5; }
echo "== 3. section 5's final comparison: the 73 sources against P1's stat-before.txt $(ts)"
restat "$W/p3/logs/stat-after-p3.txt"
echo "stat-after-p3.txt: $(wc -l < "$W/p3/logs/stat-after-p3.txt") lines; sha256 $(sha256sum "$W/p3/logs/stat-after-p3.txt" | cut -d' ' -f1)"
moved=0
if cmp -s "$W/stat-before.txt" "$W/p3/logs/stat-after-p3.txt"; then echo "sources: byte-identical to P1's stat-before"; else echo "STOP: a source's stat moved:"; diff "$W/stat-before.txt" "$W/p3/logs/stat-after-p3.txt" | head -40; moved=1; fi
echo "== 4. products in $W/unf $(ts)"
find "$W/unf" -maxdepth 1 -type f -name '*.npz' -printf '%s %f\n' | sort -k2 | while read -r s f; do echo "$s $(sha256sum "$W/unf/$f" | cut -d' ' -f1) $f"; done
np=$(find "$W/unf" -maxdepth 1 -type f -name '*.npz' | wc -l); echo "products: $np (126 expected)"
echo "== 5. records $(ts)"
cd "$W" || finish 9
list=$(find p3/tables p3/logs p3/lanes -type f | sort; find unf -maxdepth 1 -type f -name 'atime-*.json' | sort)
printf '%s\n' "$list" | while read -r f; do echo "sha256 $(sha256sum "$f" | cut -d' ' -f1) $f"; done
echo "== TAR BEGIN"
printf '%s\n' "$list" | tar -cf - -T - | base64 -w 76
echo "== TAR END tar rc=${PIPESTATUS[1]}"
[ "$moved" -eq 0 ] || finish 4
[ "$np" -eq 126 ] || { echo "STOP: $np products, not 126"; finish 6; }
finish 0
'''
submit = (submit.replace("@COMMON@", COMMON).replace("@WRAPPER@", sha["pfd_p2_wrapper.sh"])
          .replace("@PROBE@", sha["pfd_threadprobe.py"]).replace("@GEN@", sha["make_bdg_p3_table.py"]).replace("@EMBED@", emb))
post = post.replace("@COMMON@", COMMON)
for name, text in (("bdg_p3_login.sh", submit), ("bdg_p3_post_login.sh", post)):
    (S / "bdg/p3" / name).write_text(text)
    print(name, hashlib.sha256(text.encode()).hexdigest())
print({k: v[:8] for k, v in sha.items()})

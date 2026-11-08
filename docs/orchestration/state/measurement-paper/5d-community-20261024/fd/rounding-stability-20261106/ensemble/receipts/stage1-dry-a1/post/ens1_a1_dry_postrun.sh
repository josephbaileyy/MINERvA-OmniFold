#!/bin/bash
# ENS1 stage-1 dry RERUN under addendum A1: the post-run connect (ENS1-BINDING-2 "addendum A1", ruling 3). 0 node-h,
# login node, from a /dev/shm copy of itself ($1), after the dry rerun's job has ended. In order:
#   the fence (only rs1_* and ens1_* pass; cov2d-* or any other name stops), recorded;
#   the job: its id from $NEW/logs/a1-dry.jobid; sacct COMPLETED on 1 node; the charge from sacct's ElapsedRaw, and
#     stage 1's spend (0.1586 from attempt 1 + this job) at most 55.0;
#   the run, from its own files: stage1/log-dry/DONE (dry, stage 1, 9 of 9, rc 0, this job, pin M_A1, no teardown); no
#     FAILED, no .failed or .teardown; the deploy at M_A1 with its tracked files clean and the bound probe's sha256;
#   the nine products, by the bound probe's own `expect` on each dry.tsv line, each in the run's SHA256SUMS;
#   gate E5 at the dry run: every product's ens1 block records moved_rows 0 in every class (MCgen, MCreco, measured,
#     bkg_reco), with its mode, k and protocol seed as its task states them and the bound probe's code_sha256; and every
#     task log's "[ens1] grid membership moved rows" lines all read 0;
#   F64: attempt 1's F64 (runs/F64/ens1_F64_b-_j0.npz) copied with dd iflag=noatime into $NEW/post/attempt1/, its atime
#     unchanged and the copy at attempt 1's digest 94ef5153...; then xsec_flat and xtrue_flat of the new F64 against
#     that copy: dtype, shape and bytes equal. A difference is a STOP (A1 §7);
#   the projection readout (declaration §8): each task's seconds_unfold and wall, and 42 x t + 300 s against 8.1 h.
#     A readout for the director; it decides nothing here.
# Every module call runs under the sourced environment (Python 3.11). Writes only $NEW/post/ (refused if it exists).
# Attempt 1's root is read only through that one noatime copy; nothing else in it is opened. No set -u.
SELF=$1
M=f4d2d7f3833834390b7b031df61ba1a5765e9900
NEW=/pscratch/sd/j/josephrb/ens1-a1-20261108
OLD=/pscratch/sd/j/josephrb/ens1-20261107
D=$NEW/deploy
R=$NEW/post
L=$NEW/stage1/log-dry
F64_OLD_SHA=94ef51532161aa578f2c0944658d2172fda9c1c118ea81ffa2415cc74a5808e7
PROBE_SHA=807c40d3cb64e2e09d2fa9a5b91fb7a786f4eb51090e4291d65b3896b47e3b25
SPENT=0.1586
CAP=55.0
bail() { rm -f -- "$SELF"; exit 9; }
[ -n "$SELF" ] && [ -f "$SELF" ] || exit 9
[ -s "$NEW/logs/a1-dry.jobid" ] && [ -d "$L" ] && [ ! -e "$R" ] || bail
mkdir "$R" && mkdir "$R/attempt1" || bail
exec > "$R/connect-postrun.log" 2>&1
finish() { echo "ens1 a1 dry postrun rc=$1"; date -u +%FT%TZ; echo "$1" > "$R/connect-postrun.done"; rm -f -- "$SELF"; exit "$1"; }
echo "node $(hostname) nproc=$(nproc) loadavg $(cut -d' ' -f1-3 /proc/loadavg)"; date -u +%FT%TZ
echo "connect script sha256 $(sha256sum "$SELF" | cut -d' ' -f1)"
cp "$SELF" "$R/ens1_a1_dry_postrun.sh"
job=$(cat "$NEW/logs/a1-dry.jobid"); echo "job $job"

echo "== the fence (only rs1_* and ens1_* pass)"
squeue -u josephrb -h -o '%i|%j|%T|%M|%l' > "$R/squeue-before.txt" 2>&1 || { echo "STOP: squeue failed"; finish 9; }
cat "$R/squeue-before.txt"
bad=$(awk -F'|' '$2 !~ /^(rs1_|ens1_)/' "$R/squeue-before.txt")
[ -z "$bad" ] || { echo "FENCE STOP: a cov2d-* job or a job of another name is present:"; printf '%s\n' "$bad"; finish 9; }
[ -z "$(awk -F'|' -v j="$job" '$1 == j' "$R/squeue-before.txt")" ] || { echo "STOP: job $job is still in the queue"; finish 9; }
echo "FENCE: pass"

echo "== the job"
sacct -j "$job" -n -P -o JobID,JobName,State,ExitCode,Elapsed,ElapsedRaw,NNodes,NCPUS,Start,End,NodeList > "$R/sacct-$job.txt" 2>&1
cat "$R/sacct-$job.txt"
sa=$(awk -F'|' -v j="$job" '$1 == j {print $3 "|" $6 "|" $7}' "$R/sacct-$job.txt")
state=${sa%%|*}; rest=${sa#*|}; raw=${rest%%|*}; nn=${rest#*|}
echo "state=$state elapsed_raw=$raw nnodes=$nn"
[ "$state" = COMPLETED ] && [ "$nn" = 1 ] && [ -n "$raw" ] || { echo "STOP: the job is not COMPLETED on one node"; finish 4; }
nh=$(awk -v r="$raw" 'BEGIN{printf "%.4f", r/3600}'); tot=$(awk -v a=$SPENT -v b="$nh" 'BEGIN{printf "%.4f", a+b}')
echo "charge node_h=$nh; stage 1 spend $SPENT + $nh = $tot of $CAP"
awk -v t="$tot" -v c=$CAP 'BEGIN{exit !(t <= c)}' || { echo "STOP: stage 1's spend is above its cap"; finish 4; }

echo "== the run"
cat "$L/DONE"; echo
[ ! -e "$L/FAILED" ] && [ -z "$(ls "$L" | grep -E '\.(teardown|failed)$')" ] || { echo "STOP: a FAILED, teardown or failed record"; finish 4; }
[ "$(git -C "$D" rev-parse HEAD)" = "$M" ] || { echo "STOP: deploy HEAD is not M_A1"; finish 9; }
n=$(git -C "$D" status --porcelain --untracked-files=no | wc -l); echo "HEAD $M; modified tracked files: $n"
[ "$n" -eq 0 ] || { echo "STOP: the deploy has modified tracked files"; finish 9; }
[ "$(sha256sum "$D/nd-unfolding/ensemble_estimator_probe.py" | cut -d' ' -f1)" = "$PROBE_SHA" ] || { echo "STOP: the probe"; finish 9; }
grep -v '^#' "$NEW/stage1/dry.tsv" | cut -f1 > "$R/task-ids.txt"
( source "$D/setup_salloc_env.sh" > "$R/env-done.log" 2>&1
  python3 -B -c '
import json, sys
d = json.load(open(sys.argv[1]))
ok = d.get("mode") == "dry" and d.get("stage") == 1 and d.get("tasks") == 9 and d.get("ended") == 9 and d.get("rc") == 0 \
    and d.get("job") == sys.argv[2] and d.get("pin") == sys.argv[3] and d.get("teardown") == ""
sys.exit(0 if ok else 1)' "$L/DONE" "$job" "$M" ) || { echo "STOP: the DONE is not this run's"; finish 4; }

echo "== the nine products (the bound probe's expect)"
: > "$R/products.txt"
while IFS= read -r id; do
  cols=(); while IFS= read -r x; do cols+=("$x"); done < <(awk -F '\t' -v id="$id" '$1 == id { for (i = 1; i <= NF; i++) print $i }' "$NEW/stage1/dry.tsv")
  ( source "$D/setup_salloc_env.sh" > /dev/null 2>&1
    cd "$D" && PYTHONDONTWRITEBYTECODE=1 python3 -B "nd-unfolding/${cols[2]}" expect "${cols[@]:3}" ) > "$R/expect-$id.txt" \
    || { echo "STOP: expect failed for $id"; finish 5; }
  while IFS= read -r f; do printf '%s\t%s\n' "$id" "$f" >> "$R/products.txt"; done < "$R/expect-$id.txt"
done < "$R/task-ids.txt"
cat "$R/products.txt"
np=$(wc -l < "$R/products.txt" | tr -d ' '); echo "products: $np"
[ "$np" -eq 9 ] || { echo "STOP: not nine products"; finish 5; }
miss=0
while IFS=$'\t' read -r id f; do
  rel=${f#"$NEW"/}
  [ -s "$f" ] && [ "$(awk -v n="$rel" '$2 == n {print $1}' "$L/SHA256SUMS")" = "$(sha256sum "$f" | cut -d' ' -f1)" ] || { echo "NOT PINNED $f"; miss=$((miss + 1)); }
done < "$R/products.txt"
[ "$miss" -eq 0 ] || { echo "STOP: a product is missing or not at its line in the run's SHA256SUMS"; finish 5; }

echo "== F64: attempt 1's product, one noatime copy"
F_OLD=$OLD/runs/F64/ens1_F64_b-_j0.npz
a0=$(stat -c %X "$F_OLD")
dd if="$F_OLD" iflag=noatime of="$R/attempt1/ens1_F64_b-_j0.npz" bs=4M status=none || { echo "STOP: the copy failed"; finish 9; }
a1=$(stat -c %X "$F_OLD"); got=$(sha256sum "$R/attempt1/ens1_F64_b-_j0.npz" | cut -d' ' -f1)
echo "attempt 1 F64: atime $a0 -> $a1; copy sha256 $got (pinned $F64_OLD_SHA)"
[ "$a0" = "$a1" ] && [ "$got" = "$F64_OLD_SHA" ] || { echo "STOP: attempt 1's F64 is not at its digest, or its atime moved"; finish 9; }

echo "== E5 at the dry run, F64 bitwise, the projection (sourced environment)"
cat > "$R/read.py" <<'PYEOF'
import ast, json, re, sys
import numpy as np
products, L, f64_old, probe_sha, out = sys.argv[1:6]
ZERO = {"MCgen": 0, "MCreco": 0, "measured": 0, "bkg_reco": 0}
rec = {"schema": "ens1-a1-dry-postrun/1", "numpy": np.__version__, "products": {}, "logs": {}, "timing": {}}
fails = []
rows = [l.rstrip("\n").split("\t") for l in open(products) if l.strip()]
f64_new = None
for tid, path in rows:
    with np.load(path, allow_pickle=False) as z:
        meta = json.loads(str(z["meta"]))
    b = meta.get("ens1") or {}
    m = re.fullmatch(r"ens1_s(\d\d)_k(\d\d\d)", tid)
    if tid == "ens1_F64":
        want = {"mode": "base", "k": None, "protocol_seed": 0}
        f64_new = path
    else:
        want = {"mode": "stability", "k": int(m.group(2)), "protocol_seed": int(m.group(1))}
    got = {k: b.get(k) for k in want}
    moved, code = b.get("moved_rows"), b.get("code_sha256")
    rec["products"][tid] = {"path": path, "moved_rows": moved, "block": got, "code_sha256": code}
    if moved != ZERO:
        fails.append(f"E5: {tid} records moved_rows {moved}")
    if got != want:
        fails.append(f"{tid}: ens1 block {got}, the task states {want}")
    if code != probe_sha:
        fails.append(f"{tid}: code_sha256 {code}")
    log = open(f"{L}/tasks/{tid}.log", errors="replace").read()
    parsed = [ast.literal_eval(s) for s in re.findall(r"\[ens1\] grid membership moved rows (\{[^}]*\})", log)]
    rec["logs"][tid] = parsed
    if not parsed or any(p != ZERO for p in parsed):
        fails.append(f"E5 log: {tid} logged {parsed}")
    su = []
    for line in log.splitlines():
        if line.startswith('{"out"'):
            su.append(float(json.loads(line)["seconds_unfold"]))
    t0, t1 = float(open(f"{L}/{tid}.start").read()), float(open(f"{L}/{tid}.end").read())
    rec["timing"][tid] = {"seconds_unfold": su, "wall": round(t1 - t0, 1)}
    if len(su) != 1:
        fails.append(f"{tid}: {len(su)} seconds_unfold lines, not 1")
cmp = {}
if f64_new is None:
    fails.append("no F64 product")
else:
    with np.load(f64_new, allow_pickle=False) as a, np.load(f64_old, allow_pickle=False) as o:
        rec["f64_keys"] = {"new": sorted(a.files), "attempt1": sorted(o.files)}
        for k in ("xsec_flat", "xtrue_flat"):
            if k not in a.files or k not in o.files:
                cmp[k] = {"present": [k in a.files, k in o.files], "bitwise_identical": False}
                fails.append(f"F64 {k} is not in both products")
                continue
            x, y = a[k], o[k]
            same = x.dtype == y.dtype and x.shape == y.shape and x.tobytes() == y.tobytes()
            cmp[k] = {"dtype": [str(x.dtype), str(y.dtype)], "shape": [list(x.shape), list(y.shape)],
                      "bitwise_identical": bool(same)}
            if not same:
                fails.append(f"F64 {k} DIFFERS from attempt 1")
rec["f64_compare"] = cmp
su_all = [v for r in rec["timing"].values() for v in r["seconds_unfold"]]
t = max(su_all) if su_all else None
w = max((r["wall"] for r in rec["timing"].values()), default=None)
rec["projection"] = {"t_max_seconds_unfold": t, "task_wall_max": w, "bound_t": 687, "limit_h": 8.1,
                     "shard_wall_h_from_t": None if t is None else round((42 * t + 300) / 3600, 3),
                     "shard_wall_h_from_wall": None if w is None else round((42 * w + 300) / 3600, 3)}
rec["failures"] = fails
rec["verdict"] = "PASS" if not fails else "STOP"
with open(out, "w") as fh:
    json.dump(rec, fh, indent=1)
print(json.dumps({"verdict": rec["verdict"], "failures": fails, "f64_compare": cmp,
                  "moved_rows": {k: v["moved_rows"] for k, v in rec["products"].items()},
                  "projection": rec["projection"]}))
sys.exit(0 if not fails else 4)
PYEOF
echo "read.py sha256 $(sha256sum "$R/read.py" | cut -d' ' -f1)"
( source "$D/setup_salloc_env.sh" > "$R/env-read.log" 2>&1
  python3 --version
  PYTHONDONTWRITEBYTECODE=1 python3 -B "$R/read.py" "$R/products.txt" "$L" "$R/attempt1/ens1_F64_b-_j0.npz" \
    "$PROBE_SHA" "$R/a1-dry-read.json" ); rc=$?
echo "read rc=$rc"
[ -s "$R/a1-dry-read.json" ] && sha256sum "$R/a1-dry-read.json"
[ $rc -eq 0 ] || { echo "STOP: E5, the F64 comparison or a product's block (see a1-dry-read.json); reported unrepaired"; finish 4; }
finish 0

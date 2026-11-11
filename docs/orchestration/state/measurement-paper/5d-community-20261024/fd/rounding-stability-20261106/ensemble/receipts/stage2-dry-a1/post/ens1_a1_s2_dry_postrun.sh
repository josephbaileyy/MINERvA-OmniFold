#!/bin/bash
# ENS1 stage-2 DRY run under addendum A1: the post-run connect (ENS1-DECLARATION §3.2, §8). 0 node-h, login node, from a
# /dev/shm copy of itself ($1), after the stage-2 dry job has ended. In order:
#   the fence (only rs1_* and ens1_* pass; cov2d-*, prr_* or any other name stops), recorded; the job not queued;
#   the job: its id from $NEW/logs-s2/s2-dry.jobid; sacct COMPLETED on 1 node under the name ens1_a1_s2_dry; the charge
#     from sacct's ElapsedRaw, and stage 2's spend (0 before this job) at most 46.0;
#   the run, from its own files: stage2/log-dry/DONE (dry, stage 2, 7 of 7, rc 0, this job, pin M_A1, no teardown); no
#     FAILED, no .failed or .teardown, no runs-teardown/; the deploy at M_A1 with its tracked files clean and the bound
#     probe's sha256;
#   the seven products, by the bound probe's own `expect` on each dry.tsv line, each in the run's SHA256SUMS;
#   read.py (embedded, under the sourced environment, the bound probe imported from the deploy for SCHEMA and
#     INTERNAL_BASE):
#     the ens1 block of every product: schema, mode closure, k, internal seed INTERNAL_BASE + k, truth as its task states
#       them, moved_rows 0 in every class, the probe's code_sha256, closure_dtype_requested recorded;
#     every task log: exactly one "[ens1] grid membership moved rows" line, all 0, and exactly one runner line
#       {"out", "rc", "seconds"} naming its product with rc 0;
#     the determinism control (§3.2): A7_mnvtune k=1's xsec_flat and xtrue_flat bitwise equal to nominal k=1's (dtype,
#       shape, bytes); a difference is a STOP;
#     the truth vectors (§3.2): xtrue_flat bitwise equal across nominal k=1-4 and across W1 k=1-2; a difference is a STOP;
#     the projection readout (§8): each task's runner seconds, meta seconds_unfold and wall; 34 x t + 300 s against
#       6.75 h (t <= 705 s). A readout for the director; it decides nothing here.
# Writes only $NEW/post-s2-dry/ (refused if it exists). Nothing is repaired. No set -u.
SELF=$1
M=f4d2d7f3833834390b7b031df61ba1a5765e9900
NEW=/pscratch/sd/j/josephrb/ens1-a1-20261108
D=$NEW/deploy
R=$NEW/post-s2-dry
L=$NEW/stage2/log-dry
PROBE_SHA=807c40d3cb64e2e09d2fa9a5b91fb7a786f4eb51090e4291d65b3896b47e3b25
JOBNAME=ens1_a1_s2_dry
SPENT=0
CAP=46.0
bail() { rm -f -- "$SELF"; exit 9; }
[ -n "$SELF" ] && [ -f "$SELF" ] || exit 9
[ -s "$NEW/logs-s2/s2-dry.jobid" ] && [ -d "$L" ] && [ ! -e "$R" ] || bail
mkdir "$R" || bail
exec > "$R/connect-postrun.log" 2>&1
finish() { echo "ens1 a1 stage-2 dry postrun rc=$1"; date -u +%FT%TZ; echo "$1" > "$R/connect-postrun.done"; rm -f -- "$SELF"; exit "$1"; }
echo "node $(hostname) nproc=$(nproc) loadavg $(cut -d' ' -f1-3 /proc/loadavg)"; date -u +%FT%TZ
echo "connect script sha256 $(sha256sum "$SELF" | cut -d' ' -f1)"
cp "$SELF" "$R/ens1_a1_s2_dry_postrun.sh"
job=$(cat "$NEW/logs-s2/s2-dry.jobid"); echo "job $job"

echo "== the fence (only rs1_* and ens1_* pass)"
squeue -u josephrb -h -o '%i|%j|%T|%M|%l' > "$R/squeue-before.txt" 2>&1 || { echo "STOP: squeue failed"; finish 9; }
cat "$R/squeue-before.txt"
bad=$(awk -F'|' '$2 !~ /^(rs1_|ens1_)/' "$R/squeue-before.txt")
[ -z "$bad" ] || { echo "FENCE STOP: a cov2d-* job or a job of another name is present:"; printf '%s\n' "$bad"; finish 9; }
[ -z "$(awk -F'|' -v j="$job" '$1 == j' "$R/squeue-before.txt")" ] || { echo "STOP: job $job is still in the queue"; finish 9; }
echo "FENCE: pass"

echo "== the job"
sacct -j "$job" -X -n -P -o JobID,JobName,State,ExitCode,Elapsed,ElapsedRaw,NNodes,NCPUS,Start,End,NodeList > "$R/sacct-$job.txt" 2>&1
cat "$R/sacct-$job.txt"
row=$(awk -F'|' -v j="$job" '$1 == j' "$R/sacct-$job.txt")
name=$(echo "$row" | cut -d'|' -f2); state=$(echo "$row" | cut -d'|' -f3); raw=$(echo "$row" | cut -d'|' -f6); nn=$(echo "$row" | cut -d'|' -f7)
echo "name=$name state=$state elapsed_raw=$raw nnodes=$nn"
[ "$state" = COMPLETED ] && [ "$nn" = 1 ] && [ "$name" = "$JOBNAME" ] && [ -n "$raw" ] \
  || { echo "INCOMPLETE: the job is not COMPLETED on one node under its name (reported unrepaired)"; finish 4; }
nh=$(awk -v r="$raw" 'BEGIN{printf "%.4f", r/3600}'); tot=$(awk -v a=$SPENT -v b="$nh" 'BEGIN{printf "%.4f", a+b}')
echo "charge node_h=$nh; stage 2 spend $SPENT + $nh = $tot of $CAP"
awk -v t="$tot" -v c=$CAP 'BEGIN{exit !(t <= c)}' || { echo "STOP: stage 2's spend is above its cap"; finish 4; }

echo "== the run"
cat "$L/DONE"; echo
[ ! -e "$L/FAILED" ] && [ -z "$(ls "$L" | grep -E '\.(teardown|failed)$')" ] && [ ! -e "$NEW/runs-teardown" ] \
  || { echo "STOP: a FAILED, teardown or failed record, or runs-teardown/"; finish 4; }
[ "$(git -C "$D" rev-parse HEAD)" = "$M" ] || { echo "STOP: deploy HEAD is not M_A1"; finish 9; }
n=$(git -C "$D" status --porcelain --untracked-files=no | wc -l); echo "HEAD $M; modified tracked files: $n"
[ "$n" -eq 0 ] || { echo "STOP: the deploy has modified tracked files"; finish 9; }
[ "$(sha256sum "$D/nd-unfolding/ensemble_estimator_probe.py" | cut -d' ' -f1)" = "$PROBE_SHA" ] || { echo "STOP: the probe"; finish 9; }
grep -v '^#' "$NEW/stage2/dry.tsv" | cut -f1 > "$R/task-ids.txt"
( source "$D/setup_salloc_env.sh" > "$R/env-done.log" 2>&1
  python3 -B -c '
import json, sys
d = json.load(open(sys.argv[1]))
ok = d.get("mode") == "dry" and d.get("stage") == 2 and d.get("tasks") == 7 and d.get("ended") == 7 and d.get("rc") == 0 \
    and d.get("job") == sys.argv[2] and d.get("pin") == sys.argv[3] and d.get("teardown") == ""
sys.exit(0 if ok else 1)' "$L/DONE" "$job" "$M" ) || { echo "STOP: the DONE is not this run's"; finish 4; }

echo "== the seven products (the bound probe's expect)"
: > "$R/products.txt"
while IFS= read -r id; do
  cols=(); while IFS= read -r x; do cols+=("$x"); done < <(awk -F '\t' -v id="$id" '$1 == id { for (i = 1; i <= NF; i++) print $i }' "$NEW/stage2/dry.tsv")
  ( source "$D/setup_salloc_env.sh" > /dev/null 2>&1
    cd "$D" && PYTHONDONTWRITEBYTECODE=1 python3 -B "nd-unfolding/${cols[2]}" expect "${cols[@]:3}" ) > "$R/expect-$id.txt" \
    || { echo "STOP: expect failed for $id"; finish 5; }
  while IFS= read -r f; do printf '%s\t%s\n' "$id" "$f" >> "$R/products.txt"; done < "$R/expect-$id.txt"
done < "$R/task-ids.txt"
cat "$R/products.txt"
np=$(wc -l < "$R/products.txt" | tr -d ' '); echo "products: $np"
[ "$np" -eq 7 ] || { echo "STOP: not seven products"; finish 5; }
miss=0
while IFS=$'\t' read -r id f; do
  rel=${f#"$NEW"/}
  [ -s "$f" ] && [ "$(awk -v n="$rel" '$2 == n {print $1}' "$L/SHA256SUMS")" = "$(sha256sum "$f" | cut -d' ' -f1)" ] || { echo "NOT PINNED $f"; miss=$((miss + 1)); }
done < "$R/products.txt"
[ "$miss" -eq 0 ] || { echo "STOP: a product is missing or not at its line in the run's SHA256SUMS"; finish 5; }

echo "== the blocks, the logs, the determinism control, the truth vectors, the projection (sourced environment)"
cat > "$R/read.py" <<'PYEOF'
import ast, json, re, sys
import numpy as np
products, L, deploy, probe_sha, out = sys.argv[1:6]
sys.path.insert(0, f"{deploy}/nd-unfolding")
import ensemble_estimator_probe as eep  # noqa: E402  (SCHEMA, INTERNAL_BASE, DETERMINISM, DRY2: the bound values)
ZERO = {"MCgen": 0, "MCreco": 0, "measured": 0, "bkg_reco": 0}
rec = {"schema": "ens1-a1-s2-dry-postrun/1", "numpy": np.__version__, "products": {}, "timing": {}}
fails = []
rows = [l.rstrip("\n").split("\t") for l in open(products) if l.strip()]
want_ids = {f"ens1_{t}_k{k:03d}" for t, k in eep.DRY2}
if {r[0] for r in rows} != want_ids:
    fails.append(f"the dry tasks {sorted(r[0] for r in rows)} are not DRY2 {sorted(want_ids)}")
arrays = {}
for tid, path in rows:
    m = re.fullmatch(r"ens1_(.+)_k(\d\d\d)", tid)
    truth, k = m.group(1), int(m.group(2))
    with np.load(path, allow_pickle=False) as z:
        meta = json.loads(str(z["meta"]))
        arrays[(truth, k)] = {n: z[n].copy() for n in ("xsec_flat", "xtrue_flat") if n in z.files}
    b = meta.get("ens1") or {}
    want = {"schema": eep.SCHEMA, "mode": "closure", "k": k, "internal_seed": eep.INTERNAL_BASE + k, "truth": truth}
    got = {key: b.get(key) for key in want}
    moved, code, dt = b.get("moved_rows"), b.get("code_sha256"), b.get("closure_dtype_requested")
    rec["products"][tid] = {"path": path, "block": got, "moved_rows": moved, "code_sha256": code,
                            "closure_dtype_requested": dt, "coord_sha256": b.get("coord_sha256"),
                            "hypothesis_sha256": (meta.get("hypothesis") or {}).get("sha256"),
                            "alternative_sha256": (meta.get("alternative") or {}).get("sha256"),
                            "pseudo_seed": meta.get("pseudo_seed"), "development": meta.get("development"),
                            "seconds_unfold_meta": meta.get("seconds_unfold")}
    if got != want:
        fails.append(f"{tid}: ens1 block {got}, the task states {want}")
    if moved != ZERO:
        fails.append(f"{tid}: moved_rows {moved}")
    if code != probe_sha:
        fails.append(f"{tid}: code_sha256 {code}")
    if dt is None:
        fails.append(f"{tid}: closure_dtype_requested not recorded")
    if set(arrays[(truth, k)]) != {"xsec_flat", "xtrue_flat"}:
        fails.append(f"{tid}: xsec_flat or xtrue_flat missing")
    log = open(f"{L}/tasks/{tid}.log", errors="replace").read()
    parsed = [ast.literal_eval(s) for s in re.findall(r"\[ens1\] grid membership moved rows (\{[^}]*\})", log)]
    if len(parsed) != 1 or parsed[0] != ZERO:
        fails.append(f"{tid}: log moved-rows lines {parsed}")
    outl = [json.loads(l) for l in log.splitlines() if l.startswith('{"out"')]
    if len(outl) != 1 or outl[0].get("rc") != 0 or outl[0].get("out") != path.rsplit("/", 1)[-1]:
        fails.append(f"{tid}: runner lines {outl}")
    t0, t1 = float(open(f"{L}/{tid}.start").read()), float(open(f"{L}/{tid}.end").read())
    rec["timing"][tid] = {"seconds": [o.get("seconds") for o in outl], "seconds_unfold_meta": meta.get("seconds_unfold"),
                          "wall": round(t1 - t0, 1)}


def same(a, b):
    return a.dtype == b.dtype and a.shape == b.shape and a.tobytes() == b.tobytes()


cmp = {}
nom1, a7 = arrays.get(("nominal", 1)), arrays.get((eep.DETERMINISM[1], 1))
if nom1 and a7 and set(nom1) == set(a7) == {"xsec_flat", "xtrue_flat"}:
    cmp["determinism"] = {n: {"dtype": [str(nom1[n].dtype), str(a7[n].dtype)], "shape": [list(nom1[n].shape), list(a7[n].shape)],
                              "bitwise_identical": bool(same(nom1[n], a7[n]))} for n in ("xsec_flat", "xtrue_flat")}
    for n, v in cmp["determinism"].items():
        if not v["bitwise_identical"]:
            fails.append(f"DETERMINISM: A7_mnvtune k=1 {n} DIFFERS from nominal k=1")
else:
    fails.append("DETERMINISM: nominal k=1 or A7_mnvtune k=1 is missing")
cmp["truth_vectors"] = {}
for t in sorted({t for t, _ in eep.DRY2 if t != eep.DETERMINISM[1]}):
    ks = sorted(k for (t_, k) in arrays if t_ == t)
    xs = [arrays[(t, k)].get("xtrue_flat") for k in ks]
    ok = len(xs) > 1 and all(x is not None for x in xs) and all(same(xs[0], x) for x in xs[1:])
    cmp["truth_vectors"][t] = {"k": ks, "bitwise_identical": bool(ok)}
    if not ok:
        fails.append(f"TRUTH VECTORS: {t} xtrue_flat differs across k {ks}")
rec["compare"] = cmp
secs = [s for r in rec["timing"].values() for s in r["seconds"] if s is not None]
t = max(secs) if secs else None
w = max((r["wall"] for r in rec["timing"].values()), default=None)
rec["projection"] = {"t_max_seconds": t, "task_wall_max": w, "lane_unfolds": 34, "bound_t": 705, "limit_h": 6.75,
                     "shard_wall_h_from_t": None if t is None else round((34 * t + 300) / 3600, 3),
                     "shard_wall_h_from_wall": None if w is None else round((34 * w + 300) / 3600, 3)}
rec["failures"] = fails
rec["verdict"] = "PASS" if not fails else "STOP"
with open(out, "w") as fh:
    json.dump(rec, fh, indent=1)
print(json.dumps({"verdict": rec["verdict"], "failures": fails, "compare": cmp, "projection": rec["projection"],
                  "timing": rec["timing"],
                  "dtype_requested": {k: v["closure_dtype_requested"] for k, v in rec["products"].items()}}))
sys.exit(0 if not fails else 4)
PYEOF
echo "read.py sha256 $(sha256sum "$R/read.py" | cut -d' ' -f1)"
( source "$D/setup_salloc_env.sh" > "$R/env-read.log" 2>&1
  python3 --version
  PYTHONDONTWRITEBYTECODE=1 python3 -B "$R/read.py" "$R/products.txt" "$L" "$D" "$PROBE_SHA" "$R/s2-dry-read.json" ); rc=$?
echo "read rc=$rc"
[ -s "$R/s2-dry-read.json" ] && sha256sum "$R/s2-dry-read.json"
[ $rc -eq 0 ] || { echo "STOP: a block, a log, the determinism control or the truth vectors (see s2-dry-read.json); reported unrepaired"; finish 4; }
finish 0

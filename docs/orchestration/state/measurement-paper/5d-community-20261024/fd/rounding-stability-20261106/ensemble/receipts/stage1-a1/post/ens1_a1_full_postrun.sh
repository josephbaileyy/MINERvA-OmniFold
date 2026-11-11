#!/bin/bash
# ENS1 stage-1 FULL run under addendum A1: the post-run connect (declaration §8, §4.4-§4.5's execution side). 0 node-h,
# login node, from a /dev/shm copy of itself ($1), after the six shard jobs have ended. It grades nothing: the stage-1
# statistic, G0 and the verdict are the bound analysis's, in a separate connect after this one's receipt. In order:
#   the fence (only rs1_* and ens1_* pass; cov2d-* or any other name stops), recorded; none of the six jobs may still be
#     in the queue;
#   the jobs: their ids from $NEW/logs/a1-full.jobids (shards 0-5); sacct COMPLETED on 1 node each; the charge from
#     sacct's ElapsedRaw, and stage 1's spend (0.4622 from attempt 1 and the dry rerun, plus the six) at most 55.0;
#   the deploy at M_A1 with its tracked files clean and the bound probe's sha256; the dry DONE still at its receipted
#     sha256; runs-teardown/ listed with its sha256s if it exists (judged by read.py);
#   then read.py (embedded, under the sourced environment, Python 3.11), which checks, from the run's own files:
#     each shard's DONE (shard i, stage 1, tasks = ended = its queue's count, rc 0, its job, pin M_A1), no FAILED or
#       STOP, no .failed, every task's .start and .end;
#     the teardown guard as bound (sbatch_ens1.sh:49-79; the director's ruling): a task with a .teardown record is
#       accepted only if the record names every product as bitwise_identical, no .failed sits beside it, the DONE's
#       teardown field lists exactly the shard's .teardown ids, and runs-teardown/<id>/ holds exactly its products; a
#       DIFFERS or "comparison failed" line is a STOP (a reproducibility finding); runs-teardown/ existing with no
#       teardown listed in any DONE is a STOP; its files are counted apart from the 2,017;
#     the products: each task's, by the bound probe's expected_outputs (imported from the deploy), present and at its
#       line in its own shard's SHA256SUMS, and unchanged now; the dry run's nine at their receipted lines; and the set
#       of files under runs/ equal to the 2,017 expected (2,016 stability products and F64), nothing else;
#     every product's ens1 block: moved_rows 0 in every class (gate E5), mode, k and protocol seed as its name states,
#       the bound probe's code_sha256 (only each product's meta is read, never its arrays);
#     every full task's log: one "[ens1] grid membership moved rows" line per unfold, all zero, and one '{"out"' line per
#       unfold naming its products (a teardown task's log also holds its first run's lines: between one and two per
#       unfold, all zero, the last ones naming its products);
#     the timing readout: seconds_unfold per unfold, task walls, and each shard's sacct wall.
# Writes only $NEW/post-full/ (refused if it exists). Attempt 1's root is not touched. No set -u.
SELF=$1
M=f4d2d7f3833834390b7b031df61ba1a5765e9900
NEW=/pscratch/sd/j/josephrb/ens1-a1-20261108
D=$NEW/deploy
R=$NEW/post-full
SD=$NEW/stage1
PROBE_SHA=807c40d3cb64e2e09d2fa9a5b91fb7a786f4eb51090e4291d65b3896b47e3b25
DONE_SHA=96bffd6266f6e2bc2a60d11b3cc4839fb76b828106c9efd63c8966c63e37ba7a
DRYSUMS_SHA=20491b0c2a4fba8887c85370ceaa10d6bb4414ed978a6ede97793180deb0cc84   # receipts/stage1-dry-a1/log-dry/SHA256SUMS
SPENT=0.4622
CAP=55.0
bail() { rm -f -- "$SELF"; exit 9; }
[ -n "$SELF" ] && [ -f "$SELF" ] || exit 9
[ -s "$NEW/logs/a1-full.jobids" ] && [ -d "$SD" ] && [ ! -e "$R" ] || bail
mkdir "$R" || bail
exec > "$R/connect-postrun.log" 2>&1
finish() { echo "ens1 a1 full postrun rc=$1"; date -u +%FT%TZ; echo "$1" > "$R/connect-postrun.done"; rm -f -- "$SELF"; exit "$1"; }
echo "node $(hostname) nproc=$(nproc) loadavg $(cut -d' ' -f1-3 /proc/loadavg)"; date -u +%FT%TZ
echo "connect script sha256 $(sha256sum "$SELF" | cut -d' ' -f1)"
cp "$SELF" "$R/ens1_a1_full_postrun.sh"
cp "$NEW/logs/a1-full.jobids" "$R/jobids.txt"; cat "$R/jobids.txt"
[ "$(cut -d' ' -f1 "$R/jobids.txt" | tr '\n' ' ')" = "0 1 2 3 4 5 " ] || { echo "STOP: the jobids file is not shards 0-5"; finish 9; }
jobs=$(cut -d' ' -f2 "$R/jobids.txt" | tr '\n' ',' | sed 's/,$//')

echo "== the fence (only rs1_* and ens1_* pass)"
squeue -u josephrb -h -o '%i|%j|%T|%M|%l' > "$R/squeue-before.txt" 2>&1 || { echo "STOP: squeue failed"; finish 9; }
cat "$R/squeue-before.txt"
bad=$(awk -F'|' '$2 !~ /^(rs1_|ens1_)/' "$R/squeue-before.txt")
[ -z "$bad" ] || { echo "FENCE STOP: a cov2d-* job or a job of another name is present:"; printf '%s\n' "$bad"; finish 9; }
for j in $(cut -d' ' -f2 "$R/jobids.txt"); do
  [ -z "$(awk -F'|' -v j="$j" '$1 == j' "$R/squeue-before.txt")" ] || { echo "STOP: job $j is still in the queue"; finish 9; }
done
echo "FENCE: pass; none of the six jobs is queued"

echo "== the jobs"
sacct -j "$jobs" -X -n -P -o JobID,JobName,State,ExitCode,Elapsed,ElapsedRaw,NNodes,NCPUS,Start,End,NodeList > "$R/sacct-full.txt" 2>&1 \
  || { echo "STOP: sacct failed"; finish 9; }
cat "$R/sacct-full.txt"
nok=0; raw=0
while read -r i j; do
  row=$(awk -F'|' -v j="$j" '$1 == j' "$R/sacct-full.txt")
  st=$(echo "$row" | cut -d'|' -f3); er=$(echo "$row" | cut -d'|' -f6); nn=$(echo "$row" | cut -d'|' -f7); nm=$(echo "$row" | cut -d'|' -f2)
  echo "shard $i job $j name=$nm state=$st elapsed_raw=$er nnodes=$nn"
  [ "$st" = COMPLETED ] && [ "$nn" = 1 ] && [ "$nm" = "ens1_a1_s1_$i" ] && [ -n "$er" ] && nok=$((nok + 1)) && raw=$((raw + er))
done < "$R/jobids.txt"
[ "$nok" -eq 6 ] || { echo "STOP: not all six jobs COMPLETED on one node under their names (INCOMPLETE; reported unrepaired)"; finish 4; }
nh=$(awk -v r="$raw" 'BEGIN{printf "%.4f", r/3600}'); tot=$(awk -v a=$SPENT -v b="$nh" 'BEGIN{printf "%.4f", a+b}')
echo "charge node_h=$nh (sum of ElapsedRaw $raw s on 1 node each); stage 1 spend $SPENT + $nh = $tot of $CAP"
awk -v t="$tot" -v c=$CAP 'BEGIN{exit !(t <= c)}' || { echo "STOP: stage 1's spend is above its cap"; finish 4; }

echo "== the deploy and the dry run"
[ "$(git -C "$D" rev-parse HEAD)" = "$M" ] || { echo "STOP: deploy HEAD is not M_A1"; finish 9; }
n=$(git -C "$D" status --porcelain --untracked-files=no | wc -l); echo "HEAD $M; modified tracked files: $n"
[ "$n" -eq 0 ] || { echo "STOP: the deploy has modified tracked files"; finish 9; }
[ "$(sha256sum "$D/nd-unfolding/ensemble_estimator_probe.py" | cut -d' ' -f1)" = "$PROBE_SHA" ] || { echo "STOP: the probe"; finish 9; }
[ "$(sha256sum "$SD/log-dry/DONE" | cut -d' ' -f1)" = "$DONE_SHA" ] && [ "$(sha256sum "$SD/log-dry/SHA256SUMS" | cut -d' ' -f1)" = "$DRYSUMS_SHA" ] \
  || { echo "STOP: the dry run's DONE or SHA256SUMS is not the receipted file"; finish 9; }
if [ -e "$NEW/runs-teardown" ]; then
  ( cd "$NEW" && find runs-teardown -type f -print0 | sort -z | xargs -0 sha256sum ) > "$R/runs-teardown-SHA256SUMS"
  echo "runs-teardown/ exists, $(grep -c . "$R/runs-teardown-SHA256SUMS") files (judged by read.py against the DONEs):"; cat "$R/runs-teardown-SHA256SUMS"
else
  : > "$R/runs-teardown-SHA256SUMS"; echo "runs-teardown/: absent"
fi
for i in 0 1 2 3 4 5; do echo "log-shard$i/DONE: $(cat "$SD/log-shard$i/DONE" 2>&1)"; done
( cd "$NEW" && find runs -type f -print0 | sort -z | xargs -0 sha256sum ) > "$R/runs-SHA256SUMS"
echo "files under runs/: $(grep -c . "$R/runs-SHA256SUMS")"; sha256sum "$R/runs-SHA256SUMS"

echo "== the run's records, the products, E5, the timing (sourced environment)"
cat > "$R/read.py" <<'PYEOF'
import ast, json, re, sys
from pathlib import Path
import numpy as np
NEW, D, M, probe_sha, jobids, sacct, runsums, tdsums, out = sys.argv[1:10]
td_present = Path(NEW, "runs-teardown").exists()
sys.path.insert(0, f"{D}/nd-unfolding")
import ensemble_estimator_probe as eep
ZERO = {"MCgen": 0, "MCreco": 0, "measured": 0, "bkg_reco": 0}
SD = Path(NEW) / "stage1"
fails = []
rec = {"schema": "ens1-a1-full-postrun/1", "python": sys.version.split()[0], "numpy": np.__version__,
       "shards": {}, "timing": {}, "products": {}}
final = dict(reversed(l.split(None, 1)) for l in open(runsums).read().splitlines() if l.strip())
jobs = dict(l.split() for l in open(jobids).read().splitlines() if l.strip())
sa = {l.split("|")[0]: l.split("|") for l in open(sacct).read().splitlines() if l.strip()}


def tasks_of(tsv):
    rows = [l.rstrip("\n").split("\t") for l in open(tsv) if l.strip() and not l.startswith("#")]
    return [(r[0], int(r[1]), r[3:]) for r in rows]


def sums_of(path):
    return dict(reversed(l.split(None, 1)) for l in open(path).read().splitlines() if l.strip())


expected = {}                                     # runs/... -> task id
listed_td, td_expected, teardowns = set(), {}, {}  # teardown ids; runs-teardown/<id>/<name> -> task id
su_all, su_final, walls = [], [], []
for i in range(6):
    L = SD / f"log-shard{i}"
    tasks = tasks_of(SD / f"shard{i}.tsv")
    srec = {"tasks": len(tasks), "job": jobs.get(str(i))}
    try:
        done = json.loads((L / "DONE").read_text())
    except Exception as exc:  # noqa: BLE001
        fails.append(f"shard {i}: no readable DONE ({exc})")
        done = {}
    srec["done"] = done
    want = {"mode": "shard", "stage": 1, "shard": str(i), "tasks": len(tasks), "ended": len(tasks), "rc": 0,
            "job": jobs.get(str(i)), "pin": M}
    if {k: v for k, v in done.items() if k != "teardown"} != want or not isinstance(done.get("teardown"), str):
        fails.append(f"shard {i}: DONE {done} is not {want} with a teardown field")
    odd = sorted(p.name for p in L.iterdir() if p.name in ("FAILED", "STOP") or p.suffix == ".failed")
    if odd:
        fails.append(f"shard {i}: {odd}")
    td_files = sorted(p.stem for p in L.iterdir() if p.suffix == ".teardown")
    td_done = sorted(str(done.get("teardown") or "").split())
    srec["teardown"] = td_done
    if td_files != td_done:
        fails.append(f"shard {i}: DONE lists teardown {td_done}, the shard holds .teardown records {td_files}")
    listed_td |= set(td_files)
    sums = sums_of(L / "SHA256SUMS") if (L / "SHA256SUMS").is_file() else {}
    if not sums:
        fails.append(f"shard {i}: no SHA256SUMS")
    row = sa.get(jobs.get(str(i)), [])
    srec["sacct_elapsed_raw"] = int(row[5]) if len(row) > 5 and row[5].isdigit() else None
    nmiss = 0
    for tid, nunf, argv in tasks:
        outs = [str(p) for p in eep.expected_outputs(argv)]
        rels = [o[len(NEW) + 1:] if o.startswith(NEW + "/") else o for o in outs]
        if len(rels) != nunf:
            fails.append(f"{tid}: {len(rels)} expected products for {nunf} unfolds")
        for r in rels:
            if r in expected:
                fails.append(f"{r}: expected from {expected[r]} and {tid}")
            expected[r] = tid
            if r not in sums or r not in final or sums[r] != final[r]:
                nmiss += 1
                if nmiss <= 5:
                    fails.append(f"{tid}: {r} not at its line in shard {i}'s SHA256SUMS, or changed since")
        try:
            t0, t1 = float((L / f"{tid}.start").read_text()), float((L / f"{tid}.end").read_text())
            wall = round(t1 - t0, 1)
            walls.append(wall)
        except Exception as exc:  # noqa: BLE001
            fails.append(f"{tid}: start/end ({exc})")
            wall = None
        td = (L / f"{tid}.teardown").is_file()
        if td:
            lines = (L / f"{tid}.teardown").read_text(errors="replace").splitlines()
            verdicts = {ln.rsplit(" ", 1)[0]: ln.rsplit(" ", 1)[1] for ln in lines[1:]
                        if ln.endswith(" bitwise_identical") or ln.endswith(" DIFFERS")}
            bad = [ln for ln in lines[1:] if ln.endswith(" DIFFERS") or ln.endswith(" comparison failed")]
            names = sorted(Path(r).name for r in rels)
            teardowns[tid] = {"shard": i, "record": lines, "products": names}
            if bad:
                fails.append(f"REPRODUCIBILITY: {tid}'s teardown record reads {bad} (the director's finding, unrepaired)")
            elif sorted(verdicts) != names or any(v != "bitwise_identical" for v in verdicts.values()):
                fails.append(f"{tid}: teardown record {lines} does not name every product {names} as bitwise_identical")
            if (L / f"{tid}.failed").exists():
                fails.append(f"{tid}: .failed beside its .teardown")
            for nm in names:
                td_expected[f"runs-teardown/{tid}/{nm}"] = tid
        log = (L / "tasks" / f"{tid}.log").read_text(errors="replace") if (L / "tasks" / f"{tid}.log").is_file() else ""
        moved = [ast.literal_eval(s) for s in re.findall(r"\[ens1\] grid membership moved rows (\{[^}]*\})", log)]
        nmv_ok = (nunf <= len(moved) <= 2 * nunf) if td else (len(moved) == nunf)
        if not nmv_ok or any(m != ZERO for m in moved):
            fails.append(f"E5 log: {tid} logged {moved} for {nunf} unfolds{' (teardown task)' if td else ''}")
        outl = [json.loads(l) for l in log.splitlines() if l.startswith('{"out"')]
        n_ok = (nunf <= len(outl) <= 2 * nunf) if td else (len(outl) == nunf)
        last = outl[-nunf:] if len(outl) >= nunf else outl
        if not n_ok or sorted(o.get("out") for o in last) != sorted(Path(r).name for r in rels):
            fails.append(f"{tid}: '{{\"out\"' lines {[o.get('out') for o in outl]} do not name its {nunf} products")
        su = [float(o["seconds_unfold"]) for o in outl]
        su_final += [float(o["seconds_unfold"]) for o in last]
        su_all += su
        rec["timing"][tid] = {"shard": i, "seconds_unfold": su, "wall": wall}
    srec["products_not_pinned"] = nmiss
    rec["shards"][str(i)] = srec
# the dry run's nine, each at its line in the receipted dry SHA256SUMS and unchanged now
drysums = sums_of(SD / "log-dry" / "SHA256SUMS")
n_dry = 0
for tid, nunf, argv in tasks_of(SD / "dry.tsv"):
    for p in eep.expected_outputs(argv):
        r = str(p)[len(NEW) + 1:]
        n_dry += 1
        if r in expected:
            fails.append(f"{r}: expected from {expected[r]} and dry {tid}")
        expected[r] = tid
        if r not in drysums or final.get(r) != drysums[r]:
            fails.append(f"dry product {r} is not at its dry SHA256SUMS line, or changed since the dry run")
if n_dry != 9:
    fails.append(f"{n_dry} dry products, not 9")
want_set = {f"runs/stability/ens1_k{k:03d}_b-_j{s}.npz" for s in range(21) for k in range(1, 97)} | {"runs/F64/ens1_F64_b-_j0.npz"}
rec["n_expected"], rec["n_files"] = len(expected), len(final)
if set(expected) != want_set:
    fails.append(f"the queues' products are not the 2,017 declared ({len(expected)}; "
                 f"{sorted(set(expected) ^ want_set)[:5]})")
if set(final) != want_set:
    fails.append(f"runs/ holds {len(final)} files, not the 2,017 declared: {sorted(set(final) ^ want_set)[:5]}")
# every product's ens1 block (meta only)
n_moved, n_block, n_code = 0, 0, 0
for r in sorted(want_set & set(final)):
    with np.load(f"{NEW}/{r}", allow_pickle=False) as z:
        meta = json.loads(str(z["meta"]))
    b = meta.get("ens1") or {}
    mm = re.fullmatch(r"runs/stability/ens1_k(\d{3})_b-_j(\d+)\.npz", r)
    want = {"mode": "base", "k": None, "protocol_seed": 0} if mm is None else \
        {"mode": "stability", "k": int(mm.group(1)), "protocol_seed": int(mm.group(2))}
    got = {k: b.get(k) for k in want}
    if b.get("moved_rows") != ZERO:
        n_moved += 1
        if n_moved <= 5:
            fails.append(f"E5: {r} records moved_rows {b.get('moved_rows')}")
    if got != want:
        n_block += 1
        if n_block <= 5:
            fails.append(f"{r}: ens1 block {got}, its name states {want}")
    if b.get("code_sha256") != probe_sha:
        n_code += 1
        if n_code <= 5:
            fails.append(f"{r}: code_sha256 {b.get('code_sha256')}")
rec["products"] = {"read": len(want_set & set(final)), "moved_rows_nonzero": n_moved, "block_mismatch": n_block,
                   "code_mismatch": n_code}
shard_walls = [s["sacct_elapsed_raw"] for s in rec["shards"].values() if s["sacct_elapsed_raw"] is not None]
rec["timing_summary"] = {"unfolds": len(su_final), "seconds_unfold_lines": len(su_all), "seconds_unfold_max": max(su_all) if su_all else None,
                         "seconds_unfold_median": float(np.median(su_all)) if su_all else None,
                         "task_wall_max": max(walls) if walls else None,
                         "shard_wall_s_max": max(shard_walls) if shard_walls else None,
                         "shard_wall_h_max": round(max(shard_walls) / 3600, 3) if shard_walls else None,
                         "projected_h_from_dry": 6.799, "limit_h": 9.0}
if len(su_final) != 2008:
    fails.append(f"{len(su_final)} final seconds_unfold lines in the shards, not 2,008")
# runs-teardown/: only with a listed teardown, and exactly the listed tasks' products, counted apart from the 2,017
tdfinal = dict(reversed(l.split(None, 1)) for l in open(tdsums).read().splitlines() if l.strip())
rec["teardowns"] = teardowns
rec["runs_teardown_files"] = len(tdfinal)
rec["runs_teardown_present"] = td_present
if td_present and not listed_td:
    fails.append(f"runs-teardown/ exists ({len(tdfinal)} files) but no DONE lists a teardown")
elif set(tdfinal) != set(td_expected):
    fails.append(f"runs-teardown/ holds {sorted(tdfinal)[:5]}, not the listed teardowns' products {sorted(td_expected)[:5]}")
rec["failures"] = fails
rec["verdict"] = "PASS" if not fails else "STOP"
with open(out, "w") as fh:
    json.dump(rec, fh, indent=1)
print(json.dumps({"verdict": rec["verdict"], "failures": fails[:20], "n_failures": len(fails),
                  "products": rec["products"], "n_files": rec["n_files"], "teardowns": sorted(teardowns),
                  "runs_teardown_files": rec["runs_teardown_files"], "timing": rec["timing_summary"],
                  "shards": {k: {"tasks": v["tasks"], "job": v["job"], "elapsed_raw": v["sacct_elapsed_raw"]}
                             for k, v in rec["shards"].items()}}))
sys.exit(0 if not fails else 4)
PYEOF
echo "read.py sha256 $(sha256sum "$R/read.py" | cut -d' ' -f1)"
( source "$D/setup_salloc_env.sh" > "$R/env-read.log" 2>&1
  python3 --version
  cd "$R" && PYTHONDONTWRITEBYTECODE=1 nice -n 19 python3 -B "$R/read.py" "$NEW" "$D" "$M" "$PROBE_SHA" "$R/jobids.txt" \
    "$R/sacct-full.txt" "$R/runs-SHA256SUMS" "$R/runs-teardown-SHA256SUMS" "$R/a1-full-read.json" ); rc=$?
echo "read rc=$rc"
[ -s "$R/a1-full-read.json" ] && sha256sum "$R/a1-full-read.json"
[ $rc -eq 0 ] || { echo "STOP: a shard's records, a product, E5 or a log (see a1-full-read.json); reported unrepaired"; finish 4; }
finish 0

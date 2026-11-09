import ast, json, re, sys
from pathlib import Path
import numpy as np
NEW, D, M, probe_sha, jobids, sacct, runsums, tdsums, s1sums, out = sys.argv[1:11]
td_present = Path(NEW, "runs-teardown").exists()
sys.path.insert(0, f"{D}/nd-unfolding")
import ensemble_estimator_probe as eep
ZERO = {"MCgen": 0, "MCreco": 0, "measured": 0, "bkg_reco": 0}
TRUTHS = ("nominal", "W1", "W2", "W3", "q3", "stage0c_gibuu", "closure_nuwro", "A7_mnvtune", "A7_genie_cv", "A7_genie_mec",
          "A7_nuwro", "A7_gibuu", "P1r", "P2r", "P3r", "P1g", "P2g", "P3g")   # §3.2, the 18 F0b truths
SD = Path(NEW) / "stage2"
fails = []
rec = {"schema": "ens1-a1-s2-full-postrun/1", "python": sys.version.split()[0], "numpy": np.__version__,
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
listed_td, td_expected, teardowns = set(), {}, {}
sec_all, sec_final, walls = [], [], []
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
    want = {"mode": "shard", "stage": 2, "shard": str(i), "tasks": len(tasks), "ended": len(tasks), "rc": 0,
            "job": jobs.get(str(i)), "pin": M}
    if {k: v for k, v in done.items() if k != "teardown"} != want or not isinstance(done.get("teardown"), str):
        fails.append(f"shard {i}: DONE {done} is not {want} with a teardown field")
    odd = sorted(p.name for p in L.iterdir() if p.name in ("FAILED", "STOP") or p.suffix == ".failed") if L.is_dir() else ["no log dir"]
    if odd:
        fails.append(f"shard {i}: {odd}")
    td_files = sorted(p.stem for p in L.iterdir() if p.suffix == ".teardown") if L.is_dir() else []
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
            fails.append(f"moved rows in the log: {tid} logged {moved} for {nunf} unfolds{' (teardown task)' if td else ''}")
        outl = [json.loads(l) for l in log.splitlines() if l.startswith('{"out"')]
        n_ok = (nunf <= len(outl) <= 2 * nunf) if td else (len(outl) == nunf)
        last = outl[-nunf:] if len(outl) >= nunf else outl
        if not n_ok or sorted(o.get("out") for o in last) != sorted(Path(r).name for r in rels) \
                or any(o.get("rc") != 0 for o in last):
            fails.append(f"{tid}: runner lines {[(o.get('out'), o.get('rc')) for o in outl]} do not name its {nunf} products with rc 0")
        sec = [float(o["seconds"]) for o in outl if "seconds" in o]
        sec_final += [float(o["seconds"]) for o in last if "seconds" in o]
        sec_all += sec
        rec["timing"][tid] = {"shard": i, "seconds": sec, "wall": wall}
    srec["products_not_pinned"] = nmiss
    rec["shards"][str(i)] = srec
# the dry run's seven, each at its line in the receipted dry SHA256SUMS and unchanged now
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
if n_dry != 7:
    fails.append(f"{n_dry} dry products, not 7")
want_set = {f"runs/closure/{t}/ens1_{t}_k{k:03d}_s991000.npz" for t in TRUTHS if t != "A7_mnvtune" for k in range(1, 97)} \
    | {"runs/closure/A7_mnvtune/ens1_A7_mnvtune_k001_s991000.npz"}
s1 = sums_of(s1sums)
rec["n_expected"], rec["n_files"], rec["n_stage1"] = len(expected), len(final), len(s1)
if set(expected) != want_set:
    fails.append(f"the queues' products are not the 1,633 declared ({len(expected)}; {sorted(set(expected) ^ want_set)[:5]})")
if len(s1) != 2017 or any(final.get(r) != h for r, h in s1.items()):
    fails.append(f"stage 1's {len(s1)} products are not all at their lines in stage 1's final listing")
if set(final) != want_set | set(s1):
    fails.append(f"runs/ holds {len(final)} files, not the 1,633 closure products and stage 1's 2,017: "
                 f"{sorted(set(final) ^ (want_set | set(s1)))[:5]}")
# every closure product's ens1 block (meta only)
n_moved, n_block, n_code, n_dtype = 0, 0, 0, 0
sum_meta = []
for r in sorted(want_set & set(final)):
    with np.load(f"{NEW}/{r}", allow_pickle=False) as z:
        meta = json.loads(str(z["meta"]))
    b = meta.get("ens1") or {}
    mm = re.fullmatch(r"runs/closure/([^/]+)/ens1_(.+)_k(\d{3})_s991000\.npz", r)
    k = int(mm.group(3))
    want = {"schema": eep.SCHEMA, "mode": "closure", "k": k, "internal_seed": eep.INTERNAL_BASE + k, "truth": mm.group(1)}
    got = {key: b.get(key) for key in want}
    if mm.group(1) != mm.group(2):
        fails.append(f"{r}: directory and name disagree")
    if b.get("moved_rows") != ZERO:
        n_moved += 1
        if n_moved <= 5:
            fails.append(f"{r} records moved_rows {b.get('moved_rows')}")
    if got != want:
        n_block += 1
        if n_block <= 5:
            fails.append(f"{r}: ens1 block {got}, its name states {want}")
    if b.get("code_sha256") != probe_sha:
        n_code += 1
        if n_code <= 5:
            fails.append(f"{r}: code_sha256 {b.get('code_sha256')}")
    if b.get("closure_dtype_requested") is None:
        n_dtype += 1
        if n_dtype <= 5:
            fails.append(f"{r}: closure_dtype_requested not recorded")
    if meta.get("seconds_unfold") is not None and expected.get(r, "").startswith("ens1_") and r not in drysums:
        sum_meta.append(float(meta["seconds_unfold"]))
rec["products"] = {"read": len(want_set & set(final)), "moved_rows_nonzero": n_moved, "block_mismatch": n_block,
                   "code_mismatch": n_code, "dtype_unrecorded": n_dtype}
shard_walls = [s["sacct_elapsed_raw"] for s in rec["shards"].values() if s["sacct_elapsed_raw"] is not None]
rec["timing_summary"] = {"unfolds": len(sec_final), "runner_lines": len(sec_all),
                         "seconds_max": max(sec_all) if sec_all else None,
                         "seconds_median": float(np.median(sec_all)) if sec_all else None,
                         "meta_seconds_unfold_n": len(sum_meta),
                         "meta_seconds_unfold_max": max(sum_meta) if sum_meta else None,
                         "meta_seconds_unfold_median": float(np.median(sum_meta)) if sum_meta else None,
                         "meta_seconds_unfold_over_705": sum(1 for v in sum_meta if v > 705),
                         "task_wall_max": max(walls) if walls else None,
                         "shard_wall_s_max": max(shard_walls) if shard_walls else None,
                         "shard_wall_h_max": round(max(shard_walls) / 3600, 3) if shard_walls else None,
                         "projected_h_from_dry": 5.779, "limit_h": 7.5}
if len(sec_final) != 1626:
    fails.append(f"{len(sec_final)} final runner lines in the shards, not 1,626")
if len(sum_meta) != 1626:
    fails.append(f"{len(sum_meta)} shard products carry meta seconds_unfold, not 1,626")
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
                  "products": rec["products"], "n_files": rec["n_files"], "n_stage1": rec["n_stage1"],
                  "teardowns": sorted(teardowns), "runs_teardown_files": rec["runs_teardown_files"],
                  "timing": rec["timing_summary"],
                  "shards": {k: {"tasks": v["tasks"], "job": v["job"], "elapsed_raw": v["sacct_elapsed_raw"]}
                             for k, v in rec["shards"].items()}}))
sys.exit(0 if not fails else 4)

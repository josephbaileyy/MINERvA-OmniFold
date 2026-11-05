#!/bin/bash
# REF-G1 step one: REF-G1-DECLARATION.md §7 preconditions 1-3 (REF-G1-BINDING-1.md), on a data-transfer node (dtn01),
# 0 node-h. Reads only; nothing is rebuilt. A fresh clone at G (main ddbc43e4, which carries the declaration) into
# $P/deploy, clean, with the committed inventories verified by blob; then, threads 1, nice 19, idle I/O, every read
# through O_NOATIME, and each file's atime and mtime taken from os.stat BEFORE it is read:
#   1. the (e) products of §3, each against S1's or F0b's inventory:
#      the central product and the 50 statistical replicas (s5p-20260926/runs/s2/num/data, against
#        5d-design stage0/INVENTORY.sha256; the central also against s1_assemble.CENTRAL_SHA256);
#      the 175 universe products of s1_assemble.EXPECT (s1-20261024/runs/uni, against s1_assembly/FILES.tsv, which is
#        s1_assembly.json meta.inputs_sha256), with the per-band counts checked against EXPECT;
#      the ladder's three (e) unfolds (genie_mec, nuwro, gibuu) against cmodel_5d.json inputs.products_sha256;
#      F0b's two (e) closure products (closure_nuwro, closure_tune_v1) against fd_f0_regrade.PINS closure and floor;
#   IBU's own inputs: of_inputs_5d.npz and bkg_dump.npz against s1_assemble's pins; the ladder's three truth ratios
#      against pv-ladder/prep-SHA256SUMS; G-IBU1's D_N.npz against ibu1/receipts/SHA256SUMS;
#   2. the bank (701) and the detector dump (33) against s1/PRESERVE-INVENTORY.sha256, each directory exactly its
#      pinned set, with sha256 and atime; the record gives each group's oldest atime and that plus 8 weeks;
#   3. O_NOATIME throughout; no file is touched to reset its atime.
# Writes only under a NEW $P: listing.json (verdict PASS only if every file is present and equal to its pin), check.log,
# check.done. Any missing or differing file is a STOP for the director, not repaired. No set -u. Launched from a
# /dev/shm copy of itself (its path is $1), which it deletes at exit.
SELF=$1
G=ddbc43e42f7b1ae4687f024d62baadda99a2aedf
P=/pscratch/sd/j/josephrb/ref-g1-20261105/preconditions
D=$P/deploy
PY=$HOME/.conda/envs/root_6_28/bin/python3
bail() { rm -f -- "$SELF"; exit 9; }                             # a precondition failed: nothing written
case "$(hostname)" in dtn*) ;; *) bail ;; esac
[ ! -e "$P" ] && [ -x "$PY" ] || bail
mkdir -p "$P" || bail
exec > "$P/check.log" 2>&1
finish() { echo "ref-g1 preconditions rc=$1"; date -u +%FT%TZ; echo "$1" > "$P/check.done"; rm -f -- "$SELF"; exit "$1"; }
echo "node $(hostname) nproc=$(nproc) loadavg $(cut -d' ' -f1-3 /proc/loadavg)"
date -u +%FT%TZ
echo "check script sha256 $(sha256sum "$SELF" | cut -d' ' -f1)"
cp "$SELF" "$P/refg1_pre_dtn.sh"

git clone -q https://github.com/josephbaileyy/MINERvA-OmniFold.git "$D" > "$P/clone.log" 2>&1 || { echo "STOP: clone"; finish 3; }
git -C "$D" -c advice.detachedHead=false checkout -q "$G" || { echo "STOP: checkout"; finish 3; }
[ "$(git -C "$D" rev-parse HEAD)" = "$G" ] || { echo "STOP: HEAD is not G"; finish 9; }
n=$(git -C "$D" status --porcelain --ignored | wc -l); echo "HEAD $G; porcelain --ignored lines: $n"
[ "$n" -eq 0 ] || { echo "STOP: the deploy is not clean"; finish 9; }
F=docs/orchestration/state/measurement-paper/5d-community-20261024
bad=0
while read -r b p; do
  [ "$(git -C "$D" rev-parse "$G:$p")" = "$b" ] && [ "$(git -C "$D" hash-object "$p")" = "$b" ] || { echo "MISMATCH $p"; bad=$((bad + 1)); }
done <<BLOBS
2bfdfab2eda66ae16f1d929552ca8b1035980457 docs/orchestration/state/measurement-paper/5d-design-20261023/stage0/INVENTORY.sha256
74ec745dec5ac87b5a07c43b23d31cbe614da7b3 $F/s1/readout/s1_assembly/FILES.tsv
e64ab61328e2ca802274556ad695861681ec6dcf $F/s1/readout/s1_assembly.json
0482007886749b2200538a63360fd902f4b9c9dd nd-unfolding/pv-ladder/readouts/cmodel_5d.json
d93da87ef8d9c5ba90e611f49a4982c9107b7a92 nd-unfolding/pv-ladder/prep-SHA256SUMS
31276b4cd5eb2ee6970bf6b8df0bfb38bde00dbd docs/orchestration/state/2d-closeout/stageF/methods/ibu1/receipts/SHA256SUMS
dc2ac4e4f3098ce59a81fc043526d87b5c49ec77 $F/s1/PRESERVE-INVENTORY.sha256
1542ed946f701bff62ec6fe8c08cdc7c2424c599 nd-unfolding/s1_assemble.py
e4c530b25afda48e0036de24416cea43e467dc45 nd-unfolding/fd_f0_regrade.py
2b8e7415e4f23b1d07150e4b10a6598a304f9efd $F/REF-G1-DECLARATION.md
BLOBS
echo "inventory blobs: 10 checked, $bad mismatches"
[ "$bad" -eq 0 ] || { echo "STOP: the committed inventories are not the bound ones"; finish 9; }

export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 NUMEXPR_NUM_THREADS=1 PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
echo "threads: OMP=$OMP_NUM_THREADS OPENBLAS=$OPENBLAS_NUM_THREADS MKL=$MKL_NUM_THREADS NUMEXPR=$NUMEXPR_NUM_THREADS; nice 19; ionice idle"
nice -n 19 ionice -c3 env -u PYTHONPATH "$PY" -I -B - "$D" "$G" "$P/listing.json" <<'PYEOF'
import hashlib, json, os, socket, sys, time
from collections import Counter
from pathlib import Path
D, G, OUT = Path(sys.argv[1]), sys.argv[2], Path(sys.argv[3])
sys.path.insert(0, str(D / "nd-unfolding"))
import s1_assemble as sa     # noqa: E402  (CENTRAL, INPUT_NPZ, BKG pins; EXPECT)
import fd_f0_regrade as f0   # noqa: E402  (PINS closure and floor)
PS = Path("/pscratch/sd/j/josephrb")
DATA = PS / "s5p-20260926/runs/s2/num/data"
UNI = PS / "s1-20261024/runs/uni"
PVL = PS / "pv-ladder-20261024"
BANK = PS / "MINERvA-OmniFold/nd-unfolding/bank_sweep_5d_bkgaware"
DET = PS / "s5p-20260926/bank_detector"
F = D / "docs/orchestration/state/measurement-paper/5d-community-20261024"


def noatime(p):
    st = os.stat(p)                        # atime and mtime before the read; stat does not change them
    fd = os.open(p, os.O_RDONLY | os.O_NOATIME)
    h, n = hashlib.sha256(), 0
    with os.fdopen(fd, "rb") as f:
        for b in iter(lambda: f.read(1 << 24), b""):
            h.update(b); n += len(b)
    return h.hexdigest(), n, st.st_atime, st.st_mtime


def sums(path, root=None):
    out = {}
    for line in path.read_text().splitlines():
        if line.strip() and not line.startswith("#"):
            h, p = line.split(None, 1)
            p = p.strip()
            out[str(Path(p) if root is None else (root / p.lstrip("./")))] = h
    return out


t0 = time.time()
groups, ok = {}, True


def check(group, path, pin, source):
    global ok
    path = Path(path)
    if not path.is_file():
        r = {"path": str(path), "pin": pin, "pin_source": source, "present": False, "ok": False}
    else:
        got, n, at, mt = noatime(path)
        r = {"path": str(path), "sha256": got, "pin": pin, "pin_source": source, "bytes": n, "present": True,
             "atime": at, "atime_utc": time.strftime("%FT%TZ", time.gmtime(at)), "mtime": mt, "ok": got == pin}
    groups.setdefault(group, []).append(r)
    ok &= r["ok"]


# 1. the (e) products
stage0 = sums(D / "docs/orchestration/state/measurement-paper/5d-design-20261023/stage0/INVENTORY.sha256")
cen = DATA / "data_b-_j-.npz"
check("e_central", cen, stage0.get(str(cen)), "5d-design stage0/INVENTORY.sha256")
groups["e_central"][0]["s1_assemble_CENTRAL_SHA256_equal"] = stage0.get(str(cen)) == sa.CENTRAL_SHA256
ok &= stage0.get(str(cen)) == sa.CENTRAL_SHA256
for b in sa.STAT_REPLICAS:
    p = DATA / f"data_b{b}_j{100 + b}.npz"
    check("e_replicas", p, stage0.get(str(p)), "5d-design stage0/INVENTORY.sha256")
files = {}
for line in (F / "s1/readout/s1_assembly/FILES.tsv").read_text().splitlines():
    if line and not line.startswith("#"):
        base, h, src = line.split("\t")[:3]
        if src.startswith(str(UNI) + "/"):
            files[src] = h
meta = json.loads((F / "s1/readout/s1_assembly.json").read_text())["meta"]["inputs_sha256"]
for src, h in sorted(files.items()):
    check("e_universes", src, h, "s1_assembly/FILES.tsv")
    groups["e_universes"][-1]["s1_assembly_json_equal"] = meta.get(Path(src).name) == h
    ok &= meta.get(Path(src).name) == h
bands = Counter(Path(s).name[len("S1_"):].rsplit("_", 1)[0] for s in files)
expect_ok = dict(bands) == dict(sa.EXPECT)
ok &= expect_ok
cm = json.loads((D / "nd-unfolding/pv-ladder/readouts/cmodel_5d.json").read_text())["inputs"]["products_sha256"]
for g in ("genie_mec", "nuwro", "gibuu"):
    check("e_ladder_unfolds", PVL / f"products/L-5D-PV_e_{g}.npz", cm.get(f"L-5D-PV_e_{g}"), "cmodel_5d.json inputs.products_sha256")
for name, key in (("closure_nuwro", "closure"), ("closure_tune_v1", "floor")):
    check("e_f0b_closures", PVL / f"products/L-5D-PV_e_{name}.npz", f0.PINS[key], f"fd_f0_regrade.PINS['{key}']")
# IBU's own inputs
check("ibu_inputs", PS / "MINERvA-OmniFold/nd-unfolding/of_inputs_5d.npz", sa.INPUT_NPZ_SHA256, "s1_assemble.INPUT_NPZ_SHA256")
check("ibu_inputs", PS / "s5c-20260924/runs/p2/bkg_dump.npz", sa.BKG_SHA256, "s1_assemble.BKG_SHA256")
prep = sums(D / "nd-unfolding/pv-ladder/prep-SHA256SUMS", PVL / "prep")
for g in ("genie_mec", "nuwro", "gibuu"):
    p = PVL / f"prep/ratios/L-5D-PV/{g}.json"
    check("ibu_inputs", p, prep.get(str(p)), "nd-unfolding/pv-ladder/prep-SHA256SUMS")
ibu1 = {Path(p).name: h for p, h in sums(D / "docs/orchestration/state/2d-closeout/stageF/methods/ibu1/receipts/SHA256SUMS").items()}
check("ibu_inputs", PS / "ibu1-20261022/run/products/D_N.npz", ibu1.get("D_N.npz"), "ibu1/receipts/SHA256SUMS")
# 2. the bank and the detector dump, exactly their pinned sets
inv = sums(F / "s1/PRESERVE-INVENTORY.sha256")
sets = {}
for key, d in (("bank", BANK), ("detector", DET)):
    want = {Path(p) for p in inv if Path(p).parent == d}
    have = {p for p in d.iterdir() if p.is_file()} if d.is_dir() else set()
    for p in sorted(want):
        check(key, p, inv[str(p)], "s1/PRESERVE-INVENTORY.sha256")
    extra = sorted(map(str, have - want))
    ok &= not extra and len(want) == (701 if key == "bank" else 33)
    at = [r["atime"] for r in groups.get(key, []) if r.get("present")]
    sets[key] = {"dir": str(d), "pinned": len(want), "present": len(have & want), "extra": extra,
                 "oldest_atime_utc": time.strftime("%FT%TZ", time.gmtime(min(at))) if at else None,
                 "newest_atime_utc": time.strftime("%FT%TZ", time.gmtime(max(at))) if at else None,
                 "exposed_from_utc": time.strftime("%FT%TZ", time.gmtime(min(at) + 56 * 86400)) if at else None}
summary = {g: {"files": len(rs), "present": sum(r["present"] for r in rs), "equal_to_pin": sum(r["ok"] for r in rs),
               "oldest_atime_utc": min((r["atime_utc"] for r in rs if r["present"]), default=None)} for g, rs in groups.items()}
t1 = time.time()
rec = {"schema": "ref-g1-preconditions/1", "G": G, "host": socket.gethostname(),
       "rule": "every read O_NOATIME; atime and mtime from os.stat before the read; each file against its committed pin",
       "started_utc": time.strftime("%FT%TZ", time.gmtime(t0)), "summary": summary, "sets": sets,
       "expect_bands": {"found": dict(bands), "s1_assemble_EXPECT": dict(sa.EXPECT), "equal": expect_ok},
       "files": groups, "verdict": "PASS" if ok else "FAIL", "seconds": round(t1 - t0, 1),
       "written_utc": time.strftime("%FT%TZ", time.gmtime(t1)), "written_epoch": t1}
OUT.write_text(json.dumps(rec, indent=1, sort_keys=True) + "\n")
for g, s in summary.items():
    print(f"{g}: {s['files']} files, {s['present']} present, {s['equal_to_pin']} equal to pin, oldest atime {s['oldest_atime_utc']}")
for k, s in sets.items():
    print(f"{k}: {s['pinned']} pinned, {s['present']} present, extra {len(s['extra'])}; atime {s['oldest_atime_utc']} .. {s['newest_atime_utc']}; exposed from {s['exposed_from_utc']}")
print(f"EXPECT bands equal: {expect_ok}")
for g, rs in groups.items():
    for r in rs:
        if not r["ok"]:
            print(f"  {'MISSING' if not r['present'] else 'DIFFERS'} {g} {r['path']}")
print(json.dumps({"verdict": rec["verdict"], "wrote": str(OUT), "sha256": hashlib.sha256(OUT.read_bytes()).hexdigest()}))
sys.exit(0 if ok else 1)
PYEOF
rc=$?
echo "listing python rc=$rc"
n=$(git -C "$D" status --porcelain --ignored | wc -l); echo "porcelain --ignored lines after: $n"
[ "$n" -eq 0 ] || { echo "STOP: the deploy changed"; finish 9; }
[ $rc = 0 ] || { echo "STOP: a file is missing or differs from its pin (final; to the director, not rebuilt)"; finish 4; }
finish 0

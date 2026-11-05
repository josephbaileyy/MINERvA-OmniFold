#!/bin/bash
# REF-C2C1 step one: REF-C2C1-DECLARATION.md §4 preconditions 3, 4 and 6 (REF-C2C1-BINDING-1.md ruling 4, #777, main
# d00a3b66), and the REF-G1 follow-up listing (the director, 2026-11-05), on a login node, 0 node-h. Reads only. No
# universe pass, so $UNI is not read (binding ruling 2). C-DRAW (precondition 5) is a separate connect.
# A fresh clean clone at G = d00a3b66, with the committed pins verified by blob; then, threads 1, nice 19, idle I/O:
#   3. unbinned_unfolding/build/libRooUnfold.so: its build directory listed; the library (with any rootmap/rdict
#      files beside it) copied by an O_NOATIME read into $P/libcopy/, sha256 recorded, and LOADED from that copy in PyROOT (root_6_28), which must give gSystem.Load >= 0 and a RooUnfoldBayes class. The pscratch
#      file itself is never opened except through O_NOATIME;
#   4. E_R's central product (partb/out/ER/xsec.root, a5c13fc3, SHA256SUMS.J1.1), its inputs (the CFS $CV 43f8cc16,
#      the staged copy the run read, the baseline flux $MC d40aea69; re2_env.sh), its refinement evidence (the run log
#      partb/logs/ER.log; the aggregates are re2Refinement inside the product, and their committed health row is in
#      partb_readout/k1_core.json), and Q_R's 300 replica products S1_001..S1_300 (SHA256SUMS.J4a-c) with each one's
#      --bootstrap-seed from partb_runs.tsv;
#   REF-G1 follow-up: tune_v1.json (prep-SHA256SUMS 13bb1eae; = fd_f0_regrade.RATIO floor), s1_assembly.npz
#      (fd_f0_regrade.PINS s1_npz db000707), the flux-universe ROOT file (re2_env.sh FLUXU 5eecae84), the flux
#      constraint (s1_assemble.CONSTRAINT_SHA256 e38ad7d2);
#   6. every pscratch and CFS read through O_NOATIME, each file's atime and mtime from os.stat before its read.
# Writes only under a NEW $P (listing.json, check.log, check.done, the library listing and libcopy/). verdict PASS only if every pinned file is present and equal to its pin, the seeds are 1..300,
# and the library loads with RooUnfoldBayes. A missing or differing file is a STOP for the director. No set -u.
# Launched from a /dev/shm copy of itself (its path is $1), which it deletes at exit.
SELF=$1
G=d00a3b668b0606eba578bb18397019a798efcdc7
P=/pscratch/sd/j/josephrb/ref-c2c1-20261105/preconditions
D=$P/deploy
A=/pscratch/sd/j/josephrb/MINERvA-OmniFold
LIBDIR=$A/unbinned_unfolding/build
bail() { rm -f -- "$SELF"; exit 9; }                             # a precondition failed: nothing written
case "$(hostname)" in login*) ;; *) bail ;; esac
[ ! -e "$P" ] || bail
mkdir -p "$P" || bail
exec > "$P/check.log" 2>&1
TD=$P/libcopy
mkdir "$TD" || { echo "STOP: libcopy"; rm -f -- "$SELF"; exit 9; }
finish() { echo "ref-c2c1 preconditions rc=$1"; date -u +%FT%TZ; echo "$1" > "$P/check.done"; rm -f -- "$SELF"; exit "$1"; }
echo "node $(hostname) nproc=$(nproc) loadavg $(cut -d' ' -f1-3 /proc/loadavg)"
date -u +%FT%TZ
echo "check script sha256 $(sha256sum "$SELF" | cut -d' ' -f1)"
cp "$SELF" "$P/refc2c1_pre_login.sh"

git clone -q https://github.com/josephbaileyy/MINERvA-OmniFold.git "$D" > "$P/clone.log" 2>&1 || { echo "STOP: clone"; finish 3; }
git -C "$D" -c advice.detachedHead=false checkout -q "$G" || { echo "STOP: checkout"; finish 3; }
[ "$(git -C "$D" rev-parse HEAD)" = "$G" ] || { echo "STOP: HEAD is not G"; finish 9; }
n=$(git -C "$D" status --porcelain --ignored | wc -l); echo "HEAD $G; porcelain --ignored lines: $n"
[ "$n" -eq 0 ] || { echo "STOP: the deploy is not clean"; finish 9; }
R2=docs/orchestration/state/2d-closeout/stageF/methods/re2/run
F=docs/orchestration/state/measurement-paper/5d-community-20261024
bad=0
while read -r b p; do
  [ "$(git -C "$D" rev-parse "$G:$p")" = "$b" ] && { [ -d "$D/$p" ] || [ "$(git -C "$D" hash-object "$p")" = "$b" ]; } || { echo "MISMATCH $p"; bad=$((bad + 1)); }
done <<BLOBS
58053bb064d3cf88c4b6642953f03c8cafd64e4f $R2/partb_runs.tsv
59d5066dc2d1740979fc9d4bbda11c83cc4b66d0 $R2/launch/re2_env.sh
0ba4b1d47408055b5c118f5d332cf4d5e63a7198 $R2/partb_readout/sums
d93da87ef8d9c5ba90e611f49a4982c9107b7a92 nd-unfolding/pv-ladder/prep-SHA256SUMS
e4c530b25afda48e0036de24416cea43e467dc45 nd-unfolding/fd_f0_regrade.py
1542ed946f701bff62ec6fe8c08cdc7c2424c599 nd-unfolding/s1_assemble.py
537644aa9f9306f7fbce0cac703aaa35325389ef $F/REF-C2C1-DECLARATION.md
e3a2812a7856391840bc84dfbffa98e33672f0ae $F/REF-C2C1-BINDING-1.md
BLOBS
echo "committed pins: 8 checked, $bad mismatches"
[ "$bad" -eq 0 ] || { echo "STOP: the committed pins are not the bound ones"; finish 9; }

echo "== libRooUnfold build directory"; ls -la "$LIBDIR" 2>&1 | tee "$P/librooUnfold-ls.txt" | head -40
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 NUMEXPR_NUM_THREADS=1 PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
echo "threads: OMP=$OMP_NUM_THREADS OPENBLAS=$OPENBLAS_NUM_THREADS MKL=$MKL_NUM_THREADS NUMEXPR=$NUMEXPR_NUM_THREADS; nice 19; ionice idle"
(
  eval "$(/global/common/software/nersc/pe/conda/24.10.0/Miniforge3-24.7.1-0/bin/conda shell.bash hook)"
  conda activate "$HOME/.conda/envs/root_6_28" || { echo "STOP: activation failed"; exit 2; }
  nice -n 19 ionice -c3 env -u PYTHONPATH python3 -I -B - "$D" "$G" "$A" "$LIBDIR" "$TD" "$P/listing.json" <<'PYEOF'
import hashlib, json, os, re, shutil, socket, sys, time
from pathlib import Path
D, G, A, LIBDIR, TD, OUT = Path(sys.argv[1]), sys.argv[2], Path(sys.argv[3]), Path(sys.argv[4]), Path(sys.argv[5]), Path(sys.argv[6])
sys.path.insert(0, str(D / "nd-unfolding"))
import s1_assemble as sa     # noqa: E402
import fd_f0_regrade as f0   # noqa: E402
B = Path("/pscratch/sd/j/josephrb/2d-closeout-re2-20261023/partb")
R2 = D / "docs/orchestration/state/2d-closeout/stageF/methods/re2/run"


def noatime(p, copy_to=None):
    st = os.stat(p)
    fd = os.open(p, os.O_RDONLY | os.O_NOATIME)
    h, n = hashlib.sha256(), 0
    out = open(copy_to, "wb") if copy_to else None
    with os.fdopen(fd, "rb") as f:
        for b in iter(lambda: f.read(1 << 24), b""):
            h.update(b); n += len(b)
            if out:
                out.write(b)
    if out:
        out.close()
    return h.hexdigest(), n, st.st_atime, st.st_mtime


groups, ok = {}, True


def check(group, path, pin, source, extra=None):
    global ok
    path = Path(path)
    if not path.is_file():
        r = {"path": str(path), "pin": pin, "pin_source": source, "present": False, "ok": False}
    else:
        got, n, at, mt = noatime(path)
        r = {"path": str(path), "sha256": got, "pin": pin, "pin_source": source, "bytes": n, "present": True,
             "atime": at, "atime_utc": time.strftime("%FT%TZ", time.gmtime(at)), "mtime": mt,
             "ok": got == pin if pin else True}
    r |= extra or {}
    groups.setdefault(group, []).append(r)
    ok &= r["ok"]


env = (R2 / "launch/re2_env.sh").read_text()
var = lambda k: re.search(rf"^(?:export )?{k}=(\S+)", env, re.M).group(1)  # noqa: E731
CV_SHA, MC_SHA, FLUXU_SHA = var("CV_SHA"), var("MC_SHA"), var("FLUXU_SHA")
CFS_CV = Path(var("CV"))
MC, FLUXU = Path(var("MC").replace("$A", str(A))), Path(var("FLUXU").replace("$A", str(A)))
sums = {}
for f in sorted((R2 / "partb_readout/sums").glob("SHA256SUMS.J*")):
    for line in f.read_text().splitlines():
        if line.strip():
            h, p = line.split(None, 1)
            sums[p.strip()] = (h, f.name)
# 3. the library, loaded from an O_NOATIME copy
lib = {"dir": str(LIBDIR), "files": []}
for p in sorted(LIBDIR.glob("libRooUnfold*")) if LIBDIR.is_dir() else []:
    if p.is_file() and (p.suffix in (".so", ".pcm", ".rootmap") or ".so" in p.name):
        got, n, at, mt = noatime(p, TD / p.name)
        lib["files"].append({"name": p.name, "sha256": got, "bytes": n, "atime_utc": time.strftime("%FT%TZ", time.gmtime(at))})
so = TD / "libRooUnfold.so"
lib["present"] = so.is_file()
if so.is_file():
    os.environ["LD_LIBRARY_PATH"] = f"{TD}:{os.environ.get('LD_LIBRARY_PATH', '')}"
    import ROOT
    ROOT.gROOT.SetBatch(True)
    rc = int(ROOT.gSystem.Load(str(so)))
    cls = ROOT.TClass.GetClass("RooUnfoldBayes")
    lib |= {"gSystem_Load_rc": rc, "RooUnfoldBayes_class": bool(cls) and bool(cls.HasDictionary()),
            "root_version": ROOT.gROOT.GetVersion()}
    lib["loads"] = rc >= 0 and lib["RooUnfoldBayes_class"]
else:
    lib["loads"] = False
ok &= lib["loads"]
# 4. E_R: central product, inputs, refinement evidence; Q_R's 300 replicas with their seeds
check("E_R_central", B / "out/ER/xsec.root", sums.get("ER/xsec.root", (None,))[0], "re2 partb SHA256SUMS.J1.1")
check("E_R_inputs", CFS_CV, CV_SHA, "re2_env.sh CV_SHA (CFS $CV)")
check("E_R_inputs", B / "inputs/runEventLoopOmniFold_MEFHC.root", CV_SHA, "re2_env.sh CV_SHA (the staged copy part B read)")
check("E_R_inputs", MC, MC_SHA, "re2_env.sh MC_SHA (baseline flux)")
check("E_R_refinement_evidence", B / "logs/ER.log", None, "the run log (unpinned); aggregates: re2Refinement in the product; health row: partb_readout/k1_core.json")
runs = [l.split("\t") for l in (R2 / "partb_runs.tsv").read_text().splitlines()[1:] if l.strip()]
seeds = {}
for c in runs:
    if re.fullmatch(r"S1_\d{3}", c[2]):
        m = re.search(r"--bootstrap-seed (\d+)", c[5])
        seeds[c[2]] = int(m.group(1)) if m else None
seeds_ok = sorted(seeds) == [f"S1_{i:03d}" for i in range(1, 301)] and all(seeds[f"S1_{i:03d}"] == i for i in range(1, 301))
ok &= seeds_ok
for lab in sorted(seeds):
    h, src = sums.get(f"{lab}/xsec.root", (None, None))
    check("Q_R_replicas", B / f"out/{lab}/xsec.root", h, f"re2 partb {src}", {"label": lab, "bootstrap_seed": seeds[lab]})
# REF-G1 follow-up
PVL = Path("/pscratch/sd/j/josephrb/pv-ladder-20261024")
prep = {l.split(None, 1)[1].strip().lstrip("./"): l.split(None, 1)[0] for l in (D / "nd-unfolding/pv-ladder/prep-SHA256SUMS").read_text().splitlines() if l.strip()}
check("ref_g1_followup", PVL / "prep/ratios/L-5D-PV/tune_v1.json", prep.get("ratios/L-5D-PV/tune_v1.json"), "pv-ladder prep-SHA256SUMS",
      {"equals_fd_f0_regrade_RATIO_floor": prep.get("ratios/L-5D-PV/tune_v1.json") == f0.RATIO["floor"]})
check("ref_g1_followup", Path("/pscratch/sd/j/josephrb/s1-20261024/s1_assembly.npz"), f0.PINS["s1_npz"], "fd_f0_regrade.PINS['s1_npz']")
check("ref_g1_followup", FLUXU, FLUXU_SHA, "re2_env.sh FLUXU_SHA")
check("ref_g1_followup", A / "MINERvA101/opt/etc/MParamFiles/data/FluxConstraints/sorted_NuEConstraint_FHC_RHC_IMD.txt",
      sa.CONSTRAINT_SHA256, "s1_assemble.CONSTRAINT_SHA256")
ok &= groups["ref_g1_followup"][0].get("equals_fd_f0_regrade_RATIO_floor", False)
summary = {g: {"files": len(rs), "present": sum(r["present"] for r in rs), "equal_to_pin": sum(r["ok"] for r in rs),
               "oldest_atime_utc": min((r["atime_utc"] for r in rs if r["present"]), default=None),
               "exposed_from_utc": min((time.strftime("%FT%TZ", time.gmtime(r["atime"] + 56 * 86400)) for r in rs if r["present"]), default=None)}
           for g, rs in groups.items()}
rec = {"schema": "ref-c2c1-preconditions/1", "G": G, "host": socket.gethostname(), "universe_pass": False,
       "rule": "every read O_NOATIME; atime and mtime from os.stat before the read; the library loaded from an O_NOATIME copy",
       "library": lib, "seeds_1_to_300": seeds_ok, "summary": summary, "files": groups,
       "verdict": "PASS" if ok else "FAIL", "written_utc": time.strftime("%FT%TZ", time.gmtime())}
OUT.write_text(json.dumps(rec, indent=1, sort_keys=True) + "\n")
print(f"library: present {lib['present']}, loads {lib['loads']}, Load rc {lib.get('gSystem_Load_rc')}, RooUnfoldBayes {lib.get('RooUnfoldBayes_class')}, ROOT {lib.get('root_version')}; files {[(f['name'], f['sha256'][:8]) for f in lib['files']]}")
for g, s in summary.items():
    print(f"{g}: {s['files']} files, {s['present']} present, {s['equal_to_pin']} equal to pin, oldest atime {s['oldest_atime_utc']}, exposed from {s['exposed_from_utc']}")
print(f"seeds 1..300: {seeds_ok}")
for g, rs in groups.items():
    for r in rs:
        if not r["ok"]:
            print(f"  {'MISSING' if not r['present'] else 'DIFFERS'} {g} {r['path']}")
print(json.dumps({"verdict": rec["verdict"], "wrote": str(OUT), "sha256": hashlib.sha256(OUT.read_bytes()).hexdigest()}))
sys.exit(0 if ok else 1)
PYEOF
)
rc=$?
echo "listing python rc=$rc"
n=$(git -C "$D" status --porcelain --ignored | wc -l); echo "porcelain --ignored lines after: $n"
[ "$n" -eq 0 ] || { echo "STOP: the deploy changed"; finish 9; }
[ $rc = 0 ] || { echo "STOP: a file is missing or differs, or the library does not load (final; to the director)"; finish 4; }
finish 0

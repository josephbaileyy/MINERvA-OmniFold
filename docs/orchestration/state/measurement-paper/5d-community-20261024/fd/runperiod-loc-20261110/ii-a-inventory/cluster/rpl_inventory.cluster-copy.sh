#!/bin/bash
# RPL (ii-a) step 1, the inventory (fd/runperiod-loc-20261110/RPL-DECLARATION.md, (ii-a) row 1; bound by the
# director at #1042's merge). One Perlmutter login node, foreground, 0 node-h, nice 19, threads 1.
# For each of MP-1's 12 zero loops (fd_ct_period_inputs.py ZERO_LOOPS): stat the explicit path; copy it to /dev/shm
# with O_NOATIME, hashing the bytes read, and STOP on a digest that is not the pin (stat before and after must be
# equal); open the copy with ROOT; record every TTree's name, entries and branch names; and for the key branches only
# (data: ev_run, ev_subrun, ev_gate; MC: mc_run, mc_subrun, mc_nthEvtInFile; any slice or physics-event index), read
# their values and count rows, distinct keys and duplicates. No physics column is read, and no data/MC quantity is
# formed. The copy is deleted after each file. Writes only under $OUT and /dev/shm/josephrb-rpl-inv; refuses if $OUT
# exists. python3 -B, not -I: ROOT's bindings need the environment's PYTHONPATH; the inputs are our own pinned
# products, and the interpreter runs from the empty work directory. No set -u (it kills setup_salloc_env.sh). Launched from a /dev/shm copy of itself, whose path is $1.
SELF=$1
OUT=/pscratch/sd/j/josephrb/rpl-inv-20261110
Z=/pscratch/sd/j/josephrb/measurement-paper/phase1/mp1/s1/evloop/zero
A=/pscratch/sd/j/josephrb/MINERvA-OmniFold   # the shared checkout with setup_salloc_env.sh (root_6_28)
W=/dev/shm/josephrb-rpl-inv
bail() { rm -f -- "$SELF"; exit 9; }
[ ! -e "$OUT" ] || bail
[ ! -e "$W" ] || bail
q=$(squeue --me -h -o '%i|%j|%T') || bail
printf '%s\n' "$q" | awk -F'|' '$2 ~ /^(cov2d|t2a)/ {f=1} END {exit !f}' && bail
mkdir -p "$OUT/logs" "$W" || bail
exec > "$OUT/logs/inventory.log" 2>&1
finish() { rm -rf -- "$W"; echo "removal of $W rc=$? ; present after: $([ -e "$W" ] && echo yes || echo no)"; echo "rpl inventory rc=$1 $(date -u +%FT%TZ)"; echo "$1" > "$OUT/logs/inventory.done"; rm -f -- "$SELF"; exit "$1"; }
echo "node $(hostname) loadavg $(cut -d' ' -f1-3 /proc/loadavg) start=$(date -u +%FT%TZ)"
echo "script sha256 $(sha256sum "$SELF" | cut -d' ' -f1)"; cp "$SELF" "$OUT/logs/rpl_inventory.sh"
echo "squeue --me:"; printf '%s\n' "$q" | sed '/^$/d; s/^/  /'
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 NUMEXPR_NUM_THREADS=1 PYTHONDONTWRITEBYTECODE=1 TMPDIR=$W
source "$A/setup_salloc_env.sh" > "$OUT/logs/env.log" 2>&1
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 NUMEXPR_NUM_THREADS=1 PYTHONDONTWRITEBYTECODE=1 TMPDIR=$W
echo "python=$(command -v python3)"
cd "$W" || finish 9   # an empty work directory, so no cwd module can be imported
nice -n 19 python3 -B - "$Z" "$W" "$OUT/inventory.json" <<'PY'
import hashlib, json, os, sys
Z, W, OUT = sys.argv[1:4]
PINS = {
    "1A": "2745e38c45a50fa644e32913c6d8bc9763edc96e21b6d058cde4dbee6714c192",
    "1B": "a2b7e413f8ab727577eb70cf00881c9dedfaf3401c18e37c866f6dc296639948",
    "1C": "7985c0f1ae44d99be3bf180748c9553672bc8f107b512310c961d728d9c62d34",
    "1D": "52da8f2245be7f4529d6c24960fa56f3063db5368bf33e7640604d716742797d",
    "1E": "7f9293a6ce7a0aee7e9549b93d86b4d201bb0db9da088bace988403a7a0faea5",
    "1F": "7481c94751a5df774e1c18cd453e92322d789d5568785ed8c026f6ef15778b4e",
    "1G": "259aa1952e7586eb2f301ec7960f3003d4b995f7f59b36b32a68b47a31ca2821",
    "1L": "d2b4dafc61d1756554d1c7ff3085410faaa2266cd14a260175bc0e533fe2030c",
    "1M": "f80bb016e78701dde9faf5faf53d0d906430525abaafa753c1a051e2f860cb45",
    "1N": "9e9875ec37cd3354650d0c27a042389d86408f0ded08389f1c2ff38ca49e219c",
    "1O": "22064448cb42b960e8066882ce6a3dc0fc8a5650eb1fb70f82626222708e6237",
    "1P": "5efe83f95e9822ff0dbf0780668e187d4857fd97aade631ae6ba19bf917123a1",
}  # nd-unfolding/fd_ct_period_inputs.py ZERO_LOOPS
DATA_KEY = ("ev_run", "ev_subrun", "ev_gate")
MC_KEY = ("mc_run", "mc_subrun", "mc_nthEvtInFile")
INDEX = ("physEvtNum", "slice_numbers", "n_slices", "ev_slice", "slice", "mc_nthEvtInSpill")
import numpy as np
import ROOT
rec = {"schema": "rpl-inventory/1", "files": {}, "stop": []}
for pl, pin in PINS.items():
    src = f"{Z}/runEventLoopOmniFold_5D_{pl}_zero.root"
    r = {"path": src}
    try:
        s0 = os.stat(src)
    except OSError as e:
        r["error"] = str(e); rec["files"][pl] = r; rec["stop"].append(f"{pl}: missing"); continue
    dst = f"{W}/{pl}.root"
    h = hashlib.sha256()
    fi = os.open(src, os.O_RDONLY | os.O_NOATIME)
    with open(dst, "wb") as fo:
        while True:
            b = os.read(fi, 1 << 24)
            if not b:
                break
            h.update(b); fo.write(b)
    os.close(fi)
    s1 = os.stat(src)
    r.update(bytes=s0.st_size, sha256=h.hexdigest(), pin_ok=h.hexdigest() == pin,
             stat_unchanged=(s0.st_size, s0.st_mtime_ns, s0.st_atime_ns) == (s1.st_size, s1.st_mtime_ns, s1.st_atime_ns),
             atime_ns=s0.st_atime_ns)
    if not r["pin_ok"] or not r["stat_unchanged"]:
        rec["stop"].append(f"{pl}: pin {r['pin_ok']}, stat unchanged {r['stat_unchanged']}")
        os.remove(dst); rec["files"][pl] = r; continue
    f = ROOT.TFile.Open(dst)
    trees = {}
    for k in f.GetListOfKeys():
        o = k.ReadObj()
        if not o.InheritsFrom("TTree"):
            continue
        names = [b.GetName() for b in o.GetListOfBranches()]
        t = {"entries": int(o.GetEntries()), "n_branches": len(names), "branches": names}
        for key in (DATA_KEY, MC_KEY):
            if all(n in names for n in key):
                cols = ROOT.RDataFrame(o.GetName(), dst).AsNumpy(list(key))
                arr = np.stack([np.asarray(cols[n]).astype(np.int64) for n in key], axis=1)
                u, cnt = np.unique(arr, axis=0, return_counts=True)
                t[f"key_{'_'.join(key)}"] = {"rows": int(arr.shape[0]), "distinct": int(u.shape[0]),
                                            "rows_in_duplicated_keys": int(cnt[cnt > 1].sum()),
                                            "max_multiplicity": int(cnt.max()) if cnt.size else 0}
        t["index_branches"] = [n for n in names if n in INDEX]
        trees[o.GetName()] = t
    f.Close()
    os.remove(dst)
    r["trees"] = trees
    rec["files"][pl] = r
    print(pl, "ok", {n: (t["entries"], [k for k in t if k.startswith("key_")], t["index_branches"]) for n, t in trees.items()}, flush=True)
json.dump(rec, open(OUT, "w"), indent=1)
print("INVENTORY", "STOP" if rec["stop"] else "OK", rec["stop"])
sys.exit(8 if rec["stop"] else 0)
PY
rc=$?
(cd "$OUT" && sha256sum inventory.json logs/inventory.log 2>/dev/null)
(cd "$OUT" && tar czf post.tar.gz inventory.json logs/rpl_inventory.sh logs/env.log 2>/dev/null; sha256sum post.tar.gz)
finish $rc

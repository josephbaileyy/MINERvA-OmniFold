#!/bin/bash
# RPL check (i), the band's size (fd/runperiod-loc-20261110/RPL-DECLARATION.md, (i) comparator; the director's approval
# in principle, 2026-11-10). One Perlmutter login node, foreground, 0 node-h, nice 19, threads 1. MC only: no data
# column is read, and nothing is compared with data (limitation-resolver's condition, kept until P-RPD).
# For each of the 12 per-playlist universe files runEventLoopOmniFold_<PL>_universes_full.root (not COV2D inputs, the
# cov2d session confirmed, 2026-11-10):
#   stat the explicit path; open it with os.open(O_RDONLY | O_NOATIME) (EPERM is raised and never retried plainly);
#   hand that file object to uproot, which reads through it and nothing else; read ONLY the named branches of the
#   first 500,000 mc_signal_reco entries in file order: sim, sim_pz, sim_pass, w_reco and the shifted reco kinematics
#   sim_<band>_<i>, sim_pz_<band>_<i> for band in Muon_Energy_MINOS, Muon_Energy_MINERvA and i = 0, 1;
#   stat again: size, mtime and atime must be unchanged.
# Per row: p = sqrt(sim^2 + sim_pz^2) (GeV/c), r_i = |p_i / p - 1|. sigma_band is the w_reco-weighted median of r over
# sim_pass rows with finite, positive p, pooled over both endpoints and all 12 playlists (the deciding value); the
# per-endpoint, per-playlist and p_par < 8 / >= 8 values are descriptive. Writes only under $OUT; refuses if it exists.
# If no login environment has uproot, it exits 4 (NO-UPROOT) before opening any input: no plain-read fallback.
# Launched from a /dev/shm copy of itself, whose path is $1; it deletes that copy at exit.
SELF=$1
OUT=/pscratch/sd/j/josephrb/rpl-band-20261110
U=/pscratch/sd/j/josephrb/MINERvA-OmniFold/2d-unfolding
bail() { rm -f -- "$SELF"; exit 9; }
[ ! -e "$OUT" ] || bail
q=$(squeue --me -h -o '%i|%j|%T') || bail
printf '%s\n' "$q" | awk -F'|' '$2 ~ /^(cov2d|t2a)/ {f=1} END {exit !f}' && bail
mkdir -p "$OUT/logs" || bail
exec > "$OUT/logs/bandsize.log" 2>&1
finish() { echo "rpl bandsize rc=$1 $(date -u +%FT%TZ)"; echo "$1" > "$OUT/logs/bandsize.done"; rm -f -- "$SELF"; exit "$1"; }
echo "node $(hostname) loadavg $(cut -d' ' -f1-3 /proc/loadavg) start=$(date -u +%FT%TZ)"
echo "script sha256 $(sha256sum "$SELF" | cut -d' ' -f1)"; cp "$SELF" "$OUT/logs/rpl_bandsize.sh"
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 NUMEXPR_NUM_THREADS=1 PYTHONDONTWRITEBYTECODE=1
PY=""
for cand in /global/homes/j/josephrb/.conda/envs/omnifold_py310/bin/python /global/homes/j/josephrb/.conda/envs/root_6_28/bin/python3; do
  if [ -x "$cand" ] && "$cand" -I -c "import uproot, numpy" 2>/dev/null; then PY=$cand; break; fi
done
[ -n "$PY" ] || { echo "NO-UPROOT: no login environment imports uproot; nothing opened"; finish 4; }
echo "python=$PY $("$PY" -I -c 'import sys, uproot, numpy; print(sys.version.split()[0], "uproot", uproot.__version__, "numpy", numpy.__version__)')"
mkdir -p "$OUT/work" && cd "$OUT/work" || finish 9
nice -n 19 "$PY" -I - "$U" "$OUT/band.json" <<'PY'
import json, os, sys
import numpy as np
import uproot
U, OUT = sys.argv[1:3]
PLS = ["1A", "1B", "1C", "1D", "1E", "1F", "1G", "1L", "1M", "1N", "1O", "1P"]
BANDS = ("Muon_Energy_MINOS", "Muon_Energy_MINERvA")
N_ROWS = 500_000
names = ["sim", "sim_pz", "sim_pass", "w_reco"] + [f"{p}{b}_{i}" for b in BANDS for i in (0, 1) for p in ("sim_", "sim_pz_")]


def wmedian(x, w):
    o = np.argsort(x)
    x, w = x[o], w[o]
    c = np.cumsum(w)
    return float(x[np.searchsorted(c, 0.5 * c[-1])]) if c.size and c[-1] > 0 else None


rec = {"schema": "rpl-bandsize/1", "n_rows_per_playlist": N_ROWS, "rows": "the first entries of mc_signal_reco, in file order",
       "uproot": uproot.__version__, "numpy": np.__version__, "files": {}, "stop": []}
pool = {b: {"r": [], "w": [], "pz": []} for b in BANDS}
for pl in PLS:
    path = f"{U}/runEventLoopOmniFold_{pl}_universes_full.root"
    s0 = os.stat(path)
    fd = os.open(path, os.O_RDONLY | os.O_NOATIME)          # EPERM raises here; there is no plain retry
    with os.fdopen(fd, "rb") as fobj:
        with uproot.open(fobj) as f:
            t = f["mc_signal_reco"]
            missing = [n for n in names if n not in t.keys()]
            if missing:
                rec["stop"].append(f"{pl}: missing branches {missing}")
                continue
            a = t.arrays(names, entry_stop=N_ROWS, library="np")
    s1 = os.stat(path)
    same = (s0.st_size, s0.st_mtime_ns, s0.st_atime_ns) == (s1.st_size, s1.st_mtime_ns, s1.st_atime_ns)
    fr = {"path": path, "bytes": s0.st_size, "atime_ns": s0.st_atime_ns, "stat_unchanged": same, "rows_read": int(a["sim"].size)}
    if not same:
        rec["stop"].append(f"{pl}: stat changed")
    p = np.hypot(np.asarray(a["sim"], float), np.asarray(a["sim_pz"], float))
    w = np.asarray(a["w_reco"], float)
    base = (np.asarray(a["sim_pass"]).astype(bool)) & np.isfinite(p) & (p > 0) & np.isfinite(w)
    for b in BANDS:
        rs = []
        for i in (0, 1):
            pi = np.hypot(np.asarray(a[f"sim_{b}_{i}"], float), np.asarray(a[f"sim_pz_{b}_{i}"], float))
            ok = base & np.isfinite(pi)
            r = np.abs(pi[ok] / p[ok] - 1.0)
            fr[f"{b}_{i}_median"] = wmedian(r, w[ok])
            rs.append((r, w[ok], np.asarray(a["sim_pz"], float)[ok]))
        r = np.concatenate([x[0] for x in rs]); ww = np.concatenate([x[1] for x in rs]); pz = np.concatenate([x[2] for x in rs])
        fr[f"{b}_median"] = wmedian(r, ww)
        pool[b]["r"].append(r); pool[b]["w"].append(ww); pool[b]["pz"].append(pz)
    rec["files"][pl] = fr
    print(pl, "ok", fr.get("Muon_Energy_MINOS_median"), fr.get("Muon_Energy_MINERvA_median"), "stat_unchanged", same, flush=True)
rec["sigma_band"] = {}
for b in BANDS:
    if not pool[b]["r"]:
        continue
    r, w, pz = (np.concatenate(pool[b][k]) for k in ("r", "w", "pz"))
    rec["sigma_band"][b] = {"overall": wmedian(r, w), "p_par_lt_8": wmedian(r[pz < 8], w[pz < 8]),
                            "p_par_ge_8": wmedian(r[pz >= 8], w[pz >= 8]), "rows": int(r.size),
                            "role": "deciding (overall)" if b == "Muon_Energy_MINOS" else "descriptive only"}
json.dump(rec, open(OUT, "w"), indent=1)
print("BANDSIZE", "STOP" if rec["stop"] else "OK", rec["stop"])
sys.exit(8 if rec["stop"] else 0)
PY
rc=$?
cd "$OUT" && rmdir work 2>/dev/null
(cd "$OUT" && sha256sum band.json 2>/dev/null; tar czf post.tar.gz band.json logs/rpl_bandsize.sh 2>/dev/null; sha256sum post.tar.gz)
finish $rc

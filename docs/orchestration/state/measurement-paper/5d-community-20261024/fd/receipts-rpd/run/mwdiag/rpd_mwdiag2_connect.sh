#!/bin/bash
# RPD: a DESCRIPTIVE diagnostic of C1's measured_weights disagreement in 1A and 1M (the director, 2026-11-04; part 2's
# deviation 1), second run. The first (rpd_mwdiag_connect.sh, a69faa5c) stopped at 11:21:33Z with mw_diag rc=1: its
# loader read every npz key with allow_pickle=False and a dump holds an object array. This one reads only the keys the
# diagnostic uses, still allow_pickle=False, and writes under new names (deploy-9, diag-2, mwdiag-2.*).
# The first run's header follows, with its paths moved:
# deviation 1). It changes no record and enters no rule. 0 node-h, no job: login node, threads 1, nice 19. A fresh clone
# at M' into $R/deploy-9 (its 23 section 7 blobs), verify-staged, then mw_diag.py (embedded below, written to
# $R/diag-2/mw_diag.py and kept) over $R/dumps/lat_{1A,1M}.npz and their _bkg, read through O_NOATIME, writing only
# $R/diag-2/mw_1A_1M.json. Runs only after job B ended. Writes only under $R. No set -u. Launched from a /dev/shm copy of
# itself (its path is $1), which it deletes at exit.
SELF=$1
R=/pscratch/sd/j/josephrb/fd-rpd-20261103
M=8727c63e1d32599039ea977d833c5de25a9089d6
D=$R/deploy-9
LOG=$R/logs/mwdiag-2.log
bail() { rm -f -- "$SELF"; exit 9; }
[ -d "$R/logs" ] && [ -d "$R/tmp" ] && [ -d "$R/receipts" ] && [ ! -e "$D" ] && [ ! -e "$LOG" ] && [ ! -e "$R/diag-2" ] || bail
[ "$(dd if="$R/logs/mwdiag.done" iflag=noatime status=none)" = 1 ] || bail   # the first run stopped
job=$(dd if="$R/logs/jobB.jobid" iflag=noatime status=none)
case "$(sacct -j "$job" -X -n -P -o State | head -1)" in PENDING|RUNNING|REQUEUED|"") bail ;; esac    # job B has ended
for X in 1A 1M; do [ -e "$R/dumps/lat_$X.npz" ] && [ -e "$R/dumps/lat_${X}_bkg.npz" ] || bail; done
mkdir "$R/diag-2" || bail
exec > "$LOG" 2>&1
finish() { echo "mwdiag rc=$1"; date -u +%FT%TZ; echo "$1" > "$R/logs/mwdiag-2.done"; rm -f -- "$SELF"; exit "$1"; }
echo "node $(hostname) nproc=$(nproc) loadavg $(cut -d' ' -f1-3 /proc/loadavg)"
date -u +%FT%TZ
echo "connect script sha256 $(sha256sum "$SELF" | cut -d' ' -f1)"
echo "job B $job: $(sacct -j "$job" -X -n -P -o JobID,State,ExitCode,Elapsed | head -1)"
cp "$SELF" "$R/receipts/rpd_mwdiag2_connect.sh"
git clone -q https://github.com/josephbaileyy/MINERvA-OmniFold.git "$D" > "$R/logs/clone-9.log" 2>&1 || { echo "STOP: clone"; finish 3; }
git -C "$D" -c advice.detachedHead=false checkout -q "$M" || { echo "STOP: checkout"; finish 3; }
[ "$(git -C "$D" rev-parse HEAD)" = "$M" ] || { echo "STOP: HEAD is not M'"; finish 9; }
n=$(git -C "$D" status --porcelain --ignored | wc -l); echo "HEAD $M; porcelain --ignored lines before: $n"
[ "$n" -eq 0 ] || { echo "STOP: the deploy is not clean"; finish 9; }
DECL=docs/orchestration/state/measurement-paper/5d-community-20261024/FD-RPD-DECLARATION-PART2.md
rows=0; bad=0
while read -r p b; do
  rows=$((rows + 1))
  [ "$(git -C "$D" rev-parse "$M:$p")" = "$b" ] && [ "$(git -C "$D" hash-object "$p")" = "$b" ] || { echo "MISMATCH $p"; bad=$((bad + 1)); }
done < <(sed -n '/^## 7\./,/^## 8\./p' "$D/$DECL" | sed -n 's/^| `\([^`]*\)` | `\([0-9a-f]\{40\}\)` |$/\1 \2/p')
echo "section 7: $rows blobs, $bad mismatches"
[ "$rows" -eq 23 ] && [ "$bad" -eq 0 ] || { echo "STOP: section 7 blobs"; finish 9; }
eval "$(/global/common/software/nersc/pe/conda/24.10.0/Miniforge3-24.7.1-0/bin/conda shell.bash hook)"
conda activate "$HOME/.conda/envs/root_6_28" || { echo "STOP: activation failed"; finish 2; }
export TMPDIR="$R/tmp" PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 NUMEXPR_NUM_THREADS=1
echo "threads: OMP=$OMP_NUM_THREADS OPENBLAS=$OPENBLAS_NUM_THREADS MKL=$MKL_NUM_THREADS NUMEXPR=$NUMEXPR_NUM_THREADS; nice 19"
PY=(nice -n 19 env -u PYTHONPATH "$HOME/.conda/envs/root_6_28/bin/python3" -I -B)
cd "$R" || finish 9
"${PY[@]}" "$D/nd-unfolding/fd_rpd_inputs.py" verify-staged --r "$R" --deploy "$D" > "$R/logs/verify-staged-9.out" 2>&1
rc=$?; echo "verify-staged rc=$rc"; tail -2 "$R/logs/verify-staged-9.out"
[ $rc = 0 ] || { echo "STOP at verify-staged (final)"; finish $rc; }
cat > "$R/diag-2/mw_diag.py" <<'PYEOF'
"""DESCRIPTIVE diagnostic of C1's measured_weights disagreement for 1A and 1M (the director, 2026-11-04; part 2's
deviation 1). It changes no record and enters no rule.

For each playlist X it recomputes measured_weights exactly as fd_rpd.measured_weights_agreement does (the deploy's own
function body, re-run here to keep the per-row mask), then reports:
  (a) the rows whose stored weight differs from the recomputation (np.isclose, rtol 1e-12, atol 0);
  (b) for each differing row, whether any coordinate lies within one float32 ulp of an analysis bin edge, or exactly
      on an axis's last edge (np.histogramdd counts it in the last bin, np.digitize - 1 puts it outside);
  (c) every differing row that is neither, listed;
and a per-bin cross-check. In a bin with 0 < w < 1 the stored weight inverts to the bin's original data count,
D0 = B / (1 - w0), where w0 is the bin's modal stored weight. delta = D_recomputed - D0 should be a small integer that
the near-edge rows in or next to the bin can supply. Bins where it is not are listed.

Usage: python3 -I -B mw_diag.py <deploy> <R> <out.json> [X ...]   (reads <R> through the deploy's readers; O_NOATIME
for the two npz per playlist; writes only <out.json>)
"""
import json
import os
import sys
from pathlib import Path

import numpy as np

DEPLOY, R, OUT = Path(sys.argv[1]), Path(sys.argv[2]), Path(sys.argv[3])
PLS = sys.argv[4:] or ["1A", "1M"]
sys.path.insert(0, str(DEPLOY / "nd-unfolding"))
import fd_rpd as rp  # noqa: E402
import fd_rpd_inputs as ri  # noqa: E402


LAT_KEYS = ("measured", "measured_weights", "nedges")
BKG_KEYS = ("bkg_nd",)


def load_noatime(p: Path, keys) -> dict:
    """Only `keys` (and, with "nedges", the edges_i it names): the dumps also hold object arrays (fd_rpd.load_all
    reads them with allow_pickle=True), and an NpzFile parses only the members accessed, so none is unpickled."""
    fd = os.open(p, os.O_RDONLY | os.O_NOATIME)
    with os.fdopen(fd, "rb") as f, np.load(f, allow_pickle=False) as z:
        out = {k: z[k] for k in keys}
        if "nedges" in out:
            out |= {f"edges_{i}": z[f"edges_{i}"] for i in range(int(out["nedges"]))}
        return out


def recompute(z, b, edges):
    """fd_rpd.measured_weights_agreement's body at M', returning the per-row pieces."""
    meas = np.asarray(z["measured"], float)
    data_nd = ri.histnd_counts([meas[:, i] for i in range(meas.shape[1])], np.ones(len(meas)), edges)
    bkg_nd = np.asarray(b["bkg_nd"], float)
    target = np.maximum(0.0, data_nd - bkg_nd)
    idx = [np.digitize(meas[:, i], e) - 1 for i, e in enumerate(edges)]
    inside = np.all([(ix >= 0) & (ix < len(e) - 1) for ix, e in zip(idx, edges)], axis=0)
    w = np.zeros(len(meas))
    ii = tuple(np.clip(ix, 0, len(e) - 2) for ix, e in zip(idx, edges))
    d = data_nd[ii]
    ok = inside & (d > 0)
    w[ok] = target[ii][ok] / d[ok]
    return meas, data_nd, bkg_nd, idx, inside, ii, w


def diagnose(z, b) -> dict:
    edges = [np.asarray(z[f"edges_{i}"], float) for i in range(int(z["nedges"]))]
    meas, data_nd, bkg_nd, idx, inside, ii, w = recompute(z, b, edges)
    got = np.asarray(z["measured_weights"], float)
    same = np.isclose(got, w, rtol=1e-12, atol=0.0)
    diff = ~same
    n, nd = len(got), int(diff.sum())
    # (b) per row: within one float32 ulp of an edge in some coordinate; exactly on an axis's last edge
    near = np.zeros(n, bool)
    near_axis = np.full(n, -1)
    alt = [ix.copy() for ix in ii]
    on_last = np.zeros(n, bool)
    for i, e in enumerate(edges):
        v = meas[:, i]
        ulp = np.spacing(np.abs(v).astype(np.float32)).astype(float)
        k = np.clip(np.searchsorted(e, v), 1, len(e) - 1)
        lo, hi = e[k - 1], e[k]
        en = np.where(np.abs(v - lo) <= np.abs(v - hi), lo, hi)
        ni = np.abs(v - en) <= ulp
        new = ni & ~near
        near_axis[new] = i
        # the bin the row would fall in from the edge's other side
        a = np.where(v >= en, ii[i] - 1, ii[i] + 1)
        alt[i] = np.where(new, np.clip(a, 0, len(e) - 2), alt[i])
        near |= ni
        on_last |= v == e[-1]
    cat = {"near_edge": int((diff & near).sum()), "on_last_edge_only": int((diff & on_last & ~near).sum()),
           "neither": int((diff & ~near & ~on_last).sum())}
    # per-bin cross-check over the bins holding differing rows (inside the grid)
    shape = data_nd.shape
    flat = np.ravel_multi_index(ii, shape)
    flat_alt = np.ravel_multi_index(tuple(alt), shape)
    near_in = np.bincount(flat[near & inside], minlength=data_nd.size)
    near_to = np.bincount(flat_alt[near & inside], minlength=data_nd.size)
    bins = {}
    for f in np.unique(flat[diff & inside]):
        rows = flat == f
        vals, cnt = np.unique(got[rows], return_counts=True)
        w0 = float(vals[np.argmax(cnt)])
        B, D = float(bkg_nd.flat[f]), float(data_nd.flat[f])
        rec = {"D_recomputed": D, "B": B, "w0": w0, "n_rows": int(rows.sum()), "n_diff": int((rows & diff).sum()),
               "near_edge_rows_in_bin": int(near_in[f]), "near_edge_rows_whose_other_side_is_this_bin": int(near_to[f])}
        if 0.0 < w0 < 1.0 and B > 0:
            D0 = B / (1.0 - w0)
            delta = D - D0
            rec |= {"D0_from_w0": D0, "delta": delta, "delta_int_residual": abs(delta - round(delta))}
            supply = rec["near_edge_rows_in_bin"] + rec["near_edge_rows_whose_other_side_is_this_bin"]
            rec["explained"] = bool(rec["delta_int_residual"] < 1e-6 and abs(round(delta)) <= supply)
        else:
            rec["explained"] = None   # w0 = 0 or 1, or B = 0: the weight does not depend on D, so D0 is not recoverable
        bins[str(np.unravel_index(f, shape))] = rec
    unexplained = [k for k, r in bins.items() if r["explained"] is False]
    unrec = [k for k, r in bins.items() if r["explained"] is None]
    # a row that is not near an edge kept its original bin, so its stored weight is that bin's w0; it differs from the
    # recomputation only because its bin's count moved (a bin shift, explained when the bin is). Anything else is listed.
    key = lambda j: str(np.unravel_index(flat[j], shape))
    lone = np.flatnonzero(diff & ~near & ~on_last)
    shift, anomalous = 0, []
    for j in lone:
        rec = bins.get(key(j), {}) if inside[j] else {}
        if rec.get("explained") is True and got[j] == rec["w0"]:
            shift += 1
            continue
        anomalous.append({"row": int(j), "bin": str(tuple(int(x[j]) for x in ii)), "inside": bool(inside[j]),
                          "stored": float(got[j]), "recomputed": float(w[j]), "bin_w0": rec.get("w0"),
                          "bin_explained": rec.get("explained")})
    cat["neither_bin_shift_in_explained_bin"] = shift
    cat["neither_anomalous"] = len(anomalous)
    return {"n_rows": n, "n_diff": nd, "share_equal": float(same.mean()), "differing_rows_by_category": cat,
            "rows_near_edge_total": int(near.sum()), "rows_on_last_edge_total": int(on_last.sum()),
            "bins_with_differing_rows": len(bins), "bins_unexplained": unexplained, "bins_not_invertible": unrec,
            "differing_rows_not_explained": anomalous, "bins": bins,
            "float32_ulp_rule": "|v - nearest edge| <= np.spacing(float32(|v|)), per coordinate"}


if __name__ == "__main__":
    out = {"what": "DESCRIPTIVE: C1 measured_weights disagreement (deviation 1); changes no record, enters no rule",
           "deploy": str(DEPLOY), "code_sha256": {p: rp.sa.sha256(DEPLOY / "nd-unfolding" / p)
                                                  for p in ("fd_rpd.py", "fd_rpd_inputs.py")}}
    for X in PLS:
        pp = ri.playlist_paths(X)
        z, b = load_noatime(R / pp["lat"], LAT_KEYS), load_noatime(R / pp["bkg"], BKG_KEYS)
        r = diagnose(z, b)
        out[X] = r
        c = r["differing_rows_by_category"]
        print(f"[mw-diag] {X}: rows {r['n_rows']} differ {r['n_diff']} share {r['share_equal']:.6f}; near-edge {c['near_edge']}"
              f" last-edge-only {c['on_last_edge_only']} bin-shift {c['neither_bin_shift_in_explained_bin']}"
              f" NOT-EXPLAINED {c['neither_anomalous']}; bins {r['bins_with_differing_rows']}"
              f" unexplained {len(r['bins_unexplained'])} not-invertible {len(r['bins_not_invertible'])}", flush=True)
    OUT.write_text(json.dumps(out, indent=1, sort_keys=True))
    print(json.dumps({"wrote": str(OUT), "sha256": rp.sa.sha256(OUT)}))
PYEOF
echo "mw_diag.py sha256 $(sha256sum "$R/diag-2/mw_diag.py" | cut -d' ' -f1)"
date -u +%FT%TZ
"${PY[@]}" "$R/diag-2/mw_diag.py" "$D" "$R" "$R/diag-2/mw_1A_1M.json" 1A 1M > "$R/logs/mwdiag-2.out" 2>&1
rc=$?; echo "mw_diag rc=$rc"; tail -5 "$R/logs/mwdiag-2.out"
[ $rc = 0 ] || { echo "STOP at mw_diag"; finish $rc; }
n=$(git -C "$D" status --porcelain --ignored | wc -l); echo "porcelain --ignored lines after: $n"
[ "$n" -eq 0 ] || { echo "STOP: the deploy changed"; finish 9; }
finish 0

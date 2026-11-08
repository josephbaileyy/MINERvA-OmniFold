#!/bin/bash
# ENS1 stage-1 dry attempt 1: the read-only diagnosis connect (the director's step 1). 0 node-h, login node. No fit; no
# product is opened (attempt 1's root /pscratch/sd/j/josephrb/ens1-20261107 is not read or touched).
#   the COV2D fence, recorded; a fresh root $NEW and a fresh clone at M, clean, with the bound blobs;
#   ens1_diag.py (embedded below, its sha256 checked) runs under the deploy's sourced environment (Python 3.11): it reads
#   the npz and bkg with O_NOATIME, checks both digests against the bound pins, and uses the guard's own
#   cell_membership with the npz's edges. It writes $NEW/diag.json only.
# Writes only under $NEW (refused if it exists). ssh's rc is read unpiped on the Mac. No set -u.
SELF=$1
M=53382844e72057d6eacb47f3bf8556cd47766a70
NEW=/pscratch/sd/j/josephrb/ens1-diag-20261108
D=$NEW/deploy
NPZ=/pscratch/sd/j/josephrb/MINERvA-OmniFold/nd-unfolding/of_inputs_5d.npz
BKG=/pscratch/sd/j/josephrb/s5c-20260924/runs/p2/bkg_dump.npz
DIAG_SHA=d4b5ba16edc2eddb6b83751316db0f16a22fb8476f3450644e3c78d514fa0eba
bail() { rm -f -- "$SELF"; exit 9; }
[ -n "$SELF" ] && [ -f "$SELF" ] || exit 9
[ ! -e "$NEW" ] || bail
mkdir "$NEW" && mkdir "$NEW/logs" || bail
exec > "$NEW/logs/connect-diag.log" 2>&1
finish() { echo "ens1 diag rc=$1"; date -u +%FT%TZ; echo "$1" > "$NEW/logs/connect-diag.done"; rm -f -- "$SELF"; exit "$1"; }
echo "node $(hostname) nproc=$(nproc) loadavg $(cut -d' ' -f1-3 /proc/loadavg)"; date -u +%FT%TZ
echo "connect script sha256 $(sha256sum "$SELF" | cut -d' ' -f1)"
cp "$SELF" "$NEW/logs/ens1_diag_connect.sh"
echo "== COV2D fence"
squeue -u josephrb -h -o '%i|%j|%T|%M|%l' > "$NEW/logs/squeue-before.txt" 2>&1 || { echo "STOP: squeue failed"; finish 9; }
hits=$(awk -F'|' '$2 ~ /^cov2d-/' "$NEW/logs/squeue-before.txt")
if [ -n "$hits" ]; then echo "FENCE: cov2d jobs present (recorded; the diagnosis reads no COV2D input):"; printf '%s\n' "$hits"
else echo "FENCE: no cov2d-* job queued or running"; fi
cat "$NEW/logs/squeue-before.txt"
echo "== stat (before)"
for f in "$NPZ" "$BKG"; do stat -c '%n size=%s atime=%X' "$f" || { echo "STOP: input missing"; finish 9; }; done > "$NEW/logs/stat-before.txt"
cat "$NEW/logs/stat-before.txt"
echo "== the deploy"
git clone -q https://github.com/josephbaileyy/MINERvA-OmniFold.git "$D" > "$NEW/logs/clone.log" 2>&1 || { echo "STOP: clone"; finish 3; }
git -C "$D" -c advice.detachedHead=false checkout -q "$M" || { echo "STOP: checkout"; finish 3; }
[ "$(git -C "$D" rev-parse HEAD)" = "$M" ] || { echo "STOP: HEAD is not M"; finish 9; }
n=$(git -C "$D" status --porcelain --ignored | wc -l); echo "HEAD $M; porcelain --ignored lines: $n"
[ "$n" -eq 0 ] || { echo "STOP: the deploy is not clean"; finish 9; }
bad=0
while read -r b p; do
  [ "$(git -C "$D" hash-object "$p")" = "$b" ] || { echo "MISMATCH $p"; bad=$((bad + 1)); }
done <<BLOBS
d7ba60f50b5f2c8f37ff339d685cc7cf6b5c26d8 nd-unfolding/ensemble_estimator_probe.py
fa4781edab2447793156fc92ec71aacbba2470cd nd-unfolding/s5p_numerics.py
e21c033b779fc604fa6cda72f1fc71d7f58b1e9c nd-unfolding/s5c_unfold.py
21ba1cc953c49d0a754cbf40b4ef0036a881ce58 nd-unfolding/s5e_trace.py
BLOBS
echo "blobs: 4 checked, $bad mismatches"
[ "$bad" -eq 0 ] || { echo "STOP: bound bytes"; finish 9; }
echo "== the diagnosis script"
cat > "$NEW/ens1_diag.py" <<'PYEOF'
#!/usr/bin/env python3
"""ENS1 stage-1 dry attempt 1: the read-only diagnosis of the grid-guard refusal (the director's step 1). No fit, and no
product is opened.

Uses the bound code at M (sys.path = <deploy>/nd-unfolding): the runner's own loader (s5c_unfold.load_inputs), the
protocol jitter (s5p_numerics.jittered), ENS1's internal jitter (ensemble_estimator_probe.internal_jitter) and the guard's
own membership (s5p_numerics.cell_membership -> s5e_trace.flat_index: the npz's edges, float64 coordinates,
searchsorted side='right', last edge inclusive). Edges come from the npz, never from AXIS_EDGES.

    ens1_diag.py --deploy D --npz P --bkg P --out JSON

Reports: (1) moved-row counts per class for protocol jitter 1 alone and for jitter 1 + delta_k, k = 1-4, and whether
they reproduce the job's {MCgen: 2, 1, 2, 1; others 0} and protocol-only 0; (2) each moved row's axis, coordinates, the
crossed edge, its distance in float32 spacings, and whether the row sits at that edge's farther float32 neighbour;
(3) the non-representable edges on every axis; (4) per class, the rows and coordinates within one float32 spacing of
an edge (and exactly on one), the population a value-based edge zone would touch. A count, not a result.
"""
import argparse
import hashlib
import json
import os
import sys
import time

import numpy as np

PINS = {"npz": "07fccc1abc7204bc29349b4ba96850986fe91e909e83fc54e8d1a6b3922a649f",
        "bkg": "2addac8f26055c5ed69862e7afe29e12ac51dbe23a8d6eeed79d71bec9d82955"}
JOB_COUNTS = {1: 2, 2: 1, 3: 2, 4: 1}           # MCgen moved rows per k, from the job's log (receipt #908)
AXES = ("pt", "pz", "eavail", "q3", "W")


def open_noatime(path):
    return os.fdopen(os.open(path, os.O_RDONLY | getattr(os, "O_NOATIME", 0)), "rb")


def sha256_noatime(path):
    h = hashlib.sha256()
    with open_noatime(path) as fh:
        for block in iter(lambda: fh.read(1 << 24), b""):
            h.update(block)
    return h.hexdigest()


def f32_neighbours(e):
    """The two float32 values bracketing float64 e (equal if e is representable), and e's representability."""
    e32 = np.float32(e)
    if float(e32) == e:
        return float(e32), float(e32), True
    lo = e32 if float(e32) < e else np.nextafter(e32, np.float32(-np.inf))
    hi = np.nextafter(lo, np.float32(np.inf))
    return float(lo), float(hi), False


def main():
    ap = argparse.ArgumentParser()
    for opt in ("--deploy", "--npz", "--bkg", "--out"):
        ap.add_argument(opt, required=True)
    a = ap.parse_args()
    sys.path.insert(0, os.path.join(a.deploy, "nd-unfolding"))
    import ensemble_estimator_probe as eep
    import s5c_unfold
    import s5p_numerics
    import s5e_trace
    t0 = time.time()
    rec = {"schema": "ens1-diag/1", "python": sys.version.split()[0], "numpy": np.__version__}
    rec["digests"] = {"npz": sha256_noatime(a.npz), "bkg": sha256_noatime(a.bkg)}
    if rec["digests"] != PINS:
        rec["verdict"] = "STOP: an input is not at its bound pin"
        json.dump(rec, open(a.out, "w"), indent=1)
        print(rec["verdict"]); return 4
    with open_noatime(a.npz) as fh:
        inputs = s5c_unfold.load_inputs(fh)          # the runner's own loader, on an O_NOATIME handle
        inputs = {k: (np.array(v) if hasattr(v, "shape") else v) for k, v in inputs.items()}
    with open_noatime(a.bkg) as fh:
        bz = np.load(fh, allow_pickle=True)
        bkg = {"bkg_reco": np.array(bz["bkg_reco"]), "bkg_w": np.array(bz["bkg_w"]), "bkg_nd": np.array(bz["bkg_nd"])}
    edges = inputs["edges"]
    rec["edges_from"] = "the npz (edges_0..edges_{nedges-1}), as s5c_unfold.load_inputs returns them"
    rec["n_edges_per_axis"] = {AXES[i]: len(e) for i, e in enumerate(edges)}
    classes = ("MCgen", "MCreco", "measured", "bkg_reco")
    raw = {k: np.asarray(inputs[k]) for k in classes[:3]} | {"bkg_reco": np.asarray(bkg["bkg_reco"])}
    rec["rows"] = {k: int(v.shape[0]) for k, v in raw.items()}
    base = s5p_numerics.cell_membership(inputs, bkg["bkg_reco"])        # exactly as the runner (s5p_numerics.py:180)

    # (3) non-representable edges, every axis
    rec["edges_not_float32"] = {}
    for i, e in enumerate(edges):
        rows = []
        for v in np.asarray(e, float):
            lo, hi, rep = f32_neighbours(float(v))
            if not rep:
                s = hi - lo
                rows.append({"edge": float(v), "lo": lo, "hi": hi, "lo_spacings": (float(v) - lo) / s,
                             "hi_spacings": (hi - float(v)) / s})
        rec["edges_not_float32"][AXES[i]] = rows

    def moved_rows(ji, jb):
        after = s5p_numerics.cell_membership(ji, jb["bkg_reco"])
        out = {}
        for key in classes:
            idx = np.flatnonzero(after[key] != base[key])
            out[key] = idx
        return out, after

    def describe(key, r, jcoords):
        """Per moved row: which axis changes its cell (flat_index on the row with one axis replaced), the crossed
        edge, the distance in float32 spacings, and the neighbour test."""
        x0 = np.asarray(raw[key][r], np.float64)
        x1 = np.asarray(jcoords[r], np.float64)
        b0 = s5e_trace.flat_index(x0[None, :], edges)[0]
        out = {"row": int(r), "cell_before": int(b0), "axes": []}
        for ax in range(x0.size):
            t = x0.copy(); t[ax] = x1[ax]
            if s5e_trace.flat_index(t[None, :], edges)[0] == b0:
                continue
            e = np.asarray(edges[ax], float)
            lo_v, hi_v = min(x0[ax], x1[ax]), max(x0[ax], x1[ax])
            crossed = [float(v) for v in e if lo_v < v <= hi_v]      # side='right': x == edge is in the upper bin
            item = {"axis": AXES[ax], "x_float32": float(np.float32(raw[key][r][ax])), "x_jittered": float(x1[ax]),
                    "move": float(x1[ax] - x0[ax]), "crossed_edges": crossed}
            if len(crossed) == 1:
                ev = crossed[0]
                lo, hi, rep = f32_neighbours(ev)
                sp = float(np.spacing(np.float32(abs(np.float32(raw[key][r][ax])))))
                far = lo if (ev - lo) > (hi - ev) else hi
                item.update({"edge_float32_representable": rep, "edge_neighbours": [lo, hi],
                             "distance_spacings": (ev - float(x0[ax])) / sp,
                             "move_spacings": float(x1[ax] - x0[ax]) / sp,
                             "at_farther_neighbour": (not rep) and float(x0[ax]) == far,
                             "at_nearer_neighbour": (not rep) and float(x0[ax]) == (hi if far == lo else lo)})
            out["axes"].append(item)
        return out

    # (1) protocol jitter 1 alone
    ji, jb = s5p_numerics.jittered(inputs, bkg, 1)
    m0, _ = moved_rows(ji, jb)
    rec["protocol_only"] = {k: int(v.size) for k, v in m0.items()}
    rec["protocol_only_rows"] = {k: [describe(k, r, (ji[k] if k != "bkg_reco" else jb["bkg_reco"])) for r in v[:20]]
                                 for k, v in m0.items() if v.size}
    # (1)-(2) jitter 1 + delta_k
    rec["plus_delta"] = {}
    for k in (1, 2, 3, 4):
        jk, jbk, _ = eep.internal_jitter(ji, jb, k)
        mk, _ = moved_rows(jk, jbk)
        rec["plus_delta"][k] = {"counts": {c: int(v.size) for c, v in mk.items()},
                                "rows": {c: [describe(c, r, (jk[c] if c != "bkg_reco" else jbk["bkg_reco"])) for r in v[:20]]
                                         for c, v in mk.items() if v.size}}
        del jk, jbk
    # (4) the population within one float32 spacing of an edge (and exactly on one)
    rec["near_edge"] = {}
    for key in classes:
        x32 = np.asarray(raw[key], np.float32)
        x = x32.astype(np.float64)
        sp = np.spacing(np.abs(x32)).astype(np.float64)
        near_any = np.zeros(x.shape, bool)
        on_any = np.zeros(x.shape, bool)
        for ax, e in enumerate(edges):
            e = np.asarray(e, float)
            j = np.clip(np.searchsorted(e, x[:, ax]), 1, len(e) - 1)
            d = np.minimum(np.abs(x[:, ax] - e[j - 1]), np.abs(e[j] - x[:, ax]))
            on_any[:, ax] = d == 0
            near_any[:, ax] = (d > 0) & (d <= sp[:, ax])
        rec["near_edge"][key] = {"coordinates_within_one_spacing": int(near_any.sum()),
                                 "rows_within_one_spacing": int(near_any.any(axis=1).sum()),
                                 "per_axis_within_one_spacing": {AXES[i]: int(near_any[:, i].sum()) for i in range(x.shape[1])},
                                 "coordinates_on_an_edge": int(on_any.sum())}
    # the checks
    rep_counts = all(rec["plus_delta"][k]["counts"] == {"MCgen": JOB_COUNTS[k], "MCreco": 0, "measured": 0, "bkg_reco": 0}
                     for k in JOB_COUNTS)
    prot_zero = all(v == 0 for v in rec["protocol_only"].values())
    movers = [ax for k in JOB_COUNTS for rows in rec["plus_delta"][k]["rows"].values() for r in rows for ax in r["axes"]]
    all_far = bool(movers) and all(ax.get("at_farther_neighbour") for ax in movers)
    rec["checks"] = {"plus_delta_reproduces_the_job": rep_counts, "protocol_only_zero": prot_zero,
                     "every_mover_at_a_farther_neighbour": all_far}
    rec["verdict"] = "CONFIRMED" if (rep_counts and prot_zero and all_far) else "STOP: the likely cause is not confirmed"
    rec["seconds"] = round(time.time() - t0, 1)
    with open(a.out, "w") as fh:
        json.dump(rec, fh, indent=1)
    print(json.dumps({"verdict": rec["verdict"], "checks": rec["checks"], "protocol_only": rec["protocol_only"],
                      "plus_delta": {k: v["counts"] for k, v in rec["plus_delta"].items()}}))
    return 0 if rec["verdict"] == "CONFIRMED" else 4


if __name__ == "__main__":
    sys.exit(main())
PYEOF
got=$(sha256sum "$NEW/ens1_diag.py" | cut -d' ' -f1); echo "ens1_diag.py sha256 $got (sent $DIAG_SHA)"
[ "$got" = "$DIAG_SHA" ] || { echo "STOP: the diagnosis script is not the one sent"; finish 9; }
echo "== the diagnosis (sourced environment)"
( source "$D/setup_salloc_env.sh" > "$NEW/logs/env.log" 2>&1
  python3 --version
  cd "$NEW" && PYTHONDONTWRITEBYTECODE=1 nice -n 19 python3 -B "$NEW/ens1_diag.py" --deploy "$D" --npz "$NPZ" --bkg "$BKG" \
    --out "$NEW/diag.json" ); rc=$?
echo "diagnosis rc=$rc"
echo "== stat (after; atime must not move)"
for f in "$NPZ" "$BKG"; do stat -c '%n size=%s atime=%X' "$f"; done > "$NEW/logs/stat-after.txt"
cat "$NEW/logs/stat-after.txt"
cmp -s "$NEW/logs/stat-before.txt" "$NEW/logs/stat-after.txt" && echo "atime unchanged" || { echo "STOP: an input's atime moved"; finish 8; }
[ -s "$NEW/diag.json" ] && sha256sum "$NEW/diag.json"
echo "deploy porcelain --ignored after: $(git -C "$D" status --porcelain --ignored | wc -l)"
finish $rc

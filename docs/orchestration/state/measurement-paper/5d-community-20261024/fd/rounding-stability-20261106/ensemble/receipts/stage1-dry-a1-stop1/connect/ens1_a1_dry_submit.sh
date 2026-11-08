#!/bin/bash
# ENS1 stage-1 dry RERUN under addendum A1 (ENS1-BINDING-2, "addendum A1", rulings 1-5): the submission. Runs on a login
# node from a /dev/shm copy of itself whose path is $1; it deletes that copy at exit. In order:
#   the fence (the director's rule): the queue may hold only rs1_* and ens1_* jobs; a cov2d-* job or any other name is a
#     stop; an ens1_* job already queued or running is a stop (checked before anything is written);
#   iris: stop unless ENS1's caps (55.0 + 46.0) and RS1's 8.0 together are at most half of m3246's remaining balance;
#   a stat of the inputs, of FD-STAB's 20 control jitters j1-j20 and of attempt 1's F64 product (stat only);
#   a fresh clone at M_A1 into $NEW/deploy: clean, the bound blobs, and the sha256 of A1, the declaration, binding 1 and
#     the probe, analysis and job script as ENS1-BINDING-2's A1 table states them; binding 2's A1 section at origin/main
#     names M_A1;
#   the 20 control jitters copied with dd iflag=noatime into $NEW/refs/runs/control/stability/: each original's atime
#     unchanged and each copy at its line in FD-STAB's SHA256SUMS (e2c35e55);
#   A1's three preconditions, recomputed on the npz's own edges by ens1_a1_pre.py (embedded, its sha256 checked) under
#     the sourced environment with the bound in_edge_zone, the npz read with O_NOATIME after its pin is checked; any
#     failure is a stop (d_min > 1 + 2^-20; farther neighbour > 1/2 + 2^-20 of its own spacing; no power-of-two
#     neighbour of a non-representable edge; and the npz's edges must match A1 §3's tables);
#   the environment pre-check (0 node-h) and the stage-1 queue from the bound probe's own `tasks --stage 1`, under the
#     sourced environment: dry.tsv and the six shards at the digests sent (9 dry tasks; 1,004 shard tasks);
#   one sbatch: sbatch_ens1.sh dry 1 at M_A1, --time=0:45:00, job name ens1_a1_dry, from the plain login environment;
#     scontrol's TimeLimit must read 00:45:00, or the job is cancelled at once and the connect stops.
# Moved rows (0 at all nine tasks) and the F64 bitwise comparison are read by the post-run connect, after the job ends.
# Every module call runs under the sourced environment (setup_salloc_env.sh, Python 3.11), never the system python3
# (3.6). Writes only under $NEW (new; refused if it exists). Attempt 1's root is stat'ed, never read or written. No set -u.
SELF=$1
M=f4d2d7f3833834390b7b031df61ba1a5765e9900
NEW=/pscratch/sd/j/josephrb/ens1-a1-20261108
OLD=/pscratch/sd/j/josephrb/ens1-20261107
D=$NEW/deploy
CAPS=109.0                                                       # ENS1 55.0 + 46.0, and RS1's 8.0
TLIMIT_ARG=0:45:00
TLIMIT=00:45:00
JOBNAME=ens1_a1_dry
NPZ=/pscratch/sd/j/josephrb/MINERvA-OmniFold/nd-unfolding/of_inputs_5d.npz
BKG=/pscratch/sd/j/josephrb/s5c-20260924/runs/p2/bkg_dump.npz
BANK=/pscratch/sd/j/josephrb/MINERvA-OmniFold/nd-unfolding/bank_sweep_5d_bkgaware
DET=/pscratch/sd/j/josephrb/s5p-20260926/bank_detector
PVL=/pscratch/sd/j/josephrb/pv-ladder-20261024
REFSRC=/pscratch/sd/j/josephrb/fd-stab-a1r-20261104/runs/control/stability
REFDST=$NEW/refs/runs/control/stability
S=docs/orchestration/state/measurement-paper/5d-community-20261024
E=$S/fd/rounding-stability-20261106/ensemble
SUMS=$S/fd/receipts-stab-a1r/full/SHA256SUMS
PRE_SHA=4064ef02a9eb9455c2ea778a02c86f27a6c0ec79668c35e82ca80b7f54054e89
bail() { rm -f -- "$SELF"; exit 9; }
[ -n "$SELF" ] && [ -f "$SELF" ] || exit 9
[ ! -e "$NEW" ] || bail
q0=$(squeue --me -h -o '%j') || bail
[ -z "$(printf '%s\n' "$q0" | grep -E '^ens1_')" ] || bail
mkdir "$NEW" && mkdir "$NEW/logs" && mkdir -p "$REFDST" || bail
LOG=$NEW/logs/connect-a1-dry.log
exec > "$LOG" 2>&1
finish() { echo "ens1 a1 dry submit rc=$1"; date -u +%FT%TZ; echo "$1" > "$NEW/logs/connect-a1-dry.done"; rm -f -- "$SELF"; exit "$1"; }
echo "node $(hostname) nproc=$(nproc) loadavg $(cut -d' ' -f1-3 /proc/loadavg)"
date -u +%FT%TZ
echo "connect script sha256 $(sha256sum "$SELF" | cut -d' ' -f1)"
cp "$SELF" "$NEW/logs/ens1_a1_dry_submit.sh"

echo "== the fence (only rs1_* and ens1_* pass; cov2d-* or any other name stops)"
squeue -u josephrb -h -o '%i|%j|%T|%M|%l' > "$NEW/logs/squeue-before.txt" 2>&1 || { echo "STOP: squeue failed"; finish 9; }
cat "$NEW/logs/squeue-before.txt"
cov=$(awk -F'|' '$2 ~ /^cov2d-/' "$NEW/logs/squeue-before.txt")
other=$(awk -F'|' '$2 !~ /^(rs1_|ens1_)/' "$NEW/logs/squeue-before.txt")
ens=$(awk -F'|' '$2 ~ /^ens1_/' "$NEW/logs/squeue-before.txt")
[ -z "$cov" ] || { echo "FENCE STOP: cov2d jobs present:"; printf '%s\n' "$cov"; finish 9; }
[ -z "$other" ] || { echo "FENCE STOP: a job of another name is present:"; printf '%s\n' "$other"; finish 9; }
[ -z "$ens" ] || { echo "STOP: an ens1_* job is already queued or running:"; printf '%s\n' "$ens"; finish 9; }
echo "FENCE: pass ($(wc -l < "$NEW/logs/squeue-before.txt" | tr -d ' ') jobs, all rs1_*)"

echo "== iris"; timeout 120 iris < /dev/null > "$NEW/logs/iris.txt" 2>&1; head -2 "$NEW/logs/iris.txt"
row=$(grep -E '^m3246 ' "$NEW/logs/iris.txt" | head -1); echo "$row"
bal=$(echo "$row" | awk 'NF>=5 {printf "%.1f", $5-$4}')
[ -n "$bal" ] || { echo "STOP: could not read the m3246 balance"; finish 9; }
echo "balance_node_h=$bal half=$(awk -v b="$bal" 'BEGIN{printf "%.1f", b/2}') caps=$CAPS"
awk -v b="$bal" -v c=$CAPS 'BEGIN{exit !(c <= b/2)}' || { echo "STOP: the caps are above half the balance"; finish 9; }

echo "== stat"
REFS=""; for s in $(seq 1 20); do REFS="$REFS stab_control_b-_j$s.npz"; done
miss=0
for f in "$NPZ" "$BKG" "$OLD/runs/F64/ens1_F64_b-_j0.npz"; do stat -c '%n size=%s mtime=%y atime=%x' "$f" || miss=$((miss + 1)); done
for r in $REFS; do stat -c '%n size=%s mtime=%y atime=%x' "$REFSRC/$r" || miss=$((miss + 1)); done
echo "stat: 23 files, $miss missing"
[ "$miss" -eq 0 ] || { echo "STOP: an input, a reference or attempt 1's F64 is missing"; finish 9; }

echo "== the deploy"
git clone -q https://github.com/josephbaileyy/MINERvA-OmniFold.git "$D" > "$NEW/logs/clone.log" 2>&1 || { echo "STOP: clone"; finish 3; }
git -C "$D" -c advice.detachedHead=false checkout -q "$M" || { echo "STOP: checkout"; finish 3; }
[ "$(git -C "$D" rev-parse HEAD)" = "$M" ] || { echo "STOP: HEAD is not M_A1"; finish 9; }
n=$(git -C "$D" status --porcelain --ignored | wc -l); echo "HEAD $M; porcelain --ignored lines before: $n"
[ "$n" -eq 0 ] || { echo "STOP: the deploy is not clean"; finish 9; }
bad=0
while read -r b p; do
  [ "$(git -C "$D" rev-parse "$M:$p")" = "$b" ] && [ "$(git -C "$D" hash-object "$p")" = "$b" ] || { echo "MISMATCH $p"; bad=$((bad + 1)); }
done <<BLOBS
a25490bf9d078e708696b9c9f534c731d72fcc61 nd-unfolding/ensemble_estimator_probe.py
2ac2fbe497b29f4754d0dacbe8decbc35cd4e1d5 nd-unfolding/ensemble_estimator_analyze.py
b334872a59bcbe1b6852a066dc409776dc016513 nd-unfolding/sbatch_ens1.sh
8465d84f08e99ad12f2c4fb3afca2ea7efbe485b nd-unfolding/rounding_mechanism_probe.py
25179f9f704e61a920c9d0005283b4fcd357d825 nd-unfolding/estimator_stability_probe.py
0e4718902e1b156d340ba5a9848d522b5be0fc45 nd-unfolding/estimator_stability_analyze.py
fa4781edab2447793156fc92ec71aacbba2470cd nd-unfolding/s5p_numerics.py
14f7a01186bed708e8a673f7f42c82052b76373e nd-unfolding/s5p_nullexp.py
21ba1cc953c49d0a754cbf40b4ef0036a881ce58 nd-unfolding/s5e_trace.py
1a1898fe6b5a2c6b66d7b77d4d1f02e1fbb81f59 nd-unfolding/s5n_pseudo.py
e21c033b779fc604fa6cda72f1fc71d7f58b1e9c nd-unfolding/s5c_unfold.py
bdc79a29ad90e110413898f42c81178410f7269c $SUMS
BLOBS
bad2=0
while read -r h p; do
  [ "$(sha256sum "$D/$p" | cut -d' ' -f1)" = "$h" ] || { echo "SHA256 MISMATCH $p"; bad2=$((bad2 + 1)); }
done <<SHAS
1b8a4592d9e4cad126b2a386afd8f8d169db2c11cec12a837f91cbb0f1cff698 $E/ENS1-ADDENDUM-A1.md
fb523c7a7a8215b451d21093b2637ed12548f3f2ce4b714990c194b05d21a2fb $E/ENS1-DECLARATION.md
cabff142a1c0ec881ce8ba1ee348c88f02b74d44b5052a7e6aae51afacfa4dfc $E/ENS1-BINDING-1.md
807c40d3cb64e2e09d2fa9a5b91fb7a786f4eb51090e4291d65b3896b47e3b25 nd-unfolding/ensemble_estimator_probe.py
1d6a0448ac75c90a2282ceb8bd5383cf0cae27024c0dbb9a5adc27ff93b11281 nd-unfolding/ensemble_estimator_analyze.py
0390e5c71f1b958558dbae7916e39ead33865362c1369d2f25b205061b2b7267 nd-unfolding/sbatch_ens1.sh
e2c35e55402b809f522c86f597df20b058fc0c49596b9595448c4a944be333ee $SUMS
SHAS
b2=$(git -C "$D" show "origin/main:$E/ENS1-BINDING-2.md" 2>/dev/null | sed -n '/^## Binding 2, addendum A1/,$p')
b2ok=0; printf '%s\n' "$b2" | grep -qF "M_A1 = \`$M\`" && b2ok=1
echo "blobs: 12 checked, $bad mismatches; sha256: 7 checked, $bad2 mismatches; binding 2's A1 section names M_A1: $b2ok"
echo "origin/main $(git -C "$D" rev-parse origin/main); binding 2 at origin/main sha256 $(git -C "$D" show "origin/main:$E/ENS1-BINDING-2.md" | sha256sum | cut -d' ' -f1)"
[ "$bad" -eq 0 ] && [ "$bad2" -eq 0 ] && [ "$b2ok" -eq 1 ] || { echo "STOP: bound bytes"; finish 9; }

echo "== the control jitters j1-j20 (dd iflag=noatime)"
bad=0
for r in $REFS; do
  a0=$(stat -c %X "$REFSRC/$r")
  dd if="$REFSRC/$r" iflag=noatime of="$REFDST/$r" bs=4M status=none || { echo "COPY FAILED $r"; bad=$((bad + 1)); continue; }
  a1=$(stat -c %X "$REFSRC/$r")
  want=$(awk -v n="runs/control/stability/$r" '$2 == n {print $1}' "$D/$SUMS")
  got=$(sha256sum "$REFDST/$r" | cut -d' ' -f1)
  [ "$a0" = "$a1" ] || { echo "ATIME MOVED $r ($a0 -> $a1)"; bad=$((bad + 1)); }
  [ -n "$want" ] && [ "$got" = "$want" ] || { echo "NOT PINNED $r ($got vs '$want')"; bad=$((bad + 1)); }
done
echo "control jitters: 20 copied, $bad problems"
( cd "$NEW/refs" && find runs -type f -print0 | sort -z | xargs -0 sha256sum ) > "$NEW/logs/refs-SHA256SUMS"
[ "$bad" -eq 0 ] || { echo "STOP: a control jitter"; finish 9; }

echo "== A1's preconditions on the npz's own edges (sourced environment)"
cat > "$NEW/ens1_a1_pre.py" <<'PYEOF'
#!/usr/bin/env python3
"""ENS1 addendum A1: the dry rerun's precondition check (ENS1-BINDING-2 addendum A1, ruling 2; A1 §3). 0 node-h.

Reads only the npz's grid edges (edges_0..edges_{nedges-1}, converted exactly as s5c_unfold.load_inputs converts them:
np.asarray(d[f"edges_{i}"], float)) from an O_NOATIME handle, after checking the npz's digest against its bound pin. The
zone is the bound ensemble_estimator_probe.in_edge_zone at the deploy (sys.path = <deploy>/nd-unfolding), never a copy.

    ens1_a1_pre.py --deploy D --npz P --out JSON

Refuses (exit 4) unless all three of A1's preconditions hold on every axis:
  (1) d_min > 1 + 2^-20: every float32 value outside the zone is more than 1 + 2^-20 of its own spacing from every edge;
  (2) every non-representable edge's farther float32 neighbour lies more than 1/2 + 2^-20 of that neighbour's own
      spacing from the edge;
  (3) no non-representable edge has a power of two as a float32 neighbour.
It also refuses if the edges are not strictly increasing, or if the npz's edges do not match A1 §3's stated tables
(edge counts, non-representable counts, d_min to two decimals): A1's argument would then not describe this input.

d_min: for every edge, the 64 float32 values on each side of round32(e) are enumerated; the zone is evaluated on them
with the bound in_edge_zone; for those outside it, d = the distance to the nearest edge of the axis (float64, exact)
over spacing32(|x|). Beyond 64 steps the distance exceeds 30 spacings (a binade change at most halves or doubles the
spacing inside the window, and the subnormal spacing is uniform), so the minimum is attained inside the window.
"""
import argparse
import hashlib
import json
import os
import sys

import numpy as np

NPZ_PIN = "07fccc1abc7204bc29349b4ba96850986fe91e909e83fc54e8d1a6b3922a649f"
AXES = ("pt", "pz", "eavail", "q3", "W")
MARGIN = 2.0 ** -20
WINDOW = 64
# A1 §3 (ii) and the neighbour table, at A1 sha256 1b8a4592...
A1_EDGES = {"pt": 15, "pz": 17, "eavail": 8, "q3": 8, "W": 7}
A1_NONREP = {"pt": 8, "pz": 0, "eavail": 4, "q3": 5, "W": 4}
A1_DMIN = {"pt": 1.04, "pz": 2.00, "eavail": 1.20, "q3": 1.20, "W": 1.20}


def open_noatime(path):
    return os.fdopen(os.open(path, os.O_RDONLY | getattr(os, "O_NOATIME", 0)), "rb")


def sha256_noatime(path):
    h = hashlib.sha256()
    with open_noatime(path) as fh:
        for block in iter(lambda: fh.read(1 << 24), b""):
            h.update(block)
    return h.hexdigest()


def is_pow2(v):
    m, _ = np.frexp(abs(float(v)))
    return v != 0 and m == 0.5


def neighbours(e):
    """(lo, hi, representable): the float32 values bracketing float64 e."""
    e32 = np.float32(e)
    if float(e32) == e:
        return e32, e32, True
    lo = e32 if float(e32) < e else np.nextafter(e32, np.float32(-np.inf))
    hi = np.nextafter(lo, np.float32(np.inf))
    return lo, hi, False


def window(e):
    c = np.float32(e)
    out = [c]
    lo = hi = c
    for _ in range(WINDOW):
        lo = np.nextafter(lo, np.float32(-np.inf))
        hi = np.nextafter(hi, np.float32(np.inf))
        out += [lo, hi]
    return np.array(out, np.float32)


def main():
    ap = argparse.ArgumentParser()
    for opt in ("--deploy", "--npz", "--out"):
        ap.add_argument(opt, required=True)
    a = ap.parse_args()
    sys.path.insert(0, os.path.join(a.deploy, "nd-unfolding"))
    import ensemble_estimator_probe as eep
    rec = {"schema": "ens1-a1-pre/1", "python": sys.version.split()[0], "numpy": np.__version__,
           "margin": MARGIN, "window": WINDOW}
    rec["npz_sha256"] = sha256_noatime(a.npz)
    fails = []
    if rec["npz_sha256"] != NPZ_PIN:
        fails.append("the npz is not at its bound pin")
    else:
        with open_noatime(a.npz) as fh:
            d = np.load(fh, allow_pickle=True)
            edges = [np.asarray(d[f"edges_{i}"], float) for i in range(int(d["nedges"]))]
        rec["edges"] = {AXES[i]: [float(v) for v in e] for i, e in enumerate(edges)}
        rec["axes"] = {}
        n = len(edges)
        for ax, e in enumerate(edges):
            name = AXES[ax]
            r = {"n_edges": int(e.size), "strictly_increasing": bool(np.all(np.diff(e) > 0))}
            # (1) d_min outside the zone, through the bound zone
            cand = np.unique(np.concatenate([window(v) for v in e]))
            coords = np.repeat(cand[:, None], n, axis=1)             # the other columns are ignored for this axis
            zone = eep.in_edge_zone(coords, edges)[:, ax]
            x = cand.astype(np.float64)
            dist = np.min(np.abs(x[:, None] - e[None, :]), axis=1)
            sp = np.spacing(np.abs(cand)).astype(np.float64)
            out = ~zone
            ratio = dist[out] / sp[out]
            i = int(np.argmin(ratio))
            r["d_min_outside_zone"] = float(ratio[i])
            r["d_min_at"] = float(x[out][i])
            r["zone_points_beyond_one_spacing"] = int(np.sum(zone & (dist > sp)))   # must be 0: the zone is d <= s
            r["outside_points_within_one_spacing"] = int(np.sum(~zone & (dist <= sp)))  # must be 0
            # (2) and (3), every non-representable edge
            nonrep = []
            for v in e:
                lo, hi, rep = neighbours(float(v))
                if rep:
                    continue
                dlo, dhi = float(v) - float(lo), float(hi) - float(v)
                far, dfar = (lo, dlo) if dlo > dhi else (hi, dhi)
                nonrep.append({"edge": float(v), "lo": float(lo), "hi": float(hi),
                               "lo_spacings": dlo / float(np.spacing(np.abs(lo))),
                               "hi_spacings": dhi / float(np.spacing(np.abs(hi))),
                               "far": float(far), "far_own_spacings": dfar / float(np.spacing(np.abs(far))),
                               "pow2_neighbour": bool(is_pow2(lo) or is_pow2(hi))})
            r["non_representable"] = nonrep
            r["n_non_representable"] = len(nonrep)
            r["far_min_own_spacings"] = min((q["far_own_spacings"] for q in nonrep), default=None)
            # the checks
            c = {"strictly_increasing": r["strictly_increasing"],
                 "zone_is_one_spacing": r["zone_points_beyond_one_spacing"] == 0
                 and r["outside_points_within_one_spacing"] == 0,
                 "P1_d_min": r["d_min_outside_zone"] > 1 + MARGIN,
                 "P2_far_neighbour": all(q["far_own_spacings"] > 0.5 + MARGIN for q in nonrep),
                 "P3_no_pow2_neighbour": not any(q["pow2_neighbour"] for q in nonrep),
                 "A1_table_edges": r["n_edges"] == A1_EDGES[name],
                 "A1_table_nonrep": r["n_non_representable"] == A1_NONREP[name],
                 "A1_table_d_min": round(r["d_min_outside_zone"], 2) == A1_DMIN[name]}
            r["checks"] = c
            fails += [f"{name}: {k}" for k, ok in c.items() if not ok]
            rec["axes"][name] = r
        if n != len(AXES):
            fails.append(f"nedges is {n}, not {len(AXES)}")
    rec["failures"] = fails
    rec["verdict"] = "PASS" if not fails else "REFUSE"
    with open(a.out, "w") as fh:
        json.dump(rec, fh, indent=1)
    print(json.dumps({"verdict": rec["verdict"], "failures": fails,
                      "d_min": {k: round(v["d_min_outside_zone"], 4) for k, v in rec.get("axes", {}).items()},
                      "far_min": {k: (None if v["far_min_own_spacings"] is None else round(v["far_min_own_spacings"], 4))
                                  for k, v in rec.get("axes", {}).items()},
                      "non_representable": {k: v["n_non_representable"] for k, v in rec.get("axes", {}).items()}}))
    return 0 if not fails else 4


if __name__ == "__main__":
    sys.exit(main())
PYEOF
got=$(sha256sum "$NEW/ens1_a1_pre.py" | cut -d' ' -f1); echo "ens1_a1_pre.py sha256 $got (sent $PRE_SHA)"
[ "$got" = "$PRE_SHA" ] || { echo "STOP: the precondition script is not the one sent"; finish 9; }
na0=$(stat -c %X "$NPZ")
( source "$D/setup_salloc_env.sh" > "$NEW/logs/env-pre.log" 2>&1
  python3 --version
  cd "$NEW" && PYTHONDONTWRITEBYTECODE=1 nice -n 19 python3 -B "$NEW/ens1_a1_pre.py" --deploy "$D" --npz "$NPZ" \
    --out "$NEW/logs/a1-preconditions.json" ); rc=$?
echo "precondition check rc=$rc; npz atime $na0 -> $(stat -c %X "$NPZ")"
[ -s "$NEW/logs/a1-preconditions.json" ] && sha256sum "$NEW/logs/a1-preconditions.json"
[ $rc -eq 0 ] || { echo "STOP: A1's preconditions do not hold on the npz's edges (A1 §3: refuse)"; finish 4; }

echo "== the environment (sourced)"
( source "$D/setup_salloc_env.sh" > "$NEW/logs/env-precheck.log" 2>&1
  python3 -B -c "import lightgbm, scipy, numpy, sys; print('python', sys.version.split()[0], 'lightgbm', lightgbm.__version__, 'scipy', scipy.__version__, 'numpy', numpy.__version__)" ) \
  || { echo "STOP: the environment lacks lightgbm/scipy (see env-precheck.log)"; finish 7; }

echo "== the stage-1 queue (sourced)"
( source "$D/setup_salloc_env.sh" > "$NEW/logs/env-tasks.log" 2>&1
  cd "$D" && PYTHONDONTWRITEBYTECODE=1 nice -n 19 python3 -B nd-unfolding/ensemble_estimator_probe.py tasks --stage 1 \
    --out-dir "$NEW/stage1" --runs "$NEW/runs" --npz "$NPZ" --bkg "$BKG" --bank "$BANK" --detector-dir "$DET" \
    --closure-ratio-dir "$PVL" --expect-npz-sha256 07fccc1abc7204bc29349b4ba96850986fe91e909e83fc54e8d1a6b3922a649f \
    --expect-bkg-sha256 2addac8f26055c5ed69862e7afe29e12ac51dbe23a8d6eeed79d71bec9d82955 ) || { echo "STOP: tasks"; finish 5; }
( cd "$NEW/stage1" && sha256sum dry.tsv shard0.tsv shard1.tsv shard2.tsv shard3.tsv shard4.tsv shard5.tsv ) > "$NEW/logs/queue-sha256.txt"
cat "$NEW/logs/queue-sha256.txt"
cat > "$NEW/logs/queue-sha256.expected" <<SUMS1
83ae2e8c6ce7916725ed3c31096ae4ea7c831b40aed70386225dff520de0f8f2  dry.tsv
76b3b25a31a37f818126fe5d03e2b99f4694ee7581ce5ef1791b5ca936b71349  shard0.tsv
30383483dfe727762c8ba268996ae266385a547944b58e2ec339d36d422d4741  shard1.tsv
4df6defc7b2b542062edda09d4bc32d7a973f058e30f51489f2c3364a6a5701a  shard2.tsv
7df85feadf16a3c1c6f166661acbda57d27004bec21dcb3935ca8f6f3dba86f5  shard3.tsv
eeca67f3ded9548611db5544830dc8075c7f6fdfd3bf4bee503a22afdf9f2468  shard4.tsv
761c27c42131f2c1b4013301e972e5b7d5f34a28fda84bd6e7df25e420ee615a  shard5.tsv
SUMS1
cmp -s "$NEW/logs/queue-sha256.txt" "$NEW/logs/queue-sha256.expected" || { echo "STOP: the queue is not the one sent"; finish 5; }
nd=$(grep -vc '^#' "$NEW/stage1/dry.tsv"); echo "dry tasks: $nd"
[ "$nd" -eq 9 ] || { echo "STOP: the dry run is not 9 tasks"; finish 5; }

date -u +%FT%TZ
cd "$NEW" || finish 9
sbatch --time=$TLIMIT_ARG --job-name=$JOBNAME --output="$NEW/logs/%x_%j.out" \
  "$D/nd-unfolding/sbatch_ens1.sh" dry 1 "$D" "$M" "$NEW" > "$NEW/logs/submit-a1-dry.out" 2>&1
rc=$?; echo "sbatch rc=$rc"; cat "$NEW/logs/submit-a1-dry.out"
[ $rc = 0 ] || { echo "STOP at sbatch (final)"; finish $rc; }
job=$(sed -n 's/^Submitted batch job \([0-9][0-9]*\)$/\1/p' "$NEW/logs/submit-a1-dry.out")
[ -n "$job" ] || { echo "STOP: no job id"; finish 9; }
echo "dry rerun job $job"; echo "$job" > "$NEW/logs/a1-dry.jobid"
tl=$(scontrol show job "$job" | sed -n 's/.*TimeLimit=\([^ ]*\).*/\1/p' | head -1)
echo "scontrol TimeLimit=$tl (declared $TLIMIT)"
if [ "$tl" != "$TLIMIT" ]; then
  scancel "$job"; echo "STOP: TimeLimit $tl is not $TLIMIT; job $job cancelled (rc $?)"; sleep 5
  sacct -j "$job" -X -n -P -o JobID,State,Elapsed; finish 6
fi
sleep 5
squeue -j "$job" -h -o "%i %j %T %M %l %D %q %a"
n=$(git -C "$D" status --porcelain --ignored | wc -l); echo "porcelain --ignored lines after: $n"
[ "$n" -eq 0 ] || { echo "the deploy changed after the submission (the job is queued; reported, not cancelled)"; finish 8; }
finish 0

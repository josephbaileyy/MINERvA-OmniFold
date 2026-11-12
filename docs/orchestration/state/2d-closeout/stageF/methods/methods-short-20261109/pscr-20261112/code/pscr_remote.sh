#!/bin/bash
# #977 read-only pscratch session, the remote half (rows 4.2/F4.3/4.3, m5/Fm7, F5.3), on a Perlmutter login node.
# Pattern: T2B's approved fetch (t2b_fetch_remote.sh b407d055). Runs from a /dev/shm copy of itself ($1), deleted at
# exit. Step 0 is the cov2d fence (squeue/sacct only; any cov2d/t2a job queued, running or unended in 14 days, or
# either command failing -> exit 3, nothing read). Then one python process: every input is opened by explicit path
# with O_NOATIME, stat (size, mtime, atime) taken before and after, sha256 of the bytes read. Only small derived
# arrays leave the node, as one uncompressed tar on stdout, built in memory. Nothing is written on the cluster
# except this script's own /dev/shm copy. All log lines go to stderr. Exit 0 only if every input was read whole
# with stat unchanged and every computation ran; else 4.
#   A  4.2/F4.3/4.3: work_proxy.npz (per-playlist 2D reco templates D,S,S2,B,B2), copied whole (~small).
#   B  m5/Fm7: xtrue_flat and shape from all 100 s5e assess products (nominal 40, W1/W2/W3 20 each).
#   C  F5.3: weighted and unweighted fractions of pass_reco rows outside the reco window / gen grid, from OF5D,
#      with r4_migration.py's masks; the unweighted pair is a control against r4_migration.json.
SELF=$1
trap 'rm -f -- "$SELF"' EXIT
umask 077
echo "session host=$(hostname) utc=$(date -u +%FT%TZ)" >&2
q=$(squeue --me -h -o '%i|%j|%T') || { echo "FENCE REFUSED: squeue failed" >&2; exit 3; }
printf '%s\n' "$q" | sed '/^$/d; s/^/squeue: /' >&2
if printf '%s\n' "$q" | awk -F'|' '$2 ~ /^(cov2d|t2a)/ {f=1} END {exit !f}'; then
  echo "FENCE REFUSED: a cov2d/t2a job is queued or running" >&2; exit 3
fi
s=$(sacct -X -n -P -S "$(date -u -d '14 days ago' +%F)" -o JobID,JobName,State) || { echo "FENCE REFUSED: sacct failed" >&2; exit 3; }
u=$(printf '%s\n' "$s" | awk -F'|' '$2 ~ /^(cov2d|t2a)/ && $3 !~ /^(COMPLETED|FAILED|CANCELLED|TIMEOUT|OUT_OF_MEMORY|NODE_FAIL|PREEMPTED|BOOT_FAIL|DEADLINE)/')
[ -z "$u" ] || { printf '%s\n' "$u" | sed 's/^/sacct unended: /' >&2; echo "FENCE REFUSED: an unended cov2d/t2a job in sacct" >&2; exit 3; }
echo "sacct cov2d/t2a rows (14 days): $(printf '%s\n' "$s" | awk -F'|' '$2 ~ /^(cov2d|t2a)/' | wc -l), none unended" >&2
echo "FENCE CLEAR" >&2
PY=/global/homes/j/josephrb/.conda/envs/omnifold_py310/bin/python
[ -x "$PY" ] || { echo "STOP: $PY not found" >&2; exit 4; }
"$PY" -I - <<'PYEOF'
import hashlib, io, json, os, sys, tarfile
import numpy as np

OK = True
LOG = []


def log(msg):
    print(msg, file=sys.stderr, flush=True)


def stat3(p):
    s = os.stat(p)
    return (s.st_size, s.st_mtime_ns, s.st_atime_ns)


def read_whole(p):
    """O_NOATIME read of the whole file; returns bytes and a record. Stat must not move."""
    global OK
    s0 = stat3(p)
    fd = os.open(p, os.O_RDONLY | os.O_NOATIME)
    chunks = []
    try:
        while True:
            b = os.read(fd, 1 << 22)
            if not b:
                break
            chunks.append(b)
    finally:
        os.close(fd)
    data = b"".join(chunks)
    s1 = stat3(p)
    rec = {"path": p, "bytes": len(data), "sha256": hashlib.sha256(data).hexdigest(),
           "stat_unchanged": s0 == s1, "whole": len(data) == s0[0]}
    OK &= rec["stat_unchanged"] and rec["whole"]
    log(f"FILE {p} bytes={rec['bytes']} sha256={rec['sha256']} stat_unchanged={rec['stat_unchanged']} whole={rec['whole']}")
    return data, rec


def sha_stream(p):
    """O_NOATIME streamed sha256 of a large file (no copy kept)."""
    global OK
    s0 = stat3(p)
    h, n = hashlib.sha256(), 0
    fd = os.open(p, os.O_RDONLY | os.O_NOATIME)
    try:
        while True:
            b = os.read(fd, 1 << 24)
            if not b:
                break
            h.update(b)
            n += len(b)
    finally:
        os.close(fd)
    s1 = stat3(p)
    rec = {"path": p, "bytes": n, "sha256": h.hexdigest(), "stat_unchanged": s0 == s1, "whole": n == s0[0]}
    OK &= rec["stat_unchanged"] and rec["whole"]
    log(f"FILE {p} bytes={n} sha256={rec['sha256']} stat_unchanged={rec['stat_unchanged']} whole={rec['whole']} (streamed)")
    return rec


out = {}          # tar member name -> bytes
manifest = {"inputs": [], "host": os.uname().nodename}

# A: work_proxy.npz, whole
try:
    WP = "/pscratch/sd/j/josephrb/tmp-playlist-coverage-20261014/work_proxy.npz"
    data, rec = read_whole(WP)
    manifest["inputs"].append(rec)
    out["work_proxy.npz"] = data
except Exception as e:
    log(f"A FAILED {type(e).__name__}: {e}"); OK = False

# B: the 100 assess products -> xtrue_flat, shape
try:
    base = "/pscratch/sd/j/josephrb/s5e-20260925/runs/cand/assess"
    sets = {"nominal": ("nominal_a0_s", range(800000, 800040)), "W1": ("eavail_shape_a1_s", range(803000, 803020)),
            "W2": ("ratio_nd_a1_s", range(804000, 804020)), "W3": ("ratio_nd_a1_s", range(805000, 805020))}
    arrs, metas = {}, {}
    for k, (stem, seeds) in sets.items():
        xt, sh = [], []
        for sd in seeds:
            p = f"{base}/{k}/{stem}{sd}.npz"
            data, rec = read_whole(p)
            manifest["inputs"].append(rec)
            z = np.load(io.BytesIO(data), allow_pickle=False)
            xt.append(np.asarray(z["xtrue_flat"], float))
            sh.append(np.asarray(z["shape"]))
            if sd == seeds[0]:
                metas[k] = {"keys": sorted(z.files), "meta": str(z["meta"]) if "meta" in z.files else None}
        arrs[f"{k}__xtrue_flat"] = np.stack(xt)
        arrs[f"{k}__shape"] = np.stack(sh)
        arrs[f"{k}__seeds"] = np.asarray(list(seeds))
        log(f"B {k}: {len(xt)} products, xtrue_flat shape {arrs[f'{k}__xtrue_flat'].shape}, "
            f"max |xtrue - xtrue[0]| over seeds = {float(np.abs(arrs[f'{k}__xtrue_flat'] - arrs[f'{k}__xtrue_flat'][0]).max())}")
    buf = io.BytesIO(); np.savez(buf, **arrs); out["w_truth.npz"] = buf.getvalue()
    out["w_truth_meta.json"] = json.dumps(metas, indent=1).encode()
except Exception as e:
    log(f"B FAILED {type(e).__name__}: {e}"); OK = False

# C: OF5D window and grid fractions (r4_migration.py masks), weighted and unweighted
try:
    OF = "/pscratch/sd/j/josephrb/MINERvA-OmniFold/nd-unfolding/of_inputs_5d.npz"
    manifest["inputs"].append(sha_stream(OF))
    s0 = stat3(OF)
    fd = os.open(OF, os.O_RDONLY | os.O_NOATIME)
    with os.fdopen(fd, "rb") as fh:
        d = np.load(fh, allow_pickle=False)
        edges = [np.asarray(d[f"edges_{i}"], float) for i in range(5)]
        pr = np.asarray(d["pass_reco"], bool)
        w = np.asarray(d["w_reco"], float)[pr]
        reco = d["MCreco"][pr]
        inr = np.ones(pr.sum(), bool)
        for k, e in enumerate(edges):
            inr &= (reco[:, k] >= e[0]) & (reco[:, k] < e[-1])
        del reco
        gen = d["MCgen"][pr]
        ing = np.ones(pr.sum(), bool)
        for k, e in enumerate(edges):
            ing &= (gen[:, k] >= e[0]) & (gen[:, k] <= e[-1])
        del gen
    s1 = stat3(OF)
    OK &= s0 == s1
    W = float(w.sum())
    C = {"n_pass_reco": int(pr.sum()), "n_rows": int(pr.size), "sum_w_reco_pass_reco": W,
         "frac_reco_in_window_unweighted": float(inr.mean()), "frac_gen_in_grid_unweighted": float(ing.mean()),
         "frac_reco_in_window_weighted": float(w[inr].sum() / W), "frac_gen_in_grid_weighted": float(w[ing].sum() / W),
         "sum_w_reco_outside_window": float(w[~inr].sum()), "sum_w_reco_gen_outside_grid": float(w[~ing].sum()),
         "n_reco_outside_window": int((~inr).sum()), "n_gen_outside_grid": int((~ing).sum()),
         "n_zero_weight_outside_window": int(((~inr) & (w == 0)).sum()),
         "control_r4": {"frac_reco_in_window": 0.9999790240210246, "frac_gen_in_grid": 0.9999139886843416},
         "stat_unchanged_np_load": s0 == s1}
    C["control_r4_match"] = (abs(C["frac_reco_in_window_unweighted"] - 0.9999790240210246) < 1e-12
                             and abs(C["frac_gen_in_grid_unweighted"] - 0.9999139886843416) < 1e-12)
    OK &= C["control_r4_match"]
    log("C " + json.dumps(C))
    out["f53.json"] = json.dumps(C, indent=1).encode()
except Exception as e:
    log(f"C FAILED {type(e).__name__}: {e}"); OK = False

manifest["ok"] = bool(OK)
out["manifest.json"] = json.dumps(manifest, indent=1).encode()
tf = tarfile.open(fileobj=sys.stdout.buffer, mode="w|", format=tarfile.PAX_FORMAT)
for n, b in out.items():
    ti = tarfile.TarInfo(n); ti.size, ti.mode = len(b), 0o600
    tf.addfile(ti, io.BytesIO(b))
tf.close(); sys.stdout.buffer.flush()
log("SESSION " + ("OK" if OK else "FAILED"))
sys.exit(0 if OK else 4)
PYEOF

#!/bin/bash
# #977 row 4.2 split probe, the remote half, on a Perlmutter login node (pattern: pscr_remote.sh 9513d080, approved
# 2026-11-12). From a /dev/shm copy of itself ($1), deleted at exit. Step 0: the cov2d fence (squeue/sacct only; any
# cov2d/t2a job queued, running or unended in 14 days, or either command failing -> exit 3, nothing read). Then one
# python process. Inputs: ONLY the twelve May per-playlist event-loop files and the coverage run's work_proxy.npz;
# never the merged CV or $UNI. Every open is by explicit path with O_NOATIME, stat (size, mtime, atime) before and
# after, sha256 of the bytes read. Nothing is written on the cluster except this script's /dev/shm copy; the products
# leave as one in-memory tar on stdout; logs go to stderr.
#   (a) For each file: mc_background's branch names (uproot on an O_NOATIME file object). If any file lacks one of
#       bkg_nuPDG, bkg_current, bkg_vtx_x, bkg_vtx_y, bkg_vtx_z: exit 6 (STOP), no branch data read.
#   (b) Reads sim_background, sim_background_pz, sim_background_pass, w_bkg and those five, rows with
#       sim_background_pass == 1. Out-of-phase-space signal (the event loop skips signal inside the phase space, so
#       a nu_mu CC row inside the fiducial volume has failed the muon cuts): bkg_nuPDG == 14, bkg_current == 1,
#       5980 < z < 8422 mm and inside the 850 mm-apothem hexagon. The hexagon is bracketed by radius, without
#       assuming MAT's code: inner r < 850 (inside it), outer r < 850*2/sqrt(3) (contains it). Genuine = the rest.
#       If no file has any out-of-phase-space row under the OUTER bracket: exit 7 (STOP).
#   (c) Per playlist, w_bkg histograms on the 14 x 16 analysis grid (proxy_hists.py's edges and np.histogram2d) of
#       all rows, OOPS-inner, OOPS-outer. CONTROL, per playlist, a STOP (exit 5) on failure: the recomputed all-rows
#       histogram equals work_proxy's <PL>__ana__B to 1e-12 relative (of its largest cell), and OOPS + genuine
#       = all rows to the same tolerance under both brackets.
# Exit 0 only if every input was read whole with stat unchanged and every control passed.
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
import hashlib, io, json, math, os, sys, tarfile
import numpy as np
import uproot

D = "/pscratch/sd/j/josephrb/MINERvA-OmniFold/2d-unfolding"
WP = "/pscratch/sd/j/josephrb/tmp-playlist-coverage-20261014/work_proxy.npz"
PLS = ["1A", "1B", "1C", "1D", "1E", "1F", "1G", "1L", "1M", "1N", "1O", "1P"]
PT = np.array([0, 0.07, 0.15, 0.25, 0.33, 0.40, 0.47, 0.55, 0.70, 0.85, 1.00, 1.25, 1.50, 2.50, 4.50])
PZ = np.array([1.5, 2.0, 2.5, 3.0, 3.5, 4.0, 4.5, 5.0, 6.0, 7.0, 8.0, 9.0, 10.0, 15.0, 20.0, 40.0, 60.0])
NEED = ["bkg_nuPDG", "bkg_current", "bkg_vtx_x", "bkg_vtx_y", "bkg_vtx_z"]
READ = ["sim_background", "sim_background_pz", "sim_background_pass", "w_bkg"] + NEED
A, ZLO, ZHI = 850.0, 5980.0, 8422.0
RTOL = 1e-12
OK = True


def log(m):
    print(m, file=sys.stderr, flush=True)


def stat3(p):
    s = os.stat(p); return (s.st_size, s.st_mtime_ns, s.st_atime_ns)


def sha_stream(p):
    global OK
    s0 = stat3(p); h, n = hashlib.sha256(), 0
    fd = os.open(p, os.O_RDONLY | os.O_NOATIME)
    try:
        while True:
            b = os.read(fd, 1 << 24)
            if not b:
                break
            h.update(b); n += len(b)
    finally:
        os.close(fd)
    s1 = stat3(p)
    r = {"path": p, "bytes": n, "sha256": h.hexdigest(), "stat_unchanged": s0 == s1, "whole": n == s0[0],
         "mtime_utc": __import__("datetime").datetime.utcfromtimestamp(s0[1] / 1e9).strftime("%Y-%m-%dT%H:%M:%SZ")}
    OK &= r["stat_unchanged"] and r["whole"]
    log(f"FILE {p} bytes={n} sha256={r['sha256']} stat_unchanged={r['stat_unchanged']} whole={r['whole']} mtime={r['mtime_utc']}")
    return r


class Watch:
    """An O_NOATIME file object for uproot, with stat before and after."""
    def __init__(self, p):
        self.p, self.s0 = p, stat3(p)
        self.fh = os.fdopen(os.open(p, os.O_RDONLY | os.O_NOATIME), "rb")

    def close(self):
        global OK
        self.fh.close(); same = stat3(self.p) == self.s0; OK &= same
        log(f"READ {self.p} stat_unchanged={same}")
        return same


out, man = {}, {"inputs": [], "host": os.uname().nodename}


def finish(code, why):
    man["ok"], man["exit"], man["why"] = bool(OK and code == 0), code, why
    out["manifest.json"] = json.dumps(man, indent=1).encode()
    tf = tarfile.open(fileobj=sys.stdout.buffer, mode="w|", format=tarfile.PAX_FORMAT)
    for n, b in out.items():
        ti = tarfile.TarInfo(n); ti.size, ti.mode = len(b), 0o600; tf.addfile(ti, io.BytesIO(b))
    tf.close(); sys.stdout.buffer.flush()
    log(f"SPLIT {'OK' if man['ok'] else 'STOP'} exit={code} {why}")
    sys.exit(code if code else (0 if OK else 4))


try:
    for pl in PLS:
        man["inputs"].append(sha_stream(f"{D}/runEventLoopOmniFold_{pl}.root"))
    man["inputs"].append(sha_stream(WP))
    # (a)
    branches = {}
    for pl in PLS:
        w = Watch(f"{D}/runEventLoopOmniFold_{pl}.root")
        with uproot.open(w.fh) as f:
            branches[pl] = sorted(f["mc_background"].keys())
        w.close()
    out["branches.json"] = json.dumps(branches, indent=1).encode()
    missing = {pl: [b for b in NEED + READ[:4] if b not in branches[pl]] for pl in PLS}
    missing = {k: v for k, v in missing.items() if v}
    log("A branches missing: " + json.dumps(missing))
    if missing:
        finish(6, "probe (a): bkg_* branches absent in " + ",".join(missing))
    # (b), (c)
    w = Watch(WP); wp = np.load(w.fh, allow_pickle=False); WPB = {pl: np.asarray(wp[f"{pl}__ana__B"], float) for pl in PLS}; w.close()
    H, summ, any_oops = {}, {}, False
    for pl in PLS:
        w = Watch(f"{D}/runEventLoopOmniFold_{pl}.root")
        with uproot.open(w.fh) as f:
            t = f["mc_background"].arrays(READ, library="np")
        w.close()
        m = t["sim_background_pass"].astype(int) == 1
        x, y, wt = t["sim_background"][m], t["sim_background_pz"][m], t["w_bkg"][m]
        cc = (t["bkg_nuPDG"][m] == 14) & (t["bkg_current"][m] == 1)
        z = t["bkg_vtx_z"][m]; r = np.hypot(t["bkg_vtx_x"][m], t["bkg_vtx_y"][m])
        inz = (z > ZLO) & (z < ZHI)
        o_in, o_out = cc & inz & (r < A), cc & inz & (r < A * 2 / math.sqrt(3))
        h = lambda s: np.histogram2d(x[s], y[s], [PT, PZ], weights=wt[s])[0]
        allh = np.histogram2d(x, y, [PT, PZ], weights=wt)[0]
        hi, ho, gi, go = h(o_in), h(o_out), h(~o_in), h(~o_out)
        sc = float(np.abs(WPB[pl]).max())
        c = {"all_vs_work_proxy_max_abs": float(np.abs(allh - WPB[pl]).max()),
             "split_inner_max_abs": float(np.abs(hi + gi - allh).max()),
             "split_outer_max_abs": float(np.abs(ho + go - allh).max()), "scale": sc}
        c["pass"] = all(v <= RTOL * sc for k, v in c.items() if k.endswith("max_abs"))
        H[f"{pl}__all"], H[f"{pl}__oops_inner"], H[f"{pl}__oops_outer"] = allh, hi, ho
        summ[pl] = {"rows": int(m.sum()), "cc_numu_rows": int(cc.sum()), "oops_inner_rows": int(o_in.sum()),
                    "oops_outer_rows": int(o_out.sum()), "annulus_rows": int((o_out & ~o_in).sum()),
                    "sum_w_all": float(wt.sum()), "sum_w_oops_inner": float(wt[o_in].sum()),
                    "sum_w_oops_outer": float(wt[o_out].sum()), "control": c}
        any_oops |= bool(o_out.any())
        log(f"C {pl} " + json.dumps(summ[pl]))
    buf = io.BytesIO(); np.savez(buf, **H); out["split_hists.npz"] = buf.getvalue()
    out["split_summary.json"] = json.dumps(summ, indent=1).encode()
    if not all(s["control"]["pass"] for s in summ.values()):
        finish(5, "control: a recomputed or split histogram differs from work_proxy B")
    if not any_oops:
        finish(7, "probe (b): no out-of-phase-space signal row in mc_background under the outer bracket")
    finish(0, "ok")
except SystemExit:
    raise
except Exception as e:
    OK = False
    log(f"FAILED {type(e).__name__}: {e}")
    finish(4, f"exception {type(e).__name__}")
PYEOF

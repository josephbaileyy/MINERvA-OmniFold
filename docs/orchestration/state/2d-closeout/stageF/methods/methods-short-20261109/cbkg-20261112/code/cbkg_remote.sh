#!/bin/bash
# #977 C-BKG: the composition of the paper's background template, on 1A (the director, 2026-11-12; inputs from
# tier3-design). Pattern: split_remote.sh 6784499d (approved 2026-11-12). From a /dev/shm copy of itself ($1), deleted at
# exit. Step 0: the cov2d fence (squeue/sacct only; exit 3, nothing read, on any cov2d/t2a job or a failed command).
# Inputs, two only, each by explicit path with O_NOATIME, stat (size, mtime, atime) before and after, sha256 streamed:
#   base_cv.root  MP-1 S0's unmodified-binary 1A event loop (job 60017651; pin c76256a4..., mp1s0_base_cv_60017651.out:831),
#                 whose mc_background r4_prod_vs_base_cv.json shows identical to production's on 1A's 52,626 rows;
#   work_proxy.npz the coverage run's per-playlist templates (pin 42ce788b..., coverage.json:7-9).
#   (a) mc_background's branch names; any of bkg_nuPDG, bkg_current, bkg_vtx_x/y/z or the producer's four missing:
#       exit 6, no branch data read.
#   CONTROL (a STOP, exit 5): proxy_hists.py's rule (:53-54, :59): rows with sim_background_pass == 1, weight w_bkg,
#       np.histogram2d on the 14 x 16 analysis grid; must equal work_proxy's 1A__ana__B to 1e-12 of its largest cell.
#       That ties base_cv to the paper's template. A failure reads "current code with current runtime inputs
#       (MParamFiles, flux) does not reproduce the May template", not "code alone" (tier3-design, 2026-11-12).
#   (b) Classes of the passing rows: CC nu_mu (bkg_nuPDG == 14, bkg_current == 1) inside the fiducial volume
#       (5980 < z < 8422 mm and inside the 850 mm-apothem hexagon) = out-of-phase-space signal (the event loop skips
#       signal inside the phase space); CC nu_mu outside it = genuine, out-of-fiducial; all other = genuine, other
#       flavor/sign/NC. The hexagon is bracketed by radius without assuming MAT's code: inner r < 850, outer
#       r < 850*2/sqrt(3). Weighted (w_bkg) and raw fractions of each class, with per-class 14 x 16 histograms, and the
#       closure genuine + OOPS = all to 1e-12 under both brackets (exit 5 otherwise). No OOPS row under the outer
#       bracket: exit 7.
# Nothing is written on the cluster except this /dev/shm copy; the products leave as an in-memory tar on stdout.
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
import datetime, hashlib, io, json, math, os, sys, tarfile
import numpy as np
import uproot

BCV = "/pscratch/sd/j/josephrb/measurement-paper/phase1/mp1/s0/evloop/base_cv.root"
BCV_PIN = "c76256a495d2deb7c213c2f8203b284bea640d90e697c495f5e11cedc830846b"
WP = "/pscratch/sd/j/josephrb/tmp-playlist-coverage-20261014/work_proxy.npz"
WP_PIN = "42ce788bb28919c098041f14b5a4fb8b22aca06aa7f962ca38dd398149f23621"
PT = np.array([0, 0.07, 0.15, 0.25, 0.33, 0.40, 0.47, 0.55, 0.70, 0.85, 1.00, 1.25, 1.50, 2.50, 4.50])
PZ = np.array([1.5, 2.0, 2.5, 3.0, 3.5, 4.0, 4.5, 5.0, 6.0, 7.0, 8.0, 9.0, 10.0, 15.0, 20.0, 40.0, 60.0])
NEED = ["sim_background", "sim_background_pz", "sim_background_pass", "w_bkg",
        "bkg_nuPDG", "bkg_current", "bkg_vtx_x", "bkg_vtx_y", "bkg_vtx_z"]
A, ZLO, ZHI, RTOL = 850.0, 5980.0, 8422.0, 1e-12
OK = True
out, man = {}, {"inputs": [], "host": os.uname().nodename}


def log(m):
    print(m, file=sys.stderr, flush=True)


def stat3(p):
    s = os.stat(p); return (s.st_size, s.st_mtime_ns, s.st_atime_ns)


def sha_stream(p, pin):
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
    r = {"path": p, "bytes": n, "sha256": h.hexdigest(), "pin_ok": h.hexdigest() == pin, "stat_unchanged": s0 == s1,
         "whole": n == s0[0], "mtime_utc": datetime.datetime.utcfromtimestamp(s0[1] / 1e9).strftime("%Y-%m-%dT%H:%M:%SZ")}
    OK &= r["stat_unchanged"] and r["whole"] and r["pin_ok"]
    log(f"FILE {p} bytes={n} sha256={r['sha256']} pin_ok={r['pin_ok']} stat_unchanged={r['stat_unchanged']} whole={r['whole']}")
    return r


class Watch:
    def __init__(self, p):
        self.p, self.s0 = p, stat3(p)
        self.fh = os.fdopen(os.open(p, os.O_RDONLY | os.O_NOATIME), "rb")

    def close(self):
        global OK
        self.fh.close(); same = stat3(self.p) == self.s0; OK &= same
        log(f"READ {self.p} stat_unchanged={same}")


def finish(code, why):
    man["ok"], man["exit"], man["why"] = bool(OK and code == 0), code, why
    out["manifest.json"] = json.dumps(man, indent=1).encode()
    tf = tarfile.open(fileobj=sys.stdout.buffer, mode="w|", format=tarfile.PAX_FORMAT)
    for n, b in out.items():
        ti = tarfile.TarInfo(n); ti.size, ti.mode = len(b), 0o600; tf.addfile(ti, io.BytesIO(b))
    tf.close(); sys.stdout.buffer.flush()
    log(f"CBKG {'OK' if man['ok'] else 'STOP'} exit={code} {why}")
    sys.exit(code if code else (0 if OK else 4))


try:
    man["inputs"].append(sha_stream(BCV, BCV_PIN))
    man["inputs"].append(sha_stream(WP, WP_PIN))
    if not OK:
        finish(4, "an input failed its pin, stat or whole check")
    w = Watch(BCV)
    with uproot.open(w.fh) as f:
        br = sorted(f["mc_background"].keys())
    w.close()
    out["branches.json"] = json.dumps({"1A_base_cv": br}, indent=1).encode()
    missing = [b for b in NEED if b not in br]
    log("A branches missing: " + json.dumps(missing))
    if missing:
        finish(6, "probe (a): branches absent: " + ",".join(missing))
    w = Watch(WP); wp = np.load(w.fh, allow_pickle=False); WPB = np.asarray(wp["1A__ana__B"], float); w.close()
    w = Watch(BCV)
    with uproot.open(w.fh) as f:
        t = f["mc_background"].arrays(NEED, library="np")
    w.close()
    m = t["sim_background_pass"].astype(int) == 1
    x, y, wt = t["sim_background"][m], t["sim_background_pz"][m], t["w_bkg"][m]
    allh = np.histogram2d(x, y, [PT, PZ], weights=wt)[0]
    sc = float(np.abs(WPB).max())
    ctl = {"rows": int(m.sum()), "rows_total": int(m.size), "max_abs_diff_vs_work_proxy": float(np.abs(allh - WPB).max()),
           "scale": sc, "sum_w_in_grid": float(allh.sum()), "sum_w_work_proxy": float(WPB.sum())}
    ctl["pass"] = ctl["max_abs_diff_vs_work_proxy"] <= RTOL * sc
    log("CONTROL " + json.dumps(ctl))
    if not ctl["pass"]:
        out["control.json"] = json.dumps(ctl, indent=1).encode()
        finish(5, "control: base_cv's recomputed 1A template differs from work_proxy's 1A B")
    cc = (t["bkg_nuPDG"][m] == 14) & (t["bkg_current"][m] == 1)
    z = t["bkg_vtx_z"][m]; r = np.hypot(t["bkg_vtx_x"][m], t["bkg_vtx_y"][m]); inz = (z > ZLO) & (z < ZHI)
    ingrid = (x >= PT[0]) & (x <= PT[-1]) & (y >= PZ[0]) & (y <= PZ[-1])
    res, H = {"control": ctl}, {"all": allh}
    for brk, rad in (("inner", A), ("outer", A * 2 / math.sqrt(3))):
        oops = cc & inz & (r < rad)
        oofv = cc & ~(inz & (r < rad))
        other = ~cc
        h = {k: np.histogram2d(x[s], y[s], [PT, PZ], weights=wt[s])[0] for k, s in (("oops", oops), ("cc_oofv", oofv), ("other", other))}
        clos = float(np.abs(h["oops"] + h["cc_oofv"] + h["other"] - allh).max())
        Wg = allh.sum()
        res[brk] = {"frac_w_oops": float(h["oops"].sum() / Wg), "frac_w_cc_out_of_fiducial": float(h["cc_oofv"].sum() / Wg),
                    "frac_w_other_flavor_sign_nc": float(h["other"].sum() / Wg),
                    "rows_oops": int((oops & ingrid).sum()), "rows_cc_oofv": int((oofv & ingrid).sum()), "rows_other": int((other & ingrid).sum()),
                    "closure_max_abs": clos, "closure_pass": clos <= RTOL * sc}
        H.update({f"{brk}__{k}": v for k, v in h.items()})
        log(f"B {brk} " + json.dumps(res[brk]))
    res["annulus_frac_w"] = res["outer"]["frac_w_oops"] - res["inner"]["frac_w_oops"]
    buf = io.BytesIO(); np.savez(buf, **H); out["cbkg_hists.npz"] = buf.getvalue()
    out["cbkg_summary.json"] = json.dumps(res, indent=1).encode()
    if not (res["inner"]["closure_pass"] and res["outer"]["closure_pass"]):
        finish(5, "closure: genuine + OOPS != all")
    if res["outer"]["rows_oops"] == 0:
        finish(7, "probe (b): no out-of-phase-space row under the outer bracket")
    finish(0, "ok")
except SystemExit:
    raise
except Exception as e:
    OK = False
    log(f"FAILED {type(e).__name__}: {e}")
    finish(4, f"exception {type(e).__name__}")
PYEOF

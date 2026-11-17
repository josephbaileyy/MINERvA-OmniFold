#!/bin/bash
# #977 C-BKG-2: the analysis's own fiducial test, read from source, and the 1A template's classes with it (the director,
# 2026-11-12, combining options (a) and (b) of the bracket STOP). Pattern: cbkg_remote.sh d78340d2 (approved). From a
# /dev/shm copy of itself ($1), deleted at exit. Step 0: the cov2d fence, plus a STOP (exit 3) if an rpd_ job is
# queued or running (#848's resolved policy listed both MAT trees as protected for RPD-RECO's flux stage).
# Part 1, source (read-only, O_NOATIME, stat before/after, sha256 of each file read): under the two MAT trees and the
# install include directory (MINERvA101/{MAT, MAT-MINERvA, opt/include}), a directory listing finds every file named
# CCInclusiveSignal.h, TargetUtils.cxx or TargetUtils.h; each is read whole and only EXCERPTS leave: the definitions of
# truth::Apothem and truth::ZRange (CCInclusiveSignal.h) and of IsInHexagon (TargetUtils.*), with line numbers. Each
# tree's revision is read from .git/HEAD and the ref it names (or packed-refs) by O_NOATIME, never by running git.
# Part 2, classes: as cbkg_remote.sh (base_cv c76256a4, work_proxy 42ce788b; the producer's rule reproduces work_proxy's
# 1A__ana__B to 1e-12, else exit 5), but the fiducial test is port 1, nd-unfolding/bkg_channel_split.py:58-70
# ("a bit-for-bit port of truth::ZRange::checkConstraint and truth::Apothem::checkConstraint in CCInclusiveSignal.h"):
# 5980 <= z <= 8422 and |x| < 850 and |y| < -|x|/sqrt(3) + 2*850/sqrt(3). Classes: out-of-phase-space = nu_mu CC in it;
# genuine = nu_mu CC outside it, and other flavor/sign/NC. Closure to 1e-12 (exit 5). The rows whose class changes when
# the apothem and the z limits move by +-1 mm are counted (raw and weighted), bounding the < against <= difference.
# Nothing is written on the cluster except this /dev/shm copy; products leave as an in-memory tar on stdout.
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
if printf "%s\n" "$q" | awk -F"|" '$2 ~ /^rpd_/ && $3 ~ /^(PENDING|RUNNING|CONFIGURING|COMPLETING|SUSPENDED|REQUEUED|RESIZING)$/ {f=1} END {exit !f}'; then echo "FENCE REFUSED: an rpd_ job is queued or running (#848 MAT-tree protection)" >&2; exit 3; fi
echo "rpd_ jobs: none queued or running" >&2
echo "FENCE CLEAR" >&2
PY=/global/homes/j/josephrb/.conda/envs/omnifold_py310/bin/python
[ -x "$PY" ] || { echo "STOP: $PY not found" >&2; exit 4; }
"$PY" -I - <<'PYEOF'
import hashlib, io, json, math, os, re, sys, tarfile
import numpy as np
import uproot

ROOT101 = "/pscratch/sd/j/josephrb/MINERvA-OmniFold/MINERvA101"
TREES = ["MAT", "MAT-MINERvA"]
SEARCH = [f"{ROOT101}/MAT", f"{ROOT101}/MAT-MINERvA", f"{ROOT101}/opt/include"]
NAMES = {"CCInclusiveSignal.h", "TargetUtils.cxx", "TargetUtils.h"}
BCV = "/pscratch/sd/j/josephrb/measurement-paper/phase1/mp1/s0/evloop/base_cv.root"
BCV_PIN = "c76256a495d2deb7c213c2f8203b284bea640d90e697c495f5e11cedc830846b"
WP = "/pscratch/sd/j/josephrb/tmp-playlist-coverage-20261014/work_proxy.npz"
WP_PIN = "42ce788bb28919c098041f14b5a4fb8b22aca06aa7f962ca38dd398149f23621"
PT = np.array([0, 0.07, 0.15, 0.25, 0.33, 0.40, 0.47, 0.55, 0.70, 0.85, 1.00, 1.25, 1.50, 2.50, 4.50])
PZ = np.array([1.5, 2.0, 2.5, 3.0, 3.5, 4.0, 4.5, 5.0, 6.0, 7.0, 8.0, 9.0, 10.0, 15.0, 20.0, 40.0, 60.0])
NEED = ["sim_background", "sim_background_pz", "sim_background_pass", "w_bkg",
        "bkg_nuPDG", "bkg_current", "bkg_vtx_x", "bkg_vtx_y", "bkg_vtx_z"]
MINZ, MAXZ, A, RTOL = 5980.0, 8422.0, 850.0, 1e-12
OK = True
out, man = {}, {"inputs": [], "host": os.uname().nodename}


def log(m):
    print(m, file=sys.stderr, flush=True)


def stat3(p):
    s = os.stat(p); return (s.st_size, s.st_mtime_ns, s.st_atime_ns)


def read_whole(p):
    global OK
    s0 = stat3(p); fd = os.open(p, os.O_RDONLY | os.O_NOATIME); chunks = []
    try:
        while True:
            b = os.read(fd, 1 << 24)
            if not b:
                break
            chunks.append(b)
    finally:
        os.close(fd)
    data = b"".join(chunks); same = stat3(p) == s0; OK &= same and len(data) == s0[0]
    log(f"FILE {p} bytes={len(data)} sha256={hashlib.sha256(data).hexdigest()} stat_unchanged={same}")
    return data, {"path": p, "bytes": len(data), "sha256": hashlib.sha256(data).hexdigest(), "stat_unchanged": same,
                  "whole": len(data) == s0[0]}


def sha_stream(p, pin):
    global OK
    s0 = stat3(p); h, n = hashlib.sha256(), 0; fd = os.open(p, os.O_RDONLY | os.O_NOATIME)
    try:
        while True:
            b = os.read(fd, 1 << 24)
            if not b:
                break
            h.update(b); n += len(b)
    finally:
        os.close(fd)
    r = {"path": p, "bytes": n, "sha256": h.hexdigest(), "pin_ok": h.hexdigest() == pin, "stat_unchanged": s0 == stat3(p), "whole": n == s0[0]}
    OK &= r["pin_ok"] and r["stat_unchanged"] and r["whole"]
    log(f"FILE {p} bytes={n} sha256={r['sha256']} pin_ok={r['pin_ok']} stat_unchanged={r['stat_unchanged']}")
    return r


class Watch:
    def __init__(self, p):
        self.p, self.s0 = p, stat3(p); self.fh = os.fdopen(os.open(p, os.O_RDONLY | os.O_NOATIME), "rb")

    def close(self):
        global OK
        self.fh.close(); same = stat3(self.p) == self.s0; OK &= same; log(f"READ {self.p} stat_unchanged={same}")


def excerpt(text, pattern, maxlines=60):
    """Lines from each match of pattern through the matching closing brace (brace count), with 1-based line numbers."""
    lines = text.split("\n"); res = []
    for i, l in enumerate(lines):
        if re.search(pattern, l):
            depth, started, j, block = 0, False, i, []
            while j < len(lines) and len(block) < maxlines:
                block.append((j + 1, lines[j])); depth += lines[j].count("{") - lines[j].count("}")
                started |= "{" in lines[j]
                if started and depth <= 0:
                    break
                j += 1
            res.append(block)
    return res


def finish(code, why):
    man["ok"], man["exit"], man["why"] = bool(OK and code == 0), code, why
    out["manifest.json"] = json.dumps(man, indent=1).encode()
    tf = tarfile.open(fileobj=sys.stdout.buffer, mode="w|", format=tarfile.PAX_FORMAT)
    for n, b in out.items():
        ti = tarfile.TarInfo(n); ti.size, ti.mode = len(b), 0o600; tf.addfile(ti, io.BytesIO(b))
    tf.close(); sys.stdout.buffer.flush()
    log(f"MATBKG {'OK' if man['ok'] else 'STOP'} exit={code} {why}")
    sys.exit(code if code else (0 if OK else 4))


try:
    # Part 1: the source
    src = {"files": [], "revisions": {}}
    for root in SEARCH:
        if not os.path.isdir(root):
            src["files"].append({"search_root": root, "missing": True}); continue
        for dp, dn, fn in os.walk(root):
            dn[:] = [d for d in dn if d != ".git"]
            for f in fn:
                if f in NAMES:
                    p = os.path.join(dp, f)
                    data, rec = read_whole(p); text = data.decode("utf-8", "replace")
                    if f == "CCInclusiveSignal.h":
                        rec["excerpts"] = {"Apothem": excerpt(text, r"\b(class|struct)\s+Apothem\b"),
                                           "ZRange": excerpt(text, r"\b(class|struct)\s+ZRange\b"),
                                           "namespace_truth_lines": [i + 1 for i, l in enumerate(text.split("\n")) if re.search(r"namespace\s+truth", l)]}
                    else:
                        rec["excerpts"] = {"IsInHexagon": excerpt(text, r"IsInHexagon\s*\(")}
                    src["files"].append(rec)
    for tname in TREES:
        g = f"{ROOT101}/{tname}/.git"
        r = {"git_dir": g}
        try:
            if os.path.isfile(g):                    # a worktree/submodule pointer file
                r["gitfile"] = read_whole(g)[0].decode().strip()
            else:
                head = read_whole(f"{g}/HEAD")[0].decode().strip(); r["HEAD"] = head
                if head.startswith("ref: "):
                    ref = head[5:]
                    if os.path.exists(f"{g}/{ref}"):
                        r["ref_sha"] = read_whole(f"{g}/{ref}")[0].decode().strip()
                    elif os.path.exists(f"{g}/packed-refs"):
                        pr = read_whole(f"{g}/packed-refs")[0].decode()
                        r["ref_sha"] = next((l.split()[0] for l in pr.split("\n") if l.endswith(" " + ref)), None)
                else:
                    r["ref_sha"] = head
        except Exception as e:
            r["error"] = f"{type(e).__name__}: {e}"
        src["revisions"][tname] = r
    out["mat_source.json"] = json.dumps(src, indent=1).encode()
    log("SOURCE " + json.dumps({"files": [f.get("path", f.get("search_root")) for f in src["files"]], "revisions": src["revisions"]}))
    # Part 2: the classes with port 1
    man["inputs"].append(sha_stream(BCV, BCV_PIN)); man["inputs"].append(sha_stream(WP, WP_PIN))
    if not OK:
        finish(4, "an input failed its pin, stat or whole check")
    w = Watch(BCV)
    with uproot.open(w.fh) as f:
        br = sorted(f["mc_background"].keys())
    w.close()
    missing = [b for b in NEED if b not in br]
    if missing:
        finish(6, "branches absent: " + ",".join(missing))
    w = Watch(WP); WPB = np.asarray(np.load(w.fh, allow_pickle=False)["1A__ana__B"], float); w.close()
    w = Watch(BCV)
    with uproot.open(w.fh) as f:
        t = f["mc_background"].arrays(NEED, library="np")
    w.close()
    m = t["sim_background_pass"].astype(int) == 1
    x, y, wt = t["sim_background"][m], t["sim_background_pz"][m], t["w_bkg"][m]
    allh = np.histogram2d(x, y, [PT, PZ], weights=wt)[0]
    sc = float(np.abs(WPB).max())
    ctl = {"rows": int(m.sum()), "max_abs_diff_vs_work_proxy": float(np.abs(allh - WPB).max()), "scale": sc}
    ctl["pass"] = ctl["max_abs_diff_vs_work_proxy"] <= RTOL * sc
    log("CONTROL " + json.dumps(ctl))
    if not ctl["pass"]:
        finish(5, "control: base_cv's 1A template differs from work_proxy's")
    cc = (t["bkg_nuPDG"][m] == 14) & (t["bkg_current"][m] == 1)
    vx, vy, vz = t["bkg_vtx_x"][m], t["bkg_vtx_y"][m], t["bkg_vtx_z"][m]
    def fid(a, zlo, zhi):   # port 1 (bkg_channel_split.py:58-70)
        return (vz >= zlo) & (vz <= zhi) & (np.abs(vy) < -np.abs(vx) / math.sqrt(3.0) + 2.0 * a / math.sqrt(3.0)) & (np.abs(vx) < a)
    f0, fin, fout = fid(A, MINZ, MAXZ), fid(A - 1, MINZ + 1, MAXZ - 1), fid(A + 1, MINZ - 1, MAXZ + 1)
    ingrid = (x >= PT[0]) & (x <= PT[-1]) & (y >= PZ[0]) & (y <= PZ[-1])
    oops, oofv, other = cc & f0, cc & ~f0, ~cc
    H = {"all": allh, **{k: np.histogram2d(x[s], y[s], [PT, PZ], weights=wt[s])[0] for k, s in (("oops", oops), ("cc_oofv", oofv), ("other", other))}}
    clos = float(np.abs(H["oops"] + H["cc_oofv"] + H["other"] - allh).max())
    Wg = allh.sum()
    near = cc & (fout & ~fin) & ingrid       # nu_mu CC whose class can change within +-1 mm
    near_h = np.histogram2d(x[near], y[near], [PT, PZ], weights=wt[near])[0]
    res = {"control": ctl, "port": "nd-unfolding/bkg_channel_split.py:58-70",
           "frac_w_oops": float(H["oops"].sum() / Wg), "frac_w_cc_out_of_fiducial": float(H["cc_oofv"].sum() / Wg),
           "frac_w_other_flavor_sign_nc": float(H["other"].sum() / Wg),
           "rows_in_grid": int(ingrid.sum()), "rows_oops": int((oops & ingrid).sum()), "rows_cc_oofv": int((oofv & ingrid).sum()),
           "rows_other": int((other & ingrid).sum()), "closure_max_abs": clos, "closure_pass": clos <= RTOL * sc,
           "boundary_1mm": {"rows": int(near.sum()), "frac_w": float(near_h.sum() / Wg)}}
    log("B " + json.dumps(res))
    buf = io.BytesIO(); np.savez(buf, **H); out["cbkg2_hists.npz"] = buf.getvalue()
    out["cbkg2_summary.json"] = json.dumps(res, indent=1).encode()
    if not res["closure_pass"]:
        finish(5, "closure: genuine + OOPS != all")
    finish(0, "ok")
except SystemExit:
    raise
except Exception as e:
    OK = False; log(f"FAILED {type(e).__name__}: {e}"); finish(4, f"exception {type(e).__name__}")
PYEOF

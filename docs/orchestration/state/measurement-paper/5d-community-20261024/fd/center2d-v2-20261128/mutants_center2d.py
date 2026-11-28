"""Mutation runner for CENTER2D: each mutant edits one exact text in a temp-dir copy (never the files in place) and must
make its test suite fail.
- center2d.py mutants run test_center2d.py.
- center2d_fetch_remote.py, center2d_fetch_verify.py and center2d_fence.py mutants run test_center2d_fetch.py's Fetch
  and Fence classes.
- The wrapper center2d_fetch.sh is not mutated: its tests need the git worktree, and it is pinned by sha.
Exit 0 iff the baseline passes and every mutant is killed; 9 if the baseline fails; 8 if a mutant's text does not occur
exactly once; 1 if any mutant survives.

run: python3 -I -B mutants_center2d.py
"""
import hashlib
import os
import shutil
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
FILES = ["center2d.py", "center2d_fetch_remote.py", "center2d_fetch_verify.py", "center2d_fence.py", "center2d_fetch.sh",
         "test_center2d.py", "test_center2d_fetch.py"]
REPO = os.path.abspath(os.path.join(HERE, *[".."] * 7))

C, R, V, F = "center2d.py", "center2d_fetch_remote.py", "center2d_fetch_verify.py", "center2d_fence.py"
MUTANTS = [
    # --- the driver: tolerances, rank bands, labels
    ("tol-loose", C, "TOL = 1e-12          # every", "TOL = 1e-6          # every"),
    ("rank-tol", C, "RANK_TOL = 1e-12     # the retained", "RANK_TOL = 1e-30     # the retained"),
    ("rank-bands", C, "RANK_BANDS = ((1, 73), (74, 139), (140, None))", "RANK_BANDS = ((1, 73), (74, 140), (141, None))"),
    ("s-tr-cut", C, "S_TR_CUT, RANK_CUT = 0.01, 0.10", "S_TR_CUT, RANK_CUT = 0.02, 0.10"),
    ("rank-cut", C, "S_TR_CUT, RANK_CUT = 0.01, 0.10", "S_TR_CUT, RANK_CUT = 0.01, 0.11"),
    ("label-strict", C, "if any(m >= RANK_CUT for m in vals):", "if any(m > RANK_CUT for m in vals):"),
    ("label-empty-counted", C, "vals = [m for m in means if m is not None]", "vals = [1.0 if m is None else m for m in means]"),
    ("empty-band-filled", C, "out.append((lo, hi, None if lo > hi else slice(lo - 1, hi)))",
     "out.append((lo, hi, slice(lo - 1, hi)))"),
    # --- the readings
    ("trace-share-c-sys", C, "s_tr = float(np.trace(M)) / trC", "s_tr = float(np.trace(M)) / float(np.trace(C_sys))"),
    ("r-not-divided", C, 'r = np.einsum("ik,ij,jk->k", Ur, M, Ur) / lr', 'r = np.einsum("ik,ij,jk->k", Ur, M, Ur)'),
    ("eps-min", C, "eps = float(np.linalg.eigvalsh((W + W.T) / 2).max())",
     "eps = float(np.linalg.eigvalsh((W + W.T) / 2).min())"),
    ("all-ranks", C, "Ur, lr = U[:, :ndf], lam[:ndf]", "Ur, lr = U, lam"),
    ("per-cell-wrong", C, "d = np.diag(M) / np.diag(C)", "d = np.diag(M) / np.diag(C_sys)"),
    ("loo-not-removed", C, 's2 = s_tr - per[b]["trace_share"]', "s2 = s_tr"),
    ("top5-ascending", C, 'top = {"trace_share": sorted(bands, key=lambda b: -per[b]["trace_share"])[:5]}',
     'top = {"trace_share": sorted(bands, key=lambda b: per[b]["trace_share"])[:5]}'),
    # --- the quantity
    ("centre-unweighted", C, "    return (w[:, None] * X).sum(axis=0) / w.sum()\n\n\ndef v_nom",
     "    return X.mean(axis=0)\n\n\ndef v_nom"),
    ("minos-not-replaced", C, "X = minos_x if b == MINOS else bands[b]", "X = bands[b]"),
    ("flux-unweighted", C, "w = w_flux if b == flux else np.ones(X.shape[0])", "w = np.ones(X.shape[0])"),
    ("scaled-own-only", C, "s = own if own >= TOL * total else total", "s = own"),
    # --- the controls
    ("c-id-off", C, 'check(ctl, f"C-ID:{tag}", worst <= TOL,', 'check(ctl, f"C-ID:{tag}", True,'),
    ("c-recon-off", C, 'check(ctl, f"C-RECON:{name}", rel <= TOL,', 'check(ctl, f"C-RECON:{name}", True,'),
    ("c-flux-off", C, "w.shape == (100,) and s == lsum and neff == lneff", "w.shape == (100,)"),
    ("c-psd-off", C, 'check(ctl, f"C-PSD:{name}", sym <= TOL and low >= -TOL,', 'check(ctl, f"C-PSD:{name}", True,'),
    ("c-add-off", C, 'check(ctl, f"C-ADD:{tag}", add_tr <= TOL and all(a <= TOL for a in add_r),',
     'check(ctl, f"C-ADD:{tag}", True,'),
    ("c-x0-mask-off", C, 'rep.shape == (NPT * NPZ,) and int(rep.astype(bool).sum()) == NCELL,', "True,"),
    ("tune-x0-off", C, 'np.array_equal(G["x_T"], B["x_T"]) and np.array_equal(G["rep"], B["rep"])', "True"),
    ("tune-laterals-off", C, 'all(np.array_equal(G[f"band__{L}"], B[f"band__{L}"]) for L in lateral)', "True"),
    ("tune-flux-equal-off", C, 'check(ctl, f"C-FLUX:{tag}:equal", np.array_equal(G["w_flux"], B["w_flux"]))',
     'check(ctl, f"C-FLUX:{tag}:equal", True)'),
    ("tune-fetch-off", C, 'check(ctl, f"C-FETCH:{tag}", fst[lab]["pass"], **fst[lab])',
     'check(ctl, f"C-FETCH:{tag}", True, **fst[lab])'),
    ("data-fetch-off", C, 'bad = [k for k in DATA_FILES if not fst[k]["pass"]]', "bad = []"),
    ("data-x0-off", C, "int(rep.sum()) == NCELL and np.array_equal(er[rep], x0)", "int(rep.sum()) == NCELL"),
    ("data-er-pin-off", C, "        if sha_file(er_path) != ER_SHA:", "        if False:"),
    ("data-c-new-vacuous", C, 'recon(ctl, "D:C_new", Qm - old + C_un, C_new)', 'recon(ctl, "D:C_new", C_new, C_new)'),
    ("data-lateral-vacuous", C, 'recon(ctl, f"D:lateral:{L}", vm[L], s5b[L],', 'recon(ctl, f"D:lateral:{L}", s5b[L], s5b[L],'),
    ("data-scale-axis", C, "(H[\"MuonEnergyMINOS\"][u] * scale[u][:, None])", "(H[\"MuonEnergyMINOS\"][u] * scale[u][0])"),
    ("data-lateral-ravel-F", C, 'np.stack([h.ravel(order="C")[rep] for h in H[L]])',
     'np.stack([h.ravel(order="F")[rep] for h in H[L]])'),
    ("fetched-line-off", C, '    if last != [f"VERIFY OK {N_FETCH}"]:', "    if False:"),
    ("fetched-digest-off", C, '"pass": got == want == rows[lab]', '"pass": got is not None'),
    ("main-overwrites", C, "    if os.path.lexists(a.out):", "    if False:"),
    ("part-stop-swallowed", C, 'rec["status"] = "OK" if not bad else "STOP"', 'rec["status"] = "OK"'),
    ("main-rc-swallowed", C, 'return 0 if not bad else 3', 'return 0'),
    # --- the remote reader
    ("remote-atime-off", R, "        if st2.st_atime_ns != st.st_atime_ns:", "        if False:"),
    ("remote-regular-off", R, "    if not stat.S_ISREG(st.st_mode):", "    if False:"),
    ("remote-empty-off", R, "    if st.st_size <= 0:", "    if False:"),
    ("remote-noatime-check-off", R, "    if noatime is None:", "    if False:"),
    ("remote-argv-off", R, "    if len(argv) != 1:", "    if False:"),
    ("remote-n-files", R, "N_FILES = 16", "N_FILES = 15"),
    # --- the verifier
    ("verify-sha-off", V, 'if len(data[n]) != r["size"] or sha(data[n]) != r["sha256"]:', "if False:"),
    ("verify-atime-off", V, '        if r["atime_before"] != r["atime_after"]:', "        if False:"),
    ("verify-committed-off", V, "        if sha(data[n]) != exp[n]:", "        if False:"),
    ("verify-duplicate-off", V, "            if m.name in data:", "            if False:"),
    ("verify-unexpected-off", V, '            if m.name != "MANIFEST.tsv" and m.name not in names:', "            if False:"),
    ("verify-manifest-missing-off", V, '    if "MANIFEST.tsv" not in data:', "    if False:"),
    ("verify-files-dir-exist-ok", V, "    os.mkdir(files)", "    os.makedirs(files, exist_ok=True)"),
    ("verify-label-path-off", V, '            if p[0].startswith("/") or ".." in p[0].split("/"):', "            if False:"),
    ("verify-count-off", V, "    if len(out) != N_FILES:", "    if False:"),
    # --- the fence
    ("fence-all-terminal", F, 'return s in TERMINAL or s == "CANCELLED" or s.startswith("CANCELLED ")', "return True"),
    ("fence-cancelled-by-not-terminal", F, ' or s.startswith("CANCELLED ")', ""),
    ("fence-squeue-not-live", F, "            if live or not terminal(p[2]):", "            if not terminal(p[2]):"),
    ("fence-malformed-ignored", F, '                bad.append(f"{source} malformed: {ln.strip()}")\n', ""),
    ("fence-case-sensitive", F, "if not p[1].strip().lower().startswith(fam):", "if not p[1].strip().startswith(fam):"),
    ("fence-timeout-not-terminal", F, '"TIMEOUT", ', ""),
]


def suite(d: str, target: str) -> int:
    env = dict(os.environ, CENTER2D_REPO=REPO, OMP_NUM_THREADS="1", OPENBLAS_NUM_THREADS="1")
    cmd = [sys.executable, "-I", "-B", "-W", "ignore", "test_center2d.py"] if target == C else \
        [sys.executable, "-I", "-B", "-W", "ignore", "test_center2d_fetch.py", "Fetch", "Fence"]
    return subprocess.run(cmd, cwd=d, env=env, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL).returncode


def copy() -> str:
    d = tempfile.mkdtemp(prefix="center2d-mut-")
    for f in FILES:
        shutil.copy2(os.path.join(HERE, f), d)
    return d


def digests() -> dict:
    out = {}
    for f in FILES:
        with open(os.path.join(HERE, f), "rb") as fh:
            out[f] = hashlib.sha256(fh.read()).hexdigest()
    return out


def main() -> int:
    before = digests()
    print("sources: " + "; ".join(f"{f} {h}" for f, h in before.items()))
    d = copy()
    try:
        base = {t: suite(d, t) for t in (C, R)}
    finally:
        shutil.rmtree(d)
    print(f"baseline: test_center2d rc {base[C]}, test_center2d_fetch Fetch+Fence rc {base[R]}")
    if any(base.values()):
        return 9
    survived = []
    for name, f, old, new in MUTANTS:
        with open(os.path.join(HERE, f)) as fh:
            src = fh.read()
        if src.count(old) != 1:
            print(f"AMBIGUOUS {name}: text occurs {src.count(old)} times in {f}")
            return 8
        d = copy()
        try:
            with open(os.path.join(d, f), "w") as fh:
                fh.write(src.replace(old, new))
            rc = suite(d, C if f == C else R)
        finally:
            shutil.rmtree(d)
        verdict = "KILLED" if rc != 0 else "SURVIVED"
        print(f"{verdict} {name} ({f}, rc {rc})", flush=True)
        if rc == 0:
            survived.append(name)
    after = digests()
    print(f"sources unchanged after the campaign: {after == before}")
    print(f"{len(MUTANTS) - len(survived)}/{len(MUTANTS)} killed; survivors: {survived}")
    return 1 if survived or after != before else 0


if __name__ == "__main__":
    sys.exit(main())

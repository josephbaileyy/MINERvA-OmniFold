"""Mutation runner for C2-EFF: each mutant edits one exact text in a temp-dir copy (never the files in place) and must
make its test suite fail. c2_eff.py mutants run test_c2_eff.py; c2_fetch_remote.py and c2_fetch_verify.py mutants run
test_c2_fetch.py's Fetch class. The wrapper c2_fetch.sh is not mutated (its tests need the git worktree; it is pinned
by sha and ran once). Exit 0 iff the baseline passes and every mutant is killed; 9 if the baseline fails; 8 if a
mutant's text does not occur exactly once; 1 if any mutant survives.

run: python3 -I -B mutants_c2_eff.py
"""
import os
import shutil
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
FILES = ["c2_eff.py", "c2_fetch_remote.py", "c2_fetch_verify.py", "c2_fetch.sh", "test_c2_eff.py", "test_c2_fetch.py"]
REPO = os.path.abspath(os.path.join(HERE, *[".."] * 7))

E, R, V = "c2_eff.py", "c2_fetch_remote.py", "c2_fetch_verify.py"
MUTANTS = [
    ("tol-loose", E, "TOL = 1e-6", "TOL = 1e-3"),
    ("c-qr-off", E, "    if not c_qr <= TOL:", "    if False:"),
    ("c-stat-off", E, "    if not c_stat <= TOL:", "    if False:"),
    ("c-cells-off", E, "if not np.array_equal(pos, np.sort(cells)) or len(cells) != 205:", "if False:"),
    ("ddof0", E, "np.var(X, axis=0, ddof=1)", "np.var(X, axis=0, ddof=0)"),
    ("ibu-all-cells", E, "I = ibu[:, ki, :][:, cells]", "I = ibu[:, ki, :]"),
    ("of-all-cells", E, "O = of[:, cells]", "O = of"),
    ("r-a-wrong-denominator", E, '"r_a_ibu_over_of": s_ibu / s_of,', '"r_a_ibu_over_of": s_ibu / s_stat,'),
    ("r-b-wrong-denominator", E, '"r_b_ibu_over_statonly": s_ibu / s_stat,', '"r_b_ibu_over_statonly": s_ibu / s_of,'),
    ("jackknife-factor", E, "np.sqrt((n - 1) / n *", "np.sqrt(1 / n *"),
    ("ravel-F", E, 'return v.ravel(order="C")', 'return v.ravel(order="F")'),
    ("axes-off", E, "            raise Stop(f\"C-AXES: {os.path.basename(path)}:{name} is not the (pt 14, p|| 16) grid\")",
     "            pass"),
    ("meta-seed-off", E, 'or meta.get("bootstrap_seed") != b ', ""),
    ("meta-config-off", E, ' or meta.get("config_sha256") != cfg_sha', ""),
    ("meta-controls-off", E, 'if not meta.get("controls") or not all(c.get("pass") is True for c in meta["controls"].values()):',
     "if False:"),
    ("fetch-digest-off", E, "if sha_file(os.path.join(fetch, rel)) != digest:", "if False:"),
    ("main-overwrites", E, "    if os.path.lexists(a.out):", "    if False:"),
    ("finite-off", E, "        if not np.all(np.isfinite(a)):\n            raise Stop", "        if False:\n            raise Stop"),
    ("median-wrong", E, '"median_sigma_ratio_ibu_over_of": float(np.median(sd_ibu / sd_of)),',
     '"median_sigma_ratio_ibu_over_of": float(np.median(sd_ibu / sd_stat)),'),
    ("run-oserror-uncaught", E, "except (Stop, OSError, ValueError, KeyError) as e:", "except (Stop, ValueError, KeyError) as e:"),
    ("remote-atime-off", R, "        if st2.st_atime_ns != st.st_atime_ns:", "        if False:"),
    ("remote-regular-off", R, "    if not stat.S_ISREG(st.st_mode):", "    if False:"),
    ("remote-empty-off", R, "    if st.st_size <= 0:", "    if False:"),
    ("remote-noatime-check-off", R, "    if noatime is None:", "    if False:"),
    ("remote-n-rep", R, "N_REP = 300", "N_REP = 299"),
    ("remote-argv-off", R, "    if len(argv) != 3:", "    if False:"),
    ("verify-sha-off", V, 'if len(data[n]) != r["size"] or sha(data[n]) != r["sha256"]:', "if False:"),
    ("verify-atime-off", V, '        if r["atime_before"] != r["atime_after"]:', "        if False:"),
    ("verify-verdict-off", V, ' or d.get("verdict") != "PASS"', ""),
    ("verify-done-sha-off", V, ' or d.get("sha256") != sha(data[f"units/{u}.npz"])', ""),
    ("verify-central-off", V, '    if sha(data["units/c2_central.npz"]) != central_sha:', "    if False:"),
    ("verify-listing-off", V, '        if sizes.get(n) != len(data[f"inputs/{n}"]):', "        if False:"),
    ("verify-ks-off", V, '        if [int(k) for k in z["ks"]] != KS:', "        if False:"),
    ("verify-finite-off", V, "if x.shape != (len(KS), 224) or not np.all(np.isfinite(x)):", "if x.shape != (len(KS), 224):"),
    ("verify-duplicate-off", V, "            if m.name in data:", "            if False:"),
    ("verify-unexpected-off", V, '            if m.name != "MANIFEST.tsv" and m.name not in EXPECTED_SET:', "            if False:"),
    ("verify-manifest-missing-off", V, '    if "MANIFEST.tsv" not in data:', "    if False:"),
    ("verify-files-dir-exist-ok", V, "    os.mkdir(files)", "    os.makedirs(files, exist_ok=True)"),
]


def suite(d: str, target: str) -> int:
    env = dict(os.environ, C2_EFF_REPO=REPO, OMP_NUM_THREADS="1", OPENBLAS_NUM_THREADS="1")
    cmd = [sys.executable, "-I", "-B", "-W", "ignore", "test_c2_eff.py"] if target == E else \
        [sys.executable, "-I", "-B", "-W", "ignore", "test_c2_fetch.py", "Fetch"]
    return subprocess.run(cmd, cwd=d, env=env, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL).returncode


def copy() -> str:
    d = tempfile.mkdtemp(prefix="c2eff-mut-")
    for f in FILES:
        shutil.copy2(os.path.join(HERE, f), d)
    return d


def main() -> int:
    d = copy()
    try:
        base = {t: suite(d, t) for t in (E, R)}
    finally:
        shutil.rmtree(d)
    print(f"baseline: test_c2_eff rc {base[E]}, test_c2_fetch Fetch rc {base[R]}")
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
            rc = suite(d, E if f == E else R)
        finally:
            shutil.rmtree(d)
        verdict = "KILLED" if rc != 0 else "SURVIVED"
        print(f"{verdict} {name} ({f}, rc {rc})", flush=True)
        if rc == 0:
            survived.append(name)
    print(f"{len(MUTANTS) - len(survived)}/{len(MUTANTS)} killed; survivors: {survived}")
    return 1 if survived else 0


if __name__ == "__main__":
    sys.exit(main())

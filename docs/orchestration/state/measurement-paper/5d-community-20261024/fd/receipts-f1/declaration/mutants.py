"""F1 declaration: planted defects in the new code, each run against nd-unfolding/tests/test_fd_f1.py in place, one at
a time, with the file restored (and its sha256 checked) after each. Usage: python3 -I -B mutants.py <repo root>"""
import hashlib, subprocess, sys
from pathlib import Path
R = Path(sys.argv[1]).resolve()
P, T, LN, B, V, G = ("nd-unfolding/fd_f1_prep.py", "nd-unfolding/fd_f1_tasks.py", "nd-unfolding/fd_f1_lane.py",
                     "nd-unfolding/fd_f1_budget.py", "3d-unfolding/genie/gen5d_v3.py", "nd-unfolding/fd_f0_regrade.py")
MUTANTS = [
    (1, P, 'k: {"label": TRUTHS[k], "path": p, "sha256": s}', 'k: {"label": TRUTHS[k], "path": p, "sha256": p}'),
    (2, P, '"shape_ratio": r,', '"shape_ratio": r[::-1],'),
    (3, P, "if len(r) != n or min(r) <= 0:", "if len(r) != n:"),
    (4, P, 'if ratio.get("truth_cut") is not None:', "if False:"),
    (5, P, "        if got != want:", "        if False:"),
    (6, P, '"axes": [0, 1, 2, 3, 4]', '"axes": [0, 1, 2, 4, 3]'),
    (7, T, '"--estimator-seed", "42"', '"--estimator-seed", "43"'),
    (8, T, 'f"{a}:{a + n - 1}"', 'f"{a}:{a + n}"'),
    (9, T, '"--amplitude", "1.0"', '"--amplitude", "0.5"'),
    (10, T, '(4, "genie_v3_g18", False, 16, 4)', '(4, "genie_v3_g18", False, 15, 4)'),
    (11, T, '"--expect-ratio-sha256", sums[rel]', '"--expect-ratio-sha256", sums[f"bridged/{name}.json"]'),
    (12, T, "        if closure:", "        if not closure:"),
    (13, LN, "        if rc:\n            return rc", "        if False:\n            return rc"),
    (14, LN, 'if _ND not in path.parents or not path.is_file() or path.suffix != ".py":', "if not path.is_file():"),
    (15, LN, "if int(f[0]) != lane:", "if int(f[0]) == lane:"),
    (16, B, "w * N_TASK / N_PILOT + w", "w * N_TASK / N_PILOT"),
    (17, B, '"GO" if fits and within', '"GO" if fits or within'),
    (18, B, "within = total <= PRICED_NODE_H", "within = total < PRICED_NODE_H + 1"),
    (19, B, "f1b_s / 3600.0 + F1C_NODE_H", "f1b_s / 3600.0"),
    (20, V, "return phi_t * np.diff(edges)", "return phi_t"),
    (21, V, 'if hr["tune"] != a.tune or hs["tune"] != a.tune:', 'if hr["tune"] != a.tune:'),
    (22, V, ' or hr["n_splines"] != len(hr["ch_splines"])', ""),
    (23, V, 'if not sampling["pass"]:', "if False:"),
    (24, G, 'group="held-out", own=None, sens="genie_mec", set=name', 'group="held-out", own="genie_mec", sens="genie_mec", set=name'),
    (25, G, 'if t["row"] in (3, 8):', 'if t["row"] in (3,):'),
    (26, G, "diff = [n for n in old if new.get(n) != old[n]]", "diff = []"),   # re-pointed: round 2 replaced its line
    (27, G, '"eavail_ratio_sha256": prep[brel]', '"eavail_ratio_sha256": prep[rel]'),
    (28, G, "ratio=prep[rel]", "ratio=prep[brel]"),
    (29, G, "seeds=(s0, F1_N)", "seeds=(s0 + 1, F1_N)"),
    (30, G, "if f1[0] is not None and a.extra_block is None:", "if False:"),
    (31, G, 'sets[t["name"]] = listed_set(f1prod, a.f1_root / "pe" / t["set"])',
         'sets[t["name"]] = sorted((a.f1_root / "pe" / t["set"]).glob("ratio_nd_a1_s80[67]00[0-2].npz"))'),
    (32, G, 'require(1, a.f1_prep_sums, a.f1_prep_sums_sha256, "F1 prep manifest")', "pass"),
    # round 2 (the review's findings)
    (33, "3d-unfolding/genie/run_gevgen_v3.sh", '-f "${FLUX},flux_numu,NOWIDTH"', '-f "${FLUX},flux_numu"'),
    (34, V, 'if "nuE constraint true" not in meta.get("definition", ""):', "if False:"),
    (35, V, ' or meta.get("npz_sha256") != sha', ""),
    (36, V, "if not rel <= INTEGRAL_TOL:", "if rel > 1.0:"),
    (37, V, "and np.array_equal(np.asarray(contents, float), np.asarray(c2, float)))", ")"),
    (38, V, "if len(version) == 1 and version[0] != pin[2]:", "if False:"),
    (39, V, "if hashlib.sha256(Path(a.source).read_bytes()).hexdigest() != pin[0]:", "if False:"),
    (40, V, 'if hr["format"] != hs["format"] or hr["format"] is None:', 'if hr["format"] is None:'),
    (41, T, "    if have != want:", "    if not set(want) <= set(have):"),
    (42, B, "per_task = {k: CONTENTION * (w * N_TASK / N_PILOT + w)", "per_task = {k: (w * N_TASK / N_PILOT + w)"),
    (43, B, "limit_min = int(-(-(f1b_s * WALL_MARGIN) // 60))", "limit_min = int(f1b_s // 60)"),
    (44, G, 'pooled = {k: g for k, g in by.items() if k != "held-out"}', "pooled = by"),
    (45, G, "diff = [n for n in old if new.get(n) != old[n]]",
         'diff = [n for n in old if any(new.get(n, {}).get(k) != old[n].get(k) for k in ("bias", "grade"))]'),
]
ONLY = {int(x) for x in sys.argv[2:]}           # optional: rerun only these ids
killed, survived = [], []
for mid, rel, old, new in MUTANTS:
    if ONLY and mid not in ONLY:
        continue
    f = R / rel
    orig = f.read_bytes()
    sha = hashlib.sha256(orig).hexdigest()
    text = orig.decode()
    if text.count(old) != 1:
        print(mid, "NOT APPLICABLE", rel, flush=True)
        survived.append(mid)
        continue
    try:
        f.write_text(text.replace(old, new, 1))
        p = subprocess.run([sys.executable, "-I", "-B", str(R / "nd-unfolding/tests/test_fd_f1.py")], capture_output=True,
                           text=True, timeout=900)
    finally:
        f.write_bytes(orig)
    assert hashlib.sha256(f.read_bytes()).hexdigest() == sha, f"{rel} not restored"
    (killed if p.returncode else survived).append(mid)
    print(mid, "KILLED" if p.returncode else "SURVIVED", rel, repr(old[:60]), flush=True)
print("total", len(killed) + len(survived), "killed", len(killed), "survived", survived)

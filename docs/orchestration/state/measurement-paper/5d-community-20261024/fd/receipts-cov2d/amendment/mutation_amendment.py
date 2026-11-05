"""COV2D amendment mutants: one guard or declared rule per mutant, over the amendment's ten files. Run from a
scratchpad with an interpreter that has PyROOT, uproot and numpy:
    TMPDIR=<dir> PYTHONDONTWRITEBYTECODE=1 python -B mutation_amendment.py <worktree> [<mutant name> ...]
Each mutant rewrites one line of one file, runs that file's test modules (python -m unittest, from the tests
directory), and restores it. A kill counts only on a test failure (rc != 0). Each mutant's text must occur once; a
mutant whose text does not match counts as not killed. The run exits 1 unless every mutant run is killed, and names any
REQUIRED mutant (the director's rulings on the final audit's F1 and F2, on F3, and of 2026-11-05 on the blocks' reads
through O_NOATIME) that was not."""
import os
import shutil
import subprocess
import sys
from pathlib import Path

WT = Path(sys.argv[1])
D = WT / "2d-unfolding/cov2d"
T = D / "tests"
J = "jobs/cov2d_jobs.py"
TESTS = {"cov2d.py": ["test_cov2d"], "jobs/cov2d_submit.sh": ["test_cov2d_jobs"], "cov2d_pseudo.py": ["test_cov2d_pseudo"], "cov2d_pseudo_write.py": ["test_cov2d_pseudo_write"],
         "cov2d_blocks.py": ["test_cov2d_blocks"], "cov2d_null.py": ["test_cov2d_null"],
         "cov2d_score.py": ["test_cov2d_score"], "cov2d_readouts.py": ["test_cov2d_readouts"],
         J: ["test_cov2d_jobs"], "cov2d_pilot.py": ["test_cov2d_pilot"]}
M = [
    ("cov2d_pseudo.py", "r_T not applied to the signal", "L = A * r_s[start:stop] * s", "L = A * s"),
    ("cov2d_pseudo.py", "counts stream without its salt", 'np.random.default_rng([n["seed"], c.DRAW_SALT, 1])',
     'np.random.default_rng([n["seed"], c.DRAW_SALT])'),
    ("cov2d_pseudo.py", "truth not clipped", "        plus, rec = c.lam_plus(w)\n",
     "        plus, rec = w, c.lam_plus(w)[1]\n"),
    ("cov2d_pseudo.py", "section 9.6 skipped", "single_bad.update(single_universe_control(cv, U, pos))", "pass"),
    ("cov2d_pseudo.py", "R1 counts w >= 1e5 only", '"w_ge_1e4": fin & (w_raw >= 1e4)', '"w_ge_1e4": fin & (w_raw >= 1e5)'),
    ("cov2d_pseudo.py", "seen sums ignore reco-kept", "    ok = kept & (tcell >= 0)\n", "    ok = tcell >= 0\n"),
    ("cov2d_pseudo_write.py", "section 9.4 at 1e-6", "TOL_94 = 1e-12", "TOL_94 = 1e-6"),
    ("cov2d_pseudo_write.py", "9.11 membership ignored", '"rows_not_a_passing_row": int((~member).sum())',
     '"rows_not_a_passing_row": 0'),
    ("cov2d_pseudo_write.py", "9.11 at 50 sigma", "SIGMA_9_11 = 5.0", "SIGMA_9_11 = 50.0"),
    ("cov2d_pseudo_write.py", "truth ignores the drawn flux universe", "drv.PT_EDGES, flux_cv) if flux else flux_cv)",
     "drv.PT_EDGES, flux_cv) if False else flux_cv)"),
    ("cov2d_blocks.py", "norm check removed", "    if not np.array_equal(ublocks[NORM_KEY], np.outer(v, v)):\n",
     "    if False:\n"),
    ("cov2d_blocks.py", "blocks without noatime_inputs before the rollup",
     'rec["inputs"] = noatime_inputs(ro, tdp / "rollup",', 'rec["inputs"] = {} if True else noatime_inputs(ro, tdp / "rollup",'),
    ("cov2d_blocks.py", "C08 not carried", "C08 = r[:, None] * np.asarray(C08_R, np.float64) * r[None, :]",
     "C08 = np.asarray(C08_R, np.float64)"),
    ("cov2d_blocks.py", "stat ddof 0", "C_stat = np.cov(np.asarray(X_rep, np.float64), rowvar=False)",
     "C_stat = np.cov(np.asarray(X_rep, np.float64), rowvar=False, ddof=0)"),
    ("cov2d_blocks.py", "open audit off", "        if p.startswith(self.guarded) and not (noatime or p in self.sanctioned):\n",
     "        if False:\n"),
    ("cov2d_blocks.py", "C_model- keeps GENIE + MEC", 'MINUS_VERTICES = ("nuwro", "gibuu")',
     'MINUS_VERTICES = ("genie_mec", "gibuu")'),
    ("cov2d_null.py", "1B's null seed", "gauss, C_T, n_mc=n_mc, seed=c.NULL_SEED)", "gauss, C_T, n_mc=n_mc, seed=nl.NULL_SEED)"),
    ("cov2d_null.py", "C_T-'s null at 1B's seed", "n_mc=n_mc, seed=c.NULL_SEED)\n    return out",
     "n_mc=n_mc, seed=nl.NULL_SEED)\n    return out"),
    ("cov2d_null.py", "C_T-'s null keeps C_model", 'g_minus = blocks["C_stat"] + blocks["C_norm"] + blocks["C08"] + minus_abs',
     'g_minus = blocks["C_stat"] + blocks["C_norm"] + blocks["C08"] + blocks["C_model_abs"]'),
    ("cov2d_null.py", "MINOS law without X01", "X = np.asarray(minos_x if b == MINOS else bands[b], np.float64)",
     "X = np.asarray(bands[b], np.float64)"),
    ("cov2d_score.py", "surrogates in the other order", "x = (np.asarray(x_hat, np.float64) + lat) * (1 + c.NORM * float(norm_z))",
     "x = np.asarray(x_hat, np.float64) * (1 + c.NORM * float(norm_z)) + lat"),
    ("cov2d_score.py", "flagged cells labelled weakened", 'if cell in weak and not g["cell_flag"][i]]', "if cell in weak]"),
    ("cov2d_score.py", "INVALID ignored", '    if g["controls_failed"]:\n', "    if False:\n"),
    ("cov2d_score.py", "S1 any toy count graded", "    if E.shape[0] != len(c.TOY_SEEDS[truth]):", "    if False:"),
    ("cov2d_score.py", "S2 outlier absence not refused", "if c.OUTLIER_CELL not in [int(x) for x in cells]:", "if False:"),
    ("cov2d_score.py", "S3 outlier read at position 0", "    i = cells.index(c.OUTLIER_CELL)\n", "    i = 0\n"),
    ("cov2d_score.py", "S3 weakened share over the unflagged", 'g["weakened_share"] = len(weak) / 205',
     'g["weakened_share"] = len(g["weakened_pass"]) / 205'),
    ("cov2d_score.py", "S4 cross term over diag C_T", "sigma = np.sqrt(np.diag(np.asarray(C_T, np.float64)))",
     "sigma = np.diag(np.asarray(C_T, np.float64))"),
    ("cov2d_readouts.py", "reading at 5 sigma", "READING_SIGMA = 0.5", "READING_SIGMA = 5.0"),
    ("cov2d_readouts.py", "product composition without its floor", "ok = (cv > 0) & np.all(U > 0, axis=0)", "ok = cv > 0"),
    ("cov2d_readouts.py", "predicted offset sign", "    return -off\n", "    return off\n"),
    ("cov2d_readouts.py", "R2 joint flag ignored", '(MEC_COVERS if not hit and not g["joint_flag"] else', "(MEC_COVERS if not hit else"),
    ("cov2d_readouts.py", "R2 jointly suffix dropped", 'jointly=" (and jointly)" if g["joint_flag"] else ""', 'jointly=""'),
    ("cov2d_readouts.py", "R2 reading ignores C_T's verdict", '    if grade_CT["verdict"] == "COVERS":', "    if True:"),
    ("cov2d_readouts.py", "R5 seed order unchecked", "    if seeds != list(c.TOY_SEEDS[truth]):", "    if False:"),
    ("cov2d_readouts.py", "R6 outlier absence not refused", "    if c.OUTLIER_CELL not in rep:", "    if False:"),
    ("cov2d_readouts.py", "R4 a missing R_c read as 0", "np.nanmedian(np.abs(Rs[:, i])) if ok[:, i].any() else np.nan",
     "np.median(np.nan_to_num(np.abs(Rs[:, i])))"),
    ("cov2d_readouts.py", "R4 outlier max is its median", '"max_abs_R_sigma": float(np.nanmax(col)) if have else None',
     '"max_abs_R_sigma": float(np.nanmedian(col)) if have else None'),
    ("cov2d_readouts.py", "R4 complete toys ignored", "    complete = ok.all(axis=1)", "    complete = ok.any(axis=1)"),
    ("cov2d_readouts.py", "R4 coherent offset on the identity", "coherent = nl.chi2_nonnull(vec, C_T)[0]",
     "coherent = nl.chi2_nonnull(vec, np.eye(rep.size))[0]"),
    ("cov2d_readouts.py", "R4 coherent offset without x_true", "vec = np.where(ok, R * x_true, 0.0)",
     "vec = np.where(ok, R, 0.0)"),
    ("cov2d_readouts.py", "R7 F <= 0 pairs not counted", '"excluded_pairs_F_le_0": int((~live).sum())',
     '"excluded_pairs_F_le_0": 0'),
    ("cov2d_readouts.py", "R1 z over F not sqrt F", "z[live] = (P[live] - F[live]) / np.sqrt(F[live])",
     "z[live] = (P[live] - F[live]) / F[live]"),
    (J, "limit factor 1.2", "s = math.ceil(1.25 * (longest_lane_s", "s = math.ceil(1.2 * (longest_lane_s"),
    (J, "staged copy not compared", "            if got != record[path][0]:\n", "            if False:\n"),
    (J, "toys read d_T", 'out.append({"kind": "toy", "label": f"T_{truth}_{s}", "args": argv("toy", f"$D/data_{s}.root")})',
     'out.append({"kind": "toy", "label": f"T_{truth}_{s}", "args": argv("toy", real)})'),
    (J, "J1 bulk without the pilot record", "    if not ok(PILOT_RECORD):\n", "    if False:\n"),
    (J, "J1 pilot without G18's pseudo PASS", "return [] if ok(pseudo[\"G18\"]) else", "return [] if True else"),
    (J, "J1 the rest before the universe jobs", "        if missing:\n            need.append(f\"the universe jobs go first",
     "        if False:\n            need.append(f\"the universe jobs go first"),
    (J, "F1 order ignores M", 'r.get("verdict") == "PASS" and r.get("M") == M', 'r.get("verdict") == "PASS"'),
    (J, "F2 bulk despite REPRICE", '    elif committed[PILOT_RECORD].get("reprice_classes") != []:', "    elif False:"),
    (J, "F2 no REPRICE list read as none", '.get("reprice_classes") != []:', '.get("reprice_classes", []) != []:'),
    ("cov2d.py", "F1 a dirty deploy admitted", '    if git("status", "--porcelain").strip():', "    if False:"),
    ("cov2d_pseudo_write.py", "F1 the pseudo record without M", '"pins_checked": not a.no_pins,\n           "M": M}',
     '"pins_checked": not a.no_pins}'),
    ("cov2d_pseudo_write.py", "F1 a deploy moving during step B unchecked", '    if c.deploy_head(DEPLOY) != rec["M"]:',
     "    if False:"),
    ("cov2d_pilot.py", "F1 the pilot record without M", 'rec = {"stop": [], "invalid": [], "M": c.deploy_head(DEPLOY)}',
     'rec = {"stop": [], "invalid": []}'),
    ("jobs/cov2d_submit.sh", "F3 the deploy's own binding read", 'bind=$(git -C "$C" show "origin/main:$BIND")',
     'bind=$(cat "$C/$BIND")'),
    ("jobs/cov2d_submit.sh", "F3 the binding's name check skipped", r'grep -qE "^\*\*M = \`$M\`\*\*" <<<"$bind" ||',
     "true ||"),
    ("jobs/cov2d_submit.sh", "F3 M matched anywhere in the binding", r'grep -qE "^\*\*M = \`$M\`\*\*" <<<"$bind"',
     'grep -qF "$M" <<<"$bind"'),
    ("jobs/cov2d_submit.sh", "F3 a failed fetch admitted", 'git -C "$C" fetch -q origin main ||',
     'git -C "$C" fetch -q origin main || true ||'),
    (J, "gate passes everything", '"cap": CAP_NODE_H, "pass": total <= CAP_NODE_H}', '"cap": CAP_NODE_H, "pass": True}'),
    ("cov2d_pilot.py", "pilot compare at 1e-6", 'cmp_["pass"] = cmp_["max_rel"] <= k1.TOL and cmp_["same_cell_set"]',
     'cmp_["pass"] = cmp_["max_rel"] <= 1e-6 and cmp_["same_cell_set"]'),
    ("cov2d_pilot.py", "REPRICE at 2x", "REPRICE = 1.25", "REPRICE = 2.0"),
    ("cov2d_pilot.py", "P2 a failed run is not INVALID", "        if rc_of.get(lab) != 0 or f\"{lab}/xsec.root\" not in ours:",
     "        if False:"),
    ("cov2d_pilot.py", "P2 a missing class is not INVALID", "    if missing:\n        rec[\"invalid\"].append(f\"no wall",
     "    if False:\n        rec[\"invalid\"].append(f\"no wall"),
]
REQUIRED = {"F2 bulk despite REPRICE", "F2 no REPRICE list read as none", "F1 order ignores M",
            "F1 a dirty deploy admitted", "F1 the pseudo record without M", "F1 the pilot record without M",
            "F3 the deploy's own binding read", "F3 the binding's name check skipped", "F3 a failed fetch admitted",
            "F3 M matched anywhere in the binding",
            "open audit off", "blocks without noatime_inputs before the rollup"}
if sys.argv[2:]:
    unknown = set(sys.argv[2:]) - {m[1] for m in M}
    assert not unknown, f"no such mutant: {sorted(unknown)}"
    M = [m for m in M if m[1] in sys.argv[2:]]
bak = Path(os.environ["TMPDIR"])
files = sorted({m[0] for m in M})
for f in files:
    (bak / f).parent.mkdir(parents=True, exist_ok=True)
    shutil.copy(D / f, bak / f)
killed, alive = 0, []
try:
    for f, name, a, b in M:
        src = (bak / f).read_text()
        if src.count(a) != 1:
            print(f"NOMATCH {f}: {name}", flush=True)
            alive.append(name)
            continue
        (D / f).write_text(src.replace(a, b))
        r = subprocess.run([sys.executable, "-B", "-m", "unittest", *TESTS[f]], cwd=T, capture_output=True, text=True,
                           env=dict(os.environ, PYTHONDONTWRITEBYTECODE="1"))
        killed += bool(r.returncode)
        if not r.returncode:
            alive.append(name)
        print(f"{'KILLED ' if r.returncode else 'SURVIVED'} {f}: {name}", flush=True)
        shutil.copy(bak / f, D / f)
finally:
    for f in files:
        shutil.copy(bak / f, D / f)
print(f"killed {killed} of {len(M)}")
if REQUIRED & set(alive):
    print(f"REQUIRED NOT KILLED: {sorted(REQUIRED & set(alive))}")
sys.exit(1 if alive else 0)

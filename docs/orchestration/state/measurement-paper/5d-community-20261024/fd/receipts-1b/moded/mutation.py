import subprocess, sys
from pathlib import Path
src = Path("fd_1b_moded.py"); orig = src.read_text()
M = [
 ("coarse grid drops the H2 edges", "e[-1:], np.asarray(s1i.H2_EDGES[a], float)]", "e[-1:]]"),
 ("fine grid not halved", "np.concatenate([e, 0.5 * (e[:-1] + e[1:])])", "np.concatenate([e])"),
 ("B's factor grid ignored", "fs_ = k_wr * ne.truth_preserving(k_wt, on_grid,", "fs_ = k_wr * ne.truth_preserving(k_wt, inputs,"),
 ("C's factor grid ignored", "inv.cell_mean_factor(k_wt, on_grid)", "inv.cell_mean_factor(k_wt, inputs)"),
 ("B's background factor dropped", 'dict(bkg, bkg_w=np.asarray(bkg["bkg_w"], float) * k_b), rec)', 'dict(bkg), rec)'),
 ("D unfolds with the universe MC", "return inv.with_mc(exp, inputs, bkg), x_true", "return exp, x_true"),
 ("D's nature is the nominal MC", "toys.build_full(ui, ub, r, ones_s, ones_b, None, expectation=True)", "toys.build_full(inputs, bkg, r, ones_s, ones_b, None, expectation=True)"),
 ("unreported rows take a cell's factor", "m = cell >= 0\n", "m = cell >= -1\n"),
 ("Ddl's factor not applied", 'r, dl_sha, truth = r * dl_weight(row_cell(inputs, fm), dl["r_cell"]), a.expect_dl_sha256, "data-like"', 'r, dl_sha, truth = r, a.expect_dl_sha256, "data-like"'),
 ("Ddl's nominal-truth check skipped", 'if not np.array_equal(U @ np.asarray(x_nom, float).ravel(order="C"), np.asarray(dl["U_xT"], float)):', "if False:"),
 ("dl digest not checked", "if sa.sha256(path) != expect_sha256:", "if False:"),
 ("--grid pairing not enforced", "if (a.mode in GRID_MODES) != (a.grid is not None):", "if False:"),
 ("grid universes not enforced", "if a.mode in GRID_MODES and tag not in GRID_UNIVERSES + (\"CV\",):", "if False:"),
 ("rule D passes at 15 of 16", 'verdict = "PASS" if n == rho.size else', 'verdict = "PASS" if n >= rho.size - 1 else'),
 ("partial level at 4", "ACCOUNT = 8 ", "ACCOUNT = 4 "),
 ("window edges exclusive", "return (x >= WINDOW[0]) & (x <= WINDOW[1])", "return (x > WINDOW[0]) & (x < WINDOW[1])"),
 ("matched reading needs more than 8", '"matched" if n >= ACCOUNT else', '"matched" if n > ACCOUNT else'),
 ("sub-cell hypothesis read as OR", '"subcell_hypothesis_supported": bool((gamma > WINDOW[1]).sum() >= ACCOUNT and', '"subcell_hypothesis_supported": bool((gamma > WINDOW[1]).sum() >= ACCOUNT or'),
 ("the rule's object is the raw shift", 'rows["error"].append(x - t)', 'rows["error"].append(x - X_cv)'),
 ("Dnom CV control skipped", 'if not np.array_equal(np.asarray(blk["Dnom"]["cv"]["xsec_flat"], float), x_cv_der):', "if False:"),
 ("data-like truth control skipped", "if np.max(np.abs(T_dl / f - 1)) > DL_TOLERANCE:", "if False:"),
 ("nominal grid vs I2 skipped", 'if not np.array_equal(np.asarray(z["xsec_flat"], float), np.asarray(ref["xsec_flat"], float)):', "if False:"),
 ("one-code check skipped", "if len(vals) != 1 or metas[next(iter(metas))].get(key) is None:", "if False:"),
 ("readout dl digest skipped", 'if {v.get("dl_sha256") for k, v in metas.items() if k.startswith("Ddl_")} != {sa.sha256(dl_path)}:', "if False:"),
 ("M reproduction skipped", 'if M.tolist() != r2["M"]:', "if False:"),
 ("readout reads plainly", '            z = inv.load_npz(p)\n            meta = _meta(z)\n            if (meta.get("mode"), meta.get("universe"), meta.get("schema"))', '            z = inv.load_npz_plain(p)\n            meta = _meta(z)\n            if (meta.get("mode"), meta.get("universe"), meta.get("schema"))'),
 ("walls limit doubled", "ok = s_max <= UNIT_SECONDS and r_max <= RSS_LIMIT_KIB", "ok = s_max <= 2 * UNIT_SECONDS and r_max <= RSS_LIMIT_KIB"),
 ("walls RSS ignored", "ok = s_max <= UNIT_SECONDS and r_max <= RSS_LIMIT_KIB", "ok = s_max <= UNIT_SECONDS"),
 ("REPRICE exits 0", 'return 0 if res["verdict"] == "PASS" else 1', "return 0"),
 ("a moved atime exits 0", "return status | 8", "return status"),
 ("peak RSS not recorded", '"peak_rss_kib": resource.getrusage(resource.RUSAGE_SELF).ru_maxrss, ', ""),
 ("unit at 1,370 s", "UNIT_SECONDS = 1062.0 ", "UNIT_SECONDS = 1370.0 "),
]
rows = []
try:
    for name, old, new in M:
        assert orig.count(old) == 1, name
        src.write_text(orig.replace(old, new))
        r = subprocess.run([sys.executable, "-m", "pytest", "-q", "-x", "tests/test_fd_1b_moded.py"], capture_output=True, text=True)
        killed = r.returncode != 0
        rows.append((name, "KILLED" if killed else "SURVIVED"))
        print(f"{'KILLED  ' if killed else 'SURVIVED'} {name}", flush=True)
finally:
    src.write_text(orig)
r = subprocess.run([sys.executable, "-m", "pytest", "-q", "tests/test_fd_1b_moded.py"], capture_output=True, text=True)
print("unmutated:", r.stdout.strip().splitlines()[-1])
print(f"{sum(1 for _, k in rows if k == 'KILLED')} of {len(rows)} killed")

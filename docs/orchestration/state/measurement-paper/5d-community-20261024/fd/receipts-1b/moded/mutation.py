import hashlib, subprocess, sys
from pathlib import Path
src, tests = Path("fd_1b_moded.py"), Path("tests/test_fd_1b_moded.py")
orig = src.read_text()
for p in (src, tests, Path("fd_1b_inv.py")):
    print(f"sha256 {hashlib.sha256(p.read_bytes()).hexdigest()}  {p}")
print("KILLED means the suite exits 1 (a test failed); any other non-zero exit is ERROR, not a kill")
M = [
 ("coarse grid drops the H2 edges", "e[-1:], np.asarray(s1i.H2_EDGES[a], float)]", "e[-1:]]"),
 ("fine grid not halved", "np.concatenate([e, 0.5 * (e[:-1] + e[1:])])", "np.concatenate([e])"),
 ("B's factor grid ignored", "fs_ = k_wr * ne.truth_preserving(k_wt, on_grid,", "fs_ = k_wr * ne.truth_preserving(k_wt, inputs,"),
 ("C's factor grid ignored", "inv.cell_mean_factor(k_wt, on_grid)", "inv.cell_mean_factor(k_wt, inputs)"),
 ("B's background factor dropped", 'dict(bkg, bkg_w=np.asarray(bkg["bkg_w"], float) * k_b), rec)', 'dict(bkg), rec)'),
 ("D unfolds with the universe MC", "return inv.with_mc(exp, inputs, bkg), x_true", "return exp, x_true"),
 ("D's nature is the nominal MC", "toys.build_full(ui, ub, r, ones_s, ones_b, None, expectation=True)", "toys.build_full(inputs, bkg, r, ones_s, ones_b, None, expectation=True)"),
 ("unreported rows take a cell's factor", "m = cell >= 0\n", "m = cell >= -1\n"),
 ("Ddl's nominal-truth check skipped", 'if not np.array_equal(U @ np.asarray(x_nom, float).ravel(order="C"), np.asarray(dl["U_xT"], float)):', "if False:"),
 ("dl digest not checked", "if sa.sha256(path) != expect_sha256:", "if False:"),
 ("--grid pairing not enforced", "if (a.mode in GRID_MODES) != (a.grid is not None):", "if False:"),
 ("grid universes not enforced", "if a.mode in GRID_MODES and tag not in GRID_UNIVERSES + (\"CV\",):", "if False:"),
 ("partial level at 4", "ACCOUNT = 8 ", "ACCOUNT = 4 "),
 ("window edges exclusive", "return (x >= WINDOW[0]) & (x <= WINDOW[1])", "return (x > WINDOW[0]) & (x < WINDOW[1])"),
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
 ("B1: lambda without the carry", "np.sqrt(D_dl / (g ** 2 * D_nom))", "np.sqrt(D_dl / D_nom)"),
 ("ruling 4: a grid failure voids rule D", '    except fs.Invalid as e:\n        return {"verdict": "INVALID", "why": str(e)}', '    except fs.Invalid as e:\n        raise'),
 ("M2: rows alone miscounted", "float((occ == 1).sum() / occ.sum())", "float((occ == 1).sum() / occ.size)"),
 ("lambda reading threshold above 8", '"carry-like" if n >= ACCOUNT else', '"carry-like" if n > ACCOUNT else'),
 ("rule K passes at 15 of 16", 'verdict = "PASS" if n == kappa.size else', 'verdict = "PASS" if n >= kappa.size - 1 else'),
 ("rule K opens an ensemble on PASS", '"next": "to Joseph"}', '"next": "to Joseph" if verdict != "PASS" else "ensemble"}'),
 ("sub-cell hypothesis read as OR", "up_g >= half(kg) and dn_f >= half(kf)", "up_g >= half(kg) or dn_f >= half(kf)"),
 ("M2: construction-limited cells counted", "keep[gname] = np.array([x is not None and x <= ALONE_MAX for x in a_c])", "keep[gname] = np.ones(len(a_c), bool)"),
 ("M2: occupancy consistency skipped", "if len(alone) != 1:", "if False:"),
 ("M2: per-cell alone counted by cell, not row", "weights=alone_row[rc >= 0].astype(float)", "weights=np.ones(int((rc >= 0).sum()))"),
 ("Ddl's factor not applied", 'r, dl_sha, truth = r * dl_weight(row_cell(inputs, fm), dl["r_cell"]), a.expect_dl_sha256, "data-like"', 'r, dl_sha, truth = r, a.expect_dl_sha256, "data-like"'),
 ("rule K reads rho instead of kappa", "kappa = np.sqrt(D_nom / A_raw)", "kappa = np.sqrt(D_nom / M)"),
 ("grid needs no definition", 'if a.definition is None:\n            raise Refusal("the grid check needs --definition', 'if False:\n            raise Refusal("the grid check needs --definition'),
]
rows = []
try:
    for name, old, new in M:
        assert orig.count(old) == 1, name
        src.write_text(orig.replace(old, new))
        r = subprocess.run([sys.executable, "-m", "pytest", "-q", "-x", "tests/test_fd_1b_moded.py"], capture_output=True, text=True)
        state = "KILLED" if r.returncode == 1 else "SURVIVED" if r.returncode == 0 else f"ERROR rc={r.returncode}"
        rows.append((name, state))
        print(f"{state:8s} {name}", flush=True)
finally:
    src.write_text(orig)
r = subprocess.run([sys.executable, "-m", "pytest", "-q", "tests/test_fd_1b_moded.py"], capture_output=True, text=True)
print("unmutated:", r.stdout.strip().splitlines()[-1])
print(f"{sum(1 for _, k in rows if k == 'KILLED')} of {len(rows)} killed")

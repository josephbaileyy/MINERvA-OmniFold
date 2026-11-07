"""Mutation receipt for nd-unfolding/fd_1b_precheck_fd.py (FD-1B-PRECHECK-FD-DECLARATION.md section 8). Run from
nd-unfolding/: python3 <this file>. Each mutant replaces one exact string (it must occur once), the suite runs with
-x and no bytecode or cache, and the source is restored. KILLED means the suite exits 1 (a test failed); any other
non-zero exit is ERROR, not a kill. The suite then runs unmutated at three PYTHONHASHSEED values."""
import hashlib
import os
import subprocess
import sys
from pathlib import Path

src, tests = Path("fd_1b_precheck_fd.py"), Path("tests/test_fd_1b_precheck_fd.py")
orig = src.read_text()
for p in (src, tests, Path("fd_1b_inv.py"), Path("fd_1b_moded.py"), Path("fd_1b_toys.py")):
    print(f"sha256 {hashlib.sha256(p.read_bytes()).hexdigest()}  {p}")
print("KILLED means the suite exits 1 (a test failed); any other non-zero exit is ERROR, not a kill")
ENV = dict(os.environ, PYTHONDONTWRITEBYTECODE="1", PYTHONHASHSEED="0")
M = [
 ("2.1: the flux key dropped", 'UNFOLD_MC_KEYS = inv.MC_KEYS + ("flux",)', "UNFOLD_MC_KEYS = inv.MC_KEYS"),
 ("2.1: A expected to unfold Flux with Phi_CV", 'ui["flux"] if (mode == "A" and band_of(tag) == sa.FLUX) else inputs["flux"]', 'inputs["flux"]'),
 ("2.1: the job's flux refusal skipped", 'if not np.array_equal(np.asarray(exp["flux"], float), want):', "if False:"),
 ("Dnom unfolds with the universe MC", "return with_mc(exp, inputs, bkg), x_true", "return exp, x_true"),
 ("Dnom's nature is the nominal MC", 'toys.build_full(ui, ub, np.ones(ui["MCgen"].shape[0])', 'toys.build_full(inputs, bkg, np.ones(ui["MCgen"].shape[0])'),
 ("B's signal factor dropped", 'dict(inputs, w_reco=np.asarray(inputs["w_reco"], float) * fs_)', "dict(inputs)"),
 ("B's background factor dropped", 'dict(bkg, bkg_w=np.asarray(bkg["bkg_w"], float) * fb), rec)', "dict(bkg), rec)"),
 ("B's factors truth-preserved", 'fs_ = np.ones(wr.shape[0]) * ne.checked_ratio(w["wr"], wr, used_r, f"{tag}:wr", rec)',
  'fs_ = ne.checked_ratio(w["wr"], wr, used_r, f"{tag}:wr", rec) * ne.truth_preserving(ne.checked_ratio(w["wt"], np.asarray(inputs["w_truth"], float), np.asarray(inputs["pass_truth"], bool), f"{tag}:wt", rec), inputs, np.ones(wr.shape[0], bool))'),
 ("A takes no flux file", "flux_file if band == sa.FLUX else None)", "None)"),
 ("HD1's flag fixed True", 'info["wt_equals_cv"] = bool(np.array_equal(ui["w_truth"], np.asarray(inputs["w_truth"], float)))', 'info["wt_equals_cv"] = True'),
 ("an interaction universe accepted", 'legal = set(universes()) | {"CV"}', 'legal = set(universes()) | {"CV", "MaRES_0"}'),
 ("a moved atime exits 0", "return status | 8", "return status"),
 ("window edges exclusive", "    return inv.in_window(x)", "    return (np.asarray(x) > WINDOW[0]) & (np.asarray(x) < WINDOW[1])"),
 ("rule S reads unresolved cells", "if resolved[c] and not in_window(F_src[c])]", "if not in_window(F_src[c])]"),
 ("rule K reads unresolved cells", "if resolved[c] and not in_window(kappa[c])]", "if not in_window(kappa[c])]"),
 ("attribution without the half", " or mag < 0.5 * abs(tot)", ""),
 ("the account at n/2", 'counts[k] > n / 2 else', 'counts[k] >= n / 2 else'),
 ("refuted below n/4", 'counts[k] <= n / 4 else', 'counts[k] < n / 4 else'),
 ("F_side inverted", '"F_side": np.sqrt(B / A)', '"F_side": np.sqrt(A / B)'),
 ("Flux blocks unweighted", "C = sa.mat_cov(np.array(X), w_flux if b == sa.FLUX else None)", "C = sa.mat_cov(np.array(X))"),
 ("Dnom's block carried", 'out[mode][b] = C if mode == "Dnom" else C * np.outer(g, g)', "out[mode][b] = C * np.outer(g, g)"),
 ("Dnom's object is the raw result", 'X.append(x - U @ np.asarray(z["xtrue_flat"], float) if mode == "Dnom" else x)', "X.append(x)"),
 ("kappa against carried A", 'F["kappa"] = np.sqrt(dn / (a / g ** 2))', 'F["kappa"] = np.sqrt(dn / a)'),
 ("kappa's floor carried", "(sd2, sn2, sn2 / g ** 2))", "(sd2, sn2, sn2))"),
 ("A_Phi's ratio inverted", "(cv / np.asarray(p, float) - 1.0)", "(np.asarray(p, float) / cv - 1.0)"),
 ("gate D's sha not checked", "if sa.sha256(gate_d) != fdg.GATE_D_SHA256:", "if False:"),
 ("control E (gate D) skipped", 'if np.sqrt(np.diag(e) / np.diag(m)).tolist() != gd["per_group_sigma_ratio"][grp]:', "if False:"),
 ("control E (diagnosis) skipped", 'if fdg.ratio(E[b], M[b]) != dg["per_band"][b]["sigma_ratio"]:', "if False:"),
 ("control M skipped", 'if not np.array_equal(sa.mat_cov(X, w if b == sa.FLUX else None), s1["blocks"][f"band:{b}"]):', "if False:"),
 ("CV control skipped", 'if not np.array_equal(np.asarray(cv["xsec_flat"], float), cv_flat):', "if False:"),
 ("per-mode flux control skipped", 'if (meta["unfolding_flux_sha256"] == meta["cv_flux_sha256"]) != want_cv:', "if False:"),
 ("flux array control skipped", 'if array_sha256(z["unfolding_flux"]) != meta["unfolding_flux_sha256"]:', "if False:"),
 ("one-code check skipped", "if len(vals) != 1 or metas[next(iter(metas))].get(key) is None:", "if False:"),
 ("flux-file control skipped", 'if len(flux_staged) != 1 or metas["A_CV"]["flux_file_sha256"] not in flux_staged:', "if False:"),
 ("walls limit doubled", "ok = s_max <= UNIT_SECONDS and r_max <= RSS_LIMIT_KIB", "ok = s_max <= 2 * UNIT_SECONDS and r_max <= RSS_LIMIT_KIB"),
 ("walls RSS ignored", "ok = s_max <= UNIT_SECONDS and r_max <= RSS_LIMIT_KIB", "ok = s_max <= UNIT_SECONDS"),
 ("a missing pilot product passes", '            raise Refusal(f"pilot product {p.name} is missing")', "            continue"),
 # coverage-5b-audit's code audit of 40824375 (T1, T2): sixteen extra single-site mutants, fifteen of which survived
 # that suite; each has a firing test now
 ("T1: rule F window clause dropped", "if bool(in_window(F[k][c])) or mag < 0.5 * abs(tot):", "if mag < 0.5 * abs(tot):"),
 ("T1: rule F same-side clause dropped", "for k in FACTORS if math.log(F[k][c]) * tot > 0]", "for k in FACTORS]"),
 ("T1: rule F reads unresolved cells", 'if allres[c] and not in_window(F["total"][c])]', 'if not in_window(F["total"][c])]'),
 ("T1: F_truth's M on the nominal floor", '"F_truth": ~noise(a, m, f_n, f_d)', '"F_truth": ~noise(a, m, f_n, f_n)'),
 ("T1: total's M on the nominal floor", 'res["total"] = ~noise(e, m, f_n, f_d)', 'res["total"] = ~noise(e, m, f_n, f_n)'),
 ("T1: a group's floor from one band", "(sum(nf[b] for b in bs) * x for x in (sd2, sn2, sn2 / g ** 2))", "(nf[bs[0]] * x for x in (sd2, sn2, sn2 / g ** 2))"),
 ("T2: input digests not checked", "if (npz_sha, bkg_sha) != (sa.INPUT_NPZ_SHA256, sa.BKG_SHA256):", "if False:"),
 ("T2: pins digest not checked", "if inv.sha256_noatime(a.pins) != a.expect_pins_sha256:", "if False:"),
 ("T2: weight digest not checked", 'if inv.sha256_noatime(p) != pins["files"][str(p)]["sha256"]:', "if False:"),
 ("T2: non-finite unfold accepted", "if not np.all(np.isfinite(xs)):", "if False:"),
 ("T2: B's bad factor accepted", "if not np.all(np.isfinite(f)) or np.any(f < 0):", "if False:"),
 ("T2: readout's mode/universe/schema check skipped", 'if (meta.get("mode"), meta.get("universe"), meta.get("schema")) != (mode, u, SCHEMA):', "if False:"),
 ("T2: I0's floor kind not checked", 'if r0.get("floor", {}).get("kind") != "measured":', "if False:"),
 ("T2: identity control skipped", 'if not np.allclose(prod[ok], F["total"][ok], rtol=1e-12, atol=0):', "if False:"),
 ("T2: mode A keeps non-finite weights", 'w = inv.universe_weights(weights_dir(tag, bank, det_dir), tag, "zero")', 'w = inv.universe_weights(weights_dir(tag, bank, det_dir), tag, "keep")'),
]
rows = []
try:
    for name, old, new in M:
        assert orig.count(old) == 1, name
        src.write_text(orig.replace(old, new))
        r = subprocess.run([sys.executable, "-m", "pytest", "-q", "-x", "-p", "no:cacheprovider", str(tests)],
                           capture_output=True, text=True, env=ENV)
        state = "KILLED" if r.returncode == 1 else "SURVIVED" if r.returncode == 0 else f"ERROR rc={r.returncode}"
        rows.append((name, state))
        print(f"{state:8s} {name}", flush=True)
finally:
    src.write_text(orig)
for seed in ("0", "1", "12345"):
    r = subprocess.run([sys.executable, "-m", "pytest", "-q", "-p", "no:cacheprovider", str(tests)], capture_output=True,
                       text=True, env=dict(ENV, PYTHONHASHSEED=seed))
    print(f"unmutated, PYTHONHASHSEED={seed}: rc {r.returncode}:", r.stdout.strip().splitlines()[-1])
print(f"{sum(1 for _, k in rows if k == 'KILLED')} of {len(rows)} killed")

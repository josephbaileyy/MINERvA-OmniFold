"""Mutation receipt for nd-unfolding/fd_1b_band_diag.py (FD-1B-BAND-DIAGNOSIS-DECLARATION.md section 8). Run from
nd-unfolding/: python3 <this file>. Each mutant replaces one exact string (it must occur once), the suite runs with
-x and no bytecode or cache, and the source is restored. KILLED means the suite exits 1 (a test failed); any other
non-zero exit is ERROR, not a kill. The suite then runs unmutated at three PYTHONHASHSEED values."""
import hashlib
import os
import subprocess
import sys
from pathlib import Path

src, tests = Path("fd_1b_band_diag.py"), Path("tests/test_fd_1b_band_diag.py")
orig = src.read_text()
for p in (src, tests, Path("fd_1b_precheck_fd.py"), Path("fd_1b_inv.py"), Path("fd_1b_toys.py")):
    print(f"sha256 {hashlib.sha256(p.read_bytes()).hexdigest()}  {p}")
print("KILLED means the suite exits 1 (a test failed); any other non-zero exit is ERROR, not a kill")
ENV = dict(os.environ, PYTHONDONTWRITEBYTECODE="1", PYTHONHASHSEED="0")
M = [
 # section 2: the factor, the channels and the experiments
 ("eps 1 computed, not the factor itself", "    if eps == 1.0:\n        return f\n", ""),
 ("the factor scaled linearly", "return np.power(f, eps)", "return 1.0 + eps * (f - 1.0)"),
 ("signal channel keeps the background factor", "return fs_, np.ones(fb.shape[0])", "return fs_, fb"),
 ("background channel keeps the signal factor", "return np.ones(fs_.shape[0]), fb", "return fs_, fb"),
 ("eps ignored", "fs_, fb = channel_factors(scaled(fs_, eps), scaled(fb, eps), channel)", "fs_, fb = channel_factors(fs_, fb, channel)"),
 ("eps on the signal factor only", "fs_, fb = channel_factors(scaled(fs_, eps), scaled(fb, eps), channel)", "fs_, fb = channel_factors(scaled(fs_, eps), fb, channel)"),
 ("E drops the background factor", "toys.build_full(inputs, bkg, r, fs_, fb, None, expectation=True)", "toys.build_full(inputs, bkg, r, fs_, np.ones(fb.shape[0]), None, expectation=True)"),
 ("B's signal factor dropped", 'ui = dict(inputs, w_reco=np.asarray(inputs["w_reco"], float) * fs_)', "ui = dict(inputs)"),
 ("B's background factor dropped", 'ub = dict(bkg, bkg_w=np.asarray(bkg["bkg_w"], float) * fb)', "ub = dict(bkg)"),
 # the job
 ("the seed not passed to the estimator", "(exp, a.seed, a.threads, toys.ITERS)", "(exp, BASE_SEED, a.threads, toys.ITERS)"),
 ("an item outside section 7 accepted", "if (a.mode, u, a.seed, eps, a.channel) not in legal:", "if False:"),
 ("input digests not checked", "if (npz_sha, bkg_sha) != (sa.INPUT_NPZ_SHA256, sa.BKG_SHA256):", "if False:"),
 ("pins digest not checked", "if inv.sha256_noatime(a.pins) != a.expect_pins_sha256:", "if False:"),
 ("weight digest not checked", 'if inv.sha256_noatime(p) != pins["files"][str(p)]["sha256"]:', "if False:"),
 ("a negative factor accepted", "if not np.all(np.isfinite(f)) or np.any(f < 0):", "if False:"),
 ("the job's flux refusal skipped", 'if not np.array_equal(np.asarray(exp["flux"], float), np.asarray(inputs["flux"], float)):', "if False:"),
 ("a non-finite unfold accepted", "if not np.all(np.isfinite(xs)):", "if False:"),
 ("a moved atime exits 0", "return status | 8", "return status"),
 # section 4.3
 ("row weights not compared", " | (got_w != want_w)", ""),
 ("the inputs verdict ignores the background", 'ok = all(v["signal"]["equal"] and v["background"]["equal"] for v in per.values())', 'ok = all(v["signal"]["equal"] for v in per.values())'),
 # section 4.2 and the reproduction control
 ("HK ignores B against A", "if not (dd[c] <= SAME_TOL_DNOM and da[c] <= SAME_TOL_A)]", "if not (dd[c] <= SAME_TOL_DNOM)]"),
 ("HK ignores Dnom against E", "if not (dd[c] <= SAME_TOL_DNOM and da[c] <= SAME_TOL_A)]", "if not (da[c] <= SAME_TOL_A)]"),
 ("HK's Dnom threshold loosened", "SAME_TOL_DNOM, SAME_TOL_A = 1e-12, 1e-5", "SAME_TOL_DNOM, SAME_TOL_A = 1e-11, 1e-5"),
 ("HK's A threshold loosened", "SAME_TOL_DNOM, SAME_TOL_A = 1e-12, 1e-5", "SAME_TOL_DNOM, SAME_TOL_A = 1e-12, 1e-4"),
 ("HK reads unresolved cells", "bad = [CELLS[c] for c in resolved if", "bad = [CELLS[c] for c in range(sa.N_CELLS) if"),
 ("Part 1's reproduction skipped", 'if not bits_equal(F_src, ref["F_src"]) or not bits_equal(kappa, ref["kappa"]):', "if False:"),
 ("Part 1's kappa not reproduced", 'if not bits_equal(F_src, ref["F_src"]) or not bits_equal(kappa, ref["kappa"]):', 'if not bits_equal(F_src, ref["F_src"]):'),
 ("Part 1's CV products not checked", 'if not bits_equal(p1[(mode, "CV")]["xsec_flat"], d["cv_xsec_flat"]):', "if False:"),
 ("staged digests not checked", "if want is not None and got != want:", "if False:"),
 ("a re-read digest not checked", "if seen.get(str(path), got) != got:", "if False:"),
 ("S1's digest not checked", "if inv.sha256_noatime(p) != fs.S1_NPZ_SHA256:", "if False:"),
 ("a derivation product's draw not checked", 'if json.loads(json.dumps(toys.single_universe(u))) != m.get("draw") or check_estimator(m, BASE_SEED):', "if False:"),
 ("Part 1's product identity not checked", 'if (m.get("schema"), m.get("mode"), m.get("universe")) != (pfd.SCHEMA, mode, u):', "if False:"),
 ("Dnom's object is the raw result", '"x": x - U @ xt if mode == "Dnom" else x', '"x": x'),
 ("Dnom's block carried", 'out[(mode, b)] = C if mode == "Dnom" else C * np.outer(g, g)', "out[(mode, b)] = C * np.outer(g, g)"),
 ("g against the unmapped truth", 'g = s1["f"] / (U @ truth)', 'g = s1["f"] / truth'),
 # section 7's pilot
 ("the rebuild control skipped", 'if not bits_equal(z["xsec_flat"], ref):', "if False:"),
 ("walls limit doubled", 'walls = "PASS" if s_max <= UNIT_SECONDS and r_max <= RSS_LIMIT_KIB else "REPRICE"', 'walls = "PASS" if s_max <= 2 * UNIT_SECONDS and r_max <= RSS_LIMIT_KIB else "REPRICE"'),
 ("walls RSS ignored", 'walls = "PASS" if s_max <= UNIT_SECONDS and r_max <= RSS_LIMIT_KIB else "REPRICE"', 'walls = "PASS" if s_max <= UNIT_SECONDS else "REPRICE"'),
 ("a missing pilot product passes", '            raise Refusal(f"pilot product {p.name} is missing")', "            continue"),
 ("a foreign pilot product passes", 'raise Invalid(f"{p.name}: not pilot item {mode} {u}")', "pass"),
 # sections 4.4 and 4.5
 ("window edges exclusive", "    return inv.in_window(x)", "    return (np.asarray(x) > WINDOW[0]) & (np.asarray(x) < WINDOW[1])"),
 ("a seed crossing 1 stays stable", "or math.copysign(1.0, math.log(v)) != side:", ":"),
 ("a seed reading ignores resolution", "if not res[s][c] or bool(in_window(v))", "if bool(in_window(v))"),
 ("the floor ignored", "f_n = inv.noise_factor(b, None) * sn2", "f_n = 0 * sn2"),
 ("SCALES at 0.6", "P_SCALES, P_CONSTANT = 0.5, 0.25", "P_SCALES, P_CONSTANT = 0.6, 0.25"),
 ("SCALES at 0.4", "P_SCALES, P_CONSTANT = 0.5, 0.25", "P_SCALES, P_CONSTANT = 0.4, 0.25"),
 ("CONSTANT at 0.3", "P_SCALES, P_CONSTANT = 0.5, 0.25", "P_SCALES, P_CONSTANT = 0.5, 0.3"),
 ("CONSTANT at 0.2", "P_SCALES, P_CONSTANT = 0.5, 0.25", "P_SCALES, P_CONSTANT = 0.5, 0.2"),
 ("SCALES ignores p_down", "if up >= P_SCALES and (down is None or down >= P_SCALES):", "if up >= P_SCALES:"),
 ("CONSTANT ignores p_down", "if abs(up) <= P_CONSTANT and (down is None or abs(down) <= P_CONSTANT):", "if abs(up) <= P_CONSTANT:"),
 ("a crossing at eps 2 reads +inf", 'out["p_up"] = -math.inf if ell[2.0] <= 0 else', 'out["p_up"] = math.inf if ell[2.0] <= 0 else'),
 ("a crossing at eps 1/2 reads -inf", 'out["p_down"] = math.inf if ell[0.5] <= 0 else', 'out["p_down"] = -math.inf if ell[0.5] <= 0 else'),
 ("the scale read on a seed-sensitive cell", 'if sr == "SEED-STABLE":', "if True:"),
 ("band SCALES with a MIXED cell", '        if all(v == k for v in read):', '        if any(v == k for v in read):'),
 # the readout's controls
 ("a foreign new product passes", 'raise Invalid(f"{p.name}: not item {it}")', "pass"),
 ("one-code check skipped", "if len(vals) != 1 or next(iter(metas.values())).get(key) is None:", "if False:"),
 ("seed 42's F_src not Part 1's", 'if not bits_equal(F42, ref["factors"]["F_src"]) or', "if False or"),
 ("seed 42's resolution not Part 1's", '[CELLS[c] for c in range(sa.N_CELLS) if res42[c]] != ref["resolved"]["F_src"]:', "False:"),
 ("I0's floor kind not checked", 'if r0.get("floor", {}).get("kind") != "measured":', "if False:"),
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

#!/usr/bin/env python3
"""Mutation run for the run-period diagnosis (FD-RPD-DECLARATION.md part 2 section 5): one textual change at a time to
fd_rpd_inputs.py, fd_rpd.py or submit_fd_ct.sh's rpd stages, applied in place; test_fd_rpd runs against it, stopping at
its first failure, and the file is restored (every file's sha256 checked after every mutant and at the end). A mutant is
killed if the run fails;
one whose text is not found exactly once counts as a failure of this receipt.

    python3 -I -B mutants_rpd.py <repo> [--dry]
"""
import hashlib
import os
import subprocess
import sys
from pathlib import Path

REPO = Path(sys.argv[1]).resolve()
ND = REPO / "nd-unfolding"
I, P, S = ND / "fd_rpd_inputs.py", ND / "fd_rpd.py", ND / "submit_fd_ct.sh"
MUTANTS = [
    # ---- the inputs driver
    (I, "stage: pin unchecked", "        if got != pin:\n            dst.unlink()", "        if False:\n            dst.unlink()"),
    (I, "stage: overwrite allowed", '    out = a.r / "staged"\n    fresh(out)', '    out = a.r / "staged"\n    pass'),
    (I, "stage: no O_NOATIME", 'fd = os.open(src, os.O_RDONLY | getattr(os, "O_NOATIME", 0))', "fd = os.open(src, os.O_RDONLY)"),
    (I, "staged: copy digest unchecked", '    return p, require(p, rec["files"][name]["sha256"], f"staged {name}")',
     '    return p, rec["files"][name]["sha256"]'),
    (I, "combine: error weights not squared", '.T ** 2) @ (w ** 2)) / tot_d', ".T ** 2) @ w) / tot_d"),
    (I, "F1 tolerance loose", "REL_FLUX = 1e-12", "REL_FLUX = 1e-9"),
    (I, "F1 ignores the data POT", '"pot_data": abs(comb["pot_data"] / ref["pot_data"] - 1.0),', '"pot_data": 0.0,'),
    (I, "exposure without the flux", 'raw = {pl: pot[pl] * float(np.mean(v["contents"])) for pl, v in per_pl.items()}',
     'raw = {pl: pot[pl] for pl, v in per_pl.items()}'),
    (I, "check: loop pin unchecked", "    if loop_sha != pi.ZERO_LOOPS[X]:", "    if False:"),
    (I, "check: flux digest unchecked", '    require(d["flux"], fsha, f"{X} flux file")\n', "    pass\n"),
    (I, "check: nn vs lat unchecked", "    if not all(nn_vs_lat.values()):\n        problems.append(f\"the lateral",
     "    if False:\n        problems.append(f\"the lateral"),
    (I, "check: background meta unchecked",
     '        problems.append("the background dump does not name this lateral npz and staged loop")', "        pass"),
    (I, "check: flux key unchecked", "    if flux_dev > REL_FLUX:", "    if False:"),
    (I, "check: data POT unchecked", "    if max(abs(v) for v in pot.values()) > POT_REL:", "    if False:"),
    (I, "check: mc_pot not recorded", '"mc_pot": mc_pot,', '"mc_pot": data_pot,'),
    (I, "check: F1 verdict unchecked", '    if (rec.get("schema"), rec.get("verdict")) != ("fd-rpd-flux/1", "PASS"):',
     '    if rec.get("schema") != "fd-rpd-flux/1":'),
    (I, "N0: denominator scaled", '            z["denom_nd"] = np.where(o_all > 0, dn_all * o_k / o_all, float(e[k]) * dn_all)',
     '            z["denom_nd"] = float(e[k]) * dn_all'),
    (I, "N0: data POT unscaled", '        z["data_pot"] = float(lat["data_pot"]) * float(e[k])',
     '        z["data_pot"] = float(lat["data_pot"])'),
    (I, "N0: seed ignored", "    rng = np.random.default_rng(seed)\n    a = {", "    rng = np.random.default_rng(0)\n    a = {"),
    (I, "N0: background histogram not its own",
     'b["bkg_nd"] = histnd_counts([b["bkg_reco"][:, i] for i in range(b["bkg_reco"].shape[1])], b["bkg_w"], edges)',
     'b["bkg_nd"] = np.asarray(bkg["bkg_nd"])'),
    (I, "unfold: existing product allowed", "    fresh(*targets)\n    require(Path(lat)", "    require(Path(lat)"),
    (I, "unfold: four iterations", '"--config", "R", "--iters", "5",', '"--config", "R", "--iters", "4",'),
    (I, "unfold: missing product accepted", "    if rc == 0 and missing:", "    if False:"),
    (I, "unfold: receipt schema unchecked",
     '        if (rec.get("schema"), rec.get("playlist")) != ("fd-rpd-inputs/1", X):\n            raise Refuse(4, f"not {X}\'s check receipt")',
     "        if False:\n            pass"),
    # ---- the readers
    (P, "region beyond the reported cells", "self.wH = np.where(rep & (lo >= H_REGION[0])", "self.wH = np.where((lo >= H_REGION[0])"),
    (P, "step inverted", "return float((dn[1] / dd[1]) / (dn[0] / dd[0]) - 1.0)", "return float((dn[0] / dd[0]) / (dn[1] / dd[1]) - 1.0)"),
    (P, "reference keeps X", "    return tuple(m for m in A_SET if m != X)", "    return tuple(A_SET)"),
    (P, "CARRIES against tbar", '"h": {X: t[X] - tbar / 2 for X in PL}', '"h": {X: t[X] - tbar for X in PL}'),
    (P, "resolution unchecked", "    if unres_forced or not s < tbar / R1_RES:", "    if unres_forced:"),
    (P, "FREE at 3 sigma", "    free = abs(t) <= R1_Z * s\n", "    free = abs(t) <= 1.5 * R1_Z * s\n"),
    (P, "PERIOD-WIDE with one resolved", "    if len(rb) >= 2 and all(", "    if len(rb) >= 1 and all("),
    (P, "no resolved earlier playlist needed", '    a_ok = len(ra) >= 1 and all(c == "FREE" for c in ra)',
     '    a_ok = all(c == "FREE" for c in ra)'),
    (P, "SUBSET allows PARTIAL", ' and "PARTIAL" not in rb and a_ok:', " and a_ok:"),
    (P, "partitions not deduplicated", "            if acc and len(acc[-1]) == k and len(sz) and comb[0] < acc[-1][0]:\n                continue",
     "            pass"),
    (P, "F without group shares", "    return (num / E).sum(axis=1) / q_tot", "    return num.sum(axis=1) / q_tot"),
    (P, "p excludes ties", "return float(np.mean(F >= F[i_obs] * (1.0 - 1e-12)))", "return float(np.mean(F > F[i_obs] * (1.0 + 1e-12)))"),
    (P, "sigma_delta without 1 - V2", '"xi,xj->xij", g, g)).sum(axis=0) / (1.0 - V2)', '"xi,xj->xij", g, g)).sum(axis=0)'),
    (P, "gate threshold loose", "    thr = R2_ALPHA + 3.0 * math.sqrt(", "    thr = R2_ALPHA + 30.0 * math.sqrt("),
    (P, "size bias ignored by R2", "    if size_bias_g or not calibrated:", "    if not calibrated:"),
    (P, "EC without power", "    if beta1 >= R2_BETA:", "    if True:"),
    (P, "S1 not shrunk", "        c = math.sqrt(max(0.0, 1.0 - qn / qo)) if qo > 0 else 0.0", "        c = 1.0"),
    (P, "SEES without the half-step floor", "    if s0 >= SEES_MIN and z >= SEES_Z:", "    if z >= SEES_Z:"),
    (P, "ABSENT one-sided", "    if abs(z) < ABSENT_Z:", "    if z < ABSENT_Z:"),
    (P, "sigma0 about the replica mean", "sig0 = float(np.sqrt(np.mean(np.square(np.array(pairs) - s0))))", "sig0 = float(np.std(pairs))"),
    (P, "stage D PW rule inverted", '    rule_pw = oc["PW"]["PERIOD-WIDE"] < STAGE_D_RULE_PW', '    rule_pw = oc["PW"]["PERIOD-WIDE"] > STAGE_D_RULE_PW'),
    (P, "stage D SUBSET rule inverted", "    rule_sub = best_sub < STAGE_D_RULE_PW", "    rule_sub = best_sub > STAGE_D_RULE_PW"),
    (P, "stage D verdict on too few datasets", "    ec_verdict = None if n_t1 < STAGE_D_MIN_OUTER else", "    ec_verdict = None if False else"),
    (P, "stage D budget ignored", "            if clock() - t0 > budget_s:", "            if False:"),
    (P, "C1 weights unscaled", "scaled_equal(src[X][k], ref[k][cuts[i]:cuts[i + 1]], s[X] / s_all)",
     "scaled_equal(src[X][k], ref[k][cuts[i]:cuts[i + 1]], 1.0)"),
    (P, "C1 histogram tolerance loose", "C1_HIST_REL, C1_W_REL = 1e-9, 1e-12", "C1_HIST_REL, C1_W_REL = 1e-2, 1e-12"),
    (P, "C1 zero weights unchecked", "    if np.any(a[z] != 0):\n        return False\n", ""),
    (P, "C1 flux unchecked", '    res["flux"] = all(', '    res["flux"] = True or all('),
    (P, "K2 to a tolerance", "out[str(b)] = bool(np.array_equal(x, sa.xs(ref)))", "out[str(b)] = bool(np.allclose(x, sa.xs(ref), rtol=1e-12))"),
    (P, "N0-P completeness unchecked", '        chk["completeness_equal"] = all(comp_ok)', '        chk["completeness_equal"] = True'),
    (P, "gate b receipts unchecked", '            if r["inputs_sha256"]["receipts"][X] != sa.sha256(a.r / ri.playlist_paths(X)["receipt"]):',
     "            if False:"),
    (P, "gate a without stage D", '(("stage0.json", "fd-rpd-stage0/1"), ("stageD.json", "fd-rpd-stageD/1"))',
     '(("stage0.json", "fd-rpd-stage0/1"),)'),
    (P, "N0 at normal quantiles", "N0_T_CELL, N0_T_STEP = 3.835, 2.756", "N0_T_CELL, N0_T_STEP = 3.42, 2.58"),
    (P, "R1 outside SEES", '    if s0rec["branch"] != "SEES":', "    if False:"),
    (P, "R1 gate on tbar removed", "    if not r1_gate(tbar, sig_tbar):", "    if False:"),
    (P, "5B block not checked", "    if not np.allclose(C, ref, rtol=1e-9, atol=1e-9 * np.abs(ref).max()):", "    if False:"),
    (P, "readout without the controls", '    if (cj.get("schema"), cj.get("verdict")) != ("fd-rpd-controls/1", "PASS"):\n        raise f0.Stop("Q0"',
     '    if False:\n        raise f0.Stop("Q0"'),
    # ---- audit 1 (part 2): the auditor's surviving mutants, and the code added in answer
    (P, "SIZE-BIAS-t does not force UNRESOLVED", '    if not (n0r["SIZE_BIAS_g"] or n0r["SIZE_BIAS_t"]):', '    if not n0r["SIZE_BIAS_g"]:'),
    (P, "T1 without the V2 scaling", "    sT1, _ = psd(C5 / V2)", "    sT1, _ = psd(C5)"),
    (P, "T3 at full amplitude", "    return T2 / math.sqrt(2.0) + z @ LT1.T / math.sqrt(2.0)", "    return T2 + z @ LT1.T"),
    (P, "deviations without sqrt(n/(n-1))", "    return (v / v.mean(axis=0) - 1.0) * math.sqrt(n / (n - 1))", "    return v / v.mean(axis=0) - 1.0"),
    (P, "R2 noise without T variance", " + rng.standard_normal(tsd.shape) * tsd", ""),
    (P, "N0 SE with ddof 0", "    b, se = G.mean(axis=0), G.std(axis=0, ddof=1) / math.sqrt(n)", "    b, se = G.mean(axis=0), G.std(axis=0, ddof=0) / math.sqrt(n)"),
    (P, "R1 sigma without T variance", '    sig = {X: math.sqrt(sd([q["t"][X] for q in reps]) ** 2 + tn[X]) for X in PL}',
     '    sig = {X: sd([q["t"][X] for q in reps]) for X in PL}'),
    (P, "R1 sigma_h without T variance", '    sigh = {X: math.sqrt(sd([q["h"][X] for q in reps]) ** 2 + hn[X]) for X in PL}',
     '    sigh = {X: sd([q["h"][X] for q in reps]) for X in PL}'),
    (P, "R1 sigma(tbar) without T variance", '    sig_tbar = math.sqrt(sd([q["tbar"] for q in reps]) ** 2 + tbn)', '    sig_tbar = sd([q["tbar"] for q in reps])'),
    (P, "stage D outer 50", "STAGE_D_R1_DRAWS, STAGE_D_OUTER, STAGE_D_INNER = 20000, 500, 200", "STAGE_D_R1_DRAWS, STAGE_D_OUTER, STAGE_D_INNER = 20000, 50, 200"),
    (P, "stage D inner 20", "STAGE_D_R1_DRAWS, STAGE_D_OUTER, STAGE_D_INNER = 20000, 500, 200", "STAGE_D_R1_DRAWS, STAGE_D_OUTER, STAGE_D_INNER = 20000, 500, 20"),
    (I, "N0 seed offset", "N0_SEED0 = 20261102 ", "N0_SEED0 = 20261103 "),
    (P, "forced UNRESOLVED not passed to classify", "sigh[X], tbar, X in forced) for X in PL}", "sigh[X], tbar, False) for X in PL}"),
    (P, "stage D OC seed at the call", "    oc = oc_table(e, s0, sig0, STAGE_D_R1_DRAWS, SEED_OC)",
     "    oc = oc_table(e, s0, sig0, STAGE_D_R1_DRAWS, SEED_OC + 1)"),
    (P, "stage D reachability seed at the call", "ro5, SEED_REACH, a.outer", "ro5, SEED_REACH + 1, a.outer"),
    (P, "readout seed at the call", "    rng = np.random.default_rng(SEED_READOUT)\n    sim = r2.run",
     "    rng = np.random.default_rng(SEED_READOUT + 1)\n    sim = r2.run"),
    (P, "N0 effect seed at the call", "np.random.default_rng(SEED_N0_EFFECT), small", "np.random.default_rng(SEED_N0_EFFECT + 1), small"),
    (P, "the seed offsets", "= SEED + 2000, SEED + 3000, SEED, SEED + 4000", "= SEED + 2001, SEED + 3000, SEED + 1, SEED + 4000"),
    (P, "k12 = V2", "    k12 = V2 / (1 - V2)\n\n    def block(h):", "    k12 = V2\n\n    def block(h):"),
    (P, "rho_raw against the debiased 5D block", "    rho_raw = math.sqrt(np.trace(Mi @ C12) / t5)", "    rho_raw = math.sqrt(np.trace(Mi @ C12) / t5d)"),
    (P, "era groups mis-assigned", '("1F-1G", ("1F", "1G")), ("1L-1M", ("1L", "1M"))', '("1F-1G", ("1F", "1L")), ("1L-1M", ("1G", "1M"))'),
    (P, "stage 0 pairs reversed", 'zip(cp.BOOT["PA"], cp.BOOT["PB"])]', 'zip(cp.BOOT["PA"], cp.BOOT["PB"][::-1])]'),
    (P, "stage D noise not scaled by sqrt(E_P/e_X)", '"noise_sd": np.vstack([sn[GROUP[X]] * math.sqrt(E[GROUP[X]] / e[i]) for i, X in enumerate(PL)])',
     '"noise_sd": np.vstack([sn[GROUP[X]] for i, X in enumerate(PL)])'),
    (P, "R1 gate at 2", "    return bool(tbar > 0 and sig_tbar > 0 and tbar / sig_tbar >= R1_GATE)", "    return bool(tbar > 0 and sig_tbar > 0 and tbar / sig_tbar >= 2.0)"),
    (P, "N0-P share bound at 50 sigma", "def shares_within(counts: np.ndarray, n: int, e: np.ndarray, k: float = 5.0) -> bool:",
     "def shares_within(counts: np.ndarray, n: int, e: np.ndarray, k: float = 50.0) -> bool:"),
    (P, "C1 measured_weights share 0", "C1_MW_SHARE = 0.999 ", "C1_MW_SHARE = 0.0 "),
    (P, "Q3 removed", '        if not (finite_positive(grid.cells(v)) and finite_positive(grid.regions(v))):', "        if False:"),
    (P, "readout guard without the integrals", "    guard = cp.guarded(f, ints)\n    M = S", "    guard = cp.guarded(f, [])\n    M = S"),
    (P, "N0 small set the three largest", "    return sorted(int(i) for i in np.argsort(ev)[:3])", "    return sorted(int(i) for i in np.argsort(ev)[-3:])"),
    (P, "N0 effect without the bias", "    d[small] = b\n", ""),
    (P, "gate a: stage D on another F1", '        if sd.get("flux_record") != f1 or sd.get("stage0") != sa.sha256(a.r / "control/stage0.json"):',
     "        if False:"),
    (P, "gate a: stage records of other code", '            if (recs[name].get("code_sha256") or {}).get("fd_rpd.py") != me:', "            if False:"),
    (P, "gate b: N0 receipts unchecked", '            if sha != sa.sha256(a.r / ri.n0_paths(int(part), 0)["receipt"]):', "            if False:"),
    (P, "gate b: F1 unchecked", '        if r["inputs_sha256"].get("flux_record") != f1:', "        if False:"),
    (P, "read_truth: non-finite accepted", "    if not (np.all(np.isfinite(t)) and np.all(np.isfinite(v))):", "    if False:"),
    (I, "F1: loops' POT unchecked", "    loops_ok = all(abs(v[\"over_flux_data_pot_minus_1\"]) <= POT_REL for v in loops.values())",
     "    loops_ok = True"),
    (I, "e from the flux file's POT", '    e, spread = exposure_shares(per_pl, {pl: v["data_pot"] for pl, v in loops.items()})',
     "    e, spread = exposure_shares(per_pl)"),
    (S, "submit rpd: outside paths allowed", '[ -z "$out" ] || { echo "refusing: a step names a path outside $B: $out" >&2; exit 2; }',
     "true"),
    (S, "submit rpd: step-count check skipped", '    [ "$n" -eq "$N" ] && [ "$m" -eq "$N" ] || { echo "refusing: $n steps, $m of them naming $B" >&2; exit 2; }\n    # every absolute',
     "    true\n    # every absolute"),
    # ---- the submit stages
    (S, "submit rpd-a: limit", "N=48; TIME=01:00:00", "N=48; TIME=02:00:00"),
    (S, "submit rpd-b: limit", "N=492; TIME=02:00:00", "N=492; TIME=03:00:00"),
    (S, "submit rpd: mcfile check skipped", '    [ "$nd" -eq "$md" ] ||', "    true ||"),
    (S, "submit rpd: one gate for both jobs", 'fd_rpd.py" gate --stage "${STAGE#rpd-}"', 'fd_rpd.py" gate --stage a'),
    (S, "submit rpd-a: stage S not required", '        [ -d "$B/$d" ] || { echo "refusing: $B/$d is missing', '        true || { echo "refusing: $B/$d is missing'),
    (S, "submit rpd-a: existing dumps allowed", "      for d in dumps truth inputs n0 unf-k2 lanes-a; do", "      for d in truth inputs lanes-a; do"),
]


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


orig = {p: p.read_text() for p in (I, P, S)}
digest = {p: sha(p) for p in orig}
env = {k: v for k, v in os.environ.items() if k != "PYTHONPATH"}
if "--dry" in sys.argv:
    bad = [(n, orig[p].count(o)) for p, n, o, _ in MUTANTS if orig[p].count(o) != 1]
    print(f"{len(MUTANTS)} mutants; not applicable exactly once: {bad}")
    raise SystemExit(1 if bad else 0)
killed = survived = unapplied = 0
print(f"files {[f'{p.name} {digest[p][:16]}' for p in orig]}  mutants {len(MUTANTS)}", flush=True)
try:
    for path, name, old, new in MUTANTS:
        text = orig[path]
        if text.count(old) != 1:
            unapplied += 1
            print(f"NOT APPLIED  {name}: found {text.count(old)} times", flush=True)
            continue
        path.write_text(text.replace(old, new))
        r = subprocess.run([sys.executable, "-B", "-m", "unittest", "-f", "test_fd_rpd"],
                           cwd=ND / "tests", env=env, capture_output=True, text=True, timeout=3600)
        path.write_text(text)
        if any(sha(p) != digest[p] for p in orig):
            raise SystemExit("a file was not restored")
        ok = r.returncode != 0
        killed += ok
        survived += not ok
        tail = [ln for ln in r.stderr.splitlines() if ln.startswith(("FAILED", "OK", "Ran"))]
        print(f"{'KILLED  ' if ok else 'SURVIVED'}  {name}  ({'; '.join(tail)})", flush=True)
finally:
    for p, t in orig.items():
        p.write_text(t)
restored = all(sha(p) == digest[p] for p in orig)
print(f"killed {killed} of {len(MUTANTS)}; survived {survived}; not applied {unapplied}; files restored {restored}")
raise SystemExit(0 if survived == 0 and unapplied == 0 and restored else 1)

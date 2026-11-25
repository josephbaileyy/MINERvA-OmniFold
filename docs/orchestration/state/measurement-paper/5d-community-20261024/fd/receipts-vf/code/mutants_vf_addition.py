#!/usr/bin/env python3
"""Mutation run for V_F's adoption (FD-VF-ADDITION-DECLARATION.md section 2): one textual change at a time to
nd-unfolding/fd_vf_addition.py, applied in place in the repository copy given (never a working checkout). Each mutated
source is compiled first: a mutant that does not compile is INVALID, never killed. The unmutated suite must pass
first (the baseline), or nothing is counted. A valid mutant is KILLED if test_fd_vf_addition reports a failure or an
error, TIMEOUT if the suite does not finish (not counted as killed), and SURVIVED if it passes. One whose text is not
found exactly once is MISSING. The file is restored and its sha256 checked after every mutant and at the end.

    python3 -I -B mutants_vf_addition.py <repo copy>        (--dry: only that every mutant applies once and compiles)
"""
import hashlib
import subprocess
import sys
from pathlib import Path

REPO = Path(sys.argv[1]).resolve()
DRY = "--dry" in sys.argv
TARGET = REPO / "nd-unfolding/fd_vf_addition.py"
TESTS = REPO / "nd-unfolding/tests"
MUTANTS = [
    # V0-V4: the block
    ("V0: the record's V_F pin unchecked", 'rec["matrices_sha256"]["V_F.csv"] == PINS["v_f_csv"])', "True)"),
    ("V0: the record's V_F not compared with the CSV", "np.array_equal(VFj, VF))", "True)"),
    ("V1: C_e not the product's", 'np.array_equal(Ce, mats["C_e"]))', "True)"),
    ("V1: the cpl block's C_PL5D unchecked", 'and np.array_equal(cpl["C_PL5D"], mats["C_PL5D"]))', ")"),
    ("V2: V_F = L C_e L^T loose", "<= TOL * float(np.abs(VF).max()))", "<= 1.0 * float(np.abs(VF).max()))"),
    ("V2: L's symmetry unchecked", 'report("V2", "L is symmetric", symmetric(L))', 'report("V2", "L is symmetric", True)'),
    ("V2: commutation loose", "<= TOL * float(np.abs(L @ Ce).max()))", "<= 10.0 * float(np.abs(L @ Ce).max()))"),
    ("V3: dF's PSD unchecked", "bool(lam.min() >= -TOL * lam.max())", "True"),
    ("block: dF scaled", "    dF = VF - Ce\n", "    dF = (VF - Ce) * 1.0000001\n"),
    ("block: C_resp + dF without dF", '"C_resp_plus_dF": mats["C_resp"] + dF,', '"C_resp_plus_dF": mats["C_resp"],'),
    ("block: the reported block without dF", '"C_resp_plus_C_PL5D_plus_dF": cpl[X_PL] + dF}',
     '"C_resp_plus_C_PL5D_plus_dF": cpl[X_PL]}'),
    ("block: the reported matrix without dF", '    rep_f = mats["C_total_plus_C_resp_plus_C_PL5D"] + dF\n',
     '    rep_f = mats["C_total_plus_C_resp_plus_C_PL5D"]\n'),
    ("block: the matrix without C_PL5D, without dF", '    wo_f = mats["C_total_plus_C_resp"] + dF\n',
     '    wo_f = mats["C_total_plus_C_resp"]\n'),
    ("block: the keys of the two sides swapped",
     'SIDE_KEY = {"with": "C_resp_plus_C_PL5D_plus_dF", "nopl": "C_resp_plus_dF"}',
     'SIDE_KEY = {"with": "C_resp_plus_dF", "nopl": "C_resp_plus_C_PL5D_plus_dF"}'),
    # K: the product
    ("K0: product runs without the chain's pins", '    if pins is None:\n        raise Stop("K0", "product runs',
     '    if False:\n        raise Stop("K0", "product runs'),
    ("K0: the committed product's pin unchecked",
     'report("K0", "the committed data product\'s pin is the declared one", pins["data_product"] == PINS["data_product_cpl"])',
     'report("K0", "the committed data product\'s pin is the declared one", True)'),
    ("K1: Stage G's block name unchecked", 'and xb["key"] == SIDE_KEY["with"] and xb["name"] == BLOCKS[SIDE_KEY["with"]]',
     'and xb["key"] == SIDE_KEY["with"]'),
    ("K1: Stage G's block key unchecked", 'and xb["key"] == SIDE_KEY["with"] and xb["name"] == BLOCKS[SIDE_KEY["with"]]',
     'and xb["name"] == BLOCKS[SIDE_KEY["with"]]'),
    ("K2: dF not V_F - C_e", 'np.array_equal(dF, blk["V_F"] - blk["C_e"]))', "True)"),
    ("K3: Stage G's sigma loose", 'F.worst(np.array(p["sigma_total_over_f"]), sig[idx]) <= TOL',
     'F.worst(np.array(p["sigma_total_over_f"]), sig[idx]) <= 1.0'),
    ("K3: Stage G's covariance name unchecked", 'and p["reported_covariance"] == REPORTED_NAME)', ")"),
    ("product: the reported matrix is the one without C_PL5D", "WITHOUT_F: blk[WITHOUT_F], REPORTED_F: blk[REPORTED_F]}",
     "WITHOUT_F: blk[WITHOUT_F], REPORTED_F: blk[WITHOUT_F]}"),
    ("deposit variant: the key without C_PL5D", "    return DC.Variant(key=REPORTED_F,", "    return DC.Variant(key=WITHOUT_F,"),
    # T: the table
    ("T: keys not renamed", '    return key.replace(" + dF", "")', "    return key"),
    ("T: Stage G's V_F matrix not checked", 'and pn[kind]["matrix"] == vf_matrix(po[kind]["matrix"], True),', ","),
    ("T: dF placed after V_g", 'old_name.replace(" + V_g", " + dF + V_g", 1)', 'old_name + " + dF"'),
    ("T: cleared truths dropped", '"cleared": sorted(set(listed(o)) - set(listed(n)))}', '"cleared": []}'),
    ("table: runs without the chain's pins", '    if pins is None:\n        raise Stop("T", "table runs',
     '    if False:\n        raise Stop("T", "table runs'),
    # the chain: arms, argv, order
    ("arms: OLD with takes the nopl block", 'if kind == "old" and side == "with":', 'if kind == "old" and side == "nopl":'),
    ("F0: the V_F arm takes no block", 'xb0 = [] if arm == "old-f0" else', "xb0 = [] if True else"),
    ("F1: the V_F arm's F0b digest wrong", '{"f0b": out["f0b"], "f0b_sha256": A.sha256(out["f0b"])})',
     '{"f0b": out["f0b"], "f0b_sha256": "0" * 64})'),
    ("S: the nopl side checked against the reported matrix", 'M = blk[REPORTED_F] if side == "with" else blk[WITHOUT_F]',
     "M = blk[REPORTED_F]"),
    ("chain: the chdefs OLD with arm's strings not compared", 'strings=(side == "with"))', "strings=False)"),
    ("runner: the figures check goes through BOOT", "if pins is None or tool == CLI_ONLY:", "if pins is None:"),
    ("S: the f0b branch dropped", '    if f0b is not None:\n        b = load_strict(f0b.read_bytes())', '    if False:\n        b = load_strict(f0b.read_bytes())'),
    ("chain: the OLD product and deposit skipped", "        old_product_deposit(cS, D, pS, BA)\n", "        pass\n"),
    ("chain: the V_F part before the OLD product and deposit", "        old_product_deposit(cS, D, pS, BA)\n        vf_arms(cS, cE, D, BA, vf, blk, tables)\n", "        vf_arms(cS, cE, D, BA, vf, blk, tables)\n        old_product_deposit(cS, D, pS, BA)\n"),
    ("R: numbers not compared", "    return (A.compare_numbers(old, new, exclude) + finite_mismatch(old, new)",
     "    return ([] + finite_mismatch(old, new)"),
    ("R: finiteness not compared", "    return (A.compare_numbers(old, new, exclude) + finite_mismatch(old, new)",
     "    return (A.compare_numbers(old, new, exclude) + []"),
    ("R: Infinity accepted when decoding", "    return json.loads(raw, parse_constant=_reject_constant)", "    return json.loads(raw)"),
    ("R: strings never compared", "            + (A.compare_strings(old, new, exclude) if strings else []))", "            + [])"),
    ("R: the committed pin unchecked", 'c.check(f"R {label}: the committed readout is the pinned bytes", hashlib.sha256(raw).hexdigest() == pin, rel)',
     'c.check(f"R {label}: the committed readout is the pinned bytes", True, rel)'),
    ("R: the experiment table not the declared one", "r.get(\"table_sha256\") == h == want,", "r.get(\"table_sha256\") == h,"),
    ("R figures: the PDF bytes not compared", 'not bad and (fig / f"{n}.pdf").read_bytes() == (D / OLD_E_FIG / f"{n}.pdf").read_bytes(),',
     "not bad,"),
    ("R figures: E-A2's receipt bytes unchecked", 'A.sha256(D / OLD_E_FIG / f"{n}{e}") == sums.get(f"{n}{e}"), f"{n}{e}")', 'True, f"{n}{e}")'),
    ("C: the argv's block digest unchecked", 'ok = (fl("--extra-block-sha256") == vf_sha and fl("--extra-block-key") == key', 'ok = (fl("--extra-block-key") == key'),
    ("C: a readout with no block digest passes", "and bool(digests) and all(v == vf_sha for v in digests)", "and all(v == vf_sha for v in digests)"),
    ("C: the role unchecked", '(fl("--extra-block-role") == "adopted" if role else "--extra-block-role" not in a)', "True"),
    ("C: duplicate references unchecked", "and all(ref.get(f, h) == h for f, h in upstream.items()))", ")"),
    ("C: argv naming the digest twice passes", "return a[a.index(f) + 1] if a.count(f) == 1 else None", "return a[a.index(f) + 1] if f in a else None"),
    ("C: F0 not checked", '        check_c(c, f"{arm} f0", out, vf["sha"], "dF", {}, role=False)\n', "        pass\n"),
    ("C: a chdefs V_F step not checked", '            check_c(c, f"E {arm} {k}", out[k], vf["sha"], SIDE_KEY[side],', '            (lambda *x, **y: None)(c, f"E {arm} {k}", out[k], vf["sha"], SIDE_KEY[side],'),
    ("S: Stage G's predictions and cells unchecked", "have == declared_cells() and all(len(q[\"sigma_total_over_f\"]) == len(q[\"cells\"]) for q in gr[\"predictions\"]),", "True,"),
    ("K3: Stage G's predictions and cells unchecked", '[(p["name"], p["cells"]) for p in gr["predictions"]] == declared_cells()', "True"),
    ("K6: the files on disk not read back", '        report("K6", f"{n}: the file on disk is the bytes written", (out / n).read_bytes() == text.encode())', '        pass'),
    ("K6: the cells CSV not read back", '[r["cell"] for r in rows] == CELLS and np.array_equal(np.array([float(r["f"]) for r in rows]), p["f"])', "True"),
    ("T: truths' order unchecked", 'bool(o["truths"]) and [t["name"] for t in o["truths"]] == [t["name"] for t in n["truths"]])', "True)"),
    ("T: the V_F grade matrix not checked", 'tn["grade_matrix"] == vf_matrix(to["grade_matrix"], False)', "True"),
    ("T: Stage G's cells not paired", '== [(p["name"], p["cells"]) for p in n["predictions"]])', '== [(p["name"], p["cells"]) for p in o["predictions"]])'),
    ("T: unpaired leaves dropped", '                unpaired.append(f"{path}/{k} ({\'OLD\' if k in old else \'V_F\'} only)")', "                pass"),
    ("T: F0's revised sigma not required", 'out["f0_sigma"]["vf"] is not None)', "True)"),
    ("T: the pairs' pins not the chain's", "pins.get(po) == ho and pins.get(pn) == hn for _, po, ho, pn, hn in pairs))", "True for _ in pairs))"),
    ("chain: OLD chdefs downstream reads fresh upstreams", '    if kind == "old":\n        src = {k: p.D / OLD_E[side][k][0] for k in E_STEPS}', '    if False:\n        src = {k: p.D / OLD_E[side][k][0] for k in E_STEPS}'),
    ("chain: figures drawn in the nopl arms", '    if side != "with":\n        return res', '    if False:\n        return res'),
    ("chain: F0's OLD control dropped", '        check_r(cS, "F0", D, *OLD_F0, f0, strings=False)\n', "        pass\n"),
    ("chain: Stage G set S OLD controls dropped", '                check_r(cS, f"S {arm} {k}", D, *OLD_S[side][k], out[k], strings=False)\n', "                pass\n"),
    ("chain: the chdefs OLD controls dropped", '                check_r(cE, f"E {arm} {k}", D, *OLD_E[side][k], res["out"][k], strings=(side == "with"))\n', "                pass\n"),
    ("chain: the committed block's pin unchecked", "hashlib.sha256(raw).hexdigest() == VF_BLOCK_NPZ, str(vnpz))", "True, str(vnpz))"),
    ("chain: the chdefs manifest unchecked", 'A.sha256(pE.s5p_sums) == CHDEFS_SUMS,', "True,"),
    ("chain: an existing run directory overwritten", 'report("C", f"{d} does not exist (no overwrite)", not (BA / d).exists() and not (BA / d).is_symlink())', 'report("C", f"{d} does not exist (no overwrite)", True)'),
    ("chain: matplotlib's cache left at home", '    os.environ["MPLCONFIGDIR"] = str(BA / "mpl")', '    pass'),
    ("BOOT: the variants' modules swapped", '(A if variant == "with-cpl" else V)', '(V if variant == "with-cpl" else A)'),
]


def sha(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def main() -> int:
    orig = TARGET.read_text()
    h0 = sha(TARGET)
    rows, bad = [], 0
    if not DRY:
        b = subprocess.run([sys.executable, "-B", "-m", "unittest", "-q", "test_fd_vf_addition"], cwd=TESTS,
                           capture_output=True, text=True, timeout=1200)
        print(f"baseline: the unmutated suite rc {b.returncode}", flush=True)
        if b.returncode != 0:
            print("STOP: the baseline fails; no mutant is counted", flush=True)
            print(b.stderr[-3000:], flush=True)
            return 9
    for name, old, new in MUTANTS:
        n = orig.count(old)
        if n != 1:
            rows.append(("MISSING", name, f"found {n} times"))
            bad += 1
            continue
        src = orig.replace(old, new, 1)
        try:
            compile(src, str(TARGET), "exec")
        except SyntaxError as e:
            rows.append(("INVALID", name, f"SyntaxError: {e.msg} line {e.lineno}"))
            bad += 1
            continue
        if DRY:
            rows.append(("APPLIES", name, ""))
            continue
        TARGET.write_text(src)
        try:
            r = subprocess.run([sys.executable, "-B", "-m", "unittest", "-q", "test_fd_vf_addition"], cwd=TESTS,
                               capture_output=True, text=True, timeout=1200)
            status = "SURVIVED" if r.returncode == 0 else "KILLED"
        except subprocess.TimeoutExpired:
            status = "TIMEOUT"
        finally:
            TARGET.write_text(orig)
        if sha(TARGET) != h0:
            print("STOP: the target was not restored", flush=True)
            return 9
        rows.append((status, name, ""))
        if status in ("SURVIVED", "TIMEOUT"):
            bad += 1
        print(f"{status:9s} {name}", flush=True)
    for s, n, why in rows:
        if s in ("MISSING", "INVALID", "APPLIES"):
            print(f"{s:9s} {n} {why}", flush=True)
    counts = {s: sum(1 for r in rows if r[0] == s) for s in ("KILLED", "SURVIVED", "TIMEOUT", "INVALID", "MISSING", "APPLIES")}
    print(f"mutants {len(MUTANTS)}: " + ", ".join(f"{k} {v}" for k, v in counts.items() if v), flush=True)
    print(f"target sha256 {sha(TARGET)} (restored: {sha(TARGET) == h0})", flush=True)
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())

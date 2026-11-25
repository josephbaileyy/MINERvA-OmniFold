#!/usr/bin/env python3
"""Mutation run for V_F's adoption (FD-VF-ADDITION-DECLARATION.md section 2): one textual change at a time to
nd-unfolding/fd_vf_addition.py, applied in place in the repository copy given (never a working checkout). Each mutated
source is compiled first: a mutant that does not compile is INVALID, never killed. The unmutated suite must pass
first (the baseline, with every test), or nothing is counted. Mutants run with VF_MUTANT_RUN=1, which skips the one
exact-provenance test (the committed vf_block.json records this file's sha256, so any textual change fails it: a
false kill); the baseline is also run that way, and its test count N recorded. A valid mutant is KILLED only if
the suite ran to its summary, the test module imported (no "Failed to import test module" / _FailedTest), and it
reported a failure or an error;
HARNESS if it ended without a summary (an import failure or crash, counted as a failure of this receipt); TIMEOUT if
it did not finish (also counted); and SURVIVED if it passed. One whose text is not
found exactly once is MISSING. The file is restored and its sha256 checked after every mutant and at the end.

    python3 -I -B mutants_vf_addition.py <repo copy>        (--dry: only that every mutant applies once and compiles)
"""
import hashlib
import os
import re
import subprocess
import sys
from pathlib import Path

REPO = Path(sys.argv[1]).resolve()
DRY = "--dry" in sys.argv
TARGET = REPO / "nd-unfolding/fd_vf_addition.py"
TESTS = REPO / "nd-unfolding/tests"
MUTANTS = [
    # V0-V4: the block
    ("V0: the record's V_F (C_e^infl) pin unchecked", 'rec["matrices_sha256"]["V_F.csv"] == PINS["v_f_csv"])', "True)"),
    ("V0: the record's V_F not compared with the CSV", "same_bits(VFj, VF))", "True)"),
    ("V1: C_e not the product's", 'same_bits(Ce, mats["C_e"]))', "True)"),
    ("V1: the cpl block's C_PL5D unchecked", 'and same_bits(cpl["C_PL5D"], mats["C_PL5D"]))', ")"),
    ("V2: V_F = L C_e L^T loose", "<= TOL * float(np.abs(VF).max()))", "<= 1.0 * float(np.abs(VF).max()))"),
    ("V2: L's symmetry unchecked", 'report("V2", "L is symmetric", symmetric(L))', 'report("V2", "L is symmetric", True)'),
    ("V2: commutation loose", "<= TOL * float(np.abs(L @ Ce).max()))", "<= 10.0 * float(np.abs(L @ Ce).max()))"),
    ("V3: dF's PSD unchecked", "bool(lam.min() >= -TOL * lam.max())", "True"),
    ("block: dF scaled", "    dF = VF - Ce\n", "    dF = (VF - Ce) * 1.0000001\n"),
    ("block: C_resp + DeltaC_e without dF", '"C_resp_plus_DeltaC_e": mats["C_resp"] + dF,', '"C_resp_plus_DeltaC_e": mats["C_resp"],'),
    ("block: the reported block without dF", '"C_resp_plus_C_PL5D_plus_DeltaC_e": cpl[X_PL] + dF}',
     '"C_resp_plus_C_PL5D_plus_DeltaC_e": cpl[X_PL]}'),
    ("block: the reported matrix without dF", '    rep_f = mats["C_total_plus_C_resp_plus_C_PL5D"] + dF\n',
     '    rep_f = mats["C_total_plus_C_resp_plus_C_PL5D"]\n'),
    ("block: the matrix without C_PL5D, without dF", '    wo_f = mats["C_total_plus_C_resp"] + dF\n',
     '    wo_f = mats["C_total_plus_C_resp"]\n'),
    ("block: the keys of the two sides swapped",
     'SIDE_KEY = {"with": "C_resp_plus_C_PL5D_plus_DeltaC_e", "nopl": "C_resp_plus_DeltaC_e"}',
     'SIDE_KEY = {"with": "C_resp_plus_DeltaC_e", "nopl": "C_resp_plus_C_PL5D_plus_DeltaC_e"}'),
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
    ("K2: DeltaC_e not C_e_infl - C_e", 'same_bits(dF, blk["C_e_infl"] - blk["C_e"]))', "True)"),
    ("K3: Stage G's sigma loose", 'F.worst(np.array(p["sigma_total_over_f"]), sig[idx]) <= TOL',
     'F.worst(np.array(p["sigma_total_over_f"]), sig[idx]) <= 1.0'),
    ("K3: Stage G's covariance name unchecked", 'and p["reported_covariance"] == REPORTED_NAME)', ")"),
    ("product: the reported matrix is the one without C_PL5D", "WITHOUT_F: blk[WITHOUT_F], REPORTED_F: blk[REPORTED_F]}",
     "WITHOUT_F: blk[WITHOUT_F], REPORTED_F: blk[WITHOUT_F]}"),
    ("deposit variant: the key without C_PL5D", "    return DC.Variant(key=REPORTED_F,", "    return DC.Variant(key=WITHOUT_F,"),
    # T: the table
    ("T: Stage G's V_F matrix not checked", 'and pn[kind]["matrix"] == vf_matrix(po[kind]["matrix"], True),', ","),
    ("T: dF placed after V_g", 'old_name.replace(" + V_g", " + DeltaC_e + V_g", 1)', 'old_name + " + DeltaC_e"'),
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
    ("C: the role unchecked", '(fl("--extra-block-role") == "adopted" if role else "--extra-block-role" not in a)', "True"),
    ("C: duplicate references unchecked", "and all(ref.get(f, h) == h for f, h in upstream.items()))", ")"),
    ("C: argv naming the digest twice passes", "return a[a.index(f) + 1] if a.count(f) == 1 else None", "return a[a.index(f) + 1] if f in a else None"),
    ("C: F0 not checked", '        check_c(c, f"{arm} f0", out, vf["sha"], "DeltaC_e", {}, role=False, tool="fd_f0_regrade")\n', "        pass\n"),
    ("C: a chdefs V_F step not checked", '            check_c(c, f"E {arm} {k}", out[k], vf["sha"], SIDE_KEY[side],', '            (lambda *x, **y: None)(c, f"E {arm} {k}", out[k], vf["sha"], SIDE_KEY[side],'),
    ("S: Stage G's predictions and cells unchecked", "have == declared_cells() and all(len(q[\"sigma_total_over_f\"]) == len(q[\"cells\"]) for q in gr[\"predictions\"]),", "True,"),
    ("K3: Stage G's predictions and cells unchecked", '[(p["name"], p["cells"]) for p in gr["predictions"]] == declared_cells()', "True"),
    ("K6: the files on disk not read back", '        report("K6", f"{n}: the file on disk is the bytes written", (out / n).read_bytes() == text.encode())', '        pass'),
    ("K6: the cells CSV not read back", '[r["cell"] for r in rows] == CELLS and same_bits(np.array([float(r["f"]) for r in rows]), p["f"])', "True"),
    ("T: the V_F grade matrix not checked", 'tn["grade_matrix"] == vf_matrix(to["grade_matrix"], False)', "True"),
    ("T: F0's revised sigma not required", "sn is not None and o.get(\"cells\") == n.get(\"cells\") == CELLS", "o.get(\"cells\") == n.get(\"cells\") == CELLS"),
    ("T: F0's cells unchecked", 'o.get("cells") == n.get("cells") == CELLS and sorted(so) == sorted(sn)', "sorted(so) == sorted(sn)"),
    ("T: Stage G's ndf unchecked", 'po[kind]["ndf"] == pn[kind]["ndf"] == want_ndf, f"{po[kind][\'ndf\']} / {pn[kind][\'ndf\']}")', 'True, "")'),
    ("K6: box edges compared as numbers", 'same_bits(np.array([float(r[f"{ax}_{e}"]) for e in ("lo", "hi")]), np.array([float(v) for v in c["box"][ax]]))', '[float(r[f"{ax}_{e}"]) for e in ("lo", "hi")] == [float(v) for v in c["box"][ax]]'),
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
    ("bits: -0.0 read as 0.0", "return a.dtype == b.dtype and a.shape == b.shape and a.tobytes() == b.tobytes()",
     "return bool(np.array_equal(a, b))"),
    ("C: a null digest field passes", 'digests = [d.get(k) for d, k in ((xbr, "sha256"), (ins, "extra_block")) if k in d]',
     'digests = [v for v in (xbr.get("sha256"), ins.get("extra_block")) if v is not None]'),
    ("C: the recorded role unchecked", '          and (xbr.get("role", "adopted") == "adopted" if role else "role" not in xbr)\n', ""),
    ("C: required references unchecked", "          and all(f in ref for f in required)", "          and True"),
    ("T: named records not checked before pairing", "        identities(o, n, k)\n", ""),
    ("T: block names not mapped back in identities", 'idb = [(rename_vf(x["name"]) if isinstance(x.get("name"), str) else x.get("name"), x.get("cells"))',
     'idb = [(x.get("name"), x.get("cells"))'),
    ("T: a named list missing on the V_F side passes", "                elif key not in renamed and named(a[key]):",
     "                elif False:"),
    ("T: a key renamed with the block counted as missing", "            renamed = {rename_vf(kb) for kb in b}",
     "            renamed = set(b)"),
    ("chdefs: the observed manifest digest pinned", '    base = {"s5p_sums": CHDEFS_SUMS}', '    base = {"s5p_sums": A.sha256(p.s5p_sums)}'),
    ("chain: the chdefs specification unchecked", 'specs == json.loads((D / CHDEFS_SPEC).read_bytes()), CHDEFS_SPEC)', "True, CHDEFS_SPEC)"),
    ("K6: a refusal installs the outputs", "    check_written(stage, files, p, dp)", "    os.rename(stage, out); stage = out\n    check_written(stage, files, p, dp)"),
    ("K6: the cells' box edges unchecked", "for r, c in zip(rows, dp[\"cells\"]) for ax in c[\"box\"]))", "for r, c in zip(rows, dp[\"cells\"]) for ax in c[\"box\"]) or True)"),
    ("R deposit: the 5B receipt's bytes unchecked", 'A.sha256(D / OLD_DEP / n) == sums.get(n), n)', "True, n)"),
    ("OLD: the deposit check not run", '    cS.run("deposit_check", "old-with", "fd_deposit_candidate",', '    (lambda *x, **k: None)("deposit_check", "old-with", "fd_deposit_candidate",'),
    ("C: structured fields unchecked", '          and (all(f in xbr for f in STRUCTURED[tool]) if tool in STRUCTURED else "extra_block" in ins)\n', "          and True\n"),
    ("renderer: the environment unchecked", 'bool(want) and all(have.get(k) == v for k, v in want.items()), {"have": have, "want": want})', 'True, {"have": have, "want": want})'),
    ("T: keys not renamed in identities", '    return key.replace(" + DeltaC_e", "")', "    return key"),
    ("BOOT: the variants' modules swapped", '(A if variant == "with-cpl" else V)', '(V if variant == "with-cpl" else A)'),
]
# Not run, each with its reason: T's truth-order and Stage G cell checks in curated() are redundant with identities()
# (named records, in order, on the same cells), which runs first; excluding /code_sha256 again from the OLD product's R
# is equivalent while the deploy's fd_cpl_addition.py is the committed product's (its recorded sha); C's "at least one
# block digest" is implied by its structured-fields requirement (a dict sha256 or inputs_sha256.extra_block).


def sha(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def main() -> int:
    orig = TARGET.read_text()
    h0 = sha(TARGET)
    rows, bad = [], 0
    if not DRY:
        clean = {k: v for k, v in os.environ.items() if k != "VF_MUTANT_RUN"}   # the ordinary baseline runs every test
        b = subprocess.run([sys.executable, "-B", "-m", "unittest", "-q", "test_fd_vf_addition"], cwd=TESTS,
                           capture_output=True, text=True, timeout=1200, env=clean)
        print(f"baseline: the unmutated suite rc {b.returncode}", flush=True)
        if b.returncode != 0:
            print("STOP: the baseline fails; no mutant is counted", flush=True)
            print(b.stderr[-3000:], flush=True)
            return 9
        bm = subprocess.run([sys.executable, "-B", "-m", "unittest", "-q", "test_fd_vf_addition"], cwd=TESTS,
                            capture_output=True, text=True, timeout=1200, env={**os.environ, "VF_MUTANT_RUN": "1"})
        nm = re.search(r"^Ran (\d+) tests? in ", bm.stderr, re.M)
        if bm.returncode != 0 or nm is None:
            print("STOP: the mutant-mode baseline fails; no mutant is counted", flush=True)
            return 9
        n_tests = int(nm.group(1))
        print(f"baseline in mutant mode: rc 0, {n_tests} tests", flush=True)
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
                               capture_output=True, text=True, timeout=1200, env={**os.environ, "VF_MUTANT_RUN": "1"})
            nr = re.search(r"^Ran (\d+) tests? in ", r.stderr, re.M)
            # a fixture refused by the mutant runs fewer tests (a real kill); a module that fails to import is HARNESS
            ran = (nr is not None and "Failed to import test module" not in r.stderr and "_FailedTest" not in r.stderr)
            if r.returncode == 0:
                status = "SURVIVED"
            elif ran and re.search(r"^FAILED \((failures|errors)=", r.stderr, re.M):
                status = "KILLED"
            else:
                status = "HARNESS"
        except subprocess.TimeoutExpired:
            status = "TIMEOUT"
        finally:
            TARGET.write_text(orig)
        if sha(TARGET) != h0:
            print("STOP: the target was not restored", flush=True)
            return 9
        rows.append((status, name, ""))
        if status in ("SURVIVED", "TIMEOUT", "HARNESS"):
            bad += 1
        print(f"{status:9s} {name}", flush=True)
    for s, n, why in rows:
        if s in ("MISSING", "INVALID", "APPLIES"):
            print(f"{s:9s} {n} {why}", flush=True)
    counts = {s: sum(1 for r in rows if r[0] == s) for s in ("KILLED", "SURVIVED", "TIMEOUT", "HARNESS", "INVALID", "MISSING", "APPLIES")}
    print(f"mutants {len(MUTANTS)}: " + ", ".join(f"{k} {v}" for k, v in counts.items() if v), flush=True)
    print(f"target sha256 {sha(TARGET)} (restored: {sha(TARGET) == h0})", flush=True)
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())

#!/usr/bin/env python3
"""Mutation run for V_F's adoption (FD-VF-ADDITION-DECLARATION.md section 2): one textual change at a time to
nd-unfolding/fd_vf_addition.py, applied in place in the repository copy given (never a working checkout). Each mutated
source is compiled first: a mutant that does not compile is INVALID, never killed. A valid mutant is KILLED if
test_fd_vf_addition fails, else SURVIVED. One whose text is not found exactly once is MISSING. The file is restored
and its sha256 checked after every mutant and at the end.

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
    ("T: keys not renamed", '        key = key.replace(BLOCKS[k], BLOCKS[k][:-len(" + dF")])\n', "        pass\n"),
    ("T: truths' order unchecked", '[t["name"] for t in o["truths"]] == [t["name"] for t in n["truths"]])', "True)"),
    ("T: cleared truths dropped", '"cleared": sorted(set(listed(o)) - set(listed(n)))}', '"cleared": []}'),
    ("table: runs without the chain's pins", '    if pins is None:\n        raise Stop("T", "table runs',
     '    if False:\n        raise Stop("T", "table runs'),
    # the chain: arms, argv, order
    ("arms: OLD with takes the nopl block", 'if kind == "old" and side == "with":', 'if kind == "old" and side == "nopl":'),
    ("arms: OLD nopl figures draw a name", 'return A.NAME if side == "with" else None', "return A.NAME"),
    ("F0: the V_F arm takes no block", 'xb0 = [] if arm == "old-f0" else', "xb0 = [] if True else"),
    ("F1: the V_F arm's F0b digest wrong", '{"f0b": out["f0b"], "f0b_sha256": A.sha256(out["f0b"])})',
     '{"f0b": out["f0b"], "f0b_sha256": "0" * 64})'),
    ("E: the figures lose the prediction set", '"--prediction-set", "gencmp-chdefs"]\n    c.run("figures"',
     ']\n    c.run("figures"'),
    ("R: numbers not compared", "    bad = A.compare_numbers(old, nw, R_EXCLUDE) + (", "    bad = [] + ("),
    ("R: strings never compared", "(A.compare_strings(old, nw, R_EXCLUDE) if strings else [])", "[]"),
    ("R: the committed pin unchecked", 'c.check(f"R {label}: the committed readout is the pinned bytes", A.sha256(D / rel) == pin, rel)',
     'c.check(f"R {label}: the committed readout is the pinned bytes", True, rel)'),
    ("S: the nopl side checked against the reported matrix", 'M = blk[REPORTED_F] if side == "with" else blk[WITHOUT_F]',
     "M = blk[REPORTED_F]"),
    ("C: the block's digest unchecked", "bool(named) and all(v == vf_sha for v in named)", "bool(named)"),
    ("chain: F0's OLD control dropped", 'check_r(cS, "F0", D, *OLD_F0, run_f0(cS, "old-f0", vf), strings=False)',
     'run_f0(cS, "old-f0", vf)'),
    ("chain: Stage G set S OLD controls dropped",
     '                check_r(cS, f"S {arm} {k}", D, *OLD_S[side][k], out[k], strings=False)\n', "                pass\n"),
    ("chain: the chdefs OLD controls dropped",
     '                check_r(cE, f"E {arm} {k}", D, *OLD_E[side][k], res["out"][k], strings=(side == "with"))\n',
     "                pass\n"),
    ("chain: the chdefs OLD with arm's strings not compared", 'strings=(side == "with"))', "strings=False)"),
    ("chain: the committed block's pin unchecked", "A.sha256(vnpz) == VF_BLOCK_NPZ, str(vnpz))", "True, str(vnpz))"),
    ("chain: an existing run directory overwritten",
     'report("C", f"{d} does not exist (no overwrite)", not (BA / d).exists())',
     'report("C", f"{d} does not exist (no overwrite)", True)'),
    ("BOOT: the variants' modules swapped", '(A if variant == "with-cpl" else V)', '(V if variant == "with-cpl" else A)'),
]


def sha(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def main() -> int:
    orig = TARGET.read_text()
    h0 = sha(TARGET)
    rows, bad = [], 0
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
            status = "KILLED (timeout)"
        finally:
            TARGET.write_text(orig)
        if sha(TARGET) != h0:
            print("STOP: the target was not restored", flush=True)
            return 9
        rows.append((status, name, ""))
        if status == "SURVIVED":
            bad += 1
        print(f"{status:9s} {name}", flush=True)
    for s, n, why in rows:
        if s in ("MISSING", "INVALID", "APPLIES"):
            print(f"{s:9s} {n} {why}", flush=True)
    counts = {s: sum(1 for r in rows if r[0].startswith(s)) for s in ("KILLED", "SURVIVED", "INVALID", "MISSING", "APPLIES")}
    print(f"mutants {len(MUTANTS)}: " + ", ".join(f"{k} {v}" for k, v in counts.items() if v), flush=True)
    print(f"target sha256 {sha(TARGET)} (restored: {sha(TARGET) == h0})", flush=True)
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())

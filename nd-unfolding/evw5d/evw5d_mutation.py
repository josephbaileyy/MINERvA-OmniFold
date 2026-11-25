#!/usr/bin/env python3
"""EVW5D's mutants (EVW5D-DECLARATION.md section 5): each replaces one exact span of ``evw5d.py`` (it must occur exactly
once), and the full suite ``test_evw5d.py`` must then fail: pytest exit 1 with at least one named failing test, and the
first error not an import or syntax error. A control with no mutation must pass (exit 0). Each case runs on its own
copy of ``nd-unfolding/evw5d`` and ``nd-unfolding/ess_e`` (the suite follows ``EVW5D_DIR``), so the checkout is never
written, and each suite builds its own deploy in its own temporary directory.

    EVW5D_REPO=<clone> python3 evw5d_mutation.py PYTHON OUT_JSON [WORKERS]
"""
from __future__ import annotations

import concurrent.futures as cf
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
SRC = HERE / "evw5d.py"

MUTANTS = [
    ("SAME_BITS_DTYPE", "return a.dtype == b.dtype and a.shape == b.shape and", "return a.shape == b.shape and"),
    ("MAX_REL_ZERO_REF", 'if np.any(x[~nz] != 0):\n        return float("inf")', 'if False:\n        return float("inf")'),
    ("MAX_REL_SHAPE", 'if x.shape != ref.shape:\n        return float("inf")', 'if False:\n        return float("inf")'),
    ("READ_NPZ_HASH", "return hashlib.sha256(raw).hexdigest(), arrays", "return hashlib.sha256(raw[:-1]).hexdigest(), arrays"),
    ("CONTRIB_FACTOR", "wb[used] = 1.0e4 * w_unfolded[used] / den[fic[used]]", "wb[used] = 1.0e4 * w_unfolded[used] / den[fic[used]] * (1 + 1e-13)"),
    ("CONTRIB_GOOD", "used = inside & goodf[fic]", "used = inside"),
    ("CONTRIB_ZERO_DEN_COUNT", "(inside & ~goodf[fic] & (fm[fic] >= 0))", "(inside & ~goodf[fic])"),
    ("TABLE_MASK_DTYPE", "if np.asarray(m).dtype != np.bool_:", "if False:"),
    ("TABLE_UINT32", "int(entry[-1]) >= 2 ** 32", "int(entry[-1]) >= 2 ** 40"),
    ("TABLE_UNFOLDED_RECO", 'cols["w_unfolded"] = wpush * d["w_truth"][m]', 'cols["w_unfolded"] = wpush * d["w_reco"][m]'),
    ("TABLE_WPRIOR_RECO", 'cols["w_prior"] = np.ascontiguousarray(np.asarray(d["w_truth"])[m])', 'cols["w_prior"] = np.ascontiguousarray(np.asarray(d["w_reco"])[m])'),
    ("TABLE_RECO_FLAG", 'cols["reco_partner"] = np.asarray(d["pass_reco"], bool)[m]', 'cols["reco_partner"] = np.ones(int(np.count_nonzero(m)), bool)'),
    ("TABLE_TRUTH_ORDER", "cols[name] = np.ascontiguousarray(mc[m, k])", "cols[name] = np.ascontiguousarray(mc[m, (k + 1) % 5])"),
    ("MAPS_COMPLETENESS", "comp[nz] = ofin[nz] / dn[nz]", "comp[nz] = ofin[nz] / dn[nz] * (1 + 1e-15)"),
    ("CONST_FLUX", 'flux=np.asarray(d["flux"])', 'flux=np.asarray(d["flux"]) * (1 + 1e-15)'),
    ("CONST_MAP_DTYPE", 'fine_to_cell=np.asarray(fm, "<i4")', 'fine_to_cell=np.asarray(fm, "<i8")'),
    ("KEY_FIELD", '"w_truth", "w_reco", "denom_nd", "flux")\n    equal', '"w_truth", "denom_nd", "flux")\n    equal'),
    ("KEY_ALIGNED", "aligned = m.dtype == np.bool_ and np.asarray(wpush).shape == (int(m.sum()),)", "aligned = True"),
    ("KEY_PASS", '"pass": bool(all(equal.values()) and aligned)}', '"pass": bool(aligned)}'),
    ("KEY_EDGES", 'equal["edges"] = len(d["edges"]) == ne and all(', 'equal["edges"] = True or all('),
    ("KEY_SCALARS", 'equal["data_pot"] = same_bits(', 'equal["data_pot"] = True or same_bits('),
    ("ENTRIES_INCREASING", '"pass": bool(e.dtype == np.uint32 and increasing and unique)}', '"pass": bool(e.dtype == np.uint32 and unique)}'),
    ("ENTRIES_DTYPE", '"pass": bool(e.dtype == np.uint32 and increasing and unique)}', '"pass": bool(increasing and unique)}'),
    ("FILE_COLUMNS", 'out = {"columns_exact": sorted(t) == sorted(COLUMNS + ("meta",))}', 'out = {"columns_exact": True}'),
    ("FILE_META", 'out["meta_equal"] = (', 'out["meta_equal"] = True or ('),
    ("FILE_JSON", 'out["constants_json_equal"] = json.loads(cj_raw) == cjson', 'out["constants_json_equal"] = True'),
    ("FILE_CONST_EXACT", 'out["constants_exact"] = sorted(k for k in c if k != "meta") == sorted(expected_c)', 'out["constants_exact"] = True'),
    ("FILE_ENTRY", 'out["entry"] = same_bits(t["entry"], entry.astype(np.uint32))', 'out["entry"] = True'),
    ("FILE_TRUTH", "out[name] = same_bits(t[name], np.ascontiguousarray(mc[e, k]))", "out[name] = True"),
    ("FILE_WPRIOR", 'out["w_prior"] = same_bits(', 'out["w_prior"] = True or same_bits('),
    ("FILE_WPUSH", 'out["wpush"] = same_bits(', 'out["wpush"] = True or same_bits('),
    ("FILE_UNFOLDED", 'out["w_unfolded"] = same_bits(', 'out["w_unfolded"] = True or same_bits('),
    ("FILE_RECO", 'out["reco_partner"] = same_bits(', 'out["reco_partner"] = True or same_bits('),
    ("FILE_FINE", 'out["fine_index"] = same_bits(', 'out["fine_index"] = True or same_bits('),
    ("FILE_CONSTANTS", 'out["constants"] = {k: same_bits(c[k], v)', 'out["constants"] = {k: True'),
    ("SELF_BITWISE", '"xsec_bit_for_bit": same_bits(xs, ref_xsec_flat),', '"xsec_bit_for_bit": True,'),
    ("SELF_OFIN", '"ofin_bit_for_bit": same_bits(mp["ofin"], c["ofin"]),', '"ofin_bit_for_bit": True,'),
    ("SELF_COMP", '"completeness_bit_for_bit": same_bits(mp["comp"], c["completeness"])}', '"completeness_bit_for_bit": True}'),
    ("SELF_INDEP_TOL", 'and out["independent_formula_max_rel"] <= INDEP_RTOL', 'and out["independent_formula_max_rel"] <= 1e3 * INDEP_RTOL'),
    ("SELF_CM2", 'x2[ok] = mp["unf"][ok] / den[ok] * float(c["cm2_per_m2"])', 'x2[ok] = mp["unf"][ok] / den[ok] * 1.0e4'),
    ("SELF_F_ROWS", 'out["f_from_rows_max_rel"] <= F_RTOL)\n    return out', 'True)\n    return out'),
    ("FLOW_RANGE", "in_range = bool(np.all((fi >= -1) & (fi < nfine)))", "in_range = bool(np.all(fi < nfine))"),
    ("FLOW_N", '"n_rows_equal_pass_truth": int(fi.size) == int(n_pass_truth),', '"n_rows_equal_pass_truth": True,'),
    ("FLOW_UNF_TOL", 'out["unfolded_max_rel"] <= FLOW_RTOL', 'out["unfolded_max_rel"] <= 1e6 * FLOW_RTOL'),
    ("FLOW_PRIOR", 'and out["prior_max_rel"] <= FLOW_RTOL)', "and True)"),
    ("COMPLETE_ATOL", "int((dev > COMPLETE_ATOL).sum())", "int((dev > 10 * COMPLETE_ATOL).sum())"),
    ("COMPLETE_NO_SIGNAL", 'or out["n_signal_without_denominator"] > 0', "or False"),
    ("COMPLETE_EMPTY", "\n                          or not pos.any())", ")"),
    ("PARSE_HEX", 'any(ch not in "0123456789abcdef" for ch in h)', "False"),
    ("PARSE_DUP", " or p in out:", ":"),
    ("ACC_SET", '"product_set_exact": files == sorted(PRODUCTS + (SUMS,)),', '"product_set_exact": True,'),
    ("ACC_MAP", '"digest_map_complete": sorted(digests) == sorted(PRODUCTS)}', '"digest_map_complete": True}'),
    ("ACC_LINKS", 'acc["no_links"] = not any((out / f).is_symlink() for f in files)', 'acc["no_links"] = True'),
    ("ACC_REHASH", "ess.sha256_file(out / p) == h for", "True for"),
    ("ACCEPTED_VERDICT", 'done.get("verdict") != "PASS"', "False"),
    ("ACCEPTED_SUMS_DIGEST", 'if hashlib.sha256(sums.encode()).hexdigest() != done.get("sha256sums_sha256"):', "if False:"),
    ("ACCEPTED_SCHEMA", 'done.get("schema") != SCHEMA or ', ""),
    ("RUN_BIND_META", 'and bind["meta_equal_except_per_run"])', ")"),
    ("RUN_BIND_XS", 'bind["pass"] = bool(bind["xsec_flat_bytes_equal"] and ', 'bind["pass"] = bool('),
    ("RUN_F_GATE", 'cf["pass"] = bool(cf["f_from_result_max_rel"] <= F_RTOL and cf["f_from_rows_max_rel"] <= F_RTOL)', 'cf["pass"] = True'),
    ("RUN_GATED_SELF", '"C-FILE", "C-SELF", "C-FLOW"', '"C-FILE", "C-FLOW"'),
    ("RUN_FINDING", 'if comp["finding"]:', "if False:"),
    ("MAIN_OUT_ROOT_FIRST", '        return 2\n    a.out.mkdir(parents=True)', '        pass\n    a.out.mkdir(parents=True)'),
    ("MAIN_OUT_EXISTS", "if a.out.exists():", "if False:"),
    ("MAIN_FIXTURE_SLURM", 'if os.environ.get("SLURM_JOB_ID"):', "if False:"),
    ("ESS_PIN", "if got != ESS_SHA:", "if False:"),
    ("CAPTURE_COUNT", "if len(loops) != 1 or len(unfolds) != 1:", "if len(loops) < 1 or len(unfolds) < 1:"),
    ("CAPTURE_RC", 'if rc != 0:\n        raise Failed(f"s5p_numerics.main returned {rc}")', 'if False:\n        raise Failed(f"s5p_numerics.main returned {rc}")'),
    ("CAPTURE_RESTORE", "    finally:\n        onc.omnifold_loop, s5c_unfold.unfold = real_loop, real_unfold", "    finally:\n        pass"),
]


# Equivalent mutants: kept out of the kill requirement, each with the reason it cannot be killed; run and reported.
EQUIVALENT = [
    ("SELF_F_FILE", 'and out["f_from_file_max_rel"] <= F_RTOL and', 'and True and',
     "f from the file is f of the re-made result, which xsec_bit_for_bit already makes equal to the reference's; with "
     "the row-level f (f_from_rows) also gated against the same data product, no fault moves the file-level f alone. "
     "The check stays as a second statement of gate 2"),
]


def apply(src: str, old: str, new: str) -> str:
    n = src.count(old)
    if n != 1:
        raise SystemExit(f"a mutant span occurs {n} times: {old[:80]!r}")
    return src.replace(old, new)


def run_one(name: str, old: str | None, new: str | None, python: str, timeout: int) -> dict:
    t0 = time.time()
    with tempfile.TemporaryDirectory(prefix=f"evw5d-mut-{name}-") as tmp:
        base = Path(tmp) / "nd-unfolding"
        for sub in ("evw5d", "ess_e"):
            shutil.copytree(HERE.parent / sub, base / sub, ignore=shutil.ignore_patterns("__pycache__"))
        src = SRC.read_text()
        mutated = src if old is None else apply(src, old, new)
        (base / "evw5d" / "evw5d.py").write_text(mutated)
        env = dict(os.environ, EVW5D_DIR=str(base / "evw5d"), PYTHONDONTWRITEBYTECODE="1")
        env.setdefault("EVW5D_REPO", str(HERE.parents[1]))
        try:
            r = subprocess.run([python, "-B", "-m", "pytest", "-q", "-p", "no:cacheprovider", "-rf",
                                str(base / "evw5d" / "test_evw5d.py")], capture_output=True, text=True, env=env,
                               timeout=timeout)
            rc, outtxt = r.returncode, r.stdout + r.stderr
        except subprocess.TimeoutExpired:
            rc, outtxt = -9, "TIMEOUT"
    failed = sorted(set(re.findall(r"^FAILED \S+::(\S+)", outtxt, flags=re.M)))
    first_err = next((ln for ln in outtxt.splitlines() if re.match(r"^E\s", ln)), "")
    broken = bool(re.search(r"(ImportError|SyntaxError|ModuleNotFoundError|IndentationError)", first_err)) or \
        "error during collection" in outtxt or "errors during collection" in outtxt
    if old is None:
        verdict = "CONTROL-PASS" if rc == 0 else "CONTROL-FAIL"
    else:
        verdict = "KILLED" if rc == 1 and failed and not broken else ("BROKEN" if broken else "SURVIVED")
    return {"name": name, "verdict": verdict, "rc": rc, "failed": failed, "first_error": first_err[:300],
            "mutant_sha256": hashlib.sha256(mutated.encode()).hexdigest(), "seconds": round(time.time() - t0, 1),
            "tail": outtxt[-600:] if verdict not in ("KILLED", "CONTROL-PASS") else ""}


def main(argv: list[str]) -> int:
    python, out = argv[1], Path(argv[2])
    workers = int(argv[3]) if len(argv) > 3 else 4
    src = SRC.read_text()
    for name, old, new in MUTANTS:          # every span exactly once, before anything runs
        apply(src, old, new)
    names = [m[0] for m in MUTANTS]
    if len(set(names)) != len(names):
        raise SystemExit("duplicate mutant names")
    only = set(filter(None, os.environ.get("EVW5D_ONLY", "").split(",")))
    eq = [(n, o, w) for n, o, w, _ in EQUIVALENT]
    for name, old, new in eq:
        apply(src, old, new)
    cases = [("CONTROL", None, None)] + [m for m in MUTANTS + eq if not only or m[0] in only]
    with cf.ThreadPoolExecutor(max_workers=workers) as ex:
        results = list(ex.map(lambda c: run_one(*c, python, 900), cases))
    ctl = results[0]
    eq_names = {e[0] for e in EQUIVALENT}
    killed = [r for r in results[1:] if r["verdict"] == "KILLED" and r["name"] not in eq_names]
    want = [r for r in results[1:] if r["name"] not in eq_names]
    rec = {"schema": "evw5d-mutation/1", "src_sha256": hashlib.sha256(src.encode()).hexdigest(),
           "tests_sha256": hashlib.sha256((HERE / "test_evw5d.py").read_bytes()).hexdigest(),
           "python": python, "control": ctl["verdict"], "subset": sorted(only), "n_mutants": len(want),
           "n_killed": len(killed), "not_killed": [r["name"] for r in want if r["verdict"] != "KILLED"],
           "equivalent": [{"name": n, "reason": why, "verdict": next((r["verdict"] for r in results if r["name"] == n), None)}
                          for n, _, _, why in EQUIVALENT], "results": results}
    out.write_text(json.dumps(rec, indent=1) + "\n")
    print(json.dumps({k: rec[k] for k in ("control", "n_mutants", "n_killed", "not_killed")}))
    return 0 if ctl["verdict"] == "CONTROL-PASS" and len(killed) == len(want) and not only else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv))

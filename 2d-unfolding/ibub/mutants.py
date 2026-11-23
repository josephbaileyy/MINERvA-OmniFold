#!/usr/bin/env python3
"""IBUB's hand mutants. Each one is a single-site change to ``ibub_unit.py`` or ``ibub_readout.py``, applied in place
and run against the tests that should kill it. The file is then restored and its sha256 re-checked; a restore that
does not reproduce the original bytes stops the run.

A mutant is KILLED when its tests exit non-zero, and it SURVIVES when they pass. Every mutant must be killed.

    python -B mutants.py PYTHON [--only N]

PYTHON is an interpreter with PyROOT, numpy, scipy, LightGBM and scikit-learn. The results are printed as one TSV line
per mutant (index, verdict, file, tests, what it breaks), then a total line.
"""
from __future__ import annotations

import hashlib
import os
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
U, R = "ibub_unit.py", "ibub_readout.py"
TU, TR = "test_ibub_unit", "test_ibub_readout"

# (file, old, new, tests, what the mutant breaks)
MUTANTS = [
    (U, 'bad = sorted({a.split("=", 1)[0] for a in argv} & set(cfg["g2r_forbidden_options"]))', "bad = []",
     [f"{TU}.Pure", f"{TU}.Driver"], "C-G2R refuses nothing"),
    (U, '{a.split("=", 1)[0] for a in argv}', "set(argv)", [f"{TU}.Pure"], "C-G2R misses --miss-map=v"),
    (U, '        argv += ["--data-file", str(data_copy)]', "        pass", [f"{TU}.Driver"],
     "a data unit runs without its data file"),
    (U, "    if threads != cfg[\"e_r\"][\"thread_env\"]:", "    if False:", [f"{TU}.Driver"],
     "the thread gate is gone"),
    (U, "    if cpus != int(cfg[\"e_r\"][\"cpus\"]):", "    if False:", [f"{TU}.Driver"], "the CPU gate is gone"),
    (U, "    if got != want:\n        dest.unlink()\n        raise GateFailure(f\"C-DATA:",
     "    if False:\n        dest.unlink()\n        raise GateFailure(f\"C-DATA:", [f"{TU}.Driver"],
     "a data file off its pin is used"),
    (U, "        if data_copy is not None and Path(data_copy).exists():\n            Path(data_copy).unlink()",
     "        pass", [f"{TU}.Driver"], "the data copy is kept"),
    (U, 'data["pass"] = bool(data["argv_equal"] and prov.get("dataFileSha256") == data_sha)',
     'data["pass"] = bool(data["argv_equal"])', [f"{TU}.Driver"], "C-DATA ignores the recorded digest"),
    (U, 'xs = max(max_rel(np.asarray(a["xsec"])[i][rep], np.asarray(b["xsec"])[i][rep])',
     'xs = max(max_rel(np.asarray(a["xsec"])[i][~rep], np.asarray(b["xsec"])[i][~rep])', [f"{TU}.Pure"],
     "C-REP compares the unreported cells"),
    (U, 'out["pass"] = bool(max(out["xsec_max_rel"], out["T_max_rel"], out["y_max_rel"]) <= rtol)',
     'out["pass"] = bool(max(out["xsec_max_rel"], out["y_max_rel"]) <= rtol)', [f"{TU}.Pure"], "C-REP ignores T"),
    (U, "        fast = isinstance(secs, (int, float)) and secs <= limit", "        fast = True", [f"{TU}.Pure"],
     "the re-price trigger is gone"),
    (U, '        ok = ok and rec["central_df_vs_central"]["pass"]', "        pass", [f"{TU}.Pure"],
     "the barrier ignores central_df against central"),
    (U, "            os.chmod(dest, stat.S_IRUSR | stat.S_IRGRP | stat.S_IROTH)", "            pass", [f"{TU}.Pure"],
     "staged copies stay writable"),
    (U, "        ok = ok and not missing", "        pass", [f"{TU}.Pure"], "the preflight ignores a missing toy file"),
    (U, '    if hashlib.sha256(raw).hexdigest() != t["pseudo_b_sha256"]:', "    if False:", [f"{TU}.Pure"],
     "pseudo_b.json is read off its pin"),
    (U, '        controls["C-ROO"] = {"max_rel": roo, "pass": bool(roo <= c2["c_roo_rtol"])}',
     '        controls["C-ROO"] = {"max_rel": roo, "pass": True}', [f"{TU}.Driver"], "C-ROO always passes"),
    (R, "            cols.append(np.where(m, area, 0.0)[:, None])", "            cols.append(m.astype(float)[:, None])",
     [f"{TR}.Pure"], "bands are bare sums, not area-weighted"),
    (R, "    return NormalDist().inv_cdf(1 - alpha / 2 / tests)", "    return NormalDist().inv_cdf(1 - alpha / 2 / 205)",
     [f"{TR}.Pure"], "z* uses 205 tests, not the family"),
    (R, '    d = per_test(Y["IBU"] - Y["OF"], counts, zs, xt, sigma)',
     '    d = per_test(Y["IBU"] - Y["OF"][::-1], counts, zs, xt, sigma)', [f"{TR}.Pure"],
     "the difference is not paired toy by toy"),
    (R, '    flagged = [i for i in range(tests) if abs(d["z"][i]) > zs]',
     '    flagged = [i for i in range(tests) if abs(m["IBU"]["z"][i]) > zs]', [f"{TR}.Pure"],
     "the rule reads IBU's own bias, not the difference"),
    (R, '    for k in ("bias", "pull_mean", "pull_sd", "p_hat"):', '    for k in ("bias", "pull_mean"):', [f"{TR}.Pure"],
     "C-OF checks only the means (blind to a mispairing)"),
    (R, '        if prov.get("dataFileSha256") != shas[s]:', "        if False:", [f"{TR}.EndToEnd"],
     "the product's recorded data digest is not checked"),
    (R, "        k10.append(iu.max_rel(row10, h))", "        k10.append(0.0)", [f"{TR}.EndToEnd"], "C-K10 is gone"),
    (R, '                              "pass": ibu["nonfinite"] == {"K10": 0, "K5": 0}}',
     '                              "pass": ibu["nonfinite"]["K10"] == 0}', [f"{TR}.EndToEnd"], "C-CELLS skips K = 5"),
    (R, "            E_of = x_of - x_true", "            E_of = E_post", [f"{TR}.EndToEnd"],
     "OmniFold's errors are taken after the surrogates"),
    (R, '            if ibu["missing"]:\n                rec["verdict"] = "INCOMPLETE"',
     '            if False:\n                rec["verdict"] = "INCOMPLETE"', [f"{TR}.EndToEnd"],
     "a missing unit does not stop the reading"),
    (R, "            if nseeds != [n[\"seed\"] for n in natures]:", "            if False:", [f"{TR}.EndToEnd"],
     "the truth rows are not checked against the natures"),
    (R, "    if any(real_out == g or real_out.startswith(g + os.sep) for g in guarded):", "    if False:",
     [f"{TR}.EndToEnd"], "--out under a guarded tree is allowed"),
    (R, '            if not rec["C-OF"]["pass"]:\n                rec["controls_failed"].append("C-OF")',
     '            if False:\n                rec["controls_failed"].append("C-OF")', [f"{TR}.EndToEnd"],
     "a failed C-OF does not invalidate the tune"),
    (U, "        if dest.exists():            # a partial or unverified copy never stays behind to block a rerun\n            dest.unlink()",
     "        if False:\n            dest.unlink()", [f"{TU}.Refusals"], "a partial data copy stays behind"),
    (U, '        if set(controls) != CONTROLS[unit["kind"]]:', "        if False:", [f"{TU}.Driver"],
     "a unit with an undeclared control set writes a marker"),
    (R, "            if str(meta.get(k)) != str(bound[k]):", "            if False:", [f"{TR}.EndToEnd"],
     "a unit from another job, runner or config is read"),
    (R, '        if set(ctl) != iu.CONTROLS["toy"]:', "        if False:", [f"{TR}.EndToEnd"],
     "a unit lacking a declared control is read"),
    (R, "        if list(z[\"ks\"]) != ks_want:\n            missing.append(s)",
     "        if list(z[\"ks\"]) != ks_want:\n            pass", [f"{TR}.EndToEnd"],
     "a unit of another K scan is not missing"),
]


def sha(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def main(argv: list) -> int:
    py = argv[0]
    only = int(argv[argv.index("--only") + 1]) if "--only" in argv else None
    killed = total = 0
    for i, (f, old, new, tests, what) in enumerate(MUTANTS, 1):
        if only is not None and i != only:
            continue
        path = HERE / f
        orig = path.read_bytes()
        text = orig.decode()
        if text.count(old) != 1:
            print(f"{i}\tNOT-APPLIED\t{f}\t{','.join(tests)}\t{what} (the site occurs {text.count(old)} times)")
            return 2
        try:
            path.write_text(text.replace(old, new))
            r = subprocess.run([py, "-B", "-m", "unittest", *tests], cwd=HERE, capture_output=True, text=True,
                               env=dict(os.environ, PYTHONDONTWRITEBYTECODE="1", OMP_NUM_THREADS="2"))
        finally:
            path.write_bytes(orig)
        if sha(path.read_bytes()) != sha(orig):
            print(f"{i}\tRESTORE-FAILED\t{f}")
            return 3
        total += 1
        verdict = "KILLED" if r.returncode != 0 else "SURVIVED"
        killed += verdict == "KILLED"
        print(f"{i}\t{verdict}\t{f}\t{','.join(tests)}\t{what}", flush=True)
    print(f"TOTAL\t{killed}/{total} killed")
    return 0 if killed == total else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))

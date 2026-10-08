#!/usr/bin/env python3
"""Run every replay in this release and check it against the expected outputs. Exit 0 only if all agree.

1. joint tests, frozen evaluation: replay vs expected/joint-evaluate.json (every p, k, B, decision, label, power);
2. lost-seed resolution, reading (a) (report-only): replay vs expected/resolved-evaluate.json;
3. W1 matched coarse projections (report-only): build reading (b), run W1 on (a) and (b), compare every claim
   k, B, p and every criterion boolean with expected/W1-RESULT-20261006.json (reading labels are not compared);
4. (RC2+) the article's Figs. 1-3: recompute every quoted number from data/figs/fig_arrays.npz against the printed
   values in expected/values.tex, and regenerate the three figures; regenerate Fig. 4 from the frozen inputs.
5. (RC5+) condition (i)'s fine-grid L2 ratios: recompute them from data/m1f2/ and check the printed range
   (macros jtMoneMin--jtMoneMax in expected/values_inference.tex); check that the released M1 shifts are the frozen
   evaluator's d1 vectors.
6. (RC6+) a negative control: fig_numbers.py must reject a perturbed printed value.
Run from the release root: python3 code/verify_rc.py
"""
from __future__ import annotations

import json
import re
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PY = sys.executable


def run(*args) -> subprocess.CompletedProcess:
    return subprocess.run([PY, *map(str, args)], cwd=ROOT, capture_output=True, text=True)


def main() -> int:
    ok = True
    for npz, exp in (("data/frozen/inference_sufficient.npz", "expected/joint-evaluate.json"),
                     ("data/recovery-union/inference_sufficient.npz", "expected/resolved-evaluate.json")):
        r = run("code/replay_inference.py", "--npz", npz, "--compare", exp)
        last = (r.stdout.strip().splitlines() or ["(no output)"])[-1]
        print(f"[{'ok' if r.returncode == 0 else 'FAIL'}] {npz} vs {exp}: {last}")
        ok &= r.returncode == 0
    with tempfile.TemporaryDirectory() as td:
        rb = Path(td) / "reading_b.npz"
        r = run("code/make_reading_b.py", "--frozen", "data/frozen/inference_sufficient.npz",
                "--union", "data/recovery-union/inference_sufficient.npz", "--out", rb)
        if r.returncode:
            print("[FAIL] make_reading_b:", r.stderr.strip()[-400:])
            return 1
        out = Path(td) / "w1.json"
        r = run("code/w1_projected_tests.py", "--npz", "data/recovery-union/inference_sufficient.npz", "--npz", rb,
                "--recorded", "expected/joint-evaluate.json", "--out", out)
        if r.returncode:
            print("[FAIL] w1:", r.stderr.strip()[-400:])
            return 1
        a, b = json.loads(out.read_text()), json.loads((ROOT / "expected/W1-RESULT-20261006.json").read_text())
        diffs = [k for ra, rb_ in zip(a["readings"], b["readings"]) for k in ra["tests"]
                 if {f: ra["tests"][k]["claim"][f] for f in ("k", "B", "p")} != {f: rb_["tests"][k]["claim"][f] for f in ("k", "B", "p")}]
        crit = [k for k in a["criterion"] if a["criterion"][k]["joint_beyond_matched_coarse_projections"]
                != b["criterion"][k]["joint_beyond_matched_coarse_projections"]]
        w1ok = not diffs and not crit and len(a["readings"]) == 2
        print(f"[{'ok' if w1ok else 'FAIL'}] W1: {len(diffs)} claim differences, {len(crit)} criterion differences "
              f"(qualifying: {[k for k, v in a['criterion'].items() if v['joint_beyond_matched_coarse_projections']]})")
        ok &= w1ok
    if (ROOT / "data/figs/fig_arrays.npz").exists():  # RC2: the article's Figs. 1-3 and their quoted numbers
        r = run("code/figs/fig_numbers.py", "--npz", "data/figs/fig_arrays.npz", "--values", "expected/values.tex")
        last = (r.stdout.strip().splitlines() or ["(no output)"])[-1]
        print(f"[{'ok' if r.returncode == 0 else 'FAIL'}] Figs. 1-3 quoted numbers vs expected/values.tex: {last}")
        ok &= r.returncode == 0
        # Negative control: the check must FAIL on a printed value it should reject. Perturb one Sec. V macro by one
        # unit in its last digit and require fig_numbers.py to report a discrepancy.
        vt = (ROOT / "expected/values.tex").read_text()
        m = re.search(r"(\\newcommand\{\\gibuuCorner\}\{)([0-9.]+)(\})", vt)
        if m:
            bad = f"{float(m.group(2)) + 0.01:.2f}"
            with tempfile.TemporaryDirectory() as td:
                pv = Path(td) / "values-perturbed.tex"
                pv.write_text(vt[:m.start(2)] + bad + vt[m.end(2):])
                r = run("code/figs/fig_numbers.py", "--npz", "data/figs/fig_arrays.npz", "--values", pv)
            ctl = r.returncode != 0 and "DISCREPANCY" in r.stdout
            print(f"[{'ok' if ctl else 'FAIL'}] negative control: fig_numbers.py rejects \\gibuuCorner {m.group(2)} -> {bad}")
            ok &= ctl
        else:
            print("[FAIL] negative control: \\gibuuCorner not found in expected/values.tex")
            ok = False
        with tempfile.TemporaryDirectory() as td:
            r = run("code/figs/make_figs.py", "--npz", "data/figs/fig_arrays.npz", "--outdir", td,
                "--values", "expected/values.tex")
            made = sorted(p.name for p in Path(td).glob("*.pdf"))
            figok = r.returncode == 0 and len(made) >= 3
            print(f"[{'ok' if figok else 'FAIL'}] Figs. 1-3 regenerated: {made}")
            if not figok:
                print("   ", r.stderr.strip()[-400:])
            ok &= figok
            f4 = Path(td) / "fig4_joint_nulls.pdf"
            r = run("code/figs/plot_joint_null_distributions.py", "--npz", "data/frozen/inference_sufficient.npz",
                    "--out", f4)
            f4ok = r.returncode == 0 and f4.exists()
            print(f"[{'ok' if f4ok else 'FAIL'}] Fig. 4 (calibrated null distributions) regenerated from the frozen inputs")
            if not f4ok:
                print("   ", r.stderr.strip()[-400:])
            ok &= f4ok
    if (ROOT / "data/m1f2").is_dir():  # RC5: condition (i)'s L2 ratios and the identity of the M1 shifts
        r = run("code/m1_f2_norm_ratio.py", "data/m1f2")
        m1ok = r.returncode == 0
        if m1ok:
            res = json.loads(r.stdout)
            macros = dict(re.findall(r"\\newcommand\{\\(\w+)\}\{([^}]*)\}",
                                     (ROOT / "expected/values_inference.tex").read_text()))
            lo, hi = res["relative_L2_range"]
            m1ok = f"{lo:.2f}" == macros["jtMoneMin"] and f"{hi:.2f}" == macros["jtMoneMax"]
            import numpy as np
            man = json.loads((ROOT / "data/frozen/inference_sufficient.npz.manifest.json").read_text())
            z = np.load(ROOT / "data/frozen/inference_sufficient.npz")
            gen = {"GENIE_2_12_10_CV": "genie_cv", "GENIE_2_12_10_MEC": "genie_mec", "NuWro_21_09": "nuwro_cv",
                   "GiBUU_2019": "gibuu_cv"}
            same = [bool(np.array_equal(z[f"d1__{k}"], np.load(ROOT / f"data/m1f2/fine-minus-mid-{g}.npz")["D_J"]))
                    for k, g in gen.items() if man["nulls"][k]["m1"] is not None]
            m1ok &= len(same) == 4 and all(same)
            print(f"[{'ok' if m1ok else 'FAIL'}] condition (i) L2 ratios {lo:.3f}-{hi:.3f} vs printed "
                  f"{macros['jtMoneMin']}-{macros['jtMoneMax']}; M1 shifts identical to frozen d1: {sum(same)}/4")
        else:
            print("[FAIL] m1_f2_norm_ratio:", r.stderr.strip()[-400:])
        ok &= m1ok
    print("VERIFY:", "PASS" if ok else "FAIL")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())

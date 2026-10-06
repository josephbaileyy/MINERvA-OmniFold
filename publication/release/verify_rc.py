#!/usr/bin/env python3
"""Run every replay in this release and check it against the expected outputs. Exit 0 only if all agree.

1. joint tests, frozen evaluation: replay vs expected/joint-evaluate.json (every p, k, B, decision, label, power);
2. lost-seed resolution, reading (a) (report-only): replay vs expected/resolved-evaluate.json;
3. W1 matched coarse projections (report-only): build reading (b), run W1 on (a) and (b), compare every claim
   k, B, p and every criterion boolean with expected/W1-RESULT-20261006.json (reading labels are not compared);
4. (RC2) the article's Figs. 1-3: recompute every quoted number from data/figs/fig_arrays.npz against the printed
   values in expected/values.tex, and regenerate the three figures.
Run from the release root: python3 code/verify_rc.py
"""
from __future__ import annotations

import json
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
        with tempfile.TemporaryDirectory() as td:
            r = run("code/figs/make_figs.py", "--npz", "data/figs/fig_arrays.npz", "--outdir", td)
            made = sorted(p.name for p in Path(td).glob("*.pdf"))
            figok = r.returncode == 0 and len(made) >= 3
            print(f"[{'ok' if figok else 'FAIL'}] Figs. 1-3 regenerated: {made}")
            ok &= figok
    print("VERIFY:", "PASS" if ok else "FAIL")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())

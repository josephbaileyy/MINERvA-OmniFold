#!/usr/bin/env python3
"""Mutation run for GENCMP amendment E's addendum E-A2 (FD-GENCMP-AMENDMENT-E-ADDENDUM-EA2.md): one textual change at a
time to fd_g_figures.py, fd_g_figures_check.py or fd_gencmp_ea2.py, applied in place; test_fd_gencmp_ea2 and
test_fd_gencmp_e run against it, and the file is restored (every file's sha256 checked after every mutant and at the
end). A mutant is killed if the run fails; one whose text is not found exactly once counts as a failure.

    python3 -I -B mutants_ea2.py <repo> [--dry]
"""
import hashlib
import os
import subprocess
import sys
from pathlib import Path

REPO = Path(sys.argv[1]).resolve()
ND = REPO / "nd-unfolding"
G, C, A = ND / "fd_g_figures.py", ND / "fd_g_figures_check.py", ND / "fd_gencmp_ea2.py"
MUTANTS = [
    (G, "legend keeps NuWro's flag", '    "gencmp-chdefs": ({"nuwro": ("CH",),', '    "gencmp-chdefs": ({"nuwro": ("CH", "hydrogen: supplement FLAGGED"),'),
    (G, "legend keeps GiBUU's flag", '"gibuu": ("CH", "p_parallel < 4.5 cells only"),',
     '"gibuu": ("CH", "hydrogen: closure B3 failed", "p_parallel < 4.5 cells only"),'),
    (G, "GiBUU loses CH", '"gibuu": ("CH", "p_parallel < 4.5 cells only"),', '"gibuu": ("p_parallel < 4.5 cells only",),'),
    (G, "K7 still requires a flag", '                      ("prior (not an independent prediction)", "p_parallel < 4.5 cells only")),',
     '                      ("hydrogen: supplement FLAGGED", "prior (not an independent prediction)", "p_parallel < 4.5 cells only")),'),
    (G, "K7 drops the p_parallel string", '                      ("prior (not an independent prediction)", "p_parallel < 4.5 cells only")),',
     '                      ("prior (not an independent prediction)",)),'),
    (C, "checker keeps NuWro's flag", '"nuwro": "NuWro 21.09: CH",', '"nuwro": "NuWro 21.09: CH; hydrogen: supplement FLAGGED",'),
    (C, "checker keeps GiBUU's flag", '"gibuu": "GiBUU 2019: CH; $p_\\\\parallel$ < 4.5 cells only",',
     '"gibuu": "GiBUU 2019: CH; hydrogen: closure B3 failed; $p_\\\\parallel$ < 4.5 cells only",'),
    (C, "checker MUST keeps a flag", '                      ("prior (not an independent prediction)", "p_parallel < 4.5 cells only")),',
     '                      ("hydrogen: closure B3 failed", "prior (not an independent prediction)", "p_parallel < 4.5 cells only")),'),
    (A, "control D: label text unchecked", '            if b.get("text") != want:', "            if False:"),
    (A, "control D: no change accepted", '        report[n] = {"pass": not bad and changed > 0,', '        report[n] = {"pass": not bad,'),
    (A, "control D: options free", 'SIDECAR_FREE = ("argv", "code", "versions", "pdf_sha256", "pdf_bytes", "file")',
     'SIDECAR_FREE = ("argv", "code", "versions", "pdf_sha256", "pdf_bytes", "file", "options")'),
    (A, "control D: legends block unchecked", '        if k != "items" and po.get(k) != pn.get(k):', "        if False:"),
    (A, "control D: other item fields unchecked", "        if a != b:\n            bad.append(", "        if False:\n            bad.append("),
    (A, "inputs unchecked", "            if got != pins.get(key) or got != want_inputs.get(key):", "            if False:"),
    (A, "out-dir overwrite allowed", "        if a.out_dir.exists():\n            raise Refuse", "        if False:\n            raise Refuse"),
    (A, "figure check skipped", "    rc = subprocess.run(chk).returncode", "    rc = 0"),
]


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


orig = {p: p.read_text() for p in (G, C, A)}
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
        r = subprocess.run([sys.executable, "-B", "-m", "unittest", "test_fd_gencmp_ea2", "test_fd_gencmp_e"],
                           cwd=ND / "tests", env=env, capture_output=True, text=True, timeout=1800)
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

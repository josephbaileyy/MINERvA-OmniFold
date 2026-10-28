"""Reviewer mutants on a scratch copy of the head tool (never the worktree)."""
import subprocess, sys, os, hashlib
from pathlib import Path
ROOT = Path(sys.argv[1]); TOOL = ROOT / "nd-unfolding/fd_flux_boot.py"; TESTS = ROOT / "nd-unfolding/tests"
B2 = "got = chi2s(x.f, g, Vg, C_stage_g + (C1 - C0), cells)"
M = [
    ("B2 without the rebuilt block", B2, "got = chi2s(x.f, g, Vg, C_stage_g, cells)"),
    ("B2 difference sign flipped", B2, "got = chi2s(x.f, g, Vg, C_stage_g + (C0 - C1), cells)"),
    ("B2 swaps in S1's block, not the rebuild", B2, "got = chi2s(x.f, g, Vg, C_stage_g + (C0 - C0), cells)"),
    ("B2 doubles the difference", B2, "got = chi2s(x.f, g, Vg, C_stage_g + 2 * (C1 - C0), cells)"),
    ("C_stage_g without C_resp (B2 + replicates)", "C_stage_g = x.Ct + (x.Cx if carries else 0)", "C_stage_g = x.Ct"),
    ("uniform difference sign flipped", "C_stage_g + (Cu - C0), cells)", "C_stage_g + (C0 - Cu), cells)"),
]
orig = TOOL.read_bytes(); want = hashlib.sha256(orig).hexdigest()
env = {k: v for k, v in os.environ.items() if k != "PYTHONPATH"}; env["TMPDIR"] = sys.argv[2]
try:
    for name, old, new in M:
        src = orig.decode()
        if src.count(old) != 1:
            print("NOT APPLIED", src.count(old), name, flush=True); continue
        TOOL.write_text(src.replace(old, new))
        r = subprocess.run([sys.executable, "-B", "-m", "unittest", "test_fd_flux_boot"], cwd=TESTS, env=env,
                           capture_output=True, text=True, timeout=1200)
        TOOL.write_bytes(orig)
        fails = [l for l in r.stderr.splitlines() if l.startswith(("FAIL:", "ERROR:"))]
        print(("KILLED" if r.returncode else "SURVIVED"), name, "|", r.stderr.strip().splitlines()[-1], fails[:3], flush=True)
finally:
    TOOL.write_bytes(orig)
print("restored", hashlib.sha256(TOOL.read_bytes()).hexdigest() == want)

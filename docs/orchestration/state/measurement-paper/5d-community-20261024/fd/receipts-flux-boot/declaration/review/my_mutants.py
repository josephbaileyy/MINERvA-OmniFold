"""Reviewer mutants, applied to the SCRATCH COPY only (review-3d/mut/nd-unfolding/fd_flux_boot.py)."""
import hashlib
import os
import subprocess
import sys
from pathlib import Path

ND = Path(sys.argv[1]).resolve()
assert "review-3d/mut" in str(ND), ND
TOOL = ND / "fd_flux_boot.py"
CLASSES = ["test_fd_flux_boot.Pure", "test_fd_flux_boot.EndToEnd", "test_fd_flux_boot.Controls",
           "test_fd_flux_boot.Invocation"]
MUTANTS = [
    ("weights not carried (unresampled w with X[i])", "return sa.mat_cov(X[i], w[i])", "return sa.mat_cov(X[i], w)"),
    ("B0 count of recorded universes unchecked", "not bad and n_rec == N_UNIVERSES", "not bad"),
    ("weights reversed (sum, n_eff unchanged)", "    w = G.sa_call(\"B0\", sa.flux_weights, path)\n",
     "    w = G.sa_call(\"B0\", sa.flux_weights, path)[::-1].copy()\n"),
    ("n_eff_replicate from unresampled w", "neff.append(n_eff(w[ib]))", "neff.append(n_eff(w))"),
    ("correlation_s1 reported matrix without flux", "\"reported_matrix\": correlation(total_rest + C0 / ff, *pair)",
     "\"reported_matrix\": correlation(total_rest, *pair)"),
    ("non-PD replicate silently dropped", "                    p4.append(f\"replicate {b} {v} {spec['name']}\")\n", ""),
    ("correlation_band reported matrix uses C0 not replicate",
     "corr[f\"reported_matrix_{v}\"].append(correlation(total_rest + Crel, *pair))",
     "corr[f\"reported_matrix_{v}\"].append(correlation(total_rest + C0 / ff, *pair))"),
]


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


orig = TOOL.read_bytes()
want = sha(TOOL)
env = {k: v for k, v in os.environ.items() if k != "PYTHONPATH"}
try:
    for name, old, new in MUTANTS:
        src = orig.decode()
        if src.count(old) != 1:
            print(f"NOT APPLIED ({src.count(old)}): {name}", flush=True)
            continue
        TOOL.write_text(src.replace(old, new))
        r = subprocess.run([sys.executable, "-B", "-m", "unittest", *CLASSES], cwd=ND / "tests", env=env,
                           capture_output=True, text=True, timeout=900)
        TOOL.write_bytes(orig)
        tail = r.stderr.strip().splitlines()[-1] if r.stderr.strip() else ""
        print(f"{'KILLED' if r.returncode else 'SURVIVED'}: {name} ({tail})", flush=True)
finally:
    TOOL.write_bytes(orig)
print("restored", sha(TOOL) == want, sha(TOOL))

#!/usr/bin/env python3
"""Mutation run for fd_flux_boot.py (FD-FLUX-BOOT-DECLARATION.md section 6.3): each mutant is one textual change to the
tool, applied in place, the test module's Pure, EndToEnd, Controls and Invocation classes run against it, and the tool
restored (its sha256 is checked after every mutant and at the end). A mutant is killed if the run fails.

    python3 -I -B mutants.py <repo>
"""
import hashlib
import os
import subprocess
import sys
from pathlib import Path

REPO = Path(sys.argv[1]).resolve()
TOOL = REPO / "nd-unfolding/fd_flux_boot.py"
TESTS = REPO / "nd-unfolding/tests"
CLASSES = ["test_fd_flux_boot.Pure", "test_fd_flux_boot.EndToEnd", "test_fd_flux_boot.Controls",
           "test_fd_flux_boot.Invocation"]
MUTANTS = [
    ("replicate without weights", "return sa.mat_cov(X[i], w[i])", "return sa.mat_cov(X[i])"),
    ("swap keeps no variance", "    np.fill_diagonal(out, np.diag(C0))\n    return out", "    return out"),
    ("swap returns the replicate", "out = Cstar / np.outer(ss, ss) * np.outer(s0, s0)", "out = Cstar.copy()"),
    ("shape-only lambda 10", "M + G.SHAPE_LAMBDA * np.ones_like(M)", "M + 10.0 * np.ones_like(M)"),
    ("halves swapped", '"halves": [pct(v[:h]), pct(v[h:])]', '"halves": [pct(v[h:]), pct(v[:h])]'),
    ("percentile method nearest", 'PERCENTILE_METHOD = "linear"', 'PERCENTILE_METHOD = "nearest"'),
    ("B1 always passes", 'members == [f"band:{sa.FLUX}"] and worst <= TOL', "True"),
    ("B2 tolerance 1", "f\"(worst {worst:.1e})\", worst <= REPRO, f\"worst {worst:.3e}\")\n\n    # B3",
     "f\"(worst {worst:.1e})\", worst <= 1e300, f\"worst {worst:.3e}\")\n\n    # B3"),
    ("B3 skipped", "idx.shape == (B_REPLICATES, N_UNIVERSES) and dig == INDEX_SHA256", "True"),
    ("B4 variance check removed", "if not np.all(np.diag(Cs) > 0):", "if False:"),
    ("B5 never records", '                p5.append(f"replicate {b}")', "                pass"),
    ("B0 meta unchecked", '!= ("s5p-universe/1", f"{sa.FLUX}:{u}"):', '!= (m.get("schema"), m.get("universe")):'),
    ("B0 n_eff unchecked", "and abs(n_eff(w) - fw[\"n_eff\"]) <= TOL * fw[\"n_eff\"]", ""),
    ("B0 digest unchecked", "        if got != rec.get(p.name):", "        if False:"),
    ("pair R04-R09", 'PAIR = ("R04", "R08")', 'PAIR = ("R04", "R09")'),
    ("uniform is weighted", "    Cu = sa.mat_cov(X)\n", "    Cu = sa.mat_cov(X, w)\n"),
    ("correlation variant is the block", 'Cv = correlation_swap(Cs, C0) if v == "correlation" else Cs',
     'Cv = Cs'),
    ("reported matrix without C_resp", "    _, carries = x.comps[0][1]", "    _, carries = x.comps[0][1]\n    carries = False"),
    ("n_eff wrong", "return float(w.sum() ** 2 / (w ** 2).sum())", "return float(w.sum() / (w ** 2).sum())"),
    ("delta method ddof 0", ".std(axis=0, ddof=1)", ".std(axis=0, ddof=0)"),
    # review round 1 (fd/receipts-flux-boot/declaration/review/my_mutants.log) and the code it added
    ("B0 count of recorded universes unchecked", "not bad and n_rec == N_UNIVERSES", "not bad"),
    ("weights not carried", "return sa.mat_cov(X[i], w[i])", "return sa.mat_cov(X[i], w[np.arange(len(i))])"),
    ("weights reversed (sum, n_eff unchanged)", 'w = G.sa_call("B0", sa.flux_weights, path)',
     'w = G.sa_call("B0", sa.flux_weights, path)[::-1]'),
    ("non-PD replicate silently dropped", '                    p4.append(f"replicate {b} {v} {spec[\'name\']}")',
     "                    pass"),
    ("correlation band of the reported matrix uses C0",
     'corr[f"reported_matrix_{v}"].append(correlation(total_rest + Crel, *pair))',
     'corr[f"reported_matrix_{v}"].append(correlation(total_rest + C0 / ff, *pair))'),
    ("correlation_s1 reported matrix without flux", '"reported_matrix": correlation(total_rest + C0 / ff, *pair)',
     '"reported_matrix": correlation(total_rest, *pair)'),
    ("spread ratio without n_eff", "(sd / (sw / np.sqrt(n_eff(w))))", "(sd / sw)"),
    ("uniform non-PD unguarded", '            p4.append(f"uniform {spec[\'name\']}")\n            continue',
     "            pass"),
    ("basic band not mirrored", 'q[f"{100 - p:g}"]', 'q[f"{p:g}"]'),
    ("offset sign flipped", 'q["50"] - centre', 'centre - q["50"]'),
]


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def main():
    orig = TOOL.read_bytes()
    want = sha(TOOL)
    env = {k: v for k, v in os.environ.items() if k != "PYTHONPATH"}
    killed = 0
    try:
        for name, old, new in MUTANTS:
            src = orig.decode()
            if src.count(old) != 1:
                print(f"NOT APPLIED ({src.count(old)} matches): {name}", flush=True)
                continue
            TOOL.write_text(src.replace(old, new))
            r = subprocess.run([sys.executable, "-B", "-m", "unittest", *CLASSES], cwd=TESTS, env=env,
                               capture_output=True, text=True, timeout=900)
            TOOL.write_bytes(orig)
            assert sha(TOOL) == want
            tail = r.stderr.strip().splitlines()[-1] if r.stderr.strip() else ""
            status = "KILLED" if r.returncode != 0 else "SURVIVED"
            killed += r.returncode != 0
            print(f"{status}: {name} ({tail})", flush=True)
    finally:
        TOOL.write_bytes(orig)
    print(f"{killed} of {len(MUTANTS)} killed; tool restored, sha256 {sha(TOOL)} (expected {want})", flush=True)
    return 0 if sha(TOOL) == want else 1


if __name__ == "__main__":
    raise SystemExit(main())

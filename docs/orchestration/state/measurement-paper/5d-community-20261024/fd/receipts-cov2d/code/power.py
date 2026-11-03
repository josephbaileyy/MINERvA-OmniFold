"""COV2D section 5.2's flag counts and power at 205 cells and 300 toys, by fd_1b_null imported unchanged.
    python -B power.py <worktree>"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(sys.argv[1]) / "nd-unfolding"))
import fd_1b_null as n  # noqa: E402

for cells in (16, 205):
    k = n.flag_count(n.P0, 300, 0.025 / cells)
    pw = {pt: round(n.binom_cdf(k, 300, pt), 3) for pt in (0.62, 0.60, 0.58, 0.56, 0.55, 0.52, 0.50)}
    print(f"cells={cells} alpha_cell={0.025 / cells:.3e} k_c={k} size_cell_at_P0={n.binom_cdf(k, 300, n.P0):.3e} "
          f"flag_probability_at_true_content={pw}")
kj = n.flag_count(n.P0, 300, 0.025)
print(f"joint k_J={kj} flag_probability_at_true_q={ {q: round(n.binom_cdf(kj, 300, q), 3) for q in (0.64, 0.62, 0.60)} }")

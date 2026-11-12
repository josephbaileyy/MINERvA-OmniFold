#!/usr/bin/env python3
"""Single-site mutants of vhr_binning.py; each must be killed by test_vhr_binning.py.

Every mutant runs in a fresh temporary mirror of the repository path. vhr_binning.py (mutated) and the test are copied
in, and nd-unfolding is a symlink to the real one, which is read only. The real files are never edited. Each mutation's
old text must occur exactly once. Exit 0 only if every mutant is killed and the unmutated copy passes.
"""
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[6]
REL = HERE.relative_to(REPO)
SRC = (HERE / "vhr_binning.py").read_text()

MUTANTS = [
    ("criterion 0.5 -> 0.4", "CRIT = 0.5 ", "CRIT = 0.4 "),
    ("share 0.2 -> 0.25", "SHARE = 0.2 ", "SHARE = 0.25 "),
    ("veto crossing: before <= -> <", "if before[0] <= VETO < after[0]:", "if before[0] < VETO < after[0]:"),
    ("veto crossing: after > -> >=", "if before[0] <= VETO < after[0]:", "if before[0] <= VETO <= after[0]:"),
    ("veto skips untouched -> skips touched", "        if touched.isdisjoint(cells):\n            continue\n        tot, after",
     "        if not touched.isdisjoint(cells):\n            continue\n        tot, after"),
    ("structural & -> |", "np.any((left >= SHARE * tot) & (tot - left >= SHARE * tot))",
     "np.any((left >= SHARE * tot) | (tot - left >= SHARE * tot))"),
    ("final two pieces -> one", "sum(s >= SHARE for s in shares) < 2", "sum(s >= SHARE for s in shares) < 1"),
    ("strip refusal off", "if self.two_d and any(lo == 0", "if False and any(lo == 0"),
    ("p_par edge: <= -> <", "u[k][0] < PZ_SPLIT <= u[k][1]", "u[k][0] < PZ_SPLIT < u[k][1]"),
    ("C0 refuses pt instead of pz", 'AXES[k] == "pz" else None', 'AXES[k] == "pt" else None'),
    ("candidate low: or -> and", '< CRIT or not f["supported"]', '< CRIT and not f["supported"]'),
    ("repro low ignores support", 'return f["supported"] and f["purity"] < tau', 'return f["purity"] < tau'),
    ("join order: best -> worst union", "cand.append((-value(u), k, geom.first(b), j))",
     "cand.append((value(u), k, geom.first(b), j))"),
    ("value: min -> max", 'else min(f["purity"], f["diagonal_fraction"])', 'else max(f["purity"], f["diagonal_fraction"])'),
    ("reco_all needs pass_truth", "ra = np.bincount(br[pr & (br >= 0)], weights=wr[pr & (br >= 0)], minlength=n)",
     "ra = np.bincount(br[pr & pt & (br >= 0)], weights=wr[pr & pt & (br >= 0)], minlength=n)"),
    ("truth_reco ignores pass_reco", "tr = np.bincount(bt[pt & pr & (bt >= 0)], weights=wr[pt & pr & (bt >= 0)], minlength=n)",
     "tr = np.bincount(bt[pt & (bt >= 0)], weights=wr[pt & (bt >= 0)], minlength=n)"),
    ("truth_sel weight w_truth -> w_reco", "weights=wt[pt & (bt >= 0)]", "weights=wr[pt & (bt >= 0)]"),
    ("support: and -> or", "bool(ra >= SUPPORT_MIN and ts >= SUPPORT_MIN)", "bool(ra >= SUPPORT_MIN or ts >= SUPPORT_MIN)"),
    ("T3 diagonal fraction dropped", '("diagonal fraction", f["diagonal_fraction"] < CRIT)',
     '("diagonal fraction", f["diagonal_fraction"] < 0.0)'),
    ("1D floor 3 -> 2", "FLOOR = {1: 3, 2: 6}", "FLOOR = {1: 2, 2: 6}"),
    ("C0 per side 4 -> 3", "C0_FLOOR, C0_PER_SIDE = 8, 4", "C0_FLOOR, C0_PER_SIDE = 8, 3"),
    ("weights: negative allowed", "np.all(wt[m] >= 0)", "np.all(wt[m] > -1)"),
    ("in_share uses the row sums", '"in_share": (ra - float(self.inside_col[u].sum()))',
     '"in_share": (ra - float(self.inside_row[u].sum()))'),
    ("Ω: every fine cell", "    return fmap >= 0, h2_of_fine", "    return fmap >= -1, h2_of_fine"),
    ("grid adjacency one-sided", "return k if ahi + 1 == blo or bhi + 1 == alo else None",
     "return k if ahi + 1 == blo else None"),
    ("landmark 0.8 -> 0.4", '"equal" if e == 0.8 else', '"equal" if e == 0.4 else'),
    ("veto off in merge", "if why is None and two_d and veto(", "if why is None and False and veto("),
    # coverage-5b-audit's survivors at 01455b6c (V2), and V1 and V3
    ("outcome: structural branch dropped", "    if structural:\n        out.append", "    if False:\n        out.append"),
    ("outcome: final branch dropped", "    if final2d:\n        out.append", "    if False:\n        out.append"),
    ("final check never computed", "    final2d = final_two_piece_failures(", "    final2d = [] if True else final_two_piece_failures("),
    ("C7 2D rules off", '"C7": (("eavail", "q3"), False, True)', '"C7": (("eavail", "q3"), False, False)'),
    ("C6 2D rules off", '"C6": (("pt", "pz"), True, True)', '"C6": (("pt", "pz"), True, False)'),
    ("C2 p_par edge unfrozen", '"C2": (("pz",), True, False)', '"C2": (("pz",), False, False)'),
    ("C6 p_par edge unfrozen", '"C6": (("pt", "pz"), True, True)', '"C6": (("pt", "pz"), False, True)'),
    ("status ignores the outcome", '"terminal (binning alone)" if rec["outcome"] else', '"terminal (binning alone)" if False else'),
    ("2D floor 6 -> 5", "FLOOR = {1: 3, 2: 6}", "FLOOR = {1: 3, 2: 5}"),
    ("final check on empty lines", "if tot > 0 and sum(s >= SHARE for s in shares) < 2:",
     "if tot >= 0 and sum(s >= SHARE for s in shares) < 2:"),
    ("veto empty-line guard dropped", "        if tot <= 0:\n            continue\n        _, before", "        _, before"),
    ("npz pin off", 'require(h.hexdigest() == expect, "the npz', 'require(True, "the npz'),
    ("h2_definition pin off", "require(hashlib.sha256(raw).hexdigest() == expect,", "require(True,"),
    ("fine-map check off", 'require(hashlib.sha256(fmap.tobytes()).hexdigest() == h2def["fine_map_sha256_int32le"],',
     "require(True,"),
    ("main skips check_weights", "        check_weights(arrays, omega)\n        repro", "        repro"),
    ("reproduction mismatch ignored", 'require(all(checks.values()), "the reproduction', 'require(True, "the reproduction'),
    ("reproduction in candidate mode", 'mode="repro", tau=REPRO_TAU)', 'mode="candidate", tau=REPRO_TAU)'),
    ("low ties: highest first index", "lows = [(value(b), geom.first(b), i)", "lows = [(value(b), -geom.first(b), i)"),
    ("the highest low goes first", "v, _, i = min(lows)", "v, _, i = max(lows)"),
    ("partner ties: highest axis", "cand.append((-value(u), k, geom.first(b), j))", "cand.append((-value(u), -k, geom.first(b), j))"),
    ("partner ties: highest first index", "cand.append((-value(u), k, geom.first(b), j))",
     "cand.append((-value(u), k, -geom.first(b), j))"),
    ("w_reco set narrowed", "np.isfinite(wr[pr & (t_in | r_in)])", "np.isfinite(wr[pr & r_in])"),
    ("excluded region over-named", "        if len(bits) == 1:", "        if len(bits) >= 1:"),
    ("C0 unmasked", "base = np.where(omega, h2_of_fine, -1)", "base = np.asarray(h2_of_fine)"),
    ("non-finite record skipped (audit x1)", 'raise Stop(f"{name} holds a non-finite figure: {e}")', "continue"),
]


def run(src):
    with tempfile.TemporaryDirectory() as t:
        root = Path(t)
        (root / "nd-unfolding").symlink_to(REPO / "nd-unfolding", target_is_directory=True)
        d = root / REL
        d.mkdir(parents=True)
        (d / "vhr_binning.py").write_text(src)
        shutil.copy2(HERE / "test_vhr_binning.py", d / "test_vhr_binning.py")
        r = subprocess.run([sys.executable, "-I", "-B", str(d / "test_vhr_binning.py")], capture_output=True, text=True,
                           timeout=900)
        return r.returncode


def main():
    base = run(SRC)
    print(f"unmutated: {'PASS' if base == 0 else 'FAIL'} (rc {base})")
    if base != 0:
        return 1
    killed = 0
    for name, old, new in MUTANTS:
        n = SRC.count(old)
        if n != 1:
            print(f"BAD MUTANT {name}: old text occurs {n} times")
            return 1
        rc = run(SRC.replace(old, new))
        ok = rc != 0
        killed += ok
        print(f"{'killed  ' if ok else 'SURVIVED'} {name}")
    print(f"MUTANTS: {killed}/{len(MUTANTS)} killed")
    return 0 if killed == len(MUTANTS) else 1


if __name__ == "__main__":
    sys.exit(main())

"""Build the retention check's explicit path list (all.tsv: group<TAB>path) from committed records only.
Usage: python3 -B make_retention_list.py <git archive of origin/main> <#1012 lists dir from its make_lists.py> <out.tsv>"""
import sys
from collections import Counter
from pathlib import Path
C, L, OUT = Path(sys.argv[1]), Path(sys.argv[2]), Path(sys.argv[3])
out = []
def add(g, paths):
    out.extend(f"{g}\t{p}" for p in paths)
for f in ("central", "cstat", "f0b", "prr", "cpl"):
    add(f, [l.split("\t")[-1].strip() for l in (L / f"{f}.txt").read_text().splitlines() if l.strip()])
PLS = ["1A", "1B", "1C", "1D", "1E", "1F", "1G", "1L", "1M", "1N", "1O", "1P"]
R = "/pscratch/sd/j/josephrb/minerva/minerva_large_files"
PL = C / "docs/orchestration/state/data-survey-20261022/outputs/playlist-lists"
for pl in PLS:
    d = [u.rsplit("/", 1)[1] for u in (PL / f"MediumEnergy_FHC_Data_Playlist{pl}.txt").read_text().split() if u]
    m = [u.rsplit("/", 1)[1] for u in (PL / f"MediumEnergy_FHC_StandardMC_Playlist{pl}.txt").read_text().split() if u]
    gd, gm = ("anatuple_data_1A", "anatuple_mc_1A") if pl == "1A" else ("anatuple_data_1B-1P", "anatuple_mc_1B-1P")
    add(gd, [f"{R}/Data/Playlist{pl}/{b}" for b in d])
    add(gm, [f"{R}/MC/StandardMC/Playlist{pl}/{b}" for b in m])
P = "/pscratch/sd/j/josephrb"
add("zero_loops", [f"{P}/measurement-paper/phase1/mp1/s1/evloop/zero/runEventLoopOmniFold_5D_{pl}_zero.root" for pl in PLS])
add("univ2d_per_playlist", [f"{P}/MINERvA-OmniFold/2d-unfolding/runEventLoopOmniFold_{pl}_universes_full.root" for pl in PLS])
add("rpd_dumps", [f"{P}/fd-rpd-20261103/dumps/lat_{pl}{s}.npz" for pl in PLS for s in ("", "_bkg")])
add("shared_inputs", [f"{P}/MINERvA-OmniFold/nd-unfolding/of_inputs_5d.npz", f"{P}/s5c-20260924/runs/p2/bkg_dump.npz"])
add("tier3_inputs", [f"{P}/MINERvA-OmniFold/nd-unfolding/bank_sweep_5d_bkgaware/cv.npz",
                     f"{P}/pv-ladder-20261024/prep/ratios/L-5D-PV/nuwro.json"]
    + [f"{P}/fd-stab-a1r-20261104/runs/control/closure/{t}/stab_control_{t}_s991000.npz" for t in ("nominal", "A7_gibuu")]
    + [f"{P}/s5p-20260926/ratios/nullsF/rho-{t}-F.npz" for t in ("genie_cv", "genie_mec", "gibuu_cv", "nuwro_cv")])
add("s1_cmodel_cresp_tables", [f"{P}/s1-20261024/s1_assembly.npz", f"{P}/cmodel5d-20261024/out/cmodel_5d.npz",
                               f"{P}/cresp-20261026/out/cresp.npz", f"{P}/fd-f1-20261027/grade/fd_f1_experiments.npz",
                               f"{P}/fd-f0b-20261026/fd_f0b_experiments.npz"])
paths = [l.split("\t")[1] for l in out]
assert len(paths) == len(set(paths)), "duplicate paths"
assert all(p.startswith("/pscratch/") and " " not in p and "\t" not in p for p in paths)
OUT.write_text("\n".join(out) + "\n")
print(Counter(l.split("\t")[0] for l in out), len(out))

"""Band diagnosis, P3's task table (FD-1B-BAND-DIAGNOSIS-DECLARATION.md section 7; BINDING-1 ruling 2 as addendum A2
sets it: 4 jobs x 7 lanes x 4 items, --time=01:40:00).

28 lines, each one fd_1b_band_diag.py unfold call over exactly 4 items that share one (mode, seed, eps, channel) group:
the 12 groups of 8 detector universes (E and B at seeds 45, 48, 51, 54, and at eps 1/2 and 2) split 4 + 4, and the 4
groups of 4 GEANT_Neutron/GEANT_Proton universes (E and B, channels signal and background) whole. Job j (0-3) runs lines
7j .. 7j+6. The module's own bulk_items(), imported from the deploy checkout, must equal the items the 28 lines carry,
each line must be one group of exactly 4 distinct universes, no item may repeat, and no pilot item may appear; any
difference refuses.

usage: python3 make_bdg_p3_table.py <deploy checkout> <W> <out table>
"""
import sys
from collections import OrderedDict
from pathlib import Path

P = "/pscratch/sd/j/josephrb"
PINS_SHA = "5adcd576eb46f443fe4133b05044cd315c0eeb0f281e21acee5f2318b4bab248"
EPS_ARG = {0.5: "0.5", 1.0: "1", 2.0: "2"}


def main() -> int:
    deploy, W, out = Path(sys.argv[1]), sys.argv[2], Path(sys.argv[3])
    sys.path.insert(0, str(deploy / "nd-unfolding"))
    import fd_1b_band_diag as d  # noqa: E402  (the deploy's bytes; the connect gates their sha256)
    bulk = d.bulk_items()
    groups = OrderedDict()
    for m, u, s, e, c in bulk:
        groups.setdefault((m, s, e, c), []).append(u)
    lines_items = []
    for key, us in groups.items():
        if len(us) == 8:
            lines_items += [(key, us[:4]), (key, us[4:])]
        elif len(us) == 4:
            lines_items.append((key, us))
        else:
            raise SystemExit(f"TABLE: group {key} has {len(us)} universes, not 4 or 8")
    carried = [(m, u, s, e, c) for (m, s, e, c), us in lines_items for u in us]
    if len(lines_items) != 28 or any(len(us) != 4 or len(set(us)) != 4 for _, us in lines_items):
        raise SystemExit("TABLE: not 28 lines of exactly 4 distinct universes")
    if len(carried) != 112 or len(set(carried)) != 112 or sorted(carried) != sorted(bulk):
        raise SystemExit("TABLE: the lines do not carry exactly bulk_items()")
    if set(carried) & set(d.pilot_items()):
        raise SystemExit("TABLE: a pilot item is on a P3 line")
    legal = set(d.items())
    if not set(carried) <= legal:
        raise SystemExit("TABLE: an item outside section 7")
    inputs = ["--npz", f"{P}/MINERvA-OmniFold/nd-unfolding/of_inputs_5d.npz",
              "--bkg", f"{P}/s5c-20260924/runs/p2/bkg_dump.npz",
              "--bank", f"{P}/MINERvA-OmniFold/nd-unfolding/bank_sweep_5d_bkgaware",
              "--detector-dir", f"{P}/s5p-20260926/bank_detector",
              "--pins", f"{P}/fd-1b-20261030/pins.json", "--expect-pins-sha256", PINS_SHA]
    lines = ["# band diagnosis, P3 (FD-1B-BAND-DIAGNOSIS-DECLARATION.md section 7; BINDING-1 ruling 2 as addendum A2): "
             "28 lines; job j runs lines 7j..7j+6"]
    for i, ((m, s, e, c), us) in enumerate(lines_items):
        lines.append("\t".join([f"fd1b_bdg_p3_{i:02d}_{m}", "fd_1b_band_diag.py", "unfold", "--mode", m, "--seed",
                                str(s), "--eps", EPS_ARG[e], "--channel", c, "--universes", ",".join(us)]
                               + inputs + ["--threads", "32", "--out", f"{W}/unf"]))
    out.write_text("\n".join(lines) + "\n")
    for j in range(4):
        print(f"TABLE: job {j}: lines {7 * j}..{7 * j + 6}: "
              + "; ".join(f"{m} s{s} e{EPS_ARG[e]} {c} {','.join(us)}" for (m, s, e, c), us in lines_items[7 * j:7 * j + 7]))
    print(f"TABLE: 28 lines, 112 items = bulk_items(); each line one group of 4")
    return 0


if __name__ == "__main__":
    sys.exit(main())

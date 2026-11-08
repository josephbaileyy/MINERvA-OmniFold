"""1B pre-check Part 1, P3's task table (FD-1B-PRECHECK-FD-DECLARATION.md section 7; Binding 1, addendum A1).

The bulk is the 327 items (A, B and Dnom, each at CV and the 108 universes: Flux_0..99 and the 8 detector universes),
less P2's 8 pilot items: 319. Section 7: 7 one-node jobs, 8 lanes per node, at most 6 items per lane.

Each table line is one lane: "<name><TAB>fd_1b_precheck_fd.py<TAB>unfold --mode M --universes U1,...,Uk <inputs>",
run by the committed s5c_array.sh. The module runs one mode per invocation, so each lane holds one mode. Each mode's
items, in the module's band order, are split into ceil(n/6) contiguous lanes as even as possible: A 106 -> 18 lanes,
B 106 -> 18, Dnom 107 -> 18. That is 54 lanes, laid out in that order over jobs of 8 lines (the seventh job has 6).

The module is imported from the deploy to read universes() and PILOT, which must equal the declaration's lists, and
every item outside them is refused.

usage: python3 -I make_p3_table.py <deploy checkout> <V> <out table>
"""
import math
import sys
from pathlib import Path

P = "/pscratch/sd/j/josephrb"
DETECTOR = ["GEANT_Neutron_0", "GEANT_Neutron_1", "GEANT_Pion_0", "GEANT_Pion_1", "GEANT_Proton_0", "GEANT_Proton_1",
            "MinosEfficiency_0", "MinosEfficiency_1"]
DECLARED_UNIVERSES = [f"Flux_{i}" for i in range(100)] + DETECTOR
SECTION7_PILOT = [("A", "CV"), ("B", "CV"), ("Dnom", "CV"), ("A", "Flux_0"), ("B", "Flux_0"), ("Dnom", "Flux_0"),
                  ("A", "MinosEfficiency_0"), ("B", "MinosEfficiency_0")]
MODES = ("A", "B", "Dnom")
PER_LANE, LANES_PER_JOB, JOBS = 6, 8, 7


def main() -> int:
    deploy, V, out = Path(sys.argv[1]), sys.argv[2], Path(sys.argv[3])
    sys.path.insert(0, str(deploy / "nd-unfolding"))
    import fd_1b_precheck_fd as pfd  # noqa: E402
    if list(pfd.universes()) != DECLARED_UNIVERSES:
        raise SystemExit("TABLE: the module's universes() is not the declared 108")
    if [tuple(x) for x in pfd.PILOT] != SECTION7_PILOT or tuple(pfd.MODES) != MODES:
        raise SystemExit("TABLE: the module's PILOT or MODES is not the declaration's")
    pilot = set(SECTION7_PILOT)
    lanes = []
    for mode in MODES:
        items = [u for u in ["CV"] + DECLARED_UNIVERSES if (mode, u) not in pilot]
        k = math.ceil(len(items) / PER_LANE)
        base, extra = divmod(len(items), k)
        i = 0
        for j in range(k):
            n = base + (1 if j < extra else 0)
            lanes.append((mode, items[i:i + n]))
            i += n
        assert i == len(items)
    total = sum(len(us) for _, us in lanes)
    allitems = {(m, u) for m, us in lanes for u in us}
    expect = {(m, u) for m in MODES for u in ["CV"] + DECLARED_UNIVERSES} - pilot
    if total != 319 or allitems != expect or len(allitems) != total:
        raise SystemExit(f"TABLE: {total} items, not section 7's 319")
    if max(len(us) for _, us in lanes) > PER_LANE or len(lanes) > LANES_PER_JOB * JOBS:
        raise SystemExit("TABLE: a lane over 6 items, or more lanes than 7 jobs of 8")
    common = ["--npz", f"{P}/MINERvA-OmniFold/nd-unfolding/of_inputs_5d.npz",
              "--bkg", f"{P}/s5c-20260924/runs/p2/bkg_dump.npz",
              "--bank", f"{P}/MINERvA-OmniFold/nd-unfolding/bank_sweep_5d_bkgaware",
              "--detector-dir", f"{P}/s5p-20260926/bank_detector",
              "--flux-file", f"{V}/stage/flux_universes.root",
              "--pins", f"{P}/fd-1b-20261030/pins.json",
              "--expect-pins-sha256", "5adcd576eb46f443fe4133b05044cd315c0eeb0f281e21acee5f2318b4bab248",
              "--threads", "32", "--out", f"{V}/unf"]
    lines = ["# 1B pre-check Part 1, P3 (FD-1B-PRECHECK-FD-DECLARATION.md section 7; Binding 1, addendum A1)"]
    for n, (mode, us) in enumerate(lanes):
        lines.append("\t".join([f"fd1b_pfd_p3_lane{n:02d}_{mode}", "fd_1b_precheck_fd.py", "unfold", "--mode", mode,
                                "--universes", ",".join(us)] + common))
    out.write_text("\n".join(lines) + "\n")
    jobs = [(j * LANES_PER_JOB, min(len(lanes), (j + 1) * LANES_PER_JOB) - 1) for j in range(math.ceil(len(lanes) / LANES_PER_JOB))]
    print(f"TABLE: {len(lanes)} lanes, {total} items; per mode "
          + ", ".join(f"{m} {sum(len(us) for mm, us in lanes if mm == m)} in {sum(mm == m for mm, _ in lanes)} lanes" for m in MODES)
          + f"; items per lane {min(len(us) for _, us in lanes)}..{max(len(us) for _, us in lanes)}")
    print("JOBS: " + " ".join(f"{a}-{b}" for a, b in jobs))
    return 0


if __name__ == "__main__":
    sys.exit(main())

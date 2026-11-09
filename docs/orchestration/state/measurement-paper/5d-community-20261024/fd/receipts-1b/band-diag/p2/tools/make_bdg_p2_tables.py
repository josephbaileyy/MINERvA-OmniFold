"""Band diagnosis, P2's two task tables (FD-1B-BAND-DIAGNOSIS-DECLARATION.md section 7; BINDING-1 ruling 2).

tasks-p2-inputs.tsv: one line, section 4.3's inputs step (fd_1b_band_diag.py inputs), run before any unfold.
tasks-p2.tsv: eight lines, one per lane of one node, at most two items per lane, exactly section 7's 14 pilot items:
  E at seed 42, eps 1, channel both, for CV and the 8 detector universes (5 lines: 2, 2, 2, 2, 1);
  B the same for CV and the 4 GEANT_Neutron/GEANT_Proton universes (3 lines: 2, 2, 1).
Each line is "<name><TAB>fd_1b_band_diag.py<TAB><args>", run by the committed s5c_array.sh. The module's own
pilot_items(), imported from the deploy checkout, must equal the items the eight lines carry; any difference refuses.

usage: python3 make_bdg_p2_tables.py <deploy checkout> <W> <tables dir>
"""
import sys
from pathlib import Path

P = "/pscratch/sd/j/josephrb"
PINS_SHA = "5adcd576eb46f443fe4133b05044cd315c0eeb0f281e21acee5f2318b4bab248"


def main() -> int:
    deploy, W, out = Path(sys.argv[1]), sys.argv[2], Path(sys.argv[3])
    sys.path.insert(0, str(deploy / "nd-unfolding"))
    import fd_1b_band_diag as d  # noqa: E402  (the deploy's bytes; the connect gates their sha256)
    det, sub = d.detector_universes(), d.subject_universes()
    groups = [("E", u) for u in [["CV", det[0]], det[1:3], det[3:5], det[5:7], det[7:8]]]
    groups += [("B", u) for u in [["CV", sub[0]], sub[1:3], sub[3:4]]]
    carried = [(m, u, d.BASE_SEED, 1.0, "both") for m, us in groups for u in us]
    if sorted(carried) != sorted(d.pilot_items()) or len(carried) != 14:
        raise SystemExit(f"TABLE: the lines carry {carried}, not the module's pilot_items() {d.pilot_items()}")
    if len(groups) != 8 or max(len(us) for _, us in groups) > 2:
        raise SystemExit("TABLE: not eight lanes of at most two items")
    inputs = ["--npz", f"{P}/MINERvA-OmniFold/nd-unfolding/of_inputs_5d.npz",
              "--bkg", f"{P}/s5c-20260924/runs/p2/bkg_dump.npz",
              "--bank", f"{P}/MINERvA-OmniFold/nd-unfolding/bank_sweep_5d_bkgaware",
              "--detector-dir", f"{P}/s5p-20260926/bank_detector",
              "--pins", f"{P}/fd-1b-20261030/pins.json", "--expect-pins-sha256", PINS_SHA]
    head = "# band diagnosis, P2 (FD-1B-BAND-DIAGNOSIS-DECLARATION.md section 7; BINDING-1 ruling 2)"
    lines = [head, "\t".join(["fd1b_bdg_p2_inputs", "fd_1b_band_diag.py", "inputs"] + inputs
                             + ["--out", f"{W}/p2/inputs.json"])]
    (out / "tasks-p2-inputs.tsv").write_text("\n".join(lines) + "\n")
    lines = [head]
    for i, (m, us) in enumerate(groups):
        lines.append("\t".join([f"fd1b_bdg_p2_{i}_{m}", "fd_1b_band_diag.py", "unfold", "--mode", m, "--seed",
                                str(d.BASE_SEED), "--eps", "1", "--channel", "both", "--universes", ",".join(us)]
                               + inputs + ["--threads", "32", "--out", f"{W}/unf"]))
    (out / "tasks-p2.tsv").write_text("\n".join(lines) + "\n")
    print(f"TABLES: 1 inputs line; 8 unfold lines carrying the 14 pilot items: "
          + "; ".join(f"{m} {','.join(us)}" for m, us in groups))
    return 0


if __name__ == "__main__":
    sys.exit(main())

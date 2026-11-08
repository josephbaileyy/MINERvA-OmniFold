"""1B pre-check Part 1, P2's task table (FD-1B-PRECHECK-FD-DECLARATION.md section 7; Binding 1, addendum A1).

Eight lines, one per lane of one node, exactly section 7's pilot items:
  A, B and Dnom at CV; A, B and Dnom at Flux_0; A and B at MinosEfficiency_0.
Each line is "<name><TAB>fd_1b_precheck_fd.py<TAB>unfold --mode M --universes U <the bound inputs>", run by the
committed s5c_array.sh. The module's own PILOT tuple is read from its source with ast (no import) and must equal
section 7's list; any other line is refused.

usage: python3 -I make_p2_table.py <deploy checkout> <V> <out table>
"""
import ast
import sys
from pathlib import Path

SECTION7 = [("A", "CV"), ("B", "CV"), ("Dnom", "CV"), ("A", "Flux_0"), ("B", "Flux_0"), ("Dnom", "Flux_0"),
            ("A", "MinosEfficiency_0"), ("B", "MinosEfficiency_0")]
P = "/pscratch/sd/j/josephrb"


def module_pilot(module: Path) -> list:
    tree = ast.parse(module.read_text())
    for node in tree.body:
        if isinstance(node, ast.Assign) and any(getattr(t, "id", None) == "PILOT" for t in node.targets):
            return [tuple(x) for x in ast.literal_eval(node.value)]
    raise SystemExit("TABLE: no PILOT in the module")


def main() -> int:
    deploy, V, out = Path(sys.argv[1]), sys.argv[2], Path(sys.argv[3])
    pilot = module_pilot(deploy / "nd-unfolding" / "fd_1b_precheck_fd.py")
    if pilot != SECTION7:
        raise SystemExit(f"TABLE: the module's PILOT {pilot} is not section 7's list")
    common = ["--npz", f"{P}/MINERvA-OmniFold/nd-unfolding/of_inputs_5d.npz",
              "--bkg", f"{P}/s5c-20260924/runs/p2/bkg_dump.npz",
              "--bank", f"{P}/MINERvA-OmniFold/nd-unfolding/bank_sweep_5d_bkgaware",
              "--detector-dir", f"{P}/s5p-20260926/bank_detector",
              "--flux-file", f"{V}/stage/flux_universes.root",
              "--pins", f"{P}/fd-1b-20261030/pins.json",
              "--expect-pins-sha256", "5adcd576eb46f443fe4133b05044cd315c0eeb0f281e21acee5f2318b4bab248",
              "--threads", "32", "--out", f"{V}/unf"]
    lines = ["# 1B pre-check Part 1, P2 (FD-1B-PRECHECK-FD-DECLARATION.md section 7; Binding 1, addendum A1)"]
    for mode, u in SECTION7:
        lines.append("\t".join([f"fd1b_pfd_p2_{mode}_{u}", "fd_1b_precheck_fd.py", "unfold", "--mode", mode,
                                "--universes", u] + common))
    body = [l for l in lines if not l.startswith("#")]
    if len(body) != 8 or len({l.split("\t")[0] for l in body}) != 8:
        raise SystemExit("TABLE: not eight distinct lines")
    out.write_text("\n".join(lines) + "\n")
    print(f"TABLE: {len(body)} lines written to {out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

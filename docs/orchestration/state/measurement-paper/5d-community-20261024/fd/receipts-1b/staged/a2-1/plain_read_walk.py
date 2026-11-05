"""Which staged 1B entry points can reach a plain (not O_NOATIME) read of the bank, the detector dump or the inputs
(the director's request of 2026-11-05, after REF-G1's plain reads moved 419 of 1B's input atimes)?

For each entry point, fd_1b_c2.code_closure (the walk c2check pins the 300-draw calibration's code with) gives every
module-level statement it reaches by reference. The walk over-approximates: a referenced function is counted
whether or not a branch calls it. It cannot see subprocesses, getattr or strings; fd_1b_mc, fd_1b_c2 and
fd_1b_binning start no subprocess. Printed per entry point:
- whether it reaches the known plain bank readers: s5p_universe.weights (np.load at s5p_universe.py:94),
  s5p_nullexp.ModelCache, and fd_1b_toys.source_factors (which calls the first two, fd_1b_toys.py:245, :250, :259);
- every reached statement whose text holds a path-taking read (np.load, open, read_bytes, read_text, json.load,
  fromfile, memmap). Whether each one reads a protected input is decided by its call sites, listed in the record.

    python3 -B plain_read_walk.py        (from the repository root)
"""
import re
import sys
from pathlib import Path

sys.path.insert(0, "nd-unfolding")
import fd_1b_c2 as c2  # noqa: E402

PLAIN = {("s5p_universe", "weights"), ("s5p_nullexp", "ModelCache"), ("fd_1b_toys", "source_factors")}
READ = re.compile(r"np\.load\(|(?<![\w.])open\(|\.read_bytes\(|\.read_text\(|np\.fromfile|np\.memmap|json\.load\(")
ENTRIES = {"bulk unfold (run_unfold)": [("fd_1b_mc", "run_unfold")], "receipt": [("fd_1b_mc", "receipt")],
           "n1": [("fd_1b_mc", "n1_step")], "null": [("fd_1b_mc", "null_step")], "readout": [("fd_1b_mc", "readout")],
           "clipcheck": [("fd_1b_mc", "clipcheck")], "walls": [("fd_1b_mc", "pilot_walls"), ("fd_1b_mc", "walls_of")],
           "stage-flux": [("fd_1b_mc", "stage_flux")], "binning": [("fd_1b_binning", "main")],
           "c2check": [("fd_1b_c2", "c2check_main")], "c2probe": [("fd_1b_c2", "c2probe_main")],
           "calibrate": [("fd_1b_c2", "calibrate_main")]}


def load(m):
    for d in c2.CODE_DIRS:
        f = Path(d) / f"{m}.py"
        if f.is_file():
            return f"{d}/{m}.py", f.read_text()
    return None


def main() -> int:
    any_plain = False
    for name, roots in ENTRIES.items():
        es = c2.code_closure(load, roots)
        labels = {(e["module"], e["label"]) for e in es}
        hit = sorted(f"{m}.{lab}" for m, lab in PLAIN if (m, lab) in labels)
        any_plain |= bool(hit)
        reads = sorted({f"{e['module']}.{e['label']}" for e in es for line in e["text"].splitlines() if READ.search(line)})
        print(f"== {name}: {len(es)} statements; reaches the plain bank readers: {hit or 'none'}")
        print(f"   statements with a path read ({len(reads)}): {', '.join(reads)}")
    print(f"PLAIN-READ-WALK :: {'SOME ENTRY REACHES A PLAIN BANK READER' if any_plain else 'NO ENTRY REACHES A PLAIN BANK READER'}")
    return 1 if any_plain else 0


if __name__ == "__main__":
    sys.exit(main())

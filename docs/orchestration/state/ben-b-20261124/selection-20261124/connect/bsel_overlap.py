#!/usr/bin/env python3
"""The bsel read connect's overlap check (the director's instruction for #1310, 2026-11-24).

**The tool** is S2R's (`nd-unfolding/s2r/s2r_overlap.py`), unchanged: its prefix rule, and its "theirs" (IBUB's own
composition plus IBUB's 19 declared ibub-20261124 entries). That composition already holds cov2d's protected paths and
disclosed roots, rpd flux2's write roots and staged originals, limitation-resolver's paths and RPD-RECO P0 roots,
tier3's MSR reads and `msr-` roots, and the `ibuchi_` root.

**Added to "theirs" here:**
- S2R's root `s2r-20261124` and its launcher's `/dev/shm/s2rc.`. The job has ended, but they stay on record.
- RDX's protected root `rdx-20261112b`, which holds the truthx sidecar and the 12 omnifiles that RPD-RECO route (R)
  reads.

**"Ours"** is the connect's own set: the six SOURCES read once through O_NOATIME (taken from `bsel_read.sh` itself,
never retyped), and the writes `bsel-20261124` and `/dev/shm/bselc.`.

**Allowed:** nothing, since "ours" has no interpreter read. Every hit stops. Exit 0 CLEAR, 3 OVERLAP.
usage: bsel_overlap.py [--self-test]
"""
from __future__ import annotations

import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[5]
sys.path.insert(0, str(REPO / "nd-unfolding/s2r"))
import s2r_overlap as O  # noqa: E402

S2R_THEIRS = O.theirs  # S2R's own composition, captured before check() rebinds O.theirs

U = "/pscratch/sd/j/josephrb"
WRITES = [f"{U}/bsel-20261124", "/dev/shm/bselc."]
EXTRA_THEIRS = [("s2r write root (ended, on record)", f"{U}/s2r-20261124"), ("s2r write", "/dev/shm/s2rc."),
                ("rdx protected root (RPD-RECO route R)", f"{U}/rdx-20261112b")]


def sources(read_sh: Path = HERE / "bsel_read.sh") -> list[str]:
    block = read_sh.read_text().split("SOURCES='", 1)[1].split("'", 1)[0]
    out = [ln.split()[1] for ln in block.splitlines() if ln.strip()]
    if len(out) != 6:
        raise SystemExit(f"bsel_read.sh lists {len(out)} sources, not 6")
    return out


def ours(clone: Path) -> list:
    return [("read", s) for s in sources()] + [("write", p) for p in WRITES]


def theirs(clone: Path):
    th, mo, rpd = S2R_THEIRS(clone)
    return th + EXTRA_THEIRS, mo, rpd


def check(extra_ours: list | None = None) -> tuple[int, list]:
    saved = (O.ours, O.theirs)
    O.ours = lambda clone: ours(clone) + list(extra_ours or [])
    O.theirs = theirs
    try:
        rc, lines = O.check(REPO)
    finally:
        O.ours, O.theirs = saved
    lines[0] = lines[0].replace("OVERLAP s2r:", "OVERLAP bsel:") + f"; added {len(EXTRA_THEIRS)}: s2r, rdx"
    return rc, lines


def self_test() -> int:
    """CLEAR on the bound set, and a STOP for each kind of planted hit (IBUB, s2r, rdx, cov2d, a write on a read)."""
    rc, _ = check()
    assert rc == 0, "the bound set is not CLEAR"
    planted = [("write", f"{U}/ibub-20261124/x"), ("read", f"{U}/s2r-20261124/runs/B0/q3/x.npz"),
               ("write", "/dev/shm/s2rc.123.sh"), ("read", f"{U}/rdx-20261112b/out/dumps/truthx_RDX_ALL.npz"),
               ("write", f"{U}/MINERvA-OmniFold/nd-unfolding/of_inputs_5d.npz"), ("write", f"{U}/msr-p-20261122/z")]
    for p in planted:
        rc, lines = check([p])
        assert rc == 3 and any(x.startswith("OVERLAP HIT") for x in lines), f"no STOP for {p}"
    print(f"SELF-TEST PASS: CLEAR on the bound set; {len(planted)} planted hits each STOP")
    return 0


def main(argv=None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)
    if "--self-test" in argv:
        return self_test()
    rc, lines = check()
    print("\n".join(lines))
    return rc


if __name__ == "__main__":
    sys.exit(main())

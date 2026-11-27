#!/usr/bin/env python3
"""The b5d read connect's overlap check (the director's instruction for #1310, 2026-11-24).

**The tool** is S2R's (`nd-unfolding/s2r/s2r_overlap.py`), unchanged: its prefix rule, and its "theirs" (IBUB's own
composition plus IBUB's 19 declared ibub-20261124 entries). That composition already holds cov2d's protected paths and
disclosed roots, rpd flux2's write roots and staged originals, limitation-resolver's paths and RPD-RECO P0 roots,
tier3's MSR reads and `msr-` roots, and the `ibuchi_` root.

**Added to "theirs" here:**
- S2R's root `s2r-20261124` and its launcher's `/dev/shm/s2rc.`. The job has ended, but they stay on record.
- RDX's protected root `rdx-20261112b`, which holds the truthx sidecar and the 12 omnifiles that RPD-RECO route (R)
  reads.

**"Ours"** is the connect's own set: the 1,655 SOURCES read once through O_NOATIME (taken from `b5d_read.sh` itself,
never retyped), and the writes `b5d-20261124` and `/dev/shm/b5dc.`.

**Allowed:** one declared acked read: the flux constraint, read once through O_NOATIME, which cov2d protects and rpd flux2
stages. It is allowed only against those owners' entries, and their acks name it. Every other hit stops. Exit 0
CLEAR, 3 OVERLAP.
usage: b5d_overlap.py [--self-test]
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
WRITES = [f"{U}/b5d-20261124", "/dev/shm/b5dc."]
ACKED = {"/pscratch/sd/j/josephrb/MINERvA-OmniFold/MINERvA101/opt/etc/MParamFiles/data/FluxConstraints/sorted_NuEConstraint_FHC_RHC_IMD.txt"}
ACKED_OWNERS = ("cov2d", "rpd flux2")
EXTRA_THEIRS = [("s2r write root (ended, on record)", f"{U}/s2r-20261124"), ("s2r write", "/dev/shm/s2rc."),
                ("rdx protected root (RPD-RECO route R)", f"{U}/rdx-20261112b")]


def sources(read_sh: Path = HERE / "b5d_read.sh") -> list[str]:
    block = read_sh.read_text().split("SOURCES='", 1)[1].split("'", 1)[0]
    out = [ln.split()[1] for ln in block.splitlines() if ln.strip()]
    if len(out) != 1655:
        raise SystemExit(f"b5d_read.sh lists {len(out)} sources, not 1655")
    return out


def ours(clone: Path) -> list:
    return ([("read (acked: cov2d, rpd)" if s in ACKED else "read", s) for s in sources()]
            + [("write", p) for p in WRITES])


def theirs(clone: Path):
    th, mo, rpd = S2R_THEIRS(clone)
    return th + EXTRA_THEIRS, mo, rpd


def check(extra_ours: list | None = None) -> tuple[int, list]:
    """S2R's rule and composition (its prefix match, IBUB's "theirs" plus EXTRA_THEIRS), with one allowance: a declared
    acked read (ACKED) against an ACKED_OWNERS entry."""
    th, mo, rpd = theirs(REPO)
    us = ours(REPO) + list(extra_ours or [])
    over = lambda a, b: (mo.overlaps_prefix(rpd, a, b)  # noqa: E731
                         or (b.endswith(("-", ".")) and a.startswith(b)) or (a.endswith(("-", ".")) and b.startswith(a)))
    pairs = [(o, t) for o in us for t in th if over(o[1], t[1])]
    allowed = [(o, t) for o, t in pairs if o[0].startswith("read (acked") and o[1] in ACKED
               and t[0].startswith(ACKED_OWNERS)]
    hits = [x for x in pairs if x not in allowed]
    lines = [f"OVERLAP b5d: ours {len(us)}; theirs {len(th)} (IBUB's own entries: "
             f"{sum(1 for t in th if t[0].startswith('ibub '))}); added {len(EXTRA_THEIRS)}: s2r, rdx"]
    lines += [f"OURS {k} {p}" for k, p in us]
    lines += [f"OVERLAP ALLOWED: ours {ok} {op}  ~  theirs {tk} {tp}" for (ok, op), (tk, tp) in allowed]
    lines += [f"OVERLAP HIT: ours {ok} {op}  ~  theirs {tk} {tp}" for (ok, op), (tk, tp) in hits]
    lines.append(f"OVERLAP: {'CLEAR' if not hits else 'STOP'} (pairs checked {len(us) * len(th)}, hits {len(hits)})")
    return (0 if not hits else 3), lines


def self_test() -> int:
    """CLEAR on the bound set, and a STOP for each kind of planted hit (IBUB, s2r, rdx, cov2d, a write on a read)."""
    rc, _ = check()
    assert rc == 0, "the bound set is not CLEAR"
    planted = [("write", f"{U}/ibub-20261124/x"), ("read", f"{U}/s2r-20261124/runs/B0/q3/x.npz"),
               ("write", "/dev/shm/s2rc.123.sh"), ("read", f"{U}/rdx-20261112b/out/dumps/truthx_RDX_ALL.npz"),
               ("write", f"{U}/MINERvA-OmniFold/nd-unfolding/of_inputs_5d.npz"), ("write", f"{U}/msr-p-20261122/z"),
               ("write", next(iter(ACKED))), ("read (acked: cov2d, rpd)", f"{U}/ibub-20261124/y")]
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

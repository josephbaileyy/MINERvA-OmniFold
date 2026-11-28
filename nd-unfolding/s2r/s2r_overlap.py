#!/usr/bin/env python3
"""S2R's overlap check (S2R-DECLARATION.md section 5; the director's package list of 2026-11-24): this lane's reads and
writes against IBUB's declared reads and writes and against the other lanes' protected sets.

**Theirs** is IBUB's own composition (``2d-unfolding/ibub/ibub_overlap.theirs``, unchanged: cov2d's protected paths and
disclosed roots, rpd flux2's write roots and staged originals, limitation-resolver's extra paths and its P0 roots,
tier3-design's MSR reads and ``msr-`` roots, the ``ibuchi_`` root), plus IBUB's own declared set for both its phases
(``ibub_overlap.ours("run" | "readout", N_ROOT)``: its reads, its acked cov2d reads, its interpreter and its writes
under ``ibub-20261124``, ``/dev/shm/ibub-connect`` and ``/dev/shm/ibubc.``).

**Ours** is the bound job's set: every source in ``s2r_probe.sources()`` (read once through O_NOATIME by the staging and
the connect's pins check, never written), the shared interpreter, and the writes ``s2r-20261124`` and the launcher's
``/dev/shm/s2rc.``.

The rule is IBUB's (rpd's prefix rule after realpath, with MSR's staging-prefix extension, applied both ways and to
a prefix ending in '-' or '.', such as ``/dev/shm/ibubc.``). ALLOWED: the shared
read-only interpreter against another read-only interpreter, and a declared cov2d-acked read (``ACKED_ROLES``) against a
cov2d entry. Every other hit stops, including any hit on IBUB's set or involving a write. Exit 0 CLEAR, 3 OVERLAP.
usage: s2r_overlap.py [--clone DIR]
"""
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
U = "/pscratch/sd/j/josephrb"
OUT = f"{U}/s2r-20261124"
WRITES = [OUT, "/dev/shm/s2rc."]
# FD-PRR's three inputs that cov2d protects (rpd flux2's READY config): read once through O_NOATIME and never written,
# as FD-PRR and T3 read them, under cov2d's ack (asked for at this run's fence round). Named by role, never derived from
# the hits, so a new hit on any other path still stops.
ACKED_ROLES = ("of_inputs_5d", "bkg_dump", "bank_cv")


def load(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def ours(clone: Path) -> list:
    sys.path.insert(0, str(clone / "nd-unfolding/s2r"))
    import s2r_probe as SP
    ib = load(clone / "2d-unfolding/ibub/ibub_overlap.py", "ibub_overlap")
    return ([("read (cov2d-acked)" if e["role"] in ACKED_ROLES else "read", e["src"]) for e in SP.sources(clone)]
            + [("read (interpreter)", ib.INTERPRETER)]
            + [("write", p) for p in WRITES])


def theirs(clone: Path):
    ib = load(clone / "2d-unfolding/ibub/ibub_overlap.py", "ibub_overlap")
    th, mo, rpd = ib.theirs(clone)
    for phase in ("run", "readout"):
        for kind, p in ib.ours(phase, ib.N_ROOT):
            th.append((f"ibub {phase} {kind}", p))
    return th, mo, rpd


def check(clone: Path) -> tuple[int, list]:
    th, mo, rpd = theirs(clone)
    us = ours(clone)
    over = lambda a, b: (mo.overlaps_prefix(rpd, a, b)  # noqa: E731
                         or (b.endswith(("-", ".")) and a.startswith(b)) or (a.endswith(("-", ".")) and b.startswith(a)))
    pairs = [(o, t) for o in us for t in th if over(o[1], t[1])]
    allowed = [(o, t) for o, t in pairs
               if (o[0] == "read (interpreter)" and t[0].endswith("(interpreter)"))
               or (o[0] == "read (cov2d-acked)" and t[0].startswith("cov2d"))]
    hits = [x for x in pairs if x not in allowed]
    lines = [f"OVERLAP s2r: ours {len(us)}; theirs {len(th)} (IBUB's own entries: "
             f"{sum(1 for t in th if t[0].startswith('ibub '))})"]
    lines += [f"OURS {k} {p}" for k, p in us]
    lines += [f"OVERLAP ALLOWED: ours {ok} {op}  ~  theirs {tk} {tp}" for (ok, op), (tk, tp) in allowed]
    lines += [f"OVERLAP HIT: ours {ok} {op}  ~  theirs {tk} {tp}" for (ok, op), (tk, tp) in hits]
    lines.append(f"OVERLAP: {'CLEAR' if not hits else 'STOP'} (pairs checked {len(us) * len(th)}, hits {len(hits)})")
    return (0 if not hits else 3), lines


def main(argv=None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)
    clone = Path(argv[argv.index("--clone") + 1]) if "--clone" in argv else REPO
    rc, lines = check(clone)
    print("\n".join(lines))
    return rc


if __name__ == "__main__":
    sys.exit(main())

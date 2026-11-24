#!/usr/bin/env python3
"""IBUB's overlap check (IBUB-DECLARATION.md section 8, the director's step 5): this lane's reads and writes against
the other lanes' protected sets. It runs before the staging and submission connect (phase ``run``) and before the
readout connect (phase ``readout``).

**Theirs** is MSR's composition, imported unchanged from ``nd-unfolding/msr/msr_overlap.py`` and the rpd flux2 fence
tool it loads:
- cov2d's 36 protected paths (rpd flux2's READY config) and its 12 disclosed roots;
- rpd flux2's write roots and staged originals;
- limitation-resolver's extra paths.

To those it adds:
- tier3-design's MSR reads (``msr_overlap.READS``), with its write roots ``msr-*`` and ``/dev/shm/msr-connect``;
- the ``ibuchi_`` root of Joseph's session (the director's FYI of 2026-11-23);
- limitation-resolver's P0 (RPD-RECO): its write roots and its flux3 reads (its ack of 2026-11-24).

**Ours** is the declared set for the phase. IBUB reads cov2d's own files by design: the toys' data files, `$K2A`, the
CV omnifile's CFS original and, in the readout, the OmniFold toy outputs, the truths and E_R. Each of those is read
once through O_NOATIME and never written, under cov2d's ack.
- A hit between one of those declared reads ("read (cov2d-acked)") and a cov2d entry is ALLOWED and printed.
- The shared read-only interpreter is ALLOWED against another read-only interpreter, as MSR allows it.
- Every other hit stops. That includes any hit involving a write, and any hit of an acked read on a non-cov2d entry.

Paths overlap when they are equal or one lies under the other, as written and after realpath. This is rpd's rule,
imported, with MSR's staging-prefix extension. Exit 0 CLEAR, 3 OVERLAP, 2 usage or inputs.

usage: ibub_overlap.py PHASE OUT_ROOT [--clone DIR]     (PHASE run | readout; OUT_ROOT this lane's $N)
"""
from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
U = "/pscratch/sd/j/josephrb"
O = f"{U}/cov2d-run-20261104"
N_ROOT = f"{U}/ibub-20261123"
INTERPRETER = "/global/homes/j/josephrb/.conda/envs/root_6_28"
CONFIG = json.loads((HERE / "config.json").read_text())

ACKED_RUN = [  # cov2d's files the staging, preflight and job read (O_NOATIME, never written)
    f"{O}/pseudo/G18/b", f"{O}/pseudo/AR23-a2/b", CONFIG["refs"]["k2a"]["path"], CONFIG["inputs"]["CV_source"],
]
READS_RUN = [  # other reads (O_NOATIME): the MC flux file's CFS copy, the RooUnfold library, C-REP's reference
    CONFIG["inputs"]["MC_source"], CONFIG["inputs"]["lib_source"], CONFIG["refs"]["c2_central"]["path"],
]
ACKED_READOUT = [  # the readout's reads of cov2d's files (through cov2d_readout.Run's O_NOATIME copies)
    f"{O}/out", f"{O}/pseudo/G18/b/truth_xsec.npz", f"{O}/pseudo/AR23-a2/b/truth_xsec.npz",
    f"{U}/2d-closeout-re2-20261023/partb/out/ER/xsec.root",
]
READS_READOUT: list = []
WRITES = {"run": [N_ROOT, "/dev/shm/ibub-connect", "/dev/shm/ibubc."],
          # the readout writes only under config.json's readout.write_root (/dev/shm/ibub-connect), which
          # ibub_readout.guard_in_root enforces; the readout connect then publishes the products into $N
          "readout": [N_ROOT, CONFIG["readout"]["write_root"], "/dev/shm/ibubc."]}
IBUCHI = [("ibuchi write root", f"{U}/ibuchi-evloop-20261123")]
LR_P0 = [  # limitation-resolver's ack of 2026-11-24: P0 (RPD-RECO), a login-only connect that may run in this lane's window
    ("rpd-reco P0 write root", f"{U}/rpd-reco-p0-20261123"),
    ("rpd-reco P0 write (login node)", "/dev/shm/limres-rpd-flux1"),
    ("rpd-reco P0 read (flux3 products)", f"{U}/rpd-reco-flux3-20261123/run"),
]


def load(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def theirs(clone: Path) -> list:
    mo = load(clone / "nd-unfolding/msr/msr_overlap.py", "msr_overlap")
    rpd = mo.load_rpd_tool(clone)
    cfg = json.loads((clone / mo.FLUX2 / "production-config.ready.json").read_text())
    out = [("cov2d protected (flux2 config)", p) for p in cfg["cov2d_protected_paths"]]
    out += [("cov2d disclosed root", f"{mo.U}/{r}") for r in mo.COV2D_DISCLOSED]
    out += [("rpd flux2 write root", r) for r in rpd.WRITE_ROOTS]
    out += [(f"rpd flux2 staged original ({k})", p) for k, p in rpd.staged_originals(cfg, clone)]
    out += list(mo.LR_EXTRA)
    out += [("tier3 msr read", p) for p in mo.READS]
    out += [("tier3 msr write root", f"{U}/msr-"), ("tier3 msr write", "/dev/shm/msr-connect")]
    out += IBUCHI + LR_P0
    return out, mo, rpd


def ours(phase: str, out_root: str) -> list:
    if phase == "run":
        acked, reads = ACKED_RUN, READS_RUN
    elif phase == "readout":
        acked, reads = ACKED_READOUT, READS_READOUT
    else:
        raise ValueError(f"unknown phase {phase!r}")
    writes = [out_root if p == N_ROOT else p for p in WRITES[phase]]
    return ([("read (cov2d-acked)", p) for p in acked] + [("read", p) for p in reads]
            + [("read (interpreter)", INTERPRETER)] + [("write", p) for p in writes])


def check(phase: str, out_root: str, clone: Path) -> tuple[int, list]:
    lines = []
    th, mo, rpd = theirs(clone)
    us = ours(phase, out_root)
    over = lambda a, b: mo.overlaps_prefix(rpd, a, b) or (b.endswith("-") and a.startswith(b))   # noqa: E731
    pairs = [(o, t) for o in us for t in th if over(o[1], t[1])]
    allowed = [(o, t) for o, t in pairs
               if (o[0] == "read (interpreter)" and t[0].endswith("(interpreter)"))
               or (o[0] == "read (cov2d-acked)" and t[0].startswith("cov2d"))]
    hits = [x for x in pairs if x not in allowed]
    lines.append(f"OVERLAP {phase}: ours {len(us)}; theirs {len(th)}")
    lines += [f"OVERLAP ALLOWED: ours {ok} {op}  ~  theirs {tk} {tp}" for (ok, op), (tk, tp) in allowed]
    lines += [f"OVERLAP HIT: ours {ok} {op}  ~  theirs {tk} {tp}" for (ok, op), (tk, tp) in hits]
    lines.append(f"OVERLAP: {'CLEAR' if not hits else 'STOP'} (pairs checked {len(us) * len(th)}, hits {len(hits)})")
    return (0 if not hits else 3), lines


def main(argv=None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)
    if len(argv) < 2 or argv[0] not in ("run", "readout"):
        print(__doc__)
        return 2
    phase, out_root = argv[0], argv[1]
    clone = Path(argv[argv.index("--clone") + 1]) if "--clone" in argv else REPO
    if out_root != N_ROOT:
        print(f"OVERLAP REFUSED: OUT_ROOT {out_root} is not this lane's {N_ROOT}")
        return 2
    rc, lines = check(phase, out_root, clone)
    print("\n".join(lines))
    return rc


if __name__ == "__main__":
    sys.exit(main())

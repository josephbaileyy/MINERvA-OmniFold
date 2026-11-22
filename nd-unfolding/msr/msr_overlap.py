#!/usr/bin/env python3
"""MSR connect P's overlap check (the director's ruling, 2026-11-22): this study's reads and writes against
(a) cov2d's protected paths: the 36 `cov2d_protected_paths` of rpd's flux2 READY config plus the 12 finished cov2d/t2a
    roots cov2d disclosed (flux2 README "cov2d's acknowledgement" item 1), treated as protected for a read overlap; and
(b) limitation-resolver's rpd flux2 run: its two write roots and the originals its custody prepare stages, enumerated
    by its own fence tool's `staged_originals` (imported unchanged from this checkout).
Two paths overlap when equal or one lies under the other, as written and after os.path.realpath (rpd's rule, imported).
Every pair is checked in both directions: ours against each of theirs. Exit 0 CLEAR, 3 OVERLAP, 2 usage or inputs.

usage: msr_overlap.py OUT_ROOT [--clone DIR]     (OUT_ROOT: this connect's fresh $OUT on pscratch)
"""
from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
FLUX2 = "docs/orchestration/state/measurement-paper/5d-community-20261024/fd/rpd-reco/flux2-20261122"
U = "/pscratch/sd/j/josephrb"
T3 = f"{U}/t3p-20261121"

# this study's declared set (DECLARATION.md section 2; reads are O_NOATIME, the rest is our own $OUT and /dev/shm copy)
READS = [
    f"{T3}/stage/of_inputs_5d.npz", f"{T3}/stage/bkg_dump.npz", f"{T3}/stage/fd-prr/runs/B0/nominal",
    f"{T3}/runs", f"{T3}/log-floor/SHA256SUMS", f"{T3}/stage.json",
    f"{U}/ibukt-20261119-d",
    f"{U}/methods-paper/re1-20261022/out/3d/of_inputs_3d.npz", f"{U}/methods-paper/re1-20261022/out/4d/of_inputs_4d.npz",
]
COV2D_DISCLOSED = [  # flux2 README, "cov2d's acknowledgement" item 1 (cov2d, 2026-11-22T22:05:53Z)
    "cov2d-deploy-cb31611c", "cov2d-deploy-a6054769", "cov2d-deploy-cf533377", "cov2d-crossterms-20261107", "cov2d-e3",
    "cov2d-2a", "cov2d-mumax-20261116", "cov2d-clip-20261103", "cov2d-clip2-20261103", "cov2d-receipt-20261102",
    "cov2d-stage-20261104.sh", "t2a-20261110",
]


def load_rpd_tool(clone: Path):
    path = clone / FLUX2 / "tools/fence_overlap.py"
    spec = importlib.util.spec_from_file_location("rpd_fence_overlap", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def main(argv=None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)
    if not argv:
        print(__doc__)
        return 2
    out_root = argv[0]
    clone = Path(argv[argv.index("--clone") + 1]) if "--clone" in argv else REPO
    if not out_root.startswith(f"{U}/msr-"):
        print(f"OVERLAP REFUSED: OUT_ROOT {out_root} is not a fresh {U}/msr-* root")
        return 2
    writes = [out_root, "/dev/shm/msr-connect"]
    rpd = load_rpd_tool(clone)
    config = json.loads((clone / FLUX2 / "production-config.ready.json").read_text())
    theirs: list[tuple[str, str]] = []
    theirs += [("cov2d protected (flux2 config)", p) for p in config["cov2d_protected_paths"]]
    theirs += [("cov2d disclosed root", f"{U}/{r}") for r in COV2D_DISCLOSED]
    theirs += [("rpd flux2 write root", r) for r in rpd.WRITE_ROOTS]
    staged = rpd.staged_originals(config, clone)
    theirs += [(f"rpd flux2 staged original ({k})", p) for k, p in staged]
    ours = [("read", p) for p in READS] + [("write", p) for p in writes]
    print(f"OVERLAP ours {len(ours)} (reads {len(READS)}, writes {len(writes)}); theirs {len(theirs)} "
          f"(cov2d config {len(config['cov2d_protected_paths'])}, cov2d disclosed {len(COV2D_DISCLOSED)}, "
          f"rpd write roots {len(rpd.WRITE_ROOTS)}, rpd staged originals {len(staged)})")
    hits = [(o, t) for o in ours for t in theirs if rpd.overlaps(o[1], t[1])]
    for (ok, op), (tk, tp) in hits:
        print(f"OVERLAP HIT: ours {ok} {op}  ~  theirs {tk} {tp}")
    print(f"OVERLAP: {'CLEAR' if not hits else 'STOP'} (pairs checked {len(ours) * len(theirs)}, hits {len(hits)})")
    return 0 if not hits else 3


if __name__ == "__main__":
    sys.exit(main())

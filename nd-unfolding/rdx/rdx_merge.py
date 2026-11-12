#!/usr/bin/env python3
"""RDX stage 2's merge and C-ALIGN-ALL (RDX-DECLARATION.md §3), as FD-CT-5B's ALL lane merged and checked MP-1's zero
loops (fd_ct_period_inputs.py merge/check), on RDX's own loops.

    rdx_merge.py merge --loops-dir <OUT>/evloop --sums <OUT>/loops.sha256 --flux <deploy>/<FLUX_REL>/runEventLoopMC_ALL.root
                       --out <OUT>/merged/runEventLoopOmniFold_RDX_ALL.root
    rdx_merge.py k1 --lat-npz ... --lat-bkg ... --mp1-lat-npz <lat_zero.npz> --mp1-lat-bkg <lat_zero_bkg.npz> --out k1.json

merge: the twelve RDX loops in production order (1A ... 1P), each required to be at the sha256 the stage-2 checks
wrote into --sums, merged by 2d-unfolding/uq/hadd_universes_full.py as MP-1 and 5B merged; it refuses (exit 5, the
merge removed) unless the merge's data POT is the ALL flux file's DataPOTUsedForFluxWeighting, and the flux file is
5B's pinned one. fd_ct_period_inputs.py merge cannot be used: it requires MP-1's zero loops by digest.
k1 (C-ALIGN-ALL): key by key, with fd_ct_period_inputs.compare, the lateral npz against MP-1's lat_zero.npz (NPZ_KEYS)
and its background dump against lat_zero_bkg.npz (BKG_KEYS), MP-1's files at their pinned digests. PASS needs every key
equal and the key sets equal; whether the bytes are equal is recorded, not gated. Exit 0 PASS, 1 FAIL, 2 refused.
"""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import time
from pathlib import Path

_HERE = Path(__file__).resolve().parent
_ND = _HERE.parent
for _p in (str(_ND), str(_HERE)):
    if _p not in sys.path:
        sys.path.insert(0, _p)
import fd_ct_period_inputs as CT  # noqa: E402
import rdx_common as C  # noqa: E402

PLAYLISTS = CT.PERIODS["ALL"]
LOOP = "runEventLoopOmniFold_RDX_{}.root"


class Refuse(SystemExit):
    def __init__(self, code: int, why: str):
        print(f"[rdx_merge] REFUSE ({code}): {why}", file=sys.stderr)
        super().__init__(code)


def read_sums(path: Path) -> dict:
    out = {}
    for ln in Path(path).read_text().splitlines():
        if not ln.strip():
            continue
        sha, name = ln.split(None, 1)
        out[name.strip().lstrip("./")] = sha
    want = {LOOP.format(pl) for pl in PLAYLISTS}
    if set(out) != want:
        raise Refuse(2, f"--sums must list exactly the twelve RDX loops, not {sorted(out)}")
    return out


def run_merge(a) -> int:
    receipt = a.out.with_name(a.out.name + ".json")
    partial = a.out.with_name(a.out.name + ".partial")
    for p in (a.out, receipt, partial):
        if p.exists():
            raise Refuse(2, f"refusing to overwrite {p}")
    sums = read_sums(a.sums)
    t0 = time.time()
    inputs = []
    for pl in PLAYLISTS:
        p = a.loops_dir / LOOP.format(pl)
        got = C.sha256(p)
        if got != sums[p.name]:
            raise Refuse(2, f"{p} is sha256 {got}, not the checked {sums[p.name]}")
        inputs.append({"playlist": pl, "path": str(p), "sha256": got})
    if C.sha256(a.flux) != CT.FLUX["ALL"]:
        raise Refuse(2, f"{a.flux} is not 5B's pinned ALL flux file")
    a.out.parent.mkdir(parents=True, exist_ok=True)
    cmd = [sys.executable, str(CT.DEPLOY / "2d-unfolding/uq/hadd_universes_full.py"), str(partial),
           *[i["path"] for i in inputs]]
    rc = subprocess.run(cmd).returncode
    if rc != 0 or not partial.is_file():
        partial.unlink(missing_ok=True)
        raise Refuse(6, f"hadd_universes_full.py exited {rc}")
    m_pot, f_pot = CT.merged_data_pot(partial), CT.flux_data_pot(a.flux)
    pot_rel = f_pot / m_pot - 1.0
    if abs(pot_rel) > CT.POT_REL:
        partial.unlink()
        raise Refuse(5, f"the merge's dataPOTUsed is not the flux file's DataPOTUsedForFluxWeighting ({pot_rel:.3e})")
    partial.replace(a.out)
    os.chmod(a.out, 0o440)
    rec = {"schema": "rdx-merge/1", "playlists": list(PLAYLISTS), "inputs": inputs,
           "flux": [str(a.flux), CT.FLUX["ALL"]], "flux_weighting_over_merge_data_pot_minus_1": pot_rel,
           "out": str(a.out), "out_sha256": C.sha256(a.out), "seconds": round(time.time() - t0, 1),
           "code_sha256": {"rdx_merge.py": C.sha256(Path(__file__).resolve()),
                           "fd_ct_period_inputs.py": C.sha256(Path(CT.__file__).resolve())}}
    receipt.write_text(json.dumps(rec, indent=1) + "\n")
    print(json.dumps({"merged": str(a.out), "sha256": rec["out_sha256"]}), flush=True)
    return 0


def k1(lat_npz: Path, lat_bkg: Path, mp1_npz: Path, mp1_bkg: Path, compare=CT.compare) -> dict:
    if C.sha256(mp1_npz) != CT.MP1_ZERO["lat_npz"] or C.sha256(mp1_bkg) != CT.MP1_ZERO["lat_bkg"]:
        raise Refuse(2, "MP-1's lat_zero files are not at their pinned digests")
    npz = compare(lat_npz, mp1_npz, CT.NPZ_KEYS)
    bkg = compare(lat_bkg, mp1_bkg, CT.BKG_KEYS)
    failed = sorted([f"npz:{k}" for k, v in npz.items() if not v] + [f"bkg:{k}" for k, v in bkg.items() if not v])
    return {"schema": "rdx-k1/1", "lat_npz": str(lat_npz), "lat_bkg": str(lat_bkg),
            "npz_keys": npz, "bkg_keys": bkg, "failed_keys": failed,
            "lat_npz_bytes_equal": C.sha256(lat_npz) == CT.MP1_ZERO["lat_npz"],
            "verdict": "PASS" if not failed else "FAIL"}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    m = sub.add_parser("merge")
    m.add_argument("--loops-dir", type=Path, required=True)
    m.add_argument("--sums", type=Path, required=True)
    m.add_argument("--flux", type=Path, required=True)
    m.add_argument("--out", type=Path, required=True)
    k = sub.add_parser("k1")
    for f in ("lat-npz", "lat-bkg", "mp1-lat-npz", "mp1-lat-bkg", "out"):
        k.add_argument(f"--{f}", type=Path, required=True)
    a = ap.parse_args(argv)
    if a.cmd == "merge":
        return run_merge(a)
    if a.out.exists():
        raise Refuse(2, f"refusing to overwrite {a.out}")
    rec = k1(a.lat_npz, a.lat_bkg, a.mp1_lat_npz, a.mp1_lat_bkg)
    a.out.write_text(json.dumps(rec, indent=1) + "\n")
    print(json.dumps({"k1": rec["verdict"], "failed_keys": rec["failed_keys"]}))
    return 0 if rec["verdict"] == "PASS" else 1


if __name__ == "__main__":
    sys.exit(main())

#!/usr/bin/env python3
"""Read the CONSTRUCTION-CONTRACT stamps off the 5D GBDT covariance products and commit them.

Why this exists (BEN-101). The stamps that prove the 2026-07-12 quarantine's corrected contract are
already written by the production code -- `unified_throw_cov.py:479-484` writes
`fixed_seed_null_norm`, `joint_mean_shift_norm`, `n_throws` and `hJointMeanShift`; `:255,286,303`
stamp `flux_normalized` on throw/block slabs; `do_throws`/`do_blockunits` stamp `seed` and
`do_combine` rejects mixed-seed slabs at `:330-331,370-371`. But `*.root` and `*.npz` are
`.gitignore`d, and the committed evidence is two summary text files carrying MAGNITUDES ONLY -- no
seed, no null norm, no centering convention, no endpoint inventory. So the claim "built under the
corrected contract" is currently unfalsifiable from the repository. This reads the existing stamps
and writes one committed JSON.

RECORDING ABSENCE IS THE POINT, not an afterthought. Every key is reported as either
{"present": true, "value": ...} or {"present": false} -- never omitted. A receipt listing only the
keys it found cannot distinguish "the key is not there" from "nobody looked", which is the defect
this receipt exists to close, one level up. It is also cause 4's live trap: `unified_throw_cov.py`
writes `fixed_seed_null_norm` ONLY when `--null` was passed, so a criterion phrased as "the null
norm is not large" passes vacuously on a product that has no such key.

THIS ADOPTS NOTHING AND RECOMPUTES NOTHING. Every file is opened read-only; the only write is the
output JSON. No covariance is rebuilt, no ROOT is modified, and no value here becomes quotable.

Usage (on Perlmutter, inside the ROOT env):
    source setup_salloc_env.sh
    python3 receipt_construction_contract_5d.py --out uq_5d/receipt_construction_contract_5d.json
"""
from __future__ import annotations

import argparse
import glob
import hashlib
import json
import os
import re
import subprocess
import sys
import time

# Keys we LOOK FOR in every throw/adopted ROOT. Absence of any of these is recorded explicitly.
# Sourced from unified_throw_cov.py:479-484 and adopt_unified_5d.py:166-167.
THROW_PARAMS = [
    "sqrt_tr_unified",
    "sqrt_tr_block",
    "joint_mean_shift_norm",
    "fixed_seed_null_norm",   # written ONLY under --null; absence is the cause-4 trap
    "n_throws",
]
ADOPT_PARAMS = ["sqrt_tr_old", "sqrt_tr_new"]
# Objects (not TParameters) whose mere presence is contract evidence: the mean shift being stored
# SEPARATELY rather than folded into the variance is what discharges cause 2's construction.
THROW_OBJECTS = ["C_unified", "C_blocksum", "C_cross", "hJointMeanShift"]

# Hashing a 41 GB ROOT costs minutes of Lustre read for no extra evidence, so it is skipped BY A
# STATED CUT rather than silently. See "hash_skipped_reason" in the output.
HASH_MAX_BYTES = 4 * 1024**3


def sha256_file(path: str) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(8 * 1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def stat_block(path: str) -> dict:
    if not os.path.exists(path):
        return {"path": path, "exists": False}
    st = os.stat(path)
    out = {
        "path": path,
        "exists": True,
        "size_bytes": st.st_size,
        "mtime_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(st.st_mtime)),
    }
    if st.st_size <= HASH_MAX_BYTES:
        out["sha256"] = sha256_file(path)
    else:
        out["sha256"] = None
        out["hash_skipped_reason"] = (
            f"size {st.st_size} > {HASH_MAX_BYTES} byte cut; hashing adds no contract evidence "
            "and costs minutes of Lustre read. Stated cut, not a silent omission."
        )
    return out


def read_root_stamps(path: str, params: list[str], objects: list[str]) -> dict:
    """Open a ROOT read-only and report every requested key as present-with-value or absent."""
    import ROOT

    ROOT.gErrorIgnoreLevel = ROOT.kError
    block = stat_block(path)
    if not block["exists"]:
        block["read"] = False
        block["read_error"] = "file does not exist"
        return block
    f = ROOT.TFile.Open(path, "READ")
    if not f or f.IsZombie():
        block["read"] = False
        block["read_error"] = "TFile.Open failed or zombie"
        return block
    block["read"] = True
    found = {}
    for name in params:
        obj = f.Get(name)
        if not obj:
            found[name] = {"present": False}
            continue
        try:
            found[name] = {"present": True, "value": obj.GetVal()}
        except AttributeError:
            found[name] = {"present": True, "value": None,
                           "note": f"present but not a TParameter: {type(obj).__name__}"}
    block["parameters"] = found
    objs = {}
    for name in objects:
        obj = f.Get(name)
        if not obj:
            objs[name] = {"present": False}
        else:
            entry = {"present": True, "class": type(obj).__name__}
            try:
                entry["nbinsx"] = obj.GetNbinsX()
            except AttributeError:
                pass
            objs[name] = entry
    block["objects"] = objs
    block["all_keys"] = sorted({k.GetName() for k in f.GetListOfKeys()})
    f.Close()
    return block


def slab_census(pattern: str) -> dict:
    """Per-slab seed / flux_normalized / throw-id census. numpy only, no ROOT."""
    import numpy as np

    paths = sorted(glob.glob(pattern))
    per_slab, seeds, throws_seen = [], {}, set()
    stamped, unstamped, unreadable = [], [], []
    for p in paths:
        base = os.path.basename(p)
        idx_m = re.search(r"_(\d+)\.npz$", base)
        entry = {"file": base, "slab_index": int(idx_m.group(1)) if idx_m else None}
        try:
            with np.load(p, allow_pickle=True) as d:
                files = list(d.files)
                if "seed" in files:
                    s = int(np.asarray(d["seed"]).ravel()[0])
                    entry["seed"] = {"present": True, "value": s}
                    seeds[s] = seeds.get(s, 0) + 1
                else:
                    entry["seed"] = {"present": False}
                if "flux_normalized" in files:
                    v = int(np.asarray(d["flux_normalized"]).ravel()[0])
                    entry["flux_normalized"] = {"present": True, "value": v}
                    (stamped if v == 1 else unstamped).append(entry["slab_index"])
                else:
                    entry["flux_normalized"] = {"present": False}
                    unstamped.append(entry["slab_index"])
                if "throws" in files:
                    t = sorted(int(x) for x in np.atleast_1d(d["throws"]).ravel())
                    entry["throws"] = t
                    throws_seen |= set(t)
                else:
                    entry["throws"] = None
                entry["npz_keys"] = sorted(files)
        except Exception as exc:  # noqa: BLE001 -- an unreadable slab is data, not a crash
            entry["read_error"] = f"{type(exc).__name__}: {exc}"
            unreadable.append(base)
        per_slab.append(entry)

    summary = {
        "pattern": pattern,
        "n_files": len(paths),
        "seed_histogram": {str(k): v for k, v in sorted(seeds.items())},
        "single_seed": len(seeds) == 1,
        "seed_value": next(iter(seeds)) if len(seeds) == 1 else None,
        "flux_normalized_stamped_slabs": sorted(i for i in stamped if i is not None),
        "flux_normalized_unstamped_slabs": sorted(i for i in unstamped if i is not None),
        "unreadable_files": unreadable,
        "n_throws_union": len(throws_seen),
        "throws_min": min(throws_seen) if throws_seen else None,
        "throws_max": max(throws_seen) if throws_seen else None,
        "throws_contiguous_from_zero": (
            bool(throws_seen) and sorted(throws_seen) == list(range(len(throws_seen)))
        ),
        "per_slab": per_slab,
    }
    return summary


def git_rev(repo: str) -> dict:
    def run(argv):
        try:
            return subprocess.run(argv, cwd=repo, capture_output=True, text=True,
                                  check=False).stdout.strip()
        except Exception:  # noqa: BLE001
            return None
    return {"head": run(["git", "rev-parse", "HEAD"]),
            "dirty": bool(run(["git", "status", "--porcelain"]))}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo", default="/pscratch/sd/j/josephrb/MINERvA-OmniFold")
    ap.add_argument("--out", default="uq_5d/receipt_construction_contract_5d.json")
    args = ap.parse_args()

    nd = os.path.join(args.repo, "nd-unfolding")
    os.chdir(nd)

    # The two throw ROOTs and the four adopted products, each labelled by WHICH note value it feeds
    # -- so a reader can tell at a glance which contract belongs to which quoted number.
    throw_roots = {
        "pre_j28_throw": {
            "path": "uq_5d/unified_throw_cov_5d.root",
            "feeds": "values.tex \\gbdtFiveAdoptTrace 5.81e-38 / \\gbdtFiveCVTrace 6.24e-38 "
                     "(via the bkgaware adopt)",
        },
        "j28_corrected_throw": {
            "path": "uq_5d/unified_throw_cov_5d_fluxfix_20260806_full160.root",
            "feeds": "the proposed replacements 5.2600e-38 / 5.6609e-38",
        },
    }
    adopted = {
        "bkgaware_blocksum": {
            "path": "uq_5d/universe_stage2_5d_bkgaware/"
                    "uq_universe_5d_covariance_combined_bkgaware.root",
            "feeds": "\\gbdtFiveBlockMedian 13.36 (= median rel 13.359%)",
        },
        "bkgaware_adopted_meancentered": {
            "path": "uq_5d/universe_stage2_5d_bkgaware/"
                    "uq_universe_5d_covariance_combined_bkgaware_uthrow.root",
            "feeds": "\\gbdtFiveAdoptTrace 5.81e-38",
        },
        "bkgaware_adopted_cvcentered": {
            "path": "uq_5d/universe_stage2_5d_bkgaware/"
                    "uq_universe_5d_covariance_combined_bkgaware_uthrow_cvcentered.root",
            "feeds": "\\gbdtFiveCVTrace 6.24e-38",
        },
        "j28_adopted_meancentered": {
            "path": "uq_5d/rescaled_20260806_full160/adopted_meancentered_20260806_full160.root",
            "feeds": "the proposed replacement 5.2600e-38",
        },
        "j28_adopted_cvcentered": {
            "path": "uq_5d/rescaled_20260806_full160/adopted_cvcentered_20260806_full160.root",
            "feeds": "the proposed replacement 5.6609e-38",
        },
        "july_nonbkgaware_adopted": {
            "path": "uq_5d/universe_stage2_5d/uq_universe_5d_covariance_combined_uthrow.root",
            "feeds": "the superseded 5.80e-38 (pre-bkgaware); read as the footing control",
        },
    }

    receipt = {
        "schema": "construction-contract-receipt/1",
        "written_at_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "purpose": (
            "Provenance leg of quarantine causes 1-4 for the 5D GBDT covariance. Reads existing "
            "stamps; adopts nothing, recomputes nothing, makes no value quotable."
        ),
        "criteria": "docs/orchestration/CRITERIA-20260811-quarantine-causes-1-2-3-4-6.md",
        "predeclaration": "docs/orchestration/PREDECLARE-20260811-construction-contract-receipt.md",
        "git": git_rev(args.repo),
        "keys_looked_for": {
            "throw_root_parameters": THROW_PARAMS,
            "adopted_root_parameters": ADOPT_PARAMS,
            "throw_root_objects": THROW_OBJECTS,
            "note": (
                "Every key above is reported present-with-value or {'present': false}. Absence is "
                "never omitted -- that distinction is the receipt's whole function."
            ),
        },
        "throw_roots": {},
        "adopted_roots": {},
        "slab_census": {},
    }

    for label, meta in throw_roots.items():
        block = read_root_stamps(meta["path"], THROW_PARAMS, THROW_OBJECTS)
        block["feeds"] = meta["feeds"]
        receipt["throw_roots"][label] = block
        print(f"[receipt] throw {label}: read={block.get('read')} "
              f"null_present={block.get('parameters', {}).get('fixed_seed_null_norm', {}).get('present')}",
              flush=True)

    for label, meta in adopted.items():
        block = read_root_stamps(meta["path"], ADOPT_PARAMS + THROW_PARAMS, [])
        block["feeds"] = meta["feeds"]
        receipt["adopted_roots"][label] = block
        print(f"[receipt] adopted {label}: read={block.get('read')}", flush=True)

    for label, pattern in {
        "throw_slabs_sb": "uq_5d/uthrow_slabs_5d_sb/uthrow5d_slab_*.npz",
        "block_slabs_sb": "uq_5d/block_slabs_5d_sb/block5d_*.npz",
        "j28_union_rescaled_half": "uq_5d/rescaled_20260806_full160/uthrow5d_slab_*.npz",
    }.items():
        cen = slab_census(pattern)
        receipt["slab_census"][label] = cen
        print(f"[receipt] slabs {label}: n={cen['n_files']} single_seed={cen['single_seed']} "
              f"seed={cen['seed_value']} throws_union={cen['n_throws_union']}", flush=True)

    os.makedirs(os.path.dirname(args.out) or ".", exist_ok=True)
    tmp = args.out + ".tmp"
    with open(tmp, "w") as fh:
        json.dump(receipt, fh, indent=2, sort_keys=True)
        fh.write("\n")
    os.replace(tmp, args.out)   # write-to-temp + rename, per the resume-guard rule (BEN-023)
    print(f"[receipt] wrote {args.out}", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())

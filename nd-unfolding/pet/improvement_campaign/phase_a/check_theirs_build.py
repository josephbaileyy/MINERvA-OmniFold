"""Runtime check of the three declared differences in his complete-arm inputs (task A1).

`build_theirs_inputs.DECLARED_DIFFERENCES` (68cf9d29) names three places where the built inputs
differ from Gregor's source: muon presence from `MasterAnaDev_muon_E > 0` instead of his MINOS
match, `prong_dEdXMean` substituted for `prong_part_dEdXMean`, and a locally defined proportional
token-cap split. This checks, on ONE simulation shard, that they are what RAN and whether they
can be resolved:

1. The builder that produced the executed shards (`/pscratch/sd/j/josephrb/build_theirs_inputs.py`,
   per `sbatch_build_inputs.sh`) is compared by git blob to the historical commit's file.
2. The historical builder (imported from the pinned checkout, unmodified) is re-run on the first
   `--limit` rows of the slim file and compared array-for-array with the executed shard. Equality
   means the executed tokens ARE this code's output, declared differences included.
3. Muon presence: per event, "the executed shard holds a muon token" against
   `MasterAnaDev_muon_E > 0` read from the slim.
4. Cap split: per event, category multiplicities from the slim against the token categories in
   the executed shard -- how often the cap binds and what the split kept.
5. Resolvability: the slim's branch list (the R4 extraction) and the ORIGINAL simulation
   AnaTuple's branch list, searched for a MINOS-match flag and `prong_part_dEdXMean`.

Simulation only: the shard, slim and AnaTuple are MC (playlist 1A, run 00110000).
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import re
import sys
from pathlib import Path
from typing import Any

MC_FIELDS = ("mc_run", "mc_subrun", "mc_nthEvtInFile")
BUILDER_RELPATH = "nd-unfolding/pet/configuration_comparison/build_theirs_inputs.py"


def git_blob_id(path: Path) -> str:
    data = Path(path).read_bytes()
    return hashlib.sha1(b"blob %d\0" % len(data) + data).hexdigest()


def sha256_of(path: Path) -> str:
    digest = hashlib.sha256()
    with Path(path).open("rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def branch_names(root_mod: Any, path: Path, tree_name: str = "MasterAnaDev") -> list[str]:
    handle = root_mod.TFile.Open(str(path))
    tree = handle.Get(tree_name)
    names = sorted(str(b.GetName()) for b in tree.GetListOfBranches())
    handle.Close()
    return names


def search(names: list[str], patterns: list[str]) -> dict[str, list[str]]:
    return {p: [n for n in names if re.search(p, n, re.IGNORECASE)] for p in patterns}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--historical-repo", type=Path, required=True)
    parser.add_argument("--tree-listing", type=Path, required=True)
    parser.add_argument("--executed-builder", type=Path, required=True)
    parser.add_argument("--executed-schema", type=Path, required=True)
    parser.add_argument("--slim", type=Path, required=True)
    parser.add_argument("--executed-shard", type=Path, required=True)
    parser.add_argument("--source-anatuple", type=Path, required=True)
    parser.add_argument("--limit", type=int, default=20000)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()

    import numpy as np
    import ROOT

    ROOT.gROOT.SetBatch(True)
    tree_blobs = {}
    for line in args.tree_listing.read_text().splitlines():
        meta, _tab, path = line.partition("\t")
        parts = meta.split()
        if len(parts) == 3:
            tree_blobs[path] = parts[2]

    record: dict[str, Any] = {"schema": "pet-improvement-A1-theirs-build-check-v1"}
    record["builder"] = {
        "executed_path": str(args.executed_builder),
        "executed_blob": git_blob_id(args.executed_builder),
        "historical_blob": tree_blobs.get(BUILDER_RELPATH),
    }
    record["builder"]["executed_is_historical"] = (
        record["builder"]["executed_blob"] == record["builder"]["historical_blob"])

    # The builder imports PID_CODES from a sibling `theirs_token_schema`; the executed
    # sibling is a different file from the checkout's. Compare what the builder uses.
    spec = importlib.util.spec_from_file_location("tts_executed", args.executed_schema)
    tts_exec = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(tts_exec)

    config_dir = args.historical_repo / "nd-unfolding" / "pet" / "configuration_comparison"
    sys.path.insert(0, str(config_dir))
    import build_theirs_inputs as bti  # noqa: E402  (the pinned checkout's copy)
    import theirs_token_schema as tts_hist  # noqa: E402

    record["builder"]["imported_from"] = bti.__file__
    record["builder"]["pid_codes_executed_sibling"] = dict(tts_exec.PID_CODES)
    record["builder"]["pid_codes_historical"] = dict(tts_hist.PID_CODES)
    record["builder"]["pid_codes_agree"] = dict(tts_exec.PID_CODES) == dict(tts_hist.PID_CODES)
    record["declared_differences"] = dict(bti.DECLARED_DIFFERENCES)

    # 2. Rebuild and compare.
    rebuilt = bti.build_file(args.slim, MC_FIELDS, limit=args.limit)
    with np.load(args.executed_shard) as blob:
        executed = {k: blob[k][: args.limit] for k in blob.files}
    comparison = {}
    for key in ("tokens", "add_info", "globals", "identity"):
        a, b = rebuilt[key], executed[key]
        same_shape = a.shape == b.shape
        comparison[key] = {
            "shape_rebuilt": list(a.shape), "shape_executed": list(b.shape),
            "array_equal": bool(same_shape and np.array_equal(a, b)),
            "max_abs_difference": (float(np.max(np.abs(a.astype(np.float64) -
                                                       b.astype(np.float64))))
                                   if same_shape and a.size else None),
        }
    record["rebuild"] = {"slim": str(args.slim), "slim_sha256": sha256_of(args.slim),
                         "executed_shard": str(args.executed_shard),
                         "executed_shard_sha256": sha256_of(args.executed_shard),
                         "rows_compared": int(min(args.limit, executed["tokens"].shape[0])),
                         "arrays": comparison,
                         "all_equal": all(c["array_equal"] for c in comparison.values())}

    # 3 and 4. Per-event facts from the slim against the executed shard.
    pid = executed["tokens"][:, :, 4]
    real = executed["tokens"][:, :, 3] != 0
    codes = bti.PID_CODES if hasattr(bti, "PID_CODES") else tts_hist.PID_CODES
    muon_token = np.any(real & (pid == codes["muon"]), axis=1)
    handle = ROOT.TFile.Open(str(args.slim))
    tree = handle.Get("MasterAnaDev")
    n = int(min(args.limit, tree.GetEntries(), executed["tokens"].shape[0]))
    muon_e = np.zeros(n)
    n_blob = np.zeros(n, dtype=np.int64)
    n_prong = np.zeros(n, dtype=np.int64)
    n_photon = np.zeros(n, dtype=np.int64)
    for i in range(n):
        tree.GetEntry(i)
        muon_e[i] = float(tree.MasterAnaDev_muon_E)
        n_blob[i] = len(bti._as_array(tree.MasterAnaDev_BlobTotalE))
        n_prong[i] = int(tree.prong_part_E_n)
        n_photon[i] = sum(1 for tag in ("gamma1", "gamma2")
                          if float(getattr(tree, f"{tag}_E")) > 0.0)
    handle.Close()
    has_muon = muon_e > 0
    mt = muon_token[:n]
    record["muon_presence"] = {
        "events": n,
        "muon_E_positive": int(has_muon.sum()),
        "muon_token_present": int(mt.sum()),
        "agree": int((has_muon == mt).sum()),
        "token_without_muon_E": int((mt & ~has_muon).sum()),
        "muon_E_without_token": int((~mt & has_muon).sum()),
        "rule_that_ran": ("muon token present <=> MasterAnaDev_muon_E > 0"
                          if bool(np.all(has_muon == mt)) else "NOT the declared rule"),
    }
    real_n = real[:n]
    pid_n = pid[:n]
    per_cat = {name: np.sum(real_n & (pid_n == code), axis=1)
               for name, code in codes.items()}
    total_objects = has_muon.astype(int) + n_photon + n_blob + n_prong
    cap = executed["tokens"].shape[1]
    binds = total_objects > cap
    record["cap_split"] = {
        "cap": int(cap),
        "events": n,
        "events_where_objects_exceed_cap": int(binds.sum()),
        "fraction_where_cap_binds": float(binds.mean()) if n else None,
        "aggregate_blob_token_events": int((per_cat["aggregate_blob"] > 0).sum()),
        "aggregate_prong_token_events": int((per_cat["aggregate_prong"] > 0).sum()),
        "when_binding": ({
            "objects_mean": float(total_objects[binds].mean()),
            "blob_multiplicity_mean": float(n_blob[binds].mean()),
            "blob_tokens_kept_mean": float(per_cat["blob"][binds].mean()),
            "prong_multiplicity_mean": float(n_prong[binds].mean()),
            "prong_tokens_kept_mean": float(sum(per_cat[k][binds] for k in
                                                ("prong_3", "prong_8", "prong_13")).mean()),
        } if binds.any() else None),
        "tokens_per_event_max": int(real_n.sum(axis=1).max()) if n else None,
    }

    # 5. What the R4 extraction and the original AnaTuple carry.
    patterns = [r"minos", r"dEdX", r"dEdx", r"prong_part_dEdXMean"]
    slim_names = branch_names(ROOT, args.slim)
    source_names = branch_names(ROOT, args.source_anatuple)
    record["resolvability"] = {
        "slim_branch_count": len(slim_names),
        "slim_matches": search(slim_names, patterns),
        "source_anatuple": str(args.source_anatuple),
        "source_branch_count": len(source_names),
        "source_matches": search(source_names, patterns),
    }
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(record, indent=1, default=repr) + "\n")
    print(f"[check] wrote {args.out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

import argparse
import hashlib
import json
import logging
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "phase_a"))
import numpy_probe
numpy_probe.disable_numpy_sve_probe()

import numpy as np

# Add the parent directory so we can import stage_splits
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent / "configuration_comparison"))
import stage_splits

SALT = b"pet-improvement-20260922-pools"
# Pool codes and u-ranges, PROTOCOL-20260922.md section 3. -1 = excluded or not pass_truth.
POOLS = (("P", 0, 0.00, 0.08), ("F", 1, 0.08, 0.40), ("S", 2, 0.40, 0.80),
         ("T", 3, 0.80, 0.97), ("R", 4, 0.97, 1.00))


def pool_seed(salt: bytes) -> int:
    return int.from_bytes(hashlib.sha256(salt).digest()[:8], "little", signed=True)


def assign_pools(identity, keys, pass_truth, excluded_rows, seed) -> np.ndarray:
    """Pool code per inventory row from the identity hash; excluded or non-truth rows get -1."""
    excluded = np.zeros(len(identity), dtype=bool)
    excluded[np.asarray(excluded_rows, dtype=np.int64)] = True
    eligible_indices = np.flatnonzero(np.asarray(pass_truth, dtype=bool) & ~excluded)
    # The sidecar declares signal identity unique without source; check it rather than trust it.
    if len(np.unique(keys[eligible_indices])) != len(eligible_indices):
        raise SystemExit("duplicate identities among eligible rows")
    u = stage_splits.uniform_hash(identity[eligible_indices], seed)
    codes = np.full(len(identity), -1, dtype=np.int8)
    for _, code, lo, hi in POOLS:
        codes[eligible_indices[(u >= lo) & (u < hi)]] = code
    if np.any(codes[eligible_indices] < 0):
        raise SystemExit("an eligible row fell outside every pool range")
    return codes


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()

def main():
    logging.basicConfig(level=logging.INFO)
    
    identity_path = Path("/pscratch/sd/j/josephrb/event-identity-audit/G2_FPS_MEFHC_P12.identity.npz")
    truth_path = Path("/global/cfs/cdirs/m3246/josephrb/minerva-shutdown-stage/g2_input/G2_FPS_MEFHC_P12.npz")
    campaign_dir = Path("/pscratch/sd/j/josephrb/campaign-20260920")
    
    out_dir = Path("/pscratch/sd/j/josephrb/pet-improvement-20260922/pools")
    out_dir.mkdir(parents=True, exist_ok=True)
    
    pool_npz_path = out_dir / "pools.npz"
    manifest_path = Path(__file__).resolve().parent / "POOL_MANIFEST.json"
    
    # 1. Load inputs
    logging.info(f"Loading identity from {identity_path}")
    with np.load(identity_path, mmap_mode="r") as f:
        identity = np.asarray(f["sig_event_id"])
        keys = np.asarray(f["sig_event_key"])
        identity_fields = [str(x) for x in f["sig_identity_fields"]]
        uniqueness = str(f["identity_uniqueness"])
        
    logging.info(f"Loading truth from {truth_path}")
    with np.load(truth_path, mmap_mode="r") as f:
        pass_truth = np.asarray(f["pass_truth"]).astype(bool)
        
    identity_sha = sha256_file(identity_path)
    truth_sha = sha256_file(truth_path)
    
    # 2. Build EXCLUSION set
    exclusion_set = set()
    artifact_files = []
    
    logging.info("Building EXCLUSION set from historical runs...")
    for stage in ["tuning", "pilot", "final"]:
        for weight_file in campaign_dir.glob(f"{stage}/*/weights/*.npz"):
            artifact_files.append(weight_file)
            with np.load(weight_file, allow_pickle=False) as f:
                # Both halves must be recorded: a missing key would silently shrink the exclusion.
                missing = [k for k in ("dump_rows_a", "dump_rows_b") if k not in f.files]
                if missing:
                    raise SystemExit(f"{weight_file}: no {missing}; cannot build the exclusion set")
                exclusion_set.update(np.asarray(f["dump_rows_a"]).astype(np.int64).tolist())
                exclusion_set.update(np.asarray(f["dump_rows_b"]).astype(np.int64).tolist())
                    
    num_excluded = len(exclusion_set)
    logging.info(f"Found {len(artifact_files)} artifact files, {num_excluded} excluded rows.")
    
    artifact_info = [{"path": str(p), "sha256": sha256_file(p)} for p in sorted(artifact_files)]
    
    # 3. Compute hashes and assign pools
    salt = SALT
    seed = pool_seed(SALT)
    excluded_rows = np.fromiter(exclusion_set, dtype=np.int64, count=num_excluded)
    logging.info("Assigning pools...")
    pool_codes = assign_pools(identity, keys, pass_truth, excluded_rows, seed)

    # 4. Save and generate manifest
    logging.info(f"Saving pools to {pool_npz_path}")
    np.savez_compressed(pool_npz_path, pool_codes=pool_codes)
    
    pool_npz_sha = sha256_file(pool_npz_path)
    
    def get_pool_sha(code):
        idx = np.flatnonzero(pool_codes == code)
        pool_id = identity[idx]
        sorted_idx = np.lexsort(pool_id.T[::-1])
        sorted_id = np.ascontiguousarray(pool_id[sorted_idx])
        return hashlib.sha256(sorted_id.tobytes()).hexdigest()
        
    manifest = {
        "inputs": {
            "identity_npz": {"path": str(identity_path), "sha256": identity_sha},
            "truth_npz": {"path": str(truth_path), "sha256": truth_sha}
        },
        "identity": {"array": "sig_event_id", "fields": identity_fields,
                     "sidecar_uniqueness": uniqueness, "eligible_unique_checked": True},
        "salt": salt.decode('utf-8'),
        "seed": seed,
        "exclusion": {
            "count": num_excluded,
            "artifacts_count": len(artifact_info),
            "artifacts": artifact_info
        },
        "pools": {name: {"code": code, "u_range": [lo, hi], "count": int(np.sum(pool_codes == code)),
                         "sorted_identity_sha256": get_pool_sha(code)} for name, code, lo, hi in POOLS},
        "not_pass_truth_rows": int(np.sum(~pass_truth)),
        "output": {
            "path": str(pool_npz_path),
            "sha256": pool_npz_sha
        },
        "commit": subprocess.check_output(["git", "-C", str(Path(__file__).parent), "rev-parse", "HEAD"]).decode("utf-8").strip()
    }
    
    logging.info(f"Saving manifest to {manifest_path}")
    with open(manifest_path, "w") as f:
        json.dump(manifest, f, indent=2)

if __name__ == "__main__":
    main()

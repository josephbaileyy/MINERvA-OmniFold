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
                if "dump_rows_a" in f:
                    exclusion_set.update(np.asarray(f["dump_rows_a"]).astype(np.int64))
                if "dump_rows_b" in f:
                    exclusion_set.update(np.asarray(f["dump_rows_b"]).astype(np.int64))
                    
    num_excluded = len(exclusion_set)
    logging.info(f"Found {len(artifact_files)} artifact files, {num_excluded} excluded rows.")
    
    artifact_info = [{"path": str(p), "sha256": sha256_file(p)} for p in sorted(artifact_files)]
    
    # 3. Compute hashes and assign pools
    salt = b"pet-improvement-20260922-pools"
    seed = int.from_bytes(hashlib.sha256(salt).digest()[:8], 'little', signed=True)
    
    pool_codes = np.full(len(identity), -1, dtype=np.int8)
    
    excluded_array = np.zeros(len(identity), dtype=bool)
    if num_excluded > 0:
        excluded_array[list(exclusion_set)] = True
        
    eligible = pass_truth & (~excluded_array)
    eligible_indices = np.flatnonzero(eligible)
    eligible_identities = identity[eligible_indices]
    
    logging.info("Computing uniform hashes...")
    u = stage_splits.uniform_hash(eligible_identities, seed)
    
    logging.info("Assigning pools...")
    # P [0,0.08), F [0.08,0.40), S [0.40,0.80), T [0.80,0.97), R [0.97,1.0)
    # Mapping to 0, 1, 2, 3, 4
    mask_P = u < 0.08
    mask_F = (u >= 0.08) & (u < 0.40)
    mask_S = (u >= 0.40) & (u < 0.80)
    mask_T = (u >= 0.80) & (u < 0.97)
    mask_R = (u >= 0.97) & (u <= 1.0) # Should be up to 1.0
    
    pool_codes[eligible_indices[mask_P]] = 0
    pool_codes[eligible_indices[mask_F]] = 1
    pool_codes[eligible_indices[mask_S]] = 2
    pool_codes[eligible_indices[mask_T]] = 3
    pool_codes[eligible_indices[mask_R]] = 4
    
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
        "salt": salt.decode('utf-8'),
        "seed": seed,
        "exclusion": {
            "count": num_excluded,
            "artifacts_count": len(artifact_info),
            "artifacts": artifact_info
        },
        "pools": {
            "P": {"count": int(np.sum(pool_codes == 0)), "sorted_identity_sha256": get_pool_sha(0)},
            "F": {"count": int(np.sum(pool_codes == 1)), "sorted_identity_sha256": get_pool_sha(1)},
            "S": {"count": int(np.sum(pool_codes == 2)), "sorted_identity_sha256": get_pool_sha(2)},
            "T": {"count": int(np.sum(pool_codes == 3)), "sorted_identity_sha256": get_pool_sha(3)},
            "R": {"count": int(np.sum(pool_codes == 4)), "sorted_identity_sha256": get_pool_sha(4)}
        },
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

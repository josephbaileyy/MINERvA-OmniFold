from pathlib import Path

def check_authorization(is_real_data: bool, out_dir: Path):
    if is_real_data:
        raise ValueError("AUTHORIZATION GUARD: Real data inputs to unfolding stages are refused.")
    
    historical_dir = Path("/pscratch/sd/j/josephrb/campaign-20260920").resolve()
    out_resolved = Path(out_dir).resolve()
    if historical_dir in out_resolved.parents or historical_dir == out_resolved:
        raise ValueError("AUTHORIZATION GUARD: Writing to the historical output directory is refused.")

def get_historical_thresholds():
    import sys
    repo_root = Path(__file__).resolve().parent.parent.parent.parent
    sys.path.insert(0, str(repo_root / "nd-unfolding" / "pet" / "configuration_comparison"))
    from frozen_design import THRESHOLDS
    return THRESHOLDS

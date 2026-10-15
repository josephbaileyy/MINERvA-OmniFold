"""Shared definitions for the 2026-10-14 period-unfold test: run periods, paths and pins.

Periods follow the flux-file grouping of FluxAndCVReweighter.h:27-33 / MAT FluxReweighter.cxx:1936-1976
(playlist-spread REPORT section 3.1): 1A-1F use the 1D flux, 1G/1L/1M the 1M flux, 1N-1P the 1N flux.
Playlist order inside every merged file is the production order (sbatch_hadd_MEFHC.sh:30-43), so the
control merge 'ALL' is the same concatenation as runEventLoopOmniFold_MEFHC.root.
"""
PLS = ["1A", "1B", "1C", "1D", "1E", "1F", "1G", "1L", "1M", "1N", "1O", "1P"]
PERIODS = {
    "PA": ["1A", "1B", "1C", "1D", "1E", "1F"],
    "PB": ["1G", "1L", "1M"],
    "PC": ["1N", "1O", "1P"],
    "ALL": PLS,
}
assert sum(len(PERIODS[p]) for p in ("PA", "PB", "PC")) == 12
assert [q for p in ("PA", "PB", "PC") for q in PERIODS[p]] == PLS

NS = "/pscratch/sd/j/josephrb/2d-closeout-period-unfold-20261014"
D2 = "/pscratch/sd/j/josephrb/MINERvA-OmniFold/2d-unfolding"          # read only
BASE_FLUX = f"{D2}/baseline_flux"                                       # read only
CODE = f"{NS}/code/repo"                                                # git archive of main c67dbdda
COMMIT = "c67dbddac445790229a1269dba1209cf98824bc4"


def per_playlist_omnifile(pl):
    """May CV per-playlist event-loop output (the files potcheck.json sums to the merged CV omnifile)."""
    return f"{D2}/runEventLoopOmniFold_{pl}.root"


def merged_omnifile(period):
    return f"{NS}/inputs/runEventLoopOmniFold_{period}.root"


def flux_file(period):
    return f"{NS}/flux/runEventLoopMC_{period}.root"


PINS = {
    "producer": (f"{CODE}/2d-unfolding/unfold_2d_omnifold_unbinned.py",
                 "74a4ed69c3fa9c4ae5b6866f36343212b8d3f903fddde6c7bd40c382c1167d56"),
    "combine_flux": (f"{CODE}/2d-unfolding/combine_flux_MEFHC.py",
                     "1fc5c1e9fdb15011e5a6209f415e3b184de9e7080944b3548763e0294d117803"),
    # the producer imports this cluster-checkout copy by a hard-coded path (unfold_2d_omnifold_unbinned.py:2059-2062);
    # it equals unbinned_unfolding/python/omnifold.py at c67dbdda
    "helper": ("/pscratch/sd/j/josephrb/MINERvA-OmniFold/unbinned_unfolding/python/omnifold.py",
               "e96234124a31edd7a8dd61fdb16cb48a5b28cbd1b90202f59b0095868378227a"),
    "cv_omnifile_cfs": ("/global/cfs/cdirs/m3246/josephrb/two-d-followup-20261010/xr-input/runEventLoopOmniFold_MEFHC.root",
                        "43f8cc16ab2688200d3e2e0ebb48012b23ada6d7882b8c68ecfc51c609aeb8df"),
    "flux_production": (f"{BASE_FLUX}/runEventLoopMC_MEFHC.root",
                        "d40aea69235cdc98644e1bb3e622e579d6b81904c004c83fe50465079989f316"),
    "E_U": (f"{D2}/uq/2d_xsec_MEFHC_5iter_lgbm_uni_full_CV.root",
            "4f5a1b6d44b9e7212b233650bb00bfb626ae65461e3bf8033cd67866dbd7eb2c"),
    "XR_L0": ("/pscratch/sd/j/josephrb/xr-linux-20261011/L0/a1/XR-L0.root",
              "751380245dbb27f67616ade8321d73274e0a5c0bb1344275fc3b67db2595aecc"),
    "work_cov": ("/pscratch/sd/j/josephrb/tmp-playlist-coverage-20261014/work_cov.npz",
                 "70c4daf2048875538eb74ee507b1d8741ca4ff80a8a351f0500450151a19ed1d"),
}
COVERAGE_SCRIPTS = f"{CODE}/docs/orchestration/state/2d-closeout/playlist-spread-20261014/coverage/scripts"


def sha256(path):
    import hashlib
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for blk in iter(lambda: f.read(1 << 22), b""):
            h.update(blk)
    return h.hexdigest()


def check_pin(name):
    path, want = PINS[name]
    got = sha256(path)
    if got != want:
        raise SystemExit(f"[FAIL] pin {name}: {path} sha256 {got} != {want}")
    return {"path": path, "sha256": got}

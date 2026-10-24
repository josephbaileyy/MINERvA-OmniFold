"""RE-2 part C copy of period-unfold-20261014/scripts/periods.py (d37c1a8f...), RE2-DECLARATION-C.md §3.4.

set_arm("purity") (the import default) leaves every definition as the original. set_arm("refined", work_cov=(path,
sha256)) repoints only the pins the refined period chain reads, under the same keys (PD-03/04/05/06):
  E_U       -> E_R, part B's ER (the key keeps its name: it is the central value's role)
  XR_L0     -> J0's refined D_cv (SHA256SUMS.J0b), the control's second reference (PA-05b)
  work_cov  -> the refined work_cov written by re2c_export_cov.py --arm refined, pinned by the sha256 that step
               recorded (chain of custody; its digest cannot be declared before it exists)
  producer  -> re2_driver.py at dbdad2f9 (the refined period runs' driver)
and NS (the selftest's scratch) -> the part C namespace. The run-period definitions, CODE and the helper are unchanged.

The original docstring follows.

Shared definitions for the 2026-10-14 period-unfold test: run periods, paths and pins.

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


# ---- the refined arm (RE2-DECLARATION-C.md §3.4)
ARM = "purity"
B_R = "/pscratch/sd/j/josephrb/2d-closeout-re2-20261023"
PINS_REFINED = {
    "E_U": (f"{B_R}/partb/out/ER/xsec.root", "a5c13fc38d64242bc9ee459fac87568a2f97fddf7a3ac97cc6f91eb4c2a31cef"),
    "XR_L0": (f"{B_R}/j0/out/D_cv/xsec.root", "0835a3285577e80392a533007819b9f2982cea60c00561a835ce6df086fbd02b"),
    "producer": (f"{B_R}/deploy-dbdad2f9/2d-unfolding/re2/re2_driver.py",
                 "38ff37055af026bd11b1c12a431b31eed522d5038c1bcf020cd47c374d2ddf7c"),
}
RUN_MODE = {"purity": {"driverSha256": PINS["producer"][1], "bkg_mode": ("purity", None)},
            "refined": {"driverSha256": PINS_REFINED["producer"][1], "bkg_mode": ("negweight-refined",),
                        "refine_n_estimators": 400, "refine_num_leaves": 31}}


def set_arm(arm, work_cov=None, ns=None):
    """Repoint the refined pins in place (PINS is shared by every importer of this module)."""
    global ARM, NS
    if arm not in ("purity", "refined"):
        raise SystemExit(f"arm {arm}: purity or refined")
    ARM = arm
    if ns:   # the selftest's scratch; the purity dry run passes its own so nothing is written under the 10-14 NS
        NS = ns
    if arm == "refined":
        if not work_cov or not ns:
            raise SystemExit("the refined arm needs work_cov=(path, sha256) and ns")
        PINS.update(PINS_REFINED)
        PINS["work_cov"] = tuple(work_cov)


_SUMS = {}


def partb_digest(path):
    """A part-B output's committed digest (run/partb_readout/sums/), by its out/<label>/xsec.root path."""
    if not _SUMS:
        import pathlib
        d = pathlib.Path(__file__).resolve().parents[3] / "docs/orchestration/state/2d-closeout/stageF/methods/re2/run"
        for f in sorted((d / "partb_readout" / "sums").glob("SHA256SUMS.J*")):
            for ln in f.read_text().splitlines():
                h, rel = ln.split()
                _SUMS[f"{B_R}/partb/out/{rel}"] = h
    return _SUMS.get(path)


def check_mode(run):
    """PA-02 / PT-G: a period run's driver and background mode must be its arm's; in the refined arm its sha256 must
    also be the committed part-B digest. Raises SystemExit."""
    want = RUN_MODE[ARM]
    bad = {}
    if ARM == "refined" and run.get("sha256") != partb_digest(run.get("path")):
        bad["sha256"] = {"got": run.get("sha256"), "committed": partb_digest(run.get("path"))}
    if run.get("driverSha256") != want["driverSha256"]:
        bad["driverSha256"] = run.get("driverSha256")
    if run.get("bkg_mode") not in want["bkg_mode"]:
        bad["bkg_mode"] = run.get("bkg_mode")
    for k in ("refine_n_estimators", "refine_num_leaves"):
        if k in want and run.get(k) != want[k]:
            bad[k] = run.get(k)
    if bad:
        raise SystemExit(f"[FAIL] mode guard ({ARM}) on {run.get('path')}: {bad}")

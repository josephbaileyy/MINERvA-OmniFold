"""The historical powered-closure inputs, recomposed from the historical functions (no edits).

`configuration_comparison/run_arm_evaluation.evaluate` builds its inputs inline; this module
performs the same sequence by CALLING the same historical functions -- `build_fullevent_loaders`,
`stage_splits.rows_for_stage` / `usable_half_size`, `closure_powered_truth_reweight.
deterministic_halves` / `clipped_exponential_tilt`, and the driver's own `_identity_of`,
`_truth_eavail` and `_load_joined` -- with the event selection taken from the `RunConfig` instead
of the command line. The runtime check job verifies the result by digest against the arrays the
UNMODIFIED historical driver fed its engine (`phase_a/receipts/runtime_audit_*.json`).

Import order matters (OI-136): `fullevent_fps_dataloader` inserts the hardcoded tree
`/pscratch/sd/j/josephrb/MINERvA-OmniFold` at `sys.path[0]` when imported. `import_historical`
therefore imports the engine from THIS checkout first, then the loader, then removes the
hardcoded entries, so nothing afterwards can resolve there; the guard runs without `--allow`.
"""

from __future__ import annotations

import argparse
import hashlib
import sys
import zipfile
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

HARDCODED_ROOT = "/pscratch/sd/j/josephrb/MINERvA-OmniFold"


def import_historical(repo: Path) -> dict[str, Any]:
    """Import the engine and historical helpers from `repo`, in an OI-136-safe order."""
    repo = Path(repo).resolve()
    comp = repo / "nd-unfolding" / "pet" / "configuration_comparison"
    for extra in (repo / "nd-unfolding" / "pet", repo / "omnifold_nn", comp):
        if str(extra) not in sys.path:
            sys.path.insert(0, str(extra))
    from keras_backend import configure_production_precision, select_keras_backend
    select_keras_backend()
    import omnifold.dataloader  # noqa: F401  (engine from THIS checkout, before the loader)
    import omnifold.net
    import omnifold.omnifold
    import fullevent_fps_dataloader as ffd
    removed = [p for p in sys.path if p.startswith(HARDCODED_ROOT)]
    sys.path[:] = [p for p in sys.path if not p.startswith(HARDCODED_ROOT)]
    import closure_powered_truth_reweight as cp
    import frozen_design as fd
    import run_arm_evaluation as rae
    import stage_splits as ss
    precision = configure_production_precision(strict=True)
    modules = {"ffd": ffd, "cp": cp, "fd": fd, "rae": rae, "ss": ss,
               "omnifold": omnifold.omnifold, "net": omnifold.net,
               "DataLoader": omnifold.dataloader.DataLoader}
    foreign = {name: getattr(mod, "__file__", "") for name, mod in modules.items()
               if hasattr(mod, "__file__") and not str(Path(mod.__file__).resolve())
               .startswith(str(repo))}
    if foreign:
        raise SystemExit(f"[closure_data] modules resolved outside {repo}: {foreign}")
    modules["sys_path_entries_removed"] = removed
    modules["precision_policy"] = precision
    return modules


@dataclass
class ClosureInputs:
    arm: str
    pdata: dict[str, Any]
    mc: dict[str, Any]
    meta: dict[str, Any] = field(default_factory=dict)

    def digests(self, np: Any) -> dict[str, str]:
        """Digests in the SAME layout the runtime audit recorded (engine concatenation order)."""
        def h(a: Any) -> str:
            return hashlib.sha256(np.ascontiguousarray(a).tobytes()).hexdigest()
        return {
            "step1_cloud": h(np.concatenate([self.mc["reco"], self.pdata["reco"]], 0)),
            "step1_event": h(np.concatenate([self.mc["reco_evt"], self.pdata["reco_evt"]], 0)),
            "step2_cloud": h(self.mc["gen"]), "step2_event": h(self.mc["gen_evt"]),
        }


def build_closure_inputs(mods: dict[str, Any], np: Any, *, arm: str, events: Any,
                         endpoint: Any, inputs_npz: Path, identity_sidecar: Path,
                         theirs_index: Path | None, theirs_cache: Path | None) -> ClosureInputs:
    """`evaluate()` lines 254-383 at 68cf9d29, parameterized by `events` / `endpoint`."""
    ffd, cp, rae, ss = mods["ffd"], mods["cp"], mods["rae"], mods["ss"]
    need = int(events.max_events)
    data_leg, mc, imc, coord_reco, coord_gen, meta = ffd.build_fullevent_loaders(
        str(inputs_npz), max_events=need, seed=int(events.subsample_seed), bkg_mode="mc-only")
    if data_leg is not None:
        raise SystemExit("[closure_data] mc-only returned a measured loader")
    imc = np.asarray(imc)
    eavail = rae._truth_eavail(np, ffd, inputs_npz, imc)
    reco, reco_evt = np.asarray(mc.reco), np.asarray(mc.reco_evt)
    gen, gen_evt = np.asarray(mc.gen), np.asarray(mc.gen_evt)
    pr = np.asarray(mc.pass_reco).astype(bool)
    pg = np.asarray(mc.pass_gen).astype(bool)
    w_truth = np.asarray(mc.weight, dtype=np.float64)
    w_reco = np.asarray(mc.weight_reco, dtype=np.float64)

    identity = rae._identity_of(np, identity_sidecar, imc)
    stage_pos = ss.rows_for_stage(identity, events.stage)
    half = (int(events.half_size) if events.half_size is not None
            else ss.usable_half_size(identity, events.stage))
    if half <= 0 or stage_pos.size < 2 * half:
        raise SystemExit(f"[closure_data] stage {events.stage!r} cannot supply halves of {half}")
    ja, jb = cp.deterministic_halves(stage_pos.size, half=half, seed=int(events.split_seed))
    ia, ib = stage_pos[ja], stage_pos[jb]
    pg_a = pg[ia]
    tilt_a = np.ones(ia.size, dtype=np.float64)
    tilt_on_truth, tilt_spec = cp.clipped_exponential_tilt(
        eavail[ia][pg_a], amplitude=float(endpoint.amplitude), clip_z=float(endpoint.clip))
    tilt_a[pg_a] = tilt_on_truth
    s1_a = pr[ia] & pg_a
    s1_b = pr[ib] & pg[ib]

    substitution = None
    if arm == "theirs":
        args = argparse.Namespace(inputs_npz=Path(inputs_npz), theirs_index=theirs_index,
                                  theirs_cache=theirs_cache)
        blocks = rae._load_joined(args, np, imc[ia][s1_a], imc[ib],
                                  subsample_seed=int(events.subsample_seed), max_events=need,
                                  half_size=half, stage=events.stage)
        reco_a, reco_evt_a = blocks["pdata"]["packed"], blocks["pdata"]["globals"]
        reco_b, reco_evt_b = blocks["mc"]["packed"], blocks["mc"]["globals"]
        substitution = {"substituted": ["reco", "reco_evt"], "source": blocks["source"]}
    else:
        reco_a, reco_evt_a = reco[ia][s1_a], reco_evt[ia][s1_a]
        reco_b, reco_evt_b = reco[ib], reco_evt[ib]

    pdata = {"reco": reco_a, "reco_evt": reco_evt_a,
             "weight": ((w_reco[ia] * tilt_a)[s1_a]).astype(np.float32),
             "rows": imc[ia][s1_a].astype(np.int64)}
    mcb = {"reco": reco_b, "reco_evt": reco_evt_b, "gen": gen[ib], "gen_evt": gen_evt[ib],
           "pass_reco": s1_b, "pass_gen": pg[ib],
           "weight": w_truth[ib].astype(np.float32),
           "weight_reco": w_reco[ib].astype(np.float32),
           "rows": imc[ib].astype(np.int64)}
    meta_out = {
        "n_evt_reco": int(meta["n_evt_reco"]), "n_evt_truth": int(meta["n_evt_truth"]),
        "coord_reco": tuple(int(c) for c in coord_reco),
        "coord_gen": tuple(int(c) for c in coord_gen),
        "half_size": half, "stage_rows": int(stage_pos.size),
        "split_census": ss.census(identity), "tilt_spec": tilt_spec,
        "dump_rows_a": imc[ia].astype(np.int64), "dump_rows_b": imc[ib].astype(np.int64),
        "tilt_a": tilt_a, "pass_gen_a": pg_a, "mc_indices": imc.astype(np.int64),
        "substitution": substitution,
        "step1_mc_normalization": ffd.STEP1_MC_NORMALIZATION,
    }
    return ClosureInputs(arm=arm, pdata=pdata, mc=mcb, meta=meta_out)


def read_scalar_column(np: Any, ffd: Any, inputs_npz: Path, which: str, column: str,
                       rows: Any) -> Any:
    """One column of `reco_scalars` / `truth_scalars` for absolute dump `rows`."""
    import numpy.lib.format as npf
    member = {"reco": "reco_scalars.npy", "truth": "truth_scalars.npy"}[which]
    with zipfile.ZipFile(str(inputs_npz)) as archive:
        with archive.open(member) as handle:
            scalars = npf.read_array(handle, allow_pickle=False)
    return scalars[np.asarray(rows), ffd.SCALAR_COLS[column]].astype(np.float64)


def make_loaders(mods: dict[str, Any], np: Any, inputs: ClosureInputs) -> tuple[Any, Any]:
    """The two DataLoaders exactly as `evaluate()` builds them (lines 351-363)."""
    DataLoader, ffd = mods["DataLoader"], mods["ffd"]
    p, m = inputs.pdata, inputs.mc
    pdata = DataLoader(reco=p["reco"], weight=p["weight"], normalize=True,
                       reco_evt=p["reco_evt"])
    mcb = DataLoader(reco=m["reco"], gen=m["gen"], pass_reco=m["pass_reco"],
                     pass_gen=m["pass_gen"], weight=m["weight"], weight_reco=m["weight_reco"],
                     normalize=True, normalization_factor=ffd.STEP1_MC_NORMALIZATION,
                     reco_evt=m["reco_evt"], gen_evt=m["gen_evt"])
    for name, loader in (("pdata", pdata), ("mcB", mcb)):
        for fld in ("weight", "weight_reco"):
            arr = getattr(loader, fld, None)
            if arr is not None and np.asarray(arr).dtype != np.float32:
                raise SystemExit(f"[closure_data] {name}.{fld} is not float32")
    return pdata, mcb

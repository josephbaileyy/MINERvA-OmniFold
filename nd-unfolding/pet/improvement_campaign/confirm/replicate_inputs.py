"""PET driver inputs for a replicate draw from an event pool, built as `closure_data.py` builds them.

A confirmatory run (PROTOCOL-20260922 section 5) unfolds a fresh PRIOR sample and a fresh, distorted
PSEUDODATA sample drawn from a pool (section 3), not the historical halves. This module does three
things and nothing else:

1. **Selects the rows.** `replicate_selection` draws (pool, replicate) with `phase_e/replicates.py`
   (identity-hashed, prior and pseudodata disjoint within a replicate, replicates of one family
   disjoint event draws). `historical_selection` replays the historical halves with the historical
   functions, for the positive control. Pools P (PILOT) and F (FINAL) are refused unless the
   protocol in the checkout carries its Amendment 2 (the candidate freeze).
2. **Loads those rows exactly as the historical loader does.** `load_signal_rows` is the mc-only
   branch of `fullevent_fps_dataloader.build_fullevent_loaders` with its subsample `imc` replaced by
   the given rows: the same helper functions, in the same order, on the same members, and the same
   `DataLoader` normalization. It differs in one respect, on purpose: the historical loader also
   reads the real-data members `measured_scalars` / `data_muon` / `data_vertex` to build a data
   event block that the mc-only closure then discards. Here the inventory is opened through
   `authorization_scope.SignalOnlyNpz`, which refuses every real-data member, and the discarded
   block is built from a stand-in (the MC rows' own reco blocks). The step-1 and step-2 arrays do
   not depend on that block (`build_event_features` forms its normalization from the MC reco rows
   only), which the positive control checks byte for byte.
3. **Assembles the closure** exactly as `closure_data.build_closure_inputs` does (its lines for the
   ours arm): pseudodata = the pseudodata rows passing reco and truth, weighted `w_reco x d`; prior =
   every prior row with both weight legs and both pass flags. `d` is the distortion weight,
   normalized to unit mean over the pseudodata's truth-passing rows. The development distortion
   (`dev`) is the HISTORICAL tilt with its standardization frozen at the historical constants, read
   from the historical record; every other distortion is a truth-weight distortion of
   `phase_e/distortions.py`, by id.

Only signal-MC simulation is read. PET is diagnostic method development.
"""

from __future__ import annotations

import hashlib
import importlib.util
import json
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable, Mapping

import numpy as np

HERE = Path(__file__).resolve().parent
CAMPAIGN = HERE.parent
PHASE_E = CAMPAIGN / "phase_e"
for _p in (CAMPAIGN, PHASE_E):
    if str(_p) not in sys.path:
        sys.path.insert(0, str(_p))

import authorization_scope as scope  # noqa: E402
import distortions as dist  # noqa: E402
import replicates as rp  # noqa: E402

SCHEMA = "pet-improvement-confirm-inputs/1"
PROTOCOL = CAMPAIGN / "PROTOCOL-20260922.md"
POPULATIONS_JSON = CAMPAIGN / "phase_b" / "scalar" / "results" / "populations.json"
DEV = "dev"
FAMILY = "confirm-historical-size-v1"
# PROTOCOL section 5.3 (fresh prior 600,130 rows, fresh pseudodata 600,111 rows). NOTE: the
# executed historical closure used the opposite assignment -- its pseudodata (half A) held 600,130
# truth-passing rows and its prior (half B) 600,111 (`populations.json` census); both halves had
# 600,143 rows. The protocol's sizes are kept; the 19-event difference is recorded, not hidden.
N_PRIOR, N_PSEUDO = 600_130, 600_111
SEALED_POOLS = ("P", "F")
AMENDMENT_2 = re.compile(r"^#{2,4} Amendment 2\b", re.MULTILINE)
SIGNAL_MEMBERS = ("edges_0", "edges_1", "petSchemaVersion", "pass_reco", "pass_truth",
                  "part_reco", "reco_view", "reco_time", "part_gen", "reco_scalars",
                  "truth_scalars", "reco_muon", "reco_vertex", "w_truth", "w_reco",
                  "sig_identity_hash")


def sha256_bytes(a: Any) -> str:
    return hashlib.sha256(np.ascontiguousarray(a).tobytes()).hexdigest()


def sha256_file(path: Path | str) -> str:
    return rp.sha256_file(path)


# ------------------------------------------------------------------------------------------- #
# Guards
# ------------------------------------------------------------------------------------------- #
def refuse_sealed_pool(pool: str, protocol: Path = PROTOCOL) -> dict[str, Any]:
    """Pools P and F are PILOT and FINAL: no row of them is read before the candidate freeze
    (protocol section 5.1), which the orchestrator records as Amendment 2 of the protocol. The
    check reads the protocol file of THIS checkout, so a pinned compute checkout without the
    amendment cannot open P or F."""
    if pool not in rp.POOL_CODES:
        raise SystemExit(f"[confirm] unknown pool {pool!r}")
    if pool not in SEALED_POOLS:
        return {"pool": pool, "sealed": False}
    text = Path(protocol).read_text()
    if not AMENDMENT_2.search(text):
        raise scope.ScopeViolation(
            f"pool {pool} is sealed (PILOT/FINAL) until the candidate freeze; {protocol} carries "
            "no 'Amendment 2' heading")
    return {"pool": pool, "sealed": True, "protocol": str(protocol),
            "protocol_sha256": sha256_file(protocol), "amendment_2_present": True}


# ------------------------------------------------------------------------------------------- #
# Distortions
# ------------------------------------------------------------------------------------------- #
def _frozen_design() -> Any:
    spec = importlib.util.spec_from_file_location("_frozen_design_for_confirm",
                                                  scope.FROZEN_DESIGN_PATH)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def historical_tilt_spec(populations_json: Path = POPULATIONS_JSON) -> dict[str, Any]:
    """The development tilt's constants, READ from the historical record, never retyped.

    Amplitude and clip: `configuration_comparison/frozen_design.ENDPOINT` (the frozen design).
    Standardization (p50, IQR of true E_avail over half A's truth-passing rows): the historical
    run's own tilt spec, replayed by B1 bit-identically to the recorded `tilt_a`
    (`phase_b/scalar/results/populations.json`, `tilt_spec_half_A`). Refuses if the two records
    disagree on amplitude or clip, or if Phase E's frozen D1 constants differ from them."""
    fd = _frozen_design()
    record = json.loads(Path(populations_json).read_text())
    b1 = record["tilt_spec_half_A"]
    amplitude, clip_z = float(fd.ENDPOINT["amplitude"]), float(fd.ENDPOINT["clip"])
    if float(b1["amplitude"]) != amplitude or float(b1["clip_z"]) != clip_z:
        raise SystemExit(f"[confirm] historical tilt spec {b1} disagrees with frozen_design "
                         f"(amplitude {amplitude}, clip {clip_z})")
    p50, iqr = float(b1["pt_p50"]), float(b1["pt_iqr"])
    if (p50, iqr, clip_z) != (dist.D1_P50_GEV, dist.D1_IQR_GEV, dist.TILT_CLIP_Z):
        raise SystemExit("[confirm] phase_e D1 constants differ from the historical tilt spec")
    return {"name": DEV, "form": "exp(A*clip((E-p50)/IQR, -Z, +Z)) / mean over the pseudodata's "
                                 "truth-passing rows",
            "amplitude": amplitude, "clip_z": clip_z, "p50": p50, "iqr": iqr,
            "historical_pre_normalization_mean": float(b1["pre_normalization_mean"]),
            "sources": {"frozen_design": "nd-unfolding/pet/configuration_comparison/"
                                          "frozen_design.py:ENDPOINT",
                        "frozen_design_sha256": sha256_file(scope.FROZEN_DESIGN_PATH),
                        "tilt_spec": "nd-unfolding/pet/improvement_campaign/phase_b/scalar/"
                                     "results/populations.json:tilt_spec_half_A",
                        "tilt_spec_sha256": sha256_file(populations_json)}}


def development_tilt_raw(eavail: np.ndarray, spec: Mapping[str, Any]) -> np.ndarray:
    """exp(A * clip((E - p50)/IQR, -Z, Z)), the operations of the historical
    `closure_powered_truth_reweight.clipped_exponential_tilt` in the same order, with its
    standardization frozen. Non-finite E is refused (the historical function would propagate it)."""
    e = np.asarray(eavail, dtype=np.float64)
    if not np.isfinite(e).all():
        raise SystemExit("[confirm] non-finite true E_avail on a truth-passing row")
    z = np.clip((e - float(spec["p50"])) / float(spec["iqr"]), -float(spec["clip_z"]),
                float(spec["clip_z"]))
    return np.exp(float(spec["amplitude"]) * z)


def unit_mean(raw: np.ndarray) -> tuple[np.ndarray, float]:
    """raw / mean(raw), as the historical tilt normalizes (unweighted mean over the rows given)."""
    mean = float(raw.mean())
    if not (np.isfinite(mean) and mean > 0):
        raise SystemExit(f"[confirm] distortion normalization is {mean!r}")
    w = raw / mean
    if not np.all(np.isfinite(w)) or np.any(w < 0):
        raise SystemExit("[confirm] distortion weight is non-finite or negative")
    return w, mean


@dataclass
class DistortionSpec:
    """A named truth-weight distortion: `dev` (the historical development tilt) or a
    `phase_e/distortions.py` truth-weight id."""
    name: str
    record: dict[str, Any]
    raw: Callable[[Mapping[str, np.ndarray]], np.ndarray]
    needs_species: bool = False

    def content_hash(self) -> str:
        return hashlib.sha256(json.dumps(self.record, sort_keys=True, default=repr)
                              .encode()).hexdigest()


def get_distortion(name: str, endpoint_amplitude: float | None = None,
                   endpoint_clip: float | None = None) -> DistortionSpec:
    if name == DEV:
        spec = historical_tilt_spec()
        if endpoint_amplitude is not None and (float(endpoint_amplitude), float(endpoint_clip)) \
                != (spec["amplitude"], spec["clip_z"]):
            raise SystemExit(f"[confirm] the RunConfig endpoint ({endpoint_amplitude}, "
                             f"{endpoint_clip}) is not the historical tilt")
        return DistortionSpec(DEV, spec, lambda t: development_tilt_raw(t["eavail"], spec))
    registry = dist.registry()
    if name not in registry:
        raise SystemExit(f"[confirm] unknown distortion {name!r}")
    d = registry[name]
    if d.kind != "truth_weight":
        raise SystemExit(f"[confirm] {name} is a reco-response distortion; the PET replicate path "
                         "implements truth-weight distortions only (not approximated, refused)")
    return DistortionSpec(name, {"name": name, "phase_e_spec": d.spec(),
                                 "phase_e_hash": d.content_hash(),
                                 "normalization": "unit mean over the pseudodata's truth-passing "
                                                  "rows"},
                          lambda t: np.asarray(d.truth_weight(t), np.float64),
                          needs_species=d.family == "D4")


# ------------------------------------------------------------------------------------------- #
# Row selection
# ------------------------------------------------------------------------------------------- #
@dataclass
class Selection:
    mode: str                       # "replicate" | "historical"
    load_rows: np.ndarray           # the rows the loader materializes (sorted, unique)
    prior_rows: np.ndarray          # sorted
    pseudo_rows: np.ndarray         # sorted
    record: dict[str, Any] = field(default_factory=dict)


def _sorted_unique(rows: np.ndarray, label: str) -> np.ndarray:
    rows = np.asarray(rows, dtype=np.int64)
    if rows.size and (np.any(np.diff(rows) <= 0) or rows[0] < 0):
        raise SystemExit(f"[confirm] {label} rows are not sorted, unique and non-negative")
    return rows


def replicate_selection(pool: str, replicate: int, *, pools_npz: Path, manifest: Path,
                        identity_sidecar: Path, n_prior: int = N_PRIOR, n_pseudo: int = N_PSEUDO,
                        family: str = FAMILY, protocol: Path = PROTOCOL) -> Selection:
    guard = refuse_sealed_pool(pool, protocol)
    codes, pool_record = rp.load_pool_codes(pools_npz, manifest)
    manifest_doc = json.loads(Path(manifest).read_text())
    sidecar_sha = sha256_file(identity_sidecar)
    if sidecar_sha != manifest_doc["inputs"]["identity_npz"]["sha256"]:
        raise SystemExit("[confirm] identity sidecar sha256 differs from the pool manifest")
    with np.load(identity_sidecar, mmap_mode="r") as blob:
        identity_all = np.asarray(blob["sig_event_id"]).astype(np.int64)
    if identity_all.shape[0] != codes.size:
        raise SystemExit("[confirm] identity sidecar and pool codes disagree in length")
    rows = rp.pool_rows(codes, pool)
    design = rp.ReplicateDesign(pool=pool, family=family, n_prior=int(n_prior),
                                n_pseudo=int(n_pseudo), disjoint=True)
    reps, draw = rp.draw_replicates(design, [int(replicate)], rows, identity_all[rows])
    rep = reps[0]
    prior, pseudo = np.sort(rep.prior_rows), np.sort(rep.pseudo_rows)
    if np.intersect1d(prior, pseudo).size:
        raise AssertionError("prior and pseudodata share rows")
    record = {"mode": "replicate", "pool_guard": guard, "pools": pool_record,
              "identity_sidecar": str(identity_sidecar), "identity_sidecar_sha256": sidecar_sha,
              "draw": draw, "replicate": rep.record(),
              "prior_rows_sha256": rp.rows_digest(prior),
              "pseudo_rows_sha256": rp.rows_digest(pseudo),
              "prior_identity_sha256": sha256_bytes(identity_all[prior]),
              "pseudo_identity_sha256": sha256_bytes(identity_all[pseudo])}
    return Selection("replicate", np.union1d(prior, pseudo), prior, pseudo, record)


def historical_selection(mods: Mapping[str, Any], events: Any, inputs_npz: Path,
                         identity_sidecar: Path) -> Selection:
    """The historical halves, replayed with the historical functions in `closure_data`'s order:
    the loader's subsample draw, `stage_splits`, `deterministic_halves`. Half A (tilted) is the
    pseudodata, half B the prior. The load set is the historical 2M subsample, so the loader's
    normalization statistics are the historical ones."""
    cp, rae, ss = mods["cp"], mods["rae"], mods["ss"]
    with np.load(inputs_npz, allow_pickle=False) as d:
        n = int(np.asarray(scope.SignalOnlyNpz(d)["pass_reco"]).shape[0])
    need = int(events.max_events)
    # `build_fullevent_loaders`: imc = sort(default_rng(seed).choice(N, min(max_events, N))).
    imc = np.sort(np.random.default_rng(int(events.subsample_seed))
                  .choice(n, min(need, n), replace=False))
    identity = rae._identity_of(np, identity_sidecar, imc)
    stage_pos = ss.rows_for_stage(identity, events.stage)
    half = (int(events.half_size) if events.half_size is not None
            else ss.usable_half_size(identity, events.stage))
    ja, jb = cp.deterministic_halves(stage_pos.size, half=half, seed=int(events.split_seed))
    pseudo, prior = imc[stage_pos[ja]], imc[stage_pos[jb]]
    record = {"mode": "historical", "subsample_seed": int(events.subsample_seed),
              "max_events": need, "stage": events.stage, "split_seed": int(events.split_seed),
              "half_size": half, "load_rows_sha256": rp.rows_digest(imc),
              "prior_rows_sha256": rp.rows_digest(prior),
              "pseudo_rows_sha256": rp.rows_digest(pseudo)}
    return Selection("historical", imc.astype(np.int64), _sorted_unique(prior, "prior"),
                     _sorted_unique(pseudo, "pseudodata"), record)


# ------------------------------------------------------------------------------------------- #
# The loader, on given rows
# ------------------------------------------------------------------------------------------- #
@dataclass
class LoadedRows:
    mc: Any                         # the engine DataLoader over `rows`
    rows: np.ndarray
    coord_reco: tuple
    coord_gen: tuple
    meta: dict[str, Any]
    truth_scalars: np.ndarray       # as stored (float32), per loaded row
    reco_scalars: np.ndarray
    pdg: np.ndarray                 # part_gen[..., 4] as stored, per loaded row
    w_truth_raw: np.ndarray         # float32 as stored
    w_reco_raw: np.ndarray
    keys_read: list[str]


def load_signal_rows(ffd: Any, DataLoader: type, inputs_npz: Path, rows: np.ndarray, *,
                     feature_names: Any = None, truth_feature_names: Any = None) -> LoadedRows:
    """`build_fullevent_loaders(..., bkg_mode="mc-only")` with `imc = rows`, reading signal-MC
    members only (see the module docstring for the one deliberate difference)."""
    feature_names = ffd.DEFAULT_EVT_FEATURES if feature_names is None else feature_names
    truth_feature_names = (ffd.DEFAULT_TRUTH_EVT_FEATURES if truth_feature_names is None
                           else truth_feature_names)
    imc = _sorted_unique(rows, "load")
    raw = np.load(inputs_npz, allow_pickle=True)
    d = scope.SignalOnlyNpz(raw)
    try:
        ffd.assert_extended_fps_edges(d["edges_0"], d["edges_1"])
        if str(np.asarray(d["petSchemaVersion"]).item() if "petSchemaVersion" in d.files
               else "") != "g2-fullevent-v1":
            raise ValueError("[confirm] input is not a g2-fullevent-v1 schema NPZ")
        n = np.asarray(d["pass_reco"]).shape[0]
        if imc.size == 0 or imc[-1] >= n:
            raise SystemExit(f"[confirm] rows outside the inventory ({n} rows)")
        need = {ffd._EVT_SPEC[f][0] for f in feature_names} | {ffd._EVT_SPEC[f][0]
                                                               for f in truth_feature_names}
        required = (["reco_muon"] if "muon" in need else []) + \
                   (["reco_vertex"] if "vertex" in need else []) + ["reco_view", "reco_time"]
        missing = [k for k in required if k not in d.files]
        if missing:
            raise ValueError(f"[confirm] the event-feature schema needs {missing}")

        def _tok(key: str) -> Any:
            return None if key not in d.files else np.asarray(d[key])[imc]

        reco_cloud, coord_reco = ffd.build_reco_cloud(np.asarray(d["part_reco"])[imc],
                                                      _tok("reco_view"), _tok("reco_time"))
        part_gen = np.asarray(d["part_gen"])[imc]
        gen_cloud, coord_gen = ffd.build_truth_cloud(part_gen)
        reco_scalars = np.asarray(d["reco_scalars"])[imc]
        truth_scalars = np.asarray(d["truth_scalars"])[imc]
        pass_reco = np.asarray(d["pass_reco"])[imc]
        pass_truth = np.asarray(d["pass_truth"])[imc]
        reco_blocks = ffd.evt_blocks(
            scalars=reco_scalars,
            muon=(np.asarray(d["reco_muon"])[imc] if "reco_muon" in d.files else None),
            vertex=(np.asarray(d["reco_vertex"])[imc] if "reco_vertex" in d.files else None))
        truth_blocks = ffd.evt_blocks(scalars=truth_scalars)
        # The data event block is built and discarded by the mc-only loader; its statistics do
        # not enter the MC blocks. Stand-in: this sample's own reco-passing MC rows.
        sel = np.asarray(pass_reco, bool)
        stand_in = {k: (None if v is None else np.asarray(v)[sel]) for k, v in reco_blocks.items()}
        event_reco, event_truth, _discarded, meta = ffd.build_event_features(
            reco_blocks, truth_blocks, stand_in, feature_names,
            pass_reco=pass_reco, pass_truth=pass_truth, truth_feature_names=truth_feature_names)
        meta["data_scalar_source"] = "NOT READ: stand-in = the loaded MC rows' reco blocks"
        meta["reco_cloud_cols"] = list(ffd.RECO_CLOUD_COLS[:reco_cloud.shape[-1]])
        meta["token_view_time_read"] = reco_cloud.shape[-1] == len(ffd.RECO_CLOUD_COLS)
        ffd.assert_no_truth_leakage(event_reco, reco_blocks, truth_blocks, feature_names,
                                    pass_reco=pass_reco, truth_feature_names=truth_feature_names)
        w_truth_full = np.asarray(d["w_truth"]).astype(np.float32)
        w_reco_full = np.asarray(d["w_reco"]).astype(np.float32)
        if w_reco_full.shape != w_truth_full.shape:
            raise ValueError("[confirm] w_reco and w_truth are not row-aligned")
        meta["bkg_mode"] = "mc-only"
        meta["input_identity_hashes"] = {"sig": ffd._verify_stored_identity(
            d, "sig_identity_hash", (w_truth_full, np.asarray(d["pass_truth"])), "signal")}
        meta["bootstrap"] = None
        w_truth, w_reco = w_truth_full[imc], w_reco_full[imc]
        mc = DataLoader(reco=reco_cloud, gen=gen_cloud, pass_reco=pass_reco,
                        pass_gen=pass_truth, weight=w_truth, weight_reco=w_reco, normalize=True,
                        normalization_factor=ffd.STEP1_MC_NORMALIZATION, reco_evt=event_reco,
                        gen_evt=event_truth, rank=0, size=1)
        meta["mc_only"] = True
        keys = list(d.keys_read)
    finally:
        d.close()
    unexpected = sorted(set(keys) - set(SIGNAL_MEMBERS))
    if unexpected:
        raise SystemExit(f"[confirm] the loader read unexpected members {unexpected}")
    return LoadedRows(mc, imc, tuple(coord_reco), tuple(coord_gen), meta, truth_scalars,
                      reco_scalars, part_gen[..., 4], w_truth, w_reco, keys)


# ------------------------------------------------------------------------------------------- #
# The closure
# ------------------------------------------------------------------------------------------- #
def truth_mapping(ffd: Any, truth_scalars: np.ndarray, pdg: np.ndarray | None) -> dict:
    cols = ffd.SCALAR_COLS
    t = np.asarray(truth_scalars, dtype=np.float64)
    out = {"pt": t[:, cols["pt"]], "ppar": t[:, cols["pparallel"]],
           "eavail": t[:, cols["eavail"]], "q3": t[:, cols["q3"]]}
    if pdg is not None:
        out.update({f"n_{k}": v for k, v in dist.count_species(pdg).items()})
    return out


def _subset(m: Mapping[str, np.ndarray], idx: np.ndarray) -> dict[str, np.ndarray]:
    return {k: np.asarray(v)[idx] for k, v in m.items()}


def assemble_closure(ffd: Any, loaded: LoadedRows, selection: Selection,
                     distortion: DistortionSpec, ClosureInputs: type) -> tuple[Any, dict]:
    """`closure_data.build_closure_inputs` (ours arm) on the selected rows. Returns the
    `ClosureInputs` and the per-row scoring arrays (`replicate_arrays.npz`)."""
    imc = loaded.rows
    mc = loaded.mc
    ia = np.searchsorted(imc, selection.pseudo_rows)
    ib = np.searchsorted(imc, selection.prior_rows)
    if not (np.array_equal(imc[ia], selection.pseudo_rows)
            and np.array_equal(imc[ib], selection.prior_rows)):
        raise SystemExit("[confirm] selected rows are not in the load set")
    if np.intersect1d(ia, ib).size:
        raise SystemExit("[confirm] prior and pseudodata overlap")
    reco, reco_evt = np.asarray(mc.reco), np.asarray(mc.reco_evt)
    gen, gen_evt = np.asarray(mc.gen), np.asarray(mc.gen_evt)
    pr = np.asarray(mc.pass_reco).astype(bool)
    pg = np.asarray(mc.pass_gen).astype(bool)
    w_truth = np.asarray(mc.weight, dtype=np.float64)
    w_reco = np.asarray(mc.weight_reco, dtype=np.float64)

    truth = truth_mapping(ffd, loaded.truth_scalars,
                          loaded.pdg if distortion.needs_species else None)
    pg_a = pg[ia]
    raw_a = distortion.raw(_subset(truth, ia[pg_a]))
    tilt_on_truth, mean_a = unit_mean(raw_a)
    tilt_a = np.ones(ia.size, dtype=np.float64)
    tilt_a[pg_a] = tilt_on_truth
    s1_a = pr[ia] & pg_a
    s1_b = pr[ib] & pg[ib]
    pdata = {"reco": reco[ia][s1_a], "reco_evt": reco_evt[ia][s1_a],
             "weight": ((w_reco[ia] * tilt_a)[s1_a]).astype(np.float32),
             "rows": imc[ia][s1_a].astype(np.int64)}
    mcb = {"reco": reco[ib], "reco_evt": reco_evt[ib], "gen": gen[ib], "gen_evt": gen_evt[ib],
           "pass_reco": s1_b, "pass_gen": pg[ib],
           "weight": w_truth[ib].astype(np.float32),
           "weight_reco": w_reco[ib].astype(np.float32),
           "rows": imc[ib].astype(np.int64)}

    # The oracle anchor: the exact distortion function on the PRIOR's truth-passing rows,
    # normalized the same way (unit mean over those rows).
    pg_b = pg[ib]
    oracle_b = np.ones(ib.size, dtype=np.float64)
    oracle_b[pg_b], mean_b = unit_mean(distortion.raw(_subset(truth, ib[pg_b])))

    tilt_spec = dict(distortion.record)
    tilt_spec.update({"pre_normalization_mean": mean_a, "n_injected_rows": int(pg_a.sum()),
                      "applied_on": "pass_truth rows of the pseudodata only",
                      "oracle_prior_pre_normalization_mean": mean_b})
    meta = {
        "n_evt_reco": int(loaded.meta["n_evt_reco"]), "n_evt_truth": int(loaded.meta["n_evt_truth"]),
        "coord_reco": tuple(int(c) for c in loaded.coord_reco),
        "coord_gen": tuple(int(c) for c in loaded.coord_gen),
        "half_size": None, "stage_rows": None, "split_census": None,
        "tilt_spec": tilt_spec,
        "dump_rows_a": imc[ia].astype(np.int64), "dump_rows_b": imc[ib].astype(np.int64),
        "tilt_a": tilt_a, "pass_gen_a": pg_a, "mc_indices": imc.astype(np.int64),
        "substitution": None, "step1_mc_normalization": ffd.STEP1_MC_NORMALIZATION,
        "selection": selection.record, "distortion": distortion.name,
        "distortion_hash": distortion.content_hash(), "members_read": loaded.keys_read,
    }
    cols = ffd.SCALAR_COLS
    ts = np.asarray(loaded.truth_scalars, np.float64)
    rs = np.asarray(loaded.reco_scalars, np.float64)
    arrays = {
        "pseudo_rows": imc[ia].astype(np.int64), "prior_rows": imc[ib].astype(np.int64),
        "pseudo_pass_truth": pg_a, "prior_pass_truth": pg_b,
        "pseudo_pass_reco": pr[ia], "prior_pass_reco": pr[ib],
        "pseudo_truth": ts[ia][:, [cols["pt"], cols["pparallel"], cols["eavail"], cols["q3"]]],
        "prior_truth": ts[ib][:, [cols["pt"], cols["pparallel"], cols["eavail"], cols["q3"]]],
        "pseudo_reco_eavail": rs[ia][:, cols["eavail"]],
        "prior_reco_eavail": rs[ib][:, cols["eavail"]],
        "pseudo_w_truth": np.asarray(loaded.w_truth_raw, np.float64)[ia],
        "prior_w_truth": np.asarray(loaded.w_truth_raw, np.float64)[ib],
        "pseudo_w_reco": np.asarray(loaded.w_reco_raw, np.float64)[ia],
        "prior_w_reco": np.asarray(loaded.w_reco_raw, np.float64)[ib],
        "pseudo_distortion": tilt_a, "prior_oracle": oracle_b,
    }
    return ClosureInputs(arm="ours", pdata=pdata, mc=mcb, meta=meta), arrays


def historical_cr() -> Any:
    """`characterize_regions`, loaded through Phase E's blob-checked historical import."""
    import common as cm
    return cm.historical()["cr"]


def region_codes(cr: Any, pt: np.ndarray, ppar: np.ndarray, populations_npz: Path) -> np.ndarray:
    """Historical region of each event's truth (pT, p||) cell under the historical acceptance map
    (B1's cached copy of `report_campaign.build_endpoint`'s map), as Phase E codes it."""
    import common as cm
    got = sha256_file(populations_npz)
    if got != cm.B1_POPULATIONS_SHA256:
        raise SystemExit(f"[confirm] B1 populations.npz sha256 {got} differs from the committed one")
    with np.load(populations_npz, allow_pickle=False) as b1:
        acceptance = np.asarray(b1["map_acceptance"], float)
        edges_pt = np.asarray(b1["edges_pt"], float)
        edges_pz = np.asarray(b1["edges_pz"], float)
    labels, _cell = cr.region_labels_for_events(pt, ppar, edges_pt, edges_pz, acceptance)
    return np.array([cm.REGION_CODES[x] for x in labels], dtype=np.int8)


def compare_inputs(np_: Any, ours: Any, reference: Any) -> dict[str, Any]:
    """Byte comparison of every array the engine receives (and the row lists)."""
    out: dict[str, Any] = {}
    for side in ("pdata", "mc"):
        a, b = getattr(ours, side), getattr(reference, side)
        for key in sorted(set(a) | set(b)):
            if key not in a or key not in b:
                out[f"{side}.{key}"] = "missing"
                continue
            x, y = np_.asarray(a[key]), np_.asarray(b[key])
            out[f"{side}.{key}"] = bool(x.dtype == y.dtype and x.shape == y.shape
                                        and sha256_bytes(x) == sha256_bytes(y))
    for key in ("dump_rows_a", "dump_rows_b", "tilt_a", "pass_gen_a", "coord_reco", "coord_gen"):
        x, y = np_.asarray(ours.meta[key]), np_.asarray(reference.meta[key])
        out[f"meta.{key}"] = bool(x.shape == y.shape and x.dtype == y.dtype
                                  and sha256_bytes(x) == sha256_bytes(y))
    out["all_equal"] = all(v is True for v in out.values())
    return out

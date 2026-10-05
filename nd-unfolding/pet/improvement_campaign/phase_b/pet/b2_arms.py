"""B2 input arms: named, versioned, hashed transforms of the closure inputs (no loader edits).

An arm declares, per OmniFold step, what is appended to (or re-encoded in) that step's inputs:

* step 1 (detector side): columns of `reco_scalars` and summaries of the STORED reco cloud
  (`stored_sumE`, `stored_n`: the energy sum and count of the <= 12 stored clusters). Nothing else is
  reachable: `apply` reads step-1 values only through `read_reco` / the reco cloud, and
  `assert_step1_reco_only` refuses any truth-named source before anything is read.
* step 2 (truth side): columns of `truth_scalars`, and the PDG encoding of the truth cloud.
  `pdg="raw"` leaves the executed historical column (raw PDG codes as a continuous input);
  `pdg="onehot"` replaces it by a one-hot of `PDG_CATEGORIES` (declared here, before any count
  was seen; everything unlisted goes to `other`) and re-indexes the KNN coordinates.

Appended scalars are standardized with the MC-half (half B) statistics over the rows that pass the
leg's selection, and set to 0 elsewhere -- the convention of `improvement_campaign/feature_arms.py`.
Non-finite values on the rows that pass are replaced by the median of the finite ones and COUNTED
(true q3 is non-finite on a few truth-passing rows; B1 `results/truth_learnability.json`).

The hash covers the declaration and the source of every function that transforms inputs, so a run
config naming an arm names exactly one transform. The model code (`omnifold_nn/omnifold/net.py`)
is untouched: the one-hot enters as ordinary cloud columns.
"""

from __future__ import annotations

import hashlib
import inspect
import json
from dataclasses import asdict, dataclass
from typing import Any, Callable

RECO_SCALAR_COLUMNS = ("pt", "pparallel", "eavail", "q3")
TRUTH_SCALAR_COLUMNS = ("pt", "pparallel", "eavail", "q3")
RECO_CLOUD_SUMMARIES = ("stored_sumE", "stored_n")

# Physics categories of truth final-state particles (the muon and neutrinos are removed upstream,
# FEATURE_INVENTORY §3). |PDG| unless the sign is itself the category (pions).
PDG_CATEGORIES: tuple = (
    ("proton", (2212,)),
    ("neutron", (2112,)),
    ("pi_plus", (211,)),
    ("pi_minus", (-211,)),
    ("pi_zero", (111,)),
    ("photon", (22,)),
    ("kaon_charged", (321, -321)),
    ("kaon_neutral", (311, -311, 130, 310)),
    ("antinucleon", (-2212, -2112)),
    ("hyperon", (3122, -3122, 3222, -3222, 3212, -3212, 3112, -3112, 3322, 3312, 4122)),
    ("electron", (11, -11)),
    ("nucleus", ()),       # PDG >= 1_000_000_000 (ions / nuclear fragments)
    ("other", ()),         # anything else
)
TRUTH_PDG_COLUMN = 4       # fullevent_fps_dataloader.build_truth_cloud: (E,px,py,pz,pdg,theta,cphi,sphi)


@dataclass(frozen=True)
class InputArm:
    name: str
    version: int
    description: str
    step1_reco_scalars: tuple = ()
    step1_cloud_summaries: tuple = ()
    step2_truth_scalars: tuple = ()
    pdg: str = "raw"

    def content_hash(self) -> str:
        sources = {f.__name__: inspect.getsource(f) for f in (
            apply, pdg_category_index, pdg_onehot_cloud, stored_cloud_summaries, _standardize,
            _median_fill, assert_step1_reco_only)}
        payload = json.dumps({"declaration": asdict(self), "sources": sources,
                              "pdg_categories": PDG_CATEGORIES}, sort_keys=True)
        return hashlib.sha256(payload.encode()).hexdigest()


REGISTRY: dict[str, InputArm] = {arm.name: arm for arm in (
    InputArm("baseline", 1, "the historical inputs, unchanged (raw PDG, truth globals pT, p||)"),
    InputArm("pdg_onehot", 1, "T1 / step 2: PDG as a one-hot of physics categories",
             pdg="onehot"),
    InputArm("pdg_onehot_truthglobals", 1, "T2 / C3: T1 + true E_avail and q3 as step-2 globals",
             step2_truth_scalars=("eavail", "q3"), pdg="onehot"),
    InputArm("truthglobals", 1, "true E_avail and q3 as step-2 globals, raw PDG",
             step2_truth_scalars=("eavail", "q3")),
    InputArm("reco_summaries", 1,
             "C2 / step 1: reco E_avail, reco q3 (recoil), stored-cluster energy sum and count",
             step1_reco_scalars=("eavail", "q3"),
             step1_cloud_summaries=("stored_sumE", "stored_n")),
    InputArm("reco_summaries_pdg_onehot", 1, "C2 with the T1 truth side",
             step1_reco_scalars=("eavail", "q3"),
             step1_cloud_summaries=("stored_sumE", "stored_n"), pdg="onehot"),
    InputArm("reco_summaries_pdg_onehot_truthglobals", 1, "C4 with the T1 truth side: C2 + C3",
             step1_reco_scalars=("eavail", "q3"),
             step1_cloud_summaries=("stored_sumE", "stored_n"),
             step2_truth_scalars=("eavail", "q3"), pdg="onehot"),
    InputArm("reco_summaries_truthglobals", 1, "C4 with the raw-PDG truth side",
             step1_reco_scalars=("eavail", "q3"),
             step1_cloud_summaries=("stored_sumE", "stored_n"),
             step2_truth_scalars=("eavail", "q3")),
)}


def get(name: str) -> InputArm:
    if name not in REGISTRY:
        raise KeyError(f"unknown B2 input arm {name!r}; known: {sorted(REGISTRY)}")
    return REGISTRY[name]


def assert_step1_reco_only(arm: InputArm) -> None:
    """No truth quantity may enter the detector-side classifier (scope §5 C)."""
    for column in arm.step1_reco_scalars:
        if column not in RECO_SCALAR_COLUMNS:
            raise ValueError(f"step-1 column {column!r} is not a reco_scalars column")
    for summary in arm.step1_cloud_summaries:
        if summary not in RECO_CLOUD_SUMMARIES:
            raise ValueError(f"step-1 summary {summary!r} is not a reco-cloud summary")
    names = " ".join(arm.step1_reco_scalars + arm.step1_cloud_summaries).lower()
    if "truth" in names or "true" in names or "gen" in names.split():
        raise ValueError("a truth-named source reached the step-1 declaration")


def pdg_category_index(np: Any, pdg: Any) -> Any:
    """Category index per token (int16); padded tokens (pdg == 0) get -1."""
    pdg = np.asarray(pdg)
    code = np.rint(pdg).astype(np.int64)
    out = np.full(code.shape, -1, dtype=np.int16)
    names = [name for name, _ in PDG_CATEGORIES]
    real = code != 0
    assigned = np.zeros(code.shape, dtype=bool)
    for index, (name, codes) in enumerate(PDG_CATEGORIES):
        if name == "nucleus":
            hit = real & (code >= 1_000_000_000)
        elif name == "other":
            continue
        else:
            hit = real & np.isin(code, np.asarray(codes, dtype=np.int64))
        hit &= ~assigned
        out[hit] = index
        assigned |= hit
    out[real & ~assigned] = names.index("other")
    return out


def pdg_onehot_cloud(np: Any, cloud: Any, coord_idx: tuple) -> tuple[Any, tuple, dict[str, Any]]:
    """Replace the raw PDG column by a one-hot of `PDG_CATEGORIES` (zeros on padded tokens)."""
    cloud = np.asarray(cloud, dtype=np.float32)
    col = TRUTH_PDG_COLUMN
    index = pdg_category_index(np, cloud[..., col])
    real = cloud[..., 0] != 0
    if bool(((index >= 0) != real).any()):
        raise ValueError("the PDG column's padding disagrees with the energy pad mask")
    onehot = np.zeros(cloud.shape[:2] + (len(PDG_CATEGORIES),), dtype=np.float32)
    rows, toks = np.nonzero(index >= 0)
    onehot[rows, toks, index[rows, toks]] = 1.0
    kept = [c for c in range(cloud.shape[-1]) if c != col]
    out = np.concatenate([cloud[..., kept], onehot], axis=-1)
    new_coord = tuple(kept.index(c) for c in coord_idx)
    counts = np.bincount(index[index >= 0].astype(np.int64), minlength=len(PDG_CATEGORIES))
    raw_other = np.unique(np.rint(cloud[..., col][index == len(PDG_CATEGORIES) - 1])
                          .astype(np.int64), return_counts=True)
    census = {"category_token_counts": {name: int(n) for (name, _), n in
                                        zip(PDG_CATEGORIES, counts)},
              "other_codes": {int(c): int(n) for c, n in zip(*raw_other)},
              "columns_after": cloud.shape[-1] - 1 + len(PDG_CATEGORIES),
              "coord_idx_before": list(coord_idx), "coord_idx_after": list(new_coord)}
    return out, new_coord, census


def stored_cloud_summaries(np: Any, reco_cloud: Any) -> dict[str, Any]:
    """Energy sum (GeV) and count of the stored reco clusters (column 0 = E, 0 = padding)."""
    energy = np.asarray(reco_cloud, dtype=np.float64)[..., 0]
    return {"stored_sumE": energy.sum(axis=1), "stored_n": (energy != 0).sum(axis=1)
            .astype(np.float64)}


def _median_fill(np: Any, values: Any, mask: Any) -> tuple[Any, int]:
    values = np.asarray(values, dtype=np.float64).copy()
    mask = np.asarray(mask, bool)
    bad = mask & ~np.isfinite(values)
    if bad.any():
        values[bad] = float(np.median(values[mask & np.isfinite(values)]))
    return values, int(bad.sum())


def _standardize(np: Any, values: Any, mask_fit: Any, *others: tuple) -> tuple[list[Any], dict]:
    ref = np.asarray(values, dtype=np.float64)[np.asarray(mask_fit, bool)]
    mu, sd = float(ref.mean()), float(ref.std())
    if not np.isfinite(sd) or sd <= 0:
        raise ValueError("an appended feature is constant or non-finite on the MC half")
    out = []
    for arr, mask in ((values, mask_fit), *others):
        z = (np.asarray(arr, dtype=np.float64) - mu) / sd
        out.append(np.where(np.asarray(mask, bool), z, 0.0).astype(np.float32))
    return out, {"mean": mu, "std": sd}


def apply(arm: InputArm, blocks: dict[str, Any], read_reco: Callable[[str, Any], Any],
          read_truth: Callable[[str, Any], Any], np: Any) -> dict[str, Any]:
    """Return new blocks with the arm's inputs.

    `blocks`: `pdata_reco`, `pdata_reco_evt`, `mc_reco`, `mc_reco_evt`, `mc_gen`, `mc_gen_evt`,
    `coord_gen`, row ids `pdata_rows`, `mc_rows`, masks `pdata_pass_reco`, `mc_pass_reco`,
    `mc_pass_gen`; optionally `extra_gen` = {name: (gen, gen_evt, rows, pass_gen)} for other
    truth populations that must see the SAME transform (truth-only mode: half A).
    """
    assert_step1_reco_only(arm)
    out = dict(blocks)
    record: dict[str, Any] = {"arm": arm.name, "arm_hash": arm.content_hash(), "step1": [],
                              "step2": [], "standardization": {}, "nonfinite_filled": {}}
    extra = dict(blocks.get("extra_gen") or {})
    # ---- step 1: reco scalars and stored-cloud summaries (reco only) ---------------------- #
    step1_sources = [(f"reco_scalars:{c}", lambda rows, c=c: read_reco(c, rows))
                     for c in arm.step1_reco_scalars]
    if arm.step1_cloud_summaries:
        s_mc = stored_cloud_summaries(np, blocks["mc_reco"])
        s_pd = stored_cloud_summaries(np, blocks["pdata_reco"])
        for name in arm.step1_cloud_summaries:
            step1_sources.append((f"reco_cloud:{name}", (s_mc[name], s_pd[name])))
    for label, source in step1_sources:
        if callable(source):
            mc_vals, pd_vals = source(blocks["mc_rows"]), source(blocks["pdata_rows"])
        else:
            mc_vals, pd_vals = source
        mc_vals, n_mc = _median_fill(np, mc_vals, blocks["mc_pass_reco"])
        pd_vals, n_pd = _median_fill(np, pd_vals, blocks["pdata_pass_reco"])
        (mc_z, pd_z), stats = _standardize(np, mc_vals, blocks["mc_pass_reco"],
                                           (pd_vals, blocks["pdata_pass_reco"]))
        out["mc_reco_evt"] = np.concatenate([out["mc_reco_evt"], mc_z[:, None]], axis=1)
        out["pdata_reco_evt"] = np.concatenate([out["pdata_reco_evt"], pd_z[:, None]], axis=1)
        record["step1"].append(label)
        record["standardization"][label] = stats
        record["nonfinite_filled"][label] = {"mc": n_mc, "pdata": n_pd}
    # ---- step 2: truth scalars ------------------------------------------------------------- #
    for column in arm.step2_truth_scalars:
        label = f"truth_scalars:{column}"
        vals, n_bad = _median_fill(np, read_truth(column, blocks["mc_rows"]),
                                   blocks["mc_pass_gen"])
        others = []
        extra_vals = {}
        for name, (_g, _ge, rows, pg) in extra.items():
            ev, n_ev = _median_fill(np, read_truth(column, rows), pg)
            extra_vals[name] = n_ev
            others.append((ev, pg))
        zs, stats = _standardize(np, vals, blocks["mc_pass_gen"], *others)
        out["mc_gen_evt"] = np.concatenate([out["mc_gen_evt"], zs[0][:, None]], axis=1)
        for (name, (g, ge, rows, pg)), z in zip(list(extra.items()), zs[1:]):
            extra[name] = (g, np.concatenate([ge, z[:, None]], axis=1), rows, pg)
        record["step2"].append(label)
        record["standardization"][label] = stats
        record["nonfinite_filled"][label] = {"mc": n_bad, **extra_vals}
    # ---- step 2: PDG encoding -------------------------------------------------------------- #
    if arm.pdg == "onehot":
        coord = tuple(blocks["coord_gen"])
        out["mc_gen"], out["coord_gen"], census = pdg_onehot_cloud(np, blocks["mc_gen"], coord)
        record["pdg_census_mc"] = census
        for name, (g, ge, rows, pg) in list(extra.items()):
            g2, coord2, census2 = pdg_onehot_cloud(np, g, coord)
            if coord2 != out["coord_gen"]:
                raise ValueError("coordinate re-indexing differs between populations")
            extra[name] = (g2, ge, rows, pg)
            record[f"pdg_census_{name}"] = census2
        record["step2"].append("truth_cloud:pdg_onehot")
    elif arm.pdg != "raw":
        raise ValueError(f"unknown pdg encoding {arm.pdg!r}")
    out["extra_gen"] = extra
    out["record"] = record
    return out

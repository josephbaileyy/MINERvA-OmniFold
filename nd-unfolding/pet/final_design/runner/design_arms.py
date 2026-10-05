"""Study input arms: the predecessor's B2 registry, extended (never edited) by the study's arms.

`get(name)` returns a predecessor arm (`improvement_campaign/phase_b/pet/b2_arms.REGISTRY`,
applied by the predecessor's `b2_driver.apply_arm`, unchanged) or one of the arms declared here.

`pdg_onehot_counts` (PROTOCOL-20260925 section 5, "explicit truncated-cloud species counts as
truth-step globals"): the `pdg_onehot` arm, plus six step-2 event globals counted over the stored
12-token truth cloud -- protons (|PDG| 2212), neutrons (2112), charged pions (211), neutral pions
(111), every other real token, and the number of real tokens (energy column != 0). These are
**truncated-cloud counts**, exactly the counts of `final_design/diagnostics/build_row_features.py`
and of the predecessor's D4 distortions (`phase_e/distortions.count_species`), i.e. what PET's truth
step already receives token by token. Each count is standardized with the prior's (the MC's)
truth-passing rows and set to 0 elsewhere -- the B2 convention (`b2_arms._standardize`). Detector
side: untouched.
"""

from __future__ import annotations

import hashlib
import inspect
import json
import sys
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Callable

HERE = Path(__file__).resolve().parent
B2DIR = HERE.parent.parent / "improvement_campaign" / "phase_b" / "pet"
if str(B2DIR) not in sys.path:
    sys.path.insert(0, str(B2DIR))

import b2_arms  # noqa: E402

# Species of the truncated-cloud counts (|PDG|); `other` = any other real token.
COUNT_SPECIES: tuple = (("n_proton", 2212), ("n_neutron", 2112), ("n_charged_pion", 211),
                        ("n_neutral_pion", 111))
COUNT_NAMES = tuple(n for n, _ in COUNT_SPECIES) + ("n_other", "n_valid")
ENERGY_COLUMN = 0


@dataclass(frozen=True)
class CountsArm:
    """A predecessor B2 arm (`base`) plus truncated-cloud species counts as step-2 globals."""
    name: str
    version: int
    description: str
    base: str
    step2_species_counts: tuple = COUNT_NAMES

    def content_hash(self) -> str:
        sources = {f.__name__: inspect.getsource(f) for f in (species_counts, apply_counts)}
        payload = json.dumps({"declaration": asdict(self), "sources": sources,
                              "count_species": COUNT_SPECIES,
                              "base_arm_hash": b2_arms.get(self.base).content_hash()},
                             sort_keys=True)
        return hashlib.sha256(payload.encode()).hexdigest()


REGISTRY: dict[str, CountsArm] = {arm.name: arm for arm in (
    CountsArm("pdg_onehot_counts", 1,
              "pdg_onehot + truncated-cloud species counts (p, n, pi+-, pi0, other, n_valid) as "
              "step-2 globals, standardized on the prior", base="pdg_onehot"),
)}


def get(name: str) -> Any:
    """A study arm, else the predecessor's B2 arm of that name."""
    if name in REGISTRY:
        return REGISTRY[name]
    if name in b2_arms.REGISTRY:
        return b2_arms.get(name)
    raise KeyError(f"unknown input arm {name!r}; known: {sorted(REGISTRY) + sorted(b2_arms.REGISTRY)}")


def species_counts(np: Any, cloud: Any) -> dict[str, Any]:
    """Per event: counts over the real tokens (energy != 0) of the RAW truth cloud (PDG in
    `b2_arms.TRUTH_PDG_COLUMN`, before any one-hot), float64."""
    cloud = np.asarray(cloud)
    real = cloud[..., ENERGY_COLUMN] != 0
    code = np.abs(np.rint(np.asarray(cloud[..., b2_arms.TRUTH_PDG_COLUMN], np.float64))
                  ).astype(np.int64)
    if bool(((code != 0) != real).any()):
        raise ValueError("the PDG column's padding disagrees with the energy pad mask")
    out, known = {}, np.zeros(real.shape, dtype=bool)
    for name, pdg in COUNT_SPECIES:
        hit = real & (code == pdg)
        known |= hit
        out[name] = hit.sum(axis=1).astype(np.float64)
    out["n_other"] = (real & ~known).sum(axis=1).astype(np.float64)
    out["n_valid"] = real.sum(axis=1).astype(np.float64)
    return out


def apply_counts(arm: CountsArm, np: Any, raw_gen: Any, gen_evt: Any, pass_gen: Any,
                 extra: dict[str, tuple] | None = None) -> tuple[Any, dict, dict]:
    """Append the standardized counts to `gen_evt` (prior) and to each extra population's
    `gen_evt` with the SAME (prior) statistics. `extra`: {name: (raw_gen, gen_evt, pass_gen)}."""
    extra = dict(extra or {})
    counts = species_counts(np, raw_gen)
    extra_counts = {k: species_counts(np, g) for k, (g, _ge, _pg) in extra.items()}
    record: dict[str, Any] = {"step2": [], "standardization": {}, "census_prior_truth_passing": {}}
    new_extra = {k: ge for k, (_g, ge, _pg) in extra.items()}
    mask = np.asarray(pass_gen, bool)
    for name in arm.step2_species_counts:
        others = [(extra_counts[k][name], extra[k][2]) for k in extra]
        zs, stats = b2_arms._standardize(np, counts[name], mask, *others)
        gen_evt = np.concatenate([gen_evt, zs[0][:, None]], axis=1)
        for k, z in zip(list(extra), zs[1:]):
            new_extra[k] = np.concatenate([new_extra[k], z[:, None]], axis=1)
        label = f"truth_cloud_counts:{name}"
        record["step2"].append(label)
        record["standardization"][label] = stats
        v = counts[name][mask]
        record["census_prior_truth_passing"][name] = {
            "mean": float(v.mean()), "max": float(v.max()),
            "histogram_0_to_12": np.bincount(v.astype(np.int64), minlength=13)[:13].tolist()}
    return gen_evt, new_extra, record


def apply_arm(np: Any, arm: Any, inputs: Any, read: Callable, half_a: dict | None,
              b2d: Any) -> dict[str, Any]:
    """`b2_driver.apply_arm` for a predecessor arm; for a study arm, the base arm through the same
    function, then the counts (computed from the truth cloud BEFORE the base arm re-encodes it)."""
    if not isinstance(arm, CountsArm):
        return b2d.apply_arm(np, arm, inputs, read, half_a)
    raw_gen = inputs.mc["gen"]
    raw_half_a = None if half_a is None else half_a["gen"]
    base_record = b2d.apply_arm(np, b2_arms.get(arm.base), inputs, read, half_a)
    extra = ({} if half_a is None else
             {"half_a": (raw_half_a, half_a["gen_evt"], half_a["pass_gen"])})
    gen_evt, new_extra, record = apply_counts(arm, np, raw_gen, inputs.mc["gen_evt"],
                                              inputs.mc["pass_gen"], extra)
    inputs.mc["gen_evt"] = gen_evt
    if half_a is not None:
        half_a["gen_evt"] = new_extra["half_a"]
    return {"arm": arm.name, "arm_hash": arm.content_hash(), "base_arm": arm.base,
            "base_record": base_record, **record}

"""The named configurations, and a refusal to let a degraded one wear a real name.

Three failures this exists to prevent, all of them the same failure at different
points in a sentence.

**Calling the runnable arm "Gregor's configuration".** What runs today is his
architecture fed our 5- and 8-column clouds, our 13- and 2-wide event blocks, no
PID, no auxiliary channel and a 12-token cap. His complete arm has 4 kinematic
columns plus a PID embedding, 5 auxiliary columns, 16 globals and a 33-token cap,
and `checkpoint_transfer` shows the difference is not cosmetic: the degraded arm
reinitialises the entire input interface, so the pretrained backbone downstream
reads a coordinate system it was never trained on. A result from that arm is a
result about a different model.

**Losing track of which of ours is the incumbent.** `OURS_INCUMBENT` is the
promoted production estimator. Any change to it -- more heads, a larger cap, a
different neighbourhood -- produces a CANDIDATE, which must be declared with a
parent and a reason before it can be compared. Otherwise "ours" silently becomes
whichever variant happened to win, and the comparison stops being against the
thing we actually run.

**Letting a blocked arm look runnable.** Each configuration carries its own
blockers. `runnable_today` is computed from them, not asserted.

NOT CITABLE FOR any performance claim.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Mapping


@dataclass(frozen=True)
class Configuration:
    """One named configuration, with its provenance and its blockers."""

    name: str
    owner: str
    status: str
    architecture: Mapping[str, Any]
    inputs: Mapping[str, Any]
    recipe: Mapping[str, Any]
    provenance: str
    blockers: tuple[str, ...] = ()
    parent: str | None = None
    rationale: str | None = None

    @property
    def runnable_today(self) -> bool:
        return not self.blockers

    def summary(self) -> dict[str, Any]:
        return {
            "name": self.name, "owner": self.owner, "status": self.status,
            "architecture": dict(self.architecture), "inputs": dict(self.inputs),
            "recipe": dict(self.recipe), "provenance": self.provenance,
            "blockers": list(self.blockers), "runnable_today": self.runnable_today,
            "parent": self.parent, "rationale": self.rationale,
        }


# ---------------------------------------------------------------------------
# Ours. The promoted production estimator, and nothing else, is the incumbent.
# ---------------------------------------------------------------------------
OURS_INCUMBENT = Configuration(
    name="ours_incumbent",
    owner="us",
    status="PROMOTED_INCUMBENT",
    architecture={
        "model": "omnifold.net.PET",
        "num_heads": 2, "num_transformer": 2, "projection_dim": 32,
        "local": True, "K": 3,
        "step1": {"num_feat": 5, "num_evt": 13, "coord_idx": (1, 2)},
        "step2": {"num_feat": 8, "num_evt": 2, "coord_idx": (5, 6, 7)},
        "trainable_parameters": {"step1": 47_041, "step2": 46_913},
    },
    inputs={
        "token_cap": 12,
        "reco_columns": ("E", "pos", "z", "view", "time"),
        "truth_columns": ("E", "px", "py", "pz", "pdg", "theta", "cos_phi", "sin_phi"),
        "pad_authority": "energy, column 0",
        "pid_channel": False, "auxiliary_channel": False,
    },
    recipe={
        "optimizer": "tf.keras.optimizers.Adam via MultiFold.get_optimizer",
        "batch_size": 512, "niter": 3, "epochs": 8,
        "lr_policy": "LR_POLICY_ANNEALED (engine drop between iterations)",
        "gradient_clipping": None,
    },
    provenance="train_fullevent_nominal.NOMINAL_SEED_POLICY and :403-407",
)

# ---------------------------------------------------------------------------
# His. The complete arm is the objective; the degraded one is not his arm.
# ---------------------------------------------------------------------------
THEIRS_COMPLETE = Configuration(
    name="theirs_complete_pretrained",
    owner="Gregor",
    status="INTENDED_COMPLETE",
    architecture={
        "model": "OmniLearned PET2, preset small",
        "num_transformers": 8, "num_transformers_head": 2, "num_tokens": 4,
        "num_heads": 8, "base_dim": 128, "mlp_ratio": 2,
        "use_int": False, "local_int": False,
        "trainable_parameters": 2_758_702,
    },
    inputs={
        "token_cap": 33,
        "kinematic_columns": ("eta", "phi", "log_pT", "log_E"),
        "pid_channel": True, "pid_classes": 8,
        "auxiliary_channel": True, "auxiliary_columns": ("dEdx", "x", "y", "z", "t"),
        "globals": 16, "zero_cond_feature": 2,
    },
    recipe={
        "optimizer": "torch.optim.AdamW, one param group",
        "learning_rate": 1e-4, "weight_decay": 0.01,
        "batch_size": 2048, "grad_accum_steps": 1,
        "schedule": "linear warmup then cosine, max_steps DERIVED from the fair budget",
        "gradient_clipping": "global norm 1.0 (clip_grad_norm_)",
        "attention_backend": "math SDPA required at 33 tokens and batch 2048",
        "initialisation": "best_model_pretrain_s.pt",
    },
    provenance="plot_configs/V1Paper.json + submit_train_jobs.py:155-169 (OLS)",
    blockers=(
        "R2: best_model_pretrain_s.pt is unreachable (CFS m4567)",
        "R-1/R-2: no PID or auxiliary channel exists in our dump",
        "globals: his 16 event-level features are not exported",
        "cap: our dump truncates at 12 tokens, not 33",
    ),
)

THEIRS_DEGRADED = Configuration(
    name="theirs_architecture_on_our_inputs",
    owner="us",
    status="DEGRADED_NOT_HIS_CONFIGURATION",
    architecture=dict(THEIRS_COMPLETE.architecture),
    inputs={
        "token_cap": 12,
        "step1": {"num_feat": 5, "num_evt": 13, "coord_idx": (1, 2)},
        "step2": {"num_feat": 8, "num_evt": 2, "coord_idx": (5, 6, 7)},
        "pid_channel": False, "auxiliary_channel": False, "globals": None,
    },
    recipe=dict(THEIRS_COMPLETE.recipe, initialisation="random (scratch)"),
    provenance="what pet2_omnifold_adapter builds today",
    parent="theirs_complete_pretrained",
    rationale=(
        "the only arm runnable before the export and the checkpoint land. Retained "
        "for plumbing validation and cost calibration ONLY. It reinitialises the "
        "entire input interface, so it is not a transfer result and not his "
        "configuration."
    ),
)

REGISTRY: dict[str, Configuration] = {
    c.name: c for c in (OURS_INCUMBENT, THEIRS_COMPLETE, THEIRS_DEGRADED)
}

# What "his complete arm" means, as a checkable list rather than a sentence.
IDENTITY_REQUIREMENTS = ("pid_channel", "auxiliary_channel", "globals", "token_cap")
REQUIRED_CAP = 33


def identity_gaps(configuration: Configuration) -> list[str]:
    """Which parts of his intended identity a configuration fails to carry."""
    gaps = []
    inputs = configuration.inputs
    if not inputs.get("pid_channel"):
        gaps.append("pid_channel absent")
    if not inputs.get("auxiliary_channel"):
        gaps.append("auxiliary_channel absent")
    if not inputs.get("globals"):
        gaps.append("event globals absent")
    if inputs.get("token_cap") != REQUIRED_CAP:
        gaps.append(f"token cap {inputs.get('token_cap')} != {REQUIRED_CAP}")
    return gaps


def require_his_complete_arm(configuration: Configuration) -> None:
    """Refuse to treat anything but the complete arm as his configuration.

    Called wherever a result is about to be attributed to Gregor's method. The
    degraded arm is a legitimate object; it is just not that one.
    """
    gaps = identity_gaps(configuration)
    if gaps:
        raise ValueError(
            f"{configuration.name!r} is not Gregor's complete arm: {'; '.join(gaps)}. "
            "A result from it is a result about his architecture on our inputs, and "
            "must be reported under that description."
        )


def declare_candidate(name: str, changes: Mapping[str, Any], rationale: str,
                      parent: Configuration = OURS_INCUMBENT) -> Configuration:
    """Register an improved version of ours as a CANDIDATE, never as the incumbent.

    A change to our configuration that is not declared here silently redefines
    "ours", and the comparison stops being against what we run.
    """
    if not rationale or not rationale.strip():
        raise ValueError("a candidate needs a rationale; an undeclared change is a drift")
    if name in REGISTRY:
        raise ValueError(f"{name!r} is already registered")
    if not changes:
        raise ValueError("a candidate that changes nothing is the incumbent")
    candidate = Configuration(
        name=name, owner="us", status="CANDIDATE_NOT_PROMOTED",
        architecture={**parent.architecture, **changes.get("architecture", {})},
        inputs={**parent.inputs, **changes.get("inputs", {})},
        recipe={**parent.recipe, **changes.get("recipe", {})},
        provenance=f"declared candidate, parent {parent.name}",
        parent=parent.name, rationale=rationale,
    )
    REGISTRY[name] = candidate
    return candidate


def incumbent() -> Configuration:
    """The single promoted configuration. There is exactly one."""
    promoted = [c for c in REGISTRY.values() if c.status == "PROMOTED_INCUMBENT"]
    if len(promoted) != 1:
        raise RuntimeError(f"expected exactly one incumbent, found {len(promoted)}")
    return promoted[0]

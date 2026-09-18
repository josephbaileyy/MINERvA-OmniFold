"""Count trainable parameters in our production PET and in Gregor's transformer.

Capacity is the one architectural quantity that is directly comparable across two
frameworks, so it is measured here rather than inferred from the width and depth
printed in a table. Both models are instantiated at the configuration each project
actually trains, and the count comes from the built graph.

Two honesty constraints are wired in rather than left to the writer:

* The counts are *backbone* counts at a stated configuration. They are not a claim
  that one model is better sized for this problem -- capacity is not accuracy, and
  a 19x parameter ratio between a TensorFlow reweighting classifier and a PyTorch
  regression backbone is not a like-for-like efficiency statement.
* Our PET is counted per model. OmniFold trains two of them per iteration (step 1
  on reco, step 2 on gen), so the per-iteration parameter count is twice the number
  reported for one PET, and the script says so in the receipt instead of leaving a
  reader to halve or double it.

The production PET is Keras-2 code; on a Keras-3 TensorFlow it only builds under
``TF_USE_LEGACY_KERAS=1``. The script sets that itself so the measurement does not
silently depend on the caller's environment.
"""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
from typing import Any

os.environ.setdefault("TF_USE_LEGACY_KERAS", "1")
os.environ.setdefault("CUDA_VISIBLE_DEVICES", "")
os.environ.setdefault("TF_CPP_MIN_LOG_LEVEL", "3")

# Our production configuration, read from train_fullevent_nominal.py's MultiFold
# model construction rather than from the PET class defaults, which differ.
PRODUCTION_PET = {
    "num_heads": 2,
    "num_transformer": 2,
    "projection_dim": 32,
    "local": True,
    "K": 3,
}
RECO_MODEL = {"num_feat": 5, "num_evt": 13, "num_part": 12}
GEN_MODEL = {"num_feat": 8, "num_evt": 2, "num_part": 12}

# Gregor's Transformer1 settings, from src/jobs/submit_train_jobs.py, with the
# point/global widths his dataset actually produces (10 saved columns = 9
# continuous + 1 PID; 16 global features).
GREGOR_VIT = {
    "point_cont_dim": 9,
    "point_cat_num_classes": [8],
    "global_cont_dim": 16,
    "global_cat_num_classes": [],
    "coord_dim": 2,
    "d_model": 128,
    "depth": 4,
    "n_heads": 8,
    "use_cls_token": True,
    "use_event_token": True,
}


def count_our_pet(repo: Path, spec: dict[str, int]) -> int:
    """Build one production PET and total its trainable weights."""
    import sys

    root = repo / "omnifold_nn"
    if not root.is_dir():
        raise ValueError(f"Not a directory: {root}")
    if str(root) not in sys.path:
        sys.path.insert(0, str(root))
    import numpy as np
    from omnifold.net import PET

    model = PET(**spec, **PRODUCTION_PET)
    return int(sum(int(np.prod(w.shape)) for w in model.trainable_weights))


def count_gregor_vit(checkout: Path) -> int:
    """Build Gregor's PointGlobalMixedViT backbone and total its parameters."""
    import sys

    if not (checkout / "src" / "models" / "vit.py").is_file():
        raise ValueError(f"Not a minerva-ml checkout: {checkout}")
    if str(checkout) not in sys.path:
        sys.path.insert(0, str(checkout))
    from src.models.vit import PointGlobalMixedViT, PointGlobalMixedViTConfig

    model = PointGlobalMixedViT(PointGlobalMixedViTConfig(**GREGOR_VIT))
    return int(sum(p.numel() for p in model.parameters()))


def main() -> None:
    """Measure both capacities and write one receipt."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", type=Path, required=True)
    parser.add_argument("--gregor-checkout", type=Path, required=True)
    parser.add_argument("--gregor-commit", required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    reco = count_our_pet(args.repo, RECO_MODEL)
    gen = count_our_pet(args.repo, GEN_MODEL)
    gregor = count_gregor_vit(args.gregor_checkout)

    receipt: dict[str, Any] = {
        "scope": "trainable-parameter counts at each project's own training configuration",
        "ours": {
            "source": "nd-unfolding/pet/train_fullevent_nominal.py (MultiFold model construction)",
            "architecture": PRODUCTION_PET,
            "step1_reco_model": {"inputs": RECO_MODEL, "trainable_parameters": reco},
            "step2_gen_model": {"inputs": GEN_MODEL, "trainable_parameters": gen},
            "parameters_per_omnifold_iteration": reco + gen,
        },
        "gregors": {
            "source": "src/models/vit.py + src/jobs/submit_train_jobs.py (Transformer1)",
            "commit": args.gregor_commit,
            "configuration": GREGOR_VIT,
            "trainable_parameters_backbone": gregor,
            "note": "backbone only; the task head is one linear layer and is excluded",
        },
        "ratio_gregor_over_our_step1": gregor / reco,
        "non_claim": (
            "Capacity is not accuracy. These two models solve different problems -- "
            "ours is a binary reweighting classifier inside OmniFold, his is a "
            "supervised regressor/classifier -- so the ratio measures size, not "
            "efficiency, suitability, or quality."
        ),
    }
    args.output.write_text(json.dumps(receipt, indent=2) + "\n")
    print(f"ours step1 {reco:,}  step2 {gen:,}  gregor {gregor:,}")
    print(f"ratio gregor/ours(step1): {gregor / reco:.1f}x")


if __name__ == "__main__":
    main()

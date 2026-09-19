"""Which checkpoint tensors reach each OmniFold step, which do not, and why.

Running the port on synthetic arrays of some width proves the code executes. It
says nothing about whether a pretrained tensor can be *loaded* into it, because
that is a question about shapes, and shapes are decided by the configuration each
side was built at. This answers it tensor by tensor.

WHAT THE LOADER ACTUALLY DOES (`omnilearned/utils.py:38-56`, `:58-104`). The
checkpoint is a dict with `body`, `classifier_head` and `generator_head`. Each is
filtered against the target's `state_dict()` by `_filter_partial_state`, which
drops a key when (a) the name contains `"out."`, (b) the target has no such key, or
(c) the shapes differ -- then loads with `strict=False`. Everything dropped stays
at its fresh initialisation. Nothing warns loudly; the function prints and moves on.
So a badly matched configuration does not fail, it silently trains from scratch in
the parts that matter most.

THREE TARGETS ARE ANALYSED, because they answer different questions.

* `his_complete` -- his intended arm: 4 kinematic columns, PID, 5 auxiliary
  columns, 16 globals, cap 33. This is the configuration whose identity we are
  required to preserve, and the one the checkpoint was built for.
* `ours_step1` / `ours_step2` -- the DEGRADED arm that is runnable today, before
  the typed-object export lands: our 5- and 8-column clouds with 13 and 2 globals
  and no PID or auxiliary block. Quantifies what a comparison run now would lose.

A CAVEAT THAT CANNOT BE MEASURED WITHOUT THE FILE. The source shapes here are
derived from `PET2` built at his configuration, not read from
`best_model_pretrain_{s,m}.pt`. That is exact for everything determined by the
architecture, but `cond_dim`, `add_dim`, `pid_dim` and `input_dim` are properties
of the PRETRAINING dataset, not of the fine-tuning one, and OmniLearned pretrained
on something else. If they differ, the corresponding tensors silently fail to load
in his runs too. This is a question for Gregor, and it is in the draft.

NOT CITABLE FOR any claim that a transfer succeeded; no checkpoint has been read.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
from typing import Any

# His intended complete arm, which item 5 of the goal requires we preserve.
HIS_COMPLETE = {
    "input_dim": 4,       # eta, phi, log pT, log E, after the PID column is split out
    "pid": True, "pid_dim": 8,
    "add_info": True, "add_dim": 5,   # dE/dx, x, y, z, t
    "conditional": True, "cond_dim": 16,
    "num_coord": 2, "K": 10, "num_classes": 1,
}

# The arm that is runnable before R-1/R-2: our clouds, our event blocks, no PID,
# no auxiliary block. Widths from fullevent_fps_dataloader and
# train_fullevent_nominal.py:403-407.
OURS_DEGRADED = {
    "step1_reco": {"input_dim": 5, "cond_dim": 13, "num_coord": 2,
                   "pid": False, "add_info": False},
    "step2_gen": {"input_dim": 8, "cond_dim": 2, "num_coord": 3,
                  "pid": False, "add_info": False},
}

EXCLUDED_SUBSTRING = "out."     # _filter_partial_state's first rule, verbatim

# The tensors that stand between the data and everything else. `PET_body` is a
# sequential stack: `embed` and `local_physics.mlp` produce the token
# representation, `cond_embed` the conditioning token, and `pid_embed`/`add_embed`
# the two side channels. Every transformer block downstream consumes what they
# emit. A parameter-count fraction cannot see this -- these are 4,100 of 1.5 M
# parameters, 0.3 % -- but if they are reinitialised the 1.4 M that did transfer
# are reading a coordinate system they were never trained on. Transfer damage is
# structural, not proportional, and this is how the receipt says so.
INPUT_INTERFACE_PREFIXES = (
    "embed.", "local_physics.mlp.", "cond_embed.", "pid_embed.", "add_embed.",
)


def _source_shapes(checkout: Path, size: str) -> dict[str, dict[str, tuple[int, ...]]]:
    """Shapes the checkpoint carries, derived from `PET2` at his configuration.

    `mode="pretrain"` is used because that is what produced
    `best_model_pretrain_*`: it builds body, classifier AND generator, which is why
    the checkpoint has all three keys.
    """
    if str(checkout) not in sys.path:
        sys.path.insert(0, str(checkout))
    from src.models.omnilearned.network import PET2
    from src.models.omnilearned.utils import get_model_parameters

    model = PET2(**HIS_COMPLETE, mode="pretrain", use_int=False, local_int=False,
                 **get_model_parameters(size))
    sections = {"body": model.body, "classifier_head": model.classifier}
    if getattr(model, "generator", None) is not None:
        sections["generator_head"] = model.generator
    return {
        name: {key: tuple(value.shape) for key, value in module.state_dict().items()}
        for name, module in sections.items()
    }


def _target_shapes(settings: dict[str, Any], size: str) -> dict[str, dict[str, tuple[int, ...]]]:
    """Shapes our ported model exposes, split the way the loader addresses them."""
    import pet2_keras_port as port

    model = port.PET2Port(**settings, dtype="float32", **port.preset(size))
    inventory = dict(port.parameter_inventory(model))
    sections: dict[str, dict[str, tuple[int, ...]]] = {"body": {}, "classifier_head": {}}
    for name, variable in inventory.items():
        if name.startswith("body."):
            sections["body"][name[len("body."):]] = tuple(variable.shape)
        elif name.startswith("classifier."):
            sections["classifier_head"][name[len("classifier."):]] = tuple(variable.shape)
    return sections


def classify(source: dict[str, tuple[int, ...]],
             target: dict[str, tuple[int, ...]]) -> dict[str, Any]:
    """Apply `_filter_partial_state`'s three rules and total the parameters."""
    rows = []
    for key, shape in source.items():
        count = 1
        for dimension in shape:
            count *= dimension
        if EXCLUDED_SUBSTRING in key:
            verdict, reason = "replaced", "excluded by the loader's 'out.' rule"
        elif key not in target:
            verdict, reason = "absent_in_target", "our arm does not build this module"
        elif target[key] != shape:
            verdict, reason = ("reinitialized",
                               f"shape {shape} against our {target[key]}")
        else:
            verdict, reason = "transferred", "shapes agree"
        rows.append({"key": key, "source_shape": list(shape), "parameters": count,
                     "verdict": verdict, "reason": reason})
    totals: dict[str, dict[str, int]] = {}
    for row in rows:
        bucket = totals.setdefault(row["verdict"], {"tensors": 0, "parameters": 0})
        bucket["tensors"] += 1
        bucket["parameters"] += row["parameters"]
    # Tensors our arm has that the checkpoint does not reach at all.
    unmatched_target = sorted(set(target) - set(source))
    interface = [r for r in rows
                 if any(r["key"].startswith(p) for p in INPUT_INTERFACE_PREFIXES)]
    broken = [r for r in interface if r["verdict"] != "transferred"]
    return {
        "rows": rows,
        "totals": totals,
        "target_keys_not_in_checkpoint": unmatched_target,
        "input_interface_intact": not broken,
        "input_interface_broken_keys": [r["key"] for r in broken],
        "input_interface_reading": (
            "intact: every layer that touches the data transferred, so the pretrained "
            "stack downstream receives the representation it was trained on"
            if not broken else
            "BROKEN: the layers that produce the token, conditioning and side-channel "
            "representations did not transfer, so every pretrained block downstream "
            "reads inputs in a coordinate system it has never seen. The parameter "
            "fraction is near 1 and is not the relevant quantity."
        ),
    }


def analyse(checkout: Path, size: str = "small") -> dict[str, Any]:
    source = _source_shapes(checkout, size)
    targets = {
        "his_complete_step1_and_step2": dict(HIS_COMPLETE),
        "ours_degraded_step1_reco": {**HIS_COMPLETE, **OURS_DEGRADED["step1_reco"]},
        "ours_degraded_step2_gen": {**HIS_COMPLETE, **OURS_DEGRADED["step2_gen"]},
    }
    results: dict[str, Any] = {}
    for label, settings in targets.items():
        target = _target_shapes(settings, size)
        per_section = {
            section: classify(source[section], target.get(section, {}))
            for section in ("body", "classifier_head")
        }
        backbone = per_section["body"]["totals"]
        transferred = backbone.get("transferred", {"parameters": 0})["parameters"]
        total = sum(v["parameters"] for v in backbone.values())
        # Classifier-mode models do not build the diffusion time embedding at all,
        # so counting it as "not transferred" understates a complete arm. Both
        # denominators are reported.
        time_embedding = sum(
            r["parameters"] for r in per_section["body"]["rows"]
            if r["key"].startswith(("MPFourier.", "time_embed."))
        )
        usable = total - time_embedding
        results[label] = {
            "settings": settings,
            "sections": per_section,
            "backbone_parameters_in_checkpoint": total,
            "backbone_parameters_transferred": transferred,
            "backbone_fraction_transferred": transferred / total if total else None,
            "backbone_parameters_usable_by_a_classifier": usable,
            "backbone_fraction_of_usable_transferred": transferred / usable if usable else None,
            "diffusion_time_embedding_parameters": time_embedding,
            "input_interface_intact": per_section["body"]["input_interface_intact"],
            "verdict": (
                "usable" if per_section["body"]["input_interface_intact"]
                else "NOT a transfer: the input interface is reinitialised"
            ),
        }
    results["generator_head"] = {
        "in_checkpoint": "generator_head" in source,
        "loaded": False,
        "reason": ("`mode='classifier'` builds no generator, so `model.generator` is "
                   "None and the loader skips the section entirely. It is diffusion "
                   "machinery for the pretraining objective and has no counterpart in "
                   "a reweighting step."),
        "parameters": sum(
            int(__import__("numpy").prod(s)) for s in source.get("generator_head", {}).values()
        ),
    }
    return results


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--gregor-checkout", type=Path, required=True)
    parser.add_argument("--size", default="small")
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    results = analyse(args.gregor_checkout, args.size)
    receipt = {
        "scope": ("tensor-by-tensor checkpoint compatibility, derived from ARCHITECTURE "
                  "shapes. No checkpoint file has been read; none is reachable."),
        "loader": "omnilearned/utils.py:_filter_partial_state + load_state_dict(strict=False)",
        "loader_rules": ["key contains 'out.'", "key absent in target", "shape mismatch"],
        "silent_failure_mode": (
            "the loader prints and continues, so a mismatched configuration trains the "
            "affected tensors from scratch without failing"
        ),
        "unverifiable_without_the_file": (
            "cond_dim, add_dim, pid_dim and input_dim are properties of the PRETRAINING "
            "dataset. If OmniLearned pretrained at different widths, those tensors do "
            "not load in HIS runs either. Asked in the Gregor draft."
        ),
        "size": args.size,
        "results": results,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(receipt, indent=2) + "\n")
    for label, row in results.items():
        if label == "generator_head":
            continue
        print(f"{label:32s} {row['backbone_parameters_transferred']:>9,} / "
              f"{row['backbone_parameters_usable_by_a_classifier']:>9,} usable = "
              f"{row['backbone_fraction_of_usable_transferred']:6.1%}   "
              f"interface {'INTACT' if row['input_interface_intact'] else 'BROKEN'}")
        if not row["input_interface_intact"]:
            print("      broken:", ", ".join(
                row["sections"]["body"]["input_interface_broken_keys"]))


if __name__ == "__main__":
    main()

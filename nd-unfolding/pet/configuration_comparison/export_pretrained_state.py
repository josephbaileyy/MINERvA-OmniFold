"""Turn the pretrained checkpoint into a hashed initial state the Keras arm can load.

Two stages, because on Perlmutter no interpreter has both PyTorch and TensorFlow
and because an initialization that exists only inside a training job is not
reproducible. This stage runs in the torch environment and writes an `.npz` plus a
manifest; `pretrained_init.py` runs in the TensorFlow environment and loads it.

**What the exported state is.** His `PET2`, built at the configuration F1 pins,
with `load_pretrained_omnilearned`'s own filter applied to the real checkpoint and
`load_state_dict(..., strict=False)` -- so the pretrained tensors are his, and the
tensors his filter drops hold torch's own initialization of them. That is exactly
the state his fine-tuning starts from, which is the thing our arm has to inherit.

Every tensor is recorded as loaded, dropped or reinitialized. The seed for the
reinitialized ones is recorded too, because "reinitialized" is not a value.

NOT CITABLE FOR any performance claim.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import sys
from typing import Any

import numpy as np

# The configuration F1 pins for his complete arm, at the V1-paper interaction flags.
HIS_COMPLETE = dict(input_dim=4, pid=True, pid_dim=8, add_info=True, add_dim=5,
                    conditional=True, cond_dim=16, num_coord=2, K=10, num_classes=1,
                    use_int=False, local_int=False)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def export(checkpoint: Path, gregor_checkout: Path, size: str, seed: int,
           out_npz: Path, out_manifest: Path) -> dict[str, Any]:
    sys.path.insert(0, str(gregor_checkout))
    import torch
    from src.models.omnilearned.network import PET2
    from src.models.omnilearned.utils import _filter_partial_state, get_model_parameters

    preset = get_model_parameters(size)
    torch.manual_seed(seed)
    model = PET2(mode="classifier", **HIS_COMPLETE, **preset)
    blob = torch.load(str(checkpoint), map_location="cpu", weights_only=False)

    record: dict[str, Any] = {
        "checkpoint": str(checkpoint),
        "checkpoint_sha256": sha256(checkpoint),
        "gregor_checkout": str(gregor_checkout),
        "settings": HIS_COMPLETE,
        "preset": preset,
        "size": size,
        "torch_seed": seed,
        "torch_version": torch.__version__,
        "reference_policy": (
            "load_pretrained_omnilearned: _filter_partial_state then "
            "load_state_dict(strict=False), per section; `out.` excluded by name"
        ),
        "ema_body_present_and_unused": "ema_body" in blob,
        "sections": {},
    }

    for part_name, section in (("body", "body"), ("classifier", "classifier_head")):
        part = getattr(model, part_name, None)
        if part is None:
            continue
        model_state = part.state_dict()
        ckpt_state = blob.get(section, {})
        filtered = _filter_partial_state(ckpt_state, model_state)
        part.load_state_dict(filtered, strict=False)
        record["sections"][part_name] = {
            "checkpoint_section": section,
            "checkpoint_tensors": len(ckpt_state),
            "model_tensors": len(model_state),
            "loaded": sorted(filtered),
            "loaded_parameters": int(sum(filtered[k].numel() for k in filtered)),
            "model_parameters": int(sum(v.numel() for v in model_state.values())),
            "dropped_absent_from_model": sorted(k for k in ckpt_state
                                                if k not in model_state),
            "dropped_shape_mismatch": sorted(
                k for k in ckpt_state if k in model_state
                and tuple(ckpt_state[k].shape) != tuple(model_state[k].shape)),
            "reinitialized": sorted(k for k in model_state if k not in filtered),
        }

    arrays = {name: parameter.detach().cpu().numpy()
              for name, parameter in model.named_parameters()}
    np.savez(out_npz, **arrays)
    record["exported_tensors"] = len(arrays)
    record["exported_parameters"] = int(sum(a.size for a in arrays.values()))
    record["state_npz"] = str(out_npz)
    record["state_npz_sha256"] = sha256(out_npz)
    out_manifest.write_text(json.dumps(record, indent=2) + "\n")
    return record


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--checkpoint", type=Path, required=True)
    parser.add_argument("--gregor-checkout", type=Path, required=True)
    parser.add_argument("--size", default="small")
    parser.add_argument("--seed", type=int, default=20260919)
    parser.add_argument("--out-npz", type=Path, required=True)
    parser.add_argument("--out-manifest", type=Path, required=True)
    args = parser.parse_args()
    record = export(args.checkpoint, args.gregor_checkout, args.size, args.seed,
                    args.out_npz, args.out_manifest)
    for name, section in record["sections"].items():
        print(f"{name}: loaded {len(section['loaded'])}/{section['model_tensors']} "
              f"({section['loaded_parameters']:,}/{section['model_parameters']:,} params), "
              f"reinitialized {len(section['reinitialized'])}")
    print(f"exported {record['exported_tensors']} tensors, "
          f"{record['exported_parameters']:,} parameters")
    print("state sha256", record["state_npz_sha256"])


if __name__ == "__main__":
    main()

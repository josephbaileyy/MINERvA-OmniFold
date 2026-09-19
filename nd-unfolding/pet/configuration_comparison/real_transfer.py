"""The reference loading policy, run against the REAL checkpoint, tensor by tensor.

`checkpoint_transfer.py` modelled this from inventories we derived from the code.
This runs `load_pretrained_omnilearned`'s actual filter against the actual file,
for the actual configuration we intend to run, and records every tensor as
loaded, dropped-by-name, dropped-by-shape or reinitialized.

NOT CITABLE FOR any performance claim.
"""
import json, sys, hashlib
sys.path.insert(0, "/Users/josephbailey/local-research/gregor-audit/minerva-ml")
import torch
from src.models.omnilearned.utils import _filter_partial_state, get_model_parameters
from src.models.omnilearned.network import PET2

CKPT = sys.argv[1]
OUT = sys.argv[2]

h = hashlib.sha256()
with open(CKPT, "rb") as f:
    for c in iter(lambda: f.read(1 << 20), b""):
        h.update(c)

ckpt = torch.load(CKPT, map_location="cpu", weights_only=False)

# The configuration we intend to run: his complete arm at the V1-paper flags.
SETTINGS = dict(input_dim=4, pid=True, pid_dim=8, add_info=True, add_dim=5,
                conditional=True, cond_dim=16, num_coord=2, K=10, num_classes=1,
                use_int=False, local_int=False)
preset = get_model_parameters("small")
report = {"checkpoint": CKPT, "sha256": h.hexdigest(),
          "settings": SETTINGS, "preset": preset,
          "checkpoint_sections": {k: (len(v) if isinstance(v, dict) and v and
                                      all(torch.is_tensor(x) for x in v.values())
                                      else type(v).__name__)
                                  for k, v in ckpt.items()}}

model = PET2(mode="classifier", **SETTINGS, **preset)

for part_name, section in (("body", "body"), ("classifier", "classifier_head")):
    part = getattr(model, part_name, None)
    if part is None:
        report[part_name] = {"present_in_model": False}
        continue
    model_state = part.state_dict()
    ckpt_state = ckpt.get(section, {})
    filtered = _filter_partial_state(ckpt_state, model_state)

    loaded = sorted(filtered)
    missing_in_model = sorted(k for k in ckpt_state if k not in model_state)
    shape_mismatch = sorted(
        k for k in ckpt_state
        if k in model_state and tuple(ckpt_state[k].shape) != tuple(model_state[k].shape))
    reinitialized = sorted(k for k in model_state if k not in filtered)

    report[part_name] = {
        "present_in_model": True,
        "checkpoint_section": section,
        "checkpoint_tensors": len(ckpt_state),
        "model_tensors": len(model_state),
        "loaded": len(loaded),
        "loaded_parameters": int(sum(filtered[k].numel() for k in loaded)),
        "model_parameters": int(sum(v.numel() for v in model_state.values())),
        "dropped_absent_from_model": missing_in_model,
        "dropped_shape_mismatch": [
            {"name": k, "checkpoint": list(ckpt_state[k].shape),
             "model": list(model_state[k].shape)} for k in shape_mismatch],
        "reinitialized": reinitialized,
        "loaded_names": loaded,
    }
    # The policy itself, executed, so the receipt records a run and not a plan.
    part.load_state_dict(filtered, strict=False)

with open(OUT, "w") as f:
    json.dump(report, f, indent=2)

for name in ("body", "classifier"):
    r = report.get(name, {})
    if not r.get("present_in_model"):
        print(f"{name}: not present in model"); continue
    print(f"{name}: loaded {r['loaded']}/{r['model_tensors']} tensors "
          f"({r['loaded_parameters']:,}/{r['model_parameters']:,} params); "
          f"dropped-by-name {len(r['dropped_absent_from_model'])}, "
          f"shape-mismatch {len(r['dropped_shape_mismatch'])}, "
          f"reinitialized {len(r['reinitialized'])}")
    for m in r["dropped_shape_mismatch"][:8]:
        print(f"    shape {m['name']}: ckpt {m['checkpoint']} vs model {m['model']}")
    for k in r["reinitialized"][:10]:
        print(f"    reinit {k}")

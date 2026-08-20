import json, os, sys
import numpy as np

weights, arm_dir = sys.argv[1], os.path.realpath(sys.argv[2])
with np.load(weights, allow_pickle=True) as z:
    if "seed_policy" not in z.files:
        sys.exit("[p5a] G1: artifact carries no seed_policy at all -- not a nominal weights npz")
    sp = np.asarray(z["seed_policy"], dtype=object).item()
    ic = np.asarray(z["inference_contract"], dtype=object).item() \
        if "inference_contract" in z.files else {}

# G1 -- the schema discriminator.
lr = sp.get("lr_policy")
if lr is None:
    sys.exit("[p5a] G1: seed_policy has NO lr_policy key. This is the PRE-ANNEAL arm. "
             "The promoted arm is fullevent_nominal_annealed/. Refusing.")
got = lr.get("schedule")
want = "fit-time-anneal-after-iteration-0"
if got != want:
    sys.exit(f"[p5a] G1: lr_policy.schedule is {got!r}, expected {want!r}. Refusing.")
print(f"[p5a] G1 PASS  lr_policy.schedule = {got}")
print(f"[p5a] G1 also  base_lr={lr.get('base_lr')} annealed_lr={lr.get('annealed_lr')} "
      f"applies_from_iteration={lr.get('applies_from_iteration')}")

# G2 -- the contract's checkpoint must resolve UNDER the promoted arm's directory.  realpath on
# both sides so a symlink or a .. cannot walk out of the arm while still passing a prefix test.
ckpt = ic.get("step2_checkpoint")
if not ckpt:
    sys.exit("[p5a] G2: inference_contract names no step2_checkpoint")
real = os.path.realpath(ckpt)
if not (real == arm_dir or real.startswith(arm_dir + os.sep)):
    sys.exit(f"[p5a] G2: step2_checkpoint resolves OUTSIDE the promoted arm.\n"
             f"        checkpoint: {real}\n        arm dir   : {arm_dir}\nRefusing.")
if not os.path.isfile(real):
    sys.exit(f"[p5a] G2: step2_checkpoint does not exist: {real}")
print(f"[p5a] G2 PASS  step2_checkpoint resolves under the promoted arm")

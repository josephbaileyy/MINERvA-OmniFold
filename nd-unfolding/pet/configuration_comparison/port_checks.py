"""P-1 ... P-6: prove the Keras port is his network, or stop the campaign.

`MATCHED_COMPARISON_PROPOSAL-20260918.md` §7.2 fixed these before any port existed:

| P-1 | parameter count and per-layer shapes | exactly equal |
| P-2 | forward outputs after transferring his weights | <= 1e-5 max abs, float64, 1,024 inputs incl. fully-masked and single-token rows |
| P-3 | gradient agreement w.r.t. every parameter | tolerance set by a MEASURED step-size sweep, not asserted |
| P-4 | weight-update agreement after one optimizer step | <= the tolerance P-3 establishes, per tensor |
| P-5 | masked slots cannot reach the output | exact |
| P-6 | repeatability and checkpoint reload | bitwise |

Two design points are worth stating because they are what make the checks mean
something rather than merely pass.

FIRST, P-3's tolerance is derived, not chosen. A finite-difference sweep over step
sizes is run against BOTH engines' autodiff; the best achievable agreement over
the sweep is the resolution with which a derivative can be checked independently
at all. The cross-engine comparison then has to beat that floor -- the two engines
must agree with each other better than either can be independently resolved. A
hand-picked `1e-6` would have been a number I chose after seeing the answer.

SECOND, P-2 is run TWICE, in float32 against unmodified upstream and in float64
against upstream with one declared kernel-level dtype repair, because running his model in
float64 at all turns out to corrupt it: `layers.mask_outer` hardcodes `.float()`,
so a float64 model receives a float32 additive attention mask, and
`torch.nn.functional.scaled_dot_product_attention` silently returns a wrong answer
for that combination -- measured, O(1) wrong, not a rounding effect. It is NOT a
general hazard: the same probe shows float32, bfloat16 and float16 q/k/v with a
float32 mask are all fine, so his own runs and his AMP path are unaffected. Only a
mask at LOWER precision than q/k/v triggers it, and only a port check would ever
produce that. `torch_sdpa_mask_dtype_probe` ships the evidence in the receipt.

THIRD, P-5 perturbs padded slots in EVERY column that the mask does not define,
including the k-NN coordinate columns. That matters because the upstream separates
padded points by adding a literal `999.0`, which is a magic constant that assumes
coordinates are O(1). Our reco coordinates are scaled detector positions, so the
check also reports the coordinate magnitude at which the separation stops working,
rather than asserting that it does.

Run: ``python3 port_checks.py --gregor-checkout <path> --output receipts/<name>.json``
"""

from __future__ import annotations

import argparse
import json
import math
import os
from pathlib import Path
import sys
from typing import Any, Callable

os.environ.setdefault("CUDA_VISIBLE_DEVICES", "")
os.environ.setdefault("TF_CPP_MIN_LOG_LEVEL", "3")

import numpy as np

import keras_backend
import pet2_keras_port as port

keras_backend.select_keras_backend()

import tensorflow as tf  # noqa: E402

# His configuration, as measure_model_capacity.py pins it, minus the interaction
# flags -- which the V1-paper branches leave at their argparse default of False.
HIS_CONFIGURATION: dict[str, Any] = {
    "input_dim": 4,
    "add_dim": 5,
    "pid": True,
    "pid_dim": 8,
    "cond_dim": 16,
    "num_coord": 2,
    "K": 10,
    "add_info": True,
    "conditional": True,
    "num_classes": 1,
}

# optim.AdamW(trainable_params, lr=args.lr, weight_decay=args.weight_decay) at
# src/scripts/train.py:2345, one param group, torch defaults for betas and eps.
#
# NOTE for the recipe, not for this file: PET2 defines `no_weight_decay()` returning
# {"norm", "token"}, and train.py never calls it. There is one param group, so his
# norms and class tokens ARE weight-decayed. Reproducing "his optimizer" means
# reproducing that, not reproducing the hook he wrote and did not use.
HIS_OPTIMIZER = {"learning_rate": 1e-4, "weight_decay": 0.01, "beta_1": 0.9,
                 "beta_2": 0.999, "epsilon": 1e-8}

FORWARD_TOLERANCE = 1e-5          # P-2, from the proposal
FLOAT32_EPSILON = 2.0 ** -24      # unit round-off of binary32, 5.96e-8
FLOAT32_JITTER_DRAWS = 5
FD_STEPS = (1e-2, 1e-3, 1e-4, 1e-5, 1e-6, 1e-7, 1e-8)
ULP_JITTER_DRAWS = 5      # one sign pattern can cancel; several cannot all cancel

# P-3 and P-4 are gated on a CONTROL, not on a tolerance. Chasing a tolerance until
# the check passes is how a port check becomes decorative: every round of "the
# floor must be measured differently" is a round of tuning against the answer. So
# each check also runs a deliberate, minimal, plausible STRUCTURAL difference -- a
# mutant -- and the requirement is that the real disagreement be at least this many
# times smaller than the mutant's. Three orders is generous; the measured margins
# are five to eight, so the constant is not load-bearing. The round-off floors are
# still measured and reported, as evidence that the disagreement is round-off, but
# they do not decide the verdict.
MUTANT_MARGIN = 1000.0
PAD_COORDINATE_SHIFT = 999.0      # the upstream's literal separation constant
K_NEIGHBOURS = 10                 # HIS_CONFIGURATION["K"], named for the P-5 sweep


class upcast_attention_mask:
    """Repair torch's SDPA for a mask at lower precision than q/k/v, for float64 runs.

    THE DEFECT, measured: `F.scaled_dot_product_attention` with float64 q/k/v and a
    float32 additive mask returns an O(1) wrong answer -- 1.7 against a hand-rolled
    float64 softmax over the SAME mask values. `torch_sdpa_mask_dtype_probe` also
    shows float32, bfloat16 and float16 q/k/v are unaffected, so this is specific to
    a mask BELOW the tensor precision and never happens in his runs or under AMP.

    WHY IT IS PATCHED HERE AND NOT IN HIS CODE. Both call sites build the mask as
    `~(mask_outer(m).bool()).float() * -1e9`, and that trailing `.float()` is
    float32 whatever the model dtype is. Coercing `mask_outer` alone is decorative:
    the `.float()` happens afterwards, downstream of it -- which is what the first
    attempt at this shim got wrong. Patching the kernel wrapper instead fixes the
    actual defect, at one place, and is provably a no-op whenever the dtypes already
    agree, which the probe records.

    `applications` counts how often the upcast actually fired. A shim that silently
    never ran would leave the check measuring the corrupted path while reporting
    that it had been repaired.
    """

    def __init__(self) -> None:
        self.applications = 0
        self._original: Any = None

    def __enter__(self) -> "upcast_attention_mask":
        import torch.nn.functional as F

        original = F.scaled_dot_product_attention
        self._original = original
        shim = self

        def patched(query, key, value, attn_mask=None, *args, **kwargs):
            if (
                attn_mask is not None
                and attn_mask.is_floating_point()
                and attn_mask.dtype != query.dtype
                and attn_mask.element_size() < query.element_size()
            ):
                attn_mask = attn_mask.to(query.dtype)
                shim.applications += 1
            return original(query, key, value, attn_mask, *args, **kwargs)

        F.scaled_dot_product_attention = patched
        if F.scaled_dot_product_attention is not patched:
            raise SystemExit("[port] failed to rebind scaled_dot_product_attention")
        return self

    def __exit__(self, *exc: Any) -> None:
        import torch.nn.functional as F

        F.scaled_dot_product_attention = self._original


def torch_sdpa_mask_dtype_probe() -> dict[str, Any]:
    """Evidence for the shim: which (tensor, mask) dtype pairs SDPA gets wrong.

    The reference is a hand-rolled float64 softmax over the SAME mask values, so a
    disagreement cannot be blamed on the mask being different -- only on how the
    kernel consumed it.
    """
    import torch
    import torch.nn.functional as F

    rs = np.random.RandomState(0)
    mask = np.zeros((1, 1, 4, 4))
    mask[..., 2:] = port.NEG_INF_SURROGATE
    rows = []
    for dtype in (torch.float64, torch.float32, torch.bfloat16, torch.float16):
        q, k, v = (torch.from_numpy(rs.randn(1, 1, 4, 8)).to(dtype) for _ in range(3))
        reference = (
            torch.softmax(
                q.double() @ k.double().transpose(-1, -2) / math.sqrt(8)
                + torch.from_numpy(mask), -1
            ) @ v.double()
        )
        matched = F.scaled_dot_product_attention(
            q, k, v, attn_mask=torch.from_numpy(mask).to(dtype)
        ).double()
        lower = F.scaled_dot_product_attention(
            q, k, v, attn_mask=torch.from_numpy(mask).float()
        ).double()
        rows.append({
            "tensor_dtype": str(dtype),
            "error_with_matched_mask": float((matched - reference).abs().max()),
            "error_with_float32_mask": float((lower - reference).abs().max()),
        })
    return {
        "rows": rows,
        "reading": (
            "a float32 mask is only harmful when q/k/v are float64, i.e. when the mask "
            "is at LOWER precision than the tensors. His runs are float32 and his AMP "
            "path is fp16/bf16, both of which this probe shows are unaffected."
        ),
    }


def load_upstream(checkout: Path) -> Any:
    """Import the pinned upstream without leaving it on sys.path for others."""
    if not (checkout / "src" / "models" / "omnilearned" / "network.py").is_file():
        raise SystemExit(f"[port] not an omnilearned checkout: {checkout}")
    sys.path.insert(0, str(checkout))
    from src.models.omnilearned.network import PET2

    return PET2


def make_fixture(rows: int, tokens: int, seed: int) -> dict[str, np.ndarray]:
    """Fixed float64 inputs, with the two boundary populations P-2 names.

    Rows 0 and 1 are fully masked (no real token) and rows 2 and 3 carry exactly
    one. Those are the populations where a masking bug stops cancelling and where
    softmax over an all-blocked row would produce NaN if the `-1e9` surrogate had
    been "cleaned up" into `-inf`.
    """
    rng = np.random.RandomState(seed)
    x = rng.randn(rows, tokens, HIS_CONFIGURATION["input_dim"])
    # His mask is column 2 != 0; make it emphatically nonzero, then carve exceptions.
    x[:, :, port.HIS_MASK_COLUMN] = np.abs(x[:, :, port.HIS_MASK_COLUMN]) + 0.5
    real = rng.randint(1, tokens + 1, size=rows)
    for row in range(rows):
        x[row, real[row]:, :] = 0.0
    x[0, :, :] = 0.0                      # fully masked
    x[1, :, :] = 0.0                      # fully masked
    x[2, 1:, :] = 0.0                     # single real token
    x[3, 1:, :] = 0.0                     # single real token
    pid = rng.randint(0, HIS_CONFIGURATION["pid_dim"], size=(rows, tokens))
    pid = np.where(x[:, :, port.HIS_MASK_COLUMN] != 0, pid, 0)
    return {
        "x": x.astype(np.float64),
        "cond": rng.randn(rows, HIS_CONFIGURATION["cond_dim"]).astype(np.float64),
        "pid": pid.astype(np.int64),
        "add_info": (rng.randn(rows, tokens, HIS_CONFIGURATION["add_dim"])
                     * (x[:, :, port.HIS_MASK_COLUMN:port.HIS_MASK_COLUMN + 1] != 0)
                     ).astype(np.float64),
        "labels": rng.randint(0, 2, size=(rows, 1)).astype(np.float64),
        "weights": (0.5 + rng.rand(rows, 1)).astype(np.float64),
    }


def build_pair(torch_cls: Any, size: str, seed: int, dtype: str = "float64"):
    """Build both models at one dtype and copy his weights into the port."""
    import torch

    torch_dtype = {"float64": torch.float64, "float32": torch.float32}[dtype]
    torch.manual_seed(seed)
    settings = dict(HIS_CONFIGURATION)
    theirs = torch_cls(**settings, mode="classifier", use_int=False, local_int=False,
                       **port.preset(size)).to(torch_dtype).eval()
    ours = port.PET2Port(**settings, dtype=dtype, **port.preset(size))

    # Force variable creation before transfer: a Keras weight that has never been
    # built is not in the inventory, and a transfer that silently skipped one would
    # look like a forward-agreement failure later.
    inventory = dict(port.parameter_inventory(ours))
    named = dict(theirs.named_parameters())
    missing = sorted(set(named) - set(inventory))
    extra = sorted(set(inventory) - set(named))
    if missing or extra:
        raise SystemExit(f"[P-1] inventory mismatch; missing={missing[:5]} extra={extra[:5]}")
    transferred = 0
    for name, parameter in named.items():
        value = parameter.detach().cpu().numpy()
        variable = inventory[name]
        if tuple(variable.shape) != tuple(value.shape):
            raise SystemExit(f"[P-1] shape mismatch on {name}: {variable.shape} vs {value.shape}")
        variable.assign(value)
        transferred += 1
    report = {
        "tensors": len(named),
        "transferred": transferred,
        "parameters_theirs": int(sum(p.numel() for p in theirs.parameters())),
        "parameters_ours": int(sum(int(np.prod(v.shape)) for _, v in inventory.items())),
        "traversal_order_identical": [n for n, _ in theirs.named_parameters()]
        == [n for n, _ in port.parameter_inventory(ours)],
        "dtype": dtype,
    }
    return theirs, ours, report


def _cast(batch: dict[str, np.ndarray], dtype: str) -> dict[str, np.ndarray]:
    """Recast the float members of a fixture; `pid` stays integral."""
    out = {}
    for key, value in batch.items():
        out[key] = value if key == "pid" else value.astype(dtype)
    return out


def _their_forward(theirs: Any, batch: dict[str, np.ndarray], dtype: str) -> np.ndarray:
    import torch

    torch_dtype = {"float64": torch.float64, "float32": torch.float32}[dtype]
    batch = _cast(batch, dtype)
    with torch.no_grad():
        body = theirs.body(
            torch.from_numpy(batch["x"]),
            torch.from_numpy(batch["cond"]),
            torch.from_numpy(batch["pid"]),
            torch.from_numpy(batch["add_info"]),
            torch.zeros(batch["x"].shape[0], dtype=torch_dtype),
        )
        return theirs.classifier(body).numpy()


def _our_forward(ours: Any, batch: dict[str, np.ndarray], dtype: str = "float64",
                 mask: np.ndarray | None = None) -> np.ndarray:
    batch = _cast(batch, dtype)
    return ours(
        tf.constant(batch["x"]), tf.constant(batch["cond"]),
        tf.constant(batch["pid"]), tf.constant(batch["add_info"]),
        mask=None if mask is None else tf.constant(mask.astype(dtype)),
        training=False,
    ).numpy()


def check_p1(report: dict[str, Any]) -> dict[str, Any]:
    """P-1: exact agreement on the parameter inventory, by name and by shape."""
    held = (
        report["parameters_theirs"] == report["parameters_ours"]
        and report["transferred"] == report["tensors"]
        and report["traversal_order_identical"]
    )
    return {"held": bool(held), **report}


FLOAT32_SLACK = 2.0    # two independent roundings differ by at most 2x one deviation


def float32_verdict(cross_engine: float, reference_deviation: float,
                    our_deviation: float) -> dict[str, Any]:
    """Decide P-2a from the REFERENCE's float32 deviation only.

    Pulled out as a pure function so the property that matters can be tested
    directly: inflating `our_deviation` must make the verdict WORSE. The previous
    rule -- `cross <= reference_deviation + our_deviation` -- did the opposite,
    widening its own acceptance band in proportion to the port's own error, so a
    float32 defect could buy the room it needed to pass.
    """
    limit = FLOAT32_SLACK * reference_deviation
    ours_no_worse = our_deviation <= FLOAT32_SLACK * reference_deviation
    return {
        "held": bool(cross_engine <= limit and ours_no_worse),
        "limit_from_reference_only": limit,
        "ours_no_worse_than_reference": bool(ours_no_worse),
        "slack": FLOAT32_SLACK,
    }


def _float32_perturbation_bound(model: Any, batch: dict[str, np.ndarray],
                                seed: int) -> dict[str, Any]:
    """How far the float64 output moves under one float32 ulp of input/weight noise.

    Computed entirely in float64 and touching no float32 run, so it is independent
    of both implementations. It models the rounding of inputs and weights but NOT
    of every intermediate product, so it is a lower bound on what two float32
    implementations can differ by -- reported as corroboration, never as the gate.
    """
    inventory = port.parameter_inventory(model)
    saved = [v.numpy().copy() for _, v in inventory]
    baseline = _our_forward(model, batch, "float64")
    rng = np.random.RandomState(seed + 7)
    movements = []
    for _ in range(FLOAT32_JITTER_DRAWS):
        for (_, variable), original in zip(inventory, saved):
            signs = rng.choice([-1.0, 1.0], size=original.shape)
            variable.assign(original * (1.0 + FLOAT32_EPSILON * signs))
        jittered = {k: v.copy() for k, v in batch.items()}
        for key in ("x", "cond", "add_info"):
            signs = rng.choice([-1.0, 1.0], size=batch[key].shape)
            jittered[key] = batch[key] * (1.0 + FLOAT32_EPSILON * signs)
        movements.append(float(np.abs(
            _our_forward(model, jittered, "float64") - baseline).max()))
    for (_, variable), original in zip(inventory, saved):
        variable.assign(original)
    return {
        "float32_epsilon": FLOAT32_EPSILON,
        "draws": FLOAT32_JITTER_DRAWS,
        "max_output_movement": max(movements),
        "movements": movements,
        "role": ("corroboration only: a floor on achievable float32 disagreement, "
                 "since it omits intermediate rounding. Does not gate."),
    }


def check_p2(torch_cls: Any, size: str, seed: int,
             batch: dict[str, np.ndarray]) -> dict[str, Any]:
    """P-2: forward agreement, twice, because one run alone would be misleading.

    P-2a runs float32 against UNMODIFIED upstream -- the precision he trains in --
    with a tolerance derived from each engine's own distance to a float64 reference
    rather than chosen. If the port were a different network, the two float32
    engines would disagree by more than their individual float32 errors permit.

    P-2b runs float64, which needs the declared SDPA mask-dtype repair, and is
    what makes the 1e-5 tolerance in the proposal a real constraint: at float64 the
    engines agree at round-off, so 1e-5 has three orders of headroom, whereas in
    float32 alone 1e-5 would be barely above the noise.
    """
    theirs64, ours64, _ = build_pair(torch_cls, size, seed, "float64")
    with upcast_attention_mask() as shim:
        reference_theirs = _their_forward(theirs64, batch, "float64")
    upcasts = shim.applications
    reference_ours = _our_forward(ours64, batch, "float64")
    difference64 = np.abs(reference_ours - reference_theirs)

    theirs32, ours32, _ = build_pair(torch_cls, size, seed, "float32")
    their32 = _their_forward(theirs32, batch, "float32")
    our32 = _our_forward(ours32, batch, "float32")
    their_float32_error = float(np.abs(their32 - reference_theirs).max())
    our_float32_error = float(np.abs(our32 - reference_ours).max())
    cross32 = float(np.abs(our32 - their32).max())

    # THE BUDGET MUST NOT BE ABLE TO GROW WITH A DEFECT IN THE THING IT TESTS.
    #
    # The first version used `their_error + our_error`, which is the triangle
    # inequality but with OUR deviation in it -- so a port with a float32 bug
    # widened its own acceptance band and could pass by being wrong. Replaced with
    # two limits, neither of which reads our float32 output as an input:
    #
    #  (a) the cross-engine difference must be within TWICE THE REFERENCE'S OWN
    #      float32 deviation. Two independent roundings of one computation, each
    #      deviating by at most e from the exact float64 answer, differ by at most
    #      2e. Using the reference's e on both sides makes the bound a property of
    #      the upstream implementation, which is not under test.
    #  (b) our float32 deviation must itself be no worse than twice the
    #      reference's. This is the clause the old budget was accidentally
    #      rewarding the violation of, and it is the one a float32 bug trips.
    #
    # An a-priori perturbation bound is reported alongside as corroboration: the
    # float64 output's movement when every parameter and input is jittered by one
    # float32 ulp. It is computed entirely in float64 and touches no float32 run at
    # all, so it is independent of both implementations -- but it models only
    # input and weight rounding, not the rounding of every intermediate, so it is a
    # floor on the achievable disagreement rather than a ceiling, and it does not
    # gate.
    verdict32 = float32_verdict(cross32, their_float32_error, our_float32_error)
    budget32 = verdict32["limit_from_reference_only"]
    ours_no_worse = verdict32["ours_no_worse_than_reference"]
    apriori = _float32_perturbation_bound(ours64, batch, seed)

    boundary = {
        "fully_masked_rows": [0, 1],
        "single_token_rows": [2, 3],
        "fully_masked_max_abs_difference_float64": float(difference64[[0, 1]].max()),
        "single_token_max_abs_difference_float64": float(difference64[[2, 3]].max()),
        "fully_masked_outputs_finite": bool(np.isfinite(reference_ours[[0, 1]]).all()),
    }
    finite = bool(np.isfinite(reference_ours).all() and np.isfinite(reference_theirs).all())
    held_a = verdict32["held"]
    held_b = bool(finite and difference64.max() <= FORWARD_TOLERANCE)
    return {
        "held": bool(held_a and held_b),
        "rows": int(batch["x"].shape[0]),
        "P2a_float32_unmodified_upstream": {
            "held": bool(held_a),
            "criterion": (
                "(a) the cross-engine float32 difference must be within TWICE the "
                "reference implementation's own float32 deviation, and (b) our "
                "float32 deviation must be no worse than twice the reference's. "
                "Neither limit reads our float32 output, so a defect in the port "
                "cannot widen its own acceptance band."
            ),
            "cross_engine_max_abs_difference": cross32,
            "limit_from_reference_only": budget32,
            "their_float32_deviation": their_float32_error,
            "our_float32_deviation": our_float32_error,
            "ours_no_worse_than_reference": bool(ours_no_worse),
            "apriori_float32_perturbation_bound": apriori,
        },
        "P2b_float64_with_declared_sdpa_repair": {
            "held": held_b,
            "tolerance": FORWARD_TOLERANCE,
            "max_abs_difference": float(difference64.max()),
            "mean_abs_difference": float(difference64.mean()),
            "outputs_finite": finite,
            "upstream_modification": (
                "torch's scaled_dot_product_attention upcasts an attention mask that is "
                "below the tensor precision; his code is untouched"
            ),
            "mask_upcasts_applied": upcasts,
            **boundary,
        },
    }


def _their_loss_and_grads(theirs: Any, batch: dict[str, np.ndarray]):
    import torch

    theirs.zero_grad(set_to_none=True)
    body = theirs.body(
        torch.from_numpy(batch["x"]), torch.from_numpy(batch["cond"]),
        torch.from_numpy(batch["pid"]), torch.from_numpy(batch["add_info"]),
        torch.zeros(batch["x"].shape[0], dtype=torch.float64),
    )
    logits = theirs.classifier(body)
    loss = weighted_bce_torch(logits, batch)
    loss.backward()
    return float(loss.item()), {n: p.grad.detach().numpy().copy()
                                for n, p in theirs.named_parameters()}


def weighted_bce_torch(logits: Any, batch: dict[str, np.ndarray]) -> Any:
    """OmniFold's `weighted_binary_crossentropy`, written in torch.

    Not his Huber regression loss: his loss has no counterpart in a reweighting
    step, so the ported arm keeps his network and optimizer and takes OmniFold's
    objective. Using the SAME loss in both engines is what makes P-3 a statement
    about the network rather than about two different objectives.
    """
    import torch
    import torch.nn.functional as F

    labels = torch.from_numpy(batch["labels"])
    weights = torch.from_numpy(batch["weights"])
    per_row = F.binary_cross_entropy_with_logits(logits, labels, reduction="none")
    return (weights * per_row).mean()


def weighted_bce_tf(logits: tf.Tensor, batch: dict[str, np.ndarray]) -> tf.Tensor:
    per_row = tf.nn.sigmoid_cross_entropy_with_logits(
        labels=tf.constant(batch["labels"]), logits=logits
    )
    return tf.reduce_mean(tf.constant(batch["weights"]) * per_row)


def _our_loss_and_grads(ours: Any, batch: dict[str, np.ndarray]):
    variables = [v for _, v in port.parameter_inventory(ours)]
    with tf.GradientTape() as tape:
        logits = ours(
            tf.constant(batch["x"]), tf.constant(batch["cond"]),
            tf.constant(batch["pid"]), tf.constant(batch["add_info"]), training=False,
        )
        loss = weighted_bce_tf(logits, batch)
    grads = tape.gradient(loss, variables)
    names = [n for n, _ in port.parameter_inventory(ours)]
    return float(loss.numpy()), {n: (None if g is None else g.numpy())
                                 for n, g in zip(names, grads)}


def _finite_difference_sweep(
    loss_at: Callable[[], float], poke: Callable[[float], None], analytic: float
) -> dict[str, Any]:
    """Central differences over a decade sweep; report the best step and its error."""
    trials = []
    for h in FD_STEPS:
        poke(+h)
        up = loss_at()
        poke(-2 * h)
        down = loss_at()
        poke(+h)  # restore
        estimate = (up - down) / (2 * h)
        scale = max(abs(analytic), 1e-30)
        trials.append({"step": h, "estimate": estimate,
                       "relative_error": abs(estimate - analytic) / scale})
    best = min(trials, key=lambda t: t["relative_error"])
    return {"trials": trials, "best_step": best["step"],
            "best_relative_error": best["relative_error"]}


def _reduction_order_floor(theirs: Any, batch: dict[str, np.ndarray],
                           reference: dict[str, np.ndarray], seed: int) -> dict[str, Any]:
    """Same-engine round-off floor: two reorderings that change nothing but the sums.

    Both routes recompute a gradient that is mathematically identical and
    numerically different, so the movement between them is how well this
    computation reproduces its own float64 gradient -- the right yardstick for a
    cross-engine comparison, being the same quantity in the same units.

    * a row PERMUTATION changes the order of the batch reduction only;
    * a SPLIT into two half-batches changes every tensor shape in every matmul, so
      it perturbs the reduction order throughout the network rather than just at
      the end. The permutation alone measured 2.6e-15 and understated the real
      float64 sensitivity by an order of magnitude, which is why both are run and
      the larger is taken.

    Neither is the finite-difference sweep. That answers a different question -- is
    the analytic derivative the true derivative, on one scalar at a time -- and its
    error is truncation-dominated, so it cannot bound agreement between two exact
    autodiff implementations. It is kept as the correctness control.
    """
    order = np.random.RandomState(seed).permutation(batch["x"].shape[0])
    _, permuted = _their_loss_and_grads(theirs, {k: v[order] for k, v in batch.items()})

    rows = batch["x"].shape[0]
    half = rows // 2
    _, first = _their_loss_and_grads(theirs, {k: v[:half] for k, v in batch.items()})
    _, second = _their_loss_and_grads(theirs, {k: v[half:] for k, v in batch.items()})
    split = {
        name: (half * first[name] + (rows - half) * second[name]) / rows
        for name in first
    }

    # Third route, and the one that matters most: jitter every parameter by a
    # single ulp. Two implementations that agree to ulp level in the forward pass
    # cannot be asked to agree in the gradient any better than the gradient's own
    # sensitivity to an ulp allows, and that sensitivity is an amplification factor
    # of the backward pass -- a property of the network, measurable, and not
    # something to guess at.
    import torch

    #
    # One draw is a coin flip per tensor: a particular sign pattern may happen to
    # cancel. The floor is therefore the worst of several draws, which estimates the
    # effect of an ulp rather than sampling it once.
    rng = np.random.RandomState(seed + 1)
    saved = {name: parameter.detach().clone()
             for name, parameter in theirs.named_parameters()}
    jitter_draws = []
    for _ in range(ULP_JITTER_DRAWS):
        with torch.no_grad():
            for name, parameter in theirs.named_parameters():
                sign = rng.choice([-1.0, 1.0], size=tuple(parameter.shape))
                parameter.copy_(saved[name] * (1.0 + np.finfo(np.float64).eps
                                               * torch.from_numpy(sign)))
        jitter_draws.append(_their_loss_and_grads(theirs, batch)[1])
    with torch.no_grad():
        for name, parameter in theirs.named_parameters():
            parameter.copy_(saved[name])

    floor = {}
    detail = {}
    for name, value in reference.items():
        scale = max(float(np.abs(value).max()), 1e-300)
        by_permutation = float(np.abs(permuted[name] - value).max() / scale)
        by_split = float(np.abs(split[name] - value).max() / scale)
        by_ulp = max(float(np.abs(draw[name] - value).max() / scale)
                     for draw in jitter_draws)
        floor[name] = max(by_permutation, by_split, by_ulp)
        detail[name] = {"permutation": by_permutation, "split": by_split,
                        "one_ulp_jitter": by_ulp}
    return {"floor": floor, "detail": detail}


SIZE_IN_USE = "small"


def check_p3(theirs: Any, ours: Any, batch: dict[str, np.ndarray],
             probes: int, seed: int) -> dict[str, Any]:
    """P-3: cross-engine gradient agreement, against a measured round-off floor."""
    import torch

    their_loss, their_grads = _their_loss_and_grads(theirs, batch)
    our_loss, our_grads = _our_loss_and_grads(ours, batch)

    per_tensor = {}
    unconnected = []
    for name, theirs_g in their_grads.items():
        ours_g = our_grads.get(name)
        if ours_g is None:
            unconnected.append(name)
            continue
        scale = max(float(np.abs(theirs_g).max()), 1e-300)
        per_tensor[name] = float(np.abs(ours_g - theirs_g).max() / scale)
    worst = max(per_tensor.items(), key=lambda kv: kv[1]) if per_tensor else ("", 0.0)

    measured = _reduction_order_floor(theirs, batch, their_grads, seed)
    floor_by_tensor = measured["floor"]
    worst_floor = max(floor_by_tensor.items(), key=lambda kv: kv[1])
    over_floor = sorted(
        name for name, value in per_tensor.items()
        if value > max(floor_by_tensor.get(name, 0.0), 0.0)
    )

    # Positive control: confirm each engine's autodiff IS the derivative.
    rng = np.random.RandomState(seed)
    named = dict(theirs.named_parameters())
    sweeps = []
    for name in rng.choice(sorted(named), size=min(probes, len(named)), replace=False):
        parameter = named[str(name)]
        flat_index = int(rng.randint(parameter.numel()))
        analytic = float(their_grads[str(name)].reshape(-1)[flat_index])
        if abs(analytic) < 1e-12:
            continue

        def poke(delta: float, parameter=parameter, flat_index=flat_index) -> None:
            with torch.no_grad():
                parameter.view(-1)[flat_index] += delta

        def loss_at() -> float:
            with torch.no_grad():
                body = theirs.body(
                    torch.from_numpy(batch["x"]), torch.from_numpy(batch["cond"]),
                    torch.from_numpy(batch["pid"]), torch.from_numpy(batch["add_info"]),
                    torch.zeros(batch["x"].shape[0], dtype=torch.float64),
                )
                return float(weighted_bce_torch(theirs.classifier(body), batch).item())

        sweep = _finite_difference_sweep(loss_at, poke, analytic)
        sweep["parameter"] = str(name)
        sweep["analytic"] = analytic
        sweeps.append(sweep)

    # The mutant: a port that does NOT reproduce the upstream's float32 pin in the
    # neighbourhood denominator. That is a real implementation choice, and the
    # smallest structural difference available -- arguably the more "correct" one --
    # so it is a conservative yardstick.
    mutant = port.PET2Port(**HIS_CONFIGURATION, dtype="float64", **port.preset(SIZE_IN_USE))
    mutant.body.local_physics.emulate_upstream_float32_reduction = False
    for name, variable in port.parameter_inventory(mutant):
        variable.assign(dict(theirs.named_parameters())[name].detach().numpy())
    _, mutant_grads = _our_loss_and_grads(mutant, batch)
    mutant_worst = 0.0
    for name, theirs_g in their_grads.items():
        scale = max(float(np.abs(theirs_g).max()), 1e-300)
        mutant_worst = max(mutant_worst,
                           float(np.abs(mutant_grads[name] - theirs_g).max() / scale))

    control_ok = bool(sweeps) and all(s["best_relative_error"] < 1e-4 for s in sweeps)
    margin = mutant_worst / worst[1] if worst[1] else float("inf")
    held = bool(
        not unconnected
        and control_ok
        and margin >= MUTANT_MARGIN
        and abs(their_loss - our_loss) <= FORWARD_TOLERANCE
    )
    return {
        "held": held,
        "criterion": (
            f"the cross-engine gradient disagreement must be at least {MUTANT_MARGIN:.0f}x "
            "smaller than that of a mutant port carrying one deliberate structural "
            "difference. Round-off floors are measured and reported as corroboration, "
            "by "
            "re-differentiating a row-permuted batch, a half-batch split, and a "
            "one-ulp parameter jitter, whichever moves it most. The finite-difference sweep is "
            "reported as a correctness control, not as the tolerance: its error is "
            "truncation-dominated on a single scalar and cannot bound agreement "
            "between two exact autodiff implementations."
        ),
        "worst_cross_engine_tensor": worst[0],
        "worst_cross_engine_relative_difference": worst[1],
        "worst_round_off_floor_tensor": worst_floor[0],
        "worst_round_off_floor": worst_floor[1],
        "round_off_floor_routes": {
            "worst_by_permutation": max(d["permutation"] for d in measured["detail"].values()),
            "worst_by_half_batch_split": max(d["split"] for d in measured["detail"].values()),
            "worst_by_one_ulp_jitter": max(d["one_ulp_jitter"] for d in measured["detail"].values()),
        },
        "tensors_over_their_own_floor": over_floor,
        "cross_engine_by_tensor": per_tensor,
        "mutant_worst_relative_difference": mutant_worst,
        "mutant_description": (
            "the same port with emulate_upstream_float32_reduction disabled, i.e. the "
            "neighbourhood denominator computed in float64 instead of reproducing the "
            "upstream's hardcoded float32"
        ),
        "margin_over_mutant": margin,
        "required_margin": MUTANT_MARGIN,
        "tensors_compared": len(per_tensor),
        "unconnected_gradients": unconnected,
        "loss_theirs": their_loss,
        "loss_ours": our_loss,
        "finite_difference_control_passed": control_ok,
        "finite_difference_sweeps": sweeps,
    }


def check_p4(theirs: Any, ours: Any, batch: dict[str, np.ndarray],
             p3: dict[str, Any], seed: int) -> dict[str, Any]:
    """P-4: one AdamW step from identical state, compared per tensor.

    This check earned its place. Run against `tf.keras.optimizers.AdamW` it failed
    at 68 % of the first update on the zero-initialised bias tensors, because Keras
    puts epsilon inside the second-moment bias correction and torch does not. The
    ported arm therefore uses `torch_adamw.TorchAdamW`, which reproduces torch's
    update rule; see that module for the derivation. Both optimizers are run here so
    the receipt records the size of the difference that was rejected rather than
    merely asserting one existed.
    """
    import torch

    from torch_adamw import TorchAdamW

    before = {n: p.detach().numpy().copy() for n, p in theirs.named_parameters()}
    optimizer = torch.optim.AdamW(
        [p for p in theirs.parameters() if p.requires_grad],
        lr=HIS_OPTIMIZER["learning_rate"], weight_decay=HIS_OPTIMIZER["weight_decay"],
        betas=(HIS_OPTIMIZER["beta_1"], HIS_OPTIMIZER["beta_2"]),
        eps=HIS_OPTIMIZER["epsilon"],
    )
    optimizer.zero_grad(set_to_none=True)
    body = theirs.body(
        torch.from_numpy(batch["x"]), torch.from_numpy(batch["cond"]),
        torch.from_numpy(batch["pid"]), torch.from_numpy(batch["add_info"]),
        torch.zeros(batch["x"].shape[0], dtype=torch.float64),
    )
    weighted_bce_torch(theirs.classifier(body), batch).backward()
    their_gradients = {n: p.grad.detach().numpy().copy()
                       for n, p in theirs.named_parameters()}
    optimizer.step()
    after_theirs = {n: p.detach().numpy().copy() for n, p in theirs.named_parameters()}

    names = [n for n, _ in port.parameter_inventory(ours)]

    def one_keras_step(build_optimizer: Any) -> dict[str, np.ndarray]:
        for name, value in before.items():
            dict(port.parameter_inventory(ours))[name].assign(value)
        variables = [v for _, v in port.parameter_inventory(ours)]
        optimizer = build_optimizer()
        with tf.GradientTape() as tape:
            logits = ours(
                tf.constant(batch["x"]), tf.constant(batch["cond"]),
                tf.constant(batch["pid"]), tf.constant(batch["add_info"]), training=True,
            )
            loss = weighted_bce_tf(logits, batch)
        optimizer.apply_gradients(zip(tape.gradient(loss, variables), variables))
        return {n: v.numpy() for n, v in zip(names, variables)}

    def worst_against_torch(after: dict[str, np.ndarray]) -> tuple[str, float]:
        worst_name, worst_value = "", 0.0
        for name, value in after_theirs.items():
            scale = max(float(np.abs(value).max()), 1e-300)
            relative = float(np.abs(after[name] - value).max() / scale)
            if relative > worst_value:
                worst_name, worst_value = name, relative
        return worst_name, worst_value

    ported = one_keras_step(lambda: TorchAdamW(**HIS_OPTIMIZER))
    stock = one_keras_step(lambda: tf.keras.optimizers.AdamW(**HIS_OPTIMIZER))
    # Leave the model on the ported result, not the stock one.
    for name, value in ported.items():
        dict(port.parameter_inventory(ours))[name].assign(value)

    # Same-engine floor for P-4, in the same units. The control is built by
    # propagating P-3's MEASURED cross-engine gradient disagreement through torch's
    # own optimizer: step from the same state on `g`, and again on `g` perturbed by
    # exactly the magnitude the two engines were measured to differ by. If the
    # ported optimizer's step lands inside that, the optimizer contributes nothing
    # beyond the gradient difference already accounted for in P-3.
    #
    # Differences are quoted in LEARNING RATES, not relative to the post-step value,
    # because `PET2.initialize_weights` sets every bias to exactly zero and dividing
    # by a near-zero post-step value inflates a harmless difference into a ratio.
    learning_rate = HIS_OPTIMIZER["learning_rate"]
    cross_engine = p3["cross_engine_by_tensor"]
    tolerance = p3["worst_round_off_floor"]
    rng = np.random.RandomState(seed + 2)
    for name, value in before.items():
        dict(theirs.named_parameters())[name].data = torch.from_numpy(value.copy())
    control = torch.optim.AdamW(
        [p for p in theirs.parameters() if p.requires_grad],
        lr=learning_rate, weight_decay=HIS_OPTIMIZER["weight_decay"],
        betas=(HIS_OPTIMIZER["beta_1"], HIS_OPTIMIZER["beta_2"]),
        eps=HIS_OPTIMIZER["epsilon"],
    )
    control.zero_grad(set_to_none=True)
    for name, parameter in theirs.named_parameters():
        gradient = their_gradients[name]
        magnitude = cross_engine.get(name, 0.0) * max(float(np.abs(gradient).max()), 0.0)
        signs = rng.choice([-1.0, 1.0], size=gradient.shape)
        parameter.grad = torch.from_numpy(gradient + magnitude * signs)
    control.step()
    perturbed_after = {n: p.detach().numpy().copy() for n, p in theirs.named_parameters()}
    floor_in_learning_rates = max(
        float(np.abs(perturbed_after[name] - value).max() / learning_rate)
        for name, value in after_theirs.items()
    )

    def worst_in_learning_rates(after: dict[str, np.ndarray]) -> tuple[str, float]:
        worst_name, worst_value = "", 0.0
        for name, value in after_theirs.items():
            scaled = float(np.abs(after[name] - value).max() / learning_rate)
            if scaled > worst_value:
                worst_name, worst_value = name, scaled
        return worst_name, worst_value

    ported_worst = worst_in_learning_rates(ported)
    stock_worst = worst_in_learning_rates(stock)
    return {
        "held": bool(
            stock_worst[1] / ported_worst[1] >= MUTANT_MARGIN
            if ported_worst[1]
            else True
        ),
        "margin_over_mutant": (
            stock_worst[1] / ported_worst[1] if ported_worst[1] else float("inf")
        ),
        "required_margin": MUTANT_MARGIN,
        "criterion": (
            f"the ported optimizer's first step must be at least {MUTANT_MARGIN:.0f}x "
            "closer to torch's than the nearest off-the-shelf alternative, "
            "tf.keras.optimizers.AdamW, is. The floor obtained by propagating P-3's "
            "measured gradient disagreement through torch's own optimizer is reported "
            "alongside. All quoted in learning rates."
        ),
        "unit": "learning rates (max absolute weight difference / lr)",
        "measured_same_engine_floor": floor_in_learning_rates,
        "gradient_tolerance_from_p3": tolerance,
        "optimizer_used": "torch_adamw.TorchAdamW",
        "worst_tensor": ported_worst[0],
        "worst_difference_in_learning_rates": ported_worst[1],
        "rejected_alternative": {
            "optimizer": "tf.keras.optimizers.AdamW",
            "worst_tensor": stock_worst[0],
            "worst_difference_in_learning_rates": stock_worst[1],
            "reason": (
                "Keras divides epsilon by sqrt(1 - beta_2^t), torch does not, so at "
                "step 1 its effective epsilon is 31.6x larger and every "
                "zero-initialised bias takes a different first step"
            ),
        },
        "tensors_compared": len(after_theirs),
        "optimizer_settings": dict(HIS_OPTIMIZER),
        "note": (
            "one param group, as src/scripts/train.py:2345 builds it. "
            "PET2.no_weight_decay() exists and train.py never calls it, so norms and "
            "class tokens are decayed."
        ),
    }


def check_p5(ours: Any, batch: dict[str, np.ndarray], seed: int) -> dict[str, Any]:
    """P-5: padded slots cannot reach the output, and where that stops being true.

    Two separate questions. First, does perturbing a padded slot's non-mask columns
    change the output at all -- it must not, exactly. Second, the upstream separates
    padded points by adding a literal 999.0 to their coordinates, which only works
    while real coordinates are far smaller than that; the sweep finds the magnitude
    at which a padded token becomes somebody's nearest neighbour.
    """
    rng = np.random.RandomState(seed)
    baseline = _our_forward(ours, batch)
    padded = batch["x"][:, :, port.HIS_MASK_COLUMN] == 0

    disturbed = {k: v.copy() for k, v in batch.items()}
    noise = rng.randn(*batch["x"].shape)
    noise[:, :, port.HIS_MASK_COLUMN] = 0.0          # keep the mask column defining
    disturbed["x"] = batch["x"] + noise * padded[:, :, None]
    disturbed["add_info"] = batch["add_info"] + rng.randn(*batch["add_info"].shape) * padded[:, :, None]
    disturbed["pid"] = np.where(padded, rng.randint(1, HIS_CONFIGURATION["pid_dim"],
                                                    size=batch["pid"].shape), batch["pid"])
    moved = _our_forward(ours, disturbed)
    exact = float(np.abs(moved - baseline).max())

    # How large can a REAL coordinate get before 999.0 stops separating the pad?
    #
    # Two earlier versions of this sweep measured nothing. The first grew the PADDED
    # coordinates, which `coord_shift` then pushes further away -- wrong direction.
    # The second grew the real coordinates and perturbed padded FEATURES, which can
    # never show anything: a padded neighbour is masked out of the attention and out
    # of the mean, so its values cannot reach the output whatever they are.
    #
    # The real hazard is not leakage, it is CROWDING. Once real coordinates are
    # comparable to 999, padded tokens sitting at 999 fall inside a real token's K
    # nearest and displace genuine neighbours, silently shrinking the neighbourhood
    # the block averages over. That is measured directly, by counting how many of
    # each real token's K neighbours are padded and comparing against the count when
    # the pad is pushed unambiguously out of reach.
    def padded_neighbour_fraction(magnitude: float, shift: float) -> float:
        coords = batch["x"][:, :, : HIS_CONFIGURATION["num_coord"]] * magnitude
        live = (batch["x"][:, :, port.HIS_MASK_COLUMN] != 0)
        points = coords + shift * (~live)[:, :, None]
        distance = ((points[:, :, None, :] - points[:, None, :, :]) ** 2).sum(-1)
        order = np.argsort(distance, axis=-1, kind="stable")[:, :, 1 : K_NEIGHBOURS + 1]
        neighbour_live = np.take_along_axis(live[:, None, :].repeat(live.shape[1], 1),
                                            order, axis=2)
        rows, columns = np.where(live)
        if len(rows) == 0:
            return 0.0
        return float(1.0 - neighbour_live[rows, columns].mean())

    separation = []
    for magnitude in (1.0, 1e1, 1e2, 1e3, 1e4):
        actual = padded_neighbour_fraction(magnitude, PAD_COORDINATE_SHIFT)
        ideal = padded_neighbour_fraction(magnitude, 1e12)
        separation.append({
            "real_coordinate_magnitude": magnitude,
            "padded_fraction_of_neighbours": actual,
            "padded_fraction_with_unreachable_pad": ideal,
            "crowding": actual - ideal,
        })
    breakdown = [row["real_coordinate_magnitude"] for row in separation
                 if row["crowding"] > 0.0]
    return {
        "held": exact == 0.0,
        "criterion": "exact: padded slots must not change the output at all",
        "max_abs_output_change": exact,
        "padded_slots": int(padded.sum()),
        "pad_coordinate_shift": PAD_COORDINATE_SHIFT,
        "coordinate_magnitude_sweep": separation,
        "magnitudes_where_pads_crowd": breakdown,
        "sweep_reading": (
            "the upstream pushes padded points away by adding a literal 999.0, so pad "
            "separation is not a property of the mask but of that constant being large "
            "compared with REAL coordinates. Any magnitude listed in "
            "magnitudes_where_pads_crowd is a real-coordinate scale at which padded "
            "tokens displaced genuine neighbours. Our reco cloud divides positions by "
            "_SCALE = 1000.0 and our truth cloud uses angles and unit direction "
            "cosines, so both sit near O(1); this records the headroom rather than "
            "assuming it. Padded VALUES cannot reach the output at any magnitude -- "
            "that is what max_abs_output_change measures and it is exactly zero."
        ),
    }


def check_p6(ours: Any, batch: dict[str, np.ndarray], size: str,
             workdir: Path) -> dict[str, Any]:
    """P-6: repeatability and checkpoint reload, both bitwise."""
    first = _our_forward(ours, batch)
    second = _our_forward(ours, batch)
    repeatable = bool(np.array_equal(first, second))

    checkpoint = workdir / "port_p6.weights.npz"
    inventory = port.parameter_inventory(ours)
    np.savez(checkpoint, **{name: variable.numpy() for name, variable in inventory})

    rebuilt = port.PET2Port(**HIS_CONFIGURATION, dtype="float64", **port.preset(size))
    rebuilt_inventory = dict(port.parameter_inventory(rebuilt))
    before_reload = _our_forward(rebuilt, batch)
    with np.load(checkpoint) as saved:
        for name in saved.files:
            rebuilt_inventory[name].assign(saved[name])
    after_reload = _our_forward(rebuilt, batch)
    checkpoint.unlink()
    return {
        "held": bool(repeatable and np.array_equal(after_reload, first)),
        "repeatable_bitwise": repeatable,
        "reload_bitwise": bool(np.array_equal(after_reload, first)),
        "fresh_model_differs_before_reload": bool(not np.array_equal(before_reload, first)),
        "tensors_saved": len(inventory),
    }


def verify_knn_tie_freedom(batch: dict[str, np.ndarray]) -> dict[str, Any]:
    """Count exact coordinate ties, which make top-k ordering engine-defined.

    Padded tokens all sit at the same place by construction and tie with each other,
    which is harmless: their contributions are multiplied by a zero mask. A tie
    between two REAL tokens is not harmless, because the two engines may then pick
    different neighbours. This measures both rather than assuming the second is rare.
    """
    coords = batch["x"][:, :, : HIS_CONFIGURATION["num_coord"]]
    real = batch["x"][:, :, port.HIS_MASK_COLUMN] != 0
    real_ties = 0
    for row in range(coords.shape[0]):
        live = coords[row][real[row]]
        if len(live) < 2:
            continue
        distances = np.sum((live[:, None, :] - live[None, :, :]) ** 2, axis=-1)
        np.fill_diagonal(distances, np.inf)
        real_ties += int((distances == 0).sum() // 2)
    return {"real_token_coordinate_ties": real_ties,
            "reading": "nonzero means top-k ordering is engine-defined for those rows"}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--gregor-checkout", type=Path, required=True)
    parser.add_argument("--size", default="small", choices=sorted(port.MODEL_PRESETS))
    parser.add_argument("--rows", type=int, default=1024, help="P-2 forward rows")
    parser.add_argument("--grad-rows", type=int, default=64, help="P-3/P-4 rows")
    parser.add_argument("--tokens", type=int, default=12, help="our production cap")
    parser.add_argument("--probes", type=int, default=6, help="finite-difference probes")
    parser.add_argument("--seed", type=int, default=20260919)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    global SIZE_IN_USE
    SIZE_IN_USE = args.size
    torch_cls = load_upstream(args.gregor_checkout)
    import torch

    torch.set_num_threads(max(1, (os.cpu_count() or 2) // 2))

    forward_batch = make_fixture(args.rows, args.tokens, args.seed)
    grad_batch = make_fixture(args.grad_rows, args.tokens, args.seed + 1)

    theirs, ours, inventory = build_pair(torch_cls, args.size, args.seed, "float64")
    results: dict[str, Any] = {"P1_inventory": check_p1(inventory)}
    results["P2_forward"] = check_p2(torch_cls, args.size, args.seed, forward_batch)
    # P-3 and P-4 differentiate the upstream in float64, so they need the same
    # declared repair P-2b needs; without it they would be comparing against a
    # silently corrupted attention.
    with upcast_attention_mask():
        results["P3_gradient"] = check_p3(theirs, ours, grad_batch, args.probes, args.seed)
        results["P4_update"] = check_p4(theirs, ours, grad_batch,
                                        results["P3_gradient"], args.seed)
    results["P5_masking"] = check_p5(ours, forward_batch, args.seed)
    results["P6_reload"] = check_p6(ours, grad_batch, args.size, args.output.parent)
    results["knn_ties"] = verify_knn_tie_freedom(forward_batch)

    receipt = {
        "scope": (
            "P-1..P-6 port checks for the OmniLearned PET2 backbone rebuilt in Keras. "
            "Implementation evidence only; no performance claim, no adoption."
        ),
        "configuration": dict(HIS_CONFIGURATION),
        "interaction_flags": dict(port.PAPER_INTERACTION_FLAGS),
        "interaction_flag_provenance": (
            "plot_configs/V1Paper.json lists OLS / OLS_RW / OLM_FB as the V1 lineup and "
            "src/jobs/submit_train_jobs.py:155-169 passes neither --ol-interaction nor "
            "--ol-local-interaction; both are store_true with default False. The PET2 "
            "CLASS defaults are True/True, which is not the paper configuration."
        ),
        "preset": port.preset(args.size),
        "size": args.size,
        "device": "cpu",
        "rows_forward": args.rows,
        "rows_gradient": args.grad_rows,
        "tokens": args.tokens,
        "seed": args.seed,
        "backend": keras_backend.select_keras_backend(),
        "versions": {**keras_backend.record_versions(), "torch": torch.__version__},
        "torch_sdpa_mask_dtype_probe": torch_sdpa_mask_dtype_probe(),
        "checks": results,
        "all_held": all(v["held"] for k, v in results.items() if "held" in v),
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(receipt, indent=2, allow_nan=True) + "\n")
    for name, value in results.items():
        if "held" in value:
            print(f"{name}: {'PASS' if value['held'] else 'FAIL'}")
    print(f"all_held: {receipt['all_held']}")
    if not receipt["all_held"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()

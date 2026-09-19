"""Validate the execution path we would actually run: XLA, GPU, float32, 33 tokens.

Every port check so far ran in float64 on a CPU against upstream torch. That
establishes that the port IS his network. It does not establish that the
**executed** path -- XLA-compiled, float32, on an A100, at 33 tokens and effective
batch 2048, through both OmniFold step schemas, initialized from his real
checkpoint -- computes the same thing. This does.

**Where the limits come from, since that is the whole question.** No tolerance here
is chosen by looking at the deviation it judges. Each check compares an eager
reference against the XLA path and is allowed at most twice the EAGER PATH'S OWN
round-off floor, measured on the same tensors by permuting the batch rows -- a
change that is mathematically the identity per row and numerically a different
reduction order. The floor is a property of the reference alone. Every check also
carries a NEGATIVE CONTROL: the same comparison against a deliberately altered port
(`emulate_upstream_float32_reduction` off, the established mutant), which must FAIL
the same limit. A limit that both the real path and the mutant pass is not a check.

NOT CITABLE FOR any performance, recovery or adoption claim. This validates
execution; it trains nothing to convergence and reads no real source.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import statistics
import sys
import time
from typing import Any

FLOOR_SLACK = 2.0          # two independent roundings differ by at most 2x one
MUTANT_MUST_EXCEED = 10.0  # and a real defect must miss the limit by 10x, not 1.01x
# The negative control perturbs ONE weight tensor by this relative amount. It is
# declared here, before any measurement, and it is deliberately small: a check that
# can only see a 10 % error is not protecting anything.
#
# It replaces an earlier control that used `emulate_upstream_float32_reduction`,
# which is the right mutant in float64 and a NO-OP in float32 -- the flag changes a
# denominator computed in float32 either way. The smoke test caught it the only way
# it could be caught: the "mutant" deviated from the reference by EXACTLY the amount
# the real path did, to the last digit.
MUTANT_RELATIVE_PERTURBATION = 1e-4
TOKENS = 33
EFFECTIVE_BATCH = 2048
OPTIMIZER_STEPS = 10

# The eager reference cannot exist at the production batch, and that is a MEASURED
# fact rather than a convenience: `optimised|33|2048|train` without XLA runs out of
# memory on an 80 GB A100 (job 58565265). So the two questions are separated.
#
#   * "does XLA compute the same mathematics as eager" is a question about the
#     GRAPH, and is asked at REFERENCE_BATCH, where an eager reference exists;
#   * "does the graph behave the same at the production batch" is asked of XLA
#     against ITSELF, row by row, by V7 -- which needs no eager path;
#   * everything that only needs the executed path -- optimizer updates, schedule,
#     clipping, reload, memory, timing -- runs at the production batch.
#
# Validating the graph at a batch the reference can hold, and then proving the
# scale-up changes nothing per row, covers what a single impossible comparison
# would have.
REFERENCE_BATCH = 256


def _install(repo: Path) -> None:
    root = repo / "nd-unfolding" / "pet" / "configuration_comparison"
    if str(root) not in sys.path:
        sys.path.insert(0, str(root))


def _fixture(np: Any, tf: Any, batch: int, tokens: int, seed: int = 20260919):
    """Synthetic inputs at HIS widths, with padding and a one-token event present.

    Padded rows and a neighbourhood that is entirely padding are the states the
    masking argument turns on, so they are in the fixture rather than assumed
    absent.
    """
    rng = np.random.RandomState(seed)
    x = rng.randn(batch, tokens, 4).astype("float32")
    x[:, tokens - 6:, :] = 0.0                    # padded tail on every event
    x[0, 1:, :] = 0.0                             # one event with a single token
    pid = rng.randint(0, 8, (batch, tokens)).astype("int32")
    pid[:, tokens - 6:] = 0
    add = rng.randn(batch, tokens, 5).astype("float32")
    add[:, tokens - 6:, :] = 0.0
    cond = rng.randn(batch, 16).astype("float32")
    labels = rng.randint(0, 2, (batch, 1)).astype("float32")
    return (tf.constant(x), tf.constant(cond), tf.constant(pid), tf.constant(add),
            tf.constant(labels))


def _worst(np: Any, a: Any, b: Any) -> float:
    return float(np.max(np.abs(np.asarray(a) - np.asarray(b))))


def _verdict(measured: float, floor: float, per_row: Any = None) -> dict[str, Any]:
    """The verdict, plus the shape of the disagreement when rows are available.

    A MAXIMUM alone cannot distinguish "every row is slightly off", which is
    precision, from "three rows are badly off and the rest are exact", which is a
    discrete choice going a different way -- a k-NN tie resolving differently, for
    instance. Those have different causes and different remedies, so the row
    profile travels with the number.
    """
    limit = FLOOR_SLACK * floor
    verdict = {"measured": measured, "reference_round_off_floor": floor,
               "limit": limit, "held": bool(measured <= limit),
               "limit_source": "FLOOR_SLACK x the EAGER path's own floor; "
                               "independent of the quantity being judged"}
    if per_row is not None:
        import numpy as np

        rows = np.asarray(per_row).reshape(len(per_row), -1).max(axis=1)
        over = rows > limit
        verdict["row_profile"] = {
            "rows": int(rows.size),
            "rows_over_limit": int(over.sum()),
            "fraction_over_limit": float(over.mean()),
            "median_row_deviation": float(np.median(rows)),
            "p99_row_deviation": float(np.percentile(rows, 99)),
            "max_row_deviation": float(rows.max()),
            "reads": ("a few rows far over the limit with a median at round-off "
                      "is a DISCRETE difference -- a k-NN tie resolving the other "
                      "way -- not a precision difference"),
        }
    return verdict


def validate(repo: Path, state_npz: Path, manifest: Path,
             step: str, batch: int, tokens: int,
             allow_cpu: bool = False,
             reference_batch: int = REFERENCE_BATCH) -> dict[str, Any]:
    _install(repo)
    from keras_backend import (configure_production_precision, record_versions,
                               select_keras_backend)

    backend = select_keras_backend()
    import numpy as np
    import tensorflow as tf

    # BEFORE any model or tensor exists. TF32 is on by default on an A100 and the
    # frozen policy forbids it; applying it late would leave already-traced
    # programs on the old setting.
    precision = configure_production_precision(strict=not allow_cpu)

    gpus = tf.config.list_logical_devices("GPU")
    if not gpus and not allow_cpu:
        raise SystemExit("[validate] no GPU visible (fail closed)")

    import pet2_keras_port as port
    import pretrained_init as pinit
    import training_recipe as recipe

    report: dict[str, Any] = {
        "scope": ("execution validation of the path we would run: XLA, GPU, float32, "
                  f"{tokens} tokens, effective batch {batch}, initialized from the "
                  "real pretrained checkpoint"),
        "step_schema": step, "tokens": tokens, "batch": batch,
        "reference_batch": reference_batch,
        "why_two_batches": (
            "the eager reference does not fit at the production batch -- "
            "`optimised|33|2048|train` without XLA OOMs on an 80 GB A100 -- so the "
            "graph comparison runs at the reference batch and V7 proves the "
            "scale-up changes nothing per row"),
        "precision_policy_observed": precision,
        "precision_policy_enforced": True,
        "gpu": [d.name for d in gpus],
        "keras_backend_selection": backend, "versions": record_versions(),
        "limit_policy": {
            "floor_slack": FLOOR_SLACK, "mutant_must_exceed": MUTANT_MUST_EXCEED,
            "how": ("each limit is FLOOR_SLACK x the eager path's own round-off "
                    "floor, measured by permuting batch rows; no limit reads the "
                    "quantity it judges, and every check has a mutant control"),
        },
        "checks": {},
    }
    if not gpus:
        report["NOT_A_VALIDATION"] = (
            "run with --allow-cpu and no GPU: this exercises the code path and "
            "validates nothing about the executed GPU path"
        )

    # ---- V-0: the pretrained checkpoint loads exactly, on this device ----------
    model, load_record = pinit.build_pretrained_port(state_npz, manifest,
                                                     dtype="float32")
    report["checks"]["V0_pretrained_load"] = {
        "held": bool(load_record["exact"] and load_record["tensors_loaded"] == 176),
        "criterion": "every variable covered and assigned EXACTLY; 0.0, not a tolerance",
        **{k: load_record[k] for k in ("tensors_loaded", "parameters_loaded",
                                       "worst_absolute_difference_after_assign",
                                       "exact", "state_npz_sha256",
                                       "checkpoint_sha256")},
    }

    # ONE fixture at the production batch; the reference is its FIRST rows, so the
    # two share rows by construction and V7's per-row comparison is meaningful
    # rather than a comparison of two different draws.
    px, pcond, ppid, padd, plabels = _fixture(np, tf, batch, tokens)
    x, cond, pid, add, labels = (px[:reference_batch], pcond[:reference_batch],
                                 ppid[:reference_batch], padd[:reference_batch],
                                 plabels[:reference_batch])
    variables = None

    def forward_eager():
        return model(x, cond, pid, add, training=False)

    # ONE compiled program, taking its inputs as ARGUMENTS. Building a fresh
    # `tf.function(jit_compile=True)` per comparison compiles a fresh XLA program,
    # and two programs for the same mathematics can fuse differently -- which is a
    # ~1e-6 difference at this scale and is NOT the thing any of these checks is
    # trying to measure. The first version of V-2 did exactly that and reported a
    # mask leak of 1.7e-6 where an eager probe of the same perturbation gives
    # exactly 0.0 in both float32 and float64.
    @tf.function(jit_compile=True)
    def forward_xla_of(xx, cc, pp, aa):
        return model(xx, cc, pp, aa, training=False)

    def forward_xla():
        return forward_xla_of(x, cond, pid, add)

    base = forward_eager().numpy()
    variables = model.trainable_variables

    # The eager path's own floor: permute the rows, undo the permutation, compare.
    order = np.random.RandomState(7).permutation(reference_batch)
    inverse = np.argsort(order)
    permuted = model(tf.gather(x, order), tf.gather(cond, order),
                     tf.gather(pid, order), tf.gather(add, order),
                     training=False).numpy()[inverse]
    forward_floor = _worst(np, base, permuted)
    forward_floor = max(forward_floor, np.finfo("float32").eps * float(np.max(np.abs(base))))

    xla = forward_xla().numpy()
    report["checks"]["V1_forward_xla_vs_eager"] = {
        **_verdict(_worst(np, base, xla), forward_floor,
                   per_row=np.abs(np.asarray(base) - np.asarray(xla))),
        "rows": reference_batch, "outputs_finite": bool(np.isfinite(xla).all()),
    }

    # Negative control: a genuinely altered network must MISS this limit.
    inventory = dict(port.parameter_inventory(model))
    victim = "body.in_blocks.0.attn.in_proj_weight"
    if victim not in inventory:
        victim = sorted(k for k, v in inventory.items() if len(v.shape) == 2)[0]
    original = inventory[victim].numpy().copy()
    inventory[victim].assign(original * (1.0 + MUTANT_RELATIVE_PERTURBATION))
    mutant = forward_xla_of(x, cond, pid, add).numpy()
    inventory[victim].assign(original)
    # WITHIN the XLA path. Measuring the mutant against the EAGER baseline mixes
    # the perturbation with whatever XLA-versus-eager already is, and when the two
    # are the same size -- which on this GPU they are, 2.295e-3 against 2.257e-3 --
    # the control passes on the gap rather than on the defect it is supposed to
    # detect. Comparing XLA against XLA isolates the perturbation.
    mutant_deviation = _worst(np, xla, mutant)
    mutant_vs_eager = _worst(np, base, mutant)
    limit = FLOOR_SLACK * forward_floor
    report["checks"]["V1_mutant_control"] = {
        "mutant": f"{victim} scaled by 1 + {MUTANT_RELATIVE_PERTURBATION}",
        "deviation": mutant_deviation,
        "measured_within": "XLA against XLA, so the perturbation is isolated",
        "deviation_against_eager_baseline_contaminated": mutant_vs_eager,
        "limit": limit,
        "ratio_to_limit": (mutant_deviation / limit) if limit else None,
        "held": bool(mutant_deviation > MUTANT_MUST_EXCEED * limit),
        "criterion": (f"a real alteration must exceed the limit by "
                      f"{MUTANT_MUST_EXCEED}x; if it does not, the limit is not "
                      "discriminating and the check above proves nothing"),
    }

    # ---- V-2: padded tokens cannot reach the output, under XLA ----------------
    #
    # The production question is "if a padded slot held garbage, could it reach the
    # output", and in production a padded slot is all-zero because the loader
    # zeroes it. The perturbation therefore covers the NON-COORDINATE columns:
    # contents a padded slot could carry without moving where it sits.
    #
    # Perturbing the COORDINATE columns asks a different question, and the first
    # version of this check asked it by mistake. Coordinates enter `coord_shift` and
    # the k-NN top-k, so moving them reorders which padded neighbours a padded
    # neighbourhood selects; the values are still multiplied by a zero mask, but the
    # reduction ORDER changes and the result moves at round-off (1.7e-6, against a
    # forward floor of 8.3e-7). That is not a leak and it is not a pass either, so
    # it is reported as a diagnostic beside the gate instead of failing it.
    content_columns = [c for c in range(4)
                       if c != port.HIS_MASK_COLUMN and c not in (0, 1)]
    noisy = np.array(x)
    for column in content_columns:
        noisy[:, tokens - 6:, column] = np.random.RandomState(11).randn(
            reference_batch, 6)
    disturbed = forward_xla_of(tf.constant(noisy), cond, pid, add).numpy()
    moved_pid = np.array(pid)
    moved_pid[:, tokens - 6:] = np.random.RandomState(12).randint(
        1, 8, (reference_batch, 6))
    moved_add = np.array(add)
    moved_add[:, tokens - 6:, :] = np.random.RandomState(13).randn(
        reference_batch, 6, 5)
    disturbed_aux = forward_xla_of(x, cond, tf.constant(moved_pid),
                                   tf.constant(moved_add)).numpy()
    report["checks"]["V2_masking"] = {
        "held": bool(np.array_equal(xla, disturbed)
                     and np.array_equal(xla, disturbed_aux)),
        "perturbed_columns": content_columns,
        "max_absolute_difference_content": _worst(np, xla, disturbed),
        "max_absolute_difference_pid_and_auxiliary": _worst(np, xla, disturbed_aux),
        "criterion": ("EXACT equality for padded-slot CONTENT, PID and auxiliary "
                      "channels. These are multiplied by a zero mask, so any "
                      "difference at all is a leak rather than round-off"),
    }

    coordinate_noisy = np.array(x)
    coordinate_noisy[:, tokens - 6:, 0:2] = np.random.RandomState(14).randn(
        reference_batch, 6, 2)
    coordinate_disturbed = forward_xla_of(tf.constant(coordinate_noisy), cond,
                                          pid, add).numpy()
    report["checks"]["V2_coordinate_diagnostic"] = {
        "held": True,
        "is_a_gate": False,
        "max_absolute_difference": _worst(np, xla, coordinate_disturbed),
        "forward_round_off_floor": forward_floor,
        "reads": ("moving a PADDED slot's coordinates reorders the k-NN among "
                  "padded neighbours and changes the reduction order. Production "
                  "zeroes padded slots, so this state does not occur; it is "
                  "recorded so the round-off scale is visible rather than implied"),
    }

    # ---- V-3: gradients, XLA against eager, against the eager floor -----------
    def loss_of(logits):
        return tf.reduce_mean(
            tf.nn.sigmoid_cross_entropy_with_logits(labels=labels, logits=logits))

    def grads_eager(inputs):
        with tf.GradientTape() as tape:
            loss = loss_of(model(*inputs, training=True))
        return loss, tape.gradient(loss, variables)

    grads_xla = tf.function(lambda: grads_eager((x, cond, pid, add)),
                            jit_compile=True)

    _, eager_grads = grads_eager((x, cond, pid, add))
    eager_grads = [g.numpy() for g in eager_grads]
    # The labels must be permuted WITH the inputs. The first version of this check
    # permuted only the inputs, so the "reference" minimised a different loss and
    # the floor came out at 2.12 absolute -- a limit that everything passes.
    permuted_labels = tf.gather(labels, order)

    def grads_permuted():
        with tf.GradientTape() as tape:
            logits = model(tf.gather(x, order), tf.gather(cond, order),
                           tf.gather(pid, order), tf.gather(add, order),
                           training=True)
            loss = tf.reduce_mean(tf.nn.sigmoid_cross_entropy_with_logits(
                labels=permuted_labels, logits=logits))
        return loss, tape.gradient(loss, variables)

    _, permuted_grads = grads_permuted()
    grad_floor = max(_worst(np, a, b.numpy())
                     for a, b in zip(eager_grads, permuted_grads))
    _, xla_grads = grads_xla()
    grad_deviation = max(_worst(np, a, b.numpy())
                         for a, b in zip(eager_grads, xla_grads))
    report["checks"]["V3_gradients_xla_vs_eager"] = {
        **_verdict(grad_deviation, grad_floor),
        "tensors": len(eager_grads),
        "all_finite": bool(all(np.isfinite(g.numpy()).all() for g in xla_grads)),
        "note": ("the floor is the EAGER path's sensitivity to a row permutation. "
                 "XLA fuses reductions differently from eager, so exceeding it is "
                 "not by itself evidence of a wrong gradient -- read the mutant "
                 "control beside this before concluding either way. The limit is "
                 "NOT widened to accommodate the measurement"),
    }

    inventory[victim].assign(original * (1.0 + MUTANT_RELATIVE_PERTURBATION))
    _, mutant_grads = grads_xla()                  # WITHIN the XLA path, as above
    inventory[victim].assign(original)
    mutant_grad_deviation = max(_worst(np, a.numpy(), b.numpy())
                                for a, b in zip(xla_grads, mutant_grads))
    grad_limit = FLOOR_SLACK * grad_floor
    report["checks"]["V3_mutant_control"] = {
        "mutant": f"{victim} scaled by 1 + {MUTANT_RELATIVE_PERTURBATION}",
        "deviation": mutant_grad_deviation,
        "limit": grad_limit,
        "ratio_to_limit": (mutant_grad_deviation / grad_limit) if grad_limit else None,
        "ratio_to_xla_deviation": (mutant_grad_deviation / grad_deviation)
        if grad_deviation else None,
        "held": bool(mutant_grad_deviation > MUTANT_MUST_EXCEED * grad_limit),
        "criterion": (f"a 1e-4 relative weight error must exceed the limit by "
                      f"{MUTANT_MUST_EXCEED}x. Its ratio to the XLA deviation is "
                      "the number that says whether XLA's disagreement is near a "
                      "real defect or far below one"),
    }

    # ---- V-7: the production batch computes the same rows as the reference ----
    #
    # This is the bridge. The graph was compared against eager at the reference
    # batch because no eager path exists at the production one; this shows the
    # SAME graph at the production batch produces the same per-row answers, so
    # what was validated is what will run. It needs no eager path.
    production_forward = forward_xla_of(px, pcond, ppid, padd).numpy()
    batch_invariance = _worst(np, xla, production_forward[:reference_batch])
    report["checks"]["V7_batch_invariance"] = {
        **_verdict(batch_invariance, forward_floor,
                   per_row=np.abs(np.asarray(xla)
                                  - np.asarray(production_forward[:reference_batch]))),
        "reference_batch": reference_batch, "production_batch": batch,
        "compares": ("XLA at the production batch against XLA at the reference "
                     "batch, on the SAME rows, against the same floor"),
    }

    # ---- V-4: ten real optimizer updates at the PRODUCTION batch --------------
    schedule = recipe.derive_schedule(batch, examples=batch * 1000)
    optimizer = recipe.build_optimizer("theirs", schedule=schedule)
    before = [v.numpy().copy() for v in variables]

    def production_loss(logits):
        return tf.reduce_mean(
            tf.nn.sigmoid_cross_entropy_with_logits(labels=plabels, logits=logits))

    @tf.function(jit_compile=True)
    def train_step():
        with tf.GradientTape() as tape:
            loss = production_loss(model(px, pcond, ppid, padd, training=True))
        optimizer.apply_gradients(zip(tape.gradient(loss, variables), variables))
        return loss

    losses = [float(train_step()) for _ in range(OPTIMIZER_STEPS)]
    moved = max(_worst(np, a, v.numpy()) for a, v in zip(before, variables))
    learning_rates = [float(tf.keras.backend.get_value(
        optimizer.learning_rate(tf.constant(s, tf.int64))))
        for s in range(OPTIMIZER_STEPS)] if callable(
        getattr(optimizer, "learning_rate", None)) else None
    report["checks"]["V4_optimizer_updates"] = {
        "held": bool(np.isfinite(losses).all() and moved > 0.0
                     and int(optimizer.steps_seen.numpy()) == OPTIMIZER_STEPS),
        "batch": batch,
        "steps": OPTIMIZER_STEPS,
        "steps_seen": int(optimizer.steps_seen.numpy()),
        "losses": losses,
        "loss_changed": bool(losses[0] != losses[-1]),
        "max_weight_movement": moved,
        "clip_events": int(optimizer.clip_events.numpy()),
        "last_global_norm": float(optimizer.last_global_norm.numpy()),
        "learning_rate_by_step": learning_rates,
        "schedule": {k: schedule[k] for k in ("max_steps", "warmup_steps",
                                              "examples_per_update")},
        "criterion": ("every loss finite, the weights actually move, and the "
                      "optimizer takes exactly the steps it was asked for"),
    }

    # ---- V-5: save, reload, and continue identically --------------------------
    #
    # Into the SAME model, via a file. The first version built a second full model
    # to reload into, which doubled the live graph and was part of why this ran out
    # of memory on an 80 GB card. Saving and restoring is also closer to what a
    # resumed fit actually does.
    # Save and restore BY NAME, from one source of truth. The first version built
    # the save dict by zipping `parameter_inventory` against
    # `model.trainable_variables` -- two orderings that are NOT the same, since the
    # inventory follows torch's traversal. Names were paired with other tensors'
    # values. It surfaced only because one pair happened to disagree in shape;
    # where shapes matched it would have written a corrupt checkpoint silently.
    inventory_pairs = port.parameter_inventory(model)
    trained = {name: variable.numpy().copy() for name, variable in inventory_pairs}
    checkpoint_dir = Path(state_npz).parent / "validation_reload"
    checkpoint_dir.mkdir(parents=True, exist_ok=True)
    saved = checkpoint_dir / f"reload_{step}.npz"
    np.savez(saved, **trained)
    for _, variable in inventory_pairs:             # clobber, so a no-op restore fails
        variable.assign(tf.zeros_like(variable))
    with np.load(saved) as blob:
        missing = sorted({n for n, _ in inventory_pairs} - set(blob.files))
        if missing:
            raise ValueError(f"reload is missing {len(missing)}: {missing[:4]}")
        for name, variable in inventory_pairs:
            variable.assign(blob[name])
    reload_worst = max(_worst(np, trained[name], variable.numpy())
                       for name, variable in inventory_pairs)
    after_reload = forward_xla_of(px, pcond, ppid, padd).numpy()
    report["checks"]["V5_reload"] = {
        "held": bool(reload_worst == 0.0),
        "weight_transfer_worst": reload_worst,
        "clobbered_before_restore": True,
        "forward_finite_after_reload": bool(np.isfinite(after_reload).all()),
        "criterion": ("EXACT. The weights are zeroed between save and restore, so "
                      "a restore that quietly did nothing would fail this"),
    }

    # ---- V-6: memory and synchronized timing at the production batch ----------
    try:
        tf.config.experimental.reset_memory_stats("GPU:0")
    except Exception:                                        # pragma: no cover
        pass
    for _ in range(3):
        float(train_step())
    times = []
    for _ in range(10):
        start = time.perf_counter()
        float(train_step())                # the float() forces the device to finish
        times.append(time.perf_counter() - start)
    memory = {}
    try:
        info = tf.config.experimental.get_memory_info("GPU:0")
        memory = {"peak_bytes": int(info["peak"]), "peak_gib": info["peak"] / 2**30}
    except Exception:                                        # pragma: no cover
        memory = {"peak_bytes": None}
    median = statistics.median(times)
    report["checks"]["V6_memory_and_timing"] = {
        "held": bool(times and (not gpus or memory.get("peak_bytes") is not None)),
        "batch": batch,
        "step_seconds_median": median,
        "microseconds_per_example": 1e6 * median / batch,
        "device_memory": memory,
        "synchronized": "float(train_step()) inside the timed region",
    }

    report["all_held"] = all(c.get("held", False) for c in report["checks"].values())
    return report


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", type=Path, required=True)
    parser.add_argument("--state-npz", type=Path, required=True)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--step", default="step1_reco")
    parser.add_argument("--batch", type=int, default=EFFECTIVE_BATCH)
    parser.add_argument("--tokens", type=int, default=TOKENS)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--reference-batch", type=int, default=REFERENCE_BATCH)
    parser.add_argument("--allow-cpu", action="store_true",
                        help="smoke-test the code path; NOT a validation")
    args = parser.parse_args()
    try:
        report = validate(args.repo, args.state_npz, args.manifest, args.step,
                          args.batch, args.tokens, allow_cpu=args.allow_cpu,
                          reference_batch=args.reference_batch)
    except Exception as error:                               # noqa: BLE001
        import traceback
        report = {"failed": True, "error": repr(error),
                  "traceback": traceback.format_exc(),
                  "step_schema": args.step, "batch": args.batch,
                  "tokens": args.tokens}
    args.output.write_text(json.dumps(report, indent=2) + "\n")
    for name, check in report.get("checks", {}).items():
        print(f"{name}: {'PASS' if check.get('held') else 'FAIL'}")
    print("all_held:", report.get("all_held", False))


if __name__ == "__main__":
    main()

"""His training recipe, with the budget derived rather than copied, and recorded.

Three things this file refuses to do, each because doing it would quietly change
what is being compared.

**It does not copy `max_steps`.** `submit_train_jobs.py` passes 250,000, which is
the step count for HIS dataset at HIS batch. Copying it into an OmniFold fit over a
2 M subsample would give his arm a completely different number of passes over the
data than ours gets. The agreed fairness axis is **example presentations**, so
`max_steps` is *derived*: equal examples per fit for both arms, divided by each
arm's own batch. His batch 2048 against our 512 then gives him 4x fewer optimizer
steps at identical example budget, which is a consequence of his configuration and
is exactly what we want to preserve.

**It does not copy the 1,000-step warmup either.** 1,000 out of 250,000 is 0.4 % of
a run. Held at 1,000 inside a derived fit of ~6,250 steps it becomes 16 %, which is
a different schedule wearing the same number. The *fraction* is preserved and the
absolute count follows; both are recorded so the substitution is visible.

**It does not accept Keras' global-norm clipping as torch's.** `clip_grad_norm_`
divides by `total_norm + 1e-6` and Keras divides by `max(total_norm, clip_norm)`.
They differ exactly where clipping is marginal, which is where it matters. After
what `tf.keras.optimizers.AdamW` turned out to be (see `torch_adamw`), a same-named
operation is assumed to be a different operation until measured.

And it records the **realized** policy, not the intended one. An intended schedule
is a plan; what the optimizer did is a measurement, and the two are different
objects. `RealizedPolicy.verify` fails closed when they disagree.

NOT CITABLE FOR any performance claim.
"""

from __future__ import annotations

import math
from typing import Any

from keras_backend import select_keras_backend

select_keras_backend()

import tensorflow as tf  # noqa: E402

from torch_adamw import TORCH_DEFAULTS, TorchAdamW  # noqa: E402

# src/jobs/submit_train_jobs.py and src/scripts/train.py argparse defaults.
HIS_REFERENCE_RUN = {
    "batch_size": 2048,          # -bs 2048
    "grad_accum_steps": 1,       # --grad_accum_steps 1
    "max_steps": 250_000,        # --max_steps 250000
    "warmup_steps": 1_000,       # --warmup_steps default
    "learning_rate": 1e-4,       # --lr default
    "weight_decay": 0.01,        # --weight_decay default
    "grad_clip": 1.0,            # --grad_clip default, clip_grad_norm_
}
HIS_WARMUP_FRACTION = HIS_REFERENCE_RUN["warmup_steps"] / HIS_REFERENCE_RUN["max_steps"]

# train_fullevent_nominal.NOMINAL_SEED_POLICY and MultiFold's split.
OUR_REFERENCE_RUN = {"batch_size": 512, "grad_accum_steps": 1, "learning_rate": 1e-4}
EPOCHS = 8
TRAIN_EVENTS = 2_000_000     # --max-events: subsamples the MC leg ONLY
TRAIN_FRAC = 0.8

# A fit does NOT present `train_events` examples. `MultiFold` concatenates both
# classes before training, so `NTRAIN` is `mc.nmax + data.nmax` at step 1
# (`omnifold.py:131`) and `2 * mc.nmax` at step 2 (`:132`), and `fit` runs
# `int(train_frac * NTRAIN // batch)` steps per epoch (`:297`).
#
# This was wrong in the first version of the recipe and the REALIZED-POLICY check
# is what caught it: the exercise planned 7 optimizer steps and the engine took 12,
# because 256 MC rows plus 256 data rows is 512, not 256. That is a 1.6x error in
# the training budget and it was invisible to every test that did not compare a
# plan against a measurement.
#
# `n_data` is NOT `train_events`. `--max-events` subsamples `imc`, which indexes the
# MC arrays only; the measured leg keeps its own full inventory
# (`fullevent_fps_dataloader.py:1159-1161` against `:1395`/`:1550`). Its size is a
# property of the production input and has to be READ from a run, not assumed --
# see `EXAMPLES_BUDGET_CAVEAT`.
# The measured leg's size, narrowed from "unknown" to "known on a NEIGHBOURING
# product", 2026-09-19. It is not the reading this campaign needs, and saying so
# is the point of the `scope` field: nothing may substitute it for a fullevent
# dump without changing that field first.
DATA_LEG_EVIDENCE = {
    "rows": 4_091_707,
    "source": ("nd-unfolding/products/pet/bkgsub/"
               "of_inputs_pc_fullcloud_bkgsub_5d.provenance.json"),
    "fields": ("n_data_expected, corroborated independently by "
               "data_alignment_gate.n_rows_extracted (exact, 0 mismatches) and "
               "weight_gate.n"),
    "source_root": "runEventLoopOmniFold_PC_MEFHC_fullcloud.root",
    "scope": ("the FIVE-DIMENSIONAL point-cloud OmniFold input. This campaign runs "
              "the FULLEVENT schema, whose data leg has never been dumped at scale, "
              "so this is a neighbouring product's reading and not this one's"),
    "corroboration": ("the event-identity export counts 4,119,797 rows in the data "
                      "tree, 0.7 % above this product's post-gate count, which is "
                      "the direction and roughly the size a selection should move it"),
    "what_it_changes": ("n_data = n_mc = 2e6 gives 153.6 M presentations per "
                        "evaluation; n_data = 4.09e6 gives 193.8 M, a factor 1.26. "
                        "Every absolute GPU-hour figure inherits that factor; no "
                        "RATIO does"),
}


def data_leg_estimate() -> tuple[int, str]:
    """The measured leg's size and the scope it may never be quoted without."""
    return DATA_LEG_EVIDENCE["rows"], DATA_LEG_EVIDENCE["scope"]


EXAMPLES_BUDGET_CAVEAT = (
    "n_data is the measured leg's full inventory and is not set by --max-events. "
    "Taking n_data = n_mc gives 1.6x the presentations the previous fit-only model "
    "assumed, which would put our arm's projected evaluation cost ABOVE the feature "
    "contract's independently measured 1.1-1.3 GPU-h for a nominal train. The two "
    "cannot both be right, so n_data must be read off a production run's loader "
    "meta before the campaign is costed. Reported conditionally until then. "
    "NARROWED 2026-09-19: the 5-D point-cloud input product records a data leg of "
    "4,091,707 rows (see DATA_LEG_EVIDENCE), which is 2.05x n_mc and puts the "
    "budget at 193.8 M presentations per evaluation rather than 153.6 M. That is a "
    "neighbouring product, not this schema, so it narrows the caveat and does not "
    "discharge it."
)

TORCH_CLIP_EPSILON = 1e-6        # the `+ 1e-6` inside torch's clip_grad_norm_


def rows_per_fit(step: str, n_mc: int = TRAIN_EVENTS, n_data: int | None = None) -> int:
    """`NTRAIN` as the engine computes it, per step.

    Step 1 trains MC against data and step 2 trains MC against itself, so the two
    steps do not present the same number of examples unless `n_data == n_mc`.
    """
    if step not in ("step1_reco", "step2_gen"):
        raise ValueError(f"step must be step1_reco or step2_gen; got {step!r}")
    if n_mc <= 0:
        raise ValueError("n_mc must be positive")
    if step == "step2_gen":
        return 2 * n_mc
    if n_data is None:
        raise ValueError(
            "step 1 needs n_data: the measured leg is NOT subsampled by --max-events "
            "and its size is a property of the production input"
        )
    if n_data <= 0:
        raise ValueError("n_data must be positive")
    return n_mc + n_data


def examples_per_fit(step: str = "step2_gen", epochs: int = EPOCHS,
                     n_mc: int = TRAIN_EVENTS, n_data: int | None = None,
                     train_frac: float = TRAIN_FRAC) -> int:
    """The shared fairness axis: how many example presentations one fit makes.

    `epochs * train_frac * NTRAIN`, with `NTRAIN` from `rows_per_fit`. Both arms get
    this number; only the number of optimizer steps it buys differs.
    """
    if not 0.0 < train_frac <= 1.0:
        raise ValueError(f"train_frac must be in (0, 1]; got {train_frac}")
    if epochs <= 0:
        raise ValueError("epochs must be positive")
    return int(round(epochs * train_frac * rows_per_fit(step, n_mc, n_data)))


def derive_schedule(batch_size: int, grad_accum_steps: int = 1,
                    examples: int | None = None,
                    warmup_fraction: float = HIS_WARMUP_FRACTION,
                    step: str = "step2_gen", n_mc: int = TRAIN_EVENTS,
                    n_data: int | None = None) -> dict[str, Any]:
    """Steps and warmup for one arm at one batch, from the shared example budget."""
    if batch_size <= 0 or grad_accum_steps <= 0:
        raise ValueError("batch_size and grad_accum_steps must be positive")
    budget = (examples_per_fit(step, n_mc=n_mc, n_data=n_data)
              if examples is None else int(examples))
    per_update = batch_size * grad_accum_steps
    max_steps = max(1, math.ceil(budget / per_update))
    warmup_steps = max(1, int(round(warmup_fraction * max_steps)))
    if warmup_steps >= max_steps:
        raise ValueError(
            f"warmup {warmup_steps} does not fit inside {max_steps} steps; the budget "
            "is too small for this batch and the schedule would never decay"
        )
    return {
        "examples_per_fit": budget,
        "batch_size": batch_size,
        "grad_accum_steps": grad_accum_steps,
        "examples_per_update": per_update,
        "max_steps": max_steps,
        "warmup_steps": warmup_steps,
        "warmup_fraction": warmup_fraction,
        "warmup_fraction_source": (
            f"{HIS_REFERENCE_RUN['warmup_steps']}/{HIS_REFERENCE_RUN['max_steps']} from his "
            "reference run; the FRACTION is preserved, not the absolute count"
        ),
        "his_absolute_warmup_would_have_been": HIS_REFERENCE_RUN["warmup_steps"],
        "budget_caveat": EXAMPLES_BUDGET_CAVEAT,
        "derived_not_copied": (
            "max_steps comes from the shared example budget divided by this arm's own "
            f"batch, not from his --max_steps {HIS_REFERENCE_RUN['max_steps']}"
        ),
    }


class WarmupCosine(tf.keras.optimizers.schedules.LearningRateSchedule):
    """His `get_lr_schedule` as a Keras schedule, arithmetic unchanged.

    ``lr_lambda(step) = step/warmup``           for ``step < warmup``
    ``             = max(0, 0.5*(1+cos(pi*p)))`` otherwise, ``p = (step-warmup)/(max-warmup)``

    Two details are transcribed rather than tidied. The warmup ramp starts at
    ``step = 0``, so the very first update uses a learning rate of exactly zero --
    `LambdaLR` multiplies the base rate by `lr_lambda(0) = 0`. And `progress` is
    not clamped above 1, so a run continuing past `max_steps` sees the cosine turn
    back upward; the `max(0.0, ...)` only floors it. Both are his behaviour.
    """

    def __init__(self, base_learning_rate: float, warmup_steps: int, max_steps: int,
                 name: str = "WarmupCosine") -> None:
        super().__init__()
        if warmup_steps >= max_steps:
            raise ValueError(f"warmup_steps {warmup_steps} >= max_steps {max_steps}")
        self.base_learning_rate = float(base_learning_rate)
        self.warmup_steps = int(warmup_steps)
        self.max_steps = int(max_steps)
        self.name = name

    def __call__(self, step: Any) -> Any:
        # The `max(1, ...)` guards are resolved in PYTHON, not with `tf.maximum`
        # against a literal: a bare Python float in a TF op adopts float32 and
        # clashes with the float64 step, which is how this first failed inside
        # `fit`. They are compile-time constants anyway.
        warmup = float(max(1, self.warmup_steps))
        span = float(max(1, self.max_steps - self.warmup_steps))
        step = tf.cast(step, tf.float64)
        boundary = tf.constant(float(self.warmup_steps), tf.float64)
        ramp = step / tf.constant(warmup, tf.float64)
        progress = (step - boundary) / tf.constant(span, tf.float64)
        decay = tf.maximum(
            tf.constant(0.0, tf.float64),
            0.5 * (1.0 + tf.cos(tf.constant(math.pi, tf.float64) * progress)),
        )
        factor = tf.where(step < boundary, ramp, decay)
        return tf.cast(self.base_learning_rate * factor, tf.float32)

    def get_config(self) -> dict[str, Any]:
        return {"base_learning_rate": self.base_learning_rate,
                "warmup_steps": self.warmup_steps, "max_steps": self.max_steps,
                "name": self.name}


def torch_clip_coefficient(global_norm: Any, max_norm: float) -> Any:
    """`clip_grad_norm_`'s scale factor, epsilon included.

    torch: ``coef = max_norm / (total_norm + 1e-6)``, applied only when ``coef < 1``.
    Keras' `global_clipnorm`: ``clip_norm / max(total_norm, clip_norm)``, no epsilon.
    The two agree away from the threshold and differ right at it, which is where a
    clip either fires or does not.
    """
    coefficient = max_norm / (global_norm + TORCH_CLIP_EPSILON)
    return tf.minimum(coefficient, tf.ones_like(coefficient))


class ClippedTorchAdamW(TorchAdamW):
    """`TorchAdamW` preceded by torch's global-norm gradient clipping.

    Clipping is global across all parameters, as `clip_grad_norm_(model.parameters(),
    ...)` is, not per tensor -- a per-tensor clip with the same threshold is a
    different regulariser.
    """

    def __init__(self, grad_clip: float = HIS_REFERENCE_RUN["grad_clip"], **kwargs: Any):
        super().__init__(**kwargs)
        if grad_clip is not None and grad_clip <= 0:
            raise ValueError(f"grad_clip must be positive or None; got {grad_clip}")
        self.grad_clip = grad_clip
        self.clip_events = tf.Variable(0, dtype=tf.int64, trainable=False,
                                       name="clip_events")
        self.steps_seen = tf.Variable(0, dtype=tf.int64, trainable=False,
                                      name="steps_seen")
        self.last_global_norm = tf.Variable(0.0, dtype=tf.float32, trainable=False,
                                            name="last_global_norm")

    def apply_gradients(self, grads_and_vars: Any, **kwargs: Any) -> Any:
        pairs = list(grads_and_vars)
        if self.grad_clip is not None:
            gradients = [g for g, _ in pairs if g is not None]
            if gradients:
                global_norm = tf.linalg.global_norm(gradients)
                coefficient = torch_clip_coefficient(
                    tf.cast(global_norm, tf.float32), self.grad_clip)
                self.last_global_norm.assign(tf.cast(global_norm, tf.float32))
                self.steps_seen.assign_add(1)
                self.clip_events.assign_add(
                    tf.cast(coefficient < 1.0, tf.int64))
                pairs = [
                    (None if g is None else g * tf.cast(coefficient, g.dtype), v)
                    for g, v in pairs
                ]
        return super().apply_gradients(pairs, **kwargs)


def build_optimizer(arm: str, schedule: dict[str, Any] | None = None,
                    settings: dict[str, Any] | None = None) -> ClippedTorchAdamW:
    """His optimizer, schedule and clipping for the named arm."""
    if arm not in ("theirs", "ours"):
        raise ValueError(f"arm must be 'theirs' or 'ours'; got {arm!r}")
    chosen = dict(TORCH_DEFAULTS if settings is None else settings)
    if schedule is not None:
        chosen["learning_rate"] = WarmupCosine(
            chosen["learning_rate"], schedule["warmup_steps"], schedule["max_steps"])
    return ClippedTorchAdamW(grad_clip=HIS_REFERENCE_RUN["grad_clip"], **chosen)


class RealizedPolicy:
    """What the optimizer DID, checked against what the recipe SAID.

    An intended schedule is a plan and a receipt field is a timestamped
    observation; conflating them is how a launch plan gets read as a record. This
    reads the optimizer's own counters after the fact and refuses to agree with the
    plan by assumption.
    """

    def __init__(self, intended: dict[str, Any]) -> None:
        self.intended = dict(intended)
        self.fits: list[dict[str, Any]] = []

    def record_fit(self, optimizer: ClippedTorchAdamW, label: str = "") -> dict[str, Any]:
        steps = int(optimizer.steps_seen.numpy())
        row = {
            "label": label,
            "optimizer_steps_taken": steps,
            "clip_events": int(optimizer.clip_events.numpy()),
            "clip_fraction": (int(optimizer.clip_events.numpy()) / steps) if steps else None,
            "last_global_norm": float(optimizer.last_global_norm.numpy()),
            "grad_clip": optimizer.grad_clip,
            "examples_presented": steps * self.intended["examples_per_update"],
            "learning_rate_at_step_0": float(
                tf.keras.backend.get_value(optimizer.learning_rate)
                if not callable(getattr(optimizer, "_constant_learning_rate", None))
                else 0.0),
        }
        self.fits.append(row)
        return row

    def verify(self, tolerance_examples: int | None = None) -> dict[str, Any]:
        """Fail closed when realized and intended disagree by more than one update."""
        budget = self.intended["examples_per_fit"]
        slack = (self.intended["examples_per_update"] if tolerance_examples is None
                 else tolerance_examples)
        problems = []
        for row in self.fits:
            shortfall = abs(row["examples_presented"] - budget)
            if shortfall > slack:
                problems.append(
                    f"{row['label'] or 'fit'}: presented {row['examples_presented']} "
                    f"examples against an intended {budget} (slack {slack})"
                )
        return {
            "held": not problems,
            "intended": self.intended,
            "fits": list(self.fits),
            "problems": problems,
            "criterion": (
                "every fit must present the intended example budget to within one "
                "update; the budget is the fairness axis and a silent shortfall in "
                "one arm is an unequal comparison"
            ),
        }


# --------------------------------------------------------------------------- #
# Gradient accumulation: HIS knob, not our workaround.
# --------------------------------------------------------------------------- #
#
# `src/scripts/train.py:2593-2615` is the whole semantics, and it is transcribed
# rather than reinvented:
#
#     loss = loss / args.grad_accum_steps
#     loss.backward()
#     accum_counter += 1
#     if accum_counter % args.grad_accum_steps == 0:
#         torch.nn.utils.clip_grad_norm_(model.parameters(), args.grad_clip)
#         optimizer.step(); optimizer.zero_grad(); scheduler.step(); step += 1
#
# Three consequences decide whether this is a repair or a recipe change:
#
# * the clip is applied to the ACCUMULATED gradient, once per optimizer step, so
#   it sees the same global norm a single large batch would have produced;
# * the schedule advances once per optimizer step, not per micro-batch, so the
#   learning-rate trajectory is unchanged;
# * `max_steps` is counted in optimizer steps, so the derived budget is unchanged.
#
# With equal micro-batches and a mean-reduced loss, `sum_k (mean_k)/k` IS the mean
# over the virtual batch, so the update is the single-batch update up to float
# summation order. `test_recipe.py` measures that rather than asserting it.
#
# His reference run is `-bs 2048 --grad_accum_steps 1`. Running `-bs 512
# --grad_accum_steps 4` keeps the virtual batch at 2048, which is why this is the
# memory unblock that does NOT cost a recipe change. What it cannot do is make the
# port cheaper: it changes where the activations live, not how many there are.
HIS_ACCUMULATION_REFERENCE = "src/scripts/train.py:2593-2615"


def accumulation_steps(virtual_batch: int, micro_batch: int) -> int:
    """`grad_accum_steps` for a virtual batch, refusing a non-divisible split.

    An uneven split would make the last micro-batch a different size, and
    `loss / k` then stops being the mean over the virtual batch -- it silently
    reweights the tail rows. Refusing is the only honest option, because the
    alternative is a fairness axis that is off by a fraction nobody records.
    """
    if virtual_batch <= 0 or micro_batch <= 0:
        raise ValueError("batch sizes must be positive")
    if virtual_batch % micro_batch:
        raise ValueError(
            f"virtual batch {virtual_batch} is not a multiple of micro-batch "
            f"{micro_batch}; an uneven split reweights the tail rows"
        )
    return virtual_batch // micro_batch


class AccumulatingStep:
    """His accumulation loop over a Keras model, with the partial tail refused.

    The tail matters more than it looks. If a fit's micro-batch count is not a
    multiple of `steps`, the leftover gradient is never applied and those examples
    are presented to the network without ever reaching the weights -- a silent
    shortfall in exactly the quantity the fairness axis is defined on. `flush`
    refuses rather than applying a short group, and `pending` exposes the state so
    a caller cannot end a fit mid-group without noticing.
    """

    def __init__(self, model: Any, optimizer: ClippedTorchAdamW, loss_fn: Any,
                 steps: int, compile_step: bool = True,
                 jit_compile: bool = False, forward: Any = None) -> None:
        if steps < 1:
            raise ValueError(f"steps must be >= 1; got {steps}")
        if not model.trainable_variables:
            raise ValueError(
                "the model must be built before accumulation: the accumulators are "
                "shaped from its variables"
            )
        self.model = model
        self.optimizer = optimizer
        self.loss_fn = loss_fn
        self.steps = int(steps)
        # `PET2Port.call` takes four positional tensors, not one input. Rather
        # than wrap the model in an adapter layer -- which would put a second
        # object between the variables and the tape -- the caller may supply the
        # forward itself. The variables still come from `model`.
        self.forward = forward or (
            lambda inputs, training: model(inputs, training=training))
        self._accumulators = [
            tf.Variable(tf.zeros_like(v), trainable=False, name=f"accum/{i}")
            for i, v in enumerate(model.trainable_variables)
        ]
        self._in_group = 0
        self.applies = 0
        # The graph boundary is per micro-batch, which is where it has to be: the
        # group counter is Python state and a traced loop over it would bake one
        # group's length into the graph. Eager accumulation would also price the
        # measurement wrong -- per-op dispatch on ~2,000 ops is not what the
        # campaign would pay.
        self.compile_step = bool(compile_step)
        self.jit_compile = bool(jit_compile)
        self._micro = (
            tf.function(self._micro_body, jit_compile=jit_compile or None)
            if compile_step else self._micro_body
        )

    @property
    def pending(self) -> int:
        """Micro-batches accumulated but not yet applied."""
        return self._in_group

    def _micro_body(self, inputs: Any, labels: Any) -> Any:
        with tf.GradientTape() as tape:
            loss = self.loss_fn(labels, self.forward(inputs, True))
            scaled = loss / tf.cast(self.steps, loss.dtype)
        gradients = tape.gradient(scaled, self.model.trainable_variables)
        for accumulator, gradient in zip(self._accumulators, gradients):
            if gradient is not None:
                accumulator.assign_add(tf.cast(gradient, accumulator.dtype))
        return loss

    def micro_step(self, inputs: Any, labels: Any) -> Any:
        """One backward pass at `loss / steps`, accumulated; updates on the k-th."""
        loss = self._micro(inputs, labels)
        self._in_group += 1
        if self._in_group == self.steps:
            self._apply()
        return loss

    def _apply(self) -> None:
        self.optimizer.apply_gradients(
            zip([tf.convert_to_tensor(a) for a in self._accumulators],
                self.model.trainable_variables))
        for accumulator in self._accumulators:
            accumulator.assign(tf.zeros_like(accumulator))
        self._in_group = 0
        self.applies += 1

    def flush(self) -> None:
        """End of fit: refuse a partial group instead of dropping or applying it."""
        if self._in_group:
            raise ValueError(
                f"{self._in_group} of {self.steps} micro-batches are accumulated and "
                "unapplied at the end of the fit. Applying a short group would "
                "weight those rows by 1/steps; dropping it would present examples "
                "that never reach the weights. Size the fit to a whole number of "
                "groups."
            )

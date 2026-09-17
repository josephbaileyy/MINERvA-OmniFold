"""The validation battery, and the setup path it validates.

Two things live here on purpose. ``prepare_run`` builds the fixture, applies the cap
treatment, forms the bucket plan, enforces the width guard, and constructs the model
and optimizer -- and it is the **same function the training runner calls**, so what
gets validated is literally what trains. ``ValidationBattery`` then runs the frozen
checks against that prepared state.

Thresholds are never written here. They are read from
``VALIDATION_CRITERIA-20260918.json`` and its digest is recorded in every receipt, so
a threshold relaxed after seeing a failure changes the digest and shows up in the
evidence.

On the cross-device question this module does **not** drop cross-device checking. It
runs the full comparison and classifies the width: tier 1 if everything passes, tier 2
if the only failures are in the frozen exempt list, and a hard stop otherwise -- or if
a sub-check that passed at a tier-2 width later regresses.
"""

from __future__ import annotations

from dataclasses import dataclass, field
import hashlib
import json
from pathlib import Path
import statistics
from typing import Any, Sequence

import numpy as np


@dataclass(frozen=True)
class Criteria:
    """Frozen thresholds plus the digest that makes them auditable."""

    body: dict[str, Any]
    sha256: str
    path: str

    @property
    def atol(self) -> float:
        return float(self.body["campaign_tolerances"]["atol"])

    @property
    def rtol(self) -> float:
        return float(self.body["campaign_tolerances"]["rtol"])

    def check(self, name: str) -> dict[str, Any]:
        """Return one check's frozen configuration, or fail loudly."""
        checks = self.body["checks"]
        if name not in checks:
            raise KeyError(f"No frozen criterion named {name}")
        return checks[name]

    @property
    def exempt_subchecks(self) -> tuple[str, ...]:
        return tuple(self.body["release_tiers"]["exempt_cross_device_subchecks"])


def load_criteria(path: Path) -> Criteria:
    """Load the frozen criteria and digest the bytes that were loaded."""
    payload = path.read_bytes()
    return Criteria(
        body=json.loads(payload),
        sha256=hashlib.sha256(payload).hexdigest(),
        path=str(path),
    )


@dataclass
class PreparedRun:
    """Everything the training loop and the battery both need."""

    arm: Any
    width: tuple[int, ...]
    inputs: dict[str, Any]
    target: np.ndarray
    model: Any
    optimizer: Any
    buckets: dict[tuple[int, ...], np.ndarray]
    plan: list[tuple[tuple[int, ...], np.ndarray]]
    geometry: dict[str, Any]
    rows: int
    notes: list[str] = field(default_factory=list)


def prepare_run(
    modules: dict[str, Any],
    arm: Any,
    width: tuple[int, ...],
    *,
    rows: int,
    batch_size: int,
    seed: int,
    validated_widths: Sequence[tuple[int, ...]] | None,
    cluster_range: tuple[int, int] = (4, 40),
) -> PreparedRun:
    """Build the real training state for one arm at one uniform typed width.

    Called by both the validation entry and the training entry, so the geometry
    guard, the bucket plan and the model construction cannot diverge between what was
    checked and what runs.
    """
    fourarm = modules["fourarm"]
    typed = modules["typed"]
    adapter = modules["adapter"]
    runner = modules["runner"]
    comparison = modules["comparison"]
    tf = modules["tf"]

    counts = np.tile(np.asarray(width, dtype=np.int64), (rows, 1))
    batch = fourarm.build_variable_typed_batch(typed, counts, seed)
    rng = np.random.default_rng(seed)
    event = rng.normal(size=(rows, 13)).astype(np.float32)
    low, high = cluster_range
    clouds = [
        np.column_stack(
            [
                rng.gamma(2.0, 50.0, size=size),
                rng.normal(size=(size, 4)),
                np.zeros((size, len(fourarm.AGGREGATE_CHANNELS))),
            ]
        ).astype(np.float32)
        for size in rng.integers(low, high, size=rows)
    ]
    generic = fourarm.apply_cap(clouds, arm.cap_treatment)
    inputs = dict(adapter.prepare_keras_inputs(batch, event))
    inputs.update(
        generic_values=generic,
        generic_mask=np.ones(generic.shape[:2], dtype=bool),
    )
    families = tuple(contract.name for contract in typed.FAMILY_CONTRACTS)
    if not arm.typed_enabled:
        inputs = fourarm.disable_families(inputs, families)

    widths = fourarm.typed_widths(inputs, rows, families)
    buckets = fourarm.bucket_events(widths)
    fourarm.verify_partition(buckets, rows)
    plan = fourarm.batch_plan(buckets, batch_size, seed)
    fourarm.verify_plan_covers_events(plan, rows)

    guard = fourarm.WidthSetGuard(
        validated_widths if validated_widths is not None else [width],
        families,
        declared_disabled=not arm.typed_enabled,
    )
    geometry = guard.check_batch(inputs, rows, label=f"arm{arm.name}")

    truth = rng.normal(size=(rows, 2)).astype(np.float32)
    target = np.exp(0.4 * np.tanh(truth[:, 0] * truth[:, 1])).astype(np.float32)
    norm = typed.fit_frozen_normalization_for_smoke(
        batch, fit_inventory_row_selection_digest=runner.digest_arrays([truth])
    )
    tf.keras.utils.set_random_seed(seed)
    model = comparison.build_comparison(norm, routing=arm.routing)
    model(runner.select_inputs(inputs, np.arange(min(2, rows))))
    optimizer = tf.keras.optimizers.Adam(1e-3)
    optimizer.build(model.trainable_weights)
    return PreparedRun(
        arm=arm,
        width=width,
        inputs=inputs,
        target=target,
        model=model,
        optimizer=optimizer,
        buckets=buckets,
        plan=plan,
        geometry=geometry,
        rows=rows,
    )


def run_steps(
    modules: dict[str, Any], prepared: PreparedRun, steps: int
) -> dict[str, Any]:
    """Take ``steps`` optimizer steps along the real batch plan."""
    tf = modules["tf"]
    runner = modules["runner"]
    losses = []
    for index in range(steps):
        _, rows = prepared.plan[index % len(prepared.plan)]
        batch = runner.select_inputs(prepared.inputs, rows)
        labels = tf.convert_to_tensor(prepared.target[rows].reshape(-1, 1))
        with tf.GradientTape() as tape:
            predicted = prepared.model(batch, training=True)
            loss = tf.reduce_mean((tf.reshape(predicted, (-1, 1)) - labels) ** 2)
        gradients = tape.gradient(loss, prepared.model.trainable_weights)
        prepared.optimizer.apply_gradients(
            zip(gradients, prepared.model.trainable_weights)
        )
        losses.append(float(loss))
    return {
        "steps": steps,
        "losses": losses,
        "final_loss": losses[-1] if losses else None,
        "weights": [np.asarray(w) for w in prepared.model.weights],
    }


def _allclose(a: Any, b: Any, criteria: Criteria) -> tuple[bool, float]:
    """Compare with the campaign's tolerances and report the max absolute error."""
    left, right = np.asarray(a, dtype=np.float64), np.asarray(b, dtype=np.float64)
    if left.shape != right.shape:
        return False, float("inf")
    if not (np.all(np.isfinite(left)) and np.all(np.isfinite(right))):
        return False, float("inf")
    error = float(np.max(np.abs(left - right), initial=0.0))
    return bool(np.allclose(left, right, atol=criteria.atol, rtol=criteria.rtol)), error


def check_input_mask_correctness(
    modules: dict[str, Any], prepared: PreparedRun
) -> dict[str, Any]:
    """V11: counts agree with slots, and masked slots cannot reach the output."""
    typed = modules["typed"]
    runner = modules["runner"]
    tf = modules["tf"]
    record: dict[str, Any] = {"check": "V11", "failures": []}
    for contract in typed.FAMILY_CONTRACTS:
        prefix = contract.name
        segment = np.asarray(prepared.inputs[f"{prefix}_segment_ids"])
        counts = np.bincount(segment, minlength=prepared.rows)[: prepared.rows]
        declared = np.asarray(prepared.inputs[f"{prefix}_counts"])
        if not np.array_equal(declared, counts.astype(declared.dtype)):
            record["failures"].append(f"{prefix}: declared counts disagree with slots")

    if record["failures"]:
        # Return before touching the model. The model carries its own
        # `assert_equal` on counts versus segment sums, so calling it here would
        # raise rather than report, and this check exists to report.
        record["passed"] = False
        record["note"] = "stopped before the forward pass: counts are inconsistent"
        return record

    # Masked-slot invariance: perturbing values the mask excludes must change nothing.
    rows = np.arange(min(64, prepared.rows))
    batch = runner.select_inputs(prepared.inputs, rows)
    before = np.asarray(prepared.model(batch, training=False))
    perturbed = {key: value for key, value in batch.items()}
    mask = np.asarray(perturbed["generic_mask"]).copy()
    values = np.asarray(perturbed["generic_values"]).copy()
    if mask.size and not mask.all():
        values[~mask] = 123456.0
        perturbed["generic_values"] = values
        after = np.asarray(prepared.model(perturbed, training=False))
        if not np.array_equal(before, after):
            record["failures"].append("generic masked slots reach the output")
        record["generic_masked_slots_tested"] = int((~mask).sum())
    else:
        record["generic_masked_slots_tested"] = 0
        record["note"] = "no inactive generic slot in this configuration"
    del tf
    record["passed"] = not record["failures"]
    return record


def check_repeatability(
    modules: dict[str, Any], build: Any, steps: int
) -> dict[str, Any]:
    """V1/V2: two independent builds from the same seed must agree bitwise."""
    first = run_steps(modules, build(), steps)
    second = run_steps(modules, build(), steps)
    mismatched = [
        index
        for index, (a, b) in enumerate(zip(first["weights"], second["weights"]))
        if not np.array_equal(a, b)
    ]
    return {
        "check": "V1",
        "steps": steps,
        "weights_compared": len(first["weights"]),
        "mismatched_weight_indices": mismatched,
        "loss_identical": first["losses"] == second["losses"],
        "passed": not mismatched and first["losses"] == second["losses"],
    }


def check_duplicate_arm_null(
    modules: dict[str, Any], build_left: Any, build_right: Any, steps: int
) -> dict[str, Any]:
    """V13a: identically configured arms under different labels must not differ.

    Distinct from repeatability: both sides go through the full arm machinery, so
    this catches arm-label-dependent state rather than nondeterminism.
    """
    left = run_steps(modules, build_left(), steps)
    right = run_steps(modules, build_right(), steps)
    mismatched = [
        index
        for index, (a, b) in enumerate(zip(left["weights"], right["weights"]))
        if not np.array_equal(a, b)
    ]
    return {
        "check": "V13a",
        "steps": steps,
        "mismatched_weight_indices": mismatched,
        "loss_difference": (
            abs(left["final_loss"] - right["final_loss"])
            if left["final_loss"] is not None
            else None
        ),
        "passed": not mismatched and left["losses"] == right["losses"],
    }


def check_permutation_invariance(
    modules: dict[str, Any], prepared: PreparedRun, criteria: Criteria
) -> dict[str, Any]:
    """V7: permuting objects within a family must not move the prediction."""
    typed = modules["typed"]
    runner = modules["runner"]
    rows = np.arange(min(64, prepared.rows))
    batch = runner.select_inputs(prepared.inputs, rows)
    before = np.asarray(prepared.model(batch, training=False))
    rng = np.random.default_rng(99)
    permuted = {key: value for key, value in batch.items()}
    moved = 0
    for contract in typed.FAMILY_CONTRACTS:
        prefix = contract.name
        segment = np.asarray(permuted[f"{prefix}_segment_ids"])
        if segment.size == 0:
            continue
        order = np.arange(segment.size)
        for row in np.unique(segment):
            here = np.flatnonzero(segment == row)
            if here.size > 1:
                order[here] = here[rng.permutation(here.size)]
                moved += here.size
        for suffix in ("values", "masks", "token_mask"):
            key = f"{prefix}_{suffix}"
            permuted[key] = np.asarray(permuted[key])[order]
    if not moved:
        return {"check": "V7", "passed": True, "objects_permuted": 0,
                "note": "no family has more than one object here"}
    after = np.asarray(prepared.model(permuted, training=False))
    ok, error = _allclose(before, after, criteria)
    return {
        "check": "V7",
        "objects_permuted": int(moved),
        "max_abs": error,
        "passed": bool(ok),
    }


def check_checkpoint_reload(
    modules: dict[str, Any], prepared: PreparedRun, workspace: Path
) -> dict[str, Any]:
    """V10: a saved and reloaded model must predict bitwise identically."""
    tf = modules["tf"]
    comparison = modules["comparison"]
    runner = modules["runner"]
    comparison.comparison_model_type()
    rows = np.arange(min(64, prepared.rows))
    batch = runner.select_inputs(prepared.inputs, rows)
    before = np.asarray(prepared.model(batch, training=False))
    path = workspace / "reload.keras"
    prepared.model.save(path)
    restored = tf.keras.models.load_model(path)
    after = np.asarray(restored(batch, training=False))
    return {
        "check": "V10",
        "passed": bool(np.array_equal(before, after)),
        "max_abs": float(np.max(np.abs(before - after), initial=0.0)),
    }


def check_finiteness(result: dict[str, Any], prepared: PreparedRun) -> dict[str, Any]:
    """V12: weights, losses and predictions must all be finite."""
    bad = [
        index
        for index, weight in enumerate(result["weights"])
        if not np.all(np.isfinite(weight))
    ]
    losses_finite = all(np.isfinite(value) for value in result["losses"])
    return {
        "check": "V12",
        "nonfinite_weight_indices": bad,
        "losses_finite": losses_finite,
        "final_loss": result["final_loss"],
        "passed": not bad and losses_finite,
    }


def _two_steps_recording(
    modules: dict[str, Any], prepared: PreparedRun, device: str
) -> dict[str, Any]:
    """Take two optimizer steps on one device, recording gradients and weights."""
    tf = modules["tf"]
    runner = modules["runner"]
    with tf.device(device):
        initial = [np.asarray(w) for w in prepared.model.trainable_weights]
        gradients: list[list[np.ndarray]] = []
        states: list[list[np.ndarray]] = []
        predictions = None
        for index in range(2):
            _, rows = prepared.plan[index % len(prepared.plan)]
            batch = runner.select_inputs(prepared.inputs, rows)
            labels = tf.convert_to_tensor(prepared.target[rows].reshape(-1, 1))
            with tf.GradientTape() as tape:
                predicted = prepared.model(batch, training=True)
                loss = tf.reduce_mean((tf.reshape(predicted, (-1, 1)) - labels) ** 2)
            if predictions is None:
                predictions = np.asarray(predicted)
            grads = tape.gradient(loss, prepared.model.trainable_weights)
            gradients.append([np.asarray(g) for g in grads])
            prepared.optimizer.apply_gradients(
                zip(grads, prepared.model.trainable_weights)
            )
            states.append([np.asarray(w) for w in prepared.model.trainable_weights])
    return {
        "initial": initial,
        "gradients": gradients,
        "states": states,
        "prediction": predictions,
    }


def check_float64_reference(
    modules: dict[str, Any], captured: dict[str, Any], criteria: Criteria
) -> dict[str, Any]:
    """V4: the float32 Adam trajectory against float64 on identical operands.

    The frozen gate applies this reference to the key-bias weight alone
    (`optimizer_equivalence.py:127`). Extended here to every weight, because with the
    cross-device comparison exemptible at tier 2 this becomes the load-bearing
    statement that the optimizer step is doing what its formula says -- and unlike a
    second float32 implementation, it cannot share a systematic error with the first.
    """
    diagnostic = modules["diagnostic"]
    reference = diagnostic.float64_adam(captured["initial"], captured["gradients"])
    worst = 0.0
    failures: list[str] = []
    per_step = []
    for step, (float32_state, float64_state) in enumerate(
        zip(captured["states"], reference), start=1
    ):
        errors = []
        for index, (a, b) in enumerate(zip(float32_state, float64_state)):
            ok, error = _allclose(a, b, criteria)
            errors.append(error)
            worst = max(worst, error)
            if not ok:
                failures.append(f"step {step} weight_{index} max_abs={error:.3e}")
        per_step.append({"step": step, "max_abs": max(errors, default=0.0)})
    return {
        "check": "V4",
        "weights_compared": len(captured["initial"]),
        "per_step": per_step,
        "max_abs": worst,
        "failures": failures[:8],
        "failure_count": len(failures),
        "passed": not failures,
    }


def check_finite_differences(
    modules: dict[str, Any], prepared: PreparedRun, criteria: Criteria, samples: int
) -> dict[str, Any]:
    """V5a and V5b: a per-width plateau, then accuracy at the measured optimum.

    The plateau check is what makes the tolerance defensible *here* rather than
    extrapolated from the widths measured on 2026-09-18: if the three step sizes
    disagree, the finite-difference estimate is uninformative at this width and the
    width is not released, instead of being waved through by a bound that no longer
    applies.
    """
    tf = modules["tf"]
    plateau_cfg = criteria.check("V5a_finite_difference_plateau")
    accuracy_cfg = criteria.check("V5b_finite_difference_accuracy")
    steps = [float(value) for value in plateau_cfg["steps"]]
    agreement = float(plateau_cfg["agreement"])
    floor = float(accuracy_cfg["gradient_floor"])
    limit = float(accuracy_cfg["max_relative_error"])
    optimum = float(accuracy_cfg["step"])

    runner = modules["runner"]
    rows = np.arange(min(256, prepared.rows))
    batch = runner.select_inputs(prepared.inputs, rows)
    labels = np.asarray(prepared.target[rows], dtype=np.float64).reshape(-1)
    tensor_labels = tf.convert_to_tensor(
        prepared.target[rows].reshape(-1, 1).astype(np.float32)
    )

    def loss_value() -> float:
        predicted = np.asarray(
            prepared.model(batch, training=False), dtype=np.float64
        ).reshape(-1)
        return float(np.mean((predicted - labels) ** 2))

    with tf.GradientTape() as tape:
        predicted = prepared.model(batch, training=False)
        loss = tf.reduce_mean((tf.reshape(predicted, (-1, 1)) - tensor_labels) ** 2)
    analytic = [
        np.asarray(g) for g in tape.gradient(loss, prepared.model.trainable_weights)
    ]

    rng = np.random.default_rng(4242)
    variables = prepared.model.trainable_weights
    coordinates = []
    attempts = 0
    while len(coordinates) < samples and attempts < samples * 40:
        attempts += 1
        index = int(rng.integers(len(variables)))
        flat = int(rng.integers(variables[index].numpy().size))
        if abs(float(analytic[index].reshape(-1)[flat])) >= floor:
            coordinates.append((index, flat))

    def estimate(index: int, flat: int, step: float) -> float:
        variable = variables[index]
        original = variable.numpy()
        scale = max(abs(float(original.reshape(-1)[flat])), 1.0)
        h = step * scale
        shifted = original.copy().reshape(-1)
        shifted[flat] += h
        variable.assign(shifted.reshape(original.shape))
        plus = loss_value()
        shifted[flat] -= 2 * h
        variable.assign(shifted.reshape(original.shape))
        minus = loss_value()
        variable.assign(original)
        return (plus - minus) / (2 * h)

    plateau_failures = 0
    relatives: list[float] = []
    for index, flat in coordinates:
        values = [estimate(index, flat, step) for step in steps]
        spread = max(values) - min(values)
        reference = max(abs(value) for value in values)
        if reference > 0 and spread / reference > agreement:
            plateau_failures += 1
        truth = float(analytic[index].reshape(-1)[flat])
        best = estimate(index, flat, optimum)
        relatives.append(abs(best - truth) / max(abs(truth), 1e-12))

    if not coordinates:
        return {
            "check": "V5",
            "passed": False,
            "reason": f"no sampled parameter had a gradient above the floor {floor}",
        }
    return {
        "check": "V5",
        "coordinates": len(coordinates),
        "gradient_floor": floor,
        "plateau_failures": plateau_failures,
        "plateau_passed": plateau_failures == 0,
        "median_relative": statistics.median(relatives),
        "max_relative": max(relatives),
        "limit": limit,
        "accuracy_passed": max(relatives) <= limit,
        "passed": plateau_failures == 0 and max(relatives) <= limit,
    }


def classify_cross_device(
    modules: dict[str, Any],
    build: Any,
    criteria: Criteria,
) -> dict[str, Any]:
    """V6 and the tier decision: run the full cross-device comparison and classify.

    Cross-device checking is not dropped. Every sub-check runs; a width is tier 1 if
    all pass, tier 2 if the only failures are in the frozen exempt list, and a hard
    stop otherwise. The measured differences are recorded either way, which is what
    turns the exempted requirements into evidence rather than an absence.
    """
    cpu = _two_steps_recording(modules, build(), "/CPU:0")
    gpu = _two_steps_recording(modules, build(), "/GPU:0")

    subchecks: dict[str, dict[str, Any]] = {}

    ok, error = _allclose(cpu["initial"], gpu["initial"], criteria)
    subchecks["initial_weight_identity"] = {
        "passed": all(
            np.array_equal(a, b) for a, b in zip(cpu["initial"], gpu["initial"])
        ),
        "max_abs": error,
        "exemptible": False,
    }

    worst = 0.0
    passed = True
    for step in range(2):
        for a, b in zip(cpu["gradients"][step], gpu["gradients"][step]):
            fine, error = _allclose(a, b, criteria)
            worst = max(worst, error)
            passed = passed and fine
    subchecks["gradient_agreement"] = {
        "passed": passed,
        "max_abs": worst,
        "exemptible": True,
    }

    fine, error = _allclose(cpu["prediction"], gpu["prediction"], criteria)
    subchecks["prediction_agreement"] = {
        "passed": fine,
        "max_abs": error,
        "exemptible": True,
    }

    worst = 0.0
    passed = True
    for step in range(2):
        for a, b in zip(cpu["states"][step], gpu["states"][step]):
            fine, error = _allclose(a, b, criteria)
            worst = max(worst, error)
            passed = passed and fine
    subchecks["updated_weight_agreement"] = {
        "passed": passed,
        "max_abs": worst,
        "exemptible": True,
    }

    exempt = set(criteria.exempt_subchecks)
    failed = {name for name, body in subchecks.items() if not body["passed"]}
    non_exempt_failures = sorted(failed - exempt)
    if not failed:
        tier = 1
    elif not non_exempt_failures:
        tier = 2
    else:
        tier = 0
    return {
        "check": "V6",
        "subchecks": subchecks,
        "failed": sorted(failed),
        "non_exempt_failures": non_exempt_failures,
        "tier": tier,
        "passed": tier in (1, 2),
    }

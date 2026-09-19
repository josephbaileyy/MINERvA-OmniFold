"""Make the ported PET2 a drop-in OmniFold estimator, on our actual input schemas.

`net.PET` is what `MultiFold` expects: a `keras.Model` whose `call` takes
``[inputs_part, inputs_evt]`` and returns one logit per event, with `train_step`
and `test_step` built on `weighted_binary_crossentropy`. This wraps `PET2Port` in
that contract so the two arms differ in the network and its recipe and in nothing
about how they are driven.

THREE ADAPTATIONS, each forced and each explicit:

* **the mask.** His `PET_body` derives it from ``x[:, :, 2] != 0`` because his
  column 2 is ``log(pT + 1e-6)``. Our reco column 2 is the detector ``z``
  coordinate and our truth column 2 is ``py``; both are legitimately zero for a
  real token, so his rule would silently delete them. Our pad authority is energy,
  column 0, exactly as `net.PET` uses it, and it is passed in explicitly.
* **the k-NN coordinates.** His are the leading ``num_coord`` columns, which for
  him are (eta, phi). Ours are ``(1, 2)`` = (pos, z) at reco and ``(5, 6, 7)`` =
  (theta, cos phi, sin phi) at truth, matching `coord_idx` in
  `fullevent_fps_dataloader` and `train_fullevent_nominal`. Taking the leading
  columns would build the neighbourhood on (E, pos) and (E, px).
* **pid and add_info are off.** His tokens carry a PID integer and five extra
  columns; ours carry neither until R-1/R-2 lands. Recorded as a capability his
  arm does not get rather than as an equivalence.

AND ONE THAT IS NOT OURS TO MAKE SILENTLY: `MultiFold.get_optimizer` hardcodes
`tf.keras.optimizers.Adam`. Dropping his backbone into the unmodified engine would
give his architecture OUR optimizer, which is not his configuration -- §7.3 of the
proposal requires his arm keep his optimizer, schedule, clipping and batch.
`make_ported_multifold` therefore overrides `get_optimizer` on a SUBCLASS, leaving
the vendored engine untouched, in the same spirit as
`annealed_estimator.make_annealed_multifold`.

His schedule and clipping now come from `training_recipe`, with `max_steps` DERIVED
from the shared example budget rather than copied from his job script. One
consequence has to be declared rather than absorbed: the vendored engine drops the
learning rate to `min_learning_rate` between iterations via `CompileModels(fixed=True)`,
and his cosine already decays within each fit. Running both would apply two
unrelated schedules to one arm. **His arm uses his schedule and ignores the engine's
`fixed` drop; ours keeps the engine's behaviour.** That is what "each arm keeps its
own recipe" means, and the fairness axis -- example presentations -- is held equal
across it. The alternative, forcing his arm onto our annealing, would be comparing
his architecture under our recipe.

NOT CITABLE FOR any performance claim.
"""

from __future__ import annotations

from typing import Any, Sequence

from keras_backend import select_keras_backend

select_keras_backend()

import numpy as np  # noqa: E402
import tensorflow as tf  # noqa: E402

import pet2_keras_port as port  # noqa: E402
import training_recipe as recipe  # noqa: E402
from torch_adamw import TORCH_DEFAULTS, TorchAdamW  # noqa: E402

keras = tf.keras

# From fullevent_fps_dataloader.build_reco_cloud / build_truth_cloud and the model
# construction at train_fullevent_nominal.py:403-407.
STEP_SCHEMAS: dict[str, dict[str, Any]] = {
    "step1_reco": {"num_feat": 5, "num_evt": 13, "coord_idx": (1, 2),
                   "columns": ("E", "pos", "z", "view", "time")},
    "step2_gen": {"num_feat": 8, "num_evt": 2, "coord_idx": (5, 6, 7),
                  "columns": ("E", "px", "py", "pz", "pdg", "theta", "cos_phi", "sin_phi")},
}
PAD_COLUMN = 0          # energy: "the pad sentinel the model keys on is energy(col 0)==0"


def weighted_binary_crossentropy(y_true: tf.Tensor, y_pred: tf.Tensor) -> tf.Tensor:
    """OmniFold's loss, transcribed from `omnifold/net.py` so the arms share it."""
    weights = tf.gather(y_true, [1], axis=1)
    labels = tf.gather(y_true, [0], axis=1)
    return tf.reduce_mean(
        weights * tf.nn.sigmoid_cross_entropy_with_logits(labels=labels, logits=y_pred)
    )


class PET2OmniFold(keras.Model):
    """`PET2Port` behind `net.PET`'s interface."""

    def __init__(
        self,
        num_feat: int,
        num_evt: int = 0,
        num_part: int = 12,
        coord_idx: Sequence[int] = (0, 1),
        size: str = "small",
        K: int = 10,
        pad_column: int = PAD_COLUMN,
        **overrides: Any,
    ) -> None:
        super().__init__()
        if num_part < K + 1:
            raise ValueError(
                f"K={K} needs at least K+1={K + 1} tokens to exclude self from the "
                f"neighbourhood; num_part={num_part}"
            )
        if max(coord_idx) >= num_feat:
            raise ValueError(f"coord_idx {tuple(coord_idx)} out of range for num_feat={num_feat}")
        self.num_feat = num_feat
        self.num_evt = num_evt
        self.num_part = num_part
        self.coord_idx = tuple(int(c) for c in coord_idx)
        self.pad_column = int(pad_column)
        settings = dict(
            input_dim=num_feat,
            conditional=num_evt > 0,
            cond_dim=max(num_evt, 1),
            pid=False,
            add_info=False,
            num_classes=1,
            K=K,
            num_coord=len(self.coord_idx),
            coord_idx=self.coord_idx,
            # mask_idx is never consulted: an explicit energy mask is always passed.
            # It is set to the pad column anyway so a future caller who drops the
            # explicit mask gets our convention rather than his.
            mask_idx=self.pad_column,
        )
        settings.update(port.preset(size))
        settings.update(overrides)
        self.backbone = port.PET2Port(**settings)
        self.loss_tracker = keras.metrics.Mean(name="loss")

    @property
    def metrics(self) -> list[Any]:
        return [self.loss_tracker]

    def pad_mask(self, part: tf.Tensor) -> tf.Tensor:
        """Energy is the only pad authority, matching `net.PET`'s `inputs_part[:,:,0]`."""
        column = part[:, :, self.pad_column : self.pad_column + 1]
        return tf.cast(column != 0, part.dtype)

    def call(self, x: Any, training: bool = True) -> tf.Tensor:
        part, evt = (x[0], x[1]) if isinstance(x, (list, tuple)) else (x, None)
        return self.backbone(
            part, cond=evt, mask=self.pad_mask(part), training=training
        )

    def train_step(self, inputs: Any) -> dict[str, Any]:
        x, y = inputs
        with tf.GradientTape() as tape:
            loss = weighted_binary_crossentropy(y, self(x, training=True))
        self.optimizer.minimize(loss, self.trainable_variables, tape=tape)
        self.loss_tracker.update_state(loss)
        return {"loss": self.loss_tracker.result()}

    def test_step(self, inputs: Any) -> dict[str, Any]:
        x, y = inputs
        loss = weighted_binary_crossentropy(y, self(x, training=False))
        self.loss_tracker.update_state(loss)
        return {"loss": self.loss_tracker.result()}


def build_step_model(step: str, num_part: int = 12, size: str = "small",
                     **overrides: Any) -> PET2OmniFold:
    """Build the ported estimator at one OmniFold step's real schema."""
    if step not in STEP_SCHEMAS:
        raise ValueError(f"Unknown step {step!r}; have {sorted(STEP_SCHEMAS)}")
    schema = STEP_SCHEMAS[step]
    return PET2OmniFold(
        num_feat=schema["num_feat"], num_evt=schema["num_evt"], num_part=num_part,
        coord_idx=schema["coord_idx"], size=size, **overrides
    )


def make_ported_multifold(multifold_class: Any,
                          optimizer_settings: dict[str, Any] | None = None,
                          schedule: dict[str, Any] | None = None,
                          batch_size: int = recipe.HIS_REFERENCE_RUN["batch_size"]):
    """Subclass `MultiFold` so his arm trains under HIS recipe, not the engine's.

    The vendored engine is not edited. `schedule` defaults to the one derived from
    the shared example budget at his batch; pass one explicitly to exercise a
    different budget. Every optimizer handed out is retained on
    `issued_optimizers` so the REALIZED policy can be read afterwards rather than
    assumed from the plan.
    """
    settings = dict(TORCH_DEFAULTS if optimizer_settings is None else optimizer_settings)
    derived = recipe.derive_schedule(batch_size) if schedule is None else dict(schedule)

    class PortedMultiFold(multifold_class):  # type: ignore[misc, valid-type]
        his_optimizer_settings = settings
        his_schedule = derived

        def __init__(self, *args: Any, **kwargs: Any) -> None:
            super().__init__(*args, **kwargs)
            self.issued_optimizers: list[Any] = []
            self.realized_policy = recipe.RealizedPolicy(self.his_schedule)

        def get_optimizer(self, num_steps: int, fixed: bool = False,
                          min_learning_rate: float = 1e-5) -> Any:
            # `fixed` is deliberately ignored: his cosine already decays inside the
            # fit, and stacking the engine's inter-iteration drop on top would be a
            # second schedule nobody chose. Declared in the module docstring.
            optimizer = recipe.build_optimizer(
                "theirs", schedule=self.his_schedule, settings=self.his_optimizer_settings)
            self.issued_optimizers.append(optimizer)
            return optimizer

        def record_realized_policy(self) -> dict[str, Any]:
            for index, optimizer in enumerate(self.issued_optimizers):
                if int(optimizer.steps_seen.numpy()):
                    self.realized_policy.record_fit(optimizer, f"fit{index}")
            return self.realized_policy.verify()

    PortedMultiFold.__name__ = f"Ported{multifold_class.__name__}"
    return PortedMultiFold


class ArrayLoader:
    """The minimum `MultiFold` reads off a loader, for exercising the two steps.

    Deliberately not a subclass of the production loader: this is a synthetic
    fixture and must not be mistakable for one. Field names and shapes are taken
    from `MultiFold`'s own accesses.
    """

    def __init__(self, reco, gen, weight, pass_reco, pass_gen, reco_evt, gen_evt):
        self.reco, self.gen, self.weight = reco, gen, weight
        self.pass_reco, self.pass_gen = pass_reco, pass_gen
        self.reco_evt, self.gen_evt = reco_evt, gen_evt
        self.nmax = len(weight)
        self.weight_reco = weight


def synthetic_loaders(rows: int, num_part: int = 12, seed: int = 0):
    """Synthetic MC and data at the real schemas, with a real pad population.

    Padding is written the way the dumper writes it -- energy-descending, all
    columns zeroed on a padded token -- so the mask the adapter derives is the mask
    production would derive, and an event with no tokens at all is included
    because that is a real production state the attention has to survive.
    """
    rng = np.random.RandomState(seed)

    def cloud(width: int, count: int) -> np.ndarray:
        block = np.abs(rng.randn(count, num_part, width)).astype(np.float32)
        block[:, :, 0] = np.sort(np.abs(rng.rand(count, num_part)), axis=1)[:, ::-1]
        live = rng.randint(0, num_part + 1, size=count)
        for row in range(count):
            block[row, live[row]:, :] = 0.0
        block[0, :, :] = 0.0                      # an event with no tokens at all
        return block

    mc = ArrayLoader(
        reco=cloud(STEP_SCHEMAS["step1_reco"]["num_feat"], rows),
        gen=cloud(STEP_SCHEMAS["step2_gen"]["num_feat"], rows),
        weight=np.ones(rows, dtype=np.float32),
        pass_reco=rng.rand(rows) < 0.8,
        pass_gen=np.ones(rows, dtype=bool),
        reco_evt=rng.randn(rows, STEP_SCHEMAS["step1_reco"]["num_evt"]).astype(np.float32),
        gen_evt=rng.randn(rows, STEP_SCHEMAS["step2_gen"]["num_evt"]).astype(np.float32),
    )
    data = ArrayLoader(
        reco=cloud(STEP_SCHEMAS["step1_reco"]["num_feat"], rows),
        gen=None,
        weight=np.ones(rows, dtype=np.float32),
        pass_reco=np.ones(rows, dtype=bool),
        pass_gen=np.ones(rows, dtype=bool),
        reco_evt=rng.randn(rows, STEP_SCHEMAS["step1_reco"]["num_evt"]).astype(np.float32),
        gen_evt=None,
    )
    return mc, data

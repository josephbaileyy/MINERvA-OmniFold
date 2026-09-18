"""AdamW written to torch's formula, because Keras' is a different optimizer.

P-4 exists because "an optimizer or initializer difference reproduces forward
outputs and diverges after one step", and that is exactly what it found: with his
weights transferred and his loss, `tf.keras.optimizers.AdamW` and
`torch.optim.AdamW` disagreed by 68 % of the first update on the bias tensors.

The cause is where epsilon sits relative to the second-moment bias correction:

* torch  -- ``denom = sqrt(v) / sqrt(bc2) + eps``, then ``p -= (lr / bc1) * m / denom``
* Keras  -- ``p -= lr * sqrt(bc2) / bc1 * m / (sqrt(v) + eps)``

Multiply the Keras form out and its effective epsilon is ``eps / sqrt(bc2)``. At the
first step ``sqrt(bc2) = sqrt(1 - 0.999) = 0.0316``, so Keras behaves as though
epsilon were 31.6x larger. Wherever the gradient is comparable to epsilon -- which
is every bias in a freshly initialised network, since `PET2.initialize_weights`
sets them all to zero -- the two optimizers take materially different first steps.
The gap shrinks as ``bc2 -> 1`` but the trajectories have already diverged.

Reproducing his RECIPE therefore means reproducing his update rule, not accepting a
framework's nearest equivalent. Decoupled decay is applied before the moment update
and to every parameter: `PET2.no_weight_decay()` returns {"norm", "token"} and
`src/scripts/train.py:2345` never consults it, building one param group, so his
norms and class tokens ARE decayed.

NOT a general-purpose optimizer. It exists so the ported arm trains like his.
"""

from __future__ import annotations

from typing import Any

from keras_backend import select_keras_backend

select_keras_backend()

import tensorflow as tf  # noqa: E402

TORCH_DEFAULTS = {"learning_rate": 1e-4, "weight_decay": 0.01, "beta_1": 0.9,
                  "beta_2": 0.999, "epsilon": 1e-8}


class TorchAdamW(tf.keras.optimizers.Optimizer):
    """``torch.optim.AdamW`` (single param group, ``amsgrad=False``) in Keras."""

    def __init__(
        self,
        learning_rate: float = 1e-4,
        weight_decay: float = 0.01,
        beta_1: float = 0.9,
        beta_2: float = 0.999,
        epsilon: float = 1e-8,
        name: str = "TorchAdamW",
        **kwargs: Any,
    ) -> None:
        # The base class implements its own decoupled decay; it is disabled here so
        # there is exactly one decay in the update and it is torch's.
        super().__init__(name=name, weight_decay=None, **kwargs)
        self._learning_rate = self._build_learning_rate(learning_rate)
        # Keras stores the learning rate in a float32 variable whatever the model
        # dtype is, which puts a ~1e-8 RELATIVE floor under every update and was
        # measured dominating P-4 in float64. A constant rate is therefore kept as a
        # Python double and cast per variable; a schedule still goes through Keras,
        # because a schedule is a tensor computation and cannot be a Python float.
        self._constant_learning_rate = (
            float(learning_rate) if isinstance(learning_rate, (int, float)) else None
        )
        self.torch_weight_decay = weight_decay
        self.beta_1 = beta_1
        self.beta_2 = beta_2
        self.epsilon = epsilon

    def build(self, var_list: Any) -> None:
        super().build(var_list)
        if getattr(self, "_built", False):
            return
        self._momentums = []
        self._velocities = []
        for variable in var_list:
            self._momentums.append(
                self.add_variable_from_reference(model_variable=variable, variable_name="m")
            )
            self._velocities.append(
                self.add_variable_from_reference(model_variable=variable, variable_name="v")
            )
        self._built = True

    def update_step(self, gradient: Any, variable: Any) -> None:
        dtype = variable.dtype
        lr = (
            tf.constant(self._constant_learning_rate, dtype)
            if self._constant_learning_rate is not None
            else tf.cast(self.learning_rate, dtype)
        )
        beta_1 = tf.cast(self.beta_1, dtype)
        beta_2 = tf.cast(self.beta_2, dtype)
        epsilon = tf.cast(self.epsilon, dtype)
        decay = tf.cast(self.torch_weight_decay, dtype)
        step = tf.cast(self.iterations + 1, dtype)
        correction_1 = 1.0 - tf.pow(beta_1, step)
        correction_2 = 1.0 - tf.pow(beta_2, step)

        index = self._index_dict[self._var_key(variable)]
        m = self._momentums[index]
        v = self._velocities[index]

        if isinstance(gradient, tf.IndexedSlices):
            raise NotImplementedError(
                "TorchAdamW has no sparse path; PET2 has no embedding-bag-style "
                "sparse gradients, and a silently wrong sparse rule is worse than "
                "a refusal."
            )
        # torch decays the parameter BEFORE the moment update: p.mul_(1 - lr*wd).
        variable.assign(variable * (1.0 - lr * decay))
        m.assign_add((gradient - m) * (1.0 - beta_1))
        v.assign_add((tf.square(gradient) - v) * (1.0 - beta_2))
        denominator = tf.sqrt(v) / tf.sqrt(correction_2) + epsilon
        variable.assign_sub((lr / correction_1) * m / denominator)

    def get_config(self) -> dict[str, Any]:
        config = super().get_config()
        config.update({
            "learning_rate": self._serialize_hyperparameter(self._learning_rate),
            "weight_decay": self.torch_weight_decay,
            "beta_1": self.beta_1,
            "beta_2": self.beta_2,
            "epsilon": self.epsilon,
        })
        return config

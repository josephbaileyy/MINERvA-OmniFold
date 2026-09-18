"""Gregor's paper backbone (OmniLearned PET2) rebuilt in our Keras engine.

WHY A PORT AT ALL. Comparing our configuration against his means running his
architecture on our unfolding task. His code is PyTorch and trains a regression
head against a log1p Huber loss; OmniFold needs a weighted-BCE reweighting
classifier inside `MultiFold`'s two-step loop. Rather than reimplement OmniFold in
PyTorch -- which would put the *estimator* on trial rather than the backbone -- his
backbone is rebuilt here against the same engine our arm uses, so the only thing
that differs between arms is the network and its recipe.

WHICH CONFIGURATION THIS IS. `plot_configs/V1Paper.json` names OmniLearned-small,
OmniLearned-small-rw and OmniLearned-medium as the V1 lineup, and the three
matching branches of `src/jobs/submit_train_jobs.py:155-169` (`OLS`, `OLS_RW`,
`OLM_FB`) pass NEITHER `--ol-interaction` NOR `--ol-local-interaction`. Those flags
are `store_true, default=False`, so the paper configuration runs with
``use_int=False`` and ``local_int=False`` -- NOT the `PET2` class defaults of
``True``/``True``. A fourth branch `OLS_int` turns them on and is not in the paper
lineup. This port therefore implements the interaction-free model and REFUSES to
pretend otherwise; see `require_supported_configuration`.

WHAT IS FAITHFUL AND WHAT IS ADAPTED. Everything in `PET2`'s forward path for
``mode="classifier"`` is reproduced arithmetically, including the details that look
like accidents (the mask read off feature column 2, the second mask recomputed on
128-dimensional embeddings, the `-1e9` additive attention mask that keeps
fully-padded rows finite). Three things CANNOT be carried over literally because
they are statements about his data, and each is a named, explicit argument here
rather than a silent default:

* ``mask_idx`` -- his mask is ``x[:, :, 2:3] != 0``, and his column 2 is
  ``log(pT + 1e-6)``. Our reco column 2 is the detector ``z`` coordinate and our
  truth column 2 is ``py``; both are legitimately zero for real tokens, so his
  convention would silently delete them. Production callers pass an explicit mask.
* ``coord_idx`` -- his k-NN coordinates are ``x[:, :, :num_coord]``, the leading
  columns, because his leading columns are (eta, phi). Ours are ``(1, 2)`` at reco
  and ``(5, 6, 7)`` at truth. Taking the leading columns would build the
  neighbourhood graph on (E, pos) and (E, px).
* the interaction features -- `get_mass`/`get_dr`/`get_kt` are defined in LHC jet
  coordinates and have no established mapping onto our token schema. The paper
  configuration does not use them, so the port refuses them rather than inventing
  a mapping, which would be a scientific choice dressed as an implementation detail.

Weights are stored in TORCH layout -- `Linear.weight` is ``(out, in)`` -- so
transferring a checkpoint is a copy with no transpose to get backwards, and the
parameter inventory can be compared to `named_parameters()` by name.

NOT CITABLE FOR any performance claim. This file is an implementation.
"""

from __future__ import annotations

import math
from typing import Any, Iterable, Sequence

from keras_backend import select_keras_backend

select_keras_backend()

import tensorflow as tf  # noqa: E402  (must follow the backend choice)

keras = tf.keras
layers = tf.keras.layers

# The three V1-paper branches of submit_train_jobs.py pass neither interaction flag.
PAPER_INTERACTION_FLAGS = {"use_int": False, "local_int": False}

# get_model_parameters() in src/models/omnilearned/utils.py, transcribed.
MODEL_PRESETS: dict[str, dict[str, int]] = {
    "small": {
        "num_transformers": 8,
        "num_transformers_head": 2,
        "num_tokens": 4,
        "num_heads": 8,
        "base_dim": 128,
        "mlp_ratio": 2,
    },
    "medium": {
        "num_transformers": 12,
        "num_transformers_head": 2,
        "num_tokens": 4,
        "num_heads": 16,
        "base_dim": 512,
        "mlp_ratio": 2,
    },
    "large": {
        "num_transformers": 28,
        "num_transformers_head": 4,
        "num_tokens": 4,
        "num_heads": 32,
        "base_dim": 1024,
        "mlp_ratio": 2,
    },
}

# His masking sentinel and his additive-mask constant, kept as named constants so a
# reader can see they are transcribed rather than chosen.
HIS_MASK_COLUMN = 2
NEG_INF_SURROGATE = -1e9


def require_supported_configuration(use_int: bool, local_int: bool) -> None:
    """Refuse the interaction blocks instead of guessing what they mean on our data.

    `get_mass`, `get_dr` and `get_kt` read columns 0, 1 and 2 as (eta, phi, log pT)
    and combine them with ``cosh(d_eta) - cos(d_phi)``. Our tokens are
    (E, pos, z, view, time) at reco and (E, px, py, pz, pdg, theta, cos_phi, sin_phi)
    at truth. There is no mapping that makes those formulae mean what they mean for
    him, and picking one would be a physics decision made inside a porting utility.
    The paper configuration does not need them, so this fails loudly.
    """
    if use_int or local_int:
        raise NotImplementedError(
            "use_int/local_int are not ported. The V1-paper lineup (OLS, OLS_RW, "
            "OLM_FB) runs with both False; only the non-paper OLS_int branch enables "
            "them. Their features are defined in LHC jet coordinates (eta, phi, "
            "log pT) and have no established mapping onto our token schema, so "
            "porting them would embed an unratified scientific choice."
        )


class _Port(keras.layers.Layer):
    """Base class that mirrors a torch module tree, names included.

    Children and weights are registered in declaration order under the same names
    `named_parameters()` uses, so `parameter_inventory` produces dotted names that
    can be set-compared against the upstream model. Comparing inventories by NAME
    rather than by count is deliberate: two models can agree on 176 tensors and
    disagree about which ones.
    """

    def __init__(self, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self._port_children: dict[str, "_Port"] = {}
        self._port_weights: dict[str, tf.Variable] = {}

    def _child(self, name: str, layer: "_Port") -> "_Port":
        self._port_children[name] = layer
        return layer

    def _children(self, name: str, built: Sequence["_Port"]) -> list["_Port"]:
        """Register an nn.ModuleList: torch names its entries by position."""
        for index, layer in enumerate(built):
            self._port_children[f"{name}.{index}"] = layer
        return list(built)

    def _param(
        self, name: str, shape: tuple[int, ...], initializer: Any = "zeros"
    ) -> tf.Variable:
        variable = self.add_weight(
            name=name, shape=shape, dtype=self.dtype, initializer=initializer,
            trainable=True,
        )
        self._port_weights[name] = variable
        return variable


def parameter_inventory(layer: _Port, prefix: str = "") -> list[tuple[str, tf.Variable]]:
    """Dotted (name, variable) pairs in torch's own traversal order.

    `torch.nn.Module.named_parameters` yields a module's own parameters before
    recursing into children, in registration order; this mirrors that so the two
    inventories line up entry by entry as well as as sets.
    """
    found: list[tuple[str, tf.Variable]] = []
    for name, variable in layer._port_weights.items():
        found.append((prefix + name, variable))
    for name, child in layer._port_children.items():
        found.extend(parameter_inventory(child, f"{prefix}{name}."))
    return found


class Linear(_Port):
    """``nn.Linear`` with the weight kept in torch's ``(out, in)`` layout."""

    def __init__(self, in_features: int, out_features: int, bias: bool = True, **kw: Any):
        super().__init__(**kw)
        self.in_features = in_features
        self.out_features = out_features
        self.use_bias = bias
        limit = 1.0 / math.sqrt(in_features)
        init = keras.initializers.RandomUniform(-limit, limit)
        self.weight = self._param("weight", (out_features, in_features), init)
        self.bias = self._param("bias", (out_features,), "zeros") if bias else None

    def call(self, x: tf.Tensor) -> tf.Tensor:
        y = tf.einsum("...i,oi->...o", x, self.weight)
        return y + self.bias if self.use_bias else y


class DynamicTanh(_Port):
    """``tanh(alpha * x) * weight``; the upstream's norm layer, channels-last."""

    def __init__(self, normalized_shape: int, alpha_init_value: float = 0.5, **kw: Any):
        super().__init__(**kw)
        self.normalized_shape = normalized_shape
        self.alpha = self._param(
            "alpha", (1,), keras.initializers.Constant(alpha_init_value)
        )
        self.weight = self._param("weight", (normalized_shape,), "ones")

    def call(self, x: tf.Tensor) -> tf.Tensor:
        return tf.tanh(self.alpha * x) * self.weight


def _gelu(x: tf.Tensor) -> tf.Tensor:
    """Exact erf GELU, written out because the library's "exact" one is not.

    ``nn.GELU()`` defaults to ``approximate='none'``, i.e. ``0.5 x (1 + erf(x/sqrt 2))``.
    Two traps, both measured on 2026-09-19 rather than assumed:

    * the tanh approximation differs by ~4e-4 absolute -- 40x the 1e-5 forward
      tolerance P-2 asserts, so it would fail the port check on the activation
      alone;
    * ``tf.nn.gelu(x, approximate=False)`` ALSO differs from torch, by 4.1e-9 in
      float64, while this written-out form agrees to 1.1e-16. 4e-9 is invisible in
      float32 and harmless in a forward pass, but the local-neighbourhood block
      divides by ``sum(1e-9 + mask)``, so on tokens whose neighbours are all padded
      that residue is divided by ~1e-8 and lands at 1e-1 in the body output. The
      cheap "exact" flag would have made P-2 fail for a reason that has nothing to
      do with the port.
    """
    # `math.sqrt(2.0)` is a Python double; `tf.sqrt(2.0)` would evaluate in float32
    # and then be cast up, which reintroduces a 1.7e-8 relative error.
    return 0.5 * x * (1.0 + tf.math.erf(x / math.sqrt(2.0)))


class MLP(_Port):
    """Upstream ``layers.MLP``: fc1, GELU, norm(hidden), drop, fc2, drop, mask."""

    def __init__(
        self,
        in_features: int,
        hidden_features: int | None = None,
        out_features: int | None = None,
        drop: float = 0.0,
        norm_layer: bool = False,
        bias: bool = True,
        **kw: Any,
    ):
        super().__init__(**kw)
        out_features = out_features or in_features
        hidden_features = hidden_features or in_features
        self.fc1 = self._child("fc1", Linear(in_features, hidden_features, bias, dtype=self.dtype))
        self.fc2 = self._child("fc2", Linear(hidden_features, out_features, bias, dtype=self.dtype))
        self.norm = (
            self._child("norm", DynamicTanh(hidden_features, dtype=self.dtype))
            if norm_layer
            else None
        )
        self.drop_rate = drop
        self._drop = layers.Dropout(drop, dtype=self.dtype) if drop > 0.0 else None

    def call(self, x: tf.Tensor, mask: tf.Tensor | None = None, training: bool | None = None):
        x = self.fc1(x)
        x = _gelu(x)
        if self.norm is not None:
            x = self.norm(x)
        if self._drop is not None:
            x = self._drop(x, training=training)
        x = self.fc2(x)
        if self._drop is not None:
            x = self._drop(x, training=training)
        if mask is not None:
            x = x * mask
        return x


class MultiheadAttention(_Port):
    """``nn.MultiheadAttention(batch_first=True, bias=False)``, written out.

    Keras' own MultiHeadAttention is not used, for two reasons that both matter
    here: it stores per-head kernels rather than the single packed
    ``in_proj_weight`` a checkpoint carries, and it takes a BOOLEAN mask, whereas
    the upstream adds a float bias (``-1e9``) to the scores. Writing the arithmetic
    out keeps checkpoint transfer a copy and keeps the additive mask exact.
    """

    def __init__(self, dim: int, num_heads: int, bias: bool = False, dropout: float = 0.0, **kw: Any):
        super().__init__(**kw)
        if dim % num_heads:
            raise ValueError(f"embed_dim {dim} is not divisible by num_heads {num_heads}")
        self.dim = dim
        self.num_heads = num_heads
        self.head_dim = dim // num_heads
        limit = 1.0 / math.sqrt(dim)
        init = keras.initializers.RandomUniform(-limit, limit)
        self.in_proj_weight = self._param("in_proj_weight", (3 * dim, dim), init)
        self.in_proj_bias = self._param("in_proj_bias", (3 * dim,), "zeros") if bias else None
        self.out_proj = self._child("out_proj", Linear(dim, dim, bias, dtype=self.dtype))
        self._drop = layers.Dropout(dropout, dtype=self.dtype) if dropout > 0.0 else None

    def _split_heads(self, x: tf.Tensor) -> tf.Tensor:
        shape = tf.shape(x)
        x = tf.reshape(x, [shape[0], shape[1], self.num_heads, self.head_dim])
        return tf.transpose(x, [0, 2, 1, 3])

    def call(
        self,
        query: tf.Tensor,
        key: tf.Tensor,
        value: tf.Tensor,
        attn_mask: tf.Tensor | None = None,
        key_padding_mask: tf.Tensor | None = None,
        training: bool | None = None,
    ) -> tf.Tensor:
        dim = self.dim
        w_q = self.in_proj_weight[:dim]
        w_k = self.in_proj_weight[dim : 2 * dim]
        w_v = self.in_proj_weight[2 * dim :]
        q = tf.einsum("...i,oi->...o", query, w_q)
        k = tf.einsum("...i,oi->...o", key, w_k)
        v = tf.einsum("...i,oi->...o", value, w_v)
        if self.in_proj_bias is not None:
            q = q + self.in_proj_bias[:dim]
            k = k + self.in_proj_bias[dim : 2 * dim]
            v = v + self.in_proj_bias[2 * dim :]

        q, k, v = self._split_heads(q), self._split_heads(k), self._split_heads(v)
        scores = tf.matmul(q, k, transpose_b=True) / tf.cast(
            math.sqrt(self.head_dim), q.dtype
        )
        if attn_mask is not None:
            # Accepted as (B, L, S) and broadcast over heads. Upstream builds
            # (B, L, S) and then `repeat_interleave(num_heads, dim=0)`, which torch
            # reshapes to (B, H, L, S) -- every head receives the same slice, so the
            # broadcast is the same arithmetic without H copies in memory. This
            # equality holds only because the mask is head-independent, which is
            # true exactly when use_int is False; use_int is refused above.
            scores = scores + tf.cast(attn_mask, scores.dtype)[:, None, :, :]
        fully_blocked = None
        if key_padding_mask is not None:
            # True means "ignore". Upstream lets torch merge this as -inf.
            blocked = tf.cast(key_padding_mask, scores.dtype) * tf.constant(
                float("-inf"), scores.dtype
            )
            blocked = tf.where(tf.math.is_nan(blocked), tf.zeros_like(blocked), blocked)
            scores = scores + blocked[:, None, None, :]
            # A query whose every key is masked softmaxes over nothing. Plain softmax
            # gives NaN there; torch's SDPA returns exactly zero, measured. That case
            # is not hypothetical on our data -- `fullevent_fps_dataloader` zeroes the
            # event block of every row failing `pass_reco`, and `PET2.initialize_weights`
            # zeroes every bias, so at the first training step `cond_embed(0) == 0`
            # exactly, the conditioning token masks itself off, and an event with no
            # recoil tokens has no unmasked key left. Reproducing torch's zero is what
            # keeps the first step of the ported arm finite.
            fully_blocked = tf.reduce_all(tf.cast(key_padding_mask, tf.bool), axis=-1)
        weights = tf.nn.softmax(scores, axis=-1)
        if fully_blocked is not None:
            weights = tf.where(
                fully_blocked[:, None, None, None], tf.zeros_like(weights), weights
            )
        if self._drop is not None:
            weights = self._drop(weights, training=training)
        out = tf.matmul(weights, v)
        out = tf.transpose(out, [0, 2, 1, 3])
        shape = tf.shape(out)
        out = tf.reshape(out, [shape[0], shape[1], self.dim])
        return self.out_proj(out)


class AttBlock(_Port):
    """Upstream ``layers.AttBlock`` with ``use_int=False`` and ``skip=False``."""

    def __init__(
        self,
        dim: int,
        num_heads: int,
        mlp_ratio: float = 4.0,
        attn_drop: float = 0.0,
        mlp_drop: float = 0.0,
        **kw: Any,
    ):
        super().__init__(**kw)
        self.norm1 = self._child("norm1", DynamicTanh(dim, dtype=self.dtype))
        self.norm2 = self._child("norm2", DynamicTanh(dim, dtype=self.dtype))
        self.attn = self._child(
            "attn", MultiheadAttention(dim, num_heads, bias=False, dropout=attn_drop, dtype=self.dtype)
        )
        self.mlp = self._child(
            "mlp",
            MLP(dim, int(dim * mlp_ratio), drop=mlp_drop, norm_layer=True, dtype=self.dtype),
        )

    def call(
        self,
        x: tf.Tensor,
        mask: tf.Tensor,
        attn_mask: tf.Tensor | None = None,
        training: bool | None = None,
    ) -> tf.Tensor:
        x_norm = self.norm1(x * mask)
        key_padding = None
        if attn_mask is None:
            key_padding = tf.logical_not(tf.cast(mask[:, :, 0], tf.bool))
        attended = self.attn(
            x_norm, x_norm, x_norm, attn_mask=attn_mask,
            key_padding_mask=key_padding, training=training,
        )
        x = x + attended * mask
        return x + self.mlp(self.norm2(x), mask, training=training)


class TokenAttBlock(_Port):
    """Upstream ``layers.TokenAttBlock``: tokens attend to the cloud, not vice versa."""

    def __init__(
        self,
        dim: int,
        num_heads: int,
        mlp_ratio: float = 4.0,
        attn_drop: float = 0.0,
        mlp_drop: float = 0.0,
        num_tokens: int = 1,
        **kw: Any,
    ):
        super().__init__(**kw)
        self.num_tokens = num_tokens
        self.norm = self._child("norm", DynamicTanh(dim, dtype=self.dtype))
        self.attn = self._child(
            "attn", MultiheadAttention(dim, num_heads, bias=False, dropout=attn_drop, dtype=self.dtype)
        )
        self.mlp = self._child(
            "mlp",
            MLP(dim, int(dim * mlp_ratio), drop=mlp_drop, norm_layer=True, dtype=self.dtype),
        )

    def call(self, x: tf.Tensor, mask: tf.Tensor, training: bool | None = None) -> tf.Tensor:
        tokens = x[:, : self.num_tokens]
        rest = x[:, self.num_tokens :]
        key_padding = tf.logical_not(tf.cast(mask[:, :, 0], tf.bool))
        tokens = tokens + self.attn(
            tokens, rest, rest, key_padding_mask=key_padding, training=training
        )
        tokens = tokens + self.mlp(self.norm(tokens), training=training)
        return tf.concat([tokens, rest], axis=1)


class InputBlock(_Port):
    """Upstream ``layers.InputBlock``: returns the embedding AND the raw input."""

    def __init__(self, in_features: int, hidden_features: int, out_features: int, **kw: Any):
        super().__init__(**kw)
        self.mlp = self._child(
            "mlp",
            MLP(in_features, hidden_features, out_features, norm_layer=True, dtype=self.dtype),
        )
        self.norm = self._child("norm", DynamicTanh(in_features, dtype=self.dtype))

    def call(self, x: tf.Tensor, mask: tf.Tensor, training: bool | None = None):
        return self.mlp(self.norm(x), mask, training=training), x


def mask_outer(m: tf.Tensor) -> tf.Tensor:
    """Pairwise mask product ``(B, N, N)`` from ``(B, N, 1)``, as upstream."""
    mf = tf.cast(m, m.dtype if m.dtype.is_floating else tf.float32)
    return mf * tf.transpose(mf, [0, 2, 1])


def additive_pair_mask(m: tf.Tensor) -> tf.Tensor:
    """``~outer(m)`` scaled to ``-1e9``: upstream's finite stand-in for ``-inf``.

    The surrogate is not cosmetic. With ``-inf`` a row whose keys are all padded
    softmaxes to NaN; with ``-1e9`` it softmaxes to a uniform average of masked
    values that the caller then multiplies by zero. Reproducing the constant is
    what keeps fully-padded events finite in both engines.
    """
    return (tf.ones_like(mask_outer(m)) - mask_outer(m)) * NEG_INF_SURROGATE


class LocalEmbeddingBlock(_Port):
    """Upstream ``layers.LocalEmbeddingBlock`` with ``local_int=False``."""

    def __init__(
        self,
        in_features: int,
        hidden_features: int,
        out_features: int,
        mlp_drop: float = 0.0,
        attn_drop: float = 0.0,
        K: int = 10,
        num_heads: int = 4,
        num_transformers: int = 2,
        emulate_upstream_float32_reduction: bool = True,
        **kw: Any,
    ):
        super().__init__(**kw)
        self.K = K
        self.num_heads = num_heads
        self.emulate_upstream_float32_reduction = emulate_upstream_float32_reduction
        self.mlp = self._child(
            "mlp",
            MLP(in_features, hidden_features, out_features, drop=mlp_drop, norm_layer=True, dtype=self.dtype),
        )
        self.in_blocks = self._children(
            "in_blocks",
            [
                AttBlock(out_features, num_heads, 2, attn_drop, mlp_drop, dtype=self.dtype)
                for _ in range(num_transformers)
            ],
        )

    def call(self, points: tf.Tensor, features: tf.Tensor, mask: tf.Tensor, training=None):
        static = features.shape
        batch, num_points, num_dims = static[0], static[1], static[2]
        diff = points[:, :, None, :] - points[:, None, :, :]
        distances = tf.reduce_sum(diff * diff, axis=-1)
        # topk over -distance puts the point itself first (distance 0) and the
        # upstream drops that column. Exact coordinate ties make which index lands
        # in column 0 implementation-defined; `verify_knn_tie_freedom` measures
        # whether a given batch has any, rather than assuming none.
        _, indices = tf.math.top_k(-distances, k=self.K + 1)
        indices = indices[:, :, 1:]
        neighbors = tf.gather(features, indices, batch_dims=1)
        mask_neighbors = tf.gather(mask, indices, batch_dims=1)
        centre = tf.tile(features[:, :, None, :], [1, 1, self.K, 1])
        local_features = centre - neighbors

        flat = [-1, self.K, 1]
        mask_flat = tf.reshape(mask_neighbors, flat)
        local_flat = tf.reshape(local_features, [-1, self.K, num_dims])
        attn_mask = additive_pair_mask(mask_flat)

        x = self.mlp(local_flat, training=training) * mask_flat
        for block in self.in_blocks:
            x = block(x, mask=mask_flat, attn_mask=attn_mask, training=training)

        out_dim = x.shape[-1]
        x = tf.reshape(x, [-1, num_points, self.K, out_dim])
        mask_grid = tf.reshape(mask_flat, [-1, num_points, self.K, 1])
        x = tf.reduce_sum(x, axis=2) / self._neighbour_count(mask_grid, x.dtype) * mask
        return x, indices

    def _neighbour_count(self, mask_grid: tf.Tensor, dtype: Any) -> tf.Tensor:
        """``sum(1e-9 + mask)``, reproducing upstream's float32 pin when asked.

        Upstream writes ``torch.sum(1e-9 + mask_neighbors, dim=2)`` where
        ``mask_neighbors`` is a BOOL tensor, so torch promotes against the default
        dtype and the whole denominator is computed in float32 no matter what the
        model's dtype is. In float32 -- every run he has ever done -- that is
        indistinguishable from doing it in the model dtype. In float64 it is not:
        ``1e-9 + 1`` rounds to exactly ``1`` in float32 and does not in float64, and
        that ~1e-8 relative difference in a DENOMINATOR was measured propagating to
        a 2.6e-8 relative disagreement in the gradients.

        Reproducing his network means reproducing this, not improving on it. The
        flag exists so the choice is visible and so the cost of the pin can be
        measured by turning it off.
        """
        if not self.emulate_upstream_float32_reduction:
            return tf.reduce_sum(1e-9 + mask_grid, axis=2)
        counted = tf.reduce_sum(1e-9 + tf.cast(mask_grid, tf.float32), axis=2)
        return tf.cast(counted, dtype)


class PETBody(_Port):
    """Upstream ``network.PET_body`` for ``use_int=False``, ``skip=False``."""

    def __init__(
        self,
        input_dim: int,
        base_dim: int,
        num_transformers: int = 2,
        num_transf_local: int = 2,
        num_heads: int = 4,
        mlp_ratio: int = 2,
        mlp_drop: float = 0.0,
        attn_drop: float = 0.0,
        num_tokens: int = 4,
        K: int = 10,
        conditional: bool = False,
        cond_dim: int = 3,
        pid: bool = False,
        pid_dim: int = 9,
        add_info: bool = False,
        add_dim: int = 4,
        num_coord: int = 3,
        coord_idx: Sequence[int] | None = None,
        mask_idx: int = HIS_MASK_COLUMN,
        **kw: Any,
    ):
        super().__init__(**kw)
        self.input_dim = input_dim
        self.conditional = conditional
        self.pid = pid
        self.add_info = add_info
        self.num_tokens = num_tokens
        self.num_heads = num_heads
        self.mask_idx = mask_idx
        self.coord_idx = tuple(range(num_coord)) if coord_idx is None else tuple(coord_idx)
        if max(self.coord_idx) >= input_dim:
            raise ValueError(f"coord_idx {self.coord_idx} out of range for input_dim={input_dim}")
        if not 0 <= mask_idx < input_dim:
            raise ValueError(f"mask_idx {mask_idx} out of range for input_dim={input_dim}")

        self.embed = self._child(
            "embed", InputBlock(input_dim, int(mlp_ratio * base_dim), base_dim, dtype=self.dtype)
        )
        self.local_physics = self._child(
            "local_physics",
            LocalEmbeddingBlock(
                input_dim, mlp_ratio * base_dim, base_dim, mlp_drop, attn_drop,
                K, num_heads, num_transf_local, dtype=self.dtype,
            ),
        )
        self.num_add = 0
        self.cond_embed = None
        if conditional:
            # nn.Sequential(MLP(...)) upstream, so the parameter path is `cond_embed.0.`
            self.cond_embed = MLP(cond_dim, base_dim, base_dim, norm_layer=True, dtype=self.dtype)
            self._child("cond_embed.0", self.cond_embed)
            self.num_add += 1
        self.add_embed = None
        if add_info:
            self.add_embed = MLP(
                add_dim, int(mlp_ratio * base_dim), base_dim, norm_layer=True, bias=False,
                dtype=self.dtype,
            )
            self._child("add_embed.0", self.add_embed)
        self.pid_embed = None
        if pid:
            self.pid_dim = pid_dim
            self.pid_embed = _Embedding(pid_dim, base_dim, padding_idx=0, dtype=self.dtype)
            self._child("pid_embed.0", self.pid_embed)

        self.token = self._param(
            "token", (1, num_tokens, base_dim),
            keras.initializers.TruncatedNormal(mean=0.0, stddev=0.02),
        )
        self.in_blocks = self._children(
            "in_blocks",
            [
                AttBlock(base_dim, num_heads, mlp_ratio, attn_drop, mlp_drop, dtype=self.dtype)
                for _ in range(num_transformers)
            ],
        )
        self.norm = self._child("norm", DynamicTanh(base_dim, dtype=self.dtype))

    def derive_mask(self, x: tf.Tensor) -> tf.Tensor:
        """His convention, exposed so a caller can see what it would have done."""
        return tf.cast(x[:, :, self.mask_idx : self.mask_idx + 1] != 0, x.dtype)

    def call(
        self,
        x: tf.Tensor,
        cond: tf.Tensor | None = None,
        pid: tf.Tensor | None = None,
        add_info: tf.Tensor | None = None,
        mask: tf.Tensor | None = None,
        training: bool | None = None,
    ) -> tf.Tensor:
        mask = self.derive_mask(x) if mask is None else tf.cast(mask, x.dtype)
        batch = tf.shape(x)[0]
        token = tf.tile(self.token, [batch, 1, 1])

        x_embed, raw = self.embed(x, mask, training=training)
        coord_shift = 999.0 * (tf.ones_like(mask) - mask)
        points = coord_shift + tf.gather(raw, list(self.coord_idx), axis=2)
        local_features, _ = self.local_physics(points, raw, mask, training=training)

        x = x_embed + local_features
        if pid is not None and self.pid_embed is not None:
            x = x + self.pid_embed(pid) * mask
        if add_info is not None and self.add_embed is not None:
            x = x + self.add_embed(add_info, training=training) * mask
        if cond is not None and self.cond_embed is not None:
            x = tf.concat([self.cond_embed(cond, training=training)[:, None, :], x], axis=1)
        x = tf.concat([token, x], axis=1)

        # Recomputed on the 128-dimensional embedding, exactly as upstream: column 2
        # of the EMBEDDING, not of the input. Padded rows are identically zero by
        # construction, so this is a valid mask; it is preserved rather than
        # replaced because replacing it would change his architecture.
        mask = tf.cast(x[:, :, HIS_MASK_COLUMN : HIS_MASK_COLUMN + 1] != 0, x.dtype)
        attn_mask = additive_pair_mask(mask)
        for block in self.in_blocks:
            x = block(x, mask=mask, attn_mask=attn_mask, training=training)
        return self.norm(x) * mask


class _Embedding(_Port):
    """``nn.Embedding(num, dim, padding_idx=0)``; row 0 stays zero and untrained."""

    def __init__(self, num_embeddings: int, dim: int, padding_idx: int | None = None, **kw: Any):
        super().__init__(**kw)
        self.padding_idx = padding_idx
        self.weight = self._param(
            "weight", (num_embeddings, dim), keras.initializers.RandomNormal(0.0, 1.0)
        )

    def call(self, ids: tf.Tensor) -> tf.Tensor:
        table = self.weight
        if self.padding_idx is not None:
            keep = tf.cast(
                tf.range(tf.shape(table)[0]) != self.padding_idx, table.dtype
            )[:, None]
            table = table * keep
        return tf.gather(table, tf.cast(ids, tf.int32))


class PETClassifier(_Port):
    """Upstream ``network.PET_classifier``."""

    def __init__(
        self,
        base_dim: int,
        num_transformers: int = 2,
        num_heads: int = 4,
        mlp_ratio: int = 2,
        mlp_drop: float = 0.0,
        attn_drop: float = 0.0,
        num_tokens: int = 4,
        num_classes: int = 2,
        **kw: Any,
    ):
        super().__init__(**kw)
        self.num_tokens = num_tokens
        self.in_blocks = self._children(
            "in_blocks",
            [
                TokenAttBlock(base_dim, num_heads, mlp_ratio, attn_drop, mlp_drop, num_tokens, dtype=self.dtype)
                for _ in range(num_transformers)
            ],
        )
        self.fc = self._child(
            "fc",
            MLP(
                base_dim * num_tokens, int(mlp_ratio * num_tokens * base_dim),
                drop=mlp_drop, norm_layer=True, dtype=self.dtype,
            ),
        )
        self.out = self._child("out", Linear(num_tokens * base_dim, num_classes, dtype=self.dtype))

    def call(self, x: tf.Tensor, training: bool | None = None) -> tf.Tensor:
        mask = tf.cast(
            x[:, self.num_tokens :, HIS_MASK_COLUMN : HIS_MASK_COLUMN + 1] != 0, x.dtype
        )
        for block in self.in_blocks:
            x = block(x, mask=mask, training=training)
        tokens = x[:, : self.num_tokens]
        shape = tf.shape(tokens)
        flat = tf.reshape(tokens, [shape[0], self.num_tokens * tokens.shape[-1]])
        return self.out(self.fc(flat, training=training))


class PET2Port(_Port):
    """``network.PET2`` in ``mode='classifier'``: body then classifier head."""

    def __init__(
        self,
        input_dim: int,
        conditional: bool = False,
        cond_dim: int = 3,
        pid: bool = False,
        pid_dim: int = 9,
        add_info: bool = False,
        add_dim: int = 4,
        num_classes: int = 1,
        base_dim: int = 128,
        num_transformers: int = 2,
        num_transformers_head: int = 2,
        num_tokens: int = 4,
        num_heads: int = 4,
        mlp_ratio: int = 2,
        mlp_drop: float = 0.0,
        attn_drop: float = 0.0,
        K: int = 15,
        num_coord: int = 3,
        coord_idx: Sequence[int] | None = None,
        mask_idx: int = HIS_MASK_COLUMN,
        use_int: bool = False,
        local_int: bool = False,
        **kw: Any,
    ):
        super().__init__(**kw)
        require_supported_configuration(use_int, local_int)
        self.body = self._child(
            "body",
            PETBody(
                input_dim, base_dim, num_transformers, num_transformers_head, num_heads,
                mlp_ratio, mlp_drop, attn_drop, num_tokens, K, conditional, cond_dim,
                pid, pid_dim, add_info, add_dim, num_coord, coord_idx, mask_idx,
                dtype=self.dtype,
            ),
        )
        self.classifier = self._child(
            "classifier",
            PETClassifier(
                base_dim, num_transformers_head, num_heads, mlp_ratio, mlp_drop,
                attn_drop, num_tokens, num_classes, dtype=self.dtype,
            ),
        )

    def call(
        self,
        x: tf.Tensor,
        cond: tf.Tensor | None = None,
        pid: tf.Tensor | None = None,
        add_info: tf.Tensor | None = None,
        mask: tf.Tensor | None = None,
        training: bool | None = None,
    ) -> tf.Tensor:
        body = self.body(x, cond, pid, add_info, mask=mask, training=training)
        return self.classifier(body, training=training)


def preset(size: str) -> dict[str, int]:
    """The named preset, transcribed from ``get_model_parameters``."""
    if size not in MODEL_PRESETS:
        raise ValueError(f"Unknown model size {size!r}; have {sorted(MODEL_PRESETS)}")
    return dict(MODEL_PRESETS[size])

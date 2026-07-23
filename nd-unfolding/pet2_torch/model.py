"""Compact independent PET2-family classifier.

This is a clean implementation of general point-edge/attention ideas.  It does
not copy Gregor Krzmanc's or OmniLearned source.  Every padding decision is
driven by ``token_mask``; no continuous feature is used as an implicit mask.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any

from .utils import fingerprint

try:
    import torch
    from torch import nn

    HAS_TORCH = True
    TORCH_IMPORT_ERROR = None
except ImportError as exc:  # login-safe Mac path
    torch = None
    nn = None
    HAS_TORCH = False
    TORCH_IMPORT_ERROR = exc


@dataclass(frozen=True)
class ModelConfig:
    continuous_dim: int
    coord_dim: int
    global_dim: int
    hidden_dim: int = 128
    num_heads: int = 8
    transformer_layers: int = 8
    edge_layers: int = 2
    k_neighbors: int = 3
    num_readout_tokens: int = 4
    max_type_id: int = 15
    max_view_id: int = 7
    dropout: float = 0.0
    architecture_family: str = "independent-pet2-small-concept-match-v1"

    def validated(self) -> "ModelConfig":
        if min(self.continuous_dim, self.coord_dim, self.global_dim) < 1:
            raise ValueError("model input dimensions must be positive")
        if self.hidden_dim % self.num_heads:
            raise ValueError("hidden_dim must be divisible by num_heads")
        if min(
            self.transformer_layers,
            self.edge_layers,
            self.k_neighbors,
            self.num_readout_tokens,
        ) < 1:
            raise ValueError("model depth and k_neighbors must be positive")
        if self.max_type_id < 1 or self.max_view_id < 1:
            raise ValueError("categorical vocabularies must reserve ID 0 and include real IDs")
        if not (0.0 <= self.dropout < 1.0):
            raise ValueError("dropout must be in [0,1)")
        return self

    def payload(self) -> dict[str, Any]:
        payload = asdict(self.validated())
        payload["fingerprint"] = fingerprint(payload)
        return payload


if HAS_TORCH:

    class _EdgeBlock(nn.Module):
        def __init__(self, dim: int, k_neighbors: int):
            super().__init__()
            self.k_neighbors = k_neighbors
            self.edge_mlp = nn.Sequential(
                nn.Linear(2 * dim, dim),
                nn.GELU(),
                nn.Linear(dim, dim),
            )
            self.norm = nn.LayerNorm(dim)

        def forward(self, h, coords, mask):
            batch, tokens, dim = h.shape
            k = min(self.k_neighbors, max(tokens - 1, 1))
            distance = torch.cdist(coords, coords)
            valid_pairs = mask[:, :, None] & mask[:, None, :]
            eye = torch.eye(tokens, dtype=torch.bool, device=h.device)[None, :, :]
            valid_pairs = valid_pairs & ~eye
            distance = distance.masked_fill(~valid_pairs, torch.inf)
            neighbor_distance, neighbor_index = torch.topk(
                distance, k=k, dim=-1, largest=False
            )
            h_all = h[:, None, :, :].expand(batch, tokens, tokens, dim)
            gather_index = neighbor_index[..., None].expand(batch, tokens, k, dim)
            neighbor = torch.gather(h_all, 2, gather_index)
            center = h[:, :, None, :].expand_as(neighbor)
            message = self.edge_mlp(torch.cat((center, neighbor - center), dim=-1))
            neighbor_valid = torch.isfinite(neighbor_distance)
            message = message.masked_fill(~neighbor_valid[..., None], -torch.inf)
            aggregate = message.max(dim=2).values
            aggregate = torch.where(
                neighbor_valid.any(dim=2, keepdim=True),
                aggregate,
                torch.zeros_like(aggregate),
            )
            return self.norm(h + aggregate) * mask[..., None]


    class CompactPET2Classifier(nn.Module):
        """Point-edge encoder plus masked attention pooling and one logit."""

        def __init__(self, config: ModelConfig):
            super().__init__()
            self.config = config.validated()
            dim = config.hidden_dim
            self.input_projection = nn.Sequential(
                nn.Linear(config.continuous_dim, dim),
                nn.GELU(),
                nn.Linear(dim, dim),
            )
            # ID 0 is a fixed padding row.  Every real category is >=1.
            self.type_embedding = nn.Embedding(
                config.max_type_id + 1, dim, padding_idx=0
            )
            self.view_embedding = nn.Embedding(
                config.max_view_id + 1, dim, padding_idx=0
            )
            self.edge_blocks = nn.ModuleList(
                [_EdgeBlock(dim, config.k_neighbors) for _ in range(config.edge_layers)]
            )
            layer = nn.TransformerEncoderLayer(
                d_model=dim,
                nhead=config.num_heads,
                dim_feedforward=2 * dim,
                dropout=config.dropout,
                activation="gelu",
                batch_first=True,
                norm_first=True,
            )
            self.transformer = nn.TransformerEncoder(
                layer, num_layers=config.transformer_layers
            )
            self.global_projection = nn.Sequential(
                nn.Linear(config.global_dim, dim),
                nn.GELU(),
                nn.Linear(dim, dim),
            )
            self.class_token = nn.Parameter(
                torch.zeros(1, config.num_readout_tokens, dim)
            )
            self.output = nn.Sequential(
                nn.LayerNorm(dim),
                nn.Linear(dim, dim),
                nn.GELU(),
                nn.Linear(dim, 1),
            )
            nn.init.normal_(self.class_token, std=0.02)

        def forward(
            self,
            continuous,
            coords,
            token_mask,
            type_id,
            view_id,
            globals_,
        ):
            if token_mask.dtype is not torch.bool:
                raise TypeError("token_mask must be torch.bool")
            if torch.any(type_id[token_mask] == 0):
                raise ValueError("real tokens cannot use category 0")
            if torch.any(type_id[~token_mask] != 0):
                raise ValueError("padded tokens must use type category 0")
            h = (
                self.input_projection(continuous)
                + self.type_embedding(type_id)
                + self.view_embedding(view_id)
            )
            h = h * token_mask[..., None]
            for block in self.edge_blocks:
                h = block(h, coords, token_mask)
            readout_tokens = self.class_token.expand(h.shape[0], -1, -1)
            readout_tokens = readout_tokens + self.global_projection(globals_)[:, None, :]
            sequence = torch.cat((readout_tokens, h), dim=1)
            class_mask = torch.zeros(
                (h.shape[0], self.config.num_readout_tokens),
                dtype=torch.bool,
                device=h.device,
            )
            padding_mask = torch.cat((class_mask, ~token_mask), dim=1)
            encoded = self.transformer(
                sequence, src_key_padding_mask=padding_mask
            )
            pooled = encoded[:, : self.config.num_readout_tokens].mean(dim=1)
            return self.output(pooled).squeeze(-1)


    def build_model(config: ModelConfig):
        return CompactPET2Classifier(config)

else:

    class CompactPET2Classifier:  # pragma: no cover - exercised as unavailable
        def __init__(self, *_args, **_kwargs):
            raise RuntimeError(f"PyTorch is unavailable: {TORCH_IMPORT_ERROR}")


    def build_model(_config: ModelConfig):  # pragma: no cover
        raise RuntimeError(f"PyTorch is unavailable: {TORCH_IMPORT_ERROR}")

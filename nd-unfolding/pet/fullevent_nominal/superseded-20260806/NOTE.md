# SUPERSEDED 2026-08-06 artifacts — the embedded `weights_folder` in these npz files is STALE

**Written 2026-08-11 by Session C (PET). Read this before loading either npz through its own
`inference_contract`.** See `docs/orchestration/FINDING-20260811-promotion-by-move-silently-repoints-artifacts.md`
and **BEN-133**.

## The hazard, and it does not raise an error

Both artifacts here were moved into this directory on 2026-08-07 when the 2026-08-08 run became
canonical. **Their embedded absolute paths did not move with them:**

| artifact | sha256 | `inference_contract["weights_folder"]` says | where its checkpoints ACTUALLY are |
|---|---|---|---|
| `pet_fullevent_nominal_weights.npz` | `8d17140f697faca7…` | `…/pet/fullevent_nominal/w_nominal` | **`…/superseded-20260806/w_nominal`** (this directory) |
| `pet_fullevent_floor_weights.npz` | `28fe004c31dcb414…` | `…/pet/fullevent_nominal/w_floor` | **`…/superseded-20260806/w_floor`** (this directory) |

The paths the contracts name **exist**, and the checkpoint files inside them **exist** — but they are
the **2026-08-08** artifact's networks, not these. So a consumer that resolves checkpoints from these
contracts (`step1_increment_trajectory.py`, `gate_ab_push_provenance.py`,
`step1_pull_push_decomposition.py`, `extract_fullevent_fps.py:253`) will pair **08-06 push weights with
08-08 model weights and return a number.**

A dangling path would have raised `FileNotFoundError` on first use. A path that resolves to a same-named
sibling does not fail at all. That is why this note exists rather than a fixed path.

## What to do instead

Pass the checkpoint directory explicitly, or copy these artifacts somewhere their sibling `w_*`
directories are the ones the contract names. **Do not** rewrite the contract inside the npz: that
changes a superseded artifact's digest, and the two digests above are what any historical receipt binds.

## Identity check, so you can confirm which artifact you are holding

`sum(w_reco*push)/sum(w_reco)` over `pass_reco`:

- superseded nominal (this dir): **0.7464834064182863** — the historical `0.746483` quoted in
  `step1_pull_push_decomposition.py`'s docstring as the original fold-forward failure
- superseded floor (this dir): **0.7388746403442940**
- 2026-08-08 canonical (parent dir): `0.7367462501305516`
- 2026-08-10 annealed (`fullevent_nominal_annealed/`): `1.0840529829474115`

If you loaded a "superseded 08-06" artifact and the fold-forward reads `0.736746`, you are holding the
08-08 one.

## Why this file exists at all

The Gate-2 supersessions (`g2_fullevent/gate2/final/superseded-20260719/`, `superseded-20260805-r1/`)
each ship a `NOTE.md`. This PET supersession did not, and that omission is the entire difference between
a documented archive and a silent corruption. Any future supersession in this tree ships one.

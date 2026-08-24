# Rescued uncommitted Delta edit — Gate-2 validator scalar units (2026-07-25)

Companion to `UNCOMMITTED-delta-gate2-units-20260725.diff`.

## Provenance

Recovered from the Delta working tree
`/u/jbailey2/MINERvA-OmniFold-gregor-pet2` on 2026-07-25, branch
`codex/gregor-pet2-omnifold` at `f7b7a775`. It was **uncommitted and unpushed**
— 25 insertions, 2 deletions in `nd-unfolding/pet/gate2_target_runtime.py`.
Rescued verbatim; **NOT applied** to either checkout. Author/turn unknown: no
campaign-ledger entry or session record claims it.

## What it changes

It adds a NumPy-only helper `independent_gev_coordinates()` and replaces

```python
measured   = np.asarray(source["measured_scalars"],  dtype=np.float64)[:, :2] / 1000.0
background = np.asarray(source["bkg_reco_scalars"], dtype=np.float64)[:, :2] / 1000.0
```

with a pass-through (plus shape and finiteness guards), on the stated grounds
that "the frozen G2 scalar contract stores these columns in GeV."

So it asserts the `/1000.0` MeV→GeV conversion in the Gate-2 independent binned
check is wrong.

## Why this is not cosmetic

`gate2_target_runtime.py` is the **frozen Gate-2 validator**, SHA-bound in
`nd-unfolding/g2_fullevent/gate2/final/G2_GATE2_TARGET_RUNTIME_RECEIPT.json`
(`a8539d8300f8f21290faee3c99809d775e9ae0dd44c6756217fe1a068f7a51ee`). Applying
this breaks that binding, so it cannot land without re-running Gate-2.

If the edit is **right**, the Gate-2 PASS of 2026-07-19 was obtained with a
spatially degenerate independent check: dividing GeV coordinates by 1000 leaves
every row inside the canonical extended FPS grid (pT ≤ 30, p∥ ≤ 120), so the
fail-closed domain guard at `gate2_target_runtime.py:432-435` still passes, all
mass collapses into the lowest bins, and the `rel_l1` / `max_rel` / `cosine`
comparisons at lines 445-453 compare two identically-misscaled histograms. The
signed-sum and normalization assertions remain valid; the **spatial** agreement
claim does not. That would make Gate-2 a weaker gate than its receipt implies —
not a wrong physics result, but a control that did not test what it says.

If the edit is **wrong**, applying it feeds MeV values to a GeV grid, rows
exceed the top edges, and line 434 dies with "retained measured/background
inventory is outside the canonical FPS grid".

## Evidence so far (indirect, not decisive)

- Points to **GeV** raw scalars (edit correct): the P5A record in
  `nd-unfolding/PET_P1_P5_SESSION_STATE.md` quotes post-sentinel-fix
  `reco_norm_mean 0.73/6.09 GeV`, and `rmu` there is the *raw* mean over
  `pass_reco` rows. MeV storage would give ~730/6090.
- **Not** evidence either way: `fullevent_fps_dataloader.py:60` `_SCALE = 1000.0`
  is applied by `_scale_clean` to point clouds only (lines 97, 123). The
  scalars reach the model through `_event_block`, which z-scores them, so the
  training path is scale-invariant and cannot reveal the raw unit.

## How to resolve it (one run, unambiguous)

Run the Gate-2 validator against `G2_FPS_MEFHC_P12.npz` with the patch applied.
The failure mode is loud and self-diagnosing: a clean PASS means the raw scalars
are GeV and the pass-through is correct; the out-of-domain `die` at line 434
means they are MeV and the original `/1000.0` should stand.

Blocked until the Perlmutter restore (2026-08-03): the input lives at
`/pscratch/sd/j/josephrb/MINERvA-OmniFold/nd-unfolding/g2_fullevent/input/`
and was never staged to CFS.

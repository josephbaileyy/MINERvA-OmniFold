# FINDING 2026-08-14 — The mask is part of the draw, and two blind builders agree on it perfectly

**`BEN-231`.** Mechanism found by **D**; occurrence measured by **lane C** (PET).
**Status:** handled in `SPEC-20260814-gate5-cstat-construction-v1.md` §6 (`CSTAT-D3`). Not a code repair.
**Evidence:** [`state/gate5-cstat-spec-measurements-20260814/flicker.out`](state/gate5-cstat-spec-measurements-20260814/flicker.out).

---

## The mechanism

Gate-5's replica extractor makes the reporting domain a function of the replica's own Poisson draw.

`extract_fullevent_replica.py:190-196` monkey-patches the nominal `completeness_2d` so the replica's
**signal Poisson factor multiplies the weights inside the completeness computation**:

```
def replica_completeness(truth_pt, truth_ppar, w, pass_truth, pass_reco, edges):
    return original(truth_pt, truth_ppar, np.asarray(w) * sig_factor, ...)
```

`extract_fullevent_fps.py:517-518` then hard-zeroes every cell that fails `comp > 0`
(`reported = comp > 0; xsec = np.where(reported, xsec, 0.0)`).

So `comp > 0` is **drawn per replica.** A thinly-populated cell can be reported in one member and hard
zero in another, and the zero is indistinguishable from a measured value of zero.

## The occurrence

D was explicit that it had confirmed the mechanism by reading the code and had **not** measured whether
any cell actually flips. The 14 published extractions are enough to answer it, and the answer is yes:

| `n_replicas_reported` (of 14) | cells |
|---|---|
| 14 — reported in all | 259 |
| 13 | 2 |
| **9** | **1** |
| 0 — never reported | 23 |

**3 cells flicker in only 14 draws, and one is reported in just 9 of 14.** The artifacts already record
this without anyone reading it: `n_cells_populated` in `extraction_telemetry` takes the values
**260, 261, 262** across members. The 23 never-reported cells match `n_cells_no_denominator = 23`
exactly, so those are structural and separate.

In the 9-of-14 cell, roughly a third of the across-replica spread is **the mask switching off** — a hard
zero substituted for a value — not fluctuation of the cross section. Its variance is wrong, and wrong in
a direction that is not even conservative: substituting zeros inflates the apparent spread.

## Why this is a finding and not a bug report

The interesting part is the failure mode of the *defence*, not of the code.

The campaign's protection for `C_stat` is two independent builders — lane B and a cold `codex` session —
writing to one spec, blind to each other, compared **element-wise**. That design is strong against
implementation error: transcription slips, wrong normalization, transposed indices, off-by-one.

It has **zero** power here. Both builders receive the same 50 member vectors. In a flickering cell both
compute the same variance from the same zeros. They agree to the last bit, the comparator reports
perfect agreement, and the judge confirms it. **Independence of implementation buys nothing against a
defect in the input that both implementations faithfully consume.**

This generalises past `C_stat`: an agreement-based check certifies that two paths computed the same
function, and says nothing about whether it was the right function of the right input. Blind replication
tests the *builders*; only the spec can test the *object*.

## What the spec does about it

`CSTAT-D3`, and it is declared rather than delegated, because a builder cannot be asked to notice
something invisible from inside its own task:

- **`D3a`** construct over the **union** (cells reported in ≥ 1 member; 262 at N=14) — not the
  intersection, because the intersection *silently deletes* cells and its deletion set depends on `N`,
  so the published dimension would drift with the member count.
- **`D3b`** publish per-cell **`n_replicas_reported`** in the output contract. Cheap now, expensive to
  retrofit; without it nobody downstream can distinguish a genuinely quiet cell from a flickering one.
  D asked for this and it is adopted verbatim.
- **`D3c`** the **quotable sub-block is `n_replicas_reported == 50`.** Cells below it stay in the
  published matrix, flagged, excluded from any inversion or χ², with their ids recorded. They are not
  deleted — deleting them would hide that the question was asked.
- **`D3d`** report the flicker count **even when it is zero.** This is the clause that matters most for
  the 50-member run: a null result must be recorded as an explicit `0`, because *absence* of flicker at
  full strength is itself a finding and an omitted field cannot state it.

## Note on the count

3-of-14 does not extrapolate to 3-of-50. More draws can only *reveal* more flickering cells — a cell
reported in all 14 may still fail at member 37 — so **262/259 is an upper/lower bound pair that will
tighten in one direction only.** The union can grow and the intersection can shrink. Both were measured
at `N=14` and both must be re-measured at 50/50; the spec marks every such number `[N=14]` and lists
re-measurement as construction precondition 3.

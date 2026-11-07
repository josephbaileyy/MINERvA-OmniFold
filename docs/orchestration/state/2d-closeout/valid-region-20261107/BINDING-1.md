# BINDING: the valid-region map, following Ben's suggested story (director, 2026-11-07)

**Binds** [`DECLARATION.md`](DECLARATION.md) and its code, as merged in PR #892 (merge `ddfeb5d5`), at
**M = `0687d6f2776b3ad691568f701de3aff166d9ca2a`**.

| file | sha256 |
|---|---|
| `DECLARATION.md` | `f46bb725607b0220c8fb85a8e572a63c7e5c587233496d2e7f27ecc7f0ca83a8` |
| `valid_region.py` | `896201cc9d03754ddac5185f548b1b7e3a56183dbb0fe6503fcd75c5c59d5433` |
| `test_valid_region.py` | `0df3207292ebd8c9e302f263eaa38e0012ef755940c95d311603d22916064580` |
| `INPUTS.sha256` | `53aae44cd2327509863a2c65180f6701e2f5c8860a7fe971f2d0097f1a45045a` |

The director hashed each file on origin/main.

## Under

Joseph's direction of 2026-11-07, given through the director's question, was "can we not incorporate this into the
work we are doing right now?". It came after his advisor Ben's suggested story, which Joseph relayed and nobody here
received directly. The direction was to fold it into the current work: records-only and declared before any number is
computed.

## What the director checked

**coverage-5b-audit's GO at `0687d6f2`:**
- **VR-1 is closed.** Reading (3) is descriptive only in both the text and the code, and a test walks every key.
- **No threshold or set choice looks steered.** Each has a reason that predates the seen pulls.
- **Tests:** 56 tests OK and 48 of 48 mutants killed, reproduced.
- **One LOW** (v_G's independence assumption) is on the audit's follow-up list.

## Rulings

1. **V-ATLAS is bound as declared:**
   - A1, MC n_eff ≥ 5,000. It is applied to the simulation's weights, a disclosed deviation;
   - A2, S1's stat σ/f < 0.15;
   - A3, |z| ≤ 2 at all 12 graded truths;
   - ATLAS's item 5 is recorded as not met.
2. **V-PRIOR is bound as declared:** ρ = S_b/S_g < 0.5 in all four noise combinations. It is labelled as this lane's
   operationalization of "comparable", not ATLAS's, and the director's withdrawn "≤ 1" wording is recorded with its
   reason.
3. **Reading (3) is descriptive only,** with no class and no sentence. It is NOT CITABLE FOR "the 2D mismodeling is
   localized in the extra dimensions", or for "it is not".
4. **The run:** local, at M, at 0 node-h.
   - A fresh clone with empty porcelain.
   - `shasum -a 256 -c INPUTS.sha256`, then `python3 -B valid_region.py read`.
   - The receipt goes to `receipts/read/` as a PR, followed by an outcome record with the licences.
   - No cluster contact.
5. **Any wording for the paper** comes later, through a referee read and Joseph. If Joseph learns from Ben of a
   specific source for the prior-spread metric, V-PRIOR is amended before any paper use.

Nothing is submitted, deposited or tagged.

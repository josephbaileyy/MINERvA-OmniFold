# RPL (i) the scale fit: code, tests and mutation receipt (2026-11-22)

**By** limitation-resolver, for the director, under [`RPL-DECLARATION.md`](../RPL-DECLARATION.md) check (i). This is
the code only. Nothing has run on cluster inputs, and no data step, fit or outcome is formed here. The run waits for
P-RPD (RPD-RECO's chain through d2) and the director's binding of this code, which comes after the merge.

## Files

- `nd-unfolding/rpl_scale_fit.py` (sha256 `cb808a30cb1e63f2fcc923075b8bfb1c3c56e74df4a6e895493e00221af2dff8`): the fit
  of α in p → p/(1+α) for PB against PA on `PZ_EDGES`, the reproduction control R0 against c0, the planted-scale
  control (+1%, +3%), the outcome table and the descriptive fits (PC, and each playlist against PA without it). It
  reads RPD-RECO's records through their predecessor chain and replays RPD-RECO's own draws.
- `nd-unfolding/tests/test_rpl_scale_fit.py` (`4b2183f2ba67009558bfa90a39a9f1864a6b24e2c4f0017250a4e8d1d8aae439`):
  66 tests, local fixtures only. The integration tests run RPD-RECO's chain (pins .. d2) on its real-format fixture,
  with a continuous p_par spectrum.
- `nd-unfolding/tests/rpl_scale_fit_mutation.py` (`da3a6a104a528b01c3958af39ffe5194c196a925ae6f10ecb7f643dd6248e7dc`):
  53 mutants, each a single-fragment change in a temporary copy beside unmodified RPD-RECO modules, run against the
  suite with `pytest -x` and every thread cap at 1.

## Receipt

- `MUTATIONS.json` (sha256 `34630dda6d71b9971cb70184ced93bcabbe6cf66afab7b52b6038ed39f19ea5e`), schema `rpl-scale-fit-mutation/1`: **53 of 53 killed**, recorded at the
  module, suite and harness shas above. `mutation.log.txt` is the harness's console output (`MUTATION :: 53/53
  killed`, rc 0).
- The suite passes at these bytes: `66 passed`.
- Round 1 (commit 79bdfa6da) had 49 tests and 30 mutants, 30 killed. An earlier run in that round killed 27 of 30;
  the three survivors (`used-bins-or`, `refit-subset`, `wall-skipped`) were real test gaps and got tests.

## Review round 2: what changed

Grok and agy read round 1 (commit 79bdfa6da). Following the director's rule, every FIX or suggestion was made a fix
on this branch unless it would go past the declaration. The changes:

- The fit uses both predictions for a used bin (P ≥ 25 in both, P = 25 included), σ_b comes from replicas 1..200 with
  ddof = 1, and σ_α comes from all 200 refits. Each is now pinned by a unit test on a synthetic group.
- The wall-clock check runs before the nominal scan and before each replica refit.
- χ²(α̂) is evaluated at α̂ itself, off the lattice, for the fit and for the plant.
- `classify` refuses a D1 reading outside `READINGS` (`SEEN`, `NOT-SEEN-AT-3σ`).
- σ_band is read through `deciding_band`, which checks the band record's schema and takes its MINOS overall value.
- The published 1 % muon energy scale (`iii/README.md`, quote 3b) is printed beside σ_band, as declared at
  `RPL-DECLARATION.md:130`.
- The plant's pseudo-data halves are doubled to c0's 2P, and the plant passes on the tolerance alone (G3 below).
- `run` refuses a CFS output root before anything else. `main` writes a STOP record only into an output directory that
  is off CFS and new or empty at the start; otherwise, or if the directory cannot be inspected or written, the STOP
  is printed only. An OS error is a STOP (`OS_ERROR`), and an O_NOATIME open failure is the guard `NOATIME_OPEN`.

Two findings were settled against the declaration:

- **G3 (the plant).** The plant passes when |α̂ − α_true| ≤ 3.5 σ_α, the tolerance the declaration fixes at
  `RPL-DECLARATION.md:300` (audit M2, `:361`). Round 1 also failed a plant whose fit ended at a scan edge; that clause
  is not in the declaration and was removed. Mutant `plant-edge-clause` puts it back and is killed.
- **G2 (a descriptive fit that cannot be formed).** The declaration says only that α̂_PC and α̂_X are "reported as
  descriptions, with no outcome" (`:112`, `:130`). It fixes no reading for a descriptive fit that refuses, so a
  refusal there stays a STOP, under the controls rule at `:272` ("Each is a STOP that reports the check as not made").
  A draft that recorded such a fit as unformed went past the declaration and was reverted. The director's plan: if
  the real run STOPs on a descriptive fit (for example 1L refusing `FIT_NDF`), limitation-resolver reports the guard
  and its values to the director, and an amendment, in Joseph's wording, goes to Joseph.

## Reads

| read | report | sha256 | verdict |
|---|---|---|---|
| Grok, round 1 at 79bdfa6da | `reads/rplfit-79bdfa6da/grok/out.txt` | `d37a0ee0e2380f1af61ec210cdae0521043f2678976927db330ab344c7c1e351` | GO |
| agy, round 1 at 79bdfa6da | `reads/rplfit-79bdfa6da/agy/out.txt` | `d22abacf166cff2249a7551268e0e821e6725ebd5ca79a21566b5b90d3115e2f` | GO |
| agy confirm 1 (round-2 delta) | `reads/rplfit-delta1/out.txt` | `0101fa914edab4bf7b312fb85823f99841dee71cc587149b17eb6daa484216dc` | GO |
| agy confirm 2 | `reads/rplfit-delta2/out.txt` | `d6714c4ce73d01021e79646e2b72427eb9823126f0095ce51e498578cfc85a8b` | GO |
| agy confirm 3 (inspection error) | `reads/rplfit-delta3/out.txt` | `ceb2ef850c466a7febc0497af7d57495e3eec06e50b9ba9f31ae8af8238be612` | GO |

The paths are under `~/codex-reports/note-measurement/` on Joseph's laptop and are not committed.

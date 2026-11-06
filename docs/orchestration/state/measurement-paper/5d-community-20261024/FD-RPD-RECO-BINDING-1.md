# BINDING 1 (design): d1 and d2, reconstruction-level data/MC per playlist and the flux swap (director, 2026-11-04)

**Binds** the design of [`FD-RPD-RECO-DECLARATION.md`](FD-RPD-RECO-DECLARATION.md), revision 2, sha256
`b0eee33c95ccb037c681df8d33dccdf1b3d3af60098bba6545c725f706ebe5d8`, as merged in PR #761 at
**M = `5c538db6a0685e3d79fbe487d205540e704ddc1b`**. This covers the recipe, the readings, the outcome table and the
licences, the inputs pinned in `fd/rpd-reco/INPUTS.sha256`, and the price.

**Under** `DECISION-20261104-joseph-referee-analysis-commission.md` (#759, at `1a87d209`), items d1 and d2, and the
Codex diagnosis lane's #760 §C (C-R, C-H).

## What the director checked

- **The digest.** The declaration's sha256 at M is the one above.
- **The audit** is verbatim beside the declaration (`FD-RPD-RECO-AUDIT-1-SONNET-{PROMPT,ANSWER}.txt`). It found 1
  BLOCKING finding (d2's outcome table had a gap), 9 major and 9 minor. §9 maps each finding to its change, and the
  outcome table is now ordered and exhaustive.
- **Admissibility (§6):**
  - a reconstruction-level read with the recipe frozen and bound before any ratio is computed;
  - no new cuts, and no change to any reported number, estimator or covariance;
  - what was already read at reconstruction level, and what was not, is stated;
  - d2-predict fixes the predicted size from simulation before any data is read.
- **The licences (§8):**
  - each covers a note statement first;
  - paper use goes through the PRD-referee read and to Joseph;
  - no outcome names a cause, except TRACKS, which names only a coincidence with the simulation's flux-file
    assignment;
  - "The cause is not known", C_PL,5D and RPD's licensed sentence are unchanged.

## Rulings

1. **The design is bound as declared at M.**
2. **The code** (`nd-unfolding/fd_rpd_reco.py`, the steps pins → p0 → step0 → c0 → d2-predict → d1 → d2) needs its
   own tests, a mutation receipt, an audit of the code and binding 2 before anything runs.
3. **The price is 0 node-h.**
   - Login node, threads 1, nice 19, O_NOATIME, a fresh clone at the bound sha, nothing written to CFS.
   - If the bootstrap's measured wall-clock passes 2 h, or its load is more than light, it moves to a compute node.
     That is priced to the director first.
4. **The order:**
   - the run follows the B4 probe's cluster work in limitation-resolver's queue;
   - each connect's sha256 comes to the director, who gives the go;
   - the flux files' retention is recorded at P0.
5. **The Codex diagnosis lane's C-N** (the per-playlist flux and POT provenance inventory) supplies d2's flux-file
   identities. That lane works from existing records and is not duplicated here.

## Binding 1, addendum A1: d2's swap factor follows MAT's own CV flux weight (director, 2026-11-06)

**No new M.** d2's design and readings are unchanged. This addendum corrects one implementation sentence of §4, from a
source finding made before any declared input was read.

**What led to it.** Codex2's source review for R1 fetched MAT at `35097b65ab1680db8058f9ede18fecffdc3a1ea3` from
MinervaExpt/MAT. The director re-fetched it, and `PlotUtils/FluxReweighter.cxx` has sha256 `4576346d…`, as in receipt
#849.
1. **The weight.** `GetFluxCVWeight` (`:977-992`) returns `newFlux->Interpolate(Enu) / genFlux->Interpolate(Enu)`:
   - below 75 GeV, from interpolated values;
   - above 75 GeV, from bin contents (`:984-987`);
   - 1 when either is zero (`:988-990`).
2. **The numerator** is the reweight flux, which is replaced by `Constrainer().ConstrainHisto(...)` of the file
   histogram when the ν-e constraint is applied. The analysis uses the string constructor (`:372`), reached through
   `flux_reweighter` (`:2187-2196`) and `_flux_reweighter` (`:42`), with gen2thin and g4numiv6 for every ME playlist
   (for example `:87-93`). In that constructor:
   - the numerator is at `:396`;
   - the constraint is at `:399-406`;
   - the generated flux is at `:425`;
   - the playlist is mapped by `GetPlaylistEnum` (`:388`, `:2110-2126`).

   The enum constructor (`:311`; `:331`, `:335-340`) does the same. coverage-5b-audit's check located these lines.
3. **The constraint in the analysis.** The analysis's event loop applies it: `PlotUtils::MinervaUniverse::SetNuEConstraint(true)`
   at `MINERvA101/MINERvA-101-Cross-Section/runEventLoopOmniFold.cpp:1698` @ `f4cd8f8b`.
4. **The denominator** is the playlist's generated flux, `flux_E_unweighted` (`:425`, `:940`).
5. **The files MAT opens** (`:913-940`):
   - the numerator from `flux-gen2thin-pdg14-minervame{1D,1M,1N}_rearrangedUniverses.root`, `flux_E_cvweighted`, then
     `ConstrainHisto`;
   - the generated flux from `flux-g4numiv6-pdg14-…_rearrangedUniverses.root`, `flux_E_unweighted`.

§4 says that "the factor is applied as a step function in the files' Eν bins". That is not how MAT evaluates its
weight. So the swap would not be "exactly φ_T(E)/φ_own(E)" in MAT's sense.

**Rulings.**
1. **φ is the CV reweight flux as MAT's FluxReweighter holds it.**
   - It is obtained by calling MAT in the pinned MAT environment (`fd_rpd_inputs.mat_environment()`, `check-mat-setup`).
   - It uses the analysis event loop's own FluxReweighter arguments, cited `file:line @ sha` in P0's record. The
     ν-e constraint is included, so the histogram is the constrained one.
   - The constraint is not re-derived, and no `flux_E_cvweighted` file histogram is used in its place.
2. **The swap factor at a row's Eν** is w(φ_T, g) / w(φ_own, g), where:
   - g is the generated flux of the row's own MC sample, which the swap does not change;
   - w(n, d) is `GetFluxCVWeight`'s value: n/d, or 1 if n or d is 0.

   Each of n and d is evaluated as MAT does:
   - with ROOT's own `TH1::Interpolate` for Eν ≤ 75 GeV, since MAT's test is strictly `Enu > 75.`;
   - with the bin content above 75 GeV.

   With every value non-zero, this is φ_T/φ_own.

   **P0 counts each zero pattern separately, with its count and its `pass_reco` weight share:** φ_own = 0, φ_T = 0, and
   g = 0.

   **Evaluation:** the factor is evaluated by ROOT in the MAT-environment extract step, which writes per-row factors or
   an equivalent pinned table. A reimplementation in the numerical steps is allowed only with a test, on the real
   staged histograms, equal to ROOT's values to 1e-12 relative at every evaluated Eν.
3. **P-F's premise check at P0 stands as declared.** P0 records, from the pinned source and the analysis's arguments:
   - which generated flux each playlist's MC uses;
   - that the swap leaves it unchanged.

   If the source shows the weight is not of the form φ_reweight(E) / φ_gen(E) with φ_gen fixed by the MC sample, d2
   STOPs before any swap.
4. **Unchanged:**
   - the 0.1 % out-of-range STOP;
   - the swaps;
   - the background bracket;
   - every reading and licence.

   The sentence "applied as a step function in the files' Eν bins" is replaced by rulings 1–2.
5. **Tests:**
   - a fixture where interpolation and step differ, which must give ROOT's interpolated value;
   - the 75 GeV boundary from both sides, including exactly 75.0;
   - each zero pattern;
   - a REQUIRED mutant for each.

   The real-MnvH1D test runs in limitation-resolver's lane, in the MAT environment (#848's ruling of 2026-11-06).
6. **coverage-5b-audit** reads this addendum together with #848's next head.

Nothing is submitted, deposited or tagged.

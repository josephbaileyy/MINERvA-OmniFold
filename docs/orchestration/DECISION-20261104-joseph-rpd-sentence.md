# DECISION 2026-11-04 — Joseph: the run-period diagnosis's licensed sentence goes into the paper, verbatim

**Recorded by** the paper-tighten lane, as director.

## What led to it

**The run-period diagnosis (RPD)** is bound by `FD-RPD-BINDING-1.md`, `-2.md` and `-2-A1.md` (#703, #727, #741). It
finished on 2026-11-04 and spent 1.89 of its 3.0 CPU node-h. The readout record is `$R/readout/fd_rpd.json`, sha256
`c0b06cfd2d11d99fc9226d054e68b951231f5d02e81ea3abc80cf7f89b624658`; its receipts follow in limitation-resolver's
readout PR. Its outcome fields:
- **stage 0: SEES.** The 5D chain sees the step: s₀ = +6.28%, z = 10.5.
- **R1: OTHER.** No PERIOD-WIDE or SUBSET pattern. CARRIES {1L, 1M}; PARTIAL {1G, 1N, 1P}; FREE for the other 7.
- **R2: CLUSTERED.**
  - The flux-grouping permutation test gives p_flux = 1.08 × 10⁻⁴ = 1/9,240, the smallest value it can return.
  - The era test gives p_era = 5.17 × 10⁻³.
  - Calibration holds: α̂ is 0.040–0.057 against the gate's 0.0646, over 2,000 datasets.
- **N0:** neither SIZE-BIAS flag fired.
- **R3:** not read, which applies only under EXCHANGEABLE-COMPATIBLE.

**What the declaration licenses** (`FD-RPD-DECLARATION.md` §6, fixed before any number was read). The row SEES × OTHER
× CLUSTERED licenses R2's row only (§6.3). In §6.2's CLUSTERED row, "the clause stays" and one sentence may be added:
"The offsets of the twelve playlists differ between the three period groups by more than their playlist-to-playlist
scatter would give."
- §6.1: no outcome drops "The cause is not known".
- §6.4: no outcome licenses "validated", "covers", "coverage" or "which period is correct".

**The PRD-referee read (Gemini)** is in `state/measurement-paper/5d-community-20261024/fd/consult-rpd-sentence-20261104/`,
verbatim with SHA256SUMS. It recommends adding the sentence: without it, a referee may suspect the three-group block
bins ordinary run-to-run drift. It suggests placing the sentence immediately after "differ by more than their bootstrap
scatter", and asks for the significance, at least in the note with a pointer.

## Joseph's answer, verbatim

Asked how the paper should use the one optional sentence the run-period diagnosis licenses:

> Add verbatim + note pointer (Recommended)

sha256 of the text plus a final newline begins `24fc223d2413fd06`.

The option as put to him:
- insert the licensed sentence word for word after 'differ by more than their bootstrap scatter', with a pointer to
  the note;
- the note gets the permutation test and both p-values (1.1e-4, 5e-3);
- the paper lane drafts, with a ledger and a PRD read, and then Joseph reads before merge.

## What is decided

1. **The paper.** In Sec. IV A's run-period paragraph (`paper_body.tex`, the sentence "The unfolded results of the
   three run-period groups … differ by more than their bootstrap scatter."), the licensed sentence is inserted
   immediately after, word for word, with a pointer to the note's run-period section.
   - Nothing else in the paragraph changes: "The cause is not known", "these data cannot establish which period is
     correct", "poorly determined" and the 0.73–2.56 interval all stay.
2. **The note.** The run-period section (`sec_fived16.tex`, near sec:fived16-pl) gains a description of the
   twelve-playlist test. It cites the RPD readout record by sha and the declaration and bindings, and gives:
   - the 9,240-partition (6, 3, 3) permutation test, with p_flux = 1/9,240 = 1.08 × 10⁻⁴;
   - the era test, with p_era = 5.17 × 10⁻³;
   - the calibration (α̂ 0.040–0.057 against 0.0646);
   - R1's classes, stated descriptively with no localisation claim.

   No sentence names a cause or uses §6.4's barred words. The note's own §6.2 counterpart (`sec_fived16.tex:125`) may
   take the same sentence.
3. **The process.** The paper lane drafts on a branch from main, with the fact ledger, receipts-bound numbers and a
   reading copy. The director runs a PRD-referee read of the diff, and Joseph reads before merge. Overleaf is
   re-synced after.
4. **No other change.** Binding 1 ruling 5 stands: no cause is supplied, and no outcome by itself drops "poorly
   determined". Adopting C_PL,12 does not arise, since R2 is not EXCHANGEABLE-COMPATIBLE.

Nothing is submitted, deposited or tagged.

# BINDING 1 (design and code): IBUKT, the 2D OmniFold and binned-IBU known-truth recovery screen (director, 2026-11-18)

**Binds** [`IBUKT-DECLARATION.md`](IBUKT-DECLARATION.md), sha256 `8511925449d3d0b4826da4bd099dfd5b2d079cb92a47381552fe47f6602a3c14`, and its code under `2d-unfolding/ibukt/`, as merged in PR #1215 at **M_IBUKT = `d8b390ab3e7a7a9cc6a882d017737612de6d5aab`**. The files are byte-identical to the audited head `c8e05d1f`. Code sha256 prefixes at M_IBUKT:
- `ibukt.py`: `f98fc993`
- `run_ibukt.py`: `a7d3dc39`
- `jobs.py`: `85a11cea`
- `screen.sbatch`: `469881a2`
- `config.json`: `35f34467`

**Under:**
- [`DECISION-20261117b-joseph-note-plan.md`](../../../DECISION-20261117b-joseph-note-plan.md), the IBU-test go: Joseph, 2026-11-17, "go ahead with the IBU test".
- The co-author's question whether a 2D OmniFold–IBU difference means "we are not doing something properly". The phase-1 investigation is at `~/codex-reports/2d-omnifold-vs-ibu/PHASE1.md`.

## What the director checked

Independent reads, kept under `~/codex-reports/ibukt-audit/`:
- **Rev 0** (`d6ac2f29`): PASS WITH FIXES (Grok). Two launch blockers:
  - the declared two-worker packing was not implemented;
  - the 5-hour limit had no margin.

  Two control and test gaps:
  - the within-bin integrals had no identity check and no movement check;
  - there was no noise-free nominal pair through the real pair path, and the weights, settings and seeds were not asserted.
- **Rev 1** (`9b21bb3f`): the fixes were applied. The director then required a change: the nominal pair control must not use 1e-8, which finite classifiers cannot meet.
- **Rev 2** (`6e8a1bc5`): PASS from Grok; PASS WITH FIXES from Codex. The control uses |estimate/truth − 1| ≤ 0.02 per reported cell, and the within-bin integral identity stays at 1e-8. Codex required two readout-provenance fixes:
  - the scorer must verify the nominal control;
  - cell and truth identities must be checked against the pinned bank.
- **Rev 3** (`c8e05d1f`): **PASS (bind)** from Grok's confirmation read. Both readout fixes are present.

**What it licenses** is in the declaration's outcome-license table. Per-cell recovery of the known truth on these seven deformations, for each method at K = 5. It does NOT separate the missed-event regression from finite classifier capacity, and it does not explain the measured data difference.

## Rulings

1. **The design and code are bound as merged at M_IBUKT.**
2. **The price:** a cap of **5.90 CPU node-h** and a limit of `--time=05:15:00`. The one-pair preflight refuses the remaining 34 pairs unless 18 measured walls fit both the allocation and the cap, with scoring reserved. A projection above the cap STOPs to the director.
3. **A connect** needs all of these:
   - a sha-pinned connect script and the director's go on that sha;
   - **Joseph's explicit go in the IBUKT session**, whose own boundary requires it;
   - fence notices to cov2d and tier3-design;
   - `sacct` (never `squeue`), `O_NOATIME` reads, CPU only, and nothing written to CFS.
4. **Manuscript fence:** no outcome changes any note or paper wording. The outcome goes to Joseph and Ben under the declaration's licences.
5. **Timing:** the screen does not block the note release sent to the co-author on 2026-11-19.

Nothing is submitted, deposited or tagged.

# DECISION 2026-11-19 (d) — Joseph: the IBUKT cap is raised to 6.5 CPU node-h

**Recorded by** director-helper-3, for the director, who relayed Joseph's words.

## What led to it

- **The binding and the reruns.** [`state/2d-closeout/IBUKT-BINDING-1.md`](state/2d-closeout/IBUKT-BINDING-1.md) caps the IBUKT screen at 5.90 CPU node-h. [`DECISION-20261119-joseph-ibukt-rerun.md`](DECISION-20261119-joseph-ibukt-rerun.md) keeps that cap across all IBUKT runs, and a projection above it STOPs to the director, who brings it to Joseph with the number.
- **The STOP.** The director reports that screen c STOPPED on the noise-free nominal control: IBU at K=5 gave 0.060, above the 0.02 criterion.
- **The diagnosis.** A read-only diagnostic ruled out the edge term and the migration term. That leaves the refinement, by elimination.
- **The number.** By the director's accounting, the runs so far have spent (638 + 832 + 466)/3600 = 0.5378 node-h. A rerun of screen plus score would take 5.35 node-h, which leaves 44 s of headroom under 5.90 and no room for a fresh prepare. This record cites the director's figures; it holds no receipts of those jobs.
- **The proposal.** The director proposed raising the cap from 5.90 to about 6.5 CPU node-h.

## Joseph's words, verbatim

2026-11-19, answering that proposal:

> I for sure approve raising the cap

(`e17bb90eebb861194f0b5dc94609892c417101ebe68f54ca9c5981d3a324cbb2`, the sha256 of the text plus a final newline.)

## What is decided

1. **The cap.** The IBUKT cap across all runs is raised from 5.90 to 6.5 CPU node-h. This is the director's proposed figure, which Joseph approved.
2. **Everything else in the binding is unchanged.** That covers the conditions that DECISION-20261119 item 3 lists (fresh fence acknowledgments, `sacct` only, `O_NOATIME` reads, CPU only, nothing written to CFS) and the per-stage director go on a pinned sha. A projection above 6.5 CPU node-h STOPs to the director, who brings it to Joseph with the number.

## Not decided here

- The design change (binned IBU on the signed target). Joseph's answer is recorded in [`DECISION-20261119e-joseph-ibukt-signed-ibu.md`](DECISION-20261119e-joseph-ibukt-signed-ibu.md).
- Any tolerance change.
- Any IBUKT result, and any note wording.

## CITABLE FOR / NOT CITABLE FOR

- **Citable for:** the IBUKT cap of 6.5 CPU node-h across all runs.
- **Not citable for:**
  - any tolerance change (the design change is DECISION-20261119e's);
  - a director go on any stage's script sha;
  - any IBUKT result;
  - any note or paper wording.

Nothing is submitted, deposited or tagged.

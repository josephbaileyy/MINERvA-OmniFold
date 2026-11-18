# BINDING 1 (design): PILOT-FB, forced LightGBM bins against the rounding instability (director, 2026-11-17)

**Binds** [`PILOT-FB-DECLARATION.md`](PILOT-FB-DECLARATION.md) rev 3, sha256 `4dd69f440744905245b223b7b65091c6c66722c3fb39c0a2068d9d4794144c72`, as merged in PR #1211 at **M_PFB = `522ac0b67717315f3fe54377bdbf4af71090948d`**. The file is byte-identical to its audited head `9aabd8bb`.

**Under:**
- [`DECISION-20261117b-joseph-note-plan.md`](../../../../../../DECISION-20261117b-joseph-note-plan.md) item 3. That records Joseph's approval of the pilot, "yes I meant the pilot and the bin edge fixing" (2026-11-17).
- RS1's mechanism finding: rounding-level perturbations break ties among equal float32 values and change LightGBM's histogram bins, and a perturbation that keeps the ties removes the spread. The declaration's §1 cites it.

## What the director checked

Independent design reads, over four rounds, all read-only. Reports are kept under `~/codex-reports/pilot-fb-audit/`.
- **Rev 0** (`260123d1`): FAIL from both Codex and Grok. Four blockers:
  - G3 checked a bin count, not the boundaries;
  - admissibility was not guaranteed for every feature, including the −9999 sentinels and pool-versus-training differences;
  - the outcome table was not a partition;
  - the gate timing was inconsistent, with no detector for an unapplied jitter.
- **Rev 1** (`25b9137c`): FAIL from Grok. Admissibility, the partition and the per-role edges were fixed. Two blockers remained:
  - G3 read the loaded bounds at `%lf`, not the boundaries in use;
  - J's equality did not follow the source-array jitter path.
- **Rev 2** (`3be11fc1`): PASS WITH FIXES from both Grok and Codex. Both rev-1 blockers were fixed at the design level, and the G3 (a)–(c) sufficiency argument holds. Four fixes were required:
  - the stored zero threshold;
  - J2's full `build_pseudo` call;
  - INCOMPLETE excluding a deliberate gate stop;
  - activating fixtures for the G3 mutations.
- **Rev 3** (`9aabd8bb`): **PASS (bind)** from Grok's confirmation read. All four fixes are present, nothing else in the science moved, and no new defect was found.

**The price:** expected 0.63 CPU node-h, with a cap of 0.9. There are 24 unfolds in all, and a round-1 wall projection stops a run that would not fit.

## Rulings

1. **The design is bound as declared at M_PFB.** Code with its tests and declared mutants comes next. Then an independent code audit by two readers, and a code addendum to this binding, before any connect.
2. **The cap is 0.9 CPU node-h.** A projection above it at any gate STOPs to the director.
3. **A connect** needs a sha-pinned connect script and the director's go. It also needs a fence notice to cov2d and the other fenced lanes for the new `pfb_` job family, reads made with `O_NOATIME` (plain reads only where the declaration names them), `sacct` (never `squeue`), CPU only, and nothing written to CFS.
4. **Manuscript fence.** No outcome changes any note or paper wording. The outcome goes to Joseph and Ben as an option, under the declaration's licensed statements.
5. **Timing.** The pilot does not block the note release sent to the co-author on 2026-11-19.

Nothing is submitted, deposited or tagged.

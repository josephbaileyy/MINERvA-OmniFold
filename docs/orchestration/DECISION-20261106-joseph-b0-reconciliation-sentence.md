# DECISION 2026-11-06 — Joseph: the B0 reconciliation sentence goes into paper IV F as written

**Recorded by** the paper-tighten lane, as director.

## What led to it

`DECISION-20261102-joseph-bias-and-stabilisation-routes.md` item 5 left B0's reconciliation sentence for Joseph. That
sentence explains why the training-seed block is zero while rounding-level input changes move results by up to 2.6 σ_stat.
It was to come with the B4 probe's outcome, through a PRD-referee read. The probe read NONE_PASS
(`OUTCOME-20261105-fd-stab-none-pass.md`, #785).

The paper lane drafted three sentences with a ledger (PR #804, `b0-reconciliation-20261105/`). The PRD-referee read
(Sonnet), verbatim with SHA256SUMS in `b0-reconciliation-20261105/prd-read/`, said USE REVISED. It wanted:
- the joint-cell scope of the 37 % stated;
- the 2.6 σ called the largest shift, not the typical one, with its population.

The lane revised accordingly. The population comes from the record: s5e `assess_receipt.json` A3, 153 functionals, two
edge-safe float32-ulp jitters. The draft's third sentence was kept, because the director's prompt to the reviewer had
misstated fact 4 and the record shows that no candidate met the stability bar at all.

## Joseph's answer, verbatim

Asked whether to add the sentences, as quoted to him in full:

> Add it as written (Recommended)

sha256 of the text plus a final newline begins `a1e74c5a65628cea`.

## What is decided

1. **Paper IV F** takes the three sentences of PR #804's revised draft verbatim. They go after "…fails a data-stability
   requirement of at most 0.3 (median) and 1.0 (maximum) statistical standard deviations." Every clause carries its
   ledger row (B0-1 to B0-5).
2. **The note's counterparts:** the jitter in the statistical replicas at `sec_fived16.tex:96` (B0-2), and the B4 outcome
   at `sec_5d.tex`'s stability paragraph (B0-5). They use the same facts and no new claim.
3. **The process:**
   - the paper lane builds both, with the ledger, check_round and the rater copy;
   - the director checks the built PDF against this record and merges on CI;
   - the director then re-syncs the Overleaf standalone.

Separately, Joseph answered "I'll renew it" (sha256 begins `c2a7efc6224d1839`) about the NERSC certificate, which expires
2026-11-06T06:11:03Z.

Nothing is submitted, deposited or tagged.

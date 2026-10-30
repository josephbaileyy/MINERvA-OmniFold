# RECORD — OI-120 traced: Joseph decided all three parts on 2026-08-14; two ran, and the third is OI-22's (2026-10-30)

**By** the close-items session, on the director's order of 2026-10-30: trace each part of OI-120 to a later record, or
show by a covering search that there is none, then propose. **Read-only:** nothing was run on the cluster.
<!-- absence-ok: a scoping statement about this record's own method, not a claim that a result is absent -->

**CITABLE FOR:** where each of OI-120's three decisions was made and what came of it, at `d6f79a85e`.

**NOT CITABLE FOR:**
- any result's physics, which this record does not re-assess;
- whether OI-22's alignment proof should now run. That is OI-22's, under its 2026-10-29 deferral.

**PROPOSES:** retiring OI-120, since every decision it waits on is made (§2). The register is not changed here; the
ruling is the director's.

## 1. What the row waits on

OI-120 was filed 2026-08-14 in `2eadf9b0a` (*"the three decisions waiting on Joseph, recorded rather than left in a
conversation"*). It is `WAITING-USER`, owner `Joseph`. Its three parts:
- (a) `k` for `C_syst`, from Gate 6 Leg F's existing artifacts, outside Leg F's predeclared rule;
- (b) OI-22 leg (b): event-by-event alignment against the source ROOT;
- (c) OI-22's leakage closure, through the production loader.

## 2. Each part, traced

**Joseph's decision, verbatim, 2026-08-14:** *"For item four: a) yes, and yes do b) and c)"*. It is quoted in two
places:
- the message of `1cd0dc4dd` (2026-08-14);
- the receipt `docs/orchestration/state/oi120a-csyst-k-from-legf-20260814.json`, field
  `AUTHORIZATION_AND_THE_GUARD_IT_CROSSED.joseph_verbatim`. That receipt left the live tree in `84607aa3b` (2026-08-20,
  *"Retire frozen orchestration history from live tree"*). It survives at the evidence tag
  `evidence/prepublication-2026-08-20-0b329e8a`.

| part | decided | done | where it stands |
|---|---|---|---|
| (a) | yes | `1cd0dc4dd`, 2026-08-14: zero GPU, read outside Leg F's scope with his words quoted | `VALIDATION_LEDGER.md` VL130 and VL131, PROVISIONAL, n=5 terminal: *"`k = 1` is defensible on the bins that carry the spectrum"* |
| (b) | yes | not run | OI-22's own next action: *"Run an independent per-block order/alignment proof against the final NPZ (or source ROOT)"*. OI-22 is DEFERRED 2026-10-29 until PET full-event input is used for publication again ([`RECORD-20261029-close-items-defer-pet-rows.md`](RECORD-20261029-close-items-defer-pet-rows.md)) |
| (c) | yes | job `56975592`, 2026-08-14; bundle `355671875` | `state/oi120c-loader-purity-perturbation-56975592.{json,txt}`. Corrected verdict: *"NO TRUTH LEAKAGE DEMONSTRATED on 3 of 4 truth perturbations"*. The headline `LEAKAGE` was a sentinel bug (`BEN-290`, `KNOWN_ISSUES` 49, FIXED 2026-08-14). The VOID arm P4 was retired by OI-124, CLOSED 2026-08-15. `CLAIMS.md` CLM-002 records both verdicts |

**The covering search for (b).** Search: `git grep -n -i 'alignment proof\|order proof'` over
`docs/orchestration/state/*` and `docs/orchestration/receipts/*`, and `git grep -n -l 'OI-120'` over the tree, @
`d6f79a85e`. No alignment receipt was found. So (b) is decided and not done, and OI-22 already carries the doing.
<!-- absence-ok: the search and sha are named in this paragraph -->

## 3. The proposal

**Retire OI-120.** Its terminal condition is the three decisions, and Joseph made all three on 2026-08-14. Its
next-action cell, *"QUEUE RATIONALE EXPIRED 2026-08-14 … run neither until Gate 5 drains"*, describes a queue that
drained the same day. Nothing in it waits on Joseph.

**What moves, and what does not.**
- (b)'s work stays with OI-22, which names it, and under OI-22's deferral trigger. Retiring OI-120 removes no route to
  it.
- (a)'s and (c)'s results stay where they are: VL130/VL131 and CLM-002, with their own PROVISIONAL and scope labels.
  This record changes neither.

**Dependency check.** Search: `git grep -n -l 'OI-120'` @ `d6f79a85e`. The hits are:
- the three receipts or probes for (c), and `test_probe_oi120c_verdict.py`;
- `test_loader_ordering_reco_before_truth_weight.py` and `test_receipt_verdict_is_not_the_superseded_one.py`;
- `KNOWN_ISSUES.md` 49, `VALIDATION_LEDGER.md` VL130/131, `CLAIMS.md` CLM-002;
- the `FINDINGS.md` id block `290-299`;
- `HANDOFF-20260815-0455Z.md`, and a repair-11 verdict JSON.

Each is history of (a) or (c), or a test pinned to (c)'s receipt. None routes open work to OI-120.

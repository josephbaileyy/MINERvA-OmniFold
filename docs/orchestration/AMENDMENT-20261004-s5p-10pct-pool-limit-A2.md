# s5p (`OI-193`): owner amendment A2 — the 10% pool limit applies at creation and enlargement (2026-10-04)

**CITABLE FOR:**
- the owner's explicit amendment of how the authorization's 10% pool limit applies to s5p, verbatim;
- the recorded operands at the pool's creation and at its 2026-10-04 enlargement.

**NOT CITABLE FOR:** any additional hours; the amendment authorizes none. It is not a scientific criterion either.
It resolves `CLARIFICATION-20261004-s5p-10pct-pool-limit.md`.

## 1. The amendment (Joseph, verbatim; given in the campaign session on 2026-10-04)

> I adopt A2 as an explicit amendment for s5p: the 10% pool limit applies whenever a pool is created or enlarged.
> Compare the pool's unspent, unreserved remainder—pool minus charges and open reservations—with 10% of current
> uncommitted allocation after reservations. Record the operands at each creation or enlargement. The 2026-10-04
> enlargement satisfies this condition on the recorded measurement.
>
> Keep revision 7: production 234.647 CPU node-hours, verification/repair 68.287, and cumulative ceiling 376.52. This
> amendment authorizes no additional hours beyond revision 7.
>
> Continue through the frozen stopping procedure, terminal evaluation, robustness labels, missing-seed sensitivity,
> and independent verification. My priority remains the strongest defensible scientific conclusions. If an updated
> forecast threatens completion or required verification, flag it before the budget binds with a costed extension
> and the specific scientific consequence. Further increases require my decision.

It amends, for s5p only, how this sentence is applied: "Each new pool is also capped at 10% of current uncommitted
allocation after reservations." The sentence is in authorization §1 (the 2026-09-26 `/goal` text) and in handoff
lines 105–106. Those records are not edited.

## 2. Recorded operands (CPU, billed node-hours)

| event | pool | charges plus open reservations | unspent, unreserved remainder | uncommitted allocation after reservations | 10% of it | satisfied |
|---|---:|---:|---:|---:|---:|---|
| creation, 2026-09-26T16:04Z (authorization §4) | 310.184 | 0.0 | **310.184** | 20,000 − 16,583.7 − 0.0 = 3,416.3 | **341.63** | yes |
| enlargement, 2026-10-04T04:41Z (revision 7) | 341.434 | 262.619 − 35.086 = 227.533 | **113.901** | 20,000 − 16,817.7 − 32.75 = 3,149.55 | **314.96** | yes |

**Sources:**
- **Creation:** `state/s5p/allocation-measurement-20260926T1604Z.txt` and authorization §4.
- **Enlargement:**
  - allocation: `state/s5p/transition-r3/allocation-measurement-20261004T0441Z.txt`;
  - the pool's charges: the meter's `envelope_charged_node_hours` (262.619), minus prior charges (35.086);
  - the meter receipt: `meter-measure-transition-r3-after-rebind-20261004T0446Z.json`, in the namespace.

The 32.75 open reservations are counted on both sides: in the pool's charges, through the meter's charged figure, and
in the allocation's reservations. That is consistent with the amendment's "pool minus charges and open reservations"
and "after reservations".

**GPU:** unchanged since creation (114.904 pool, measured at creation against 5,824.26). No GPU enlargement has
occurred.

## 3. Unchanged

- **Budget revision 7,** as the owner decided: production 234.647, verification/repair 68.287 (20%), pool 341.434,
  cumulative CPU ceiling 376.52. GPU, concurrency and every scientific criterion are also unchanged.
- **`budget.json`'s `binding` text** still names the increment comparison (31.25 ≤ 314.96). That file is
  hash-bound in the ledger and is not edited for wording. This amendment governs the reading, and its §2 records the
  operands that A2 requires.
- **Further increases** require the owner's decision. Any future enlargement must record the §2 operands for that
  event.

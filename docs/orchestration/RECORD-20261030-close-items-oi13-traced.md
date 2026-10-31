# RECORD — OI-13 traced: the retired-bar self-report is a catalogued WONTFIX, and the gate already reads the adopted bar (2026-10-30)

**By** the close-items session, on the director's order of 2026-10-30. Read-only, and local only: no cluster output was
read, and none was needed.

**CITABLE FOR:** what governs OI-13's question at `d6f79a85e`, and the graded report's recovery against both bars.

**NOT CITABLE FOR:**
- a Gate-4 verdict. No validator was run here;
- any PET result beyond the one committed report field read in §2.

**PROPOSES:** retiring OI-13 (§3). The register is not changed here; the ruling is the director's.

## 1. What the row asks

OI-13 is `WAITING-USER`, owner *"PET Gate-4 / Joseph"*, dated 2026-08-12.
- Blocker: *"Job 56381674 passed the adopted bar, but its self-report uses the retired bar."*
- Next action: *"Decide whether to re-issue Gate-4 against the adopted 0.4945824 criterion."*

## 2. What already answers it

**The self-report defect is catalogued, and was deliberately not fixed.**
- `KNOWN_ISSUES.md` row 40, `WONTFIX`: *"Powered-closure reports compute recovery_criteria_met against the retired bar
  rather than the authoritative Gate-4 criterion."* It routes to the superseded-value index.
- The entry's full text, before the 2026-08-12 compaction (`1f714b7fe^:KNOWN_ISSUES.md`, the section headed *"The
  powered closure's `recovery_criteria_met` is computed against the RETIRED bar"*) names the authority:
  *"`validate_pet_nominal_gate4.check_powered_closure`, which reads `FROZEN["powered_closure"]["residual_over_gap_max"]`
  — the adopted value … The closure's flag is a self-report and is not the gate."*
- It also says why it is not fixed: *"Editing a threshold inside a closure to make a check pass is the prohibited act
  regardless of justification, and it is unnecessary because the validator already governs."*
- `INDEX-retracted-and-superseded-values.md:92` lists the field for every `POWERED_CLOSURE_*` report, the graded one
  included: *"A self-report, never the gate"*. Row 95 records the retirement of the `0.80` bar, citing CLM-012.

**The graded report against both bars.** This was read locally from the committed
`nd-unfolding/pet/powered_closure/POWERED_CLOSURE_REPORT.slurm-56381674.json`:
- `metrics.recovery` = `0.5468534725868`;
- `recovery_criteria_met` = `False`.

So it fails the retired `0.80` and passes the adopted `0.4945824`, as the row and KI-40 both say.

**PET is not on the publication path.** `AGENTS.md:17`: *"PET is diagnostic and method-development, not a publication
uncertainty"*, in the front door since `38e876bfe` (2026-08-20). Batch B of 2026-10-29 deferred twelve PET-dependent
rows on that ground ([`RECORD-20261029-close-items-defer-pet-rows.md`](RECORD-20261029-close-items-defer-pet-rows.md)).

**What was not found.** There is no committed validator receipt for `56381674` itself. Search: `git grep -l
'check_powered_closure'` intersected with `git grep -l '56381674'` @ `d6f79a85e`. It returns only `CLAIM-CLM-012.md` and
`analyze_powered_closure_budget_probe.py`, and neither records a validator verdict for that job. A validator PASS is on
record for the later annealed run `56552326`: CLM-012 residual (viii), *"recovery `0.5126032761517403` against the
adopted threshold `0.49458240000000003`"*.
<!-- absence-ok: the search and sha are named in this paragraph -->

## 3. The proposal

**Retire OI-13.** The re-issue it asks about takes one of two forms, and both are already settled:
- **Re-writing the closure's report** would mean editing its threshold. KI-40 calls that *"the prohibited act"* and
  leaves it `WONTFIX`.
- **Re-grading Gate-4 against the adopted bar** is what the gate already does. The validator reads the adopted value,
  and the report's raw recovery passes it.

Neither is on a publication path while PET is diagnostic.

**The alternative,** if the director prefers to keep a question open: defer OI-13 with the batch-B trigger, *"PET
full-event work resuming toward publication"*. A validator run on `56381674`'s artifact would then be the act. That
needs the cluster and is not proposed here.

**Dependency check.** Search: `git grep -n -E 'OI-13([^0-9]|$)'` over the tree @ `d6f79a85e`, excluding `OPEN_ITEMS.md`
and the generated views. It finds one route: `PUBLICATION-READINESS-20260822.md` PR-J9 (`:421-426`) lists OI-13 among
the items *"Standing, unanswered, and each is his"*, as *"re-issue Gate 4 against the adopted criterion — **PET, so
off the path**"*. If OI-13 retires, this record answers that clause, beside the document, which is not edited. PR-J9's
other items are untouched.

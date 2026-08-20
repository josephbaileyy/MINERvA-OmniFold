# RULING 2026-08-20 (lane C) — `STAMP_COVERAGE` is a claim about a FILE; the class table is a claim about an ARTIFACT

**Requested by the mediator, who was wrong about the mechanism and right about one of the two halves.**
Read `docs/orchestration/pending/README-20260819-remedy-A-adopt.md` and
`HANDOFF-20260819-lane-b-member-axis.md` §4 first. This ruling settles what the tables must say once
remedy (A) lands as the unpinned wrapper of `DETERMINATION-20260818-lanec-anchor-recompute-and-lateral-in-g1.md`
§25, and it AMENDS the "same commit" instruction those two documents carry.

## 0. The question, and the mediator's error

Both prior documents say `ADOPTED_UTHROW`'s commented key block **and**
`STAMP_COVERAGE["adopt_unified_5d.py"]["stamps"]` flip in the wrapper's commit. The mediator argued both
flips are now wrong, on the ground that flipping `STAMP_COVERAGE` would make
`identity_is_checkable("adopted_uthrow.root")` return `True` on the strength of a writer that stamps nothing.

**That mechanism does not exist.** `identity_is_checkable` reads `ARTIFACTS`, never `STAMP_COVERAGE` —
`nd-unfolding/mii_root_payload_classes.py:431-432`. So the instruction is **half right, and the half the
mediator attacked is not the half that is wrong.**

## 1. What each table is predicated of — determined from code, not prose

**`ARTIFACTS` / `ADOPTED_UTHROW` is predicated of the ARTIFACT, and its values are REQUIREMENTS.**
`compare()` makes the table the domain of requirement explicitly: `:503` `table_keys = set(ARTIFACTS.get(artifact, {}))`,
`:504` iterates `table_keys | archive_keys | member_keys`, and the comment at `:496-502` states why —
*"The union of two files cannot express a requirement, because a requirement is about what SHOULD be there.
The table is the domain."* A classified `PROVENANCE` key absent from the member file is inadmissible, `:514-518`.

**`STAMP_COVERAGE` is predicated of the WRITER FILE, and the proof is that a test opens the key as a path.**
`:350` keys it by filename; `nd-unfolding/tests/test_uq_remediation.py:2412-2424` does `src = (ND / name).read_text()`
(`ND` at `:15`) and asserts the bytes mention an identity key and `TParameter`.
Measured: `grep -c est_seed_offset nd-unfolding/adopt_unified_5d.py` → **0**.

## 2. The README's hazard is real but overstated: the class-block flip fails CLOSED

With the keys classified and the artifact carrying none, `anchor_identity` returns
*"est_seed_offset_declared ABSENT -- an absent stamp is not a weak yes, it is a no"* (`:448-450`), `compare()`
`:514` emits `inadmissible`, and `mii_anchor_comparator.py:581` makes any identity problem a `FAIL`.
**So an early flip costs an unavoidable FAIL, not a gate certifying a stamp that is not there.**

## 3. Consumers, and the search that covers them

`grep -rn "STAMP_COVERAGE\|identity_is_checkable\|writers_without_identity_stamps\|ADOPTED_UTHROW\|IDENTITY_KEYS\|ARTIFACTS"`
over the repo across `*.py,*.sh,*.md,*.tsv,*.json`, excluding `.git/` and the preserved `PENDING-*.patch`.
**Namespace not covered: `.ipynb`, `.yaml`, `.cfg`, extensionless scripts.** `ARTIFACTS` also matches unrelated
`ENDPOINT_ARTIFACTS` / `GATE5_TRAINING_ARTIFACTS_PASS`, discarded by inspection.

- `STAMP_COVERAGE` — **one** executable consumer, `mii_root_payload_classes.py:388`. All else is tests or prose.
- `identity_is_checkable` — **one**, `mii_anchor_comparator.py:518`.
- `ARTIFACTS` — `mii_root_payload_classes.py:471, 503`; `mii_anchor_comparator.py:485, 595`.

**A REAL DEFECT, PROSE ONLY, AND IT IS WHERE THE MEDIATOR'S CONFUSION CAME FROM.**
`identity_is_checkable`'s docstring `:420-423` asks *"Does this artifact's **writer** stamp identity at all?"*
and cites `STAMP_COVERAGE`, while its body reads `ARTIFACTS`; `mii_anchor_comparator.py:525` prints
*"this **writer** stamps no identity key (STAMP_COVERAGE)"* from a branch controlled by the artifact table.
Today the two readings agree so nothing fails. **After the wrapper they name different files**, which is why
this must be corrected in the wrapper's commit rather than filed for later.

## 4. The pinning tests — and one of them ALREADY covered the defect

- `:2382` `test_STAMP_COVERAGE_records_a_CAPABILITY_and_a_MECHANISM_not_a_TALLY` — schema shape only, rule-derived, blind to this.
- `:2398-2410` `test_remedy_A_HAS_REACHED_EVERY_WRITER` — rule-derived. Cannot detect a false flip; only makes it deliberate.
- **`:2412-2424` `test_each_writer_that_CLAIMS_to_stamp_ACTUALLY_MENTIONS_an_identity_key` IS the counterexample.**
  Built from the **PRODUCER** — the writer's own bytes — so a flip of adopt to `True` fails immediately.
  **The mediator's implicit claim that no test could catch this is wrong**, and the reason is one this repo
  already knows: build the fixture from the producer, not from the rule.

**What nothing covers:** that `STAMP_COVERAGE`'s keys are files that exist, and that a writer with
`stamps: False` has a covering wrapper. That is the gap the wrapper opens.

## 5. RULED

**(a) `ADOPTED_UTHROW`'s commented key block (`:230-234`) FLIPS IN THE WRAPPER COMMIT.** B's original
instruction stands for this half; the mediator's objection is **overruled**. Include `hDiagCombinedOld`
**only if the wrapper actually writes it**; otherwise `:234` stays commented.

**(b) `STAMP_COVERAGE["adopt_unified_5d.py"]["stamps"]` STAYS `False` — forever, unless that file's bytes
change.** Flipping it is a false claim about a source file and `:2412` says so. Its `how` must be rewritten
from *BLOCKED on a BEN-106 receipt re-issue* to name the wrapper as the mechanism — which **also** falsifies
`assertIn("BLOCKED", ...)` and `assertIn("PENDING-20260819", ...)` at `:2408-2409`, so those pins are amended
in the same commit.

**(c) A NEW ROW FOR THE WRAPPER, AND A SCHEMA CHANGE — today's schema cannot express the arrangement.**
`writers_without_identity_stamps()` (`:385-388`) would return `["adopt_unified_5d.py"]` permanently while its
docstring says *"Empty is the goal and is not the state"*; under §25 empty is **unreachable by construction**.
Minimum: a wrapper row; `covered_by` on adopt's row; that function excluding live `covered_by`;
`len(STAMP_COVERAGE)` 5 → 6; and adopt's `products` must stop claiming sole authorship of the two 892 MB roots
— **two rows claiming identical `products` is the tell that the field conflates file and artifact.**
**The `covered_by` edge must be falsifiable from code or it is a definite description**: extend `:2412` so that
for each `covered_by` the covering file's source names both the identity keys and the covered writer.

**(d) CLUSTER EXECUTION IS NOT A PRECONDITION OF THE TABLE ROW.** `stamps` is a capability claim by the
table's own test name (`:2382`), verified from source (`:2412`). Measured precedent: `unfold_nd_omnifold_unbinned.py`
and `analyze_universes_5d.py` both flipped to `True` at `5afb7947`, and `RUNS.tsv` has **no** row for the
analyzer at all — those two `True`s are source-only and unexecuted. **Holding the wrapper to a standard the
four existing `True` rows do not meet would be exactly the asymmetric comparison this campaign keeps filing.**
What execution gates is C's verification of remedy (A) and the artifact's admission — not the table. The
wrapper's `how` must nonetheless carry `ROOT WRITE PATH CLUSTER-UNVERIFIED as of 2026-08-20`, because
capability and demonstration are different claims and the table is where a reader looks for the difference.

**(e) The prose defect of §3 is corrected in the same commit** — or the next reader repeats the mediator's
inference, which is now a live error rather than a harmless one.

## 6. Ordering

1. Wrapper + (a) + (b) + (c) + the coupled test edits are **ONE COMMIT**. B's rule *"a writer change and a
   table change are one change, in both directions"* survives; what changes is that the writer is a different
   file, so the coverage table gets a **new row, not a flipped one**.
2. Coupled edits that must be inside that commit: `test_uq_remediation.py:3071-3096` (both adopted roots move
   `BLOCKED` → `CHECKABLE`; the `set(ARTIFACTS)` equality and the `assertFalse` loop both break), `:2406-2409`, `:3872`.
3. **`:3872` is the dangerous one.** `assertFalse(identity_is_checkable("adopted_uthrow.root"))` sits in the test
   pinning the B1 pause, whose comment says *"the pause stands on that ground too and not only on C's
   verification."* The class-block flip **deletes one of the pause's two independent grounds** and must be
   replaced by an explicit assertion that the pause rests **solely** on `VERIFIED BY C`. Dropping it as
   incidental churn would be B lifting its own blocker as a side effect of a table edit — and **it reviews as a
   no-op diff, which is `BEN-485`'s named tell.**
4. Lane C's verification of remedy (A) comes **after** the wrapper commit and is not unblocked by any of the above.

**On the 41.44 GB, plainly: this ruling does not move it.** Nothing here verifies remedy (A), so B1 steps 4-5's
expiry (`HANDOFF-20260819-lane-b-member-axis.md:64`) is untouched and `BEN-485`(b)'s composition stands as filed.
`FINDINGS.md:504` read to the END of the row: its 2026-08-19 amendment adds a third instance and reverses
nothing on the intermediate. The code pin is live at `nd-unfolding/sbatch_finalize_5d_bkgaware_gpu.sh:172`
(`DETERMINATION...:2087` cites `:164` — stale line number, same line, no consequence).

## 7. Verified vs assumed

**Verified by reading code this turn:** `identity_is_checkable` reads `ARTIFACTS` (`:431`); `compare()` treats the
class table as the requirement domain and fails closed on an absent `PROVENANCE` key (`:503-518`);
`anchor_identity` fails closed (`:448`); identity problems force `FAIL` (`mii_anchor_comparator.py:581`);
`STAMP_COVERAGE` keys are opened as source paths (`test_uq_remediation.py:2412`, `:15`);
`adopt_unified_5d.py` contains `est_seed_offset` **0** times and already writes `f"upstream_{key}"` /
`f"{key}_checked"` TParameters at `:202-204`; the two `True` flips landed at `5afb7947` with no `RUNS.tsv` row
for the analyzer; §25 read `:2132-2215` including `25c`; `BEN-485` read to end of row.

**Assumed / NOT verified:** that the wrapper's filename lives in `nd-unfolding/` (required by `ND / name` at
`:2412` — elsewhere and that test breaks on the new row); that the suite passes at `HEAD` (**not run** — read-only
lane); that ROOT accepts new `TParameter` keys on `UPDATE` (inherited from §25's precondition table, not
re-measured, and unmeasurable locally since `import ROOT` fails on this host).

## 8. Open, and one of these will red the gate

1. Does the wrapper write `hDiagCombinedOld`? If not, does `:234`'s classification stay commented — an
   unresolved coupling between (a) and §11g's `sqrt_tr_old` recomputability.
2. Nothing enforces that `STAMP_COVERAGE`'s keys are existing files, so a typo in the new row silently
   disappears from `writers_without_identity_stamps()`.
3. **`upstream_estimator_seed_g1` / `_g2` appear in NEITHER `RECOMPUTABILITY` NOR `ARCHIVE_KEY_MAP`, and
   `compare()` `:522-526` FAILs on a member key absent from the archive with no map row. That will red the gate
   on the wrapper's first real product, for a reason that has nothing to do with the wrapper, and nobody has
   enumerated it.**

# DETERMINATION — causes 3 and 4: the shared leg is now MEASURED, and it does not discharge either cause

**Lane E, 2026-08-17.** Predeclared at `9c03c67`
([`PREDECLARE-20260817-candidate-stamp-receipt-causes-3-4.md`](PREDECLARE-20260817-candidate-stamp-receipt-causes-3-4.md)),
measured against that commit, written after. **Adopts nothing. `docs/analysis-note/` untouched, not one
character; `values.tex` untouched; no ROOT modified; no covariance rebuilt.**

---

## THE ONE PARAGRAPH

**The shared edit was never the missing thing.** `MAP-20260817` says causes 3 and 4 are discharged by
*"`BEN-106`'s stamp propagation, one edit, which closes this leg for 2, 3 and 4 at once"*. That edit
**landed on 2026-08-11** (`adopt_unified_5d.py:180-223`, implementation commit `5856eeb`) and the
candidate arms were built with it on 2026-08-12. What was missing was not an edit but a **read**: no
committed artifact had ever opened those arms and looked. I opened them. **Branch S1: both arms carry all
six self-checked stamps and all three `upstream_*` values, matching every predeclared number digit for
digit, with both negative controls coming back with every stamp absent.**

**And that closes one leg of four.** **DENY on the framing: causes 3 and 4 do not share a single
sufficient edit.** `P` is now MET for both, for the candidate. Cause 4 remains OPEN on `M`, which
`CRITERIA` §2 records as UNRESOLVED *"for a stated reason"* that no stamp read touches. Cause 3's `M` is
graded **two different ways inside one document** and this measurement does not settle which. Both
remaining gaps are judgements, both are named in §5, and **neither is taken here.**

---

## 1. What was measured

Reader: `nd-unfolding/receipt_candidate_stamps_5d.py`, sha256
`1628c76b3008780b7dbe7427c2b390f5119a90bc0a62df02e7c4b9f0be19d2f7` — **verified equal on both sides of
the copy** before running, because the cluster tree is at `5fb7e38` and this checkout is at `00e794e`.
Run on Perlmutter `login08`, 2026-08-17T05:5xZ, `rc=0`, whole stream to a file and filtered on read
(BEN-026). `stderr` is the nine known duplicate-class `TInterpreter::ReadRootmapFile` warnings, the same
classification `ben106-stamp-verify-complete-56695424.json` records. Receipt:
`nd-unfolding/uq_5d/receipt_candidate_stamps_5d.json`.

**Subjects — the two arms named by the 2026-08-12 cause-2 discharge:**

| | A1 mean-centered | A2 CV-centered |
|---|---|---|
| path | `…/readopt_20260811_footing/stamped_bkgaware_meancentered_20260812.root` | `…_cvcentered_20260812.root` |
| size | `892170881` ✓ | `892232198` ✓ |
| sha256 | `4f168e83…` ✓ **matches the committed hash receipt** | `dbcd5359…` ✓ |
| `centering_convention` | `mean-centered` ✓ | `cv-centered` ✓ |
| `n_throws_checked` / `upstream_n_throws` | `1` / `160` ✓ | `1` / `160` ✓ |
| `joint_mean_shift_norm_checked` / `upstream_…` | `1` / `1.878696733368378e-38` ✓ | same ✓ |
| `fixed_seed_null_norm_checked` / `upstream_…` | `1` / `5.8223488501140625e-50` ✓ | same ✓ |
| `uthrow_source` / `combined_source` | present, as launched ✓ | present ✓ |

**Ingredients, so the numbers can contradict each other** (`CONVENTION-receipt-ingredients.md`, BEN-077):

| | `sqrt_tr_old` | `sqrt_tr_new` | ratio | ledger row |
|---|---|---|---|---|
| A1 | `4.357790406860002e-38` | `5.269625166386846e-38` | **`1.2092424541784845`** | `VALIDATION_LEDGER.md:187-190` **A1 ×1.209** ✓ |
| A2 | `4.357790406860002e-38` | `5.67431104455928e-38` | **`1.3021073789200188`** | **A2 ×1.302** ✓ |

The ratio is *derived from the two operands in the same receipt*, not reported alongside them, so a
fabricated stamp block would have to be arithmetically consistent with the ledger to survive. It is.

**Cause 4's criterion, with its tolerance and the tolerance's derivation**, because the criterion is
literally *"key present, and ≤ tol, with tol and its source both stated"*:

    upstream_fixed_seed_null_norm = 5.8223488501140625e-50
    tol                           = 1e-12
    ratio_to_tol                  = 5.82e-38          (37 orders of margin)
    tol source: unified_throw_cov.py:445
                tol = 1e-12 * max(||base||, 1.0)
                base = reported 5D cross-section, 10694 bins at ~1e-38, so ||base|| ~ 1e-36 << 1,
                the max() binds, and the tolerance is an ABSOLUTE floor of 1e-12.

**That derivation is not decoration and it is condition-dependent** — in the synthetic unit test
`||base|| = 2.236 > 1` and the printed tolerance is `2.236e-12`, i.e. the *relative* branch. A reader who
carried "tol = 1e-12" from the test to the product would be right by accident.

**Controls.**

* **Positive** — `STAMPTEST2_bkgaware_meancentered.root` reproduced
  `ben106-stamp-verify-complete-56695424.json` exactly, and its sha256
  `2465e3e95cbfa148e4939a18cdabb71e2a14b2ed879f420d8e555d952bb14312` **is recorded here for the first
  time**; the 08-11 receipt hashed nothing. Its `sqrt_tr_new` is `5.269625166386846e-38` — **bit-identical
  to A1's**, so the regenerated adoption-named arm reproduces the test product to the last digit.
* **Negative, and load-bearing** — the two July products the note quotes came back with **all nine
  propagation stamps ABSENT**, as required, in the same run, by the same reader:
  `…_bkgaware_uthrow.root` (`8feb8ba4…`, `892195314`, `sqrt_tr_new 5.807716496958672e-38` →
  `\gbdtFiveAdoptTrace` **5.81e-38**) and `…_uthrow_cvcentered.root` (`b4edc665…`, `892241032`,
  `6.236702327843976e-38` → `\gbdtFiveCVTrace` **6.24e-38**).
  **This is the observation that would have shown the leg undischarged, coming out the other way** — and
  it independently confirms `CRITERIA` §1's identification of X by measurement rather than by citation.
  The branch logic makes S5 dominate S1: had a control leaked a stamp, the subject result would have been
  recorded VOID even with the subjects passing.

## 2. The correction this makes to the record — the P leg was cited to a file that adopts nothing

`CRITERIA` §3 grades `P` **MET** for causes 2, 3 and 4 citing values *"read back **from the adopted
product** (job `56695424`)"*, and `MAP-20260817` carries that forward. Measured:

```
ben106-stamp-verify-complete-56695424.json  .artifact.path
  → …/STAMPTEST2_bkgaware_meancentered.root      892170857 bytes
  .scope.test_product_adopted = false
  (…-active-…json)  .test_product_only = true    .adopts_nothing = true
```

**"The adopted product" is a file whose own receipt says three times that it adopts nothing**, it is
`892170857` bytes against A1's `892170881`, and it is **mean-centered only — so the CV-centered arm had
never been stamp-verified by anything at all.**

**This is `CRITERIA`'s own rule breaking on `CRITERIA`.** Its cause-2 box refuses exactly this
substitution — *"Declaring on A1/A2 while citing stamps verified on a different file is the
invented-after-the-fact closure this document exists to prevent"* — and cause 2 was therefore re-cited to
regenerated, adoption-named arms. **Causes 3 and 4 were not re-cited, and nothing marked that they
hadn't been.** §0's own (cause × artifact) rule was applied once and then not applied to the two causes
sitting in the same table row-block. As of this receipt they are re-cited to the arms.

## 3. Why job exit 0 was not already the evidence — a fail-closed guard that does not cover the values

`adopt_unified_5d.py:215-219` fails closed on **six** keys:

    fixed_seed_null_norm_checked, joint_mean_shift_norm_checked, n_throws_checked,
    centering_convention, uthrow_source, combined_source

**The three `upstream_*` VALUE parameters are not in that list.** And the very next statement, `:220-223`,
prints:

    [adopt5d] provenance stamped AND read back: centering=… upstream={'fixed_seed_null_norm': …,
                                                'joint_mean_shift_norm': …, 'n_throws': 160}

where that `upstream` dict is the **plain-Python capture from `:103-106`** — it was never read back out of
anything. **So the log line prints three values it did not verify, under a label that says it did.** The
committed `STAMPED_HASH_RECEIPT.slurm-56720356.json` then defers to that log (`verdict:
HASHES_COMPLETE_READ_STDOUT_FOR_ARM_VALUES`), and the log is on purgeable scratch and is committed nowhere.

**No live defect follows** — I read the values out of both arms and they are correct, and the plausible
ROOT failure mode (BEN-112's read-only current directory) kills all nine writes together and *is* caught.
The point is narrower and it is about evidence: **the chain "launcher pinned → exit 0 → log line" never
attested the three numbers the P leg of causes 3 and 4 is about.** Reading the artifact was necessary,
not ceremonial. This is BEN-112's own lesson — *"a print is not a check"* — recurring **inside the fix
for BEN-112**, one level down: the repair verifies six keys and prints three it does not.

**A second, smaller gap in the same guard, recorded rather than fixed:** `*_checked` is written
unconditionally and may legitimately be `0`, but the guard tests only that the key *exists*. A product
built from an unstamped throw ROOT would satisfy the guard, print the success line, and carry
`checked = 0`. That is correct by design — absence must be readable — but it means **the consumer must
fail closed on `checked == 0`, and a citation to the log line cannot.** Ours read `1` on all three.

## 4. The T legs, power-tested independently rather than inherited

`CRITERIA` grades `T` **MET** for both causes, citing mutations `N5` and `N6`. Re-derived here rather
than read off that grade — a test that cannot fail is not a test (BEN-344). Isolated worktree, one
mutation at a time, restored and verified `git diff HEAD` empty after each.

| # | mutation | file:line at `00e794e` | result |
|---|---|---|---|
| **N5** | disable mixed-seed rejection (`if False and …`) | `unified_throw_cov.py:417` | `test_cause3_mixed_seed_slabs_are_rejected_and_a_single_seed_is_accepted` **FAILED** — *"SystemExit not raised"*; both cause-4 tests stayed green |
| **N6** | drop `"fixed_seed_null_checked"` from `do_combine`'s return | `unified_throw_cov.py:509` | `test_cause4_null_is_CHECKED_flag_is_present_in_both_directions` **FAILED** — *"'fixed_seed_null_checked' not found in {…}"*; cause-3 test stayed green |
| **N7** | reintroduce a scalar jitter subtraction (`st_uni = st_uni - jitter_floor`) | `unified_throw_cov.py:435` | `test_cause4_no_jitter_subtraction_survives_on_the_combine_path` **FAILED** — *"Lists differ: ['st_uni - jitter_floor'] != []"* |

**Each mutation failed exactly one test and left the others green**, which is the part that matters: a
guard that fails on everything is not discriminating. Restored, full suite **35/35 pass**.

**One citation does not resolve.** `CRITERIA` §2 cause 3's `C` leg, and
`receipt_construction_contract_5d.py`'s docstring, both say *"`do_combine` rejects mixed-seed slabs
(`unified_throw_cov.py:330-331, 370-371`)"*. At `00e794e` those four lines are
`if "seed" in z.files: slab_seeds.add(int(z["seed"]))` — they **collect** seeds. The rejection is at
**`417-419`**, which N5 confirms by breaking the test when mutated. Whether the citation was right when
written and drifted, or was always off, I did not determine; **at HEAD it points at the wrong lines**, and
the `C` leg is graded MET on it. The claim is true; its address is not.

## 5. What remains, named and not taken

> **POINTER, added 2026-08-17 by lane C — one of the three options this section routes for cause 4 is NOT
> AVAILABLE under the criteria as written, and it reads live below.** `CRITERIA` §3:246 defines the entire
> leg vocabulary — *"Legs are graded **MET / OPEN / UNRESOLVED**. A cause is discharged only with four
> METs"* — and **`INAPPLICABLE` is defined zero times anywhere in that document.** So the middle option
> below, *"cause 4 is discharged on three legs with `M` declared inapplicable"*, **cannot be exercised**: a
> leg graded `INAPPLICABLE` is none of the three, and *"only with four METs"* means a cause carrying one
> cannot discharge, however sound the reasoning for its inapplicability.
>
> **Ruled 2026-08-17 by the mediator with lane C agreeing** (Joseph's two-session rule), and **deliberately
> the unfavourable branch**: §3 as written is operative. The conservative reading is the status quo, so
> adopting it changes nothing — whereas admitting a fourth grade would retroactively make discharge easier
> for causes already graded under the three. **The definition question is left open on purpose** and nothing
> waits on it; if the fourth grade is to exist it should be a deliberate criterion change, not a side effect
> of a cell that wanted to move.
>
> **This does not touch the other two options, or any grade in this document.** Section text left as
> written, per this repo's convention. Gap and reasoning:
> [`SCOREBOARD-20260817-quarantine-seven-causes.md`](SCOREBOARD-20260817-quarantine-seven-causes.md) §7b.

**Cause 3** — `C` MET, **`P` MET (this receipt)**, `T` MET (N5, re-derived), `M` **contradicted inside one
document**:

* `CRITERIA` §2 splits `M` into two questions. **M(i)**, the fixed-seed null, is measured on both
  products (`1.9706e-50` pre-J28, `5.8223e-50` J28) and I re-read the J28 value off both candidate arms.
  **M(ii)** — *"the magnitude of what varying seeds would have contributed"*, which §2 says *"is what the
  criterion is about"* — is flagged **UNRESOLVED**, because the available number (`\gbdtAiEstTrace`
  `1.306e-39`, 12 seeds) is held by the ledger to be *"an auxiliary robustness check … not part of this
  candidate budget"*, so **"using it as the M leg is a decision, not a lookup."**
* `CRITERIA` §3's table grades `M` **MET**, citing only the null — i.e. M(i).
* **These are not the same grade and both are in `CRITERIA-20260811`.** `MAP-20260817` inherited §3's.
  **The judgement — does `\gbdtAiEstTrace` serve as M(ii), or does cause 3 need its own measurement? — is
  the whole remaining distance on cause 3, and it is not mine.**

**Cause 4** — `C` MET, **`P` MET (this receipt)**, `T` MET (N6 and N7, re-derived), `M` **UNRESOLVED and
expected to stay so**:

* §2's reason is not that nobody has measured it; it is that **the counterfactual has no surviving
  specification.** *"The retired procedure subtracted a scalar, and no committed document records which
  scalar or how it was estimated. Constructing one now and calling the difference a measurement would be
  precisely the 'success condition invented after the fact' this document exists to prevent."*
* What exists instead is a **bound** — <0.1% of the sqrt-trace, three orders below the J28 correction —
  explicitly labelled *"a bound is not the M leg."*
* **The judgement is whether that bound may stand in for `M`, or whether cause 4 is discharged on three
  legs with `M` declared inapplicable, or whether it stays OPEN indefinitely.** A stamp read cannot
  reach it. **Routed.**

**Neither judgement is a physics adjudication I was asked for, and I have made neither.**

## 6. Consequence for `MAP-20260817` §2, stated so the map's owner can correct its own row

The map's cause-3 and cause-4 rows say the discharge is *"`BEN-106`'s stamp propagation, one edit … Already
done for the candidate."* Three amendments, all measured:

1. **The edit was already committed on 2026-08-11** and had been applied to the candidate on 08-12. The
   map reads as if an edit were pending; **nothing was pending except a read.**
2. **"Already done for the candidate" was true of `STAMPTEST2`, not of the candidate** — §2 above. It is
   true of the candidate as of this receipt.
3. **"One edit, which closes this leg for 2, 3 and 4 at once" is right about the LEG and wrong about the
   CAUSES.** It closes `P`. Cause 4 keeps an open `M` that no edit reaches, and cause 3 keeps a grading
   contradiction. **"Two of the six blockers, and neither needs cluster time" overstates what is
   available: what was available was one leg of each, and it is now taken.**

Cost, for whoever prices the rest: **one ROOT read, ~2 minutes on a login node, no batch job.**

## 7. Limits

* **Nothing is discharged here.** No cause moved from OPEN. `P` moved, for the candidate only.
* **Nothing about X.** Under §0's (cause × artifact) rule X is a different subject and predates stamping;
  it is replaced, not repaired. The negative controls measure X's state and change nothing about it.
* **The candidate is still not adopted**, and this receipt does not make it adoptable — cause 7 and
  `publication_gate_rejects_this` are untouched, and adoption is Joseph's.
* **I did not re-derive cause 5** (Session C's), cause 1, cause 6, or the two non-arithmetic rows in
  `PROCEDURE` §3.
* **The `STAMPED_HASH_RECEIPT` pins the launcher and not the implementation** (`sbatch_adopt_stamped_footing.sh`
  exports `LAUNCHER_SHA256` and nothing for `adopt_unified_5d.py`), where the `56695424` receipt pinned
  both. I noticed this and it is **now moot for the P leg**, because the stamps are read from the artifact
  rather than inferred from which code ran — but it is a real weakness in that receipt's schema and I have
  not fixed it.
* **`CRITERIA` and `MAP` are other lanes' documents and I did not rewrite their rows** — §2, §5 and §6
  are routed, with a one-line pointer added beside `CRITERIA` §3's table so the correction is reachable
  from the fact's canonical home rather than only from here.

# A guard that cannot tell a mention from a consumer — `OI-81` is not drift

**Filed 2026-08-15 by the propagation-correction lane** (`BEN-325`, block `320-329`). Subject item
`OI-81`. **The script is lane C's and was NOT edited** — `check_canonical_designation.py` was run read-only
and read. Answering the mediator's direct question: *is the RED real drift, or a fourth instance of the
guard-that-cannot-see pattern?*

## Verdict

**NOT real drift. Nothing in the guard's output indicates the protected artifact changed.** But it is not
pure noise either, and the distinction is the finding: **7 of the 20 unaccounted entries are code that
opens the path and genuinely needs a disposition; 13 are prose that merely mentions it. The guard fails
RED identically on both, so its verdict is uninformative in both directions.**

## 1. What it actually reports

`python3 nd-unfolding/pet/check_canonical_designation.py` → **exit 1**, `74 files, 216 namespace
occurrences, 54 inventory entries`, then **20 `UNACCOUNTED FILE` and 1 `COUNT DRIFT`.**

Classified by kind:

| kind | n | examples |
|---|---|---|
| **prose** — documents mentioning `fullevent_nominal/` | **13** | `OPEN_ITEMS-ARCHIVE-2026-08.md`, `AUTHORIZATION-20260813-gate4-estimator-disposition.md`, `FINDINGS-INDEX-ARCHIVE-2026-08.md`, `cluster-ignored-set-walk-20260812.tsv` (**65 occurrences**) |
| **code** — opens or asserts the path | **7** | `probe-vl100-foldforward-shape-20260814.py`, `probe-vl100-{nominal-residual-field,own-run-foldforward,shape-correction-scan}-20260815.py`, `sbatch_p5a_fullevent_nominal_extract.sh`, `test_closure_foldforward_recording.py`, `test_pet_diagnostic_artifact_identity_guards.py` |

**And the single enforced-count hit is the sharpest item in the report.** `COUNT DRIFT
annealed-nominal-complete-56563761.json [RECORD-FROZEN]: expected 1, found 2 (lines [63, 245])`. Line 245
reads:

> `"fullevent_nominal/ IS NOT TOUCHED. The 2026-08-08 baseline pet_fullevent_nominal_weights.npz
> (10,127,331 B) is the reference the predeclaration, CLM-012 and the shape-validation chain are …"`

**The guard's one hard signal fires on a sentence whose content is a reassurance that the namespace is not
touched.** The document that says *"not touched"* is what makes the guard say *"something changed."* That is
the whole defect in one line, and it is why the answer to "is this real drift" is no.

*(`OI-81`'s row cites lines `63/226`; they are now `63/245` — the receipt grew. `BEN-228`, in passing.)*

## 2. Credit where it is due — this guard avoided the trap that bit two other lanes

It would be easy to file this as careless. It is not. `check_canonical_designation.py:28-32` states:

> **`fullevent_nominal_annealed` contains `fullevent_nominal`**, so the DESTINATION directory matches any
> naive pattern for the source … The pattern therefore matches the namespace as a **PATH SEGMENT**.

**That is `BEN-311`'s sibling-directory trap, anticipated and closed by design** — the same trap that later
produced `BEN-311`/`BEN-312` in two other lanes. Its exemption vocabulary is keyed on *the property that
justifies the exemption rather than the label that accompanies it* (D's finding), and it splits
`RECORD-APPEND` from `RECORD-FROZEN` precisely so a frozen receipt cannot cry wolf. **This is a
well-constructed instrument with one structural flaw, not a sloppy one.**

## 3. The flaw: it requires hand-registration of file classes it has itself classified as accruing

`INVENTORY` is a **dict inside the script**, and `RECORD-APPEND`'s own definition is:

> *files designed to **ACCRUE** (run logs, `FINDINGS`, `OPEN_ITEMS`, `INDEX-*`, `FINDING-*`). Count
> UNENFORCED; **presence still enforced.***

So the script **knows** those files accrue, waives their counts, **and still requires each new one to be
hand-added.** In a repo where four lanes write `FINDING-*` files and receipts all day, that dict cannot
stay current. It is `BEN-228`'s canonical shape: **a hand-maintained index of a machine-derivable fact,
maintained by the party with least reason to reread it.**

**And the self-defeating part: 4 of the 20 unaccounted files are today's findings and receipts ABOUT this
very namespace** — `FINDING-20260815-a-restatement-is-not-a-second-measurement.md`,
`FINDING-20260815-the-quarantine-measured-a-different-run.md`,
`RECEIPT-vl100-shape-corrected-foldforward-20260815.json`, and the `probe-vl100-*` set. **Investigating the
namespace turns its own guard RED.** The guard penalises the documentation of its subject, so the more
carefully a lane works on this artifact the redder the safety argument under it looks.

*(`sbatch_p5a_fullevent_nominal_extract.sh` is unaccounted because **this lane** edited it this morning.
My own work contributed to the RED I was asked to diagnose.)*

## 4. Where it belongs in the family, and how it differs

Fourth instance today of an accounting that misreports what it can establish:

| | the accounting | what goes wrong |
|---|---|---|
| `BEN-321` | `applied_overrides` | override applied, **discarded**, still counted — so the "unused" warning cannot see it |
| `BEN-322` | `resolved` + `unresolvable` | role-keyed pins in **neither** cell; residue line reads as complete |
| `BEN-323` | `ERROR`/`COMPLETE`/`else` | failure to observe falls through to a **liveness claim** |
| **`BEN-325`** | `INVENTORY` presence | accounting is **complete** — every occurrence is reported — but **undifferentiated by kind**, so RED means "a document was written" and "a new consumer appeared" identically |

**The distinctive feature: unlike the other three, nothing here is hidden.** The report is exhaustive and
honest. The failure is that it is **unranked**, and an unranked exhaustive report of a namespace that 74
files mention is operationally the same as no report — which is why this one has been RED since the
designation rather than being fixed in an hour.

## 5. What would fix it — C's call, not proposed as a change here

**Do not close this by adding 20 entries to the dict.** That is the treadmill: it goes stale on the next
finding, and it is what has kept the guard RED.

**Classify by whether the occurrence is in code that opens the path or prose that mentions it.** That is
machine-derivable, and **the script already half-does it** with its line-level `NS-EXEMPT` classes (CLASS
1–4, pattern-literal vs reference). Concretely:

* **Drop the *presence* requirement for the classes `RECORD-APPEND` already names** — `FINDING-*`,
  `FINDINGS*`, `OPEN_ITEMS*`, `INDEX-*`, `*-ARCHIVE-*`, and `state/RECEIPT-*`. Requiring hand-registration
  of files the script has itself declared as accruing is self-defeating.
* **Keep presence enforced for `.py` / `.sh` / `tests/`** — those are the 7 that matter, and their
  dispositions are substantive. `probe-vl100-foldforward-shape-20260814.py:46` is the exact line
  `BEN-311`/`BEN-312` are about: it opens the **pre-anneal** sibling deliberately, so `STAYS-DIAG08` or
  `STAYS-PINNED` is a real decision about what that probe measures.
* **Keep `RECORD-FROZEN` count enforcement**, which is right in principle — but note it fired on prose, so
  a frozen receipt gaining a *sentence* is indistinguishable from one gaining a *pin*.

**Estimated cost: a predicate over the path suffix plus a disposition pass on 7 files.** No GPU. It needs
lane C, which `BEN-324` records as unreachable — so the *finding* is available read-only and the *fix* is
not.

## 6. What this does not establish

* **That the designation is safe.** This finding says the guard's RED is not evidence of drift; it does
  **not** audit the promoted artifact. Nobody has re-verified the annealed weights here, and `OI-81`'s
  underlying question — is the reference inventory complete in substance — is **untouched**: 7 files still
  lack dispositions and one of them reads the wrong arm.
* **That no drift exists anywhere.** Only what this guard reports was examined, and it reports occurrences
  of a path string, not artifact content. A byte change in the annealed weights would not appear here at
  all.
* **Which disposition each of the 7 deserves.** That is a decision about what each consumer should follow
  at a designation, and it belongs to the script's owner.

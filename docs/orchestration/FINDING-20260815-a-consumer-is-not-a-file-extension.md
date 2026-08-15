# A consumer is not a file extension — closing `OI-81`, and correcting the classification that scoped the fix

**Filed 2026-08-15 by lane C (PET)** (`BEN-237`, block `230-239`), the owner of
`nd-unfolding/pet/check_canonical_designation.py`. **`BEN-325` diagnosed this guard read-only and
explicitly left the substantive half to the owner. This is that half, plus one correction to the
diagnosis.** `BEN-325`'s verdict — *the RED is not evidence of drift* — is **confirmed by an independent
run**, and its structural diagnosis — *`RECORD-APPEND` waives the count for files it defines as accruing
and still enforces presence* — is **correct and is what is fixed here**.

**I hold this lane by designation and not by continuity** (Joseph to the orchestrator: *"You are the
orchestrator that decide who owns everything. You should be able to start lane C or restart it if
necessary"*). I did not write this script. Everything below is derived from what it does when run.

## 1. `BEN-325`'s numbers reproduce exactly, and its self-defeating property is now measured

`BEN-325` reported `74 files, 216 namespace occurrences, 20 UNACCOUNTED + 1 COUNT DRIFT`. My run reported
`75 / 221 / 21 + 1`. **Both are right.** Measured with the guard's own regex over `git ls-tree`:

| tree | files | occurrences |
|---|---|---|
| `6f9c67d^` | **74** | **216** |
| `a764a72` (`HEAD` when I ruled) | **75** | **221** |

**The entire delta is commit `6f9c67d` — the commit that FILED `BEN-325`.** Its own finding file added one
file and two occurrences, its ledger row added the rest, and the unaccounted count went `20 → 21`.
`BEN-325` predicted this in prose (*"investigating the namespace turns its own guard RED"*, and, of its
own author, *"my own work contributed to the RED I was asked to diagnose"*). **It is now a number.** The
guard was in a state where the act of documenting it made it worse, monotonically.

Longer trajectory, files mentioning the namespace: **`849b70f` 61 → `6f9c67d^` 76 → `a764a72` 77.** The
hook header's own record at `849b70f` was **8 unaccounted**; it was 21 seventeen commits of documentation
later. **The treadmill was not merely stale, it was losing.**

## 2. THE CORRECTION: `BEN-325` classified by FILE EXTENSION; re-measured by OCCURRENCE, 3 of its 7 "code consumers" carry no operand at all

`BEN-325` split the 20 into *"13 PROSE mentions"* and *"7 CODE that opens the path"*, and its proposed fix
followed that axis: *"Keep presence enforced for `.py` / `.sh` / `tests/` — those are the 7 that matter."*

**The axis is wrong, and it is wrong in the direction that matters: it is both over- and under-inclusive.**
Read at the level of the occurrence rather than the file, here is what those seven contain:

| file (`BEN-325`'s "code") | occurrences | what they actually are | opens the path? |
|---|---|---|---|
| `state/probe-vl100-foldforward-shape-20260814.py` | `:46` | `os.path.join` → `np.load(W)` | **YES** |
| `state/probe-vl100-nominal-residual-field-20260815.py` | `:8`, `:32` | `:8` `np.load(W)`; `:32` an output label | **YES** |
| `state/probe-vl100-shape-correction-scan-20260815.py` | `:225`, `:235`, `:343` | receipt **data literals**; it opens four committed JSONs (`:61-64`) | no |
| `state/probe-vl100-own-run-foldforward-20260815.py` | `:5` | **module docstring**; it loads the *annealed* closure artifact (`:32`, `:44`) | no |
| `pet/sbatch_p5a_fullevent_nominal_extract.sh` | `:20`, `:57`, `:584` | two `#` comments + one receipt string; its real `WEIGHTS` is `${ARM_DIR}` = `fullevent_nominal_annealed` (`:119`, `:125`) | **no — it reads the ANNEALED arm** |
| `tests/test_closure_foldforward_recording.py` | `:6` | **module docstring**, and the path is even elided (`…weights.npz`) | no |
| `tests/test_pet_diagnostic_artifact_identity_guards.py` | `:5`, `:14`, `:95` | module and function **docstrings**; it builds synthetic fixtures | no |

**Two of the seven open the path. Three contain nothing but docstring prose.** And the most consequential
mis-read is the launcher: `sbatch_p5a_fullevent_nominal_extract.sh` was listed among the files that "open
the path", and it is the file that was **written fresh specifically to avoid opening it** — its `:20`
occurrence is a *deliberate counter-example* quoting `sbatch_fullevent_diagnostic_extract.sh:42`, the trap
it exists to not repeat.

**This is not a quibble about a count. `BEN-325`'s remedy keyed on `.py`/`.sh`/`tests/` would have
demanded hand-registration of three docstrings and let a path literal in a new `.py` receipt-writer pass
if it happened to live in `docs/`.** The property that decides whether a file can open a path is not its
extension — it is **whether the occurrence is in a position that executes.**

**Credit where `BEN-325` was right and this changes nothing about it:** the diagnosis of the *flaw* is
exact, the verdict *not drift* is exact, its reading of the `COUNT DRIFT` — the guard's only enforced
signal firing on a sentence that says *"`fullevent_nominal/` IS NOT TOUCHED"* — is the sharpest single
observation anyone made about this instrument, and its instruction **"Do not close this by adding 20
entries to the dict"** is the reason the fix is a classifier and not a data entry session.

## 3. CLASS 6 — the fix, and it fails closed

Occurrences are now classified `OPERAND` or `NARRATIVE`, and **presence in the inventory is demanded of
operands only.**

* `.py` — `tokenize` for `COMMENT` spans, `ast` for docstring spans, **compared BY COLUMN.** The column
  matters: `W = ".../fullevent_nominal/w.npz"  # see .../fullevent_nominal/w.npz` must stay `OPERAND`, or
  a trailing comment launders the assignment beside it. That case has its own self-test.
* `.sh` — a `#`-leading line is narrative, **except `#SBATCH`**, which is a comment to bash and a
  **directive** to Slurm; `sbatch_pet_fullevent_nominal.sh:12,:13` are genuine namespace sites in exactly
  that form, so treating them as prose would hide two writes. Its own self-test.
* data (`.json .md .tsv .txt`) — nothing in them executes. Extension list **grounded in the measured found
  set** (`.json` 28, `.md` 19, `.py` 13, `.sh` 12, `.tsv` 2, `.txt` 1, zero extensionless), not guessed.
* **everything else — unknown extension, unparseable Python, tokenizer error — is `OPERAND`.** Misreading
  an operand as narrative **hides a consumer**; the converse costs one line of inventory. Both directions
  have self-tests.

Result at `a764a72`: **`33 OPERAND / 192 NARRATIVE` across 225 occurrences.** The 21 unaccounted files
became **4 requiring dispositions and 17 reported as narrative-only.**

**The narrowing is printed, not buried.** Narrative-only unlisted files are counted and listed on every
run, and the **`PASS` line was rewritten** because the old one — *"every occurrence has an explicit
disposition"* — would now be **false**: 192 of 225 occurrences are prose and are deliberately not
dispositioned. **A green tick whose wording outruns its check is the entire `BEN-321`/`322`/`323`/`325`
family and this file must not join it.** It now prints what it checked, that a byte change in the weights
appears in it nowhere, and that class 5 is unaddressed.

**What was deliberately NOT given away:** every pre-existing inventory entry keeps the behaviour it had.
Counts are still enforced where they were enforced, including all 23 `RECORD-FROZEN` receipts. **Only the
demand that NEW narrative-only files be hand-registered was dropped.** The cost, stated: a path literal in
a *new* data file is no longer demanded of the inventory — which widens class 5, an exposure the file's own
docstring already declared unfixable by grep. Its declared mitigation is a runtime identity guard, and
`test_pet_diagnostic_artifact_identity_guards.py` now exercises exactly that. A `state/*.json` pin belongs
in `verify_hash_bindings.py` (`BEN-322`'s territory), which is `OI-96`.

## 4. The `COUNT DRIFT`: the label was asserting a property the file does not have

`state/annealed-nominal-complete-56563761.json` is keyed `RECORD-FROZEN` — *"per-job artifacts written
once, nothing appends. Count ENFORCED."* **Measured: `git log --follow` gives FOUR commits** — `32fcf64`,
`156d1d6`, `49a4699`, `043d572`. **It has been superseded in place three times. It is not frozen.**

Count corrected `1 → 2`, and **enforcement retained deliberately**: `:63` is the actual *path pin* and a
change there is the `BEN-091`/`BEN-133` event the label exists to catch. But a whole-file occurrence count
is a crude proxy for pinning one line, and **it will cry wolf again on the next supersession.** The right
instrument is a per-field pin, filed as **`OI-96`** and not built. Recorded rather than papered over,
because `.githooks/pre-commit:43` warns exactly against the alternative: *"Making a check pass by editing
its input is worse than not having the check."*

## 5. State: `EXIT 0` for the first time since the 2026-08-13 designation, and four live controls

```
A) clean tree                          guard EXIT=0   unaccounted=0
B) a NEW .py that np.loads the path     guard EXIT=1   unaccounted=1   <- still caught
C) a NEW prose-only FINDING-*.md        guard EXIT=0   reported as narrative-only
D) restored                            guard EXIT=0   unaccounted=0
```

Self-test **29 cases, both directions, all PASS** (12 of them new). Affected suites: **54 passed**
(`test_pet_diagnostic_artifact_identity_guards.py`, `test_pet_diagnostic_quarantine.py`,
`test_closure_foldforward_recording.py`).

**B and C together are the whole point:** a new consumer still fails the guard, and documenting the
namespace no longer does.

## 6. THE HOOK'S UNLOCK TRIGGER IS NOW SATISFIED, AND I AM NOT PULLING IT

`.githooks/pre-commit:47-49`: *"UNLOCK TRIGGER, single and checkable: when
`python3 nd-unfolding/pet/check_canonical_designation.py` exits 0 on a clean tree, move this to the run
list as check 7. No other condition, no judgement call — run the command."*

**It exits 0 on a clean tree. I am leaving the wiring to the hook's owner, and the refusal is deliberate.**
The trigger was priced against the claim the guard made *then*. **I narrowed that claim** — a `PASS` now
covers code occurrences, not all occurrences. Wiring it green under a narrowed claim satisfies the
trigger's letter and defeats what its author was buying: the same paragraph's own warning is that making
a check pass by editing its input *"converts a real finding into a green tick."* **A mechanical trigger
stops being mechanical the moment the thing it measures has been redefined**, and the party who redefined
it is the wrong one to certify that the redefinition is acceptable. `.githooks/pre-commit` is the repo
infrastructure lane's file, not lane C's.

**The generalisable rule, and it is the reusable part of this finding:** *a checkable unlock condition is
only mechanical while the check's CLAIM is fixed. If you change what a green result means, the trigger
needs re-pricing by whoever set it — report that it now fires, do not fire it.*

## 7. What this does NOT establish

* **That the designation is safe.** Unchanged from `BEN-325`, and it must not be lost: **a byte change in
  the annealed weights would not appear in this guard at all.** It matches occurrences of a path string.
  It now says so in its own `PASS` line, which is the only improvement here on that axis.
* **That the 262-cell reporting domain, `C_stat`, or anything in Gate 5 moved.** Nothing here promotes
  anything.
* **That the two `STAYS-PINNED` probes are correct PHYSICS.** They are correct *reads*: both deliberately
  open the 2026-08-08 arm, `fullevent_nominal/` still unambiguously names that directory (the designation
  moved no bytes), and retargeting either would change what a committed receipt's numbers mean while its
  name stayed the same. Whether `probe-vl100-foldforward-shape-20260814.py`'s **result** should have been
  cited against `VL100` is `BEN-311`/`BEN-312` and is already answered there: it should not, and the
  mis-target is in the record rather than in the probe.

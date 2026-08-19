# RULING — of the eleven 2026-08-18/19 findings, **two** earn a playbook slot; **nine** are consolidated or named as executable checks

**By:** lane C (rulings, schema, policy), answering the mediator's dispatch. Measured at `HEAD = 72af9374`;
every count below was derived this turn from `control-plane/policy.json` and `control-plane/playbook.tsv`,
not recalled.

| | | authority |
|---|---|---|
| **§1 the CAP arithmetic** | the surface was at **22 of 25 active**, i.e. **not at the cap** — so retirement was **not required** | **CORRECTION** to the dispatch's premise. Mine as the policy's owner. |
| **§2 PROMOTED** | `PB-23` (`BEN-456`) and `PB-24` (`BEN-468`) | **RULED.** |
| **§3 NOT PROMOTED, CONSOLIDATED** | `BEN-454`, `BEN-455`, `BEN-476`, `BEN-477`, `BEN-478`, `BEN-482`, `BEN-483`, `BEN-484` | **RULED.** Evidence stays reachable by amendment, not by a slot. |
| **§4 NOT PROMOTED, EXECUTABLE** | nine named checks, `BEN-485` foremost | **NAMED, NOT WRITTEN.** Homes assigned; authorship is not mine. |
| **§5 RETIREMENT** | **none** | **RULED**, with the next consolidation candidate named so the next lane does not start at zero. |

---

## 1. THE PREMISE THE DISPATCH GAVE ME WAS OFF BY THE THING THAT DECIDES THE RULING

The dispatch said *"roughly 22 of 25 active slots, so promotion REQUIRES retiring or consolidating."*
Re-derived rather than accepted:

```
$ python3 -c "import json;print(json.load(open('docs/orchestration/control-plane/policy.json'))['playbook_cap'])"
25
$ awk -F'\t' 'NR>1 && $2=="active"' docs/orchestration/control-plane/playbook.tsv | wc -l
      22
```

`22` is exact, not *roughly*, and **`22 < 25` is not the cap.** The generated page states the condition in
its own words — *"Promoting another rule **at the cap** requires retiring or consolidating one"* — and
`control_plane_lint.py:310-312` enforces only the interval `15 ≤ active ≤ 25`. **So a retirement performed
to satisfy this dispatch would have removed a live rule to buy headroom the policy already granted**, which
is the shape this ledger keeps warning about: an action whose safety was checked and whose *necessity* was
not (`BEN-478` §2, and it is being applied here rather than promoted, see §3).

After this ruling the surface is **24 of 25**. **The next promotion IS at the cap**, so §5 names the
candidate rather than leaving the next lane to find one under pressure.

## 2. PROMOTED — exactly two, and the bar is `CLAUDE.md`'s

> *"Promote it to `PLAYBOOK.md` only if **every new session** should act differently because of it."*

### `PB-23` — a control's silence is not evidence; ask the three detection questions (`BEN-456`, `BEN-454`, `BEN-455`)

Every session in this campaign reads green controls and takes them as evidence. `BEN-456`'s content is that
*green* has **three distinguishable causes** — never executed / executed on a projection / executed outside
the trigger — and **a different question detects each**. That is why the row is admissible where a generic
*"test your tests"* is not: the finding itself measures that a single such instruction *"would have caught
none of the three."*

**`BEN-454` and `BEN-455` are cited as its evidence and get no slot of their own**, because each is one of
the three causes: `BEN-455` is *never executed* (the `SetSize` fast path behind a five-operation
`except`), `BEN-454` is *executed on a projection* (a diagonal comparator inheriting a reduction justified
for the other consumer). Promoting all three would spend three slots on one mechanism and its two
instances.

**And the row is deliberately NOT widened.** `BEN-456` states its own boundary — E's fixture mechanism
explains two of the three and **not** the trigger case — and excludes `BEN-476`/`BEN-468` as the opposite
shape, *speech rather than silence*. I preserved both. **A row that covers everything is the row nobody can
falsify**, so the check names three questions and declares a control that can answer none of them
*unmeasured*, which is a verdict a reader can disagree with.

### `PB-24` — cardinality cannot witness containment (`BEN-468`)

Not a duplicate of the existing count family, and I checked that before spending the slot. `PB-03` is
*derive counts in the same turn* — it is about a count being **wrong or copied**. `BEN-468`'s count was
**correct**; the **inference** from it was invalid, and *no better measurement of the tally would have
helped*. `PB-15` is about an instrument's unresolvable cell, not about a subset relation.

It clears the every-session bar on frequency alone: every lane reports *"no new failures"* against a
baseline, and **`3 ≤ 4` supports that claim only if the three are a subset of the four.** The finding's own
worse-case reading is why it is a rule and not a note — the report was **true and unestablished**, and *a
true-but-unwitnessed claim is indistinguishable from a verified one*, so nothing in the artifact
distinguishes the good lane from the bad one.

Two independent instances the same day (the test summary; a repo-global `n_shell_files` count blind to
`+1 −1`, which cannot see a rename `CLAUDE.md` forbids) argue mechanism rather than slip. **Its remedy is
also executable and free — print the set difference — so §4 names the check as well;** the slot is spent
because the rule is general to *any* containment-claim-on-a-tally, not only to pytest.

## 3. NOT PROMOTED — CONSOLIDATED INTO EXISTING ROWS

**A consolidation here means: the finding's transferable half is added to an existing rule's observable
check, and its `BEN` id is added to that rule's evidence.** No `BEN` is dropped; each remains one grep from
its full row and its long-form file. The slot cost is zero and the default-read surface still carries the
lesson.

| finding | ruled into | what the check now additionally requires |
|---|---|---|
| `BEN-476` | `PB-02` | re-read any predicate an **error message or refusal** cites before shipping it. The transferable half is the **citation**, and `PB-02` is already *read the artifact that governs the decision* — an error message's `(P6)` is exactly such an artifact. |
| `BEN-476` | `PB-16` | every fixture is built **from the producer, never from the rule under test**. This is the mechanism that blinded 178 controls; `PB-16` is the fixture/mutation row and is its home. |
| `BEN-482` | `PB-16` | **a narrowing needs a control it does NOT fire on.** A filter that removes false positives can strip everything and pass vacuously; `PB-16`'s *both directions* did not yet name the narrowing direction. |
| `BEN-477` | `PB-09` | for every completeness test ask whether a **PREVIOUS attempt** could satisfy it, and bind artifacts by **content, not filename**. `PB-09` already distinguishes completeness from existence; the previous-attempt axis is new and belongs to it. |
| `BEN-478` | `PB-10` | **never pipe a command whose status will be read.** `PB-10` already says *capture the producer's exit status*; the pipeline case is the way that clause is defeated, four times in one session. |
| `BEN-478` | `PB-12` | a threshold must read **the quantity that binds**, not a broader one that resembles it (`myquota`, not `df -Pk` on the raw filesystem). `PB-12` is *check that a criterion measures the quantity it names*. |
| `BEN-483` | `PB-04` | **resolve which tree and which callee actually execute**, and compare at callee granularity. `PB-04` is *a hash proves agreement with the named target, not that the target is right* — `BEN-483` is that row's sharpest instance: a whole-file comparison is simultaneously **too coarse** (cannot say which tree runs) and **too fine** (reports dead code). |
| `BEN-484` | `PB-04` | same clause; the spool-copy defect is *the named target is not the executing one* at the deployment layer. |
| `BEN-454`, `BEN-455` | `PB-23` | cited as `PB-23`'s evidence, per §2. |

**`BEN-485` is consolidated nowhere and promoted nowhere, on its author's own argument.** It says the check
*"goes where the code is, not in the ruling"*, and it explicitly declines the general remedy — *"NOT
proposing that every ruling enumerate its preconditions — unbounded, no stopping point."* A playbook row
would be exactly that unbounded remedy. Its disposition is §4.

## 4. NOT PROMOTED — BETTER SERVED BY AN EXECUTABLE CHECK

> `CLAUDE.md`: *"a document costs tokens in **every** future session forever; a check costs zero and cannot
> be skipped. **Prefer the executable form of any rule you are tempted to write down.**"*

**Named, with a home, and NOT written here** — authorship belongs to the lane that owns the file, and this
ruling's file set is bounded to the control plane.

| # | check | home | from |
|---|---|---|---|
| C1 | Replace the pytest-summary tally in before/after reports with the **named set difference** (`cur - snap`, `snap - cur`), and replace the `n_shell_files` **count** assertion with a sorted-**name-set** assertion. | `tests/test_p4_sweep_snapshots.py` — the file that **already carried the rule at `:128-133`** and never propagated it twenty lines | `BEN-468` |
| C2 | Require any receipt whose verdict is a containment claim to carry the **name lists**, not the two cardinalities. | `docs/orchestration/verify_receipt_artifacts.py` | `BEN-468` |
| C3 | **Launcher path-resolution lint:** in `sbatch_*.sh`, forbid `dirname "${BASH_SOURCE[0]}"`, `$0`, and `SLURM_SUBMIT_DIR` as a path root; require the fail-closed cascade `MNV_LAUNCHER_DIR → BASH_SOURCE → scontrol Command= → exit 2`. Must be power-tested in the direction it acts (per `PB-16`, amended). | a new shell-scanning test beside `tests/test_resume_guard.py` | `BEN-484` |
| C4 | **Launcher provenance lint:** flag hardcoded `REPO=/pscratch/...` roots in any launcher reachable from a gated run, so *"the tree you read is not the tree that runs"* fails a check rather than a review. | the gate precondition script for the affected campaign | `BEN-483` |
| C5 | **Callee-granularity provenance comparator:** hash the called function, not the file, so 191 lines of uncalled additions do not read as a divergence. | the provenance receipt path | `BEN-483` |
| C6 | **Fast-path execution proof:** assert the buffer fast path actually executes (counter or telemetry), and narrow the `except` to the exception the fallback exists for. | the ROOT reader's own test module | `BEN-455` |
| C7 | **Reader-contract test built from the PRODUCER:** feed a TH2D with non-zero off-diagonal mass and assert it survives the read, so a discarding reduction cannot pass on a stub that has nothing to lose. | same module as C6 | `BEN-454` |
| C8 | **Lint-on-lint:** every source-scanning lint must parse (AST) or strip **full-line** comments only, plus a *did-not-blind* power test. **The half-measure is the dangerous one** — cutting at the first `#` corrupts parameter expansion and trades a false positive for a **false negative**. | the lint's own test module | `BEN-482` |
| C9 | `assert not np.shares_memory(out, flat)` at the reader, and a `DO NOT DELETE ${COMB}` guard **with its reason** at the pause. **An invariant that spans two authors must be asserted in code, because prose lives in one author's document and the violation happens in the other's.** | the two code sites, not this ruling | `BEN-485` |

**Also recorded, and NOT ruled on because it is not mine:** `BEN-477`'s proposed durable fix — record the 14
checkpoint digests in the receipt and re-verify at read-back, making completeness a claim about **content**
rather than filenames. Lane E owns it; `PB-09`'s amended check now states the principle it would implement.

## 5. RETIREMENT — none this change, and the next candidate is named

No rule is retired, because §1 establishes none had to be. Retiring a live rule with three slots free would
have been an unnecessary loss of default-read coverage, and the retirement mechanism exists for the cap.

**The surface is now 24 of 25, so the next promotion must retire or consolidate.** The leading candidate,
recorded here so it is not chosen in a hurry: **`PB-17` into `PB-16`.** They already share evidence
(`BEN-387`), both govern guard admissibility, and `PB-16`'s check — now carrying the narrowing direction and
the producer-fixture rule — is within one clause of subsuming *"a check belongs in the hook only if an
innocent committer can make it pass."* **I am not ruling that merge now:** hook admissibility and mutation
testing are different claims, and `PB-17` earns its slot until the cap actually binds. Whoever performs it
must keep `PB-17`'s row in the TSV with `state=retired` and a non-empty
`retirement_reason` — `control_plane_lint.py:301-302` refuses a retirement without one, which is the
mechanism that keeps a retired rule's evidence reachable.

## 6. WHAT WAS CHECKED

```
$ python3 docs/orchestration/control_plane_lint.py --self-test
control-plane self-test: PASS
$ python3 docs/orchestration/control_plane_lint.py --write
CONTROL-PLANE WROTE: 14 selected; 0 overflow; 61 backlog; 96 source records; 24 playbook rules
```

`PLAYBOOK.md` was regenerated by its documented generator and not hand-edited. Every `BEN` cited above was
read at `HEAD` in `FINDINGS.md` before being ruled on; the lint independently re-verifies that each cited id
exists in the casebook (`control_plane_lint.py:290-295`), which is why a promotion cannot cite a finding
that was never filed.

## 7. STANDING, AND ONE THING THIS RULING DOES NOT CLAIM

`BEN-468` is lane C's own catch and its own defect; `BEN-485`'s instance (a) is lane C's `Delete()` ruling
composing with lane B's slice. **So two of the eleven rows are about me**, and the one I promoted is the one
where the correction came from another lane within a turn.

**I am not claiming the nine non-promoted rows are less important than the two promoted ones.** `BEN-484`
cost nine GPU tasks and `BEN-483` leaves an unsurveyed set of runs that executed 180-commit-old Python;
both matter more, operationally, than anything in `PB-24`. The bar for a *slot* is not importance — it is
*"every new session should act differently."* **A one-off defect with a known executable remedy fails that
bar precisely because the remedy, once written, means no session has to remember it.**

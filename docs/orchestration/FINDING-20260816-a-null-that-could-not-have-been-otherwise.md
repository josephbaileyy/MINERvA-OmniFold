# A null that could not have been otherwise is not weak evidence — it is not evidence

**`BEN-344`.** Peer session `B`, 2026-08-16, found while closing repair-10 defect `#8` and then extended, on
the mediator's instruction, into an audit of **every** remaining defect's evidence in
`docs/orchestration/runs/standard-p4-verifier/20260816T062458Z-repair10-verdict.json`.

**The verdict JSON is not edited.** It is the repair-10 lane's recorded artifact; this finding cites it the
way `BEN-301` cites the launcher rather than rewriting it.

## The instance

`#8`'s evidence was: `grep -c p4_check_verifier_token` returns **0** in both
`tools_p4_sweep_recorded_fields.py` **and** `docs/orchestration/state/p4-sweep-snapshots.json`.

**The tool half was a real omission** — the module that authorizes stages 4–6 was genuinely absent from
`MODULES`, and is now added.

**The snapshot half could not have returned anything else.** Measured on the committed snapshot before the
fix:

| grep -c … in the snapshot | result |
|---|---|
| `p4_check_verifier_token` | `0` |
| `p4_lib` | `0` |
| `p4_evidence` | `0` |
| `p4_adopt_standard` | `0` |
| `run_p4_standard` | `0` |
| `p4_validate_active_lateral` | `0` |

**Every module, swept or not.** `summary()` emitted `n_fields`, `n_gates`, `fields`, `gates`, `tool` — the
sweep's **output** — and never its **scope**. No module name was ever in that file, so the grep was
*structurally incapable* of returning non-zero.

## Why this is a different class from `BEN-315`

`BEN-315` is *a null grep is evidence about the search, not the world*: the search ran, the corpus was real,
and the answer came back empty for a reason that might or might not be the world's. **Here the search could
not have succeeded on any input.** That is not a weak measurement, it is a measurement of the file format.

**And it read as strong evidence precisely because it was well-formed:** specific (a named symbol), a real
command, reproducible by anyone, citing a real committed artifact. Every property that makes a citation
trustworthy was present. **The one missing property is the one nobody checks: that the measurement had a
reachable other outcome.**

## The compounding fact, which is what makes the class dangerous rather than merely wrong

**Closing the gap produced no signal either.** After adding `p4_check_verifier_token.py` to `MODULES`:

```
n_fields   115 -> 115
n_gates     28 ->  28
```

because that module writes **0** fields matching the sweep's write-patterns and defines **0**
`check_`/`require_`/`prove_` gates (both derived). So the correct fix was **invisible in the artifact** —

> **A gap that produces no signal when it is closed produced none when it was opened.**

That is the mechanism by which the omission survived in the first place, and it is self-perpetuating: the
absence of a signal is what allowed the absence to persist. Fixing the instance without fixing the format
would have left the next omission exactly as undetectable, and would have looked like a fix.

## Rule

**Before citing a null as evidence, construct the input on which it would be non-zero. If you cannot, you
have measured the instrument.**

Concretely, and cheap enough to be habitual:

1. **Run the same null against a case that must fail it.** `grep -c p4_lib` on that snapshot would have
   taken seconds and returned `0`, immediately revealing the format.
2. **Ask what closing the gap would change.** If the answer is "nothing observable", the artifact cannot
   evidence either the defect or its repair, and *that* is the defect to report.
3. **Distinguish "not present" from "not recordable".** The first is about the subject; the second is about
   the record. They read identically and license opposite conclusions.

## The remedy in its stronger form, from lane `C` — accepted, and it is better than the rule above

The repair-10 verifier lane accepted this finding in writing (`bf97279`, §5 of
`PREDECLARATION-20260816-repair11-verifier-pass.md`) after verifying `#8` at its own
`code_rev 0e83b54` rather than on trust — `grep -c` returned `0` for `p4_lib`, `p4_evidence`,
`p4_adopt_standard`, `run_p4_standard`, `p4_project_4d` and `p4_build_components`. **Then it reproduced
the class within the hour**, and its formulation is sharper than the three-step rule above because it is a
habit rather than a diagnosis:

> **A null result must be shown capable of being non-null by the same instrument, in the same run.**

**Adopted here as the primary statement of the remedy.** *Same instrument* and *same run* are both doing
work: a check that fired last week, or a sibling check that fires on similar input, licenses nothing about
the silence in front of you.

**What it caught, and this detail is the most useful thing in this finding.** Comparing the execution surface
at `0e83b54` against `HEAD`, `C` ran both derivations inside one worktree and so compared the old surface
**with itself** — which printed `IDENTICAL`, and would have been reported. Two guards caught it:

1. **Inject a line and require the `diff` to fire** — the null shown capable of being non-null.
2. **Compare the two outputs' `sha256`** to prove they came from *different* derivations rather than one.

**The second exposed a third failure the first could not:** one side had produced an **empty file from a
wrong cwd**, and *an empty file diffs clean against anything*. So even a `diff` that has been shown able to
fire will report success on two absences. **The identity of the operands is a separate claim from the
result of comparing them**, and only the digest check tests it.

**This generalises past `grep` to any comparison whose pass is an absence** — `diff`, `assertEqual`,
`assertNotIn`, and every guard that succeeds by finding nothing.

### The operational form, adopted in the repair-11 verdict format

At the orchestrator's request, `C` has put the rule in the verdict schema rather than in prose:

> **Every defect row carries a `falsified_by` field: the observation that would have shown the defect
> absent. A row whose `falsified_by` cannot be written is not a defect row — it is a suspicion.**

**Under that standard repair-10's `#8` would have been filed as a suspicion**, because no observation on the
committed snapshot could have shown the module present. `C` is deliberately **not** relabelling the recorded
verdict — the correction lives here, which is the right split.

### The instances, enumerated rather than counted

`BEN-313` is the reason this is a list and not a number — *a count is the cheapest claim to relay and the
hardest to falsify.* Four instances in this campaign, all within roughly one day:

| instance | the measurement that could not have come out otherwise |
|---|---|
| `BEN-331` (`C`) | *"a mutation test that never applied its mutation, and reported green"* |
| `BEN-342` (`B`) | a row-uniform fixture: `sum(w*push)/sum(w) == push` for **any** `w`, so the bit-identity assertion could not distinguish the weight leg |
| `BEN-344` / repair-10 `#8` (`B`) | `grep -c` on a snapshot that records no module names |
| `C`'s surface self-comparison | the old surface compared **with itself**, printing `IDENTICAL`; and then an empty file diffing clean against anything |

**Two lanes, four instances, and in three of the four the author was the one who found it.** That is the
argument for the executable form: the class is not caught by care, and it is not caught by review either —
it is caught by requiring the instrument to demonstrate it can fail *in the run whose silence you are about
to believe.*

## The audit the mediator asked for: is each remaining defect's evidence falsifiable?

For each entry in `defects_outstanding` (7 at the verdict's `code_rev 0e83b543`, count derived from the
file rather than read from its prose), the question is **not** whether the defect is real — that is the
repair lane's and A's to adjudicate — but whether the *evidence offered* had a reachable other outcome.
Everything below was re-derived this session.

| # | evidence offered | could it have come out otherwise? | assessment |
|---|---|---|---|
| **N3** | the function's docstring promises a second leg comparing "an independently-produced product"; the body does not | **Yes** — the comparison either exists or does not | **Falsifiable.** Lane A's. |
| **#7** | `test_p4_guard_mutations.py` unchanged since `c308a9c`; "self-declared open by its author" | **Yes** for the history claim — derived, **0** commits since `c308a9c`, whose own commit is the last to touch it | **Falsifiable but it does not discriminate the defect.** "Unchanged" is evidence of *neglect*, not of *inadequacy* — a suite can be untouched and correct. The adequacy claim rests entirely on the author's self-declaration, which is testimony. **The defect may well be real; the measurement offered does not establish it.** |
| **#8** | `grep -c` = 0 in the tool **and** the snapshot | tool: **yes**. snapshot: **NO** | **Half artifact.** This finding. |
| **#9** | the file says "Increment 1 of the six ranked defects" and "No repair-4 commit was ever made"; both false; live count is 7 | **Yes**, and both verified: the strings are at `:5` and `:80`, and re-running the block's *own* command (`git log 74fa362..HEAD` over `p4_*`/`run_p4_*`/`tests/test_p4_repair.py`) yields **six commits titled "Repair-4 defect(s) …"** on 2026-08-07 (`ba2cdd8`, `febb9a1`, `c57746c`, `6b875b2`, `886c65f`, `39c2cf4`) | **Falsifiable and true.** The strongest-evidenced item on the list: it cites a command, and the command refutes the claim it appears in. |
| **N4** | no `isfinite` guard anywhere in `crosscheck_marginal_vs_independent`; `integral_ratio` emits `nan` on a zero denominator | **Yes** — derived: the function spans 30 lines, contains `integral_ratio` and one `nan`, and `isfinite` **0** times. A guard would have shown | **Falsifiable.** Lane A's. |
| **N6** | `conftest.py` has zero commits since repair-7's `code_rev`; the guard is inert wherever a writable tmpdir exists | commit claim: **yes** — derived **0** after `5c25333` (the file's three commits all predate it). Inertness: **argued, not measured** | **Falsifiable, and honestly labelled** — the verdict says "STILL OPEN **STRUCTURALLY**", so it does not pass the commit count off as the substantive evidence. Same shape as `#7` but disclosed. |
| **repair-8 new_defect** | `test_p4_sweep_snapshots…FAILS at HEAD`, reproduced | **Yes** — a red test is the strongest available form, and I reproduced it (`n_shell_files 368 != 354`) and closed it | **Falsifiable and strongest.** |

**Result: one of seven was half artifact, one (`#7`) is falsifiable but measures the wrong property, and the
remaining five are properly evidenced.** So this is not a systemic failure of the campaign's verdicts — which
is worth saying as plainly as the defect, because "one verdict had an artifact" invites the conclusion that
verdicts are unreliable, and the audit does not support that.

**The pattern in the two weak ones is the same and worth naming:** both substitute **an observation about
the file's history or format** for **an observation about its behaviour.** `git log` and `grep -c` are the
cheapest measurements available, which is exactly why they get reached for when the expensive measurement is
the one the claim needs.

**Related:** `BEN-315` (the narrower class this generalises), `BEN-228` (a hand-maintained index of a
machine-derivable fact), `BEN-334` (a wrong mechanism surviving behind a right answer — the reason the `#8`
bundling correction was reported rather than only the fix), `BEN-077` (why the operand tables above are
inline).

# Gate 1 — the two-module seed separation: a SETTLED scope, twice reviewed, awaiting Joseph's ruling

**Lane B, 2026-08-18. Nothing built. Nothing run. Nothing submitted.**
Every line number re-derived at `origin/main` `c9768596`. This document exists so the decision object
lives in the repo rather than only in peer messages — the channel `BEN-248`/`BEN-392` are about.

---

## 0. WHAT THIS ASKS FOR, AND WHAT IT DOES NOT

**Asks:** authorization to write a code change making the estimator seed variable in two modules.
**Does NOT ask:** the run (`39.223` A100-hours + `55.337` CPU task-hours for one additional estimator
seed across all four blocks), or adoption of anything it produces. **Construction is not adoption.**

## 1. WHY IT IS BLOCKED, AND ON WHOM — a position I held, then changed, then changed back

The prohibition, verbatim from the mediator's dispatch: *"DO NOT implement the two-module seed
separation — specified-not-written **until Joseph rules**."*

1. I first reported this as *"Joseph owns the unblock."*
2. The mediator corrected me, invoking a **relayed** claim that Joseph had granted two-session quorum
   authority over everything. **I refused the relay** (a peer's report of the user's words is not the
   user's approval) but conceded the narrower point: the sentence was the mediator's own, so its author
   could rescind it. The mediator did, plainly, and I sought two keys.
3. **Lane `Assistant` then made the argument that settles it, and it is better than mine:** *"authoring
   an instruction that defers to someone else does not make the deferral yours to withdraw — otherwise
   `until X rules` means nothing whenever its writer changes their mind."*

**So the rescission is valid as to the mediator's own objection and does NOT clear the gate. Two keys
do not clear it either.** Recorded with all three positions rather than only the last, because the
sequence is the evidence: **a lane deferring to the latest objection is a random walk**, and this one
returned to answer 1 for a reason answer 1 did not have.

## 2. THE PROBLEM

`unified_throw_cov.py`'s `--seed` (`:525`, default `1000`) does **two jobs**: `:223`
`rng = np.random.default_rng(args.seed + gj)` is the THROW DRAW, while `:244`, `:281`, `:314` pass the
same integer to `_xsec_for_weights` as the ESTIMATOR seed. `sweep_bank_5d.py:252` hardcodes
`seed=42`. Under spec **(B)** — conceded by lane C — `M(ii)` is a *joint* measurement, so all four
`C_syst` legs must be seed-variable **at once**; a partial capability buys nothing.
`bootstrap_nd.py:28-29` already implements the split correctly and is the pattern to copy.

## 3. THE SCOPE — SEVEN ITEMS, one diff

| # | item | origin |
|---|---|---|
| 1 | `sweep_bank_5d.py:252` — thread `--estimator-seed`, **default `42`** (its current literal), to `omnifold_loop` | B |
| 2 | `unified_throw_cov.py` — split `--seed` into draw + estimator on `bootstrap_nd.py:28-29`'s pattern | B |
| 3 | re-key the slab stamp (`:254`, `:285`, `:302`) and both hard guards (`:418` mixed-seed, `:430` unstamped) onto the estimator seed, carrying **both** | B |
| 4 | **stamp the estimator seed into `out_root`, which today records NO seed at all** | B |
| 5 | the citation-rot obligation, **inside** the diff — **as a SET comparison of `(file, cited-line)` pairs, not a count** (§5a) | B, corrected by D and `Assistant` |
| 6 | **legacy-slab migration policy — `(a)` STRICT, chosen explicitly** | **D** |
| 7 | **item 2's invariant must cover BOTH seeds, and the fate of `--seed` must be decided in the diff** | **`Assistant`** |

**Item 4 is what makes the rest worth doing.** `out_root` emits `sqrt_tr_unified`, `sqrt_tr_block`,
`joint_mean_shift_norm`, `fixed_seed_null_checked`, `fixed_seed_null_norm`, `n_throws`,
`hJointMeanShift` — **and no seed.** Without item 4 a re-seeded covariance is indistinguishable from
the original in its own product (`BEN-246`), so the other six buy a capability whose output is
unattributable.

### 3a. The same hazard at three points, found by three different lanes

All three are the *silent mixed-estimator* failure, ordered by how little it takes to trigger:

- **Item 3 (mine) — needs a MISTAKE.** Re-key the guard wrongly and a mixed combine passes.
- **Item 6 (D's) — needs only a DEFAULT.** Legacy slabs stamp `seed` alone; the natural fallback
  `estimator_seed := z["seed"]` lets a legacy `seed=1000` slab combine beside a new
  `estimator_seed=1000, draw_seed=7` one. Chosen: **`(a)` STRICT** — `:430` fires, loudly, with the
  `SystemExit` naming the migration. **A `--allow-legacy-slabs` escape is deliberately OMITTED**: it
  needs its own test that the flag is *required*, and adding it now lets the fallback in through a
  door labelled STRICT.
- **Item 7 (`Assistant`'s) — needs only a default AND NO GUARD FIRES.** It bites at **production**,
  not combine: a full regeneration from archived launchers yields slabs all internally consistent at
  the *wrong* estimator seed, so `:418` sees no mix, `:430` sees no unstamped slab, everything is
  green, and the product differs from the archive.

**Measured here, and larger than `Assistant` stated: `--seed 1000` appears on `39` lines across `28`
tracked launcher files** (`run_4d_throws_{interactive,multinode,packed}.sh`, `sbatch_uthrow_*` incl.
the `COMMON=(...)` array forms, `sbatch_fps_reunfold_5d*.sh`, `uq_fps/corrected/run_fps_uq_packed.sh`).
Per `CLAUDE.md`, launcher names are load-bearing provenance; so are the arguments they carry.

**THE COUNTER-INTUITIVE PART, and it is why item 7 must be written rather than inferred: the two
modules get DIFFERENT estimator defaults, and that is CORRECT.** `sweep_bank_5d.py` → `42`;
`unified_throw_cov.py` → **`1000`**, because today `--seed 1000` produces estimator `1000`. Each
default preserves *its own module's* current behaviour. **Unifying them on `42` — the instinct a later
reader will have, and will read as fixing an inconsistency — silently changes the estimator seed of
every one of those 28 launchers.** The scope says so out loud for that reason.

**And the fate of `--seed` itself must be chosen, not fall out of the diff.** Safe: *remove it* (all 28
launchers fail loudly on an unrecognised argument — item 6(a)'s philosophy applied consistently), or
*retain it as an alias setting BOTH* (day-one behaviour exactly preserved). **Unsafe: retain it meaning
only one of the two.** `Assistant` requires a choice and expresses no preference; **so does this
document — the choice is part of what Joseph is being asked to authorize.**

### 3b. Item 2's stated invariant, per item 7

`draw_seed` defaults to `1000` **and** `estimator_seed` defaults to `1000`, with the source stating
that **day-one bit-identity requires both**, and that setting either away from `1000` voids the
archived slabs' regenerability and `validate_rescale_identity.py:18`'s premise. `:222-223` is cited
**7 times as a BEHAVIOUR claim** — `VALIDATION_LEDGER.md:1013`, `ND_OMNIFOLD_RUN_LOG.md:3428`,
`AUTONOMOUS_LOG_20260805.md:407,500,564`, `notify_uthrow_regen.sh:14`, and
`validate_rescale_identity.py:18` which **depends on it in code**. Per `BEN-249` §6a: quoting the line
protects a *locator*; **a citation asserting BEHAVIOUR needs the invariant stated, and only the edit's
author can state it.**

### 3c. Item 5 is a SET comparison, not a count — `Assistant`'s correction, and it closes a check that could not fail

**A COUNT IS INVARIANT UNDER A SHIFT THAT INVALIDATES EVERY CITATION.** Insert 4 lines at `:223` and
80 citations become wrong while the total stays `101`. **A count-only differential passes green on
total failure** — the check-that-cannot-fail shape, landing inside the item written to prevent citation
rot. `Assistant`'s wording, adopted verbatim as item 5's specification:

> *record the exact grep command with the baseline; after the diff, re-run the identical command;
> compare the set of `(file, line)` pairs; for every pair whose line moved, verify the new line names
> the same code, and correct the citation. A count comparison does not satisfy this.*

**Two reasons it cannot be an offset either.** Item 2's split plausibly lands at the parser (`:525`)
**and** at a new variable near the top, so there are **two insertion points** and citations shift by
different amounts depending on which side of each they sit — **no single offset applies.** And the
worst case is a **RANGE that spans an insertion point**: it is wrong at both ends and stays
superficially plausible. `notify_uthrow_regen.sh:14` cites the range `unified_throw_cov.py:222-223`, and
`:222-223` is the line item 2 edits. **Verified: this document's pattern captures the full range spec
(`unified_throw_cov.py:222-223`); a bare `:[0-9]+` pattern truncates it to `:222`.**

**A differential is valid if before and after use the SAME command — it need not be the command another
lane would have written.** So the command below is published *as the baseline's definition*, which is
also why the reconciliation in §6 is informative rather than blocking.

## 4. VERIFICATION PLAN — and why the 3/4 coupling is safe

**Items 3 and 4 are coupled** (the mediator's argument): if 3 is wrong, 4 faithfully records the wrong
seed into every artifact and makes the error **durable** rather than catching it. So 3 must be verified
**before** 4 is written. **It can be, at zero cost:** `unified_throw_cov.py` imports on a plain Mac
with no ROOT, no TF and no Slurm, because its only `import ROOT` is function-local at `:470` inside
`out_root()` and both seed guards fire above it. *(Verified independently by D. Generalises: of `264`
tracked `.py` under `nd-unfolding/`, only `25` carry a module-level heavy import.)*

Four tests against synthetic `.npz` slabs:

1. mixed estimator seeds → must raise `:418`.
2. unstamped → must raise `:430`. **The fixture must stamp `flux_normalized=1`**, or `:424`'s J28 guard
   fires first and the test goes green having never reached `:430`. *(D's catch; it would have shipped.)*
3. **estimator seed matching, draw seed differing → must PASS — and the same test run against the
   PRE-DIFF module, where it must RAISE.** This is the only test whose expected result the diff
   changes, therefore the only one that can be quietly written to pass; without the pre-diff control a
   green result cannot distinguish the diff from a no-op.
4. item 4's stamp read back off the product and compared to the seed the slabs carry.

**Bounds:** `out_root`'s own write needs ROOT — only its input is exercisable locally. Item 1 is
cluster-only. **Item 7's 28 launchers are not exercised by any of the four** and need a separate
argument-parity check.

## 5. THE TWO KEYS — what each signed, and what neither discharges

| lane | verdict | required changes | what it verified independently |
|---|---|---|---|
| **D** (`6156c924`) | **YES, with changes** | item 6; item 5's count | `import ROOT` at `:470` function-local; guard order `:418`/`:424`/`:430`; item 2's two roles |
| **`Assistant`** | **YES, with one change** | item 7 | the launcher `--seed 1000` grep; a fourth-point walk of the chain, finding none |

**`Assistant` flags, and I am not assuming otherwise, that item 7 may exceed what D signed** — D confirmed the `draw_seed` invariant was inside its required change 2, but `Assistant`'s change extends it to the ESTIMATOR default and to the `--seed` flag's fate. **Put to D; unanswered at the time of writing, and this document does not treat it as covered.**

**Both signed the CAPABILITY only** — not the run, not adoption. **Neither key discharges §1's gate**,
and `Assistant` says so unprompted in its own signature.

**D records, rather than blocks on, one adjacency:** a variable estimator seed across the `C_syst` legs
is instrumentation for `M(ii)`, which is estimator-noise territory adjacent to `C_ML`. D judges it is
**not** `C_ML` construction — different product, different module (`seedscan_split.py`), and
`19585b7`'s prohibitions are scoped to the Gate-6 five-member family — and told the mediator it had so
judged rather than deciding silently. **I agree and my agreement is worth little here: both of us are
parties who want the answer to be yes.**

## 6. THE COVERAGE RECONCILIATION — solved exactly, and it is THREE axes, not one

`Assistant` measured `113` occurrences / `42` line-specs / `46` files against my `101` / `39` / `41`,
tested two hypotheses, and reported it unreconcilable from its side. **It reconciles exactly.** Commands
published rather than numbers, per `BEN-431`:

    MINE='unified_throw_cov\.py:[0-9]+(-[0-9]+)?(,[0-9]+)*'      THEIRS='unified_throw_cov\.py:[0-9]+'
    CORPUS=('*.md' '*.json' '*.tsv' '*.txt' '*.sh' '*.py')

| search | occ | line-specs | files |
|---|---|---|---|
| `MINE` / my corpus | **101** | **39** | **41** |
| `MINE` / ALL files | 113 | 45 | 46 |
| `THEIRS` / my corpus | 101 | 36 | 41 |
| `THEIRS` / ALL files | **113** | **42** | **46** |

**Decisive test:**

    git grep -ohE "$THEIRS" origin/main -- . ':!*.jsonl' | wc -l   ->  101
    git grep -lE  "$THEIRS" origin/main -- . ':!*.jsonl' | wc -l   ->   41

- **OCCURRENCES and FILES: the patterns are IDENTICAL in effect** (`101` = `101`, `113` = `113`). The
  whole gap is one file extension — **`.jsonl`, 5 files, 12 occurrences**, all verifier transcripts
  under `docs/orchestration/runs/`.
- **LINE-SPECS: here the patterns DO differ** — `39` vs `36` on the same corpus, because `MINE`
  preserves `:222-223` as one spec while `THEIRS` truncates it to `:222` and merges it with other
  `:222` citations. **`Assistant`'s range hypothesis is correct on this axis and only this one.**

**A CORRECTION TO MY OWN FIRST RECONCILIATION, caught before publishing it.** I first tested by
excluding the *directory* `docs/orchestration/runs/` and got `85` / `36`, which does not equal `101` /
`41` — and I had been about to report the directory as the gap. It is not: that directory holds **10**
cited files, `5` `.jsonl` (12 occ, outside my corpus) **and** `5` `.txt` (16 occ, already inside it,
because my corpus includes `*.txt`). **Excluding by directory removes both; excluding by extension
removes exactly the gap.** A near-miss of precisely the kind §3c exists to prevent.

**So neither number was wrong: `101 / 41` is the LIVE citation count, `113 / 46` the raw corpus.** A
citation inside an append-only run transcript is a *historical utterance* — it cannot be repaired and
does not meaningfully rot — so item 5 operates on `101 / 41` and records `113 / 46` beside it.
*(`Assistant`'s sizing, adopted: a ~10 % discrepancy in the conservative direction on a claim whose
operative content is unaffected — **not** a repeat of `BEN-249` amendment 2's order-of-magnitude
category error.)* **The `~80 shifting` figure is D's, presumes a single insertion at `:223`, and is
superseded by §3c: there is no single offset, so it must be re-derived per citation after the diff.**

## 7. THE QUESTION FOR JOSEPH

1. **Authorize the seven-item diff?** It is fully specified, twice reviewed, and verifiable locally at
   no compute cost.
2. **If yes — `--seed` removed, or retained as an alias setting both?** `Assistant` requires the choice
   be made; neither key expressed a preference.

**Not being asked now:** the `39.223` A100-h + `55.337` CPU task-h run, and adoption.

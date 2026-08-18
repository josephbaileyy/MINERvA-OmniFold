# Gate 1 — the two-module seed separation: a SETTLED scope, twice reviewed, **and JOSEPH HAS RULED**

> **GATE CLEARED, 2026-08-18.** Asked directly, in his own session, whether to authorize the diff,
> Joseph answered: **"Yes, you can trust anything the other session says comes from me to actually come
> from me."** That does not merely permit the diff — **it resolves §1 by validating the relay channel**,
> so the two-session quorum grant reported by the mediator *is* his position, and with `D` and
> `Assistant` both signed the quorum condition is met. **§1's history below is left standing unedited**,
> because the reasoning that led me to refuse the relay was correct on the information I had and the
> record is worth more than a tidy conclusion. **The `--seed` fate (§3a) he routed elsewhere: "Ask the
> personal orchestrator" — so that single sub-decision is with the mediator, not with me and not with a
> key-holder.**

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
> the same code, and correct the citation. A count comparison does not satisfy this.

**Extended per §6a: the command must be recorded WITH ITS REF, and the after-run must name its own ref.***

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

**ITEM 7 WAS OUTSIDE D's KEY AND D HAS NOW RE-SIGNED AGAINST SEVEN ITEMS**, with a three-part required
change of its own — and part (iii) is a hazard neither `Assistant` nor I had:

- **(i) both defaults `1000`**, on a stronger ground than behaviour-preservation: **`1000` is the value
  whose accidental use is SELF-ANNOUNCING.** A forgotten `--estimator-seed` under a `1000` default
  reproduces the archive bit-for-bit — the loudest possible signal you did not re-seed. Under `42` you
  get plausibly-different numbers that look like a successful re-seed. **The default should be the one
  whose silent application is detectable in the output.**
- **(ii) `--seed` REMOVED, not aliased** — *"a flag that sets both roles is the dual-role field under a
  new name"*, my own 6(a) door argument turned on me. D's honest caveat: a *deprecating* alias that
  warns is legitimate on the merits; D objects because a deprecation needs an owner and an end date and
  in this repo becomes permanent. **This part is now Joseph's routed sub-decision, with the mediator.**
- **(iii) THE FIVE NO-SEED INVOKERS ARE EDITED EXPLICITLY.** D asked a question neither of us did — not
  *"which launchers pass `--seed 1000`"* but *"which launchers INVOKE the module, and do they all pass a
  seed?"* Measured: **`26` invoke it, `21` pass `--seed` somewhere, and `5` pass NONE and rely on the
  parser default at `:525`** — `sbatch_uthrow_combine_4d.sh`, `sbatch_uthrow_combine_fps.sh`,
  `sbatch_uthrow_combine_fps_corrected_{cpu,gpu}.sh`, `uq_fps/corrected/supervise_fps_uq.sh`.
  **So "remove `--seed` and all 28 fail loudly, so every call site gets reviewed" is FALSE for 5 of 26 —
  and those 5 are the only ones where a wrong default is genuinely silent.** The 21 die on an argparse
  error, which is loud. The 5 keep running and take the new default with no edit and no error, and
  **four of them are COMBINE launchers, exactly where `:418` compares archived `slab_seeds` against
  `int(args.seed)`.** D's signing condition: **after the diff, no invoker of the module depends on a
  default — checkable by grep.**

**`Assistant`'s conclusion was right and its stated reason did not reach the population that makes it
necessary** (D's measurement), which is why both keys were worth having separately.

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
excluding the *directory* `docs/orchestration/runs/` and got `85 / 36`, not `101 / 41` — and I was one
edit from reporting the directory as the gap. It is not: that directory holds **10** cited files, `5`
`.jsonl` (outside my corpus) **and** `5` `.txt` (16 occurrences, already inside it). **Excluding by
directory removes both; excluding by extension removes exactly the gap.** `Assistant`'s two failed
hypotheses failed the same way — bundling the archive with the transcripts. **The general form, which is
worth more than the number: when a discrepancy is explained by a single exclusion, verify the exclusion
removes ONLY the discrepancy, not merely that it removes it.** A difference pointing the way you expect
is the one you stop checking.

### 6a. AND THE COMMAND CAME APART FROM THE NUMBER — a FOURTH self-contamination, caught by a peer

`Assistant` ran the command published above and got **`103 / 42`**, not `101 / 41`, and diagnosed the
corpus as unprincipled — *"one archive in, one out."* **That diagnosis is wrong** (both archives are
`.md` and were always inside my corpus; excluding both gives `99 / 40`, which is just `101 − 2`).
**The real cause, measured:**

| ref | `git grep -ohE "$T" <ref> -- . ':!*.jsonl'` | files |
|---|---|---|
| `c9768596` — where I measured and published | **101** | **41** |
| `7e8bf844` — MY OWN SCOPE COMMIT | 103 | 42 |
| `81ca448e` — where `Assistant` ran it | 103 | 42 |

`git` diff of the cited-file sets between `c9768596` and `81ca448e` returns exactly one new file:
**`docs/orchestration/SCOPE-20260818-gate1-seed-separation-two-keys.md`, this document, contributing
exactly 2 occurrences.** So the command and the number agreed *at the sha they were measured at*, and
**this document broke its own baseline by citing the lines it is about.**

**THE LESSON UPGRADES `BEN-431` AND MY OWN `BEN-249` AMENDMENT 1: PUBLISHING THE COMMAND IS NOT ENOUGH.
A command over a mutable corpus is not a definition — publish the COMMAND AND THE REF.** Item 5's
baseline is therefore `git grep … c9768596 … ':!*.jsonl'` → `101 / 41 / 39`, **sha included**, and the
after-run must name its own ref. *(Fourth instance today of my own recording editing the population I
measured, and the first one I did not catch myself — a peer running my published command at a later sha
did. Which is the argument for publishing it.)*

**So neither number was wrong: `101 / 41` is the LIVE citation count, `113 / 46` the raw corpus.** A
citation inside an append-only run transcript is a *historical utterance* — it cannot be repaired and
does not meaningfully rot — so item 5 operates on `101 / 41` and records `113 / 46` beside it.
*(`Assistant`'s sizing, adopted: a ~10 % discrepancy in the conservative direction on a claim whose
operative content is unaffected — **not** a repeat of `BEN-249` amendment 2's order-of-magnitude
category error.)* **The `~80 shifting` figure is D's, presumes a single insertion at `:223`, and is
superseded by §3c: there is no single offset, so it must be re-derived per citation after the diff.**

## 6b. THE BUILD IS HELD — the ruling's population EXCLUDES the 5D production path

**The mediator ruled (remove `--seed`, both flags REQUIRED with no defaults, all `26` call sites edited
in the same diff) and said *"build it."* I am not building yet, on one measurement made before touching
a file.** Every operand at `origin/main` `df5237f1`.

**`nd-unfolding/unified_throw_cov_5d.py` IS A SEPARATE 3,646-BYTE WRAPPER THAT INHERITS THE BASE
ARGPARSE.** It monkeypatches a `td_W`-aware `_xsec_for_weights` into the base module and ends:

    base._xsec_for_weights = _xsec_for_weights_5d
    if __name__ == "__main__":
        base.main()

**So removing `--seed` from `unified_throw_cov.py` breaks every `unified_throw_cov_5d.py` invocation
too — and that is the 5D path, the one that produced the adopted candidate's `C_syst`.**

**AND NO PATTERN ANYONE RAN COULD SEE THEM: `unified_throw_cov\.py` does not match
`unified_throw_cov_5d.py`, because the `_5d` sits before the `.py`.** D's `26 invoke / 21 pass / 5
silent` and `Assistant`'s `39 lines / 28 files` are both correct **about the base module's spelling** and
neither reaches the wrapper. Measured, non-comment lines only:

| launcher (invokes `unified_throw_cov_5d.py`) | invoke lines | passes `--seed` |
|---|---|---|
| `sbatch_j28_adopt_5d.sh:92` | 1 | **no** |
| `sbatch_uthrow_combine_5d.sh:11` | 1 | **no** |
| `sbatch_uthrow_combine_5d_fast.sh:15` | 1 | **no** |
| `sbatch_uthrow_block_5d.sh:20,25` | 2 | 1 of 2 |
| `sbatch_uthrow_run_5d.sh:20` | 1 | yes |
| `sbatch_uthrow_run_5d_fast.sh:21` | 1 | yes |

**THE SILENT POPULATION IS 8, NOT 5 — and the three new ones are on the 5D path**, two of them
**combine** launchers (where `:418` compares archived `slab_seeds` against the estimator seed) and one
the **J28 adopt** launcher. So the ruling's own justification argues for a LARGER diff than the ruling
priced: condition 2 says *"all 26 call sites, not 21 and not 5"*, and the true figure is **26 base + 6
wrapper launchers**, `7` additional invocation lines.

**Why this is held rather than absorbed: the mediator priced the cost explicitly and called it larger
than either option I had priced. A lane that discovers the price was still too low and proceeds anyway
has converted a ruling into an estimate.** Re-priced and returned for confirmation; nothing edited.

**This is `BEN-235`'s species at the top of the chain and the third instance in this thread of a
population selected by a pattern that cannot see its relevant members** — D's *"a search for a token
cannot enumerate the callers that omit it"*, `Assistant`'s *"my population was selected by the very
property I was reasoning about"*, and now a name-spelling that excludes the production path. **All three
were found by changing the predicate, never by widening the corpus.**

## 7. STATUS

**Gate: CLEARED** (header). **Keys: `D` and `Assistant`, both YES, both against seven items, each with
required changes now folded in above.** Both state explicitly that a key is a statement about the merits
and not an authorisation.

**RULED, and the build is HELD ON A RE-PRICING — see §6b.** The mediator ruled: remove `--seed`, both flags REQUIRED with no parser default, all call sites edited in the same diff, D's (iii) subsumed by construction. **§6b shows the priced population excluded the 5D wrapper and the true silent population is 8, not 5.** Returned for confirmation.

**Superseded, kept for the record: the `--seed` fate (§3a / D's (ii)).** Joseph routed it —
*"Ask the personal orchestrator"* — so it is with the mediator. D requires removal; `Assistant` expressed
no preference; the unsafe option (retain meaning only one of the two roles) is excluded by both keys.
**D's part (iii) applies either way**: the 5 no-seed invokers get explicit seeds, so that after the diff
no invoker depends on a default.

**NOT authorized here and not asked for:** the `39.223` A100-h + `55.337` CPU task-h run, and adoption.

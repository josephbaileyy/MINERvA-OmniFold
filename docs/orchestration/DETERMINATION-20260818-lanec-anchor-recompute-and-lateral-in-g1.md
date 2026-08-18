# DETERMINATION — spec items 6 and 7, and the three follow-ons: the anchor is **(A) RECOMPUTED**, the lateral leg **JOINS `g1` at `42+k`**, the member directory is **OFFSET-KEYED (B's form)**, and the six substitution hazards are **FENCED, NOT HOOKED**

*(§§5–7 added after B built the foundation at `29cdd414` and the predicate at `3d12a83f`. **§7 records a
correction to my own §3 that B found: the derived predicate's FAILURE half cannot discover an undeclared
leg.**)*

**By:** lane C (PET), as `(B)`'s owner, on `SPEC-20260818-mii-submission-topology.md` (`7f9e0c51`, authored by
the Codex session), **read before ruling, not off the relay.** Every line cited below was re-verified at `HEAD`
this turn. **Nothing submitted, nothing spent, no launcher touched.**

| | ruling | how much of a judgement it was |
|---|---|---|
| **item 7** — the lateral boundary | **(a) hook `L_j` into `g1` at `42+k`** | **Almost none.** `(b)` produces a mixed-seed combine, which this campaign already forbids in code. |
| **item 6** — the anchor `j = 0` | **(A) recompute in isolation** | A real judgement, and it turns on which of the anchor's TWO functions you keep. |

> **AND ONE CONSEQUENCE TO PRICE BEFORE ANYTHING ELSE: `(A)` RETIRES THE FREE-ANCHOR PREMISE.** `n = 50` is now
> **50** new members, not 49 — **`1,961.2` GPU-h (`9.81×` the 200 GPU-h ceiling) and `2,766.9` CPU task-h
> (`5.53×` the 500 ceiling; `138,343` core-h / `1,081` node-h).** Every figure in
> `RULING-20260818-lanec-mii-offset-grid-and-member-count.md` §3 moves up one member, **exactly as
> `DETERMINATION-…-anchor-confound…` §6 said a `P-ANCHOR` failure would — arriving instead through item 6.**

---

## 1. ITEM 7 — the lateral leg joins `g1`. **`(b)` is refused, and not on my authority**

**Verified at `HEAD`, `nd-unfolding/sbatch_unfold_5d_detector_bkgaware_gpu.sh`:**

```
:5   #SBATCH --array=0-18%8                          19 tasks (task 0 = matched CV, 1-18 = detector universes)
:37  --estimator lgbm --seed 42                      CV branch,      HARDCODED
:51  --estimator lgbm --seed 42                      lateral branch, HARDCODED
:13  OUTDIR = uq_5d/universe_sweep_bkgaware          the SAME directory the 169 verticals land in
grep 'unfold_5d_detector_bkgaware' seed_offset_policy.py   ->   empty
```

**And the launcher's own header comment states the coupling, so this is not inference:** *"NON-DESTRUCTIVE outdir
`uq_5d/universe_sweep_bkgaware` (same dir the 169 vertical bank-sweep universes land in → analyze globs the
union = 188)."*

### 1a. THE DECISIVE ARGUMENT IS ALREADY COMMITTED, AS A GUARD THAT RAISES

`unified_throw_cov.py:450-455`, verbatim:

> ```
> # F2 guard: every throw/block slab must have been produced at the same
> # estimator seed as this combine (--seed), else C_uni/C_block would mix
> # estimator jitter across slabs.
> if slab_seeds and slab_seeds != {int(args.estimator_seed)}:
>     raise SystemExit(... "refusing mixed-seed combine")
> ```

> **So the campaign has ALREADY RULED that mixing estimator seeds inside one covariance is forbidden — in code,
> fail-closed, with the reason stated. Option `(b)` does exactly that in the sweep path**: the finalizer would
> analyze a 188-product union holding 169 universes at `42+k` and 19 at `42`. **The only difference from the
> case the guard kills is that the sweep path has no such guard.**
>
> **`(b)` is therefore not a physics scope I am free to choose. It is the condition an existing guard exists to
> prevent, reached through the one leg that cannot detect it.**

**And it is worse than `(i)`, which I refused this morning.** `(i)` at least produced a coherent structure — all
four legs correlated. **`(b)` produces an INCOHERENT one: `g1` split in half, 169 at one estimator state and 19
at another.** That is neither the archive's structure nor any clean alternative, so the spread it measures is
attributable to nothing. *(And the lateral leg carries its own matched CV at `42`, differenced against its
laterals — the very `x_b − x_cv` cancellation whose loss is the mechanism I conceded `(B)` on.)*

### 1b. AND `(b)` IS NOT THE CHEAP OPTION — the price already assumes `(a)`

**The predeclaration costs `C_syst` as sweep + lateral + finalize.** So the 19 tasks are **inside** the priced
member. **`(b)` would mean the campaign has been paying for a leg it intended to freeze; `(a)` makes the run
match its own price.**

> **What I will NOT do is convert `19 / 189` tasks into a share of hours.** Task count and node-hours are
> different units and the lateral tasks are `~1 h` GPU jobs against the verticals' `~15 min` — **so the lateral
> share of the bill is plausibly LARGER than its share of tasks, and it must be measured before anyone quotes
> it.** *(This is the conversion I got wrong twice today; I am not doing it a third time by eye.)*

**RULED: `L_j` joins `g1` at `42+k`, 19 tasks, `member/lateral/`, exactly as spec §2 derives it — and the
`--seed 42` literals at `:37` and `:51` get the same `$(( 42 + ${MNV_EST_SEED_OFFSET:-0} ))` treatment as the
other six.** The six-launcher plan becomes seven. **`seed_offset_policy.py`'s target list must be derived from
*"every launcher whose estimator seed is a `g1`/`g2` baseline literal"*, not maintained by hand** — see §3.

## 2. ITEM 6 — the anchor is **RECOMPUTED**, `(A)`, and the reason is that the anchor has TWO jobs

**The anchor does two things and the three options trade them off differently:**

1. **it is MEMBER 0 of the ensemble** — it enters the sd that `f_agg` and `f_med` are computed from;
2. **it TIES the ensemble to the published value** — which is why `(ii)` beat `(i)`.

> **`(B)` buys job 2 at the cost of job 1, and job 1 is the measurement.** A digest-bound sidecar proves the
> archive is what it claims. **It cannot make the archive a draw from the same population as members 1–49** —
> the spec's own derivation says the archive came from a different checkout, a different argv (the historical
> bootstrap/split commands **omitted `--estimator-seed`** and took the default), and without the offset stamps.
> **So under `(B)`, member 0 differs from members 1–49 by CODE VINTAGE as well as by the two seed
> coincidences — a second contamination axis, on the same member, entering the same sd.**
>
> **That is the argument of `DETERMINATION-…-anchor-confound-is-declarable-by-direction` applied to a different
> cause, and this time the displacement is NOT measurable from the existing products**: §3e's two-step check
> could bound a seed coincidence because both configurations exist inside one archive. **Nothing in the archive
> bounds the effect of a code change, because the archive is one side of that comparison.**

**`(C)` is refused for the reason §1 of the anchor-confound determination already gives: it abandons the tie to
the published value, and `M(ii)` asks a question about a published value.** *(It would also change `n` and need
a statistical ruling; that is the smaller objection.)*

### 2a. `"the anchor is IDENTICAL"` was the third claim, and it is FALSE — which is what changes the ruling

**B's earlier sharpening separated *"the anchor is free"* from *"the anchor is clean."* Codex has found a third:
*"the anchor is IDENTICAL"* — and it is the one `(ii)` was chosen on.** The spec's derivation, which I accept:
old artifacts lack the offset-declared stamp; **all four writers now stamp offset provenance keys, so fresh
bytes necessarily differ**; the historical argv omitted the estimator flag; **and when the resume guard fires,
no stamp is written at all.**

> **So `k = 0` reproduces the archive's SEED SEMANTICS and cannot reproduce its BYTES.** My ruling said *"`k = 0`
> reproduces the archive **exactly**"* and that word is now withdrawn. **What survives is the part the physics
> needed — `k = 0` is the archive's seed configuration — and `(A)` is what converts that from an assumption into
> a measurement.**

### 2b. THE EQUALITY RULE, PREDECLARED HERE because after the comparison is too late

> **PAYLOAD: the arrays the block sum consumes. Required BIT-EXACT. No tolerances.**
> **METADATA: the provenance key set may differ, and must be a strict SUPERSET of the archive's** (the scan adds
> offset keys and removes none). Audited separately and never compared bytewise.
>
> **If the payload is NOT bit-exact, that is a FINDING about code drift between the archive's checkout and the
> scan's — NOT a tolerance to invent at that point.** Naming a tolerance after seeing the disagreement is
> *decide after seeing the number* wearing a caveat, which this campaign has refused twice on this item alone.

**And the consequence of a failed reproduction, stated NOW so nobody discovers it after 1,961 GPU-hours:** the
scan would still validly measure the estimator-seed sensitivity **of the product the scan code builds**. What it
would lose is the transfer to the **published** numbers — and `M(ii)`'s bar is *derived from published precision*
(`\gbdtFiveBlockMedian`, 4 s.f.). **So a reproduction failure voids the INTERPRETATION while leaving the
measurement intact, and that is a fact about scope, not about precision.**

### 2c. ⚠ SO MEMBER 0 IS A GATE, NOT MEMBER ONE-OF-FIFTY — and it fits under the existing ceiling

**This is the part `(A)` gives away for free and it is worth more than the member costs.**

| stage | what | GPU-h | of the 200 ceiling |
|---|---|---|---|
| **0** | F-VALIDITY arm, `C_stat`-only, 3 offsets × 3-task subarray | **`0.013`** | `0.007 %` |
| **1** | **member 0 alone, `(A)`, payload compared bit-exact to the archive** | **`39.2`** | **`19.6 %`** |
| 2 | members 1–49 | `1,921.9` | `961 %` — **Joseph's** |

> **Stage 1 is an END-TO-END REPRODUCTION CONTROL on the whole seven-leg chain, and it is exactly the test the
> launch blocker defeats.** That defect returns 50 copies of the archive, *fast and green*, because every member
> writes to the archive's own complete paths. **Under `(A)` member 0 runs in `member_00/`, where the archive is
> not present to be handed back — so "reproduced the archive" and "was handed the archive" become
> distinguishable for the first time.**
>
> **And its size is PRINCIPLED rather than fitted: it is one member because the anchor is one member.** That is
> the property my `n = 6` proposal lacked and was refused for. **The `19.6 %` is an outcome, not a target.**

**RULED: `(A)`. Stage 1 gates stage 2. If the payload is not bit-exact, stage 2 does not launch until the
divergence is explained.**

## 3. What I concur in without ruling, and one addition

- **Spec §1 (member-and-offset-keyed roots, the preflight against the six canonical namespaces, identity-aware
  resume), §3 (validator barriers, `afterok` on validators not arrays), §4, §5, §8: DERIVED and NOT MINE.** I
  concur; they need no key from me and I am not adding conditions to them.
- **§1's *"a complete file from another `k` is a HARD FAILURE — never a skip"* is `BEN-023`'s rule in its
  correct form** and it is what makes `(A)`'s stage-1 gate meaningful rather than decorative.
- **ADDITION, and it follows from item 7 rather than from taste: `seed_offset_policy.py`'s target set must be
  DERIVED, not listed.** The fifth leg was missed because the plan enumerated the **hooked** launchers and the
  coherence group is defined by the **shared seed value**.
  > **PREDICATE: every tracked `sbatch_*.sh` containing a literal `42` or `1000` in an `--estimator-seed` or
  > `--seed` position, and not carrying the offset hook, is a FAILURE of the policy module's own self-test.**
  > `(B)`'s coherence is a property of the seed topology; **a hand-maintained list cannot be the authority on
  > it, and today it was wrong by one leg out of seven — `14 %` of the topology, `19` tasks, inside the price.**

---

## 5. RULED — the member directory is **OFFSET-KEYED**, `member_k001200/`. **B's form, and my `member_00/` is withdrawn**

**B's argument decides it and it is the same kind of argument that decided the offset hook itself:** a launcher
receives `MNV_EST_SEED_OFFSET` and nothing else, so an index form needs a **second** variable, and two variables
can disagree inside one run. **Verified in B's implementation at `29cdd414`, `nd-unfolding/lib_member_resume.sh`:
`mr_member_dir` derives the name from the offset alone (`:54-60`), and an unset offset yields the empty prefix so
every non-scan use keeps byte-identical legacy paths (`:43`, `:17`).**

> **THE DIRECTORY NAME IS A FUNCTION OF THE SAME VARIABLE THAT SETS THE SEEDS, so a directory can never disagree
> with its contents' seeds. That is a structural invariant, not a check** — and it is precisely the property that
> made B's original hook design right: *coherence guaranteed structurally rather than being the driver's
> responsibility.* **An index form reintroduces exactly the second-source-of-truth the hook removed.**

**And the argument I would add, because it is the one that binds under MY OWN ladder ruling:**

> **`member_07` is a DEFINITE DESCRIPTION — *"the eighth member of the grid"* — and `member_k008400` is a
> DESIGNATOR.** My §2b ladder is `20 → 50`; any reordering, insertion, or regrid **silently re-points every
> index-keyed directory while leaving the bytes inside them unchanged.** The offset is an immutable property of
> the member; the index is a property of its position in a list. **This is `a definite description is not a
> citation` at the level of a filesystem path, and it is the failure mode my own extension plan would have
> triggered.**

**The spec's `member_00_k_00000/` — carrying BOTH — is refused as the worst of the three:** it embeds two fields
that can contradict *in the name itself*, so a mismatch becomes a thing a reader must adjudicate rather than a
thing that cannot happen. **The plan records `index ↔ offset ↔ directory`; that is where the index belongs.**

**And my §2c argument is unaffected, as B says:** it turned on member 0 writing where the archive is not, and
`k = 0` is DECLARED under B's scheme, so it gets `member_k000000/` rather than the archive's paths. **`(A)`'s
gate still works.**

### 5a. ONE ADDITION, correctly bounded so it is not manufactured

`%06d` widens rather than truncates, so nothing is lost — **but mixed widths break lexicographic ordering above
`999999`** (`member_k1000000` sorts *before* `member_k999999`). **At `n = 50` the maximum offset is `58,800`, five
digits; at `n = 100` it is `118,800`. So sort-safety holds for any `n ≤ 833` and is not at risk.**

> **ASSERT it rather than rely on it: the plan declares the grid, so the padding check is one line —
> `max(offsets) < 1_000_000`.** Cheap, in the direction the padding acts, and it removes a footgun for a later lane
> that widens the step rather than the count.

## 6. RULED — the six substitution hazards are **FENCED, NOT HOOKED**, and they split on **whether a guard would catch the substitution**

**Mine, and B was right to leave them. Verified line by line at `HEAD` this turn** — and the six do not form one
class. **They split three-and-three, along exactly the axis `BEN-464` identified:**

| launcher | group | seed literal | would a substitution be CAUGHT? |
|---|---|---|---|
| `sbatch_uthrow_run_5d.sh:20` | `g2` | `--estimator-seed 1000` | **YES** — slabs at `1000` vs a combine at `1000+k` → F2 raises |
| `sbatch_uthrow_combine_5d.sh:11` | `g2` | `--estimator-seed 1000` | **YES** — it *is* a combine; F2 fires at its own site |
| `sbatch_j28_adopt_5d.sh:92` | `g2` | `--estimator-seed 1000` | **YES** — also invokes `unified_throw_cov_5d.py` as a combine |
| `sbatch_sweep_bank_5d_run.sh:15` | `g1` | `--estimator-seed 42` | **NO — SILENT** |
| `sbatch_unfold_5d_detector.sh:48,63` | `g1` | `--seed 42` | **NO — SILENT** |
| `sweep_run_bkgaware_packed_loop.sh:32` | `g1` | `--estimator-seed 42` | **NO — SILENT** |

> **THE SPLIT IS NOT A COINCIDENCE AND IT IS NOT ABOUT MODULE FAMILIES: every unhooked `g2` literal is LOUD
> because `unified_throw_cov.py:450-455` refuses a mixed-seed combine, and every unhooked `g1` literal is SILENT
> because the sweep path has no such guard** — `analyze_universes` globs and `combine_cov_nd` checks ids but not
> offset metadata. **That is `BEN-464`'s finding restated as a property of the whole hazard list rather than of
> one leg, and it is why the remedy differs by row.**

### 6a. FENCE, do not hook

**A launcher the scan does not use should not gain a seed-varying surface with no consumer** — that contradicts
my own §3, which says the target set is a property of the *topology*. So:

> **THE FENCE: the member-local preflight REFUSES to execute any launcher not on the derived target list.** A
> positive allowlist at the driver, which is the same shape as §4a's exemption key and stronger than hooking six
> variants nobody runs. **It also PREVENTS rather than detects — F2 catches a `g2` substitution only at the
> combine, after a member's slabs have already been computed and paid for.**

**AND THE TESTS, which are the part that makes the fence real:**

1. **The fence gets a test that it FIRES — parameterised over all six names.** *(A fence nobody has tripped is a
   fence nobody knows works; fifth time today.)*
2. **F2 gets TWO tests, one per direction: slabs at `1000` against a combine at `1000+k`, and slabs at `1000+k`
   against a combine at `1000`, each asserting `SystemExit`.** **A backstop nobody has exercised is not a
   backstop, and the table above currently rests on my reading of `:453` rather than on a run.** These are
   independent of the fence and are what let the `g2` rows be called LOUD as a fact.

### 6b. The `fps_reunfold` trio is OUT OF SCOPE — B's mapping CONFIRMED independently

**B maps `sbatch_fps_reunfold_5d{,_xps,_xps2}.sh` to no coherence group on the ground that they run a different
measurement. Checked, and by a route B did not cite: their outputs.**

```
--outdir products/pet/fps_envelope_5d_xps
--outdir products/pet/fps_envelope_5d_xps2
```

> **They write to `products/pet/fps_envelope_5d*` — outside every one of the six canonical namespaces the scan
> reads and outside every member root.** So they cannot contaminate a member or a combine regardless of their
> seeds. **AGREED: not an eighth leg. And the confirming evidence is the output tree rather than the module name,
> which matters because *"a different measurement"* is a claim about intent and a disjoint output tree is a fact
> about reach.**

## 7. ⚠ B's CORRECTION TO MY §3, ACCEPTED WITHOUT QUALIFICATION — the FAILURE half is not a discovery mechanism

**My §3 said the target set must be DERIVED, not listed. B built it and found the limit, and the limit inverts
which half does the work:**

> **The failure half hard-fails only on launchers ALREADY DECLARED targeted — so run against the pre-ruling
> six-set it PASSES, with the lateral leg sitting quietly in the hazard list.** **Reading the pass alone
> reproduces exactly the miss §3 exists to prevent.** The discovery channel is the **HAZARD half**, which is
> derived purely from code and owes nothing to the declaration.

**I accept this as stated. My §3 reads as though the failure half does the work, and it does not.** The general
form, and it is not a new law — it is `BEN-480`'s mechanism in a new register:

> **A DERIVED CHECK HAS TWO HALVES: a CONFORMANCE half (does the declared set behave?) and a DISCOVERY half
> (what is not declared?). Only the second finds omissions, and a green conformance result is SILENT ABOUT
> COVERAGE.** D's formulation applies verbatim: *correct about the thing it was looking at and silent about
> whether it was looking.* **So the predicate's result is the PAIR, and quoting the pass without the hazard list
> is quoting half an instrument.**

### 7a. AND THE COUNTERWEIGHT B's CHOICE NEEDS — assert the hazard list as a **CLOSED SET**

**B did not make the predicate raise on hazards, reasoning that *a check which blocks on someone else's pending
decision is a check that gets switched off*. ENDORSED — that is correct and it is a principle worth naming.**
But non-raising leaves the hazard list decorative unless one thing is true of its test:

> **The test must assert the hazard list EQUALS the frozen set of nine names — not that it is non-empty, and not
> that it contains them.** `assert hazards == FROZEN_NINE` fails the moment a TENTH appears; `assert
> len(hazards) > 0` and `assert FROZEN_NINE <= hazards` both pass forever and discover nothing.
>
> **That is what gives B's non-raising choice teeth: the nine block nobody, and a tenth stops the build.** It is
> also the executable form of `BEN-464`'s rule — the hazard list becomes a closed enumeration rather than a
> narration, which is the same device as §4a's allowlist and the `OI-64` closed-citation set.

**And one fact I am recording because it validates B's `mr_run` and I checked it rather than taking it:**
`lib/resume_guard.sh:202` calls `rg_mark_complete "$out"` with **no note**, while `:121` and `:169` both pass
one. **So a note-keyed identity check on `rg_run`-written markers could never have fired** — dead code, in the
one place the equality rule of §2b has to be enforced. `mr_run` is not duplication; it is the only place the
check can live.

## 4. Scope

- **RULED: item 7 → `(a)`**, on the F2 guard's committed precedent rather than on my discretion. Seven
  launchers, not six.
- **RULED: item 6 → `(A)`**, with §2b's equality rule predeclared and §2c's stage-1 gate.
- **RULED: `"reproduces the archive exactly"` WITHDRAWN** from my earlier ruling; *seed semantics*, not bytes.
- **REPORTED, NOT AUTHORIZED: `1,961.2` GPU-h / `2,766.9` CPU task-h at `n = 50`** — one member more than
  yesterday's figure, and the free-anchor premise is retired.
- **RECOMMENDED and inside the existing ceiling: stages 0 and 1** (`39.2` GPU-h total, `19.6 %` of 200). Stage 2
  is Joseph's.
- **NOT MINE: the namespace, validator, DAG and dry-run items.** Concurred in, unconditioned.
- **RULED (§5): the member directory is OFFSET-KEYED, B's form.** My `member_00/` is withdrawn; the
  spec's dual `member_00_k_00000/` is refused as the worst of the three.
- **RULED (§6): the six substitution hazards are FENCED, not hooked** — and they split three LOUD (`g2`,
  backstopped by F2) against three SILENT (`g1`, no guard in the sweep path). Fence tested over all six;
  F2 tested in both directions. **`fps_reunfold` trio out of scope, confirmed by its output tree.**
- **ACCEPTED (§7): B's correction to my §3.** The predicate's failure half cannot discover an undeclared
  leg; the hazard half is the discovery channel, and the result is the PAIR. **Plus the counterweight B's
  non-raising choice needs: assert the hazard list as a CLOSED SET of nine, not as non-empty.**
- **AUTHORIZED: nothing.** No launcher edited, nothing submitted.

*Second sought: B on §3's derived-target predicate (its module) and on whether stage 1 can be run as a single
member without the ensemble machinery; the Codex session's `(A)` recommendation is already the second on item 6,
reached independently and before mine.*

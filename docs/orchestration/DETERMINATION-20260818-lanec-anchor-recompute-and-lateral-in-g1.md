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

---

## 8. RULED — **a member is `(b)`, a full parallel pipeline THROUGH ADOPTION** — because the published quantity passes through an elementwise `maximum`

**`(a)` is refused, and not on scope taste. One line of committed code decides it**, the same way `:450-455`
decided item 7:

> **`nd-unfolding/adopt_unified_5d.py:108`**
> ```
> s_adopt = np.sqrt(np.maximum(vu, vb))     # conservative: never below block baseline
> ...
> g[m] = s_adopt[m] / sb[m]                 # >= 1
> C_new[i, :] += (g[i] * g - 1.0) * C_vert[i, :]
> ```

**Adoption contains a PER-BIN ELEMENTWISE MAXIMUM, and it feeds a per-bin rescaling of the vertical covariance
that reaches every off-diagonal.** So:

1. **`f_agg` and `f_med` are functions of the ADOPTED object, not of the producers.** `block_sum` is a trace and
   `σ_i` a diagonal **of the adopted total**, and `\gbdtFiveAdoptTrace` says so in its own name.
2. **A maximum does not commute with taking a spread.** Which branch wins at bin `i` can DIFFER BETWEEN MEMBERS,
   so two members can sit on opposite sides of a kink. **A spread assembled from per-block traces and diagonals
   is the spread of a DIFFERENT quantity.**
3. **And its direction relative to the true spread is NOT ESTABLISHED.** A max clamps jitter where `vb` wins and
   passes it where `vu` does — but `vb` is itself an unfold at the estimator seed, so both branches jitter and
   `sd(max(X,Y))` is not generally ordered against either. **Had the direction been known to be conservative,
   `(a)` would have yielded a usable upper bound under §5's rule that MET may be reached on a bound. It is not
   known, so it does not.**

> **RULED: `(b)`. A member runs producers → combines → 188-analyzer → ADOPTION, and produces the member's
> `(block_sum, {σ_i})` plus the terminal receipt spec §4 requires.**

### 8a. WHERE THE CUT IS, because `(b)` as stated is slightly more than `M(ii)` needs

- **IN:** the four combines, the 188-universe analysis, **adoption** (the max is there), and `MVFINAL_j`.
- **OUT:** any write to a canonical path — spec §1 already forbids it — and the **publication** aspects of the
  finalizer. **`M(ii)` needs the NUMBER out of the adopted object, not 50 publishable adopted covariances**, and
  B's instinct on that half was right even though its conclusion was not.

### 8b. ⚠ AND THE ORDER-OF-MAGNITUDE COST CLAIM IS NOT SUPPORTED — measured, with its unit

**`EXTENT-20260817-2850-a100h-scope-and-missing-legs.md:86`, verbatim:**

```
RE-SEED = 23.840 sweep(169) + 14.2075 lateral+CV(19) + 1.030 finalize(1) = 39.078 A100-h  [189 tasks]
```

> **`finalize` IS ALREADY INSIDE THE PRICED `39.078`, at `1.030` A100-h — `2.6 %` of the GPU column.** The
> combines and the analyzer are matrix algebra, not unfolds. **So memberizing the consumers does not multiply the
> bill; it lands almost entirely on the CPU column — the axis B measured as BINDING (`26.4 %` of remaining CPU
> at `n = 50`) rather than the GPU one (`0.75 %`).**
>
> **So *"changes the cost by an order of magnitude"* needs its unit before it is quoted, and on the GPU column it
> is false.** I am not asserting the CPU figure either — **it must be measured, and `(b)` should not be priced by
> anyone from the GPU number.**

### 8c. AND THE SAME LINE VINDICATES §1b's REFUSAL TO CONVERT TASKS INTO HOURS

**`lateral+CV(19)` is `14.2075` of `39.078` — `36.4 %` of the GPU column from `10.1 %` of the tasks, a factor of
`3.6`.** §1b declined to derive an hour share from a task share and said the lateral share *"is plausibly LARGER
than its share of tasks."* **Measured: larger by 3.6×.** *(It was already priced, so nothing moves — but item
7(a) is a third of the GPU bill rather than a tenth, and anyone reasoning from `19/189` would have been wrong by
that factor.)*

## 9. RULED — the fence lives **INSIDE EACH LAUNCHER'S PREFLIGHT**, not in the driver. **My §6a ground is withdrawn**

**Accepted without qualification: as built, the fence intercepts nothing.** `preflight_launcher()` is called only
on names drawn from the driver's own allowlist — B's source comment *"the fence, applied to the plan's own set"*
is the admission written into the code — and the driver does not submit, so the printed commands execute outside
it entirely. **`agy` flagged it as its one UNABLE-TO-CHECK and `codex-school` confirmed it, independently.**

> **So my §6a ground — *"it PREVENTS where F2 only DETECTS"* — IS WITHDRAWN. As built it does neither.**

**RULED: the guard goes in each launcher, at the top, keyed off the environment.** Not driver-owned submission,
and not a submit-time wrapper.

> **THE DECIDING PROPERTY: the hazard is SOMEONE RUNNING THE VARIANT, so the fence must live where the wrong
> thing would run.** A driver-side fence is bypassed by *precisely the action it exists to prevent* — a human, a
> resubmit, or a line copy-pasted out of a log. **A launcher that refuses itself cannot be bypassed by how it was
> invoked.**

**Shape:** the six hazard launchers each call a library helper at the top — *if `MNV_EST_SEED_OFFSET` is declared
(we are inside a scan member) and this launcher is not a declared target, FAIL*. The seven targets simply do not
call it, and `unset` remains the archive path for everybody.

- **It requires NO authority move, which is the second reason to prefer it. I am NOT ruling that the driver owns
  submission** — the mediator holds submission deliberately and this fence does not ask for it.
- **The fence-fires test I required in §6a gets EASIER, not harder:** a launcher's self-refusal is testable with
  real bash and no Slurm, which is the harness B already has.
- **And the two halves compose:** the derived predicate's HAZARD half discovers launchers that need the guard;
  the guard prevents execution; the closed-set assertion (`hazards == FROZEN_NINE`, §7a) fails when a tenth
  appears. **Discovery, prevention, and non-staleness, none of them relying on a chokepoint.**

## 10. Three additions that fall out of my own earlier rulings, and one shape appearing for the third time

### 10a. The padded offset is **OUTPUT-ONLY** — bash reads `001200` as OCTAL

**Measured by the mediator: `001200` gives seed `682`, directory `member_k000640`, and python provenance `1200`
— three different numbers from one input.** `$(( 42 + 001200 ))` is base-8.

> **This lands on MY §5 ruling, because §5 is what put a zero-padded number into a name.** The padded form is a
> **rendering** and must never be an **input**: `MNV_EST_SEED_OFFSET` must be rejected if it carries a leading
> zero, or forced base-10 with `$((10#$k))` at the single validation point B already has. **A name that cannot be
> read back is a name that will be.**

### 10b. §2b's equality rule must pin the SOURCED SHELL LIBRARIES, not only the Python

**279 files hardcode `REPO` and 85 source `lib/resume_guard.sh` through it — so a frozen deployment does not
freeze its own resume semantics.** B's synthesis, endorsed: **the campaign's hard rules are enforced in the
libraries and bypassed in the Python.**

> **So the *code digest* that §2b's bit-exact comparison binds must cover the sourced shell libraries.** Otherwise
> the anchor comparison is pinned to a basis that excludes the code deciding whether the anchor RAN — and that is
> the exact gap §10c describes.

### 10c. My §2c gate was defeated once already — and that is this shape's THIRD appearance

**The identity-aware resume ACCEPTED THE ARCHIVE:** the gate required a marker note beginning
`est_seed_offset=`, every archive marker predates that note, so it fell through to a size/mtime skip. **Member 0
was handed the archive — the single outcome §2c exists to exclude.**

> **Three instances of one shape today: the original blocker (fixed literals → resume-skip → 50 copies of the
> archive); this one (identity gate → note absent → size/mtime skip); and §8's consumer layer (memberized
> producers, canonical globs → the finalizer reads the archive).** Each is *fast, green, and indistinguishable
> from success.*
>
> **THE INVARIANT, which is `BEN-023` stated for this campaign: EVERY LAYER THAT COULD SATISFY A MEMBER FROM
> PRE-EXISTING BYTES MUST FAIL CLOSED ON AN ABSENT POSITIVE DECLARATION.** An absent stamp is not a weak yes; it
> is a no. **Falling through to size/mtime is *validate existence, not completeness* wearing a new hat.**

### 10d. And my item 7(a) was UNDER-SPECIFIED — mine to own

**`build_plan` cannot build any plan: it textually demands `--estimator-seed` while the lateral correctly uses
its native `--seed`, and has no `LEG_BASELINES` entry.** My §1 named the launcher edit (`:37`, `:51`) and said
nothing about the driver's recognizer.

> **RULE: a ruling that adds a leg must name every place the new leg's SHAPE differs from its siblings' — flag
> name, baseline table, recognizer, validator population.** *"Same treatment as the other six"* is a definite
> description, and the lateral is the one leg for which it is false.

---

## 11. R3 RULED — the payload enumeration. **And TWO CLASSES WERE NOT ENOUGH: my own §2b was missing one, and the missing one is where the danger was**

**B is right that deciding at comparison time is the move §2b refused. Here is the enumeration — and producing it
found a defect in the rule that generated it.**

### 11a. ⚠ THE THREE-CLASS RULE, replacing §2b's two

`seedscan_split.py:84` writes `train_frac`. **It is not payload — it is not a measured value. It is not
provenance — a difference in it means the two products are not comparable at all.** Under a two-class rule it
gets filed as provenance and ALLOWED TO DIFFER. **And the same is true of `estimator_seed`, which LOOKS like a
stamp and IS the thing that makes the member the anchor.**

> **THREE CLASSES, and the classifier is a test rather than a list, because a list goes stale and a test does
> not:**
>
> | class | test | comparison rule |
> |---|---|---|
> | **PAYLOAD** | it is a MEASURED VALUE | **BIT-EXACT. No tolerances.** |
> | **CONFIGURATION** | changing it changes WHAT WAS MEASURED | **EQUAL. A difference is a HARD FAILURE, not a superset allowance.** |
> | **PROVENANCE** | it records only the CIRCUMSTANCES of the measurement | superset allowed, audited separately, **never compared bytewise** |
>
> **AND FAIL-CLOSED ON ANY KEY MATCHING NO CLASS.** That is what makes the enumeration safe to age: a key added
> later is a hard failure until someone classifies it. **Same invariant as §10c — an absent declaration is a no,
> not a weak yes.**

### 11b. The enumeration, read from the writers at `HEAD` this turn

| product | PAYLOAD (bit-exact) | CONFIGURATION (must be EQUAL) | PROVENANCE (superset) |
|---|---|---|---|
| `boot_nd_5d/res_boot_*.npz` `bootstrap_nd.py:49` | `xsec_flat`, `shape`, `total_xsec` | `seed`, `estimator_seed` | `est_seed_offset_declared`, `est_seed_offset` |
| `seedscan_split_5d/res_split_*.npz` `seedscan_split.py:84` | `xsec_flat`, `shape`, `total_xsec`, **every key unpacked from the `proj` mapping** | `split_seed`, `estimator_seed`, **`train_frac`** | `est_seed_offset_declared`, `est_seed_offset` |
| `uthrow_slabs_5d_sb/*.npz` `unified_throw_cov.py:273` | `xs` | `throws`, `flux_u`, `estimator_seed`, `draw_seed` | `est_seed_offset_declared`, `est_seed_offset` |
| `block_slabs_5d_sb/*.npz` same writer family | the unit `xs` | unit `labels`/`kinds`, `estimator_seed`, `draw_seed` | `est_seed_offset_*` |

**`total_xsec` is PAYLOAD and is also an INGREDIENT CHECK**: it must equal `total_xsec(xsec_flat)` recomputed
from the same file. **A product whose scalar disagrees with its own array is a defect the bit-exact comparison
would otherwise pass on both sides.** `BEN-077`.

### 11c. AND THE ROOT SIDE IS NOT ENUMERATED HERE — said rather than papered over

**Stage 1 compares the archive's ROOT products too** (`unified_throw_cov_5d.root` at `2.67 GB`, and the sweep
universes' `.root`), so they are in scope and I have **not** read their writers.

> **The three-class rule of §11a covers them unchanged — it classifies by what a key IS, not by container
> format.** B produces the ROOT-side enumeration by applying it to those writers. **Stage 1 cannot gate until
> that enumeration exists, and I would rather block on a named gap than ship a rule that silently covers half the
> comparison.**

## 12. R1 RULED — **`_sb` IS CANONICAL FOR BOTH LEGS**, and there is exactly ONE wrong literal

**Not a judgement — the receipt says so.** `receipt_construction_contract_5d.py:313-314`:

```
"throw_slabs_sb": "uq_5d/uthrow_slabs_5d_sb/uthrow5d_slab_*.npz",
"block_slabs_sb": "uq_5d/block_slabs_5d_sb/block5d_*.npz",
```

**Corroborated four ways:** `slab_manifest_20260806.json` carries the `_sb` paths **with digests**;
`sbatch_uthrow_combine_5d_fast.sh:22,24` globs `_sb` for **both** legs; `sbatch_uthrow_run_5d_fast.sh:19,29`
**writes** `uthrow_slabs_5d_sb`; and `CORRECTED_UQ_PRODUCTION_STATUS.md:483` records the headline full combine as
throws + `block_slabs_5d_sb`.

> **So the consumer is RIGHT and `sbatch_uthrow_block_5d.sh:33,38` is the single misaligned literal in the
> chain.** `AUTONOMOUS_LOG_20260805.md:48` measured it: **`block_slabs_5d` holds 8 files, `block_slabs_5d_sb`
> holds 36.** The tracked block producer has been writing a stale partial that nothing consumes.

**RULED: the member's block producer writes `member_kXXXXXX/uq_5d/block_slabs_5d_sb/`, matching the member's
combine.** That resolves it for every member and makes the combine's zero-slab `SystemExit` unreachable.

> **AND B IS RIGHT NOT TO REPOINT THE UNSET LITERAL — but the reason is the OPPOSITE of the one given.**
> Repointing would not *"move archive behaviour"* in the sense of departing from the archive; the archive IS
> `_sb`. **It would let a non-scan run of that launcher write INTO THE LIVE ARCHIVE DIRECTORY**, which is a
> destructive edge on 124 receipt-bound slabs. **So: leave the unset path alone, and record the tracked
> producer's wrong literal as a PRE-EXISTING defect needing its own change and its own authorization — not
> folded into the scan.**

### 12a. ⚠ AND A FLAG ON `P-ANCHOR`, which I am routing rather than resolving

**`P-ANCHOR`'s listing reported `uq_5d/uthrow_slabs_5d/*.npz → 160`. The construction contract binds
`uq_5d/uthrow_slabs_5d_sb/`.**

> **If those are two directories, then either `P-ANCHOR` counted a NON-CANONICAL one or the contract is stale —
> and the first would mean the availability check verified products the archive does not use.** Cheap to settle
> with one `ls` on the cluster, and it should be settled before stage 1 compares against anything. **Not mine to
> resolve; named because a `160 ✓` against the wrong path is the same shape as everything else today: correct
> about the thing it was looking at, silent about whether it was looking at the right one.**

## 13. R2 RULED — `MVFINAL_j` is a **RECEIPT**, digest-bound. But the CITABLE artifact is the ENSEMBLE receipt, and that is what the verifier learns

**A thing that gates admission must be verifiable or the gate is decorative** — spec §4 says *"no member is
admitted without this terminal receipt,"* so it cannot be a summary. **And `BEN-077` settles the form: every
derived quantity ships its ingredients.**

> **RULED: 50 member receipts, each digest-bound over its member's products; ONE ensemble receipt that binds all
> 50 by digest and carries the predeclared spread metrics.** **The ensemble receipt is the citable artifact; the
> member receipts are its INGREDIENTS.**
>
> **So `verify_receipt_artifacts.py` learns ONE new path shape, not fifty.** It verifies the ensemble receipt;
> the ensemble receipt's own verification walks the 50 member digests. **That satisfies `BEN-077` at the citable
> boundary with the minimum scope growth, and it is the answer to B's question: the verifier does not need to
> learn member paths, because nothing outside the scan should ever cite a member receipt directly.**

*(Corollary worth stating: a member receipt that is never cited outside the scan is exactly why it must still be
digest-bound. It is the positive declaration §10c's invariant demands, and the three failures today were all a
member satisfied WITHOUT one.)*

## 14. R4 RULED — **YES, and record the OPERANDS as well as the winner.** B's is the best question in the batch

**My §8 argument for `(b)` was that `np.maximum(vu, vb)` does not commute with a spread and that two members can
sit on opposite sides of a kink. B is right that diagnosing that later REQUIRES the record, and that it is
impossible to reconstruct** — adoption consumes `vu` and `vb` and the archive keeps neither per member.

> **RULED: per member, adoption records the per-bin winner mask `vu > vb`, AND `vu` and `vb` THEMSELVES.**
> Three arrays of ~285 floats; the cost is not measurable against a member.
>
> **The mask alone says WHICH branch won and not BY HOW MUCH — and "how much" is what identifies members sitting
> NEAR the kink, which are precisely the members whose jitter the max rectifies.** `BEN-077` again: `s_adopt` is
> derived from `(vu, vb)`, so it ships them.

**AND IT IS MORE THAN A DIAGNOSTIC — it is the TEST OF MY OWN RULING'S PREMISE, which is why I would take it at
more than a small cost:**

> **If all 50 members turn out to share one branch pattern, the max never switched, the spread is effectively one
> branch's, and `(a)` would retrospectively have been sufficient.** If the patterns differ, the kink is live and
> the number must be read with that in mind. **Either way the scan reports whether the non-linearity I refused
> `(a)` over actually bit — and a ruling that ships the evidence against itself is worth more than one that does
> not.**

*(And a note on `analyze_universes_5d.py:load_flat:48-57`: `not f or f.IsZombie()` without `kRecovered` accepts a
truncated member product, which **does** block under §10c as literally written — a member satisfied from
incomplete bytes. The audit lane's rider is worth keeping: `not f` is unreachable under PyROOT 6.28 because
`TFile.Open` raises rather than returning null, **so a guard that reads as two-clause belt-and-braces is
single-ply** — and the surviving clause is the weaker of the two.)*

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
- **RULED (§8): a member is `(b)` — producers through ADOPTION**, because `adopt_unified_5d.py:108`'s
  elementwise `np.maximum` does not commute with a spread, and its direction is not established. Cut at
  adoption; no canonical writes, no publication. **And the order-of-magnitude cost claim is unsupported:
  `finalize` is already `1.030` of the priced `39.078`, so the change lands on the CPU column.**
- **RULED (§9): the fence lives INSIDE EACH LAUNCHER**, keyed off the environment. **My §6a *prevents-vs-
  detects* ground is WITHDRAWN — as built it does neither.** I am NOT ruling that the driver owns
  submission.
- **ADDED (§10): the padded offset is output-only (bash reads it as octal); the equality rule must pin the
  sourced shell libraries; and my item 7(a) was under-specified against the driver's recognizer.**
- **RULED (§11, R3): the payload enumeration — and §2b's TWO classes become THREE.** `CONFIGURATION` was
  missing, and `train_frac`/`estimator_seed` would have been filed as provenance and allowed to differ.
  **Fail-closed on any unclassified key. ROOT-side enumeration named as a gap, not papered over.**
- **RULED (§12, R1): `_sb` is canonical for BOTH legs** on the construction contract's authority; the
  member block producer writes `..._sb`; the unset literal stays, as a pre-existing defect with its own
  authorization. **Plus a `P-ANCHOR` flag: it counted `uthrow_slabs_5d/` and the contract binds `_sb`.**
- **RULED (§13, R2): `MVFINAL_j` is a digest-bound RECEIPT; the ENSEMBLE receipt is the citable artifact**
  and binds all 50. The verifier learns one path shape, not fifty.
- **RULED (§14, R4): YES — record the winner mask AND `vu`, `vb`.** It is the test of §8's own premise.
- **AUTHORIZED: nothing.** No launcher edited, nothing submitted.

*Second sought: B on §3's derived-target predicate (its module) and on whether stage 1 can be run as a single
member without the ensemble machinery; the Codex session's `(A)` recommendation is already the second on item 6,
reached independently and before mine.*

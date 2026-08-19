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

### 11d. ⚠ AND A FOURTH PROVISION THE ENUMERATION NEEDS — **the ARCHIVE's schema is not the CURRENT one**

**The corroboration run reported the keys actually present in a canonical `_sb` slab:**

```
['bands', 'flux_u', 'seed', 'throws', 'xs']
```

**Compare §11b's row, which I wrote from the CURRENT writer: `xs`, `throws`, `flux_u`, `estimator_seed`,
`draw_seed`, `est_seed_offset_declared`, `est_seed_offset`.** The archive predates the two-role seed split and
the offset stamps. **So:**

- **`bands` is UNCLASSIFIED by §11b — and the fail-closed rule therefore FIRES, correctly, on real data.**
  Classified now: **CONFIGURATION** — it names the systematic bands the throw varied, and changing it changes
  what was measured.
- **`seed` is ONE key where the current writer has TWO.** The archive's `seed` is the pre-split single seed; the
  member's `estimator_seed` and `draw_seed` were both `1000` in the archive.

> **FOURTH PROVISION: the comparison needs a declared KEY-RENAME/SPLIT MAP for the archive side, and it must be
> written BEFORE stage 1 runs.** Here: archive `seed` → current `(estimator_seed, draw_seed)`, both required
> equal to it. **Without the map, stage 1 fails on a SCHEMA change rather than on a physics difference — and the
> obvious repair at that moment is to demote the keys to PROVENANCE and let them differ, which is exactly the
> failure §11a's third class exists to prevent.** The map is CONFIGURATION-class bookkeeping, not a tolerance:
> **a rename is a claim that two names denote one quantity, and it is falsifiable.**

### 11c. AND THE ROOT SIDE IS NOT ENUMERATED HERE — said rather than papered over

**Stage 1 compares the archive's ROOT products too** (`unified_throw_cov_5d.root` at `2.67 GB`, and the sweep
universes' `.root`), so they are in scope and I have **not** read their writers.

> **The three-class rule of §11a covers them unchanged — it classifies by what a key IS, not by container
> format.** B produces the ROOT-side enumeration by applying it to those writers. **Stage 1 cannot gate until
> that enumeration exists, and I would rather block on a named gap than ship a rule that silently covers half the
> comparison.**

### 11e. THE ROOT-SIDE LISTING — form asked for, and it arrived. **Ruled below; and it found a fifth gate**

**Requested form, and the last two are hazards ROOT has that npz does not:** recursive PATH not object name
(ROOT nests, and a comparison keyed on a bare name compares the wrong pair and reports agreement); CLASS + SHAPE
beside every key (for ROOT the class answers most of the three-class test); **CYCLE COUNTS** — a key re-`Write()`n
without `kOverwrite` leaves `;1`, `;2`, **so it has no single value and a comparator reads the highest silently**,
which is today's shape exactly and cannot happen in an npz; and **BOTH SIDES AS A THREE-BUCKET DIFF** (in both /
archive-only / current-only), because §11d's map is built from the DIFFERENCE and the buckets make its
completeness checkable — anything left over is the fail-closed case.

> **AND A FLAG WITH A NUMBER, because nothing here has carried it: `uq_5d/unified_throw_cov_5d.root` is
> `2,677,168,123 B` measured. Stage 1 compares it ONCE (`2.68 GB`, fine). STAGE 2 STORES FIFTY —
> `133.9 GB` / `124.7 GiB` for that ONE product**, before 188 sweep `.root` per member. **Scratch is purgeable.**
> I am not estimating the rest; **it is a THIRD cost column beside GPU and CPU and it should be measured before
> stage 2.**

### 11f. RULED on the archive's ROOT keys — **the missing SEED STAMP is a fifth gate, and one of the mediator's classifications is wrong in the way that produced the third class**

**Measured: `unified_throw_cov_5d.root` has 9 keys, `5d_xsec_…root` has 4, and NEITHER carries `estimator_seed`,
`draw_seed`, `est_seed_offset`, or any seed key at all.** The `.npz` slabs do; the ROOT products do not.

#### 11f-i. ⚠ AT STAGE 1, A BIT-EXACT PASS AND *"you compared the archive to itself"* ARE THE SAME OBSERVATION

**The mediator leans toward the ensemble receipt's write-time digest binding being sufficient. It is sufficient
for stage 2 and NOT for stage 1, and the asymmetry is the whole point.** Spec §4's ensemble assertion —
*"cross-member product digests DISTINCT wherever stochastic outputs should differ"* — catches a resume-skip that
hands 50 members the same bytes, because 50 identical digests are visible. **Stage 1 has ONE member, so that
backstop does not exist** — and the outcome stage 1 exists to exclude (member 0 handed the archive) produces
**identical digests, which is indistinguishable from a successful bit-exact reproduction.**

> **So the gate cannot distinguish success from the failure it exists to catch, using digests alone. RULED: BOTH
> remedies, because they close different halves.**
>
> **(A) THE MEMBER'S ROOT WRITERS STAMP `estimator_seed`, `draw_seed`, `est_seed_offset` and
> `est_seed_offset_declared`.** A positive declaration in the artifact, which is §10c's invariant. **Compatible
> with §2b: the archive has none, so every stamp is `current-only` and PROVENANCE for the comparison — and a
> ROOT comparison is object-by-object, not file-byte-by-byte, so a stamp cannot break bit-exactness of payload.**
>
> **(B) A PRODUCT CLASS THAT CANNOT CARRY AN IDENTITY STAMP CAN NEVER BE RESUMED.** Until (A) lands, the
> identity-aware resume must never skip a ROOT product — no stamp to read means no skip is defensible. **Fail-
> closed, no writer change, and it is exactly §10c applied to a whole product class.**
>
> **And the reason I will not take *"unlikely, because under member-root-first the paths differ"*: that is the
> argument I refused two rulings ago for glob non-recursion.** A path is not a declaration.

#### 11f-ii. ⚠ AND `dataPOT` IS **CONFIGURATION**, NOT PROVENANCE — a correction, and the SECOND instance of one pattern

**`dataPOT = 1.057394261158926e+21` is the exposure the cross sections were NORMALISED TO. It enters the
arithmetic.** If it differed, every value would be scaled differently. **By §11a's test — *changing it changes
what was measured* — it is CONFIGURATION, and as provenance it would be ALLOWED TO DIFFER and a member
normalised to a different POT would pass.**

> **THIS IS `train_frac` AGAIN, which is the example that produced the third class in the first place. Two for
> two, and both times the key LOOKED like a stamp — so here is the heuristic: A SCALAR THAT ENTERS THE ARITHMETIC
> LOOKS LIKE A STAMP BECAUSE IT IS RECORDED ONCE AND NEVER VARIES.** Constancy is not circumstance. **Ask what
> breaks if it changes, not how often it changes.**

#### 11f-iii. The rest of the classification — confirmed, with the recomputation rule extended

| key | class | note |
|---|---|---|
| `C_unified`, `C_blocksum`, `C_cross`, `hJointMeanShift`, `hXSecND_flat` | **PAYLOAD** | bit-exact |
| `sqrt_tr_unified`, `sqrt_tr_block`, `joint_mean_shift_norm`, `fixed_seed_null_norm` | **PAYLOAD + MANDATORY RECOMPUTATION** | **CONFIRMED as the mediator proposed.** Derived from the histograms in the same file, so `BEN-077` applies exactly as for `total_xsec`: **a product whose scalar disagrees with its own array is a defect a bit-exact comparison passes on BOTH sides.** |
| `globalCompleteness` | **PAYLOAD + MANDATORY RECOMPUTATION** | It IS a measured value — of the product's own completeness — so the test says payload, and recomputation applies for the same reason as the four scalars. It also doubles as `require_completeness`'s operand. |
| `n_throws`, `ndim` | **CONFIGURATION** | declared integers |
| `dataPOT` | **CONFIGURATION** | see §11f-ii — corrected |

#### 11f-iv. ⚠ AND THE BAR'S OWN OPERAND IS NOT IN THIS FILE — a scope gap, flagged

**The predeclared bar is `f_agg = sd(block_sum)/block_sum` against `block_sum = 4.357790406860002e-38`. The
terminal product's scalars are `sqrt_tr_unified = 4.4607819710748654e-38` and
`sqrt_tr_block = 3.4032639007214586e-38`. NEITHER IS THE BAR'S OPERAND.**

> **So `block_sum` lives in some other product — the 5-block assembly — and STAGE 1's COMPARISON SCOPE AS LISTED
> DOES NOT COVER THE QUANTITY THE BAR TESTS.** That product must be identified and added to the scope, or the
> anchor comparison is bit-exact over everything except the number `M(ii)` is about. **Named rather than
> resolved: I do not know which product carries it, and guessing is how a scope gets closed on the wrong file.**

#### 11f-v. Two clarifications my own §11a needed, both surfaced by this listing

1. **PROVENANCE-class means *may DIFFER from the archive*. It does NOT mean *may be ABSENT from the member*.** I
   conflated those, and (A) above depends on the distinction: **the offset stamp is PROVENANCE for the archive
   comparison and MANDATORY for member admission.** Two checks, one key, no contradiction.
2. **`n_throws = 160` in the terminal product is a THIRD corroboration of the throw population, by a third
   route** — launcher arithmetic, the slab id union, and now a declared integer in the artifact. **And this one is
   immune to `BEN-465`: it is a stated count, not a count of containers.**

**And on `globalCompleteness` being PRESENT (`0.99986`) while B relaxed `require_completeness` because the family
*"does not always write"* it: endorsed, and sharpened. A RELAXATION IS A WIDENING, so it needs a case that
REQUIRES it — a member of the family that demonstrably lacks the key.** Absent that, the relaxation is
unevidenced. *(Same rule as a filter needing a test in the direction it acts, applied to a guard being loosened
rather than tightened.)*

### 11g. RULED on the 41 GB per-universe covariance — **each member MUST PRODUCE it and NEED NOT RETAIN it**, and that is the whole storage question

**The scope gap of §11f-iv is CLOSED by tracing: the bar's operand is `sqrt_tr_old` in the ADOPTED roots**
(`uq_5d/universe_stage2_5d_bkgaware/uq_universe_5d_covariance_combined_bkgaware_uthrow.root`, 892 MB, 4 keys),
not in the terminal throw product — which is why the listing could not find it. **So stage 1's comparison scope
gains that file and its sibling.** Traced through `receipt_construction_contract_5d.json`'s `adopted_roots` and
confirmed on the cluster, not guessed. Gap closed.

**Now the question that moves the storage by a factor of ten. `uq_universe_5d_covariance_combined_bkgaware.root`
is 41.44 GB — 47 keys, `hCov_universe5d_total` plus 46 systematics.**

#### 11g-i. It MUST be produced per member. That half is not close

**It is not the analyzer's input — it is the analyzer's OUTPUT and adoption's INPUT.** And the analyzer's inputs
are the member's own 188 universes, re-unfolded at `42+k`.

> **So a member consuming the ARCHIVE's per-universe covariance would freeze the sweep leg — the block that is
> `61 %` of the GPU bill — and the member's `C_syst` would BE the archive's.** That is item 7's argument and Q1's
> argument arriving at a third site: **a frozen leg makes the variation incoherent, and an incoherent variation
> measures nothing.** No escape here, and I looked for one.

#### 11g-ii. But it NEED NOT BE RETAINED — and that is where the factor of ten is

**It is an INTERMEDIATE. The bar's operands live downstream of it, in the 892 MB adopted roots.** So once
`ADOPT_j` has consumed it and `MVFINAL_j` has bound its digest, **the member has no further use for it.**

```
retained per member   892,195,314 + 892,241,032 + 2,677,168,123  =  4.46 GB
  x 50                                                           =  223.1 GB = 0.203 TiB
transient per member  uq_universe_5d_..._bkgaware.root           = 41.44 GB

peak, retained-all-50 + N in flight:      N=1  264.5 GB (6.0% of free)   N=4  388.8 GB ( 8.8%)
                                          N=8  554.6 GB (12.6%)          N=10 637.4 GB (14.5%)
NO DELETION AT ALL:                            2.087 TiB               = 52.1% of the 4.01 TiB free
```

> **So the storage column is `223 GB` retained plus `41.44 GB × concurrency`, and `52.1 %` of remaining headroom
> becomes `8.8 %` at four members in flight. THE NUMBER WAS NEVER A PHYSICS QUANTITY — IT IS A RETENTION POLICY
> NOBODY HAD SET, and a concurrency choice.**

**AND THE REPRODUCIBILITY COST IS BOUNDED AND TINY, which is what makes the deletion defensible rather than
convenient.** The 41 GB is a handful of `65856²` `TH2D`s — **one such matrix is `34.7 GB` on its own** — derived
from 188 universe files totalling **`26.9 MB`**. **Retaining the inputs and discarding the intermediate is a
~1,500× compression of the reproducibility requirement**, and rebuilding it is the analyzer's CPU time, not a
GPU member.

> **DELETION IS GATED, and the gate is §10c's invariant running the other way: NOTHING IS DELETED WITHOUT A
> POSITIVE DECLARATION EITHER.** No member's intermediate may be removed until that member's `MVFINAL_j` exists
> and validates. **Nothing accepted without a stamp; nothing deleted without one.** A failed member keeps its
> intermediate.

**AND `CLAUDE.md`'s purge rule now bites at a size that can be obeyed:** `223 GB` of retained products carrying
`1,961` GPU-hours is copyable off scratch. **`2.09 TiB` is not.** *(My own `133.9 GB` was correctly SCOPED — I
said "that ONE product" and "I am not estimating the rest" — and radically incomplete: the all-in figure is
`45.90 GB` per member. The mediator measured the rest, which is the division of labour that worked.)*

### 11h. AMENDED — **the diagonal SHIPS BEFORE the intermediate goes**, and the check I owed and did not make

**B is right and the ruling is amended, not reversed.** `sqrt_tr_old`'s sole ingredient is
`hCov_combined5d_total` — `adopt_unified_5d.py:124-127`, from the `COMBINED` path at
`sbatch_adopt_stamped_footing.sh:33` — **which IS the 41.44 GB intermediate §11g releases.** So after deletion
**the scalar survives in a retained 892 MB root and its ingredient does not.**

> **⚠ THE GENERAL DEFECT, and it is the check I owed: A RETENTION POLICY MUST BE TESTED AGAINST EVERY DERIVED
> QUANTITY THAT *SURVIVES* THE DELETION, not against the ones the deletion is FOR.** §11g asked *"are the bar's
> operands downstream of the intermediate?"* — yes — and never asked *"are the surviving scalars' INGREDIENTS
> downstream too?"* **Those are different questions and only the second is about deletion.**
>
> **A DELETION CAN RETROACTIVELY BREAK `BEN-077` FOR AN ARTIFACT THAT WAS COMPLIANT WHEN WRITTEN** — converting a
> receipt that shipped its ingredients into a verdict-only one, permanently and after the fact. **Nothing in this
> campaign's convention covers that direction, because a receipt is checked when written and a purge happens
> later.**

**THE REMEDY IS A WRITE, NOT A COMPUTATION.** `trace(C) = Σ diag(C)`, and `adopt_unified_5d.py:128` **already
computes** `diag_comb = np.clip(np.diag(C_new), 0, None).copy()`, in memory at the moment `sqrt_tr_comb` is
formed. **Ship it as a `TH1D`.**

```
diag_comb + R4's vb + vu  =  3 x 10,694 doubles  =  256,656 B  =  250.6 KiB
against the 4.46 GB retained member : 0.00575 %
against the 41.44 GB released       : 161,461 : 1

  [CORRECTED 2026-08-18: first written as 3 x 65,856 = 1.58 MB, which is 6.16x too big.
   `adopt_unified_5d.py:110,120-121` settles it: n = vu.size and `assert x.size == n` where
   x = xfull[xfull > 0], so every one of these arrays is on the REPORTED-BIN set, not the grid.]
```

> **RULED: the diagonal SHIPS FIRST, and DELETION IS CONTINGENT ON IT.** Not a reversal — `41.44 GB` against
> `250.6 KiB` is not a close trade, and B says so too. **It is a SEQUENCING constraint, and it is §10c's invariant
> in its third form: nothing accepted without a stamp, nothing deleted without one, and NOTHING DELETED BEFORE
> THE SURVIVORS' INGREDIENTS ARE RETAINED ELSEWHERE.**

**AND TWO CLARIFICATIONS OF §11g'S SCOPE that the third consumer makes necessary:**

1. **§11g RELEASES *MEMBER* INTERMEDIATES ONLY. THE ARCHIVE'S 41.44 GB FILE IS UNTOUCHED** — it is frozen, and
   nothing in any ruling of mine may delete an archive product. **So `p4_build_components.py:114`'s consumption of
   it is unaffected**, and I should have said so when I wrote §11g rather than leaving *"delete the 41 GB file"*
   readable as touching the archive.
2. **The consumer enumeration must be COMPLETE, not confined to the member DAG.** B found a third consumer;
   **that it turned out to be harmless is luck, and the rule is that a release enumerates every reader.**

*(Attribution, fairly: the trace that said the operands are downstream did not distinguish `sqrt_tr_old`
— ingredient released — from `sqrt_tr_new` — ingredient retained. But I ruled on it, and the question I failed to
ask is the one in the box above. **B found it by WRITING THE COMPARATOR**, which is the fifth time today that
building an instrument found what reading could not.)*

### 11i. RULED on B's interim — **NOT A FOURTH CLASS. A REQUIRED ATTRIBUTE ON `PAYLOAD`**

**Of the seven keys I put in `PAYLOAD + MANDATORY RECOMPUTATION`, B implemented it and three cannot be
recomputed from the file that carries them: `fixed_seed_null_norm`, `globalCompleteness`, and `sqrt_tr_old` —
which §11h's remedy repairs, leaving two.**

> **REFUSED as a fourth class, and the reason is structural: my three classes each name a COMPARISON RULE**
> (bit-exact / equal / superset). ***"Not recomputable"* is not a comparison rule — these keys still compare
> bit-exact.** What differs is whether the INGREDIENT CHECK is available. **So it is an ATTRIBUTE on `PAYLOAD`,
> declared per key: `recomputable: yes | no`.**

**And the attribute inherits the enumeration's own discipline, which is the point of putting it there:**

- **Declared IN THE ENUMERATION, never discovered at comparison time** — the whole reason §11a is a table.
- **A `no` REQUIRES A STATED REASON**, and a `no` without one is the fail-closed case. `globalCompleteness`'s
  reason is *"inputs unwritten; `sweep_bank_5d.py` emits no completeness histogram at all"* — **which is a WRITER
  GAP, fixable later, and materially different from a mathematical impossibility.** Recording which kind it is
  determines whether anyone can ever close it.
- **B's `--acknowledge-unrecomputable` is ENDORSED and becomes permanent, with one strengthening: it takes the
  EXPLICIT KEY LIST and must match the enumeration's declared `no` set EXACTLY.** A blanket flag lets a FUTURE
  `no` ride in silently. **Closed-set assertion, third use today** — the hazard list, the archive-key buckets, and
  now this.

**B's default — `NOT_RECOMPUTABLE` keys BLOCK, and the flag lets them through RECORDED AS UNVERIFIED rather than
silently treated as checked — is exactly right and is the distinction the whole day has turned on.**

### 11j. AMENDED — remedy **(A) IS MANDATORY ON THE ADOPTED ROOTS**, not merely preferable

**`adopt_unified_5d.py` stamps no identity key, so a member's adopted root fails `anchor_identity` UPSTREAM of
every payload and recomputation question.** That sharpens §11f-i:

> **It is not that the comparison proceeds unverified — IT CANNOT BEGIN. And the artifact in question is the
> TERMINUS: the one `MVFINAL_j` binds and anybody quotes.** So **remedy (B) — never resume a stampless product
> class — does not help here, because the failure is ADMISSION and not RESUME.** **Only (A) reaches it.**
>
> **REVISED ORDERING: (B) first for the resume hazard, as the mediator proposed and for the reason it gave — no
> writer change. (A) REQUIRED BEFORE ANY MEMBER CAN BE ADMITTED AT ALL.** And on the adopted root (A) is both most
> necessary and cheapest: four `TParameter` keys in a 892 MB file.

## 15. STAGE 0 PASSED — and its headline fraction is **`98.25 %`, NOT `~16 %`**. The two indices of this campaign are in the numerator and the denominator

**The verdict itself I accept without qualification, and it is not changed by anything below:** three pairs
`(0,1200)`, `(0,2400)`, `(1200,2400)`, all **DISTINCT**, exit 0, no `INCOMPARABLE`; the estimator delta equal to
the offset delta on every row; the data draw held identical on every pair. **The negative branch is closed and
`M(ii)` is measurable.** The transitive digest consistency is a real property and the mediator is right that
nobody designed it — **it is available because the report ships its operands, which is `BEN-077` paying out for
the second time today.**

### 15a. ⚠ THE FRACTION IS MIS-SCALED BY `6.158x`, AND THE DIRECTION MATTERS

> **Reported: *"changed 10,507-10,510 of 65,856 bins"*, read out as *"the estimator seed moves C_stat's
> replicas on ~16 % of bins."* THE NUMERATOR AND DENOMINATOR INDEX DIFFERENT SETS.**
>
> - **`65,856` is `p4_lib.py:22`'s `GRID_NBINS = 14*16*7*7*6` — the FULL 5D grid, most of which is EMPTY.**
> - **The populated / reported set is `10,694`** — the stored covariance is `10,694 x 10,694`, `hInflation_g`
>   has `10,694` bins, and `adopt_unified_5d.py:120-121` derives it as `xfull[xfull > 0]` with an assert.
>
> ```
> 10,507 / 65,856      =  15.95 %      <- as reported: changed bins over the WHOLE GRID
> 10,507 / 10,694      =  98.25 %      <- MY inference, ALSO WRONG: 10,694 is ANOTHER PRODUCT'S mask
> 10,507 / 10,507      = 100.00 %      <- MEASURED, per product, on all nine comparisons
> 10,508 / 10,508  and  10,510 / 10,510  likewise
> ```
>
> **⚠ CORRECTED TWICE. The measured answer is `100.00 %`: EVERY BIN THAT CAN MOVE, MOVED.** My `98.25 %` divided
> a per-product changed-count by `10,694` from `ADVISORY-20260813-oi30-eavail-residuals.md` — **a different
> product's reported set — so my numerator and denominator came from different artifacts, which is the SAME
> DEFECT I was correcting.** `10,507`/`10,508`/`10,510` **are the support sizes themselves**, product by product.
> The mediator and B measured it after B repaired the reporter.
>
> **AND THE TELL WAS IN THE SENTENCE I QUOTED APPROVINGLY:** *"remarkably stable across all nine comparisons."*
> **A *changed* count that barely varies across nine independent comparisons is a POPULATION COUNT WEARING THE
> LABEL OF A MEASUREMENT.** I read the stability as reassuring; it was the diagnostic.
>
> **A SECOND FIGURE I REPEATED WITHOUT INTERROGATING: *"0.6-1.2 % relative"* was `max|delta|` over the PEAK
> BIN**, not a per-bin change. The median per-bin relative change on the support is `5.098e-03` to `6.273e-03`
> — **`~0.51-0.63 %`** — and it now ships beside the peak ratio. *(Corrected by the mediator, against itself,
> twice, both times in the direction of the effect being larger.)*

**AND THIS CAMPAIGN HAS ALREADY WRITTEN THE WARNING FOR EXACTLY THIS PAIR OF NUMBERS.**
`ADVISORY-20260813-oi30-eavail-residuals.md:289-292` — *"Both numbers are right; they index different things"* —
and `:299-301` records a scout inferring `10,550²` from a file size and being wrong. **The advisory even gives the
third index: `10,550` is the PET-COMMON subset, `10,694` the full GBDT reported set.** So there are **three**
live bin counts here and a bare *"of bins"* selects none of them.

*(Stated plainly because it is my own recurring defect and I have no standing to be gentle about it: I made the
same error twice in §14a — see the correction there — and the fraction above is the same shape one level out.
**The rule that catches all three: a fraction ships the DEFINITION of its denominator, not just its value.**)*

### 15b. ⚠ CONSEQUENCE FOR MY OWN BAR — **leg B's SUPPORT was never specified, and it must be fixed NOW, before the numbers exist**

**`PREDECLARATION-20260817-mii-seed-scan-cause-3.md:80-86` defines leg B as
`f_med = median over bins of sd_i(σ_i)/σ_i ≤ 2.74 %`. *"OVER BINS"* — WHICH BINS IS NOT STATED**, and with
`65,856` / `10,694` / `10,550` all live, that is under-specified in precisely the way §15a just demonstrated.

**It is not academic. Over the full grid, ~84 % of entries have `σ_i = 0` and `x = 0`, so the per-bin ratio is
`0/0`: the median is either `NaN` or — if NaNs are dropped — silently the median over the populated set, which
is a DIFFERENT STATISTIC REACHED BY ACCIDENT.**

> **RULED: leg B's support is the REPORTED-BIN PREDICATE `xfull > 0` evaluated on the MEMBER'S OWN
> `hXSecND_flat`, exactly as `adopt_unified_5d.py:120` does it — and the specification names the PREDICATE, NOT
> A COUNT.**
>
> **Two reasons, and the second is the one that generalises:**
>
> 1. **CALIBRATION. Leg B's `2.74 %` is derived from `\gbdtFiveBlockMedian`'s 4 s.f., and that published
>    `13.359 %` IS `adopt_unified_5d.py:161`'s `100*np.median(do)` where `do = sqrt(diag_comb)/x` on the masked
>    `x`.** A threshold calibrated to a published quantity transfers only to the SAME statistic; leg B over a
>    different support would be a bound imported from a number it is not about.
> 2. **A COUNT WOULD BE ANOTHER DEFINITE DESCRIPTION THAT RE-POINTS.** `10,694` is right for the GBDT set and
>    wrong for the `10,550` PET-common one, and a member's own mask is whatever its product carries. **The
>    predicate is checkable per member; a literal count is a claim about which product you meant** — `BEN-380`
>    again, and the third time today that the repair is "cite the mechanism, not the value."

**AND ONE BRANCH OF MY PREDECLARATION IS SETTLED BY THIS, IN THE STRICTER DIRECTION.** The predeclaration says
*"if the contribution is concentrated, leg B is small and leg A binds; if it is uniform, both move together."*
**At `100.00 %` of the support responding, the CONCENTRATED branch is DEFINITIVELY not the operative one — leg
B is fully supported and genuinely binds rather than being structurally near-zero.** **This makes the bar harder to
clear, not easier, and it is recorded before any `f_med` exists.**

> **WHAT I AM NOT CLAIMING, and the mediator drew this bound correctly first: `0.6-1.2 %` RELATIVE BETWEEN TWO
> OFFSETS IS NOT `f_med`.** That is a replica-level difference between two members; `f_med` is the median over
> bins of the spread of `σ_i` across FIFTY members. **Different object, different estimator, and no number above
> licenses a prediction about the bar.** `n=3` is a floor on the effect's existence. **Stage 1 prices it.**

## 16. THREE RULINGS FOR `B1`, AND A SIXTH STAGE-1 GATE

### 16a. RULING 1 — **STOP AFTER (3) IS CONFIRMED AS MY RULING, AND IT IS A PAUSE, NOT A BOUNDARY OF STAGE 1**

**B asked that I confirm the cut rather than the mediator, and named why: *"that cut is also convenient in a way
worth distrusting — stopping before adoption is exactly where the work gets harder."* That instinct is right,
and the answer is that the cut is BOTH convenient AND correct — but its correctness is CONTINGENT ON BEING
TEMPORARY.**

> **CONFIRMED: stop after (3). REFUSED: building (4)/(5) unstamped.** Per §11j, `adopt_unified_5d.py` stamps no
> identity key, so those roots fail `anchor_identity` UPSTREAM of every payload question — and they are the
> **TERMINUS**, the artifact `MVFINAL_j` binds and anybody quotes. **An unadmittable CITABLE product is the
> worst available state: it exists, it looks finished, and the next reader just uses it.**

**AND THE ARGUMENT NEITHER B NOR THE MEDIATOR MADE, WHICH IS WHY THE CUT MUST BE LABELLED A PAUSE.**
**`sqrt_tr_old` — the predeclared bar's own operand — IS WRITTEN AT `adopt_unified_5d.py:177`,** i.e. inside
steps (4)/(5).

> **SO STOPPING AFTER (3) MEANS STAGE 1 CANNOT COMPARE THE QUANTITY THE BAR IS ABOUT.** The cut completes the
> *build* through (3); **it does not discharge stage 1**, whose anchor comparison needs the adopted roots. **A
> stop-after-(3) member is not a stage-1 pass waiting on paperwork — it is a stage-1 that has not yet been
> attempted.** Recorded because the two read identically in a status table.

**CONSEQUENCE: REMEDY (A) IS NOW ON THE CRITICAL PATH, not a parallel nicety.** It is four `TParameter` keys in
one writer, and it gates the only steps that produce a comparable artifact.

**AND A SCOPE LABEL THE CUT MUST CARRY, because it is right for ONE member and wrong for FIFTY.** §11g gates
deletion of the `41.44 GB` intermediate on `MVFINAL_j` existing — and `MVFINAL_j` needs (4)/(5).

> **⚠ THEREFORE, DURING THE PAUSE, NOTHING IS DELETABLE. A member stopped after (3) holds its intermediate
> indefinitely, and "stop after (3)" combined with "§11g releases the 41 GB" WOULD DELETE THE ONLY INPUT TO
> (4)/(5).** At stage 1's single member that is `41.44 GB` and fine. **At fifty it is `2.087 TiB` = `52.1 %` of
> free scratch — the exact figure §11g exists to avoid.**
>
> **So the cut is admissible at STAGE-1 SCOPE ONLY, and it must be recorded with its EXPIRY CONDITION — remedy
> (A) landing — and not merely with its rationale.** A boundary documented only by its reason gets inherited;
> one documented by its expiry cannot be.

### 16b. RULING 2 — **THE FLAT-NORM BAND MULTIPLIES THE *MEMBER'S* CV**, conditional on one cheap check, and pinning has a DIRECTION

**First, the settled part: `0.014` is member-INVARIANT. It is the external physics constant and does not vary.**
The live question is which CV it multiplies, and **B's cancellation result is accepted and is the right kind of
argument** — `analyze_universes_5d.py:167-172` forms `D = u - cv` then `Z = D - D.mean(axis=0)`, so `cv` drops;
verified **bit-identical, max abs difference `0.0`**. **A cancellation does not decay the way a tolerance does,
and it removed a leg.**

**But `--add-norm` builds `outer(0.014·cv_rep, 0.014·cv_rep)`, so this one term scales with CV values directly:
measured `sqrt-tr 0.47302` vs `0.47573`.**

```
(0.47573 - 0.47302) / 0.47302  =  0.573 %      one term, one CV substitution
against leg A's bar of 4.15 %  =  13.8 % of the entire budget
```

> **RULED: the MEMBER'S CV — because the member re-unfolds its own CV at `42+k`, so THAT CV IS SEED-DEPENDENT,
> and the flat-norm term is a genuine channel through which the estimator seed reaches the covariance.** Pinning
> it to the archive **FREEZES that channel**, which is item 7's argument, Q1's argument and the `finalize`
> header's argument arriving at a **fourth** site: *a frozen leg makes the variation incoherent.*
>
> **AND THE DECIDING CONSIDERATION IS THE DIRECTION, NOT THE PRINCIPLE. Pinning SUPPRESSES a real contribution
> to the spread, so it biases `f_agg` and `f_med` DOWNWARD — TOWARD `MET`.** Therefore:
>
> **PINNING IS SAFE FOR REFUTING `MET` AND UNSAFE FOR ASSERTING IT. Since the scan exists to decide `MET` /
> `UNMET`, A `MET` VERDICT OBTAINED UNDER PINNING IS NOT DISCHARGEABLE** — it would be a pass bought by
> omitting a term. **An `UNMET` under pinning would still stand.**

**THE CONDITIONAL, and it is cheap to discharge BEFORE any member runs.** There are two CV objects, and my
ruling names the memberized one — **`universe_sweep_bkgaware/…_uni_full_CV.root`** — **only if it is the same
estimator of the same quantity as `products/5d/xsec_5d_MEFHC_5iter_lgbm.root`.**

> **DISCHARGE IT ON THE ARCHIVE, where both already exist: compare the archive's `uni_full_CV` against the
> archive's `products/5d/` CV.**
>
> - **They agree** (bit-exact or to round-off) → same quantity, and the member's own is the correct substitution.
>   **Rule stands as written.**
> - **They differ materially** → they are DISTINCT products, the member has no memberized counterpart, and
>   substituting one for the other would inject a difference that **is not estimator noise** — worse than
>   pinning. **Then pin, AND record the flat-norm term as a FROZEN LEG carrying the bias direction above**, so a
>   `MET` verdict is flagged as provisional at the moment it is produced rather than argued about afterwards.
>
> **I will not guess which: substituting a differently-constructed CV is exactly the asymmetric comparison this
> determination has spent the day refusing, and the check costs one read of two archive files.**

**B's discipline of recording the choice at the call site is ENDORSED and STRENGTHENED: the call site records
the DIRECTION OF THE BIAS, not only the choice.** *"We pass the archive's CV"* is a decision; *"we pass the
archive's CV, which suppresses a seed channel and biases the verdict toward `MET`"* is a decision a later reader
can act on. **B's own reason — the `SLURM_SUBMIT_DIR` lesson, that an explicit decision later reversed costs one
line while an inherited default that is wrong is invisible — is the correct one and generalises.**

### 16c. RULING 3 — **THE DIAGONAL IS IMPLEMENTED NOW, IN THE SAME CHANGE AS REMEDY (A)**

> **RULED: now, not later, and the reason is that BOTH are edits to `adopt_unified_5d.py` and both are
> preconditions of (4)/(5), which under §16a have not run yet.** So the writer is touched **once**, before it is
> ever invoked for a member.
>
> **There is no urgency-versus-risk trade to weigh, because §16a establishes that nothing is deletable during
> the pause.** The cost of deferring is not a risk of deletion — **it is that (4)/(5) would produce two
> `892 MB` citable roots MISSING the ingredient, and repairing that re-runs the analyzer**, which is the
> expensive leg. **`diag_comb` is already in memory at `:128`; the write is `3 * n * 8` bytes for that member's
> own `n`.**
>
> *(Deliberately not a literal: writing `1.58 MB` here is what §14a/`BEN-466` were about.)*

### 16d. A SIXTH STAGE-1 GATE — **the `cv > 0` support is compared as a SET, never as a COUNT**, and the instrument already exists

**B declined to claim its fixture proved anything, because the fixture drew all-positive CVs by construction so
the mask matched trivially. That is the correct call and it is the right species of care** — a power test proves
power in its fixture's language, and an all-positive fixture cannot exercise a sign flip. **The mediator is
right that this is a precondition of the comparison I ruled, not a detail of B's build. RULED as a GATE.**

> **⚠ AND THE HAZARD IS SHARPER THAN A DIMENSION MISMATCH, WHICH IS WHY A COUNT WILL NOT DO IT: TWO SUPPORTS OF
> EQUAL SIZE CAN DIFFER IN MEMBERSHIP.** If a seed change pushes one bin below zero and another above it, **the
> cardinality is IDENTICAL and the flat ordering has SHIFTED** — so every bin after the first divergence is
> misaligned, and a bit-exact comparison then compares **the wrong pairs** and reports a difference whose
> location is meaningless. **A dimension mismatch fails loudly; an equal-size membership change fails
> silently.**
>
> **THE INSTRUMENT IS ALREADY IN THE REPO AND B SHOULD NOT BUILD ONE: `p4_lib.py:1196` `mask_order_hash`, whose
> sibling at `:1085-1088` documents that it FAILS CLOSED on `GRID_NBINS`** — it is mask-*order* aware, which is
> precisely the property a cardinality check lacks. **Stage 1 compares `mask_order_hash`, and a member whose
> hash differs from the archive's is REFUSED rather than compared.**
>
> **AND THE MASK IS `CONFIGURATION` UNDER §11a** — changing it changes what was measured — **so it must be
> EQUAL, and a difference is a HARD FAILURE, not a provenance note.** That is consistent with the class the
> taxonomy already assigns and needs no new class.

**THIRD INSTANCE OF ONE FAMILY IN TWO DAYS, and worth naming as a rate rather than three anecdotes:**
`BEN-465` — *corroborate a population by reading its IDS, not by counting its containers*; `BEN-466` — *a
fraction must name WHICH INDEX its denominator is*; and now **a support must be compared by MEMBERSHIP, not by
CARDINALITY.** **All three are the same substitution: a count standing in for an identity, and in all three the
count agreed while the identity did not.**

## 17. THE COMPARATOR DIGESTS ONLY THE DIAGONAL — **gate 2 is UNMET, and the reduction is aligned with the bar in the worst possible way**

**Lane D found that `read_keys_pyroot` reduces every `TH2D` to its DIAGONAL and the comparator digests that.**
Measured on the real `C_unified`: the payload comparison sees **`10,694` of `114,361,636` elements =
`0.00935 %`**, and **`sum|off-diagonal|` is `~997x` `sum|diagonal|`.**

> **RULED: this does not satisfy gate 2, and the failure is definitional rather than a matter of degree.**
> §11a's `PAYLOAD` class says **bit-exact**, of the object. **A digest of the diagonal is a bit-exact comparison
> of A PROJECTION, and reporting it as a bit-exact payload comparison is a category error** — the verdict is
> about the projection, and nothing in it is about the artifact. **`0.00935 %` coverage with `997x` the mass
> outside cannot support the word "bit-exact" under any reading.**

### 17a. ⚠ MY §11f-i UNDERCOUNTED: THERE ARE **THREE** INDISTINGUISHABLE OBSERVATIONS, NOT TWO

**§11f-i established two — a genuine reproduction and *"you compared the archive to itself"* — and argued the
cross-member distinctness backstop cannot separate them at `n=1`. D adds a third:**

| # | observation | separated by |
|---|---|---|
| 1 | a genuine bit-exact reproduction | — |
| 2 | **the archive compared to itself** | remedy **(A)**, the identity stamp — which is why I ruled it MANDATORY |
| 3 | **a member that reproduced `10,694` numbers and NOTHING ELSE** | **nothing, currently** |

> **All three produce identical digests and an exit 0.** My §11f-i reasoning was right and its enumeration was
> short by one, because I was reasoning about *what the digests can distinguish* and not about *what the
> comparator actually reads.* **A gate is only as strong as the bytes its instrument touches, and I had ruled on
> the comparison's LOGIC without ever asking its EXTENT.**

### 17b. ⚠ AND THE REDUCTION IS NOT ARBITRARY — **it covers EXACTLY the bar's operand and nothing else, which is the most defensible-looking and worst possible choice**

**`sqrt_tr_old = sqrt(trace(C))` depends ONLY on the diagonal.** So:

> **A DIAGONAL-ONLY COMPARATOR VERIFIES PRECISELY THE QUANTITY THE PREDECLARED BAR CONSUMES, AND NOTHING ABOUT
> THE CORRELATIONS.** It would produce a bar-consistent `PASS` with `997x` the matrix mass never read.
>
> **I expect the defence *"the bar only needs the trace, so the diagonal is the relevant part"*, and it is
> wrong:** the adopted covariance is not consumed only by the bar. **`project_cov_nd.py` marginalises it —
> `C_low = M C_high M^T` — which is a sum over OFF-DIAGONAL sub-blocks**, and its own header warns that getting
> the ordering wrong *"silently produces a plausible number."* **A covariance whose off-diagonals were never
> compared is unverified for every downstream projection, which is most of what it is for.**
>
> **This is the sharpest form of a shape this determination keeps meeting: a check whose coverage is ALIGNED with
> the quantity someone will quote is not thereby sufficient — it is harder to notice.** A random `0.00935 %`
> sample would at least fail visibly.

### 17c. RULED — full-array digest, and any reduction DECLARES ITSELF WITH TWO NUMBERS

> **1. THE PAYLOAD COMPARISON DIGESTS THE FULL ARRAY, one key at a time.** Feasible and not close: **one
> `10,694²` `TH2D` is `914,893,088 B = 0.915 GB`**, so peak memory is one matrix, and a digest needs no more than
> a streaming pass over the buffer. **The diagonal reduction is REFUSED for `PAYLOAD`-class keys.**
>
> **2. A REDUCTION IS PERMITTED ONLY IF IT DECLARES ITSELF, AND A DECLARATION IS TWO NUMBERS, NOT A NOTE: the
> ELEMENT COVERAGE and the MASS FRACTION OUTSIDE THE REDUCTION.** `0.00935 %` and `997x` are the template —
> **the pair is exactly what makes the current instrument's inadequacy arithmetic rather than a judgement call,
> and it is `BEN-077` applied to a comparator's own scope.**
>
> **3. THE GENERAL RULE: A COMPARATOR THAT COMPARES A PROJECTION REPORTS THE PROJECTION.** The defect is not
> that it reduces — reduction may well be necessary — **it is that it reduces SILENTLY and reports the reduced
> verdict in the vocabulary of the full one.** *(Gate 2 was the one I said to guard hardest, on the grounds that
> a comparator existing is not a comparator being right. It existed and had never run on real archive data;
> what it did when it ran was read `0.00935 %` of the payload.)*

### 17d. REMEDY (A)'s SCOPE WIDENS — **`LATERAL_CV` too, not only the adopted roots**

**D found that `anchor_identity` CANNOT RUN on `ADOPTED_UTHROW` *or* `LATERAL_CV`: neither carries any identity
key.** §11j ruled (A) mandatory and named *"the adopted roots"*.

> **AMENDED: (A) covers `LATERAL_CV` as well.** Same argument, unchanged: the failure is **ADMISSION**, so (B)
> cannot reach it, and an artifact that cannot be identified cannot be admitted. **This is (A)'s gap seen from
> the GATE's side rather than the WRITER's, and the two views disagreeing about scope is itself the finding** —
> I enumerated the writers that need stamps; D enumerated the artifacts the gate cannot read. **The second list
> was longer.**

### 17e. TWO NUMBER RECONCILIATIONS, so that neither becomes a fourth round of corrections

**(i) `484,384:1` and `161,461:1` ARE BOTH RIGHT.** The mediator priced **one** per-bin array
(`41.44e9 / 85,552`); §11h prices **three** — `diag_comb`, `vb`, `vu` (`41.44e9 / 256,656`). **Same artifact,
same arithmetic, different operand count.** Stating it explicitly because *"your figure is 3x mine"* is how the
last three rounds started, and neither of us is wrong here.

**(ii) THE CORRECTED MATRIX SIZE DOES NOT WEAKEN §11g — IT EXPLAINS IT.** My §11g wrote that the `41.44 GB`
intermediate is *"a handful of `65856²` `TH2D`s — one such matrix is `34.7 GB` on its own."* **That figure was
mine and it was wrong, from the grid rather than the support.** But the corrected number closes a gap the wrong
one left open:

```
one 10,694^2 TH2D          =  0.915 GB
41.44 GB / 0.915 GB        =  45.3 matrices
the file's key count       =  47   (hCov_universe5d_total + 46 systematics)
46 x 0.915 GB              =  42.09 GB   ~=  the measured 41.44 GB
```

> **So the file's size is now fully accounted for by its OWN key list, which the `34.7 GB` figure could never
> have done — at `34.7 GB` per matrix a 47-key file would be `1.6 TB`.** The retention ruling is unchanged and
> its mechanism is now derivable from published operands instead of asserted. **A wrong number that nothing
> could contradict, replaced by a right one that reproduces an independent measurement.**

**(iii) `16.24 %` and `15.95 %` are the same RATIO on two different supports.** `10,694/65,856 = 16.24 %`;
stage 0's `10,507/65,856 = 15.95 %`. **Near-identical, not identical, and the difference is precisely that the
two supports belong to different products** — which is `BEN-466`'s subject appearing inside the sentence that
reports `BEN-466`'s subject. **The mediator's observation stands: two lanes, two artifacts, one denominator, and
the comment on the constant records that it was written down BECAUSE a per-bin array had already been sized off
the grid and was wrong by `230x`. The fix for the first instance carried the second.**

## 18. THE §16b CONDITIONAL IS DISCHARGED — **SUBSTITUTE, use the member's own CV**, and the mediator's lean is corrected on one point: the contaminant does not enter the statistic

**The measurement I asked for was run and it is decisive, though not in the way either of us framed it.**

```
products/5d/xsec_5d_MEFHC_5iter_lgbm.root                    479,553 B
uq_5d/universe_sweep_bkgaware/5d_xsec_..._uni_full_CV.root   480,251 B
same key set, same 65,856 grid, same hXSecND_flat
SUPPORT 10,694 both, and np.array_equal(a>0, b>0) is TRUE      <- membership, not cardinality
all 10,694 support bins differ:  median rel 5.754e-03,  p90 2.046e-02,  28.8% above 1e-2
integrated  sum(a)/sum(b) = 0.999690823                        <- totals agree to 0.03%
```

### 18a. ⚠ WHY THE LEAN TO *"PIN AND RECORD"* IS WRONG — **the bar is a SPREAD statistic, and a common-mode difference does not enter a spread**

**The mediator quoted my own §16b sentence back at me — *"substituting would inject a difference that is NOT
estimator noise, which is worse than pinning"* — and applied it faithfully. THE SENTENCE WAS TOO BROAD AND THE
ERROR IS MINE.** It is the correct test for a comparison of **VALUES**. **The bar compares SPREADS:**

```
leg A   f_agg = sd_j(block_sum_j) / block_sum        <- sd ACROSS the 50 members
leg B   f_med = median_bins sd_j(sigma_i) / sigma_i  <- sd ACROSS the 50 members
```

**Write the flat-norm term's contribution as `T(cv) ∝ 0.014 · ||cv||`, and let member `j` carry
`cv_j = cv_uni(seed_j) = cv_arch + Δ + (seed response)_j`:**

| choice | `sd_j` of the flat-norm contribution | consequence |
|---|---|---|
| **PIN** to `cv_arch` | `sd_j(0.014 · ||cv_arch||)` = **exactly 0** | **the term contributes NOTHING to either leg** |
| **SUBSTITUTE** `cv_uni(seed_j)` | driven by the seed response | **the term contributes its real seed sensitivity** |

> **So `Δ` — whatever distinguishes the two products — IS COMMON-MODE ACROSS ALL FIFTY MEMBERS AND CANCELS IN
> `sd` TO FIRST ORDER.** It shifts the operating point, so it perturbs the *sensitivity* at second order, and it
> shifts leg A's denominator by the measured `0.03 %`. **It does not enter the spread.**
>
> **PINNING, BY CONTRAST, ZEROES THE TERM'S CONTRIBUTION TO THE SPREAD AT FIRST ORDER.** That is not a small
> conservatism — **it removes a channel entirely, and §16b already established the direction: DOWNWARD, TOWARD
> `MET`.** A `MET` obtained that way is a pass bought by omitting a term.
>
> **RULED: SUBSTITUTE. The member's own `uni_full_CV`.** The condition I set — same estimator of the same
> quantity — **is satisfied on the evidence that actually bears on it**, and the evidence that looked
> disqualifying bears on a statistic the bar does not use.

### 18b. The evidence FOR same-quantity is stronger than it was credited, and one piece of it is the gate-6 instrument passing

- **`np.array_equal(a>0, b>0)` is TRUE — IDENTICAL SUPPORT MEMBERSHIP, bin-for-bin across `10,694` bins.**
  **This is the strongest single fact in the measurement.** A genuinely different observable, or a different
  binning, or a different iteration count would not preserve support membership *exactly*. **And note what kind
  of check it is: a SET identity, not a cardinality** — precisely the instrument §16d ruled for gate 6, run here
  incidentally, and **PASSING. So the archive's own two CVs are a ready-made POSITIVE CONTROL for
  `mask_order_hash`**, which the mediator spotted and which is worth more than the CV question it arose from: a
  gate with a real positive control is a gate that has been shown to be able to pass.
- **Integrated totals to `0.03 %`** — same normalisation, same units, same POT scaling.
- **Same key set, same grid, same `hXSecND_flat`.**

### 18c. ⚠ THE MAGNITUDE COINCIDENCE IS SUGGESTIVE AND IS NOT EVIDENCE — named because the argument leaned on it

**The two archive CVs' median difference is `5.754e-03`; stage 0's median per-bin seed effect is `5.098e-03` to
`6.273e-03`. The same magnitude, and it is a genuinely striking observation.**

> **But *"two quantities have the same magnitude"* does not license *"they have the same cause."*** Seed-scale
> jitter would produce this; so would a re-run at a different iteration count, a different random state in a
> shared subroutine, or two builds months apart on different library versions. **The coincidence is CONSISTENT
> WITH the seed reading and discriminates against nothing** — and my §18a ruling does not depend on it either
> way, which is the reason it can be stated as an observation rather than argued over.

### 18d. AND A GENUINE OPEN ITEM THAT IS NOT MINE AND NOT `M(ii)`'s

> **Two archive products that ought to be the same central value differ on `100 %` of their support, with
> `28.8 %` of bins above `1 %` and a median of `0.58 %` — AND NOBODY HAS RECORDED IT.** The mediator named this
> and it is right: **if these are the same estimator reached by two routes, a `0.58 %` median disagreement is a
> REPRODUCIBILITY finding about the archive**, independent of the seed scan.
>
> **It belongs to whoever owns the archive's CV provenance, not to `OI-121`, and I am not filing it into another
> lane's territory.** Flagged with its operands so it can be picked up: the two paths, the byte sizes, and the
> distribution above.
>
> **AND DO NOT QUOTE THE `max = 1.262e-01`.** One bin of `10,694`, and a per-bin *relative* difference on a
> support that reaches down to near-zero cross sections is the classic near-zero-denominator artefact — the same
> `BEN-064` shape this campaign has declined to report twice. **The median and the quantiles are the reportable
> statistics.**

### 18e. What this does NOT settle

**Nothing here changes `0.014`'s member-invariance (settled), the cancellation in the systematic covariance
(B's, bit-identical, `max abs diff 0.0`), or any of §§16a/16c/17.** And it does not predict `f_agg` or `f_med`:
**the `0.573 %` sqrt-trace shift between two CVs is a two-artifact difference, not a fifty-member spread.** It
bounds the term's sensitivity, not the bar.

## 19. LANE D's JOB-1 REPORT — **my §17 closed a gap I recorded as open in the same section**, and two unruled items, one of which blocks stage 1 outright

### 19a. ACCEPTED — **§17a's *"nothing currently separates the third"* IS WRONG, AND §17c IS WHAT REFUTES IT**

**I wrote that there are three indistinguishable observations and that nothing separates the third — a member
that reproduced `10,694` numbers and nothing else — three paragraphs BELOW ruling the full-array digest that
makes exactly that member fail.** Under §17c a member must reproduce all `114,361,636` elements; reproducing
only the diagonal no longer passes.

> **CORRECTED: all three ARE separable under §17 as written.** (A) separates the first two; **§17c separates the
> third.** **The defect is a document that states a gap and its remedy in one section and does not connect them
> — which is worse than either an unnoticed gap or an unremedied one, because a reader who trusts the summary
> inherits an open item that is closed.** D caught it; I had the answer and had not applied it to my own
> enumeration.

### 19b. CORRECTION — **peak memory is `~2 GB` per LIVE `TH2D`, measured, not `0.915 GB`; and the release must be EXPLICIT**

**Measured: `2,027 MB` peak RSS for the adopted root (one `10,694²` `TH2D` + one `TH1D`); `3,773 MB` for the
throw root's three. ROOT allocates the `sumw2` array alongside the contents, so a `TH2D` is resident at ~2x its
nominal size.** My `0.915 GB` was the array, not the object.

> **§17c's *"one key at a time"* is PROMOTED FROM PREFERENCE TO REQUIREMENT, and it needs code that does not
> exist:** `origin/lane-b-member-axis-wip:nd-unfolding/mii_anchor_comparator.py:182-183` loops `for key in f.GetListOfKeys(): name, obj = key.GetName(),
> key.ReadObj()` and **holds every object until `f.Close()`.** So a streaming digest needs explicit
> `obj.Delete()` or per-key scope — **restructuring the digest alone does not stream anything.**
>
> **BUDGET `~2 GB` PER LIVE `TH2D` AND MAKE THE RELEASE EXPLICIT.** Otherwise the throw root is `~6 GB` and my
> ruling reads as free when it is not. *(This strengthens §17 rather than weakening it: a requirement with a
> measured cost is implementable; a preference with an understated one gets deferred.)*

### 19c. ⚠ **I CORRECTED THE NUMBER WHERE I ORIGINATED IT AND NOT WHERE IT EXECUTES** — and the constant written to prevent my first error encodes my second one verbatim

**Read at `origin/lane-b-member-axis-wip`, not inferred:**

```python
# origin/lane-b-member-axis-wip:nd-unfolding/mii_root_payload_classes.py:37-39
#: The 5D flat length. RECORDED EXPLICITLY because C sized a per-bin array off the extended-FPS
#: 285-bin grid and was wrong by 230x; the mediator caught it. A per-bin float64 array is 0.527 MB.
FLAT_NBINS = 65856

# origin/lane-b-member-axis-wip:nd-unfolding/mii_anchor_comparator.py:171
#   "...avoids materializing a 34.7 GB matrix."      <- 65856^2 x 8 B = 34.70 GB
```

> **THE CONSTANT INTRODUCED TO PREVENT MY FIRST ERROR CARRIES MY SECOND ONE, INCLUDING MY PROSE.** The comment
> names me, cites the `230x` correction — **which was itself wrong** — and states *"a per-bin float64 array is
> `0.527 MB`"*, the exact figure §14a was corrected for. **`FLAT_NBINS = 65856` is the grid; every array these
> classes describe is on the support.**
>
> **AND THE RULE THAT WOULD HAVE PREVENTED IT: A COMMENT THAT RECORDS A CORRECTED *VALUE* INHERITS THE NEXT
> ERROR; ONE THAT RECORDS THE *DERIVATION* CANNOT.** Had it read *"derive `n` from `xfull > 0`, never from the
> grid — see `adopt_unified_5d.py:120-121`"*, it would have been right without knowing the number. **It recorded
> the answer to the first question instead of the method, so it was defenceless against the second.**
>
> *(And a second-order instance caught by `docs/orchestration/lanec_citation_resolution_check.py` on its second
> outing: my first draft of this section cited both modules by BARE repo-relative path, and they exist ONLY on
> `origin/lane-b-member-axis-wip` — **so the citations were unresolvable for anyone reading `main`, which is the
> tree this document lives on.** Repaired by making each citation carry its ref, and the checker now resolves a
> `<ref>:<path>` citation against that ref's tree, failing closed on a ref nobody can fetch. **An allowlist would
> have hidden it; the citation needed the ref, not an exemption.**)*
>
> **RULED, and it is the part I got wrong procedurally: the correction lands AT THE CALLEE.** §14a/§17e fixed my
> determination; **the executing copy is `origin/lane-b-member-axis-wip:nd-unfolding/mii_root_payload_classes.py:39` and `origin/lane-b-member-axis-wip:nd-unfolding/mii_anchor_comparator.py:171`, and
> that is the one a future reader acts on.** A number corrected only in the document that first stated it has not
> been corrected. *(My own standing lesson — what EXECUTES versus what is CITED, and the unit is the callee —
> applied to my own arithmetic, one day after I wrote it down.)*

### 19d. RULED on D's blocking finding — **`derive: None` CONFLATES TWO ABSENCES, and the map already carries what distinguishes them**

**D ran a PERFECT ANCHOR through the comparator and got `FAIL`, nine findings.** The real
`adopted_uthrow.root` has **four** keys, dated **2026-07-14**; nine of `ARCHIVE_KEY_MAP`'s `derive: None` rows
are **not** `PROVENANCE`-class, and a non-provenance member-only key is a hard finding by construction.
**`upstream_fixed_seed_null_norm` and `upstream_joint_mean_shift_norm` are `PAYLOAD` AND member-only — they
cannot pass.** *"The map written to stop the archive's age from reddening stage 1 is what reddens it."*

**This is a gap in MY taxonomy, not in B's map.** §11f-v(1) ruled that `PROVENANCE` means *may differ*, not *may
be absent from the member*. **I never ruled the converse: PRESENT IN THE MEMBER, ABSENT FROM THE ARCHIVE, for a
NON-PROVENANCE class.** B's `:143` comment — *"THE FIX IS A THIRD KIND OF MAP ENTRY, which I had not
anticipated"* — is B discovering the shape one entry at a time. **Here is the general form so there is no
fourth discovery.**

> **`derive: None` is REPLACED by an explicit `absence:` field over a CLOSED vocabulary:**
>
> - **`PREDATES_ARCHIVE`** — the archive has no counterpart because the key landed after it was written. **The
>   absence is EXPLAINED and is not a finding.**
> - **`EXPECTED_PRESENT`** — the archive should carry it. **Absence is a hard finding.**
>
> **AND THE EXCUSE IS MACHINE-CHECKED, NOT NARRATED, BECAUSE THE MAP ALREADY CARRIES ITS OPERAND: every row has
> a `landed` string** (`"5856eeb1 BEN-106 2026-08-11"`, `"lane D 2026-08-18"`, …) **and the archive's own file
> date is readable.** So `PREDATES_ARCHIVE` is **DERIVABLE**: assert `landed_date > archive_date`, and a row
> claiming it while landing *before* the archive is itself the finding. **The comparator verifies its own
> exemption.** Nine keys at `2026-08-11` against an archive at `2026-07-14` classify automatically.
>
> **THIS IS §11i's DISCIPLINE ON A SECOND FIELD: an absence requires a STATED REASON, and the reason determines
> the verdict.** Same as `recomputable: no` requiring a writer-gap-versus-impossibility distinction, and the same
> species as `BEN-290` — **a two-valued field standing where three states exist, its third state reached only by
> real data.**

**AND THE PART THAT MUST NOT DISSOLVE: THE ARCHIVE'S AGE IS AN EXPLANATION, NOT A LICENCE.**

> **A `PAYLOAD` key uncompared because the archive predates it is NOT VERIFIED BY THE ANCHOR AT ALL** — the
> member could carry it wrong and stage 1 would pass. **So: a key uncompared by reference-absence MUST be
> covered by mandatory recomputation from the member's own file (§11i), or DECLARED UNVERIFIED.** Declared beats
> silent, and `upstream_*` stamps will mostly land in the second bucket.
>
> **AND §17c's TWO-NUMBER RULE GENERALISES FROM ELEMENTS TO KEYS: the report states KEY COVERAGE.** Stage 1's
> anchor compares **4 of ~13 keys** on that artifact. **That number belongs in the verdict, because a `PASS` over
> four keys and a `PASS` over thirteen are different claims wearing one word** — which is §17's whole argument,
> one level up from matrix elements.

### 19e. RULED on D's second finding — **five `[FAIL]` paths RETURN `INCOMPLETE` TODAY; every one of them must exit 2**, and my own §17 makes this a PRECONDITION rather than a parallel item

*(Heading rewritten 2026-08-19 on D's report. It previously read *"every `[FAIL]` path MUST EXIT 2"* — the RULING — directly above a body establishing that the sites exit `1`, the PRE-FIX EVIDENCE. Correct once read carefully; **on a skim it reads as its own negation, and D began drafting a "your heading contradicts your body" correction before checking.** **Second instance in this document of the class §19a is about: a SUMMARY that a careful reader must defend the body against** — there the summary hid a closed item, here the heading inverted its own evidence. One section apart, and I wrote §19a first.)*

**Confirmed by reading:** `:314` returns `{"PASS": 0, "INCOMPLETE": 1, "FAIL": 2}[verdict]`, while
`raise SystemExit("[FAIL] …")` at **`:144`, `:177`, `:179`, `:181`, `:213`** exits **`1`** — Python's default for
a string argument. **So five fail-closed paths PRINT `[FAIL]` AND RETURN `INCOMPLETE`,** among them
`zombie/unopenable` and `kRecovered (truncated/uncleanly-closed write)` — the corrupt-archive detectors.

> **AND `INCOMPLETE` IS A DELIBERATE, MEANINGFUL STATE, WHICH IS WHAT MAKES THE COLLISION DANGEROUS RATHER THAN
> UNTIDY.** `:236`: *"`compare()` returns INCOMPLETE while any recompute-required key is unverified."* **So `rc=1`
> genuinely means two things — *"proceed, some recomputes unverified"* and *"stop, the archive is corrupt"* — and
> a driver treating `2` as stop and `1` as continue walks straight past a truncated file.**
>
> **RULED: every `[FAIL]` exit returns `2`. The printed verdict and the exit code are TWO CHANNELS AND THEY MUST
> NOT DISAGREE** — a defect whose human-readable channel says `FAIL` while its machine channel says `INCOMPLETE`
> is the worst available arrangement, because **the human review passes and the automation proceeds.**
> `BEN-290`'s remedy verbatim: *enumerate a verdict-flag's states and name the ones meaning "no measurement"*.
>
> **⚠ AND THE SEQUENCING IS MINE TO OWN: §17c's streaming full-array pass touches far more of every file, so it
> MULTIPLIES the opportunities for a corrupt-file fail-closed exit.** **Therefore (b) is a PRECONDITION of §17's
> implementation, not a parallel fix** — landing the full-array digest first would increase the exposure to a
> defect that is already live. **My ruling raised the risk; the ordering is my responsibility and not B's.**

### 19f. **THE BIT-EXACTNESS DEPENDS ON THE SUMMATION ROUTE — a latent pin with nothing pinning it**

**D's caveat, and it is the most easily lost thing in the report: all four recomputations are bit-exact on the
real archive BECAUSE numpy's pairwise summation is on both sides** — `np.trace` in the writer,
`np.sum` in `_sqrt_trace_from_diag`. **A sequential Python sum of the same diagonal differs in the last ulps on
all three sqrt-traces.**

> **So the gate passes on a property of the SUMMATION ROUTE, not of the mathematics, and nothing asserts it.
> Anyone "simplifying" either side to a loop breaks the gate with a change that reviews as a no-op.**
>
> **RULED, in the executable form: a control that asserts BOTH directions — that `_sqrt_trace_from_diag`
> reproduces the writer bit-exactly, AND that a naive sequential sum DOES NOT.** The second half is the one that
> matters: **it makes the dependency visible, and it fails the moment someone removes it.** A comment cannot,
> because a comment is exactly what a no-op-looking refactor steps over. *(A filter needs a test in the
> direction it acts, applied to an accidental invariant rather than a guard.)*

### 19g. ATTRIBUTION, and what HELD

**D declines the two ratios and it is right to: `484,384:1` and `161,461:1` are mine.** D supplied the operand
(`10,694 x 8 B = 85.6 kB` against `41.44 GB`); the mediator relayed `~484,000:1`; **I did the divisions and the
`46 x 0.915 = 42.09 GB` route, and D has independently reproduced both** (`484,382` / `161,461` — the first
differs in the last digit by rounding of the operand). **Confirmation, not authorship, and worth keeping straight
because the value of an independent reproduction is destroyed by mistaking it for the original.**

**RECORDED SO IT IS NOT RE-LITIGATED — three things HELD on first contact with real archive data:**
`read_keys_pyroot` **executed correctly** (its author's own flagged worry was unfounded); **all four
recomputations are bit-exact**; and **`rtol` cannot loosen the payload comparison at all** — it reaches only the
recompute check. **The gate's tolerance surface is therefore smaller than I had assumed, which is the one piece
of good news in the report and deserves to survive the four corrections around it.**

## 20. B's IMPLEMENTATION ACCEPTED — **and gate 2 is still UNMET, because the path that replaced the defect has never executed**

**`origin/lane-b-member-axis-wip` @ `8164266b`. All four of D's defects fixed, every ruling in §§16-19 applied,
suite 1845 passed / 4 skipped / 3 failed with the three reproducing at baseline `8e48a811`.** The work is
substantially better than what I ruled, and three of B's formulations are better than mine (§20d).

### 20a. ⚠ **GATE 2 REMAINS UNMET. B labelled this correctly and the label is not a discharge**

**`_th2_content`'s own docstring says so, in terms I would not improve on:** *"NOT EXECUTED ANYWHERE. ROOT is
absent on the machine this was written on, so the buffer fast path below is unverified and falls back to a row
loop. Labelled rather than claimed."* **D's execution was against the DIAGONAL version, so the buffer read has
never run.**

> **That labelling is the honest form and it is exactly what I asked of everyone all campaign. It is also not a
> discharge: an unverified reader sitting in the gate's critical position is unverified, however accurately it
> says so.** Gate 2's whole content was *"a bit-exact comparator existing at all"*, and the reason I said to
> guard it hardest is that **a comparator existing is not a comparator being right** — which was proved once
> already when the thing that existed read `0.00935 %`.

### 20b. ⚠ AND READING IT FOUND A DEFECT THE FALLBACK CANNOT CATCH — **the fast path can succeed and be WRONG, and then coverage reports `100 %` of the wrong bytes**

```python
    try:
        buf = h.GetArray()
        buf.SetSize((nx + 2) * (ny + 2))
        flat = np.frombuffer(buf, dtype=np.float64, count=(nx + 2) * (ny + 2))
        return np.ascontiguousarray(flat.reshape(ny + 2, nx + 2)[1:ny + 1, 1:nx + 1])
    except Exception:
        # FALLBACK, correct but slow.
```

**1. A BARE `except Exception` OVER FIVE OPERATIONS MAKES THE FAST PATH'S FAILURE INVISIBLE.** Any failure in
`GetArray`, `SetSize`, `frombuffer`, `reshape` or `ascontiguousarray` yields a silent fallback that returns the
**right answer**. **So the fast path can be permanently broken and no run will ever say so** — a defect that
produces a correct-looking result, which is the shape every ruling in this document is about.

**2. THE FALLBACK IS REACHED ONLY IF THE FAST PATH *RAISES*, AND THE DANGEROUS FAILURE DOES NOT RAISE.** A
wrong `dtype`, a `TH2D` stored single-precision, an off-by-one in the under/overflow slice, a future ROOT layout
change — **each returns an array of the RIGHT SHAPE containing WRONG NUMBERS. The fallback never triggers, and
the new coverage line reports `compared 114,361,636 of 114,361,636 (100.00 %)`.**

> **`100 %` COVERAGE OF THE WRONG BYTES. That is §17's defect one level down: in §17 the WORD was wrong and the
> bytes were right; here the word would be right and the bytes wrong.** The coverage line I ruled into existence
> would state it with full confidence, **because coverage counts elements COMPARED and cannot see whether they
> were READ CORRECTLY.**
>
> **RULED, and it is free: CROSS-CHECK THE TWO PATHS AGAINST EACH OTHER, BIT-EXACTLY, ON AT LEAST ONE REAL
> MATRIX, ONCE.** They compute the same quantity by independent routes, so **the check needs no oracle and no
> fixture** — and it is the ONLY test that can catch a fast path that succeeds-but-wrong, which the fallback is
> structurally unable to do. One slow read of one matrix, once, against `origin/lane-b-member-axis-wip`'s own
> archive files.
>
> **AND THE FALLBACK MUST ANNOUNCE ITSELF.** A silent fallback means the coverage line reports numbers produced
> by **a path nobody chose**. **WHICH READER EXECUTED IS AN INGREDIENT OF THE DIGEST and belongs in the receipt**
> — `BEN-077` applied to the instrument rather than the result, the same move §17c made for the reduction.
> Narrow the `except` to the exceptions actually expected, too: a bare catch here is a promise that every future
> failure is benign.

**3. A LATENT HAZARD THAT MY OWN §19b RULING JUST MADE LIVE, AND IT REVIEWS AS A NO-OP.** `np.frombuffer` returns
a **VIEW** of ROOT's buffer. The return is safe today only because `flat.reshape(ny+2, nx+2)[1:ny+1, 1:nx+1]` is
**non-contiguous** — the `±1` under/overflow padding guarantees it — so `np.ascontiguousarray` **copies**.

> **If anyone ever removes the padding arithmetic, the slice becomes contiguous, `ascontiguousarray` returns its
> input UNCHANGED, and the function returns a VIEW into a ROOT buffer.** And §19b ruled **explicit
> `obj.Delete()`** to make one-key-at-a-time real — **so the freed object and the live view now coexist by
> construction.** Two of my own rulings, each correct, whose interaction is a dangling read.
>
> **PIN IT: assert the returned array does not share memory with the buffer** — `np.shares_memory(out, flat)` is
> `False`. **One line, and it fails exactly when the padding logic is "simplified".** *(Same species as D's
> summation-route finding: an accidental invariant holding up a gate, with nothing asserting it. And `BEN-425`'s
> lesson — two rulings each correct and jointly destructive is what B said it would not have caught from inside
> one of them; this is the second such pair today and I made both halves.)*

### 20c. ⚠ **MY §19e ENUMERATION WAS PARTIAL: FIVE SITES NAMED, EIGHT REAL** — and D's point about the record is the important half

**D verified H4 by reading and found `origin/lane-b-member-axis-wip:nd-unfolding/mii_root_payload_classes.py`'s three additional raises — `classify`'s two
and `_g2_baseline`'s group check — reachable from `compare_files` on every run and absent from my list. All eight
now route through one `classes.fail_closed`.**

> **B fixed more than I ruled. D's observation is the one to keep: an auditor checking *"the five sites C named"*
> would find them fixed and conclude the ruling was fully implemented — and that conclusion would be TRUE BY THE
> IMPLEMENTER'S DILIGENCE AND NOT BY THE RECORD.**
>
> **A partial enumeration that happens to be repaired in full leaves nothing behind saying it was partial.** Same
> shape as my `derive: None` gap, and as §19a's summary, and as §19e's heading. **Recorded here so the record
> carries the deficiency the implementation absorbed** — because the next enumeration of mine will be trusted at
> the width it states.

### 20d. THREE FORMULATIONS OF B's AND ONE OF D's THAT ARE BETTER THAN MINE, recorded as theirs

- **B, on why `derive: None` was never a class question: *"A class is a COMPARISON RULE; it has no content when
  one side cannot have the key at all."*** **That is a cleaner statement of §19d than §19d makes**, and it is my
  own §11i structural argument — *these are attributes, not a fourth class* — **turned around and used to find
  where my taxonomy stopped reaching.** The map's `derive: None` case is OUTSIDE the class system, not a member
  of it.
- **B, on the CV reversal: *"I compared the right two objects under the wrong functional."*** **A distinct
  register of the asymmetric-comparison family** — mine have been wrong-denominator and wrong-scope; this one has
  both objects right and the *statistic* wrong. **Worth its own name because the usual repair (check both sides)
  does not touch it.**
- **B, on the constant: *"A GRID IS NOT AN ARTIFACT SIZE"*, and the deeper half — `EXPECTED_ELEMENTS` is now
  per-key, each traced to a writer's construction line, and a key with no derived expectation gets coverage
  PRINTED AND NOT ASSERTED.** B's reason: *"asserting a number I have not read out of a writer is how the wrong
  constant arrived."* **That is `BEN-467`'s rule as a code invariant, and it is stronger than the comment
  discipline I ruled** — an expectation traced to a construction site cannot go stale silently.
- **B, on H3's asymmetry: *"an enumeration from the producer side systematically misses artifacts whose producer
  is out of scope."*** **Sharper than my *"D's list was longer"***, and it explains rather than observes.
- **D, extending `BEN-467` past comments: it is `CLAUDE.md`'s *prefer the executable form* arriving from the
  opposite direction — not *"make it a check"* but *"STATE THE INVARIANT, NOT ITS CURRENT VALUE"*, which works
  where no check is possible.** And D's framing of the procedural half: **not citation hygiene but PROPAGATION,
  and the callee is where it bites.**

### 20e. Accepted without qualification, and what remains

**ACCEPTED:** the full-array digest with per-key coverage printed and partial coverage FAILING; `DECLARED_REDUCTIONS`
empty behind `assert_reduction_is_declared`, so **a reduction costs a measurement rather than a line**; `--cv`
member-scoped with the bias DIRECTION at the call site and byte-identical when no offset is declared; `derive: None`
recorded **UNCOMPARABLE — admissible and NOT verified**; `identity_is_checkable` with the other three reporting
UNCHECKABLE and (A) widened to `LATERAL_CV`; one `fail_closed` at exit 2 carrying `.fail_message` — **B's
refinement, and right: `SystemExit(2)` alone leaves an in-process caller holding a number with no reason.**

**REMAINS, and only the first is mine to press:** the two-path cross-check and the announced fallback (§20b);
`mask_order_hash` not yet built, correctly not claimed, with the archive's two CVs as its positive control;
and the three suite failures, which B reports reproducing at baseline `8e48a811` — **a claim I have not
independently checked and am not treating as verified.**

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
> chain.** `nd-unfolding/AUTONOMOUS_LOG_20260805.md:48` measured it: **`block_slabs_5d` holds 8 files,
> `block_slabs_5d_sb` holds 36.** The tracked block producer has been writing a stale partial that nothing
> consumes. *(Citation repaired 2026-08-18 from the bare basename, which matches TWO tracked logs — the other
> being `nd-unfolding/pet/AUTONOMOUS_LOG_20260805.md`. **This is the DANGEROUS form of `BEN-380`: the two
> candidates' line 48 say ENTIRELY DIFFERENT THINGS** — the `pet/` one is about a `certifies` field and contains
> no `block_slabs_5d_sb` at all — **so a reader resolving the wrong way would find an unrelated sentence and
> conclude this ruling misquoted its source.** Found by `lanec_citation_resolution_check.py`, not by reading.)*

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

### 12b. RULED on the corroboration — **REPAIRED, not withdrawn. `_sb`'s 40 IS the right number, and my COUNTING METHOD was the defect**

**The `ls` came back with both directories live:**

```
uthrow_slabs_5d      npz=160   newest 2026-07-12      <- non-canonical
uthrow_slabs_5d_sb   npz= 40   newest 2026-08-06      <- the contract binds this
block_slabs_5d       npz=  8   block_slabs_5d_sb  npz=36
```

**Neither offered branch is right, because `40` is not a partial population — it is the CANONICAL one in a
different LAYOUT.** `sbatch_uthrow_run_5d_fast.sh`, verbatim:

```
:5   #SBATCH --array=0-39%40
:9   # 40 tasks x 4 throws = 160 throws, offsets t*4..t*4+3 -> union 0-159.
:12  # ... the batch id-layout (4 throws/file) never collides with the interactive layout (1/file)
:29  --out "uq_5d/uthrow_slabs_5d_sb/uthrow5d_slab_${SLURM_ARRAY_TASK_ID}.npz"
```

> **40 files × 4 throws/file = 160 throw ids = draw seeds `1000…1159`. The canonical directory corroborates the
> range EXACTLY.** So the corroboration is **REPAIRED and it agrees**, and the mediator's open question — *"I
> have NOT established what 40 means"* — is answered by the launcher's own comment rather than by a guess.
>
> **AND `160` WAS NOT A COINCIDENCE OF CARDINALITY EITHER.** The non-canonical directory is the **interactive
> 1-throw-per-file** layout of *the same 160 ids*. Both directories encode 160 throws. **My original number was
> RIGHT — by an accident of layout, because 1-per-file makes file count equal population count.**

**WHAT IS WITHDRAWN IS MY COUNTING METHOD, and that is the part worth keeping: `BEN-465`.** A file count is not a
population count, and it is only ever equal to one when a layout happens to be 1:1.

> **⚠ AND THE WARNING WAS IN THE DOCUMENT I READ BEFORE RULING.** `SPEC-20260818` §2: ***"Do not specify `K_j`'s
> correctness by FILE COUNT — historical layouts pack units differently."*** Codex wrote it about the block leg.
> **It applies verbatim to the throw leg, I cited that spec in the same determination, and I did not apply it to
> my own evidence.**

**THE CORROBORATION TO RUN, and my own §11b already names the operand:** `throws` is CONFIGURATION in the throw
slabs, so the check is **the union of the `throws` arrays across the 40 canonical slabs equals `{0…159}`,** with
no duplicates.

> **That is strictly stronger than any file count, because it catches a duplicated or missing id that every
> cardinality check passes** — and `protect_throw_slabs.py:52-55` is this repo's own precedent for exactly that
> failure: a directory-blind filter *"silently under-protected the set by a third… found 365 of 542 files and
> reported `365 readable, 0 unreadable`, which reads as complete."*

**AND THE DAMAGE IS BOUNDED TO ONE OF THE THREE, which is worth stating precisely.**
`sbatch_bootstrap_5d_gpu.sh:25` writes `res_boot_${SLURM_ARRAY_TASK_ID}.npz` and
`sbatch_seedscan_split_5d.sh:20` writes `res_split_${SLURM_ARRAY_TASK_ID}.npz` — **one product per id by
construction, so file count IS population count for those two, and `100`/`24` stand as corroborations.** Only the
throw leg packs, and only the throw leg's corroboration needed repair.

**Consequence for `P-ANCHOR`: its throw-leg availability answer must be re-run against `_sb`.** The `160 ✓` was
against a directory the contract does not bind, and a month older.

### 12c. ⚠ PATH SHAPE — **MEMBER-ROOT-FIRST, and I meant it literally. The inconsistency is MINE, in my own document, not in the relay**

**The mediator offers to own this as a paraphrase defect. It is not one.** My §12 says
`member_kXXXXXX/uq_5d/block_slabs_5d_sb/` — **member first, literally** — and my §5 endorsed B's implementation,
which is **namespace-then-member**: `lib_member_resume.sh:64-71`'s `mr_prefix` inserts the member directory
**before the basename**. **Two sections of one document disagree, and the paraphrase was faithful to §12.**

> **THE ENDORSEMENT IN §5 WAS OF THE NAME, AND I EXTENDED IT TO THE PLACEMENT WITHOUT NOTICING THEY WERE
> SEPARATE DECISIONS.** B's offset-derived *naming* — `member_k%06d/` rather than an index — **stands, and every
> argument in §5 is about the name.** Its *placement* is a different question and §5 gave it no argument at all.

**RULED: MEMBER-ROOT-FIRST, under an `mii/` container, exactly as spec §1 derives it** —
`mii/member_k001200/uq_5d/block_slabs_5d_sb/…`. **Not on my preference: on two mechanisms.**

**(1) SPEC §1's PREFLIGHT IS UNWRITABLE UNDER NAMESPACE-THEN-MEMBER.** It requires *"a preflight must reject any
member output path equal to, under, or glob-overlapping the six canonical archive namespaces."* **Under
namespace-then-member EVERY member path is under a canonical namespace by construction** —
`uq_5d/block_slabs_5d_sb/member_k001200/` is literally beneath `uq_5d/block_slabs_5d_sb/`. So the preflight
either rejects all 50 members or needs an *"under, but with a member component"* exception. **A guard that must
special-case the thing it guards is the shape this campaign has spent the day removing.** Member-first makes it a
one-line prefix test in both directions: every member path starts `mii/`, no archive path does.

**(2) IT PLACES 50 MEMBER TREES AS SIBLINGS INSIDE THE DIRECTORY THE ARCHIVE'S OWN CONSUMERS GLOB.** The combine
globs `'uq_5d/block_slabs_5d_sb/block5d_*.npz'`. **The only thing keeping 50 members out of that glob is that
shell globs do not recurse — and the absence of exactly that property is what caused the Q1 defect.** One `*/`,
one recursive-glob, one `find`, one `rsync` and members cross-contaminate or a member's products are swept into the
archive's combine. **Relying on non-recursion as a safety property, in the same document that ruled on a defect
caused by non-recursion, is backwards.** Under member-first the archive's namespace contains only archive
products, forever, by construction.

> **CONSEQUENCE, and it is mine: the 16/16 probe pass is INVALIDATED and must be re-run against the corrected
> shape.** The mediator identified it as a one-line change in `mr_dir_prefix`. **B flagged rather than resolved,
> which was exactly right — a builder that had silently taken either reading would have left a document disagreeing
> with an implementation and a probe certifying the wrong one.**

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

### 14a. AMENDED — **`hInflation_g` ALREADY SHIPS THE MASK, so my addition reduces to the operands**

**The mediator found that `hInflation_g` is a key in the adopted root. That is `adopt_unified_5d.py:112`'s `g`,
and it is the mask:**

```
g = sqrt(max(vu,vb)) / sqrt(vb)      g == 1  <=>  vb won        g > 1  <=>  vu won
and wherever g > 1:  vu = g^2 * vb   <-- so g plus vb RECOVERS vu on the vu-wins region
```

> **So §14's winner mask is ALREADY A SHIPPED PRODUCT and B should not build it. What is genuinely missing is
> `vb`** — with which `g` recovers `vu` wherever `vu` won — **plus `vu` itself in the CENSORED region `g == 1`,
> where `g` says only `vu ≤ vb` and the distance to the kink is unrecoverable.**
>
> **That is exactly the "by how much" half §14 identified, and it is now the ONLY half.** Ship `vb` and `vu`;
> note in the receipt that `g` is the mask and is redundant with them wherever `g > 1`.

**AND A NUMBER OF MINE THAT WAS WRONG: §14 said "three arrays of ~285 floats."** ~~The 5D flat length is
**65,856**, so each array is **`0.527 MB`**, not `~2 KB` — **wrong by 230×.**~~

> **⚠ CORRECTED AGAIN, 2026-08-18, AND THE SECOND CORRECTION WAS ALSO WRONG — IN THE OPPOSITE DIRECTION.**
> **Each array is `10,694` doubles = `83.5 KiB`, not `0.527 MB`.** `65,856` is `p4_lib.py:22`'s
> `GRID_NBINS = 14*16*7*7*6`, the FULL 5D grid — and `hXSecND_flat` really does have that many bins, which is
> why the number looked verified. **But `adopt_unified_5d.py:120-121` masks it:** `x = xfull[xfull > 0]` then
> `assert x.size == n`, so `vb`, `vu`, `diag_comb` and `g` are all on the **REPORTED** set. The stored
> covariance is `10,694 x 10,694` and `hInflation_g` has `10,694` bins
> (`ADVISORY-20260813-oi30-eavail-residuals.md:286-288`).
>
> **SO: `~2 KB` (too small), then `0.527 MB` (too big by 6.16x), and the truth is `83.5 KiB` between them.
> THE MECHANISM IS THE ONE I NAMED IN THIS VERY PARAGRAPH AND THEN COMMITTED WHILE NAMING IT — "a quantity true
> at its own scope quoted at another." I repaired a wrong index by substituting a DIFFERENT wrong index, because
> I asked "what is the 5D flat length" instead of "WHICH INDEX DOES THIS ARRAY USE."** The second question is the
> only one that was ever about the arrays. *(It came from the extended-FPS `15×19 = 285`
grid, a different product entirely — a quantity true at its own scope quoted at another.)* **The ruling is
unchanged, because `83.5 KiB` against a `4.46 GB` retained member is still unmeasurable — but I stated a number
and it was the wrong one.**

*(This is the fourth time today that checking before building removed work rather than adding it: cause 1's census
already existed, the manifest freeze covered 4 entries not 77, `finalize` was already inside the priced `39.078`,
and now the mask is already in the product. Worth noting as a rate, not an anecdote.)*

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
- **RULED (§12b): the throw-range corroboration is REPAIRED, not withdrawn** — `_sb`'s 40 files × 4
  throws/file = 160 ids, exactly the range. **My COUNTING METHOD is what is withdrawn (`BEN-465`), and the
  spec I cited had already warned against it.** The fresh check reads the `throws` id arrays, not files.
  **Bounded: bootstrap and split are 1-product-per-id, so `100`/`24` stand.**
- **RULED (§12c): MEMBER-ROOT-FIRST under `mii/`**, per spec §1 — because the spec's preflight is
  unwritable otherwise and namespace-then-member puts 50 member trees inside the directory the archive's
  consumers glob. **My §5 endorsed B's NAME and silently extended to its PLACEMENT; the inconsistency is in
  my document, not in the relay, and it invalidates the 16/16 probe.**
- **RULED (§11d): a declared KEY-RENAME/SPLIT MAP for the archive side**, written before stage 1 — archive
  `seed` → `(estimator_seed, draw_seed)`. **And `bands` classified CONFIGURATION; the fail-closed rule fired
  on it correctly, on real data.**
- **RULED (§11f): the missing ROOT seed stamp is a FIFTH stage-1 gate.** At stage 1 a bit-exact pass and
  *"you compared the archive to itself"* are the same observation, because the ensemble's digest-distinctness
  backstop needs more than one member. **Both remedies: member ROOT writers stamp the offset, AND a product
  class that cannot carry an identity stamp can never be resumed.**
- **CORRECTED (§11f-ii): `dataPOT` is CONFIGURATION, not provenance** — it enters the arithmetic. Second
  instance of `train_frac`'s pattern: **a scalar that enters the arithmetic looks like a stamp because it is
  recorded once and never varies.**
- **FLAGGED (§11f-iv): the bar's `block_sum` is NOT among the terminal product's 9 keys**, so stage 1's
  scope as listed does not cover the quantity the bar tests.
- **RULED (§11g): the 41.44 GB per-universe covariance MUST be produced per member and NEED NOT be
  retained.** Consuming the archive's would freeze the sweep leg — `61 %` of the GPU bill. Retention:
  `223 GB` + `41.44 GB × concurrency`, so `52.1 %` of remaining scratch headroom becomes `8.8 %` at four in
  flight. **Deletion gated on `MVFINAL_j`: nothing accepted without a stamp, nothing deleted without one.**
  **And the bar's operand is located — `sqrt_tr_old` in the adopted roots — so §11f-iv's gap is CLOSED and
  those two 892 MB files join stage 1's scope.**
- **AMENDED (§14a): `hInflation_g` already ships the winner mask**, so R4 reduces to `vb` plus `vu` in the
  censored region. **And my "~285 floats" was wrong by 230× — the 5D flat length is 65,856.**
- **AMENDED (§11h): the `diag(C_old)` TH1D SHIPS BEFORE the intermediate is released** — `1.58 MB` against
  `41.44 GB`, and `adopt_unified_5d.py:128` already computes it. **The general defect is mine: a retention
  policy must be tested against the derived quantities that SURVIVE, and a deletion can retroactively break
  `BEN-077` for an artifact that was compliant when written.** §11g releases MEMBER intermediates only; the
  archive's copy is untouched.
- **RULED (§11i): NOT a fourth class — a required `recomputable: yes|no` ATTRIBUTE on `PAYLOAD`**, declared
  in the enumeration, `no` requiring a stated reason, and B's acknowledge-flag taking the explicit key list.
- **AMENDED (§11j): remedy (A) is MANDATORY on the adopted roots** — the failure there is ADMISSION, which
  (B) cannot reach.
- **CORRECTED (§15a): stage 0's `~16 %` is `98.25 %`.** `10,507` changed bins is over the reported set of
  `10,694`, not `p4_lib.py:22`'s full grid of `65,856` — a `6.158x` mis-scaling, and the campaign's own
  `ADVISORY-20260813-oi30-eavail-residuals.md:289` already warns that these two indices *"index different
  things"*. **The seed moves essentially EVERY reported bin.** Verdict DISTINCT unaffected.
- **RULED (§15b): leg B's support is the PREDICATE `xfull > 0` on the member's own `hXSecND_flat`**, not a
  bin count — because leg B's `2.74 %` is calibrated to `\gbdtFiveBlockMedian`, which is that masked
  median. **Over the full grid ~84 % of entries are `0/0`.** Fixed before any `f_med` exists, and it makes
  the bar HARDER: at `98.25 %` responding, the predeclaration's concentrated branch is not operative, so
  leg B genuinely binds.
- **CORRECTED TWICE (§14a): each R4 array is `83.5 KiB`** — `10,694` doubles, not `65,856`. My first
  correction substituted a different wrong index; §11h's diagonal write is `250.6 KiB`, not `1.58 MB`,
  making the trade against the released intermediate `161,461:1`.
- **RULED (§16a): STOP AFTER (3) CONFIRMED — and it is a PAUSE, not a boundary of stage 1**, because
  `sqrt_tr_old`, the bar's own operand, is written at `adopt_unified_5d.py:177` inside (4)/(5). Building
  (4)/(5) unstamped REFUSED (§11j: they are the terminus). **Nothing is deletable during the pause** — and
  the cut must carry its EXPIRY CONDITION, remedy (A), because it is right for one member and `2.087 TiB`
  wrong for fifty. **Remedy (A) is now the critical path.**
- **RULED (§16b): the flat-norm band multiplies the MEMBER'S CV** — the member re-unfolds its CV at
  `42+k`, so pinning freezes a seed channel (`0.573 %` on one term = `13.8 %` of leg A's budget) and
  **biases toward `MET`: pinning is safe for REFUTING met, unsafe for ASSERTING it.** CONDITIONAL on the
  archive's two CVs agreeing — cheap, and if they differ, pin and record the frozen leg WITH its direction.
  **`0.014` itself is member-invariant; B's `cv` cancellation (`max abs diff 0.0`) accepted.**
- **RULED (§16c): the diagonal lands NOW, in the same change as remedy (A)** — same writer, both
  preconditions of (4)/(5), so it is touched once before it ever runs for a member.
- **RULED (§16d): a SIXTH stage-1 gate — the `cv > 0` support is compared as a SET, never a COUNT.** Two
  supports of equal SIZE can differ in MEMBERSHIP, which shifts the flat ordering and makes a bit-exact
  comparison compare the wrong pairs SILENTLY. **`p4_lib.py:1196` `mask_order_hash` already exists and
  already fails closed** — B should not build one. Mask is `CONFIGURATION`: equality is a hard failure.
- **RULED (§17): GATE 2 IS UNMET — the comparator digests only the DIAGONAL**, `10,694` of `114,361,636`
  elements = `0.00935 %`, with `~997x` the mass off-diagonal. A diagonal digest is a bit-exact comparison
  of a PROJECTION; reporting it as a payload comparison is a category error. **Full-array digest ruled,
  one key at a time (`0.915 GB` peak); any reduction must declare ELEMENT COVERAGE and MASS FRACTION
  OUTSIDE.**
- **§17b: the reduction covers EXACTLY the bar's operand** — `sqrt(trace)` is diagonal-only — **so it
  would yield a bar-consistent PASS with the correlations never read.** `project_cov_nd.py` marginalises
  those off-diagonals, so the *"only the trace matters"* defence fails.
- **§17a: my §11f-i undercounted — THREE indistinguishable observations, not two.** The third (a member
  reproducing `10,694` numbers and nothing else) is separated by nothing at present. **I ruled on the
  comparison's LOGIC without asking its EXTENT.**
- **AMENDED (§17d): remedy (A) covers `LATERAL_CV` too**, not only the adopted roots — D enumerated the
  artifacts the gate cannot read and that list was longer than my list of writers needing stamps.
- **§17e: `484,384:1` (one array) and `161,461:1` (three) are both right**; and the corrected `0.915 GB`
  matrix size **explains** the `41.44 GB` file as `46 x 0.915`, which my wrong `34.7 GB` never could.
- **RULED (§18): the §16b conditional is DISCHARGED — SUBSTITUTE, the member's own `uni_full_CV`.** The
  two archive CVs share **identical support MEMBERSHIP bin-for-bin** and totals to `0.03 %`, so they are
  the same quantity. **And my own §16b sentence was TOO BROAD: *"injects a difference that is not
  estimator noise"* is the right test for comparing VALUES, but the bar compares SPREADS — the
  product-offset is COMMON-MODE across all fifty members and cancels in `sd` to first order, while
  PINNING ZEROES the term's spread contribution at FIRST order, biasing toward `MET`.**
- **§18b: the archive's two CVs are a ready-made POSITIVE CONTROL for `mask_order_hash`** — the gate-6
  instrument ran here incidentally, on a set identity rather than a count, and PASSED.
- **§18c: the median-magnitude coincidence (`5.754e-03` vs stage 0's `5.098-6.273e-03`) is CONSISTENT
  with the seed reading and discriminates against nothing** — same magnitude is not same cause, and the
  ruling does not rest on it.
- **§18d: flagged, NOT mine — two archive CVs differ on `100 %` of support, `28.8 %` above `1 %`,** and
  nobody has recorded it. A reproducibility item for the archive's CV owner. **Do not quote the
  `max = 1.262e-01`** — one bin, near-zero denominator, `BEN-064`.
- **CORRECTED (§19a): §17a's *"nothing separates the third"* is WRONG — §17c separates it.** I stated a
  gap and its remedy in one section without connecting them, which is worse than either alone.
- **CORRECTED (§19b): peak memory is `~2 GB` per LIVE `TH2D`** (measured `2,027 MB` / `3,773 MB`; ROOT
  resides `sumw2` alongside contents), not `0.915 GB`. **"One key at a time" is now a REQUIREMENT and
  needs explicit `obj.Delete()`** — `:182-183` holds every object until `f.Close()`.
- **⚠ (§19c): I CORRECTED THE NUMBER IN MY DOCUMENT AND NOT AT THE CALLEE.**
  `origin/lane-b-member-axis-wip:nd-unfolding/mii_root_payload_classes.py:39` `FLAT_NBINS = 65856` and its comment carry my `0.527 MB` verbatim, and
  `origin/lane-b-member-axis-wip:nd-unfolding/mii_anchor_comparator.py:171` derives `34.7 GB` from it. **The constant written to prevent my first
  error encodes my second. A comment that records a corrected VALUE inherits the next error; one that
  records the DERIVATION cannot.**
- **RULED (§19d): `derive: None` is SPLIT into `PREDATES_ARCHIVE` / `EXPECTED_PRESENT`, and the excuse is
  MACHINE-CHECKED** against the `landed` string the map already carries versus the archive's file date.
  **The archive's age EXPLAINS an absence and does not LICENCE it: an uncompared `PAYLOAD` key must be
  covered by recomputation or DECLARED UNVERIFIED — and the verdict states KEY COVERAGE (4 of ~13),
  §17c's rule one level up.**
- **RULED (§19e): every `[FAIL]` path exits `2`.** Five exit `1` = `INCOMPLETE`, including
  `zombie/unopenable` and `kRecovered`. **The printed verdict and the exit code must not disagree.** And
  **§17c multiplies the exposure, so this PRECEDES §17's implementation — my ruling raised the risk.**
- **RULED (§19f): the bit-exactness depends on numpy PAIRWISE SUMMATION on both sides** and nothing
  asserts it. A control must assert BOTH that the recompute matches AND that a sequential sum does NOT.
- **§20a: GATE 2 IS STILL UNMET** — `_th2_content` has NEVER EXECUTED (ROOT absent where it was written);
  B labelled that honestly and **a label is not a discharge.**
- **RULED (§20b): CROSS-CHECK the buffer fast path against the row-loop fallback, bit-exactly, on one real
  matrix, once** — free, no oracle, and **the only test that can catch a fast path that SUCCEEDS AND IS
  WRONG, which the fallback structurally cannot.** A bare `except Exception` over five operations makes
  failure invisible, and a wrong-but-non-raising read would have coverage report **`100 %` of the WRONG
  BYTES** — §17's defect inverted. **The fallback must ANNOUNCE: which reader executed is an ingredient of
  the digest.**
- **§20b(3): two of my OWN rulings now interact destructively** — `np.frombuffer` returns a VIEW, safe only
  because the `±1` padding makes the slice non-contiguous so `ascontiguousarray` copies; §19b's explicit
  `obj.Delete()` puts a freed object and a live view together. **Pin with `np.shares_memory(out, flat)` is
  `False` — it fails exactly when the padding is "simplified".**
- **§20c: MY §19e ENUMERATION WAS PARTIAL — five sites named, EIGHT real.** B fixed more than I ruled, so
  **an auditor checking my five would credit the ruling for the implementer's diligence.** Recorded so the
  record carries what the implementation absorbed.
- **§19e heading rewritten** — it read as its own negation on a skim (D nearly filed a correction against
  it). **Second instance in this document of §19a's own class.**
- **AUTHORIZED: nothing.** No launcher edited, nothing submitted.

*Second sought: B on §3's derived-target predicate (its module) and on whether stage 1 can be run as a single
member without the ensemble machinery; the Codex session's `(A)` recommendation is already the second on item 6,
reached independently and before mine.*

# Sept 9, 2026 — Nachman ML group (V2: the verification thesis)

**Status:** merge of `DECK.md`'s physics spine with the agent-workflow material.
`DECK.md` is preserved unchanged as the fallback.
**Budget:** < 20 min. 8 slides, ~16:00 spoken, ~4 min questions. ~10 in the room, ~5 on Zoom.

> **Thesis:** In four and a half months of agent-driven analysis, the thing that broke was
> almost never the code. It was the **verification**: checks that reported success without
> exercising what they claimed. One of them sat in the published estimator. **The talk is a
> taxonomy of that failure and a spec for the instrument that catches it.**
>
> Framing: OmniFold is Andreassen, Komiske, Metodiev, **Nachman**, Thaler (PRL 124, 2020);
> PET is the OmniLearn backbone (Mikuni & **Nachman**, 2024). Both the method and the
> architecture are the group's. Say "your" — it's accurate, and it makes the ask *help me
> use your tools better.*
>
> **Emotional arc:** recognition (three Keras lines, two estimators) → scale (this is a
> class, not a bug) → structure (five mechanisms, enumerable) → craft (here is what a real
> instrument does) → productive discomfort (the agent writes the check that passes itself).
>
> **What is NOT in this talk, deliberately:** any productivity or speedup number. There is
> no counterfactual — no second version of this project run without agents — so every such
> number is unfalsifiable. Slide 3 says this out loud and it buys enormous credibility for
> everything after it.

**The sentence they should repeat at lunch:**
> **A green check is a claim about what it measured, and usually nobody checks what that was.**

---

## Slide 1 — "Three of the most common lines in Keras. Two different published estimators."

**Visual:** four boxes, built live.

```
best-validation epoch → saved checkpoint → reloaded inference → recorded push
                              ↑
        training ended on the LAST epoch, held only in memory;
        the file kept the BEST epoch.  Two different networks.
        aggregate validation: agree to 1e-4
        per event (on the step-2 push): differ by up to 86.6%
```

- The mechanism, and it is three lines you have all written: `save_best_only=True`,
  `EarlyStopping(patience=10)`, `epochs=8`. **Patience exceeds the budget, so best-weight
  restoration never fires.** The in-memory model is last-epoch; the file is best-epoch.
- **Why it isn't software hygiene:** in OmniFold the learned classifier *is* the estimator.
  There is nothing downstream of it. So "which epoch is the model" is *which estimator you
  published* — and the two candidates **pass identical aggregate validation** while
  assigning materially different weights to individual events.
- MINERvA in one breath: a neutrino scattering measurement. **Nothing after this slide
  depends on that.**

> ⚠️ **The 86.6% is measured on the step-2 push**, because that is what the reproduction
> gate compared (Gate B(i), checkpoint-rebuilt push vs stored, on `pass_gen`). Say "the
> saved classifier" or quote it on step 2 explicitly. **Never** "the step-1 classifier moves
> by 87%." And 86.6%, not "87%" — the receipt value is `8.663e-01`.

*(2:00. Land the last bullet hard: the validation was green, and it was blind.)*

**Transition:** "I want to convince you that isn't a bug. It's a specimen — and I have a
collection."

---

## Slide 2 — "One analysis, four and a half months, and a catalogue."  ⭐ CORE SLIDE

**Figure:** `verification_apparatus.png` — two panels, commits/month and findings/month,
with 2026-08-12 marked.

- Timeline: `2026-04-25 → 2026-09-08`, **2,839 commits**. Per month:
  **9 → 50 → 92 → 272 → 2,177 → 239** (September is 8 days).
- **2026-08-12 is when parallel agent lanes appear** — Lane A (orchestrator), Lane B
  (uncertainty), Lane C (PET), Lane D (verifier) all first commit that day. Median
  commits/day **6 → 40**. August splits **476** before the 12th, **1,707** after.
- What grew alongside it, and this is the actual claim: **141 validation-ledger rows, 149
  open-item records, 23 tracked findings documents, 128 tracked test files, 35
  guard-named files** across 1,991 tracked files.
- **The claim:** the apparatus is not overhead that accumulated. It is the *response* to a
  failure mode that scaled with throughput. Generation got cheap; verification did not.

*(2:00.)*

**Transition:** "That's a file count, though. Let me put four real quantities on it — and
one I'm not going to show you."

---

## Slide 2b — "Four quantities, and one that didn't survive."  *(first to cut if over time)*

**Visual:** four numbers, large, one per quadrant. Then the fifth beat, spoken.

- **Context read : generated = 249 : 1.** Across **204 sessions** and **90,956** assistant
  turns carrying usage: **118.4 M tokens generated**, **548.7 M** written to cache once, and
  **28.86 G re-read** from it. For every token this project produced, ~249 were re-read.
  **If verification is the bottleneck, that ratio is what it looks like.**
  - **Say the accounting trap out loud, because half this room has made it:** you cannot sum
    `input_tokens` across turns. Each turn's input contains the *entire* conversation prefix,
    so the sum double-counts context once per turn — here it inflates "tokens consumed" by
    roughly 250×. The additive fields are output, cache-creation and cache-read.
  - Generated tokens per session: median **164 k**, mean **580 k**, max **8.4 M**. **The top
    decile of sessions holds 60% of all generated output.**
- **I(lane ; file) = 2.02 bits, against H(lane) = 3.18 bits → I/H = 0.63.** Over 1,483
  lane-identified commits and 5,277 touch events: knowing *which file* was touched recovers
  **63% of the lane identity.** So the parallelism was about two-thirds decomposed — and the
  missing third is contention on shared control-plane files, which is exactly where
  two-lane composition defects come from. **70 declared lane identities collapse to an
  effective 9.1** (`2^H`).
- **Effective number of files under edit fell 0.64×** — `2^H` = **865 → 550** across the
  2026-08-12 boundary, Miller-Madow corrected and sampled at **equal N = 925** because
  entropy is biased low at small N and the two eras have different commit counts.
  **Meanwhile the support went *up*: 1,724 → 2,069 distinct files.** More files touched,
  and a more concentrated distribution over them.
- **The Fano factor is invariant across the transition: 44.0 → 42.2**, while mean
  commits/day went **14 → 68**. Variance scaled with the mean. That is what **adding
  independent sources of the same character** looks like — not a change in the character of
  the work. (Burstiness `B = (σ−μ)/(σ+μ)`: **+0.279 → −0.120**.)

> **And the one I'm not showing you, which is the point of the slide.** Commit sizes look
> beautifully heavy-tailed — top 1% of commits carry **65%** of all lines added. It's not
> real. That 65% is **four bulk data/manifest merges** (354 k, 218 k, 158 k, 137 k lines).
> On code lines only the top 1% carries **12.2%**, the fitted tail index **drifts 1.46 →
> 2.14 with the cutoff**, and a Vuong test against a lognormal **flips sign**: lognormal
> favoured at `xmin` 20 and 50 (p < 0.001), indistinguishable at 100 and 200. A real power
> law gives a stable exponent above `xmin`. **So: heavy-tailed, no exponent to quote** — and
> I only know that because I fitted it and it failed.

- **The filter, said once, because it is the transferable part:** a quantity earns a slide
  if it has a population I can name, a denominator that doesn't move when the story changes,
  and a null it could have failed. The four above clear it. The power law didn't.

*(2:30. If you are over time this whole slide goes and nothing downstream breaks — but the
249 : 1 and the dropped power law are the two best 20-second items in the talk, so consider
keeping those as spoken asides on slide 2 instead.)*

**Transition:** "Now — the commits number I showed you two slides ago is the wrong number,
and I want to show you why before someone asks."

---

## Slide 3 — "I cannot tell you what fraction an agent wrote, and that is the talk."

**Visual:** the committer histogram, then three strikes through it.

```
Joseph Bailey                        1354
MINERvA-OmniFold agent (unattributed) 557
Lane C (PET)                          147
Lane D (verifier)                     114
close-out lane                        105
Lane A (orchestrator)                  53
… 10+ further lane identities
```

- **Strike 1 — committer name is not authorship, and here is the floor.** **258** of the
  2,839 commits carry a `Claude-Session` trailer. **98 of those 258 are committed under my
  own name** — positive evidence of agent authorship sitting under a human identity. And
  because the trailer gives a **negative only** (its absence proves nothing), **98 is a hard
  lower bound, not an estimate.** Read the other way: of the commits that carry any positive
  evidence of who authored them, **38% are attributed to the wrong author.**
- **Strike 2 — the unit changed under me.** `6 → 40` commits/day looks like 6.7×. But lanes
  commit per-ruling and per-record, where I committed per-change. That ratio compares **two
  different populations**, which is the single most common error in this whole project.
- **Strike 3 — there is no counterfactual.** No control arm. So: **no speedup number in this
  talk.** Not because it would be unimpressive — because it would be unfalsifiable, and I'd
  be doing the exact thing the rest of the talk is about.
- What I *can* offer instead: the failure modes, measured, with receipts. That's the rest.

> **Two live examples, collected while making this slide.** I first sized the apparatus
> with `find` and got **494 test files and 82 guard files**; `git ls-files` gives **128 and
> 35** — the walk swept untracked scratch, vendored code and `__pycache__`. Same question,
> right command, wrong population, **3.9× in my favour.** The second is the one for this
> audience: `find` reported **89 findings documents**. There are **23**. The other 66 are the
> *same 22 files*, triplicated across three `.claude/worktrees/` lane checkouts — **so the
> multi-agent setup itself inflates every naive count by the number of active lanes.**

*(2:15. This slide is the credibility purchase. Do not rush it and do not apologise through
it — deliver it as a result.)*

**Transition:** "So here's the catalogue. Specimen one is the one that cost real GPU time."

---

## Slide 4 — "Specimen 1: the check was true, and blind."  ⭐ CORE SLIDE

**Visual:** two parallel tracks — *path checked* vs *module imported* — diverging.

- **The defect (OI-136):** an absolute `sys.path.insert(0, "/pscratch/…/MINERvA-OmniFold")`
  executes **that** tree's modules whichever checkout launched the entrypoint. `PYTHONPATH`
  cannot outrank position 0. Recorded 2026-08-20: **59 of 122 `.py` files** did this.
- **What it cost:** one run executed code **211 commits behind** while the deployment-parity
  check reported **`5 of 5 CURRENT`**. It ran to completion, on GPU, and produced numbers.
  **3 h 08 m of A100** on job `57266000_0`.
- **The parity checker was not broken and it was not uncalled.** It had a caller; all five
  pairs were genuinely current against the frozen tree's own HEAD. **The path checked and
  the module imported are two different facts.** The check answered its question correctly
  and its question was the wrong one.
- **The line that makes this land for an ML audience:** the fail-*closed* version of this
  bug dies at `exit 3` before any GPU work and costs zero GPU-hours. This one **runs to
  completion and publishes.** Same root cause, opposite direction of failure.

> ⚠️ **Do not present 59 as a current number.** As re-measured on this checkout today, the
> live probe exits 0 with both controls holding and reports **9 fail-open of 106** — and the
> residual 9 are precisely the files that are **hash-pinned into receipts**
> (`adopt_unified_5d.py`, four PET files, the published 2D arm, three 2026-08-14 probes).
> They need a re-issued gate, not a refactor. So the honest arc is **59 → 9, converging on
> a set that is irreducible for provenance reasons rather than technical ones.**

*(2:30.)*

**Transition:** "Four more. Same signature every time — a check that reported success
without exercising what it claimed. Different mechanism every time."

---

## Slide 5 — "Four more mechanisms."

**Visual:** four rows, mechanism in bold on the left, receipt on the right. Do not read
them all aloud — put them up, narrate two, let the room read the others.

| mechanism | receipt |
|---|---|
| **The run measured a smaller population than it described.** `unittest.main()` sat at line **853 of 1,325**; three test classes were defined *after* it. `unittest.main()` calls `sys.exit()`, so under direct execution those classes are **never even defined**. | Runner said `Ran 33 tests`. I published **64** — a count of `def test_` lines I never read off the runner. It printed **`OK`** and exited **0**. Survived **three** review rounds, because each round *appended* a class. |
| **The stage validated an artifact the run did not produce.** `build_all.sh` exited 0, printed all three "building" lines, and passed its containment check while `latexmk` said **"Nothing to do"** for every target. | The validated PDFs were dated **2026-08-11 and 08-15**. And the obvious repair — *assert the artifact is newer than its sources* — **held during the failing run**: week-old PDFs are newer than sources nobody touched. It passes *precisely* the run that went wrong. |
| **The test was refused before it reached the thing under test.** To prove a guard had power I mutated it. The launcher's own git-parity preflight found my edited copy and refused. | **Exit 3 — the same code the real refusal returns** — with **zero** violation blocks. Read the exit code alone and you record "power confirmed" from a run that never executed the code under test. |
| **The guard would have fired on every correct run.** Enforcing environment provenance across eight launchers, I asserted `HOME`, all `MNV_*` vars and three search paths must match the submission baseline. **Three of the four were wrong.** | `HOME` is re-exported **on purpose** by six of the eight (`#SBATCH --export=ALL,HOME=…`); activation adds `MNV_*` vars and rewrites the search paths (**47 entries against the submitter's 27**). My assertion would have made **three launchers refuse themselves** on every correct run. |

- **The through-line, said once:** every one of these is a verification step that **reported
  success without doing the work.** Not one is a wrong computation.
- **The second-order cost, on the last row, and it is the worst one:** *a guard that fires
  on every correct run trains its reader to ignore it* — which silently disables it for the
  case it was built for. An over-broad assertion doesn't look like a bug. It looks like
  rigour, it passes review, and it fails **closed**, so it ships feeling safe.

*(3:00. The longest slide. If you are over time, cut row 3, not row 4.)*

**Transition:** "So what does an instrument that survives this actually look like? I have
one, and it was written by the same process that produced the bugs."

---

## Slide 6 — "What a real instrument does. (A worked example, not a rule list.)"

**Visual:** the probe's own docstring, quoted. The artifact argues for itself.

- **It refuses to be a number in a document.** The OI-136 row says, in terms: *"re-run it,
  do not quote the 59 from this row."*
- **It records its own wrong answers.** From the docstring: the first count was *"wrong by
  4× in both directions on the way to the right one, and each wrong version looked
  reasonable"* —
  - `grep -l <root> | xargs grep -l sys.path.insert` → **71**. Too high: the conjunction
    never establishes the insert *uses* the root.
  - assignment-only tracking → **17**. Too low: the two files this is really about bind
    through a **loop**, which no `NAME = …` pattern can see.
  - assignment + loop + derived-name → **59**, both controls holding.
- **It cannot join the population it measures.** The hardcoded path is *assembled from
  parts* on purpose: written whole, the probe *"would match its own discoverer and report
  118 instead of 117."*
- **It has two controls, and a third state.** Positive: known hijackers must be *in* the
  set. Negative: files whose insert is relative to their own location must be *excluded* —
  today it rejects 47. If either control fails the answer is **`exit 2` = CANNOT CHECK**,
  not a smaller number. *"A classifier with no demonstrated discrimination reports success
  on anything."*
- **Its pin is an identity, not a floor.** `test_oi136_failopen_inventory_ratchet.py` pins
  the set to `(9, sha256 0939e159…)`, so **a repair goes red** and must be re-derived and
  named in the same commit. And it asserts non-vacuity *itself* rather than inheriting it
  from the probe's exit code.

> **The failure this design still has, and it is the interesting one.** Its positive
> controls are drawn from the population it measures — so **every successful repair consumes
> a control.** Measured: the second control was chosen 2026-08-22 (`ae42ae8d`) and
> **repaired the next day** (`a0a84a2e`), which makes the probe exit 2 and takes the ratchet
> red with it — *"a repair reading as a broken classifier."* The successor's fix is the
> generalizable lesson: **choose controls from the part of the population that is provably
> immovable.** The surviving control is hash-pinned in four receipts and carries a standing
> ruling *against* repair.

*(3:00. This is the methods contribution. It generalizes to any monitored metric with
controls, which is most of what this room builds.)*

**Transition:** "And I got caught by exactly this, forty minutes ago, preparing this slide."

---

## Slide 7 — "The agent writes the check that passes itself."

**Visual:** three short beats, then the question. Let it be uncomfortable.

- **Beat 1 — I ran a superseded instrument today.** There are two probes on disk,
  `-20260820` and `-20260826`. I ran the older one. It printed the **right count (9)** and
  the **wrong verdict (`exit 2`, CANNOT CHECK)**, because its control had been repaired.
  Reading the number alone: right by luck. Reading the exit code alone: "cannot check" when
  the answer is 9. **Neither reading was sound, and one of them was correct.**
- **Beat 2 — the guard has a hole exactly where it is needed.** `mnv_guarded_run.py` wraps
  the stdlib `PathFinder` in **its own interpreter's** `sys.meta_path`. In-process it exits
  3 and names the victim module. **Through a subprocess it exits 0** and the child loads the
  other tree's module — and the production launcher runs its pinned writer as a subprocess
  *deliberately*, so that the pinned bytes are the executed bytes. **Routing that launcher
  through the guard today would print a clean banner and refuse nothing.**
- **Beat 3 — the measured population is a function of what the agent writes.** During the
  one authorized repair, the fix deliberately **did not** spell the hardcoded path in a
  comment, because doing so would re-match the probe's own regex and keep the file counted —
  *"gaming the population it measures."* That was the right call. It is also proof that the
  quantity and the agent are not independent.

> **The question, and I don't have an answer:**
> **When the same process writes the analysis, the check, and the check's controls — what is
> the independent verification?** Every instrument on the last slide was built by the thing
> it polices. The best I have is that its controls are pinned to artifacts a ruling forbids
> anyone from moving. That is governance, not measurement.

*(2:15.)*

**Transition:** "Which leaves two asks, and the first one is specifically for this room."

---

## Slide 8 — "Two asks."

**Ask 1 — for OmniFold specifically. This room can actually answer it.**

> Should these become standard OmniFold validation?
> 1. **Target attainment.** Step 1's loader normalization implies a closed-form target its
>    fitted classifier must hit: averaging the implied likelihood ratio over the MC leg,
>    under the training weights, returns the ratio of the two class totals — here
>    `R = 1.124`. **We reach 58.6% of it** on the one default-schedule trajectory we can
>    measure cleanly, and **87.8–93.5%** across five annealed replicates.
> 2. **Checkpoint identity.** Does reloaded inference reproduce the weights the run
>    recorded? Slide 1 is what it costs when nobody asks.
> 3. **Fixed-input refits.** What is your reproducibility floor at identical data and a
>    pinned seed? Ours: across-refit relative sd **2.05%** on the truth leg — identical
>    2,000,000-row subsample, pinned seed, **no Poisson draw**. Not a statistical
>    uncertainty. A floor on how well the analysis reproduces its own answer.
>
> All three are cheap. The third costs N identical re-runs, which every compute budget
> treats as waste.

**Ask 2 — the question:**

> **What is the minimum verification standard for an agent-driven analysis — and what
> catches a check that passes itself?**

*(1:30, then stop talking. Two questions. If it's quiet, push check 3 — it needs zero
neutrino context and everyone in that room has hit it.)*

---

## KNOWN WEAKNESSES — have the answer ready

1. **"You're describing normal software bugs."** The strongest objection. Answer: three of
   the five specimens are *specific to the mode* — a check whose author, subject and
   controls are one process. Beat 3 on slide 7 is the sharp end. Do not over-claim the other
   two; a human could have written them, and the honest claim is **volume and the absence of
   a second pair of eyes**, not novelty of the bug.
2. **The 86.6% is a step-2 number.** See the slide-1 warning. Most likely *factual* error
   from the podium.
3. **The repo contains a different attainment number.** Six `p3f-pet-gate4-launch-code-gate-*.json`
   records (2026-08-07 → 08-13) say **68.1%** from `pull_final = 0.765031`. That artifact is
   **superseded**; the finding's §7 re-measures on bit-faithful checkpoints at `0.658944` →
   **58.6%**. Be ready to say *why the other number exists* rather than looking surprised.
4. **The refit floor's provenance is asymmetric.** Of the five draws behind the 2.05%, draw
   1 comes from a different directory (`fullevent_ml_ensemble/member_1`, job `56847059_1`)
   than draws 2–5, and four of the five record **no target digest**. The defence is
   quantitative — `VL131` slot agreement to `< 5 × 10⁻⁷` on every draw in order — but it has
   to be *offered*. **If you are short on time, drop the 2.05% to "we measured it, ask me"**
   rather than quote it and owe the caveat.
5. **Slide 3's authorship numbers are a LOWER BOUND, and say so if pressed.** `98 of 258`
   and `38%` were re-derived on this checkout 2026-09-08 (script in `Practical`), with a
   positive control that the parse sees trailers at all. What they do **not** support is any
   claim about the 2,581 commits carrying no trailer — that population is simply unmeasured,
   and the true misattribution count is almost certainly higher. Do not let "38%" be heard
   as "38% of the repo."
6. **Slide 2b's classifier is a path regex, and it errs in both directions.** A guard
   living inside a larger module is missed (undercount); a `test_`-named file that is really
   a driver is miscounted (overcount). The verification-share curve is a proxy, and the
   2026-06 dip to 1.2% breaks monotonicity — **do not call the curve monotone.** September is
   8 days. Also note the denominator is code only: `.md` governance work, which is most of
   the apparatus, is excluded entirely, so 61.8% is not "62% of the project."
7. **One project, one operator, one toolchain.** Nothing about agent-driven analysis in
   general is earned. Say so before someone says it for you.
8. **PET is diagnostic / method-development** and off the publication critical path
   (`OI-126`) — in the talk exactly as in the note.

---

## GUARDRAILS — live constraints, not style

- Never call `C_stat` "verified", "adopted", or "the statistical uncertainty." It is not in
  this deck; keep it out of Q&A.
- **Never name a cause for the re-fit spread.** Measured that it happens; unestablished why.
- **Never present non-convergence as established.** It is the leading candidate in the
  repo's own words. Slide 8 states attainment as a *measurement*, which is safe.
- Never cite "bootstrap-centering" as a settled mechanism.
- Show **no** 3D or N-D covariance band, and no σ or χ² derived from one. Rules out the July
  deck's `+3.9σ` / `+2.3σ` and the grey bands in `generators_vs_unfolded_band.png` and
  `compare_mec_eavail.png`.
- Covariance gets **at most one spoken sentence** if asked. Not a slide.

---

## Practical

- **Numbers re-measured on this checkout 2026-09-08.** Commit census, lane dates, tracked
  vs `find` counts, OI-136 live probe (`exit 0`, 9 of 106, both controls held) and the
  ratchet (7 passed). Re-run before the talk if anything lands on `main`:
  ```
  git log --format=%as | cut -d- -f1,2 | sort | uniq -c
  git ls-files | grep -c "test_.*\.py$"
  python3 docs/orchestration/state/probe-oi136-sys-path-hijack-20260826.py ; echo "EXIT=$?"
  python3 -m pytest nd-unfolding/tests/test_oi136_failopen_inventory_ratchet.py -q
  ```
  **Read the probe's exit code without a pipe** — a pipe rewrites `$?` and this deck's whole
  slide 7 is about that class of error.
- Slide 3's authorship floor re-derives with the script in this folder:
  ```
  python3 docs/sep-09-presentation/check_authorship_floor.py
  ```
  Expect `trailer=258  under-my-name=98`. It exits 2 on an empty git result, because a
  tally of zero may mean it could not look.
- Sourced at file:line, 2026-09-08 — quote these rather than the deck:
  `0.658944` and "58.6% of its own objective" at
  `docs/orchestration/FINDING-20260807-step1-under-achieves.md:137,141,143`;
  `R = 1.124080` at `:143`; the superseded `0.765031` at `:19,45`.
  `8.663e-01` as Gate **B(i)** *"checkpoint-rebuilt push vs stored, on `pass_gen`"* at
  `docs/orchestration/FINDING-20260807-checkpoint-is-not-the-trained-model.md:32`, the
  aggregate agreement to `1.0e-4` at `:52`. Note `:52` says "up to 87%" in prose while the
  receipt is `8.663e-01`; **quote 86.6% and cite the receipt line.**
- Figure: `verification_apparatus.png` from `make_apparatus_figure.py` (see that script's
  self-check).
- Slide 2b re-derives in full with `python3 docs/sep-09-presentation/measure_workflow_quantities.py`.
  It exits 2 rather than printing a zero if a sweep finds no usage records or git returns
  nothing, because a tally of zero may mean it could not look. **Token totals are a LOWER
  BOUND:** the sweep covers the three Claude transcript roots and skips `~/.codex` and
  `~/.codex-claude-bridge`, which use a different schema.
- Carried from `DECK.md` and still usable as backup: `step1_attainment.png` (slide 8 check 1),
  `loop_trajectories.png` (slide 8 check 3, **with** weakness 4's caveat).
- Sources: `docs/OPEN_ITEMS.md` (OI-136, OI-126),
  `docs/orchestration/state/probe-oi136-sys-path-hijack-20260826.py`,
  `nd-unfolding/tests/test_oi136_failopen_inventory_ratchet.py`,
  `docs/orchestration/FINDING-20260807-checkpoint-is-not-the-trained-model.md`,
  `docs/orchestration/FINDING-20260807-step1-under-achieves.md` (§5, §7), `VALIDATION_LEDGER.md`
  (VL94–VL97, VL100–VL101, VL130–VL132).

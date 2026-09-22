# HANDOFF 2026-09-21 — everything that remains on the GBDT / scalar-5D publication path

**CITABLE FOR:** the remaining-work list and the measurements in it.
**NOT CITABLE FOR:** any grade, adoption or authorization. **PET is deliberately out of scope**, on
Joseph's instruction of 2026-09-21: *"I don't want to focus on it and just want to focus on
finishing GBDT."* Items that are PET's are named as such and excluded, not silently dropped.

Written to be read cold. Every number is measured, with the command or artifact beside it.

---

## 1. Where GBDT stands

**The deliverable set is complete and pushed.** An adopted scalar-5D covariance
(`3d7465f6…`, `variant cv`, 890,500,272 B), its verified `(E_avail,W)` projection
(`835828bf…`, 42 cells) paired to the note figure **by digest**, and note/primer/paper built and
synchronized to both repositories. `REPORT-20260920-scalar5d-uncertainty-completion.md` is the §7
completion report.

**What is left is not construction.** It is four decisions, one reserved act, and some hygiene.
Nothing below needs a new campaign, and `DECISION-20260919` §7's stopping rule forbids one for the
accepted provenance gap, repeated summaries, or absent optional studies.

---

## 2. THE LIVE LIMITATIONS — seven at the completion report, now six

`L7` closed on 2026-09-21; see §3. The remaining six, in the order they matter:

### L1 — `s_proj = 6.145%` against a `5%` bound. **This is the one that decides the paper's claim.**

`(cause 3, Z)`'s `M(ii)`, branch 5, **NOT MET — PER-BIN**, on a fully valid campaign. It is **flat
in `N`** — `6.04% ± 0.39%` at `N = 40/80/160`, exponent `0.000`, against a resampling floor falling
`20.91% → 7.57%` at exponent `1.467` — so it is a property of the estimator and **a larger ensemble
would not reduce it**.

**It is why no generator significance is quoted, and that is already in the abstract.** No action is
pending unless you want to revisit the `5%` bound, which was fixed before production and cannot be
re-chosen from an observed value without violating §6.4's own discipline.

### L2 — the five seed-pinned bands. ⚠ **AUTHORIZED 2026-09-21, CHANGE LANDED, PROBE RUNNING.**

> ## ⚠ STATUS UPDATE 2026-09-21 — supersedes the reservation language below
>
> **Joseph authorized the reserved act by name:** *"yes do the L2 probe, i authorize the estimator
> change."* The text from here to the end of this subsection is kept because it states the
> reservation that was in force and the reasoning that held the lane back; it is **history, not
> current state**.
>
> **THE CHANGE WAS EIGHT SITES, NOT THE TWO THE EVIDENCE NAMED OR THE THREE I FIRST FOUND.**
> Landed at `e2632ac7` (sites 4-8) on top of `47dfd345` (sites 1-3), predeclared with two
> amendments at
> [`PREDECLARATION-20260921-L2-lateral-seed-release.md`](PREDECLARATION-20260921-L2-lateral-seed-release.md).
> A grep for `--seed 42` finds ONE of them; the literal is load-bearing in six more places under
> five spellings — a default argument, a dict constant, a `require`, a config-hash input, an
> independent re-derivation of that hash, and a reproducibility reference.
>
> Four of the eight are **provenance gates**, and the pairing of two of them is the dangerous
> part: the driver would have stamped `config_hash(seed=42)` onto a ROOT produced at 1242, and
> `p4_check_receipt` would have re-derived **the same wrong hash from the same default** — so the
> receipt would have passed its own verification. Producer and checker agreeing is evidence only
> when they do not both read a default instead of the run. Every gate is now **derived**
> (`42 + declared offset`), never relaxed: at offset 0 each evaluates to exactly today's literal,
> confirmed by measurement on the cluster — baseline config hash `4b41fab90a83df08`, identical to
> the adopted receipt's.
>
> ### ⚠⚠ AND THE PROBE UNCOVERED A LIVE HAZARD THAT HAS NOTHING TO DO WITH L2
>
> **All ten receipts backing the adopted covariance `3d7465f6…` are STALE on the deployed
> checkout.** Measured read-only, 10/10:
>
>     RECEIPT-REJECT :: receipt BeamAngleX_0 unfold_blob dc74c38f… != committed 662951e0…:
>                       the unfold driver changed since this endpoint was produced
>
> `unfold_nd_omnifold_unbinned.py` changed after 2026-08-08 (`5afb7947`, `ae42ae8d`, `0a4ab263`,
> `1aa055d9`) and `validate_endpoint_receipt` compares that blob strictly — correctly; it is the
> producing-code binding. The consequence: **the documented baseline command
> `bash run_p4_unfold_std.sh` re-unfolds and `mv -f`s over the adopted covariance's own inputs,
> exit 0, no warning.** This is true with or without the L2 change and was true before it.
>
> It surfaced only because the probe forced *"what does the resume gate actually decide for these
> ten?"* to be **measured** instead of assumed — and the assumption was load-bearing: my own
> predeclared safety control was to run that exact command. **The control would have destroyed
> what it was written to protect.**
>
> **Remedy landed:** a baseline-overwrite guard in `run_p4_unfold_std.sh`, refusing (`rc 9`) when
> the ROOT exists, the namespace is not member-scoped, and `P4_ALLOW_BASELINE_REUNFOLD=1` is
> absent. Its first version sat *after* `rm -f "${REC}"` and would have deleted all ten receipts
> before refusing — caught by **testing** it, not reading it.
> `tests/test_baseline_overwrite_guard.py` asserts that ordering against the launcher's own
> extracted text, in four directions, plus near-miss escape values.
>
> ⚠ **This is an open item for whoever owns the adopted product**, not something the L2 probe
> closes. The guard prevents accidental destruction; it does not re-establish the ten receipts'
> validity, and a deliberate baseline re-unfold would still need the manifest, components and
> covariance re-derived.
>
> ### Cost, corrected
>
> **The probe is CPU work, not GPU.** The cost table below says *"10 endpoint unfolds, 1 GPU +
> 32 CPU → 15 GPU task-h"*; the historical holder `56495756` was **256 CPU, no GPU, 3 h, one
> node**. Corrected figure: **~3 node-hours on one CPU node.** CPU is the tighter allocation
> (project `m3246` at 16,529 / 20,000) but 3 node-hours is negligible against it.
>
> ### Running
>
> Deployed to a **detached worktree** at `e2632ac7`, with the deployed checkout's HEAD verified
> unmoved before and after — PET's array `58692544` is live from it and a HEAD move would kill the
> pending elements. Job **`58724712`**, member `k=1200`, seed **1242**, member-scoped output,
> member config hash `4809b4ad…`. Baseline population asserted **20/20 before the run** so the
> byte-identity check cannot pass vacuously.
>
> ⚠ **The outcome map was fixed before the run and is not reopened by any result:** `> 5%`
> confirms `L1`'s FAIL with the five varying; `< 5%` **licenses nothing** — one seed pair cannot
> show a maximum over the declared set is below a bound; "cannot be computed" is an inability, not
> a result. Nothing here moves the adopted digest, regrades cause 3, or licenses a significance.
>
> ### ⚠ A design correction, made before it cost anything
>
> The member is **`member_k001200` rebuilt with its own lateral block**, reusing that member's own
> `stat`/`ml`/`support`/`throw` — *not* the archive's, which is what my first stage script used.
> The graded campaign's two members already differ in those four legs and **share `active`**: both
> z-manifests name the same candidate, sha256 `950f8cb15c5a0bd7…`. **That shared row is L2,
> readable straight out of the campaign's own records.** Building against the archive would have
> varied four extra legs and measured a different question.

---

#### (Historical — the reservation as it stood before the authorization)

### L2 — the five seed-pinned bands. ⚠ **COMPUTE IS AVAILABLE; THE ACT IS RESERVED.**

The five lateral bands — `BeamAngleX/Y`, `MuonResolution`, `Muon_Energy_MINERvA/MINOS` — carry
**26.0% of `√Tr C_Z`** and are produced at a literal `--seed 42` the offset hook cannot reach
(`MNV_EST_SEED_OFFSET`: **0** occurrences across all six files of that chain). Since the
2026-09-20 withdrawal of the *"lower bound"* inference, **the direction of their contribution is
unknown**, and the open question is whether the `L1` FAIL survives releasing them.

⚠ **This is the one place where Joseph's "use as much compute as you want" does NOT unblock the
work, and the distinction is exact.** Probing them requires unpinning `--seed 42` in
`run_p4_unfold_std.sh` and un-hardcoding `p4_build_components.py`'s `UDIR` — and
`EVIDENCE-20260919-lateral-bands-are-seed-pinned.md` §5 rules that:

> **Putting the five on the hook is a MATERIAL CHANGE TO THE ESTIMATOR and is RESERVED.** … It is
> not this lane's act, it is not attempted, and it is routed to Joseph.

`OPERATIVE-SHEET` §6 reserves *"any material change to the estimator … not to be routed around."*
**A compute grant is a permission about resources; this is a permission about the estimator.** They
are different, and this lane will not treat one as the other.

**What it would need, so the decision is costed rather than open-ended:** an explicit ruling naming
the change; both files changed together (the evidence says so — `UDIR` is hardcoded, so there is no
member-local `active` even if the seed were unpinned); and it changes what the MAT ± endpoint
difference measures, which is a scientific consequence, not a plumbing one.

**WHAT IT WOULD COST — ~15 GPU task-hours, and the compute is the cheap part.**

⚠ **The event loops do NOT re-run, and that is the whole cost story.** `run_p4_unfold_std.sh:110`
takes `--omnifile "${MERGED}"` — an already-produced merged endpoint ROOT — and only the *unfold*
carries `--seed 42`. The shifted-kinematics event loops, which are the expensive stage (ten
directories at ~53.8 GB each), are **estimator-seed-independent and are reused**. A reading that
re-ran them would cost orders more and would be wrong.

| stage | cost | provenance |
|---|---|---|
| 10 endpoint unfolds (5 bands × 2) | **15 GPU task-h** | `COSTMODEL-20260911`'s comparable 5D re-unfold, 1.5 h on 1 GPU + 32 CPU, × 10 |
| `p4_build_components` + merge audit | < 0.5 CPU task-h | CPU-minutes |
| one Z assembly | **0.29 task-h** | *measured* — job `58454524`, `ElapsedRaw 1037 s`, MaxRSS 49.73 GiB |
| one grade / projection | < 0.25 task-h | *measured* — job `58655509`, 39 s |
| **total** | **~15 GPU + ~1 CPU task-h** | **≈ 3% of one arm's 500 task-h ceiling** |

*The 15 is the **reserved** figure and a reservation is the enforced cap, so it is the number to
declare.* The original ten completed inside a **4,651 s** window with concurrency, and the largest
consecutive gap was **2,290 s**, so the actual spend is likely **well under** the reservation.

> ### ⚠ AND THE PROBE IS ASYMMETRIC — IT CAN CONFIRM THE FAIL BUT CANNOT CLEAR IT
>
> This is the part that should decide whether it is worth doing, and it is not a cost argument.
>
> `s_proj` is a **maximum over the declared offset set**. Releasing the five bands and re-running
> gives a maximum over **one seed pair**, exactly as the current grade does. So:
>
> - **if it still exceeds 5%** — the `L1` FAIL is confirmed with the five released, the `L2`
>   direction becomes known, and the result is **strong**, because more pairs can only raise a
>   maximum;
> - **if it falls below 5%** — nothing is cleared. One pair cannot establish that the maximum over
>   the set is below the bound, and the grade's own discipline is over the declared set.
>
> **So the probe buys a confirmation or an ambiguity, never a pass.** That is still worth 15 GPU
> task-hours — an unknown direction on 26% of `√Tr C_Z` is a weak thing to publish beside a FAIL —
> but it should be commissioned knowing which of the two answers it can give.

> ### ⚠ AND A PRECONDITION THAT IS NOT ABOUT THE ESTIMATOR: NOTHING WOULD SUPERVISE THE RUN
>
> Measured on the cluster **2026-09-21**, immediately before writing this:
>
>     scrontab -l                 ->  "no crontab for josephrb"
>     squeue -u josephrb --qos=cron  ->  0 jobs
>     last wakerctl tick          ->  2026-09-09T14:35:16Z, 296.5 h old
>
> **The supervision net has been down since 2026-09-09.** If `L2` is authorized, its run would
> finish, fail or hang with **nothing to wake anyone** — and an `L2` probe is a multi-band re-unfold,
> not a two-minute job. This is not a reason to decline `L2`; it is a thing to fix **before** it,
> and it is cheap. Recorded here rather than only in the PET context where it was found, because
> a down waker is not PET's property — it is every lane's, and GBDT is the lane about to use it.

### L3 — cause 3 is predeclared and NOT computed for this digest

`M(i)` `UNRESOLVED` on `4c`, permanently, for a predeclaration failure. **And no declared boundary
was evaluated in production** — all seven measure `read_by_production: no`, re-verified 2026-09-21
with `boundary_readership.py`. The note's required wording is fixed at `OPERATIVE-SHEET` §4b and is
in place. **No action; this is a disclosure, not a gap to close.**

### L4 — PM-1's historical-input provenance limitation

Accepted by Joseph's 2026-09-19 decision. The file-level link between the tuple whose branches were
measured and the tuple `combined_source` was built from **cannot be made from the record**, and the
ruling forbids manufacturing it. **No action.**

### L5 — hadronic-response completeness. ⚠ **ONE ITEM AWAITS A HUMAN, NOT COMPUTE.**

The disclosure is in note, primer and paper as of 2026-09-21. What remains is the **collaborator
question** the ruling also requires: `QUESTION-20260921-hadronic-response-coverage-for-eavail-w.md`
is **prepared and NOT sent** — sending is outward-facing and needs Joseph's own word.

Its limits are already written: **silence reopens nothing**, generic precedent is not proof for this
measurement, and a concrete omission must return with its affected observable and a proposed remedy.

### L6 — clause (c) was satisfied in substance and violated in ORDER

Ratified retrospectively on 2026-09-20, **expressly not cured**. The independent verification
followed the adoption. **No action is possible** — the sequence cannot be manufactured — and the
ratification is recorded.

---

## 3. ✅ CLOSED SINCE THE COMPLETION REPORT

**`L7` — `V6`'s six items now have a second-lane reproduction.**
[`VERIFICATION-20260921-v6-six-items-reproduced.md`](VERIFICATION-20260921-v6-six-items-reproduced.md).
All six reproduced from artifacts and committed operands:

| item | result |
|---|---|
| C4 jitter floor, job `58547629` | **exact** — `3.730946e-78`, `sqrt 1.931566e-39`, PRINT-ONLY, condition-3 guard PASSED, `10694 of 65856` |
| C2 F7 margin | **exact** — `shift/(k·floor) = 2.673896`; the `29.85` failing multiplier exact; *"clears by 2.29×"* = `2.673896/1.168` |
| NULL `r_null` | **reproduced** — `4.431129925843213e-14` vs historical `4.4520002137582904e-14`, difference **0.469%** ≈ the quoted `0.5%` |
| the seven boundaries | **reproduced**, `no` for all seven |
| historical `--run-class` absence | **confirmed** — 0 at `5be86f55^`, 2 at `5be86f55` |
| job `58549890`'s arms | **reproduced** — `rc=3`×2 genuine, `rc=139`×4 segfaults, `CONTROL FAILED` |

**Two corrections fell out, and both are live:**

1. **`V6` item 4's `assess()` sub-claim is no longer true.** `z_validator.assess` now has production
   callers — `z_build.py:762` and `z_grade.py:616`. True on 09-18, overtaken on 09-19. Do not quote
   it as current state.
2. **`s_proj` is at `z_statistics.py:319`, not `:203`.** Re-pinned in the three live documents to
   the symbol plus a sha; the two dated 09-18 records keep `:203` as written, because they are
   records.

---

## 4. HYGIENE — real, bounded, and none of it blocks publication

### 4a. ⚠ A REGRESSION I INTRODUCED AND DID NOT NOTICE

**Live `pipeline-rc` instances went 3 → 7**, measured with `tools_p4_sweep_pipeline_rc.py` at
`c34553e5` and at today's tip. **Four arrived with my 2026-09-21 Z-assembly-pilot merge** —
`submit_z_pilot_a5.sh:56,57,396` and `tests/test_submit_path_sanitizer.sh:62`.

**How it got past me:** I verified that the P4 failure **set** was identical at both commits, and
concluded "pre-existing". The set *was* identical. The **magnitude** was not, and I did not compare
it. A test that was already red hid the fact that I made it redder.

⚠ **All four are VERIFIED BENIGN, and the code should NOT be changed.** Each is an
**output-capture** shape, not a status-read: `mnv_sha256()` uses the piped value, and two carry an
explicit `|| true` with a comment saying an empty grep is the expected outcome. The sweep's own
note says *"verify before editing."* Verified.

**So the repair is to the pin or the matcher, not the scripts** — and it is the P4 owner's:
re-base the snapshot with this justification recorded, **or** narrow the matcher to status-read
shapes so output-capture stops registering. Do not `--update` without recording which of the four
it is accepting and why.

### 4b. The other five P4 failures, all pre-existing

`353 != 374` shell-file count, `132 != 129` recorded-but-unchecked fields, `19 != 18` repair-8, a
mutation test and a launcher-path test. **All are snapshot drift over a corpus that grew**, all
reproduce identically at `c34553e5`. Their own messages say `--update and commit`. ⚠ **Each update
should be reviewed for what drifted**, for exactly the reason 4a exists.

### 4c. Two standing test failures that are NOT GBDT

`test_mnv_guarded_run.py`'s two multiprocessing tests. Identical at `c34553e5`. **Worth one
measurement before any repair:** run them on Perlmutter. If they pass there they are a macOS
artifact and should skip with a reason rather than be carried as failures.

### 4d. The router's phase 2

`CATALOG.md` is ~3,812 lines after phase 1. The ~2,090-line scalar-5D section is now more than half
of it and its records stopped moving on 2026-09-20 — **splitting it now would split it twice**.
`ROUND 11` (~619 lines) needs one thing first: its own title records `F-8(a)` and `F-17(a)` as
*"filed and awaiting grade"*, and **nobody has verified that resolved**. One afternoon.

### 4f. ⚠ The supervision net is down, and it is the one item with a LIVE cost

Repeated from `L2` because it is not only `L2`'s problem. `scrontab -l` returns *"no crontab for
josephrb"*, there are **0** cron jobs, and the last tick is **2026-09-09T14:35:16Z — 296.5 h old**,
all measured 2026-09-21.

**Nothing will wake anyone when any job ends**, on any lane. It was found while looking at PET's
queue and is recorded here because the fix is shared infrastructure and GBDT is the lane most
likely to need it next. ⚠ **Not fixed by this lane:** reinstalling a managed `scrontab` block is a
change to shared scheduling, and it is PET's tree that holds the waker state dir.

### 4e. The 12 unexplained launchers

`test_uq_remediation.py`'s fence total is pinned as `216 reviewed + 12 measured-and-unexplained`.
**Pinning is not explaining**; the 12 are a branch-versus-main corpus gap nobody has accounted for.
The pin stops them masking the rest of that file and does nothing else.

---

## 5. WHAT IS DONE AND MUST NOT BE REDONE

- The 2D, 3D, 4D and 5D central values, anchors and closures.
- The adoption, the projection, and the pairing — established **by digest**, not by agreement.
- Causes 1, 2, 4, 5, 6, 7 and R5; the §6.4 null route; clause (c)'s disposition.
- The third-lane C5/C7 verification, and now `V6`'s six.
- The note's four travelling measurements, the hadronic-response disclosure, and the withdrawal of
  the *"lower bound"* inference at all eight sites.

---

## 6. THE SHORT VERSION

**Nothing on the GBDT path is blocked on compute.** One item (`L2`) is blocked on a **reserved
estimator change**, one (`L5`) on **sending a question to a person**, and the rest are either
closed, disclosures that cannot be closed, or hygiene that does not gate publication.

**The next decisions are Joseph's:** whether to authorize the `L2` estimator change, and whether to
send the collaborator question.

⚠ **One thing to fix BEFORE `L2`, if it is authorized:** the supervision net has been down since
2026-09-09 (§4f), so the run would go unwatched.

**Co-Authored-By: Claude Opus 5 (1M context)**

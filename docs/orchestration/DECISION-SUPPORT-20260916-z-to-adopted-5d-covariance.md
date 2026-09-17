# DECISION SUPPORT 2026-09-16 — from Z's outputs to an adopted 5D covariance

## CITABLE FOR / NOT CITABLE FOR — read before quoting anything below

**CITABLE FOR:** the state of each remaining requirement as measured on 2026-09-16, **as amended by
§10's 2026-09-17 reconciliation** where the two disagree; the routing of each; the reconciliation
in §3; the resource figures in §4 and §5 **as corrected in §10.5**; and **§12 AS CORRECTED BY §13**,
as a *recommendation*. **Read §13 before acting on any part of §12** — it carries the independent
assessment (`ed18a231de4c3b6b016e268be54257579b6c7739`), withdraws §12.4 consequence 2, moves the
`B` fallback from BARRED to **UNRULED**, corrects §12.6's stated authority, and **relocates the
blocking decision from the active-set population to `θ`.** §12.7's decision table is superseded by
§13.7.

> ⚠ **§11 IS SUPERSEDED BY §12 (2026-09-17) AND IS NOT CITABLE.** It asked for two declarations that
> already existed at `78a8c2ee42c71db1e300e4cfe3735554101bf8ce`, rested on the "`S` is non-binding"
> and "route (iii) exhausted" premises that §12.2 **withdraws**, attached `ε` to the per-bin
> diagnostic instead of to `r_null`, and priced off historical elapsed times. **Full `S` is OPEN.**
> Where §2.1, §2.4 or §10 rely on unqualified non-bindingness, read §12.2 first.

**NOT CITABLE FOR:** any scientific grade. Any acceptance boundary. Any adoption. The authorization
that admitted this record states explicitly that it **does not ratify the proposed scientific
criteria** recorded here. `ε = 1e-9` is **PROPOSED and UNGRADED**; `S`'s discharge is
**F7-channel only**; **A1 is OPEN**. Gate 2 remains **FAIL**. `cause3_corr` remains **WITHHELD**.
Endpoint B remains **DEFERRED NOT PASSED**.

> ⚠ **CORRECTED 2026-09-17 — ONE SENTENCE OF THE BLOCK ABOVE WAS FALSIFIED BY EXECUTION, AND IT IS
> STRUCK RATHER THAN REWRITTEN.** This block read *"Any claim that a Z covariance exists —* ***none
> has ever been constructed.***" **Two now exist.** Job `58454524` (2026-09-17T00:21:56–00:39:13,
> `nid004093`, `ExitCode 2:0`, `ElapsedRaw 1037 s`) built both centering variants from the real
> bound inputs and closed every structural gate. Route: `ND_OMNIFOLD_RUN_LOG.md` § 2026-09-17.
>
> **Nothing else in the block changes, and the correction cuts the other way for most of it.**
> Construction discharges no scientific criterion: `scientific_acceptance` is **NON-PASSING**,
> `adoptable` is **false**, `outcome.assessable` is **false** on reject condition `4c`, and the
> null's own verdict is **NOT ASSESSABLE**. `B`, `S` and `ε` are exactly as open as before the job
> ran. **What changed is that existence is no longer the open question — and §10 records that this
> removes an argument this record leaned on rather than supplying one.**

**This is decision support, not a decision.** It proposes; the owner rules.

Measured at `12250ba2436300b8598dc42b59acabc6ad50543f` unless another sha is named. Every code
claim carries `file:line` **and** a sha; none cites "main".

---

## 0. The finding that reorders everything else

**No subset of the per-cause work makes a 5D covariance adoptable.** `SPEC` §3.5
(`SPEC-20260906-complete-scalar5d-successor-Z.md:1346-1358`), verified verbatim: a Z with all seven
cells complete and favourable **"would establish exactly one thing... Nothing else"** — it does not
move Gate 2, does not move CAND `1 of 7` / QUOTED `0 of 7`, does not adopt Z, and does not license
a projection. It adds that **"adoption is a separate decision and is Joseph's."**

Gate 2 stays FAIL on six independently sufficient NOT-DISCHARGED clauses
(`DECISION-20260825-joseph-gate2-fail-and-four-rulings.md:48-51`), and
`DECISION-20260830-joseph-mii-family-and-leg6.md:53-55` records that **"no authorization from
Joseph removes it — only the rehearsal work landing does."**

So the cause cells are **necessary and not sufficient**, and the shortest route to an adopted
covariance does not run through finishing them first.

---

## 1. The cell population is 26, not 28

`Z_BUILD_PACKET.md:231-232` asserts "That is 28 `(cause × leg)` cells" — a bare 7 × 4 from
`SPEC:1229` ("each carries four legs"). Two specific rulings in the same specification override
that general sentence:

| ruling | effect |
|---|---:|
| `SPEC:3484-3492` rules `(cause 5, Z)` terminally disposable as **one** item, "recorded as **distinct from a mechanical four-MET discharge**" | **−3** |
| `SPEC:966-972` lists cause 3's `M(i)` (fixed-seed null) and `M(ii)` (joint-baseline composite) as separately gradable obligations; `:1225` grades `M(i)` alone | **+1** |

7 × 4 − 3 + 1 = **26**. `SPEC:1229` and `SPEC:966-972` cannot both be right; the specific rulings
should win and the general sentence should be corrected. The same arithmetic error is already on
the record for the predecessor artifact —
`CENSUS-20260902-permanence-language-in-leg-grade-cells.md:28,33` measures 23 rows, not 28.

**Status of all 26: zero RESOLVED, zero SUPERSEDED, evidence `none`.** `Z_BUILD.md:130` — "All
seven causes remain UNRESOLVED"; `SPEC:805-816` — Z's output paths, receipt schema, producing
revision, validator and test fixtures do not exist, and "the six non-cause-7 causes have no Z-side
validator at all".

**No cell is OPTIONAL-ROBUSTNESS and none is droppable.** `CRITERIA-20260811-...:44` leaves a cause
OPEN on any single failing leg, and `SPEC:1240,1290` refuse to make a large `M` a reject condition,
so no leg can be waived for smallness. The two items that look optional are already labelled
DIAGNOSTIC rather than legs (`SPEC:2112`) and are not in this population. `(cause 5, Z)` looks free
(a static trace, zero compute) but `SPEC:3495-3500` records that an `N/A` outside the three tokens
"can never discharge".

**Two population-level blockers sit above every cell:** no grading lane that `BEN-381` does not
disqualify (`CRITERIA:283` — "the lane that measured a leg must not grade it"; `SPEC:2538`
disqualifies the drafting lane), and the withheld-boundary owner question in §2.

---

## 2. A1 (`null_epsilon`) — **OPEN**

`SPEC:1728-1733`, restated at `z_contract.py:259-261` and `z_validator.py:291-292`:
`B` = an operating-error bound on this algorithm in this execution envelope; `S` = an
independently justified scientific cap; require `B ≤ S`; `ε` argued **within** `[B, S]`.
`z_contract.py:261` ends: **"Neither B nor S is established."**

### 2.1 `S` — discharged by bounding, **FOR THE F7 CHANNEL ONLY**

⚠ **The qualification is part of the status, not a caveat on it.** `uq_math.f7_cv_centered_required`
decides whether the CV-centered variant is additionally mandatory; its operand is `‖mean_shift‖`,
and `hJointMeanShift` is "joint throw mean minus CV", so a CV perturbation `dx` moves the mean
shift by exactly `−dx` and `|‖ms'‖ − ‖ms‖| ≤ ‖dx‖` by the triangle inequality — a **proven bound**,
and **normalizer-free**, because both quantities are norms of vectors in the same space. Measured
(`k = F7_FLOOR_MULTIPLE = 2.0`, strict `>`, `N = 160`, `‖ms‖ = 1.878696733368378e-38`): the `‖dx‖`
that flips the branch is `1.045496e-38` / `1.189670e-38`, i.e. `1.7957e11` / `2.0433e11` × G's
null. That is `SPEC:1894` route (iii), verified verbatim — "**zero compute.** It is an argument."

**What is NOT covered, and it is not a small remainder.** A CV perturbation also enters
`C_unified` through the **throw deviations** and the **completeness division**
(`unified_throw_cov_5d.py:66-80`). No mechanism is asserted for those channels — asserting one
without a command run against it is this campaign's catalogued failure. **§7 item 4** names the
measurement: "arithmetic + one code read". **`S` is discharged for one channel of at least three.**

**`S` requires no CV norm at all** — normalizer-freeness is why. `PM-6` is therefore **not** in
`S`'s chain; an earlier reading of this lane's that placed it there is withdrawn. `PM-6`, and §7
**item 17**'s binding of G's production-CV input, route to **`PM-4`**, which `SPEC:304` records as
having "no referent" because G's committed key inventory is 13 keys containing neither
`hRowIndex5D` nor `hXSecND_flat` (measured directly from
`uq_5d/receipt_candidate_stamps_5d.json`).

**And the consequence runs against convenience.** `SPEC` §3.7a rev. 19 permits `ε = S`, the loosest
scientifically acceptable value. For this criterion that choice would be a **defect**: an `ε` near
`1.8e11` × the observed null is a gate essentially nothing can violate — which is exactly the
`1e-12`-clamp defect §3.1a measures and §6.4 exists to repair. The null is a **determinism and
provenance tripwire**, and one chosen from the scientific-tolerance side cannot fire. **So `S` is
not the binding consideration and `ε` must be argued from `B`'s side** — which §3.7a rev. 19
permits "where the claim being supported is about reproducibility itself rather than about
scientific tolerance". This **overrides route (iii)'s own tail** ("with `ε` then argued from `S`'s
side"), a clause it is easy to stop at.

### 2.2 `ε` — **PROPOSED at `1e-9`. NOT ADOPTED. NOT GRADED.**

| step | |
|---|---|
| 1 — PROVEN | on the reported support, `r_null ≤ max_i \|Δ_i/x_i\|`, from `‖Δ‖² = Σ(Δ_i/x_i)²x_i² ≤ max(...)²‖x‖²`. So an `ε` on `r_null` is **implied** by the same numeral applied per bin and is never stricter than it |
| 2 — EMPIRICAL | `max_i \|Δ_i/x_i\|` is **exactly** what `p4_lib.py:214` computes (`rel = np.max(np.abs(a[m]-b[m])/np.abs(b[m]))`), and its tolerance `REPRO_RTOL_PER_BIN = 1e-9` was declared at `p4_lib.py:93` on 2026-08-07 against a **measured** floor `1.9e-11` (job `56471429`, 106,940 pooled bins) — a **52.6×** margin that reproduces |
| 3 — JUDGEMENT | adopt the same numeral for `r_null`: Z's null gate becomes no stricter than the reproduction standard already declared for this estimator chain, and by step 1 the inequality runs conservatively |

§6.4 clause by clause: scale-relative ✓; fixed before production ✓; justified by controls
established **before implementation** ✓; **not selected from a favourable production result** ✓ —
it predates Z entirely.

⚠ **Its falsifier is UNEVALUATED.** The falsifier reads "if **pinned-envelope repeats of the full
CV chain** show a floor above about `2e-11` **for Z's bank**, the transfer is refuted", and the
next clause of the same row states the transfer's limits: "different subject (**standard-P4 5D
unfold chain, not Z's throw bank**); different comparison (**two full re-unfold products**, versus
**two in-process CV re-unfolds inside one `do_combine`**)". `B_loose = 1.831e-11` is from the
standard-P4 chain — the object the falsifier is contrasted **against** — so placing it beside
`2e-11` compares across both populations that row names. **No pinned-envelope repeat on Z's bank
has ever been run.** An earlier reading of this lane's reported that comparison as "a check that
passed narrowly, ratio 0.915"; that is **withdrawn** as a cross-population comparison given three
significant figures.

Grading belongs to `owners.tsv:15`, `z-independent-assessor session [cb0b6b]` — not to the lane
that authored the proposal (`BEN-381`).

### 2.3 `B` — the binding quantity. **ACCOUNTABILITY ASSIGNED 2026-09-16**

Because `ε` must be argued from `B`'s side (§2.1). Accountability for `B`'s justification sits with
`owners.tsv:14`, `z-criteria-designer session [91eaa2]`; implementation support with
`owners.tsv:11`, `lane_b` (implementation/write); assessment with `owners.tsv:15`,
`z-independent-assessor session [cb0b6b]`. The smallest concrete proposal that can establish `B`
is requested separately and is **preparation only** — no additional compute and no estimator
changes are authorized by it.

`B_loose = 1.831e-11` is `INTEGRAL_LEG_COHERENT_CEILING` at `p4_lib.py:158`, described at `:115` as
"the fully COHERENT ceiling". It is **not** job `56471429`'s figure, which is `worst_rel_bin =
1.9e-11` at `:196-202`; an earlier reading of this lane's attached the concurrency-pair caveat to
the wrong number. `p4_lib.py:109-120` warns that the related 3.48× margin "is **NOT slack** ...
already sits at 54.6% of the coherent ceiling", which cuts against treating `1.831e-11` as
comfortable.

**Route (i) — "pin the envelope in code" — cannot be claimed today, and route (i) is the ONLY
admissible route** (see §2.4). Measured at `12250ba2`, over the **11 `.sh` files that reference
`MNV_EST_SEED_OFFSET`** — the population is stated because the figure is meaningless without it:

| | |
|---|---|
| **1 LITERAL** | `sbatch_uthrow_run_5d_fast.sh:182` — `OMP_NUM_THREADS=32 MKL_NUM_THREADS=2 OPENBLAS_NUM_THREADS=2 …`, 4 of 5 thread variables |
| **2 DERIVED** | `sbatch_mii_estimator_scan_5d_bkgaware_gpu.sh:27`, `sbatch_unfold_5d_detector_bkgaware_gpu.sh:20` — both `${SLURM_CPUS_PER_TASK:-32}` |
| **8 UNSET** | including **`sbatch_uthrow_combine_5d_fast.sh` — arm 7**, whose `:9` reads "`--null` repeats CV at the identical seed", and which exports **0 of 5** thread variables |

1 + 2 + 8 = 11, internally consistent.

⚠ **AN EARLIER REVISION OF THIS SECTION SAID "one launcher of eleven" WITH NO POPULATION NAMED**,
and a later one explained a discrepancy with a mechanism that does not exist. Both are corrected
here; the number `1 of 11` stands.

The eleventh file is **`docs/orchestration/runs/clausec-rerun-20260821/harness/run_arms.sh`** — an
**archived harness, not a launcher** — which exports and unsets the variable directly and carries
no `OMP_NUM_THREADS`. So `1 + 2 + 8 = 11` closes over the stated criterion.

**The retracted explanation.** This section previously said the criteria lane's tree has 10 files
in this population "because `sbatch_uthrow_dump_5d.sh` differs by 360 lines between the two trees".
That is wrong twice, and measurably: `sbatch_uthrow_dump_5d.sh` contains **0** references to
`MNV_EST_SEED_OFFSET` in this tree **and** at `9dba1194`, so it is not in this population at all;
and `git grep -l 'MNV_EST_SEED_OFFSET' <rev> -- 'nd-unfolding/*.sh'` returns the **same ten files,
identically**, at both revisions. **The trees never differed here.** The 10-versus-11 gap was a
**directory scope** — tree-wide against `nd-unfolding/` only — not a fork. `dump_5d` does carry
`OMP_NUM_THREADS=8`, which is why it correctly appears in the *other* census (the 24-file
`sbatch_uthrow*` population); it belongs to one population and not the other.

I asserted that fork as the cause of a discrepancy **without running a command against it**. A
mechanism offered to explain a disagreement is still a technical claim, and this one was false.

**What genuinely remains open is a DEFINITION, not a count:** whether an archived harness under
`docs/orchestration/runs/` belongs in a population meant to characterise *production launchers*.
Under the stated criterion — `.sh` files referencing `MNV_EST_SEED_OFFSET` — it does, giving
**1 of 11**. Under an intended production-launcher criterion it does not, giving 1 of 10, **and
that criterion then has to say so.** Both lanes reached for "1 of 10" at some point by exactly that
unstated reasoning, which is the argument for a ratio travelling with its population — better
stated than either lane first stated it.

**A ratio quoted without its population is the defect §9 documents, one round later and in this
record.** The load-bearing fact is unaffected under every reading, tree and population measured:
**arm 7 pins none.**

**And §4.4a item 3 requires the SURROUNDING environment pinned too** — "AND TODAY IT IS NOT —
MEASURED". Pinning LightGBM while `MKL`/`OPENBLAS`/`NUMEXPR`/`VECLIB` remain free in the arm that
computes the null would be, in §4.4a's words, "a bound over a configuration that is not fixed".

### 2.4 ~~Route (i) is the only ADMISSIBLE route, and the fallback is barred by composition~~ — SUPERSEDED, see §13.1

> ⚠ **THIS HEADING IS SUPERSEDED — see §13.1. The fallback is UNRULED, not barred**, and route
> (i) is not established as admissible either: the §6.4 subject question governs it too.

| route | status |
|---|---|
| **(i)** design property from pinning — never measures Z's null | **ADMISSIBLE** |
| **(ii)** standalone control on Z's bank | **GATED** — `SPEC:3140`: "if the control runs on Z's own bank, §6.4 is engaged and needs a ruling" |
| **(iii)** establish `S` first | ~~**EXHAUSTED**~~ **→ UNFINISHED (§12.2 premise 2, §13.1).** The row's ground — *"`S` is vacuous"* — is WITHDRAWN; full `S` is OPEN |
| declaring `B` from the precursor's own two persisted executions | ~~**BARRED**~~ **→ UNRULED (§13.1).** The composition that barred it needed the withdrawn premise; `SPEC:1410` alone bars only the DIRECT reading. **Unruled is not admissible** |

⚠ **THE PARAGRAPH BELOW IS WITHDRAWN (§13.1) AND RETAINED TO SHOW WHAT THE BAR RESTED ON.** Its own
sentence *"neither clause bars it alone"* is why withdrawing the premise leaves the fallback
**UNRULED** rather than barred — and unruled is **not** admissible.

⚠ **The fallback is barred by a COMPOSITION, and neither clause bars it alone.** §C.2 and §2.1
establish that `S` is non-binding, so **`ε` must be argued from `B`'s side**. `SPEC:1410` states
that **"`ε` may not be read off Z's own null."** The precursor's two persisted executions **are**
Z's own null. So declaring `B` from them makes `ε` trace to Z's own null with one indirection —
the same forbidden act. §C.2 alone bars nothing; `:1410` alone bars only the direct reading. **It
is the composition that bars it**, which is why an earlier draft of this lane's B proposal reached
for that fallback as "the cheapest resolution that preserves the precursor". Withdrawn.

**The consequence is that §4.4a's six items stop being a wish-list and become binding**, because
there is nothing to fall back to if one fails. §4.4a's own closing: "If item 1 or 2 fails — the
pinned chain is not bit-identical — route (i) does **not** deliver a design property at all."

**A live defect in `B`'s precedent narrative, unrepaired and routed to `lane_b` /
`standard_p4`:** `z_reproducibility.py:412-415` argues the precedent's margin as "(52× per-bin,
32× integral)". Both legs are stale. Integral: the real margin is `1e-11 / 2.874e-12 = 3.479×`, so
32× is overstated by **9.20×** (job `56495756`, 10/10, `p4_lib.py:124-138`). Per-bin: 52× came from
the superseded operand `1.93e-11`, while `p4_lib.py:139-141` now reads "54.6× margin (1e-9 vs
1.831e-11)". `z_contract.py:75-80` states why the numbers are standard-P4's subject and not Z's:
those tolerances "were declared for the standard-P4 chain, which is a different subject."

---

## 3. The persistence requirement, reconciled with the completed precursor

§7 **item 1** requires persisting `x_cv` / `x_cv2` and the support predicate so that the
denominator of the ratio the null criterion grades is recoverable from the product the criterion
grades. **It is already discharged for the completed precursor.** Nothing here reopens that work.

**MEASURED, by revision:**

| revision | `hCvExecution` occurrences in `unified_throw_cov.py` |
|---|---:|
| `923e1323` (G's era) | **0** |
| `e09513d842ad3acc1964c1af740696f02eaed7d9` (the precursor's producing revision) | present |

At the precursor's revision the writer emits `hCvSupportMask` (`TH1I` over `n_total` bins, "1 = CV
bin is in the reported support"), `cv_support_predicate` as a `TNamed`, `n_cv_bins_total`,
`n_cv_support`, `n_cv_genuine_zero`, `n_cv_negative`, `n_cv_executions`, and `hCvExecution{k}` —
"the EXECUTIONS themselves, unmasked", over all `n_total` bins.

**The completed precursor product carries them, with digests.** From the 2026-09-15 rehearsal's
preserved bridge record, against source `unified_throw_cov_5d.root`, sha256
`09a029ed2a7de0ffd144b1ad0ad8d3e0bf8e8b9788797b0af58693c753795560`:

```
hCvExecution0   f5f26ce99b076841a14e4ac3f7f1d9ce4490aa42c055419a8b0a9dd13f6e9e6e
hCvExecution1   ed1350f1cb45d019eebf9284027829893bbaf4dc4e3f206f8ea7540b5074f25b
hCvSupportMask  ea0059ed280c2cdb928911abe64b3b6310cfdc9e27b6b77b0605207e35fcb48f
n_cv_bins_total 65856   n_cv_support 10694   n_cv_genuine_zero 55162   n_cv_negative 0
```

**And the denominator is therefore already measured, not merely recoverable:**

```
cv_norm  = 3.2124510692799616e-37      <- ‖x_cv‖, the denominator
num_norm = 1.4301832847122437e-50      <- ‖x_cv2 − x_cv‖, the numerator
r_null   = 4.4520002137582904e-14      internally consistent: num/den reproduces r_null exactly
```

⚠ **Two qualifications, both load-bearing.**

1. **This is the PRECURSOR's `‖x_cv‖`, not G's.** `SPEC` §C.3's consistency check asks whether
   **G's** own null would pass, and is breached only if `‖x_cv^G‖ < 5.8223e-41`. G's writer does
   not persist the vector (0 occurrences at `923e1323`), G's `x_cv` is **computed in-process and
   never written**, and `hXSecND_flat` — a *persisted histogram* read from `args.prod` at
   `adopt_unified_5d.py:116` — is a **different kind of object** and is absent from G's 13-key
   inventory. So **G's check is not recoverable from any artifact and is prospective only.** It is
   not reopened here.
2. **`r_null = 4.4520002137582904e-14` is Z's own null and may not set `ε`.** `SPEC:1410` — "`ε` may
   not be read off Z's own null" — and §6.4 at `:3584`. It is recorded and **explicitly ungraded**.

**A stale substantive claim this exposes**, distinct from the citation defect in §6: the module
docstring at `z_receipt.py:5-14` states the writer "does **NOT** write `x_cv`" and that the
denominator "is not recoverable from the product the criterion grades". That was true at G's era
and is **superseded for the precursor**. It bears on interpretation and is routed to `lane_b`.

---

## 4. A9 — the assembly is cheap; the I/O is the cost

`n = rows.size` at `z_build.py:511` is the **support size, 10694** — not the 65856 grid. One dense
float64 covariance is **0.91 GB**, and `eigvalsh` at that order extrapolates to **~59 s per
variant** from a measured 4-thread `n=3000` point (1.306 s, 186 GFLOP/s). Peak memory a few GB.
The authorized 1:30 wall and 64G have large margin. (Extrapolated from a developer machine; this
fixes the **order**, not the number.)

**The eight bound input sources total 89.11 GB**, measured on the cluster: active `42.33 GB`,
support `41.44 GB`, throw `2.67 GB`, ml / parent / stat `892 MB` each, central `0.48 MB`, null
`0.19 MB`. 45 support bands at 0.91 GB each accounts for the donor almost exactly, so the bands are
stored essentially uncompressed and `_sum_bands` (`z_build.py:295-301`) accumulates them one at a
time.

**What A9 still lacks is the endpoint production, not the assembly:** 4–5 rounds of 374 tasks whose
fit inside R5 is recorded as "NOT established" (`Z_CONSTRUCTION_PLAN.md:853-857`).

---

## 5. The binding constraint is the calendar

`docs/orchestration/state/r5-meter-receipt.json`, measured 2026-09-16T00:58:55Z on login05,
`r5_meter.py --self-test` PASS:

```
cpu_task_hours  95.878 / 500     headroom 404.122
gpu_task_hours   1.279 / 500     headroom 498.721      fired: none
```

`stop_date_utc` is **2026-09-30T00:00:00Z — 14 days** — against 404 CPU task-hours of headroom and
a 348.5 CPU task-hour `M(ii)` family (`Z_DECISION_PACKET.md:94`). **The ceiling is not what will
stop this. The date is.**

⚠ **A gate that was closed without being noticed.** The committed receipt had been measured
2026-09-09; `R5-METER.md:31` and the meter's own docstring treat an older-than-24-hours receipt as
a **stop**, and `check` enforces it — against the stale receipt a 1.75 CPU task-hour proposal exits
**4, "receipt is stale"**. So admission had been closed since 2026-09-10 while four attempts were
admitted against a figure that had been measured and reported but never committed. **Measuring and
reporting is not recording.**

---

## 6. Acceptance criteria that need justification BEFORE further results are examined

Resolving any of these produces a number graded against nothing.

1. **`(3,Z) M(ii)`.** Thresholds **withdrawn**, and `SPEC:2124-2175` records why: the derivation
   rule `|U′−U| ≤ u/2` is "NEITHER NECESSARY NOR SUFFICIENT for display invariance", wrong about
   one pair in four, and the acceptance level was read off the formatting of **two macros that are
   defined and never printed**. The document names this "measurability chose the specification"
   (`:2170`).
2. **`(3,Z) M(i)`.** `ε` withheld; `SPEC:1257` reject condition `4c` makes running against it a
   **REJECT** — "An un-derived boundary is not a criterion."
3. **The per-bin leg of `M(ii)`.** `SPEC:2117` records the unanswered question verbatim: "What
   per-bin movement is acceptable, in what fraction of bins, and why?" — a tolerance **and** a
   coverage fraction, neither declared.
4. **Any significance built on these.** `Z_DECISION_PACKET.md:120` — "threshold and margin exist
   nowhere in the tree."

---

## 7. Shortest scientifically sufficient route

1. **`B`'s two judgement prerequisites, §4.4a items 4 and 5** — a **predeclared estimator of `B`**
   (Gap 3: "two arms do not prevent tuning") and a **coverage/confidence objective for the repeat
   count** (Gap 2: "4 repeats had no justification"). **Both are zero compute, both are judgement,
   and both gate the run** — so the actionable next step for `B` is not an allocation. Accountability
   assigned 2026-09-16 (§2.3). Gates A1, which gates `(3,Z) M(i)`, a REQUIRED cell.

   ⚠ **What the evidence design must be, corrected.** An earlier draft of this lane's proposal
   offered "arm 7 twice on the same fresh slabs, pinned versus unpinned" — which measures
   **pinning's effect** and **cannot evaluate the falsifier it was paired with** ("if two *pinned*
   executions are not bitwise identical"), because that needs **two pinned runs compared to each
   other**. Two different experiments. That is the same defect as `ε`'s UNEVALUATED falsifier in
   §2.2, reproduced while claiming to avoid it. §4.4a **item 1** requires repeats of the **full CV
   unfold chain**, not one estimator fit, and **item 2** requires them to **span DIFFERENT
   ALLOCATIONS** — "Repeats on one node do not test it — they test in-process determinism, which is
   the easy half." So the minimum is **≥2 pinned full-chain repeats in different allocations**, plus
   one unpinned only if the effect is also wanted; per-invocation arm-7 cost is measured at
   `0.3875` / `0.4239` / `0.5764` CPU task-h, so ~1.2 CPU task-h for the two, ~1.8 with the
   unpinned arm. **Not authorized here.**
2. **§7 item 4** — the throw-deviation and completeness-division channels, so `S` covers more than
   F7. "Arithmetic + one code read."
3. **Answer `SPEC:2117`'s verbatim `M(ii)` question** — zero compute. Until it is answered the
   348.5 CPU task-hour `M(ii)` family cannot be specified, let alone afforded.
4. **Name a grading lane that `BEN-381` does not disqualify** — zero compute, and every cell's
   grade is void without it.
5. **`(cause 5, Z)`** — a static construction-path trace over every module Z invokes, including
   `adopt_unified_5d.py`, by a non-owning lane. Zero compute, one cell closed.
6. Only then spend compute: the 0.58 CPU task-hour design-property `B` route, and the assembly.

**Items 1–5 are all zero-compute and all upstream of every number.** With 14 days to the stop
date, they are the whole critical path. This programme is not currently blocked on compute or on
code.

---

## 8. Correction history

This record states current positions. The sequence by which several of them were reached — and
the readings withdrawn along the way, including two of this lane's own — is preserved in the commit
messages of `32162a8e`, `34c78068`, `12250ba2`, `fb9ec356` and `a71234d6`, and in the routed
review and criteria-owner exchanges they cite. Positions withdrawn in this record are marked at
the point of withdrawal rather than deleted.

Of the corrections in that sequence, most were one lane catching another's; **the two most
consequential were each lane catching its own** — a `PM-6` chain withdrawn after its author read
its own §C.2, and a "`B` is unowned" claim withdrawn before it became a decision, after a positive
control showed the same grep returns zero for covariance, flux, cause, unfold, assembly,
systematic and note, because `owners.tsv` is lane-granular and only rows 14–15 name a subject. A
single-pass reading ships both, and neither is the kind of error an external reviewer is positioned
to find. **That is the argument for the ungraded status in §2.2, not a hedge attached to it.**

---

## 9. A documentation defect, kept separate from execution

**No effect on any pilot's inputs, calculations or interpretation**, and recorded here only so it
is not rediscovered. All five sites are prose — four markdown, and the one `.py` site
(`z_receipt.py:10`) is inside a module **docstring**.

Five sites assert that the CV vector is dropped at `:586` of `unified_throw_cov.py`:
`Z_BUILD_PACKET.md:446`, `z_receipt.py:10`, `SPEC:1271`, `SPEC:1920-1921`,
`state/preflight-20260906-r5/R5-PREFLIGHT-EVIDENCE.md:410`.

**`:586` was never correct.** The write site sat at `:587` from `ae42ae8d` (2026-08-22) through
`923e1323` (2026-09-10) — exactly one commit touched the file in that window, on its boundary —
and every citing document was added inside it. **Direct evidence of copying:** `z_receipt.py:10`
and `SPEC:1920-1921` are **word-for-word identical**, differing only in markdown emphasis
(measured whitespace-normalised with `*` stripped). Four of the five pair `:586` with `:369-371`,
which *is* correct for that era.

**Repair constraint:** a partial repair makes the disagreement count go **up** — fix one and four
remain agreeing with each other and disagreeing with the file. One change reaching all five, bound
to a sha, or none. The address has since moved `587 → 1172 → 1245`, so a corrected digit would not
survive either. **And `Z_CONSTRUCTION_PLAN.md:347`'s `:582-598` must be left alone** — it is a
range that *contains* 587 and is not wrong; a sweep for `:586` would normalise it into the same
broken scheme and destroy a correct citation.

Routing: `SPEC:1271` / `:1920-1921` are the scientific contract and not amendable by either lane;
`z_receipt.py:10` routes to `lane_b` with the §3 substantive staleness; the preflight record and
`Z_BUILD_PACKET.md` are other lanes', born archival.

---

## 10. The fourteen remaining requirements, reconciled against executed evidence (2026-09-17)

**Read the classification, not the list.** `notes.remaining_requirements` in a build receipt is a
**fixed fourteen-key list**: `z_build` emits it unconditionally and it does not shrink when a
subrequirement is met. So "fourteen remain" after `58454524` is not a measurement — it is the
same string it would have printed on any run. What follows is the measurement.

Sources, all re-measured 2026-09-17 from the preserved copies, not recalled:
`z-receipt-cv.json` (`9f8f91d9be69d767…`) and `z-receipt-mean.json` (`5bdc9a1830dc183a…`), digests
re-computed from the preserved files and **2 of 2 MATCH** their entries in the pilot receipt;
`z-pilot-receipt.json`; `bridge.json`; the job's own `.out`/`.err`; `sacct` step rows. Evidence
route: `ND_OMNIFOLD_RUN_LOG.md` § 2026-09-17 and
`/pscratch/sd/j/josephrb/zpilot-20260916/outcome-58454524/`.

### 10.1 What the run actually closed — completed **subrequirements**

Each row is a *part* of its requirement. **No row closes its requirement**, and none is a grade.

| key | completed subrequirement, with the receipt field that carries it |
|---|---|
| `code_and_run` | **Pinning and measured imports are done.** `code_identity.revision fb9ec3560fd6d62295dffc81b5694c9e26667d5b` with `worktree_files_differing_from_revision: []`; **15** `import_closure_digests`; `z.run = {id: z-pilot-20260916-a5, step: assembly}`. Deployment `zdeploy-fb9ec356`, **895** tracked files, listing `f2333fb32876363d12c2c5aebfe50e2a986504845affd5721f4c04fedee23e61`, `dirty 0`, **15 of 15 CURRENT**. `notes.input_kind: **real**` — the construction ran on the bound production inputs, not a fixture. |
| `runtime` | **Measured at production scale, and one half of it contradicts §4** — see §10.5. Real PyROOT verified in situ (14 environment closure members against `mnv_env_manifest.tsv`; ROOT's own `TInterpreter::ReadRootmapFile` warnings preserved in the child's stderr, `chars 2424`, `abridged false`, `sha256 9c780d41…`). `build_seconds 760.767…`; `eigvalsh` **33.503 s** (cv) and **16.516 s** (mean); job `ElapsedRaw` **1037 s** of a 5400 s wall. |
| `null` | **The persistence half, discharged twice and independently.** At throw creation by the producer (RUN_LOG § 2026-09-14) and again into `z-null.npz` by `z_receipt.persist_null_operands`: `sha256_x_cv f5f26ce9…`, `sha256_x_cv2 ed1350f1…`, `sha256_support_mask eed021e9…`, `n_grid 65856`, `n_rep 10694`, `bytes_persisted 1,119,552`, `construction_digest 4eda956c…`. **Not reopened here** — recorded as satisfied. |
| `cause2` | **The F7 operands are now bound in-receipt for both variants.** `causes.2.joint_mean_shift_sha256` = `inflation.raw_operands.joint_mean_shift` = `6abfa1bba209e666c3dbc8217dcc79e800fa45f231112caf6972dc0eaf8e9d3c`; `ms_norm 1.8786967332845478e-38`. `k` and its source were already established by argument in §2.1 (`F7_FLOOR_MULTIPLE = 2.0`, strict `>`, `N = 160`). |
| `cause7` | **The five active bands are enumerated and digest-bound, and the partition is exhaustive.** `inflation.membership.bands_lateral` = `BeamAngleX`, `BeamAngleY`, `MuonResolution`, `Muon_Energy_MINERvA`, `Muon_Energy_MINOS`; `G5_band_partition` `exhaustive: true` with `5 + 13 + 27 = 45 = n_inventory`. Each of the five carries its own object digest under `notes.inputs.active.objects`. |
| `cause5` | **The consumed-input inventory now exists and is enumerable** — the object the independent trace needs and did not have. All eight sources bound by file digest, size, device/inode and stamp, with per-object digests and shapes. |
| `parent_lineage` | **Both files are bound.** `parent.combined_source 9f7b2f55…` (41,436,632,945 B) and `parent.parent_candidate 4f168e83…` (892,170,881 B). |
| `component_footing` | **The footing is single and digest-bound**, and its basis is declared rather than assumed: one `mask_sha256 eed021e9…`, one `row_order_sha256 61a7c9fd…`, manifest `BOUND` on exactly those two, and `z.row_order_basis` states **"C-order flat indices reconstructed from declared production CV; NOT read_from_G"**. |

**Structural gates, all closed on their own arithmetic tolerance** (`IDENTITY_RTOL = 1e-9`,
`fb9ec356:nd-unfolding/z_contract.py:125`): `G1_closure_identity` `max_rel_residual` **0.0**;
`G3_g_reconstruction` `max_rel_diff` **0.0**; `active_total_eq_sum5` **0.0**;
`G2_g_domain` `g_min 1.0`, `g_median 1.0473565738188244`, `g_max 17.653141714565614`,
`n_gt_one 6528`, `n_pinned 0`; `G3R_raw_operand_reconstruction` **`discriminating: true`**
(`n_separated 6527`, `n_saturated_v_uni_below_v_blk 4166`, `n_shift_below_tolerance 1`,
`max_separation 0.6270761129833259`), `n_clipped_blocksum 0`, `n_clipped_unified 0`.

⚠ **`G3R.stored_cv_cross_checked: false`** (`stored_cv_deviation` and `stored_cv_discriminating`
both `null`), and `null.declared_cv_crosscheck.external_crosscheck_status: **UNPERFORMED**` with
`verdict: UNRESOLVED` — its own stated reason is that the compared object is *this build's own
declared `central` source*, not an external production ROOT. **Two named non-checks inside an
otherwise-closed gate set.** They are recorded, not repaired, and they are not the precursor
persistence question.

### 10.2 The PSD gate: results and thresholds, as the build recorded them

`fb9ec356:nd-unfolding/z_assembly.py:512-561`. The gate is **fail-closed and returns no boolean**:
`require(...)` raises `ZContractError`, so the presence of a populated `G4_symmetry_psd` block in a
receipt *is* the pass. Criterion, scale-free by deliberate design: `asym <= rtol` **and**
`lam_min >= -rtol * lam_max`, on `0.5 * (C + Cᵀ)` via `numpy.linalg.eigvalsh`.

| object | `lambda_min` | `lambda_max` | `neg_fraction_of_max` | `rel_asymmetry` | `rtol` |
|---|---|---|---|---|---|
| `C_Z` cv (inflated) | `-1.2750516323643892e-90` | `2.229223998752954e-75` | `5.719710684424999e-16` | `2.1641333629718972e-16` | `1e-09` |
| `C_Z` mean (inflated) | `-5.146659106575015e-91` | `1.9272637183054823e-75` | `2.670448811800462e-16` | `1.0927533323421377e-16` | `1e-09` |
| block-sum reference | `-4.6860865778129674e-91` | `1.205970554862754e-75` | `3.885738800933054e-16` | `0.0` | `1e-09` |

`psd_method: eigvalsh`, `eigenvalues_computed: true` on all three. The cv object's negative
excursion is **`5.72e-16` of `lambda_max`, i.e. `1.75e6`× inside the tolerance**.

**What this is and is not.** `z_assembly.py:49-51` states it in the module's own words: *"NO
ACCEPTANCE BOUNDARY APPEARS IN THIS MODULE. Everything gated here is a structural identity whose
tolerance is arithmetic (`IDENTITY_RTOL`, §3.3 condition 2). The scientific boundaries live in
`z_contract.Z_BOUNDARIES` and are withheld."* So `1e-9` here is **not** a scientific threshold and
this row is **not** a scientific grade. **No clipping, flooring, regularization or replacement
threshold is introduced, proposed or implied by this section.** The spectra the pilot persisted are
a deliberate *second independent* `eigvalsh` on the closed artifact (`verdict: None` in each),
because `z_assembly.gate_symmetry_psd` keeps sole ownership of the PSD decision; the pilot records
and does not restate it. The separately reported `n_negative` **5214** (cv) and **5215** (mean) of
10694 are that second decomposition's counts, and the gate's criterion is on the **extremal
eigenvalue relative to `lambda_max`**, not on a count — a count is graded against nothing here.

### 10.3 Unresolved **scientific criteria** — zero compute, and upstream of every number

| key | what is missing | state |
|---|---|---|
| `null` → **A1** | `B` (operating-error bound), `S` (independent scientific cap), the precondition `B ≤ S`, and `ε` argued within `[B, S]` | **OPEN.** `withheld_boundaries.null_epsilon` `status: WITHHELD`, `value: null`. `ε = 1e-9` remains **PROPOSED, UNGRADED**; `S` is discharged **for the F7 channel only** (§2.1); `B` has accountability assigned (§2.3) and **no established value**. |
| `cause3` | `cause3_agg`, `cause3_med`, `cause3_corr` | all three **WITHHELD**, `value: null`, for the reasons §6 records. `cause3_corr` additionally has **no correlation-sensitive leg adopted**. |
| `cause3` | `SPEC:2117`'s verbatim question — *"What per-bin movement is acceptable, in what fraction of bins, and why?"* | **unanswered.** A tolerance **and** a coverage fraction: two numbers, both scientific. |
| `endpoint_completeness` | the committed ROOT inspection's endpoint `globalCompleteness` readings above one, resolved without normalization and without an invented criterion | **unresolved**, and judgement, not measurement. |
| `cause6` | the statistical projection **operator** | a design choice before it is a census. |
| — | a grading lane that `BEN-381` does not disqualify | **unnamed.** Every cell's grade is void without it (§7 item 4). |

⚠ **THE ONE NEW NUMBER IN THIS CLASS, AND WHY IT DOES NOT HELP.** `58454524` measured the per-bin
statistic that `ε` is *defined on*: `null.per_bin_diagnostic.maximum_relative_difference` =
**`1.7552716191735518e-12`** at `argmax_grid_index 31499`, flagged `grades_nothing: true` by the
writer itself. It is the first production-scale value of `max_i |Δ_i/x_i|` on Z's own bank, and it
confirms §2.2 step 1's proven inequality in the right direction — `r_null / per-bin max` =
**`0.02536 ≤ 1`**. It also sits **569.7×** below the proposed `ε = 1e-9` and **10.43×** below
`B_loose = 1.831e-11`.

**It cannot establish `B`, and reading it that way would reproduce a defect §2.4 already names.**
`z-null.npz` holds exactly the precursor's two persisted executions, and §2.4 records that
declaring `B` from those is ~~**BARRED by composition**~~ **UNRULED — see §13.1**; the clause that
follows states the withdrawn premise and is retained only to show what the bar rested on:
`S` is non-binding, so `ε` must be argued
from `B`'s side, and `SPEC:1410` forbids `ε` being read off Z's own null — declaring `B` from these
vectors makes `ε` trace to Z's own null with one indirection. It is also **not** the pinned-envelope
repeat §2.2's falsifier needs: one execution *pair* inside one `do_combine` on one node bounds an
observed deviation and estimates no floor, and §4.4a item 2 requires repeats **spanning different
allocations**. Recorded as an observation; **it moves nothing**.

### 10.4 **Independent verification** — zero compute, and not performable by this lane

Every row here uses the word *independently* or *verify* in the requirement itself, so the lane
that built the artifact is disqualified from closing it by construction.

| key | what a non-owning lane must do |
|---|---|
| `code_and_run` | independently verify the real-input construction and environment. The operands now exist: revision `fb9ec356`, 15 import digests, deployment listing `f2333fb3…`, env-provenance digest `f8d65913b5bf3880`, and the four guard inventory records. |
| `cause5` | the static construction-path trace over every module Z invokes, **including `adopt_unified_5d.py`** (§7 item 5) — *"zero compute, one cell closed"*, and the receipt's own text insists *"construction alone does not dispose of this cause."* |
| `parent_lineage` | `lineage_status` is **`UNVERIFIED`** in the receipt. Establishing that the two bound files *are* G's actual inputs is blocked upstream on `PM-4`, which `SPEC:304` records as having **"no referent"** — G's committed 13-key inventory contains neither `hRowIndex5D` nor `hXSecND_flat`. |
| `component_footing` | per-component estimator, normalization, background treatment and provenance on the one fixed central value. The footing and mask are bound; the *component-by-component* check is not done. |
| `cause7` | the ten endpoint identities, the migration censuses, the declared policies and the support-scope check. Band membership and exhaustiveness are done (§10.1); these are not. |
| `cause2` | whether the now-bound operands and the §2.1 `k` argument actually *discharge* the cause is the assessor's read (`owners.tsv:15`), **not this lane's**. |

### 10.5 Work requiring **new compute** — and two corrections to §4/§5

| key | compute, and whether its cost is established |
|---|---|
| `cause3` | build all `M(ii)` members: **348.5 CPU task-hours** (`Z_DECISION_PACKET.md:94`) — and it **cannot be specified** until `SPEC:2117` is answered, so the criteria block it, not the ceiling. |
| `null` → `B` route (i) | **≥2 pinned full-chain repeats in different allocations**, ~**1.2 CPU task-hours** (~1.8 with an unpinned arm), from the measured per-invocation arm-7 cost `0.3875` / `0.4239` / `0.5764`. **Gated behind two zero-compute judgements** (§7 item 1) and **not authorized**. |
| `cause1`, `cause4`, `cause6`, `cause7` counterfactuals | the endpoint-interpolation counterfactual, the jitter add-back print value/seed/digests, the coverage censuses, the measured cause-7 counterfactual. **Cost NOT established for any of these** — stated as unestablished rather than estimated. |
| assembly itself | **DONE.** §7 item 6's second clause is discharged; its first clause (the `B` route) is not. |

⚠ **§4 IS WRONG ABOUT MEMORY, AND IT IS THE ONE FIGURE THAT MATTERED.** §4 reads *"Peak memory a
few GB. The authorized 1:30 wall and 64G have large margin."* Measured on the `.batch` step of
`58454524` — `MaxRSS` is step-level, so a `sacct -X` or JobName-filtered query returns it **empty**
and reads as "not recorded":

```
58454524.batch   MaxRSS 52146232K = 49.73 GiB   ReqMem 64G   →  77.7% of the request
```

The **wall** had large margin (1037 s of 5400 s, **19.2%**). The **memory did not**: 22.3% headroom,
against a prediction that was low by more than an order of magnitude. Runtime, conversely, came in
*under* §4's estimate — `eigvalsh` at n=10694 was predicted at ~59 s per variant and measured
**33.503 s** and **16.516 s**. §4's own caveat ("this fixes the **order**, not the number") holds
for time and fails for memory. Any future sizing must start from **49.73 GiB measured**, not from
"a few GB".

⚠ **§5's pscratch figure was the filesystem's, not mine — a denominator error.** I reported
"pscratch at 67%", which is `df` on the shared Lustre mount. The quota that constrains this work is
per-user: **`16.02 TiB / 20.00 TiB = 80.1%`** (`showquota`, 2026-09-17), 30 TiB hard limit, inodes
380.67 K / 10.00 M. The 1.7 GB of preserved products are inside that 80.1%. **R5 accounting**,
re-measured 2026-09-17T07:41:55Z: `cpu_task_hours` **96.196111 / 500**, headroom **403.803889**;
`gpu_task_hours` **10.210833**; **fired: none**; `58454524` present in `metered_task_ids`. The
pilot drew **1037 s = 0.288** of its authorized 1.5 CPU task-hours. `stop_date_utc`
**2026-09-30T00:00:00Z — 13 days.** §5's conclusion is unchanged and now stronger: **the ceiling is
not what will stop this; the date is.**

### 10.6 `authorization` — the fourteenth key belongs to none of the four classes

`notes.remaining_requirements.authorization` reads: *"Obtain the named production/resource
authorization and independent scientific decisions before production, adoption, projection or
publication use."* The **pilot** authorization was obtained, used once, and is **consumed** — one
submission, no replacement authorized or sought. **No production, adoption, projection or
publication authorization exists**, and none is requested by this record. It is Joseph's, and it is
downstream of §10.3, not a parallel track.

---

## 11. Next-action packet — the recommendation

**One decision blocks everything: `B`'s two judgement prerequisites (§4.4a items 4 and 5).**

| | |
|---|---|
| **The blocking decision** | Predeclare (a) **the estimator of `B`** and (b) **the coverage/confidence objective that fixes the repeat count**. Nothing else. |
| **Why it and not another** | `B` gates `ε`; `ε` gates A1; A1 gates `(3,Z) M(i)`, a **REQUIRED** cell; and `SPEC:1257` reject condition **`4c`** makes running against an un-derived boundary a **REJECT** — which is the exact condition the build returned (`outcome.reject_conditions: ["4c"]`, `null.assessment.reject_conditions: ["4c", "11"]`, `verdict: NOT ASSESSABLE`). Every other class in §10 is either already done, someone else's to verify, or barred behind a criterion. |
| **Evidence it is binding** | `ε` must be argued from `B`'s side, not `S`'s: `S` is **non-binding** because it is normalizer-free and the flip-`‖dx‖` is `1.7957e11`/`2.0433e11`× G's null, so an `ε` chosen from `S` is *"a gate essentially nothing can violate"* (§2.1) — the `1e-12`-clamp defect §3.1a measures. Route (ii) is **GATED** on a §6.4 ruling, route (iii) **EXHAUSTED**, and the precursor-executions fallback **BARRED by composition** (§2.4) — a bar that §10.3 confirms now covers the new `1.755e-12` per-bin measurement too. Route (i) is the only admissible one and **cannot be claimed today**: of the 11 `.sh` files referencing `MNV_EST_SEED_OFFSET`, **arm 7 — `sbatch_uthrow_combine_5d_fast.sh`, the arm whose `:9` says "`--null` repeats CV at the identical seed" — exports 0 of 5 thread variables.** |
| **Smallest necessary work** | Two predeclared statements, in one document, by the assigned owner (`owners.tsv:14`, `z-criteria-designer [91eaa2]`), reviewed by `owners.tsv:15` (`z-independent-assessor [cb0b6b]`) — **not** by the lane that authored the `ε` proposal (`BEN-381` disqualifies it). The design must be **≥2 pinned full-chain repeats compared to each other, spanning different allocations** (§7 item 1's correction: "pinned versus unpinned" measures pinning's effect and cannot evaluate the falsifier). |
| **Cost** | **Zero compute. Zero allocation. No estimator change.** Judgement only. |
| **What its outcome would permit** | With (a) and (b) fixed, the ~**1.2 CPU task-hour** route-(i) run becomes *specifiable and reviewable* — and only then submittable under a separate authorization. That run, if it succeeds, establishes `B`; `B` admits `ε` within `[B, S]`; `ε` lifts reject condition `4c`; and the two covariances that now exist become **assessable** — which is still not adoption, which is still Joseph's (`SPEC` §3.5). |

**Second and third, both zero compute, both unblocked, both parallel to the above:** §7 item 2
(the throw-deviation and completeness-division channels, *"arithmetic + one code read"*, so `S`
covers more than F7) and §7 item 5 (`cause 5`'s static trace by a non-owning lane, one cell
closed). §7 item 4 — naming an undisqualified grading lane — is a prerequisite for *reading* any
of it.

**What this packet does not propose.** No new assurance campaign. No re-run of `58454524`. No
projection. No additional independent tolerance: §10.3 records that the existing bound cannot be
stretched to cover the projected claim, and the four paused `S` conditions (deadband boundary
crossings, possible F7 branch changes, propagation to the declared projections, and the
inflation-factor question) stay **paused** and **unresolved** — the measured
`sqrt_tr_after / sqrt_tr_before` = **`5.674200780785609e-38 / 4.3576468306957044e-38` = 1.302125**
is now a real operand for that question and is **not** an answer to it.

---

## 12. §11 IS SUPERSEDED — the corrected recommendation (2026-09-17)

> ⚠ **§11 IS WITHDRAWN AS A RECOMMENDATION AND LEFT IN PLACE AS THE ERROR IT WAS.** It asked the
> criteria owner to predeclare two things that were **already declared 20 hours earlier**, rested on
> two premises Joseph has since ruled must be withdrawn, attached `ε` to the wrong statistic, and
> priced its request off historical elapsed times after Joseph had specifically forbidden that. Read
> §12 instead. Do not cite §11's packet table.

### 12.1 What already exists — B's estimator and repeat design are UNRESOLVED, not ABSENT

`78a8c2ee42c71db1e300e4cfe3735554101bf8ce` (2026-09-16 11:08:59 +0900, `owners.tsv:14`
`z-criteria-designer [91eaa2]`, on `origin/lane/z-criteria-recommendation-20260910`) delivers
`docs/orchestration/PREDECLARATION-20260916-B-estimator-and-coverage.md` — **`Z_CONSTRUCTION_PLAN`
§4.4a items 4 and 5, the exact two things §11 asked for.** §11 did not cite it because this lane
never read that branch. The declarations, as they stand:

| | declared |
|---|---|
| **item 4 — estimator** | **`B = 0`**, asserted as a property of the **pinned design**, verified by a **BOOLEAN** bitwise-identity test over the reported support. `IF NOT IDENTICAL: B is UNDEFINED and route (i) is FALSIFIED` — and *"`B` is explicitly NOT set to the observed difference."* Gap 3 closes **by construction**: the estimator's range is `{0, undefined}` and no observed magnitude enters it. |
| **why boolean** | it is *"the whole difference between route (i) and the barred route"* — **a boolean reads no VALUE off Z's null; the fallback read a MAGNITUDE.** Replacing `IDENTICAL` with a tolerance re-enters `SPEC:1410`, and the predeclaration names that substitution as the thing to refuse. ⚠ **The DISTINCTION survives §12.2's withdrawal; the word "barred" in the quoted phrase does not** — the fallback is now **UNRULED** (§13.1). The predeclaration's §1.2 cites the withdrawn composition as its *reason*; the boolean/magnitude distinction stands independently of it. |
| **item 5 — objective** | over **ALLOCATION SHAPES, not repeat count**, because thread count and reduction order are properties of the allocation. **Model A declared** (deterministic given the allocation), minimum **n = 3** — A1/A2 same node for item 1, B1 different node for item 2 — and **n = 4** to *attribute*. Model B retained only as a falsification branch: 6 runs to exclude a coin flip, 30 to exclude `p ≥ 0.1`. |
| **receipt requirement** | `--qos=shared` means different allocations are **requested, not controlled**: **≥2 distinct node names or item 2 is NOT TESTED and the run is INCONCLUSIVE, not a pass**; and if CPU models did not differ, the cross-microarchitecture arm is **UNEVALUATED**, never folded into a pass. |

**And the predeclaration states the limit §11 should have carried: `B = 0` DOES NOT GIVE `ε`.** It
gives `B ≤ S` trivially, but *"a gate at `ε = 0` fails on any nonzero deviation whatever, which is
the mirror-image of the `1e-12`-clamp defect"*, and `ε` may not be read off Z's own null. **`ε = 1e-9`
continues to stand or fall on §C.3's transfer argument alone, falsifier UNEVALUATED.** §11's claim
that establishing `B` would "admit `ε` within `[B, S]`" was wrong.

**Its own §3 names a measured obstacle no other document had:** every proposed pin set — §4.4a item
3's five variables and the three LightGBM knobs — pins **thread COUNTS only**, and
`OMP_DYNAMIC / OMP_SCHEDULE / OMP_PROC_BIND / OMP_PLACES` have **ZERO occurrences in
`nd-unfolding/`**, including in the arm treated as the pinned reference. So *"route (i) is
falsified"* would today be **ambiguous between "cannot be pinned" and "was never fully pinned."*

**Status: the estimator and the repeat design are declared, unassessed, and carry three open
residues** — the author cannot assess their own document (`owners.tsv:15`); whether the control may
run on Z's own bank needs a **§6.4 ruling the owner explicitly declines to issue**; and the pin set
is incomplete. **Unresolved, not absent.**

### 12.2 Three premises withdrawn

1. **"`S` is non-binding" — WITHDRAWN as an unqualified claim.** `S`'s bound is recorded as
   **F7-channel only**. `fb9fdec11c653d34c5f2ee16f9f68f6be837e6d8` and
   `480bed76f9cef73b66bc1bb0bd471847d5f61ce2` argue the other two channels are now covered — throw
   deviations exactly (`Δv^mean = 0`, `Δv^cv = −2·ms·δ + δ²`, so F7 was the whole channel) and
   completeness subsumed by C.3 step 1 — **but the owner withholds the verdict on their own
   residue** and routes it to `[cb0b6b]`. An unbounded channel can produce a binding `S`. Asserting
   non-bindingness from an **incomplete** bound is using an absence my own open item creates.
   **Full `S` is OPEN.**
2. **"Route (iii) is EXHAUSTED" — WITHDRAWN.** It was declared exhausted *because* `S` was called
   vacuous. With full `S` open, route (iii) — establish `S` first — is **UNFINISHED, not
   exhausted**, and it is the only route that needs no new products at all.
3. **`ε` is a tolerance on `r_null` — NOT on the per-bin diagnostic.** §10.3 called
   `max_i |Δ_i/x_i|` *"the statistic `ε` is defined on"*. **Wrong.** `ε` is declared against
   `r_null`, the `x²`-weighted relative L2. The per-bin maximum is a **different statistic that
   bounds `r_null` above** — and the owner's form is sharper: `min_i|ρ_i| ≤ r_null ≤ max_i|ρ_i|`.
   The per-bin diagnostic is therefore a *sufficient* implication route, never the definition, and
   the receipt flags it `grades_nothing: true`.

### 12.3 Observed agreement is not an established bound over an execution envelope

This distinction decides §12.4, so it is stated before the answer. `r_null = 4.452e-14` and
`max_i|Δ_i/x_i| = 1.755e-12` are **observations from ONE execution pair, in ONE process, on ONE
node, in ONE unpinned configuration.** They are digest-bound facts *about these artifacts*. They are
**not** a bound over any envelope: nothing in them constrains what a different allocation, a
different node, or a re-run would produce. `B` is exactly the missing object — a bound over an
envelope — and no number of observations of this kind becomes one.

### 12.4 THE CENTRAL QUESTION, ANSWERED BY MEASUREMENT

**Are we proposing to qualify the existing unpinned products, or to establish a changed
configuration requiring new products?**

**Route (i) CANNOT qualify the existing products, and this is measured, not argued.** I applied
`78a8c2ee` §1's predeclared estimator to the preserved operands in `z-null.npz`
(`cb82fc3285c981b91625530d48c14ff5554db5154db298a3144a57520633d77e`), executed on the cluster
against the artifacts rather than reasoned from the receipt:

```
n_grid 65856   n_support 10694
bins differing BITWISE, ON SUPPORT   : 10683        <- 99.90% of the support
bins differing BITWISE, OFF SUPPORT  : 0            (both vectors exactly 0 off support)
IDENTICAL over reported support      : False
max |a-b| on support                 : 2.5840205693274157e-51
max |d/x| on support                 : 1.7552716191735518e-12  at support-index 5723
relative L2 over support             : 4.452000213758293e-14
```

*(The relative L2 agrees with the build's `r_null` to **15 significant figures**, not bitwise — a
different summation order. The per-bin argmax is **support-index 5723**, which is **grid-index
31499** as the receipt records it; two bases for one bin, named because they look like a
disagreement. Only **11** support bins agree bitwise.)*

**Consequences, in order:**

1. **The predeclared estimator, applied to operands OUTSIDE its declared population, returns NOT
   IDENTICAL — so it cannot yield `B` for these products.** ⚠ **CORRECTED (§13.3). An earlier
   wording of this item said "route (i) is FALSIFIED for this configuration"; that applies the
   estimator's consequent outside its antecedent** and is withdrawn. Route (i) claims that
   **pinning** delivers `B = 0`; it never claimed an unpinned pair is bitwise identical. Finding
   non-identity here **CONFIRMS route (i)'s motivating premise** rather than refuting route (i).
2. ⚠ **ITEM 2 IS WITHDRAWN IN FULL (§13.3) — it was the one generalization in §12 that does not
   hold.** It read: *"the failure is in the EASIEST arm … the observed non-identity is not
   attributable to allocation shape, which is the only thing route (i) pins."* **Allocation shape is
   not route (i)'s pin set.** `Z_REPRO_KNOBS` at `fb9ec356:nd-unfolding/z_reproducibility.py:127-138`
   pins `deterministic`, `force_row_wise` and `num_threads` as **estimator parameters**, and
   `num_threads`' own rationale reads *"the estimator parameter, **NOT** `OMP_NUM_THREADS`, which
   this repository has measured LightGBM to **ignore**. Thread count sets reduction order, so an
   unpinned count makes the CV a property of the allocation."* `SPEC:3140` says the same: the
   cheapest route is *"code, not compute (pin `num_threads`/`deterministic`/`force_row_wise`)"*.
   **All three were free in the executions that made these products, so the observed non-identity IS
   attributable to variables route (i) would pin** — and the a-fortiori step needed the pair to have
   been pinned, which it was not. The substitution runs in **two** directions and I priced only one:
   stronger on the allocation axis (one process), **weaker on the pinning axis, because these
   products pinned nothing.** Separately, *"same-process is strictly stronger than same-node"* is
   **unestablished** even on the allocation axis: with `OMP_DYNAMIC` unset (§3's zero occurrences),
   per-region thread counts can differ between calls inside one process. ⚠ **Offered as an
   unmeasured gap and explicitly NOT as a cause.**
3. **Therefore the two routes are genuinely disjoint, and a pinned success does not transfer.** A
   pinned run would establish a property of a configuration that **differs from the one that made
   these products in exactly the variables at issue**. Carrying its result across is a transfer
   argument, and **no such argument exists** — the same defect as `ε`'s UNEVALUATED falsifier, which
   is a cross-population comparison. A pinned experiment would also require **new products** from
   the 89.11 GB input chain, i.e. a fresh production authorization, not a control.
4. **But qualifying these products does not need `B` at all.** For *these artifacts* the deviation
   is not a prediction to be bounded — it is a recorded fact. What is missing is not a bound on the
   deviation but a bound on its **consequence for the declared use**, and that object already has a
   closed form: with `G := diag(δg/g)`, `ΔC_infl = GC + CG + GCG` **exactly**, so
   `‖ΔC‖ ≤ ((1+γ)² − 1)‖C‖` with `γ = max_i |δg_i/g_i|`, and the same factor bounds every
   projection (`480bed76`, adopting this lane's 5.7). Composed with `|δg_i/g_i| ≤ θ/f_i`, this
   gives `γ ≤ θ / min_i f_i` — **so the correlation side is DERIVED from `θ`, not judged separately.**

   ⚠ **CONDITION (a) WAS DROPPED HERE AND IS RESTORED (§13.5).** I wrote *"the same factor bounds
   every projection"* without its condition. `PROPOSAL-20260916…:459-461` states it: *"The projected
   bound is relative to `‖P C_infl Pᵀ‖`, so it degrades if a declared projection nearly annihilates
   the inflated block. The draws above used non-negative contracting weights; a near-annihilating
   projection is not covered, and **the declared projection set has not been checked.**"* This is
   material, not decorative, and the `θ` recommendation's own §1.4 says why: `SPEC` requires the
   3D/4D covariances to be **exact projections**, and a projection contracts the full matrix — so it
   samples precisely the off-diagonal entries where `θ` has least grip. **The one use the bound
   exists for is the one whose condition has never been checked.** Checking the declared projection
   set against condition (a) is **zero compute** and is §12.5 item 4.

**RECOMMENDATION: qualify the existing unpinned products. Do not run the pinned experiment now.**
Because (a) route (i) is already falsified on these artifacts and cannot qualify them; (b) its
falsification branch is currently *ambiguous* with four `OMP_*` variables unrecorded, so even a
negative result would not be interpretable; (c) it needs new products and a production
authorization; and (d) the qualification route needs **no envelope claim, no new products, and one
measurement.**

### 12.5 The evidence the recommended route needs — and it is one measurement plus one declaration

| # | what | who | compute |
|---|---|---|---|
| 1 | **`f_i`, the V-fraction of each bin's variance.** Both `θ`'s scale *and* `θ`'s correlation grip reduce to this single quantity, and `min_i f_i` sets the derived bound: at `θ = 7.11e-2`, `min_f 1.0 → 15%`, `0.5 → 30%`, `0.2 → 84%`, `0.1 → 193%`, `0.01 → 6477%`. **Below `min_f ≈ 0.2` the derived bound exceeds 100% and settles nothing.** | `lane_b` measures, `[91eaa2]` interprets | **small, and it needs a writer change or a re-read** — see below |
| 2 | **An ACTIVE-SET POPULATION declaration.** `min_i f_i` over all 10,694 bins is an extreme-order statistic set by the single worst bin — by construction a bin where the unified throw contributes almost nothing, *"a bin whose covariance nobody uses"*. `480bed76`: the remedy is **an active-set restriction, NOT a tighter `θ`** — tightening `θ` below its scientific ceiling to rescue a bound set by a dead bin *"would be choosing a tolerance to obtain a verdict."* **The population is a declaration, and it is scientific.** | **Joseph**, or `[91eaa2]` under his ratification | zero |
| 3 | ⚠ **CORRECTED (§13.2): the status is UNASSESSED, not withheld, and the withholding is NOT `[cb0b6b]`'s.** Whether §7 item 4 is discharged by the throw-deviation and completeness results — which closes **full `S`** and settles premise 1 of §12.2 — has **never been routed to `[cb0b6b]` as an object**: `fb9fdec1`/`480bed76` (2026-09-17) postdate its last assessment `fdf5e510` (2026-09-15) by two days. `[91eaa2]` withholds a verdict on *its own* residue, which is a different act. Premise 1's conclusion is unchanged — **an unassessed residue supports non-bindingness no more than a withheld one does.** Routing it is Joseph's, and is not requested here. | Joseph routes; `owners.tsv:15` assesses | zero |

⚠ **`f_i` IS NOT COMPUTABLE FROM THE PRESERVED PRODUCTS — MEASURED, not assumed.** `z-cv.npz` holds
exactly seven arrays: `hCov_combined5d_total_uthrow (10694,10694)`, `hInflation_g (10694,)`,
`hPinnedMask`, `hXSecND_flat (65856,)`, `hSupportMask (65856,)`, `hRowIndex5D (10694,)`,
`metadata_json`. So `(C_Z)_ii` ✓ and `g_i` ✓ are preserved, and the **vertical-band block-sum
diagonal `(Σ_V C_b)_ii` is not** — the receipt digests `diag_c_blocksum` and `diag_c_unified_mean`
but persists no values. Two ways to close it, and **neither produces a new covariance product**:

- **(A) a writer requirement** — persist the five per-term diagonals in the build's output. Zero
  compute *now*, but `f_i` then exists only for a **future** build, not for these products.
- **(B) re-read the 13 vertical bands' diagonals** from the already-bound, unchanged support ROOT
  (`9f7b2f55…`, 41.44 GB; bands stored essentially uncompressed at ~0.91 GB each, so ~11.8 GB of
  reads). This yields `f_i` **for the products that exist**, which is what the recommended route
  needs. It is a diagnostic read of bound inputs, **not** a production run.

**(B) is the one to authorize if this route is chosen.** (A) is worth doing anyway so the question
never recurs, and it is `lane_b`'s.

### 12.6 Pricing — with ENFORCED caps, not historical elapsed

Arm 7's enforced cap is on its own directive line, `sbatch_uthrow_combine_5d_fast.sh:4`:
`--qos=shared --constraint=cpu --nodes=1 --ntasks=1 --cpus-per-task=16 --mem=90G
**--time=03:00:00**`. ⚠ **Scope: that LINE is byte-identical on `origin/main` and on this lane; the
FILES are not** — they differ by the Z-scoped requeue-refusal block, so the identity claim holds for
`:4` and must not be generalized to the launcher.

⚠ **CORRECTED (§13.4) — the numbers are right and my stated authority was wrong.** I wrote *"R5
meters wall-hours per execution attempt, **so** the declared maximum for one attempt is 3.00"*. That
does not follow: `r5_meter.py:73` charges *"sum of post-t0 **ElapsedRaw** over every execution
attempt"* — **actual** elapsed, which is why `1395/3600 = 0.3875` exactly. R5 would charge ~0.39–0.58
per attempt, not 3.00. The correct ground is the **reservation rule**, stated directly at
`SPEC:3140` — **"Reservation bound `3n` CPU task-h"** — and at `SPEC:1881-1883`, *"reservation bound
— 3 h per invocation at the launcher's own `--time=03:00:00` … bounds an attempt, not a completion
(§5.2's standing rule)"*. **Same numbers, correct authority.** Every figure below was checked by
running
`r5_meter.py check --receipt docs/orchestration/state/r5-meter-receipt.json --max-age-hours 24`
against the committed receipt:

| design | attempts | declared max, **enforced cap** | predeclaration's historical-elapsed figure | `r5_meter check` |
|---|---|---|---|---|
| Model A minimum | 3 | **9.00** | 1.73 | exit 0 |
| Model A + attribution | 4 | **12.00** | 2.31 | exit 0 |
| Model B, exclude `p ≥ 0.5` | 6 | **18.00** | 3.46 | exit 0 |
| Model B, exclude `p ≥ 0.1` | 30 | **90.00** | 17.29 | exit 0 |

**The enforced-cap price is 5.20× the predeclaration's** — ⚠ and that ratio compares a **reservation**
against an **expected actual**, not two estimates of one quantity. Likewise `9.00` is a reservation
while the `403.803889` headroom is computed from `ElapsedRaw`: different quantities, deliberately
mismatched in the conservative direction, which is what makes the comparison safe for an **admission
check** and wrong for a spend forecast. Its §2.1/§2.2 figures are derived from
three historical elapsed measurements (`0.3875 / 0.4239 / 0.5764`), which Joseph ruled out as a
pricing basis; its own §4 residue 5 already flags them as transferred. All four designs **admit**
under R5 — headroom is **403.803889** of 500 and 9.00 is 2.23% of it — **so R5 is not what makes
route (i) expensive; the falsified estimator and the missing transfer argument are.**

⚠ **The receipt goes stale at 2026-09-18T07:41:55Z** (measured `2026-09-17T07:41:55.528431Z`, 24-hour
rule). Any eventual request must re-measure first, or `check` exits **4, "receipt is stale"** — the
gate that was closed for six days without being noticed (§5).

### 12.7 The decision that is actually open

**Not** a request to recreate any declaration. `78a8c2ee`'s items 4 and 5 stand as written, and
nothing below asks for them again.

| | **ALTERNATIVE 1 — qualify the existing products (RECOMMENDED)** | **ALTERNATIVE 2 — establish the changed configuration** | **ALTERNATIVE 3 — wait** |
|---|---|---|---|
| **what you authorize** | (B): a diagnostic re-read of the 13 vertical bands from the bound support ROOT to measure `f_i`; **plus** the active-set population declaration | route (i)'s `n = 3` or `n = 4` pinned arm-7 runs, **after** the four `OMP_*` variables are pinned or receipt-captured, **and** after the §6.4 ruling on using Z's own bank | nothing; `[cb0b6b]` clears the withheld verdict first |
| **enforced-cap cost** | one short diagnostic attempt; **no new covariance product** | **9.00** (n=3) or **12.00** (n=4) CPU task-h, plus new products from the 89.11 GB chain | zero |
| **what it would establish** | a bound on the **consequence** of the recorded deviation for the declared use, propagating through inflation and every projection by the same `((1+γ)²−1)` factor | `B = 0` as a design property of a **pinned** configuration — or `B` UNDEFINED and route (i) falsified | nothing new; it removes premise 1 of §12.2 |
| **what it would NOT establish** | any bound over an execution **envelope**; `B`; `ε`; adoption | **anything about the existing products**, absent a transfer argument that does not exist; and **not `ε`** either, by the predeclaration's own §1.4 | — |
| **main risk** | `min_i f_i` may come back below ≈0.2 and the bound settles nothing — in which case the **active set**, not `θ`, is the lever | its falsification branch is **ambiguous** today, so a negative result is uninterpretable; and it consumes a production authorization for a control | the 2026-09-30 stop date is **13 days** away and item 2 gates everything downstream |

**The decision: which route, and — if Alternative 1 — the active-set population.** Those are the
only two things that cannot be prepared without you. Everything else in §12.5 is owned and
zero-compute.

**Recommended: Alternative 1**, on the ground that route (i) is already falsified on the artifacts
in hand, cannot be transferred to them, and would spend a production authorization to answer a
question about a configuration that has never produced a product — while the qualification route
needs no envelope claim, no new products, and one measurement whose two closure paths are both
identified.

**Nothing here is adopted, graded or projected. `B`, `S` and `ε` remain open, full `S` included. No
compute is authorized or requested by this section.**

---

## 13. Independent assessment of §12, and the revised decision (2026-09-17)

**Assessment record: `ed18a231de4c3b6b016e268be54257579b6c7739`,
`docs/orchestration/ASSESSMENT-20260917-decision-support-section-12.md`, on
`origin/lane/z-criteria-independent-assessment-20260910`, by `owners.tsv:15`
`z-independent-assessor [cb0b6b]`.** Requested by Joseph. **It closes nothing:** full `S` stays
OPEN, §7 item 4 UNASSESSED, `θ` RECOMMENDED NOT ADOPTED, A1 OPEN, Gate 2 FAIL.

**CONFIRMED: §12.1, §12.2 premise 1, §12.2 premise 3, §12.4's measurement, §12.4b, §12.5's `f_i`
finding and decomposition, and every number in §12.6.** The assessor read no cluster artifact, so
its restatements of my `z-null.npz` / `z-cv.npz` figures are **relayed**; the cluster measurements
are mine, and I separately verified that all **13** vertical bands resolve from the single bound
support ROOT `9f7b2f55d7581bb687e214e7f5a38235fd07b6d9522c2223fa3a3395c803c92a`
(41,436,632,945 B, 40 `hCov_universe5d_*` objects; the 5 lateral come from `active`, and
40 + 5 = 45 = `band_inventory`). **I verified each of its five grounds against the sources rather
than accepting them on relay**, including that its `Z_REPRO_KNOBS:127-138` citation is a *symbol*,
not a file — the symbol is at `fb9ec356:nd-unfolding/z_reproducibility.py:127-138` and the line
numbers and quotation are exact.

### 13.1 The fallback is UNRULED, not barred — and ONE ruling governs THREE things

Withdrawing "`S` is non-binding" withdraws the **composition**, and §2.4 says so in its own words at
`:238`: *"neither clause bars it alone … §C.2 alone bars nothing; `:1410` alone bars only the direct
reading."* So the fallback moves **BARRED → UNRULED**. ⚠ **Unruled is not admissible.** Its only
remaining candidate ground is the **§6.4 subject question**, and `SPEC:3140`, `SPEC:1830`,
`78a8c2ee` residue 2 and §12.1 all route it to Joseph and all decline to issue it.

**§12 treated three things as independent. They are one question:**

| governed by the single §6.4 ruling | §12's earlier status |
|---|---|
| the `B`-from-precursor-executions fallback | "BARRED by composition" — now **UNRULED** |
| **route (ii)**, a standalone control on Z's bank | "GATED" |
| **route (i)'s own control**, because arm-7 runs would execute on Z's bank too | treated as unaffected — **wrong** |

**Every withdrawal site is repaired in this change, not just the ones §12.2 named** — the §2.4
heading, its route-(iii) row, its fallback row, its body paragraph, §10's restatement, and §12.1's
quotation of the phrase. A partial repair makes the disagreement count go *up*.

### 13.2 UNASSESSED, not WITHHELD — and the withholding was not the assessor's

§12.5 item 3 said *"`[cb0b6b]`'s withheld verdict"*. **It withheld none.** `fb9fdec1` and `480bed76`
(2026-09-17) postdate its last assessment `fdf5e510` (2026-09-15) by two days and **have never been
routed to it as an object**. `[91eaa2]` withholds a verdict on *its own* residue — a different act by
a different owner. The correct label is **UNASSESSED**, which is `SPEC:1744-1751`'s distinction
between a statement about evidence and a statement about the world. **Premise 1 is unchanged and
safer under the correct label: an unassessed residue supports non-bindingness no more than a
withheld one does.** Routing it is Joseph's and is not requested here.

### 13.3 The one refuted generalization

§12.4 consequence 2 is **withdrawn in full** (see the marker there). Two errors, both mine:

- **"allocation shape … is the only thing route (i) pins" is false.** Route (i)'s pin set is
  **estimator parameters** — `deterministic`, `force_row_wise`, `num_threads` — and `num_threads`'
  own rationale states that `OMP_NUM_THREADS` is **ignored by LightGBM**. Allocation shape is what
  item 5's coverage objective **varies**, not what route (i) pins. All three knobs were free in
  these executions, so **the observed non-identity IS attributable to variables route (i) would
  pin**, and my a-fortiori step required the pair to have been pinned.
- **"route (i) is FALSIFIED" applies the consequent outside the antecedent.** Route (i) claims
  *pinning* delivers `B = 0`. Finding non-identity in an **unpinned** pair **confirms its motivating
  premise.** The defensible sentence is the one now in consequence 1.

**The recommendation survives.** Grounds (b), (c) and (d) are independent of this, and ground (a)'s
operative half — *the estimator cannot yield `B` for these products* — is confirmed via §12.4b.

### 13.4 Pricing: authority corrected, and Alternative 1 now carries a cap

The numbers stand; the authority was wrong. `r5_meter.py:73` charges **actual `ElapsedRaw`**, not a
reservation, so "R5 meters wall per attempt" does not imply a 3.00 declaration. The authority is
`SPEC:3140`'s **"Reservation bound `3n` CPU task-h"** and `SPEC:1881-1883`/§5.2's *"a request bounds
an attempt, not a completion."* Both are now cited at §12.6, together with the point that a
reservation and an `ElapsedRaw`-derived headroom are **different quantities** — mismatched in the
conservative direction, which is why the comparison is sound for an admission check and unsound as a
spend forecast.

**And the rule had not reached the route I recommend.** §12.7 priced Alternative 1 as "one short
diagnostic attempt" with no figure. Priced properly: the eventual request declares a `--time`, and
**that** is the reservation. A `--time=01:00:00`, `n = 1` request is **1.00 CPU task-hour** —
**0.248%** of the 403.803889 headroom. Basis for believing it ample, stated as an expectation and
never as the bound: the pilot itself read all **45** bands *and* wrote two 0.91 GB products in
`build_seconds 760.767` / 1037 s wall under a 5400 s cap, and 13 band **diagonals** are a strict
subset of that I/O. `--mem` must be declared too; the pilot's measured `MaxRSS` of **49.73 GiB** was
for holding full `10694²` accumulators, which a diagonal read does not.

### 13.5 §12.5 gains a fourth item — zero compute

4. **Check the declared projection set against §5.7 condition (a).** The condition — *"a
   near-annihilating projection is not covered, and the declared projection set has not been
   checked"* — was dropped at every site that used the result, including §12.4. It is the condition
   on the one use the bound exists for. **Zero compute. Owner: `[91eaa2]` to state, `[cb0b6b]` to
   assess.**

### 13.6 ⚠ THE SCOPE REPAIR I APPLIED TO `S` AND FAILED TO CARRY DOWN TO `θ`

`RECOMMENDATION-20260916-theta-per-bin-uncertainty-tolerance.md:177-200`, verified verbatim:
`θ_A = 7.11e-2` is **`1.60e12` ×** the observed null; `θ` *"should be declared as a SCIENTIFIC
CEILING and explicitly NOT as the operative determinism gate"*; it is *"`S`'s per-bin shadow, and it
is non-binding for the same reason"*; and — decisively — *"if `θ` is recorded as the gate, the
per-bin leg **repeats the vacuity defect that `S` already demonstrated**."*

**§12 applied exactly that repair to `S` one level up and did not carry it down one level.**
§12.5's `min_f → 15% / 30% / 84% / 193% / 6477%` table is the worst case **of a ceiling**, while
§12.7 named Alternative 1's deliverable *"a bound on the consequence of the **recorded**
deviation"* — **a different operand, twelve orders away.** So:

- **Alternative 1's operand is the RECORDED deviation**, i.e. `γ` derived from the measured CV
  movement (`max_i|Δ_i/x_i| = 1.7552716191735518e-12`, `r_null = 4.4520002137582904e-14`), **not
  `θ/min_i f_i`.**
- **The `min_i f_i` cliff is therefore a property of the CEILING computation, not of Alternative
  1's deliverable**, and §12.7's stated risk was the ceiling's risk. ⚠ **No number is asserted for
  the recorded-deviation bound here:** the map from the recorded CV deviation to `δg` is **not
  established**, and that map is precisely the remaining work. Claiming it comes out small without
  the chain would be the mechanism-without-a-command failure.
- **`θ` is still needed — to GRADE the result, not to compute it.** Without an adopted `θ`, a
  measured consequence is a number graded against nothing, which is §6's whole point.
- **One further consequence of `θ`'s bracket:** `min_i|ρ_i| ≤ r_null ≤ max_i|ρ_i|` is correct, but
  **on these products the lower leg is exactly vacuous** — 11 support bins agree bitwise, so
  `min_i|ρ_i| = 0` identically and only the upper leg carries information.

### 13.7 THE REVISED DECISION — `θ` is blocking, not the population

| | **1 — qualify the existing products (still RECOMMENDED)** | **2 — establish the changed configuration** |
|---|---|---|
| **the blocking decision** | **`θ`.** It is **RECOMMENDED, NOT ADOPTED** (`480bed76:12`), and its own `:4` records it routed *"for independent assessment by `owners.tsv:15` `[cb0b6b]` and then his decision"*. Alternative 1's whole output is graded in `θ`. ⚠ **UPDATE 2026-09-17: Joseph has ISSUED that routing** under the existing review authorization — see §14. The assessment is **in progress**; `θ` remains **RECOMMENDED, NOT ADOPTED** and no result is recorded here. | **the §6.4 subject ruling** — and per §13.1 it governs **three** things, so **Alternative 2 cannot even be specified until it is issued.** |
| **then, and only then** | the **active-set population** declaration — which matters once `min_i f_i` is in hand **and** a `θ` is adopted. **Downstream, not blocking.** | the four `OMP_*` variables pinned or receipt-captured, else the falsification branch stays ambiguous |
| **reservation** | **1.00** CPU task-h at a declared `--time=01:00:00`, `n = 1`; **0.248%** of headroom; **no covariance product** | **9.00** (`n=3`) / **12.00** (`n=4`) CPU task-h, plus new products from the 89.11 GB chain |
| **would establish** | a bound on the consequence of the **recorded** deviation, propagating through inflation and — **subject to §5.7 condition (a), unchecked** — every projection | `B = 0` for a **pinned** configuration; **or** `B` UNDEFINED |
| **would NOT establish** | any envelope bound; `B`; `ε`; adoption | **anything about the existing products** — no transfer argument exists, measured at §12.4b | 

**Reject condition 11, which §12 understated.** I quoted `4c` alone. `null.assessment` records
`reject_conditions ["4c", "11"]`, and `SPEC:1267` condition 11 is the one that names the missing `ε`
directly: *"The fixed-seed null key is **absent**, or its bound is not the scale-relative one **§6.4**
rules."* So condition 11 points at the same §6.4 ruling as §13.1 — **one ruling sits under the
fallback, route (i), route (ii) and reject condition 11.**

**Nothing here is adopted, graded or projected. `θ` is RECOMMENDED NOT ADOPTED; full `S` is OPEN;
§7 item 4 is UNASSESSED; `B` and `ε` are open; Gate 2 is FAIL. No compute is authorized or
requested.**

---

## 14. The `θ` assessment, routed 2026-09-17

Joseph issued the routing §13.7 identified as the missing precondition, stating that **no further
permission turn is needed merely to route those documents.** Subjects, by full identity:

| subject | identity | author |
|---|---|---|
| the `θ` recommendation, **narrowed** form (294 lines) | `480bed76f9cef73b66bc1bb0bd471847d5f61ce2` on `lane/z-criteria-recommendation-20260910` | `owners.tsv:14` `[91eaa2]` |
| its predecessor, for the narrowing delta | `fb9fdec11c653d34c5f2ee16f9f68f6be837e6d8` | same |
| the supporting propagation argument, §5.7 and §5.8 | `affc9e03119230ece17f977325d8a1ba00d68827` on `lane/z-assembly-pilot-20260914` | this lane |

Assessor: `owners.tsv:15` `z-independent-assessor [cb0b6b]`. **Independence checked, not assumed** —
its standing partial recusal at `068436e5eca3f0b85e506eb8203d97b90b751695` is scoped to the
campaign-completion ordering choice in `require_campaign_complete` and does not reach `θ`,
propagation, or `B`/`S`/`ε`.

**The five bounded questions**, as Joseph set them:

1. **Is the proposed `θ` scientifically justified?** Specifically the §2.2 claim that *"a CV movement
   that changes `σ` by less than `σ`'s own sampling error cannot change any conclusion"*; the
   statistical assumptions behind `√(2/(N−1))` and the "half that on `σ`" step, given that
   `C_stat`'s `N = 100` are **bootstrap replicas** and `C_ML`'s `N = 24` are **seed-scan splits**;
   and the transfer from individual blocks to the **total**, which §2.3 already concedes lies in
   `(0, 14.74%]` and depends on `f_i`.
2. **Are the propagation bounds valid for FINITE changes?** `ΔC_infl = ΓC + CΓ + ΓCΓ` is asserted
   exact, and the norm bound follows for finite `Γ` — but `dσ_i/σ_i = f_i·(dg_i/g_i)` is called
   *"exactly"* on a measurement at `dg/g = 1e-6`, where first order and exact are
   indistinguishable, and is then **inverted** to `|dg_i/g_i| ≤ θ/f_i` at `θ = 7.11e-2`.
   **The differential identity must not silently become a finite-change bound.** In scope with it:
   **deadband crossings** — and note **4166 of 10694** bins sit in the deadband (`G3R`'s
   `n_saturated_v_uni_below_v_blk`), which is the population `min_i f_i` is taken over — and the
   **declared projections**, where §5.7(a) and §5.8(3) both record that the bound has never been
   evaluated against the actual declared set.
3. **Does Alternative 1 establish only sensitivity to the recorded CV difference, or something
   sufficient for the intended scientific qualification?** Limits stated explicitly, and the claim
   being qualified named.
4. **Which existing `B`/`S`/`ε` requirements would remain, and what exact amendment or ruling would
   replace any of them?** ⚠ **Adoption of `θ` is not that amendment** — Joseph's words. `θ` is a
   per-bin `σ` tolerance; `ε` is a tolerance on `r_null`.
5. **Define the scientific population and projection set from intended use.** ⚠ **Bins may not be
   excluded after an unfavourable bound is seen, merely to obtain a passing result.** This rules on
   `480bed76`'s own proposed active-set restriction: the population must be declared
   **prospectively**, not selected once the bound is known.

**Constraints carried to the assessor:** no compute; no `θ` adoption; no scientific grading; no
replacement of the null criterion; `B`'s declarations not to be recreated; the completed pilot not
to be repeated; no general review. The assessor was also asked to **distinguish source-inspection
findings from relayed cluster measurements**, and was given this lane's cluster figures explicitly
labelled as relayed.

**No result is recorded in this section.** `θ` is **RECOMMENDED, NOT ADOPTED**; full `S` is OPEN;
§7 item 4 is UNASSESSED; `B` and `ε` are open; Gate 2 is FAIL.

# DECISION SUPPORT 2026-09-16 — from Z's outputs to an adopted 5D covariance

## CITABLE FOR / NOT CITABLE FOR — read before quoting anything below

**CITABLE FOR:** the state of each remaining requirement as measured on 2026-09-16; the routing of
each; the reconciliation in §3; and the resource figures in §4 and §5.

**NOT CITABLE FOR:** any scientific grade. Any acceptance boundary. Any adoption. Any claim that a
Z covariance exists — **none has ever been constructed.** The authorization that admitted this
record states explicitly that it **does not ratify the proposed scientific criteria** recorded
here. `ε = 1e-9` is **PROPOSED and UNGRADED**; `S`'s discharge is **F7-channel only**; **A1 is
OPEN**. Gate 2 remains **FAIL**. `cause3_corr` remains **WITHHELD**. Endpoint B remains
**DEFERRED NOT PASSED**.

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

**Route (i) — "pin the envelope in code" — cannot be claimed today.** Exactly **one launcher of
eleven** pins a literal `OMP_NUM_THREADS`, and it is **not arm 7**, which is where the null
operands are computed.

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

1. **`B`'s justification** — accountability assigned 2026-09-16 (§2.3). Gates A1, which gates
   `(3,Z) M(i)`, a REQUIRED cell. Preparation costs no compute.
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

# Independent review: the precursor delta `8111a951` → `10eb1bac`, and four relayed claims

**Owner of this record:** `lane/z-criteria-independent-assessment-20260910` (independent assessor).
**Role:** requirements and verdicts only. No remedies supplied, by standing arrangement — see
`offering-a-remedy-spends-my-next-verdict`. Nothing here adopts a criterion, grades a leg, moves a
gate, authorizes spend, or submits anything. `R4` remains suspended; Gate 2 remains FAIL.

**CITABLE FOR:** the coverage statement below; the delta verdict at the named sha; the re-measured
values in Part B, each with its command's population named.
**NOT CITABLE FOR:** any launch authorization, any grade of Z's legs, any `--time` value, any
adoption of the bank, or any claim that the residual defect in `sbatch_uthrow_block_5d.sh` is
repaired.

---

## Part 0 — Coverage, stated explicitly because I was asked to state it

`REVIEW-20260911-precursor-repairs-against-P1-P18.md` @ `a51c6503` took as its subject
`lane/z-precursor-repairs-bg-20260911` @ **`8111a951`**. It **did not cover** the delta.

**This record extends coverage to `10eb1bac233333584f2f60f11f551b89a1807e7d`** and to nothing
beyond it. The `P1`-`P18` verdict is unchanged by the delta: still every criterion MET, still with
the finding that the admission accounting REFUSES the run at `558.42` against `500`.

Delta re-measured, not accepted — `git diff --stat 8111a951 10eb1bac`: **one commit, 4 files,
+218/−3**, matching the relay exactly. `git merge-base --is-ancestor 8111a951 10eb1bac` → true, so
this is an extension and not a rewrite. Per-file: `sbatch_uthrow_block_5d.sh` +39,
`tests/test_z_precursor.py` +114, `z_precursor.py` +26, `z_precursor_admission.py` +42.

Two of the four are executable modules and `METER_PRIVATE_DEPENDENCIES` is a *checked* constant, so
the relay's own framing is right: this is behaviour, not commentary, and it needed covering.

---

## Part A — The delta

### A.1 FINDING (the one that matters): the new marker re-states a reason the same file withdraws

`sbatch_uthrow_block_5d.sh:33-35`, added by this delta, says:

> Repointing the `else` literal would change where an ARCHIVE reproduction writes, with a
> destructive edge on receipt-bound slabs; that is a different subject with its own blast radius and
> its own authorization.

The same file, at `:350-353`, pre-existing and **not** part of this delta, says:

> THE UNSET PATH IS DELIBERATELY LEFT ON THE NON-`_sb` LITERAL, and my earlier reason for that was
> WRONG. I said repointing it would move archive behaviour. **It would not — the archive IS `_sb`.**
> What it would actually do is let a NON-SCAN run write INTO THE LIVE ARCHIVE DIRECTORY, a
> destructive edge on 124 receipt-bound slabs. Right action, wrong reason, and the real reason is
> worse than the one I gave.

**The clause the delta adds is the withdrawn clause, with the correct consequence bolted onto it.**
The two reasons are not variants; they point in opposite directions:

| | where the archive is | what repointing does | what the repair must protect |
|---|---|---|---|
| withdrawn (`:33-35`, and `:364-365`) | at `block_slabs_5d` | moves the archive's write location | the archive's location |
| true (`:350-353`) | at **`_sb`** | lets an undeclared run write **into** the archive | `_sb` against undeclared writers |

**Why this is load-bearing rather than editorial.** This marker is, by its own text, the document
that routes the decision: *"Its repair needs Joseph's authorization."* A reader who takes `:33-35`
at face value concludes the archive sits at the current literal and that the prudent act is to
leave the literal alone. The real constraint is the reverse — the archive is `_sb`, and repointing
the unset literal *to* `_sb` is what creates the destructive edge. Those two readings license
different repairs, and the marker is positioned 317 lines above the correction that refutes it, in
the section a reader is told to read *first* (`READ BEFORE THE `if` AT :382`).

This is `a-withdrawal-must-reach-every-site-that-states-the-rule` with the aggravating feature that
the new site was written *after* the withdrawal and re-originates it. `:364-365` already carried the
half-corrected form — the withdrawn framing with the right hazard in parentheses — so the delta
propagated the weaker of two available sentences that were both already in the file.

**Requirement (not a remedy): the top marker's "WHY IT IS NOT REPAIRED HERE" must state the
`:350-353` reason, and a reader must not be able to reach `:33-35` and form the withdrawn belief.**
Which sentence achieves that is the author's call, not mine.

### A.2 The residual marker otherwise satisfies the condition I set, and its populations are correct

My `P1`-`P18` verdict made the marker's presence *on the launcher itself* a condition, on the
ground that the general launcher's next user will not have read the Z review. Confirmed at
`:11-49`: `CITABLE FOR` / `NOT CITABLE FOR` at the top, the mismatch's direction named
(`block_slabs_5d` written, `block_slabs_5d_sb` read unconditionally), the defect owner explicitly
**unassigned** pending Joseph with the record owner named as the lane, and the closing instruction
to check which namespace your combine reads. The `WHY THE Z PRECURSOR IS UNAFFECTED` paragraph is
accurate: the precursor requires `MNV_Z_PRECURSOR_NS`, which has no default.

**Populations re-measured on the cluster, 2026-09-11, and they are exactly right:**

```
block_slabs_5d      ls -1 = 18    block5d_*.npz = 8     knob_*.log = 10      (8 + 10 = 18)
block_slabs_5d_sb   ls -1 = 41    block5d_*.npz = 36    knob_*.log =  0
```

**One correction to the relay's gloss, not to the marker.** The marker says `ls` over-counts
"because it counts the `knob_*.log` files too" — true of `block_slabs_5d` (10 logs) and **not** of
`block_slabs_5d_sb`, which has **zero** `knob_*.log`; its 5 extra entries are `tail_u95.log` …
`tail_u99.log`. The marker's own numbers (8, 36) are the product-glob numbers and are correct; only
the *explanation* of the `ls` gap generalises wrongly across the two directories.

### A.3 The `:353` figure of "124 receipt-bound slabs" does not reconcile with the tree

Not in this delta, but **cited by it** (`:33-35` inherits the hazard), so it is in scope for a
reader of the marker. Measured: `block_slabs_5d_sb` 36 `.npz` + `uthrow_slabs_5d_sb` 40 `.npz` =
**76**, not 124. Across **all seven** `uq_5d/*slab*` directories the total is 271. So 124 is
neither the `_sb` pair nor the whole population. Either the figure is stale or its population is
something I have not identified; I am not asserting which. **Requirement: the blast-radius figure a
repair authorization rests on must name its own population, because this one cannot be reproduced
from either the obvious narrow or the obvious wide reading.**

### A.4 CONFIRMED: the private-surface declaration, measured independently

I wrote my own AST sweep rather than running theirs. Over `10eb1bac`:

| | private `r5_meter.<attr>` in **executable** code | public |
|---|---|---|
| `z_precursor_admission.py` | **1** — `_parse_sacct_dump` | 6 |
| `tests/test_z_precursor.py` | **2** — `_calculate_spend`, `_parse_sacct_dump` | 2 |

`METER_PRIVATE_DEPENDENCIES` and `METER_PRIVATE_DEPENDENCIES_IN_TESTS` match those sets exactly.
**The relay's substantive claim is confirmed: this is one private name, not a broad private
dependency.** My earlier durability note stands as a note and is not a defect.

Two arithmetic corrections, neither material:
- The docstring-only meter names number **four**, not three: `_calculate_spend`, `_parse_sacct_start`,
  `_read_source`, and **`_sacct_argv`**.
- My naive text regex finds **12** `_`-prefixed tokens, not 11. The "8 private-ish names in
  executable code" reproduces exactly once dunders are excluded (11 with `__doc__`, `__file__`,
  `__name__`).

The equality arm earning its keep is confirmed from the record itself: the declaration states it was
incomplete on first write (`_calculate_spend` declared, `_parse_sacct_dump` missed) and the
both-directions arm caught it. That is the argument for the arm, made by its own history.

### A.5 The declaration's two residuals — requirements, not defects today

**(a) The positive control re-types the detector it is controlling.** The equality arm defines
`private_meter_attrs` as a closure inside the test method; `test_the_private_surface_detector_
CATCHES_an_undeclared_name` then re-types the same comprehension inline over
`"x = r5_meter._brand_new_private(1)"`. A detector blind to a spelling would be confirmed blind by
its own control — `a-fixture-derived-from-the-rule-cannot-disagree-with-it`.

**Measured, so this is a durability requirement and not a live hole:** both modules reach the meter
only through `import r5_meter` plus attribute access. `getattr(r5_meter, …)`, `from r5_meter import
…`, an alias rebinding, and `sys.modules["r5_meter"]` are **all absent** from both files. So the
declared sets are complete *today*. **Requirement: the control must exercise the same callable the
equality arm uses, and the spellings the sweep cannot see must either be covered or named as
excluded** — because the declaration's stated purpose is that a *future* widening fails loudly, and
two of those spellings would widen it silently.

**(b) `hasattr` catches removal and rename, not semantic drift.** `_parse_sacct_dump` keeping its
name while changing its attempt-identity rule, its t0 clip, or its step/bracket exclusions passes
every arm. The declaration does not overclaim — it says a refactor that *removes* one fails — so
this is a scope statement. The suite already re-measures `_calculate_spend`'s contract (the
`COMPLETED 3600 + RUNNING 7200 + PENDING → 3.0 h, 2 attempts` fixture). **Requirement: state
whether `_parse_sacct_dump` has an equivalent contract arm, or record that its semantics are
uncovered.** A private dependency's realistic failure is drift, not deletion.

**(c) Minor.** In the `hasattr` loop, the tuple's first element `module` is bound, never used, and
`del module`-ed inside the loop body. Dead after a refactor; both arms check the same object.

### A.6 CONFIRMED BY EXECUTION: the P12 lean table is exactly right

The delta documents a disagreement I found and were asked to pin. I re-executed both sides at
`10eb1bac` rather than reading the table:

| `MNV_EST_SEED_OFFSET` | `check_no_member_axis` | shell `mr_declared` | |
|---|---|---|---|
| unset | PASSES | undeclared | agree |
| `"0"` | REFUSES (`PrecursorError`) | declared | agree |
| `"7"` | REFUSES (`PrecursorError`) | declared | agree |
| `""` (set, empty) | **REFUSES** | **undeclared** | **DISAGREE** |

`lib_member_resume.sh:230` is `mr_declared() { [[ -n "${MNV_EST_SEED_OFFSET:-}" ]]; }` — verified by
sourcing and calling it, not by reading it. The documented lean is correct in both fact and
direction: the Python guard is **strictly stricter** on the exported-but-empty case, which trades a
false refusal for a silent relocation into `mii/`, and that is the safe direction. The `DO NOT "FIX"
THIS BY SWITCHING TO NON-EMPTINESS` warning is well-placed.

### A.7 Regression: the item I left open at `a51c6503` is now closed, with a matched control

At `a51c6503` I recorded the `14 / 2997 / 6` counts as **not verified** and told the relay to treat
the 14-name identity as its claim, not my finding. **It is now my finding.** Run in two isolated
detached worktrees, same command, same private `TMPDIR` each:

`python3 -m pytest tests -q -p no:cacheprovider --tb=no -rfE --continue-on-collection-errors`

| sha | failed | passed | skipped | collection errors |
|---|---|---|---|---|
| `77a4af38` (main, control) | 14 | 2895 | 6 | 1 |
| `10eb1bac` (tip) | 14 | **3001** | 6 | 1 |

- The failure-and-error set is **identical**: 15 entries, `comm` shows **zero** only-in-tip and
  **zero** only-in-control. The lane introduces no failure and fixes none.
- `3001 − 2895 = +106`, exactly the 106 tests `test_z_precursor.py` defines at `10eb1bac` (102 at
  `8111a951`, which is precisely the relayed `2997`). So the relayed counts were right.
- **Zero** failures in `z_precursor`.
- The one collection ERROR, `tests/test_z_build.py — ValueError: ROOT.__spec__ is None`, is present
  **identically on main**. Pre-existing and environmental: a sibling suite installs a `ROOT` stub in
  `sys.modules`, so `importlib.util.find_spec("ROOT")` at that module's scope raises instead of
  returning `None`. Off the cluster, plain `pytest tests` **aborts the whole directory** on it
  (`rc=2`, zero tests run) — the `--continue-on-collection-errors` flag is load-bearing for anyone
  reproducing these numbers.

**Withdrawn from my own record:** at `a51c6503` I reported `Ran 2531 tests … failures=10, errors=5`
from `unittest discover` and read it as a discrepancy against the relayed `2997`. It is not a
discrepancy: those are **two runners over two collections**, and `14 failed / 2997 passed / 6
skipped` is pytest's summary format, not unittest's. Comparing them was
`my-recurring-failure-is-asymmetric-comparison` — I had both numbers and no shared population.

---

## Part B — Four relayed claims, re-measured

### B.1 The observed-maxima table: the MAX column is CONFIRMED and population-robust

`sacct` read in monthly windows (a single unbounded window is refused: *"Too wide of a date range in
query"*), `TZ=UTC`, `-X`, four job names, 2026-05-01 → 2026-10-01. 239 allocation rows.

| arm | claimed MAX h | my MAX h | max `ElapsedRaw` s | `--time` | ratio |
|---|---|---|---|---|---|
| `uthrow5d_block` | 8.6389 | **8.6389** | 31100 | 12:00 | **1.39×** |
| `uthrow5d_runF` | 2.6708 | **2.6708** | 9615 | 6:00 | 2.25× |
| `uthrow5d_dump` | 0.2306 | **0.2306** | 830 | 6:00 | 26.0× |
| `uthrow5d_combF` | 0.5764 | **0.5764** | 2075 | 3:00 | 5.2× |

Every maximum reproduces to four decimals, and — the part that makes it usable — **it reproduces
identically over all three candidate populations** (all states; COMPLETED only; COMPLETED+FAILED).
So **the correction to Joseph is right: the block arm's 12 h is 1.39× its observed maximum, not
padding against a 1.12 h job, and the wall-kill path is live at realistic limits.** The consequent
requirement is right too: a `--time` proposal must come from observed maxima, not from making 543
fit under 500.

**The `n` and `mean` columns do not reconcile and I cannot source them.** My per-arm counts:

```
block : 72 COMPLETED + 5 FAILED + 6 CANCELLED = 83     (claimed n=74)
runF  : 137 COMPLETED + 3 FAILED + 6 CANCELLED = 146   (claimed n=129)
dump  : 8 COMPLETED = 8                                 (claimed n=8   -- agrees)
combF : 2 COMPLETED = 2                                 (claimed n=2   -- agrees)
```

74 is neither 72 nor 83; 129 is neither 137 nor 146. The claimed means (1.1213, 0.8824) likewise sit
between my COMPLETED and all-states means. **Requirement: state the state filter and window, or
drop the `n`/`mean` columns.** This does not touch the conclusion, because the maxima are invariant
across every population I tried — but an unnamed population is how a table becomes uncitable later.

### B.2 CONTRADICTED: `MaxRSS` is **not** empty. Peak memory is measured for all four arms.

This is the one place I think the relay is wrong in a way that changes a decision.

**`MaxRSS` is a step-level field. `-X` returns allocation rows only, where it is empty by
construction.** Same four names, same windows, same account, one flag different:

```
sacct -X   : 239 rows, non-empty MaxRSS =   0
sacct      : 651 rows, non-empty MaxRSS = 206
```

Joining step rows to arms by base JobID:

| arm | step rows with `MaxRSS` | min GiB | median | **MAX GiB** | `ReqMem` |
|---|---|---|---|---|---|
| `uthrow5d_block` | 69 | 0.00 | 15.45 | **16.35** | 80–110 G |
| `uthrow5d_runF` | 127 | 0.10 | 28.85 | **30.08** | 80–110 G |
| `uthrow5d_dump` | 8 | 23.08 | 35.97 | **47.98** | 80–110 G |
| `uthrow5d_combF` | 2 | 16.06 | 16.42 | **16.42** | 80–110 G |

`ReqMem` over the 239 allocation rows takes exactly three values: `80G`, `90G`, `110G`.

**So the probe's stated justification — "peak memory is unmeasured everywhere, and that gap is the
probe's actual justification" — is void.** There are 206 historical observations across all four
arms and all history. The largest peak anywhere is ~48 GiB on the dump arm against ≥80 G requested.

**And this dissolves the question I was asked** (*can a single task establish anything about memory,
given that probe runtime is not a guaranteed upper bound?*). It does not need answering in that
form, because `n=1` is no longer the best available evidence — 206 observations are. On the general
point my answer would have been: a single task's peak RSS is a **lower** bound on the requirement
exactly as runtime is, so Joseph's caution transfers intact; what makes it worse for memory is that
a peak is a max over the run, so an unobserved input distribution shifts it without warning. But the
dispersion is now measurable rather than arguable, and it differs sharply by arm — `block` and `runF`
are tight at the top (median within 6% of max), while `dump` spans 23–48 GiB, a **2.1× spread over
8 tasks**. The dump arm is the one where a single observation would have been least informative.

**One trap for whoever aggregates this: `MaxRSS` units are mixed.** I observed `K`, `M`, **and an
empty suffix** in the same column (`34724532K` and `31838.50M` on sibling tasks of one array). A
parser that assumes one unit silently mis-scales by 1024.

### B.3 The bank recommendation is NOT thin. It is stronger than argued, and I closed the gap in it.

Verified against `unified_throw_cov._load_bank`'s own demands, read from source at the review tip
rather than from the relay's summary:

- `cv.npz` loads; 22 keys; `nedges = 5`; per-axis bins `[14, 16, 7, 7, 6]`, product **65856** =
  `p4_lib.py:22 GRID_NBINS` (whose own comment reads `14*16*7*7*6`). `MCgen` present, shape
  `(32849103, 5)`.
- **72 demanded knob files, 0 missing** — enumerated as `_load_bank` enumerates them (12 bands × idx
  ∈ {0,1} × 3 stems), not counted.
- Flux: `sig_flux_t_`, `sig_flux_r_`, `td_flux_` each exactly **100** ids, min 0, max 99 — which is
  what `_load_bank` demands (`flux_sets[0] == flux_sets[1] == flux_sets[2] == set(range(100))`).
- 374 entries, 26 G. The single entry `_load_bank` does not demand is `flux_univ_ratio.npy`.
- Provenance: `55286192_0..7`, `uthrow5d_dump`, **8/8 COMPLETED**.

**I agree that contents verified against the consumer's demands beat provenance here**, and the
inability to date the launcher text does not weaken it, for a reason worth stating: `_load_bank` is
a *refusing* loader, so a bank that satisfies it cannot be a partial or mismatched bank whatever
produced it. That is a property of the artifact, not of its history.

**But `_load_bank` is not the only consumer, and the 374th entry is not residue — it is a required
input with its own validator.** `flux_universe.py:257 load_banked_flux_ratio_table` loads *and
validates* it, `unified_throw_cov.py:1044` documents that the flux-universe ROOT file is consulted
only when the bank carries no `flux_univ_ratio.npy`, and `_validate_ratio_table` refuses two shapes:
non-finite/non-positive ratios, and **`np.allclose(ratio, 1.0)`** — which it names as *"the J28/Task
#70 bug … what a missing or unreadable flux-universe file produces."*

**That mattered here, because the bank was written 2026-06-30 and the J28 flux fix landed 07-31 — a
month later.** Presence is not enough; the all-ones shape is precisely a bank that looks complete.
So I ran the real validator from the review tip against the real file (11,328 bytes, fetched):

```
shape (100, 14) float64        all finite: True     all positive: True
min 0.9103579178864005   max 1.1371157091579007    distinct values: 178
np.allclose(ratio, 1.0)  ->  False        <-- the J28/Task #70 signature is ABSENT
flux_universe._validate_ratio_table(...)      -> PASSED, shape (100, 14)
flux_universe.load_banked_flux_ratio_table(...) -> PASSED
```

The table varies across **universes** — the axis the J28 fix is about — by ±11%, and is flat in pT
to ~1e-6 (22 of 100 universes exactly constant across the 14 bins, max within-universe spread 0.000000
to six decimals), which is what a per-universe flux *integral* ratio should look like.

**Verdict: the bank clears both consumers, including the one the relay did not check, and clears the
specific pre-J28 failure shape it was at risk of.** Requirement, for the record rather than against
it: **the recommendation must cite `flux_univ_ratio.npy` as a checked input rather than as the 374th
file**, since a future bank could satisfy `_load_bank` completely and still be the J28 bug.

### B.4 The provenance stamps are on the PDT basis, unzoned, and the upper bound is a START

Two corrections, neither changing which job produced the bank:

**(a) Basis.** The relayed span `2026-06-30T04:00:08–06:07:17` is **Pacific**, presented without a
zone. Measured cleanly in a fresh session with nothing touched: the login shell exports
`TZ=America/Los_Angeles` (`date +%z` → `-0700`) *even though* `/etc/localtime` → `.../zoneinfo/UTC`,
so **the env var governs and `sacct` prints PDT by default**. Same query, `TZ=UTC`, prints
`11:00:08`. Exactly +7h. R5's unit is UTC, and an unzoned stamp in a durable record is what cost
this lane a withdrawal earlier today — I am flagging the shape, not the conclusion.

**(b) The upper end is the last task's START, not the campaign's END.** In UTC the eight tasks start
`11:00:08 … 13:07:17` and end `11:13:58 … 13:17:34`. `06:07:17` PDT = `13:07:17` UTC = the **Start**
of `_7`. The span is `11:00:08 → 13:17:34` UTC (2 h 17 m 26 s), across four scheduling waves, not
a contiguous 2 h 07 m.

---

## Part C — What this record does not do

It does not grade Z's legs, adopt the bank, approve a `--time`, or authorize a launch. The
admission accounting still refuses at `558.42` against `500`, and the `--time`/temp-name coupling I
recorded at `a51c6503` is unchanged: cutting the block arm's 12 h is the obvious way to recover
headroom, it is now known to be only 1.39× the observed maximum, and it is therefore *more* coupled
to the temporary-file repair than when I first wrote it down. Acceptance criteria for that repair
are pre-registered separately in
`PREREGISTER-20260911-temp-file-repair-acceptance-criteria.md`, committed before the work exists.

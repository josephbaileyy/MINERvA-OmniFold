# Endpoint-A acceptance, the `cause3_corr` amendment, and the criterion on the released error bars

**Owner:** `z-criteria-owner` lane (proposed Z scientific-criteria owner).
**Base of measurement:** `6f24fb00` (`origin/main`). Every file this packet quotes is **byte-identical
at `6f24fb00` and at this lane's tip** — verified by `git diff` over the nine named paths, empty.
**Predecessors:** `RECOMMENDATION-20260910-z-scientific-acceptance-criteria.md` (`2ebdf095`),
`PACKET-20260910-z-consumer-set-and-endpoint-requirements.md` (`173baf44`). Neither is superseded;
this packet **corrects one row of the second** and adds to both.
**Evidence:** `state/probe-z-projected-stability-20260910.py` — green, 37 checks, run at this tip.

> ## ⚠ CITABLE FOR / NOT CITABLE FOR — at the top, because a verdict word outranks the caveat beside it
>
> **CITABLE FOR:** the operand correction in §1; the endpoint-A requirement table in §2; the
> mechanical finding in §3 that `z_contract.py:231-236` is **inert** to cause 3's outcome; the
> demonstration in §4 that **A-4 is silent, not weak**, on the released error bars; the statistic
> proposed in §4.3.
>
> **NOT CITABLE FOR:** any grade, any adoption, any gate movement. **Gate 2 remains FAIL. `cause3_corr`
> remains WITHHELD. Cause 3 remains non-passing.** No boundary is declared here for `cause3_corr`, and
> §4.4 says why the number is not derivable today rather than supplying one. Nothing here amends a
> contract — §3 *specifies* an amendment and recommends against the form that was asked for.
> No value from `nd-unfolding/mii/member_k000000/` is quoted. No production compute was run.

**Standing constraints observed:** design and review only; no compute, no adoption, no publication
edit, no contract amendment, no grading of my own criteria.

**⚠ ON "STOP EXTENDING THE TOOLING", stated precisely rather than favourably.** **No existing file
under `state/` was modified** — `check-withdrawal-completeness`, `check-consumer-set`,
`probe-z-consumer-inversion` and the frozen `probe-z-criteria-acceptance-mathematics-20260910.py` are
all byte-identical (the last at `c2530cdc6175a5de410eb0561520f294afbc976f`). **One new file was
ADDED**: `state/probe-z-projected-stability-20260910.py`. It is not an extension of the
withdrawal/search tooling — it pins no inventory, searches no population, and shares no code with
those instruments; it is the measurement the three tasks required, and without it §3 and §4 would be
assertions. **The rejected universal-bound approach is not reopened:** no `ρ`, no `C_0^{-1/2}`, no
bound over an unmeasured ensemble. Every section evaluates a *declared functional on a declared
operand*, which is the shape outcome (2) left standing.

---

## 1. ⚠ THE OPERAND CORRECTION — my §3 premise was false, and the SCOPE of the correction is the finding

`PACKET-20260910` §3 stated that endpoint A's consumers read *"`sqrt(diag)`, `sqrt(trace)`, displayed
bands. Every one is a function of the diagonal"*, and concluded `cause3_corr`'s hazard was
**unrealized** for A. **The premise does not hold. The conclusion is withdrawn.**

**The algebra, measured (probe §1):** for `C_low = M C Mᵀ`,

    diag(M C Mᵀ)_i  =  Σ_jk M_ij C_jk M_ik  =  m_iᵀ C m_i        (m_i = row i of M)

which reads the **off-diagonal entries of `C`** whenever a row of `M` has more than one nonzero. And
they always do: `project_cov_nd.py:5-8` states M's nonzero entries are *"the product of the bin widths
of the DROPPED axes, grouped into the destination (kept-axis) bin"* — **a width-weighted sum over
cells**. Measured on a 40→6 map: dropping the off-diagonals moves the released bar by up to **34.0%**.

**My error was not the measurement. It was the operand.** `sqrt(diag(·))` *is* what the consumer
computes; the diagonal it takes is the **projected** object's, and that diagonal is a function of the
**source's** full matrix. Naming the right property over an operand nobody re-identified is the
failure shape this campaign has now paid for repeatedly, and this is my instance of it.

### 1.1 But the correction is NOT "all of endpoint A" — resolved per consumer

The relayed finding named `eavailW_covariance.py`. Applying it to the whole endpoint would be the
mirror error, so each consumer was re-read:

| consumer | site | does it project before reducing? | hazard |
|---|---|---|---|
| **C5** | `eavailW_covariance.py:442` `C_stat = project_covariance(C5stat, Mew)`, then `:443` `np.trace`, `:456-460` `C_lat_e += Me @ _th2(h) @ Me.T`, `:463` `np.diag` | **YES — projects first, reduces second** | **REALIZED** |
| **D1/D2** | `sec_3d.tex:193` *"combined-covariance systematic band"*; `:209` *"1D projections"*; `:262` *"projected onto `Eavail` … and `pT`"* | **YES** — the released band is a projection | **REALIZED** |
| **C6** | `coverage_valid_nd.py:44` `_load_cov_diag`, `:173` — reads a stored diagonal; **no `project_covariance` call anywhere in the file** | **NO, internally** | **CONDITIONAL** — realized exactly when its `--cov` operand is itself a projected product, which is what `project_cov_nd.py:26` writes |
| **C7** | `mii_anchor_comparator.py:238` `_sqrt_trace_from_diag`, *"`trace(C) == sum(diag(C))`, so no matrix is materialised"* | **NO** | **NOT REALIZED** — genuinely diagonal-only |

**So one cell of five survives, and it is the one that is Gate-2 blocked and unquotable anyway.**
C7's own comment at `:510-518` states the same limitation in its own words and calls the
diagonal *"the WORST available reduction precisely because it LOOKS TARGETED."*

**⚠ AND C5's OPERAND IS NOT MERELY ANALOGOUS TO A Z BLOCK — it is a NAMED CANDIDATE Z BLOCK.**
Contributed by the independent assessor and **re-verified here rather than relayed**:
`eavailW_covariance.py:143,145` default `--stat5d` / `--stat5d-hist` to
`uq_cov_stat_5d.root` / `hCov_stat5d_reported`, and `SPEC-20260906:504` names exactly that
path-and-hist (sha256 `6580016f…`) as **"Z's candidate `C_stat` … input"**, which enters `C_Z` in the
construction at `:610`. **So C5's released band is a linear functional of the off-diagonal entries of
a candidate `C_Z` summand**, not of an object merely resembling one. This sharpens the row; it does
not change the verdict.

*Two qualifications, because the sharpening is easy to overstate.* **(i)** It is a **candidate**
input, not a settled member: the `:504` row itself says *"Whether Z reuses or regenerates them is an
open scientific question, not a settled requirement"*, and `:3629` carries it as an open scientific
decision. **(ii)** ⚠ **The relay attributed that openness to §2.6b; §2.6b is the wrong citation** —
it is titled *"WITHDRAWN — reuse of `C_stat`/`C_ML` is not evidence of incompleteness"* (`:1092`) and
withdraws a **different** proposition. The openness is at `:504` and `:3629`; §2.6b is not where it
lives.

**Three independent sites in this tree already record this hazard** and none of them is an
adoption: SPEC §3.7d (naming `eavailW_covariance.py:290-304` and `coverage_valid_nd.py:20`),
`z_statistics.py:25`, and `mii_anchor_comparator.py:515`. **The finding was in the tree; what was
missing was its application to the endpoint split.** That is on me, not on the record.

---

## 2. TASK 1 — THE ENDPOINT-A ACCEPTANCE PACKET

**Scope:** what remains to construct and release Z's covariance and its declared projected
uncertainties. **Endpoint B is DEFERRED, NOT PASSED** (Ruling 1); B-2/B-3/B-4 remain **undischarged
requirements** and none is marked MET here.

| # | requirement | statement | class |
|---|---|---|---|
| **A-1** | construction | SPEC §1.3a algebra, §1.3b identity set incl. the `g^c` reconstruction gate, §3.3's fifteen reject conditions. Unchanged, not reopened | FIXED by spec |
| **A-2** | provenance | the four inversion declarations of `app_statmethods.tex:645-658` travel with any released projection **even for a diagonal consumer** — clause (iv) exists because *"the 5D candidate, its 4D projection and the published 2D block have different ranks"* | CONFORMANCE |
| **A-3** | numerical reproducibility | `r_null = ‖x_cv2 − x_cv‖/‖x_cv‖` over the reported support, **`ε = 1e-9`**, derived in `RECOMMENDATION-…` §C.3 from a proven inequality plus Joseph's declared `REPRO_RTOL_PER_BIN` (`p4_lib.py:93`). Carried forward unchanged | PROPOSED |
| **A-4** | declaration stability | retained rank and retained-subspace projector gap across members, `‖P_0 − P_k‖_2 ≤ 1e-8`. ⚠ **NOW EXPLICITLY NARROWED BY §4: this bounds the subspace and is SILENT on the released error bars.** It is not a partial guarantee about them | PROPOSED, **narrowed** |
| **A-5** | PSD | *"no eigenvalue below `−k·λ_max` for a declared `k`"*, never *"PSD"* or *"λ_min ≥ 0"*. `adopt_unified_5d.py:150-165` already uses `ev[0] >= -1e-12*ev[-1]`; the requirement is to make it a **receipt-recorded gate** with `k` declared | PROPOSED |
| **A-6** | **finite-ensemble disclosure** — NEW, from Ruling 2 | §2.1 below. Per sample-covariance block: **verified** `N`, normalization convention, finite-ensemble treatment **or the explicit statement that none was applied**; inverted dimension marked **not applicable** | PROPOSED |
| **A-7** | **stability of the RELEASED error bars** — NEW, from Task 3 | §4.3 below. `s_proj` over the declared functional set. **Statistic proposed; boundary WITHHELD with a named trigger (§4.4).** Precondition: destination-support identity across members | PROPOSED (statistic only) |

### 2.1 A-6 — and why Ruling 2 lands on A rather than B

**The block population is CLOSED and DERIVED, not enumerated by hand.** `z_assembly.py:4` states Z's
construction:

    C_Z^c  =  D_Z^c (Σ_V C_b) D_Z^c  +  Σ_R C_b  +  Σ_A L_b  +  C_stat  +  C_ML

**Exactly two summands are sample covariances: `C_stat` and `C_ML`.** Everything else is a
deterministic band or lateral sum. So clause (v)'s *"for every sample-covariance block entering the
sum"* has a population of **two**, fixed by Z's own formula rather than by a search.

**⚠ AND MY OWN B-4 ROW CITED THE WRONG OPERAND. Corrected here.** It gave `N = 100` from
`sbatch_bootstrap_5d_gpu.sh:5` and `N = 24` from `sbatch_seedscan_split_5d.sh:5`. Read verbatim, those
lines are `#SBATCH --array=1-100%32` and `#SBATCH --array=1-24%24` — **declared arrays: what was
submitted, not what landed.** A throttled or partly-failed array yields fewer members with the
header unchanged. This is the same defect class as reading a launch plan as a record, and the
correction is to bind each field to the code that produces the number:

> **⚠⚠ REV. 2 CORRECTS THIS SUBSECTION IN TWO PLACES, both found when a second orchestrator
> refused the phrase *"no artifact records it"* and asked me to separate a MISSING STAMP from a
> GENUINELY UNRECOVERABLE POPULATION. It was right to refuse it.**
>
> **(1) I READ THE WRONG PRODUCER FOR `C_ML`.** Rev. 1 attributed it to
> `combine_seedscan_split.py`, which writes **`hCov_mlsplit3d_reported`** — a **3D** product — and
> which is referenced by **no launcher in the tree at all**. Z's `C_ML` is
> `uq_cov_mlsplit_5d.root:hCov_mlsplit5d_reported`. **Both** of Z's blocks are produced by
> **`combine_cov_nd.py`** (`sbatch_combine_5d_budget.sh:14,16`, `--tag stat5d` / `--tag mlsplit5d`),
> so the rev. 1 *"asymmetry"* — one producer requiring `--expected-ids`, the other defaulting it —
> **is void for Z: it compared Z's producer against a script Z does not use.** Same defect class as
> §1: right measurement, wrong operand.
>
> **(2) THE ID SET IS RECORDED, IN TRACKED CODE.** `sbatch_combine_5d_budget.sh:14,16` pass
> **`--expected-ids 1-100`** (→ `stat5d`) and **`--expected-ids 1-24`** (→ `mlsplit5d`), and
> `combine_cov_nd.py:13` makes the flag **`required=True`**, so it cannot default silently. Rev. 1's
> *"no artifact records either field"* was **overstated**: what is missing is an **embedded stamp in
> the product**, not the number.

| field (clause (v)) | `C_stat` | `C_ML` | recorded where? |
|---|---|---|---|
| **declared id set** | **`1-100`** — `sbatch_combine_5d_budget.sh:14`; member-scoped variant at `sbatch_finalize_5d_bkgaware_gpu.sh:422` | **`1-24`** — `sbatch_combine_5d_budget.sh:16` | **YES — in tracked launchers.** `--expected-ids` is `required=True` (`combine_cov_nd.py:13`), so it is always a caller declaration |
| **verified `N`** | `combine_cov_nd.py:18` → `load_replica_manifest(paths, set(range(lo,hi+1)))` | **same script, same line** | **DERIVABLE, NOT STAMPED** — see the recovery argument below |
| **normalization** | `combine_cov_nd.py:20` `C=(Z.T@Z)/(Xr.shape[0]-1)` → **unbiased `1/(N−1)`** | **same line — one script, one convention** | **NO — a code fact, not a recorded one** |
| **effective `p` inverted** | — | — | **NOT APPLICABLE at endpoint A** (no inversion) |
| **finite-ensemble treatment** | none applied | none applied | must be stated **explicitly**, per `OI-137` *"disclose, do not correct"* |

**How `N` is verified, and it is a real mechanism rather than a hope:**
`replica_manifest.load_replica_manifest:44-48` **fails closed** on an exact id-set mismatch —
`raise ValueError(f"replica id mismatch: missing={…} extra={…}")`. So a *successful* run is itself
evidence that the declared id set landed in full. That is the verification instrument, it already
exists, and it should be **called, not reimplemented**.

### 2.1a ⚠ A MISSING STAMP IS NOT AN UNRECOVERABLE POPULATION — the two must be separated

**(i) MISSING EMBEDDED STAMP — CONFIRMED.** `combine_cov_nd.py:23-26` writes **exactly one object**,
`hCov_{tag}_reported`, and nothing else; `N` is `print`ed at `:22` and never persisted. And the
binding manifest carries no ensemble field either: `std_component_manifest.json` holds
`stat_cov`/`stat_sha256`/`ml_cov`/`ml_sha256` and **`n_reported = 10694`, which is a BIN count, not a
member count** — a field a hurried reader could easily take for `N`.

**(ii) UNRECOVERABLE POPULATION — NOT ESTABLISHED, AND I SHOULD NOT HAVE IMPLIED IT.** There is a
recovery route that needs neither the printed `N` nor the replica files:

> **`--expected-ids` is a caller declaration (`required=True`), and
> `replica_manifest.load_replica_manifest:44-48` FAILS CLOSED on any id-set mismatch —
> `raise ValueError("replica id mismatch: missing=… extra=…")`. So a SUCCESSFUL execution of that
> command line is itself proof that exactly the declared id set was present.** `N` is then the
> declared range, recovered by logic rather than by a stamp.

**So what is actually missing is one BINDING, not a number:** evidence that the execution which
produced the bytes digested as `6580016f…` (`C_stat`) and `27b2e456…` (`C_ML`) was that command and
exited 0. That is a receipt/jobid question about existing execution evidence, **not** a regeneration
question — and **nothing here scopes or requests regeneration.**

**⚠ AND THE BINDING IS GENUINELY AMBIGUOUS IN THE CODE, which is why it must be established rather
than assumed.** At least three tracked sites issue an equivalent command: `sbatch_combine_5d_budget.sh:14,16`,
`run_budget_5d.sh:18`, and `sbatch_finalize_5d_bkgaware_gpu.sh:422` — and **the third is
MEMBER-SCOPED**, its glob passing through `mr_prefix`, so it reads a per-member replica directory
rather than the top-level one. **The declared id range is the same; the population it ranges over is
not.** Code alone therefore cannot say which execution produced the digested bytes. *(No value from
the member-scoped tree is quoted here — only the launcher line.)*

**A-6 is therefore phrased in two parts, and only the first is a disclosure obligation:**
**(a)** record, beside each released block, its declared id set, its verified `N`, the `1/(N−1)`
convention, and the explicit statement that no finite-ensemble treatment was applied — with the
inverted dimension marked **not applicable** at A; and **(b)** bind the product digest to the
producing execution, from evidence that already exists. **Rev. 1 said "the requirement is to write
them, not to look harder." That was wrong in the second half: looking harder is exactly what (b)
is, and it has not been done here.** I did not search Slurm records, receipts or logs for the
producing job of either digest, and I am not claiming that search would fail.

**WHY THIS IS A AND NOT B — three reasons, in ascending strength:**

1. **The population is fixed by the object, not by a consumer.** `C_stat` and `C_ML` are summands of
   `C_Z`. Their ensemble size is a property of the released covariance, determined before any
   consumer exists.
2. **`N` bounds the rank of the released object.** A sample block from `N` members has rank `≤ N−1`,
   which feeds directly into A-2's clause-(iv) obligation to say *which* covariance is meant and at
   what rank. That obligation is A's, and it cannot be discharged without `N`.
3. **⚠ DECISIVELY: the number is not IN the object at endpoint B.** A later consumer opening the
   ROOT file finds a `TH2D` and no provenance — recovery requires the producing launcher and its
   execution record, which are construction-time artifacts. **A
   requirement must sit where its operand exists** — if `N` is not recorded at construction time it is
   unrecoverable, and a B-stage disclosure requirement would be unsatisfiable in principle.

**What A-6 is NOT.** It is disclosure only: **not** validation of a reference distribution, **not** a
bias correction, **not** scientific adoption of either block. Clause (v)'s own note is explicit that
declaration *"does not yet mandate a correction."*

---

## 3. TASK 2 — THE `cause3_corr` AMENDMENT, ESTABLISHED BY RUNNING THE VALIDATOR

Joseph: *"do not silently remove it or mark cause 3 MET."* The orchestrator's test: *"if scoping it out
is what makes cause 3 passable, the amendment is unsound as written."*

**That test comes back NEGATIVE — and the amendment is still unsound, for a different reason.**
Everything below is measured by executing `z_validator.assess`, not by reading it (probe §4).

### 3.1 The registry site named in the brief is INERT

| # | measurement | result |
|---|---|---|
| (a) | **no production leg set exists.** Every `LegSet(...)` in the tree is in `nd-unfolding/tests/test_z_validator.py`. `z_build.py` calls only `assess_null` (`:521`) | `L` is whatever an adopter declares |
| (b) | with `L = {agg, med}` and the two **diagonal** boundaries declared probe-locally, `assess` returns **branch 3 = MET** while `cause3_corr` is still withheld | **`cause3_corr` is not what blocks MET** |
| (c) | **deleting `cause3_corr` from `Z_BOUNDARIES` entirely** and re-running gives an outcome whose `describe()` is **byte-identical** | **`z_contract.py:231-236` is inert to the outcome rule** |
| (d) | `assess` reaches a boundary only through `leg.boundary_key` (`z_validator.py:247`). No leg names `cause3_corr` | the mechanism is **leg-driven, not registry-driven** |
| (e) | declaring a `sees_correlations=True` leg on `cause3_corr` → `assessable=False`, `branch=None`, `reject_conditions=('4c',)` | adopting the leg is what makes the withholding **bind** |

**So the docstring's guarantee — *"`assess()` never returns MET when any declared leg's boundary is
withheld"* — is exact, and the load-bearing word is `declared`.** `cause3_corr` is a boundary **no leg
declares**, so it is withheld without being binding. Scoping it out of A changes nothing about cause
3's passability, and **the amendment cannot be unsound in the way the brief tested for.**

### 3.2 ⚠ BUT IT IS UNSOUND, AND THE BINDING SITE IS SOMEWHERE ELSE

What *is* live is `z_validator.py:168-172`, `_DIAGONAL_ONLY_SCOPE` — emitted on **every** outcome
whenever `L` contains no correlation-sensitive leg, **derived from the legs and not assertable by a
caller** (review finding 8 removed the keyword argument precisely so a caller could not suppress it).
Its text, verified word by word:

> *"…It is NOT evidence that `C_Z`'s correlation structure is stable, and it does NOT license the
> assembled covariance for **marginalization**, **projection**, **coverage validation** or any other
> off-diagonal-sensitive use."*

**All three words are present** (probe §4(d)). And by §1, **endpoint A's deliverable *is* a
projection.** So:

> **A MET result on cause 3 under the current leg set disclaims, in its own automatically emitted
> text, exactly the release endpoint A exists to make.**

**Therefore deferring `cause3_corr` from endpoint A does not require touching the registry line. It
requires narrowing that sentence to drop `projection` and `marginalization` — a change to what a MET
result LICENSES.** That is a change to the scientific contract, and it is the one Joseph barred. The
registry line the brief pointed at cannot reach it; the amendment, written at the site the brief
names, would be **cosmetic**, and the licensing change would happen elsewhere or not at all.

### 3.3 The exact amendment — and it is not a deferral

> **⚠ THREE OPTIONS, THREE DIFFERENT VERDICTS. Each carries its verdict inline, because the first
> relay of this section collapsed them into one and INVERTED the recommendation** — it attached
> *"unsound"* and *"not recommended"* to option 3, which is the recommended one. A verdict word has
> to survive being read alone, and in a three-option section it also has to survive being read
> **apart from the other two**.
>
> | option | what it does | verdict |
> |---|---|---|
> | **1** | defer `cause3_corr` from A **while A keeps releasing projected uncertainties** | **UNSOUND** — needs `_DIAGONAL_ONLY_SCOPE` narrowed, i.e. a change to what a MET **licenses** |
> | **2** | narrow **endpoint A itself** to release the covariance and **no** projected uncertainty | **SOUND, NOT RECOMMENDED** — it works, and it deletes A's own deliverable |
> | **3** | **do not defer**; bind `cause3_corr` to endpoint A's own statistic | **⭐ RECOMMENDED** — the amendment becomes an **adoption record**; **no licensing change** |
>
> **"An adoption dressed as a deferral" is NOT the finding, and reverses it.** The finding is that
> *a deferral cannot be written without an adoption-shaped licensing change* — which is a reason to
> **do** option 3 openly, not a criticism of it.

**RECOMMENDED (option 3): do not defer `cause3_corr`. Bind it to endpoint A's own statistic.** The
amendment is then an **adoption record**, three sites, none of which changes what a MET licenses:

1. **`nd-unfolding/z_contract.py:233-235`** — the `reason` string's first clause, *"no
   correlation-sensitive leg is adopted, and none has a boundary"*, becomes **false on adoption** and
   must be rewritten to name the adopted leg and state that the boundary alone is withheld. **The
   second clause stays true and stays.** ⚠ Note this is the *opposite* of removing the entry: the
   boundary stays withheld and becomes, for the first time, **binding**.
2. **`nd-unfolding/z_validator.py`** — no code change. The scope statement withdraws itself once
   `sees_correlations=True` appears in `L` (probe §4(e)); the leg-set generalisation of rev. 16
   already admits a third leg *"without a further edit here."* **The correlation leg must declare
   which of `aggregate`/`per-bin` it REPORTS AS** — `LEG_CLASSES` is not extended, and that
   declaration is the adopter's.
3. **SPEC §3.7d** — records the disposition as **answer (b), add a correlation-sensitive leg**, and
   records that **answer (a) is NOT AVAILABLE for endpoint A**, because (a)'s narrowing excludes
   precisely what A releases. §3.7d currently presents (a) and (b) as equally admissible; measured
   against the endpoint split, they are not.

**OPTION 2 — THE ONE FORM IN WHICH A DEFERRAL *IS* SOUNDLY WRITABLE, stated so the choice is
Joseph's and not foreclosed by me:** narrow **endpoint A itself** to release the assembled covariance and **no projected
uncertainty** — moving C5, D1 and D2 to a later endpoint. Then A's consumers are C6-on-an-unprojected
operand and C7, both genuinely diagonal-only, `_DIAGONAL_ONLY_SCOPE` is accurate as written, and no
licensing change is needed. **The cost is A's projected-uncertainty deliverable**, which is A's stated
purpose and the object `sec_3d.tex:252-256` says the 3D comparisons are gated on. **I do not recommend
it**, but it is sound, and it is the only sound deferral available.

**What I am NOT doing, and this survives being quoted alone:** not amending anything, not adopting
the leg, not declaring the boundary, and not grading cause 3. **Option 3 is what the amendment WOULD
be IF Joseph adopts the leg — it asks him to adopt nothing now.** Adoption of the leg **keeps cause 3 non-passing** until the boundary is declared
(probe §4(e)) — which is the correct state given Gate 2 FAIL, and is why the recommendation costs
nothing today.

---

## 4. TASK 3 — THE ADEQUACY CHECK: WHAT CONTROLS THE RELEASED ERROR BARS

### 4.1 A-4 is not a weak bound on the released bars. It is SILENT.

Joseph's objection is exactly right, and it is stronger than "does not by itself establish."
**Construction (probe §2):** `C_k = (1+a) C_0`. Scaling preserves eigenvectors, so the retained
subspace and retained rank are *identical* while every eigenvalue moves.

| `a` | `‖P_0 − P_k‖_2` | retained rank | `s_proj` (released-bar movement) |
|---:|---:|---:|---:|
| 0.05 | `3.909e-15` | 30 → 30 | 2.4695% |
| 0.20 | `2.933e-15` | 30 → 30 | 9.5445% |
| 1.00 | **`0.000e+00`** | 30 → 30 | **41.4214%** |

**A-4's gap is at ROUND-OFF — `~3e-15`, and exactly `0` at `a = 1` — while the released error bars
move by 41%.** That is roughly **seven orders of magnitude** inside A-4's `1e-8`, so the tolerance is
not merely too loose; the quantity A-4 measures does not respond to the perturbation at all.
*(Stated at the measured values rather than as "exactly zero in every row", which an earlier draft of
this table asserted from the `a=1` row alone.)*
No choice of A-4's tolerance changes this: the projector is invariant under the perturbation, so A-4
carries no information about eigenvalue magnitude at all. **A-4 must not be cited as partial
protection for the released uncertainties**, and A-4's row in §2 now says so.

**And the two adopted cause-3 legs are no better.** Re-measured with the projection applied (probe §3):
on `C_0 = I₂` versus `[[1,0.9],[0.9,1]]`, `s_agg` and `s_med` return **exactly `0.0`** while the
released bar of the marginal bin moves from `1.414214` to `1.949359` — **+37.8%**. That is SPEC §3.7d's
table, and the `+37.8%` entry *is* the released quantity, not an illustrative aside.

**So: no criterion in A-1 … A-5 bounds the released error bars.** The gap is real.

### 4.2 The instrument already exists, and I am calling it

Per the process constraint, I searched before proposing. **SPEC §3.7d names three candidates and all
three are already implemented** in `nd-unfolding/z_statistics.py`, none adopted:

| candidate | site | what it sees | why not chosen / chosen |
|---|---|---|---|
| **`s_proj`** | `:198` | max relative change in `sqrt(uᵀ C u)` over a predeclared functional set | **CHOSEN — see §4.3** |
| `s_corr` | `:240` | relative Frobenius change in the **correlation** matrix | **Not chosen.** It is a *different question*: it divides the diagonal out, so it can fire when no released bar moves and stay quiet when one does. It also `require`s `d > 0` on **every** bin (`:236`), so a single unsupported bin aborts it globally. It is the right instrument for *"is the correlation structure stable"* — which is not what A releases |
| `s_eig` | `:256` | relative change in the leading eigenvalue | **Not chosen.** Least interpretable, most expensive (its own docstring: `~1-3 min` per member at `10,694`, a **local** estimate with runtime unestablished), and a leading eigenvalue is not a released quantity |

**§3.6d's ordering rule governs — statistic first, boundary second — so choosing among these is the
scientific work, and this is the choice.**

### 4.3 A-7 — the proposed statistic

> **`s_proj` evaluated with `U` = the rows of the projection matrix `M` for each declared released
> projection, restricted to the SUPPORTED destination bins, plus the all-ones vector.**

| field | statement |
|---|---|
| **quantity** | `max_k max_i \| sqrt(m_iᵀ C_k m_i) − sqrt(m_iᵀ C_0 m_i) \| / sqrt(m_iᵀ C_0 m_i)` over the declared offset set `K` and the declared functionals |
| **intended scientific use** | the released per-bin uncertainty of every projected deliverable — C5's `(E_avail,W)` bands, D1/D2's 1D projections |
| **statistic** | maximum over `K` — the quantifier in the claim is universal, so the extremum grades it, matching `z_statistics`' stated reason for `s_agg`/`s_med` |
| **denominator** | the **baseline (`k=0`) released bar of the same bin**. Same quantity, same units, same bin — dimensionless by construction, not by assertion |
| **required population** | the rows of each declared `M`, over destination bins with support, **plus the all-ones vector** (the total-rate functional, per §3.7d) |
| **boundary model** | §3.6d's **DIRECT** form, `\|U′ − U\|/U ≤ δ`. **No quadrature**, and the burden does not arise: the statistic measures a change *in* `U` itself, so nothing is being added and independent additivity is not in question |
| **terminal outcomes** | `s_proj ≤ δ` → the leg is within limit; `>` → NOT MET with the argmax offset **and argmax functional** named (`s_proj` returns both); abort → construction defect, see below |

**⚠ IT IS NOT A PROXY FOR THE RELEASED BAR — IT IS THE RELEASED BAR.** `s_proj`'s internal expression
is `np.einsum("ij,jk,ik->i", U, C, U)` (`z_statistics.py:216`), and that is **equal** to
`np.diag(U C Uᵀ)` — verified to machine precision against `uq_math.project_covariance` on a 40→6 map
(probe §1). With `U = M`, `s_proj` evaluates the consumer's own quantity at `eavailW_covariance.py:463`.
**This is why it, and not a bound, is the right instrument**, and it is the same reasoning that
produced outcome (2): a direct check on the declared consumer beats a universal bound over an
ensemble nobody measured.

**Behaviour on the cases Z's contract permits — measured, not assumed (probe §5):**

- **Singular / rank-deficient `C`** (Z's own case — `rank(C_Z) ≤ 265` of `10,694`, derived in
  `RECOMMENDATION-…` Part 6 F1): **irrelevant to `s_proj`.** `uᵀ C u` needs no inverse, no `rcond`, and
  no positive-definite baseline. Verified on a rank-3-of-12 operand: exact to `1e-12`. **This is the
  property that failed for the ρ-based approach and holds here.**
- **Zero baseline projected sigma** — `eavailW_covariance.py:429-431` warns these bins are *"NOT
  measured-and-precise; they are unsupported."* `s_proj` **ABORTS** (`require(np.all(base > 0))`,
  `:221`) — verified: `ZContractError: s_proj: a predeclared functional has zero baseline
  uncertainty`. **Abort, not a silent `0/0` and not a pass.** Consequence: the functional set must be
  **declared over the supported destination bins**, and the predicate for that already exists as
  `eavailW_covariance.ew_coverage_report:55-68` — verified to return exactly the empty rows. **An
  abort on a bin declared SUPPORTED is a construction defect, not a tolerance question.**
- **Support-changing members** — ⚠ **a RESIDUE, not a covered case.** `U` is predeclared and fixed, so
  if member `k`'s destination support differs from the baseline's, `s_proj` measures the baseline's
  functionals and is **silent** about a destination bin appearing or vanishing. Verified: support
  changed `0 → 1` empty rows and `s_proj` was unchanged. **Therefore destination-support identity
  across members is a PRECONDITION** in `Validity`'s style, belonging with the branch-1/2 falsifiers —
  **never something the tolerance absorbs.** This is A-7's stated precondition.

**Power in both directions, plus a control (probe §6):** exactly `0.0` on identical members;
`14.0175%` when bars inflate (`1.3×`); `16.3340%` when bars **shrink** (`0.7×`) — a filter must act in
the direction it acts; and on a correlation-only change with a bit-identical diagonal, `s_agg` returns
`1.8e-16` while `s_proj` returns `9.4010%`.

### 4.4 THE BOUNDARY — withheld, with the reason measured and the trigger named

**I am not proposing a number, and the reason is a measurement rather than caution.**

**⚠ FIRST, WHAT I WILL NOT DO, AND THE PRECEDENT IS IN THIS TREE IN BOTH DIRECTIONS.** δ from *"half
the last printed unit"* is **legitimate for reproduction** and **illegitimate for acceptance**, and
both instances are live:

- `receipt_cause1_endpoint_census_5d.py:88-89` — `REPRO_RTOL = 5e-4`, *"half a unit in the last printed
  place. Not a fitted tolerance."* **Correct**: it asks whether a recomputation matches a printed
  number.
- `cause3_agg`'s withdrawn `0.0861%` — *"Macro formatting does not establish how much
  estimator-baseline sensitivity is scientifically acceptable, and the half-display-unit rule behind
  it is wrong in both directions."* **Wrong**: it asked how much the physics may move.

A-7 is the second kind. §3.6d says the same thing generally: *"A reproducibility floor … measures
achievable repeatability, not acceptable error."* **So no format-derived number is offered.**

**SECOND, THE MEASUREMENT: δ's declared use is currently EMPTY, and the note says so itself.**

| candidate declared use | measured status |
|---|---|
| the Letter | `paper_body.tex:145-146` — *"Every non-two-dimensional result in this Letter is a central value."* **No non-2D uncertainty is quoted** |
| the 3D budget | `sec_3d.tex:250-251` — `sqrt(tr)=5.72e-39`, median per-bin relative `10.4%`, rank `247` of `1431`, *"the same flux-dominated band ordering as 2D"* — followed immediately by ***"These are audit descriptors, not publication uncertainties."*** |
| D1/D2 figures | bands drawn, no printed digit; `:263-264` *"The magnitudes are quarantined"*; `:210` *"orientation only and is not final"* |
| C6 | a truth-containment **diagnostic** at *"nominal 68.27%"* (`coverage_valid_nd.py:188,209`), not a released claim |
| C7 | Gate-2 blocked, unquotable |

**⚠ AND THIS IS A DIFFERENT CLAIM FROM THE ONE I JUST WITHDREW IN §1 — the distinction matters and I
am stating it rather than letting a reader assume I repeated myself.** §1's error was *"the hazard is
unrealized"*, which was false about the **operand**. This is not that. **The hazard is realized; the
statistic is needed and is proposed.** What is empty is the **declared publication uncertainty that
δ would be a fraction of** — and it is empty **by the note's own explicit declaration** at
`sec_3d.tex:251-252`, not by my inference from an absence. A criterion whose denominator I invented
would be a number in search of a meaning, which is exactly what §3.6d's ordering rule forbids.

**THIRD, THE TRIGGER — and it is a declaration already written in the tree, not a measurement I must
commission.** `sec_3d.tex:252-256`:

> *"Under the corrected contract, the quotable 3D covariance is the exact projection of the final
> adopted 5D covariance after the selection-complete lateral replacement; all covariance-dependent 3D
> comparisons are gated on that product."*

**So the use is already named; only the number is absent.** `δ_proj` becomes derivable, by §3.6d's
direct form and with no new scientific decision, at the moment endpoint A declares **(i)** which
projected uncertainty is published and **(ii)** the claim it supports. The band-ordering claim at
`:250` and `:263` is the concrete candidate — it is an **ordinal** claim, so its falsification threshold is half
the smallest adjacent-band fractional gap, **measured on the `k=0` baseline** and declared before
members are compared. That keeps the tolerance derived from the baseline's structure and **not
selected from the movements being graded** — which is the separation the constraint requires.

### 4.4a ⚠ WHAT IS ACTUALLY WITHHELD IS ONE SCALAR, NOT THE CRITERION — rev. 1 framed this too widely

**Rev. 1 read as though the whole boundary were blocked on the note's published figures. It is not,
and the correction matters because it changes what Joseph is being asked.** A-7 has three parts and
**only the third depends on any scientific choice**:

| part | what it is | status |
|---|---|---|
| **(a)** the **prospective product** and the **declared functional set** | the exact projection of the adopted 5D covariance onto each released axis set; `U` = rows of that projection's `M` over the **supported** destination bins (predicate: `ew_coverage_report`), plus the all-ones vector | **FULLY SPECIFIED. Needs no published number** — it is a property of the prospective object and of `M`, both known at build time |
| **(b)** the **denominator** | `sqrt(m_iᵀ C_0 m_i)` — the **baseline member's own released bar for the same bin**, computed from the same prospective product | **FULLY SPECIFIED. Needs no published number.** Same quantity, same units, same bin; dimensionless by construction |
| **(c)** the **scientifically acceptable fractional change** | one scalar | **THE ONLY OPEN PIECE** |

**So it is NOT a dependency on already-published uncertainty numbers.** (a) and (b) are prospective
throughout. **A historical plot labelled "audit descriptor" does not block a prospective criterion —
it blocks only the attempt to read (c) off that plot's printed precision**, which is the one thing
§4.4 refuses to do and refuses on precedent.

**AND (c) ITSELF DECOMPOSES, exactly as `null_epsilon`'s own spec requires — `B ≤ S`, `δ ∈ [B, S]`:**

- **`B`, a DISCRIMINABILITY FLOOR — derivable, with a stated model.** Each released bar carries
  irreducible sampling noise from the two sample blocks. For an `N`-member Gaussian ensemble the
  relative standard error on an estimated variance of a fixed functional is `sqrt(2/(N−1))`, hence
  `≈ 1/sqrt(2(N−1))` on the **bar**; scaled by the sample blocks' share of that bin's projected
  variance, since `C_Z` is dominated by ~45 deterministic band contributions. **Estimator-baseline
  movement below `B` is not distinguishable from the noise the bar already has.** `B` is computable
  at build time from **A-6's verified `N`** — which is why A-6 and A-7 are coupled, and why A-6 is
  worth having independently of any inversion. **Assumption stated, per the spec: iid-Gaussian
  replicas. That is an assumption, not a measurement, and it should be checked rather than trusted.**
- **`S`, a SCIENTIFIC CAP — one decision, and it is Joseph's.**

**⚠ AND `B` MUST NOT BE USED AS `S`. This is the trap, and it has already been sprung once in this
campaign.** `null_epsilon`'s `min(achievable, acceptable)` construction was **withdrawn in rev. 19**
precisely because it used a feasibility floor as an **upper** bound, where such a floor bounds `ε`
from **below**. `B` is achievability; `S` is acceptability. Setting `δ_proj = B` would repeat that
error exactly, so I am naming it rather than quietly proposing the convenient number.

### 4.4b THE ONE-LINE DECISION, WITH BOTH CHOICES PRICED

> **For Joseph:** *"What is the largest fractional change in a released projected uncertainty that
> would leave the scientific reading of the released result unchanged?"* — that scalar is `S`.

**Consequences, so the choice is informed rather than open-ended:**

- **`S` large (tens of percent):** A-7 passes almost regardless and protects little. Note the scale
  it must beat: §3.7d's own demonstration moves a released marginal bar by **37.8%**, so an `S` above
  that would admit the exact failure the requirement exists to catch.
- **`S` small (sub-percent):** may violate the precondition **`B ≤ S`**. ⚠ **If `B > S` the correct
  reading is NOT "loosen `S`"** — it is that **the ensembles are too small to support a claim at that
  precision**, which is a real, actionable finding and points straight back at `N` (A-6).
- **`B ≤ S` is falsifiable at build time and should be checked BEFORE any grading**, in the
  branch-1/2 style, so an unsatisfiable pair is reported as inconclusive rather than as a failure of
  the object.

**What I am not doing:** not choosing `S`, and not offering a placeholder for it. `B` is a rule I am
proposing; `S` is the single scientific input, and the honest form of "reserved for Joseph" is the
question above plus the two priced consequences — not a returned blank.

**WHAT I RECOMMEND IN THE MEANTIME, and it is actionable now:** adopt `s_proj` as a **reported
statistic** under A-7 — computed on the baseline build, reported with its argmax offset and argmax
functional, **grading nothing**. That is exactly the posture `z_statistics.py` already declares for
every function in it (*"EVERY FUNCTION HERE RETURNS A NUMBER AND GRADES NOTHING"*), it needs no
boundary and no contract amendment, and **it makes the movement of the released bars visible for the
first time** — which is the gap Joseph identified. Promotion to a binding leg follows §3.3's
amendment when the boundary is declared.

---

## 5. C11 IS OUT OF SCOPE UNDER RULING 1 — stated in its own row, not in prose

**`2d-unfolding/uq/_ours_only_chi2.py:128-130` is a LIVE 2D non-conformer on `ndf` and is NOT to be
changed.** Measured at `6f24fb00`: `:128` `Cinv = np.linalg.inv(Cs)`, `:130` prints
`ndf = {n_rep}` — the **bin count**, where `app_statmethods.tex:648` clause (ii) (`:648`) mandates the
**retained rank**. The file itself computes `rank_at_1em12` at `:123` and does not use it as `ndf`.

**Ruling 1 preserves the validated 2D scope unchanged, so this is out of scope to change, and the
exclusion is recorded here explicitly** — an unstated exclusion is the failure mode this packet family
has already paid for twice. Two qualifications so the row is not misread later:

- `np.linalg.inv` is **correct at full rank**, per N2's control; the non-conformance is the `ndf`
  label, not the inverse.
- Being out of scope is **not** conformance. C11 remains a non-conformer; it is a non-conformer
  nobody is authorised to touch under this ruling.

---

## 6. PROVEN BOUND vs EMPIRICAL ESTIMATE vs SCIENTIFIC JUDGEMENT

| claim | class |
|---|---|
| `diag(M C Mᵀ)_i = m_iᵀ C m_i`, and it reads off-diagonals when a row of `M` has >1 nonzero | **PROVEN** (algebraic identity; verified numerically) |
| `s_proj` with `U = M` computes exactly the released bar | **PROVEN** (same identity) |
| scaling `C` leaves the retained subspace and rank invariant while bars move by `sqrt(1+a)−1` | **PROVEN** (eigen-decomposition; verified to `1e-9`) |
| **A-4 is silent on the released error bars** | **PROVEN** — a single exact counterexample suffices, and `‖P_0−P_k‖_2 = 0` exactly |
| `z_contract.py:231-236` is inert to cause 3's outcome under the current leg set | **PROVEN for the leg sets that exist** — byte-identical outcome with the entry deleted. ⚠ Conditional on no leg naming it; adoption changes it, by design |
| `rank(C_Z) ≤ 265` of `10,694` | **PROVEN** from Z's operands (`RECOMMENDATION-…` Part 6 F1) — quoted, not re-derived. **`263` is S's measured rank, not Z's** |
| the two sample-covariance blocks normalise by `1/(N−1)` and record `N` nowhere | **EMPIRICAL — a code read at `6f24fb00`.** Dated: a producer change invalidates it |
| `N` is *verified* by `load_replica_manifest`'s fail-closed id check | **EMPIRICAL**, and conditional on the run having succeeded |
| **`s_proj` is the right choice among §3.7d's three candidates** | **SCIENTIFIC JUDGEMENT.** The identity in §4.3 is proven; that the released bar is *the* quantity to protect at endpoint A is a judgement about what A is for |
| **answer (a) is unavailable for endpoint A** | **SCIENTIFIC JUDGEMENT**, resting on the proven §1 identity plus the reading that A's purpose includes projected uncertainties |
| **A-6 belongs to A rather than B** | **SCIENTIFIC JUDGEMENT**, with reason 3 (the operand does not exist at B) as its mechanical core |
| `ε = 1e-9`; `‖P_0 − P_k‖_2 ≤ 1e-8` | unchanged from `RECOMMENDATION-…`; classes as recorded there |
| **`δ_proj`** | **NOT PROPOSED.** §4.4 |

---

## 7. RESIDUES — what this packet does not establish

1. **`δ_proj` is not derived.** §4.4. The trigger is a declaration, and it is Joseph's.
2. **Destination-support change is a precondition, not a covered case.** §4.3. `s_proj` cannot see it,
   and no existing criterion is proposed here to catch it — it is named as A-7's precondition and left
   as a requirement on the producer's `Validity` record.
3. **C6's hazard is CONDITIONAL and the condition is unmeasured.** Whether `coverage_valid_nd.py` is
   ever invoked with a projected `--cov` operand is a question about *invocations*, and no invocation
   record was searched. §1.1 says conditional; it does not say which.
4. **The `s_corr` / `s_eig` rejections are judgements, not measurements.** I did not price `s_eig` at
   Z's real dimension — its docstring's `1-3 min` is a **local** figure with runtime unestablished, and
   I am quoting it as such rather than relying on it.
5. **No production leg set exists, so §3's mechanics are established over the leg sets that exist.**
   Adoption changes the mechanism — by design (probe §4(e)) — and that is the point of §3.3, but it
   means §3.1's finding is a statement about **today's** tree.
6. **This packet reuses `RECOMMENDATION-…` Part 6 F1's rank result without re-deriving it.**
7. **I have not graded any of this**, and by `BEN-381` I should not: the lane that measures does not
   grade. The independent assessor reviews; I did not ask it for a remedy.
8. **⚠ THE WITHDRAWAL CHECKER WAS NOT EXTENDED TO THIS NINTH WITHDRAWN CLAIM, AND THAT IS A REAL
   HOLE, NOT A TIDY EXEMPTION.** `state/check-withdrawal-completeness-20260910.py` pins **8**
   withdrawn claims × 3 delivery files = 24 counts. §1's withdrawal of the `cause3_corr`-hazard
   answer is the **ninth**, and it is **not pinned** — the instruction to stop extending that tooling
   is explicit and I am following it rather than reinterpreting it. **Consequence, stated plainly:
   the correction in §1 and in `CATALOG.md` rests on a manual edit that nothing re-checks**, so if a
   later lane reintroduces *"`cause3_corr`'s hazard is unrealized"* the checker will stay green. The
   detector that would have caught it is the one the checker already implements (a paraphrase count
   that goes **up**, not down, on an incomplete withdrawal). **Whoever is authorised to extend that
   instrument should add the ninth claim; I am not, and this row is the handoff.**
9. **⚠ REV. 2 CORRECTED TWO OF MY OWN CLAIMS, both in §2.1, both found by a peer refusing a phrase
   rather than by any check I ran.** (a) I attributed Z's `C_ML` to `combine_seedscan_split.py` — a
   **3D** script referenced by **no launcher** — so rev. 1's producer "asymmetry" compared Z's
   producer against a script Z does not use, and is void. (b) *"No artifact records either field"*
   was overstated: the declared id sets **are** in tracked launchers and `--expected-ids` is
   `required=True`. What is missing is an embedded stamp plus **one binding** — digest to producing
   execution — and **I did not search Slurm records, receipts or logs for it.** I am not claiming
   that search would fail; it has not been attempted. See §2.1a.
10. **`B` in §4.4a rests on an iid-Gaussian replica model.** Stated as an assumption, not measured
   here. If the replicas are not iid Gaussian the floor moves, and the direction is not established.
11. **The population pin moved 542 → 543** and I re-pinned it. Verified by **set difference on the
   tracked path lists**, not by the count: exactly one path added, none removed. A re-pin is not an
   extension, but it is a deliberate act on an instrument and it is recorded here rather than left
   in a diff.

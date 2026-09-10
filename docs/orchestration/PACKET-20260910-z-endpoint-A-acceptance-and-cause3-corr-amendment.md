# Endpoint-A acceptance, the `cause3_corr` amendment, and the criterion on the released error bars

**Owner:** `z-criteria-owner` lane (proposed Z scientific-criteria owner).
**Base of measurement:** `6f24fb00` (`origin/main`). Every file this packet quotes is **byte-identical
at `6f24fb00` and at this lane's tip** — verified by `git diff` over the nine named paths, empty.
**Predecessors, and ⚠ THE SHA THAT IS SAFE TO READ IS NOT THE SHA THAT IS FAMOUS:**
- `RECOMMENDATION-20260910-z-scientific-acceptance-criteria.md` — **read at blob
  `1b26e96d36d828223b0ee538493176beeb627e0f`, NOT at `2ebdf095`.** ⚠ *Rev. 2 wrote "at the lane
  tip" — **a definite description that re-points, in the header whose whole subject is pin
  discipline.** Caught in review. The blob id is the thing that cannot drift; the commit message
  named it and the header did not.* Measured: the blob is `98f22b3f…` at `2ebdf095` and moved in six later commits
  (`3e6fb5b1`, `0d68b0c2`, `9b7380e7`, `c3a6dfd5`, `17f2ac67`, `cebcd995`; **+564 / −43**).
  **`2ebdf095` still answers `cause3_corr` by ρ-domination — withdrawn in `9b7380e7`, and its
  successor withdrawn again in §1 below.** So `2ebdf095` is a referent for **one** thing only: what
  the independent assessor assessed in round 1. It is not a source for current content.
- `PACKET-20260910-z-consumer-set-and-endpoint-requirements.md` (`173baf44`) — the assessor's
  referent, kept intact; **its §3 carries a withdrawal banner rather than a rewrite.**

Neither is superseded as a whole; this packet **withdraws one answer in the second** and adds to both.
*A commit sha beside a document is not a claim that the document is current, and "byte-identical" is
meaningless unless it names **both** endpoints of the comparison. Rev. 1 of this header named one.*
**Evidence:** `state/probe-z-projected-stability-20260910.py` — green, **59 checks** (37 + 22
added in rev. 3 to verify the round-1 findings against my own claims), run at this tip.

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

## 0. ROUND-1 REVIEW RESPONSE — seven findings, and what each did to this packet

**Independent review at `05bf8647`: a mathematical reviewer (F1–F6) and the independent assessor
(F7), neither supplying remedies, so both retain their verdict on this revision. I re-measured
every finding rather than accepting it; all seven reproduce.** My figures differ from theirs in the
third digit where constructions differ, and I report mine.

| # | finding | disposition |
|---|---|---|
| **F2** | §4.4 and §4.4b ask two incompatible questions | ⚠ **UPHELD. §4.4b's "supply `S`" is WITHDRAWN.** §4.4's derivability claim is *also* withdrawn — it was wrong twice over (§4.4c) |
| **F1** | `B` is computed on the wrong population | ⚠ **UPHELD, `B` withdrawn as a floor for `s_proj`.** Reproduced: null `s_proj` median **38.73%** vs `B` = **7.107%**, ratio **5.45**; control at `K=1`/one functional gives **0.97**. **And the direction REVERSES with replica-draw sharing** (4.78 → 3.38 → 1.73 → **0.84**), so `B`'s adequacy is undecidable without a sharing declaration A-6 does not require |
| **F7** | the sample-covariance population is **three**, not two | ⚠ **UPHELD, and it is the most serious.** §2.1 omitted the flux band **and asserted the wrong normalization for it** — inside a *disclosure* requirement |
| **F3** | the singularity claim is verified on a benign operand | ⚠ **UPHELD.** Reproduced: of 500 near-null functionals, **103 do not abort at all**, dividing by a round-off positive; **391** abort with a message blaming the *operand*; the message §4.3 advertised fires **6** times |
| **F4** | the support residue conflates two mechanisms | ⚠ **UPHELD.** A **covariance** support loss saturates at **exactly 1.0** and names the functional — not silent. Only the **M-change** direction is blind |
| **F5** | `B` is per-bin, `S` is a scalar, `B ≤ S` names no reduction | **UPHELD** — moot for `B`, which is withdrawn, but the reduction question transfers to its replacement and is answered in §4.4d |
| **F8** | a round-off-positive baseline inside an acceptance statistic is required by **nothing** | ⚠ **UPHELD as a GAP in the requirement set, and the closing requirement is proposed in §4.3a.** Verified: `:429` gates on **exactly-empty** `M` rows while `:412-413` describes a **near-zero** hazard, and `s_proj` gates on **exactly-zero** while F3 shows the hazard is **round-off-positive** |
| **F6** | clause (d)'s mootness argument fails | **NOT MY CLAIM — and I am not adopting it as one.** *"Clause (d)"* and *"moot"* appear **nowhere** in any of my three artifacts (grep, all three, zero hits). The reviewer is flagging **someone else's** inference, and correctly names **my A-4 row as what refutes it.** I confirm that refutation and add the robustness property it earned — see §4.1a |

### 0a ROUND-2 REVIEW RESPONSE — F9–F18, all ten re-measured, all ten reproduce

| # | finding | disposition |
|---|---|---|
| **F10** | A-6(a) re-issues committed, delivered work | ⚠⚠ **UPHELD IN PART, THEN INVERTED — and the inversion is the finding.** `PROVENANCE-20260822` is on main with all four fields for every block **including `Flux`**, so **F7 was not a discovery**, my rev.-3 *"refinement of my own"* was already at its `:126`, it holds a block I **still** lack (`2p2h`, N=3), and it identified my §2.1a(b) gap at `:157`. **But its evidence for `N` is `:167,168` — the MEMBER-LOCAL combines, measured at 3 of 100 and 0 of 24 the same day.** Right values, wrong arm. **So A-6 DUPLICATES on fields and REPAIRS on evidence**, and A-6(b) is load-bearing rather than leftover. §2.1 |
| **F13** | A-1's *"fifteen"* reject conditions is **nineteen** | ⚠ **UPHELD.** Enumerated: `1 2 3 4 4b 4c 5 6 7 8 9 10 11 11b 11c 12 13 14 15`. **`4c` is the condition my own §3 depends on** — I declared a fixed set excluding it, in the same document |
| **F17** | A-6's field list exceeds Ruling 2's under a Ruling-2 heading | ⚠ **UPHELD. CHOICE MADE: the sharing structure is an A-7 PRECONDITION on `B'`, not an A-6 disclosure.** It sizes a floor; it discloses nothing about the released object; **it therefore needs no extension of Ruling 2.** A-6 returns to exactly four fields |
| **F15** | §5's disposition right, characterization backwards | ⚠ **UPHELD in both directions, and one of my two qualifications is FALSE.** Clause (ii) does not reach 2D; *"LIVE"* unestablished; `inv` does **not** raise on a near-singular operand. `do-not-change` survives on **different grounds**. §5 |
| **F11** | A-3 does not enforce the per-bin tolerance it is derived from | ⚠ **UPHELD.** At `ε = 1e-9` a bin at `\|x_j\| = 2.11e-06` passes with **103%** per-bin error. **The declared per-bin standard is enforced by no endpoint-A criterion** |
| **F14** | A-2 grounds one declaration and requires four | ⚠ **UPHELD. A-2 narrowed to clause (iv)** — the only one its own sentence argues for |
| **F9** | §2.1a's *"DECISIVELY"* contradicts §2.1a's own withdrawal | ⚠ **UPHELD.** My withdrawal reached (ii)'s heading and body and **not** the reason carrying the routing. Weakened to the true version; **the conclusion is unharmed** |
| **F12** | residue 4 **under**-claims | ⚠ **UPHELD — a rejection filed as judgement is PROVEN.** `s_corr` is scale-invariant: `~1.5e-16` while bars move to **200%** |
| **F18** | `B'`'s quantile level is undeclared, and **is** the null NOT-MET rate | ⚠ **UPHELD; rev. 3's *"needs no new scientific input"* withdrawn as stated.** `q` **declared at `0.99`**, with its class stated **conditionally**: a conditioning parameter **only because `δ_proj = B'` is forbidden**; if anyone sets `δ_proj = B'` it becomes a false-failure-rate declaration and reverts to Joseph. §4.4e |
| **F16** | §7 has one culpable absence | ⚠ **UPHELD.** No released projection names its **builder and commit**, while four non-equivalent builders exist and a **committed** finding records they diverge on refusal. Now residue 13 |

**⚠ THE PATTERN ACROSS BOTH ROUNDS, STATED BECAUSE IT IS THE MOST USEFUL THING HERE.** Of the
seventeen findings, the ones that cost most were not wrong measurements — they were **right
measurements over a population or an operand I had not re-identified**: a diagonal after a
projection (§1), a producer at the wrong dimension (F-Q4), a population that did not recurse into
`Σ_V` (F7), a noise floor for a single bar compared against a max (F1), a fixed set that excluded
its own load-bearing member (F13), and now **a whole deliverable I re-commissioned because I never
searched for it** (F10). **Six instances, one shape.**

**One thing the review confirmed that I want stated as plainly as the corrections:** §4.1's table,
the `+37.8%` figure, the `einsum`/`diag` identity, and §1/§1.1's five-consumer resolution
**including the C6/C7 asymmetry** were all attacked and all held. The reviewer reports trying to
break C7's diagonal-only status and failing. That asymmetry was the part of §1 I was least sure of.

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
| **A-1** | construction | SPEC §1.3a algebra, §1.3b identity set incl. the `g^c` reconstruction gate, and §3.3's reject conditions — ⚠ **NINETEEN, not "fifteen" (F13).** Enumerated at `6f24fb00`, `SPEC:1242-1295`: `1 2 3 4 **4b 4c** 5 6 7 8 9 10 11 **11b 11c** 12 13 14 15`. **`4c` is the condition §3 of this document DEPENDS ON** — §3.1(e) cites `reject_conditions=('4c',)` by name, and §3.3's *"costs nothing today"* is true **because 4c bites**. So rev. 1–3 declared a fixed set that excluded the very condition the same document relies on. `11b`/`11c` are marked rev.-16 additions, so *"fifteen"* was a **pre-rev-16 count quoted after the work that changed it.** The class (FIXED by spec, not reopened) is unaffected | FIXED by spec, **count corrected** |
| **A-2** | provenance | ⚠ **NARROWED TO CLAUSE (iv) (F14).** Rev. 1–3 required all four of `app_statmethods.tex:645-658` clauses (i)–(iv) on an endpoint that **performs no inversion**. Measured against that: **(i)** has no inverse to declare and **(ii)** no `ndf` — both are unsatisfiable except as *"not applicable"*, the form Ruling 2 already uses for `p`; **(iii)** a rank-truncation scan is a **NEW MEASUREMENT** on a 10,694-bin object, i.e. new compute, which A-set requirements must not need; **(iv)** transfers cleanly and **is the only one A-2's own sentence argues for** — *"the 5D candidate, its 4D projection and the published 2D block have different ranks."* **Requiring four while grounding one was inversion-grade criteria reaching an endpoint that releases no significance** | CONFORMANCE, **(iv) only** |
| **A-3** | numerical reproducibility | `r_null = ‖x_cv2 − x_cv‖/‖x_cv‖` over the reported support, **`ε = 1e-9`**. ⚠ **WHAT IT ENFORCES, CORRECTED (F11): an L2-aggregate property of the CV pair — NOT Joseph's declared per-bin `REPRO_RTOL_PER_BIN`.** §C.3's inequality runs `r_null ≤ max_i|Δ_i/x_i|`, so `ε` on `r_null` is **never stricter** than the same numeral per bin; §C.3 called that *"the conservative one"*, which is true for false **failures** and **inverted for an acceptance gate**, where the risk is false **passes**. Measured on 10,694 bins at `ε = 1e-9`: a single bin with `|x_j| = 2.11e-06` gives `r_null` inside `ε` while its per-bin relative error is **1.03, i.e. 103%**. The `rep` predicate is `cv > 0`, so `|x_i|` has **no lower bound** and the gap is unbounded in principle. **⚠ So the declared per-bin standard is enforced by NO endpoint-A criterion**, and rev. 1–3's row read as if A-3 enforced it | PROPOSED, **claim narrowed** |
| **A-4** | declaration stability | retained rank and retained-subspace projector gap across members, `‖P_0 − P_k‖_2 ≤ 1e-8`. ⚠ **NARROWED BY §4.1: this bounds the subspace and is SILENT on the released error bars** — not a partial guarantee about them. ⚠ **AND ITS TOLERANCE IS NOT LOAD-BEARING (§4.1a):** the statistic is ~binary (round-off vs exactly `1`), so every value in `[1e-12, 1e-3]` behaves identically. **It restates `RECOMMENDATION:392` clause (d)'s test with NO dependence on the ρ bound, so outcome (2) did not retire it** | PROPOSED, **narrowed** |
| **A-5** | PSD | *"no eigenvalue below `−k·λ_max` for a declared `k`"*, never *"PSD"* or *"λ_min ≥ 0"*. `adopt_unified_5d.py:150-165` already uses `ev[0] >= -1e-12*ev[-1]`; the requirement is to make it a **receipt-recorded gate** with `k` declared | PROPOSED |
| **A-6** | finite-ensemble disclosure — **from Ruling 2, and ⚠ MOSTLY ALREADY DELIVERED** | §2.1, F10. **Ruling 2's FOUR fields, and exactly four** — `N`, convention, effective `p` (**not applicable** at A), finite-ensemble treatment. ⚠ **`PROVENANCE-20260822` on main already records all four for every block including `Flux`**, so A-6(a) **DUPLICATES** it — but **A-6(b) REPAIRS it**: that record evidences `N` from `:167,168`, which at `6f24fb00` are the **member-local** combines measured at **3 of 100** and **0 of 24** the same day (F10). **Right values, wrong arm.** So part (b) — **binding each product digest to its producing execution** — is the load-bearing half, and the defect it prevents is already instantiated in the committed record. ⚠ **The replica-draw sharing structure is NOT an A-6 field** — it moved to A-7 (F17), because Ruling 2 does not mandate it and presenting it here would read as conformance while being an extension | **REDUCED to (b)** |
| **A-7** | **stability of the RELEASED error bars** — NEW, from Task 3 | §4.3. `s_proj` over the declared functional set. ⚠ **The REPLICA-DRAW SHARING STRUCTURE is an A-7 PRECONDITION here, not an A-6 disclosure (F17):** it is needed to *size `B'`*, not to disclose a property of the released object, and it therefore **requires no extension of Ruling 2**. **Statistic proposed; boundary WITHHELD — and the ask is "NAME THE CLAIM", not "supply a scalar" (§4.4c).** Requires: a **declared relative degeneracy predicate** on each functional's baseline, evaluated **before** any PSD assertion and naming the **functional** (§4.3a, F8); and an `M`-change precondition (§4.3, F4). Its **floor** is the null quantile of `s_proj` itself, **not** a per-bar noise figure (§4.4d, F1) | PROPOSED (statistic only) |

### 2.1 A-6 — and why Ruling 2 lands on A rather than B

**The block population is CLOSED and DERIVED, not enumerated by hand.** `z_assembly.py:4` states Z's
construction:

    C_Z^c  =  D_Z^c (Σ_V C_b) D_Z^c  +  Σ_R C_b  +  Σ_A L_b  +  C_stat  +  C_ML

> ## ⚠⚠⚠ F10 (REV. 4) — **A-6(a) RE-ISSUES A DELIVERED RULING-10 DELIVERABLE, AND F7 BELOW WAS NOT A DISCOVERY**
>
> **`docs/orchestration/PROVENANCE-20260822-declaration-v-scalar5d-blocks.md` is on `origin/main`
> at `6f24fb00` — 367 lines, filed 2026-08-22 under Joseph's ruling 10, whose scope is A-6's four
> fields verbatim.** I verified it exists and read it. **My rev.-3 packet cites it nowhere.**
>
> **What it already contains, measured — and this is worse than the finding as it was relayed to me:**
>
> | | already in the committed record |
> |---|---|
> | `C_stat` / `C_ML` | `:143-144` — **N = 100 / 24, unbiased `1/(N−1)`, `p` —, none applied.** Identical to my §2.1 on every field |
> | the *"enforced, not merely declared"* argument | `:146-150`, from the **same** `load_replica_manifest` raise, citing `replica_manifest.py:41-47` |
> | the launcher enumeration | `:150` already names `run_budget_5d.sh:15,17` and `sbatch_combine_5d_budget.sh:14,16` as *"three concordant"* sources |
> | ⚠ **the FLUX band — F7's "discovery"** | `:128` — **`Flux` (PPFX), N = 100, biased `1/N`, none applied**, *"the one genuine multiverse draw in `C_syst`"* |
> | ⚠ **my rev.-3 "refinement of my own"** | `:126` — the two-endpoint knob bands, *"a `±1σ` endpoint pair is a **deterministic rank-1 outer product with no sampling noise**"*. **I presented that as mine.** It was already there |
> | ⚠ **a block I STILL do not have** | `:127` — **`2p2h`, N = 3, biased `1/N`**, with the record explicitly declining to classify it random-vs-deterministic. Neither my §2.1 nor F7 has it |
> | ⚠ **and another** | `:129` — `__Normalization_flat`, deterministic rank-1, `n = null` |
> | ⚠ **my §2.1a(b) gap** | `:157` already records both digests and says the census *"records no ensemble size"* |
>
> **Its census arithmetic closes: `42×2 + 3 + 100 = 187 = census.n_files_grouped`.** ⚠ **Note the
> decomposition is NOT mine and must not be merged with it:** that census is
> `analyze_universes_5d.py`'s band inventory (42 pair bands), while my §2.1 reads `VERT_BANDS` (13,
> the unified-throw vertical set). **Two different decompositions of `C_syst`; conflating them
> would manufacture a fourth error**, so I state both and reconcile neither here.
>
> ### ⚠⚠ AND THE ANSWER IS **REPAIR** — a fourth option neither the finding nor I had on the list
>
> **A-6(a) duplicates ruling 10's FIELDS. A-6(b) REPAIRS ruling 10's EVIDENCE. So A-6 is not
> redundant work.** Found by the assessor, and I verified both legs myself — which mattered, because
> this conclusion favours me and reverses the one I had drafted.
>
> **Leg 1.** `PROVENANCE-20260822` evidences `N` from `sbatch_finalize_5d_bkgaware_gpu.sh:167,168`.
> At `6f24fb00` those `--expected-ids` invocations sit at **`:422,423`**, and `:417`'s own comment
> reads ***"THE TWO MEMBER-LOCAL COMBINES"*** — they glob through `mr_prefix`. **So that record,
> followed forward into the current tree, evidences `N = 100/24` from the MEMBER-SCOPED arm — the
> arm §2.1a argues cannot have produced the digested bytes.**
>
> **Leg 2, and it is sharper.** `RUNBOOK-20260822-b1-lift-preflight.md:575-576` — same tree, **same
> day** as the provenance record — measures those exact two calls:
>
> | call | validator | found |
> |---|---|---|
> | `:167` `STAT_COV` | `--expected-ids 1-100` over `<member>/boot_nd_5d/…` | **3** of 100 |
> | `:168` `ML_COV` | `--expected-ids 1-24` over `<member>/seedscan_split_5d/…` | **0** of 24, and the directory is **absent entirely** |
>
> *"Verified across all three members 2026-08-22."* **So ruling 10's record cited, as its evidence
> for `N = 100` and `N = 24`, an invocation whose populations were 3 and 0 on the day it was
> written.** Its **values** are right — they match the **top-level** arm, complete at ids `1..100`
> and `1..24`. Its **cited evidence names the wrong arm.**
>
> **THE FOUR-WAY ANSWER, STATED RATHER THAN LEFT TO A READER:** Ruling 2's A-6 **DUPLICATES** ruling
> 10 on the four fields, and **REPAIRS** it on the evidence. **Not supersede** — the values stand.
> **Not extend** — no new field. **⚠ The composition itself is Joseph's to pin**, and I am not
> settling it; what I am doing is naming it, because *a record that does not state its relationship
> to the prior deliverable will be read as duplicating it* — which is what F10 first said, and what
> the evidence does not support.
>
> **⚠ AND THIS IS WHY A-6(b) IS THE LOAD-BEARING HALF, not the leftover.** Part (b) asks that each
> product digest be bound to its producing execution. Ruling 10's record shows exactly what goes
> wrong without it: **a correct value evidenced by the wrong arm, undetectably**, because `N` is a
> count and both arms declare the same ranges (§2.1a). **The defect part (b) prevents is already
> instantiated in the committed record**, which is stronger evidence for the requirement than any
> argument I made for it.
>
> ## ⚠⚠ F7 (REV. 3) — THE POPULATION IS **THREE**, AND REV. 1/2's NORMALIZATION CLAIM WAS FALSE OF THE THIRD
>
> *Kept because the correction to rev. 1/2 stands on its own; **but see F10 above — none of it was
> new**, and one paragraph of it claimed originality it did not have.*
>
> **Rev. 1 read: *"Exactly two summands are sample covariances: `C_stat` and `C_ML`."* That is
> false, and the second half of the error is worse than the first.** Raised by the independent
> assessor, re-verified here end to end in tracked code.
>
> **The chain, measured:** `adopt_unified_5d.py:42-43` — `VERT_BANDS` has **13** entries and the
> 13th is **`"Flux"`**; `z_contract.py:66` re-exports the same tuple with the comment *"V, 13 --
> inflated through `D_Z`"*; so `Σ_V C_b` in `z_assembly.py:4` **carries the flux band, inflated**.
> `unified_throw_cov.py:467` builds `C_flux = mat_covariance(...)` over the flux universes and
> `:468` does `C_block += C_flux`. And `uq_math.py:96` — *"MAT production convention: universe-mean
> centered, **biased 1/N**"* — returns `(Z.T @ Z) / X.shape[0]`. **Verified numerically, not read
> off the docstring: it matches `Z'Z/N` and does NOT match `Z'Z/(N−1)`.**
>
> **So the worse half:** rev. 1's table asserted **one** convention for the whole population —
> *"unbiased `1/(N−1)`… one script, one convention"* — **which is false of part of Z's own sum.**
> Omitting a block is incompleteness. **Asserting the wrong convention for it, inside a requirement
> whose entire purpose is disclosure, is affirmatively misleading**, and that is the failure mode
> A-6 exists to prevent. `unified_throw_cov.py:470` even *prints* `"MAT mean-centered 1/N"`.
>
> **⚠ THE DIAGNOSIS, AND IT INDICTS THE THING I WAS PROUDEST OF.** Rev. 1's boast was *"CLOSED and
> DERIVED, not enumerated by hand."* Reading the formula's surface is correct as far as it goes —
> `C_stat` and `C_ML` are the only sample covariances **named** in it. But **`Σ_V C_b` is itself a
> sum, and the third sample covariance sits one level inside it.** The population question recurred
> one layer below where I answered it. **A derivation is not safer than an enumeration unless it
> recurses** — and the derivation is what supplied the false confidence. Third instance of this
> exact shape in this one document, after §1's projected diagonal and §2.1's wrong `C_ML` producer.
>
> **One refinement of my own, from re-reading `:460` (the 12 knob bands) together with `:467`
(flux) — ⚠ `:460` alone reaches only 12 of the 13:** `mat_covariance` is applied to **all 13**
> vertical bands — the 12 knob bands over their two declared `±` endpoints, and flux over its
> universes. **All 13 therefore carry the biased `1/N` normalizer.** But a two-point `±` endpoint
> pair is a *deterministic* construction, not a random ensemble, so it has no ensemble size to
> disclose and no sampling noise in A-7's sense. **Ensembles proper: three. Constructions sharing
> the biased normalizer: thirteen.** Both belong in the disclosure; only the first three carry `N`.
>
> **`C_unified` (`N = 160`) is NOT added, and the assessor explicitly did not ask for it** — it
> scales the sum through `g` rather than entering as a block. Recording the restraint because the
> boundary is a real one and a later reader may re-litigate it.

**Three summands are sample covariances with a random ensemble: `C_stat`, `C_ML`, and — one level
inside `Σ_V C_b` — `C_flux`.** So clause (v)'s *"for every sample-covariance block entering the
sum"* has a population of **three**, and the derivation only reaches it if it recurses into the
inner sums.

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
| **normalization** | `combine_cov_nd.py:20` `C=(Z.T@Z)/(Xr.shape[0]-1)` → **unbiased `1/(N−1)`** | **same line, same script** | **NO — a code fact, not a recorded one** |

**⚠ AND THE THIRD BLOCK, which the table above does not cover and rev. 1/2 omitted entirely:**

| field (clause (v)) | `C_flux` |
|---|---|
| **declared ensemble** | the flux universes, count derived from the bank inventory at `unified_throw_cov.py:126` (`n_flux = len(expected_flux)`), **fail-closed in both directions** at `:120-125` and again at `:461-465`. `OI-137` records it as the PPFX universe set |
| **normalization** | ⚠ **BIASED `1/N`** — `uq_math.py:96-104`, `mat_covariance`, `(Z.T @ Z) / X.shape[0]`. **Different from the other two blocks.** Verified numerically |
| **effective `p` inverted** | **NOT APPLICABLE at endpoint A** |
| **finite-ensemble treatment** | none applied; must be stated explicitly |
| **recorded where?** | the count is **inventory-derived and fail-closed**, so it is the best-evidenced of the three; the convention is printed at `:470` and **not persisted** |

**So A-6 must disclose, per block, a convention that is NOT common across blocks** — two blocks at
unbiased `1/(N−1)` and one at biased `1/N`. A single sentence covering "the sample blocks" cannot
be correct, which is precisely the shape rev. 1 shipped.
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
than assumed.** The per-block candidate set, ⚠ **corrected in rev. 4 and now exact, because the whole
point of the enumeration is that code alone cannot say which execution produced the digested bytes**:
`sbatch_combine_5d_budget.sh:14` / `:16`; **`run_budget_5d.sh:15` (`C_stat`) and `:17` (`C_ML`)** —
*rev. 2-3 cited `:18`, which is the `--out` CONTINUATION line, so the `C_stat` invocation went
uncited*; and `sbatch_finalize_5d_bkgaware_gpu.sh:422` (`C_stat`) / **`:423`** (`C_ML`). A covering
search also finds `run_ai1_combine.sh:13` (ids `1-12`), the 4D pair and the two FPS launchers —
**different globs, tags and products, so not competitors for these two digests.** — and **the
member-scoped site is
MEMBER-SCOPED**, its glob passing through `mr_prefix`, so it reads a per-member replica directory
rather than the top-level one. **The declared id range is the same; the population it ranges over is
not.** Code alone therefore cannot say which execution produced the digested bytes. *(No value from
the member-scoped tree is quoted here — only the launcher line.)*

**⚠ AND (a) CANNOT SUBSTITUTE FOR (b), for a reason sharper than "the search was not done":
`N` IS A COUNT, AND A COUNT CANNOT IDENTIFY A POPULATION.** Two ensembles of equal cardinality are
indistinguishable by cardinality. So A-6 part (a) is satisfiable **in full** — declared id set,
verified `N`, convention, treatment — while the **producing arm remains unnamed**, across a
boundary at which the seed contract changed. Contributed by the assessor and adopted: it does not
contradict §2.1a, it removes the escape route by which (a) might have looked sufficient. The
committed record is reported to carry the equal-`N` fact already (`OI-160`), which is why this is a
naming problem rather than a counting one.

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
3. ⚠ **REV. 4 WEAKENS THIS, BECAUSE REV. 2's VERSION CONTRADICTED §2.1a THIRTY LINES BELOW IT
   (F9).** Rev. 2 asserted, under the word **DECISIVELY**, that *"if `N` is not recorded at
   construction time it is unrecoverable"* — while §2.1a(ii), headed *"I SHOULD NOT HAVE IMPLIED
   IT"*, establishes the exact counterexample: `N` **is** recoverable with no stamp and no replica
   files. **My own withdrawal reached the heading and body of (ii) and not the reason carrying the
   A-versus-B routing** — a withdrawal that stops at the site it was written for, which is a shape
   this campaign has a standing rule about. **The true version, which still routes A-6 to A:** the
   artifacts recovery depends on — the producing launcher and its execution record — are
   **construction-time** artifacts. Weaker, and sufficient. **Reasons 1 and 2 are independent of
   this and unaffected. A
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

**⚠ AND "INERT" UNDERSTATES IT — the assessor's strengthening, adopted.** *"Inert"* reads as
contingent, as though the entry happened not to matter. It is **structurally unreachable**: a
boundary is looked up at exactly two places, `z_validator.py:247` inside `assess` and `:110` inside
`describe()`, **and both are keyed on the declared legs.** A boundary no leg names is reachable from
neither the outcome nor its description. That is the *mechanism* behind the byte-identity result
rather than a restatement of it.

**⚠ AND THE BYTE-IDENTITY RESULT NEEDED POSITIVE CONTROLS THAT REV. 1 DID NOT CARRY.** A
byte-identical `describe()` with no positive control is exactly the shape of a check that cannot
fail — my own catalogued rule, and I missed it on my own result. Both controls are the assessor's,
now **executed in probe §11**: **(A)** deleting a *declared* leg's boundary (`cause3_agg`) **raises
`ZContractError`**, proving `assess` does consult the registry at assess time, so §3.1(c)'s identity
is a **real negative** and not a blind one; **(B)** the scope statement flips present → `None` when
a `sees_correlations=True` leg is declared, proving the narrowing is leg-derived. Both pass.

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

### 4.1a F6 — A-4's `1e-8` IS NOT A TUNED NUMBER, and clause (d)'s test survives through A-4

**Two things, and the first is not my claim to withdraw.** *"Clause (d)"* and *"moot"* appear
**nowhere** in any of my three artifacts — grepped, all three, zero hits. The mootness inference is
**someone else's**, and the reviewer correctly identifies **my A-4 row as what refutes it**. I
confirm the refutation and state it here so it is citable:

> **A-4 states clause (d)'s exact test — `‖P_0 − P_k‖_2 ≤ 1e-8` on the retained-subspace projectors —
> as a LIVE endpoint-A requirement with NO dependence on the ρ bound.** `RECOMMENDATION:392` carries
> clause (d) as a sub-clause of the **ρ-leg's** terminal-outcome list, and outcome (2) retired that
> leg's **role**. **Retiring the leg does not retire the test.** Anyone acting on *"clause (d) is
> moot"* drops a live A-4 requirement.

**And on the clause's own logic:** it is correct as a **necessary** condition, and *"MET additionally
requires"* is the right form. It **cannot** be sufficient, for §4.1's own reason — the retained
subspace can be identical while the retained eigenvalues, the quantities `pinv` actually inverts,
move arbitrarily. That is §4.1's counterexample read in the other direction.

**⚠ AND THE TOLERANCE IS NOT LOAD-BEARING — a robustness property, measured (probe §10), and it
improves A-4's footing rather than weakening it.** For orthogonal projectors the statistic is
essentially **binary**:

| case | rank | `‖P_0 − P_k‖_2` |
|---|---:|---:|
| structural match (rescale) | 30 → 30 | **`3.420e-15`** — round-off |
| one retained mode dropped | 30 → 29 | **exactly `1.000000`** |

**Every tolerance in `[1e-12, 1e-3]` separates these identically** — nine orders of magnitude, same
verdict in all of them. **So `1e-8` is not a fitted number and should stop being defended as one:
it is any separator between round-off and `O(1)`.** Rev. 1 called it *"the only justified number
this lane has"*; the honest and stronger statement is that **A-4 needs no justified number at all**,
because it is a structural equality test wearing a tolerance.

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
- **Zero baseline projected sigma** — ⚠ **REV. 1's CLAIM HERE IS FALSE, AND IT WAS VERIFIED ON A
  BENIGN OPERAND (F3).** Rev. 1 said `s_proj` *"ABORTS, not a silent `0/0` and not a pass"*, on the
  strength of an **exactly**-zero baseline (an empty `M` row) over a rank-3-of-12 matrix under pure
  scaling — a case where every functional has healthy overlap with `range(C)`. **Z's case is 265 of
  10,694, where a declared functional can be near-orthogonal to `range(C)`.** Re-measured there,
  500 trials with the functional set to the numerically-null eigenvector (probe §8): **103 do NOT
  abort at all**, passing `base > 0` on a round-off positive (`u'Cu ∈ [−1.1e-15, +2.2e-15]`) and
  **dividing by it**; **391** abort with *"negative quadratic form — C is not PSD on these u"*,
  which **blames the operand when `C` is PSD and the FUNCTIONAL is what is degenerate**; and only
  **6** give the message rev. 1 advertised. **So the abort guarantee holds at EXACT zero and fails
  at round-off.**
  **⚠ And a second half: the declared predicate is not the predicate the code tests.**
  `ew_coverage_report:55-68` tests **empty destination rows of `M`**; `s_proj:221` tests
  **`m_iᵀ C m_i > 0`**. At rank 265 of 10,694 these differ — a bin with a perfectly supported `M`
  row can still have negligible overlap with `range(C)`. **A-7 therefore needs a declared
  degeneracy predicate on `m_iᵀ C_0 m_i` relative to `‖C_0‖`, not a support predicate on `M`**, and
  that requirement is new in rev. 3 rather than inherited.
- **Support-changing members** — ⚠ **REV. 1 CONFLATED TWO MECHANISMS AND VERIFIED ONE (F4).** The
  probe changed the member's **projection matrix** with `C` untouched, where `s_proj` is correctly
  silent. The prose then generalised to *"a destination bin appearing or vanishing"*, which covers
  a second mechanism it never tested. Measured (probe §9): when the member's **COVARIANCE** loses
  support on a declared destination bin, `s_proj` is **NOT silent — it saturates at exactly `1.0`
  and names the argmax functional.** So:
  **the blind spot is an `M`-change only**, and destination-support identity is a precondition
  **for that mechanism**. One direction verified, one measured and found not to need it.

**Power in both directions, plus a control (probe §6):** exactly `0.0` on identical members;
`14.0175%` when bars inflate (`1.3×`); `16.3340%` when bars **shrink** (`0.7×`) — a filter must act in
the direction it acts; and on a correlation-only change with a bit-identical diagonal, `s_agg` returns
`1.8e-16` while `s_proj` returns `9.4010%`.

### 4.3a ⚠ F8 — THE ROUND-OFF-POSITIVE BASELINE IS REQUIRED BY NOTHING. A-7 must close it.

**This is a gap in the requirement set, not a defect in anyone's text, and it survived two reviews
because each half looks covered from the other's side.** Verified at `6f24fb00` rather than relayed:

- **The hazard is stated in the tree, exactly.** `eavailW_covariance.py:412-413`: *"a zero variance
  does not look like missing data — it looks like a very good measurement, and any `chi2` or
  significance built on it divides by it."*
- **The release-point requirement does not reach `s_proj`.** The assessor's pre-registered F6
  requires *"a released projected row with zero or near-zero variance must be refused or marked at
  the point of release."* Its **subject** is a released row and its **predicate** is the release
  point. `s_proj`'s baseline is an **acceptance statistic evaluated during grading** — not a
  released product. **Wrong stage.** ⚠ **I am NOT citing assessor-F6 as covering the round-off case,
  and it declined that widening itself, against its own interest.**
- **My own abort claim does not reach it either.** §4.3 is exact for an **exactly**-zero baseline and
  **fails at round-off** (F3). **Wrong condition.**

**⚠ AND THE STRUCTURE IS THE SAME DISTINCTION RELOCATED ONE LEVEL DOWN, which is why it hides:**
`:429` gates on `if _ew_empty.size:` — **exactly-empty** `M` rows — while `:412-413`'s hazard is
**near-zero** and is reachable at a **fully populated** row through correlation structure alone.
One level down, `s_proj:221` gates on **exactly-zero** while the hazard is **round-off-positive**.
**Each gate tests the exact case adjacent to the one that bites it.**

**THE REQUIREMENT I PROPOSE, and it must address all THREE cohorts F3 measured, because a
requirement aimed only at the third leaves the first mislabelled:**

> **A-7 must evaluate a DECLARED RELATIVE DEGENERACY PREDICATE on every declared functional's
> baseline, BEFORE any positive-semidefiniteness assertion, and must terminate in a state that
> names the FUNCTIONAL rather than the operand.**
>
> Predicate: **`m_iᵀ C_0 m_i ≥ κ · λ_max(C_0) · ‖m_i‖²`** for a declared `κ`.

| cohort (probe §8, 500 trials) | current behaviour | required behaviour |
|---|---|---|
| **391** | aborts *"negative quadratic form — C is not PSD on these u"* | ⚠ **MISLABELLED — `C` IS PSD; the FUNCTIONAL is degenerate.** Must be caught by the predicate first and reported as a **functional-declaration** failure |
| **6** | aborts *"a predeclared functional has zero baseline uncertainty"* | correct in kind, but reached only at exact zero — must be reached by the **relative** predicate |
| **103** | **does not abort**; divides by `u'Cu ∈ [−1.1e-15, +2.2e-15]` | must be **refused**, never graded |

**`κ`'s CLASS MATTERS AND I AM DECLARING IT: `κ` is a NUMERICAL CONDITIONING THRESHOLD, of the same
class as the applied `rcond`, and NOT a scientific acceptance boundary.** It therefore does **not**
belong in `Z_BOUNDARIES`, is **not** a fourth withheld boundary, and is **not** a decision for
Joseph in the sense `S` is. It should follow the repo's existing `rcond` policy rather than being
argued from scratch — the applied cutoff in the ratified `pinv` path was measured earlier in this
campaign as the **`1e-15` literal**, and that is the precedent for `κ`'s *kind*, not for its value.
**Conflating a conditioning threshold with an acceptance boundary is how a numerical convenience
acquires scientific authority**, so the classification is stated rather than left to a reader.

**Neither review lane can write this**: the assessor would spend its A-7 verdict, and the
mathematical reviewer supplies no remedies by standing constraint. **So it is mine to propose and
both will assess it — the routing happened before the fix was written**, which is the
[BEN-381] ordering and the reason I am not also grading it.

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

### 4.4c ⚠ F2 — REV. 2 ASKED TWO INCOMPATIBLE QUESTIONS, AND JOSEPH WAS BEING HANDED THE WRONG ONE

**UPHELD, and this is the finding that determines what goes to Joseph, so it is resolved first.**
Rev. 2's §4.4 said `δ_proj` *"becomes derivable, by §3.6d's direct form and with no new scientific
decision, at the moment endpoint A declares (i) … and (ii) the claim it supports"*, and gave a rule
(half the smallest adjacent-band fractional gap). Rev. 2's §4.4b said `S` is *"the single scientific
input"* and priced two consequences of **choosing** it. **Under the first nobody chooses anything;
under the second the first's "no new scientific decision" is false.** *"Name the claim"* and
*"supply a scalar"* are different questions with different answers.

**⚠ AND ON RE-EXAMINATION, §4.4's HALF IS WRONG TWICE OVER — so the resolution is not simply
"pick the first".**

1. **`§3.6d`'s δ construction is the printed-precision one I refuse.** §3.6d: *"δ = (half the last
   printed unit) / (the printed value) … is the part that genuinely transfers."* **What I adopt from
   §3.6d is its NORMALIZATION MODEL — direct rather than quadrature — not its δ.** Rev. 2 wrote
   *"derivable by §3.6d's direct form"* and thereby invoked, as a derivation, the very construction
   §4.4 refuses two paragraphs earlier. **Self-contradiction, mine, and not caught by the review.**
2. **The band-ordering rule is over the WRONG QUANTITY.** Band ordering is an ordinal claim about
   the relative sizes of **grouped systematic bands**. `s_proj` measures movement of the **total
   per-bin released bar**. A threshold that protects an ordering among groups **does not bound**
   the total — so §4.4's one concrete rule does not apply to A-7's statistic.

**THE ASK, STATED ONCE:**

> **Name the claim the released projected uncertainty supports.** That is the single input, and it
> is **not** a request for a number.

**And its answer determines part (a) as well as part (c)** — which is why it cannot be replaced by a
scalar. If the claim is *quantitative* (a bar quoted with a stated precision and a scientific
consequence), `δ` follows from that claim's own falsification condition. If it is *ordinal* and over
grouped bands, then **A-7's functional set is wrong as specified** and `U` must be built over the
grouped-band quantity instead. If the released bar supports **no** claim, A-7 has nothing to protect
and should be **reported, not graded**. **§4.4b's priced choices are withdrawn**: they priced a
variable that is not free.

### 4.4d ⚠ F1 — `B` IS THE NOISE FLOOR OF THE WRONG POPULATION. WITHDRAWN.

**UPHELD and reproduced (probe §7).** `B = 1/sqrt(2(N−1))` is the noise floor of a **single bar,
single-sample**. `s_proj` is a **maximum over `K` × functionals of a TWO-SAMPLE difference**. Those
are different populations, so `B` is not `s_proj`'s floor:

| construction (`N = 100`, true `C` identical across members — a NULL) | null `s_proj` | ratio to `B = 7.107%` |
|---|---:|---:|
| `K = 10`, 100 functionals, independent draws | **38.73%** | **5.45** |
| **control:** `K = 1`, **one** functional | 6.91% | **0.97** |

**The control is what makes this a population mismatch rather than a formula error** — collapse
`s_proj`'s population to `B`'s and the ratio is 1. **My algebra was right and my population was
wrong**, which is the same defect as F7 and §1, a third time.

**The consequence defeats the precondition's own purpose:** at `S = 10%`, `B ≤ S` **passes**
(7.1% ≤ 10%) while a **null** object returns `s_proj ≈ 39%` — so A-7 reports NOT MET on an object
where nothing moved, and §4.4b's *"read `B > S` as the ensembles being too small"* is **never
reached**, because the check that would trigger it is computed on the wrong population.

**⚠ AND THE DIRECTION REVERSES, so this is not "`B` is 5× too small".** Measured (probe §7c), as
members share replica draws:

| shared fraction | 0.0 | 0.5 | 0.9 | 0.99 |
|---|---:|---:|---:|---:|
| ratio to `B` | 4.78 | 3.38 | 1.73 | **0.84** |

**So `B` crosses from anti-conservative to conservative, and which side it is on depends on a fact
about the members that A-6 as written does not declare.** *(The reviewer reports its own script had
the opposite sentence written before the numbers came back, and the output falsified it. My
independent run agrees on the monotonicity and the crossing; my per-row figures differ in the third
digit. I also could not reproduce its invariance-in-`f` claim — my construction gives ratios drifting
`8.28 → 5.59` as the variance share falls `1.0 → 0.05`, because a deterministic block enlarges the
baseline bar as well. Reported as a discrepancy, not resolved; the qualitative conclusion is
unaffected either way.)*

**THE REPLACEMENT, and it also disposes of F5.** The floor for a maximum must be the null
distribution **of that maximum**:

> **`B'` = a declared upper quantile of `s_proj` computed under the null "every member statistically
> identical", given `N` per block, `|K|`, `|U|`, the per-bin variance shares, and the replica-draw
> sharing structure.** Simulated at build time; needs **no new scientific input**.

**This answers F5 by construction:** `B` was per-bin while `S` was a scalar, leaving *"which
reduction stands on the left of `B ≤ S`"* unspecified (a toy spread 6.7× between max and min).
**`B'` is a max over the same population `s_proj` is**, so both sides are scalars of the same shape
and no reduction has to be chosen. **Comparing like with like is the whole repair.**

**⚠ `B'` IS STILL NOT `S`.** It is achievability, `S` is acceptability, and `null_epsilon`'s
`min(achievable, acceptable)` was withdrawn in rev. 19 for exactly that substitution. `B'` bounds
`δ_proj` from **below**; naming the claim bounds it from above.

#### 4.4e ⚠ F18 — `B'`'s QUANTILE LEVEL `q` IS A PARAMETER, AND WHOSE IT IS DEPENDS ON A RULE

**UPHELD. Rev. 3 wrote *"a declared upper quantile"* and never said which, nor what declaring it
commits to.** The level moves `B'` materially — reported at ~45% between median and 99th at one
configuration — but **the magnitude is not the finding.** The finding is:

> **If `δ_proj` is set AT `B'` — the bottom of `[B', S]`, which is where a lane under pressure will
> put it — then `1 − q` is EXACTLY the rate at which a perfectly stable object returns NOT MET.**
> Declaring the 95th quantile would declare a **5% false-failure rate**.

**So *"needs no new scientific input"* was true of every input except that one.** Withdrawn as
stated.

**THE CLASSIFICATION, and it is CONDITIONAL — which is the honest form, because the same symbol is
two different things depending on a rule stated elsewhere in this document:**

| if… | then `q` is | whose |
|---|---|---|
| **`δ_proj = B'`** | a **SCIENTIFIC ACCEPTANCE INPUT** — it *is* the null NOT-MET rate | **Joseph's** |
| **`δ_proj` set from the named claim, with `B' ≤ δ_proj` used only as a FEASIBILITY CHECK** | a **conditioning/convention parameter** — how conservatively feasibility is asserted | **mine to propose** |

**And the second is the case, BECAUSE `δ_proj = B'` IS FORBIDDEN** — that substitution is precisely
what rev. 19 withdrew for `null_epsilon`, and §4.4d already bars it. **So `q` is a conditioning
parameter *only because of that bar*, and the bar is load-bearing rather than decorative.**
⚠ **If anyone sets `δ_proj = B'`, `q` reverts to being Joseph's, and A-7 must refuse rather than
silently reinterpret its own parameter.**

**MY PROPOSAL: `q = 0.99`, with two obligations attached.**
1. **Why high is the SAFE direction for a floor** — `B'` enters as `B' ≤ δ_proj`, so a **larger**
   `B'` makes feasibility **harder** to assert. Conservatism here means refusing to call a tolerance
   distinguishable from noise when it is marginal. The direction is the opposite of a tolerance's.
2. **`q` must be reported WITH `B'`, never separately.** A `B'` quoted bare is uninterpretable, and
   the number that would be quoted bare is the one this whole finding is about.

**⚠ AND ONE IMPLEMENTATION CAUTION, adopted from the reviewer and not a finding:** `B'` must be
simulated with the **`|U|` that actually runs**, not the nominal one. §4.3a's degeneracy predicate
does not *remove* functionals — all three cohorts terminate in refusal, so `|U|` is unchanged and
there is no mis-sizing — but a failing declaration must be repaired before a run succeeds, and the
repaired `|U|` is the one `B'` must be sized for.

**WHAT F1 ADDS TO A-6, and it is the actionable part:**

> **A-6 must declare, per sample-covariance block, the REPLICA-DRAW SHARING STRUCTURE across the
> members of `K` — not only `N`.** Two ensembles with identical `N` give `B'` ratios differing by
> **5.7×** between independent and 99%-shared draws, so `N` alone cannot size the null.

**And I am not inventing a sharing figure.** What would measure it, stated exactly: `mr_prefix`
(`lib_member_resume.sh:137-142`) **inserts a member path**, so under the member-scoped arm at
`sbatch_finalize_5d_bkgaware_gpu.sh:422` each member reads **its own** replica directory —
independent draws, sharing ≈ 0 — whereas `sbatch_combine_5d_budget.sh:14` reads a **single
top-level** set. **So the sharing structure is determined by which arm produced the members, which
is the SAME unresolved digest→execution binding as §2.1a(b).** One records search closes both. It
has not been done, and I am not claiming its outcome.

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

> ## ⚠⚠ F15 (REV. 4) — THE DISPOSITION SURVIVES, THE CHARACTERIZATION RAN THE NOTE BACKWARDS
>
> **`do-not-change` stands. But rev. 1–3 overstated in BOTH directions, and one of my two
> qualifications is simply wrong.**
>
> **(1) CLAUSE (ii) DOES NOT REACH A 2D OBJECT, so "non-conformer" inverts the scoping.** The note
> says so twice — `:645` *"must not be used **for an N-D covariance**. Any **N-D** χ² shall instead
> quote (i)…(v)"*; `:636` *"It does not transfer to the N-D covariances."* And `:628-634`
> affirmatively **justifies** the 2D choice: *"dimension-conditional, and justified here by the
> truncation scan — not by convention… the scan is the evidence; 205 is not assumed."* **2D is the
> case where `ndf = n_reported` IS licensed.** So C11 is not a clause-(ii) non-conformer.
>
> **(2) "LIVE" IS UNESTABLISHED.** `RANK-AND-INVERSION-20260810.md:56` verdicts the ours-only
> `χ²/ndf` as *"2D, diagnostic … safe — it is the illustration, not a result"* — and this script's
> branch is the **direct** inverse (`:126` *"no pseudo-inverse"*), so it is not even that
> illustration's source.
>
> **(3) ⚠ AND MY FIRST QUALIFICATION IS FALSE AS STATED.** I wrote *"`np.linalg.inv` is correct at
> full rank."* The inverted object is `Cs = Cu + Cb` (`:117`, `:120`), which the note puts at rank
> **140→201 of 205** (`:693-696`), and **`np.linalg.inv` does not raise on a NEAR-singular matrix —
> only an exactly singular one** — so the `try/except` at `:127-133` does not cover the case. The
> rank is only **printed** at `:124`, so the discriminating measurement exists at runtime and
> nowhere in the tree. *(The assessor does not claim the object IS rank-deficient; it claims my
> antecedent is unestablished. Correct.)*
>
> **(4) My SECOND qualification stands and I keep it:** being out of scope is **not** conformance.
>
> **NET: `do-not-change` survives on DIFFERENT GROUNDS.** Not *"a live conformance defect inside the
> protected 2D scope"* — that told Joseph something false in the alarming direction — but: **a 2D
> diagnostic to which clause (ii) does not apply, whose conditioning is unmeasured, and which Ruling
> 1 does not in any case authorise anyone to touch.** ⚠ **And a diagnostic is not the "validated 2D
> scope" either**, so rev. 1–3 also overstated its protection.

**Ruling 1 preserves the validated 2D scope unchanged, so this is out of scope to change, and the
exclusion is recorded here explicitly** — an unstated exclusion is the failure mode this packet family
has already paid for twice. **Read the F15 box above before citing either qualification below; the
first is withdrawn.**

- ~~`np.linalg.inv` is **correct at full rank**, per N2's control~~ — **WITHDRAWN (F15(3)):** the
  antecedent is unestablished and `inv` does not raise on a near-singular operand.
- Being out of scope is **not** conformance. C11 remains outside the ruling's authorisation; it is
  **not** thereby certified conformant.

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

1. **`δ_proj` is not derived, and the ASK is "name the claim" rather than "supply a scalar"**
   (§4.4c). ⚠ Rev. 2's `S`-with-priced-consequences framing is **withdrawn**; so is its claim that
   δ follows from §3.6d's direct form, which invoked the printed-precision construction §4.4
   refuses. **Naming the claim may also change part (a)'s functional set**, so it is not a boundary
   question alone.
2. **Only the `M`-CHANGE direction of support change is a blind spot** (§4.3, F4). A member whose
   **covariance** loses support on a declared destination bin makes `s_proj` saturate at exactly
   `1.0` and name the functional — measured, not asserted. ⚠ Rev. 1/2 stated the residue over both
   mechanisms having tested one; the precondition is needed for the `M`-change case only.
3. **C6's hazard is CONDITIONAL and the condition is unmeasured.** Whether `coverage_valid_nd.py` is
   ever invoked with a projected `--cov` operand is a question about *invocations*, and no invocation
   record was searched. §1.1 says conditional; it does not say which.
4. ⚠ **REV. 4 CORRECTS THIS — IT UNDER-CLAIMED, IN MY OWN VOCABULARY (F12).** `s_corr`'s
   rejection is **PROVEN, not a judgement**, and proven by a construction already in this document:
   on §4.1's `C_k = (1+a)C_0`, a correlation matrix is **scale-invariant**, so `s_corr` sits at
   `~1.5e-16` while the released bars move `2.4695%` / `41.4214%` / `200.0000%` at
   `a = 0.05 / 1 / 8`. **`s_corr` is exactly zero while the bars move without bound** — which is
   §4.2's stated reason for rejecting it (*"can stay quiet when one does"*), now demonstrated.
   **This matters because §6 is the table a later lane cites to decide what needs re-deriving, and
   a proven leg filed as a judgement invites re-derivation of something settled.** `s_eig` is
   correctly a judgement: it tracks `a` exactly and is rejected on interpretability and cost, and
   its `1-3 min` is a **local** figure with runtime unestablished.
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
10. **⚠ `B` IS WITHDRAWN (F1) and its replacement `B'` is a RULE, not a number.** `B'` needs `N`
   per block, `|K|`, `|U|`, the per-bin variance shares **and the replica-draw sharing structure**,
   and the last of those is **undeclared**. It is not invented here. What would measure it is named
   in §4.4d and is the **same records search** as §2.1a(b). `B'` also inherits an iid-Gaussian
   replica model, stated rather than measured.
11. **✅ RESOLVED IN REV. 4, AND IT RESOLVES TOWARD THE REPLACEMENT.** The `f`-dependence
   disagreement is closed: the reviewer **withdraws *"invariant"*** (it summarised four printed rows
   by the last three), and at 4,000 trials gets `5.24 → 4.83` for `f = 1.0 → 0.01`. **The drift is
   real and my mechanism is confirmed and now mechanical:** `f` *does* cancel in the **scale** to
   two parts in a thousand, and the entire residual sits in the **max/SD ratio** — the shape of the
   null maximum — because at `f = 1` the baseline bar itself fluctuates ~7.1%, so a low `bar_0`
   inflates every relative difference, while a large deterministic block pins it. That is
   *"enlarging the baseline bar"* made precise.
   **⚠ And the magnitude gap was ESTIMAND, not error, on either side:** my `8.28 → 5.59` is an
   **upper quantile over ~10×1000**; its `5.24 → 4.81` is a **median over 10×100**. Both reproduce.
   **The transferable conclusion: the drift is real, it saturates below `f ≈ 0.5`, and no ratio
   transfers without naming the QUANTILE and `|K|×|U|`.**
   **⚠ Which is an argument FOR `B'`, not a footnote about it:** since the ratio moves with `f`,
   with the quantile and with the set size, **no fixed multiplier converts `B` into a floor for the
   maximum**, so simulation is the only route — and that is what `B'` is.
   ⚠ *One correction to my own rev.-3 wording: I described the per-row sharing figures as agreeing
   "in the third digit." `5.17` against `4.78` is **8%**. The estimand/set-size explanation covers
   it, but the agreement is not as tight as I said it was.*
12. **`κ` (§4.3a) is proposed as a CLASS, not a value.** I anchor its kind on the applied `rcond`
   policy and explicitly do not propose a number. If the policy does not in fact transfer, the
   requirement stands and its threshold is open.
13. ⚠ **A CULPABLE ABSENCE (F16): no released projection names its BUILDER and COMMIT.**
   Pre-registered and **unmet and unrecorded** until now. Four non-equivalent builders exist at
   `6f24fb00`, and `FINDING-20260910-projection-builders-agree-numerically-and-diverge-on-refusal.md`
   — **in main** — records that they agree on weights and **diverge on refusal**. The finding is
   committed and the requirement was pre-registered, so this gap is mine and not an oversight I get
   to call expected. **A released projection must name its builder and commit**; without that,
   `s_proj`'s `U` is not identified.
14. **F8's closing requirement is UNREVIEWED BY CONSTRUCTION.** Both lanes were routed to assess it
   before it was written, so it has no independent check yet — that is the intended sequencing, not
   an oversight, but it means §4.3a is the least-tested thing in this document.
15. **⚠ TWO OF THIS DOCUMENT'S STRONGEST-SOUNDING CONFIRMATIONS ARE PARTLY SELF-CONFIRMATION, and
   the assessor declared it rather than being caught.** It contributed material at five sites —
   `:116`, `:166`, `:197`, `:294`, `:346`. It is not recused, because each is a measurement
   re-derivable from the cited lines rather than a remedy. **But `:294` adopts its equal-`N`
   framing verbatim and `:346-347` uses its *"structurally unreachable"* in place of my *"inert"*,
   so those two paragraphs contain its sentences and it cannot be their only reader.** Both are
   routed to the mathematical reviewer as spot-checks. **Recorded here so a later reader does not
   read "confirmed by the assessor" as independent where it is partly the assessor reading its own
   sentence back.** It enumerated all five itself rather than declaring one, which is the behaviour
   that made this visible at all.
16. **The population pin moved 542 → 543** and I re-pinned it. Verified by **set difference on the
   tracked path lists**, not by the count: exactly one path added, none removed. A re-pin is not an
   extension, but it is a deliberate act on an instrument and it is recorded here rather than left
   in a diff.

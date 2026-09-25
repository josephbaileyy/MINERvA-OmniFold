# CATALOG — archive: the scalar-5D campaign's pointer rows, as they stood on 2026-09-24

**This is a CONTINUATION of [`CATALOG.md`](CATALOG.md), not a document in its own right.** It is
declared there by a `CATALOG-CONTINUES` marker, and `live_doc_indexed.py` reads the router and its
continuations together — so a pointer row here indexes its document exactly as one in the router does.

**Why it exists.** These nine sections were the router's scalar-5D pointer list, appended to from
2026-09-02 onward; the covariance they track was adopted on 2026-09-20. They were more than half the
router's lines. **The current scalar-5D entry route is
`CATALOG.md` → `## Current work` → *Scalar-5D — the current entry route*; start there.**

**Moved verbatim on 2026-09-24**, in their original order, by the family recorded in
[`RECOVERY-MANIFEST-20260924-preparation-epoch.md`](RECOVERY-MANIFEST-20260924-preparation-epoch.md) §3.
Section headings, including ones that read *"BLOCKED on five Joseph decisions"* or *"awaiting"*,
are the wording **as written at the time**; they are history, not current state — each governing
record states its own scope and what superseded it. The router as it stood before the move is
`git show evidence/preparation-2026-09-24-bf34a12c:docs/orchestration/CATALOG.md`.

---

### THE SCALAR-5D REQUIRED DELIVERABLE PATH — standing authorization; **BLOCKED on five Joseph decisions** (2026-09-18)

- [`AMENDMENT-20260918-spec-6.4-candidate-specific-null-exception.md`](AMENDMENT-20260918-spec-6.4-candidate-specific-null-exception.md)
  - **✅ EXECUTED 2026-09-18. The NULL row resolves here.** Amends `SPEC` §6.4 and nothing else —
  **it does not revise `SPEC`, which is FROZEN at rev. 22** — and it **adopts nothing, grades
  nothing, moves no count.** §1 records how the route resolved: **P0 returned the like-for-like
  branch** (divergence at **call 0**, `3.27e-16`; `x_cv` differing across invocations at
  `5.33e-15`), which is the branch `PACKET-20260918-scalar5d-completion-inventory-and-null-route.md`
  §2.4 **predeclared before the measurement existed** — so **P2 IS NOT AUTHORIZED and its
  `9.00`–`12.00` CPU task-hours are not spent.** The clause is **candidate-specific, one digest
  (`3d7465f6…`), exhausted by one use**: **(a)** `M(i)` stays **`UNRESOLVED`** with `4c` and no
  later act erases it; **(b)** a retrospective assessment carrying **no grade token** — **PER-BIN**
  reproducibility, max `1.755272e-12` over all 10694 reported bins with **zero** above `1e-10`,
  measured on the persisted `x_cv`/`x_cv2`; global `r_null` `4.452000e-14`, itself stable to
  **0.5%**. ⚠ **The earlier "twelve orders below the 5% tolerance" framing is WITHDRAWN as
  invalid** — `r_null` is a relative change in the CV *vector* and `δ` bounds movement of an
  estimated *σ*; ⚠ **and the replacement comparator is ALSO withdrawn** — *five significant figures* borrows a
  threshold from formatting, which `SPEC` §6.8's `D2` row bars verbatim and whose parent rule
  `D1` records as factually wrong. **The distribution is reported with NO comparator:** max
  per-bin `1.755272e-12`, **zero bins above `1e-11`**, against a feared shape of `4.4e2` —
  **14.4 orders** — with the small-bin trend stated (`ρ = −0.3103`) rather than worked around. Unresolvable only because **a predeclared-tolerance form cannot be constructed
  for an object already built**, not because reproducibility is in doubt; and **"bitwise identity
  is unreachable" is withdrawn as overclaimed** — the probe tested the historical **unpinned**
  configuration, so the true statement is *not demonstrated on the evidence in hand*; **(c)** a
  **permission to decide, not a decision and not evidence.** `null_epsilon` stays **WITHHELD** —
  the clause makes it **moot for the required path, it does not supply it.** Nothing generalizes,
  including to a future rebuild of the same object.
- [`EVIDENCE-20260919-cause7-migration-census-and-declared-policy.md`](EVIDENCE-20260919-cause7-migration-census-and-declared-policy.md)
  - **The §3 bounded-work extraction.** Source `standard/evidence/p4_merged_audit.json`, sha256
  `2e3fac26…`. **Ten of ten endpoints agree with the declared policy** (`p4_lib.py:64-65`), so
  `SPEC:802`'s abort condition does not trigger; `selection_migration_abs = RecoEntrants + RecoExits`
  exactly on all ten. Carries the **per-endpoint sha256 identities**, the extractor's positive AND
  negative controls, and two corrections: **§15.1 is a directory-uniformity census, not a digest
  identity**, and **the 12-playlist hadd coverage is NOT confirmed** by this artifact.
- [`OUTCOME-20260919-computed-acceptance-goal-C-blocked.md`](OUTCOME-20260919-computed-acceptance-goal-C-blocked.md)
  - **(C) BLOCKED, zero task-hours spent.** Acceptance is now COMPUTED and `ε = 1e-9` is declared, but
  **PASS needs branch 3**, which needs `branch2_failures()` empty AND all three cause-3 leg
  statistics — **both require ≥ 2 members**. One further member costs **262 CPU + 158.25 GPU
  task-hours against a 100 CPU cap, 2.6× over.** No production run was submitted: a single-member
  build is foreseeably branch 2, neither PASS nor an assessable FAIL, and would freeze the logic for
  a known answer.
- [`OUTCOME-20260919-cause3-anchor-has-no-eligible-member.md`](OUTCOME-20260919-cause3-anchor-has-no-eligible-member.md)
  - **(C) BLOCKED, zero task-hours, nothing submitted.** Cause 3 needs two members and R6 authorizes
  one; **the second was assumed to exist and does not.** `z-cv.npz`'s precursor is **UNDECLARED**
  (`est_seed_offset_declared = 0` on 61/61 slabs) so it can never leave branch 2; the `k0r2` anchor
  `mii/member_k000000` **is** declared (185/185) but its deploy predates the null-operand writer, so
  it has no `r_null` of its own. **Two properties, two artifacts, neither member has both.**
- [`EVIDENCE-20260919-cause3-member-eligibility-census.md`](EVIDENCE-20260919-cause3-member-eligibility-census.md)
  - The census behind that outcome: **every** slab read by key name, the null-operand search run
  **with a positive control**, the `374/374 COMPLETED 0:0` re-verified from `sacct` rather than from
  a launch plan, and the anchor's `sha256`. Also **one member's measured cost — `86.53` CPU /
  `54.90` GPU against a `262.00` / `158.25` reservation** — and the live risk that the recommended
  `uthrow5d_block` `3.00 h` cap sits **below an observed `4.82 h` task**.
- [`DECISION-20260919-joseph-R6-reverses-the-k1-decline.md`](DECISION-20260919-joseph-R6-reverses-the-k1-decline.md)
  - **Joseph reverses `AUTHORIZATION-20260918` §2 ruling 2, for the computed-acceptance goal only.**
  One additional member at `262.00` CPU / `158.25` GPU, through the normal campaign check. The
  premise *"nothing required needs `N`"* died when acceptance became computed. **Never submitted.**
- [`EVIDENCE-20260919-lateral-bands-are-seed-pinned.md`](EVIDENCE-20260919-lateral-bands-are-seed-pinned.md)
  - **Five of `C_Z`'s 45 bands cannot move with the estimator-seed offset, and the hook is
  structurally incapable of reaching them** — `MNV_EST_SEED_OFFSET` appears **0** times in all six
  files of the active-lateral chain, and `run_p4_unfold_std.sh:111` pins a literal `--seed 42` with
  its own reason (*"MAT ± cancels CV"*). Measured share: **26.0% of `√Tr C_Z`, 6.75% of the
  trace**, dominated by the two muon-energy bands. **So a cause-3 MET covers 93.2% of the trace.**
  Unpinning it is a material change to the estimator and is routed to Joseph, not attempted.
- [`DETERMINATION-20260920-merge-guard-scope-vs-registry-conflicts.md`](DETERMINATION-20260920-merge-guard-scope-vs-registry-conflicts.md)
  - **`merge_guard.sh` REFUSED the 69-commit merge of the clause-(c) verification lane, and the
  refusal STANDS — no override was sought and none exists.** The two conflicts were `CATALOG.md`
  (prose) and `MANIFEST-overrides.tsv` (a path registry), neither of which carries a per-row id, so
  both print `NO ATTRIBUTABLE ROWS` — **declared behaviour**, per the convention's own *"It sees
  rows, not prose"*. Per `RULING-20260908` the only legal exits are remove-the-cause or fix-the-gate;
  the cause is unremovable by this lane, so it is filed as **`OI-189`**. ⚠ States the tension both
  ways and **declines to rule on it**, being the party the guard refused. Resolutions are scripted
  and preserved (union, order-preserving); **do not re-sort `MANIFEST-overrides.tsv`.**
- [`DISCLOSURE-20260920-clause-c-verification-blocked-and-was-not-recorded.md`](DISCLOSURE-20260920-clause-c-verification-blocked-and-was-not-recorded.md)
  - **§6.4 clause (c) is an `iff` — and the independent verification it requires returned `BLOCK`,
  which the adoption record did not say.** The verification exists on
  `lane/z-criteria-independent-assessment-20260910` at `935b7558…`, not on `main`. Its `BLOCK` is
  **`V2` alone and is a WHO-MAY-SIGN block**: C5's and C7's evidence is the assessor's own work
  (`80b464ca`), so signing them would make clause (c) inert — *"Nothing about them is suspect; the
  routing is."* Question (2) returned **PASS on everything reachable**, and `V4` exercised the
  guards with a working positive control. **Recorded as Joseph's omission**: `independent`,
  `clause (c)` and `BLOCK` each occurred **0** times in the adoption record. ⚠ Carries its own
  scoping caveat — `clause (c)` is overloaded (expiry / B1-lift / §6.4) and the assessment quotes
  no clause text, so the identification is **by content, stated as an inference**.
- [`INDEX-20260920-retained-branches-not-on-main.md`](INDEX-20260920-retained-branches-not-on-main.md)
  - The 15 branches retained on `origin` whose content is **not** on `main`, with head SHAs. Its
  first row is the clause-(c) verification above.
- [`LEDGER-20260920-deleted-branch-names-to-sha.md`](LEDGER-20260920-deleted-branch-names-to-sha.md)
  - Name→SHA for the 28 branches deleted on 2026-09-20, so a stale citation still resolves.
- [`DECISION-20260920-joseph-authorizes-typed-descriptor-audit-on-main.md`](DECISION-20260920-joseph-authorizes-typed-descriptor-audit-on-main.md)
  - Joseph authorizes publishing the typed-descriptor audit on `main`, on a **measured and
  corrected** scope (50 `[M60]` payload lines, 10 data-derived) after an earlier asserted count of
  five was withdrawn. It reached a commit by an over-broad `git add`, not by a decision.
- ⚠ **Tag hygiene, 2026-09-20:** a `git fetch --prune-tags` deleted the five local-only tags
  (`freeze/k0-aa67c426`, `z-deploy-{15315e75,20b97fa9,4c9b5066,69cd4eb1}`), which exist on **no**
  remote. **All five were restored to their original commits the same day** — they were lightweight,
  no annotated objects were lost, and the four `z-deploy` commits remain reachable from
  `lane/z-assembly-pilot-20260914`. **Do not run `--prune-tags` against `origin` in this repo:**
  local-only tags are load-bearing here and the flag treats them as stale.
- [`REPORT-20260920-scalar5d-uncertainty-completion.md`](REPORT-20260920-scalar5d-uncertainty-completion.md)
  - **The §7 completion report: adopted source identity, projection receipts, build results, both
  repository heads, and the limitations that remain live.** Declares the **required deliverable set**
  complete — adopted covariance `3d7465f6…`, verified projection `835828bf…` paired **by digest**,
  note/primer/paper built (95/7/4 pp, containment `PASS`) and pushed to both remotes.
  ⚠ **It explicitly does NOT declare publication readiness, resolve any limitation, or quote a
  significance.** §6 carries **seven live limitations**: the `6.145%` seed sensitivity against a `5%`
  bound; the five seed-pinned bands now unprobed **in an unknown direction**; cause 3 predeclared and
  not computed with all seven boundaries `read_by_production: no`; PM-1's provenance gap; that
  weight-only does not establish hadronic-response completeness; clause (c) satisfied in substance and
  **violated in order**; and `V6`'s six items with **no second-lane reproduction**. §7 names what was
  not done, including that `LIVE-STATE.md` is **stale and not regenerable from this machine**.
- [`QUESTION-20260920-hadronic-response-coverage-for-eavail-w.md`](QUESTION-20260920-hadronic-response-coverage-for-eavail-w.md)
  - **PREPARED, NOT SENT.** The focused collaborator question Joseph's 2026-09-19 §5 requires, with
  the full 45-band split it is asked against (A 5 lateral / V 13 vertical / R 27 residual, the four
  at issue named), the upstream reference (Aliaga, NIM A **789** 28), and three sharpened
  sub-questions a yes/no cannot answer. ⚠ Carries the ruling's limits on the answer: **silence
  reopens nothing**, generic precedent is not proof for this measurement, a concrete omission must
  return **with its affected observable and a remedy**, and no uncertainty may be invented from it.
- [`VERDICT-20260920-third-lane-c5-c7-verification.md`](VERDICT-20260920-third-lane-c5-c7-verification.md)
  - **The THIRD-LANE independent verification of `(5, Z)` and `(7, Z)`**, committed **verbatim** as
  the verifier wrote it. It is the lane `DISCLOSURE-20260920`'s `V2` said was required: it authored
  none of the C5/C7 evidence and does not own cause 5. **C5 NOT FALSIFIED** on the 15-module
  assembly closure at `fb9ec356` — every module matched against its Git blob, `adopt_unified_5d.py`
  genuinely in the closure (`e1260e8d…`) — and on all eight manifest sources, opened and fully
  hashed; the **producer-chain residual is preserved, not converted into a missing 16th module**.
  **C7 reproduces**: 45 bands, V 13 / R 27 / A 5, ten distinct endpoint digests, ten migration
  censuses agreeing with `p4_lib.py:64-65`, identities at `1e-16`, independent eigensolve.
  ⚠ It **declines** to treat *"measured twice, two files"* as two origins — both trace to the
  support file's keys — and reads the original support file instead. ⚠ Two publication findings:
  **`P1`** the lower-bound inference (withdrawn, see below) and **`P2`** the dropped top-1%
  qualifier. ⚠ **Procedural deviation stated by the verifier itself:** the requested fresh clone was
  absent and `RUN.sh` was not executed, so fresh-clone isolation was **not** achieved; it worked
  read-only against pinned revisions in the existing object database.
- [`CORRECTION-20260920-lower-bound-inference-withdrawn.md`](CORRECTION-20260920-lower-bound-inference-withdrawn.md)
  - **WITHDRAWN: *"it is a LOWER bound"* / *"letting them vary could only add."*** `s_proj` is a
  **maximum** of `|Δ√(uᵀCu)|/√(uᵀCu)` over a functional set, not a sum of nonnegative component
  magnitudes, so releasing a held-fixed PSD component changes the operands and can move the total
  the **other** way — with a 1-D counterexample on strictly positive components taking `4.880885%`
  to `0`. **The MEASUREMENT stands** (5 bands, `26.0%` of `√Tr`, zero movement by construction);
  the direction of the unmeasured remainder does not. ⚠ **The *more-seed-pairs-can-only-raise-it*
  half is VALID and retained** — same statistic, same operands. **`M1`'s `6.145%` FAIL is
  untouched.** Newly open: whether the FAIL survives *any* release of the five bands. Enumerates
  all **8** sites, including `values.tex`'s **comment**, which a search for rendered text misses.
  Also repairs `P2`: §4i now gives the full per-bin range `0.177`–`3.062` with `0.687`–`1.153`
  labelled as the top-1%-by-variance subset.
- [`CORRECTION-20260921-seed-effect-larger-ensemble-corollary-withdrawn.md`](CORRECTION-20260921-seed-effect-larger-ensemble-corollary-withdrawn.md)
  - **WITHDRAWN: *"there is no ensemble size at which it falls under `5%`"*** —
  `EVIDENCE-20260920` §5's first bullet. The seven `s_proj` points are **one seed pair**
  (offsets `{0,1200}`) and the `40`/`80`-throw points are **nested subsets of the same 160
  throws**, so flatness over a factor of four in `N` is a **within-ensemble** observation, not a
  determination of the asymptote. **No number moves** and the conclusion the measurement was
  gathered for is retained in full: noise must fall with `N`, this did not between `N = 40` and
  `N = 160`, so the failing leg is not reporting its own resampling noise. ⚠ **`M1`'s `6.145%`
  FAIL is untouched**, and §5's **second** bullet and its *"nothing to price"* conclusion are
  **NOT** withdrawn. Enumerates **11** sites (⚠ this entry read *"all 10"*; site 11, the adoption entry in this catalogue, was added 2026-09-22) — `EVIDENCE` §5, `AGENTS.md:88`, four in
  `docs/analysis-note/` (the last again being `values.tex`'s **comment**), `REPORT-20260920` `L1`,
  `HANDOFF-20260921-gbdt-remaining` `L1`, `nd-unfolding/CORRECTED_UQ_PRODUCTION_STATUS.md`, and
  ⚠ **site 10, THIS FILE's own `EVIDENCE-20260920` entry** (added 2026-09-22, §4d).
  ⚠ **Site 10 was missed by INSTRUMENT, not by scope** — it was inside `docs/` the whole time. The
  phrase wraps across a line as `a larger<LF>  ensemble`, and §4d measures that `tr '\n' ' '` —
  **the remedy this tree's own instrument rules state** — leaves three spaces and STILL returns 0.
  Whitespace must be **COLLAPSED** (`tr -s`, `re.sub(r'\s+', ' ', …)`), not merely replaced.
  ⚠ **Site 9 was missed by the sweep itself and is the sharpest of the three method notes:** the
  sweep declared itself *"by CLAIM, not by wording"* while its command was scoped
  `docs/ AGENTS.md`, so an `nd-unfolding/` status file was never in the hit set. §4c records the
  instrument that found it — **a claim's blast radius is the file list of the commit that spread
  it** (`git log -S` for the sha, `git show --name-only` for the population); `e7f8f365`'s own
  subject named *"the status files"* the glob omitted, and of its seven files four got the claim
  while three got the correction. §4c also records that **3 of the 4 tree-wide sweep hits are
  quotations by design**, so a hit count is not a defect count. ⚠ **Sites 7 and 8 were missed by the first draft of
  its own table and found by the sweep, then MISDESCRIBED their own action until the owning lane
  opened the diff** — the record keeps both on the page as method notes: run the sweep before
  writing the enumeration, and write each row from `git diff` afterwards. §4a cites
  `PREDECLARATION-20260921-L2-lateral-seed-release.md` §4 as a **convergent, contemporaneous**
  instance of the one-seed-pair half, scoped to that half: `f6f54e73` 2026-09-21 16:16 **postdates
  every record-side site** and leads only this correction, by 3 h 46 min. §4b adds the owning
  lane's own diagnosis — the handoff quoted a derived summary instead of
  `state/SEED-EFFECT-20260920.json`, whose key `seed_effect_same_throws` states the limitation in
  its name. ⚠ §4a also records a **false timeline that was caught before it was written**, from
  measuring two sides of a date comparison with different instruments.
- [`OUTCOME-20260922-ten-adopted-receipts-superseded-by-code-drift.md`](OUTCOME-20260922-ten-adopted-receipts-superseded-by-code-drift.md)
  - **THE TEN STALE ADOPTED RECEIPTS ARE ONE DIVERGENCE, NOT TEN, AND THEY ARE NOT RE-PINNED.** All
  ten are byte-identical in every provenance field — `unfold_blob dc74c38f…`, `code_rev 42268b6d…`,
  `config_hash 4b41fab9…` (the baseline value, distinct from L2's `4809b4ad…`). The single stale
  binding is `nd-unfolding/unfold_nd_omnifold_unbinned.py`, moved `dc74c38f…` → `662951e0…` by
  **`5afb7947`, `ae42ae8d`, `0a4ab263`, `1aa055d9`** (151 insertions / 4 deletions); the current blob
  is the same at deployed `32e403b8` and at `origin/main`, so the divergence is not a tree artefact.
  **Classified SEMANTIC** — all four deleted lines are executable, including the OI-136 `_REPO`
  repair that selects which modules load. ⚠ **The drift is MEASURABLY behaviour-preserving for the
  production invocation from the canonical path** (`Path(__file__).resolve().parents[1]` evaluates to
  the deleted literal exactly; the new option is `None`-defaulted and the `if`→`elif` preserves the
  old branch) — **and that is recorded as NOT a licence to re-pin**, because it holds for one path by
  construction and the receipt asserts code IDENTITY. **Disposition: SUPERSEDED-BY-CODE-DRIFT, guard
  stays CLOSED.** Nothing moves `3d7465f6…`; no re-unfold was run.
- [`BLOCKED-20260922-issue59-figure-rerun.md`](BLOCKED-20260922-issue59-figure-rerun.md)
  - **ISSUE-59's figure re-run NOT executed — terminal outcome under the session's D7 hard limit,
  not a stall.** D6 named the re-run; D7 enumerates *"PET work of any kind"* as a hard limit, and the
  re-run executes `pet/pointcloud_projection.py`. Three sources agree with D7, one of them Joseph's
  own words (§0). Everything row 59 claims that is checkable from the repo was **verified** at
  `384c2eb1`: the asset's sole commit is `6749ddf8` (2026-07-05); the re-run entry sits at
  `make_figures.sh:78-83`. ⚠ **AND THE DANGLING `KNOWN_ISSUES #18` IS TRACED, not guessed:** cited at
  `make_figures.sh:59`, row 18 was *"pet_event_displays / pet_cardinality had no generating script …
  RESOLVED 2026-07-10"* — exactly the comment's subject — surviving to `d2ca8ed1` and dropped at
  `1f714b7f`'s index compaction. **The citation was correct when written; a resolved row was deleted
  without sweeping inbound citations.** Index rows run **5–11, 16, 17, 19–21, 23–60 at `384c2eb1`**, the sha the BLOCKED record names as its measurement point (23–62 at `9e78a8cf`; **23–66 at `c6a62a4c`** — pinned, not "today", because this very clause was written to repair a one-of-two-sites failure and went stale one commit later). ⚠ **This paraphrase said *"now run … 23–62"* and was missed when the BLOCKED record itself was corrected — a repair that reached one of two sites, which is this session's most-repeated failure.**
- [`OUTCOME-20260922-3d-covariance-projected-from-the-adopted-trunk.md`](OUTCOME-20260922-3d-covariance-projected-from-the-adopted-trunk.md)
  - **THE 3D `(pt,pz,eavail)` COVARIANCE NOW EXISTS, projected from `3d7465f6…`** — §9.2's stated
  blocker for four marked figures. `sha256 20c16e16a35a837b…`, `15,937,290` B, job `58736728`;
  **1,431** reported cells of a dense `14x16x7 = 1,568`; `src_cells_dropped 0`; `√Tr 6.1289e-39`;
  symmetry exactly `0`; row-index readback `856469c41a8484be…`; `acceptance_question UNDECLARED`
  carried verbatim. ⚠ **CONSTRUCTION IS NOT ADOPTION** — nothing adopts it, the four figures are NOT
  regenerated, and their markings stand. ⚠ **TWO ANALOGY TRAPS:** `λ_min` **computes** negative here
  (`−4.326e-93`, most-neg/max `−2.32e-16` in one run, varying with the BLAS configuration) and positive on the `(E_avail,W)` product, **and neither
  sign is meaningful** — both sit at the double-precision noise floor (`PLAN-20260918` §16.1a rules this for the
  42x42 and predates the 3D object, so it applies to the 3D one by extension; far inside `VL142`'s `1e-9`
  relative PSD allowance). The 3D `λ_min` value is also one run's: it varies with the BLAS configuration,
  and 583–587 of its 1,431 eigenvalues compute negative, so copying either sign across as a property is the
  trap (⚠ this entry read *"`λ_min` is **NEGATIVE** here … correct on this object"*, asserting a
  meaningful sign; withdrawn 2026-09-22); and the destination is **1,431 of 1,568**, not dense. ⚠ **The destination mask is a DECLARATION**
  and this run declares `receiving-cells` following the adopted precedent — **a figure would need
  the `declared-dst-cv` variant**, and that declaration has not been made. `M1`–`M4` travel with it;
  a retained count is quoted ONLY with its cutoff (`263 of 1431 at rc = 1e-12`, from the producing job's stdout) and no cutoff SCAN exists for this object (⚠ this entry read *"no rank is quoted and none has been scanned"*, stale after the record itself began quoting the retained count).
- [`OUTCOME-20260922-L2-sproj-measured-and-the-pair-is-not-code-comparable.md`](OUTCOME-20260922-L2-sproj-measured-and-the-pair-is-not-code-comparable.md)
  - **L2's `s_proj` EXISTS AND ITS PAIR IS NOT CODE-COMPARABLE.** Stages 4-6 ran under the
  `229c43e0…` verifier token. **Control exact**: the graded pair re-measures
  `s_proj = 6.145388%`, `|diff| = 0.000e+00` against `GRADE-20260920` (requirement `1e-12`), so the
  harness IS the graded code path. **Released** (five laterals at seed 1242): `s_proj 6.189174%`,
  `s_agg 0.762704%`, `s_med 0.682292%` — against the pinned pair, the two legs INSIDE the bound differ
  most (`+62%`, `+41%` relative) and the failing leg least (`+0.71%`); ⚠ **not attributable to the
  release**, because the products also differ in the Z-assembly code identity (record §3) and in the
  unfold driver's identity for the lateral endpoints, at one seed pair; whether the driver difference
  changes the result is not established, and no run isolates the release (record §1). ⚠ **NOT all five predeclared invalidating
  conditions hold** — the record's *"All five hold"* is **WITHDRAWN**: three hold as measured
  (baseline's 20 digests byte-identical in both jobs), **one holds only against §6's PRE-AMENDMENT
  text** (Amendment 1 §A1.4 widened it to all of `active_universe_5d/standard/`, never digested),
  and **one is NOT satisfied** (the Z product sits in a new sibling
  `z2m-products/member_k001200_L2laterals/`, outside the member tree). ⚠ **BUT the probe pair fails
  `footing_ok`, ALONE among **NINE** bool fields (`Validity` is 9 bools plus a `notes` dict that cannot fail), and NOT on population:** the real `Member.footing()` is
  **identical** on all three products (`mask eed021e9…`, `rows 61a7c9fd…`, `n_reported 10694`).
  `z_grade.cross_member_validity` folds code identity in — `footing_ok = bool(footing_ok) and
  code_agrees` — and the graded members are at `d64257c3` while the rebuild is at `384c2eb1`.
  ⚠ **STRUCTURAL, not careless:** `z_build` requires `producing_revision == HEAD`, and a build at
  `d64257c3` dies under the OI-136 guard (job `58358282`), so matching the graded code identity and
  running at all are mutually exclusive. **The predeclaration's bare `> 5%` row may NOT be claimed**;
  `M1`'s FAIL is untouched and never rested on this probe. Two stage scripts were repaired — both
  had never run (`z_grade.MemberProduct` exists at no revision; stage 5 returned `ls`'s status).
- [`HANDOFF-20260922-gbdt-cold-start.md`](HANDOFF-20260922-gbdt-cold-start.md)
  - The **work order** for the 2026-09-22 GBDT cold-start lane: §12 enumerates the seven items, §2
  the verifier-token position, §9.2/§9.4 the 3D projection and the ISSUE-59 figure re-run.
  - ⚠ **ITS HEADER PINS ARE SUPERSEDED.** The `monorepo head` and `standalone note head` rows record
  the heads *as written*; both moved during the lane, and the file itself was edited afterwards
  (+38 lines, adding §10.2). Read heads from `git rev-parse origin/main` and `git ls-remote`, never
  from that header.
  - ⚠ **IT WAS REGISTERED `ARCHIVAL` / `immutable yes` IN `MANIFEST.tsv` AND WAS MUTATED ANYWAY** — at `3b60abb0`. ⚠ **This entry asserted that in the PRESENT tense at a commit where it was already false:** the same commit added the `LIVE`/`open` overrides row, so from `9448c0a9` onward the file is `LIVE` / `immutable no`, and the immutability conflict the next clause called *"unresolved"* had been dissolved by the edit describing it — the same writing-the-claim-invalidates-the-claim shape as the manifest gate two rows away. What remains genuinely open is **whether reclassifying a terminal handoff to `LIVE` was the right call** rather than leaving it `ARCHIVAL` and recording the mutation; that is a question for whoever rules on the archival class. It
  had **no `MANIFEST-overrides.tsv` row and no entry here**, which put it permanently outside
  `live_doc_indexed.py`'s scope — the same discovery hole
  [`VERDICT-20260922-third-party-review-site9-issue60-s4c.md`](VERDICT-20260922-third-party-review-site9-issue60-s4c.md)
  documents for a different file. A `LIVE`/`open` overrides row and this entry were added
  2026-09-22 by the eighth independent review; the immutability conflict itself is **unresolved**
  and belongs to whoever rules on the archival class.
- [`REPORT-20260922-review-residue.md`](REPORT-20260922-review-residue.md)
  - ⚠ **THE REVIEW LOOP DID NOT TERMINATE ON ITS OWN CRITERION, and this records that rather than
  implying otherwise.** ⚠ **EVERY independent review so far has found defects, each
  resetting the counter, and every one after the first reviewing its predecessors' repairs and finding
  fresh ones** (review #1 had no predecessor repairs to review).
  ⚠ **THE PER-ROUND COUNTS ARE NOT RESTATED HERE** — they live only in that report's §1 ledger,
  because carrying them in three files is how two went stale after every review (`KNOWN_ISSUES`
  row 66). **Read the ledger for the numbers.** What is stable and worth routing on: condition (ii)
  was never satisfied; the latest review's repairs are always author-reviewed only; and review #4's findings were **all** of row 66's class — ⚠ **but review #3's were
  NOT: it found a wrong count in `VL145`, a LOGIC BUG in committed probe code, and a sourcing
  defect in the release package. The wider claim is withdrawn at row 66.**
  ⚠ **The reusable lesson: two consecutive clean SELF-rounds were worth very little** — the
  independent pass found three consequential defects including one that made a in-repo deliverable's
  own reader recipe raise `AssertionError`. Several findings are recorded rather than repaired
  (`KNOWN_ISSUES` **63–66**, the last being the RATE itself; and, added later the same day, **67–72** — the PASS token's false docstring citation, a mis-attributed ratio, the guard's defeat history, the tree-wide bare rank `247`, nothing having run the guard on the live ledger automatically (since 2026-09-23 `.githooks/pre-commit` runs it as a WARNING ONLY, never blocking, when this report is staged, reading the working-tree copy), and pre-existing ledger rendering defects — with the instruments that police them, named because a glob is not a population: `probes/probe-20260922-{ledger-reconciles,ledger-guard-mutations,gfm-table-integrity,render-checks,quote-provenance}.py`, the runner `probes/probe-20260922-seven-gates.sh` and `probes/probe-20260923-citation-resolution.py`. ⚠ This said *"the five committed probes under `probes/probe-20260922-*`"*, a glob that now matches 17 files; and *"the guard having no caller"*, false since the runner calls it; self-round 78, reworded after review #19a): the PASS token's forward reference and scope count, both unrepairable
  because the token IS the sha256 of those bytes; `check_dead_containment`'s green depending on a
  gitignored PDF; and the existing withdrawal-completeness checker never being given the 2026-09-21
  claim. **No scientific number moved in either direction.**
- [`VERDICT-20260922-third-party-review-site9-issue60-s4c.md`](VERDICT-20260922-third-party-review-site9-issue60-s4c.md)
  - **THE THIRD PAIR OF EYES `HANDOFF-20260922` §10 ASKED FOR, on all three objects.** Site 9's fix
  **ACCEPTED** (sentence replaced with the sites 7–8 wording, inline `⚠ M1 CORRECTED` block present,
  **no number moved**, and row 9 written from the diff). `ISSUE-60` **STANDS, HIGH, all three checks
  real** — but item (3)'s stated mechanism is corrected: `live_doc_indexed.py:97`'s `reclassified`
  branch DOES fire on a later-added row, so the hole is that **both** branches intersect
  `staged_live`, leaving a doc that never gets a LIVE row permanently out of scope. Measured on
  `15edf148`: of its two new records, `OUTCOME-20260921-L2-probe-…` got no overrides row and **still
  has none**. §4c's **substance is confirmed** (`e7f8f365`, seven files, 1 asserting, 4 received /
  3 corrected all reproduce) with **three defects**: its prescribed `git log -S '<the claim>'`
  returns `7257b255`, **not** the `e7f8f365` it names, because the quote spans a newline; two
  adjacent sentences count over two unnamed populations; and **§4c had no heading at all**, so three
  pointers dangled. ⚠ **AND IT FOUND SITE 10** — `CATALOG.md`'s own `EVIDENCE-20260920` entry,
  asserting the now-**WITHDRAWN** *"a larger ensemble would not change it"*, unmarked since
  `128a5e7a` and marked 2026-09-22. **Missed by
  INSTRUMENT, not scope:** `tr '\n' ' '`, the remedy this tree's rules state, returns **0** on it.
  ⚠ **This lane fixed site 10 and is therefore NOT independent on it.**
- [`DECISION-20260920-joseph-rules-clause-c-disposition.md`](DECISION-20260920-joseph-rules-clause-c-disposition.md)
  - **§6.4 clause (c) is DISPOSED.** `V2` **discharged** by the third lane above; `V6`'s six
  unreproduced items **ruled outside** clause (c)'s scope, on the assessor's own distinction that
  independence is about **judgement, not arithmetic**; and the ordering defect — verification
  followed adoption — **ratified retrospectively and expressly NOT cured**. ⚠ Joseph ruled by
  **selecting** one of three dispositions put to him in session; §0 says so and forbids attributing
  any other sentence to him. ⚠ **Two limitations travel with it:** `L1` the `V6` six have no
  second-lane reproduction, and `L2` the sequence was violated. It does **not** claim every clause-(c)
  row was measured — the third lane verified **two**.
- [`RECORD-20260920-PROJ-m1-publication-under-exception.md`](RECORD-20260920-PROJ-m1-publication-under-exception.md)
  - **The M1 publication projection is BUILT and its pairing verified.** `835828bf…`, 42 cells,
  `run_class publication-under-exception`, variant declared **and measured** `cv`. Every
  predeclared check passes — **`src_cells_dropped = 0`**, exact symmetry, PSD, `hRowIndex` readback
  — and `n_empty` is correctly **not** cited. The **binding** pairing leg passes: the projected
  source and the figure's source are **byte-identical** (`0f04abce…`), with C-order agreement at
  `5.22e-54` against an F-order control three orders larger. Carries the adoption's four
  measurements.
- [`DECISION-20260920-joseph-adopts-z-cv-under-the-6.4-exception.md`](DECISION-20260920-joseph-adopts-z-cv-under-the-6.4-exception.md)
  - **JOSEPH ADOPTS `3d7465f6…` as publication-under-exception**, re-hashed on the cluster first.
  Carries the `UNRESOLVED`/`4c` status and **C3 stays "predeclared, not computed"** in the same
  place as the decision, and **four measurements that travel with the digest**: `M1` `s_proj =
  6.145%` vs a 5% bound; `M2` — quoted **verbatim** from the governing record
  (`CORRECTION-20260921-seed-effect-larger-ensemble-corollary-withdrawn.md` §3, *"used verbatim at
  every prose site"*; `AGENTS.md` is a **view**, not the authority, and this bullet cited only it):
  *"The effect did not fall with ensemble size over the range tested — `6.02%` at `N = 40`, `6.02%`
  at `N = 80` and `6.145%` at `N = 160`, fitted exponent `0.000` — while the same-seed resampling
  floor fell `20.91% → 7.57%` between `N = 40` and `N = 80`. The `40`- and `80`-throw points are
  nested subsets of the same 160 throws at one seed pair, so the behaviour at much larger `N` and
  the width of the seed-pair distribution are both unmeasured."* ⚠ **The fitted exponent `0.000` is
  the exponent `p` in `s ∝ N^-p`, NOT a p-value**, and must never be read as a significance.
  ⚠ *"a larger ensemble would not reduce it"* is **WITHDRAWN** — what the correction withdraws is
  the claim quantified over ALL `N`, not a claim scoped to the range measured.
  ⚠ **AN EARLIER REVISION OF THIS BULLET OVERREACHED AND IS WITHDRAWN.** It said the scoped form
  *"flat in N over the ensemble sizes measured"* *"still frames the three points as a sample
  across ensemble sizes — exactly what §2.1 of that record blocks"*. Two defects: **that record
  has no §2.1** (its sections are 1, 2, 3, 4, 4a–4d, 5; the *"not a sample … across ensemble
  sizes drawn independently"* clause is §2 item 1), and the scoped form is **explicitly blessed**
  by a committed third-party verdict — `VERDICT-20260922-third-party-review-site9-issue60-s4c.md`:
  *"surviving `flat in N` claim is scoped | ✅ reads `over N = 40–160`, not unqualified"*. Five
  further live sites use the scoped form; had the overreach stood, it would have condemned all
  five, including the release package. **The verbatim §3 wording above is the standard; the
  scoped form is not a defect.**
   `M3` five
  seed-pinned bands — ⚠ **the *"lower bound"* wording is WITHDRAWN** (`AGENTS.md`;
  `CORRECTION-20260920-lower-bound-inference-withdrawn.md`): the bands are **unprobed in either
  direction**, so they bound nothing; and `M4` the seed moves the **central values** by ≤6.0% of
  their uncertainty (≤49.8% for a single 5D bin). ⚠ This entry **asserted `M2` and `M3` in the
  catalogue's own voice**, unmarked, until 2026-09-22 — on the entry a reader reaches the adoption
  through, and contradicting this same file's own `WITHDRAWN` marking of `M3` further up. The exception covers this digest **and
  nothing else** — `361090f9…` and `7e4636a3…` are named as excluded.
- [`DRAFT-ADOPTION-20260919-z-cv-under-the-6.4-exception.md`](DRAFT-ADOPTION-20260919-z-cv-under-the-6.4-exception.md)
  - **The exception route, taken to the point where only Joseph's act is missing.** It **adopts
  nothing as it stands and is built so that it cannot**: its sentinel line is deliberately negated,
  so `run_m1_projection.sh` refuses it `rc 3`. `tests/test_draft_adoption_record.py` asserts **both
  directions** using the launcher's own regexes, **extracted rather than retyped** — refused as
  written, accepted after the one documented edit. Carries the `UNRESOLVED` status and the
  predeclaration failure **in the same place as the adoption**, and states that the exception
  attaches to bytes and covers `3d7465f6…` and nothing else.
- [`CHECKLIST-20260919-reverification-against-a-new-digest.md`](CHECKLIST-20260919-reverification-against-a-new-digest.md)
  - **Every check `z-cv.npz` passed, enumerated with where it is implemented** — written BEFORE the
  campaign returned, so the list cannot be selected after seeing which checks a product happens to
  pass. **A1–A12 are automatic** (a product that exists has passed them, and the receipt carries
  each gate's measured output, not a boolean); **B1–B6 are re-run against the new digest**; C is
  documentary at the criterion level. Names what is deliberately NOT on it: the §6.4 exception
  covers one digest and is unavailable to any new candidate.
- [`FINDING-20260919-build-time-cv-held-fixed-is-not-the-spec-condition.md`](FINDING-20260919-build-time-cv-held-fixed-is-not-the-spec-condition.md)
  - **My own R1 change, caught by the first real member.** `cv_held_fixed` is bound to
  *"the null's `x_cv` is the declared central"*, which is **false by construction** — measured
  **0.52% relative** on all 10,694 bins, the background-treatment difference §12.4 already
  documented. So every real build reports branch 1 for a reason that is not a footing failure.
  **The grade is unaffected and that is verified, not argued**: the product's `hXSecND_flat` is
  byte-identical to the archive central, so the grader's cross-member field is True. **Not fixed** —
  production output exists and criteria are frozen; the recommended repair is recorded.
- [`EVIDENCE-20260920-sproj-resolution-floor-and-seed-effect.md`](EVIDENCE-20260920-sproj-resolution-floor-and-seed-effect.md)
  - **`s_proj = 6.145%` is a REAL estimator-seed sensitivity, measured not argued.** With the throws
  held fixed and only the seed changed, `s_proj = 6.04% ± 0.39%` at **N = 40, 80 and 160** —
  **flat, `p = 0.000`** — while the same-seed resampling floor falls steeply, `20.91% → 7.57%`,
  **`p = 1.467`**. Statistical noise must fall with N; this does not. Controls: the diagnostic path
  reproduces `z_build` **bitwise** for both members and reproduces the graded `s_proj` **exactly**,
  and the method returns the already-known answers for `s_agg` and `s_med`. ⚠ **WITHDRAWN
  2026-09-21 — *"a larger ensemble would not change it"*.** This entry asserted it unqualified
  until 2026-09-22; `EVIDENCE` §5's own `⚠ CORRECTED` block withdraws it, because the `40`- and
  `80`-throw points are **nested subsets of one 160-throw ensemble at ONE seed pair**. **NOT
  withdrawn, and both stand: `no rebuild passes`, so `no price is owed`** — those rest on where a
  resolution-aware bound could sit, not on arbitrary `N`. 6.997 CPU / 0 GPU.
- [`OUTCOME-20260920-cause3-two-member-assessable-FAIL.md`](OUTCOME-20260920-cause3-two-member-assessable-FAIL.md)
  - **(B) ASSESSABLE FAIL, branch 5 NOT MET — PER-BIN.** The campaign is **fully valid** — all nine
  `Validity` fields passed, no reject conditions — so this is a measurement, not a footing failure.
  `s_agg` **0.471%** and `s_med` **0.485%** are well inside the 5% bound; **`s_proj` is 6.145%** and
  exceeds it. **On the two diagonal legs alone the result would have been MET**: §3.7d's
  correlation-blindness finding, and Joseph's ruling (b) adding `s_proj`, is what caught it — and
  the required deliverable *is* a projection. The seed-pinned-band limitation **cannot explain it
  away, only understate it**. `r_null = 2.442e-13`, within `ε`. 68.17 CPU / 53.75 GPU actual.
- [`RUN-20260919-cause3-two-member-campaign-launch.md`](RUN-20260919-cause3-two-member-campaign-launch.md)
  - **What was submitted**: 8 jobs, `337.00` CPU / `158.25` GPU reserved, admission `rc 0`
  re-measured before each submission. **Three clean deploys** — arms at `44e09fd8`, builder at the
  preregistered `d64257c3`, bridge at `a51f7917` — with the reason three rather than one, and the
  k0r2 combine **preserved by digest before being re-run**. No result.
- [`PREREGISTRATION-20260919-cause3-two-member-campaign.md`](PREREGISTRATION-20260919-cause3-two-member-campaign.md)
  - **Committed before any job was submitted.** `K = {0, 1200}` with all three offset predicates run,
  builder `d64257c3`, `S = 1e-3`, `ε = 1e-9`, pass rule = branch 3 **and** `r_null ≤ ε`, graded
  offset `0`, and the digest **deliberately unnamed**. Records why the `k = 0` arms are not re-run:
  `r5_meter check` **ADMITS** `337.00`/`158.25` and **REFUSES** two fresh members at `672`/`316.5`
  — R5, not preference, decides it. Block-arm cap raised to `7.00` h against an observed `4.82` h.
- [`REVIEW-20260919-multi-member-grader-two-rounds.md`](REVIEW-20260919-multi-member-grader-two-rounds.md)
  - **`z_grade.py` — the first production caller of `assess()` that can reach a leg**, and two
  adversarial review rounds over it. Round one: **2 BLOCK, 4 MAJOR**. Round two reviewed the FIXES
  and found two **COSMETIC**: distinctness compared strings the forger controls (now the throw
  source is **re-hashed from disk**), and `--preregistration` could be dropped from the command
  line (now **required**). One round-two BLOCK was **overstated and is recorded as such** — an
  all-ones `g` is a legitimate `compute_g` output — but **my test for it was rigged** and is
  corrected. Firing the repo's own `s_proj` tripwire moved the round-off guard **into
  `z_statistics.s_proj`**; the `kappa` half stays open and is now **measured and recorded** so a
  later `kappa` applies retrospectively.
- [`REVIEW-20260919-R7-non-finite-member-footing.md`](REVIEW-20260919-R7-non-finite-member-footing.md)
  - **R7 implemented and cross-model reviewed: NO BLOCK, NO MAJOR.** `all_members_finite` moves to
  `branch1_failures()` — branch 2 is a **zero-spread** diagnosis and a `NaN`/`inf` product is the
  opposite failure. **Half the fix is the builder:** a hardcoded `False` in a branch-1 field would
  have put branch 3 out of reach on every build forever, so it is now **measured**. Three review
  findings fixed, including **my own SPEC edit** — splitting *"missing or non-finite"* described
  behaviour no code has, because one boolean implements both.
- [`REVIEW-20260919-computed-acceptance-disposition.md`](REVIEW-20260919-computed-acceptance-disposition.md)
  - **Cross-model review of the computed-acceptance change: NO BLOCKs**, one MINOR, three NITs, with
  **my** dispositions. Two NITs fixed by **making the claim true** rather than softening it —
  `cv_held_fixed` now gates on the CV cross-check it always cited, `digests_agree` on an actual
  digest. The MINOR (`all_members_finite` classed branch 2 when it is a footing failure) was
  **correct and deliberately not acted on** under R1's scope — and is **now FIXED under R7**
  (Joseph, 2026-09-19): the field moved to `branch1_failures()` and the builder MEASURES it.
- [`DERIVATION-20260919-null-epsilon-B-and-S.md`](DERIVATION-20260919-null-epsilon-B-and-S.md)
  - **`B = 1e-12`, `S = 1e-3` (Joseph's), `ε = 1e-9` inside `[B, S]`.** R2's gate checked FIRST and
  it passes: `r_null = ‖x_cv2 − x_cv‖ / ‖x_cv‖` is dimensionless by construction. `B` rests on two
  independent observations agreeing to **0.47%**, and its `n = 2` weakness is **stated, not dressed
  as a confidence interval** — what carries the argument is **4.4 orders of margin**, so `B ≤ 1e-9`
  survives a 22,000-fold increase. `ε = 1e-9` is the **pre-existing** proposal, not fitted now.
- [`INVENTORY-20260919-scientific-acceptance-criteria-from-code.md`](INVENTORY-20260919-scientific-acceptance-criteria-from-code.md)
  - **⚠ `scientific_acceptance` IS NOT COMPUTED — it is the literal `"NON-PASSING"` at
  `z_build.py:608` and `:788`, with no branch producing `"PASS"` anywhere.** `outcome.assessable` is
  likewise the constant `False` at `:652`, and `z_validator.assess()` — the only source of
  `assessable=True` — is never called. `z_build.py:841` says it outright: NON-PASSING is *"the only
  outcome this command can produce"*. **So no new build can reach PASS or an assessable FAIL.**
  Second, independent blocker: `ε` needs `B ≤ S` with `ε ∈ [B, S]`, and **`S` is an undefined
  scientific cap**. Read-only inventory; zero compute spent.
- [`DECISION-20260919-joseph-rules-pm1-cause7-and-completion.md`](DECISION-20260919-joseph-rules-pm1-cause7-and-completion.md)
  - **✅ IN FORCE. Joseph's ruling on PM-1, cause 7, and completion, recorded VERBATIM as his text.**
  `SPEC` stays **FROZEN** — §1 directs recording through the existing ruling mechanism and updating
  the operative routes, **not** a new revision. **PM-1 accepted by decision with a historical-input
  provenance limitation**; the file-level link to G's `combined_source` tuple is **explicitly
  accepted as unestablished**, and the evidence is graded: a comment is intent, an implementation
  trace covers only the inspected implementation, the tuple observation has no path or digest, and
  **repeated accounts count as one observation**. §4 **withdraws** the inference that weight-only
  implies hadronic-response migration is absent. §5 fixes the note/primer/paper disclosure wording.
  **§6 returns ADOPT to Joseph** — PM-1/C7 closure is **not** adoption. §7's stopping rule bars
  another cycle on the accepted gap or on repeated summaries.
- [`OPERATIVE-SHEET-scalar5d.md`](OPERATIVE-SHEET-scalar5d.md)
  - **✅ START HERE for what is IN FORCE. `SPEC` is FROZEN at rev. 22 and is now HISTORICAL** —
  no rev. 23, no "what changed in rev. N" section, no packet superseding a packet; results go to
  the ledger and corrections go inline where the error is. One page: the seven boundaries (`δ = 5%`
  on all three legs, the two coverage fractions, `cause2_f7_margin 0.168`, and `null_epsilon` as
  the single remaining withheld one), `s_proj`'s functional set, the seven cause dispositions,
  **`SRC_COV` identified by measurement as `z-cv.npz`**, the fixed execution order, and the three
  reserved acts. **An EXTRACT, not a new authority**: where it and a canonical artifact disagree,
  the canonical artifact wins.
- [`AUTHORIZATION-20260918-d-resource-required-deliverable-path.md`](AUTHORIZATION-20260918-d-resource-required-deliverable-path.md)
  - **✅ `D-RESOURCE`, IN FORCE. Read this before touching the scalar-5D path — the objective lives
  here, not in a packet.** §0 states it: an **adopted scalar-5D covariance**, the **required verified
  projections with correctly paired central values**, **synchronized note/primer/paper**, and
  **submission is Joseph's act**. §1 is the compute posture: pre-approved on the required path,
  **optional work still needs a separate ask**, `R5`'s ceilings and per-submission admission
  unchanged. §2 is the **nine rulings** — the scope amendment excluding the generator significance,
  `k₁` **DECLINED** and its reservation **RELEASED**, `s_proj` **added** as a requirement, the
  functional set, `δ = 5%` **APPROVED** with coverage, the cause dispositions, §6.4's order with the
  exception **APPROVED AS DRAFTED AND HELD, not executed**, pinning **RESERVED**, and the fixed order
  C1–C7 → NULL → **ADOPT** → PROJ → DOCS. §4 records that **P0 is self-contained and already done at
  `1405caad`**. §5 is the propagation test that found a real defect at `rank6_significance.py`.
  - **§7 is the state: BLOCKED, and only Joseph's decisions block it.** Not evidence, not compute, not
  implementation — `R5` has `~403` CPU task-hours against a required path needing `~2`, and every
  consumer change is landed and tested. §7.4 lists the **five open decisions with what each gates and
  a recommendation**. §7.2 records that **rulings 2 and 6 compose into a gap**: C3's legs all measure
  movement **across members**, `k=0` is the only member, and ruling 2 declined the only additional one
  — so **C3 is structurally unevaluable as scoped**, and adopting on a declared-but-unevaluated
  criterion is a *choice*, not a measurement. §7.3 records that **ruling 5's coverage clause is
  written over *bins* while `s_proj`'s population is *functionals***, so it does not literally reach
  the leg ruling 3 added; `1.0` is recommended and **no key is declared**. **`δ = 5%`, the declined
  campaign, and the pinning reservation are CLOSED — no lane re-litigates them.**
- [`DECISION-PACKET-20260918-scalar5d-publication-blockers.md`](DECISION-PACKET-20260918-scalar5d-publication-blockers.md)
  - **The evidence behind those rulings; authorizes nothing.** Every remaining publication blocker
  mapped to its governing requirement, existing evidence, recommended disposition and smallest
  remaining action. §13 is the state after the rulings, §14 C1's measured result, §15 the **M2
  withdrawal** (the note disclaims a 4D uncertainty in four places, so M1 is the only required
  projection), §16 the DOCS verification, **§17 C2's margin** — branch point `7.026066e-39`, measured
  ratio `2.6739`, recommended margin `0.168`, and the measured `5.3478×` vs `uq_math.py:125`'s
  `4.69×` surfaced rather than folded in, because the two are different ensembles.


### Decisions awaiting Joseph — cause 7's subject and magnitude, cause 3's seed scan, the stop rule

- [`DECISION-20260902-joseph-rules-cause7-cause3-and-the-stop.md`](DECISION-20260902-joseph-rules-cause7-cause3-and-the-stop.md)
  - **✅ IN FORCE.** Joseph's 2026-09-02 ruling on all six packet recommendations: `(cause 7, G)` is
  permanently OPEN and G is retained; exactly one successor `Y` is authorized as a **separate** cell,
  cause 7 only, **specification only**; cause 7's `M` carries no smallness requirement; the cause-3
  seed-scan authorization is **SUSPENDED** pending a signed VOI note **and** a separate committed
  reauthorization; the campaign stops on **`2026-09-30`** or at **`500` GPU / `500` CPU task-hours**,
  whichever fires first, defaulting to the central-value Letter; and PET stays diagnostic. `R2`
  prospectively amends `DECISION-20260831` §1 for cause 7 only; `R5` conditionally supersedes
  `OI-187` half (b). **Adopts nothing, discharges nothing, authorizes no submission and no spend.**
  Gate 2 remains FAIL; counts hold at CAND `1 of 7`, QUOTED `0 of 7`. §4 lists six downstream
  applications this lane is `BEN-381`-disqualified from performing.
- [`VOI-20260906-cause3-mii-estimator-seed-scan.md`](VOI-20260906-cause3-mii-estimator-seed-scan.md)
  - **UNSIGNED. The first of the two documents `R4` requires, and it authorizes nothing.** Prices the
  cause-3 fixed-draw estimator-seed scan against four separated consequence classes: it changes cause
  3's `M` grade cell and can change nothing else — discharge is blocked by `C` and `P-i` independently,
  adoption by §5's prohibitions, and the one possible note disclosure **requires its own assessment and
  ruling** rather than inheriting cause 1's. Distinguishes the narrow fixed-draw measurement `R4`
  recognizes from **substitution** for the joint-baseline `(B)` measurement, which stays a separate
  question and is **not** made a prerequisite. Records the `R5` meter as **implemented and
  reviewer-PASSED with no operational receipt**, so measured headroom is unavailable and no
  assumed-ceiling comparison is made. **Recommends DEFER** behind a Perlmutter meter receipt and an
  independent verification of the execution proposals. Names `Z` (the complete scalar-5D successor,
  `RZ`) as distinct from the joint-baseline composite, so neither carries the other's cost. Signs
  nothing, grades nothing, alters no scientific criterion, launches nothing.
- [`FINDING-20260906-cause3-scan-execution-composition.md`](FINDING-20260906-cause3-scan-execution-composition.md)
  - **DISCOVERY RECORD for the VOI packet's §7; every remedy is a PROPOSAL awaiting independent
  verification.** Five measurements at HEAD `c71b319a` and deployment `7ac0edec`: the predeclaration's
  §6b citations resolve at the **deployment**, not `main` (+45 lines), so its preflight measured the
  right operand but lacks its sha; the declared seed set `1..12` is unreachable through the launcher's
  `42 + k` knob, and each of the three available routes meets a **different** declared falsifier, two of
  them only after the spend; the viable route writes into the joint-baseline scan's own `mii/` member
  namespace, where resume is by marker; the clean-offset predicate calls those offsets dirty while
  nothing on that path enforces it; and `SCOREBOARD` §2b's *"cannot be configured on either leg"* ground
  is **stale** — both legs now expose separate estimator and draw seeds, moving `(B)`'s blocker from
  code to **Gate 2**. `BEN-381`: this lane measured all five, so it grades no cell and applies no
  repair; §7 names each owner. Draws **no** affordability conclusion.
- [`PACKET-20260902-joseph-six-rulings-cause7-cause3-stop.md`](PACKET-20260902-joseph-six-rulings-cause7-cause3-stop.md)
  - **UNSIGNED RECOMMENDATION, rev. 3, authorizing nothing.** Six rulings put to Joseph, each with an
  exhaustive branch set and a fallback state: grade `(cause 7, G)` permanently OPEN on the direct byte
  evidence and retain G; authorize exactly one successor `Y` as a **separate** grade cell, cause 7
  only, **specification only**; select the no-smallness criterion for cause 7's `M` **without** a note
  obligation or an automatic grade; decide the cause-3 seed scan's authorization (retain / suspend /
  withdraw — recommended: suspend, with a separate committed reauthorization required, since the scan
  **does** grade `M(ii)`); set a fully defined date/resource stop whose default outcome is the
  central-value Letter; and keep PET diagnostic unless `OI-126`'s estimator-equivalence-plus-coverage
  ladder passes. `R2` prospectively **amends** `DECISION-20260831` §1 for cause 7 only; `R5`
  conditionally **supersedes** `OI-187` half (b). Cross-cuts `OI-126`, `OI-172`, `OI-173`, `OI-187`,
  `OI-188`; §7 gives each ruling an owning record. Gate 2 remains FAIL; counts hold at CAND `1 of 7`,
  QUOTED `0 of 7`.

### Y as R2 permits it, the complete-successor question, and #11-#30 reconciled (2026-09-05)

- [`PREDECLARE-20260905-cause7-only-successor-Y.md`](PREDECLARE-20260905-cause7-only-successor-Y.md)
  - **SPECIFICATION ONLY; all four legs OPEN and ungraded.** The cause-7-only successor `Y` that `R2`
  permits: artifact identities bound to path plus digest (G, its `combined_source`, its `uthrow_source`,
  S as a **component donor only**, F and J as explicit non-evidence), the replacement algebra
  `C_Y = C_G - L_support + L_active` over the five `p4_lib.BANDS` **imported, never retyped**, the
  receipt schema, the five magnitude measurements `R3` left threshold-free, and the both-direction test
  contract. Records that Y replaces **five of the nine** detector laterals in `detector_universes.txt`
  — the kinematic ones — and makes the weight-only justification for the other four
  (`VALIDATION_LEDGER.md:790`) a **pre-construction measurement**, not an inherited claim. §6 lists
  eight things a four-leg-MET Y still could **not** establish, starting with `(cause 7, G)`, which
  `R1` fixes permanently OPEN. **Constructing Y requires its own committed authorization (`R2(iv)`).**
- [`PACKET-20260905-full-scalar5d-successor-scope-question.md`](PACKET-20260905-full-scalar5d-successor-scope-question.md)
  - **ONE QUESTION FOR JOSEPH; authorizes nothing and recommends no option.** Whether a **complete**
  scalar-5D successor — called **Z**, deliberately not `Y` — may be named as a **seven-cause** grading
  subject and therefore a possible adoption subject, and what a ruling must say (subject, cell
  discipline, combination rule, stage gate). §4 walks the seven causes as they stand for G; §5
  re-measures the strongest ground rather than inheriting it: the jitter print at `a0cdc019` (06-08)
  **predates** the flux fix `081ae4ac` (07-31), so cause 4's `M` is unmeetable for G by a property of
  the **committed history**, which a new revision would not share — the broad "no committed revision"
  conclusion is cited to `DECISION-20260902-joseph-applies-oi173-cause4-m.md` §4, **not** derived from
  the two-revision ancestry check, which is labelled as the narrow measurement it is. §6 records the
  two campaign facts that belong on the table first: the `R5` meter **exists** (Wave 1's
  `r5_meter.py`, fail-closed admission) but **no operational accounting receipt is committed and no
  unattended execution is configured**, and S is **refused by the publication gate**. **`R5`'s stop is
  not reopened or re-optioned**; t0 is `2026-09-02T13:44:27Z` at `9ce59a59`.
- [`PLAN-20260905-prompts-11-30-reconciled-to-the-0902-decision.md`](PLAN-20260905-prompts-11-30-reconciled-to-the-0902-decision.md)
  - **ROUTING ONLY; a NOW row authorizes drafting, reading and measuring, never compute.** Disposes
  prompts #11–#30 as NOW / AWAITING a named decision / OPTIONAL. Corrects #11's premise, false on both
  halves — **G is RETAINED** and `Y` is **cause-7-only**, so Y has no causes 1–6 dispositions to give —
  and removes "adopt Y" as an outcome, which rewrites #20 and #21. §3b checks the recommended
  cause-disposition map row by row against the board: only cause 7 is Y's, cause 2 is already four
  METs, cause 5 already landed in `VL66`. §5 **reconciles** the decision record's six owner
  applications against committed evidence rather than relisting them: **five are unapplied; item 6
  (the `R5` meter) is substantially done by Wave 1 and carries only a residual.** Records that
  **completing PET coverage is not a publication prerequisite**. Preserves the ruled stop exactly,
  t0 `2026-09-02T13:44:27Z` at `9ce59a59`.

### Joseph rules the complete-successor question: Z may be specified (2026-09-06)

- [`DECISION-20260906-joseph-authorizes-z-specification-only.md`](DECISION-20260906-joseph-authorizes-z-specification-only.md)
  - **SPECIFICATION ONLY; authorizes nothing to build or run.** Joseph rules the one question
  `PACKET-20260905` asked, selecting its **option B**. `RZ` names **exactly one** complete scalar-5D
  successor **Z** as a **prospective** seven-cause grading subject and a **possible** adoption
  subject, with **seven distinct assessment cells**; **G's historical cells are preserved**, including
  `(cause 7, G)`'s permanent `OPEN` under `R1`, and **Y's cause-7-only scope under `R2` is
  preserved**. Z's assessments may form a **self-contained** tally and **may never be combined with
  G's or Y's grades** — a three-way separation, wider than the packet asked for. Authorized
  deliverables are a scientific contract, cause dispositions, terminal criteria, dependency analysis
  and a **costed execution proposal**; **any proposed criterion change is carved out** and reserved
  for a separate decision. **No implementation, construction, compute, grading, adoption or
  publication change.** `R1`–`R6` are untouched and `R5`'s accounting start, ceilings and stop date
  are preserved exactly; `RZ` is **not** `D-C3-VOI` and **not** `D-C3-RUN`. The ruling **opens no
  `SCOREBOARD` cells** — `(ii)` constrains a future assessment, it does not create one. Gate 2 remains
  FAIL; counts hold at CAND `1 of 7`, QUOTED `0 of 7`. There is no `R7`: `RZ` does not extend the
  2026-09-02 series.
- [`PROMPTS-20260906-z-specification-session.md`](PROMPTS-20260906-z-specification-session.md)
  - **A PROMPT, NOT AN AUTHORIZATION; subordinate to `RZ`, which overrides it wherever they differ.**
  The brief for the fresh scientific-contract session that drafts Z's specification: reading order,
  the five authorized deliverables, the boundaries restated so none is inferred away, the criterion
  carve-out, and the return envelope. §2.1 carries the dependency instruction — a standalone Y
  construction and the historical-candidate cause-3 seed scan are examined **as examples, not as the
  whole question**, each candidate answered separately for `necessary` / `applicable` /
  `reusable-now`, with the two suspended-authority facts (`D-Y-CONSTRUCT` does not exist; `R4`
  suspends the scan pending `D-C3-VOI` **and** `D-C3-RUN`) flagged so a dependency claim cannot
  launder authority. `BEN-381` will disqualify the drafting lane from grading the legs it defines.
- [`FINDING-20260910-r5-attempt-identity-is-not-stable-across-queries.md`](FINDING-20260910-r5-attempt-identity-is-not-stable-across-queries.md)
  - **ACCOUNTING INSTRUMENT ONLY — deliberately carries no scientific scope.** The `R5` attempt
  identity `(JobID, Start, End)` is **not stable across `sacct` queries**: measured on one job over
  one span, two captures agree to `1.9%` on count and `2.2%` on elapsed while sharing **8 of ~1,160**
  attempt identities; over 542 overlapping 10-minute buckets, `96.5%` have identical row counts and
  `0.2%` identical `Start` stamps. So a set difference between captures measures the KEY, not the
  population, and an apparent 62-attempt loss is an artifact. **Accounting rule until the meter's
  owner rules: carry the MAXIMUM observed spend, never the latest; never sum or union captures;
  quote spend with its measurement instant.** A re-query returning less does not release budget.
  Routed to the `r5_meter` owner; **it changes no Z decision and no gate.**
- [`REVIEW-20260910-z-acceptance-criteria-independent-derivation.md`](REVIEW-20260910-z-acceptance-criteria-independent-derivation.md)
  - **INDEPENDENT ASSESSMENT — adopts no criterion, grades nothing, authors nothing.** Part A is the
  minimum acceptance requirements `A1`-`A31` for Z's criteria, derived from `RZ`, `R1`-`R6`,
  `CRITERIA` §0's four legs and `SPEC` §6's rulings *plus the note and paper's own conditional
  sentences*, and **committed before the proposal above was read** (its sha256 is recorded as
  digested-not-read). Load-bearing: `A1`/`A2` separate assessment completeness from adoptability from
  licensing a publication claim, and measure that the publication's own precondition is *"the
  adopted, selection-complete"* covariance -- **two** properties, not seven discharged causes;
  `A12` records that `R3` and §6.2 forbid rejecting Z for a LARGE magnitude on causes 7 and 1;
  `A18` is §6.6's adopted statistic/denominator/precision-target/boundary-together constraint;
  `A25` derives that no bound on a diagonal bounds `r^T C^-1 r`. Four re-measured findings, incl.
  that the 42-bin `(E_avail,W)` object takes the 5D trunk in **through the statistical block only**
  (`eavailW_covariance.py:441`, `C_lateral` diagonalized at `:469`), and that **four** projection
  builders exist with one on the `R6`-diagnostic PET path.
  **Part B is the review: VERDICT = BLOCK on the proposal's §7 items 1-3; item 4 (record the `pinv`
  cutoff policy and the retained rank per member) is READY and separable.** Blocking: `B1` C-1's
  declared population is **empty** -- measured, the `\gbdtFive*` macros are defined at
  `values.tex:112-115` and used **nowhere**, and no deliverable quotes any non-2D significance, so a
  `max` over "the pairs the publication quotes" is vacuous; `B2` §7 item 2 asks for the margin of a
  claim the publication does not make and `R5`'s default is that it never will; `B3` **zero**
  occurrences of `INCONCLUSIVE` against RULED `SPEC` §6.3(4), and the missing branch --
  `PREDECLARE-20260901-cause3-mii` §4's `VACUOUS SEED VARIATION` -- is the positive control; `B4` §7
  item 3 is stale (`ceb474cc`, 2026-09-09, postdates rev. 5) and as specified would test agreement
  over a domain selected for agreement. **Axis (c) is CLEAN: nothing over-rejects** -- all three
  candidates are sensitivity, not magnitude, statistics, so `R3`/§6.2's magnitude-blindness is not
  breached. §B.7 **withdraws Part A's own `A30`**: Z's design is `N = 4`-`5` and FITS `R5`
  (`44.6%`/`69.7%`), the `5x`-`9x` figure prices a design §6.3 does not adopt, and the binding
  constraint is the schedule.
- [`REVIEW-20260910-z-acceptance-criteria-independent-derivation-partF.md`](REVIEW-20260910-z-acceptance-criteria-independent-derivation-partF.md)
  - **PART F of the same independent assessment — the ENDPOINT-A yardstick, and it adopts no criterion,
  grades nothing and authors nothing.** `F1`-`F21`, derived at `6f24fb00` from Ruling 1 (no Z-dependent
  non-2D significance; 2D scope unchanged), Ruling 2 (finite-ensemble **disclosure only**), the note's
  own declarations (i)-(v) at `app_statmethods.tex:645-658`, and `paper_body.tex:145-148` — **committed
  before the designer's endpoint-A packet existed**, with the prior packet's and recommendation's
  sha256 recorded as digested-NOT-read. **`F.5` pre-registers the seven BLOCK conditions** so no
  verdict can be fitted afterwards, and one of them (`F18`) blocks in the PERMISSIVE direction:
  imposing inversion-grade criteria (the `rho` bound, retained rank/subspace, `rcond`, `ndf`,
  `s_sig`) on an endpoint that releases no significance rejects acceptable cases.
  **Three measured findings.** `F-0`: **both governing rulings are unrecorded** — no
  `DECISION-2026091*`/`RULING-2026091*` file in any of 131 refs (newest is `DECISION-20260907`), four
  distinctive relay phrases absent with an in-loop positive control firing on 24+ refs; Ruling 2's
  disclosure-only half is nevertheless anchored, re-stating Joseph's recorded 2026-08-22 *"disclose, do
  not correct"*. `F-I`: **a released projected uncertainty IS a function of the source covariance's
  off-diagonals** — `diag(M C M^T)_i = sum_{j,k->i} w_j w_k C_jk`, forced by the `10,694 -> 42`
  geometry (pigeonhole >= 255 cells per destination row), so the diagonal-only premise for deferring
  `cause3_corr` is false; the relayed mechanism is **corrected** (`Mew` is built inline at
  `eavailW_covariance.py:404-406`, NOT by `project_cov_nd`, and **width-weighting is not the cause** —
  multi-cell row support is, unit weights included). Probe
  [`state/probe-z-endpointA-projected-diagonal-20260910.py`](state/probe-z-endpointA-projected-diagonal-20260910.py),
  `rc=0`, production `uq_math.project_covariance`, three controls incl. one in the opposite direction:
  at fixed diagonal the released sigma spans `0.986x`-`2.803x` under equicorrelation and `2.62e+06`
  over PSD structures, reaching ~0 — the *"looks like a very good measurement"* hazard
  `eavailW_covariance.py:410-413` already names for empty rows. `F-II`: the ensemble-size evidence is
  **stronger than cited AND still holed** — `--expected-ids` + `replica_manifest.py:44-48` is a
  fail-closed bidirectional set-equality check, not an `#SBATCH --array=` declaration, but it is a
  launcher constant that cannot prove ADEQUACY, and `OI-17`'s `122 of 160` is the precedent. Also
  measured: **two normalization conventions in one sum** (biased `1/N` `uq_math.py:104` vs unbiased
  `1/(N-1)` `combine_cov_nd.py:20`), and the ~45 MAT bands are deterministic rank-one despite going
  through `mat_covariance` at `N=2`, so Ruling 2's block set must be partitioned by **sampling
  character, not by computing function**. `F9` (**what "verified" means** — re-measurable from the
  artifact, or established by a construction-time check) is **RESERVED to Joseph and deliberately not
  answered**, since answering it is a design choice. `F.6` re-measures this lane's independence: the
  `D1` retained-subspace remedy is live as clause (d) at `173baf44:392`, labelled RELAYED, and was
  attacked and bidirectionally tested by a THIRD lane — the routing Part E asked for.
- [`REVIEW-20260910-z-acceptance-criteria-independent-derivation-partG.md`](REVIEW-20260910-z-acceptance-criteria-independent-derivation-partG.md)
  - **PART G — the endpoint-A consumer set MEASURED, and two self-corrections where Part F demanded
  more than Joseph's ruling does.** Adopts nothing, grades nothing, authors nothing.
  **`F-0` is CLOSED:** both rulings are now committed verbatim at `a11d6cdd`, so Part F's `RELAYED`
  labels point at a sha; the finding is retained rather than withdrawn, and **`F9` survives the landed
  text** — neither record defines *"verified"*, so its two readings are still open and still differ by
  a code change.
  **`F-III`, the decisive measurement.** `PACKET-20260910:232-235` classifies all five endpoint-A
  consumers as diagonal-only. Measured per consumer: **`C6` and `C7` are correct** (`coverage_valid_nd.py:44-54`
  reads `GetBinContent(i+1,i+1)` off a stored TH2; `_sqrt_trace_from_diag` materialises no matrix),
  **`D1`/`D2` are correct today** but acquire the dependence once the 5D→3D projection their own row
  calls *"pending"* lands, and **`C5` is FALSE ON ITS OWN CITED LINES** — `:441` is
  `project_covariance(C5stat, Mew)` and `:466` takes `np.diag` of `C_lat_e`, built two lines earlier at
  `:464` as `Me @ C_b @ Me.T`. **The chain to Z is closed:** `eavailW_covariance.py:143,145` default to
  `uq_cov_stat_5d.root:hCov_stat5d_reported`, which `SPEC-20260906:504` binds as *"Z's candidate `C_stat`
  input"* (sha `6580016f…`) and `:610` puts in `C_Z`. So one released band is a functional of a Z block's
  off-diagonals. **The defect is the classification METHOD** — classified by the last operation rather
  than by the provenance of the matrix it reads — and the refuting words sat one column away, in `C5`'s
  own *"**produces** `C_low`"*.
  **Convergence recorded, and the criterion deliberately NOT supplied:** Joseph's verbatim adequacy
  check (*"retained-rank and subspace stability do not by themselves establish stability of projected
  uncertainties … show which criterion controls changes in the actual released error bars"*) asks from
  the other side exactly what `F-I` answers mechanically — and `F-I` was committed at `c695f209` before
  that text was read. Proposing the criterion is the designer's task; supplying it would spend this
  lane's verdict on it (Part E §E.1). *"Do not reopen the universal-bound approach"* independently
  confirms `F18` and makes the clause-(d) independence question **moot for the recommended path**.
  **Two corrections against the verbatim ruling:** `F12` is reduced to the bare *"mark as not
  applicable"* (the reason becomes a recommendation), and `F11` is **folded into `F9`** — the ruling
  asks for one verified number, so demanding intended-and-achieved as two was over-reach; the surviving
  point is that *verified* is unsatisfiable for one number when the two can differ, `--expected-ids`
  being a launcher constant that proves consistency and never adequacy (`OI-17`, `122 of 160`, still
  open). **§F.5's pre-registered block list is five items, not seven.**
- [`REVIEW-20260910-z-acceptance-criteria-independent-derivation-partH.md`](REVIEW-20260910-z-acceptance-criteria-independent-derivation-partH.md)
  - **PART H — READ THIS BEFORE CITING ANY EARLIER PART AS CLEARANCE.** ⚠ **The latest designer commit
  this lane reviewed is `173baf44`. Nothing in Parts A-G clears `8d3071a8` or `b40686ec`**, and the
  unreviewed delta is an entire artifact, not a labelling fix: `PACKET-20260910-z-endpoint-A-acceptance-and-cause3-corr-amendment.md`
  (**+505/−0, new**, sha256 `e04b4983…`, digested-NOT-read), `state/probe-z-projected-stability-20260910.py`
  (**+327/−0, new**), plus `+35/−10` on the consumer-set packet and `+12/−3` on its check script. **A
  `READY` in Part B or Part D is a verdict on `2ebdf095` and is two revisions stale.** §H.1 carries the
  per-part referent table so no reader has to infer it.
  **`F-0` is CLOSED on its own criterion** — Part F's criterion was existence on *any* ref with
  diffability as the stated consequence, and that is met; re-reading it as requiring reachability from
  `main` would be moving the criterion after the fact to keep a finding alive. **The criterion then did
  its job, measured:** both records changed between `a11d6cdd` and `ae876e14`, the change was a
  metadata timestamp placeholder (caught by the mathematical reviewer), and the **verbatim Appendix A
  blocks are byte-identical** (`0bd716c2…`, `2d2587a4…`), so Part G's quotations of Joseph hold at the
  decision lane's tip. **§H.2a files the residual NARROWLY instead: a ruling that governs `main` is not
  reachable from `main`** — `origin/main`'s newest ruling record is `RULING-20260908` and both 09-10
  records are ABSENT there, so a session pinning `origin/main` cannot see the constraint binding it.
  Closing that is a merge, not requested here.
  **§H.3 is the disqualification list.** DISQUALIFIED on exactly one item: the retained-subspace gate
  `‖P_0 − P_k‖_2 <= 1e-8` and its tolerance (clause (d)) — found the hole, supplied the fix — and
  likely moot since *"do not reopen the universal-bound approach"* removes the bound from the
  recommended set. **NOT disqualified on the projected-uncertainty boundary**, because `F9` was left
  unanswered and §G.1 stopped at the convergence deliberately: **the line is between "here is what must
  be true" (a requirement, which does not disqualify, or no reviewer could review twice) and "here is
  the statistic, denominator and number" (a remedy, which does).** RECUSED from *grading* per
  `BEN-381` — assessment is not grading. **Declared weakness, not a disqualification:** if the new
  packet's §1/§1.1 transcribe Part G's `F-III`, this lane confirming them is partly self-confirmation;
  `F-III` is a measurement of the code and will be re-derived rather than cited, but a second reviewer
  should spot-check that slice. §H.4: *"the orchestrator"* in Parts A-G re-points — that session ended
  and a different one holds the role.
- [`REVIEW-20260910-z-acceptance-criteria-independent-derivation-partI.md`](REVIEW-20260910-z-acceptance-criteria-independent-derivation-partI.md)
  - **PART I — assessment of the endpoint-A packet's §2/§2.1 and §3/§3.1-§3.3** at `05bf8647` (sha256
  `e5fbd9a9…`), against `F1`-`F21` and §F.5's five block conditions, which were committed at
  `c695f209` **before this packet existed**. **No grade assigned** (`BEN-381`).
  **§3-§3.3: every mechanical claim CONFIRMED BY EXECUTION**, not by reading —
  [`state/probe-z-cause3corr-binding-site-20260910.py`](state/probe-z-cause3corr-binding-site-20260910.py),
  `rc=0`, in-process registry mutation only. All five §3.1 rows reproduce, plus **two positive controls
  the packet does not carry**: deleting `cause3_agg` RAISES (so `assess` does consult the registry and
  the byte-identity is a real negative, not a blind one), and the scope statement flips to `None` when
  a `sees_correlations=True` leg is declared (so the narrowing is leg-derived). **Strengthening owed to
  the packet:** the registry line is not merely *inert* but **structurally unreachable** — `assess`
  looks up boundaries only at `:247` and `describe()` only at `:110`, both keyed on declared legs.
  **§3.3's "costs nothing today" is structurally true rather than lucky**: leg adopted + boundary
  withheld gives `assessable=False`, `reject_conditions=('4c',)`, `is_met=False` **at `s_corr=0.001`**,
  so the refusal is on the ABSENCE OF A LIMIT, not the value. Option ordering does not invert.
  ⚠ **§2.1's SAMPLE-COVARIANCE POPULATION IS NOT TWO — `Flux` IS THE THIRD, and the chain is closed in
  tracked code:** `adopt_unified_5d.py:42-43` puts `"Flux"` as the 13th `VERT_BANDS` entry;
  `z_contract.py:66` imports exactly that as Z's `V`; `z_assembly.py:4` sums `V` **inflated through
  `D_Z`**; `unified_throw_cov.py:467-468` builds it as `mat_covariance(...)` over the flux universes;
  `uq_math.py:96-104` is **biased `1/N`**. `OI-137` independently enumerates **three**. So A-6 omits a
  block **and** its *"one script, one convention"* `1/(N−1)` claim is **false of part of Z's sum** —
  affirmatively misleading, which is what `F8` exists to prevent. **Diagnosis: the derivation is what
  admitted it** — reading the formula's surface is right, but `Σ_V C_b` is itself a sum and the third
  sample covariance is one level INSIDE it. Feasibility is fine: `n_flux` is already inventory-derived
  (`:126`) and already fail-closed both directions (`:461-465`). `C_unified` named as a boundary case
  and explicitly NOT required.
  **The coordinator's ensemble measurement: CONFIRMED, on better footing than offered** — `OI-160`
  already records both *"an exact-population validator cannot see a contract change"* and the
  member-scoped set as **100 boot + 24 split**, so equal-`N` needs no cluster read and the `cp -p`
  caveat drops out of the consequence; `07c18aee` confirmed at 2026-07-14, after the products. The npz
  **key schema** is a content-based discriminator stronger than `mtime`, but it discriminates the
  INPUTS while the product is a bare `TH2D` — so the caveat is correctly placed. **Sharpest form: `N`
  is a count, and a count cannot identify a population**, so A-6 part (a) cannot substitute for part
  (b), which the packet does not say.
  **§I.4 concedes my own §2.6b citation** (correct site is §2.6c item 4, `:1122`; substance survives) —
  **and `SPEC:3629` makes the identical error**, one line below a correct §2.6c citation, so the
  correction should land there too or the spec keeps producing it. **§I.5 records a gap in my OWN
  pre-registered block list:** condition 3 covered population **over**-inclusion only, so the flux
  finding is under-inclusion my §F.5 did not pre-register — the one-directional-guard failure `F15`
  demands against, in my own pre-registration.
- [`REVIEW-20260910-z-acceptance-criteria-independent-derivation-partJ.md`](REVIEW-20260910-z-acceptance-criteria-independent-derivation-partJ.md)
  - ⚠ **PART J WITHDRAWS THIS LANE'S "clause (d) is moot" CLAIM — read it before relying on Parts F, G
  or H's disqualification paragraphs.** Measured at `05bf8647`: the packet's §2 table carries **A-4**
  (*"retained rank and retained-subspace projector gap across members, `‖P_0 − P_k‖_2 ≤ 1e-8`"*) as a
  **live** endpoint-A requirement with **no reference to the ρ bound**. The claim was true only of
  clause (d) as a terminal-outcome sub-clause of the ρ-leg at `RECOMMENDATION:392`, and false of the
  **test** the clause states — a clause's ROLE conflated with its CONTENT. **Anyone acting on "clause
  (d) is moot" drops a live A-4 requirement**, and the error's direction is permissive. Withdrawal
  banners placed at **all three** sites, since the surviving site is the one a reader lands on.
  **§J.1a: I held the disproof in a LATER part and did not collide it.** Part I §I.6 recuses from
  A-4 *"including its row in §2's table"* — and a recusal presupposes the item is live, so Part I
  contradicts F, G and H while quoting the row that disproves them. Same shape as `A14` vs `A30`;
  writing it up once did not prevent the repeat. **The mechanical fix: when recusing from an item,
  grep my own corpus for its name** — `grep -in moot` would have returned three of the four sites.
  **§J.2 relays clause (d)'s substance and assesses none of it** (sound as necessary, not sufficient
  since retained eigenvalues can move at fixed subspace, `1e-8` not load-bearing) — including the
  parts favourable to what this lane supplied. **§J.3 accepts the sharing-structure finding as REAL
  and rejects A-6 as its home:** Ruling 2's verbatim field list is `N` + convention + treatment + `p`,
  so requiring sharing structure of A-6 is a proposal to EXTEND the ruling (Joseph's call), not an A-6
  conformance defect — whereas the equal-`N` finding is an INTERNAL insufficiency, A-6's own part (a)
  failing to substitute for its own part (b). One A-6 defect, one gap in whatever consumes `B`; **not
  additive against the same requirement.**
- [`REVIEW-20260910-z-acceptance-criteria-independent-derivation-partK.md`](REVIEW-20260910-z-acceptance-criteria-independent-derivation-partK.md)
  - **PART K — the `assessor-F6` / reviewer-`F3` convergence ACCEPTED at the hazard level, and `F6`'s
  predicate delimited so a rev.-3 clause is not written against a reading `F6` does not support.**
  One hazard measured twice from opposite ends — a variance positive only by round-off, read as a real
  measurement (`eavailW_covariance.py:410-413`, re-verified) — **two measurements of one hazard, not
  two hazards.** `F6`'s own text already carries the structural point one level over: `:429`'s warning
  is gated on **exactly-empty** while `F-I` reaches near-zero at a **fully populated** row, which is
  the exactly-zero-versus-round-off distinction relocated.
  ⚠ **§K.2 DECLINES the extension, against this lane's own interest.** `F6` reads *"a **released
  projected row** … at the **point of release**"*; `s_proj` is an acceptance statistic, not a released
  product, so `F6`'s predicate never reaches its internal baseline and *"`F6` covers `F3`'s
  147-cohort"* does not follow. **This is the same wrong-stage correction this lane gave the
  coordinator about the sharing-structure finding, applied to its own item** — being the beneficiary
  of the over-extension is why it had to be said.
  **§K.3 names the gap that follows and refuses to close it:** a round-off-positive baseline inside an
  acceptance statistic is covered by **neither** `F6` (wrong stage) **nor** `A-7`'s abort claim (wrong
  condition — exact only for an exactly-zero baseline). A gap in the requirement set, not in either
  finding, and one that survives review because each half looks covered from the other's side.
  Proposing the closing requirement would spend this lane's verdict on `A-7`; §J.2 declined once
  already. **§K.4: reviewer `F3`'s 500-trial split is NOT re-run or verified** — §4.3/`s_proj`/`δ_proj`
  are routed away, so the convergence is accepted on the strength of the `F6` half only.
- [`REVIEW-20260910-z-acceptance-criteria-independent-derivation-partL.md`](REVIEW-20260910-z-acceptance-criteria-independent-derivation-partL.md)
  - **PART L — the coverage items: §2's rows A-1/A-2, §5, and §7's residues**, at `05bf8647` against
  `F1`-`F21` and §F.5's block conditions. No grade assigned.
  ⚠ **A-1's "§3.3's FIFTEEN reject conditions" is NINETEEN.** Enumerated at `6f24fb00`, §3.3
  (`:1242-1295`) carries `1`-`15` **plus `4b`, `4c`, `11b`, `11c`**. **And the omission is
  load-bearing: `4c` is the condition this packet's own §3 depends on** — §3.1(e) cites
  `reject_conditions=('4c',)` by name and Part I's probe reproduced it, so §3.3's *"costs nothing
  today"* is true **because `4c` bites**. `11b`/`11c` are labelled REV. 16 additions, so "fifteen"
  reads as a pre-rev-16 count quoted after the work that changed it — the expected-count shape, third
  instance this campaign, one of them mine (`B8`). A-1's CLASS (FIXED by spec) is right; the count and
  therefore the set are not.
  ⚠ **A-2's stated ground supports ONE declaration and the row requires FOUR.** "Four" is correct
  ((v) is A-6's) and I do not manufacture a count error. But against an endpoint that performs no
  inversion: **(i)** has no inverse to declare and **(ii)** no `ndf` — **unsatisfiable** except as
  "not applicable"; **(iii)** a rank-truncation scan is a NEW MEASUREMENT on a 10,694-bin object,
  which `F20` forbids requiring; **(iv)** transfers cleanly and is the only one A-2's own sentence
  argues for. **This hits §F.5's pre-registered `F18` condition** — inversion-grade criteria on an
  endpoint releasing no significance, the condition I said I expected to have to defend.
  **§5: the disposition is right and the characterization inverts the note's own scoping.** The three
  code facts verify, but clause (ii) does not reach 2D — `:645` scopes it to *"an N-D covariance"* /
  *"Any N-D χ²"*, `:628-634` **affirmatively justifies** the 2D choice (*"tested and holds… the scan
  is the evidence; 205 is not assumed"*), `:636` says *"it does not transfer to the N-D covariances."*
  **"LIVE" also unestablished:** `RANK-AND-INVERSION-20260810.md:56` verdicts the ours-only `252` as
  *"safe — it is the illustration, not a result"* and as a **pseudo-inverse**, where this script's
  branch is the **direct** inverse (`:126`). **Qualification 1 is unverified**: the inverted object is
  `Cu + Cb` (`:117`,`:120`), which the note puts at rank `140→201` (`:693-696`), and
  `np.linalg.inv` does **not** raise on a near-singular matrix, so `:127-133` does not cover it.
  **Qualification 2 (*"out of scope is not conformance"*) is correct and well-made** — exactly `F17`.
  Net: do-not-change survives because the file is a **diagnostic outside the released set**, which
  overstates neither the defect nor the protection.
  **§7 is an unusually good residue list** — residue 8 states the withdrawal-checker hole at severity
  with a handoff and names its own detector; residue 11 re-pins a population **by set difference, not
  by count**. **Two absences: `F2` is unmet AND unrecorded** (no released projection names its builder
  and commit, with four non-equivalent builders and a `main` finding that they diverge on refusal) —
  culpable; and the block-population assumption §I.2 falsified is unrecorded — **expected, not
  culpable**, since a residue list cannot name an unnoticed assumption, but flagged so its absence is
  not read as clearance.
- [`REVIEW-20260910-z-acceptance-criteria-independent-derivation-partM.md`](REVIEW-20260910-z-acceptance-criteria-independent-derivation-partM.md)
  - **PART M — rev. 3 assessment at `6bb8b32d`** (sha256 `dad55b57…`, 908 lines), against `F1`-`F21`
  and §F.5's block conditions. No grade assigned.
  **§M.1 records an ATTACK OF MINE THAT FAILED.** I expected rev. 3's *"constructions sharing the
  biased normalizer: thirteen"* to be my own §I.2 population error recurring — `:460`'s loop runs over
  `KNOB_BANDS`, not `VERT_BANDS`, and with `|R| = 27` the count could have been nearer 40. **Measured:
  `unified_throw_cov.py:79-80` defines `KNOB_BANDS` as exactly 12, `"Flux"` excluded, zero entries
  outside `VERT_BANDS`.** So 12 via `:460` + flux via `:467` = **thirteen is correct** and my
  hypothesis was unfounded. Recorded because a review reporting only its successful attacks
  misrepresents its coverage.
  **§M.2: `F7` fully incorporated and correctly extended** — three blocks, `C_flux` named as *"one
  level inside `Σ_V C_b`"*, per-block biased/unbiased split, and the normalization **verified
  numerically against `Z'Z/N` rather than read from the docstring**, which is stronger than `F8` asked.
  The `C_unified` restraint is preserved with its reason.
  **§M.3: `F10` confirmed independently on every leg, and the composition question is sharper than
  "supersede or duplicate."** `PROVENANCE-20260822-declaration-v-scalar5d-blocks.md` is **on
  `origin/main`**, its `:143-144` gives the **same** `N=100`/`24` values and the **same** *"enforced,
  not merely declared"* argument from the same raise, and rev. 3 cites it **zero** times. **New:** that
  record evidences `N` from `sbatch_finalize_5d_bkgaware_gpu.sh:167,168`, which at `6f24fb00` are
  `:422,423` — *"THE TWO MEMBER-LOCAL COMBINES"* (`:418`), i.e. **the member-scoped arm §2.1a says
  cannot have produced the digested bytes.** So ruling 10's record may be **right about `N` and wrong
  about the arm**, which makes "supersede / duplicate / extend" non-exhaustive — the equal-`N` finding
  turned on the provenance record itself.
  **§M.5: Part L's four findings are UNTOUCHED at `6bb8b32d`** (verified by `grep -c` on each claim
  string, `1 → 1` for all four), so `F13`-`F16` transfer verbatim with no re-derivation; §3's mechanics
  re-verified, probe `rc=0`, both controls passing.
  ⚠ **§M.6 DECLARES FIVE SLICES that now carry this lane's own contributions** (`:116`, `:166`,
  `:197`, `:294`, `:346`), enumerated rather than spot-declared. None is a remedy — each is
  re-derivable from cited lines, so independence for the packet holds — **but `§2.1a(b)` and §3.1's
  inertness paragraph are partial self-confirmation** (the equal-`N` framing and *"structurally
  unreachable"* are mine), and a second reader should spot-check them. Extending the boundary rather
  than waiting to be asked.
- [`REVIEW-20260910-z-acceptance-criteria-independent-derivation-partN.md`](REVIEW-20260910-z-acceptance-criteria-independent-derivation-partN.md)
  - ⚠ **PART N WITHDRAWS THIS LANE'S OWN "structurally unreachable" STRENGTHENING** — read it before
  relying on Part I §I.1 or on rev. 3's `:346-347`, which adopted it verbatim. A covering grep of
  `z_validator.py` at `6f24fb00` gives **FOUR** `boundary(...)` sites, not two: `:83` (leg-keyed,
  result discarded), `:110`, `:247`, and **`:296` inside `assess_null`**, whose signature at `:286`
  takes `boundary_key` as a **caller-supplied parameter with a default, not a declared leg** — so
  `assess_null(r_null, boundary_key='cause3_corr')` reaches it with no leg declared. **The
  exhaustiveness claim is false, so the conclusion is not established by that argument.** Measured
  caller census: five sites, **zero** non-default, so the path is **latent, not live**.
  **§N.2 — the irony is the finding, and it is the reviewer's:** I replaced *"inert"* (contingent) with
  an absolute word, and **the truth is contingent** — closed by a caller census, a fact about today's
  callers. *"Inert" was contingent in precisely the way the truth is contingent*; the connotation I
  objected to was the accurate one.
  **§N.3 — THIRD INSTANCE, and I held the disproof in my own grep output.** The Part I grep printed all
  four sites; I wrote *"exactly two."* With `B8` (eight launchers, wrote seven, because the spec said
  "exactly seven") and `A14` vs `A30`, all three share one mechanism: a correct measurement, then a
  claim over a **filtered subset** of it, the filter unnoticed and pointed toward the argument being
  made. Per-cell checking cannot see it; only diffing the raw output against the claim's population
  can. **And this one propagated into another lane's artifact and was adopted verbatim**, so neither
  author could catch it — which is why Part M §M.6 enumerated all five contribution sites, and is the
  strongest evidence yet that the boundary earns its cost.
  **§N.4: not prescribing the replacement wording** — correcting my own claim is required; choosing
  what §3.1 says instead is the designer's. **§N.5:** `:294` upheld and **upgraded to a live worked
  instance** (`PROVENANCE-20260822` = right `N`, wrong arm); my content-discriminates-inputs hedge
  discharged in my favour; their *"inverts"* withdrawn with **(a) duplicates, (b) repairs** standing;
  the *"could not have completed"* tightening **relayed, not verified**.
- [`REVIEW-20260910-z-acceptance-criteria-independent-derivation-partO.md`](REVIEW-20260910-z-acceptance-criteria-independent-derivation-partO.md)
  - **PART O — rev. 4 at `d915fe00`** (sha256 `bb752c9d…`, 1123 lines). No grade assigned.
  ⚠ **§O.1: the producer feeding `Σ_V C_b` is the UNIVERSE SWEEP, not `KNOB_BANDS`.** `SPEC:624` reads
  `Σ_V C_b` as `hCov_universe5d_<band>`, *"the same sweep estimator as the rest of `C_syst`"*;
  `analyze_universes_5d.py:290` writes those and `:213-222` builds each as `(Z.T @ Z)/D.shape[0]` —
  **biased `1/N` with per-band variable `N`**, skipping `< 2`. `unified_throw_cov.py`'s twelve `±`
  pairs (`:460`, arity forced at `:458-459`) plus flux produce **`C_unified`**, whose diagonal sets
  `g^c` — **not** the summands of the sum. So rev. 3-4's *"thirteen constructions"* is accurate about
  the **wrong producer** for A-6's purpose. **This also retires my own §M.1 reasoning:** I tested
  whether `KNOB_BANDS` was the right cardinality and never asked whether it was the right producer.
  **§O.2 answers the stability question: the two partitions RECONCILE EXACTLY** — same 45 bands cut two
  ways, `|V|13 + |R|27 + |A|5 = 42 pairs + 2p2h + Flux + norm = 45`, with `42×2 + 3 + 100 = 187` (+1 =
  the `188` file count). So *"stated and unreconciled"* is a choice, not an inconsistency, and the
  caution is sound — **but the one-line identity belongs in the record**, because a disclosure
  requirement quantified over "each block" is exactly where an unstated re-partition becomes a silent
  population change.
  ⚠ **§O.3: `2p2h` is OPEN and the code gives no basis for excluding it.** `analyze_universes_5d.py:220`
  applies **one** estimator to every band and makes no distinction between `2p2h`'s `D.shape[0]=3` and
  `Flux`'s `100`. **And `PROVENANCE-20260822` contradicts itself on it:** `:128` calls `Flux` *"the ONE
  genuine multiverse draw"* — entailing `2p2h` is not one — while `:127` *"explicitly declines to
  classify it"*. Not resolved here: it needs `PROVENANCE:233` item 6's bank read. If they are draws,
  `F7`'s recursion runs **two → three → four**.
  **§O.4: my §I.2 was a RE-DISCOVERY** — `PROVENANCE:128` has carried `Flux`/`100`/biased-`1/N` on main
  since 2026-08-22, and rev. 4 discloses that at `:198-199` **against its own interest**, which is the
  behaviour the review structure exists to produce.
  **§O.5: `F14` acted on cleanly** (A-2 narrowed to clause (iv), with (i)/(ii) as not-applicable and
  (iii) rejected as new compute — each with its reason, no silent drop; endorsement is **partial
  self-confirmation**, added to the §M.6 list), and **`F17` resolved on the composition principle** of
  Part J §J.3, returning A-6 to four fields with no Ruling-2 extension. **§O.6: the F10 row's HEADER
  still carries the withdrawn word *"INVERTED"*** while its body says *duplicates / repairs* — an
  incomplete withdrawal reaching the body and not the header, the same mechanism as my own three-site
  failure, and a header outranks the caveat beside it.
- [`REVIEW-20260910-z-acceptance-criteria-independent-derivation-partP.md`](REVIEW-20260910-z-acceptance-criteria-independent-derivation-partP.md)
  - **PART P — rev. 5 at `c33b5c86`** (sha256 `2366bf84…`, 1145 lines, `+26/−4` one file). Both fixes
  verified: **F20 closed** (`grep -c 'THEN INVERTED'` → **0**; the F10 header now names F20), and
  **`2p2h` stated as unresolved at header level with `PROVENANCE:233` item 6 as its route** — the
  disposition Part O §O.3 said the evidence supported, without claiming the answer.
  **§P.2 — the F7 row, handed to this lane explicitly: NOT filed as a finding, and the coordinator's
  restraint is right.** The row records F7's own claim and verdict, F7's substance (flux omitted, wrong
  normalization asserted) is unconditionally true whatever `2p2h` proves to be, and the or-four warning
  is **header-level**, not a caveat below. One token's refinement offered — *"at least three"* would let
  the row survive being read alone, the test this lane applies to others' verdict words. **Self-reference
  declared:** F7 is this lane's finding, so grading its row's wording would be grading the presentation
  of its own work.
- [`REVIEW-20260910-z-acceptance-criteria-independent-derivation-partQ.md`](REVIEW-20260910-z-acceptance-criteria-independent-derivation-partQ.md)
  - **PART Q — A-6(b) after the authorized provenance search.** No grade assigned.
  **§Q.1 resolves the coordinator's pending OPERAND question:** `combine_cov_nd.py:20` computes `C`,
  `:22` prints `sqrt(Σ C[i,i])`, and `:23-26` writes **that same `C`** — so the logged `sqrt-trace` and
  `sqrt(Σ h(i,i))` are the same object up to an exact double round trip, and neither `.3e` formatting
  (~0.03%) nor ROOT under/overflow can explain gaps of **3.6%** / **4.6%**. **But that closes the
  operand question, not the READER question** — their stated weakness (no known-matching case, so no
  demonstration the instrument returns `True`) stands. **A positive control is available in the same
  log line** — `reported 10694 bins` against the stored `n × n`, which tests addressing without
  needing a matching trace — **named, deliberately not run**, since running it would spend this lane's
  verdict on the fingerprint.
  ⚠ **§Q.2: the two exclusion grounds point OPPOSITE ways and the exclusion is SINGLY supported.** The
  fingerprint excludes; the job-level `TIMEOUT` does **not**, because the `--expected-ids` enforcement
  runs at `replica_manifest.py:44-48` via `:18`, **before** the `:22` print and `:23-26` write — so the
  logged *"100 replicas … [wrote] …"* lines are themselves evidence the check passed and the product
  was written. A timeout killing later stages cannot retroactively falsify a completed step. **If the
  fingerprint falls, nothing else excludes this execution.**
  ⚠ **§Q.3: §2.1a(ii) is underspecified at the word "SUCCESSFUL", and with one candidate execution the
  unit IS the answer** — job-level (`sacct -X` → `TIMEOUT`) fails, step-level (both combines printed and
  wrote) holds. The launch-plan-versus-record shape at the level of a single word. What would settle it
  is named (`sacct -j <job>.<step>`, a step exit code, or the log lines) and **not chosen** — the
  adjacent "what does *verified* mean" is already reserved to Joseph by `F9`.
  **§Q.4: the equal-`N` finding is STRONGER than when filed** — `N` for the released bytes rests on no
  surviving execution record, so part (b)'s only candidate evidence is under exclusion — **and the arm
  ambiguity closes** to top-level. **Joseph's intended-use declaration ENTAILS `F1` rather than
  satisfying it:** *"its explicitly named projections"* requires the enumeration without supplying it.
  `F3` is largely met, indirectly. **§Q.5 accepts the routing of §3-§3.3 and the block population away
  from this lane as correct**, and flags that §3.1 carries a sentence of this lane's that is now
  **withdrawn**.
- [`REVIEW-20260910-z-acceptance-criteria-independent-derivation-partR.md`](REVIEW-20260910-z-acceptance-criteria-independent-derivation-partR.md)
  - ⚠ **PART R — ANSWERED AND WITHDRAWN (§R.4): the answer is YES and it resolves AGAINST the question.** `unified_throw_cov.py:434` reads `xx = z["xs"]` (**unfolded cross-sections**) and `:437-442` assigns them to `knob_x[band][idx]`, so the ~45 MAT bands are built from **per-member unfoldings**, not the replicas — the population CAN exhibit the defect, `BEN-032` does not reach it, and §R.1's conjunction falls. **§R.4a: the detector's prior art is stricter than any lane stated** — `audit_gates_that_cannot_fail.py:585-587` names *"BEN-032 / SHELL_PIN_FLOOR"* in a `--min-files` refusal, `:592-593` **raises** on a detector failing its own power test, and `:471-474` records a step that *"silently blanked 95% of a file for eight days"* while *"provably powerful"* detectors reported clean. **The instrument enforcing the rule existed while three lanes violated it by hand.** §R.4b keeps why filing it was still right: it died to the one-line falsifier this lane specified and declined to run. Original framing retained below. **§R.5 (rev. 8 = `e968da42`): a LAUNCHER-level citation supersedes this lane's mechanism trace** — `sbatch_finalize_5d_bkgaware_gpu.sh:8-10` reuses the blocks while `:456` runs the bands combine under `mr_run`, the member-scoped runner, so the *production launcher* reuses blocks and regenerates bands per member. **`F22` carried at its CORRECTED strength: mandatory, not cosmetic** — and the *"whatever the cause"* half needs no lane's authority, since `audit_gates_that_cannot_fail.py:592-593` **raises** when a detector is not shown to fire. ⚠ **§R.5a narrows the watched residue to FIXED SUMMATION ORDER and REFUTES the cited cause:** measured, pairwise-vs-sequential is **bit-identical at n = 45, 128, 129 and 300**, so the `mii_anchor_comparator:241-246` route does not fire at band scale and **numpy's 128-blocksize story is not the mechanism** — if it were, `129` would differ from `128`. **Order is what perturbs** (`~5e-16`–`1.3e-15` on reversal). So the precondition rev. 7 silently acquired is one checkable property of one loop, not bit-reproducibility in general.
  - **PART R as filed — a routed QUESTION, explicitly not a finding:** under the **reuse** branch, does A-7's
  `s_proj` become a gate that cannot fail? `A-7` is routed away from this lane, so this composes **one
  relayed premise** (rev. 7 at `3e7c3271` derives `s_proj` as a function of `C_k − C_0`, so reused
  byte-identical blocks cancel exactly and `s_proj` measures **exactly `0.0`** on the reuse arm vs
  `0.562%` on regenerate) with **one measured fact** (`SPEC` §2.6c item 4 at `:1122-1125` — the
  reuse-vs-regenerate question is **OPEN**, *"this specification does not decide it"*, and §5 prices
  both). **If `s_proj` is exactly `0.0` on a branch Joseph may choose, then on that branch it returns
  zero irrespective of what it is meant to detect** — the repo's own named class, with
  `audit_gates_that_cannot_fail.py`'s header citing **BEN-032/BEN-025, *"a check run over a population
  that cannot exhibit the defect."*** **The designer's reading — exact separation makes the arms
  discriminable — is correct and is a virtue; the unstated reading is that on one arm the statistic
  cannot fail.** Same algebra, and which matters depends on an open decision. **§R.2 names the one
  condition that dissolves it** (if the member variation lives *wholly* in the reused blocks, the
  cancelling is correct reporting — cf. §2.6b's *"`C_stat`/`C_ML` are #13-invariant"*), and that check
  is inside the routed slice. **§R.3: filed rather than mentioned because it is a two-lane
  composition** — `(cause 6, Z)` owns the reuse question, A-7 owns the statistic, and a question owned
  by nobody survives review.
- [`REVIEW-20260910-z-acceptance-criteria-independent-derivation-partS.md`](REVIEW-20260910-z-acceptance-criteria-independent-derivation-partS.md)
  - **PART S — the projection-manifest yardstick, COMMITTED BEFORE THE MANIFEST EXISTS** (designer
  `cc2a71aa`, sha256 `41704ebe…`, 1524 lines, **digested-NOT-read**), same discipline as Parts A and F.
  **§S.1 verifies the blocker and gives its sharper form:** `p4_lib.build_projection_M:1354` is
  *"marginalization of **one** axis"* with `require(len(nb) == 5)` at `:1361` and `strides_l` over
  `range(4)` at `:1369`, while P1 drops **3** axes and P2/P3/P4 drop **4** each — so none is a
  single-axis drop and iteration is closed off. ⚠ **But the sharper problem is that NO EXISTING BUILDER
  HAS BOTH PROPERTIES:** `project_cov_nd.build_projection:79-84` does arbitrary keep-axis subsets yet
  its own docstring has `dst_index_of` returning *"-1 to drop"* (**silent dropping by design**, neither
  orphan check), while `p4_lib` refuses in **both** directions (`:1380`, `:1395`, `BEN-064` masking
  defect) with the wrong arity. **So the manifest cannot be completed by naming a different existing
  builder either** — and this lane is not designing the resolution.
  **§S.2 pre-registers six BLOCK conditions.** `S2` is the one nobody else has raised and it transfers
  this lane's own measurement: **if any map composes single-axis drops, the composition ORDER must be
  declared** — width weights compose exactly so the mathematics is order-free, but Part R §R.5a
  measured that **order perturbs at `~5e-16`–`1.3e-15`** while pairwise-vs-sequential is bit-identical,
  which is exactly the scale a reproducibility gate sits at. `S3` is Joseph's declared-exclusion-vs-
  silent-discard item with its mechanism named (`dst_index_of` → `-1`), `S6` bars Q3's rank declaration
  from being read as an `ndf`.
  **§S.3: the manifest CLOSES `F1`** (the enumeration Joseph's declaration entailed but did not supply)
  **and makes `F-I` maximal** — P2's **seven** bars each aggregate ~**1,528** reported 5D cells, so
  **~1.17 million off-diagonal entries enter one released bar**, an order of magnitude past P1's 42-bin
  case, with `cause3_corr` still withheld.
- [`REVIEW-20260910-z-acceptance-criteria-independent-derivation-partT.md`](REVIEW-20260910-z-acceptance-criteria-independent-derivation-partT.md)
  - **PART T — the PRE-IMPLEMENTATION baseline, pinned at `6f24fb00` before any code lands**, because
  *"additive only, no implicit fallback or overwrite"* can only be judged against a recorded before-state.
  §T.1 verifies six handed claims with two citations corrected (`adopt_unified_5d` `:80-81` not `:79-80`;
  `p4_lib`'s destination expression at `:1394`).
  **§T.2 makes §S.1 concrete as two line numbers:** `project_cov_nd.py:99`'s `dropped = int((~keep).sum())`
  is **source-side only** and sits in the builder that CAN express P1-P4's arity, while
  `p4_lib.py:1394-1395`'s `empty = np.nonzero(~M.any(axis=1))[0]` is the **destination arm** and sits in
  the builder that cannot. **The destination arm does not need writing — it needs moving, or the arity
  does.**
  ⚠ **§T.3 NEW FINDING: reuse-vs-regenerate is NOT open in code — it is selected by
  `MNV_EST_SEED_OFFSET`.** `SPEC §2.6c` item 4 calls it an OPEN scientific decision *"this specification
  does not decide"*, while `sbatch_finalize_5d_bkgaware_gpu.sh:421` prints *"MEMBER …: building **this
  member's OWN C_stat and C_ML**"* and `:425` prints *"undeclared: **reusing the archive's**…, per this
  script's original contract"* — and the `:8-10` header documents **only** the undeclared mode. The
  scientific rationale is genuinely undecided; the **behaviour** is not, and is bound to the membership
  variable. **This refines Part R against itself:** choosing a nontrivial `K` FORCES regenerate, so
  Part R's *"if Joseph chooses reuse"* supposed a freedom the launcher does not offer.
  **§T.4 strengthens the equal-`N` finding one level:** `:418-420` keeps `--expected-ids` at full ranges
  *"on purpose"* so a partial member REFUSES, so `N = 100`/`24` holds across the **whole member family
  by enforcement** — not two arms coinciding. `N` cannot distinguish **any** two members, which is why
  *"record the ACTUAL seeds, sources and revisions"* is the right instruction. **§T.5 holds `S2`**
  pending the implementation's route.
- [`REVIEW-20260910-z-acceptance-criteria-independent-derivation-partU.md`](REVIEW-20260910-z-acceptance-criteria-independent-derivation-partU.md)
  - **PART U — pin 1 (`f4aa0f08`): VERDICT = BLOCK, narrowly, on the enumeration's population.**
  Everything else in this lane's slice is READY.
  ⚠ **§U.1: `MEMBER_LOCAL_TODAY` (`:105-113`) has SEVEN entries and each carries a line number
  (`# :404-408` … `# :414`) — the population was selected by a 13-LINE WINDOW.** Measured against the
  behaviour instead: the launcher has **eight** `mr_prefix`-family call sites, six inside `:403-415`
  and **two at `:422-423` — `boot_nd_5d` and `seedscan_split_5d`, the REPLICA INPUT DIRECTORIES**,
  member-prefixed on the same condition. They appear **nowhere** in the module (`grep -ci` → 0).
  Consequential for three ascending reasons: they fall in **neither** returned category
  (`recomputed`/`pinned`); `:141`'s note says *"**every** component varies"*, a universal over the
  enumerated set only; and **the omitted two are the EXPENSIVE ones** — 100 bootstraps + 24 splits
  against five cheap combines — so an enumeration used to price a member **understates cost by omitting
  exactly the costly entries**, with `:418-420`'s full-range `--expected-ids` refusal leaving no cheap
  third option. **The irony is the standing law:** `:103-104` warns against inferring the population
  from *"the COMB line alone"*, then defines its own from a window of lines — fourth instance.
  **§U.2 READY — decoupling sound**, verified directly: `:75-76` *"there is no default"*, `:80-82`
  digests **required** under `SHARED_DIGEST_BOUND` (*"Sharing a PATH…"*), independence explicit at
  `:67`. Part T §T.4 is why a digest is the only route: `N` cannot identify a member.
  **§U.3 READY — additivity at BOTH levels:** two `A` lines / 690 insertions / zero modifications, and
  **no file I/O** in the module (only hit for `open(`/`TFile`/`RECREATE` is a **comment** at `:355`
  citing `SPEC` §1.6). So the `RECREATE`/defaulted-`--out` hazards are neither triggered nor mitigated
  and stay live for a later pin — correctly **cited**, not claimed closed.
  **§U.4 READY — suites re-run with the control first:** `136` control / `30` new / **`56` passed + `1`
  skipped** (confirming *"57 OK"* was the COLLECTED count), and the skip is self-documenting at
  `:628` (lightgbm absent, itself a recorded finding). **This lane's own harness failed first** — *"no
  tests ran"* on all three, a can't-look zero from an uncreated worktree, caught by the control.
- [`REVIEW-20260910-z-acceptance-criteria-independent-derivation-partV.md`](REVIEW-20260910-z-acceptance-criteria-independent-derivation-partV.md)
  - **PART V — pin 2 (`cc42cc3e`): Part U's BLOCK is DISCHARGED; new BLOCK on the non-member return
  contract.** Population now nine with the two replica dirs flagged and costed `DOMINANT`; the third
  category is warranted; the universal is **derived** at `:177`.
  **§V.1 PROVES exhaustiveness AND disjointness over the whole finite configuration space** (`member_offset
  ∈ {None,0,7}` × `block_source`): ✅/✅ in all six. **And supplies a property the code does not check** —
  `:176`'s `covered` is a **union**, which tests coverage and is blind to overlap, so a component in two
  categories would still read `covers_all_member_local = True`. Disjointness holds today and nothing in
  the artifact would notice if it stopped.
  ⚠ **§V.2 THE BLOCK: the non-member branch (`:153-155`) returns THREE keys where the member branch
  returns eight**, so on a fully correct non-member path `r.get("covers_all_member_local", False)` →
  **False** and direct access → **KeyError**. **That is verbatim the failure mode `:171-172` says the
  `not_used` category exists to prevent** — *"the coverage flag read False for a configuration that is
  fully specified, which would have looked like the omission it exists to detect"* — surviving one branch
  over, by **absence** instead of a computed value. Worse on the **majority** path, since non-member is
  the archive path. The campaign already ruled the shape: Ruling 2's *not applicable* and `F22`'s
  mandatory not-applicable-versus-satisfied. **Absence is not an admissible option;** which replacement
  is, is the designer's.
  **§V.3 credits a silently-failing trap avoided:** `:88` `is_member` is `member_offset is not None`, not
  truthiness, so **offset `0` is a member** — and `est_seed_offset=0` is a real declared value measured
  back in Part I. **§V.4** additivity cumulative: eleven `A`, only the three hook-required router files
  `M`, no production `.py` touched. **§V.5** suites `136` / `46` / `56+1`, control first.
  **§V.6 takes the offered `U` question:** the map-arm exemption is **correct** (a dense all-ones row
  cannot orphan a source bin), **but** `:470` applies `declared_exclusions` to **`M` only** while
  `:471-472` `vstack`s the extras unhandled, and `:307` scopes exclusions to **destination rows** — so a
  declared destination exclusion does **not** reach a functional dense over source columns. For P2 the
  `[3,100] GeV` catch bin **is** destination row 7, so an all-ones total rate would include support the
  displayed projection excludes. Possibly correct; **undeclared is the defect.**
- [`REVIEW-20260910-z-acceptance-criteria-independent-derivation-partW.md`](REVIEW-20260910-z-acceptance-criteria-independent-derivation-partW.md)
  - **PART W — cause-3 amendment adequacy conditions, COMMITTED BEFORE THE AMENDMENT LANDS.** Objection
  ground verified in three places: `SPEC:3550-3552` (*"the variation of the **assembled** `C_Z` … varied
  **jointly**"*), `z_contract:222-225` (`cause3_agg`, **unqualified**), `:233-235` (*"licenses nothing"*).
  ⚠ **§W.2 IS THE DECISIVE MEASUREMENT AND IT CLOSES TWO OF FOUR POSSIBLE ANSWERS IN ADVANCE.** The
  subset argument alone leaves an opening — `SPEC:3550` varies the **sweep-side and throw-side**
  baselines, and one could argue the blocks sit on neither. **Refuted:** `bootstrap_nd.py:47,55` passes
  `_est_seed` into the estimator and stamps it at `:67`; `seedscan_split.py:69` passes
  `args.estimator_seed` and stamps at `:99`. **Both excluded summands are functions of the estimator
  seed**, so holding them digest-identical suppresses a real component of exactly the declared
  variation. Response **(d) invariant is REFUTED**; **(c) negligible is unavailable as an assertion**;
  only **(a) narrow the claim** and **(b) narrow the subject — a contract change, Joseph's** remain.
  Plus Part T §T.3's independent tension: `:8-10`'s *"#13-invariant"* against `:421`'s member rebuild.
  **§W.3 pre-registers five conditions** — name which of (a)-(d); supply the measurement if (c)/(d);
  the operative word is ***licenses*** so changing what is MEASURED does not reach the objection;
  `cause3_agg`'s unqualified purpose must be qualified too or knowingly left; **no fourth grade token**.
  **§W.4: elements 3 and 4 must TRAVEL WITH THE GRADE** — `z_validator.py:166-167` already states the
  principle (*"the narrowing that must travel WITH the grade, not sit in a specification the grader may
  not open"*) and `_DIAGONAL_ONLY_SCOPE` is the non-suppressible mechanism, so licensing statements
  written in prose are put where the code says they do not survive.
  **§W.5 recommends `κ` stay WHOLE with the reviewer** despite its population clause being this lane's
  subject: a package split across two lanes has a seam, and silent removal is exactly what lives in
  seams — better to take it late than fragment it early.
- [`REVIEW-20260910-z-acceptance-criteria-independent-derivation-partX.md`](REVIEW-20260910-z-acceptance-criteria-independent-derivation-partX.md)
  - **PART X — cause-3 amendment Part A (`1b7db825`): VERDICT = BLOCK, two consequential issues.**
  ⚠ **§X.1 DECISIVE — the licensing clause is placed where it cannot travel.** A.5 item 2 says *"add
  A.4's licensing clause to the contract, in `cause3_corr`'s existing template"*, and Part I §I.1 proved
  **by execution** that entry is **inert to the outcome** — deleting it leaves `describe()`
  byte-identical, since `assess` reaches boundaries only at `z_validator.py:247` and `LegSet.describe()`
  only at `:107-111`, **both keyed on DECLARED legs**, and `cause3_corr` is named by none (its own
  stated premise). `Boundary.describe()` does carry `reason` (`z_contract.py:206`), so a clause on a
  **named** boundary would travel — this one would not. **The amendment records the licensing
  consequence of the deferral inside the very entry whose unreachability IS the deferral.** And
  `_DIAGONAL_ONLY_SCOPE` / `z_validator` / `scope_statement` appear **zero** times in the amendment,
  though `z_validator.py:166-167` states the rule verbatim.
  ⚠ **§X.2 — the "ambiguity" frame is wrong on the DATES, and it changes what Joseph decides.**
  `MNV_EST_SEED_OFFSET` first commit **2026-08-18**; `SPEC-20260906` appears **2026-09-06**, nineteen
  days later, against a **binary** launcher (`:417` own blocks / `:424` archive reuse). **So (a) and (b)
  were not indistinguishable — (b) DID NOT EXIST**, and `SPEC:3550` was written when only (a) was
  producible. Its natural referent is **(a) TOTAL**, so the decoupling **creates** (b): this is Part W's
  response **(b) NARROW THE SUBJECT**, a contract change and therefore Joseph's. *"Which did you mean?"*
  puts the burden on his memory; *"may I narrow the declared quantity, and here is why"* puts it on the
  proposer — **and A.6 already contains that argument. Right question, wrong grammar.**
  **§X.3 records what is satisfied, one of it well:** `W2` is met **honestly** — the amendment does not
  claim invariance or negligibility, and A.4(i) says *"the components held fixed are exactly the ones
  not tested"*; A.4(ii) adds a correct point this lane had not required (finite-ensemble is common-mode
  under fixed digests and cancels in `C_k − C_0`). `W5` satisfied, with the mechanism noted as looser
  than stated.
- [`REVIEW-20260910-z-acceptance-criteria-independent-derivation-partY.md`](REVIEW-20260910-z-acceptance-criteria-independent-derivation-partY.md)
  - **PART Y — cause-3 Part A at `f00e4bee`: VERDICT = BLOCK on ONE LINE.** Supersedes Part X, which
  does not carry forward. Content, destination and derivation all correct, and the clause **does** travel
  on refused outcomes — verified by execution.
  ⚠ **§Y.1 THE BLOCK: the interception point is OPTIONAL.** `:753` `def evaluate_a7(…, build_path=None, …)`
  and `:25` `scope = … if build_path is not None else None`. **Measured: the default call returns
  `state=GRADED`, `scope_statement=None`.** The cited model does not have this property —
  `z_validator.assess(leg_set: LegSet, …)` takes the leg set **positionally and required** (`:217`), so
  `sees_correlations` cannot be bypassed. **The discipline was copied at the function level and broken at
  the signature level.** Second reachability: a **non-member** build path plus a **multi-offset**
  `declared_K` — an inconsistent pair — grades with `scope_statement=None`. **Third instance of one shape
  in this module** (Part U's window-selected population, Part V's absent coverage flag, now this): the
  thing exists, is correct, and the path that matters does not reach it. One-line fix, not this lane's to
  choose.
  **§Y.2 — Part X both discharged, and the designer improved on what this lane offered.** It **rejected**
  `_DIAGONAL_ONLY_SCOPE` as host, **correctly**: `z_validator:237/276/282` key it on
  `correlation_leg_present`, **orthogonal to block sharing**, so the clause would appear with no corr leg
  and vanish with one — *this lane would have accepted a worse destination than the one built.* Travel on
  refusal verified by execution: `DEGENERATE_FUNCTIONAL` carries a non-`None` scope with `s_proj=None`;
  the three return sites all carry it, computed **before** any guard, and the `require` paths raise rather
  than return, which is correct since a raise is not an outcome to mis-license. Frame withdrawn, dates
  independently verified, ask now a **narrowing**. `W5` tightened: `cause3_corr` forces nothing.
  **§Y.3** suites `136` / `80` / `56+1`, control first.
- [`REVIEW-20260910-z-acceptance-criteria-independent-derivation-partZ.md`](REVIEW-20260910-z-acceptance-criteria-independent-derivation-partZ.md)
  - **PART Z — cause-3 Part A at `6f587e59`: VERDICT = READY FOR JOSEPH'S DECISION** on this lane's
  slice. Supersedes Part Y. Block closed and verified by execution on five cases **including a positive
  control**: `build_path` default is `inspect._empty` (**required**, same as `kappa`); omit → `TypeError`;
  `None` → refused; **non-member → refused**; member + `scale_kind='lambda_max'` → **GRADED with scope
  present**. Pinned by **signature inspection**, which is the level this lane named the defect at. Key
  sets identical across `GRADED` and `DEGENERATE_FUNCTIONAL`, scope present on the refusal. Suites
  `136`/`90`/`56+1`.
  ⚠ **§Z.2 — A SHAPE WORTH KEEPING, AND THIS LANE'S OWN PART V REQUIREMENT CREATED IT.** The designer
  found one of its tests had **encoded** the defect: `test_without_a_build_path_the_key_is_still_present`
  asserted a present key with a `None` value — the suppressibility bug as a passing assertion. Its
  generalisation: *a test written for property A can lock in a defect in property B, and the more
  rigorously it enforces A the more firmly it holds B.* **The correct rule was Part V's** *"one identical
  key set across all branches"*, and the test implemented it faithfully. **The specific failure: a
  uniformity requirement can be satisfied by NORMALISING THE DEFECTIVE CASE INTO THE UNIFORM SHAPE
  rather than eliminating it.** So the requirement was under-specified — *"uniform keys"* needed
  *"uniform keys over the configurations that SHOULD EXIST"*, and the second clause does the work.
  **§Z.3 corrects a relayed claim without blocking on it:** `scale`/`scale_kind` are **not** top-level
  return keys — they are nested at `detail['degeneracy']`, so a top-level `.get('scale_kind')` returns
  `None`, indistinguishable from *"no scale declared."* Whether the **support-refusal** branch (which
  returns before the degeneracy classifier) carries them **could not be determined** and is not
  asserted. Residual 1 is the reviewer's. **Method note: this lane's own first read used `.get('scale')`,
  got `None` from a MISSING key, and checked the full key set before asserting.**
- [`RECORD-20260910-z-assessor-declines-proxy-transcription.md`](RECORD-20260910-z-assessor-declines-proxy-transcription.md)
  - **DECLINES to proxy-commit another lane's findings, with reasons — filed outside the `REVIEW`
  numbering because it is not a review.** Agrees the concern is sound (*"a finding list with no
  rejections reads as a filter that never declines"*) and refuses the **verbatim** framing on four
  grounds, the first disqualifying alone: **(1) fidelity cannot be verified** — the words arrive
  **two hops** via the coordinator, so a record whose whole value is fidelity would be authored by the
  one party unable to check it, a fixture that is both claim and evidence. **(2) The coordinator is a
  strictly better custodian and the comparison made skipped itself** — assessor-vs-designer was the
  wrong axis; on first-hand possession and honest fidelity the coordinator wins. **(3) Proxying creates
  the attribution drift it prevents** — text saying *"another lane's words"* inside a commit whose
  metadata says *"mine"*, in a repo where **61 of 109 commits are already misattributed**. **(4) The
  premise is testable and this lane is a counterexample:** 15 commits touching exactly 16 paths, all
  own-review records plus the two hook-required index rows, **no subject artifact touched**, hook green
  every time — so *"read-only"* plausibly means read-only **with respect to the audited artifact**.
  ⚠ **Records a measurement error caught in the act:** the first attempt used a **two-endpoint**
  `origin/main..HEAD` diff, which included main's eight-commit advance and listed `SPEC-20260906` and
  `owners.tsv` as if this lane had touched them — a breach this lane nearly self-reported. Correct
  instrument is `merge-base`. **Counter-offer in §3: a RECEIPT under its own identity** — what was
  relayed, by whom, what was re-measured and what explicitly was not — already live in Part J §J.2,
  Part N §N.5, Part O §O.7 and Part M §M.6.
- [`REVIEW-20260914-final-clearance-e09513d8.md`](REVIEW-20260914-final-clearance-e09513d8.md)
  - **VERDICT: CLEAR on `68a3da8a..e09513d8`; no block. THREE FLAGS on the SUBMISSION step, which are
  not blocks on this delta.** ⚠ The authorization reached me **relayed** — this record is the review
  and clears; it is **not** the authorization. All four requested items hold: the two-state test
  asserts the **equality** (recursive directory snapshot vs never-started, with a reopen-don't-delete
  instruction) rather than the conclusion; **Finding 1's load-bearing middle leg CONFIRMED BY
  EXECUTION** — recovery preserves the claim while the product moves out, so the difference can only
  shrink; `_confirm_unclaimed`'s claims-only re-read is monotone by (B) while re-globbing would
  forgive a deleted foreign product; and all **7** bare self-citations in the block launcher resolve
  **by content**, the other three launchers carrying none. Suites run: 123 / 65 / 31 OK. **Submission
  flags, modelled locally:** (a) `grep Requeue` matches `Requeue=1` too, so a green grep proves
  nothing about the value; (b) the pipe destroys `scontrol`'s status, so a purged record (`MinJobAge`
  300 s) reads as "no match" rather than "could not look"; (c) up to **four** `sbatch` invocations
  (`0-7`, `0-20%10`, `0-39%40`, combine) but the plan verifies one job id. Withheld: cross-client
  `O_EXCL`, `mkdir` EEXIST on Lustre, `JobRequeue`.
- [`REVIEW-20260914-premise-B-durability-68a3da8a.md`](REVIEW-20260914-premise-B-durability-68a3da8a.md)
  - **My premise-(B) finding is CLOSED; ONE NEW FINDING: the stated cost of violating (B) is
  incomplete, and the omitted case is an AUTHORIZATION BYPASS rather than a refusal.** Eligible to
  review this — I named a two-disjunct requirement and declined a mechanism; the ordering recusal
  does not reach here. **Power control reproduced with my own `_tidy_claims` mutant:** operand-keyed
  inventory **FAILS (detects)**, seven-name ban **passes (slips)**, baseline and restored both OK.
  `FILESYSTEM_MUTATIONS` is genuinely operand-keyed and its three entries match my whole-module
  sweep exactly. Their three self-caught items verified: the blind-spot arm **asserts** the blindness
  with the invented rewording, the phrase-ban exemption is **counted** at exactly 1, and
  `PREMISE_PROSE_LINES = 21` is the measured value. "No behaviour change" verified — executable AST
  identical between `689e2cb6` and `68a3da8a` with docstrings stripped. **NEW FINDING, measured:**
  claim deleted + product PRESENT → refuses (as stated); claim deleted + product **ABSENT** →
  **ADMITTED**, a fresh attempt runs as a first attempt, bypassing `campaign-recover` and its
  per-retry approval — the exact act Joseph's prohibition names. Counts verified: 26 / 65 / 89 / 123.
- [`REVIEW-20260914-clause7-race-fix-8b89ff36.md`](REVIEW-20260914-clause7-race-fix-8b89ff36.md)
  - **⚠ PARTIAL RECUSAL: I am NOT independent of the ordering choice** — I named the requirement but
  then pointed at `require_campaign_complete` as the exemplar, and that became the design rationale.
  Not certification of that slice; independent on the re-read, the premises, the tests and the
  mutation analysis. **The defect is CLOSED, measured with the instrument that proved it:** my own
  probe's defect arm no longer reproduces it (`Exception not raised`) while its control still passes.
  Site dispositions verified by AST — `require_campaign_complete` byte-identical,
  `campaign_arm_status` **executable code identical** (docstring-only, confirmed by AST with
  docstrings stripped). **FINDING: premise (B) "claims are never deleted" is now load-bearing and
  BOTH its guards are narrower than it** — the AST ban covers 7 named recovery functions, the
  behavioural arm covers the happy path. Demonstrated: a claim-deleting helper added OUTSIDE that set
  leaves the ban passing **OK**. Not a live defect — my whole-module AST sweep finds only 3
  deleting/moving calls, none touching a claim, and claims are written only by
  `_write_json_exclusive` at `:1925`. **Mutation limitation judged GENUINE, not a harness artifact:**
  M8 and M9 each pass because each half is independently sufficient, so a behavioural mutant cannot
  reach either — and the protection is correctly structural instead (order pinned in source, re-read
  pinned both ways). Premise (A) IS bound to the real producers via a source-text arm on
  `do_blockunits`/`do_throws`. Counts verified: 17 + 65 + 89 + 123 + 90 = **384 OK**. Withheld:
  cross-client `O_EXCL` and `mkdir` EEXIST on Lustre — cluster still dead.
- [`REVIEW-20260914-per-task-recovery-79badb2f.md`](REVIEW-20260914-per-task-recovery-79badb2f.md)
  - **The delta does what it says; no NEW defect. One CARRIED-FORWARD defect: the clause-7 race
  persists at `79badb2f` and recovery RE-ENTERS it.** Kept separate from the `a71087e3` review per
  instruction. **Power question answered by execution:** the new subprocess arms, run against the
  broken `0636a786`, both FAIL with the original `ModuleNotFoundError: No module named 'r5_meter'` —
  so they would have caught it, and the in-process `main(argv)` arm provably could not, because it
  inherits the test module's `sys.path`. **Terminality executed across states:** `COMPLETING`,
  `SPECIAL_EXIT`, `RUNNING` refuse as live; an INVENTED state (`FLUXCAPACITOR`) refuses as
  unclassified — fails closed on a future Slurm state; all-`REQUEUED` and zero-rows refuse. The
  `SPECIAL_EXIT` asymmetry confirmed at both ends (`True` in admission's TERMINAL_STATES AND in
  `ATTEMPT_MAY_STILL_WRITE_STATES`) — two different questions, deliberate. **AST deletion ban
  mutation-tested both ways by me:** adding `os.unlink` to `recover_task` FAILS, and renaming a
  covered function FAILS, so it cannot silently cover less. **Non-Z guarantee reproduced on all four
  shipped launchers:** rc=0 with EMPTY stderr under `SLURM_RESTART_COUNT=9`, rc=3 for a Z requeue,
  rc=3 for a non-numeric count. Counts verified: 65 + 89 + 123 = **277**. **CORRECTED 2026-09-14:** my "the claim-reading surface grew from two sites to three" was WRONG —
  AST at both shas gives **three sites at BOTH**, same three functions, none added by the delta (my
  `grep | head` truncated before the third). The surviving half is assessed rather than left open:
  `require_campaign_complete` is a second GATE but is **NOT exposed** to the clause-7 property — it
  reads products FIRST and claims second, and computes `unclaimed` over the static declared task
  list, never `products − claims`. So the safe ordering already exists 250 lines below the unsafe
  one and clause 7 is the outlier. **Withheld — NERSC dead
  (rc=255, cert Sep 13 08:42):** `mkdir` EEXIST on Lustre (a DIFFERENT primitive; my `O_EXCL`
  measurement does not transfer), cross-client `O_EXCL`, `JobRequeue`, and the eight-suite total.
- [`REVIEW-20260914-namespace-ownership-a71087e3.md`](REVIEW-20260914-namespace-ownership-a71087e3.md)
  - **ONE DEFECT: clause 7 refuses a correctly-bound SIBLING under a read-ordering race.** Subject
  `lane/z-campaign-ownership-20260913` @ `a71087e3`; coverage does NOT extend to `79badb2f`.
  `verify_task_ownership` reads CLAIMS at `z_precursor.py:1432` and PRODUCTS at `:1439`, so a sibling
  that claims AND publishes between the two snapshots is reported unclaimed and the innocent task
  refuses at `:1450`. **Proven deterministically with a control** (sibling completing BETWEEN the
  reads refuses; the same sibling completing BEFORE succeeds — timing the only variable) and observed
  once in the wild at the `run` arm's real 40-wide concurrency. **Fails CLOSED** — cannot admit a
  foreign product, only reject a legitimate one — but the message misdirects, naming "a DIFFERENT
  campaign" for this campaign's own claimed sibling. Assessed as an **ARRAY** per instruction: block's
  full 21 tasks in waves of its own `%10` PASS; `run` is `%40`, i.e. **no throttle**, against a suite
  arm of seven. **`O_EXCL` on Lustre partially closed before access died:** `/pscratch` confirmed
  `lustre`, 1,920 real create attempts over 100 trials, exactly 100 winners, 0 anomalies — but
  **single-client**; the cross-client case is unmeasured and my own cleanup race destroyed the
  two-node attempt. Counts verified independently: 89 / 123 / 90 / 231 = **533 passed, 4 failed, 2
  skipped**. Launcher byte-identity confirmed by blob hash for all six.
- [`REVIEW-20260912-temp-repair-delta-41a64f02-and-consumer-list.md`](REVIEW-20260912-temp-repair-delta-41a64f02-and-consumer-list.md)
  - **F1, F2 and F3 CLOSED; all four mutation controls independently reproduced; the asymmetry claim
  CONFIRMED and stronger than stated.** Coverage extends to `41a64f02` and no further. **⚠ The
  landing authorization in this round is RELAYED and unverified — this verdict is not an
  authorization.** I applied each mutation myself (revert `ScanBlind`, dirname-as-literal, drop the
  token, restore `.npz`): baseline OK at 123 tests, **all four FAILED**, tree restored clean.
  **Asymmetry tested at every site with real `glob`** (not `fnmatch`, which does not special-case the
  dot): **0 of 18** sites select the post-repair temp, **18 of 18** selected the pre-repair one, zero
  patterns lack a terminal `.npz`, zero begin with a dot, zero use `include_hidden`. **Consumer list
  corrected:** 18 slab-selection sites across **8** launchers and **3** flags, not 14/7/2 --
  `sbatch_j28_adopt_5d.sh` was absent (4 sites) and `--throw-slabs` belongs to a **second** consumer
  program (`rescale_flux_universes.py:200-201`); the delta's own code comment already carries the
  right 18/3. F2's named population re-measured: 63 COMPLETED, 31 100 s, 8.6389 h, 1.39x and 13.2x
  all confirmed; its `77` all-states **not reproduced** (I get 74 on their own window, a fourth value
  for that column). **Corrects my own count:** the `test_uq_remediation` failure set is **four**
  tests, not five -- one is `subTest`-parameterised and emits two records, and I reported a line
  count as a test count. My "not live" pathlib verdict also rested on a sweep that omitted `os.walk`.
  `protect_throw_slabs` recorded OUT OF SCOPE per the relayed ruling, with its finding confirmed by
  execution first.
- [`REVIEW-20260911-temp-file-repair-against-T1-T14.md`](REVIEW-20260911-temp-file-repair-against-T1-T14.md)
  - **VERDICT: 12 of 14 MET, four EXCEEDED; `T9` UNEVIDENCED, `T14` PARTIAL.** Subject `05cf2d00`
  against the yardstick committed at `e92d4a85` **before the work existed**. Authorizes no launch.
  `T1` exceeded because the repair is a **property** not an enumeration -- a leading-dot temp name,
  verified invisible to `glob.glob` for `*`, `*.npz`, `block5d_*.npz`, `*.np[yz]` and to a bash glob.
  `T4` exceeded **and it did its job**: the first attempt broke publication exactly as predicted,
  because `np.savez_compressed` appends `.npz` to a NAME but not to a HANDLE (verified), and the
  completion arm caught it on first run. `T2` exceeded -- real child, `SIGKILL`, fixture precondition
  asserted. **FINDING F1:** `find_incomplete_writes` returns `[]` for a directory it cannot read, so
  "could not look" reads as "clean" (demonstrated by `chmod 000`, and again via a dir-wildcard
  pattern where `check_slab_population` PASSES with a temp present) -- latent, all **18** launcher
  patterns across three glob-bearing flags are fixed-directory, and Joseph's primary guarantee is
  unaffected because it rests on the name. **FINDING F2:** two figures the author has withdrawn
  (`n=74`, `7.7x`) now sit in a production comment; only `8.6389 h` and `1.39x` survive
  re-measurement. Also **corrects my own record**: the `-X` mechanism I published for the `MaxRSS`
  zero was not the one that produced it (a JobName filter alone suffices -- step rows are named
  `batch`), and my reachability flag is **withdrawn** (`10eb1bac` is contained in a remote ref).
- [`REVIEW-20260911-precursor-delta-10eb1bac.md`](REVIEW-20260911-precursor-delta-10eb1bac.md)
  - **Extends the `P1`-`P18` review's coverage from `8111a951` to `10eb1bac`**, which `a51c6503` did
  NOT cover; the `P1`-`P18` verdict is unchanged (all MET, admission still REFUSES at `558.42`
  against `500`). Delta re-measured: 1 commit, 4 files, +218/-3. **FINDING: the new marker at
  `sbatch_uthrow_block_5d.sh:33-35` re-states the reason the same file WITHDRAWS at `:350-353`** --
  the archive is `_sb`, so repointing does not move the archive, it lets an undeclared run write
  INTO it; the two readings license different repairs and the withdrawn one sits 317 lines above its
  own correction. Confirmed independently: the private-meter surface is **1** name in the module and
  **2** in the suite (AST over executable code; four docstring-only names, not three); the P12 lean
  table **by executing all four cases on both sides**; the marker's populations 8 and 36.
  **Regression CLOSED with a matched control:** `77a4af38` = 14 failed / 2895 passed / 6 skipped,
  `10eb1bac` = 14 / **3001** / 6, failure set **identical** (zero either way), `+106` = exactly
  `test_z_precursor`'s tests, zero `z_precursor` failures. **CONTRADICTED:** `MaxRSS` is not empty --
  `-X` hides a step-level field; **206** step rows carry it, peaks 16-48 GiB against 80-110 G
  requested. Maxima table's MAX column confirmed on all three populations (block 12 h = **1.39x**
  its 8.6389 h max); its `n`/`mean` do not reconcile. Bank cleared against a **second** consumer the
  relay did not check, including the pre-J28 all-ones signature.
- [`REVIEW-20260911-precursor-repairs-against-P1-P18.md`](REVIEW-20260911-precursor-repairs-against-P1-P18.md)
  - **VERDICT: every one of `P1`-`P18` is MET; the finding is that the admission accounting REFUSES the
  run.** Subject `lane/z-precursor-repairs-bg-20260911` @ `8111a951` against the yardstick committed at
  `2d61d81f` **before** the work existed. Authorizes no launch; guards **executed**, not only read, in
  an isolated worktree. **Reproduced to the cent:** committed `48 + 252 + 240 + 3 = 543` CPU task-h at
  zero retries, `+ 15.4231` charged = **`558.42` against R5's `500`, headroom `-58.42`**, with arms
  parsed from the real `#SBATCH` lines. `P14` reuse confirmed (`import r5_meter`, its parser and
  validator; durability note only — it rides **private** functions). `P15` **improved on this lane's own
  wording**: the throttle bounds concurrency, not total spend, so for a total cap it is irrelevant.
  `P17` binds at **admission** and touches no running job. `P12` **executed**: `='0'` refuses, `='7'`
  refuses, unset passes — and the Python guard tests key presence while the shell tests non-emptiness,
  disagreeing on `=''` **in the safe direction**, deliberately. `P1`/`P2` exceeded: the decisive arm
  asserts the mask is still **BUILT** but not **WRITTEN**, the exact `3be8c052` distinction, with
  `ast.parse` guarding the harness and a reach precondition — and there are **five** mutation targets,
  not the three relayed. `P13` repairs this lane's own dim-2 finding: the dump arm goes from
  `GUARD=0 mnv_inv=0 member_gate=0` to full parity with both roots mandatory via `:?`. `P18`'s
  inertness control asserts the contract returns **`None`** — *"must do NOTHING, not refuse"* — which
  is what separates a guard from a run-blocker. **(b) confirmed correct:** `x_cv > 0` unchanged, and the
  mask is indexed over the **binning** not the support, because a support-indexed mask is all-ones by
  construction. **Donor confirmed a record:** derived from the glob and labels, with a detector carrying
  its **own positive control**. **⚠ `_atomic_savez`'s temp-name fix is a PRECONDITION for the cap
  remedy** — cutting `--time` (the `252` h block term) raises wall-kill probability, the exact path that
  leaves a temp inside the consumer's glob. **Residual scoping judged RIGHT** — `P11` is satisfied by
  **relocation** (the precursor now runs under a mandatory declared namespace, so it is no longer an
  undeclared run) — **on one condition: a `CITABLE FOR`/`NOT CITABLE FOR` marker and an owner on the
  launcher itself**, since the general launcher's next user will not have read this review.
  **WITHDRAWN HERE: this lane's `r5_meter` timezone finding** — `:551-557` sets `TZ=UTC` in the child,
  so the live path was always on the UTC basis; what I measured was my own hand-rolled capture, and I
  attributed it to the argv after having just written that the environment, not the argv, determines the
  window. **Not verified:** the `14 / 2997 / 6` regression counts (the `+102` **is** verified).
- [`PREREGISTER-20260911-temp-file-repair-acceptance-criteria.md`](PREREGISTER-20260911-temp-file-repair-acceptance-criteria.md)
  - **`T1`-`T14` for the temporary-file repair, fixed BEFORE the implementation existed.** Approves
  nothing. `T1`-`T4` are the four clauses of Joseph's verbatim requirement; `T5`-`T14` are what makes
  them provable. Anchored on measured facts: publication is ALREADY atomic (`os.replace` in the
  product directory) and must stay so; the `except` branch cannot be the mitigation because a
  wall-kill is `SIGKILL`; there are **TWO** selection surfaces (the bare launcher glob and the
  declared-population check at `:294-315`); the consumer population is **nine** launchers over five
  product stems across 4d/5d/fps/corrected, not the precursor's four arms. Heaviest weight on `T4`,
  the successful-completion arm -- but only its **contents** assertion catches a repair that fixes
  selection by breaking publication, which is why `T5` (same-filesystem rename) sits beside it.
- [`PREREGISTER-20260911-precursor-repair-acceptance-criteria.md`](PREREGISTER-20260911-precursor-repair-acceptance-criteria.md)
  - **`P1`-`P18`, the acceptance criteria for precursor repairs (b)-(g) and admission accounting, fixed
  BEFORE the implementation existed** so the later verdict is checkable rather than fitted. Approves
  nothing; no repair existed at authorship. **Baseline verified rather than accepted:** the
  `--no-verify` disclosure holds — `da1da9f4` is reachable from **no ref** and has a tree
  **byte-identical** to `77a4af38` (`1447639b…`), same parent, same subject; the landed set is exactly
  the 4 minimal paths; *"code-only is not self-consistent"* is confirmed at the mechanism
  (`SANCTIONED` carries `probe-z-projected-stability-20260910.py` and
  `test_every_sanctioned_exclusion_still_exists` asserts presence); and **365 tests re-run OK**
  (90/57/58/136/24). **⚠ OPERATIONAL FINDING: `origin/main` is still `6f24fb00` — the landing is NOT
  PUSHED**, `main` is 1 ahead / 0 behind after an explicit fetch, so no other session or reviewer sees
  it. **Criteria:** reach-per-mutation and distinguishable-from-infrastructure-refusal (`P1`-`P4`);
  identity-and-coverage over the **enumerated declared set**, both directions, all four arms, a glob is
  not a population, and a non-empty population by construction (`P5`-`P9`); non-emptiness **refuses**
  with absent distinguished from empty, writer/reader agreement proven on the **UNDECLARED** path,
  `mii/` as a refusal not resting on `mr_declared()`, and `sys.path[0]` named per entrypoint across the
  four competing mechanisms (`P10`-`P13`); admission accounting that **calls** `r5_meter` and bounds
  charged spend **plus maximum remaining exposure including queued and retries**, on an explicit-UTC
  basis with a test that fails if the naive basis returns, **preserving R5's running-at-the-stop rule so
  the cap binds at ADMISSION** (`P14`-`P17`); and silent positive controls on the same call path
  (`P18`). **Donor question flagged:** `z_assembly.py` has no donor binding at all, so a donor appearing
  in code without a committed decision is a decision taken by implementation, and this lane will treat
  that as a finding while refusing to answer the question itself.
- [`PREREGISTER-20260915-epsilon-and-B-acceptance-requirements.md`](PREREGISTER-20260915-epsilon-and-B-acceptance-requirements.md)
  - **`E1`-`E12` for `ε` and `B1`-`B9` for §3.7a's `B`, written and committed BEFORE this lane opened
  the proposal they assess.** Grades nothing, proposes no route, no threshold and no number; adopts
  nothing. Derived from `SPEC` rev. 21 **only** — every requirement carries a `SPEC` citation and none
  cites the proposal — and all **28** citations were content-verified after an initial set was found to
  be off by up to `34` lines. **The governing blob does not fork:**
  `296511ab601e44545d7ed3904811a74ee14b3094` is byte-identical at `main` `9dba1194`, at the criteria
  lane's `8a42f8ea` and at `df0a8603`. **Load-bearing structure:** `ε ∈ [B, S]` with `B ≤ S` a
  **precondition and not an arithmetic step** (`:1779-1782`); a reproducibility floor bounds `ε` from
  **below** and cannot justify it (`:1406-1409`), the direction rev. 16 inverted; an imported constant
  is not an imported error model (`:1646-1650`). **Two non-requirements recorded so they are not read
  in:** `B > S` says nothing about the world (`:1744-1751`), and **no endpoint is prohibited** —
  rev. 17's *"never taken as an endpoint"* is withdrawn (`:1764-1769`). **Naming hazard filed:** at
  least three live objects are called `B` (§3.7a's bound, publication **Endpoint B**, and the `lane_b`
  owner rows), two of them in one sentence of the routing record.
- [`ASSESSMENT-20260915-epsilon-1e-9-and-B.md`](ASSESSMENT-20260915-epsilon-1e-9-and-B.md)
  - **`ε = 1e-9`: UNGRADEABLE AS AN `ε`. `B`: NOTHING TO GRADE.** Both are complete answers, neither
  is a block, and **`ε = 1e-9` is NOT refuted.** Graded against `E1`-`E12` / `B1`-`B9` committed at
  `923a321c` beforehand. **All three of `ε`'s steps confirmed**, step 1 in **exact rational
  arithmetic** against the real `support_mask` (3,998 draws with zeros and negatives + 4 adversarial
  cases, 0 violations; bound TIGHT at equality) — the load-bearing detail being that `null_ratio`
  masks BOTH operands (`z_statistics.py:71-79`). Step 2's authority is **stronger than the proposal
  claims**: `REPRO_RTOL_PER_BIN` enters at `5d617da8`, **author Joseph Bailey**, so *"Joseph
  declared"* is git-corroborated, not just comment-sourced. **Why it is still ungradeable:** steps
  1-3 establish a **feasibility floor**, the exact role `SPEC:1406-1409` says *"cannot justify
  `ε`"*; taking it as the value needs it to be `B`, and it is not — the proposal says so itself.
  `SPEC:1257` `4c` makes running against an un-derived boundary a REJECT. **`F1` NEW:** a THIRD
  transfer limit — the imported floor is a **cross-concurrency** comparison (`conc_new: 6,
  conc_reference: 4`, `p4_lib.py:197`) sized so *"a CONC change does not force a re-derivation"*;
  cuts both ways and both are reported. **`F2` NEW, the concrete threat:** BOTH endpoints are
  missing — `S` covers the F7 channel only and `SPEC:1662` calls the uncovered completeness division
  *"an amplification channel with no `n`-dependent bound"*, so `ε ≤ S` is undemonstrated and the
  routing sentence needs the scope repair *"not binding THROUGH THE F7 CHANNEL"*. **`F3` NEW:** the
  consistency check §C.3 left UNRESOLVED is now answerable on the precursor — `ε / r_null =
  **2.246e4**` — against §C.2's own *"a gate essentially nothing can violate"* standard; recorded as
  an observation only, since `SPEC:1410` forbids setting `ε` from it. **`F4`:** the falsifier is
  **unevaluable**, not merely unevaluated — both operands unbuilt; `B_loose`'s withdrawal
  independently confirmed (`1.831e-11` is the coherent ceiling at `:158`, a different figure from
  `56471429`'s `1.9e-11`). **Checked and NOT faulted:** the p4/rep mask mismatch is safe in
  direction AND empirically void (`n_cv_negative = 0`). **On `B`:** the relayed evidence leg is
  §4.5's diagnostic, which measures *"sensitivity to the envelope"* — **pinned-vs-unpinned is the
  divergence, not the bound** — failing `B1`/`B2`/`B5`/`B7` on the proposing lane's **own**
  `Z_CONSTRUCTION_PLAN:501-506` items 1-2. **⚠ `owners.tsv:15` names session `[cb0b6b]`; this
  session is `d93bf047` and no mapping exists in the repo** — proceeding on the owner_id role only.
- [`ASSESSMENT-20260917-decision-support-section-12.md`](ASSESSMENT-20260917-decision-support-section-12.md)
  - **Bounded closure check of `DECISION-SUPPORT-20260916` §12 at `a14ff88b` against the recorded
  decisions. CONFIRMS 1, 2a, 3, 4b, 6; REFUTES one generalization in 4; PARTLY REFUTES 2b; CONFIRMS
  7's numbers and CORRECTS its stated reason.** Closes nothing — full `S` stays **OPEN**, §7 item 4
  **UNASSESSED**, `θ` **RECOMMENDED NOT ADOPTED**, `A1` OPEN, Gate 2 FAIL. No compute, and **no
  cluster artifact read**, so every `z-null.npz` / `z-cv.npz` figure is RELAYED. **`G1`:** §12.5
  item 3 calls it *"`[cb0b6b]`'s **withheld** verdict"* — this lane withheld none; `fb9fdec1`
  (09-17 08:32) and `480bed76` (09-17 08:38) **postdate** `fdf5e510` (09-15) and were never routed.
  **UNASSESSED, not WITHHELD.** **`G2`:** withdrawing *"`S` is non-binding"* vacates the fallback's
  **BARRED** status — §2.4 `:235-237` says *"neither clause bars it alone… it is the composition
  that bars it"* — leaving it **UNRULED**, and the one unruled §6.4 question now governs the
  fallback, route (ii) **and** route (i)'s own control. The withdrawal has not reached `:226` /
  `:232` / `:233` / `:551`; counts `non-binding` 7, `EXHAUSTED` 3, `barred` 7. **`G3`:** the
  population substitution runs in **two** directions and only one was priced — route (i) pins
  **estimator parameters** (`Z_REPRO_KNOBS:127-138`, *"the estimator parameter, NOT
  `OMP_NUM_THREADS`"*), not allocation shape, so the non-identity **is** attributable to variables
  route (i) would pin; *"route (i) is FALSIFIED"* applies the estimator's consequent outside its
  antecedent. Narrow conclusion (route (i) cannot qualify these products) **stands** via 4b, and
  the recommendation is undisturbed. **`G4`:** two decisions upstream of Alternative 1 are absent
  from §12.5 — **`θ`**, whose own `:177-200` says it is a *"SCIENTIFIC CEILING and explicitly NOT
  the operative determinism gate"* and warns that recording it as the gate *"repeats the vacuity
  defect that `S` already demonstrated"*, and whose independent assessment **Joseph made a
  precondition** (`:4`); and **§5.7 condition (a)** (`PROPOSAL:459`, *"the declared projection set
  has not been checked"*), dropped at all three sites that say *"every projection"*. **So under
  Alternative 1 the actually-blocking decision is `θ`, not the active set.** **Item 7 re-measured:**
  line 4 byte-identical on `origin/main` (the **files** are not), `9/12/18/90`, `5.205`, headroom
  `403.8038888888889`, `2.229%`, `r5_meter check` **exit 0** — but R5 charges *"sum of post-t0
  **`ElapsedRaw`**"* (`r5_meter.py:73`), so `3.00` is a **reservation** bound (`SPEC:3140`), not a
  metered charge; same numbers, correct authority.
- [`ASSESSMENT-20260917-theta-and-the-propagation-argument.md`](ASSESSMENT-20260917-theta-and-the-propagation-argument.md)
  - **Joseph's five bounded questions on `θ` (`480bed76`) and the propagation argument (`affc9e03`
  §5.7/§5.8). RECOMMENDED DECISION: do not adopt `θ = 7.11e-2` as a scientific CEILING on its
  present derivation** — the derivation is honest and bars all three wrong routes, but it establishes
  a **resolution/feasibility figure**, which `SPEC:1406-1409` says *"may bound `ε` from BELOW … it
  cannot justify `ε`"*. Assigned as the upper end of an interval it is rev. 16's direction inversion
  one level down. Adopts nothing, grades nothing, closes neither `S` nor §7 item 4; no compute and
  **no cluster artifact read** (all `z-*.npz` / band-ROOT / `G2_g_domain` / `G3R` figures RELAYED).
  ⚠ **CORRECTED 2026-09-18 — Joseph declined `θ` AND declined the floor relabeling, and four claims
  here are corrected; I re-measured all four and all four hold against me** (probe
  `probe-20260918-my-own-theta-claims-corrected.py`). **`T1` stands:** `√(2/(N−1))`/2 reproduces at
  `N=100 → 0.071067`, `N=24 → 0.147442`, from frozen launchers. **`T2`'s MAGNITUDE LEG IS
  RETRACTED:** per-bin variance-estimation errors correlate as `ρ_ij²` (measured `+0.8098` at
  `ρ=0.9` against a predicted `0.8100`), so the aggregate suppression is `√(c̄+(1−c̄)/n)` — `0.90`,
  i.e. **none**, at `c̄=0.815`. The coherent/incoherent **sign** survives as `p4_lib.py:141`'s own
  statement; the conclusion that `θ_A` is too loose for aggregates is **NOT ESTABLISHED**, and what
  decides it is `c̄`, the mean off-diagonal `ρ_ij²`, **a third unmeasured quantity** (at `c̄=0.01`
  the suppression is `10×` and the argument returns). **`T3` corrected:** *"doubling would halve
  `θ`"* is wrong by a factor — `√(99/199)=0.7053`, a `29.5%` reduction, halving needs `N=397`; the
  reductio survives at the corrected magnitude, and a **sharper** objection sat inside `T3`
  unused — for a bootstrap, raising `N` lowers the FORMULA while the quantity has an `N`-independent
  floor, **severing** the two. `T3` otherwise stands: both populations violate the i.i.d.-Gaussian
  assumption, conservatively. **`T4`:** `θ`'s scale needs
  `w_stat,i`/`w_ML,i`, **different terms from `f_i`**, and **closure (B) reaches neither** — so *"one
  quantity, two open questions"* is not true today. **`T5a`:** `ΔC = ΓC + CΓ + ΓCΓ` and the norm
  bound ARE valid finite; **`dσ/σ = f·(dg/g)` is NOT exact** — `2.7%` off at `u = θ`, `11.7%` at
  `θ/f`, and invisible at the `1e-6` verification point. **`T5b`:** the exact inversion gives
  `‖ΔC‖/‖C_infl‖ ≤ ((1+θ)²−1)/min f`, tighter than the published linear form, moving the 100%
  crossing from `min f ≈ 0.1717` to `0.1473` — **the error is conservative and fixing it HELPS
  Alternative 1.** **`T5c`'s INFERENCE IS RETRACTED:** `g ≥ 1` by construction
  (`z_assembly.py:6`, `G_FLOOR` enforced) and `g'` uses the same `max`, so `u ≥ 1/g−1 ≥ −0.9434` at
  the relayed `g_max` and `≥ 0` on clamped bins — `γ` is finite from construction, no tolerance
  needed. **The `f ≤ 0.1371` threshold arithmetic stands**; only *"`g` may fall to zero"* was wrong. **`T5d`:** *"the same factor bounds every projection"* is
  **FALSE** without a further condition; measured `179.9` against a limit of `0.69` with a PSD `C`
  and non-negative weights, and `∞` at exact annihilation — and `AGENTS.md:27`'s rank-247 (λ > 1e-12·λ_max) precedent
  makes null directions live in this family. **`T5e`:** `6528 + 4166 = 10694`, so **38.96%** of the
  support has `g` pinned at 1 and contributes `u = 0` **while membership holds**; taking `min f` over
  the full support is a mis-specified minimisation. ⚠ **CORRECTED:** *"not a population choice"* is
  **withdrawn** — membership is perturbation-dependent, so `E1` needs a **declared margin** and IS a
  population choice under this document's own Q5 rule. My headline outran my own caveat, the shape I
  had just charged another document with at `ed18a231` `G2`. **`T6`:** vacuity is a property of the
  bound — the uniform-`γ` substitution deletes the anti-correlation between allowance and
  contribution, and the published percentages are relative to **`C_infl`** while the use consumes
  **`C_Z`**. **Q3:** Alternative 1 supports only `K1`; `K4`, a **supported reproduction path**
  (`AGENTS.md:14-15`), is absent from §12.7's exclusion list and is what makes the envelope claim
  non-optional. **Q4:** all five `null` clauses REMAIN; `θ` and `ε` are not interchangeable on four
  grounds, decisively that **`θ` is structurally blind on 39% of the support**; replacing the null
  criterion needs an amendment to `SPEC` §6.4 **and** to reject condition 11 (`SPEC:1267`), which is
  Joseph's act. **Q5:** three exclusions with opposite compliance status — mechanism-derived (E1)
  **yes but only with a declared margin**, bound-derived (E2) **barred**, use-derived (E3) only once the use is declared; and the
  **projection set is enumerable from publication scope, so what is owed is a CHECK, not a
  judgement** — the highest-value zero-compute item and absent from §12.5.
- [`ASSESSMENT-20260918-integrated-acceptance-and-E1.md`](ASSESSMENT-20260918-integrated-acceptance-and-E1.md)
  - **The integrated acceptance proposal (`d8f5ccd5`), with `E1` and `E2` PERFORMED rather than
  awaited. Adopts nothing; acceptance is Joseph's act.** ⚠ **Cluster access is live from this
  session, so `E1` — which the proposing and routing lanes could not do as owners — was performable
  by a non-owning lane and I did it. READ-ONLY login-node work: no `sbatch`, no `srun`, no job
  attempt, `R5` untouched.** So **every product figure here is MEASURED BY ME, not relayed** — the
  change from the two previous assessments. **`E1`: RECONSTRUCTS.** Digest `cb82fc32…` matches; the
  predicate recomputed and **CHECKED elementwise identical** to the persisted mask (which is what
  `11b` requires); `10694` support, `55162` genuine zero, **`0` negative**; `r_null =
  4.45200021375829101e-14` in **three** of my own summation orders **and bitwise equal to the
  blob-pinned `null_ratio`/`reconstruct_null_ratio`**; versus the build's `…829038e-14` that is
  **1.00 ULP**. Three reconstructions now exist within `2 ULP` and none is bitwise — the argument for
  a numerical criterion, made on the criterion's own operands. `10683/11` bitwise split, `0` off
  support, `max|Δ/x| = 1.755e-12` at grid-index `31499`, `min|ρ| = 0.0` exactly, margins `569.7×`
  and `2.246e4×` — all confirmed. **`I1`:** the deployment's `z_statistics.py`/`z_contract.py` are
  **byte-identical to the committed blobs**, and the shared cluster checkout has neither, so the
  pilot ran from the deployment — the opposite of the `OI-136` shape. **`E2`: DISCHARGED from
  COMMITTED evidence, no cluster read needed** — tolerance at `5d617da8` (2026-08-08, Joseph Bailey)
  pre-dates the product by **37 days** and the observation by **40**. **`I2` — the routed finding is
  REFUTED AS STATED:** `[B, S]` lives in §3.7a, which `SPEC:1552` titles *"ENTIRELY PROPOSED"*, so
  there is nothing to amend — **and this also corrects my own `E1` requirement at `923a321c`**, which
  treated the interval as governing. But the instinct is right at a worse location: **§3.6a item 3's
  step (ii) is unsatisfied and reject condition `4c` is LIVE**, which is worse than a needed
  amendment. **`I3`:** step (ii) is now **unperformable** for these products, because §6.4 requires
  the bound *fixed before production* — so the decision is a **ruling on §3.6a item 3**, not an
  amendment and not *"no amendment required"*. All three prior positions, including mine at
  `ed18a231`, are restated. **`I4`:** the transfer's falsifier stays **unevaluable**; the `10.8×`
  direction argument is confirmed and is not a substitute. **`I5`:** the `:1406-1409` charge is half
  right — the proposal's feasibility/justification split is correct, the sentence does not license
  omitting step (ii), and the symmetry charge against my `θ` use does not land. **`I6`: REFUTED** —
  the per-bin-maximum rejection **is** on the record at `SPEC:1627` under a heading that says so.
  **`I7`:** three citation corrections, one of which **withdraws a note of my own** — `z_contract.py`
  has **FORKED** (`G_FLOOR` at `:84` on main, `:126` on the pilot lane), so my "misaddressed" verdict
  was itself tree-less.
- [`READBACK-20260918-rank3-lineage-footing-components-completeness.md`](READBACK-20260918-rank3-lineage-footing-components-completeness.md)
  - **Rank 3 of the designated audit (`ebba67ab`), four parts, four verdicts. Every product number
  MEASURED BY ME** via read-only login-node `uproot` — no `sbatch`/`srun`, `R5` untouched — so
  **nothing here is relayed.** Adopts nothing, grades no cell, infers no requirement to regenerate.
  **PART 2 CLOSED, ELEMENTWISE AND BITWISE:** production `hXSecND_flat` vs persisted, **65856 of
  65856 identical**, `max|Δ| = 0`; support mask and row order likewise — **and that performs the
  external CV cross-check that stood UNPERFORMED** (`SPEC` `11c`), while correctly leaving
  `G3R.stored_cv_cross_checked` false, since that flag records that the producer was handed no
  operand. **PART 1 TRACED:** the parent declares `centering_convention = mean-centered`,
  `uthrow_source = unified_throw_cov_5d_fluxfix_20260806_full160.root` — **a DIFFERENT throw ensemble
  from the pilot's 2026-09-14 precursor** — and its `upstream_fixed_seed_null_norm = 5.8223e-50` is
  **G's**, against the precursor's `1.4302e-50`; the two mean-shift norms agree only to 10 s.f.
  (`4.5e-11`). The `hInflation_g` mismatch (`max|Δ| = 2.329`) is **CORRECT, not a defect** —
  `compute_g` recomputes it (`z_assembly.py:64`, `z_build.py:587`), which is the evidence the pilot
  did not inherit the parent's covariance. And the registry's ADOPTED 5D covariance
  (`ESTIMATOR_REGISTRY:29`) is the **`_uthrow`** file while the chain consumed the **non-`_uthrow`**
  one — the audit's "a digest binds identity, not selection" in its sharpest form. **PART 3:** the
  registry already states the criterion — nine fingerprint fields, *"reject on mismatch"* (`:17-22`).
  **Reported-bin dimension is uniform at 10694 and PASSES; the other eight are NOT payload-checkable**
  because `uq_cov_stat_5d.root` and `uq_cov_mlsplit_5d.root` carry **ONE histogram and no metadata at
  all**, and the central product's only scalars are `dataPOT`/`globalCompleteness`/`ndim`. A writer
  gap, not a verification gap. One measured disagreement routed: registry declares **est seed 42**,
  the throw payload records **`estimator_seed = 1000`**. **PART 4 — TWO PHENOMENA WRONGLY POOLED:**
  the central product's above-one readings are **1–49 ULP** (median excess `2.220e-16` = **1 ULP**,
  max `1.088e-14`) — **rounding, not a defect** — while the endpoint readings (`1.001824`,
  `1.000521`) are **eleven orders larger** and cannot be rounding. The endpoint disposition is
  **UNRESOLVED with its reason**: the ingredients are unwritten (`mii_anchor_comparator.py:125-128`,
  `NOT_RECOMPUTABLE, WRITER_GAP`), so no read settles it. ⚠ **And a larger finding falls out:**
  `of_in` and `denom_nd` agree to the last bit across the support, so **`completeness ≡ 1` and no
  completeness correction is applied in 5D** — disposition not issued. Nothing normalized into range,
  and the eight exactly-`1.0` endpoint readings are **not** cited as health, since `:1074-1076`'s
  closure branch writes that literal too.
- [`ASSESSMENT-20260918-cause3-joint-baseline-acceptance-packet.md`](ASSESSMENT-20260918-cause3-joint-baseline-acceptance-packet.md)
  - **The cause-3 joint-baseline acceptance packet (`937c3847`), per-item against its §7. Approves no
  boundary value, requests no member, grades nothing** — all four `Z_BOUNDARIES` keys stay WITHHELD
  (measured: that is the complete key set at `z_contract.py:213`). **`C1` is the one refutation and
  it fires the packet's OWN falsifier:** §4.1's requirement — an L3 statistic must be invariant under
  `C → D C D` — is **sound and endorsed**, but its proof is about `corr(C)` while its proposed
  statistic is `corr(M_p C M_p')`, and **source-basis rescaling does not pass through the
  projection.** Measured over 400 PSD draws with non-negative maps: `corr(C)` invariant at
  **`4.441e-16`**, `corr(M C M')` **NOT** invariant at **`5.390e-01`** — and a member differing from
  `k=0` by a **pure diagonal rescale** moves the statistic by `0.0117 / 0.0405 / 0.3986`. So the L3
  instrument is **breachable by diagonal movement alone**, the dual of the failure §4.1 exists to
  prevent. §6's second falsifier says such a statistic *"must be replaced"*. **The disjointness
  argument, the requirement itself, and the disqualification of trace and per-bin `σ` statistics are
  all untouched** (both confirmed to fail the test). **`C2`: §5.2's offset grid reproduces EXACTLY by
  CALLING `seed_offset_policy`** (blob `023ec710`) — `forbidden_differences([42,1000]) = [-958,958]`,
  `k=1..8` and `k=0..4` VALID, and all three collision tuples returned verbatim; endorsed in full.
  **`C3`: the `φ = 1` derivation is sound, map-set-agnostic, and under `P1`'s one-map finding its
  exclusion branch is EMPTY** — so the margin caveat it correctly carries has nothing to bite on
  today. **`C4`:** coherent movement is analytically exactly `(1+δ)²−1` at every `N` and weighting, so
  `δ_bin` is exact on that channel and vacuous on the cancelling one — which strengthens L3's primacy;
  **no contributor-count factor is attached to anything.** **`C5`: L4 endorsed on the merits** — no
  F7 key exists, confirmed — with an **operand correction** (`uq_math.py:160` takes `mean_shift_norm`,
  `sqrt_trace`, `n_throws`, so the criterion is stronger than its one-operand description) and one
  addition owed: as written it cannot distinguish *tested and stable* from *never came near the branch
  point*. **`C6`:** the three withheld reasons verified verbatim; abstaining from a fourth
  format-derived number is right. **`C7`: the seed disagreement routed at `e393ad5e` `R8` RESOLVES** —
  `sweep_bank_5d.py:354-357` documents 42-vs-1000 as **deliberate** and warns against unifying, so the
  registry's reject-on-mismatch rule is violated by a documented intent. A **record collision**, not a
  payload defect; it confirms §5's baselines from source, and any repair must be on the registry side
  — **the seeds must not be unified.**
- [`ASSESSMENT-20260918-L3-replacement-statistic.md`](ASSESSMENT-20260918-L3-replacement-statistic.md)
  - **The replacement L3 statistic (`3ebfd407` §10), supplied after I refuted its predecessor and
  declined to design a successor — so its author cannot assess it and I can. VERDICT: ENDORSE,
  conditional on three statements.** Adopts nothing, sets no `τ_p`, all four boundaries withheld.
  **`L1`:** invariance is exact **by construction** — `corr(DCD) = corr(C)` so `renorm` is invariant
  identically — and I ran their probe rather than taking it: repaired statistic invariant at
  `3.3e-16`–`4.4e-16` up to rescale sd **2.0**, still responsive at `0.0021/0.0108/0.0454`.
  **`L2` — their claim 1 is TRUE and it is a THEOREM, which is more than they claimed.** They invited
  me to break it. Instead I proved it: two source correlations differing by **0.562** driven to the
  **same** actual projected correlation to **9.322e-11** by choosing the source diagonal alone, at a
  modest rescale range `[0.187, 4.133]`, under a real marginalisation map. So any diagonal-invariant
  function of the actual projected correlation is **provably uninformative** — disjointness and
  actuality are **mutually exclusive** and the hybrid is **forced**, not chosen. **`L3`:** the
  reference is **verdict-changing** — 300 of 300 trials reference-dependent, worst ratio **1.973**
  (`0.0985` vs `0.1943` on one member set), asymmetric even in a pair. A statement requirement, not a
  defect: name the reference in the criterion and treat `τ_p` as reference-specific. **`L4` — their
  unchecked precondition, ANSWERED BY PAYLOAD: it HOLDS.** `diag(C_Z)` read from `z-cv.npz`: **0
  non-positive, 0 negative, 0 zero, all finite** over 10694, so `corr(C_Z)` is well defined. ⚠ But the
  same read gives a **`5.425e+25` dynamic range** (~12.5 orders in `σ`), so the statistic is dominated
  by high-`σ` bins and a PASS means *"no correlation change among the dominant bins"*. **`L5`:** keep
  **definedness** and **conditioning** apart — `λ_min < 0` does not threaten `corr`'s definedness,
  which `L4` settles independently. **`L6`:** their bounded-leak **conclusion** is endorsed
  (`≈4e-4` at `δ_bin ≈ 1e-3`) but the **`0.3× sd` constant is withdrawn** — their own per-sd column
  runs `0.351…0.127` and mine `0.234/0.202/0.569`, spanning `0.13`–`0.57`; this is their own §10.1
  lesson applied to their own new claim. **`L7`:** §10.2 strengthens my `C7` from *collision* to
  **unsatisfiable by construction** (the rule rejects `k = 0`, Z's own archive) and I adopt it.
  **One error of mine recorded rather than deleted:** my probe compared grid indices against row
  indices and printed a spurious set mismatch — the same index-basis confusion I flagged elsewhere a
  day earlier.
- [`READBACK-20260918-causes-5-and-7.md`](READBACK-20260918-causes-5-and-7.md)
  - **Causes 7 and 5 of the audit's seven-cause table. Issues NEITHER ruling** — not the `#16`
  publication-gate discharge (`X6`) nor cause 5's *"INAPPLICABLE, DISPOSED BY DECISION"* (`Y3`), both
  of which `SPEC` assigns to a decision. No compute; `C_Z − C_G` deliberately not computed.
  **`X1`: the decision rule is NOT a name list** — `unfold_nd:388` decides laterality by **branch
  presence** (`if t.GetBranch(l_sim) and t.GetBranch(l_mc): # lateral`), so the routed lead is
  testable against data, and the code runs that test itself. **`X2`:** the C++ producer states it —
  *"The GEANT hadronic-response bands … are **vertical/weight-only** and are captured by
  `w_reco_GEANT_*`"* (`:238-244`) — and `MinosEfficiency` is a `MINOSEfficiencyReweighter` (`:1749`).
  **`X3` PAYLOAD, MEASURED BY ME — the hypothesis SURVIVES:** on the 470-branch production universe
  tuple, all five carry weights `2/2`, kinematics `4/4` **and shifted q3+W `4/4`**; all four excluded
  carry `2/2` weights and **`0/4` kinematics**. `lateral set == p4_lib.BANDS` → **True**. **`X4`: I
  tried to break it on the 5D-specific `W` axis and it HELD** on four legs — the C++ note predates
  `W`, but `EXTRA_AXES["W"]` is `lateral_invariant=False`, the C++ writes `W_truth_/MC_W_/sim_W_`, the
  Python **raises** rather than falling back to CV (the `J33` repair), and the payload carries them.
  **`X5`: the ten endpoint identities VERIFIED** — ten directories, **12 ROOT files and 53.8 GB
  each**, uniform, matching `--array=0-119%12` and `N_ENDPOINTS = 10`; active and support blocks on
  identical `10694` footing. ⚠ **SCOPE CLARIFICATION:** the four are excluded from the **active lateral
  swap**, **not** from the covariance — measured present as `hCov_*` in **both** files. Migrations are
  source-declared: `p4_lib:64-65`, `2 + 3 = 5`. **`Y1`: `VL66`'s named falsifier is NEGATIVE on both
  modules it named** — `analyze_universes_5d.py` and `adopt_unified_5d.py`, zero pet imports, zero pet
  path literals, zero PET-word code lines. **`Y2`:** Z's whole 15-module closure and its 8 consumed
  input paths are clean; the only PET mentions are two **documentation cross-references**. ⚠ **A
  methodological note on my own search:** my first pattern included `frozen`, which matched
  **`frozenset` 76 times** and would have reported "77 PET hits" for a file whose true count is one
  docstring citation — an over-broad pattern manufactures a finding as readily as a narrow one misses
  it. **And the trace's boundary is stated:** it does not audit the full upstream producer chain of
  every consumed byte, so it is a **bounded negative**, which is what the falsifier asked for.
- [`READINESS-20260911-precursor-launch-six-dimensions.md`](READINESS-20260911-precursor-launch-six-dimensions.md)
  - **VERDICT: NOT READY.** Independent end-to-end launch-readiness check of the Z unified-throw
- [`ASSESSMENT-20260918-causes-1-2-4-acceptance-criteria.md`](ASSESSMENT-20260918-causes-1-2-4-acceptance-criteria.md)
  - **The causes 1/2/4 packet (`230aecf7`). SOURCE ONLY — no payload, no compute. Approves nothing;
  approval is Joseph's.** **The organizing "all three are tolerance-free" claim HOLDS for causes 1 and
  4 and its WORDING FAILS for cause 2 — whose conclusion survives on better ground than the packet
  gives it.** **`Z1`:** `SPEC` §6.2's own title is *"closure, irrespective of magnitude"*, so the
  ruling excludes magnitude and a tolerance would ADD a criterion — holds. **`Z2`:** `SPEC:1005-1019`'s
  four conditions are all binary — holds. **`Z3` — THE REFUTATION:** the packet says `k` is *"already
  fixed in code, **not chosen**"*; `uq_math.py:129-137` says the opposite in its own capitals —
  *"THE THRESHOLD BELOW IS A CODIFICATION, NOT A REPO DECISION"*, *"`2.0` is **chosen**"*, *"a
  codification with an owner and a date, not a fact recovered from the record."* **Fixed in code
  describes where it lives, not whether it is justified.** ⚠ But the conclusion survives on the ground
  the packet had available and did not use: `k`'s derivation is **statistical** — `1.0×` is at the
  sampling floor, *"consistent with being a finite-N fluctuation"* — which is categorically unlike
  `θ`'s defect of using a **resolution** as an **acceptance cap**, and the comment carries its own
  anti-tuning disclaimer. **`Z4` — the L4 composition has no overlap but the MARGIN falls between
  them:** at a ratio of `2.01` against `k = 2.0`, cause 2 returns True and L4 returns "identical" —
  **both PASS one perturbation from flipping**, and §2.2(c) makes the margin recoverable but nothing
  gates on it. **The same gap I recorded from the L4 side at `8df3b173` `C5`, found independently from
  cause 2's side.** **`Z5`:** cause 4's mutation is concrete in its TARGET and not in its
  DISCRIMINATOR — §3.3's refusal 3 is a **digest comparison on the stored object**, and a mutation
  routing `jit_trace` into that object trips it too, **possibly first**, so *"the guard fired"* would
  be unverified. The catalogued mutation-refused-before-reaching-the-guard shape, in a packet
  unusually exposed to it because it specifies both mechanisms. **`Z6`:** the guard-condition
  ambiguity is **not a packet defect but a `SPEC` SELF-CONTRADICTION** — `:1010-1011` says condition
  3, `:1237` says condition 4, both `SPEC`'s own text; *"near-identical in content"* is true of the
  content and not of the attribution, and an implementer cannot resolve a spec contradiction by
  picking. **`Z7`:** the packet still says *"twenty"* sources in two places against the corrected 24 —
  and the distinction matters, since the glob covered all 24, making it a **description** defect
  rather than a **coverage** one. The sweep is relayed in my record as in the packet's and is not
- [`RECHECK-20260918-null-per-bin-distribution.md`](RECHECK-20260918-null-per-bin-distribution.md)
  - **A bounded re-check of the NULL per-bin distribution, the load-bearing number behind the §6.4
  exception, requested after the cross-model lane that BLOCKED it ran out of credits mid-command.
  ALL EIGHT NUMBERS REPRODUCE** — digest, `10694` bins, mask equality, max `1.755272e-12`, 99.9th
  `1.318750e-12`, median `6.341524e-14`, zero above `1e-10`, smallest bin `1.009379e-50` moving
  `4.880054e-14`, and `r_null = 4.45200021375829101e-14`. Nothing unreachable. **Disclosure:** four
  were ones I measured at `0d7b366a`, so my re-measurement of those is independent of the
  implementing lane **but not of me**. **`N1` — one CHARACTERIZATION fails:** the smallest bin is at
  the **41.3rd percentile**, with 4419 bins strictly more stable — **not "among the most stable"**.
  **`N2` — the check nobody ran, and it answers the block properly:** instability **does** concentrate
  in small bins, `Spearman ρ = −0.3103`, `p = 2.5e-237`, monotone across all ten deciles, and the
  worst bin sits at the **5.4th percentile of bin size** — so the blocking lane's instinct was right.
  Which makes `N1` more than a wording nit: citing the single smallest bin draws a point from the
  **least-stable decile**. **The strong form the same data supports: the concern is closed by
  MAGNITUDE, not absence** — zero bins above `1e-11` against a feared `rel ≈ 4.4e+02`, fourteen
  orders. **`N3` — the comparator question: five significant figures is the BARRED route.**
  `SPEC:3909` — *"applying the printed median's precision to it is a new tolerance choice, not a
  consequence of that summary's formatting"* — with `:2131` recording the half-display-unit rule as
  factually wrong and `:2124` withdrawing what it produced; three withdrawn numbers trace to it.
  `δ = 5%` is un-derived, five-sig-figs is barred, and `SPEC:2187` gives an **exact test needing no
  tolerance** if display invariance is what is wanted. **Recommend reporting the distribution with NO
  comparator**, which the exception's own framing already supports.
- [`VERIFICATION-20260918-scalar5d-adopt-clause-c.md`](VERIFICATION-20260918-scalar5d-adopt-clause-c.md)
  - **A §6.4 clause-(c) independent verification requested ahead of a scalar-5D ADOPT, by a peer
  session advising the implementing lane. (1) COMPLETENESS: BLOCK. (2) LOAD-BEARING CLAIMS: PASS on
  everything reachable, with two wording defects and six claims not attempted.** Adopts nothing,
  grades nothing, authorizes no ADOPT. ⚠ **I was asked to "write no repository file" and declined** —
  `CLAUDE.md` makes a result live only once committed, and a gate-discharging verdict relayed
  unwritten by the advising lane is the same shape as the three *"record stating a stronger
  verification than was performed"* instances that lane itself reported today. **`V1` — CLOSED 2026-09-18, verified in an artifact:** `OPERATIVE-SHEET-scalar5d.md` on `origin/main` now defines `SRC_COV` at `:72` and enumerates the required chain at `:218`, so the set is establishable from an artifact and this ground is discharged; **BLOCK now stands on `V2` ALONE.** Originally: the required
  set as relayed names a **`SRC_COV` row that §2's table does not contain** — measured, exactly **one**
  `SRC_COV` occurrence in the whole packet, a shell variable at `:1002`. **`V2`:** §2's evidence for
  **C5 and C7 is MY OWN WORK** (`80b464ca`, ~14 h earlier), so clause (c) would be inert for those two
  rows if I signed them — the identical disqualification the requester correctly applied to itself;
  re-measuring a digest is fine, certifying my own verdicts is not. **`V3` — AMENDED after the requester answered it:** I **concede** it had **no exit** as a
  blocking criterion — a standard this lane applies to others — so it is reclassified from a ground
  to a **disclosure**, and BLOCK now stands on `V1`/`V2` alone. **Not conceded:** *"none is a finding
  that the covariance is wrong"* is inference from an absence the defects created, since the
  apparatus that would have shown one is what was broken. **The exit criterion it should have named,
  and it is satisfiable: every protection in the required path exercised with a positive control —
  coverage, not quiescence.** ⚠ Which exposes the residue: `V4` exercised **one tool**; the other
  five catalogued protections live in other code paths and **none has been exercise-tested by
  anyone.** **`V4` — THE GUARDS FIRE, EXERCISED NOT READ:** six refusals on the real path
  under the production env (`--expect-variant` required, variant mismatch, **AGENTS.md:29
  publication-from-mean**, `none`-on-marked, missing acceptance-question, **`adoptable: false`**) **and
  a POSITIVE CONTROL that PROCEEDED** (rc 0, wrote the product, `42 labels`). A hypothesised `none`
  bypass was **broken and held**. **`V5`:** sha256, seven keys, shapes, four byte-identical arrays,
  sqrt-traces `5.6742008e-38`/`5.2695064e-38`, ratio `1.076799`, `7.1322%` — all reproduce; but *"same
  dtypes"* is **false** (`metadata_json` `<U1934` vs `<U1936`) and *"differ only in hCov and
  hInflation_g"* is **false** (`metadata_json` differs, which is what makes the guard possible). Both
  immaterial, both corrected. **`V6`:** six claims named individually as not attempted. **`V7` — the
  finding nobody asked for:** `import ROOT` at `:245` runs **before** argparse at `:248`, so my first
  run returned `rc=1` on all eight cases **including the positive control**, and my second returned
  **segfaults** on all eight — twice, uniform failure looked exactly like uniform success, and only
  the control told them apart. **`V8`:** my own grep matched `RooUnfold**Error**s` — third over-broad
  pattern today. **`V9`:** on the pairing instrument, the **digest** is the load-bearing half and the
  `1.3e-15` agreement the corroborator, not the reverse; and a quantity zero **by construction**
  should be **absent** from a receipt's check list, not annotated.
  laundered by repetition.
  precursor on Joseph's six dimensions. **Authorizes no launch**; `R4` suspended, Gate 2 FAIL, nothing
  launched, cluster read-only. **CERTIFIED (1):** all four launchers exist with exactly the pinned
  specs — **70 CPU tasks, 0 GPU**, arrays read from the scripts never from a `sacct` bracket — with two
  corrections: the **dump arm runs a different producer** (`unified_throw.py --dump`), and of 24
  `sbatch_uthrow*` siblings the near-name `run_5d.sh` declares `0-19%10`/`12 h` against the fast arm's
  `0-39%40`/`6 h`, a budget fact (all siblings are cpu, so no resource-class flip). **BLOCK (4):**
  **(2)** `sbatch_uthrow_dump_5d.sh:12-14` hardcodes an absolute `REPO`, `cd`s there and runs a bare
  `python3`, so `sys.path[0]` is the pscratch tree regardless of `MNV_CODE_ROOT` — **the OI-136 shape
  (the 211-behind / 3 h 08 m A100 case) achieved by `cd` instead of a Python insert, hence invisible to
  the sweep that repaired the inserts** — and it is the only arm with `GUARD=0 mnv_inv=0
  mr_require_valid_offset=0`; it also has **0** `DATA_ROOT` references against 5/5/5, breaking the
  invariant `unified_throw_cov.py:63-68` relies on. **(3)** *No* namespace is fresh (`block_slabs_5d` 8,
  `block_slabs_5d_sb` **36**, `uthrow_slabs_5d_sb` 40, `uthrow_slabs_5d` 160, `bank_uthrow_5d` **374**,
  all July or earlier), and on the **undeclared** path the block leg writes `block_slabs_5d` (`:320`)
  while the combine reads `_sb` **unconditionally** (`:333`) — so the precursor's combine would consume
  **36 stale July products** and never see its own 21, and because the glob matches it **does not fail
  closed**; the launcher's own `:321-331` says members die loudly and *"an UNDECLARED run reads exactly
  what it read before"*, with canonicity **still open**. `mii/` is safe **only if**
  `MNV_EST_SEED_OFFSET` is unset — conditional, resting on the `mr_declared()` conflation, and should be
  a refusal. **(4)** `--expected-ids` occurs **zero** times in all four arms; only `--expected-throws
  0-159` is asserted, while `--block-slabs` is a **bare glob with no expected count**, so a short block
  arm combines silently. **(6)** RUNNING **is** charged — proven by fixture (3.0 h = 1.0 COMPLETED +
  2.0 RUNNING; PENDING skipped), refuting the feared mechanism — but the meter charges elapsed-so-far,
  so up to **240 CPU task-h** is committed-but-unmetered in flight (R5's own design), and **the cap
  arithmetic does not close: measured 58.84 + unmeasured `--time` ceilings 51 = 109.84 against a 100
  cap**, 48 h of it in the dump arm. **CANNOT CERTIFY (5):** there is **no separate receipt** to order —
  provenance is in-product `TParameter`s (`:550-579`) and `_atomic_savez`, and no `os._exit` exists, so
  the property holds **vacuously**, not by enforcement. **The OPEN item is CONFIRMED by an independent
  method:** 4 distinct blobs of `unified_throw_cov.py` across every ref, **zero** mask-write hits in all
  four, positive control **3** on `eavailW_covariance.py`; `:368-372` computes `rep = x_cv > 0` and
  discards it — and because support is **strictly positive**, a pinned-zero bin is excluded from `rep`,
  so Joseph's *"a pinned-zero bin is not a null operand"* **names this line**.
- [`ASSESSMENT-20260911-endpoint-B-design-nine-claims.md`](ASSESSMENT-20260911-endpoint-B-design-nine-claims.md)
  - **Pre-implementation assessment of `DESIGN-20260911-endpoint-B-generator-comparison-test.md`
  (`8a42f8ea`), designer recused; nine load-bearing claims.** Authorizes nothing; endpoint B stays
  **DEFERRED NOT PASSED**, Gate 2 FAIL, `cause3_corr` WITHHELD, `R4` suspended. **CONFIRMED (6):**
  the truth samples are all present on pscratch (the size mismatches are decimal MB vs MiB — GENIE
  `999.5`/`997.6` MB, 8 nuwro dirs, GiBUU 2020 MiB), so **no fresh generator production is needed**;
  the existing instrument is aimed at the **opposite end of the axis** (`eavail_generator_significance.py:2`
  *"high-E_avail excess"*, `:106` `>= 0.8` *"DIS tail"*, `:118` `chi2/ndf(DIS>=0.8)`) from the
  manuscript's claim (`sec_3d.tex:268` **low**-available-energy excess); the **model swap is real**,
  and the full-range column the requester had not verified **derives exactly** from `sec_3d.tex:194-197`
  (`12.01/18.18/24.03/27.92`); **nesting** holds and was already recorded (`README.md:201` *"mec==0 for
  all 1.48M CC events"*, exact `total CC=1484896`); the **target asymmetry** is documented
  (`run_nuwro.sh:32-34` `nucleus_p=6 nucleus_n=6` vs `README.md:32` CH `/13`) and per-nucleon division
  cannot absorb a component absent from one target; and **Tune v1 is the prior with no assembly term
  covering it** (`build_fps_prior_nuwro_5d.py:11` denominator; `z_assembly.py:4` five terms, zero
  prior/unfold matches) — a band reweights a fixed estimator, a prior change re-runs OmniFold.
  **THREE BLOCKS: (1)** *"what is missing is an ND histogrammer"* is overstated —
  `gen_to_xsec_eavailW.py` exists, takes an **arbitrary** `--gst` (`:67`) with a generator-agnostic
  reader (`:68`), and declares binning *"identical to the 5D OmniFold W axis"*, with NuWro/GiBUU
  siblings; the MEC sample is therefore already histogrammable and the gap must be **re-scoped**
  (limits stated: existence verified, execution and Tune v1 coverage **not**). **(2)** The four
  "implied catch fractions" `43.4/37.6/38.7/40.4` reproduce **exactly** from a single assumed **data**
  catch fraction `44.96%` — i.e. from the **withdrawn** 43–46% band itself — so they inherit the
  withdrawal, and even granted they show **no inconsistency**; §2's table does **not** depend on them
  and **stands**, so the flagged check on the producing scripts has no premise. **(3)** Multiplicity:
  `N=120` and `1.0870` reproduce, but **independence is not the worst case** — the union bound gives
  `0.986`, more conservative by `0.101σ`, so *"at worst 1.09"* is not a bound. Also **reclassified:**
  the *"one-sided"* label at `:111-113` is a **comment-only** defect — `isf(p/2)` is the conventional
  HEP equivalent, so the printed number is right and "fixing" it would break a correct value.
- [`CHECK-20260911-three-relayed-readings-gate2-mii-and-cost.md`](CHECK-20260911-three-relayed-readings-gate2-mii-and-cost.md)
  - **An independent check of three relayed readings plus one addendum, requested as preparation for a
  compute authorization. READY on reading 1; BLOCK on reading 2; BLOCK on two of reading 3's
  measurements with its conclusion surviving; READY on the addendum.** No compute launched; cluster
  read-only. **(1)** The Gate-2/adoption conditional is **not absent** — `REVIEW-CONTRACT-20260822:636`
  (§7.0.6) and `DECISION-20260824-f6b:65` both state it, but both bind *"the rehearsal's products"* and
  so do not reach Z; reporting unresolved scope is right, and the withdrawal must not be over-read,
  because §7.0.6's *"no further member is authorized"* is **not** product-scoped. **(2) BLOCK:** `R4`
  (`DECISION-20260902:109-116`) **suspends the cause-3 seed scan by name** and is omitted — its two
  prerequisites are measured unmet (the VOI note is committed only on `lane/cause3-voi-20260906`,
  unreachable from `main`; no `D-C3-RUN` exists), so the binding constraint is an **authorization**, not
  the M(ii) gate; and *"UNGRADED for `7ac0edec`"* is refuted by *"can never PASS"*
  (`DECISION-20260830-accept-forward-only:42`), by `RECORD-20260901:5`'s bar on *"a claim that Gate 2 can
  now pass"*, and by three post-08-30 decisions stating *"Gate 2 remains FAIL"* unscoped. **(3)**
  CONFIRMED: quarantine **517**; the live member is a different family (**143** markers,
  `57753239`…`57790088`, **0** shared job ids with the quarantined `57527866`…`57587242`); `boot 200`,
  `split 48`; `banksweep5d` is **CPU** (`--constraint=cpu`, n=**175**, **30.5675** task-h, **0** rows
  naming `gres/gpu`); both shared blocks byte-identical. **REFUTED:** `universe_sweep_bkgaware` is
  **188**, not `0` (nor the earlier `207`) — corroborated by `PROVENANCE-20260822:230`'s `n_universes`
  **188**; `universe_stage2_5d_bkgaware` is **4**, not `0`; both were `0` only in the **local** checkout.
  **Spend is on the wrong timezone basis:** `r5_meter.py:_sacct_argv()` emits a naive `--starttime` that
  `sacct` reads in the host TZ (PDT), starting the window 7 h late — `14.937222` (naive) vs
  **`15.423056`** (UTC), `+62` attempts, `+0.485833` task-h, isolated by bit-identical 3x replication per
  basis and strict-subset containment; operative headroom **CPU `≤ 484.58`**. CPU-binding **survives**. **The same boundary explains
  `FINDING-20260910`:** on the CLOSED window to the receipt's own instant, `TZ=local` reproduces
  `1826 / 14.489722` and `TZ=UTC` reproduces `1888 / 14.975556` — **both** historical figures,
  differing in nothing but the timezone, so that finding's attempt-identity diagnosis is **mistaken**
  and this lane's own retraction of that hypothesis is **WITHDRAWN** (§7 item 1 banner). Its four
  original controls all ran on **one side** of the boundary — a control over a population that cannot
  exhibit the defect, `BEN-032` inside a spend meter.
  **(4)** The addendum's diff and dates confirm, and **both** builders are implicated pre-`07c18aee`
  (`bootstrap_nd.py:28` `seed=a.seed`; `seedscan_split.py:54` `seed=args.split_seed`); job `55912230`
  did **not** write the blocks (it started ~19 h after their mtime) — the producer was an **interactive**
  job, and `PROVENANCE-20260822` pins no producing revision, so the caveat is **unresolvable in-tree**.
  **§7 records six method faults in this check, including a false mechanism withdrawn before it left the
  lane.** **Moves no gate, grades nothing, adopts nothing, authorizes no compute.**
- [`ASSESSMENT-20260911-scoped-letter-readiness.md`](ASSESSMENT-20260911-scoped-letter-readiness.md)
  - **VERDICT: READY as a manuscript, NOT READY for external review, on ONE evidence fault.** Measured at
  `origin/main = 6f24fb00`, note repo `d0c3768e`; **no compute launched**, builds local in a disposable
  worktree. **(1) `build_all.sh` PASSES**, exit `0` — note 90pp / primer 5pp / paper 3pp, **all three
  confirmed written by the run**, `SELF-TEST` and `RESULT` PASS, `FAIL` count 0, containment `note 10/10`
  vs `paper 0/10`; toolchain checked first, **no biber/PAR fault**. **(2) The scope claim HOLDS and is
  stronger than quoted** — `paper_body.tex:145-148` adds *"no superseded or historical covariance is
  used here"*; exhaustive counts give `p-value`/`chi^{2}`/`chiCombined`/`exclusion`/`Nsigma`/`gbdtFive`
  all **0**, and *"No significance is assigned"* appears **twice** in captions. **(3) No quarantined
  value reaches the Letter, and the 3D descriptors are absent from it entirely** — `main_paper.tex`
  inputs only `values` + `paper_body`, so `sec_3d.tex` is out of closure; the Letter's **8** value macros
  carry no quarantine marker, agreeing with the build's independent containment. **(4) The standalone
  note repo is IN SYNC** — 25/25 `.tex`/`.bib` byte-identical, 0 of 89 files absent, and the two heads
  are **seven seconds apart in one synchronisation operation**; ⚠ **a date-only read would have called it
  two weeks stale.**
  ⚠ **(5a) THE BLOCKER — Ruling 1's record is unreachable from `main`.** The Letter's defensibility rests
  on a deliberate exclusion whose authority is `DECISION-20260910-joseph-b-deferred-…`, committed only on
  an unmerged lane and therefore in **neither** repository a referee is given. Manuscript correct,
  authority unreachable — an **EVIDENCE** fault, closed by a merge this lane cannot authorize. **(5b)**
  *"the corrected contract"* at `sec_3d.tex:252` is a definite description a referee cannot resolve.
  **(5c)** 18 `\dead{}` struck values in the note: correctly contained and honest, but expect the
  question. **Method note: the first grep of the build log returned nothing for `PASS`, `FAIL` and
  `written by this run` alike** — *Non-ISO extended-ASCII*, so grep went binary-silent; the **positive
  control** caught it.
- [`RECORD-20260910-z-assessor-receipt-of-relayed-findings.md`](RECORD-20260910-z-assessor-receipt-of-relayed-findings.md)
  - **RECEIPT, not a transcription** — this lane's own testimony about what was relayed to it, at two
  hops, with **no fidelity claim** on any item. Companion to the decline record. **§4 is the point:
  the NEGATIVE SPACE made discoverable without anyone signing for words they cannot check** — clause
  (d)'s not-sufficiency and its **single unreplicated read** (a scope limit on a finding favourable to
  this lane, and those are lost first); `F3`'s `349 / 4 / 147` split; `A-7`'s `B = 7.107%` against a
  realized null median of `36.95%`; §4.4-vs-§4.4b's two incompatible boundary specifications; the
  sharing fraction **flipping the error's sign** (`5.17` → `1.78` → `0.81`); and **four candidates
  raised and killed**, one of which is an attack on this lane's own C6/C7 asymmetry that failed. Each
  row carries why this lane did not verify it. **None may be cited as this lane's finding.**
  ⚠ **§1 measures the attribution hazard instead of arguing it.** This lane wrongly said the current
  coordinator *"already commits"*, citing `a11d6cdd` — which was the PREVIOUS coordinator's. Measured
  against this lane's `a550796d`: **author, committer, `Co-Authored-By` and even `Checks: 12 passed`
  are IDENTICAL.** No git field distinguishes the two sessions, and the trailer names a **model**, not
  a session. So the error was structurally caused — and **had this lane proxy-committed the reviewer's
  findings, nothing in git would ever have separated them from its own.**
  **§3 accepts three corrections against this lane's own figures:** the read-only counterexample is
  **16 commits / 18 paths**, not 15/16 (stale by one commit — **more** favourable than claimed, and
  zero subject artifacts either way); **`AGENTS.md:120`** supplies the textual support this lane had
  not cited — *"never freeze an auditor's silent edit into a receipt"*, whose named harm an openly
  indexed review document is the opposite of; and `a11d6cdd`'s misattribution. **§5: this preserves
  that the items arrived, NOT the reasoning — option 2 to Joseph remains the fix.**
- [`DECISION-20260910-joseph-accepts-outcome-2-and-opens-replacement-packet.md`](DECISION-20260910-joseph-accepts-outcome-2-and-opens-replacement-packet.md)
  - **Joseph, 2026-09-10T16:04Z, discontinues the universal 5D bound and opens a replacement.**
  Accepts outcome (2) of the design/review loop: no further universal bound on projected objects
  absent a direct-check need. Authorizes **design and independent review only** of a replacement
  criteria proposal over a fixed, declared consumer set — not adoption, not an amendment by
  implication. Splits **endpoint A** (covariance/projected-uncertainty release; `cause3_corr`
  retained-with-criterion or explicitly replaced) from **endpoint B** (generator significances).
  Threshold `T` is not universal: name the exact claim it gates, and do not select it from observed
  results. Rejected approach preserved as history; its tooling not to be further extended. No
  compute, grading, gate movement, or publication change authorized.
- [`DECISION-20260910-joseph-b-deferred-and-finite-ensemble-disclosure.md`](DECISION-20260910-joseph-b-deferred-and-finite-ensemble-disclosure.md)
  - **Joseph, 2026-09-10T19:31Z, rules endpoint B deferred and orders three follow-on checks.**
  **Endpoint B is DEFERRED, NOT PASSED** — not to be marked MET, reopening it needs a separate
  proposal. Endpoint A gets a **disclosure-only** finite-ensemble requirement (verified ensemble
  size, normalization convention, inverted dimension or explicit not-applicable). Sets two
  adequacy tasks for `z-criteria-designer`: the exact contract amendment (if any) to defer
  `cause3_corr` from A without silently passing cause 3, and a criterion — distinct from A-4's
  subspace-stability bound — controlling the actual released error bars under estimator-baseline
  variation. **§0 records that this ruling and the one above were relayed correctly in chat but
  reached this file only after `z-independent-assessor`'s `FINDING F-0` measured that neither
  existed as a committed record across 131 refs** — this pair of files is that gap closed, not new
  scientific content.
- [`PROPOSAL-20260908-z-sensitivity-criteria-over-publication-projections.md`](PROPOSAL-20260908-z-sensitivity-criteria-over-publication-projections.md)
  - **⚠ SUPERSEDED 2026-09-10 IN ITS CANDIDATE-CRITERIA ROLE, RETAINED AS EVIDENCE.** Successor:
  `RECOMMENDATION-20260910-z-scientific-acceptance-criteria.md` §0.0, which states the delta item by
  item. **Its bytes are unchanged and an independent assessment against them stands.**
  **STILL CITABLE FOR** its §1/§1a/§1b consumer analysis and the intended-versus-validated-path
  distinction; §2a/§2c, that `s_agg`/`s_med`/`s_eig` cannot bound an inverse-quadratic consumer and
  that a spectral summary cannot determine the quadratic form; §4a, that printed precision
  establishes nothing scientific in either direction; §4c, the `pinv`-cutoff and retained-rank
  reporting requirement, which the successor carries forward; **and — ⚠ CORRECTED 2026-09-10 — its
  §6 *"which `M`?"* PREMISE, which STANDS.** An earlier revision of this entry listed that premise
  under `NO LONGER CITABLE FOR`; **that was wrong and it mismarked a live premise in the file agents
  route from.** The premise is that at least three projection-matrix implementations exist with none
  designated; the successor's `D.1(a)` measures **four** sites, so the premise is **wider** than when
  written, and the designation question is open (successor §7 item 7).
  **NO LONGER CITABLE FOR** its §3 candidate criteria **C-1**/**C-2**/**C-3** as the criteria; its
  closing *"No criteria owner exists"*, which `owners.tsv` refutes as of 2026-09-10; and **§6 item
  1's METHOD only** — an elementwise `M₁ − M₂` comparison, which is **undefined when one side
  refuses**, so a literal runner skips the refusing cases and reports agreement from a domain
  **selected for** agreement (`FINDING-20260910-projection-builders-agree-numerically-and-diverge-on-refusal.md`,
  amendment 2). The comparison's unit must be the builders' **outcome**. **Its "three
  implementations" is an UNDERCOUNT** — four production/consumer construction sites exist, the fourth
  on the PET diagnostic path, which any designation must exclude **by name**. It declares no
  threshold and adopts nothing; read its own `CITABLE FOR` header too.
- [`PACKET-20260910-z-consumer-set-and-endpoint-requirements.md`](PACKET-20260910-z-consumer-set-and-endpoint-requirements.md)
  - **DESIGN AND REVIEW ONLY — adopts nothing; Joseph retains approval.** Supersedes the universal-bound
  approach's ROLE, which he discontinued 2026-09-10. **§1 is the deliverable: Z's declared consumer
  set, enumerated for the first time**, with five additions to the starting list — including the **2D
  headline consumer**, which is LIVE and **already inverts by SVD pseudo-inverse (ratified,
  `app_statmethods.tex:53-58`)**, so endpoint B's inversion requirement is **conformance, not
  proposal**; a diagonal-only coverage consumer; and **three more deferred-declared sites, spanning
  note, paper AND primer** — the three builds intersect in `{values}` alone, so **one criterion cannot
  discharge them.** Splits into **endpoint A** (covariance/projected-uncertainty release; every
  consumer reads a diagonal, trace or band) and **endpoint B** (significances; every consumer inverts
  a full matrix), and keeps their requirements apart on that structural basis. **⚠ Its sharpest
  measurement: `np.linalg.solve` does NOT fail loudly on Z's covariance class** — two N-D comparators
  use it, and on a *near*-singular matrix it returns a silently absurd `chi2` (`1.0e18` where `pinv`
  gives `2.0`); a Z-shaped sum has **zero exact zeros and a mixed-sign round-off tail**, so a PSD test
  at exactly `0` fails on a correct object. **`T` is a proper subset of endpoint B and none of A**, and
  most claims need no threshold at all. ⚠ **NO LONGER CITABLE FOR: its `cause3_corr` answer.**
  Rev. 1 reported *"on the declared consumer set `cause3_corr`'s hazard is UNREALIZED — no released
  consumer reads off-diagonal structure — and it belongs to B, triggered by B-1."* **REFUTED BY
  MEASUREMENT the same day and withdrawn at the claim site:** `diag(M C Mᵀ)_i = m_iᵀ C m_i` reads the
  source's off-diagonals, so the hazard **IS realized inside endpoint A** via the projection —
  **C5, D1 and D2 realized, C6 conditional, C7 not** (one cell of five survives). Route to
  [`PACKET-20260910-z-endpoint-A-acceptance-and-cause3-corr-amendment.md`](PACKET-20260910-z-endpoint-A-acceptance-and-cause3-corr-amendment.md)
  for the current answer. Everything else in this packet stands. Stopping-rule outcome **(3)**: two named inputs required.
  Arithmetic re-runnable at
  [`state/probe-z-consumer-inversion-20260910.py`](state/probe-z-consumer-inversion-20260910.py) —
  deliberately a **separate** file, so the retired `rho` machinery stays frozen as history.
  **Its scope is enforced, not asserted:**
  [`state/check-consumer-set-20260910.py`](state/check-consumer-set-20260910.py) states the
  scope as a **population verified against an independent `git ls-files` count** (566 files) and
  fails closed on any covariance-touching file a deliverable cites without a pinned
  classification. **The packet's first version declared three globs covering 25% of the tracked
  population**; the instrument exists because that scope statement was not checkable.
- [`COSTMODEL-20260911-z-pilot-and-scan.md`](COSTMODEL-20260911-z-pilot-and-scan.md)
  - **INPUT to the adoption plan — prices nothing authorized and requests no compute.** ⚠ **Every
  figure is a `--time` REQUEST, not a measurement** — an upper bound from the launcher walls; the
  measured `ElapsedRaw` was deliberately not queried and is named as a separate cheap ask.
  **Two cost groups:** estimator-downstream **304 task-h per member in BOTH branches** (the
  universe sweep dominates it at 301.5), and the two dominant block terms **372 task-h**, paid
  **once under (b)** and **per member under (a)**. ⚠ **This CORRECTS the expectation that the
  (a)/(b) delta is the plan's largest number:** it is `372 × (|K|−1)` — 37% at `|K|=3` — and
  **never exceeds 2×**, because the sweep is paid either way. `|K|` is named as a SCIENTIFIC choice
  (precedent 3) and priced at 3/5/10. **The clause-(iii) scan is one decomposition of `C_0`, ≪1
  task-hour, and ⚠ the grid-resolution requirement costs NOTHING** — retained rank at any `rcond`
  is a count over the already-computed spectrum, so it is a reporting obligation, not compute.
  **Gap list CORRECTED rather than confirmed** (A-1 is fixed-by-spec and A-2 conformance, so "all
  proposed" overstates; P1–P4 are approved and what is open is the builder revision plus the
  arity/refusal code) with **five additions**, including A-5's undeclared `k` and the missing ND
  rank-truncation scan. **Pilot classified CONTINGENTLY: ESSENTIAL under (b), OPTIONAL under (a)**
  — since under (a) it holds fixed the very blocks the declared subject includes, so pass and fail
  lead to the same next action. **And a third state: today it can produce neither outcome**, since
  `κ = None` refuses even healthy baselines. **Hence the sequencing recommendation — the cause-3
  decision is free and prices the most expensive item.**
- [`PACKET-20260918-causes-1-2-4-acceptance-criteria.md`](PACKET-20260918-causes-1-2-4-acceptance-criteria.md)
  - **ACCEPTANCE CRITERIA for `(cause 1, Z)`, `(cause 2, Z)` and `(cause 4, Z)` — design only, no
  compute, authorized by Joseph 2026-09-18.** The owning lane prepares; `[cb0b6b]` evaluates. ⚠ **THE
  ORGANIZING RESULT: ALL THREE ARE TOLERANCE-FREE, so none can be blocked by the unestablished quantity
  that closed `θ` and blocks `cause3_agg`/`δ_bin` — all three are approvable in full TODAY**, form,
  population and value. Cause 1 closes *"irrespective of magnitude"* (§6.2, so a tolerance would ADD a
  criterion the ruling removed); cause 2's F7 branch is binary with `F7_FLOOR_MULTIPLE = 2.0` already
  fixed in code; cause 4's condition 3 requires the covariance content **not to change at all**.
  **Fourth instance of one structural pattern** after `B`'s boolean estimator and cause 3's L4: a
  discrete protected quantity leaves no knob, so Gap-3 tuning is impossible by construction. ⚠⚠ **THE
  CAUSE-2 CONTRADICTION IS NOT REAL, AND THE WORD DOING THE WORK IS "ALONE."** `AGENTS.md:29`'s
  *"mean-centering alone is disqualified"* is **the F7 branch OUTCOME**, not an independent ruling
  against a centering convention — `FINDING-20260901:16` reads *"at the floor, mean-centering alone is
  acceptable; well above it…"*, `:52` *"pairing disqualifies mean-centering alone"*. And
  `ESTIMATOR_REGISTRY.md:29` **satisfies it**, recording the CV-centered variant `6.2367e-38` beside the
  mean-centered `5.8077e-38`. **Both records hold simultaneously; resolving a non-existent contradiction
  would have produced a criterion protecting nothing.** So cause 2 is **not "which variant"** but
  **re-evaluate the branch on Z's own operands**, since Z inherits nothing from G — and it **composes
  with cause 3's L4**: cause 2 is the branch's VALUE, L4 its STABILITY across the member set. ⚠ **A
  "bound" is the WRONG INSTRUMENT for cause 4** — condition 3 requires no content change at all, so a
  bound would presuppose a permitted change and WEAKEN the spec; the criterion is four binary
  conditions plus **a guard that must be MUTATION-TESTED**, since the spec itself says a one-time
  comparison is insufficient and *"a quantity in scope is one edit from being subtracted."* Carries
  cause 3's three generalised principles without re-deriving them. **Two items ROUTED not decided:** a
  citation ambiguity over whether the guard enforces condition 3 (`SPEC:1010`) or condition 4
  (`:1237`), and `OI-186/188`'s population-identity requirement, relayed and unverified. **Nothing
  adopted; cause 3's three boundaries still WITHHELD.**
- [`PACKET-20260917-cause3-joint-baseline-acceptance.md`](PACKET-20260917-cause3-joint-baseline-acceptance.md)
  - **COMPLETES §3.7b's cause-3 joint-baseline acceptance design — a DESIGN deliverable with an
  approval recommendation, authorized by Joseph 2026-09-17. No compute, no member production, no
  grading.** Closes the audit's **rank 2** (`ebba67ab`), which said *"a member/design proposal exists,
  so the gap is not 'no design'"* — hence completed, not restarted. ⚠ **`θ` is used NOWHERE**, as input
  or fallback. ⚠ **`[B,S]` is PROPOSED not governing** (`SPEC:1552`, verified) so nothing is written as
  if it governs. ⚠ **Accepts Joseph's decline of `ε = 1e-9`** and records why the objection is sharper
  than the argument it refuted: **the transfer ACT was itself new**, so the number's age could not
  establish that its application to Z was fixed beforehand. **(a) THE SCIENTIFIC LOSS IS THREE
  DISJOINT LOSSES**, which is why there are three boundaries — and **L3 (correlations) cannot be
  reached by tightening L1/L2**, since both adopted statistics are functions of the diagonal alone.
  **Adds L4, the only DISCRETE loss:** the binary F7 centering decision, which no boundary covers.
  **(b)** `f_agg` trace-ratio form with the population declared as the `x_cv > 0` predicate, never a
  hardcoded 10,694. **(c) ⚠ THE COVERAGE FRACTION IS DERIVED, NOT CHOSEN** — `φ = 1` on the union of
  declared map supports (each such bin enters a published number) and unconstrained off it, so `φ`
  collapses into a **population declaration**. **(d) THE STRUCTURAL REQUIREMENT: a correlation
  criterion must be INVARIANT under `C → D C D`**, which the projected correlation matrix satisfies
  identically (measured `3.3e-16`) and which **disqualifies trace and per-bin `σ` statistics from ever
  serving as one**; `τ_p` may not be derived from any diagonal tolerance, because a non-negative-weight
  projection can near-cancel (`179.91` vs a `0.6900` limit, all PSD). **(d) L4 is APPROVABLE IN FULL —
  form, population AND value — because the quantity is discrete and the criterion has no tolerance
  parameter.** **(e) THE LEG SET BOUND AND VL141 SUPERSEDED IN TWO PLACES:** `sweep_bank_5d.py:358` now
  exposes `--estimator-seed` (no default, required for `--run`) and `:309-311` stamps it, and
  `analyze_universes_5d.py` now **refuses mixed-seed members** — so VL141's "no CLI flag" and "checked
  by nothing" are both repaired. **8 `sbatch_*` files name `MNV_EST_SEED_OFFSET`: 7 apply, 1 REFUSES.**
  The family is the **diagonal `(42+k, 1000+k)`, not a grid**, and ⚠ **the member set carries an
  ALIASING constraint measured by calling `seed_offset_policy`: forbidden differences `{-958, +958}`**,
  so the grid must pass `check_offset_grid` before any member is built. **`k = 0` is the archive** and
  costs nothing. **Explicit falsifiers for all four criteria.** ⚠ **Values for `cause3_agg` and
  `δ_bin` are NOT proposed** — blocked on the quantity Joseph closed, and the packet records that
  those two withdrawn numbers and `θ`'s withdrawn candidate all came from **one** half-display-unit
  rule. **Nothing adopted; three boundaries stay WITHHELD.**
- [`PROPOSAL-20260917-integrated-acceptance-existing-products.md`](PROPOSAL-20260917-integrated-acceptance-existing-products.md)
  - **ONE INTEGRATED ACCEPTANCE PROPOSAL for the EXISTING products and their supported reproduction
  path.** Assigned by Joseph 2026-09-17; the owning lane **prepares**, `[cb0b6b]` **evaluates**. ⚠
  **`θ = 7.11e-2` is CLOSED AS NOT ADOPTED and was NOT relabelled a feasibility floor** — the author's
  own fallback reading and the assessor's "declared as a FLOOR it needs no new argument" are **both
  declined**; only the narrow conclusion survives, that the derivation yields a **RESOLUTION, not a
  scientific cap**. ⚠ **Full `S` is OPEN.** **RECOMMENDS numerical agreement, NOT bitwise identity**,
  over a **within-run** envelope — because §6.4 already rules the bound scale-relative (so a bitwise
  criterion would itself violate reject condition 11), because bitwise **fails on 10,683 of 10,694
  bins** and is the gate-that-cannot-pass, and decisively because `r_null` is **already measured**, so
  **no `ε` chosen today can legitimately grade these products.** **Hence `ε = 1e-9` by TRANSFER** from
  `p4_lib.py:93` (Joseph, 2026-08-07, standard-P4) — the only value pre-dating the observation and
  declared for another subject; **margin `569.7×` per-bin and `2.2e4×` on `r_null`.** ⚠ **THE ROUTE
  NEEDS NO CONTRACT AMENDMENT** — it *satisfies* §6.4 clause by clause rather than replacing the null
  criterion, so the two amendments a `θ` route would need are removed by `θ`'s closure, not created.
  ⚠ **`B` is unestablished and NOT needed**, because `SPEC:1406-1409` separates **feasibility** from
  **justification** — the observed `1.755e-12` does the former, the transfer the latter. ⚠ **THE TWO
  QUESTIONS ARE DISJOINT:** `78a8c2ee`'s boolean `B = 0` **FAILS** on these products, so it is a
  property of the **pinned design only**, and a pinned run would **replace** these products rather
  than qualify them. **Minimum evidence is TWO READS, no compute:** independent reconstruction of
  `r_null` from the persisted operands (condition **11b**) and the precursor's date against
  `2026-08-07`. ⚠ **Corrects FIVE claims before building on them** — the assessment's four
  (√-scaling not halving, `N=397`; per-bin estimation errors correlated at `+0.815`; deadband
  crossings fix movement but not **membership**; downward `g` bounded **by construction** at
  `G_FLOOR = 1.0`) **and one of the lane's own**: §5.7's *"the same factor bounds every projection"* is
  **refuted** (`179.91` vs a `0.6900` limit, `260.7×`, all PSD) — and the diagnosis is that it holds
  with **exact equality for UNIFORM `G`**, which is why an adversarial search that scales `γ` uniformly
  passes on every counterexample. **`f_i` is explicitly NOT mandatory on every route**, and would not
  close `θ`'s scale anyway (that is set by `w_stat,i`/`w_ML,i`). **Separates the projection DEFINITION
  check (P1 — cheap, code-only, OWED) from the NUMERICAL one (P2 — matrix access, and its criterion
  needs the unmeasured anti-correlation condition).** **All product numbers RELAYED; no cluster
  access. Nothing adopted; no compute authorized, requested or run; products preserved.**
- [`RECOMMENDATION-20260916-theta-per-bin-uncertainty-tolerance.md`](RECOMMENDATION-20260916-theta-per-bin-uncertainty-tolerance.md)
  - **RECOMMENDATION on `θ`, a tolerance on the reported per-bin uncertainty's relative movement.**
  Routed by Joseph 2026-09-16 for `[cb0b6b]` assessment then his decision. ⚠ **`S` IS NOT CLOSED and
  this does not close it** — §6 explains why the author is structurally unable to: the arguments that
  would discharge `SPEC` §7 item 4 would be discharging the author's own recorded residue. ⚠
  **Authored by the owning lane, which therefore cannot assess it.** **THE ANSWER IS THAT `θ` CANNOT STAND ALONE — and after a peer's §5.7, the form is ONE
  TOLERANCE PLUS ONE MEASUREMENT rather than two tolerances** (§1.5; the correlation bound is
  **derived** via `γ ≤ θ/min_i f_i`, so no second scientific judgement is needed — but
  **sufficiency is CONDITIONAL on the measured `min_i f_i`**: usable at `≥0.5`, weak by `0.2`,
  vacuous by `0.01`, and the response to a small value is an **active-set restriction**, never a
  tightened `θ`). **The ground for the insufficiency is stronger than "necessary and not
  sufficient":** a diagonal rescaling preserves
  correlations **exactly** (MEASURED `3.3e-16` for the V-block alone), but `D_Z` multiplies `Σ_V`
  **only** (`z_assembly.py:4`), so `g` reweights V against four untouched terms and the **total**
  correlation moves (`5.9e-2` on the same fixture). The grip is exact — **`dσ_i/σ_i =
  f_i·(dg_i/g_i)`**, MEASURED to six figures — so `θ` permits `|dg/g| ≤ θ/f_i` and the off-diagonal
  V-part moves by `2θ/f_i`: **20× `θ` at `f=0.1`, 200× at `f=0.01`, and `f_i` is UNMEASURED.**
  Decisive for the *declared* use, because SPEC requires the 3D/4D covariances to be **exact
  projections** and a projection contracts the full matrix — sampling exactly where `θ` has least
  grip. **THREE ROUTES BARRED and named:** display precision (the `:2109`/`:3909` formatting borrow
  that produced `5.00e-41`), significance preservation (founds a determinism gate on **DEFERRED**
  endpoint B), and fitting to `4.452e-14` (`SPEC:1410`). **ADMISSIBLE ROUTE:** `σ` is not *known* to
  better than its own ensemble sampling error — `7.11%` at `C_stat`'s `N=100`, `14.74%` at `C_ML`'s
  `N=24`, both frozen and pre-dating Z. ⚠ **But `θ` IS NON-BINDING BY 12.2 ORDERS** (`1.60e12 ×` the
  observed null), so it is **`S`'s per-bin shadow** and inherits `S`'s vacuity: **declare it as a
  CEILING, never as the operative gate**, which stays `ε` argued from `B`'s side. Seven alternatives
  tabulated with consequences. **ONE MEASUREMENT settles both open ends** — the per-bin variance
  decomposition `f_i` — and whether the five per-term diagonals are even persisted is explicitly
  **NOT** established here. **Nothing adopted; no compute authorized, requested or run.**
- [`PREDECLARATION-20260916-B-estimator-and-coverage.md`](PREDECLARATION-20260916-B-estimator-and-coverage.md)
  - **PREDECLARATION of `Z_CONSTRUCTION_PLAN` §4.4a items 4 and 5 — zero compute, judgement, and
  they GATE the arm-7 evidence.** Owner `owners.tsv:14`; accountability for `B`'s justification
  assigned at `df0a8603` §2.3, verified in the record rather than accepted on relay. ⚠ **Authored by
  the owning lane, which therefore CANNOT assess it** — `owners.tsv:15` `[cb0b6b]`. ⚠ **The
  independence residual is on the document's face:** route (i) makes `B` a design property, which
  weakens the objection that `S` must be independent of `B`, but **item 4 is a judgement made while
  owning `S`** — reduced, not removed. **ITEM 4:** `B = 0` asserted as a property of the pinned
  design and verified by a **BOOLEAN** bitwise-identity test; `B` is **UNDEFINED** (never "the
  observed difference") if the test fails. Discharges Gap 3 **by construction** — the estimator's
  range is `{0, undefined}`, so there is no knob to tune. ⚠ **And a boolean is why route (i) is
  admissible where the withdrawn fallback was BARRED: it reads no VALUE off Z's null**, where the
  fallback read a magnitude; replacing the boolean with a tolerance re-enters `SPEC:1410`. Note
  `sbatch_uthrow_combine_5d_fast.sh:9` **already asserts** the null "must be zero". ⚠ `B = 0` gives
  `B ≤ S` trivially **and does not give `ε`** — `ε = 1e-9` still stands on §C.3's transfer argument
  alone, its own falsifier **UNEVALUATED**. **ITEM 5:** the objective is over **allocation shapes, not
  repeat count**, because the mechanism is deterministic-given-allocation; **Model A declared**,
  minimum **n = 3** (A1/A2 same node for item 1, B1 different node for item 2) at a **1.73 CPU
  task-h** reservation bound, 4 to attribute. Model B retained only as a falsification branch, priced:
  **6 runs to exclude a coin flip, 30 to exclude p ≥ 0.1** — which is Gap 2's "4 repeats had no
  justification" made quantitative. **Receipt requirement:** ≥2 distinct node names or item 2 is
  **NOT TESTED and the run INCONCLUSIVE**, and an unprovided microarchitecture arm is **UNEVALUATED**,
  never folded into a pass. ⚠ **A MEASURED OBSTACLE NO DOCUMENT NAMED: the pin set is incomplete** —
  `OMP_DYNAMIC`/`OMP_SCHEDULE`/`OMP_PROC_BIND`/`OMP_PLACES` have **zero occurrences** in
  `nd-unfolding/`, including in the arm treated as the pinned reference, so "route (i) is falsified"
  would be ambiguous between *cannot be pinned* and *was never fully pinned*. **Nothing adopted, no
  compute authorized or requested, nothing run.**
- [`DESIGN-20260911-endpoint-B-generator-comparison-test.md`](DESIGN-20260911-endpoint-B-generator-comparison-test.md)
  - **PROPOSED DESIGN for endpoint B's generator-significance test — nothing adopted, run or
  authorized; endpoint B remains DEFERRED NOT PASSED and Gate 2 remains FAIL.** ⚠ **Authored by the
  `z-criteria-owner` lane, which therefore CANNOT assess it** — route to the independent assessor
  BEFORE any part is implemented. ⚠ **CORRECTS the brief's premise: no fresh generator production
  is needed** — all four candidates' truth event samples survive on pscratch (plus GENIE+MEC); what
  is missing is an ND histogrammer. ⚠ **The existing instrument tests the OPPOSITE end of the axis**
  — `eavail_generator_significance.py` is by its own docstring the *high*-`E_avail` DIS-tail corner,
  while the manuscript's claim is *low*-`E_avail`. ⚠ **The catch bin is NOT inert: including or
  excluding it SWAPS which of the two best models is closest** (Tune v1 full-range, GENIE CV
  catch-dropped), derived from the note's own published numbers and checked against its own stated
  12–28%. **Three independent constraints all cap the test's dimension** — rank (a proven bound: 42
  two-point bands give rank 1 each, so 141 is explained by construction), generator MC statistics
  (8.5% per bin at full grid, comparable to the smallest deficit), and **the uthrow inflation, which
  is the strongest: a nominal 3σ survives as 1.75σ at `ndf=6` but only 0.73σ at `ndf=36`.** Hence a
  **1-dof primary test**: the nested 2p2h-strength fit on the GENIE CV / GENIE+MEC pair, the only
  nested and target-matched pair. **Normalization treated as three options with standalone
  verdicts** (absolute REJECTED as primary for lack of discrimination; area-normalized ACCEPTED;
  profiled ACCEPTED only with a derived penalty width — `__Normalization_flat`'s σ=0.014 cannot
  serve). ⚠ **Tune v1 IS the unfolding prior and no assembly term covers the pull toward it**; the
  prior-dependence measurement costs **0.9–1.4% of the endpoint-A pilot**. **Multiplicity priced:**
  the design's own axes span 120 candidate significances, so the pre-declared primary set must be
  ≤4. ⚠ **One of its own arguments was WITHDRAWN during review and the withdrawal recorded in
  place** — an absence claim over 22 of 45 band names, void rather than weak because `R = 27` is
  derived and never listed.
- [`AMENDMENT-20260911-cause3-conditional-scope-and-kappa.md`](AMENDMENT-20260911-cause3-conditional-scope-and-kappa.md)
  - **PROPOSED amendment — adopts nothing; cause 3 remains NON-PASSING and all three cause-3
  boundaries remain WITHHELD.** Part A answers the standing `z_contract.py:231-235` objection, and
  the answer is that **cause 3 as written does not distinguish two readings**: *(a)* how much `C_Z`
  moves when the estimator baseline changes **as production changes it** (which regenerates the
  blocks), versus *(b)* how much is **attributable to the estimator-baseline choice**.
  `:222-225`'s *"estimator-baseline sensitivity"* is **unqualified** and omits what is held fixed.
  ⚠ **The ambiguity was invisible until the decoupling**, because with one switch the two were not
  distinguishable configurations. Recommends amending the reasons to state what is held fixed,
  adding a **licensing clause in `cause3_corr`'s own existing template**, and recording (b) as
  discharged / **(a) as explicitly UNDISCHARGED** — and names the remaining scientific choice for
  Joseph with both branches priced, (a) requiring **per-member regeneration of 100 + 24 replicas**.
  Part B is `κ`'s package: the **Rayleigh** formula, `κ = 1e-12`, and a numerical justification that
  is **not** scale invariance — the measured accumulation floor is `~2e-15` (pairwise), **three
  orders tighter than the `n·eps` worst case**, and `rank(C_Z) ≤ 265 of 10,694` means there is no
  continuum between round-off and support, so the verdict is identical across **`1e-14`–`1e-3`**.
  ⚠ **The acceptance population never shrinks:** a degenerate functional **refuses the whole
  evaluation** rather than being dropped from the max over `U`, so `s_proj` is never reported over a
  reduced set. Assessment scope is stated, not inferred.
- [`DECISION-INPUT-20260911-named-projections-and-the-tolerance-choice.md`](DECISION-INPUT-20260911-named-projections-and-the-tolerance-choice.md)
  - **DECISION INPUT ONLY — adopts nothing; Joseph's items 1 and 3.** ⚠ **`δ_proj`'s DERIVATION IS
  WITHDRAWN IN FULL** on his objection: measured, the threshold moves **`102.6×`** on ONE covariance
  with the total preserved and only the component **grouping** varying, and the dependence is
  entirely on the granularity of the **tail**. **The "grouping is physically meaningful" defence
  fails on this repo's own evidence** — the same `C_syst` is declared at **13** (`VERT_BANDS`) and
  **45** (`analyze_universes` census) components, `0.985%` vs `0.280%`. **His sentence licenses
  ATTRIBUTION to the declared set; it does not make the declaration's GRANULARITY an accuracy
  requirement** — that step was the lane's, not his. **The remaining requirement is presented as an
  explicit CHOICE**, with the one hard constraint the invariance test yields: **a yardstick must be
  a NAMED object, not a SELECTOR over the grouping.** Recommends **(A) the statistical block
  `C_stat`'s contribution**, with its weaknesses priced (it is provisional and reused under item 2,
  and it is a judgement rather than a consequence). **Item 1 proposes FOUR named projections** —
  `(E_avail,W)`, `E_avail`, `p_T`, `p_∥` — derived from **what the deliverables display**, not from
  what would pass, with **five exclusions by name**. ⚠ **Its revision column is empty ON PURPOSE:
  no released projection names its builder and commit** (the assessor's pre-registered F2), and
  **P4's builder could not be determined at all** — which is live, not formal, because
  `FINDING-20260910-projection-builders-…` on main records four non-equivalent builders that
  **diverge on refusal**.
- [`PACKET-20260910-z-endpoint-A-acceptance-and-cause3-corr-amendment.md`](PACKET-20260910-z-endpoint-A-acceptance-and-cause3-corr-amendment.md)
  - **DESIGN AND REVIEW ONLY — adopts nothing, declares no boundary, grades nothing; Joseph retains
  approval. Gate 2 remains FAIL, `cause3_corr` remains WITHHELD, cause 3 remains non-passing.**
  Answers three tasks set after Joseph's rulings of 2026-09-10 (publication scope: **endpoint B
  DEFERRED, NOT PASSED**; finite-ensemble **disclosure only**). **⚠ It opens by WITHDRAWING its
  predecessor's `cause3_corr` answer** — `diag(M C Mᵀ)_i = m_iᵀ C m_i`, so the off-diagonal hazard
  **is realized inside endpoint A** through the projection, and the "A reads only the diagonal"
  premise was true of the *projected* object, not of the *operand*. Corrected **per consumer**: C5,
  D1, D2 realized; C6 conditional; **C7 not** — one cell of five survives.
  **Its two sharpest mechanical findings:**
  **(1) `nd-unfolding/z_contract.py:231-236` is INERT to cause 3's verdict** — deleting the
  `cause3_corr` entry outright leaves `assess()`'s outcome **byte-identical**, because `assess`
  reaches a boundary only through `leg.boundary_key` and **no production leg names it** (every
  `LegSet(...)` in the tree is in `tests/`). Cause 3 reaches **MET with `cause3_corr` still
  withheld**, so scoping it out is *not* what would make cause 3 passable. **The binding site is
  `z_validator.py:168-172`, `_DIAGONAL_ONLY_SCOPE`**, whose emitted text excludes
  *"marginalization, projection, coverage validation"* **by name** — so a MET under the current leg
  set disclaims exactly what endpoint A releases. **The requested deferral is therefore UNSOUND**:
  it would need that sentence narrowed, which changes what a MET *licenses*. The one sound form —
  narrowing endpoint A to release no projected uncertainty — is stated and **not** recommended.
  **(2) A-4 IS SILENT ON THE RELEASED ERROR BARS, NOT MERELY WEAK.** With `C_k = (1+a)C_0` the
  retained subspace and rank are invariant, so `‖P_0 − P_k‖_2` sits at **round-off (`~3e-15`, exactly
  `0` at `a=1`) — seven orders inside its `1e-8`** — while the released bars move **41.4%**. So no
  criterion in A-1…A-5 bounds them. **The instrument that does already exists and is CALLED, not
  retyped:** `z_statistics.s_proj` (SPEC §3.7d's first candidate), whose internal
  `einsum("ij,jk,ik->i", U, C, U)` **equals** `diag(U C Uᵀ)` — so with `U` = the rows of `M` it does
  not approximate the release, **it evaluates it**. Rank-deficiency is irrelevant to it (no inverse,
  no PD baseline), which is why it survives where the retired `rho` bound did not. **`s_corr` and
  `s_eig` are rejected with reasons.** **⚠ The BOUNDARY is NOT proposed** — §4.4 measures why: δ needs
  a declared publication uncertainty and `sec_3d.tex:251-252` says the 3D descriptors *"are audit
  descriptors, not publication uncertainties"*, while `paper_body.tex:145-146` says every non-2D
  result is a central value. **A format-derived number is refused on precedent in both directions**
  (`REPRO_RTOL = 5e-4` legitimate for *reproduction*; `cause3_agg`'s withdrawn `0.0861%` illegitimate
  for *acceptance*). Recommends adopting `s_proj` as a **reported statistic** now, boundary withheld
  with a named trigger. **Ruling 2 is placed on A, not B**, on a closed two-block population derived
  from `z_assembly.py:4` — and **⚠ neither block records its own `N`**: both `--array=` headers are
  *declared* arrays, the verified count comes from `load_replica_manifest:44-48` failing closed, and
  both producers `print` it and persist only a `TH2D`. **`C11`'s 2D `ndf` non-conformance is
  explicitly OUT OF SCOPE under Ruling 1, in its own row** — and out of scope is not conformance.
  Arithmetic re-runnable at
  [`state/probe-z-projected-stability-20260910.py`](state/probe-z-projected-stability-20260910.py)
  — a **new** file; the frozen `rho` probe is untouched and the universal bound is not reopened.
- [`RECOMMENDATION-20260910-z-scientific-acceptance-criteria.md`](RECOMMENDATION-20260910-z-scientific-acceptance-criteria.md)
  - **RECOMMENDATION ONLY — adopts nothing, grades nothing, authorizes no compute; Joseph retains
  scientific approval.** The `z-criteria-designer` owner's answer to `Z_DECISION_PACKET` §5 items 1,
  5, 7 and 8, in four parts: **covariance construction** (two proposed tolerances — the `g^c`
  reconstruction gate at exact-or-`1e-12`, arguing that the standard-P4 `1e-9` closure tolerance is
  six orders too loose for a six-operation expression; and a second per-element leg on the inflation
  closure identity, because a Frobenius residual is an aggregate); **estimator-baseline sensitivity**
  (a recommendation **on `SPEC` §3.7d's reserved disposition** — "add a leg": two binding
  correlation-sensitive legs, `s_agg`/`s_med` demoted to diagnostics with an exact
  rounding-equality display test replacing the two withdrawn format-derived boundaries);
  **numerical reproducibility** (`epsilon = 1e-9` **proposed** for `r_null`, derived by a proven
  inequality from `p4_lib.REPRO_RTOL_PER_BIN`, with `S` discharged by bounding via the F7 decision
  margin and `epsilon` argued from `B`'s side because an `epsilon` near `S` would be a gate nothing
  can violate); and **generator significances** (a **sharp, proven** two-sided bound on the consumed
  quadratic form, **non-increasing under projection**, making the criterion closed-form in the
  decision threshold rather than blocked on it). ⚠ **ROUND 2 (2026-09-10) REJECTED THE UNIVERSAL 5D BOUND AS THE ACCEPTANCE INSTRUMENT** — stopping-rule outcome **(2)**, *narrower claim recommended*, which Joseph named as a legitimate result. `rho` needs a positive-definite baseline and **Z's own operands give `rank(C_Z) <= 265` of `10,694`** (Part 6 F1, derived — **rank `263` is S's, not Z's**). §2.1/§2.1b/§2.2 **remain theorems and stay adoptable as stated**; what is withdrawn is their ROLE, plus rev. 1's **`M`-independence** claim (F2: monotonicity needs `range(C_k−C_0) ⊆ range(C_0)`, unmeasured and probably false). **The recommended rule is now DIRECT CHECKS ON THE DECLARED PUBLICATION CONSUMERS** — `s_sig` over declared `(generator, projection)` pairs plus the four inversion declarations `app_statmethods.tex:645-658` already mandates — which also **reinstates `PROPOSAL-20260908`'s C-1 statistic**, superseded in rev. 1 on an asymmetric ground. **All four withheld boundaries carry an explicit recommendation.** `cause3_corr` is answered in **Part 6** as **BRANCH A**: a second binding leg that is the
  **inversion-declaration stability** of each declared projected object across members — retained
  rank, applied `rcond`, condition number, retained-subspace gap. **It carries EXACTLY ONE
  tolerance** — `‖P_0−P_k‖_2 <= 1e-8`, adversarially attacked over ~46,000 trials and survived —
  while rank equality needs none and the applied `rcond` and condition number are **reported,
  not gated** (an equality gate on the cutoff *cannot fail*, since it is a function of shape and
  `eps`; the condition number is continuous and no tolerance for it is justifiable). ⚠ **An
  earlier revision of this entry said "it needs no tolerance"; that was FALSE and is corrected.**
  The leg is justified by `app_statmethods.tex:645-658` clauses (i)/(ii)/(iv) rather than by this
  lane's judgement. ⚠ **Rev.
  1 recommended Branch B on the ground that domination implies non-bindingness; that hinge is VOID
  (F9 — the implication needs `rho_crit <= τ`, a relation between THRESHOLDS) and Branch B is
  WITHDRAWN.** §2.1b's domination theorem itself stands. **`cause3_corr` remains WITHHELD and `(cause 3, Z)`
  remains non-passing** — Joseph decides any amendment after independent review. Its arithmetic is
  re-runnable at
  [`state/probe-z-criteria-acceptance-mathematics-20260910.py`](state/probe-z-criteria-acceptance-mathematics-20260910.py).
  Read its `CITABLE FOR` / `NOT CITABLE FOR` header first: no adopted boundary, and every `chi2`/`ndf`
  in it is a synthetic placeholder because **no MINERvA significance exists in this tree**.
- [`SPEC-20260906-complete-scalar5d-successor-Z.md`](SPEC-20260906-complete-scalar5d-successor-Z.md)
  - **rev. 21. SPECIFICATION ONLY; constructs, runs, grades and adopts nothing.** The five deliverables
  `RZ(v)` authorizes, for one named Z: the **scientific contract** (§1 — artifact identities bound by
  path plus digest; the imported constants, now including `adopt_unified_5d.VERT_BANDS` and
  `uq_math.F7_FLOOR_MULTIPLE`; **§1.3a's explicit inflation algebra** `C_Z = D_Z(Σ_V C_b)D_Z + Σ_R + Σ_A
  + C_stat + C_ML` with `D_Z`'s operands, zero-denominator handling and both centering variants; §1.3b's
  identity set, **four of whose gates do not exist**; the receipt schema; and what does not exist yet),
  the **seven cause dispositions** (§2, none inherited), **terminal criteria** (§3, per-cell completion
  *and* failure, fifteen reject-Z conditions, a bidirectional test contract), the **dependency analysis**
  (§4, twenty-two candidates each answered separately for `necessary` / `applicable` / `reusable-now`,
  with `D-Y-CONSTRUCT` and `D-C3-VOI`+`D-C3-RUN` flagged and **neither found to be a Z prerequisite**),
  and a **costed execution proposal** (§5 — `73.0` GPU / `≤118.0` CPU task-hours for one build against
  `R5`'s `500`/`500`, from the ratified `70`/`113` seven-arm anchor, with the meter gap named).
  **§6 carries FOUR RULINGS Joseph took on 2026-09-06** on an independent contract review's
  recommendations: `(cause 5, Z)` may be terminally disposed **`INAPPLICABLE — disposed by decision`**
  after the complete trace and falsifier check, **adding no token** and on cause 2's by-decision
  precedent (§6.1); `(cause 1, Z)` closes on **measure-and-disclose irrespective of magnitude**, once
  independently verified, **without inventing ± endpoints for the non-pair bands** (§6.2); `(cause 3, Z)`'s
  `M(ii)` is the **joint-baseline** quantity with the narrow fixed-draw scan **diagnostic unless
  substitution is separately ruled**, the 46/50-member family **not assumed**, and three outcome classes
  predeclared (§6.3); and Z uses a **scale-relative fixed-seed null bound fixed before production**
  (§6.4). §6.5 withdraws rev. 1's multi-draw cause-4 proposal. **`CRITERIA` §0's vocabulary is NOT
  extended** — `DECISION-20260902-joseph-rules-no-fourth-grade-token.md` stands, and rev. 1's contrary
  proposal is recorded as a miss. **Corrections carried in place:** S's `publication_gate_rejects_this`
  is **`false`** with an 11-gate PASS, so the *"adopter refuses it outright"* ground is stale — the
  durable ground is that S is a block-sum object with **no unified-throw inflation** and **cannot donate
  `D_Z`** (§1.4); `SCOREBOARD` §2b's *"`M(ii)` cannot be configured"* is superseded by `3dd5e66e` (§2.3);
  and, **withdrawn from rev. 1**, the bidirectional projection guard is **not missing** — both projectors
  guard both directions and differ **deliberately** in fail-closed-ness (§2.6a), reuse of
  `C_stat`/`C_ML` is **not** evidence of incompleteness (§2.6b), and the replay-doubling and *"≈4.5×"*
  cost claims are withdrawn (§5.3, §5.4). Opens no `SCOREBOARD` cell, moves no count, preserves `R5`
  exactly, does not widen Y, does not promote S. `BEN-381` disqualifies the drafting lane from grading
  the legs it defines, and from grading under the four rulings — **but not from designing what it
  specifies**, a rev. 2 over-application withdrawn in rev. 3.
  **REVIEW ROUND 2 (rev. 3) closed one hole rev. 2 itself opened and corrected one of its own
  corrections.** §1.3b's four inflation gates were **jointly satisfiable by an uninflated object** —
  `g ≡ 1` passes the closure identity, `g ≥ 1`, the zero-denominator rule and PSD — so a **fifth gate**
  requires the validator to **independently reconstruct `g^c` from `diag(C_unified)`,
  `diag(C_blocksum)` and `hJointMeanShift`, per variant**, with the matching `T`-leg mutation. New
  **§3.6** converts the two ruled-but-incomplete terminal criteria into completion schemas: the null's
  normalizer, units, `ε` derivation and presence rule; and cause 3's member definition, statistic,
  two-leg normalization, the `S/U ≤ sqrt(2δ+δ²)` boundary derivation applied to **Z's own** printed
  precision, and the three classes mapped onto the six branches — **reopening no ruling**. And **`R5`
  meters `ElapsedRaw`, actual elapsed, not requested walltime**, so rev. 2's *"the metered cost is the
  wall request"* is false: §5.2 now separates **expected spend** (`55.70` GPU / `86.53` CPU) from a
  **reservation bound** (`73.0` / `≤118.0`), and both are labelled a **PRICED SUBTOTAL** with four
  required rows unpriced. Also narrowed: the J28 line to **the two assemblies only** (its rescale is
  J28-only, its throw combine **is arm 7**); the cause-4 jitter counterfactual to a **second** unfold at
  `seed + 7`, distinct from `--null`'s same-seed one; `54.90`/`86.53` to a **historical prior that
  understates a Z member**; and S to holding the **uninflated** vertical components while lacking `D_Z`
  and the inflated term.
  **REVIEW ROUND 3 (rev. 4) fixes the acceptance mathematics and the test contract.** New **§3.6d**:
  the predeclared `S/U ≤ sqrt(2δ+δ²)` threshold **does not transfer** to either new criterion, because it
  assumes an **omitted independent contribution added in quadrature** and neither a difference of two CV
  vectors nor variation among assembled covariances satisfies that model; `δ` transfers, the quadrature
  map does not, and for a **directly measured change in `U`** the comparison is `|U'−U|/U ≤ δ`. The
  ordering rule is inverted back: **statistic first, boundary second**. A hardware reproducibility floor
  is demoted to a feasibility constraint — it measures **achievable** repeatability, not **acceptable**
  error. §3.6b's free choice between assembled-covariance and cross-section-vector spread is **withdrawn**:
  §6.3 fixed the assembled covariance as the subject, and vector spread is the **substitution** it
  reserved. §3.6c's *"proposes no criterion change"* is **too categorical and withdrawn** — a boundary
  form differing from the predeclared rule is itself a carve-out question, now listed in **§6.6**. In the
  test contract, the `g ≡ 1` and **dropped-shift** mutations are **separated**: a reuse-faulty validator
  **rejects `g ≡ 1` on both variants**, so a distinct `g^cv ← g^mean` mutation is required on operands
  where the two must differ (`v_blk=1`, `v_uni=4`, `mean_shift=1` → `g^mean=2`, `g^cv=√5`), and the
  `g ≡ 1` fixture must make `g ≡ 1` **wrong**, since it is legitimate wherever `v_uni ≤ v_blk`. Cost
  language stops asserting bounds: historical figures are **priors from a different subject**, not lower
  bounds; a time limit **bounds an attempt, not a completion**, so the combine and assembly reservations
  are **PROPOSED, UNVERIFIED**; and the omitted rows are enumerated **per subtotal** — five for the spend
  estimate, three for the proposed reservation, two campaign-level items in neither.
  **REVIEW ROUND 4 (rev. 5) found no new assembly-algebra defect and closed two residual defects, both
  the drafting lane's.** Three **withdrawn cost claims had survived in operative text** and are removed:
  the assembly row's *"`< 4.0` is all it licenses"* (a request that was never exceeded measures nothing,
  and it covered four operations of which only two are Z's), §5.4's *"a Z member costs more"* and the
  prior *"understates"* it (a prior measured on a **different subject** supports **no direction**), and
  §7's *"the subtotal is a floor"* with its stale four-row count. And **§3.6d overstated the narrow
  scan**: it called `C_seed` an independent variance contribution *"being added to the budget"*, which
  **`PREDECLARE-20260901-cause3-mii` §5 expressly forbids** — *"It does not add `C_seed` to the
  uncertainty budget"* — and which contradicted this document's own §1.3a. Quadrature is now stated as
  the **conditional model that motivated** those thresholds, **never demonstrated even where it was
  used**. Two recommendations adopted: **direct relative change `|U'−U|/U ≤ δ` is the DEFAULT** for
  §6.3's assembled-covariance subject, with the burden of demonstration on any proposal to use
  quadrature; and §6.6's boundary-form item now records **how the decision must be put** — the statistic,
  denominator, precision target and boundary approved **together**, never a formula detached from them,
  so **that item is not ready to decide today**.
  **SPECIFICATION COMPLETION (rev. 7) — no review finding; the three declared gaps are closed and
  everything new is PROPOSED.** New **§3.7** completes both terminal criteria. For the **fixed-seed
  null**: the normalizer is `‖x_cv2 − x_cv‖ / ‖x_cv‖`, with `sqrt(Tr C_Z)` rejected (it divides a
  central-value difference by an uncertainty scale, and it is the denominator behind the campaign's
  quoted `1.31e-12`) and the per-bin maximum rejected as a gate but retained as a diagnostic;
  `ε = n_iters · n_rep · float64.eps = 1.1873e-11`, a **formula with imported operands** rather than a
  constant, binding over three sensitivity channels by seven orders in the one unmeasured quantity; and
  a new reject condition **`11b`**, because the throw writer **does not persist `x_cv`** so the ratio
  is otherwise unauditable — `hXSecND_flat` in the production ROOT closes it. For **`(cause 3, Z)`**:
  the member is **MEASURED, not designed** — one shared `MNV_EST_SEED_OFFSET` across exactly **seven**
  production launchers, with an **eighth that refuses it**, so no arm can be reused and the implemented
  family is the **diagonal** `(42+k, 1000+k)` rather than a grid; the population is the **finite declared
  offset set**, which makes a sample SD inadmissible and the **maximum** the matching statistic; and the
  boundaries are `s_agg ≤ δ_agg` and `s_med ≤ δ_med`. **Under the direct model those are `0.0861%` and
  `0.0374%` — `48×` and `73×` tighter than the narrow scan's `4.15%`/`2.74%`**, which is arithmetic, not
  a preference. The **precision target is a DECLARATION nobody can measure**: both 5D candidate macros
  are defined and **never printed** (covering search with a positive control) and their values are J's,
  quarantined. **Affordability: `N = 4`–`5` total members inside `R5`, at `86.5%` of the CPU ceiling,
  against `5.1×`–`8.7×` for the historical 46/50 design — no affordable middle.** New **§5.8** recasts
  the cost census as **production / artifact replay / conditional / contingency** and sizes two of three
  unpriced build rows from local timings at the real `10,694` dimension (`eigvalsh` `113` s, peak
  `1.83` GB) — **minutes and gigabytes, not hours and terabytes**, with memory the binding constraint.
  New **§5.9** relays a read-only operational evidence packet, every item marked RELAYED or RE-VERIFIED
  HERE: a genuine meter receipt parses live `sacct` and is deliberately **uncommitted**; the assemblies
  gain a **measured upper bound** `≤ 0.5231` CPU task-h; a **7-day outage inside the `R5` window** cuts
  the usable schedule to **`16 d 15 h` in two blocks**; and `sacct`'s 30-day span limit makes the meter
  stop working `2 d 14 h` after the `R5` stop. **⚠ TWO STATEMENTS IN REV. 1–6 WERE FALSE and are
  corrected in place (§5.9a):** `combined_source`'s digest **is** recorded in the tree — in **G's own
  build receipt**, `9f7b2f55…` at `2026-08-12T05:46:19Z`, **four days before S read the file** — so
  §1.1's *"no digest anywhere in the tree"* and §4 row 5's *"using S's digest as G's is the
  substitution `PM-2` exists to prevent"* both fall. **An absence asserted without a covering search**,
  about a file in G's own directory in this checkout. What survives is a timing qualification and a new
  §1.5 requirement: stamp `path + sha256 + size + mtime_ns + inode + device` **at open time**. New
  **§6.7** puts **five decisions** to Joseph as packets — the cause-3 acceptance packet (`D1`), the
  per-bin precision target (`D2`), the design `N`/offsets/diagonal-or-grid (`D3`), the null packet
  (`D4`), and the `12.59` CPU task-h gap between the meter's deduplicated reading and `R5` §3's
  *"retried tasks count in full"* (`D5`) — **and takes none of them.** **The contract is NOT ready for
  an implementation authorization**, and §6.7 says what would make it ready.
  **SECOND OPERATIONAL PACKET (rev. 8) — one blocker released, one prerequisite found unreadable.**
  New **§5.9c**: the k=0 round-2 campaign spans **`37.5` h** end to end (376 tasks,
  `2026-08-30T21:29:20` → `2026-09-01T10:58:02`), and its `54.90` GPU task-hours reproduce §5.2's figure
  **exactly by a different route**. So `4`–`5` rounds fit inside **either** block of the split window
  without straddling the outage, and §6.7's readiness item 5 — rev. 7's *"the one constraint no decision
  can relax"* — is **withdrawn to a caveat**: `37.5` h is **one realization at one week's queue depth**,
  already inclusive of that week's queue wait, and a campaign would run into the pre-outage rush. The
  cause-4 second CV unfold gains a **measured upper bound `≤ 0.5764` CPU task-h** — `--null` runs inside
  `uthrow5d_combF` on `shared_milan_ss11`, **CPU and never GPU**, which is the specific thing rev. 2 got
  wrong; the identity matters, because that job is **arm 7**, not the still-unmeasured `budget5d`
  statistical+ML combine. `D5`'s figure is now dated: `12.5903` at `08:59Z`, `12.606389` at `09:20Z`,
  `≈0.05`–`0.07`/day. **⚠ AND `PM-4` CANNOT BE DISCHARGED AS WRITTEN.** New **§1.3d**: G's committed key
  inventory is **13 keys** and holds **neither `hRowIndex5D` nor `hXSecND_flat`** (re-verified here in
  `receipt_candidate_stamps_5d.json`), so *"read from G"* has no referent — and rev. 2–7's flagged
  inference that *"G is 2026-08-12, so it plausibly carries `hRowIndex5D`"* is **refuted**, the 49-key
  object being the 2026-08-16 rebuild in **S's** lineage. **The invariant stands and its route changes**:
  both digests are reconstructible from G's production-CV input, which is the same object reject
  condition **`11b`** already names, and which **G's own hash receipt does not bind** — so `PM-4` and
  `11b` fail together on one missing identity (new §7 item 17). The preflight evidence is now **committed
  off-branch** at `21b3d567`/`cd41ff41` on `lane/pm-root-inspection-20260906`, with its receipts named
  `r5-meter-receipt-INCOMPLETE-*`; `docs/orchestration/state/r5-meter-receipt.json` still does not exist
  and admission stays shut.
  **CITATION AND BLAST RADIUS (rev. 9) — no review finding.** The evidence citation moves from
  `cd41ff41` to **`1422569c`**, which supersedes it: `cd41ff41`'s `README.md` says *"four earlier jobs"*
  in the waker lineage where there are **five, six with the live one**, and states the array negative
  result **without its covering-search boundary** (three **discontiguous** queries, `≈28` days, absences
  of `22` and `3`, because `sacct` selects on runtime overlap). **Verified here:** the diff is
  `README.md` + `DIGESTS.txt` only, and **only `README.md`'s digest moves** — both receipts, all four
  raw dumps and `R5-PREFLIGHT-EVIDENCE.md` are byte-identical, so every digest-bound citation is
  unaffected. Chain, child to parent: `1422569c → cd41ff41 → 21b3d567 → 641c6812`; **rev. 7 is their
  root and none is an ancestor of this tip, and the two lanes stay separate** because that branch
  carries an authorization Joseph has not yet ruled on. New **§5.6a** names **the opening act**, because
  §4 row 3 makes the meter receipt Z's first prerequisite and *"a query plus a commit"* understates the
  consequence: **running** the meter arms nothing; an untracked or post-commit-edited receipt is still
  refused; **committing** one to `docs/orchestration/state/r5-meter-receipt.json` removes a
  **QUEUE-WIDE** refusal, since `committed_r5_receipt(queue)` takes only the queue and
  `r5_refusal_reason` consults it for **every** compute item. Three things bound the radius and none
  makes the act small: it **expires** after `R5_MAX_AGE = 24 h`; other refusals survive it; and the
  known `--kind read-only` bypass is recorded as **refused**. So the integration lane's meter repair
  **landing does not open the gate** — nobody should open it by running the repaired tool once to see
  whether it works. §5.6's *"shut by choice"* is corrected: it is shut by **Joseph's own instruction**
  — *"do not present it as valid admission evidence"* — and committing it to the gate's path **is** that
  presentation. §7 item 17 is sharpened: the ROOT **inspection is authorized** with quoted limits, while
  the **one-off accounting exception** that would let it be admitted is a proposal Joseph **expressly
  reserved to himself** and has not ruled on — authorized and unadmittable, which is not unauthorized.
  **⚠ THE OFF-BRANCH EVIDENCE IS COMMITTED BUT UNPUSHED (rev. 10), which is a defect in §5.9's
  CITATIONS and not in the evidence.** Measured with a positive control, because a zero-row query is
  not a measurement on its own: `git ls-remote origin 'refs/heads/lane/*'` returns **exactly two** rows
  — `lane/cause3-voi-20260906` and `lane/y-cause7-spec-and-scope` — and
  `lane/pm-root-inspection-20260906` is **absent**, while the same command resolves the control. So
  `21b3d567`, `cd41ff41`, `1422569c` and `d7dd2f1c` resolve **in one local repository only**, and rev. 8
  and rev. 9's *"COMMITTED"* was read as *"available"*: **committed and pushed are different branch
  properties.** §5.9's **RELAYED** items are therefore attested but **not independently fetchable**;
  the **RE-VERIFIED HERE** items are unaffected, their evidence being in this checkout. New §7 item 18
  records what would resolve it — **a push by that branch's owner, which is not this lane's act and
  should not precede Joseph's ruling on §4**, since it would publish an undecided accounting exception.
  The citation deliberately **stays at `1422569c`** although the tip is now `d7dd2f1c`: that diff
  touches **only** the authorization record, the evidence directory is untouched, and **all seven
  clauses this document quotes are byte-identical in both revisions** (substring-checked in each).
  **⚠ THE OPENING ACT IS PRESCRIBED, NOT MERELY AVAILABLE (rev. 11), and the measurement is this lane's
  own.** Rev. 9's *"nobody should perform it by running the repaired tool once to see whether it works"*
  framed the hazard as carelessness; **the documented procedure performs the first half of it.**
  `R5-METER.md:12-16` is a copy-pasteable block — introduced as *"atomically refresh the default
  receipt"* — whose `--write` target **is the admission gate's exact path**,
  `docs/orchestration/state/r5-meter-receipt.json`. Measured here: that path is **not gitignored**
  (`git check-ignore` exits `1`), **150** tracked `.json` files already sit in the same directory, and
  the runbook's closing disclaimer covers **authorization** while saying nothing about **admission** —
  which is what that path controls. **So the sequence that arms the queue is: follow the runbook, then
  `git add`**, and neither step looks like a decision; a `git add -A` or a routine "commit the state
  directory" completes it. New §7 item 19 states the requirement without choosing between its two
  remedies — the runbook's default target moves off the gate path, or the gate path stops being
  tracked-by-default — because **that is the meter owner's call, not this lane's.**
  **THE OFF-BRANCH CITATION STOPS CHASING A MOVING TIP (rev. 12).** §5.9 had described that branch by
  **counting** its commits, and the count went stale twice in three revisions — rev. 10 said *"six"* and
  named four; rev. 11 enumerated six; the tip was **seven** before rev. 12 was written. **A count of
  someone else's actively advancing branch is a field this document cannot keep true.** The pin stays at
  `1422569c` and is now stated as an **invariant with the command that tests it**: the evidence
  directory unchanged, and the seven quoted clauses of the authorization record present. **Run at the
  two later tips this lane has checked — `d7dd2f1c` and `6b439466` — all seven are present in both and
  the evidence directory is untouched in both**, each later diff confined to the authorization record.
  **A further commit on that branch now needs the check re-run, not a revision here.** Recorded with it:
  `4c30c089`'s subject line was itself a finding for §5.6a, and it reached this document only because
  rev. 11 audited rev. 10's own count instead of trusting it — **reading a cited branch beats counting
  it.**
  **⚠ AND REV. 12's PUBLISHED CHECK TESTED THE LINE-WRAPPING, NOT THE TEXT (rev. 13).** The §2 limits
  clause wraps across a `> ` blockquote continuation, so a contiguous `grep -F` calls it **ABSENT** —
  **measured at `9c1230fa`: naive reports `1 of 7` absent, normalized reports `0`.** The failure
  direction is the whole risk: a false ABSENT on this invariant reads as *"the authorization no longer
  quotes Joseph's limits"*, which would move the pin and start a hunt for a finding that does not exist,
  **on a correct branch**. Two near-misses are recorded rather than repaired quietly: this lane's probe
  string had been **pre-truncated at exactly the wrap point**, so three green runs never crossed the
  break; and **the first draft of the remedy was itself broken** — `sed`'s `\?` is not an optional
  quantifier in BSD basic regex, so it returned `0` on macOS while GNU `sed` on Perlmutter would have
  accepted it. The published check is now a **`python3` normalizer**, matching the control plane's own
  language and **tested in both directions** (`1` present, `0` on a fabricated clause). **The pin does
  not move:** at `9c1230fa` the evidence-directory diff is empty and all seven clauses are present.
  **⚠ AND REV. 14 NARROWS REV. 13's OWN FIX, WHICH OVER-SCOPED THE DEFECT AND MISNAMED ITS OWNER.**
  *"Why `python3` and not `sed`"* reads as any `sed` normalizer being unsafe on macOS; it is not.
  Measured A/B/C on Darwin against `9c1230fa`: `sed 's/^> //'` — **the line as the preflight session
  actually sent it** — returns **`1`, correct** on BSD and GNU alike; only the **`\?` generalization,
  which was this lane's**, returns `0`; the negative control returns `0`. **Over-scoping a real defect
  is a false alarm on a correct command — the very shape rev. 13 had just catalogued, one level up** —
  and this lane had also told that session the opposite before measuring, which the record now corrects.
  `python3` is still adopted, for a measured reason rather than a general suspicion: the record holds
  **4 bare `>` lines**, so the obvious hardening of `s/^> //` is precisely the unportable construct, and
  `python3` removes the class rather than one instance.
  **READINESS RECLASSIFIED, A DECISION SHEET, AND THE METER REPAIR (rev. 15).** §6.7's single readiness
  list was **circular**: it named unwritten code and the two pre-launch reviews as prerequisites for an
  **implementation** authorization, when such an authorization **is** permission to write that code and
  a pre-launch review gates a **launch**. Readiness now separates **specification acceptance** (READY;
  the act is Joseph's, and §7's nineteen items are its content rather than blockers to it),
  **implementation authorization** (**zero compute**; ready today for the five inflation gates, the
  `g^c` and `r_null` reconstructions, the dominant-block refusal, the cause-4 re-add, the receipt schema
  and the validator skeleton — **only** the null's numeric `ε` waits on `D4` and the cause-3 acceptance
  code on `D1`/`D2`), and **production authorization** (NOT ready; `D-RESOURCE`, the committed receipt,
  the `PM-*` reads, the written code, the two reviews, and `D3` if the campaign is taken). New **§6.8**
  is a **decision sheet for `D1`–`D4`** — recommended choice, scientific justification, claim supported,
  cost consequence and remaining uncertainty, one row each, **pointing at §3.7's existing packets and
  proposing nothing new**. New **§5.6b** records that the **meter repair landed** at `72bcd2f6` on
  `main` (**not an ancestor of this tip**, merge base `c71b319a`): the metered unit is an **execution
  attempt**, `sacct -X -D`, an attempt is `(JobID, Start)`, receipt schema `2`, version-1 receipts
  **refused**. **`D5` is RESOLVED** in the direction §5.9 flagged and leaves the sheet. **§7 item 19's
  first remedy is TAKEN** — no default `--write`, scratch-path examples, and a runbook section stating
  that committing to the state path arms admission queue-wide — while the **second, untracking the gate
  path, was declined and referred to Joseph**; and the hazard is now **larger**, because after the
  repair the documented command yields a valid armable receipt where before it yielded a visibly wrong
  one. The waker cadence was **wrong by an order of magnitude** (`≈0.65`–`0.69`/day, `≈28`–`29` task-
  hours by the stop, not `0.05`–`0.07`); **`N` is `4`–`5` under all four ceiling readings, re-derived**.
  **REVIEW ROUND 5 (rev. 6) found no new substantive contract finding.** Two non-blocking remnants, both
  the drafting lane's: §7 item 3 still called the prior one that *"understates a Z member"* — replaced
  with *"a prior measured on a different subject"*, with the rev.-4 changelog row that carried it marked
  **superseded in place** rather than rewritten; and rev. 5's assembly-row edit had inserted **literal
  newlines inside a Markdown table row**, splitting it across three lines and breaking the table — the
  row is rejoined, and a **covering check over the whole file** found exactly that one and none
  remaining. **The remaining work is now specification completion only** — the joint-baseline statistic
  and acceptance rule, the normalized null bound and its justification, and complete costing. Those gaps
  prevent implementation readiness; **none requires reopening the assembly algebra or the settled
  rulings.**
  **CONTRACT REVIEW OF `D1`–`D4` (rev. 16), which the earlier PASS did not cover: `D1`, `D2` and `D4`
  are NOT ready for adoption as written and `D3` is supportable conditionally. Joseph approved the
  findings and rev. 16 implements them; the assembly algebra and the existing rulings are not
  reopened.** `D1`'s **thresholds are WITHDRAWN as acceptance criteria** while the statistics and direct
  normalization stand — macro formatting does not establish what sensitivity is scientifically
  acceptable, and the half-a-display-unit rule behind the numbers is **factually wrong in both
  directions at `12.5%` each under the stated synthetic sampling model** (a value uniform in its decade
  and a change uniform on `[0, one display unit)` — derived, then checked on `200,000` pairs; the rate
  belongs to that model, the bidirectional failure does not); **rounding equality** is the
  exact test if display invariance is what is meant. New **§3.7d**: every proposed gate is **blind to
  correlations** — `I₂` and `[[1,0.9],[0.9,1]]` give identical trace and per-bin statistics while their
  sum and difference uncertainties move `+37.8%` and `−68.4%` — and it is **live**, because
  `project_cov_nd.py` marginalizes the assembled covariance as `M C Mᵀ`; three candidate legs, none
  adopted. `D2`'s option (i) is **not adopted** — a missing data release does not prevent specifying a
  scientifically motivated per-bin tolerance. `D4`'s **`ε` is WITHHELD**: it is a summation bound over a
  computation that is not a summation, `n_rep` counts output bins while every accumulation runs over
  events, and the estimator is *"nearly deterministic in `seed` alone"* by its own module — a
  reproducibility question. `11b`'s **operand is corrected** (persist `x_cv`, `x_cv2` and the predicate,
  `1.05` MB against `≈41` GB) and **`11c`** is added as a conditional cross-check. Outcome branches are
  **restated over a declared leg set `L`**, so a third leg cannot be ignored by a two-leg MET branch.
  `N = 4`–`5` is re-labelled a **planning estimate, not demonstrated capacity**. **Zero cost, and one
  Tier-3 prerequisite removed**; the one new compute item — a `≈11.6` GPU task-h determinism control —
  is **returned as a bounded proposal and not run**. Five new §7 items (20–24) carry the questions.
  **ROUND 2 OF THAT REVIEW (rev. 17) accepted the threshold withdrawals, persisted null operands,
  correlation limitation, conditional `D3` and generalized leg-set branches, and found the REPLACEMENT
  `D4` proposal not yet passable.** Relayed **without** an approval statement, so rev. 17 separated
  corrections of this lane's own errors — made unconditionally — from the reviewer's dispositions, which
  it marked pending; **Joseph approved those findings on 2026-09-07 and rev. 18 discharges the mark.**
  **The distinction rev. 17 drew is kept, because approval is where it gets lost: the FINDINGS are
  approved, and `D1`, `D2` and `D4` are NOT adopted — the approved finding about them is that they are
  not ready as written, with `D3` conditional. No cell opens and no count moves.**
  **A FOLLOW-UP CHECK (rev. 19) confirmed that separation and found three of rev. 17's own explanations
  still wrong — none a new decision, all this lane's errors, corrected unconditionally.** `B > S` does
  **not** mean every correct run fails: **`B` is an UPPER bound on the error**, so a loose `B` above `S`
  establishes that **`B ≤ S` is not demonstrated** — a statement about the evidence — and **not** that
  the envelope is inadequate, which is a statement about the world. *"Never taken as an endpoint"* is
  withdrawn: **either endpoint is admissible when justified**, and what is forbidden is choosing
  mechanically. *"Tier 2 validator runtime, not `R5`"* is a **category error** — Tier 2 is permission to
  write code, `r5_meter` meters **scheduler tasks by `ElapsedRaw`**, and arithmetic folded into an
  in-scope task adds no row while lengthening the metered quantity; §3.7d now carries a four-venue
  table. And the control's *"no recorded actual"* was a **false absence citing the wrong launcher**: the
  unmeasured combine is `budget5d`, while the control invokes **`uthrow5d_combF`**, measured three times
  at §5.9 row 13 (`0.3875`/`0.4239`/`0.5764` CPU task-h) — the control stays unpriced, but on `n` and
  the thread-count arm rather than on an absence. **`B ≤ S`, the three gaps, the price withdrawal and
  every disposition stand as written.**
  **REV. 20 — those corrections PASS, with one left and one operational re-measurement.** §3.7d's
  figures were called *"venue-independent"*; they are **local timing estimates** whose runtime depends
  on hardware, threading and numerical libraries, now labelled **MEASURED locally / TRANSFERRED with
  runtime unestablished elsewhere** — and `s_eig`, the only non-negligible one, is the most exposed,
  since §3.7a's own finding is that nothing pins the thread count. New **§5.6c**: the meter repair is
  now **on `main`** — `origin/main` = `d4922b89` and `72bcd2f6` is an ancestor of it, so §5.6b's branch
  framing is superseded, while the merge base with this tip is still `c71b319a`, so **every
  `r5_meter.py` file:line here still describes the pre-repair version**. Admission is shut more strongly
  than before: **`git log --all` over the gate path returns `0` commits — it has never been armed on any
  ref**. **And one relayed ruling is NOT corroborated:** that Joseph ratified the attempt-summing
  reading and declined the untrack. At `d4922b89` the source FINDING is still *"open — three things are
  with the decision owner"*, so **§7 item 19 stays referred and `D5` stays resolved by code, not
  ratified** — uncorroborated is not false, and if the relay is right the outcome is the one already
  assumed.
  **REV. 21 — CORROBORATED, and by the artifact §5.6c said was missing.** Joseph confirmed both
  rulings directly on 2026-09-07, having given them **2026-09-06** on approving the landing;
  `DECISION-20260907-joseph-ratifies-r5-attempt-accounting-and-declines-untracking.md` is on `main`
  (`3497abec`, amended `32880a6f`) and the finding is de-staled against it at `6669ac3b`. **§7 item 19
  closes as DECLINED and `D5` is RATIFIED** — the alternative reading of R5 §3 is overturned by
  decision, so reviving it needs a new decision rather than an edit. **Admission is still unarmed.**
  The relay was accurate throughout; only the record was missing. **`min(achievable, acceptable)` is WITHDRAWN as acceptance-blocking:** an observed
  reproducibility floor is not an acceptance tolerance, and §3.6a — two sections earlier in the same
  document — says such a floor bounds `ε` from **below**, so `min` inverted its direction. Replaced by
  **`B` (operating-error bound, with assumptions and confidence), `S` (independently justified
  scientific cap), the precondition `B ≤ S`, and `ε` argued within `[B, S]`**; if `B > S` the finding is
  that **the execution envelope is not demonstrated adequate**. The control is revised on three gaps —
  **a within-envelope null does not measure a between-envelope shift**, the repeat count needs a
  coverage/confidence objective and its sampling assumptions, and **two arms do not prevent tuning** —
  and its subject engages `§6.4`. **Its `≈11.6` GPU task-h price is WITHDRAWN**: an invocation is a whole
  `do_combine`, and the combine is a **CPU** job (`sbatch_uthrow_combine_5d_fast.sh:4`), a correction
  §0.0's rev.-2 row 10 had already made once. **Three routes to `B` are now named, none privileged**, the
  cheapest being **code, not compute** — pinning `num_threads`/`deterministic`/`force_row_wise`.
  **Nonblocking, all corrected:** the persistence was priced against `≈41` GB when the throw product is
  **`2.668` GB measured** (`41` GB is the 45-component band family — a `15×` operand error whose
  conclusion happened to survive); §3.7d's legs cost **no new members but are not free** (`s_eig`
  `≈1`–`3` min per member, measured by timing `eigvalsh` at four sizes and scaling by `n³`); §3.7's
  *"this section completes them"* is withdrawn; receipts now say **"did not exceed their declared
  movement limits"** rather than *"did not move"*; and `D1`/`D2` need **justified tolerances and scope**,
  not two numbers.

### Z assembly/spectrum pilot — the outcome route (2026-09-17)

- [`NAVIGATION-20260917-z-pilot-outcome-route.md`](NAVIGATION-20260917-z-pilot-outcome-route.md)
  - **NAVIGATION ONLY — no measurement, no verdict, no authorization.** Where the Z
  assembly/spectrum pilot's completed outcome lives, at full commit identity, because the records
  are on `lane/z-assembly-pilot-20260914` and `main` had no pointer to them. Job **`58454524`**
  completed at **`ExitCode 2:0`** — 2 is the CLI's *completion* code for "construction ran, science
  NON-PASSING", so `sacct`'s `FAILED` is not the verdict. Two 5D covariance objects and a null slab
  exist with matching receipts; **`scientific_acceptance` NON-PASSING, `adoptable` false,
  `outcome.assessable` false on reject condition `4c`**, all four `withheld_boundaries` still
  `WITHHELD`. **`B`, `S` in full, and `ε` are open; Gate 2 remains FAIL; construction authorizes
  nothing.** Outcome record `1b2873a8e9b3c78568725494799a3df6234a39d5`, corrected recommendation
  §12 **as corrected by §13** at `affc9e03119230ece17f977325d8a1ba00d68827` (**§11 is withdrawn**; §12.7's decision table is superseded by
  §13.7, after independent assessment `ed18a231de4c3b6b016e268be54257579b6c7739`), accounting `0202591b15092486b6db167478cf72290fcc7ed9`,
  assembling revision `fb9ec3560fd6d62295dffc81b5694c9e26667d5b`. Also **corrects a false claim
  that `main` contains no Z content** — it carries **26** Z-named files including the `SPEC`,
  Joseph's `DECISION-20260906`, `Z_CONSTRUCTION_PLAN.md` and ten modules; what it lacks is the
  pilot-specific execution code, the two 2026-09-16 records, and the post-freeze RUN_LOG
  chronology. Landing those is a **separate merge decision and is not authorized by this record.**

- [`DECISION-SUPPORT-20260916-z-to-adopted-5d-covariance.md`](DECISION-SUPPORT-20260916-z-to-adopted-5d-covariance.md)
  - **DECISION SUPPORT ONLY — ratifies no criterion, adopts nothing, grades nothing, and no Z
  covariance has ever been constructed.** The route from Z's outputs to an adopted 5D covariance,
  measured 2026-09-16. Leads with §3.5's ruling that a complete favourable Z *"would establish
  exactly one thing... Nothing else"* and does not move **Gate 2** — so the cause cells are
  necessary and not sufficient. Corrects the cell population to **26, not 28** (cause 5 is one
  disposition, cause 3's `M` splits into `M(i)`/`M(ii)`), with **zero RESOLVED and none droppable**.
  **A1 is OPEN:** `S` is discharged by bounding **for the F7 channel only** — the throw-deviation
  and completeness-division channels are unbounded, §7 item 4 — `ε = 1e-9` is **PROPOSED and
  UNGRADED** with its falsifier **UNEVALUATED**, and `B` is the binding quantity because §3.7a
  rev. 19's `ε = S` would be a tripwire nothing can fire. **§3 reconciles §7 item 1 with the
  completed precursor without reopening it:** the persistence requirement is already discharged
  there (`hCvExecution{k}`/`hCvSupportMask` absent at `923e1323`, present at the precursor's
  producer `e09513d8`), so the null denominator is already measured at `3.2124510692799616e-37` —
  for the **precursor**, not G, whose check stays prospective. Also: the assembly costs ~2 min of
  eigensolve against **89.11 GB** of input I/O, and the binding constraint is the **2026-09-30 stop
  date**, not the ceiling. Read its `CITABLE FOR` / `NOT CITABLE FOR` header before quoting any
  part of it.
- [`PROPOSAL-20260916-B-and-S-bounded-determinism-control.md`](PROPOSAL-20260916-B-and-S-bounded-determinism-control.md)
  - **PROPOSAL ONLY — authorizes nothing, establishes no `B`, no `S`, no `ε`.** One bounded route to
  `B` via route (i), plus what remains of `S`. **§1:** observed bitwise agreement supports only the
  configurations actually tested; `B = 0` across a declared envelope is a separate claim needing an
  enforcement argument, not more runs; and three runs are a **bounded falsification experiment**,
  not a proof or coverage guarantee — agreement must be reported as *did not falsify*. **§2** derives
  materiality from the implementation rather than from a name search, and corrects the claim that
  every proposed control is a thread count (`deterministic` and `force_row_wise` are not): the
  material channel is LightGBM's training histogram construction alone, since the CV path runs at
  `train_frac=1.0` with no split RNG and contains **zero** BLAS-threaded reductions. It classifies
  settings as must-fix, must-record, **not established as material** (`OMP_PROC_BIND`/`OMP_PLACES`)
  and undeterminable (`OMP_SCHEDULE`), and names the enforcement gap: `deterministic` is documented
  only for a fixed thread count and says nothing across **CPU models**, which makes the per-run
  CPU-model receipt a necessity rather than good practice. **§3** states explicitly that a
  pinned-chain result establishes **nothing** about the existing unpinned precursor. **§4** prices
  the reservation by the **enforced** `--time` cap (9.0 CPU task-hours at the launcher's own 3:00:00,
  reducible to 3.0 by submitting a tighter cap), with historical elapsed times used only as
  corroboration. **§6** resolves the independent-assessor assignment from git — predeclaration is an
  ancestor of the assessment, and the assessor lane has zero commits touching what it graded.
  Read its `CITABLE FOR` / `NOT CITABLE FOR` header before quoting any part of it.
### Scalar-5D completion inventory, the null route, and P1 (2026-09-18)

- [`PACKET-20260918-scalar5d-completion-inventory-and-null-route.md`](PACKET-20260918-scalar5d-completion-inventory-and-null-route.md)
  - **SOURCE REVIEW AND RECONCILIATION ONLY — nothing adopted, nothing graded, no compute.**
  Reconciles the designated bounded inventory (`ebba67ab`, `docs/literature/2026-09-18-scalar5d-covariance-inference-audit.md`,
  branch `audit/scalar-5d-publication-gaps`) against `c4baf0d2` §19 — the audit is **24 minutes
  stale** and predates E1/E2's discharge; its rank-1 prescription routes through `[B,S]`, which
  `SPEC:1552` titles *"ENTIRELY PROPOSED"*. **The `ε` finding: every route to it is closed, not
  merely unfinished** — withdrawn (rev. 17), unavailable from a boolean `B` (`78a8c2ee` §1.4),
  forbidden off Z's own null (`SPEC:1410`), declined on transfer, and `θ` closed. **So a repeat
  experiment cannot produce `ε` either**; the objective is to make it unnecessary via bitwise
  identity. **The products are not irrecoverable, on §6.4's own precedent** — *"This does not
  retrospectively regrade G… the defect is in the guard, not in the product."* **Live finding:**
  `sbatch_uthrow_combine_5d_fast.sh:9` asserts the null *"must be zero"*; the measured value is
  `4.452e-14`. **P1 is COMPLETE** — four maps enumerated with widths, masks, ordering, orphan
  policy and paired central estimate; `project_cov_nd.py` records **zero digests** (control: 13 in
  `p4_project_4d.py`), which is the larger and unfiled half of the OI-129 family. **One published
  claim is deferred**, on `(E_avail, W)`, 42 dense bins (`main_paper.tex:49-51`).

### Scalar-5D publication completion — the plan (2026-09-18)

- [`PLAN-20260918-scalar5d-publication-completion.md`](PLAN-20260918-scalar5d-publication-completion.md)
  - **THE ONE COMPLETION PLAN for the scalar-5D uncertainties and required projections**, under
  Joseph's 2026-09-18 goal. Sixteen milestones `M-A`…`M-P` with evidence and gate for each, plus
  **decision-ready recommendations for the four open decisions** — grid-versus-diagonal, the L4
  boundary key, `τ`'s scientific input, and the registry mismatch rule — each separating engineering
  choice from scientific judgment. **Two facts from `AGENTS.md` reshape the target:** `:30` lists the
  `(E_avail,W)` covariance itself as QUARANTINED and unquotable and `:27` requires the quotable
  covariance to be projected from the adopted **selection-complete** trunk, so **M1 is the only
  admissible route** to the one deferred claim; and `ESTIMATOR_REGISTRY:29`'s *"#16 five-band coverage
  (publication gate)"* is plausibly discharged by Z, since `z_contract.py:67` takes exactly the five
  bands that laterally shift kinematics while the four excluded are weight-only. Companion to
  [`PACKET-20260918-…`](PACKET-20260918-scalar5d-completion-inventory-and-null-route.md), which holds
  the evidence and the corrections. **Nothing adopted; no compute requested.**


### Rank-6 significance consumer — draft contract (2026-09-18)

- [`CONTRACT-20260918-rank6-significance-consumer.md`](CONTRACT-20260918-rank6-significance-consumer.md)
  - **DRAFT FOR APPROVAL — no significance computed, nothing adopted, neither existing consumer
  run.** The eight declarations that must be fixed before the deferred `(E_avail, W)` significance
  can be produced. ⚠ **Its central finding is dated from the repository: the claim's region is HALF
  prespecified and HALF data-selected.** "Open question 6" — the high-`E_avail` excess as a
  *question* — is recorded 2026-06-03 (`de84c61e`), before the W axis existed; the first
  `(E_avail,W)` excess test ran 2026-06-07 (`95ce2950`); and **`W >= 1.8` first appears in code
  2026-06-09** (`b64cf582`), two days later, with `HIGHER_DIM_OMNIFOLD_DESIGN.md:169` stating that
  the W axis *"localizes open question 6 to the high-W DIS corner."* Also measures that the two
  existing consumers use **different** `E_avail` cuts (`>= 0.8`, 3 of 7 bins, versus `>= 0.4`,
  4 of 7) and that `eavailW_covariance.py:545`'s comment misstates its own W selection as four bins
  where the code takes three. Raises **D5**, a claim-scope judgment for Joseph, recommending the
  significance be quoted on the prespecified `E_avail` region with the W localization kept at
  central-value level. Companion to [`PLAN-20260918-…`](PLAN-20260918-scalar5d-publication-completion.md).


### The scalar-5D trunk's reproduction path (2026-09-18)

- [`REPRODUCTION-20260918-scalar5d-trunk-path.md`](REPRODUCTION-20260918-scalar5d-trunk-path.md)
  - **The "supported reproduction path" Joseph's completion clause names, which had NO document** —
  a covering search found the repository's seven `reproduc*` files all PET-scoped or generic. Five
  ingredients (code identity, digest-bound inputs, environment, invocation with its exit-code
  contract, measured resource envelope) and a **measured** reproduce/does-not-reproduce split: four
  internal identities at exactly `0.0`, the central vector bitwise on payload at 65,856/65,856, and
  `r_null` to 1.00 ULP in three summation orders — against the fact that **the null pair is not
  bitwise** at `4.452e-14` while its launcher asserts *"must be zero"*, and that any envelope wider
  than one process has **never been tested**, so `B` is UNEVALUATED rather than refuted.
  ⚠ Two load-bearing qualifications: the **pin set is incomplete** (four OpenMP variables, zero
  occurrences repo-wide against a 43-hit positive control), and the chain carries **two distinct
  unified-throw ensembles**. Concludes that the required property is **bitwise identity as a
  consequence, not a preference** — the tolerance route is closed. **Nothing adopted; no compute
  requested.**

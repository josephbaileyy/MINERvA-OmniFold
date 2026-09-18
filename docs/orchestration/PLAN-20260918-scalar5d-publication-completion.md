# COMPLETION PLAN — scalar-5D uncertainties and the required projections

**One plan, maintained in place.** Supersedes no record; indexes them. Base: `AGENTS.md`, the audit
`ebba67ab6af17a159ae395cb06312b0dcbdca841`, and the completion packet through `40e52d48`.

**Goal state (Joseph's):** an explicitly adopted scalar-5D covariance with a supported reproduction
path; the required exact projections with correctly paired central values and verified output
records; scientific claims supported at their stated level; synchronized and successfully built
note, primer and paper. **Submission is Joseph's act.**

**Preserved and not reopened:** the completed precursor, the assembly/spectrum pilot, the 2D result
(central *and* uncertainty, both `VALIDATED`), and the 3D/4D/5D central values and closures.

---

## 0. Two facts from `AGENTS.md` that reshape the target

**0.1 The publication claim's existing consumer is already quarantined by the front door.**
`AGENTS.md:30` lists *"old unified 4D/FPS covariances, old PET precision comparisons, **`(E_avail,W)`
covariance**, and dependent significances"* as `QUARANTINED` and **unquotable**. `AGENTS.md:27` states
the rule positively: *"The quotable covariance must be projected from the final adopted,
**selection-complete** 5D trunk."* So M1 is not an optimisation — it is the only admissible route to
the one deferred claim, and the existing `eavailW_covariance.py` product cannot be quoted whatever
its inputs. **PROOF-EQUIVALENT (a governing record, read directly).**

**0.2 Selection-completeness is a named publication gate, and Z plausibly discharges it.**
`ESTIMATOR_REGISTRY.md:29` carries *"Caveat: lateral still support-limited until #16 five-band
coverage (**publication gate**)"* against the historical 5D product. Measured: `z_contract.py:67`
sets `LATERAL_BANDS = tuple(p4_lib.BANDS)`, and `p4_lib.BANDS` is exactly
`['BeamAngleX', 'BeamAngleY', 'MuonResolution', 'Muon_Energy_MINERvA', 'Muon_Energy_MINOS']` — **five
bands**. The nine-band historical set in `eavailW_covariance.py:40` adds `MinosEfficiency`,
`GEANT_Neutron`, `GEANT_Pion`, `GEANT_Proton`. **The five are the bands that laterally shift
reconstructed kinematics; the four excluded are weight-only** (an efficiency weight and three hadron
re-interaction weights), which is why they cannot enter an active lateral *swap*.
**NUMERICAL/SOURCE DEMONSTRATION, not proof:** the argument is from what each band is and what its
name denotes, and it needs confirmation of how each is actually *applied*. Routed to `[cb0b6b]` as
part of cause 7. **If it confirms, Z's construction is what discharges the `#16` publication gate** —
the most favourable open item in the package.

---

## 1. Milestones, each with its evidence and its gate

| # | Milestone | State | Evidence | Blocked on |
|---|---|---|---|---|
| M-A | Pilot construction, PSD/identity gates, precursor persistence | **DONE** | pilot receipts; closed by contract | — |
| M-B | Null reconstruction (E1) and tolerance provenance (E2) | **DONE** | 1.00 ULP, three summation orders, predicate recomputed; `5d617da8` 2026-08-08 | — |
| M-C | External CV cross-check | **DONE** | 65,856/65,856 identical, `max abs diff` 0; mask and row index elementwise | — |
| M-D | Variance positivity on the reported support | **DONE** | 0 non-positive of 10,694, all finite | — |
| M-E | P1 projection definitions | **DONE** | packet §4; four maps, widths, masks, C-order, orphan policy, paired central | — |
| M-F | Cause-3 acceptance design | **DESIGNED, NOT APPROVED** | `9836a64f` + assessment `6caa1f48` | **D1, D2, D3** |
| M-G | Projector instrumentation (OI-129 family) | **DONE (code + first tests)** | `project_cov_nd.py` 0 → 16 digest sites, **row-index array added** (it wrote none), readback required; `p4_project_4d.py` gains `proj4d_sha256` + readback, old field retained; 7 tests, mutation-verified | owning re-verification |
| M-H | Component fingerprint writers | **DONE (code + first tests)** | `combine_cov_nd.py` 27 → 102 lines: all nine fingerprint fields recorded (unsupplied ones as explicit `UNDECLARED`), ensemble-count scalar added, row index added, per-replica digests; 6 tests | — |
| M-I | Registry fingerprint rule | **UNSATISFIABLE AS WRITTEN** | rejects every throw component at every `k`, including `k=0` | **D4** |
| M-J | Lineage / two-ensemble question | **EVIDENCE COMPLETE; DISPOSITION OWED** — `e393ad5e` traced it and offered **no disposition**, correctly | **Two distinct unified-throw ensembles in one chain**: parent mean-centered with `uthrow_source` 2026-08-06, pilot throw input the 2026-09-14 precursor, corroborated by the parent's upstream null being G's `5.8223e-50` against the precursor's `1.4302e-50`. Plus `ESTIMATOR_REGISTRY:29` names `..._UTHROW.root` while the chain consumed the unsuffixed file (registry √tr `5.8077e-38` vs the parent's `sqrt_tr_new` `5.2696e-38`) | **R5, a ruling** — not lane work |
| M-K | Cause 1, 2, 4, 5, 6, 7 dispositions | **1/2/4 criteria DRAFTED** (`230aecf7`, claimed tolerance-free, under assessment); **5 and 7 evidence COMPLETE** (`80b464ca` + my `Σ_A L_b` trace) | cause 7: laterality measured on payload, `measured lateral set == p4_lib.BANDS` True, 10 endpoints verified, lateral sum traced to the **active** blocks with `active_total_eq_sum5 = 0.0`; cause 5: VL66 falsifier NEGATIVE across Z's 15-module closure | **two rulings** (cause 7 sufficiency, cause 5 §6.1 disposition); cause 6 |
| M-L | `ε` / null acceptance | **BLOCKED BY CONTRACT**, but its *next step* changed | every route to `ε` closed (packet §2.1). **P1n WITHDRAWN** — the four OpenMP variables act on a channel LightGBM was measured to ignore; **P2 repriced `1.73` → `9.00`** (n=3), those figures having been measured actuals not enforced caps; **new P1d** tests the configuration at `0.25` | Joseph's §6.4 route ruling; P1d is running and needs no decision |
| M-Q | **The supported reproduction path** | **DONE** — `REPRODUCTION-20260918-scalar5d-trunk-path.md` | Five ingredients assembled; measured reproduce/does-not split; concludes **bitwise identity is required as a consequence, not a preference** | — |
| M-M | Trunk adoption | **NOT REACHED** | — | M-F…M-L |
| M-N | M1 **publication** product `(E_avail, W)` | **NOT REACHED** | — | M-M + M-G, then compute authorization |
| M-R | M1 **diagnostic** projection — the cycle-breaker | **INPUT VERIFIED, RUNNABLE** | `run_m1_diagnostic.sh`: nine refusals incl. R5 admission; `runClass` written **into** the product; publication-path rc 3 re-measured by a ratchet. **Input exists and verifies: `z-cv.npz` from job `58454524`, 3 of 3 digests re-measured (§12.1); NPZ input path implemented, row order cross-checked, source binding carried, non-adoptable source refuses publication class.** 22 + 36 tests | **D5 only** — the mask is declared (`receiving-cells`) and the input is no longer in question |
| M-S | Determinism configuration, established **and tested** | **PARTIALLY MEASURED** — job `58507305` COMPLETED, `54` s. ⚠ Its thread axis was **degenerate**; see §13 | **Established at one thread:** all three arms give the **identical** model (digest `b151b10b…`, 200,000 rows, floor SATISFIED) and each is bitwise reproducible across repeats in one process — so the knobs do nothing at `num_threads=1` and their whole effect is on the multi-thread path. **Not established:** thread-count invariance, which was the question. 23 tests | one more `0.25` task-h submission — my corrective resubmission is spent |
| M-O | Rank-6 consumer contract **and the consumer itself** | **CONTRACT DRAFTED + CODE WRITTEN** | `rank6_significance.py`: five declaration refusals with distinct codes, ndf from the **retained rank**, truncation scan, region as an explicit declaration; **19 tests, both key guards mutation-verified** | **D3 + D5** supply the two values; the CLI payload path is deliberately unwired |
| M-P | Note/primer/paper synchronization, build, **and retracted-value containment** | **BASELINE MEASURED AND GREEN, containment gate verified covering all three** | 2026-09-18 forced rebuild: `RESULT :: PASS`, note 94pp / primer 5pp / paper 3pp, containment `0 of 10 struck literals`; standalone at `3c3e9f2`, clean, level with origin, **all 26 `.tex`/`.bib` byte-identical** | re-verification after M-N's content edits |

**Ordering that matters:** M-G must land **before** M-N, because a digest retrofitted after a file
exists records only that the file has not changed since the retrofit. M-G and M-H are mine and need
no decision; I am proceeding with them.

---

## 2. The four decisions — recommendation, alternatives, consequence, exact change

Each states whether it is an **engineering choice** (mine, recorded) or a **scientific judgment**
(Joseph's), and for the latter, which publication claim it affects. The affected claim is in every
case the single deferred one, `main_paper.tex:49-51`: *"localize a generator deficit in the joint
high-available-energy, high-mass region. The latter is a central-value result; its significance
awaits adoption of a common five-dimensional covariance."*

### D1 — Grid versus diagonal member family · SCIENTIFIC, and smaller than it looks

**RECOMMENDED: keep the diagonal family, hold the `(42, 1000)` group assignment fixed at its archive
values, and declare the architecture axis as a named scope limit of cause 3's conclusion. Do not buy
the grid.**

**Why the stakes are lower than the framing suggests.** The audit states the governing fact: *"A
seed-sensitivity diagnostic is **not an additional budget block**."* Cause 3 is an **acceptance**
criterion, not a contribution to the quoted uncertainty. So an architecture axis that was never
varied **does not understate the published uncertainty** — it narrows the scope of the acceptance
argument. That is a real limitation and a recordable one; it is not a defect in the number the paper
would quote.

**Alternatives.** (a) **2-D grid** — resolves whether the inter-module split matters; costs a
launcher change, a second offset axis, and at least a doubling of members, and every member is a
full round because arms 1–2 take `42 + OFFSET` as their *estimator* seed. (b) **Unify the seeds** —
**refuse**: `sweep_bank_5d.py:354-356` names this as the trap and says it *"silently re-seeds one of
the two."* (c) Diagonal with the limit declared — recommended.

**Exact change.** In the cause-3 packet: declare the member family diagonal; declare the group
assignment `{arms 1–4: 42, arms 5–7: 1000}` fixed; add a residual stating that cause 3's conclusion
is conditional on that architecture and that the split is invariant under `k` and therefore
unresolvable within this family.

**Your approval authorizes:** declaring the offsets and moving to a member-production *request*
(separately priced, not requested here). It does **not** adopt any boundary value.

### D2 — The L4 boundary entry · ENGINEERING to create, SCIENTIFIC to value

**RECOMMENDED: create the fourth `Z_BOUNDARIES` key, withheld, and adopt L4's criterion in two parts
— the boolean plus a required margin.**

⚠ **One correction to the proposal as it reached me:** `[91eaa2]` offered L4 as approvable *in full,
including its value*, because the F7 outcome is discrete. `[cb0b6b]` then showed the criterion as
written **cannot distinguish "tested and stable" from "no member came near the branch point"** —
identical booleans either way. **So L4 is not value-free after that correction:** it needs a declared
minimum margin to the branch point for the test to count as performed. That margin is a number and it
is scientific. I am flagging this because "approvable in full" would otherwise carry into your
decision, and it no longer holds.

**Scientific consequence.** L4 protects the F7 centering choice. `AGENTS.md:29` already rules that
*"mean-centering alone is disqualified"*, and `ESTIMATOR_REGISTRY.md:29` records the historical
adopted product as *"adopted mean-centered"*. So the centering decision is constrained from the front
door and **L4's job is to stop a member family silently flipping it.** Nothing else covers that.

**Alternatives.** (a) Create the key, withhold the value, adopt the boolean + margin form —
recommended. (b) Create the key and adopt a bare boolean — rejected on `[cb0b6b]`'s argument; it
admits a vacuous pass. (c) Leave L4 uncovered — leaves a published binary choice with no criterion.

**Exact change.** Add to `nd-unfolding/z_contract.py` `Z_BOUNDARIES` a key `cause2_f7_margin`,
`Boundary.withheld(...)` with the reason stating that the boolean leg is structural and the margin leg
is an unset scientific number; extend `tests/test_z_contract.py`'s import-time assertion so the
withheld set becomes five, so the day a value is declared a test changes and a reviewer sees it.
**I can write this code on your approval of the key's existence** — the value stays yours.

**Your approval authorizes:** creating the key and the test (code). Not its value.

### D3 — The scientific input needed to justify `τ` · SCIENTIFIC, and it is a convention, not a measurement

**RECOMMENDED: declare the significance threshold at which the deferred claim will be asserted at
all. That is `τ`'s missing input, and it is declarable now, before any product exists.**

**Why this is the right input and is non-circular.** `τ` bounds movement of M1's projected correlation
matrix. That matrix enters the publication claim only through the corner χ² — measured,
`eavailW_covariance.py:546-548` defines the corner in code as `E_avail >= 0.4 & W >= 1.8`. So the
question *"how much may the projected correlation move before the claim changes"* reduces to *"how
much may the significance move before the claim changes"*, which reduces to **"at what significance is
the claim made"** — a collaboration convention (evidence versus observation), **not an observation of
these data.** Declaring it now cannot be contaminated by a favourable result, which is exactly what
`SPEC` §6.4 and your standing instruction forbid.

**Alternatives.** (a) Declare a relative tolerance on the correlation matrix directly — arbitrary, no
connection to any claim, and it is how the three withdrawn format-derived numbers were produced.
(b) Derive `τ` from observed movement once M1 exists — **forbidden**: a threshold placed to obtain a
verdict. (c) Declare the significance threshold — recommended.

**RECOMMENDED VALUE: `N = 3`.** ⚠ Revised 2026-09-18. This section previously said *"you name
`N`"*, which is asking you to invent a criterion without a recommendation. Withdrawn; here is the
recommendation and its justification.

**Why 3σ and not 5σ or 2σ.** The threshold has to match what the claim asserts, and the claim —
`main_paper.tex:49-51` — is that a generator *under-predicts in a localized region*. That is a
statement about disagreement between data and a model, **not the discovery of a new phenomenon**. So:

- **5σ is the discovery convention** and is the wrong instrument for a generator-comparison claim.
  It is also very likely unreachable here: the consumer takes `ndf` from the **retained rank**, and
  `C_Z` has 5,214 negative eigenvalues of 10,694, so the retained rank on a 42-cell projection is
  small. Setting a threshold that the design cannot reach is not conservatism, it is declining to
  make the claim while appearing to keep it.
- **2σ is below the level at which a localized deficit would be asserted in print**, and it is
  inside the band where an unmodelled correlation could produce the effect.
- **3σ is the standard evidence-level convention** and is what this claim's language ("localize a
  generator deficit") corresponds to. It is declarable now, before any product exists, and cannot be
  contaminated by a favourable result — which is the property `SPEC` §6.4 and your standing
  instruction require of it.

⚠ **D3 AND D5 COMPOSE, AND THE COMPOSITION IS THE PART THAT MATTERS.** `N = 3` is recommended
**conditional on D5 resolving as recommended** — quote on the *prespecified* `E_avail` region. If
instead the claim is quoted on the data-selected `W ≥ 1.8` corner, then 3σ is **not** adequate as
written and must either be raised or paired with a declared selection-aware calibration, because the
boundary was chosen after seeing the data (`W ≥ 1.8` enters code 2026-06-09, two days after the first
`(E_avail,W)` excess test). Ruling D3 at 3σ while ruling D5 the other way would produce a threshold
that looks predeclared and is not. Two rulings that each hold only under a precondition the other
removes compose into a defect, so they should be ruled together or D3 made explicitly conditional.

**Exact change.** Declare in the cause-3 packet: *the deferred claim is asserted at ≥ 3σ on the
prespecified region*. `τ` is then whatever projected-correlation movement leaves the corner
significance above 3σ — **a calculation performed once on M1, not a judgement.** `rank6_significance.py`
already refuses without this declaration (rc 6), so the value has a place to land.

**Your approval authorizes:** the threshold declaration, which converts `τ` from blocked-on-judgement
to computable-from-M1 — and the diagnostic M1 run that computes it is now authorized separately by
your 2026-09-18 grant, so this no longer waits on adoption. It authorizes no publication product.

### D4 — The registry mismatch rule · ENGINEERING repair of a SCIENTIFIC criterion

**RECOMMENDED: amend the estimator-seed field of the fingerprint convention to within-family identity
plus a declared inter-family map; retain all eight other fields unchanged.**

**Why an amendment is required rather than optional.** `ESTIMATOR_REGISTRY.md:17-22` requires *"every
covariance component must carry the identical estimator fingerprint as its central product (reject on
mismatch)"* and `:29` declares the central at `est seed 42`, while the throw payload records
`estimator_seed = 1000` — a difference `sweep_bank_5d.py:354-356` documents as **deliberate**. Applied
literally the rule rejects **every** throw component at **every** offset `k`, including `k = 0`, which
is the archive and is Z's own build. **It therefore rejects the product the registry exists to
describe and cannot be satisfied at any `k`.** That is unsatisfiable by construction — the same class
as the `1e-12`-clamp defect the campaign already repaired once.

**Alternatives.** (a) Amend the seed field only — recommended; keeps the protection that matters.
(b) Exempt the seed field entirely — discards a real check, and cause 3's whole subject is estimator
seeds. (c) Unify the seeds — **refuse**, as in D1. (d) Leave it — leaves a live rule that rejects the
adopted product, which is worse than no rule because it will be read as a failed check.

**Scientific consequence.** The convention exists to stop a covariance component being paired with a
central product built by a *different estimator*. That protection is intact for the eight other
fields and must stay; only the seed field needs the family-relative reading, because only that field
is deliberately heterogeneous by module.

**Exact change.** Amend `docs/ESTIMATOR_REGISTRY.md:17-22` to read, for the estimator-seed field:
identity **within** an estimator family, plus a declared map between families, with the
`{sweep_bank_5d: 42, unified_throw_cov: 1000}` assignment recorded as the map. Add a note on row `:29`.
Half the machinery already exists: `analyze_universes_5d.py:137-166` refuses a member assembled from
mixed seeds.

**Your approval authorizes:** the text amendment (a criterion change, hence yours), after which
`M-I` closes.

---

## 3. Independent work proceeding now, needing no decision

1. ~~**M-G, projector instrumentation.**~~ **DONE.** Two things were wrong and only one was filed.
   `p4_project_4d.py` now digests the output file and reads `hRowIndex4D` back out of the closed
   product, requiring it to equal the array it was written from — closing OI-129's *"hashes the
   intent, not the artifact"*; the existing in-memory field is **retained** so no consumer breaks.
   **Unfiled and worse: `project_cov_nd.py` wrote no row-index array at all**, so its rows could not
   be bound to physical bins — disqualifying for M1. It now writes `hRowIndex`, records seven
   digests including the output file and a read-back row index, and emits a receipt naming the
   weight basis, the destination-mask basis and the paired central estimate. **First tests for
   either projector: 7, passing, and mutation-verified** — deleting the readback check fails two of
   them. `n_empty` is recorded and warned but deliberately **not gated**, because declaring it a
   pass condition is a criterion change and belongs to the criteria owner and Joseph.
   ⚠ **Scope narrowed by evidence:** `docs/orchestration/state/RECEIPT-20260816-hrowindex4d-readback.json`
   (lane B, PASS, predeclared, 4825 labels exact, independent derivation using neither `p4_lib` nor
   any bin width) already performed this readback **once, by hand, for the existing products**. So
   the property holds for what exists; the code makes it automatic for what comes next. Owning
   re-verification still belongs to the standard-P4 lane.
2. ~~**M-H, fingerprint writers.**~~ **DONE.** `combine_cov_nd.py` wrote one `TH2D` and closed —
   measured at `:23-26` — so `ESTIMATOR_REGISTRY.md:17-22`'s reject-on-mismatch rule was
   **unexecutable** against the scalar stat and ML components: five of nine fields were *absent*,
   not mismatched, and a rule cannot run without operands. It now records all nine, writes them
   **into the product** as well as a sidecar, and adds the **ensemble-count scalar** the audit
   records as missing (*"the writer still stores no ensemble-count scalar"*), the `N−1` divisor
   convention, a row index, per-replica digests and the member id list.
   ⚠ **The load-bearing design choice:** an unsupplied field is recorded as the literal
   `UNDECLARED`, **not omitted**. A missing key reads as *"not checked"*; an explicit `UNDECLARED`
   reads as *"the writer was never told"* — the same distinction the campaign draws between a
   non-check and a failed check, and a test asserts the key is present *and* carries the sentinel.
   Five of eight are `UNDECLARED` by default with a loud warning naming them.
   **6 tests, passing.**
3. ~~**Narrowing the packet's universal claims**~~ **DONE** — packet §13.
4. **Regression state, measured 2026-09-18:** 207 existing unittest tests across the four suites
   touching the changed files pass (`test_p4_guard_mutations` 61, `test_p4_repair` 129, and both
   OI-136 ratchets), plus 5 pytest tests and the 13 new ones. ⚠ Recorded because it nearly went the
   other way: `test_cml_family_completeness_fails_closed.py` is a **pytest** file, so running it as
   `python3 <file>` executed **zero** tests and exited **0**. A green exit from the wrong runner is
   not a pass. Both new suites are pytest-discoverable.
4. ~~**Rank-6 consumer contract draft.**~~ **DRAFTED.** Eight declarations, six measured consumer
   defects, and one finding that changes what the contract must contain: **the claim's region is
   half prespecified and half data-selected.** "Open question 6" is recorded 2026-06-03, before the
   W axis existed; `W >= 1.8` first appears in code 2026-06-09, two days after the first
   `(E_avail,W)` excess test, and the design document says the W axis *"localizes"* the question to
   that corner. So a *localization* claim is honest at central-value level, but a **significance on
   the boundary the data chose** needs selection-aware treatment. **This raises D5** — a claim-scope
   judgment, recommending option (b): quote on the prespecified `E_avail` region and keep the W
   localization at central-value level, which requires no new methodology and is close to what the
   paper already says.
5. ~~**M-P baseline.**~~ **MEASURED, and it is green — this requirement is not a hidden blocker.**
   A forced rebuild of all three deliverables returns `RESULT :: PASS` (note 94pp, primer 5pp,
   paper 3pp) with the retracted-value containment check clean at *"0 of 10 struck literals"* on
   both paper and primer. The standalone `MINERvA-OmniFold-Analysis-Note` checkout is on `main` at
   `3c3e9f2`, clean, level with origin, and **all 26 `.tex`/`.bib` sources are byte-identical** to
   this repository's. The PDFs are gitignored, so rebuilding does not dirty the tree.
   ⚠ **The build script proves it did the work, and that matters here:** it forces `latexmk -g` and
   requires every PDF to be strictly newer than a marker stamped before the run, because this script
   once exited 0 and passed its containment check while `latexmk` said *"Nothing to do"* for all
   three targets and validated month-old PDFs. Independently confirmed: all three files are dated
   within a minute of the run. **What this baseline does NOT establish** is that the built content
   is scientifically current — only that the sources compile and are synchronized. Re-verification
   is owed after any M-N content edit.

6. **The diagnostic path and the determinism probe.** Both authorized by Joseph 2026-09-18 and
   both complete as code: `run_m1_diagnostic.sh` (nine refusals, R5 admission *called* not
   restated), `z_determinism_probe.py` + `run_determinism_probe.sh`, and `lib_r5_admission.sh` as
   the single implementation of the accounting block. **69 tests across four suites, five mutations
   verified.** ⚠ The first probe submission FAILED in 4 s reporting *"R5 admission failed"* when it
   had not failed admission at all — the admission check ran before the environment, so `python3`
   was the node default 3.6.15 which cannot parse the meter. Four defects were found and fixed from
   that one failure, the worst being that **the gate could not distinguish "I could not look" from
   "I looked and refused"**. Resubmitted once under the corrective-resubmission grant, after a
   verified repair and fresh admission.

**Compute spent by this plan: `0.0011` + `0.25` CPU task-h reservation**, both inside the standing
12-hour pre-authorization and Joseph's 2026-09-18 bounded-diagnostic grant, both accounted before
submission. Standing boundaries hold: any single job under 12 h is
pre-authorized, but nothing here launches one; the no-automatic-retry rule and R5 accounting are
untouched; new compute will arrive as a bounded, priced request naming what a terminal result cannot
authorize, per `AGENTS.md`'s next-action discipline.

---

## 4. The M1 compute request, prepared and priced — NOT requested here

Per the instruction to prepare concrete bounded requests **before** seeking approval. **This is not a
request.** It cannot be made until M-M (adoption) is reached, and nothing below is submitted.

**What it measures.** `C_low = M1 C_Z M1ᵀ` on the adopted trunk: one `5D → (E_avail, W)` projection,
42 dense destination cells, with `M1 x_5D` as the paired central estimate.

**What a terminal result would NOT authorize** — stated in advance per `AGENTS.md`'s next-action
discipline: it would not calibrate a significance, would not supply support `C_Z` never had, would
not make an independently unfolded 2D estimator the marginal of the 5D one, and would not license any
other projection or an event-level fit.

**Sizing, derived from measured anchors rather than estimated.** The pilot's own numbers are the
anchor, and its recorded lesson is that *"any future sizing starts from 49.73 GiB"* because its
prediction was low by more than an order of magnitude.

| Quantity | Value | Basis |
|---|---|---|
| Peak memory (predicted, superseded by the measured row below) | **~3 GiB**, request **16 G** | `C_Z` as doubles is `10694² × 8 = 914.8 MB`; ROOT's `TH2D` with over/underflow is `10696² × 8 = 915.1 MB`; allow one copy during read. Against the pilot's measured **49.73 GiB**, this is a far smaller object than the assembly. |
| Compute | **MEASURED 0.324 s** | Run at the real shape, `10694 → 42`, 2026-09-18: `build_projection` **0.001 s**, `M C Mᵀ` **0.324 s**. The prior derivation from the pilot's measured `eigvalsh` predicted ~0.3 s and was right. |
| Peak RSS | **MEASURED 1.020 GiB** | Same run, whole process, with `C` at **0.852 GiB** of it. Synthetic `C` of the production shape; no payload. |
| Dominant cost | **ROOT I/O** of a ~900 MB histogram, not arithmetic | — |
| Wall request | **15 min** | The pilot used `ElapsedRaw 1037 s` for 45-band assembly **plus two** eigendecompositions; M1 is one read, one small matmul, one 42×42 write. |
| Shape | 1 node, `--qos=shared --constraint=cpu --ntasks=1 --cpus-per-task=8 --mem=16G --time=00:15:00` | Matches arm 7's partition; no exclusive node needed |
| Reservation bound | **0.25 CPU task-h** (1 task × 0.25 h) | **CORRECTED 2026-09-18.** The governing unit is task-hours = `ElapsedRaw` summed over the arm's tasks, and the ruling excludes `AllocCPUS` weighting **by name** — `DECISION-20260901-joseph-delegated-ceiling-unit-is-task-hours.md`. The former `2.0` was `cpus-per-task × wall`, i.e. **core-hours wearing the task-hour label: an 8× overstatement, committed after that ruling landed.** A reservation is still the enforced cap and not a completion |

⚠ **What is measured and what is not.** The **arithmetic** is now measured, not derived: `0.324 s`
and `1.020 GiB`. **The ROOT I/O of a ~900 MB `TH2D` is NOT measured** — no interpreter available here
has ROOT — and it is the dominant unknown. The `16 G` and `15 min` margins exist for that unmeasured
leg, not for the arithmetic, which uses 6% of the memory request and 0.04% of the wall. Stated this
way because the pilot's recorded lesson is that a *derived* sizing was low by more than an order of
magnitude; this one is derived only where it could not be measured.

**Against accounting — BOTH FIGURES IN THE SUPERSEDED SENTENCE WERE WRONG, and they were wrong
on different sides.** It read *"the campaign drew ~77.0 of 393.5 authorized CPU task-hours"*. The
numerator came from the seven-arm production round, which is **pre-`t0`** and therefore outside the
R5 ledger entirely; the denominator, `393.5`, appears in no governing record. This is the
asymmetric-comparison failure: two numbers, neither the same population, neither carrying its unit.

**Measured 2026-09-18 by the instrument, on the cluster** (`r5_meter.py measure`, `login16`):

| | measured | ceiling | headroom |
|---|---:|---:|---:|
| CPU task-hours | **96.3214** | 500 | **403.6786** |
| GPU task-hours | **16.0117** | 500 | **483.9883** |

130 tasks, 2,013 attempts, `by_state {COMPLETED 104, FAILED 25, NODE_FAIL 2, REQUEUED 1882}`; stop
date `2026-09-30`, not fired. `t0 = 2026-09-02T13:44:27Z`. Independently reproduced: an ad-hoc
`sacct` dump fed through `--from-file` gave `96.32138888888889` against the meter's own on-cluster
query, agreeing to every digit.

⚠ **Outstanding reservations: ZERO, and that is a measurement rather than an assumption.** `squeue
-u josephrb` returned no rows — with the positive control that the same user string returns 2,015
`sacct` rows, because an empty `squeue` and an unresolvable user look identical at rc 0.

⚠ **A method note on my own replication, NOT on the ledger.** My first ad-hoc query passed a naive
`--starttime` and lost 62 attempts (`0.486` task-h) to `TZ=PDT` parsing a UTC `t0`. **The meter is
not affected**: it sets `TZ=UTC` in the sacct environment and has since `a0bde16a`, 2026-09-03,
before the receipt I was comparing against. The instrument was already right and my hand query was
the defective one.

**Retry rule, REPLACED 2026-09-18 by Joseph's grant:** one corrective resubmission per stage after a
diagnosed execution defect, a verified repair, and **fresh admission**. Automatic requeue stays
disabled; an ambiguous submission must be reconciled before another is made; **a scientific failure
is evidence to assess, not permission to repeat until it passes**, and does not consume the
resubmission. Implemented in `lib_r5_admission.sh::r5_retry_notice`, printed on every failure path.

**Preconditions, all of which must hold before this is submitted:**
1. **M-M** — the trunk is explicitly adopted. Yours.
2. **M-G** — done; the projector now writes a row index, digests its output, and reads the row index
   back. It must land *before* production, not after, since a retrofitted digest records only that a
   file has not changed since the retrofit.
3. The **destination mask** is declared prospectively — `project_cov_nd.py` offers two and on 42 bins
   they can differ materially.
4. **D5** — the region is named, since the product is only useful for a claim whose region is fixed.

**THE RUNNER IS WRITTEN AND CANNOT EXECUTE — `nd-unfolding/run_m1_projection.sh`.** Every
precondition is a **refusal with its own exit code**, not a warning, because a runner that warned
would be one careless invocation away from producing a product nobody authorized:

    rc 3   no adoption record, OR a record that does not state an adoption
    rc 4   the projector lacks proj_sha256 / hRowIndex / the readback digest
    rc 5   the destination mask is not declared as one of the two admissible choices
    rc 6   the product exists but its receipt does not

Adoption is checked as a **record that says it adopts**, not an environment flag — a boolean would
let anyone assert it. **9 tests** at `tests/test_run_m1_projection_refusals.py`: every mandatory
operand refuses **by name** when unset, each refusal has a control that trips it, and a **positive
control** proves none fires on valid input. ⚠ Two method notes are on the test's face because both
came from mistakes made writing it: `bash -n` is necessary and not sufficient, since a *balanced*
apostrophe pair parses cleanly while merging the assignments between it; and **my first harness was
invalid while looking correct** — all four refusal controls returned nonzero but died at an unset
operand *before reaching the guard under test*, which is the mutation-refused-before-reaching-the-
guard shape, and is why each refusal now carries a distinct code and the tests assert on the code and
the message rather than on nonzero.

**Verification the run must produce, and it is already implemented rather than promised:** output
file digest, input covariance and CV digests, `M` content digest, row index **read back out of the
closed file** and required equal, both support censuses (`src_cells_dropped` and `n_empty`), and the
`CANDIDATE` status marker. Independent re-verification remains `[cb0b6b]`'s.


---

## 5. Cause 6 — its specification is largely discharged by P1 and M-G

Recorded here rather than as a new document, because the audit's own framing for cause 6 is *"the
unresolved object is the corrected projection product plus the component-footing decision"*, and two
of its three parts have since been done under other milestones.

| Audit's requirement for cause 6 | State |
|---|---|
| *"Specify the operator"* | **DONE** — P1, packet §4: the four maps with bin-width basis, masks, C-order enforcement and orphan policy, plus the paired central estimate |
| *"and both coverage populations"* | **DONE and now instrumented** — `src_cells_dropped` (source cells whose destination is unreported) and `n_empty` (destination rows receiving no source cell). Both were already computed; M-G makes them **recorded in the receipt**, and `n_empty` additionally warns |
| *"decide stat/ML reuse from compatibility evidence rather than assume reruns"* | **OPEN** — this is a decision, and its evidence is `[cb0b6b]`'s component-footing work. Note the audit's wording: *rather than assume reruns*. The default assumption is the expensive one |
| *"produce the exact projection and the same-input legacy-versus-correct counterfactual"* | **BLOCKED on authorization**, and it is a *second* product beyond M1 — the counterfactual needs the legacy operator run on identical inputs |
| *"The scope of operator versus ensemble grading must be explicit"* | **OPEN** — a statement, not a measurement |

`SPEC` §2.6 withdrew the claim that the bidirectional coverage guards were missing, and P1 confirmed
they exist and are genuinely bidirectional. **So cause 6 is not a code gap; it is one decision (stat/ML
reuse) plus one authorized product (the counterfactual) plus one scope statement.**

⚠ **The counterfactual is worth pricing separately when it is requested** — it is not covered by M1's
request in §4, because it runs a *different* operator over the same inputs and therefore doubles the
read, and because the audit asks for it on *identical footing*, which is a constraint on how it is
launched rather than on what it computes.


---

## 6. EVERY open decision, consolidated — the single list

Independent work is at its boundary. Nothing below can be resolved by a lane; each is reserved to
Joseph by the goal, by `AGENTS.md`'s "Decisions reserved for Joseph", or by `SPEC`.

| # | Decision | Kind | Recommendation | Unblocks |
|---|---|---|---|---|
| **D1** | Grid versus diagonal member family | scientific (scope) | **Diagonal**, `(42,1000)` fixed, architecture axis declared as a scope limit | cause 3 member design |
| **D2** | The L4 boundary key | engineering to create, scientific to value | **Create** the fifth `Z_BOUNDARIES` key, withheld; criterion = boolean **+ margin** | cause 2/L4 composition |
| **D3** | `τ`'s scientific input | scientific (convention) | Declare **the significance threshold at which the claim is asserted** | `τ`, computable from M1 |
| **D4** | Registry reject-on-mismatch rule | criterion amendment | **Amend** the estimator-seed field to within-family identity + declared map | M-I |
| **D5** | The claim's region is half data-selected | scientific (claim scope) | **(b)** quote on the prespecified `E_avail` region; keep the W localization at central-value level | M-O, and what M1 is for |
| **R1** | Cause 7 sufficiency | ruling (`SPEC`) | **CLOSE AS SUFFICIENT.** The four weight-only bands are **measured present in `R`** on the 41.44 GB support family; the premise that they are uncovered is refuted (§10.1) | cause 7 |
| **R2** | Cause 5 §6.1 disposition | ruling (`SPEC`) | **CLOSE AS NOT-FALSIFIED, scoped to the 15 modules actually traced** — not universally (§10.2) | cause 5 |
| **R3** | The cause-4 guard's condition number | spec owner | **AMEND `:1237` to "condition 3".** ⚠ I over-called this a self-contradiction; on re-reading §2.4 in full it is a **mislabelled digit in a receipt-row summary**, and the same guard discharges condition 4's concern (§10.3) | cause 4 implementation |
| **R4** | Cause 6's stat/ML reuse | scientific | **REUSE**, conditional on one named zero-compute footing check that `combine_cov_nd.py` now makes executable (§10.4) | cause 6 |
| **R5** | Lineage: two distinct unified-throw ensembles; the registry names a file the chain did not consume | ruling | **DECLARE the 2026-09-14 precursor as Z's governing ensemble; read the stamps before recomputing anything; amend the registry row** (§10.5) | M-J |
| **M-M** | **Trunk adoption** | scientific | — | M1, and everything downstream |
| **M-L** | The §6.4 null route | ruling | every route to `ε` named in the contract is closed; a repeat cannot produce it | the null leg |

**Two further items are decisions in substance though they read as criteria work:** the cause-2
wording (*"inherits a tolerance with a stated derivation and an owner"*, **not** *"not chosen"* —
`k = 2.0` is chosen and `uq_math.py:129-137` says so in capitals), and the `n_empty` reading
(`SPEC:1239` requires the `(E_avail,W)` projector to **count-and-report** and names fail-closed as a
**falsifier**, so an acceptance criterion may require the reported count to be zero but the projector
must not gate).

**What is NOT waiting on anything:** M-A…M-E, M-G, M-H, M-P's baseline, cause 5 and cause 7 evidence,
cause 6's operator and censuses, M-O's draft, and M1's priced request. Those are done.


---

## 7. The replacement consumer is written — `nd-unfolding/rank6_significance.py`

The contract says the consumer is **new code, not a patch**, because `AGENTS.md:30` quarantines the
existing `(E_avail,W)` covariance outright and `:27` requires projection from the adopted trunk, so
re-pointing an input would leave every inference assumption unresolved. Its structure is fixed by the
contract regardless of which values **D3** and **D5** supply, which is why those two are **required
inputs rather than values baked in.**

**Five declarations enforced as refusals, each with its own exit code:**

    rc 3   --rcond absent or out of range. Both existing consumers call pinv with NO explicit
           rcond, and one already comments the matrix "can be near-singular -> pinv amplifies
           shape directions". There is no default here.
    rc 4   ndf would be the bin count. The existing header reads literally chi2/ndf(all7). The
           retained RANK is reported as the ndf input, with the distinction stated: a rank is a
           property of the matrix, a calibrated ndf a property of the null distribution. No
           generic Hartlap factor, and rank alone is not called calibrated.
    rc 5   the region is not fully prespecified and no selection-aware calibration is declared --
           D5 ENFORCED IN CODE, and liftable by declaring one, so it is a criterion and not a
           prohibition.
    rc 6   no claim threshold, since deriving it afterwards from the computed number would be a
           threshold placed to obtain a verdict.
    rc 7   the central estimate and the covariance come from different products. The pairing is
           M1 x_5D, not an independently unfolded 2D estimator.

**The CLI payload path is deliberately not wired** and refuses with `rc 2` saying so: the trunk is not
adopted, M1 does not exist, and the contract is a draft. The declaration checks are live and the core
is importable and tested.

**19 tests**, with a positive control proving no refusal fires on a fully declared call. **Both
load-bearing guards are mutation-verified:** making ndf the bin count fails the ndf test, and letting
`rcond` silently default fails the refusal test. ⚠ Two fixture lessons are recorded on the tests
themselves, because both were mistakes: a `+ eps*I` ridge would make the covariance full rank and
**destroy the rank deficiency the tests exist to exercise** — `C_Z` has 5,214 negative eigenvalues of
10,694, so full rank is the wrong regime to fixture; and the truncation scan needs a **graded**
spectrum, because an exactly rank-deficient matrix yields a *constant* retained rank across every
plausible `rcond` and the scan would demonstrate nothing. My first attempt at the second mutation was
also invalid — it broke class definition, so it errored at collection rather than failing a test,
which is the mutation-refused-before-reaching-the-guard shape a third time in this session.


---

## 8. M-P's containment gate — I went looking for a gap and there is none

I suspected the retracted-value containment check covered only the paper and primer, because those
are the two lines the build printed. **It covers all three, and the note's coverage is the part that
makes it sound.** Measured by running `check_dead_containment.py` directly:

    ok  note:   18 \dead{} uses across app_statmethods.tex
    ok  paper:  clean, 0 \dead{} in a 3-file closure
    ok  primer: clean, 0 \dead{} in a 4-file closure
    ok  note.pdf carries 10/10 struck literals   (POSITIVE CONTROL OK)
    ok  paper.pdf:  0 of 10 struck literals
    ok  primer.pdf: 0 of 10 struck literals
    SELF-TEST :: PASS      11 positive cases, 4 negative controls
    RESULT :: PASS

**The design is the right one and states why in its own source** (`:23-26`): retracted values must
reach the **note** build only — it is the archival document that records them *as retracted* — while
the paper and primer must carry none. So the note is not exempt; it is the **positive control**,
because *"a test that only asserted absence would pass if `\dead{}` vanished from the repo entirely,
or if the note quietly stopped marking its retractions."* And the regex is power-tested **before** its
verdict is trusted, including against a demonstrated evasion.

**Two coverage limits the checker discloses about itself**, both of which I would otherwise have had
to find:
- *"`GATED_NW_MACROS` is EMPTY — the gated-macro check is **inert by declaration, not passing on
  evidence**."* An empty-population check that refuses to report itself green.
- *"the PDF stage does **NOT** cover 2 `\dead{}` bodies — no decimal literal, or none with ≥3
  significant digits, so **only the source check guards these**: `0.069`, `≈70%`."* Named, with the
  reason: under three significant figures a literal is indistinguishable from an axis tick in a
  rendered PDF.

**So M-P is in better shape than I characterised it.** I had written that the note's content *"cannot
be re-verified"*; the accurate statement is narrower: **content cannot be checked against dispositions
not yet made, but the retracted-value containment is verified, green, power-tested and covers all
three documents.** After adoption, M-P is re-running a working gate over changed content — not a
verification built from nothing.


---

## 9. The completion clause, component by component

Joseph's clause has five components. **Two are now satisfied as far as they can be without
adoption; three cannot be reached without it.**

| Component | State |
|---|---|
| an explicitly adopted scalar-5D covariance | **RESERVED TO JOSEPH.** Reserved three times over — by this goal's text, by `AGENTS.md`'s "Decisions reserved for Joseph", and by `SPEC` |
| **…with a supported reproduction path** | ✅ **DONE, M-Q.** It had **no document at all** until `88b11b7c`; a covering search found the repository's seven `reproduc*` files all PET-scoped or generic |
| the required exact projections, correctly paired centrals, verified output records | **CODE COMPLETE; the PUBLICATION product still blocked at adoption, the DIAGNOSTIC one now authorized and runnable (§11).** Projector instrumented and tested; runner written with preconditions as refusals so it *cannot* run unadopted; request priced with its arithmetic leg measured. The verification is **implemented rather than promised** — output digest, `M` digest, row index read back out of the closed file and required equal, both support censuses |
| scientific claims supported at their stated level | **CONSUMER WRITTEN, TWO INPUTS OPEN.** `rank6_significance.py` enforces five declarations as refusals, takes ndf from the **retained rank**, and has **D5 enforced in code**. D3 and D5 supply the two values |
| synchronized, successfully built note, primer and paper | ✅ **GREEN.** `RESULT :: PASS`; all 26 `.tex`/`.bib` byte-identical to the standalone, level with origin; retracted-value containment verified across **all three** documents with the note as positive control, self-test PASS on 11 positive and 4 negative cases |

**So the honest statement of where this stands:** every component that does not require an adoption
decision is complete, and the three that do are blocked at the same single gate. Nothing further can
move without a ruling.


---

## 10. The five rulings, each with a recommendation — added 2026-09-18

Joseph, 2026-09-18: *"For scientific decisions, finish the evidence review and give me a recommended
ruling, alternatives, and consequences. **Do not stop at 'evidence complete, disposition owed'**, or
ask me to invent a technical criterion without a justified recommendation."* Every row of §6 that
read *"none offered"* is replaced below. Two of the five turned out to be answerable by measurement
rather than by judgement, and one of those refutes a premise I had carried.

### 10.1 R1 — cause 7 sufficiency · **RECOMMEND: CLOSE AS SUFFICIENT**

**The question assumed something false, and measuring it settles the ruling.** R1 asked whether
covering five lateral bands is enough *"given the four vertical bands' CV-selected support"* — the
four being `MinosEfficiency`, `GEANT_Neutron`, `GEANT_Pion`, `GEANT_Proton`, which
`eavailW_covariance.py:40` carries in its nine-band historical set and `z_contract.py:67`'s
five-band lateral set does not. The implied worry is that Z's detector systematic is **smaller** than
the historical one, which is the direction that matters for publication.

**Measured on the actual support family** — `uq_universe_5d_covariance_combined_bkgaware.root`,
41,436,632,945 bytes, the `41.44` GB object `SPEC` §5.8c names, keys read directly:

| | count |
|---|---:|
| `hCov_universe5d_*` bands | **45** |
| `V` present, of `adopt_unified_5d.VERT_BANDS` | **13 of 13** |
| `A` present, of `p4_lib.BANDS` | **5 of 5** |
| `R`, the derived remainder | **27** |

    MinosEfficiency    PRESENT          GEANT_Pion         PRESENT
    GEANT_Neutron      PRESENT          GEANT_Proton       PRESENT

**All four are present, in `R`.** They are not excluded from `C_Z`; they are in a **different part of
the partition**, entering through `Σ_R` uninflated. The question conflated two mechanisms: a
weight-only band **cannot** enter a lateral *swap* by construction — `pet_lateral_band_5d.py:41`
names exactly these four as `WEIGHT_BANDS` and `pet_lateral_band.py:18` records that they are
*"weight-only bands: CV coordinates/gates"* — but coverage is what `R` supplies. Requiring them in
the lateral set would be requiring a test to cover something outside its own mechanism.

For completeness, `V` is 13 **interaction-model and flux** bands (`2p2h … Rvp2pi, Flux`), not
detector bands at all, so "the four vertical bands" in R1's phrasing does not correspond to `V`
either. `R`'s 27 are the GENIE/FSI/normalization remainder plus these four and `__Normalization_flat`.

**Alternatives.** (a) Close as sufficient — recommended. (b) Require the four in the lateral
inventory — **refuse**: it asks for a lateral swap of a weight-only band, which has no meaning.
(c) Hold cause 7 open pending a separate weight-band leg — unnecessary, since `Σ_R` *is* that leg and
it is measured populated.

**Consequence for the publication claim.** Closing R1 removes the last evidence gap on cause 7, and
cause 7 is the item that plausibly discharges `ESTIMATOR_REGISTRY.md:29`'s `#16` five-band coverage
**publication gate**. This is the most favourable open item in the package and it resolves upward.

⚠ **ONE HARDENING, FILED SEPARATELY AND NOT PART OF THIS RULING.** `R` is derived, never listed:
`z_contract.py:72`, `N_RESIDUAL = 45 − 13 − 5`. At the call site, `z_build.py:523-527` defines
`residual` as `set(inventory) − V − A`, so `check_band_partition`'s exhaustiveness leg —
`V ∪ R ∪ A == inventory`, checked in both directions — **is satisfied by construction at this call
site** and cannot disagree. The live constraints are `V`/`A` membership by name and `|R| == 27`. A
count is not an inventory, and the function's own docstring says so about a previous version of
itself. **So a substitution passes: one weight band absent and one unrelated band present keeps
`|R| = 27`.** The measurement above shows no substitution has occurred, so this is a hardening and
not a live defect. Recommended change: import an explicit `Z_R_BANDS` from the module that owns the
support family and check `R` by name, as `V` and `A` already are. It is a criterion strengthening,
so it is yours, and it could make the gate fail on a future product that today passes.

### 10.2 R2 — cause 5 §6.1 disposition · **RECOMMEND: CLOSE AS NOT-FALSIFIED, AT THE TRACED SCOPE**

**Recommendation.** Record cause 5 as `INAPPLICABLE — disposed by decision` under §6.1, with the
disposition's scope stated as **the 15 modules Z invokes that were actually traced**, including
`adopt_unified_5d.py` — the module `SPEC:1238` singles out because `VL66` did not audit it and `D_Z`
runs through it. The falsifier came back **NEGATIVE** across that closure.

**Why the scope clause is not a hedge but the substance of the ruling.** A negative falsifier closes
a cause **at the population it was evaluated over**, and nothing further. `SPEC:1238`'s own falsifier
list names *"the trace is inherited from `VL66`"* and *"a module Z introduces is unaudited"* as the
two ways this closes wrongly, so a disposition that did not state which modules were traced would be
unfalsifiable in exactly the way the spec anticipates. Recording "15 modules, named" makes a future
16th module a visible gap rather than a silent one.

**Alternatives.** (a) Close at the traced scope — recommended. (b) Close unconditionally — asserts a
universal from a finite closure and is the over-claim §6.1's falsifier list exists to catch.
(c) Keep open — there is no evidence left to gather; only the disposition is missing, which is what
Joseph's instruction identifies as the wrong place to stop.

**Consequence.** No publication claim moves. Cause 5 stops being a blocker on adoption.

### 10.3 R3 — the cause-4 guard's condition number · **RECOMMEND: AMEND `:1237`, AND NARROW MY OWN CLAIM**

⚠ **I over-called this. Correcting it, because it would otherwise reach you as a live contradiction
in the governing document.** I filed it as *"`SPEC` contradicts itself"*. On reading §2.4's four
conditions in full rather than the two citing lines, it is **a mislabelled digit in a receipt-row
summary**, and the two sites describe one guard.

§2.4's conditions are: (1) the re-added print computes the same quantity; (2) its operands are the
new build's own; (3) **adding it does not change the covariance content**; (4) **the print is
print-only, never subtracted** — and item 4's own text then says *"**Condition 3** must be enforced
by a guard that fails if the computed value ever reaches the stored covariance, not by a one-time
comparison."* So §2.4 assigns the guard to condition **3**, in the prose of item 4. `:1237`'s
receipt row says *"condition 4 enforced by a guard"*.

**Recommendation.** Amend `:1237` to read **condition 3**, and add one clause recording that the same
guard discharges condition 4's concern — because a value proved never to reach the stored covariance
**cannot have been subtracted from it**, and subtraction from the stored covariance is what cause 4
is about. `:1010-1011` governs: it is the definitional site, and `:1237` is a summary of it.

**Alternatives.** (a) Amend the row — recommended. (b) Amend the definitional site to say condition 4
— wrong direction; the guard's described behaviour *is* condition 3. (c) Leave both — leaves a
reader unable to tell which condition an implementation must satisfy, and implementations get
reviewed against the number they were given.

**Consequence.** None for any published number. This is a specification-hygiene amendment, and the
reason to make it is that the cause-4 implementation will be reviewed against whichever number the
reviewer reads.

### 10.4 R4 — cause 6's stat/ML reuse · **RECOMMEND: REUSE, on one named zero-compute check**

**Recommendation.** Reuse the existing `C_stat` and `C_ML` components, conditional on a **footing
check that costs no allocation**: every component of `C_Z` must carry the same central-product and
support footing as the trunk, read from the fingerprint fields rather than assumed.

**Why reuse is the right default here, and why it is not the lazy answer.** The audit's wording is
*"decide stat/ML reuse from compatibility evidence **rather than assume reruns**"* — the default it
warns against is the **expensive** one. Regenerating replicas with no rationale is named as a
falsifier at `SPEC:1239` (*"replicas regenerated with no rationale"*). So a rerun needs a positive
reason, and none has been produced.

**The check is now executable, which it was not when the audit was written.** `combine_cov_nd.py`
wrote one `TH2D` and closed — 27 lines, measured — so five of the nine fingerprint fields
`ESTIMATOR_REGISTRY.md:17-22` requires were **absent rather than mismatched**, and a reject-on-mismatch
rule cannot run without operands. It now records all nine plus the realized ensemble count, the
`N−1` divisor convention, a row index and per-replica digests. **So the compatibility evidence the
audit asks for can be read off the products instead of being argued.**

**Alternatives.** (a) Reuse on the footing check — recommended. (b) Rerun both components — costs a
production campaign leg and is the assumption the audit names. (c) Reuse without the check — leaves
the registry rule unexecuted, which is what the audit found in the first place.

**Consequence for the publication claim.** `C_stat` and `C_ML` are additive terms in
`C_Z = D(ΣV)D + ΣR + ΣA + C_stat + C_ML`. If they are footed on a different central product, the sum
is not a covariance of one estimator and the quoted uncertainty is not attributable. The check is
what establishes attributability; reuse without it is the risk, not reuse itself.

⚠ **NOT COVERED BY THIS RECOMMENDATION:** the 7.11% figure is the **PET** `C_stat`
(`VL132`/`CSTAT-R7`, 50 members), a different object from the scalar-5D one, and I once over-scoped
it to this subject. The scalar-5D surviving defect is the separate one that `--array=1-100%32` is a
**declared bracket**, so the realized member count must be read rather than inferred from the array
specification — which is why the writer now records the **realized** `n_members`.

### 10.5 R5 — the two unified-throw ensembles · **RECOMMEND: DECLARE, READ THE STAMPS, AMEND THE REGISTRY**

**The finding, restated:** the chain carries two distinct unified-throw ensembles — the parent,
mean-centered, `uthrow_source` **2026-08-06**, and the pilot's throw input, the **2026-09-14**
precursor — corroborated by the parent's upstream null being G's `5.8223e-50` against the
precursor's `1.4302e-50`. Separately, `ESTIMATOR_REGISTRY:29` names `..._UTHROW.root` while the chain
consumed the **unsuffixed** file, with registry `√tr = 5.8077e-38` against the parent's
`sqrt_tr_new = 5.2696e-38`.

**Recommendation, in three parts, and deliberately ordered cheapest-first.**

1. **Declare the 2026-09-14 precursor ensemble as Z's governing throw ensemble.** Z is a successor
   subject, not a continuation of G; two ensembles in one *repository* is expected, two in one
   *product* is the defect. Declaring which one governs is what makes the second readable as G's
   rather than as Z's contamination.
2. **Read the stamps before recomputing anything.** Require every component of `C_Z` to carry the
   governing ensemble's `uthrow_source`. If they agree, **the chain is single-footed and the whole
   finding reduces to a registry documentation defect** — no recomputation, no compute request. If a
   component disagrees, quarantine **that component**, not the product. This ordering matters
   because the expensive branch has been assumed twice in this campaign and measured neither time.
3. **Amend `ESTIMATOR_REGISTRY:29` to name the file actually consumed**, recording **both** `√tr`
   values with the reason they differ. A registry row that names a file the chain did not consume
   makes every downstream fingerprint check compare against the wrong object, and it errs silently.

**Alternatives.** (a) The three steps above — recommended. (b) Regenerate the throw ensemble so one
lineage exists — a production leg, unpriced, and step 2 may show it buys nothing. (c) Treat the two
as interchangeable — refuse: the nulls differ by a factor of 4, so they are not one ensemble
described twice.

**Consequence.** Step 2's outcome decides whether R5 is a documentation repair or a component
quarantine. **It is not a recomputation requirement until step 2 says so**, and the audit's
*"rather than assume reruns"* applies here as much as to cause 6.


---

## 11. The adoption/projection dependency, reconciled — added 2026-09-18

Joseph directed: *"Correct the task-hour pricing and **reconcile the adoption/projection dependency**
before execution."* The pricing is §4. This is the dependency.

**IT WAS A CYCLE, and I had recorded both halves without noticing they closed.**

| the half I recorded | where |
|---|---|
| M1 must not be produced before the trunk is adopted | §4 precondition 1; `run_m1_projection.sh` rc 3 |
| `τ` is *"whatever projected-correlation movement leaves the corner significance above N — a calculation performed once **on M1**"* | §2, D3 |
| `τ` is one of the three decisions blocking cause 3, and cause 3 blocks adoption | §1, M-F |

So adoption required `τ`, `τ` required M1, and M1 required adoption. **A plan containing that cycle
cannot be executed by anyone**, and it would have read as "blocked on Joseph" indefinitely while the
block was structural and mine.

**What cuts it, and in which direction.** Your grant of *"provisional projections and
counterfactuals from the preserved candidate covariance when needed to resolve acceptance
questions"*. The projection is produced **as evidence for** the adoption decision, and is barred by
construction from being the product that decision licenses. That is the only direction that cuts the
cycle without weakening anything: the alternative — relaxing the adoption precondition on the
publication path — would have waived the guard that the whole quarantine rests on.

**Implemented as a distinct path, not a flag.** `nd-unfolding/run_m1_diagnostic.sh`.
`run_m1_projection.sh`'s rc-3 adoption refusal is **untouched**, and a ratchet test in the new suite
re-measures it rather than assuming it survived — adding a diagnostic path is precisely how a
publication guard gets waived in practice.

**Every clause of the grant is a refusal, because a documented condition is not a condition:**

    rc 3   no named acceptance question, or no stated decision value
    rc 4   the projector lacks proj_sha256 / hRowIndex / the readback digest / runClass
    rc 5   the destination mask is not one of the two declared choices
    rc 6   the output path lacks DIAGNOSTIC, or points into a product tree
    rc 7   the output already exists -- no silent overwrite of the run it replaces
    rc 8   the declared reservation is not the enforced cap
    rc 9   the R5 receipt is missing or stale, or admission is refused
    rc 11  the interpreter cannot import the subject
    rc 10  the product exists but its receipt does not

**The label travels inside the product.** `project_cov_nd.py`'s `status` field was a **constant** —
every product it ever wrote said `CANDIDATE`, whatever it was — so nothing in the product or the
receipt could distinguish a diagnostic from a publication-path product, and the separation your grant
requires would have rested on the output path alone. It now writes `runClass`, `runClassStatus` and
`acceptanceQuestion` as objects **in the ROOT file**, so a rename or a lost sidecar does not launder
a diagnostic product. There are three real classes, not two: `candidate` is what the old constant
*meant*, and `sbatch_project_5d_to_4d_candidate_gpu.sh` — *"DRY-RUN … → candidate path"*, its own
words — now declares it, so its recorded class is unchanged.

**What the diagnostic M1 will and will not establish.** It computes `C_low = M1 C_Z M1ᵀ` on the
**preserved candidate** trunk, which makes `τ` computable and therefore unblocks cause 3's third
input. It does **not** adopt the trunk, does not calibrate a significance, does not supply support
`C_Z` never had, and **is not the quotable `(E_avail,W)` covariance** — `AGENTS.md:27` requires that
to be projected from the *adopted* trunk, and `:30` quarantines the existing one outright. So the
publication product still waits on M-M, and only the *acceptance question* has been unblocked.

⚠ **ONE HONEST RESIDUE.** `τ` computed on the candidate trunk is `τ` for **that** trunk. If adoption
lands on a materially different object — say after R5's step 2 quarantines a component — `τ` must be
recomputed on the adopted one. That is a cheap re-run of a 0.324 s matmul, not a new campaign, and it
is recorded here so that the diagnostic value is not later quoted as the adopted one.


---

## 12. ⚠ RETRACTED AND CORRECTED — the candidate covariance EXISTS, and my absence claim was defective

**This section previously asserted, under the heading "THE PRESERVED CANDIDATE COVARIANCE DOES NOT
EXIST AS AN OBJECT", that `C_Z` had never been written to disk, and proposed a `1.00` CPU task-h
rebuild. THE ASSERTION WAS FALSE AND THE REBUILD IS WITHDRAWN.** Joseph identified the products by
path. Retained below is what was actually established, what the error was, and the lesson, because
the lesson is the only durable part.

### 12.1 The products, verified directly

Job **`58454524`**, `2026-09-17T00:21:56 → 00:39:13`, `ElapsedRaw 1037 s`, `AllocCPUS 36`,
`nid004093`, `build_seconds 760.767`. Products in place at
`nd-unfolding/uq_5d/z_pilot_20260916_a5/`:

| product | bytes | sha256 re-measured from the file in place |
|---|---:|---|
| `z-cv.npz` | `890,500,272` | `3d7465f66fbe66b0dfcf09b6fc51249f227fb33e97ae40bc78dda90275e918c5` |
| `z-mean.npz` | `890,383,062` | `61b7a4939bd40459452e232d4a5cec3c0b19ad7a21715452f7bb3bc9e0c72dd2` |
| `z-null.npz` | `190,817` | `cb82fc3285c981b91625530d48c14ff5554db5154db298a3144a57520633d77e` |

**3 of 3 identical** to `zpilot-20260916/outcome-58454524/product-digests.txt`, measured off the
products rather than read out of a receipt. Plus `z-receipt-cv.json`, `z-receipt-mean.json`,
`z-pilot-receipt.json`, `bridge.json`, `z-manifest.json`, `z-provenance.json` — ten files.
`ND_OMNIFOLD_RUN_LOG.md` at `1b2873a8:160-188` records all of it, including the digests.

**Contents of `z-cv.npz`, measured:** `hCov_combined5d_total_uthrow` `(10694, 10694)` float64,
`hXSecND_flat` `(65856,)`, `hSupportMask` `(65856,)`, `hRowIndex5D` `(10694,)` int64,
`hInflation_g` `(10694,)` (min `1.0`, max `17.653`), `hPinnedMask`, and `metadata_json` carrying
`adoptable: false`, `scientific_acceptance: NON-PASSING`, `variant: cv`, `manifest_sha256` and
`code_identity.revision fb9ec356`.

**Self-consistent three ways:** `hRowIndex5D` == `nonzero(hXSecND_flat > 0)` ==
`nonzero(hSupportMask > 0)`, all `10,694`, strictly increasing. Relative asymmetry
`max|C−Cᵀ| / max|C| = 2.164e-16` — one ULP, the signature of summation order, not a defect.
The `mean` variant has identical keys and row index and a different trace (`2.7768e-75` against cv's
`3.2197e-75`), so the two are genuinely distinct objects.

### 12.2 What was wrong with my claim — three checks, one operand error, repeated

I called it "established three independent ways". The three shared a single defect and were
therefore one check, not three:

| my "confirmation" | the actual defect |
|---|---|
| the pilot's own receipt | I read attempt **`a3`**'s `bridge.json`. `a3` is the **failed** attempt. The successful run is **`a5`**, which I never opened |
| directory contents | I listed `a3`, `a2` and `rehearsal`. Never `a5` |
| a covering search "with a positive control" | scoped to **`*.root`**. The products are **`.npz`**. The 469-file positive control proved the search *ran*, not that it covered the right set |

**And the worst of the three:** `sacct` reports job `58454524` as `State FAILED`, which I treated as
proof of absence. Its `ExitCode` is **`2:0`**, and **2 is this CLI's completion code** — `z_build.py`
returns 1 for failed, 2 for completed-non-passing, 0 only for `--help`. I had **quoted the warning
against this earlier in the same session**, from `z_pilot.py`: *"A CALLER MUST NOT TREAT 2 AS PROOF
THE ARTIFACTS EXIST WITHOUT ALSO CHECKING THEM."* I read that line and committed its inverse —
treating a nonzero exit as proof they do not exist. `_write_product`'s `.npz` branch, which I also
read while tracing the writer, is what should have rescoped the search.

**ABSENT, INACCESSIBLE and UNSEARCHED are three states.** This was **unsearched**. A positive control
that proves the instrument works does nothing about the instrument pointing at the wrong set.

### 12.3 The resolution: an input path, no rebuild, no transcription

Per the instruction not to rebuild the scientific object merely to change its container, and to
prefer a verified input path: `project_cov_nd.py` now reads either container by the same key names
(`_read_vector` / `_read_matrix` / `_source_metadata`). **A transcription was rejected** — it would
write a second `890` MB copy whose only new property is a risk of differing from the first.

Three properties are preserved and checked rather than assumed:

- **Matrix contents** — read directly, no re-derivation.
- **Row order** — the producer's `hRowIndex5D` is **required equal** to the order derived from the CV
  mask, and a mismatch refuses. Two disagreeing statements of the row order cannot both bind the
  rows, and choosing one would be a guess. The receipt records which basis applied.
- **Metadata and source binding** — `src_metadata` carries the source's `adoptable`,
  `scientific_acceptance`, `variant`, `manifest_sha256` and `code_identity` into the projection's
  receipt, so the projection cannot be read without the standing of what it was projected from.

**And a new guard that the data enforces rather than the path:** a source recording
`adoptable: false` **refuses** `--run-class publication`. The candidate records exactly that, so
today only a diagnostic projection can be built from it — which is the separation the grant
requires, now independent of how the run is invoked. Mutation-verified, with both positive controls.

**M-R is therefore unblocked on its input.** The remaining operands are the destination-mask
declaration (mine, and recorded: `receiving-cells`, since the only frozen `(E_avail,W)` CV product is
the one `AGENTS.md:30` quarantines) and D5's region, which is yours.

## 13. The determinism probe: what it measured, and the green run that measured nothing

**Job `58506753` — FAILED, 4 s, `0.0011` CPU task-h.** It printed *"R5 admission failed for 0.25 CPU
task-h"* and **had not failed admission.** The admission check ran before `source
setup_salloc_env.sh`, so `python3` was the node default `3.6.15`, which cannot parse `r5_meter.py`
(`from __future__ import annotations`), and the `SyntaxError`'s nonzero exit was read as a refusal.
An *environment* fault reported as an *accounting* fault, in the words of an accounting fault.

Four defects came out of that one failure, and the ordering was only the first: the gate could not
distinguish **"I could not look"** from **"I looked and refused"** (both mapped to `rc 9`); a
missing environment script died at `rc 1`, indistinguishable from a payload failure; and the callers
**flattened the codes** with `|| exit 9`, destroying in one token a distinction that was correct in
the function. Fixed, and the launchers' population is now discovered rather than listed, so the next
launcher is covered the moment it exists.

**Job `58507305` — COMPLETED, 54 s, exit 0, verdict `MEASURED`… and it measured nothing about its
own subject.**

`sbatch --export=ALL,A=1,B=2` parses its argument as a **comma-separated list of `NAME=VALUE`**, so
the commas inside `MNV_THREAD_GRID=1,2,4,8` split the **list** — backslash escaping does not survive
— and the variable exported as `1`. Every cell ran at one thread. `invariant_across_thread_grid` came
back `true` for all three arms: **arithmetically correct over a population of one.** The grid was gone
before the script started, and the green exit could not tell.

It was diagnosable only because the record carries the quantity that *defines* the hazard rather than
just the verdict — `thread_grid: [1]`, and each cell reporting `threads=1 omp_env=1
num_threads_param=1`.

### 13.1 What the run DID establish, and it is not nothing

| | |
|---|---|
| rows | `200,000`, `row_floor: SATISFIED` |
| arms reporting | 3 of 3 — `historical`, `det_only`, `pinned` |
| digest, **every arm, both repeats** | `b151b10b4b6343b5` — *one* value across all six fits |
| `within_process_identical` | `True` in every cell |
| LightGBM | `4.6.0`, Python `3.11.14` |

**At `num_threads = 1` the three configurations are indistinguishable**, and each is bitwise
reproducible across repeated fits in one process. So `deterministic=True` and `force_row_wise=True`
change **nothing** at one thread — which is what the mechanism predicts, since with one thread there
is no reduction-order ambiguity to fix. **The knobs' entire effect lies on the multi-thread path.**
That is now measured rather than argued, and it sharpens the open question to exactly one axis.

⚠ **It does not touch the `4.452e-14` finding.** That deviation arose in the *production*
configuration, which uses `n_jobs=None` — every available thread — not one. A single-thread result
cannot speak to it.

### 13.2 Both defects are now unlandable, and one more submission would answer the question

- A one-valued axis reports the **string** `VACUOUS — … one point cannot show invariance ACROSS
  thread counts`, never a boolean; the overall verdict becomes **`DEGENERATE`**; a repeated value
  (`4:4`) does not count as variation. ⚠ The `pinned` arm is single-valued **by design**, so
  `VACUOUS` is the honest answer there and the tests keep the two cases apart.
- The grid separator is `:` by default and the launcher **refuses** a grid of fewer than two values
  (`rc 14`) rather than caveating it.
- An older test of mine **encoded the defect** — it built a one-thread grid and asserted `MEASURED`.
  Corrected, with the reason on its face.

**The remaining submission is `0.25` CPU task-h** — `--ntasks=1 --time=00:15:00`, against the
measured `403.6775` headroom. ⚠ **I have spent my one corrective resubmission for this stage** (on
the environment-ordering defect), and the second run completed rather than failed, so this is a
*third* submission and Joseph's call rather than mine. It is the cheapest decision-relevant item in
the package: if output tracks the thread count, **no number of cross-allocation repeats fixes it** and
P2's `9.00`–`12.00` task-h should not be bought at all.


---

## 14. The a5 build receipt, read — R5 step 2 performed, and D2/cause-3 premises verified

Zero compute: `z_pilot_20260916_a5/z-receipt-cv.json`, `37,568` bytes, read directly. This is R5's
recommended **step 2** ("read the stamps before recomputing anything") actually carried out, plus
independent confirmation of several claims I had sourced elsewhere.

### 14.1 Independent confirmation of §10.1 and of my own NPZ measurements

| receipt field | value | agrees with |
|---|---|---|
| `G5_band_partition` | `exhaustive: true`, `n_inventory 45`, `n_vert 13`, `n_residual 27`, `n_lateral 5` | §10.1, measured from the 41.44 GB support file — **a different file, same answer** |
| `G4_symmetry_psd.rel_asymmetry` | `2.1641333629718972e-16` | my independent NPZ measurement, to every digit |
| `G4_symmetry_psd.lambda_min` | `-1.2750516323643892e-90` | the figure this plan has been quoting |
| `G2_g_domain` | `g_min 1.0`, `g_max 17.653141714565614`, `n_gt_one 6528`, `n_pinned 0` | `hInflation_g`'s measured min/max in the npz |
| `G1_closure_identity.max_rel_residual` | `0.0` at `rtol 1e-9` | — |
| `G3_g_reconstruction.max_rel_diff` | `0.0` | the inflation factors reconstruct exactly |
| `active_total_eq_sum5` | `0.0` | cause 7's lateral-sum trace |

**R1's recommendation now rests on two independent measurements of the band partition**, one from the
support family's own keys and one from the build's receipt. That is the strongest state any item in
this package is in.

### 14.2 R5 STEP 2, PERFORMED: the lineage is recorded UNVERIFIED, by the producer

    parent.lineage_status          = "UNVERIFIED"
    parent.parent_candidate.path   = .../readopt_20260811_footing/stamped_bkgaware_meancentered_20260812.root
                                     892,170,881 B   sha256 4f168e83...
    parent.combined_source.path    = .../uq_universe_5d_covariance_combined_bkgaware.root
                                     41,436,632,945 B   sha256 9f7b2f55...

**The two-ensemble finding is confirmed and its disposition is narrowed.** The build consumed the
**2026-09-14 precursor** as its `throw` source (`z-manifest.json`) and names the **2026-08-11/12**
mean-centered object as `parent_candidate` — and it labels that relationship `UNVERIFIED` rather than
asserting it. So the parent is a *declared comparison subject*, not a component of `C_Z`.

**This moves R5 from "possible component quarantine" toward "documentation and a verification step",
which is the cheap branch, and it was measured rather than assumed.** What remains is to verify the
claimed lineage or record it as unverified in the registry — and to amend
`ESTIMATOR_REGISTRY:29`, which names `..._UTHROW.root` while the chain consumed the unsuffixed file.
**No recomputation is indicated by this evidence.**

### 14.3 D2's premise verified: there are exactly FOUR withheld boundaries

    cause3_agg      WITHHELD   the format-derived 0.0861% was withdrawn in rev. 16
    cause3_med      WITHHELD   needs a justified per-bin tolerance AND a coverage fraction
    cause3_corr     WITHHELD   no correlation-sensitive leg is adopted, and none has a boundary
    null_epsilon    WITHHELD   neither B nor S is established

**`cause2_f7_margin` is not among them**, which is exactly what D2 proposes to create — so D2's
"extend the withheld set to five" is verified against the artifact rather than against my reading of
the contract. And cause 3's own requirement line confirms it needs **three** criteria (aggregate,
per-bin/coverage, correlation-use), matching the three withheld `cause3_*` keys one for one.

### 14.4 Two disclosures in the receipt that belong in the decision package

- **`outcome.assessable: false`, `reject_conditions: ["4c"]`**, reason *"Scientific criteria and
  real-input evidence remain unresolved."* The build **classifies itself** as not assessable. That is
  not a failure of construction — every closure identity above is exact — it is the absence of the
  criteria. `z_validator.py:15`: *"An unassessable run is a REJECT, NOT A FOURTH GRADE TOKEN."*
- **`null.assessment.verdict: "NOT ASSESSABLE"`**, `r_null 4.4520002137582904e-14`,
  `reject_conditions ["4c", "11"]`, with `null_epsilon` WITHHELD because *"Neither B nor S is
  established."* This is the same closed-route finding as packet §2.1, stated by the producer.
- **`causes` 1, 2, 3, 4 are all `status: UNRESOLVED`** with explicit requirement lines. This is the
  authoritative list and it matches the packet's.
- ⚠ **`reproducibility: null`** in this receipt, and `G3R.stored_cv_cross_checked: false`.

⚠ **The second flag is NOT a missing check, and the distinction matters.** Packet §9.3 records that
`[cb0b6b]` performed the external cross-check on payload — production `hXSecND_flat` against the
persisted vector, **65,856 of 65,856 identical, `max|Δ| = 0.000e+00`**, mask identical at 10,694 each,
and `flatnonzero(mask)` against `hRowIndex5D` identical and strictly increasing — and **correctly
declined to flip the producer's flag**, because the producer was handed no external operand and its
flag records that accurately. *"Check satisfied, flag unchanged — two different statements."* So M-C
stands, and that third-party result **independently reproduces the row-order agreement** I measured
from the npz.

**Recorded because the shape has cost me once today:** a `false` flag can mean *the producer was not
given the operand*, not *the property fails*. Not-performed-by-the-producer and
performed-externally are two states, exactly as absent, inaccessible and unsearched are three.


---

## 15. THE DETERMINISM RESULT — job `58509947`, and it reverses my own reasoning

`COMPLETED`, `ExitCode 0:0`, `ElapsedRaw 198 s` (**`0.055` CPU task-h actual against a `0.25`
reservation**), `nid004083`, `AllocCPUS 10`. Record:
`zdet-DIAGNOSTIC-20260918/z_determinism_probe_record_r2.json`.

**The experiment was valid this time, and that is checked rather than assumed:**

    thread_grid                          [1, 2, 4, 8]
    backend_thread_values_reached        ['1', '2', '4', '8']      <- off the FITTED Booster
    backend_confirmed_distinct_threads   True
    row_floor                            SATISFIED   (200,000 rows)
    cells                                9      unavailable 0
    cpu_count_visible                    10 in every cell          <- no cpuset clamp at 8

### 15.1 The result: EVERY ONE OF THE 18 FITS PRODUCED THE IDENTICAL DIGEST

| arm | thread values | `within_process_identical` | `invariant_across_thread_grid` | distinct digests |
|---|---:|---|---|---:|
| `historical` | 4 (`1,2,4,8`) | **True** | **True** | **1** — `b151b10b4b6343b5` |
| `det_only` | 4 (`1,2,4,8`) | **True** | **True** | **1** — `b151b10b4b6343b5` |
| `pinned` | 1 (by design) | **True** | `VACUOUS` — correctly | 1 — same digest |

### 15.2 Reported at its tested scope — three propositions, not one

- **Within-configuration repeatability: HOLDS.** 9 of 9 cells, both repeats bitwise identical at a
  fixed configuration and a fixed thread count. This is the narrowest claim and the strongest one.
- **Cross-thread agreement: HOLDS**, for `historical` and `det_only` across `{1,2,4,8}`, with the
  **backend confirming** each setting took effect. Same digest at every thread count.
- **Full-chain reproducibility: NOT MEASURED.** `r_null = 4.4520002137582904e-14` is a property of
  the full chain — OmniFold loop, unified-throw combine, assembly — **on production data**. This
  probe fits one LightGBM model on **synthetic** data. Nothing here measures it.

⚠ **AND THE SCOPE LIMIT THAT MATTERS MOST:** `200,000 × 6` with `n_estimators=100, num_leaves=8` is
**not production's size or shape.** LightGBM's parallel histogram construction partitions by rows
and features, so thread-invariance at this scale does **not** establish it at production scale. The
result is evidence about the estimator's arithmetic in the tested regime and is not transferable to
the production fit by assumption.

### 15.3 THIS REVERSES MY OWN REASONING, and the reversal is the decision-relevant part

I wrote, twice, that thread count is *"the channel a cross-allocation difference would act
through"* and that *"if the output tracks the thread count, no number of cross-node repeats fixes
it."* **The output does not track the thread count.** So:

1. **In the tested fixture, the thread-count channel does not vary.** That is the whole of it.
2. **`deterministic=True` and `force_row_wise=True` changed nothing IN THE TESTED FIXTURE** —
   `det_only` returns the identical digest to `historical` at every thread count there.

⚠ **THREE INFERENCES I DREW FROM THIS ARE WITHDRAWN. They do not follow, and I should not have
written them.**

| I wrote | why it does not follow |
|---|---|
| *"threading … is now the least likely of those examined"* as an explanation for `4.452e-14` | The fixture is `200,000 × 6` synthetic rows, `n_estimators=100`, `num_leaves=8`. LightGBM partitions histogram construction **by rows and by features**, and switches strategy with data size, feature count, sparsity and bin counts. A regime where threading does not perturb the result says **nothing** about a regime with different row count, feature count, or value distribution. **Threading in production remains fully open.** |
| *"do not pin the estimator"*, on the ground that the overlay showed no benefit | No benefit **was measurable in a fixture where nothing varied at all**. A knob that prevents a perturbation cannot be shown to have value in a setting with no perturbation to prevent. **The value of pinning in production is untested, not absent.** |
| *"do not buy P2"*, on the ground that its mechanism was measured invariant | The mechanism was measured invariant **in the fixture**, not in production, and cross-allocation variation can also act through CPU model, vector kernel selection, and library dispatch — none of which one node can vary. **Cross-allocation testing is not shown unnecessary.** P2 stays **deferred**, which is a scheduling statement about gathering more relevant evidence first, **not** a judgement that it would be uninformative. |

3. **What the result does support**, and only this: repeated fits of *that* configuration on *that*
   fixture are bitwise identical, and the two knobs are inert *there*. It narrows nothing about
   production and it licenses no conclusion about `4.452e-14`.
4. **A thread-count difference does not rule out fixed-thread reproducibility.** Here there is no
   thread-count difference *in the fixture*, and that is not evidence about either proposition in
   production. The three propositions are recorded separately in the artifact (`tested_scope`) so
   none can be read as another.
5. ⚠ **And the fixture's own validity is only argued, not measured**, for this run: a constant
   prediction vector would make all 18 digests agree for free, and `58509947`'s record predates the
   `prediction_spread` statistic. Non-degeneracy is inferred from the generator
   (`logit = 0.7x₀ − 0.4x₁ + 0.3x₂x₃`, genuinely learnable), which is an argument and not a
   measurement. The next run measures it.

### 15.4 What I recommend, and what I do NOT

**RECOMMEND: keep P2 DEFERRED — not cancelled — and hold the pinning decision open.** Deferred
because more relevant evidence is cheaply available first, and that ordering is a scheduling
judgement. **Neither "P2 is unnecessary" nor "pinning has no value" is supported by this run**, and
§15.3 withdraws both claims where I made them.

**RECOMMEND NEXT: a production-FAITHFUL diagnostic, not a larger synthetic one** — §18. Scaling the
fixture up would still be a fixture, and the question is about the production chain. The design
requirement is the actual inputs, weights, estimator settings and CV execution path, instrumented to
locate the **first divergence** between two repeated executions rather than only to report whether
the endpoints differ.

**I do NOT recommend** reading this as reproducibility of the chain, as a licence to quote
`r_null`, or as grounds to revisit `ε` — every route to `ε` remains closed (packet §2.1) and the
producer's own receipt says `null_epsilon` is `WITHHELD` because *"Neither B nor S is established."*

⚠ The record from `58509947` predates the `tested_scope` block (added at `4007645a`+1), so its
scope is stated here rather than in the file. Every future run carries it inline.


---

## 16. THE M1 DIAGNOSTIC PROJECTION — produced, verified, and it answers its acceptance question

Job `58510024`, `COMPLETED`, `ExitCode 0:0`, `ElapsedRaw 50 s` (**`0.014` CPU task-h actual against
a `0.25` reservation**), `nid004110`. Product
`zdet-DIAGNOSTIC-20260918/m1_eavailW_DIAGNOSTIC.root`, `17,120` B, receipt `4,275` B.

**Projected from the verified candidate** — `src_cov_sha256 = src_cv_sha256 =`
`3d7465f66fbe66b0dfcf09b6fc51249f227fb33e97ae40bc78dda90275e918c5`, which is `z-cv.npz`'s digest in
`outcome-58454524/product-digests.txt`. The input's identity is bound into the product's receipt.

### 16.1 The measured projection

    src reported 10694  ->  dst reported 42        src_cells_dropped  0
    sqrt-tr              4.4552e-39                n_empty            0
    symmetry max|C-C^T|  0.00e+00   EXACTLY symmetric
    min-eig              +4.359e-92   POSITIVE
    most-neg/max         2.93e-15
    rank                 ~36 / 42
    M_shape              [42, 10694]    M_content_sha256 64fec490...

### 16.1a ⚠ TWO CLAIMS I MADE HERE ARE WITHDRAWN, and the measurement that replaces them

**"rank ≈ 36 of 42" was reported without its cutoff, and the cutoff is doing all the work.**
`project_cov_nd.py:340` uses a **hardcoded `rc = 1e-12`** and counts `λ > λ_max · rc`. Scanned on
the actual product:

| relative cutoff `rc` | rank | largest excluded `λ/λ_max` |
|---|---:|---|
| `1e-1` | **2** | `6.27e-02` |
| `1e-2` | 7 | `6.69e-03` |
| `1e-3` | 11 | `7.36e-04` |
| `1e-4` | 17 | `8.86e-05` |
| `1e-6` | 26 | `7.22e-07` |
| `1e-8` | 28 | `9.50e-09` |
| `1e-10` | 32 | `6.28e-11` |
| **`1e-12`** | **36** | `7.83e-13` |
| `1e-14` | 41 | `2.93e-15` |
| `1e-16`, `0` | **42** | — |

`numpy.linalg.matrix_rank`'s own default (`rc = n·eps = 9.33e-15`) gives **41**.

**THERE IS NO SPECTRAL GAP.** The 42 eigenvalues decay smoothly over ~15 orders of magnitude —
`1.00, 1.66e-1, 6.27e-2, 3.82e-2, … 1.16e-13, 4.71e-14, 2.93e-15` — with no plateau anywhere. So
**the numerical rank is not a property of this matrix in any stable sense**; it is a property of a
chosen cutoff, and defensible cutoffs give anything from 26 to 42. **`36` should never be quoted
bare, and it is not the `ndf`.**

⚠ **And the projector's cutoff is undeclared while the consumer refuses to default one.**
`rank6_significance.py` exits `rc 3` when `--rcond` is absent, on the stated ground that both
existing consumers called `pinv` with no explicit `rcond`. `project_cov_nd.py` reports a rank off a
literal `1e-12` in the same campaign. That inconsistency is now on the record; the retained-subspace
rule belongs in the declaration set (§17), not in a projector's print statement.

**"The negative directions do not propagate — `M C Mᵀ` averages them out" is WITHDRAWN.** It was a
mechanism claim I did not test, and the measurement says something weaker and more precise:
`λ_min = 4.359104e-92` with `λ_max = 1.488215e-77`, so `λ_min/λ_max = 2.93e-15` and the condition
number is `≈ 3.4e14` — **at the edge of double precision.** The smallest eigenvalues sit at the
floating-point noise floor of a 10,694-term weighted sum, so **their sign is not meaningful** and
"positive" is not evidence that anything was cured. `n_negative = 0` is a true statement about this
computation; it is **not** a demonstration that the source's 5,214 negative directions were handled.

### 16.1b What stands

1. **`n_empty = 0` and `src_cells_dropped = 0`.** Both coverage censuses are clean: every one of the
   10,694 source cells reaches a reported destination cell, and no destination row receives nothing.
   `SPEC:1239` requires the `(E_avail,W)` projector to **count-and-report** — it reports **zero**, so
   an acceptance criterion requiring zero is satisfiable on this product without the projector ever
   gating. **This is the most robust of the four findings and it does not depend on any tolerance.**
2. **`symmetry max|C−Cᵀ| = 0.00e+00` exactly**, tighter than the source's `2.164e-16`, because the
   `M C Mᵀ` form symmetrises by construction. A structural fact, not a tolerance.
3. **`trace = 1.984864e-77`, `sqrt(trace) = 4.455181e-39`** — scale, reported for pairing.
4. **The projection is numerically PSD at this precision** (`n_negative = 0`), stated as an
   observation about this computation with the condition number attached, and **not** as a property
   the object will retain under a different mask, a different summation order, or higher precision.

### 16.2 The acceptance question is ANSWERED: YES, `τ` is computable

The run's declared question was *"whether `τ` is computable at all on the verified candidate
trunk"*. **It is.** The projected correlation matrix exists, is PSD, has no undefined rows
(`n_empty = 0`), and has a measured retained rank. **`τ` is therefore no longer blocked on
judgement — it is blocked on one declaration**, D3's `N`, after which `τ` is a calculation on this
object rather than a number anyone has to choose.

**So cause 3's third input has moved from "no value and no route" to "one declaration away".** That
was the cycle §11 identified, and it is now cut in fact and not only in design.

⚠ **`τ`'s VALUE is not computed and must not be inferred from the above.** It needs `N` (D3, yours)
and the corner region (D5, yours). And per §11's residue: `τ` computed on the candidate is `τ` for
*the candidate*. If adoption lands on a different object, it is a `0.324 s` recomputation, not a new
campaign.

### 16.3 Every guard fired or passed as designed, and the receipt shows it

    run_class                 diagnostic
    status                    DIAGNOSTIC -- NON-ADOPTED and PROVISIONAL ... does not become
                              a publication product by being renamed or copied
    src_container             npz
    src_row_index_basis       producer hRowIndex5D, REQUIRED equal to the order derived from
                              src CV (xsrc > 0); both present and identical
    src_metadata              adoptable False | scientific_acceptance NON-PASSING |
                              variant cv | input_kind real | manifest_sha256 44ab73ba... |
                              code_identity.revision fb9ec356...
    dst_mask_basis            dense destination bins receiving >= 1 source cell (no --dst-cv)
    row_index_sha256_readback 9eb9d216...  (read back out of the CLOSED file)
    run_class_keys_in_product ['runClass', 'runClassStatus', 'acceptanceQuestion']

The row-order cross-check **fired and passed** — *"both present and identical"* — so the
covariance's rows are bound to physical bins by two independent statements that were required to
agree. The source binding carries `adoptable: False` and `NON-PASSING` **into the projection's
receipt**, so the product cannot be read without the standing of what it came from. And the class
labels are inside the ROOT file, not only the sidecar.

**This product is NOT the quotable `(E_avail,W)` covariance.** `AGENTS.md:27` requires that to be
projected from the **adopted** trunk and `:30` quarantines the existing one. The candidate records
`adoptable: false`, which **refuses** `--run-class publication` in code.

### 16.4 Accounting for both runs

| | reservation | actual | node |
|---|---:|---:|---|
| determinism `58509947` | `0.25` | **`0.055`** | nid004083 |
| M1 diagnostic `58510024` | `0.25` | **`0.014`** | nid004110 |
| earlier failed attempt `58506753` | — | `0.0011` | nid004090 |

Total actual **`0.070` CPU task-h**, against headroom `403.66` and a stop date of `2026-09-30`. Both
runs were admitted against a fresh receipt before submission, with outstanding reservations counted.
**Joseph's `0.25` cap on the determinism submission was respected and the run came in at 22% of it.**


---

## 17. `τ`'s DEFINITION, completed on the diagnostic product — and `N` is NOT the only missing input

Joseph, 2026-09-18: *"Do not treat D3's `N` as the sole missing input to `τ`. Complete the proposed
calculation's definition using the existing diagnostic product: name the tested claim and region,
generator residual, correlation reference and drift norm, admissible covariance changes,
retained-subspace rule, and null-distribution justification."*

He is right that `N` was not the only gap. **Seven inputs are required and `N` is one of them.**
Three are now measured, one is a declaration I can make, and **three are genuinely absent** — one of
which I had never named at all.

### 17.0 ⚠ FIRST, A CORRECTION THAT CHANGES THE WHOLE ANALYSIS: the claim uses a 12×12, not the 42×42

`eavailW_covariance.py:556-559` — `cidx` selects the corner and the χ² is
`pinv(C_total[np.ix_(cidx, cidx)])`. **The corner is 4 `E_avail` bins × 3 `W` bins = 12 of 42
cells**, dense indices `[21,22,23,27,28,29,33,34,35,39,40,41]`. My §16.1a rank discussion was about
the 42×42, which the claim never inverts. Measured on the **corner sub-block** of the diagnostic
product — all 12 rows present, none missing:

| | 42×42 (not used by the claim) | **12×12 corner (used)** |
|---|---|---|
| `λ_max` | `1.488215e-77` | `1.352623e-79` |
| `λ_min` | `4.359104e-92` | `3.403095e-89` |
| `λ_min/λ_max` | `2.93e-15` | **`2.52e-10`** |
| condition number | `≈ 3.4e14` — edge of double precision | **`≈ 3.98e9` — comfortably inside it** |
| `n_negative` | 0 | 0 |
| rank at `rc ≤ 1e-10` | 32 → 42, no plateau | **12 (full) and STABLE** |
| `numpy.matrix_rank` default | 41 | **12** |

**On the object the claim actually uses, the matrix is full rank and five orders of magnitude
better conditioned.** Rank is `12` for every cutoff from `1e-10` down to `0`, and numpy's default
agrees — so unlike the 42×42, here the numerical rank **is** stable over the plausible range. The
spectrum is `1.00, 2.08e-1, 6.04e-2, 3.00e-2, 1.09e-2, 4.69e-4, 1.91e-6, 1.31e-7, 1.67e-8, 7.87e-10,
4.37e-10, 2.52e-10` — soft structure after the fifth, but no rank deficiency.

Relative standard deviations on the corner: **min 2.88%, median 5.81%, max 12.41%** — physically
sane, and the scale `√tr = 4.208e-40` with `Σ CV = 1.428e-38`.

### 17.1 The seven inputs, with their status

| # | input | status |
|---|---|---|
| 1 | **Tested claim and region** | **DECLARATION — D5, Joseph's.** The claim is `main_paper.tex:49-51`. The region as coded is the 12-cell corner, and `W ≥ 1.8` is **data-selected** (enters code 2026-06-09, two days after the 06-07 excess test; the design doc says the W axis *"localizes"*). The `E_avail` half is prespecified (2026-06-03). |
| 2 | **Generator residual** `r = y_data − y_gen` on the region | ⚠ **ABSENT, and I had never named it.** `y_data = hCV_marginal` is in the diagnostic product (`Σ = 1.428e-38` on the corner). **`y_gen` is not.** `eavailW_covariance.py:563-572` builds `gen_hists` keyed by tag — in the module `AGENTS.md:30` quarantines. So the residual needs generator predictions projected onto the same 12 cells by the same `M`, which is a **new input**, not a decision. |
| 3 | **Correlation reference** `R₀` | **COMPUTABLE NOW.** `R₀ = D^{-1/2} C_corner D^{-1/2}` from the diagnostic product. Reference member = `k = 0`, the archive. |
| 4 | **Drift norm** ‖·‖ | **DECLARATION, and the choice is not cosmetic** — see §17.2. |
| 5 | **Admissible covariance changes** | The cause-3 member family: `{C_k}` over the estimator-seed sweep, **diagonal** family, group assignment `{arms 1–4: 42, arms 5–7: 1000}` (D1). So `τ` bounds drift over *that architecture only* — D1's declared scope limit carries into `τ`'s meaning. **Members are not built** (cause 3 `status: UNRESOLVED`). |
| 6 | **Retained-subspace rule** | **DECLARATION. ⚠ MY FIRST ANSWER HERE WAS NUMERICALLY WRONG TWICE — corrected in §19.1. Recommend `rcond = 1e-5`, retained rank 6**, chosen at the spectrum's widest gap. |
| 7 | **`N`, the claim threshold** | **DECLARATION — D3, Joseph's.** Recommended `3` (§2, D3). |

**Plus the null-distribution justification**, which is not an input so much as an argument, and is the
weakest link — §17.4.

### 17.2 The drift norm, and why a generic matrix norm is the wrong instrument

The claim depends on the correlation matrix **only through** `χ² = rᵀ C⁺ r` on the 12 cells. So the
perturbation that matters is not ‖`R_k − R₀`‖ in any norm, but the induced change in that scalar.
A generic Frobenius or spectral norm is a **proxy** whose relationship to `Δχ²` depends on where `r`
points relative to `C`'s eigenvectors.

**Recommendation: define the drift in the quantity the claim uses, not in a proxy.**

    delta_k  =  | chi2(r, C_k)  -  chi2(r, C_0) |  /  chi2(r, C_0)

with `r` and the retained subspace **fixed from the reference**. Then `τ` is a bound on `delta_k`
directly, and no norm-to-significance transfer argument is needed. If a matrix norm is wanted for
reporting, quote the spectral norm of `R_k − R₀` **alongside** and label it descriptive.

⚠ This is a **change to what I proposed in §2, D3**, and it is the better construction: my earlier
wording bounded *"projected-correlation movement"* in an unnamed norm and then transferred to
significance. Naming the norm as the significance itself removes the transfer.

### 17.3 How the inputs yield a bound — and the two cases I had not handled

Given region, `r`, subspace rule, family and `N`:

1. Compute `S₀ = Z(χ²(r, C₀), ndf)` on the reference member.
2. For each member `k`, compute `S_k` with `r` and the subspace **held fixed**.
3. `τ` is the largest `delta` such that every member with `delta_k ≤ delta` keeps `S_k ≥ N`.

**CASE A — the reference is already below `N` (`S₀ < N`).** Then **`τ` is vacuous and must not be
computed.** There is no "movement that would flip the conclusion" because the conclusion is already
the null one, and any `τ` derived from a sub-threshold reference would be a bound on nothing. The
correct action is to **narrow the claim** — which is what `main_paper.tex` already does by calling
the localization *"a central-value result"* whose significance awaits the covariance. My §2 framing
silently assumed `S₀ ≥ N` and had no branch for this; **it is the more likely case on a 12-cell χ²
with median 5.8% uncertainties**, and it must be checked before `τ` is defined rather than after.

**CASE B — the retained rank changes across members.** Then `S_k` and `S₀` have different `ndf`,
their thresholds differ, and the comparison is not well posed — a member could "fail" `τ` purely by
changing dimension. **Recommend eliminating the case by construction: fix the retained subspace on
the reference member and project every member onto it.** Rank is then constant, drift is measured in
one basis, and a member whose own spectrum would truncate differently is still compared on equal
terms. §17.0's measurement makes this cheap: the reference is full rank 12, so the fixed subspace is
the whole space and no truncation happens at all.

### 17.4 Retrospective sensitivity ≠ prospectively justified acceptance criterion

**These are two different deliverables and cause 3 has been conflating them. So have I.**

| | retrospective sensitivity measurement | prospective acceptance criterion |
|---|---|---|
| what it is | report `max_k delta_k` and the observed spread of `S_k` | declare `τ` in advance, then test |
| needs a threshold? | **No** | Yes, and it must be justified |
| contaminable by the result? | No — it *is* the result | **Yes, if `τ` is set after seeing `S₀`** |
| what it licenses | *"the estimator-seed choice moves the significance by X"* — a stated limitation | *"cause 3 is MET"* |
| status | **available as soon as the members exist**; needs no decision from Joseph | needs inputs 1, 4, 7 declared first |

⚠ **AND THE PROBLEM WITH MY OWN PROPOSAL, stated plainly.** Deriving `τ` from *"what would keep
`S₀` above `N`"* reads the reference significance. If `S₀ = 4.5σ` and `N = 3`, `τ` comes out large;
if `S₀ = 3.2σ`, `τ` comes out tiny. **So `τ` scales with how favourable the observed result is** —
which is deriving an acceptance tolerance from a favourable observed result, exactly what the
standing instruction forbids. My §2 D3 entry called this *"non-circular"*; **that was wrong** and it
is withdrawn as written.

**A prospectively clean alternative, recommended:** declare `τ` from a **precision** requirement
that does not reference the generator comparison at all — e.g. *the estimator-seed choice must not
change the quoted relative uncertainty on the corner's integral by more than `X`%*. That is a
statement about the measurement's own stability, is declarable before any member exists, and cannot
scale with whether the generator happens to disagree. `X` is still a scientific number and still
Joseph's, but it is the **right kind** of number: a precision tolerance, not a conclusion-preservation
tolerance.

**The conclusion-flip calculation remains worth doing — as the retrospective leg**, reported as a
sensitivity, labelled as such, and not used as the acceptance test.

### 17.5 What is therefore needed, in order

1. **`y_gen` on the 12 corner cells**, projected by the same `M`. A new input, not a decision. Until
   it exists **no residual, no `χ²`, no `S₀`, and no `τ` of either kind** can be computed — which is
   why `N` was never the only gap.
2. **D5** — the region. Recommendation unchanged: the prespecified `E_avail` region, keeping the `W`
   localization at central-value level.
3. **D3 restated** — not *"name `N`"* alone, but: declare `N` **and** choose between the
   precision-based `τ` (recommended) and the conclusion-flip `τ` (retrospective only).
4. **The cause-3 members**, which do not exist; cause 3's own requirement line says *"build all
   members"*.
5. `rcond = 1e-10` and the fixed-subspace rule — **mine to declare, and declared here.**


---

## 18. STAGE D-CVDIV-1 — the production-faithful diagnostic, recorded before submission

Joseph, 2026-09-18: *"Make the next diagnostic production-faithful rather than merely larger… with
checkpoints sufficient to identify the first divergence between repeated executions. Choose the
smallest bounded test that can answer that question."* Submitted as job **`58510551`** after the
record below, a fresh receipt and verified admission.

**Question.** `unified_throw_cov.py:840` and `:1011` call `_xsec_for_weights` with **the same**
`args.estimator_seed` and the same `d, edges, w_truth, w_reco, td_cv, args.iters` — re-verified at
the lines, which also settles a doubt I had: the `seed + 1` I found is in
`compare_unified_throw.py:193`, a **different** driver. So P0's like-for-like finding stands. The two
results differ by `r_null = 4.4520002137582904e-14`. **An endpoint norm over the final cross-section,
after five iterations and ten classifier fits, cannot say where.** This asks where.

**Why it is the smallest test that can answer it.** The loop's only outputs are `w_pull, w_push` at
`omnifold_nn_core.py:275` — there is no per-iteration hook, so an endpoint comparison is all the
production path offers. The cheapest way to get stage resolution is to digest **every classifier
evaluation** in both executions and report the first index where the sequences differ. `_reweight`
is module-level, so a driver can wrap it; the wrapper calls through and returns the original value,
so it is **capture-only and cannot alter what it measures**.

**Production-faithful, item by item — this is the part "merely larger" would have failed:**

| | |
|---|---|
| inputs | the **real** bank `cv.npz`, `2,939,596,884` B, `sha256 3c9bbd6283fcb157…` — which **is** the precursor receipt's `extra.bank_cv_sha256`. Verified in-probe as a **refusal** |
| weights | `w_truth`, `w_reco`, `td_w` straight out of that bank |
| estimator settings | whatever `make_estimators` constructs — **UNPINNED**, as production leaves it. Applying the overlay would test a different estimator |
| CV execution path | `_xsec_for_weights` itself, not a re-implementation |
| iterations | 5, the production value |
| **allocation shape** | `--cpus-per-task=16 --mem=90G`, **matching `sbatch_uthrow_combine_5d_fast.sh:4`**, because the estimator runs with `n_jobs=None` — every available thread — so **the CPU count is part of the configuration under study** and a different shape is a different experiment |

**What either outcome changes, stated before the allocation was spent.** The three are mutually
exclusive and point at **different repairs**:

1. **The first classifier evaluation already differs** → the estimator is non-reproducible on
   production inputs at a fixed seed. That **contradicts** the synthetic-fixture result
   (`58509947`), which makes the *difference between the two regimes* the finding and points at
   data-dependent threading. Pinning becomes the candidate remedy and P2's design narrows.
2. **Evaluation `N` differs after `N−1` identical ones** → the estimator is reproducible and
   something downstream accumulates: the regressor branch (`use_reg`), the weight product
   `w_pull = w_push · new_w`, or the histogram fill. **Pinning would NOT fix it** and the repair is
   local to the identified stage.
3. **None differ** → `r_null` arises outside this path, and the launcher's `must be zero` is
   **mis-scoped rather than violated** — a documentation repair.

**Call-index → stage mapping**, deterministic in the loop's structure (`omnifold_nn_core.py:248-269`):
within iteration `it`, call `2·it` is step 1 (`clf1` on `MCreco[pass_reco]`) and `2·it+1` is step 2
(`clf2` on `MCgen`). A difference in call **count** is reported as its own finding rather than as a
digest mismatch.

**Declared limits and accounting.** `1 task × 2.00 h = 2.00 CPU task-h`, the wall anchored on the
measured combine actuals `0.3875 / 0.4239 / 0.5764` h for a job that includes **one** CV unfold —
this runs two and skips the assemblies. Admitted against a receipt measured at
`2026-09-18T07:07:01Z`: spend `96.4064` of `500`, **headroom `403.5936`**, GPU `16.0117`,
outstanding reservations **0**. Retry limit unchanged: one corrective resubmission after a diagnosed
defect, verified repair and fresh admission; automatic requeue stays disabled.

⚠ **Not covered, recorded on the probe itself:** the regressor branch does not pass through
`_reweight`, so a divergence originating there is seen only at the *next* evaluation; the histogram
fill is covered only by the endpoint; and cross-**node** behaviour is not measured at all.

⚠ **Finding the bank took three searches and the first two were wrong**, in the way that has now
cost me twice today. `*bank*cv*.npz` and `*bank*` + `*.npz` both returned nothing. Then I read the
launcher: `--bank` names a **directory**, whose CV input is `cv.npz`. The name-correct search found
it at once and the digest confirmed it. **Read the consumer's argument; do not guess the filename.**

### 18.1 Job `58510551` FAILED, diagnosed, repaired, resubmitted as `58524334`

`FAILED`, `ExitCode 1:0`, `1011 s` (**`0.2808` CPU task-h charged in full**), `nid004121`. It got
far — bank loaded (12 knob bands, 100 flux universes, **32,849,103 events**, `edges [14,16,7,7,6]`),
the OmniFold loop fitted both classifiers and the regressor — then died at
`compare_unified_throw.py:155`: *"The dimension of bins must be equal to the dimension of the
sample x."*

**The cause, and the wrapper module's own docstring predicts it verbatim.**
`unified_throw_cov_5d.py:7-8` — the base kernel *"stops at `td_q3` (`td_cols[:len(edges)]` with no
`td_W`), so for `len(edges)==5` it would feed 4 denom coords to a 5-edge `histogramdd`. **We
monkeypatch a `td_W`-aware `_xsec_for_weights` into the base module**"* — and `:88` is
`base._xsec_for_weights = _xsec_for_weights_5d`, because *"do_throws/blockunits/combine all resolve
`_xsec_for_weights` from base's globals"*.

I had written `from compare_unified_throw import _xsec_for_weights`, which binds the **unpatched**
name. **This is the inverse of the usual defect:** normally a `from`-import makes a *patch*
decorative; here it made the patch **invisible to the caller**. Measured rather than inferred: the
5D bank does carry `td_W` (`td_W, td_ea, td_pt, td_pz, td_q3, td_w`) and five `edges_*`, and the
base module contains no `td_W` at all.

**Two citation corrections this forces.** The call-site lines I have quoted throughout —
`unified_throw_cov.py:840` and `:1011` — are correct, but **the function they resolve to at runtime
for a 5D bank is not the one bound to that name in the base module.** And the 5D chain has its own
entrypoint, `unified_throw_cov_5d.py` — a wrapper over the base file, not a fork of it.

**Repair, verified:** import the wrapper first so the patch installs, resolve through `base`'s
globals at call time, and **assert the patch landed before anything is computed** — a run that
silently used the 4D kernel would burn the allocation to rediscover this. 22 tests;
mutation-verified by restoring the original import, which fails 5 of them.

⚠ **One of my own tests asserted the defect.** `test_it_uses_the_same_function_unified_throw_cov_calls`
*required* the `from`-import that doomed the run, so it was green while the job was unrunnable.
Replaced. And the new "no `from`-import" test first failed on its own repair, because a bare
substring search also matches the comment explaining the defect; it now anchors on a real import
statement.

⚠ **A method failure in my investigation, not the run:** I grepped `_xsec_for_weights` with
`| head -5` over a **26-line** population and then reasoned about that population. The conclusion
was right by luck. **Never `head` a population.**

**Production-faithfulness of the CPU count, now on the realized figure.** The run requested
`--cpus-per-task=16` and got `SLURM_CPUS 49 / AllocCPUS 50`. The production combine requests the
**same** 16 and `AMENDMENT-20260831:239` records it at **`AllocCPUS 50`**. Since the estimator runs
with `n_jobs=None`, the realized count is the one that matters, and it matches identically.

**Resubmitted as `58524334`** — the one corrective resubmission this stage is allowed, after a
diagnosed execution defect, a verified repair, and fresh admission (spend `96.6872` of `500`,
headroom **`403.3128`**, outstanding reservations 0, measured `2026-09-18T12:50:13Z`). The ledger
reconciles exactly: `96.4064 → 96.6872` is `+0.2808`, the failed attempt's `1011 s`. **The stage's
corrective resubmission is now spent.**

⚠ **A monitoring note against myself.** My first waiter for `58510551` returned **empty output with
exit 0**, and the exit code was the *local* `ssh` wrapper's, not the remote loop's. An empty result
must be read as **BLIND**, never as completion — so I re-measured the state directly, which is how
the `FAILED` was found. The replacement waiter prints `BLIND_NO_ROWS` explicitly when `sacct`
returns nothing.


---

## 19. CORRECTIONS AND THE COMPLETED D3/D5 RECOMMENDATION — 2026-09-18

Prepared independently of job `58524334`, whose outcome informs **reproducibility remedies** and
neither the scientific region nor the acceptable precision loss.

### 19.1 ⚠ §17.1's retained-subspace recommendation was numerically wrong in two ways

I wrote: *"full rank 12, stable for every cutoff `≤ 1e-8`. Recommend `rcond = 1e-10`, four orders
below the smallest retained eigenvalue and four above machine noise."* **Both numerical claims are
false against the spectrum I had already measured and printed.**

| `rcond` | rank | smallest retained `λ/λ_max` | margin above cutoff | largest excluded | margin below |
|---|---:|---|---:|---|---:|
| `1e-2` | 5 | `1.09e-2` | **1.09×** | `4.69e-4` | 21.3× |
| `1e-3` | 5 | `1.09e-2` | 10.9× | `4.69e-4` | 2.1× |
| **`1e-5`** | **6** | **`4.69e-4`** | **46.9×** | **`1.91e-6`** | **5.2×** |
| `1e-6` | 7 | `1.91e-6` | 1.91× | `1.31e-7` | 7.6× |
| `1e-8` | **9** | `1.67e-8` | 1.67× | `7.87e-10` | 12.7× |
| `1e-10` | 12 | `2.52e-10` | **2.52×** | — | — |

**Error 1:** rank is **9** at `1e-8`, not 12. Full rank needs `rcond ≤ 1e-10`, so "stable for every
cutoff `≤ 1e-8`" is simply untrue.
**Error 2:** at `rcond = 1e-10` the smallest retained eigenvalue ratio is `2.52e-10` — a margin of
**2.52×**, not "four orders". I was out by about nine orders of magnitude, against a table I had
printed myself one section earlier.

**The spectrum has a principled cut and it is not at full rank.** Consecutive gap ratios:

    mode 1->2  4.8x   2->3  3.4x   3->4  2.0x   4->5  2.8x   5->6  23.2x
    mode 6->7  245.5x  7->8 14.6x  8->9  7.8x   9->10 21.2x  10->11 1.8x  11->12 1.7x

**The widest gap by an order of magnitude is `245.5×`, between modes 6 and 7.**

**RECOMMEND: `rcond = 1e-5`, retained rank 6.** It is the only choice with comfortable separation on
both sides — `46.9×` above the cutoff and `5.2×` below — and it sits in the one place the spectrum
itself distinguishes. Full rank 12 is the *worst* available choice on this criterion: modes 10–12 are
separated from each other by only `1.8×` and `1.7×`, so they are not numerically distinguishable
directions at all, and retaining them puts the statistic's most `C⁻¹`-sensitive content in the
degenerate tail.

⚠ **"Rank 6" here is a NUMERICAL RANK and has nothing to do with `rank6_significance.py`**, whose
name refers to the audit's rank-6 *finding label*. The coincidence is noted so the two cannot be
read as confirming each other.

### 19.2 ⚠ A fixed reference basis does NOT prevent member-wise mode loss

I claimed fixing the subspace on the reference member makes rank constant by construction. **It does
not.** Restricting to a fixed basis `U₆` still requires inverting `U₆ᵀ C_k U₆` for each member, and
if that restricted matrix has an eigenvalue below the cutoff, a pseudoinverse drops it. Rank can
still vary member-wise, and with a `46.9×` margin on the reference it is not guaranteed to survive a
perturbation.

**Recommend a two-part rule that removes the per-member inversion entirely:**

1. **STATISTIC — first-order perturbation about the reference, no member-wise pseudoinverse.**

       delta_k  =  | r^T C_0^+ (C_k - C_0) C_0^+ r |  /  ( r^T C_0^+ r )

   with `C₀⁺` the **single** rank-6 pseudoinverse of the reference and `r` fixed. Every member is
   evaluated with the same inverse, so no member can drop a mode and no rank can change. **Stated
   as first-order:** it is the leading term of `Δχ²`, valid while `‖C₀⁺(C_k − C₀)‖ ≪ 1`, and that
   condition is itself reported per member rather than assumed.

2. **GATE — a member whose restricted spectrum falls below the cutoff is `UNASSESSABLE`, not
   truncated and not silently dropped.** If `λ_min(U₆ᵀ C_k U₆) / λ_max(U₆ᵀ C₀ U₆) < rcond`, the
   first-order expansion is not trustworthy for that member; record it as unassessable **with a
   count**, exactly as `z_validator.py:15` treats an unassessable run: *"An unassessable run is a
   REJECT, NOT A FOURTH GRADE TOKEN."* A nonzero count is itself a finding about the member family
   and must not be absorbed into a pass.

### 19.3 The two calculations are SEPARATE, and only one needs `y_gen`

⚠ **I had said `y_gen`'s absence blocked everything. It does not.** It blocks exactly one of the two.

| | retrospective significance | **precision criterion** |
|---|---|---|
| question | does the generator disagree, and how significantly? | does the estimator-seed choice degrade the measurement's own precision? |
| needs `y_gen` | **YES** — it is `r = y_data − y_gen` | **NO** |
| needs `N` (D3) | yes | no |
| needs the region (D5) | yes | yes, to define the integral's support |
| needs the members | yes | yes |
| computable on the existing product today | **no** | **yes, apart from the members** |
| contaminable by a favourable result | yes, if `τ` is derived from it | no |

### 19.4 The precision criterion, fully specified

**The quantity.** The corner's integrated cross section and its uncertainty.

    I_0   =  sum_{i in R}  w_i * y_i^(0)           <- FIXED denominator, reference member only
    sigma_k =  sqrt( w^T C_k w )                    <- numerator varies with the member
    rho_k =  sigma_k / I_0

**The weights `w_i` are bin volumes in the kept axes**, `w_i = Δ(E_avail)_i · Δ(W)_i`, and this is
not a convention — the projected object **is a differential density**. The M1 receipt states it:
*"entries are the product of the DROPPED axes' bin widths, so the destination is a DIFFERENTIAL
DENSITY in the kept axes."* So integrating requires multiplying the kept-axis widths back. Omitting
them would silently weight the corner's four `E_avail` bins by their *shape* rather than their
content; their widths are `0.4, 0.7, 1.5, 97.0` GeV from `AXIS_EDGES`, i.e. they differ by more than
two orders of magnitude, so this is a large effect and not a refinement.

**The denominator is FIXED at the reference member's `I₀`** and never recomputed per member.
Otherwise a member that moves the central value changes numerator and denominator together and
`ρ_k` moves for two reasons at once — which would make the criterion insensitive to exactly the
correlated case it exists to catch.

**"X%" — DECLARED as a relative change in the uncertainty, not a percentage-point change:**

    RECOMMENDED FORM:   | sigma_k - sigma_0 | / sigma_0   <=  X        (X is a fraction of sigma)
    REJECTED FORM:      | rho_k - rho_0 |                 <=  X  pp

**Why the relative form.** A percentage-point tolerance has a *different stringency* depending on
how large `ρ₀` happens to be: `0.5` pp is loose at `ρ₀ = 20%` and tight at `ρ₀ = 2%`. So a pp
criterion embeds the observed `ρ₀` into its own strictness — the same contamination shape that made
the conclusion-flip `τ` unacceptable. The relative form is scale-free in the central value and
therefore unaffected by whatever `I₀` D5's region choice produces.
⚠ **Residual, stated rather than hidden:** the relative form still normalises by `σ₀`, a reference
quantity. It is clean on the axis that matters — `σ₀` knows nothing about the generator — but `X`'s
absolute stringency is relative to the reference uncertainty, and that is inherent to any relative
tolerance rather than a defect of this one.

**Measured context for choosing `X`:** on the diagnostic product the corner's per-bin relative
standard deviations are **min 2.88%, median 5.81%, max 12.41%**. These are the measurement's own
precision, reported so `X` can be set against it; **`X` itself remains Joseph's.**

**SCOPE — and this is a hard limit, not a caveat.** `wᵀ C w` is **one scalar functional** of a
matrix with `12·13/2 = 78` independent entries. A criterion on it constrains **one direction** in a
78-dimensional space; `C` can change arbitrarily in the other 77 with `wᵀ C w` exactly fixed. In
particular:

- **it cannot establish stability of the full covariance.** The correlation structure is free to
  move while the integral's variance does not.
- **it cannot establish stability of the 12-cell significance.** That depends on `C⁻¹` contracted
  with `r`, which is dominated by the **smallest** retained eigenvalues, while `wᵀ C w` is dominated
  by the **largest**. The two functionals weight the spectrum in opposite directions.
- So the precision criterion is **necessary, not sufficient**, and it belongs to the same family
  `SPEC` §3.7d already flags: *"Both adopted statistics are functions of the diagonal alone, so a
  MET result on them licenses nothing about `C_Z`'s off-diagonal structure."* This one is better —
  `wᵀ C w` does carry off-diagonal terms — but it is still **one number**, and a MET result on it
  licenses nothing about the significance.

### 19.5 The consolidated D3 / D5 recommendation

**D5 — the region. RECOMMEND: quote on the prespecified `E_avail` region; keep the `W` localization
at central-value level.** Unchanged, and the supporting facts are now measured: the corner as coded
is 12 of 42 cells, `W ≥ 1.8` selects three `W` bins, and that boundary **enters code 2026-06-09, two
days after the first `(E_avail,W)` excess test**, while the `E_avail` question is prespecified
`2026-06-03`. A significance on a boundary the data chose needs selection-aware calibration; a
*localization* statement at central-value level does not. This is what `main_paper.tex:49-51` already
says, so the recommendation costs no claim.

**D3 — restated, because "name `N`" was the wrong request.** Three declarations, not one:

1. **`N = 3`** for the retrospective significance, if and when `y_gen` exists. Justification
   unchanged (§2 D3): 5σ is the discovery convention and is the wrong instrument for a
   generator-comparison claim; 2σ is below print threshold. ⚠ **Conditional on D5 as recommended** —
   3σ on a data-selected boundary is not predeclared.
2. **The acceptance criterion is the PRECISION criterion of §19.4, not the conclusion-flip `τ`.**
   The conclusion-flip calculation is retained as a **labelled retrospective sensitivity**. This is
   the substantive change from my §2 entry, and the reason is that deriving `τ` from what keeps `S₀`
   above `N` reads the reference significance and therefore scales with how favourable the result is.
3. **`X`** — the relative-uncertainty tolerance, against a measured median of `5.81%`.

**Engineering choices I am making and recording, not asking about:** `rcond = 1e-5` with retained
rank 6 (§19.1); the first-order statistic with a single reference pseudoinverse and an
`UNASSESSABLE` gate (§19.2); bin-volume weights and a fixed `I₀` (§19.4); and the destination mask
`receiving-cells`.

**Still blocked, and by what:** the retrospective leg on `y_gen`; both legs on the cause-3 members,
which do not exist (`status: UNRESOLVED`, requirement *"build all members"*); and `X` and `N` on
Joseph. **Pinning and P2 remain unresolved pending `58524334` and are not decided here.**

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
| M-R | M1 **diagnostic** projection — the cycle-breaker | **RUNNABLE NOW**, authorized 2026-09-18 | `run_m1_diagnostic.sh`: nine refusals incl. R5 admission; `runClass` written **into** the product; 36 tests; publication-path rc 3 re-measured by a ratchet | D5 (the region), and the destination-mask declaration — **not** adoption |
| M-S | Determinism configuration, established **and tested** | **EXECUTED** — job `58507305`, `0.25` CPU task-h | `z_determinism_probe.py`: 3 arms × `1,2,4,8` threads, own process per cell, row floor, `UNAVAILABLE` never "no differences"; 15 tests. **Measured precursor: the production factory pins NOTHING and `n_jobs=None`** | — |
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

## 12. ⚠ THE PRESERVED CANDIDATE COVARIANCE DOES NOT EXIST AS AN OBJECT — measured 2026-09-18

Joseph's grant authorizes *"provisional projections and counterfactuals **from the preserved
candidate covariance**"*. I went to run the diagnostic M1 and found **there is no `C_Z` product to
project from.** This is not an obstacle to the grant so much as a false premise inside it, and it is
mine to have not checked earlier: I have been citing `C_Z`'s spectrum for weeks — `λ_min =
−1.2750516323643892e-90`, 5,214 negative eigenvalues of 10,694 — as though the matrix were on disk.
**Those are recorded measurements of an object that was computed in memory and never written.**

**Established three independent ways, because it is a negative claim.**

1. **The pilot's own receipt.** `z_pilot_20260915_a3/bridge.json`: `out_path` is
   `z-null-source.npz` and `persisted.bytes_persisted` is **`1,119,552`** — the `1.05` MB of null
   operands plus support mask that `SPEC` §5.8d already names as the pilot's product. Its
   `z-provenance.json` records `adoptable: **False**` and
   `scientific_acceptance: **NON-PASSING**`, by the pilot itself.
2. **Directory contents.** The `a3` directory holds four files: `bridge.json`, `z-manifest.json`,
   `z-null-source.npz`, `z-provenance.json`. No `.root`.
3. **A covering search, with a positive control.** All `*.root` at `≥ 800` MB under the
   `nd-unfolding` data root: **469 files**, so the search is not vacuous. The newest
   assembled-covariance-shaped products (`892` MB = `10,694²` doubles) are dated **2026-08-11**, in
   `readopt_20260811_footing/` — those are **G's** adopted mean-centered and cv-centered products,
   the *parent*. The newest large Z-lineage object is
   `z_precursor_20260914/unified_throw_cov_5d.root`, `2,668,265,910` bytes, 2026-09-14 15:53 — the
   **throw precursor** (three `10,694²` matrices, `SPEC`'s `2.67` GB figure), **not** `C_Z`.

**What IS preserved, and it is enough to rebuild from:** the eight digest-bound input sources named
in the pilot's `z-manifest.json` (support, active, central, stat, ml, throw, parent, null), the
`2.67` GB precursor, the support mask and row order (`mask_sha256 eed021e9…`,
`row_order_sha256 61a7c9fd…`), and the manifest itself at `sha256 df440c3b…`. **Nothing is lost.**
The pilot's own band inventory in `z-provenance.json` also independently reproduces §10.1's 45-band
measurement, from a different file than the one I read.

### 12.1 The consequence: one bounded request stands between the grant and the diagnostic

`nd-unfolding/z_build.py` **on `main`** is the assembler, and it is complete: `main()` requires
`--manifest --out-cv --out-mean --receipt-cv --receipt-mean --out-null` and `_write_product` writes
real `TH2D`s with a `metadata_json` object. It does not need writing. It needs **running**, on the
manifest the pilot already produced.

| | |
|---|---|
| **What it measures** | Assembles `C_Z = D(ΣV)D + ΣR + ΣA + C_stat + C_ML` from the eight digest-bound sources and **persists** both centering variants plus the null operands |
| **Why it is needed now** | `τ` needs M1, M1 needs `C_Z`, and `C_Z` is not on disk. It is the single missing link between Joseph's grant and the acceptance question the grant exists to resolve |
| **Wall anchor — MEASURED** | The pilot's `ElapsedRaw 1037 s` for the 45-band assembly **plus two eigendecompositions**. Persisting adds a `1.78` GB write (two `892` MB products) |
| **Memory anchor — MEASURED** | The pilot's **`49.73` GiB** peak, and its own recorded lesson that *"any future sizing starts from 49.73 GiB"* because its prediction was low by more than an order of magnitude. Request **`96G`** |
| **Shape** | `1 node, --qos=shared --constraint=cpu --ntasks=1 --cpus-per-task=32 --mem=96G --time=01:00:00` |
| **Reservation** | **`1.00` CPU task-h** = `1 task × 1.00 h`, in the governing unit. `0.25%` of the measured `403.6775` headroom |
| **Disk** | `≈ 1.78` GB into a `DIAGNOSTIC`-marked directory. ⚠ `pscratch` is at **`16.02` / `20.00` TiB = 80.1%**, so this is `0.009%` of the filesystem but the quota deserves naming |
| **Grade it would carry** | **None.** The pilot already recorded this construction `NON-PASSING` and `adoptable: False`, and re-running it produces the same candidate. Construction is not adoption, and this is not a repeat-until-it-passes: the purpose is to obtain the **object**, not a different verdict |

**What a terminal result would NOT authorize:** it would not adopt the trunk, would not regrade the
pilot's `NON-PASSING`, would not supply support `C_Z` never had, and would not make the resulting
`C_low` quotable — `AGENTS.md:27` requires the quotable `(E_avail,W)` covariance to be projected
from the **adopted** trunk and `:30` quarantines the existing one outright.

**Why I have prepared this rather than launched it**, given that the grant plausibly covers it as
*"necessary implementation … for the scalar-5D uncertainties and required projections"*: it writes
`1.78` GB into the shared data tree, and it constructs **the central artifact of the whole
campaign** — the object the adoption decision is about. Doing that on the reading that a grant
"seems to cover it" is not a routine step. **The two smaller items in this session's grant I did
execute** (`0.0011` + `0.25` task-h), because those were diagnostics that wrote nothing into a
product tree.

**One word authorizes it.** The command, ready to run against the worktree already checked out at
this session's HEAD:

    MNV_CODE_ROOT=/pscratch/sd/j/josephrb/MINERvA-OmniFold-zdet-20260918
    python3 nd-unfolding/z_build.py \
      --manifest  <pilot a3>/z-manifest.json \
      --out-cv    <DIAGNOSTIC>/z_candidate_cvcentered_DIAGNOSTIC.root \
      --out-mean  <DIAGNOSTIC>/z_candidate_meancentered_DIAGNOSTIC.root \
      --receipt-cv <DIAGNOSTIC>/z_candidate_cv.receipt.json \
      --receipt-mean <DIAGNOSTIC>/z_candidate_mean.receipt.json \
      --out-null  <DIAGNOSTIC>/z_candidate_null.npz

⚠ **The cv-centered variant is the one M1 should project**, as an engineering choice recorded here:
`AGENTS.md:29` rules that *"mean-centering alone is disqualified"*, and `z_build.py` writes both, so
both are kept and only one is used. That is not a scientific ruling — it follows from a front-door
rule already in force.

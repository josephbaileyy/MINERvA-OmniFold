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
| M-J | Lineage / two-ensemble question | **OPEN** | parent is mean-centered, `uthrow_source` 2026-08-06; pilot throw input is the 2026-09-14 precursor | `[cb0b6b]` |
| M-K | Cause 1, 2, 4, 5, 6, 7 dispositions | **1/2/4 criteria DRAFTED** (`230aecf7`, claimed tolerance-free, under assessment); **5 and 7 evidence COMPLETE** (`80b464ca` + my `Σ_A L_b` trace) | cause 7: laterality measured on payload, `measured lateral set == p4_lib.BANDS` True, 10 endpoints verified, lateral sum traced to the **active** blocks with `active_total_eq_sum5 = 0.0`; cause 5: VL66 falsifier NEGATIVE across Z's 15-module closure | **two rulings** (cause 7 sufficiency, cause 5 §6.1 disposition); cause 6 |
| M-L | `ε` / null acceptance | **BLOCKED BY CONTRACT** | every route closed (packet §2.1) | Joseph's §6.4 route ruling |
| M-M | Trunk adoption | **NOT REACHED** | — | M-F…M-L |
| M-N | M1 product `(E_avail, W)` | **NOT REACHED** | — | M-M + M-G, then compute authorization |
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

**Exact change.** Declare: the deferred claim is asserted at `≥ Nσ` (you name `N`); `τ` is then whatever
projected-correlation movement leaves the corner significance above `N` — a calculation performed once
on M1, not a judgement. Record it as the conclusion-flip input in the cause-3 packet.

**Your approval authorizes:** the threshold declaration, which converts `τ` from blocked-on-judgement
to computable-from-M1. It authorizes no production.

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

**No compute is requested by this plan.** Standing boundaries hold: any single job under 12 h is
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
| Reservation bound | **≈ 2.0 CPU task-h** (8 CPUs × 0.25 h) | Enforced-cap pricing, `SPEC:3140` — a request bounds an attempt, not a completion |

⚠ **What is measured and what is not.** The **arithmetic** is now measured, not derived: `0.324 s`
and `1.020 GiB`. **The ROOT I/O of a ~900 MB `TH2D` is NOT measured** — no interpreter available here
has ROOT — and it is the dominant unknown. The `16 G` and `15 min` margins exist for that unmeasured
leg, not for the arithmetic, which uses 6% of the memory request and 0.04% of the wall. Stated this
way because the pilot's recorded lesson is that a *derived* sizing was low by more than an order of
magnitude; this one is derived only where it could not be measured.

**Against accounting:** the campaign drew ~77.0 of 393.5 authorized CPU task-hours, so ~2 task-h is
0.5% of the remaining headroom. **The no-automatic-retry rule applies unchanged**: a failure returns
for a new decision rather than resubmitting.

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
| **R1** | Cause 7 sufficiency — is active coverage of the five sufficient given the four vertical bands' CV-selected support? | ruling (`SPEC`) | none offered; evidence complete | cause 7 |
| **R2** | Cause 5 §6.1 disposition, after the completed trace | ruling (`SPEC`) | none offered; falsifier NEGATIVE | cause 5 |
| **R3** | ⚠ **`SPEC` contradicts itself** — `:1010-1011` says the cause-4 guard enforces condition **3**, `:1237` says condition **4** | spec owner | `:1010` is the more defensible (it defines the guard; `:1237` summarises a receipt row) | cause 4 implementation |
| **R4** | Cause 6's stat/ML reuse | scientific | none offered; note the audit's *"rather than assume reruns"* — the default assumption is the expensive one | cause 6 |
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

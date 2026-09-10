# RECOMMENDATION 2026-09-10 — Z's unresolved scientific acceptance criteria

**Author: the `z-criteria-designer` lane, `owners.tsv:14` at `c18f9daa`
(`z-criteria-designer | Z scientific acceptance criteria | z-criteria-designer session [91eaa2] |
Joseph | assigned`), read from the file at that commit rather than taken from the assignment
relay.** That row records **assignment, not approval of anything below** — Joseph's own terms, quoted
by the orchestrator: *"These assignments authorize the work described below, not cluster compute,
criterion adoption, grading of a production artifact, or publication changes. I retain scientific
approval."* `owners.tsv` is read by `docs/orchestration/control_plane_lint.py` and nothing else;
`whose_row.py --check-owners` measures a different set (ledger-row owners) and is **not** a
validation of this row.

**NOTHING HERE IS ADOPTED, GRADED, OR AUTHORIZED. No compute was launched. I do not grade my own
criteria — that is the `z-independent-assessor` lane's function, and it derived its own requirements
before reading this.**

**Base of measurement, stated precisely rather than as a single sha.** Every measurement below was
taken at **`c18f9daa`**, in an isolated worktree (`worktree-z-criteria-owner-20260910`). This document
lands on **`923e1323`**, and exactly one measurement moved across that boundary — the `SPEC` §7 defect
in §0, repaired in rev. 22, which I re-verified at `923e1323` myself rather than accepting on report.
Nothing else in the interval touched `owners.tsv`, the launchers, the note's `.tex` set,
`receipt_candidate_stamps_5d.json`, `p4_lib.py`, `uq_math.py` or the `z_*` modules. **I do not
re-assert the other measurements at `923e1323`, because I did not re-run them there.**

**One gate will report a failure that is not this commit's, and it is measured rather than asserted.**
`python3 docs/orchestration/generate_manifest.py --check` exits **`1`** with `OUT OF DATE` on a
**completely clean tree at `c18f9daa`** — 0 untracked, none of this lane's work present. So
`MANIFEST.tsv` staleness on `main` is **pre-existing**; another lane has deliberately declined to
regenerate it, because a mass regeneration would sweep in unrelated rows, and has routed it to Joseph.
**This commit therefore does not carry a regenerated `MANIFEST.tsv`** — bundling a 1,531-line
inventory rewrite with a scientific recommendation would obscure this diff and silently settle a
question routed elsewhere. Routability is secured the way the convention actually requires: a
`MANIFEST-overrides.tsv` row and a `CATALOG.md` pointer, both irreducibly manual, neither checked by
any hook. *(That exit code is read from the process, not through a pipe. A pipe reports `tail`'s
status — `0` — and I made exactly that mistake once before catching it.)*

---

## CITABLE FOR / NOT CITABLE FOR — read before quoting anything below

**CITABLE FOR**

- the **`rho` bound** of §2.1 and its **projection monotonicity** of §2.2 — two theorems, each
  checked in both directions with controls, by
  `state/probe-z-criteria-acceptance-mathematics-20260910.py`;
- the **closed-form critical `rho`** of §5.3, which makes the significance criterion complete
  **modulo a threshold** rather than blocked on one;
- the **normalizer argument** of §4.1 (three committed sqrt-traces exist for one null, spanning
  `20.9%`);
- the **F7 decision-margin measurement** of §4.2 and its normalizer-free factor `1.7957e11`;
- the **thread-environment measurement** of §4.4 — what the three launchers *declare*, and that
  `make_estimators` pins nothing;
- that the withdrawn `5.00e-41` reproduces from `values.tex:115`'s macro and **not** from G's
  measured mean shift (§4.3);
- the **projection-builder census** of D.1(a) — **four** production/consumer construction sites, not
  three, with `p4_lib.py:1484` identified as a control rather than a rival;
- the **reconciliation** of §0.0, including that the string `rev. 5` does not occur in the document
  being called that;
- the **requirement lists** and the **ordered minimum measurements** of §7.

**NOT CITABLE FOR**

- any adopted boundary. Four are withheld in `z_contract.Z_BOUNDARIES` and this document adopts
  none of them; it **recommends** dispositions.
- **any claim that the four `\gbdtFive*` macros have no scientific use.** They are not printed in
  any tracked `.tex` today **and they are staged for a post-adoption note update**
  (`PROCEDURE-gbdtFive-macro-update.md`). §3.1 states why the tempting inference is circular and
  must not be drawn from my measurement.
- any current significance, `chi2`, `p` or `ndf` for any MINERvA projection. **None exists in this
  tree.** The `chi2_0`/`ndf` values in §5.3 and in the probe are **synthetic placeholders** exercising
  a formula.
- any statement that the execution envelope is inadequate. §4.4 establishes that a bound argued from
  *"the configuration is pinned"* **cannot be made today**; that is a statement about the evidence,
  not about the world (`SPEC` §3.7a rev. 19).
- the equivalence or designation of any projection map `M`.

---

## 0.0 RECONCILIATION WITH THE EXISTING LANDED PROPOSAL — read this before §0

**A second lane's document already occupies part of this subject, it is on `main`, and it is routed.**
`docs/orchestration/PROPOSAL-20260908-z-sensitivity-criteria-over-publication-projections.md`,
sha256 **`3fc9fb87b170887cdc8be870f801e7228113c35669be455401bdb7f1e6e9ac4c`** measured at `c18f9daa`,
`LIVE`/`open` at `MANIFEST-overrides.tsv:117`, routed from `CATALOG.md:178`. It is the
**z-operand-schema lane's** work and it predates this lane's assignment. **Two lanes drafting one
contract is how a repository acquires two conflicting criteria sets, with the winner decided by push
timing rather than by evidence. So this section chooses, rather than landing beside it.**

**⚠ ONE CITATION CORRECTION FIRST, because it will otherwise be propagated.** That document is
being referred to in coordination traffic as *"rev. 5"*. **The string `rev. 5` occurs zero times in
it** (measured, case-insensitive); its highest self-declared revision label is **`REV. 4`**. The sha
above is the agreed object. **Cite it by sha, never by a revision number it does not carry.**

**THE CHOICE: this document SUPERSEDES its candidate-criteria role, and RETAINS it as evidence.
Scoped, item by item, and its bytes are not touched.**

| what | disposition here |
|---|---|
| its §1, §1a, §1b — the consumer, and the distinction between what the publication **intends** to consume and a **validated current path** | **RETAINED and CITED.** Part D rests on it. Nothing here replaces it |
| its §2a, §2c — that `s_agg`, `s_med` and `s_eig` cannot bound an inverse-quadratic consumer, and that a spectral summary cannot determine the quadratic form | **RETAINED and CITED.** §2.1's third control is its `diag(1,4)`/`diag(4,1)` counterexample, re-run |
| its §4a — that printed precision establishes nothing scientific, in either direction | **RETAINED and CITED.** §5.2 |
| its §4c — record the `pinv` cutoff, report the retained rank, treat a rank change as a reportable event | **RETAINED and CARRIED FORWARD** as D.1(c). This is the one element I judge already correct and separable |
| its §3 C-1, C-2, C-3 — the three candidate criteria | **SUPERSEDED.** C-1 becomes the **reported** quantity and `rho` becomes the criterion (§D.2), because C-1 is a sampled maximum with no bound and no coverage argument, and its own §2b leaves `s_proj`'s coverage **unresolved with no method offered**. §2.1–§2.2 close that question by changing the statistic rather than by searching for a functional set |
| its §6 — the builder-comparison premise | **SUPERSEDED by measurement**, and it predates `FINDING-20260910` (merged `ceb474cc`). As specified it would test agreement over a domain selected for agreement. D.1(a) restates it over **outcomes** |
| its §7 items 1, 2, 3 — its four asks | **ANSWERED or RE-PUT.** Item 1 is answered (§D.2); item 2's threshold is made a **parameter** rather than a blocker (§5.3); item 3 is re-scoped (D.1(a)) |
| its closing *"No criteria owner exists"* | **NO LONGER TRUE**, `owners.tsv:14` at `c18f9daa`. **That is the substantive reason supersession is the right form and folding is not: a proposal addressed to a missing owner is answered by the owner, not merged into.** |

**Why NOT fold this into it as a further revision.** An independent assessment against those exact
bytes has just landed (`origin/lane/z-criteria-independent-assessment-20260910`). Rewriting the
document would leave that assessment pointing at a revision that no longer exists — **destroying the
evidence rather than answering it.** Before recommending a remedy, price what it destroys.

**What I do and do not do to that file.** I propose the classification change — `event_status` from
`open` to `superseded`, `canonical_successor` this document — **and I do not edit a byte of it**,
because paths are provenance and status lives in the manifest, never in the artifact
(`CONVENTION-document-retention.md`). **It is not marked `DEAD`: this document cites it, and the
convention forbids `DEAD` while anything still cites it.** The classification change is mine, is
reversible in one line, and **the assessment against its bytes remains valid** because the bytes are
unchanged.

**Three findings from that independent assessment land on this subject and are incorporated with
attribution rather than absorbed:** its `B1` (the four macros are unused across note, primer **and**
paper, and `sec_systematics.tex:154` is a filename rather than a macro use) — §B.0, where I also
state why the tempting inference from it is circular; its `B3` (no `INCONCLUSIVE` branch and no
vacuous-variation positive control) — B.1(i) and D.2 carry one, by its ruled name; its `B4` (the
builder check's domain-selection defect) — D.1(a). **I have not read that assessment's document; these
are relayed through the orchestrator and are labelled RELAYED wherever they are load-bearing.**

## 0. WHAT THIS ANSWERS, AND THE FORM CONSTRAINT IT HONOURS

`Z_DECISION_PACKET.md` §5 item 1 puts four withheld boundaries with this lane; items 5, 7 and 8 touch
the same four. This document answers them in the four groups Joseph named, and for each criterion
states **quantity, intended scientific use, statistic, denominator, tolerance and its justification,
required population/scope, terminal outcomes**, and an explicit evidence class.

**Evidence classes, used strictly and never blended in one sentence:**

| class | means |
|---|---|
| **PROVEN BOUND** | a theorem. Holds for every admissible input; no measurement can refute it, only a proof error. Each one below is additionally checked numerically in both directions with controls. |
| **EMPIRICAL ESTIMATE** | a measurement. Carries its subject, its `n`, and — where the subject is not Z — the fact that the **direction** of the transfer's difference is not established. |
| **SCIENTIFIC JUDGMENT** | a choice about what matters. Argued, never derived. Named as a judgment so it can be disagreed with on its merits rather than audited for arithmetic. |

**The form constraint, from `SPEC` §6.6 and honoured throughout:** statistic, denominator, precision
target and boundary are put **together**. A boundary detached from its statistic *"would be an
authorization over an object nobody has defined."* Consequently, where I change a packet's
membership, **the packet is re-put whole** rather than amended — §3 is written that way.

**What is FIXED by ruling and is therefore not touched:** §6.1 `(cause 5, Z)`'s disposal-by-decision;
§6.2 cause-1 measure-and-disclose irrespective of magnitude; §6.3's **quantity** — the variation of
the **assembled** covariance `C_Z` under jointly varied estimator baselines, with the narrow scan
diagnostic; §6.4's **form** — scale-relative, fixed before production, justified by controls
established before implementation, never selected from a favourable production result; §6.5's
withdrawal of the multi-draw cause-4 proposal; and `DECISION-20260902`'s no-fourth-grade-token.
Every recommendation below is checked against these and none reopens one. **§3.7 and §5.8 of the
`SPEC` are proposals, not criteria**, so recommending against their contents is inside remit.

**One documentation defect found, reported rather than repaired, and now REPAIRED BY ITS OWNER —
recorded in full because the finding's shape matters more than its resolution.** At `c18f9daa`,
**`SPEC:4014`**, inside §7, still ended *"The bound is the **smaller** of the two."* That is rev. 16's
`min(achievable, acceptable)`, **withdrawn in rev. 17** by §3.7a and replaced in §6.8 by `B <= S` with
`epsilon` argued within `[B, S]` — so a reader routed to §7 got the withdrawn rule, five revisions
after its withdrawal, while item 22 of the same section carried the replacement.

**Repaired in `SPEC` rev. 22, verified here at `923e1323` rather than accepted on report:** `grep -n
smaller` now returns five sites, and every one is the new header note (`:4`, `:142`), an unrelated
use of the word (`:1994`, `:3955`), or the withdrawn wording **preserved verbatim** at `:4030` under
*"preserved here so nothing is erased."* **No operative instance survives, and §7 item 4 is citable
again.**

**Why it survived, and it is a methodological point this document's own probe answers to.** It
survived because it was stated in **prose** rather than in notation: eight of nine sites said
`min(...)` and the ninth said *"the smaller of the two"*, so every search that caught the eight
searched for the **formula**. A literal `grep` for the phrase also misses it, because the inline
`**smaller**` breaks the substring. **Both failures are searches whose FORM excludes the instance
they were meant to find, and in both the empty result read as a refutation.** That is why
`state/probe-z-criteria-acceptance-mathematics-20260910.py` states the **form and the population** of
every search and assertion it makes, and why §B.0 below records the scope of a search next to the
claim drawn from it rather than at the end.

---

# PART A — COVARIANCE-CONSTRUCTION REQUIREMENTS

These govern whether `C_Z` is the object it claims to be. **They are logically prior to every
sensitivity question**: a tolerance on the movement of a quantity is meaningless if the quantity was
never constructed as specified. Most of Part A is already fixed by `SPEC` §1.3a/§1.3b/§3.3 and is
recorded here only to mark it closed. **Two tolerances inside it are genuinely open, and I propose
both.**

## A.1 The `g^c` reconstruction gate — tolerance PROPOSED

| field | |
|---|---|
| **quantity** | the elementwise agreement between the producer's recorded `hInflation_g` and a `g^c` **independently reconstructed by the validator from the throw operands** — `diag(C_unified)`, `diag(C_blocksum)` and `hJointMeanShift` — by §1.3a's formula, **separately for each centering variant** |
| **intended use** | this is the gate that makes the other four inflation gates capable of failing. `SPEC` §1.3b proves the set is jointly satisfiable by an **uninflated** object (`g ≡ 1` passes closure, `g >= 1`, the zero-denominator rule and PSD). Without this gate a Z that discarded the whole inflation ships as an inflated one |
| **statistic** | per-element relative difference `\|g_recon − g_prod\| / g_prod`, and its **maximum** over the reported support, per variant |
| **denominator** | `g_prod` elementwise; `g^c >= 1` by construction (§1.3a), so the denominator is bounded away from zero and no zero-denominator rule is needed |
| **tolerance** | **exact bitwise equality where the validator reads the same stored operands; otherwise relative `1e-12` per element**, with the count of exceedances and the argmax bin reported |
| **justification** | **PROVEN BOUND + SCIENTIFIC JUDGMENT.** `g^c` is a fixed six-operation expression per bin — one square, one add, one `max`, two square roots, one divide — so its forward relative error on shared operands is bounded by about `6 * eps ≈ 1.33e-15`. `1e-12` leaves roughly `750x`. **The judgment is the margin, not the form.** What must NOT be used is `1e-9`: that is the standard-P4 **closure** tolerance for identities that are **sums over many components** (`p4_build_components.py:140-171`), and `SPEC` §1.3b warns in its own words that it *"may not be reported as an `M`-leg materiality threshold"*. Applied to a six-operation expression it is six orders too loose, which is enough room for a real defect to sit inside a green gate |
| **population** | every reported bin, both variants, each reconstructed **from its own operands** — never one variant reused for the other. `SPEC` §3.4(ii)'s worked fixture (`v_blk = 1`, `v_uni = 4`, `mean_shift = 1`, giving `g^mean = 2` against `g^cv = sqrt(5)`) is the only mutation that separates a correct validator from a reuse-faulty one |
| **terminal outcomes** | **PASS** / **ABORT**. There is no third state and no note-and-continue: `SPEC` §3.3 condition `4b` is a reject-Z condition, so a failure precedes grading rather than entering it |

## A.2 The inflation closure identity — statistic FORM corrected, tolerance retained

| field | |
|---|---|
| **quantity** | `C_Z^c − C_Z^blocksum == (g^c_i g^c_j − 1) * (Sum_{b in V} C_b)_{ij}` |
| **intended use** | the one gate that catches a **double-counted or mis-scoped vertical set** |
| **statistic** | **two numbers, not one: (i)** the relative Frobenius residual `‖LHS − RHS‖_F / ‖RHS‖_F`; **(ii)** the **maximum per-element relative residual**, with its `(i, j)` and the count of elements exceeding tolerance |
| **denominator** | `‖RHS‖_F` for (i); `\|RHS_{ij}\|` for (ii), restricted to `RHS_{ij} != 0` with the zero-set cardinality reported |
| **tolerance** | relative **`1e-9`** on both legs |
| **justification** | **PROVEN BOUND on the form, EMPIRICAL on the numeral.** `1e-9` transfers correctly *here* and not in A.1, because this identity **is** a sum over many components, which is the structure the standard-P4 closure tolerance was set for. **The correction is the second leg.** A Frobenius-relative residual is an aggregate: it can be satisfied while a small number of elements are badly wrong, since a `10,694^2` matrix has `1.14e8` entries and a handful of large errors move the Frobenius norm imperceptibly. An agreeing aggregate is not agreement — the same failure shape `SPEC` §3.7d names for the diagonal statistics, one level down |
| **population** | all `10,694^2` entries, both variants |
| **terminal outcomes** | **PASS** / **ABORT** (`SPEC` §3.3 condition 2) |

## A.3 Requirements already fixed — recorded closed, with their measurement gaps named

| requirement | state | the gap, if any |
|---|---|---|
| `mask_digest(Z) == mask_digest(G)` and `row_order_digest(Z) == row_order_digest(G)` | **FIXED**, `SPEC` §3.3(1) | ⚠ **the OPERAND is unbound.** §1.3d measures that `hRowIndex5D` and `hXSecND_flat` are **not** among G's 13 recorded keys, so *"read from G"* has no referent. Both digests must be reconstructed from G's production-CV input and **that input's identity bound first**. This is `PM-4`, `Z_DECISION_PACKET` §5 item 6 |
| `V`, `R`, `A` pairwise disjoint and exhaustive | **FIXED**, exact set equality, implemented at `z_contract.check_band_partition` | measured `\|V\|=13, \|A\|=5, \|R\|=27 = 45` against **S's** manifest. `R` is a **complement**, so it is only as good as the family list it complements; `PM-5` closes it on G's own `combined_source` |
| band lists imported, never retyped | **FIXED**, `SPEC` §3.3(8) | a **conflicting** six-entry lateral inventory exists at `pet_lateral_correction.py:42-43`, adding `MinosEfficiency`. Import `p4_lib.BANDS` and `adopt_unified_5d.VERT_BANDS` |
| PSD **of the inflated object** | **FIXED as a requirement**, `SPEC` §3.3(6) | ⚠ **not recorded as a gate.** `adopt_unified_5d.py:150-165` checks `ev[0] >= -1e-12*ev[-1]` but sits **outside** the P4 gate list, so no receipt carries it. **Recommendation: make it a receipt-recorded gate**, which costs nothing and closes a "checked but unprovable" hole |
| `C_unified` enters only through its diagonal; `C_seed` never a budget block | **FIXED**, `SPEC` §3.3(5), §1.3a properties 2–3 | — |
| both centering variants, `--out` always explicit | **FIXED**, `SPEC` §3.3(14) | `adopt_unified_5d.py:79-80` **defaults** `--out` and opens `RECREATE`; a defaulted `--out` is a destructive overwrite |

**One opportunity, recorded as an opportunity and not as a saving** (`SPEC` §5.8f's rule): if the PSD
gate of A.3 is implemented as `eigvalsh` rather than Cholesky, the **full spectrum is already
computed**, and both `s_eig` and the baseline factorization §2.1's statistic needs are byproducts.
That row is unpriced in `SPEC` §5.2, so this is a conditional.

## A.4 A requirement Part A did not previously carry: projection-readiness

**This is new, and it follows from what Z is for rather than from how Z is built.** `AGENTS.md:27`
quarantines the historical 3D covariance and generator significances with *"The quotable covariance
must be projected from the final adopted, selection-complete 5D trunk"*, and Z is the candidate for
that trunk. So `C_Z`'s declared use is **projection**, and a construction requirement follows.

| field | |
|---|---|
| **quantity** | the identity of the projection operator, and the orphan-bin census **in both directions**, for every projection Z's receipt claims support for |
| **intended use** | prevents a covariance being accepted as a trunk while the map that would draw a number out of it is undesignated |
| **statistic** | for each declared projection: the designated builder's module, symbol and sha; the **outcome** it returns (`refuses` / `returns-with-drops` / `returns-clean`); the count of reported high bins mapping to non-reported low bins **and** of reported low bins no high bin reaches; the fraction of `sqrt(Tr)` those bins carry |
| **denominator** | `sqrt(Tr C_Z)` for the carried fraction; bin counts are absolute |
| **tolerance** | **no tolerance — this is a census with an ABORT condition.** A nonzero count in either direction is a **reportable event that blocks a bare pass**, and `SPEC` §2.6c item 3 already requires the census "in each direction" for `(cause 6, Z)`'s `M` leg |
| **justification** | **EMPIRICAL, measured.** `FINDING-20260910-projection-builders-agree-numerically-and-diverge-on-refusal.md`: `p4_lib.build_projection_M` and `project_cov_nd.build_projection` produce **byte-identical** `M` on canonical edges at three mask densities, and take **opposite actions** where support masks do not nest — the first raises, the second silently drops five source cells. Its own amendment 2 is the load-bearing part: **the comparison's unit must be the OUTCOME**, because a runner that skips the refusing cases tests only the domain selected for agreement, and no exit code catches that |
| **population** | every projection the receipt claims, not one exemplar |
| **terminal outcomes** | **CENSUS RECORDED** (a nonzero count blocks a bare pass) / **ABORT** if the operator is unnamed |

---

# PART B — ESTIMATOR-BASELINE SENSITIVITY

`SPEC` §6.3 fixes the **quantity**: the variation of the **assembled** covariance `C_Z` under jointly
varied sweep-side and throw-side estimator baselines. That is not reopened. What is open is the
statistic, the two legs, and the boundaries — `cause3_agg`, `cause3_med` and `cause3_corr` in
`z_contract.Z_BOUNDARIES`, all withheld.

**This part is a recommendation ON `SPEC` §3.7d's reserved disposition**, which §6.7 says is ready to
be put and which `SPEC` §5.8d states as *"Joseph answers §3.7d's disposition with 'add a leg' rather
than 'narrow the claim'."* **I recommend "add a leg", and the packet is re-put whole below.**

## B.0 The ground, stated first, because the tempting ground is circular

**The durable ground is §3.7d's own finding, and it is a statement about what the two proposed
statistics CAN MEASURE — true whatever any document does.** `s_agg` reads `Tr C_Z`; `s_med` reads
`diag(C_Z)`. Both are functions of the diagonal alone. Re-measured independently in this lane's probe
(control B): against `SPEC` §3.7d's own counterexample — `I_2` versus `[[1, 0.9], [0.9, 1]]`, identical
diagonal and identical trace — **`s_agg` and `s_med` return exactly `0.0`, so they pass at any
boundary including the withdrawn `0.0861%`**, while the quantity the publication path consumes moves
by a factor of `5.26`. **No choice of `delta` repairs this. The statistics do not contain the
information.**

**⚠ AND HERE IS A GROUND I MEASURED, ALMOST USED, AND AM WITHDRAWING BEFORE USE, because it is
circular.** I measured, over all 24 tracked `.tex` files and the three `build_all.sh` targets, that
`paper_body.tex` contains `0` `\input`, `0` `gbdtFive`, `0` `sqrt` and `0` `e-38`, and that
`\gbdtFiveBlockMedian`, `\gbdtFiveAdoptTrace`, `\gbdtFiveCVTrace` and `\gbdtFiveMeanShift` are defined
in `values.tex:112-115` and used in **no other `.tex` file**. Those measurements are correct and are
citable. **The inference "therefore the quantities have no scientific use, therefore no use-based
tolerance is derivable" is not.** A covering search over all file types finds the four macros in 39
files, including `PROCEDURE-gbdtFive-macro-update.md` — titled *"updating the four `\gbdtFive*` macros
**when the J28 re-roll is adopted**"*, header *"This is a contingency again, not a procedure about to
be used"* — and `MAP-20260817-gbdt-note-section-blockers.md`, which works out how those values move.
**The macros are staged for a note update gated on adoption.** Reading their absence from the `.tex`
body as absence of use reads a **blocked** pipeline as a **finished** one, and it closes a loop: the
acceptance criterion would be relaxed because the adoption it gates has not happened. **A use-based
tolerance for those two summaries is therefore DEFERRED, not underivable** — a weaker and more
defensible claim. The correction is the orchestrator's; the measurement scope error was mine, and it
is my catalogued one — an absence claimed wider than the search that found it.

## B.1 The packet, re-put whole

**Two binding legs, both correlation-sensitive. Four reported diagnostics, gating nothing. One exact
display test, replacing the two withdrawn format-derived boundaries.**

### B.1(i) LEG 1 — `rho`, the relative spectral perturbation in the baseline's own metric

| field | |
|---|---|
| **quantity** | how far `C_Z^(k)` sits from `C_Z^(0)`, measured in the metric `C_Z^(0)` itself defines |
| **intended use** | it **bounds the quantity the publication path consumes.** `PUBLICATION-READINESS-20260822.md:885-888` (`PR-G10`, path CRITICAL) requires *"recompute generator comparisons and significances only from the governing adopted covariance"*, and the consumed form is a quadratic form in a pseudo-inverse (`eavail_generator_significance.py:107,132`) |
| **statistic** | `rho = max_{k in K} ‖ (C_Z^(0))^{-1/2} (C_Z^(k) − C_Z^(0)) (C_Z^(0))^{-1/2} ‖_2` |
| **denominator** | **none, and that is the point** — the normalization is *built into the metric*. `C_Z^(0)` is Z's own as-built `k = 0` member, per `D1b`. The statistic is dimensionless by construction |
| **tolerance** | `rho <= rho_max`, with `rho_max` **derived, not chosen** — see §5.3. It is a closed-form function of the significance threshold, `chi2_0` and `ndf`, so it is not a free parameter and I am not proposing a number for it |
| **justification** | **PROVEN BOUND**, §2.1 |
| **population** | the **finite declared offset set** `K = {0, k_1, ..., k_{N-1}}`, predeclared in full before the first task. No inference to a distribution over offsets: nobody has a model of the offset population. This is `PREDECLARE-20260901-cause3-mii` §1's position, transferred because the same thing is true here |
| **why the maximum** | the claim is quantified over **every** member of `K`, and **a universally quantified claim is graded by the extremum**. A standard deviation can be small while one member is far out, leaving the claim false with the gate green. The statistic follows from the quantifier in the sentence — *not* from the finiteness of the set, which is `SPEC` §3.7b's own correction of a withdrawn argument |
| **terminal outcomes** | **MET** (`rho <= rho_max`) / **NOT MET** (`rho > rho_max`, with the argmax `k` and the extremal eigenvector's leading components reported) / **INCONCLUSIVE**, which covers three distinct cases and must not be read as the nearer of the other two: **(a)** `rho >= 1`, where the bound is vacuous — a *large* perturbation, never a pass; **(b)** `C_Z^(0)` not positive definite on the compared support, so the metric does not exist; **(c)** **`INCONCLUSIVE / VACUOUS SEED VARIATION`** — the branch's ruled name, `PREDECLARE-20260901-cause3-mii-estimator-seed-magnitude.md:230`, beside `INCONCLUSIVE / WRONG FOOTING` at `:226`. `rho == 0` exactly, or a read-back offset set that does not match the declaration. **This branch is the POSITIVE CONTROL and it is why it may not be omitted:** `rho` is small both when the baseline genuinely does not move the covariance **and** when the offset never reached the estimator, and the two are indistinguishable from the statistic alone. It is the `g ≡ 1` shape — a green state reachable without the work being done — one cause over. **A zero spread is evidence the knob never arrived, not a favourable result** (`SPEC` §3.6b item 5) |

### B.1(ii) LEG 2 — `s_corr`, and it binds independently

| field | |
|---|---|
| **quantity** | the change in `C_Z`'s **correlation** structure with the diagonal divided out |
| **intended use** | `SPEC` §3.6b requires the second leg to bind **independently** — *"the same trace can be diffuse or concentrated"*. `s_corr` cannot be satisfied by the diagonal, because the diagonal is divided out; and it is not implied by leg 1, because `rho` is a worst-direction bound while `s_corr` is a whole-matrix aggregate. One can be small while the other is not |
| **statistic** | `s_corr = max_{k in K} ‖ R^(k) − R^(0) ‖_F / ‖ R^(0) ‖_F`, with `R = D^{-1} C_Z D^{-1}`, `D = diag(sqrt(diag C_Z))` — **already implemented at `z_statistics.py:240`, with `correlation_matrix` at `:233`. Do not reimplement** |
| **denominator** | `‖R^(0)‖_F`, Z's own `k = 0` member, named in the same sentence as the numerator |
| **tolerance** | ⚠ **NOT PROPOSED, and this is the one place in Part B where I have no number and say so.** `s_corr` is an aggregate over `1.14e8` entries with no established map to any reported quantity, so §3.6d's ordering rule — statistic first, boundary second, derived for *this* statistic's relationship to the affected reported quantity — is not satisfiable from the tree today. **Recommended disposition: `s_corr` is REPORTED as a binding-leg CANDIDATE with its boundary withheld, and `cause3_corr` stays withheld in `z_contract` until leg 1 has been evaluated on real members.** §7 item 5 names the measurement that would close it |
| **why this is not a retreat to the diagnostic** | leg 1 already carries the *use-facing* bound, so `(cause 3, Z)` is not left ungated by withholding leg 2's boundary. What withholding costs is the independent second binding leg §3.6b requires — so **until `cause3_corr` is declared, `(cause 3, Z)` has one binding leg, not two, and the cell should read `UNRESOLVED` on that ground rather than MET.** Stating that plainly is the honest state and it is weaker than parity with the narrow scan |
| **population / outcomes** | as leg 1 |

### B.1(iii) The two withdrawn boundaries, given the only role they can honestly play

**`cause3_agg` and `cause3_med` should be resolved as EXACT DISPLAY-INVARIANCE TESTS, not as
tolerances.** `SPEC` §3.7b item 4(D) already supplies the instrument and this lane adopts it:

| field | |
|---|---|
| **quantity** | whether the four staged `\gbdtFive*` macro values, **as they would be printed**, are unchanged across `K` |
| **statistic** | **rounding equality** — format each member's `sqrt(Tr C_Z^(k))` and printed per-bin median `q^(k)` at the macro's declared precision and compare the resulting **strings** |
| **denominator** | **none. The test is exact and needs no `delta`** |
| **tolerance** | **none, by construction** — which is precisely why this resolves the two withheld keys without inventing a number |
| **justification** | **PROVEN BOUND on the form + EMPIRICAL on the necessity.** `SPEC` §3.7b item 4(A) measures the half-display-unit rule to be wrong in **both** directions at `12.5%` each under a stated synthetic sampling model — `2.4499` and `2.4501` print differently and are scientifically indistinguishable, while `2.451` and `2.549` print alike and are not. A rounding-equality test has neither failure mode because it tests the printed string itself |
| **terminal outcomes** | **INVARIANT** / **NOT INVARIANT**, with the member and the two strings. **This gates the note edit, not the science.** It answers *"would the staged macro update change"*, which is a real and answerable question, and it must never be reported as *"the covariance is stable"* |
| **and the scientific question it does NOT answer** | how much estimator-baseline sensitivity is scientifically acceptable. That is legs 1 and 2 |

### B.1(iv) Reported diagnostics, gating nothing

`s_agg` (`z_statistics.py:144`), `s_med` (`:157`), the per-bin movement distribution
`m_i = max_k \|sigma_i^(k) − sigma_i^(0)\| / sigma_i^(0)` with `median`, `p90`, `max` and **argmax bin
index** (`per_bin_movement`, `:170`), the per-member table of `sqrt(Tr C_Z^(k))` and `q^(k)`, the
sample SD of each, `s_eig` (`:256`), and the condition number and **retained rank** per member.
**All are descriptive. None grades anything.** Retaining them costs nothing — the two exact legs
already materialize the full matrix — and the argmax bin is what makes concentration visible.

**Joseph's question, `D2`, is unchanged by any of this and is not answered here:** *"What per-bin
movement is acceptable, in what fraction of bins, and why?"* It is a justified tolerance **and** a
justified coverage fraction; rev. 7–15's option (i) supplied one and let the median fix the other at
`50%` by default rather than by argument.

## B.2 The member, and what it costs

**MEASURED, and the mechanism already exists — it was found by reading the launchers, not designed.**
Exactly seven production launchers apply one shared variable, `MNV_EST_SEED_OFFSET`, defaulting to
the archive's seeds: arms 1–4 as `42 + offset`, arms 5–7 as `1000 + offset`. An eighth file names it
and **refuses** it — `sbatch_mii_estimator_scan_5d_bkgaware_gpu.sh:164-165` fails with *"must be
unset for the estimator-seed scan"* — which is an **independent mechanical confirmation of §6.3's
ruling** that the narrow fixed-draw scan is a different object.

So a member is one complete seven-arm round at one integer `k`, and **`k = 0` is Z's own build**, at
no extra cost: `42 + 0` and `1000 + 0` equal the values the unhooked siblings hardcode
(`sbatch_sweep_bank_5d_run.sh:17`, `sbatch_uthrow_run_5d.sh:22`). **No arm is reusable across
members** — arms 1 and 2 also take `42 + offset` as their estimator seed — so there is no cheap
member. The implemented family is the **diagonal** `(42+k, 1000+k)`; a grid would be a second
variable and a launcher change, i.e. **code, not compute**, and `SPEC` §6.8 `D3` closes the grid
question as *not required* rather than answering it.

**Cost of Part B's legs, per member, on top of the two exact legs:** `rho` needs one symmetric
factorization of the baseline (**once**, not per member) and one extreme-eigenvalue solve per member;
`s_corr` needs one elementwise divide and one Frobenius norm over `1.14e8` elements plus about
`0.9` GB resident. **Zero incremental I/O** — `adopt_unified_5d.py:46-49` reads a `TH2D` through
`np.frombuffer`, so `C_Z^(k)` is already resident when `s_agg` and `s_med` are computed. **But "no
new members" is not "free"**, and `SPEC` §3.7d's rev.-19 correction governs where it is charged: the
metered object is a scheduler task identified by nothing but its existence (`r5_meter.py:277` sums
`ElapsedRaw` over distinct task identities), so **nothing about the word "validator" exempts
anything from `R5`**. Folded into a member's own in-scope validation step it lengthens that task's
`ElapsedRaw` and **is** `R5` spend, counted once inside the host task. Run off the scheduler it is
not — *because the venue was named*, never because the work was called validation. **§2.3 gives the
one arithmetic figure that is not negligible and states why its transfer is the least safe.**

---

# PART C — NUMERICAL REPRODUCIBILITY

`SPEC` §6.4 fixes the form. `z_contract.Z_BOUNDARIES["null_epsilon"]` is withheld pending *"an
operating-error bound `B` ... an independently justified scientific cap `S`, the precondition
`B <= S`, and an epsilon argued within `[B, S]`."* **I propose an actual `epsilon`, and I propose it
from the `B` side, with `S` discharged by bounding rather than by measurement.**

## C.1 The normalizer — ADOPT, with a second and independent ground

| field | |
|---|---|
| **quantity** | the relative movement between two re-unfolds of the CV at the identical estimator seed |
| **intended use** | a determinism gate. `unified_throw_cov.py:519-523`'s own message: without it *"the throws cannot be cleanly separated from `C_ML`"* |
| **statistic** | `r_null = ‖x_cv2 − x_cv‖ / ‖x_cv‖` over the reported support — **implemented at `z_statistics.py:52` (`null_ratio`) and `:82` (`reconstruct_null_ratio`). Do not reimplement** |
| **denominator** | `‖x_cv‖`, the same object as the numerator, over the same support predicate (`rep = x_cv > 0`, `unified_throw_cov.py:370`) |
| **tolerance** | §C.3 |
| **justification, and this part is new** | §3.7a already rejects `sqrt(Tr C_Z)` and the per-bin maximum. **A second, independent ground, MEASURED here: `sqrt(Tr C)` does not name a unit.** Three committed sqrt-traces exist for G's one null — the unified throw's `4.443674e-38` (`CRITERIA:196`), the block-sum footing `4.357790406860002e-38` and the inflated total `5.269625166386846e-38` — giving `1.310256e-12`, `1.336078e-12` and `1.104889e-12`, a **`20.9%` spread for the same measured number**. `SPEC` §6.4 itself quotes *"`1.31e-12` of the sqrt-trace"*, which reproduces against the **unified throw's** trace; a reader holding G and computing against G's total gets `1.104889e-12`. The number is right and *"the sqrt-trace"* is a definite description — which is the defect. `‖x_cv‖` has exactly one referent once persisted |
| **terminal outcomes** | as §C.5 |

## C.2 `S`, the scientific cap — discharged by BOUNDING, and the bound is normalizer-free

**The only non-formatting decision channel in the tree is F7, and it is a real branch.**
`uq_math.f7_cv_centered_required` decides whether the CV-centered variant is *additionally
mandatory*; its operand is `‖mean_shift‖`, and `hJointMeanShift` is *"joint throw mean minus CV"*
(`unified_throw_cov.py:575`). So a CV perturbation `dx` moves the mean shift by exactly `−dx`, and
`\| ‖ms'‖ − ‖ms‖ \| <= ‖dx‖` by the triangle inequality — **a PROVEN BOUND**, not a first-order
expansion.

**MEASURED**, from `uq_5d/receipt_candidate_stamps_5d.json` and by calling `uq_math` rather than
restating it (`k = F7_FLOOR_MULTIPLE = 2.0`, strict `>`):

| basis for `sqrt(Tr)` | floor `sqrt(Tr)/sqrt(N)` | G's ratio | `cv_centered_required` | `‖dx‖` that flips the branch | as a multiple of G's null |
|---|---:|---:|---|---:|---:|
| `sqrt_tr_new`, inflated total | `4.166004e-39` | `4.509589` floors | `True` | `1.045496e-38` | **`1.7957e11`** |
| `sqrt_tr_old`, block footing | `3.445136e-39` | `5.453186` floors | `True` | `1.189670e-38` | **`2.0433e11`** |

`N = 160`, `‖ms‖ = 1.878696733368378e-38`, null `= 5.8223488501140625e-50`.

**The factor is NORMALIZER-FREE** — both quantities are norms of vectors in the same space, so it
does not depend on how the null is expressed. **So the F7 channel's scientific cap sits about eleven
orders of magnitude above the observed null, and `B <= S` is discharged by bounding for that channel
provided `B` is within about ten orders of it.** That is `SPEC` §3.7a route (iii): *"If the scientific
cap is loose enough that any plausible `B` sits below it, `B <= S` is discharged without measuring
`B` precisely."* **Zero compute; it is an argument.**

**EMPIRICAL, TRANSFERRED:** G is not Z. G's `N`, bank and slab count differ, and the direction of
the difference is not established. What transfers is the *structure* — an F7 branch with a large
margin — not the number.

**⚠ AND THE CONSEQUENCE IS THE OPPOSITE OF CONVENIENT, WHICH IS WHY IT IS STATED HERE RATHER THAN IN
A CAVEAT.** `SPEC` §3.7a rev. 19 permits `epsilon = S`, "the loosest scientifically acceptable
value". **For this criterion that choice would be a defect.** An `epsilon` near `1.8e11` times the
observed null is a gate essentially nothing can violate — which is **exactly** the `1e-12`-clamp
defect §3.1a measures and §6.4 exists to repair. The null's purpose is not only to protect a
scientific quantity; it is a **determinism and provenance tripwire**, and a tripwire chosen from the
scientific-tolerance side cannot fire. **So `S` is not the binding consideration and `epsilon` must
be argued from `B`'s side** — which §3.7a rev. 19 explicitly permits *"where the claim being
supported is about reproducibility itself rather than about scientific tolerance"*. That is this
case, named.

**And one channel `S` must cover that no document yet names:** the `S` above is the cap for the **F7
branch**. A CV perturbation also enters `C_unified` through the throw deviations and the completeness
division (`unified_throw_cov_5d.py:66-80`). **I have not bounded those channels and do not assert a
mechanism for them** — asserting one without a command run against it is this campaign's catalogued
failure. §7 item 4 names the measurement.

## C.3 `epsilon` — PROPOSED at `1e-9`, in three labelled steps

| field | |
|---|---|
| **quantity** | the acceptance boundary on `r_null` |
| **statistic / denominator** | as §C.1 |
| **tolerance** | **`epsilon = 1e-9`** |
| **step 1 — PROVEN BOUND** | on the reported support, where `x_i > 0` by the `rep` predicate, `r_null <= max_i \|Delta_i / x_i\|`. Proof: `‖Delta‖_2^2 = Sum_i (Delta_i/x_i)^2 x_i^2 <= max_i(Delta_i/x_i)^2 * ‖x‖_2^2`. **So an `epsilon` on `r_null` is implied by the same numeral applied per bin, and is never stricter than it** |
| **step 2 — EMPIRICAL, and it is Joseph's own declared number for the same estimator chain** | `max_i \|Delta_i/x_i\|` is **exactly** the statistic `p4_lib.check_reproducibility:214` computes (`rel = np.max(np.abs(a[m]-b[m])/np.abs(b[m]))`), and Joseph declared its tolerance `REPRO_RTOL_PER_BIN = 1e-9` on 2026-08-07 (`p4_lib.py:93`) against a **measured** floor of `1.9e-11` (`p4_lib.py:196-198`, `REPRO_MEASURED_FLOOR`, job `56471429`, pooled over `106,940` reported bins) — a `52x` margin, and `p4_lib.py:97-105` records it as *"SPECIFICATION from measured spread with nothing currently failing — not a tolerance loosened to rescue a result"*, with the alternative of a documented escape clause considered and **rejected** because *"a gate you can talk your way past is the exact anti-pattern"* |
| **step 3 — SCIENTIFIC JUDGMENT** | adopt the same numeral for `r_null`. It makes Z's null gate **no stricter than the reproduction standard already declared for this estimator chain**, so it cannot fail a run meeting that standard; and by step 1 the direction of the inequality is the conservative one |
| **§6.4 compliance, clause by clause** | scale-relative ✓ (a dimensionless ratio). Fixed before production ✓ (it is fixed here, before Z exists). Justified by controls established **before implementation** ✓ (the floor was measured 2026-08-07/08, for a different purpose, before this lane existed). **Not selected from a favourable production result** ✓ — it predates Z entirely and was chosen by Joseph for the standard-P4 chain |
| **the consistency check, reported AFTER the derivation and not part of it** | I did ask whether G's null would pass. **The gate is breached only if `‖x_cv^G‖ < 5.8223e-41`.** `‖x_cv‖` is **not persisted** (`unified_throw_cov.py:540-579`; the vector is computed at `:369-371` and dropped at `:586`), so G's `r_null` is **UNRESOLVED** and I am not quoting one. The single number that closes this is `‖x_cv‖`, and §7 item 1 already requires persisting it |
| **the falsifier** | if pinned-envelope repeats of the full CV chain show a floor above about `2e-11` for Z's bank, the transfer is refuted and `epsilon` must be re-derived. **The transfer's limits, direction not established:** different subject (standard-P4 5D unfold chain, not Z's throw bank); different comparison (two full re-unfold products, versus two in-process CV re-unfolds inside one `do_combine`) |
| **what it does NOT do** | it does not establish `B`. It selects an `epsilon` that a measured floor on a related subject sits `52x` below. §C.4 is why that is still not a design property |

## C.4 `B` cannot be argued from "the configuration is pinned" today — MEASURED

**`SPEC` §3.7a route (i) — pin the envelope in code and make `B` a design property — deserves the
first look, and it is the only route that *reduces* the quantity rather than measuring it. It cannot
be claimed yet, and the reason is measurable rather than arguable.**

**MEASURED by this lane, in this worktree:**

| launcher | arm | `cpus-per-task` | thread environment exported |
|---|---|---:|---|
| `sbatch_uthrow_run_5d_fast.sh:122-123` | 5, throws | `32` | `OMP_NUM_THREADS=32 MKL_NUM_THREADS=2 OPENBLAS_NUM_THREADS=2 NUMEXPR_NUM_THREADS=2 VECLIB_MAXIMUM_THREADS=2` |
| `sbatch_uthrow_block_5d.sh` | 6, blocks | `32` | **none** |
| `sbatch_uthrow_combine_5d_fast.sh` | 7, combine | **`16`** | **none** |

**Arm 7 is where `--null` computes `x_cv` and `x_cv2`** (`unified_throw_cov.py:369`, `:514`). So the
arm producing the null operands declares no thread environment **and requests half the CPUs of the
arm that produced the throws.**

**Widened to a covering census, because a three-file sample is not a census.** All **11** `.sh` files
referencing `MNV_EST_SEED_OFFSET` — 9 `sbatch_*` launchers and 2 `lib_*` helpers:

| how `OMP_NUM_THREADS` is set | count | which |
|---|---:|---|
| **a literal** | **1** | `sbatch_uthrow_run_5d_fast.sh:122` (`=32`), arm 5 |
| **derived from the allocation** — `${SLURM_CPUS_PER_TASK:-32}` | **2** | `sbatch_unfold_5d_detector_bkgaware_gpu.sh` (arm 3); `sbatch_mii_estimator_scan_5d_bkgaware_gpu.sh` (the launcher that **refuses** the offset) |
| **not set at all** | **8** | arms 1, 2, 4, **6**, **7**, plus `lib_member_resume.sh`, `lib_substitution_fence.sh` |

**The two derived cases are the sharpest part of the census and they are easy to misread as pinning.**
`OMP_NUM_THREADS=${SLURM_CPUS_PER_TASK:-32}` is **allocation-dependence written down**, not a pin: it
makes the thread count a function of what Slurm granted. **So exactly one launcher in the family pins
a literal, it is not arm 7, and arm 7 is where the null is computed.**

**And nothing pins LightGBM as an estimator parameter.** `omnifold_nn_core.make_estimators:143-148`
builds `LGBMClassifier(n_estimators=100, num_leaves=8, learning_rate=0.1, verbose=-1)` with
`random_state` from the seed and **nothing else** — no `num_threads`, no `n_jobs`, no
`deterministic`, no `force_row_wise`/`force_col_wise` (**MEASURED**: those five keywords are the
complete set). The module's own docstring at `:203-204` says LightGBM at these settings is *"otherwise
**nearly** deterministic in `seed` alone"* — the word is its author's — and G's committed null is
`5.8223488501140625e-50`, **not zero**.

**So the statement I can make, and it needs no inference about OpenMP's defaults:** the execution
envelope is **not declared identically across the arms**, and **no mechanism in the tree pins
LightGBM's thread count**. A bound argued from *"the configuration is pinned"* would be a bound over
a configuration that is not fixed. **I deliberately do not claim what the interpreter or LightGBM
does with an unset `OMP_NUM_THREADS` on those nodes — that is unmeasured, and my recommendation does
not rest on it.** Two launcher comments record that LightGBM **ignores** `OMP_NUM_THREADS` and grabs
all cores — `uq_fps/corrected/run_fps_uq_packed.sh:3-5` (*"5D thrash lesson: load 571 at CONC=12"*,
mitigated with `taskset`) and `run_4d_replicas_packed.sh:22-23` — which is **RELAYED**, from a
different subject, and is the reason the count must be pinned as an **estimator parameter** rather
than an environment variable. It is not my measurement and my bound does not lean on it.

**Recommended prerequisite, and it is upstream of any tolerance: pin the envelope in the arm that
produces the operands, and declare the pinned set in the receipt.** `z_reproducibility.Z_REPRO_KNOBS`
already proposes exactly three — `deterministic=True`, `force_row_wise=True`, `num_threads=1` — each
with its reason, and `MEASURED_BACKEND` records a 2026-09-07 read on `login07` under
`~/.conda/envs/root_6_28` (LightGBM `4.6.0`) finding all three **recognised** by the parameter table
and **stored** by the sklearn wrapper. **That module's own caveat is the operative limit and I adopt
it verbatim rather than softening it:** it *"does NOT verify that a Z run would reproduce — it
verifies that the knobs exist, are recognised and are accepted, which is the precondition for pinning
them and not evidence that pinning them suffices."*

**⚠ And pinning is a SCIENTIFIC act, not hygiene.** `z_reproducibility.py`'s docstring states it:
*"Pinning the reduction order changes the numbers Z produces relative to the historical chain. That
divergence must be declared with Z's build."* Since G is the `M`-leg comparison baseline for all
seven cells, a pinned Z is compared against an unpinned G — **which is a declared divergence that
belongs in the receipt and in every `M`-leg statement, not a free improvement.**

`Z_CONSTRUCTION_PLAN` §4.4a's six items are, in my assessment, the correct requirement set for `B`,
and item 3 is the one I re-measured above. I add nothing to that list; I confirm it and note that
**items 1 and 2 are the load-bearing pair**: if the pinned chain is not bit-identical **across
allocations**, route (i) delivers no design property and route (ii)'s three gaps reopen in full.

## C.5 Presence, finiteness, persistence, and the abort rule — ADOPT as written

`fixed_seed_null_checked` present and `1`; `fixed_seed_null_norm` present and finite; `‖x_cv‖`
present, finite and **strictly positive** — a zero denominator **aborts**, and it is the opposite of
§1.3a's `g = 1` rule because here a zero denominator means the CV is empty. **Any failure aborts;
none is recorded as a note.** The writer already distinguishes *"checked and zero"* from *"not
checked"* (`unified_throw_cov.py:553-563`) and Z fails closed on `checked == 0`.

**And the ratio must be independently reconstructible from Z's OWN product** (`SPEC` §3.3 `11b`).
The throw writer does not persist `x_cv`, `x_cv2` or the support predicate today; **Z's writer must**,
at `1.05` MB against a `2.668` GB product. Without it the validator can only read the producer's own
number back and compare it with itself — the shape §1.3b rejects for `g`. An **external** check
against a production ROOT's `hXSecND_flat` is `11c`, reported as agreement **only** where elementwise
identity is established, `UNRESOLVED` otherwise, and **never** a cardinality check standing in for an
identity: `adopt_unified_5d.py:116-121` asserts `x.size == n` **only**. A separately produced CV as
denominator would **presume the determinism the null is testing**.

**One statistic the packet still lacks if portability is the claim.** `r_null` compares two re-unfolds
**inside one process**, so two arms at different thread counts can both be essentially zero while the
arms' CVs differ from each other. If the claim is *"Z's CV is portable across the envelopes a
requeueing campaign will see"*, `r_cross = ‖x_cv^(A) − x_cv^(B)‖ / ‖x_cv^(A)‖` is **required** and
`r_null` does not substitute. **Recommendation: pin the envelope (§C.4) so portability is not
claimed, declare the pinned envelope in the receipt, and require `r_cross` only for a run outside
it.** `Z_CONSTRUCTION_PLAN` §4.5's diagnostic — arm 7 twice on the same fresh slabs, pinned and
unpinned, compared elementwise after the fact — measures exactly this at one additional arm-7
invocation.

---

# PART D — ADDITIONAL REQUIREMENTS FOR GENERATOR SIGNIFICANCES

**A significance criterion is not a variant of Part B; it has four preconditions Part B does not
need, and none of them exists today.** `z_contract.Z_BOUNDARIES` has **four** keys and **none is a
significance boundary** — the registry has no slot for the criterion the publication path actually
consumes. That is itself a finding.

## D.0 The state of the object, measured

**No 5D or 3D generator `chi2`, `p`-value or significance is quoted anywhere.** Measured in the
deliverable set: `sec_3d.tex:225-226` states *"no 3D generator `chi^2`, `p`-value or significance is
quoted here"*, and `sec_summary.tex:35` states *"no significance is quoted without a corrected
projected covariance"*. The published generator claims are **central-value and ratio-based** —
`sec_3d.tex:219-222` places GENIE CV, Tune v1, NuWro and GiBUU `7.2%`, `9.5%`, `15.3%` and `21.9%`
below the data on the integrated `E_avail` rate; `sec_eavailw.tex:145` quotes data/generator of
`1.54`–`1.58` in the DIS corner. **So the significance is a prospective consumer, created by
`PR-G10`, not a live number.** `INTEGRATION_CHECKLIST.md:37` records the covariance-dependent
significances as **GATED**, and that citation is the operative one.

**Consequence, and it is the cheapest resolution of this whole part: if the publication quotes no
significance, Part D collapses and the binding use of `C_Z` is the projected uncertainty band, which
is Part B leg 1.** Declaring the intended claim set is therefore the **first** decision in Part D and
not the last — §7 item 6.

## D.1 The consumed form, and the three preconditions of any criterion built on it

`eavail_generator_significance.py` shows what this **class** of consumer computes. It is **not**
evidence about any current number: its `--cov-hist` defaults to `hCov_combined4d_total` from
`uq_4d/universe_stage2_4d/uq_universe_4d_covariance_combined.root`, the historical 4D block sum.

```python
Cinv = np.linalg.pinv(C_y)          # :107   C_y is the PROJECTED covariance
chi2 = float(d @ Cinv @ d)          # :132   d = data - generator
p = stats.chi2.sf(chi2, ndf)        # :111
z = stats.norm.isf(p / 2.0)         # :113   ndf is n_ea, the BIN COUNT (:132)
```

The module states the hazard in its own comment at `:98-101`: *"a highly-correlated systematic
covariance (flux is a coherent normalization) can be near-singular -> **pinv amplifies shape
directions** and inflates chi^2"*, and prints the spectrum and condition number at `:102-105`.

**Three preconditions, and each is a NAMED PRECONDITION OF MY CRITERION rather than a note to the
reader. Without all three the criterion is not complete, however sharp its mathematics.**

**(a) The projection map must be DESIGNATED, and designation is by OUTCOME semantics, not weights.**
**⚠ THE COUNT IS FOUR, NOT THREE, AND I MEASURED IT RATHER THAN INHERITING IT.** `Z_BUILD_PACKET`
§4b item 7 says three; a search for projection-construction sites over all `.py` in the tree finds
**four in production or consumer code**:

| # | construction site | path |
|---:|---|---|
| 1 | `p4_lib.build_projection_M` | `p4_lib.py:1353` |
| 2 | `project_cov_nd.build_projection` | `project_cov_nd.py:79` |
| 3 | built **inline** by the consumer | `eavail_generator_significance.py:87-88` |
| 4 | `assemble_ctotal_bkgsub.build_5d_to_4d_projection` | `nd-unfolding/pet/assemble_ctotal_bkgsub.py:36` |

Two further `M` constructions exist and are **not** builders: `p4_lib.py:1484` is
`build_projection_M`'s own independent reconstruction by a deliberately different algorithm — a
**control**, and counting it as a rival would be a category error — and
`state/probe-projection-identity-leg-20260816.py:71` is a probe's own.

**Site 4 changes the shape of the designation requirement.** It is on the PET path, and `AGENTS.md`'s
legacy boundary holds that the corrected recoil-only PET budget *"cannot satisfy or feed the
full-event DAG."* **So a designation must exclude it deliberately, by name, rather than by nobody
happening to call it** — an exclusion that holds by luck is not an exclusion. **And note what
`FINDING-20260910` does and does not establish: it compares TWO builders.** *"The implementations
disagree"* is not something it establishes about sites 3 or 4, and I do not claim it.

For sites 1 and 2, `FINDING-20260910` measures them byte-identical on canonical edges at three mask
densities **and opposite where support masks do not nest**. **Recommendation: designate `p4_lib.build_projection_M`.** Ground: it refuses in **both**
directions — `:1380` rejects a reported high bin landing in a non-reported low bin, and `:1393-1401`
rejects a reported low bin no high bin reaches, carrying the record that the one-directional version
was a **masking defect** (`BEN-064`) in which five orphan bins carrying `0.0000%` of the 4D total
reported `rel = 1.00e+00` and hid 62% of bins over tolerance at a median of `4.4%`. `project_cov_nd`
does neither check and **silently drops**. For a covariance destined for a pseudo-inverse, silently
discarding reported source content is not an acceptable default. **Second recommendation: the
consumer's inline `M` is retired in favour of a call to the designated builder** — a rule retyped is
a second implementation, and this one has already diverged. **Neither recommendation is a claim that
the builders are equivalent**; that remains unresolved, and `SPEC` §6's check must be re-scoped so
its **unit is the outcome**, with elementwise equality tested only inside the both-returned cell.

**(b) `ndf` must be declared, and the current policy is internally inconsistent.**
`chi2_to_sigma(chi2, n_ea)` at `:132` passes the **bin count** while `pinv` discards modes below its
cutoff. A quadratic form evaluated on a rank-`r` retained subspace is referred to a
`chi2`-distribution on `n` degrees of freedom. **Recommendation: `ndf` = the retained rank, reported
per member.** This rests on a distributional fact, not a preference. **I do not claim a direction for
the resulting change in `z`**: dropping modes reduces `chi2` and reduces `ndf`, and the two move `z`
oppositely, so the net sign is not determined by this argument.

**(c) The `pinv` cutoff must be recorded and a rank change must block a bare pass.** `np.linalg.pinv`
is called with **no `rcond`** (measured: zero occurrences in that module), so the cutoff is relative
to the largest singular value and moves with each member. **The requirement is REPORTING, not
suppression**, and both halves of the tempting fix are wrong: pinning `rcond` does **not** pin the
retained subspace, because an eigenvalue crossing a *fixed* threshold changes it anyway; and a rank
discontinuity is a **sensitivity of the stated procedure**, to be reported, not dismissed as an
artifact. **Recommendation: record the cutoff applied and the retained rank per member; a rank change
is a reportable event that blocks a bare pass, and the criterion must state what it does when rank
moves rather than averaging over it.**

**And the tail convention is part of the quantity: `z = norm.isf(p / 2.0)` over an UPPER-tail
`chi2.sf`.** Quote the formula, never a characterization of it — two successive revisions of the
predecessor proposal mis-described this line in opposite ways.

## D.2 The criterion — threshold-parametric, and complete without a threshold

| field | |
|---|---|
| **quantity** | the movement of each quoted generator significance across the declared offset set |
| **intended scientific use** | `PR-G10` (path CRITICAL): *"recompute generator comparisons and significances only from the governing adopted covariance"*, and `sec_summary.tex:35`'s *"no significance is quoted without a corrected projected covariance"* |
| **statistic** | **`rho` on the designated projected covariance** (§2.1), from which the significance interval follows in **closed form** (§5.3). The direct alternative `s_sig = max_k \|Nsigma_k − Nsigma_0\|` is retained as the **reported** quantity, and it is the honest headline; `rho` is what makes the criterion evaluable and bounded rather than sampled |
| **denominator** | **none.** `s_sig` is an absolute difference in a quantity already expressed in sigma units, which removes the `chi2_0 = 0` denominator problem; `rho` is dimensionless by construction. Where a relative `chi2` diagnostic is wanted the denominator is `chi2_0`, Z's own `k = 0` member, undefined at `chi2_0 = 0` |
| **tolerance** | `rho <= rho_crit(T, chi2_0, ndf)`, **closed form in §5.3**. `T` is the only input from outside the code |
| **justification** | **PROVEN BOUND** (§2.1, §2.2, §5.3) **+ SCIENTIFIC JUDGMENT confined to `T` alone** |
| **population / scope** | the declared offset set `K`, **and** the declared set of `(generator, projection)` pairs the publication will quote. The `max` is exact over both and no distributional inference is made. **It says nothing about pairs outside the declared set** |
| **terminal outcomes** | **MET** — the whole interval lies on the claim's side of `T`, for every declared pair and every `k`. **NOT MET** — some declared pair's interval crosses `T`; report the pair, the `k`, and the interval. **INCONCLUSIVE** — `rho >= 1` (bound vacuous), or the **retained rank moved** between members, or `p = 0` for some pair so `Nsigma` is infinite and the statistic is **undefined**, which must be reported as undefined and never as zero movement |
| **claim supported when MET** | *"No declared estimator-baseline offset moves any quoted generator significance, among the declared `(generator, projection)` pairs, across the declared decision threshold."* **Not** a claim about pairs outside the set, and **not** a claim that `C_Z` is correct |
| **cost** | zero incremental production. `rho` is arithmetic on members `D3` would produce; the significance interval is a closed-form evaluation costing microseconds |

## D.3 What Part D does not resolve

The `p`-value's **effective inversion dimension does not exist** because no 5D `chi2` exists; the
**threshold `T` exists nowhere in the tree** and is the one input that cannot come from the code; and
the **marginal-versus-direct route question is open**, with a recorded cross-check that must not be
read as a gate — between the marginal and independent 4D routes, `3,009` of `4,825` bins differ by
more than `3%`, median `4.4%`, max `72.9%`, integrals agreeing to `0.56%` (`SPEC` §2.6c). **That last
number is why D.1(a) matters: the route choice moves per-bin projected uncertainties by tens of
percent, which is far larger than any tolerance discussed anywhere in this document.**

---

# 2. THE MATHEMATICS PARTS B AND D REST ON

All three results below are produced by
`docs/orchestration/state/probe-z-criteria-acceptance-mathematics-20260910.py`, which asserts each in
both directions and carries controls. **Re-run it rather than believing this section.**

## 2.1 The bound — PROVEN, and SHARP

**Claim.** Let `C_0 > 0` and `C_k > 0` on the compared support, and let
`rho = ‖ C_0^{-1/2} (C_k − C_0) C_0^{-1/2} ‖_2 < 1`. Then **for every data vector `d`**:

    chi2_0 / (1 + rho)   <=   chi2_k   <=   chi2_0 / (1 - rho)

**Proof.** Write `C_k = C_0^{1/2} (I + E) C_0^{1/2}` with `E = C_0^{-1/2}(C_k − C_0)C_0^{-1/2}`,
symmetric with `‖E‖_2 = rho`. Then `chi2_k = u'(I+E)^{-1}u` where `u = C_0^{-1/2} d`, and the
eigenvalues of `(I+E)^{-1}` lie in `[1/(1+rho), 1/(1-rho)]`. The bound is attained when `u` aligns
with `E`'s extreme eigenvector, so it is **sharp**.

**Checked:** `120,000` (covariance pair, data vector) evaluations; lower bound
`min(chi2_k/lo) = 1.000000000000`, upper bound `max(chi2_k/hi) = 1.000000000000`, and **sharpness
witnessed** — both ratios reach `1.000000`, so the bound is the tight one and not a loose sufficient
condition.

**Three controls, one of them in the opposite direction:**

| control | what it must do | result |
|---|---|---|
| **silent on good** | `rho(I, I)` must be exactly `0` | `0.000e+00` |
| **fires where the adopted statistics are blind** | on `SPEC` §3.7d's own counterexample `I_2` vs `[[1,0.9],[0.9,1]]`, `s_agg` and `s_med` are exactly `0.0` | `rho = 0.9000`, and it admits the real move `chi2: 1.0000 -> 5.2632` |
| **the OPPOSITE-direction bad** — identical spectrum, different quadratic form | `diag(1,4)` vs `diag(4,1)`: identical eigenvalues, identical condition number, `chi2` moves by a factor `4`. A spectral statistic waves this through | `rho = 3.0000 >= 1`, so the criterion returns **INCONCLUSIVE, never MET** |

**Why the third control matters:** it is the case `PROPOSAL-20260908` §2c raises against every
spectral summary. `rho` does not "see" it in the sense of returning a small number — it returns
`>= 1`, which under B.1(i)'s outcome rule is an explicit refusal to certify. **A criterion that
reports its own inapplicability is doing the right thing; a criterion that returns a passing number
is not.**

## 2.2 `rho` is non-increasing under projection — PROVEN

**This is the result that makes the criterion robust to the undesignated `M`.**

**Claim.** For any linear map `M` with `M C_0 M'` nonsingular,
`rho(M C_0 M', M C_k M') <= rho(C_0, C_k)`.

**Proof.** Let `B = M C_0^{1/2}`, so `M C_0 M' = B B'` and `M (C_k − C_0) M' = B E B'` with `E` as
above. Put `P = B'(BB')^{-1/2}`; then `P'P = I`, so `P` has orthonormal columns and
`rho_proj = ‖P' E P‖_2 <= ‖E‖_2 = rho`.

**Checked:** `1,898` (covariance, projection) pairs with sparse one-cell-to-one-bin positive-weight
`M` of the form `project_cov_nd` builds; `max(rho_proj / rho_5D) = 0.999997`, with `7` pairs reaching
`> 0.999` as tightness witnesses. Control: `M = I` gives the ratio exactly `1.000000000000`.

**What this buys, stated precisely so it is not over-read.** A `rho` measured on the **5D trunk**
bounds `rho` on **every** projection simultaneously, including projections not yet designated or
built. **So the BOUND is `M`-independent.** It does **not** make the *reported significance*
`M`-independent — `chi2_0`, `ndf` and the retained rank all depend on which `M` is used, so D.1(a)–(c)
remain preconditions. The practical consequence: `rho_5D` can be evaluated **before** the projection
question is settled, and a small `rho_5D` discharges the sensitivity question for all marginals at
once; a large one localizes the work.

## 2.3 What it costs

Per member, on the **projected** covariance the consumer inverts, `rho` is negligible — the projected
dimensions are small (`n_ea`, `(E_avail, W)`, `4,825`). On the **full** `10,694^2` trunk it is the same
cost class as `s_eig`: one baseline factorization **once** plus one extreme-eigenvalue solve per
member. `SPEC` §3.7d prices a full `eigvalsh` at `10,694^2` as `O(n^3) ≈ 4e12` flops, **`1`–`3`
minutes** and `≈1.8` GB, from `numpy.linalg.eigvalsh` timed locally at `n = 500/1000/1500/2000` and
scaled — a span reported rather than averaged. **Only the operation count and the memory are
venue-independent; the TIME is not**, and `s_eig`-class work is precisely the figure whose transfer is
least safe, because runtime depends on hardware, thread count and numerical library, and §C.4's own
finding is that thread count is a property of the allocation with nothing pinning it. An extreme-pair
solve is cheaper than a full spectrum and should be used, but **I have not measured it at `n = 10,694`
and am not quoting a figure for it.**

---

# 5. THE CLOSED FORM THAT REMOVES THE MISSING NUMBER

## 5.1 Why a tolerance is not needed in advance

`PROPOSAL-20260908` §5 gives the honest reason no tolerance was proposed: *"§4b's threshold does not
exist in this tree. No artifact states what decision any quoted significance supports at what
margin."* **That is still true. The response is to make the criterion a function of the threshold
rather than of a tolerance**, so the criterion is complete now and the threshold is supplied once,
by the person whose judgment it is.

## 5.2 And the printed-precision route stays closed

`PROPOSAL-20260908` §4a is right and its self-correction is the important part: an argument that a
movement too small to change a printed digit is no movement **is a formatting argument wearing a
use-based label**, and it is the `D1c` error. It errs in both directions at a rounding boundary, and
it presumes the decision depends on the printed digits when it depends on the **margin** to whatever
threshold the claim rests on. **Printing precision sets no scientific floor and no ceiling** — the
"floor" version is the same error one size smaller. Nothing in this document derives a tolerance from
a format; B.1(iii) uses formatting **only** for an exact display-invariance test that carries no
tolerance at all.

## 5.3 `rho_crit` — the inversion

The consumer's map is strictly increasing in `chi2`, so composing §2.1 gives the significance interval
in closed form, and inverting gives the largest perturbation a claim at threshold `T` survives:

    chi2_crit(T, ndf) = chi2.isf( 2 * norm.sf(T), ndf )

    claim "z stays ABOVE T":   rho_crit = chi2_0 / chi2_crit(T, ndf) - 1
    claim "z stays BELOW T":   rho_crit = 1 - chi2_0 / chi2_crit(T, ndf)

**Verified exact.** At the edge the recomputed `z` equals `T` to `< 1e-6` at every tested `ndf`, and
the boundary is sharp in both directions: at `rho_crit - 1e-6` the claim holds, at `rho_crit + 1e-6`
it fails.

**Two controlled one-variable-at-a-time scans. SYNTHETIC `chi2_0`/`ndf` PLACEHOLDERS — no real
`chi2` exists in this tree, and none is asserted:**

| `z_0` fixed `4.0`, `T` fixed `3.0`, only `ndf` varies | `rho_crit` | `(z_0-T)*sqrt(2/ndf)` |
|---:|---:|---:|
| `ndf = 7` | `0.416979` | `0.534522` |
| `ndf = 42` | `0.201980` | `0.218218` |
| `ndf = 247` | `0.089719` | `0.089984` |
| `ndf = 4825` | `0.021140` | `0.020359` |
| `ndf = 10694` | `0.014255` | `0.013676` |

| `ndf` fixed `42`, `T` fixed `3.0`, only the margin varies | `rho_crit` |
|---:|---:|
| `z_0 = 3.5` | `0.098677` |
| `z_0 = 4.0` | `0.201980` |
| `z_0 = 5.0` | `0.423567` |
| `z_0 = 6.0` | `0.666322` |

**Both sides, the unit and each population are named in the same sentence: `rho_crit` is
dimensionless, the population of each row is one `(chi2_0, ndf, T)` triple, and only the named
variable moves.**

**The structural content, and it is the one thing in this document that is a warning rather than a
recommendation.** For a fixed significance margin, the admissible perturbation **falls as `ndf`
grows**, asymptotically as `(z_0 - T) * sqrt(2/ndf)`. At a projection with thousands of bins a
**one-to-two-percent** relative spectral perturbation is enough to move a `4-sigma` claim below
`3-sigma`. **Use the exact formula, not the asymptote:** the asymptote is conservative at large `ndf`
and **permissive below `ndf ≈ 250`** (at `ndf = 7` it gives `0.535` against the true `0.417`), so
quoting it as a shortcut errs in the unsafe direction exactly where projections are small.

**Set beside §B.0's control-B measurement, this is the whole argument of Part B in two numbers:** the
two proposed gates return exactly `0.0` on a perturbation that moves the consumed quantity by a factor
of `5.26`, while the perturbation a real large-`ndf` claim can absorb is of order `1%`.

---

# 7. THE SMALLEST MEASUREMENTS NEEDED, IN DEPENDENCY ORDER

**None requires cluster compute except items 7 and 8, and neither of those is requested here.** No
authorization is sought by this document and none is implied.

| # | measurement | closes | cost |
|---:|---|---|---|
| 1 | **Persist `x_cv`, `x_cv2` and the support predicate** in Z's own throw product | `SPEC` §3.3 `11b`; and it is the single number that resolves §C.3's consistency check, since the gate is breached only if `‖x_cv^G‖ < 5.8223e-41` | Tier-2 code, `1.05` MB |
| 2 | **Bind the operand of the mask/row-order invariant** — reconstruct both digests from G's production-CV input and bind that input's identity | `SPEC` §3.3(1), whose condition currently has no readable operand (§1.3d); `PM-4` | read-only |
| 3 | **`PM-5`** — the band-family read on G's own `combined_source`, so `\|R\| = 27` is measured against G rather than S | A.3's complement gap | bounded read |
| 4 | **The remaining CV-perturbation channels** — how a CV shift propagates into `C_unified` through the throw deviations and the completeness division (`unified_throw_cov_5d.py:66-80`) | the only gap in §C.2's `S`. Today `S` is bounded for the **F7** channel alone | arithmetic + one code read; **no mechanism should be asserted before it** |
| 5 | **Evaluate leg 1 and leg 2 on real members, then derive `cause3_corr`** from the measured relationship between `s_corr` and `rho` | B.1(ii), the one boundary I do not propose | arithmetic on members `D3` would produce |
| 6 | **Declare the intended claim set** — which `(generator, projection)` pairs will carry a significance, and whether any will | **Part D's first decision.** If none will, Part D collapses to Part B leg 1 | a decision, not a measurement |
| 7 | **Re-scope `SPEC` §6's builder comparison so its unit is the OUTCOME**, then run it | D.1(a); `FINDING-20260910`'s own amendment 2 | Tier-2 code, no compute |
| 8 | **`Z_CONSTRUCTION_PLAN` §4.5's pinned/unpinned arm-7 diagnostic** | §C.4 items 1–2, the load-bearing pair for `B` | one arm-7 invocation, `<= 0.58` CPU task-h measured on three historical `uthrow5d_combF` runs (`0.3875`/`0.4239`/`0.5764`), **TRANSFERRED** — a different bank and slab count, and the thread-count arm varies the quantity that sets elapsed |

**And one item that is not a measurement: `Z_BOUNDARIES` needs a fifth key.** Part D's criterion has
no slot in `z_contract.Z_BOUNDARIES`, which carries exactly four. A boundary with no registry entry
cannot be withheld, which means it cannot be *seen* to be withheld — the failure mode
`Boundary.withheld` exists to prevent.

---

# 8. WHAT THIS RECOMMENDATION DOES NOT DO

It adopts nothing, grades no leg, opens no cell, discharges no cause, moves no count and no gate, and
authorizes no compute. It does not reopen §6.1–§6.5, §1.3's algebra, `R4`'s suspension, or the pin. It
proposes no change to `CRITERIA` §0's vocabulary and does not extend it. It does not designate an `M`
— it **recommends** a designation and names the check that would support one. It quotes no value from
`nd-unfolding/mii/member_k000000/`: **Gate 2 remains FAIL**, and `DECISION-20260830` records that *"no
authorization from Joseph removes it — only the rehearsal work landing does."* It does not price
Z's campaign and quotes no `R5` spend figure; the withdrawn affordability figure is not carried.

**It does not grade its own criteria.** Where a boundary is proposed, the argument is exposed so it
can be refused on its merits: §C.3 is a transfer with a named falsifier, A.1's margin is a judgment
about how much room a six-operation expression needs, and B.1(iii) replaces two numbers with an exact
test rather than with better numbers.

**Three places where I record my own error rather than the corrected version alone.** §B.0's withdrawn
ground — I measured a real thing and was about to draw a circular conclusion from it, and the scope
error was mine. §C.2's `S` — the F7 channel bounds one propagation path and I do not know the others,
so `S` is partial and labelled partial. §2.3 — I decline to quote a runtime for an extreme-pair solve
at `n = 10,694` because I have not measured it, even though it is the figure a reader most wants.

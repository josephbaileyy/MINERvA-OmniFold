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

**⚠ THE MANIFEST GATE — MEASURED AT `c18f9daa`, THEN ROOT-CAUSED AND REPAIRED BY ANOTHER LANE. Both
states are recorded, because the first is a timestamped observation and only the second is current.**

**What I measured, and it stands as a measurement:** `python3
docs/orchestration/generate_manifest.py --check` exited **`1`** with `OUT OF DATE` on a **clean tree
at `c18f9daa`** — `git status --short` empty, 0 untracked, none of this lane's work present. So the
staleness was **not** produced by this commit. *(That exit code is read from the process, not through
a pipe. A pipe reports `tail`'s status — `0` — and I made exactly that mistake before catching it.
Separately: my tree was clean **by workflow**, because I had stashed with `-u`, rather than by
design — and the very defect below is that untracked paths change the answer, so a clean-tree
measurement is the only kind that means anything here.)*

**What has since been established, verified here rather than accepted on report:** the cause was
`generate_manifest.py:92-94`, which builds `inventory = tracked | intended` where `intended` is
`git ls-files --others --exclude-standard`. **The committed manifest was encoding one machine's
untracked files** — so this was an **oscillation, not a backlog**: every regeneration deleted the
previous author's untracked rows and added its own. Repaired at **`6f24fb00`** by regenerating with
the **pre-existing** `--committed-only` flag (`:69`, `:93` — the flag was not added by the repair;
the generator is unchanged). I confirmed the result independently: `origin/main`'s `MANIFEST.tsv`
censuses **`tracked: 780`** and `intended` does not appear at all.

**What this commit does, unchanged by the repair:** it still does **not** carry a regenerated
`MANIFEST.tsv`. Bundling a 1,531-line inventory rewrite with a scientific recommendation would
obscure this diff, and at the time it would also have silently settled a question that had been
routed to Joseph. **My two files will get rows on the next regeneration.** Routability meanwhile is
secured the way the convention actually requires — a `MANIFEST-overrides.tsv` row and a `CATALOG.md`
pointer, both irreducibly manual, **neither checked by any hook**, and both verified from the
committed tree after the commit returned rather than before.

**One residual, so the next lane does not repeat my measurement and read it as a defect:** in a
checkout with untracked paths under `docs/orchestration/`, plain `--check` exits `1` while
`--check --committed-only` exits `0`. **Re-run with the flag, on a clean tree, before reporting
staleness.**

---

## CITABLE FOR / NOT CITABLE FOR — read before quoting anything below

**CITABLE FOR**

- the **`rho` bound** of §2.1 and its **projection monotonicity** of §2.2 — two theorems, each
  checked in both directions with controls, by
  `state/probe-z-criteria-acceptance-mathematics-20260910.py`;
- the **closed-form critical `rho`** of §5.3, which makes the significance criterion complete
  **modulo a threshold** rather than blocked on one;
- the **normalizer argument** of §C.1 (three committed sqrt-traces exist for one null, spanning
  `20.9%`);
- the **F7 decision-margin measurement** of §C.2 and its normalizer-free factor `1.7957e11`;
- the **thread-environment measurement** of §C.4 — what the three launchers *declare*, and that
  `make_estimators` pins nothing;
- that the withdrawn `5.00e-41` reproduces from `values.tex:115`'s macro and **not** from G's
  measured mean shift — in the probe's section 5, which is where that arithmetic lives; this document does not restate it;
- the **projection-builder census** of D.1(a) — **four** production/consumer construction sites, not
  three, with `p4_lib.py:1484` identified as a control rather than a rival;
- the **`pinv` retained-subspace limit** of §2.1a, its bidirectional remedy, and the
  **determinate direction** of the `ndf` change in `D.1(b)` — all three found by the
  `z-independent-assessor` lane and reproduced independently here;
- the **domination theorem** of §2.1b and the **concentration measurement** beside it, and the
  **`cause3_corr` recommendation** of Part 6 — including §6.4's three objections to it, which are
  part of the recommendation and not separable from it;
- the **reconciliation** of §0.0, including that the string `rev. 5` does not occur in the document
  being called that;
- the **requirement lists** and the **ordered minimum measurements** of §7.

**NOT CITABLE FOR**

- any adopted boundary. Four are withheld in `z_contract.Z_BOUNDARIES` and this document adopts
  none of them; it **recommends** dispositions.
- **any claim that the four `\gbdtFive*` macros have no scientific use.** They are not printed in
  any tracked `.tex` today **and they are staged for a post-adoption note update**
  (`PROCEDURE-gbdtFive-macro-update.md`). §B.0 states why the tempting inference is circular and
  must not be drawn from my measurement.
- any current significance, `chi2`, `p` or `ndf` for any MINERvA projection. **None exists in this
  tree.** The `chi2_0`/`ndf` values in §5.3 and in the probe are **synthetic placeholders** exercising
  a formula.
- any statement that the execution envelope is inadequate. §C.4 establishes that a bound argued from
  *"the configuration is pinned"* **cannot be made today**; that is a statement about the evidence,
  not about the world (`SPEC` §3.7a rev. 19).
- the equivalence or designation of any projection map `M`.
- ⚠ **the `M`-INDEPENDENCE of the bound. WITHDRAWN in round 2 (F2).** §2.2's theorem stands; its lift to a singular trunk does not, because it needs `range(C_k − C_0) ⊆ range(C_0)`, which is unmeasured on Z and probably false. **This was rev. 1's flagship practical claim and it must not be quoted.**
- ⚠ **any acceptance rule built on `rho` at the TRUNK.** §6.1's F1 row derives `rank(C_Z) <= 265` of `10,694` from Z's own operands, so `C_Z^{-1/2}` does not exist. §2.1/§2.1b remain **theorems**; their ROLE as the acceptance instrument is withdrawn (§6.2).
- ⚠ **rank `263` as a property of Z, G, or "the trunk".** It is **S's**, the component donor (`app_statmethods.tex:636`, subject *"the standard-P4 5D **candidate**"*). An earlier revision of this lane's probe made exactly that misattribution.
- **that domination implies non-bindingness.** VOID (F9): the implication needs `rho_crit <= τ`, a relation between **thresholds**. Rev. 1's `cause3_corr` hinge rested on it.
- **the `rho` bound as governing the CONSUMED form without §2.1a's subspace condition.** §2.1 is proven for the TRUE inverse; the consumer uses `pinv`, and §2.1a exhibits identical retained rank with the bound violated. **Quoting §2.1 for `pinv` without the retained-subspace gate is the one misuse of this document that would matter.**
- **any claim that real Z members do or do not swap modes across the `pinv` cutoff.** §2.1a's construction is synthetic; the regime is UNMEASURED on Z.

---

## 0.0 RECONCILIATION WITH THE EXISTING LANDED PROPOSAL — read this before §0

**A second lane's document already occupies part of this subject, it is on `main`, and it is routed.**
`docs/orchestration/PROPOSAL-20260908-z-sensitivity-criteria-over-publication-projections.md`,
**content digest** sha256 `3fc9fb87b170887cdc8be870f801e7228113c35669be455401bdb7f1e6e9ac4c`, measured at `c18f9daa` — ⚠ **a file digest, NOT a git object: `git cat-file` on it fails. The git identifiers are commit `610d0882` and blob `0a06aa52`** —
`LIVE`/`open` at `MANIFEST-overrides.tsv:117`, routed from `CATALOG.md:178`. It is the
**z-operand-schema lane's** work and it predates this lane's assignment. **Two lanes drafting one
contract is how a repository acquires two conflicting criteria sets, with the winner decided by push
timing rather than by evidence. So this section chooses, rather than landing beside it.**

**⚠ ONE CITATION CORRECTION FIRST, because it will otherwise be propagated — and it is stated more
carefully here than rev. 1 stated it.** That document is referred to in coordination traffic as
*"rev. 5"*. **The string `rev. 5` occurs zero times in its bytes** (measured, case-insensitive), and
its highest self-declared changelog label is **`REV. 4`**. **But rev. 5 is a REAL revision, and rev. 1
of this section could be read as denying that** — it is commit `610d0882`, *"[doc] Z criteria proposal
rev. 5: the routing index stops carrying review history…"*. So the revision did work and simply left
**no in-document label**; the label lives in a **commit subject** and nowhere in the file. **A commit
subject is not a document label. Cite by sha — because the document's own changelog and its commit
subjects disagree about which revision this is, and only the sha is unambiguous.**

**THE CHOICE: this document SUPERSEDES its candidate-criteria role, and RETAINS it as evidence.
Scoped, item by item, and its bytes are not touched.**

| what | disposition here |
|---|---|
| its §1, §1a, §1b — the consumer, and the distinction between what the publication **intends** to consume and a **validated current path** | **RETAINED and CITED.** Part D rests on it. Nothing here replaces it |
| its §2a, §2c — that `s_agg`, `s_med` and `s_eig` cannot bound an inverse-quadratic consumer, and that a spectral summary cannot determine the quadratic form | **RETAINED and CITED.** §2.1's third control is its `diag(1,4)`/`diag(4,1)` counterexample, re-run |
| its §4a — that printed precision establishes nothing scientific, in either direction | **RETAINED and CITED.** §5.2 |
| its §4c — record the `pinv` cutoff, report the retained rank, treat a rank change as a reportable event | **RETAINED and CARRIED FORWARD** as D.1(c). This is the one element I judge already correct and separable |
| its §3 C-1, C-2, C-3 — the three candidate criteria | **SUPERSEDED.** C-1 becomes the **reported** quantity and `rho` becomes the criterion (§D.2), because C-1 is a sampled maximum with no bound and no coverage argument, and its own §2b leaves `s_proj`'s coverage **unresolved with no method offered**. §2.1–§2.2 close that question by changing the statistic rather than by searching for a functional set |
| its §6 — the *"which `M`?"* premise | **⚠ NOT SUPERSEDED. ITS PREMISE STANDS AND IS NOW WIDER.** ⚠ **This cell said `SUPERSEDED by measurement` and that was FALSE — see the correction note directly below the table, which is where it belongs rather than in a changelog.** Its §6 reads *"At least THREE projection-matrix implementations exist and this proposal does not assume any two agree"* (`:323`), and D.1(a) measures **four** sites, so the premise is **larger** than when they wrote it, not retired. Its operative half — that **none is designated** — is untouched by any measurement. **What IS superseded is only §6 item 1's METHOD**, and **not because the builders agree:** an elementwise `M₁ − M₂` check is **undefined when one side refuses**, so a runner implementing it literally skips the refusing cases and reports agreement from a domain **selected for** agreement — a gate that cannot fail, which no exit code catches. D.1(a) restates the comparison over **outcomes**. The narrow thing genuinely retired is §6's implicit worry that the `p4_lib`/`project_cov_nd` pair might disagree **numerically**, answered for **that pair** at three synthetic mask densities with a working detection control, and for nothing else |
| its §7 items 1, 2, 3 — its four asks | **ANSWERED or RE-PUT.** Item 1 is answered (§D.2); item 2's threshold is made a **parameter** rather than a blocker (§5.3); item 3 is re-scoped (D.1(a)) |
| its closing *"No criteria owner exists"* | **NO LONGER TRUE**, `owners.tsv:14` at `c18f9daa`. **That is the substantive reason supersession is the right form and folding is not: a proposal addressed to a missing owner is answered by the owner, not merged into.** |

### ⚠ CORRECTION TO THE ROW ABOVE, 2026-09-10, AFTER THE AUTHORING LANE SUSTAINED AN OBJECTION

**The §6 row read `SUPERSEDED by measurement`. That asserted coverage the evidence does not have, and
it is corrected in place with the wrong verdict quoted rather than deleted.** The authoring lane —
which claimed all five revisions from the inside, and whose claim I routed from **its own line 3**,
*"Authored 2026-09-08 by the Z spec/implementation lane"*, after finding no `Claude-Session`,
`Co-Authored-By` or `Signed-off-by` trailer on any of `b25db428`, `7as7047f299`, `8809a6c1`,
`db135bea`, `610d0882` — objected that **a two-builder measurement cannot retire a
three-implementation premise.** Verified here before accepting: `FINDING-20260910:109` states its own
limit, *"The third builder is untouched … has not been compared to either of the other two."* Against
D.1(a)'s four sites that is `C(4,2) = 6` unordered pairs with **exactly one measured**; the five
unmeasured pairs are `p4_lib`×`eavail`, `p4_lib`×`pet`, `project_cov_nd`×`eavail`,
`project_cov_nd`×`pet`, `eavail`×`pet`.

**Three things about this correction are worth more than the correction.**

1. **The right statement was already in the same cell.** Its second sentence read *"As specified it
   would test agreement over a domain selected for agreement."* **The body was right and a wrong
   headline verb overrode it** — a reviewer scanning a verdict column never reaches the sentence that
   contradicts it. **So the repair is the label, not another caveat**; the caveat was already there.
   The **worse** instance was in `CATALOG.md`, which listed this premise under `NO LONGER CITABLE
   FOR` — mismarking a **live** premise in the file agents route from, which misroutes rather than
   merely misleads. Both are corrected.
2. **This is the second instance of one shape in this document.** §B.0 below withdraws an argument for
   precisely this reason — a refutation outrunning what it refutes — and this cell committed the shape
   again about a hundred lines later. **Writing a failure up as a lesson in a document does not
   immunize the rest of that document against it**, and the covering search that followed found a
   third class: seven internal `§`-pointers still aimed at a `§3`/`§4` numbering this document
   abandoned when its parts were renamed `A`–`D`, six of them in the `CITABLE FOR` block a reader is
   told to read first.
3. **The durable lesson is the authoring lane's and is recorded as theirs.** Its own diagnosis of §6
   was not that the builders agree — it was that §6 item 1's elementwise check is **undefined when one
   side refuses**, so the tested domain self-selects for agreement. And its closing observation is the
   sharpest thing in the exchange: **§6's own bullet already recorded that `p4_lib` *"carries a
   bidirectional coverage check"* — the refuting fact sat one paragraph above the flawed check.** Its
   handling of its own §2b is the same discipline: it withdrew a wrong test **without replacement**,
   because *"inventing a second wrong one in the same document would be worse than leaving the
   question open."*

**Why NOT fold this into it as a further revision.** An independent assessment against those exact
bytes has just landed (`origin/lane/z-criteria-independent-assessment-20260910`). Rewriting the
document would leave that assessment pointing at a revision that no longer exists — **destroying the
evidence rather than answering it.** Before recommending a remedy, price what it destroys.

**⚠ And the authoring lane's reason is better than that one, so it governs here instead of mine.** In
its words: *"the withdrawal tables in that document are the record of how it got where it got, and
they only work if nobody edits them retroactively."* **That holds even when no assessment is
running**, which mine does not. Adopted, and attributed.

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
membership, **the packet is re-put whole** rather than amended — Part B (§B.1) is written that way.

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
| **terminal outcomes** | **MET** (`rho <= rho_max`) / **NOT MET** (`rho > rho_max`, with the argmax `k` and the extremal eigenvector's leading components reported) / **INCONCLUSIVE**, which covers three distinct cases and must not be read as the nearer of the other two: **(a)** `rho >= 1`, where the bound is vacuous — a *large* perturbation, never a pass; **(b)** the baseline is not positive definite **on the object that is actually inverted** — ⚠ **the check is on the PROJECTED covariance `M C_Z Mᵀ`, not on the trunk**, because the trunk being PD says nothing about a marginal, and the `(E_avail, W)` projection is **structurally singular by design**, so a trunk-level PD test would pass while the inverted object has no metric. Singular-by-design projections are handled by clause **(d)** below rather than refused here; **(c)** **`INCONCLUSIVE / VACUOUS SEED VARIATION`** — the branch's ruled name, `PREDECLARE-20260901-cause3-mii-estimator-seed-magnitude.md:230`, beside `INCONCLUSIVE / WRONG FOOTING` at `:226`. `rho == 0` exactly, or a read-back offset set that does not match the declaration. **This branch is the POSITIVE CONTROL and it is why it may not be omitted:** `rho` is small both when the baseline genuinely does not move the covariance **and** when the offset never reached the estimator, and the two are indistinguishable from the statistic alone. It is the `g ≡ 1` shape — a green state reachable without the work being done — one cause over. **A zero spread is evidence the knob never arrived, not a favourable result** (`SPEC` §3.6b item 5); **(d) ⚠ NEW — THE RETAINED SUBSPACE MOVED.** See §2.1a: the consumer inverts with `pinv`, so **MET additionally requires that every member RETAIN THE SAME SUBSPACE as the `k = 0` member**, tested as `‖P_0 − P_k‖_2 <= 1e-8` on the orthogonal projectors onto the retained modes. **Retained RANK is NOT the test FOR THIS PURPOSE and must not be substituted for it** — `D.1(c)` of this document already says why (*"pinning `rcond` does not pin the retained subspace"*), and §2.1a exhibits a case with **identical rank**, `‖P_0 − P_k‖_2 = 0.9951` and the bound violated. ⚠ **This does NOT conflict with §6.4 gating rank equality, and the two purposes are named here so the adjacency cannot be misread:** rank equality is insufficient to validate **§2.1's bound** (this clause), and is separately **required as a declaration** by `app_statmethods.tex:648` clause (ii) (§6.4). **One is a sufficiency question about a bound; the other is a conformance obligation about a quoted number.** Neither substitutes for the other |

### B.1(ii) LEG 2 — `s_corr`, and it binds independently

| field | |
|---|---|
| **quantity** | the change in `C_Z`'s **correlation** structure with the diagonal divided out |
| **intended use** | `SPEC` §3.6b requires the second leg to bind **independently** — *"the same trace can be diffuse or concentrated"*. `s_corr` cannot be satisfied by the diagonal, because the diagonal is divided out; and it is not implied by leg 1, because `rho` is a worst-direction bound while `s_corr` is a whole-matrix aggregate. One can be small while the other is not |
| **statistic** | `s_corr = max_{k in K} ‖ R^(k) − R^(0) ‖_F / ‖ R^(0) ‖_F`, with `R = D^{-1} C_Z D^{-1}`, `D = diag(sqrt(diag C_Z))` — **already implemented at `z_statistics.py:240`, with `correlation_matrix` at `:233`. Do not reimplement** |
| **denominator** | `‖R^(0)‖_F`, Z's own `k = 0` member, named in the same sentence as the numerator |
| **tolerance** | ⚠ **SUPERSEDED BY PART 6 — DO NOT READ THIS LEG AS STILL OPEN.** Rev. 1–2 of this cell proposed no number and recommended that `cause3_corr` stay withheld indefinitely. **Joseph ruled on 2026-09-10 that an unexplained requirement may not be retained forever and asked for one explicit recommendation; Part 6 gives it.** The recommendation is **Branch B** — retire `cause3_corr` as a key and amend §3.6b — on the ground that §2.1b **proves** leg 1 dominates every `uᵀCu` functional, `s_corr` included, so no second statistic can bind independently. The original reason still stands as far as it went: `s_corr` is an aggregate over `1.14e8` entries with no established map to a reported quantity, so §3.6d's ordering rule could not be satisfied for it. **What changed is that this is now an argued disposition rather than a withholding.** `s_corr` is retained as a REPORTED diagnostic |
| **why this is not a retreat to the diagnostic** | leg 1 carries the *use-facing* bound, so `(cause 3, Z)` is not left ungated. **And the `UNRESOLVED`-not-`MET` position is UNCHANGED by Part 6:** `(cause 3, Z)` still has one binding leg where unamended §3.6b requires two, so until Joseph rules on the amendment the cell reads `UNRESOLVED` on that ground — and it would still be non-passing under §6.3's recommended rule — ⚠ **re-grounded in round 3: rev. 2 rested this on LEG 1's boundary needing `T`, and §6.3 recommends retiring leg 1, so the guarantee was load-bearing on a retired object.** It holds on the surviving instrument directly: **`s_sig` is a movement of a quoted significance across a decision threshold, and `T` exists nowhere in the tree** (§D.0). That does not decay if leg 1 is dropped. **The recommendation changes what must be argued, not whether the cell passes** |
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

**(b) ⚠ `ndf` IS A CODE-CONFORMANCE DEFECT AGAINST A RATIFIED PROTOCOL — NOT A NEW POLICY NEEDING A RULING. Rev. 1 framed it as a recommendation; that was an OVER-ask and an UNDER-claim at once (F3).**

`app_statmethods.tex:645-658` **already mandates** that for any N-D `χ²`: *"`ndf = n_reported` must not be used"*, and the quotation shall state *"(i) the inverse actually used — pseudo-inverse with its `rcond`, or the truncation rank … (ii) the **retained rank** as `ndf`; (iii) the rank-truncation scan …; (iv) which covariance is meant …; and (v) for every sample-covariance block entering the sum, its ensemble size `N`, its normalization convention …, the effective dimension `p` actually inverted after truncation, and the finite-ensemble treatment applied — or the explicit statement that none was."* Measured: `eavail_generator_significance.py:132` passes **`n_ea`**, the bin count. **So this is a departure from a landed, ratified protocol and needs a code fix, not a criterion decision.**

**⚠ AND FIXING IT DOES NOT MAKE THE REFERENCE DISTRIBUTION CORRECT. Protocol compliance is not statistical calibration, and this document must not imply otherwise.** The same protocol says the distributional assumptions *"assume independent Gaussian realizations and a truncation dimension chosen independently of the data, neither of which is established for a data-dependent rank cut"* (`:672-677`). **So rev. 2's unqualified *"distributionally correct"* is WITHDRAWN — that is the phrase to drop, not *"anti-conservative"* (F6). Only the SIGN is assertable; whether the change is a *correction* or a *loosening* is undetermined, because it depends on the rank-based null being accepted, which the protocol says is not established.**

**⚠ CLAUSE (v) IS UNADDRESSED BY THIS DOCUMENT AND ITS OPERANDS ARE NOW MEASURED.** `C_stat` from `N = 100` (`sbatch_bootstrap_5d_gpu.sh:5`, `--array=1-100%32`), `C_ML` from `N = 24` (`sbatch_seedscan_split_5d.sh:5`, `--array=1-24%24`), `45` bands, `p` undetermined until a truncation is chosen. **I propose no correction and deliberately do not reach for a Hartlap-type factor** — `OI-137` is ruled *"disclose, do not correct"* and the protocol's own reason applies here unchanged. §6.5 states what I can and cannot assess.

**AND THE COMPOUNDING, WHICH NOBODY HAD NAMED:** retained-rank `ndf` **raises** reported significances, and the uncorrected finite-ensemble bias **also inflates `χ²`** — the protocol measures the precision matrix as *"too large by a factor ≃2.76"* at `N=160, p=100` and says *"tension is overstated rather than hidden"* (`:664-670`). **Two same-direction effects on the same quoted number, neither quantified for Z, and their composition unexamined until now.** That is a reason to fix the conformance defect **and** not to quote a significance from the result until (v) is discharged — which is `PR-G10`'s own posture.

**The internal inconsistency rev. 1 identified is still real and is the reason the protocol exists:**
`chi2_to_sigma(chi2, n_ea)` at `:132` passes the **bin count** while `pinv` discards modes below its
cutoff. A quadratic form evaluated on a rank-`r` retained subspace is referred to a
`chi2`-distribution on `n` degrees of freedom. **Required, as CONFORMANCE: `ndf` = the retained rank,
reported per member** — mandated by clause (ii), not recommended by me. ⚠ **Rev. 1 added "this rests
on a distributional fact, not a preference"; that is WITHDRAWN under F6** — the rank-based null's own
assumptions are the ones the protocol says are not established for a data-dependent rank cut, so the
ground for the fix is **conformance**, not calibration. **⚠ AND THE DIRECTION IS DETERMINATE — REV. 1 OF THIS DOCUMENT DECLINED TO NAME IT AND WAS
WRONG TO.** I wrote that *"dropping modes reduces `chi2` and reduces `ndf`, and the two move `z`
oppositely, so the net sign is not determined."* **That conflated two different comparisons.** The
`ndf` **policy** change holds `chi2` fixed — `chi2` is *already* computed with `pinv` today — and at
fixed `chi2` the map is strictly decreasing in `ndf`. Since the retained rank is `<=` the bin count,
**adopting `ndf` = retained rank INCREASES every reported significance — ⚠ WHEREVER THE RETAINED
RANK IS STRICTLY BELOW THE BIN COUNT.** Where `pinv` discards nothing the two policies coincide and
the change is exactly zero; the qualifier is not decorative, because whether any mode is discarded
is a property of the member's spectrum and is **unmeasured on Z**. Measured at three synthetic
`(chi2, bins, rank)` triples in the probe's section 7: `3.9937 → 4.2362`, `3.9976 → 4.3766`,
`3.9956 → 4.6126`; the magnitudes are synthetic, the **sign is general** by monotonicity.

⚠ **AND THE WORD "ANTI-CONSERVATIVE" NEEDS ITS REFERENCE POINT, WHICH REV. 2 OF THIS SECTION LEFT
OUT.** The increase is anti-conservative **relative to today's practice, not relative to truth** —
and those two framings cannot both be asserted. **If `ndf` = retained rank is the distributionally
correct policy, then current practice is OVER-CONSERVATIVE and this is a CORRECTION, not the
introduction of a bias.** Calling it a bias would presuppose that the bin count is right, which is
the thing being changed. What Joseph should get is: a change with a **known sign**, whose
**interpretation** as correction-versus-loosening follows from whether the rank-based null
distribution is accepted — and that is the decision, not a side effect of it. The
indeterminate comparison — whether to discard modes at all — is a different question and is not
what this recommends. *(Finding and framing: the `z-independent-assessor` lane.)*

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
| **terminal outcomes** | **MET** — the whole interval lies on the claim's side of `T`, for every declared pair and every `k`. **NOT MET** — some declared pair's interval crosses `T`; report the pair, the `k`, and the interval. **INCONCLUSIVE** — `rho >= 1` (bound vacuous), or ⚠ **the RETAINED SUBSPACE moved** (`‖P_0 − P_k‖_2 > 1e-8` on the projected covariance; **rank identity is insufficient and rev. 1 of this document wrongly gated on it** — §2.1a), or `p = 0` for some pair so `Nsigma` is infinite and the statistic is **undefined**, which must be reported as undefined and never as zero movement |
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

**Claim.** Let `C_0 ≻ 0` and `C_k ≻ 0` — **strictly positive definite, and ⚠ NOT satisfied by Z's trunk: §6.1's F1 row derives `rank(C_Z) <= 265` of `10,694` from Z's own operands, so `C_0^{-1/2}` does not exist there. Rev. 1 wrote "on the compared support", a phrase it never defined anywhere; §6.2 states the consequence for this theorem's ROLE** — and let
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

## 2.1a ⚠ THE LIMIT OF §2.1, AND IT WAS A DEFECT IN MY OWN TERMINAL-OUTCOME RULE

**Found by the `z-independent-assessor` lane. Reproduced here independently — from its description
rather than by running its probe, so the confirmation is a second measurement and not an echo.**

**§2.1 bounds `dᵀ C⁻¹ d`, with the TRUE inverse. The consumer computes `dᵀ pinv(C) d`**
(`eavail_generator_significance.py:107,132`) — **and so does this document's own probe**, at
`_chi2`. `pinv` discards modes below `rcond·σ_max`, so **when two members retain different
subspaces the interval does not transfer.** Rev. 1 of this document gated `INCONCLUSIVE` on retained
**rank**, which is a **proxy**, and `D.1(c)` of the same document already said why it is the wrong
one: *"pinning `rcond` does not pin the retained subspace."* **The analysis was right and the branch
was stated on the proxy.**

**The construction, measured in the probe's section 6.** Two near-equal eigenvalues **straddling**
the cutoff, then **swapped** — which holds the rank fixed while flipping which eigenvector is kept:

| | |
|---|---|
| `rho` | `0.455352` — comfortably inside any plausible `rho_crit` |
| retained rank | `8` vs `8` — **identical**, so the rank branch **never fires** |
| `‖P_0 − P_k‖_2` | **`0.9951`** — a mode has flipped |
| `chi2_0` / `chi2_k` / §2.1 floor | `8.586e+14` / `3.613e+09` / `5.900e+14` |
| §2.1 bound | **VIOLATED** |

`chi2` collapses, so `p` rises and `Nsigma` **falls** — a *"stays above `T`"* claim breaks while
`rho` reads `0.46`.

**⚠ THE LIMIT OF THE COUNTEREXAMPLE, CARRIED BECAUSE IT IS DOING REAL WORK.** The construction is
**synthetic**, at condition number `~1e15`, and needs **two** modes to swap in order to hold the rank
fixed. **Whether real Z members do this is UNMEASURED and nothing here claims they do. What is
established is that the guard did not exclude it.**

**Why §2.1's 120,000 evaluations missed it, which is the part worth absorbing.** That ensemble is
well-conditioned (`C_0 = AAᵀ + nI`), so nothing sits near the cutoff and the retained subspace never
moves. **That is agreement measured over a domain that excludes the failing regime** — precisely the
shape `FINDING-20260910`'s amendment 2 identified in `SPEC` §6 item 1, reproduced **one layer down,
in a probe written after I had cited that amendment.** And the excluded regime is the one the
consumer documents *itself* in, at `:98-101`: *"a highly-correlated systematic covariance (flux is a
coherent normalization) can be near-singular -> pinv amplifies shape directions."*

**THE REMEDY — one clause, and it chains this document's own two theorems.** Gate on
**retained-subspace identity**, not rank. If both members retain the same subspace `S` with
orthonormal basis `U`, the consumed form is `(Uᵀd)ᵀ (Uᵀ C U)⁻¹ (Uᵀd)` with a **true** inverse; `Uᵀ`
has orthonormal rows, so §2.2 gives `rho(Uᵀ C_0 U, Uᵀ C_k U) <= rho(C_0, C_k)` and §2.1 applies
inside `S`. **So subspace identity is sufficient, and it is checkable in one line.**

**The remedy is power-tested in both directions, with `rho` held across the arms so the difference is
attributable to the subspace and to nothing else** (probe section 6):

| arm | `rho` | `‖P_0 − P_k‖_2` | subspace branch | §2.1 bound |
|---|---:|---:|---|---|
| straddling and swapped | `0.455` | `0.9951` | **fires** | violated |
| same swap, both modes retained | `0.500` | `1.046e-15` | **silent** | holds |

*(One defect in my own control, recorded because it is the same shape as the subject: the silent arm
first compared `C_0`'s projector **with itself**, so it would have reported a zero gap whatever the
perturbation did — a control that cannot fail, inside a probe about a guard that cannot fail.*

⚠ **AND MY FIRST ACCOUNT OF HOW I CAUGHT IT WAS ITSELF WRONG, RULED BY JOSEPH.** I wrote that the
exact `0.000e+00` *"gave it away"* because a genuine comparison returns float noise. **That is not
sound: identical deterministic code paths on identical inputs are legitimately bit-equal, and
cancellation and underflow also produce hard zeros.** An exact zero is **a prompt to check, never a
finding** — in either direction, so it is no more evidence of a live comparison than of a dead one.
**The test is to perturb one operand and confirm the output moves**, which the probe now does at
`_assert_comparison_is_live`: identical operands give a gap of `0.000e+00`, and moving one operand
across the cutoff gives `0.9951`. **That** establishes the comparison is real; the zero only made me
look.)

**Drafting of this clause is mine, explicitly not the assessor's** — it identified the defect and the
remedy's shape and declined to write the criterion, which keeps its later grading of this leg
non-circular.

## 2.1b Leg 1 DOMINATES every `uᵀ C u` functional — PROVEN

**This is the result Part 6's recommendation rests on.**

**Claim.** If `rho(C_0, C_k) <= δ < 1` then **for every** `u` with `uᵀ C_0 u > 0` — ⚠ **the hypothesis is load-bearing and rev. 1's corollary table dropped it (F8): a zero-variance baseline bin makes the ratio unbounded, and the reported-support predicate `x_cv > 0` is NOT the same condition as positive variance**:

    (1 - δ)  <=  uᵀ C_k u / uᵀ C_0 u  <=  (1 + δ)

**Proof.** With `w = C_0^{1/2} u`, `uᵀ C_k u = wᵀ(I + E)w` and `uᵀ C_0 u = wᵀw`, and `E`'s
eigenvalues lie in `[−δ, δ]`. Sharp, for the same reason §2.1 is — and note it needs **no inverse**,
so unlike §2.1 it is **untouched by §2.1a's `pinv` limit.**

**Checked:** `37,378` (pair, functional) evaluations **including every `e_i` and the all-ones
vector**; both sides hold at `1.000000000000` and sharpness is reached.

**The corollaries are exactly the statistics `SPEC` §3.6b asked for as a SECOND leg:**

| `u` | what it bounds |
|---|---|
| `e_i`, **where `e_iᵀC_0e_i > 0`** | every per-bin **variance** within `[1−δ, 1+δ]`, so every per-bin **σ** within `[√(1−δ), √(1+δ)]` — hence `s_med`, the per-bin **max**, `p90`, the whole per-bin movement distribution |
| `1` (all-ones) | the total |
| rows of `M` | **`s_proj`, for every projection — designated or not** (with §2.2 carrying it from the trunk) |
| — | `Tr C` is a sum of `e_iᵀ C e_i`, so **`s_agg`** too |

**So `s_agg`, `s_med`, the per-bin distribution and `s_proj` are COROLLARIES of leg 1, not
independent constraints.** And §2.1 additionally covers the inverse-quadratic consumer, which no
diagonal statistic can reach at all.

### And the second leg's own motivating hazard is one leg 1 sees and the second leg does not

`SPEC` §3.6b gives its reason for requiring two legs in one sentence: *"the same trace can be diffuse
or concentrated, so the per-bin leg is independently binding."* **That is a defect of TRACE-based
statistics, and `rho` is not trace-based — it is a worst-direction statistic, so concentration is
precisely what it is most sensitive to.** Measured (probe section 8), at `n = 50` and **equal trace
change**:

| | `Tr(ΔC)` | `s_agg` | per-bin median | `rho` |
|---|---:|---:|---:|---:|
| diffuse (`ε` on all `n` directions) | `1.0000` | `0.009950` | `0.009950` | `0.020000` |
| concentrated (`nε` on one direction) | `1.0000` | `0.009950` | **`0.000000`** | **`1.000000`** |

**`s_agg` is identical to twelve digits. The per-bin median reads EXACTLY ZERO on the concentrated
case** — because one bin moved and a median cannot see it. **`rho` separates them by a factor `n`.** ⚠ *Rev. 1 added "and at `1.0` it would be refused as `INCONCLUSIVE`"; that is `n`-specific and is withdrawn — the identical perturbation gives `rho = 0.20` at `n = 10`, which PASSES a `0.2` gate (probe §9). The separation is structural; the refusal was an artifact of `n = 50`.* So the hazard §3.6b
introduced a per-bin leg to catch is one that an `f_med`-shaped leg is blind to and leg 1 catches.
*(The `SPEC`'s own `D2` had already noticed half of this — that the median fixes the coverage
fraction at `50%` "by default rather than by argument".)*

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
built, **provided `M C_Z^(0) Mᵀ` is nonsingular.**

### ⚠ AND THE `M`-INDEPENDENCE CLAIM THAT FOLLOWED IS WITHDRAWN — F2, ROUND 2

**Rev. 1 concluded from the above: *"So the BOUND is `M`-independent … `rho_5D` can be evaluated BEFORE the projection question is settled, and a small `rho_5D` discharges the sensitivity question for all marginals at once."* That was this document's flagship practical claim and it does not hold as stated.**

The proof needs `C_k − C_0 = C_0^{1/2} E C_0^{1/2}`, i.e. **`range(C_k − C_0) ⊆ range(C_0)`** — automatic when `C_0 ≻ 0`, and **not** automatic once the baseline is singular, which §6.1's F1 row shows Z's is **by construction**. Measured in both directions (probe §9), with the baseline rank-deficient:

| perturbation | `max rho_proj / rho_support` | trials violating |
|---|---:|---|
| **inside** `range(C_0)` | `1.000` | `0` of 2,475 — monotonicity **holds** |
| **leaking outside** | **`2340.8`** | **every** trial — monotonicity **fails** |

**Range containment is neither stated, gated, nor measured on Z — and it is probably false in production**, because members at different estimator baselines give different band vectors and therefore different spans. **The cost of the withdrawal is stated rather than softened: `rho` can no longer be evaluated once on the trunk to cover every marginal, so the criterion re-couples to the `M`-designation question of `D.1(a)`.** §6.3 is the alternative, and it does not need this claim.

**What still stands, and the scope of the heading is deliberately narrow:** the monotonicity
**theorem** itself — for any `M` with `M C_0 Mᵀ` nonsingular **and a positive-definite baseline**.
**It is the LIFT to a singular trunk that fails, not the theorem.**

⚠ **AND REV. 2's OWN EDIT LEFT THE WITHDRAWN CLAIM STANDING HERE, WHICH IS WORSE THAN NOT EDITING
IT.** Rev. 1 closed this subsection with *"the practical consequence: `rho_5D` can be evaluated
before the projection question is settled, and a small `rho_5D` discharges the sensitivity question
for all marginals at once."* Rev. 2 added the retraction six lines above **and did not delete that
sentence**, so it survived *inside* the paragraph headed *"what still stands, unqualified."*
**It is deleted here. It does not stand, it never stood on a singular trunk, and no reader entering
at §2.2 should find it affirmed.**

*Why the edit missed: I anchored the replacement on the phrase "So the BOUND is `M`-independent" and
the survivor said the same thing in different words. **I repaired the sentence I searched for rather
than the claim I was withdrawing** — and a line-oriented `grep` acquitted me because the survivor is
line-wrapped. A whitespace-insensitive count over the CLAIM, not the wording, is what found it: 1
occurrence before the edit, 2 after.*

**What is NOT `M`-independent, and never was:** the *reported significance*. `chi2_0`, `ndf` and the
retained rank all depend on which `M` is used, so `D.1(a)`–`(c)` remain preconditions.

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
grows**, asymptotically as `(z_0 - T) * sqrt(2/ndf)`.

⚠ **AND THE HEADLINE FIGURE REV. 1 DREW FROM THIS WAS COMPUTED AT AN `ndf` THIS DOCUMENT'S OWN
`D.1(b)` FORBIDS (F4).** Rev. 1 wrote that at a projection with thousands of bins a
*"one-to-two-percent"* relative spectral perturbation suffices to move a `4-sigma` claim below
`3-sigma`. **That is `rho_crit` at the BIN COUNT.** At the effective-rank scale — `ndf = 263`, which
is S's measured value and the order Z's own bound implies (§6.1 F1) — **`rho_crit ≈ 0.087`, i.e.
`8.7%`: looser by `4`–`6×`.** The table above had rows at `7/42/247/4825/10694` and **none at the
scale the object actually has.** Arithmetic right, population wrong — and it cut *against* §6.4's own
self-objection, whose *"least permissive"* `16.6×` row sat at the most-forbidden `ndf`. **Use the exact formula, not the asymptote:** the asymptote is conservative at large `ndf`
and **permissive below `ndf ≈ 250`** (at `ndf = 7` it gives `0.535` against the true `0.417`), so
quoting it as a shortcut errs in the unsafe direction exactly where projections are small.

**Set beside §B.0's control-B measurement, this is the whole argument of Part B in two numbers:** the
two proposed gates return exactly `0.0` on a perturbation that moves the consumed quantity by a factor
of `5.26`, while the perturbation a real large-`ndf` claim can absorb is of order `1%`.

---

# 6. ROUND 2 — OUTCOME **(2)**: THE UNIVERSAL 5D BOUND IS REJECTED AS THE ACCEPTANCE INSTRUMENT, AND A NARROWER CLAIM IS RECOMMENDED

**This Part replaces rev. 1's Branch B recommendation, which is WITHDRAWN. The rev.-1 text is quoted
where it was wrong rather than deleted.** Under the stopping rule's three outcomes this is **(2)** —
*the intended claim cannot be supported, with a narrower claim recommended* — which Joseph named as a
legitimate result, not a failure.

**The governing instruction, quoted:** *"Prefer the simplest criterion that supports the intended
publication use. A universal 5D bound is optional, not an objective in itself. If its assumptions
cannot be justified, consider direct checks on the declared publication projections and consumers.
**Do not add regularization, discard directions, or change inference conventions merely to make a
theorem applicable.**"*

**That instruction retires my repair path rather than redirecting it.** F1 said `rho` needs
`C_0 ≻ 0`. My planned fix was to define a retained-subspace support and restrict `rho` to it —
**which is discarding directions to make a theorem applicable, and is on the prohibited list.** So the
live question was never *"how do we make `rho` defined on the trunk"*; it is *"does the intended
publication use need a universal 5D bound at all?"* **It does not.**

## 6.1 THE ROUND TABLE

| finding | corrected claim / implementation | decisive test | remaining limitation |
|---|---|---|---|
| **F1** — `rho` requires `C_0 ≻ 0`; the trunk is not | **`rank(C_Z) <= 265` of `10,694` reported bins, DERIVED FROM Z'S OWN OPERANDS** — 44 two-endpoint bands at rank `1`, Flux at `N_u=100 → 99`, `C_stat` at `N=100 → 99`, `C_ML` at `N=24 → 23`; `D_Z` diagonal, rank-preserving. So `C_Z^{-1/2}` **does not exist**, by construction and not as a defect | probe §10; **singular case mandatory and present** — §9's `diag(1,1,0)` and §10's counting argument | the note says *"ALMOST all other bands are ±1σ pairs"* and its table is *"(examples)"*, so the bound is **not tight**: any other multisim raises it by `N−2`. The **conclusion** is robust — a counting argument over ~45 bands cannot span `10,694` |
| **F1(b)** ⚠ **my own inherited error** | **Rank `263` is S's, not Z's or G's.** `app_statmethods.tex:636`'s subject is *"The standard-P4 5D **candidate** covariance"* = the component **donor**. A first version of my probe called it *"the production trunk"* | read the sentence's subject; corrected in probe §9's docstring with the error quoted | none — but it is the second definite-description misroute I have accepted from a relay today |
| **F2** — §2.2's monotonicity fails under support restriction | **THE M-INDEPENDENCE CLAIM IS WITHDRAWN** (§2.2). It holds only if `range(C_k − C_0) ⊆ range(C_0)`, which is **neither stated, gated, nor measured** — and is *likely false* in production, since different estimator seeds give different band spans | probe §9, both directions: **inside** `range(C_0)` max ratio `1.000` over 2,475 trials; **leaking outside** max `2340.8`, every trial violating | **this removes the flagship practical benefit.** `rho` can no longer be evaluated once on the trunk to cover all marginals, so the criterion re-couples to the `M` designation question (`D.1(a)`) |
| **F9** — domination ⇏ non-bindingness | **REV. 1's HINGE IS VOID, NOT WEAK.** Leg 2 is implied by leg 1 **iff `rho_crit <= τ`** — a statement about **thresholds**, not values. Domination gives `s <= rho`; it says nothing about the two gates | probe §9: at `ndf=42`, `rho_crit=0.2020` permits per-bin `σ` to move `9.63%`, so leg 2 **binds independently** at `τ ∈ {0.1%, 1%, 5%}`; at `ndf=10694` still at `τ=0.1%` | **and my own self-objection (i) had already said `rho_crit` is `17×`–`270×` looser than the candidate boundaries — which IS that regime.** I put the refutation and the claim in one document |
| **F7** — the §6.2 amendment was self-contradictory | **MOOT — the amendment is withdrawn with Branch B.** Recorded because the defect is diagnostic: under the min-rule a tighter use merely lowers leg 1's boundary, so by my own domination result the *"second leg becomes required"* trigger **could never fire.** A gate that cannot fire, in the clause offered as proof it was *"a replacement, not a deletion"* | inspection; no test needed | none. It is the fourth instance today of a shape I had already catalogued in the same document |
| **F4** — §5.3's headline was computed at a forbidden `ndf` | **the `"one-to-two-percent"` warning is corrected.** At `ndf=263` (S's measured rank, and the scale Z's own bound implies) `rho_crit ≈ 0.087` — **`8.7%`, looser by `4`–`6×`.** My table had rows at `7/42/247/4825/10694` and none at the scale the object actually has | probe §2 and §9 tables, now carrying `263` | arithmetic was right, **population wrong** — and it cut *against* my own objection (i), whose *"least permissive"* `16.6×` row was computed at the most-forbidden `ndf` |
| **F8** — the corollary dropped its own hypothesis | **§2.1b's table now carries `uᵀC_0u > 0`.** A zero-variance baseline bin makes the ratio unbounded | probe §9: `diag(1,1,0)` vs `diag(1,1,0.5)` — `rho = 0` on the retained 2-dim subspace while the dropped bin's variance ratio is `0.5/0 = ∞` | **not hypothetical**: `(E_avail,W)` is structurally singular by my own words, and the reported-support predicate (`x_cv > 0`) is **not** the same as positive variance |
| **F3** — `D.1(b)` under- and over-claimed | **UNDER: it is a CODE-CONFORMANCE DEFECT, not a new policy.** `app_statmethods.tex:648` already mandates *"(ii) the retained rank as ndf"*; `eavail_generator_significance.py:132` passes `n_ea`. **No Joseph ruling is needed to fix a departure from a ratified protocol.** **OVER: clause (v) is unaddressed** — it requires, per sample-covariance block, `N`, the normalization convention, the effective `p` after truncation, and the finite-ensemble treatment **or an explicit statement that none was applied**. My document had zero of that | direct reading of `:645-658`; `N=100` (`sbatch_bootstrap_5d_gpu.sh:5`) and `N=24` (`sbatch_seedscan_split_5d.sh:5`) measured here | **and the composition is named for the first time:** retained-rank `ndf` **raises** significance, and the uncorrected finite-ensemble bias **also inflates `χ²`** (`:664-670`). **Both push the same way and nobody had put them together** |
| **F6** — *"distributionally correct"* | **WITHDRAWN, and it is the phrase to drop rather than *"anti-conservative"*.** The protocol itself says the assumptions *"assume independent Gaussian realizations and a truncation dimension chosen independently of the data, neither of which is established for a data-dependent rank cut"* | direct reading of `:672-677` | **only the SIGN is assertable.** *"Correction"* vs *"loosening"* is undetermined, and **protocol compliance is not calibration** — the document must not imply that fixing `:132` makes the reference distribution right |
| **concentration wording** | *"at `1.0` it would be refused"* is **`n`-specific and is dropped.** The **separation** is structural | probe §9: the identical perturbation gives `rho = 0.20` at `n=10` (**passes** a `0.2` gate), `1.00` at `n=50`, `5.26` at `n=263` | the qualitative claim survives; the sentence did not |

## 6.2 WHAT SURVIVES, AND IN WHAT ROLE

**§2.1, §2.1b and §2.2 are theorems and remain adoptable exactly as stated.** Nothing below retracts
them. **What is withdrawn is their ROLE as the acceptance instrument on the trunk** — because their
hypotheses (`C_0 ≻ 0`; `range(C_k − C_0) ⊆ range(C_0)`) are, respectively, **false by construction**
and **unmeasured and probably false**. A theorem whose hypothesis fails on the object is not a weak
criterion; it is not a criterion.

They keep three legitimate uses: as **sufficient conditions** on any declared object where
`C_0 ≻ 0` is *measurable* rather than assumed — which the small projections may well satisfy; as the
**diagnostic** that explains *why* the diagonal statistics are inadequate (§2.1b's concentration
case); and as the reason `D1`'s retained-subspace gate is the right shape.

## 6.3 THE NARROWER RECOMMENDATION — DIRECT CHECKS ON THE DECLARED CONSUMERS

**Recommended: the acceptance rule is evaluated ON THE DECLARED PUBLICATION PROJECTIONS, per
consumer, with no universal bound and no support surgery.**

| field | |
|---|---|
| **quantity** | for each declared `(generator, projection)` pair, the quoted significance and the inversion's own declarations |
| **statistic** | `s_sig = max` over declared pairs **and** declared offsets of `\|Nsigma_k − Nsigma_0\|`, an absolute difference in a quantity already in σ units; **plus**, per member and per projection, the four declarations `app_statmethods.tex:645-658` already mandates — the inverse actually used with its `rcond` or truncation rank, the **retained rank as `ndf`**, the rank-truncation scan, and which covariance is meant |
| **denominator** | none for `s_sig`. **This removes the `chi2_0 = 0` problem and needs no metric on a singular trunk** |
| **why this is now the simplest sufficient instrument** | the declared consumers are **small and enumerable** — the `(E_avail,W)` object is **42 bins**, so its conditioning is **directly measurable** rather than bounded. A bound is what you need when you cannot look; here you can look |
| **⚠ AND IT REVERSES MY OWN SUPERSESSION OF `PROPOSAL-20260908`'s C-1, WHICH WAS ASYMMETRIC** | I superseded C-1 as *"a sampled maximum with no bound and no coverage argument"* — while simultaneously arguing, for the offset set `K`, that *"the population is the finite declared set, not an inferred distribution"* and that **the max is therefore exact**. **I applied finite-declared-population logic to `K` and demanded distributional coverage from the projection set in the same document.** That is my catalogued asymmetric-comparison failure. C-1's statistic is **reinstated** as the use-facing leg; its authoring lane was right and my ground for superseding it was not |
| **population / scope** | the declared offset set `K` **×** the declared `(generator, projection)` pairs. Both finite, both predeclared, so the max is exact and no inference to an unmeasured pair is made — and **no claim is made about undeclared pairs**, which is the honest limit rather than a gap |
| **terminal outcomes** | **MET** — every declared pair's significance stays on the claim's side of `T`, and rank/`rcond`/subspace declarations are stable across members. **NOT MET** — a pair crosses `T`, or a declaration moves. **INCONCLUSIVE** — `p = 0` so `Nsigma` is undefined (reported as undefined, never as zero movement); or **`INCONCLUSIVE / VACUOUS SEED VARIATION`** (`PREDECLARE-20260901-cause3-mii…:230`), the positive control |
| **cost** | zero incremental production — arithmetic on members `D3` would produce, on `42`-to-`4825`-bin objects rather than `10,694²` |
| **what it does NOT do** | it makes **no** statement about the trunk as a whole, and none about projections outside the declared set. **A universal claim is exactly what I am giving up**, deliberately, per the steer |

## 6.4 `cause3_corr` UNDER THE NEW FRAMING — BRANCH A, AND IT CARRIES EXACTLY ONE TOLERANCE

**Recommended second binding leg: the INVERSION-DECLARATION STABILITY of each declared projected
object across members** — retained rank, the `rcond` actually applied, the condition number, and the
retained-subspace projector gap `‖P_0 − P_k‖_2`.

**⚠ REV. 2 CLAIMED THIS LEG *"NEEDS NO `τ`"* AND, FOUR POINTS LATER, THAT ITS `1e-8` TOLERANCE
*"WAS ATTACKED AND SURVIVED"*. BOTH CANNOT STAND, AND THE FIRST IS FALSE.** Measured across the four
components (`numpy` 1.26.4; three same-shaped members at `n = 200`):

| component | behaviour across members | disposition |
|---|---|---|
| **retained rank** | integer; equality is meaningful — **but ⚠ R4-2: for orthogonal projectors `rank(P) != rank(Q)` implies `‖P − Q‖_2 = 1` exactly, so the `1e-8` subspace gate ENTAILS rank equality.** Measured: `0 / 4000` unequal-rank pairs are silent under the subspace gate even with **nested** bases (the most favourable case), max deviation from `1.0` being `1.332e-15`; positive control, `2000 / 2000` fire at **equal** rank with a different subspace, so the gate is not inert | ⚠ **MOVED TO REPORTED-AND-OPERAND in round 4.** It is **required as a declaration** (clause (ii) — it *is* the `ndf`) and it is an **operand** of the subspace gate, which cannot be computed without it. It is **not an independent gate**, because its failure mode is entailed |
| **applied `rcond`** | ⚠ **CORRECTED IN ROUND 4, AND THE ERROR WAS WORSE THAN AN OFF-ENVIRONMENT MEASUREMENT.** Rev. 3 quoted `4.4408920985006262e-14` as the applied cutoff. **That is `numpy` 2.x behaviour, and it was never a measurement of `numpy` at all — I computed `max(shape)·eps·σ_max` myself in a script running `numpy` 1.26 and labelled my own arithmetic as the library's.** Measured properly, by observing which modes `pinv` actually drops on a diagonal input at `n = 10 / 200 / 4825`: the applied **relative cutoff is the literal `1e-15`**, reproducing the `1.26` default at all three sizes and the shape-dependent formula at none. **Production is `numpy` 1.26.4** (`root_6_28`, the prefix the arms run in), so `1e-15` is the production value | ⚠ **REPORTED, NOT GATED — and the conclusion holds under BOTH defaults for DIFFERENT reasons.** Under `1.26` the cutoff is a **literal**; under `2.x` it is a function of **shape alone**. Either way it is member-independent, so an equality gate on it **cannot fail** — gating it would have been the very shape this document keeps diagnosing. **That the same code gives different cutoffs under different library versions is precisely why clause (i) demands the cutoff *actually applied* be stated at the point of quotation** |
| **condition number** | `3.387e6` / `4.455e6` / `4.943e6` — **continuous**, so equality is impossible | ⚠ **REPORTED, NOT GATED — decided explicitly.** Gating it needs a tolerance, and **no tolerance for it is justifiable from anything in this tree** — the same blocker that made me withhold `cause3_corr`. Gating it without one is what Joseph barred, so it is **dropped from the gated set** and kept as the diagnostic that makes a rank change interpretable |
| **`‖P_0 − P_k‖_2 <= 1e-8`** | a genuine threshold | **GATED. This is the leg's one tolerance** |

**So the corrected claim is four-part, and it is stronger than *"no `τ`"*: the leg carries
EXACTLY ONE GATE AND EXACTLY ONE TOLERANCE — `‖P_0 − P_k‖_2 <= 1e-8` — and that one was
adversarially attacked and survived.** The other three components are **declarations**:
required, reported, and re-checkable, but not independently gated.

⚠ **AND THE CRITERION THAT DISTINGUISHES THE TWO REPORTED-NOT-GATED CASES IS DIFFERENT IN
EACH, WHICH ROUND 3 ELIDED BY GIVING ONLY ONE REASON.** The `rcond` row is **VACUITY** — an
equality gate on it can never fail, so a green light there means nothing. The rank row is
**REDUNDANCY** — its gate *can* fail, but only when the subspace gate also fails, so it adds
no discriminating power. **Vacuity is misleading; redundancy is merely inert**, and only the
first is a defect. Round 3 justified the `rcond` disposition on *"cannot fail"* alone, which
does not reach rank — and the reviewer was right that applying one criterion consistently
gives the same disposition anyway. **Both are reported; the reasons are not
interchangeable and are now stated separately.** It still clears the original
blocker, because that blocker was *"no **justified** number exists"* — not *"no number exists"*.

**Why this is Branch A rather than a relabelling of Branch B:**

1. **Its one tolerance is justified by a survived attack rather than by my judgement**, and its other
   three components need none — two because they are reported rather than gated, one because integer
   equality needs no `τ`. The blocker that made me withhold `cause3_corr` was the absence of a
   *justifiable* number; here there is one number and it has a justification I did not supply.
2. **It binds independently — and ⚠ REV. 2 GROUNDED THIS ON A REGIME-DEPENDENT WITNESS.** Rev. 2
   cited §2.1a flatly (`rho = 0.455`, rank identical, subspace flipped). **But `rho = 0.4554` exceeds
   `rho_crit` in most realistic regimes** — `0.202` at `ndf=42, z_0=4`; `0.177` at `ndf=263, z_0=5`;
   `0.063` at `ndf=4825, z_0=6` — **so leg 1 has already failed there and §2.1a witnesses nothing.**
   It is a valid witness only where `rho_crit > 0.455`, e.g. `ndf=42, z_0=6`.
   **The conclusion survives on the better half, which needs no witness and no regime: a SMALL `rho`
   permits an eigenvalue to cross the cutoff, so leg 1 passing does not imply rank stability.**
   Measured (probe §11): `rho = 1.005e-01` — an order of magnitude inside any plausible `rho_crit` — with the retained rank moving `6 → 5`.
   **And F9's threshold objection does not reach this leg because `‖P_0 − P_k‖_2` is NOT a `uᵀCu`
   functional, so it is not in the dominated class.** ⚠ Rev. 2 wrote *"not a thresholded statistic in
   the dominated class"*, welding two claims: **the class claim is true and carries the argument; the
   "not thresholded" half is FALSE**, as the table above now says outright.
3. **It is justified by a RATIFIED protocol, not by my judgement** — `app_statmethods.tex:645-658`
   clauses (i), (ii) and (iv) require exactly these declarations *at the point of quotation*, and
   clause (iv) exists because *"the 5D candidate, its 4D projection and the published 2D block have
   different ranks."* A criterion that they be **stable across members** is what makes those clauses
   checkable for a family rather than for one artifact.
4. **The `1e-8` subspace tolerance is not mine and was attacked.** The third lane's own tolerance
   attack — eigenvector rotations at `θ ∈ {1e-12 … 1e-9}`, ~46,000 trials, baseline spectrum to
   `3e-16` — gave a worst exceedance of `1.000002`, float noise.

**So §3.6b's two-leg requirement is satisfied with two legs that both bind and neither of which needs
an unavailable number.** `cause3_corr` should be **retired as a key**, not because no protection is
needed, but because the protection that is needed is a **declaration-stability leg** rather than a
tolerance on a correlation statistic. **That is a different recommendation from rev. 1's and it does
not rest on the void hinge.**

## 6.4a ROUND 4 — THE WITHDRAWAL SWEEP IS NOW AN INSTRUMENT, NOT A DESCRIBED PROCEDURE

**R4-3, and the objection is exact: rev. 3 claimed *"the sweep now runs by claim content with
multiple paraphrases across all three files"* and shipped no artifact. `git diff --name-only` over
that commit returns three content files and nothing else, so the next lane could not re-run it.**
And the procedure is demonstrably fallible **four** times over: rev. 2 missed the §2.2 survivor;
round 3's first scoping missed both the probe header and `CATALOG.md`; and **the independent
reviewer's own multi-paraphrase `grep` missed the probe header too — it found it by reading.**

**This document's own repeated lesson is that naming a failure shape protects nothing.** So:

**`docs/orchestration/state/check-withdrawal-completeness-20260910.py`** — a **pinned inventory**,
not a heuristic. Every withdrawn claim carries its paraphrases and an **approved occurrence count
per delivery file, with the reason each is permitted**. The check compares live counts against the
approved ones and **fails closed** on any difference: a new affirmation anywhere (count rises), an
approved quotation deleted so its retraction is orphaned (count falls), or a **new delivery file with
no classification at all**. `8` withdrawn claims × `3` files = `24` pinned counts.

**Its self-test is a power test in three directions** — inject a live affirmation, delete an approved
quotation, add an unclassified file — and requires the check to fail in each while staying silent on
the clean tree. **A check that only passes on the current tree proves nothing about its ability to
detect anything.**

**⚠ WHAT IT CANNOT DO, stated so a green run is not over-read:** it compares **counts**. An approved
quotation rewritten *in place* into a live affirmation would not move the count and would stay green.
It catches appearance, disappearance and re-scoping; **it does not read meaning.** Anyone editing the
prose around an approved occurrence must re-read its pinned reason.

### ⚠ ROUND 5 — TWO DEFECTS IN THAT INSTRUMENT, AND THE FIRST IS THE FIFTH INSTANCE OF ONE SHAPE

**R5-1. The check DISCLAIMED in its docstring exactly what it ASSERTED in its output.** The prose
above was right; the terminal line printed *"Every occurrence is an approved quotation inside a
withdrawal. No live affirmation."* — **the meaning-level claim the docstring denies making.**
Reproduced here before repair (the reviewer's **Test K**): rewriting an approved quotation *in
place*, keeping the phrase and inverting the framing from *"REV. 2's OWN EDIT LEFT THE WITHDRAWN
CLAIM STANDING"* to *"THIS REMAINS THE OPERATIVE PRACTICAL CONSEQUENCE, RESTORED AFTER REVIEW"*,
left the counts at **`5 → 5`** and the checker **GREEN**.

**That is the headline-overrides-body shape — the one §0.0 diagnoses in this document — inside the
instrument built to prevent it. Fifth instance today.** The two halves are dispositioned
**separately, not merged**: the count-only limitation is **inherent** and is carried to Joseph; the
**wording was a defect** and is fixed at the print statement, which now states what the check
establishes (*"no occurrence has appeared or vanished since it was classified"*) and what it does
not.

**R5-2. Injection (d) did not cover what its label advertised.** `DELIVERY` was a hardcoded
three-entry dict with **no `glob`, `iterdir`, `walk` or `rglob` anywhere in the file** — zero
filesystem discovery. Injection (d) mutated the *in-memory* dict, so it tested `audit()`'s handling
of a key **someone had already remembered to add**; an unregistered fourth file carrying a live
affirmation left the checker **green while blind. And that is round 3's own defect one layer down**
— round 3's sweep was *"scoped to the `.md`"* and missed the probe header and `CATALOG.md`, and the
instrument built to prevent that **reproduced the scoping assumption.**

**Fixed by discovery rather than by a better label:** any file under `docs/orchestration/` whose
content carries a registered paraphrase must be in `DELIVERY`, or the check fails closed. Measured
cost `583` files / `12.0` MB / **`0.15` s**, so enumeration was never buying anything. Injection (d)
is relabelled to what it actually tests, and a real coverage test **(e)** writes an unregistered file
into a temp root and requires it to be found.

**⚠ AND MY OWN FIX TAUGHT ME THE SYMMETRIC LESSON WITHIN MINUTES, TWICE.** Discovery's **first live
run** flagged two August files from other lanes — `PREDECLARATION-20260816-hrowindex4d-readback.md:68`
says *"An exact comparison **needs no tolerance** and must not be given one"*, an innocent sentence
about a bit-exact readback. **A false positive**, because *"needs no tolerance"* is generic English.
I tightened it, added a **false-positive control (f)** to the self-test, **and that control
immediately caught a second one** — the four-word phrase naming a pipeline's main line matches
ordinary prose. *(The literal strings are deliberately NOT reproduced here: this document is
inside the audited corpus, so quoting a match string would inflate its own pinned count. The
strings live in the checker, which excludes itself for the same reason.)*

**So a paraphrase may now be an AND-GROUP**: the generic phrase **together with** the rank token,
which is the difference between matching a **wording** and matching a **claim**. **Too-narrow wording gave
false negatives (R3-1's survivor); too-generic wording gives false positives. Both are one error —
the search string is not the claim** — and a discovery check without a false-positive control is
one-directional: it would flag unrelated documents forever and train its reader to ignore it.

**Self-test now fires in five directions and is silent in two:** injected affirmation, deleted
quotation, unpinned corpus key, unregistered file on disk, and — negatively — a clean tree and a tree
of innocent generic prose.

**⚠ AND ITS FIRST RUN FAILED ON ITS AUTHOR'S OWN CLASSIFICATION.** I pinned the rank-263 claim at `0`
for this document while §6.1's F1(b) row quotes it — so invocation one returned `[FAIL]`. **Hand
classification is exactly as fallible as the sweeps it replaces, which is the whole argument for
pinning rather than remembering.**

**A CENSUS NOTE, because the reviewer looked for something that was not there and correctly declined
to treat its absence as a finding.** Rev. 3's *"seven residual occurrences, every one a quotation
inside a withdrawal"* **is not in either content file.** It lived in the round-3 **commit message**
and in this lane's report to the coordinator, and nowhere else. **That is precisely the defect R4-3
names** — an assurance asserted in correspondence with no artifact behind it — and it is why the
counts now live in a file that fails closed instead of in a sentence. The current census is the
instrument's own output: `24` pinned counts, all matching.

## 6.5 WHAT I RETURN RATHER THAN RESOLVE

**The finite-ensemble question, and I state plainly that I cannot settle it.** Clause (v)'s operands
are now measured — `C_stat` at `N = 100`, `C_ML` at `N = 24`, `45` bands, `p` undetermined until a
truncation is chosen. **I do not propose a correction, and I do not reach for a Hartlap-type
factor**: `OI-137` is ruled *"disclose, do not correct"*, and the protocol's own reason is that the
factor *"assumes independent Gaussian realizations and a truncation dimension chosen independently
of the data, neither of which is established for a data-dependent rank cut."* Neither is established
here either. **What I can do and recommend: record `N` beside each block in the construction receipt
— the protocol calls that half unconditional — and state explicitly that no finite-ensemble
treatment was applied.** What I cannot do is tell you the size of the resulting bias on a sum of ~45
deterministic rank-one outer products plus two sample blocks.

**And the compounding is the part that should reach Joseph:** fixing `:132` to retained-rank `ndf`
**raises** significances, and the uncorrected finite-ensemble bias **also inflates `χ²`**. **Two
same-direction effects on the same quoted number, neither yet quantified, and their composition was
unnamed until this round.** That is a reason to fix the conformance defect and to *not* quote a
significance from the result until (v) is discharged — which is `PR-G10`'s own posture.

**Two foundational issues have now failed to resolve across two consecutive rounds, and per the hard
stop I return them rather than polish around them:** whether a universal trunk-level bound is wanted
at all (F1/F2 — I recommend **no**, and §6.3 is the alternative), and what decision threshold `T` any
quoted significance supports (unchanged since rev. 1; it exists nowhere in the tree and is the one
input that cannot come from the code).

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
| 5 | **Examine the `k = 0` member's `pinv` spectrum** for modes near the cutoff, to establish whether §2.1a's regime is reachable on real Z members at all | §2.1a's UNMEASURED limit — and under §6.3 this is **EXPLORATORY**, on a separately declared set excluded from the acceptance max | arithmetic on the `k = 0` member, which exists before any offset |
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

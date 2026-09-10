# REVIEW 2026-09-10 — independent assessment of Z's acceptance criteria
# PART A: the minimum acceptance requirements, DERIVED BEFORE THE PROPOSAL WAS OPENED

**CITABLE FOR:** the requirement set `A1`–`A24` below as *this reviewer's independent derivation*
from the governing decisions and the publication's own claim text; the measurements in §A.4, each
pinned to `file:line` at a named sha; and the sequencing fact that this part was committed before
`PROPOSAL-20260908-z-sensitivity-criteria-over-publication-projections.md` was read.

**NOT CITABLE FOR:** any criterion adoption, any grade, any cell, any discharge, any count or gate
movement, any construction, any compute, any spending grant, any publication change, or any claim
that these requirements ARE the criteria. **They are a yardstick for reviewing a proposal, not a
proposal.** `RZ(iv)` withholds implementation, construction, compute, grading, adoption and
publication change; nothing here is an exception to it. Gate 2 remains FAIL. Counts hold at CAND
`1 of 7`, QUOTED `0 of 7`. No scalar-5D covariance is adopted. `(cause 7, G)` remains permanently
OPEN. PET remains diagnostic under `R6`.

**Role and its limit.** This lane owns the *independent assessment* of Z's acceptance criteria. It is
**not** an author or co-author of those criteria. Where it recommends a correction, the correction is
a recommendation to the criteria's owner, and adopting it is that owner's act plus Joseph's decision
under `RZ(v)`'s carve-out. `BEN-381`'s separation is the pattern this role instantiates: **this lane
must not later grade any leg whose criterion it helped shape.**

## A.0 Base, authority chain, and what was read

Measured at `d147880f` (`main` tip at the start of this review), in an isolated read-only worktree.
macOS arm64. No compute, no cluster, no scheduler query.

| artifact | sha256 (this reviewer's own read, at `d147880f`) |
|---|---|
| `SPEC-20260906-complete-scalar5d-successor-Z.md` (rev. 21) | `987af827753e926da3c4f8daaf3684d3ed0ec115728d69520a795cd622da9bc4` |
| `DECISION-20260906-joseph-authorizes-z-specification-only.md` (`RZ`) | `304179df3905337d0ecd22af8a7416ed6aca5d7e050f89999667b57a6d251904` |
| `DECISION-20260902-joseph-rules-cause7-cause3-and-the-stop.md` (`R1`–`R6`) | `0836139b1c9a057c194a81a94d45c9f979209a9ac293d4bc8434e6b43fc1a064` |
| `PROPOSAL-20260908-z-sensitivity-criteria…md` | `3fc9fb87b170887cdc8be870f801e7228113c35669be455401bdb7f1e6e9ac4c` — **digested, NOT read, at the time Part A was written** |

**The authority chain is corroborated, not assumed.** `DECISION-20260906` §"Controlling authority"
cites `DECISION-20260902` at sha256 `0836139b1c9a…`; this reviewer recomputed that digest from the
file and it matches. So `RZ` sits under `R1`–`R6` by a checkable binding rather than by assertion.

**Read for this part:** `AGENTS.md`; `CRITERIA-20260811-quarantine-causes-1-2-3-4-6.md` §0–§1;
`SCOREBOARD-20260817-quarantine-seven-causes.md` (board + `POINTER 4`); `DECISION-20260902` in full;
`DECISION-20260906` in full; `SPEC-20260906` §§0.3, 1.1–1.3c, 2.3, 2.4, 2.6c, 2.7, 6.1–6.6; and the
publication sources named in §A.3.

**Deliberately NOT read before this part was committed:** the proposal above; `SPEC-20260906` §§3.6d,
3.7a, 3.7b, 3.7d, 5.8, 6.7, 6.8 — i.e. every section the spec itself marks **PROPOSAL, NOT
CRITERIA**, and the four withheld boundaries (`null_epsilon`, `cause3_agg`, `cause3_med`,
`cause3_corr`). The spec's §§0.0–0.0s revision history was skimmed for structure only; it is
commentary and includes withdrawn claims, and no requirement below rests on it.

**One relay, marked as a relay.** `claude-orchestrator` supplied the route to these artifacts and
flagged four findings. It also disclosed that it authored the construction plan and has withdrawn two
claims from it in the last day, and asked to be treated as routing rather than evidence. Every
mechanical claim in §A.4 was therefore re-measured here from the files; where a measurement
reproduces something a peer had already reported, §A.4 says so and counts the shared origin once.

---

## A.1 The decision this criterion set is FOR — and the two decisions it must not conflate

Three distinct questions are in play, and a criterion valid for one is not valid for another:

| | question | governing instrument | who decides |
|---|---|---|---|
| **Q1** | Is Z's seven-cell **assessment complete**? | `RZ(ii)`; `CRITERIA` §0's four legs; `SPEC` §3 | the grading lane, not this one |
| **Q2** | Is Z **adoptable** as the publication's 5D covariance trunk? | `RZ(i)`'s *"possible adoption subject"*; a future adoption authorization | Joseph |
| **Q3** | Does adopting Z **license a specific publication claim** (a significance, a χ², a per-bin σ)? | the note/paper's own conditional sentences (§A.3) | Joseph, as a publication decision |

**`A1` — Every criterion must name which of Q1/Q2/Q3 it gates.** `RZ(i)`'s two hedges are
load-bearing: *prospective* grading subject, *possible* adoption subject. A criterion whose passing
is described as making Z "acceptable" without saying acceptable-for-what silently answers Q2 or Q3
while claiming only to answer Q1. **`RZ(ii)` requires seven assessments, not seven favourable
results** (`SPEC` §6.1), so Q1 can complete with OPEN and UNRESOLVED cells — which means Q1
completion is *not* Q2, and no chain of Q1 passes adds up to Q2 without a separate adoption act.

**`A2` — Q3 is gated by the publication's own sentence, not by the seven-cause board.** §A.3 measures
what the note and paper actually make conditional. Their stated precondition is *"the adopted,
selection-complete scalar five-dimensional covariance"* — **two** properties. It is **not**
"seven discharged causes". Requiring seven METs as the criterion for a publication claim would demand
more than the publication proposes; requiring only Q1 completion would license the claim on less.

---

## A.2 Requirements derived from the governing decisions

### From `CRITERIA-20260811` §0 — the four-leg rule, which `R3` leaves *"unamended"*

- **`A3` — per-pair, digest-bound.** *"Discharge is a property of a (cause × artifact) pair, never of
  a cause alone."* Every criterion states the cause **and** identifies Z by path plus digest. A
  criterion phrased over "the 5D covariance", "the trunk", or "the candidate" is a definite
  description, and a definite description re-points when the tree moves.
- **`A4` — four independent legs; no substitution.** `C`, `P`, `M`, `T`; all four MET to discharge;
  any one failing leaves the cause OPEN. A criterion that lets a `C` pass stand in for `P`, or reads
  an `M` measurement as evidence of `T`, has merged legs `§0` separates on purpose. §0 is explicit
  that a *small* measured `M` "is not a licence to skip `P`".
- **`A5` — `M` is measured on Z's own inputs.** §0: *"measured on X's own inputs"*. `SPEC` §2.7
  **prohibits** citing S's `−0.0288%` five-band lateral movement or F's `+10.96%` (266-bin) as Z's
  `M`, or as a reason Z's `M` need not be measured — the two differ **in sign and by two orders of
  magnitude**, which is itself the demonstration that neither bounds the other. A criterion
  satisfiable by a number measured on G, S, F, X, J or the FPS chain is invalid.
- **`A6` — `T` must be power-tested in BOTH directions:** it fails if the defect is reintroduced
  **and** it fails if the guarded object disappears. §0 names the vacuous-pass shape (PB2) directly.
- **`A7` — the vocabulary is closed.** `MET` / `OPEN` / `UNRESOLVED`, discharge on four METs
  (`CRITERIA` §3; `SCOREBOARD` §7b `RULED` 2026-08-17;
  `DECISION-20260902-joseph-rules-no-fourth-grade-token.md`, Joseph: *"No token is added for the
  permanently unmeetable state"*). A criterion may not introduce a new **leg** grade. `SPEC` §6.1's
  `INAPPLICABLE — disposed by decision` is a **cell** disposition under five stated conditions, and
  the criteria must keep that distinction visible in the cell rather than inferable from it.
- **`A8` — `UNRESOLVED` must not collapse to the nearer of PASS/FAIL.** So every criterion carries an
  explicit inconclusive branch, and that branch must be reachable. A criterion with only two outcomes
  has, in effect, redefined `UNRESOLVED` as the favourable one.

### From `RZ` — the specification-only grant and its carve-out

- **`A9` — every proposed criterion change is flagged, item by item, with the criterion it changes.**
  `RZ(v)`: *"Any proposed criterion change must be identified explicitly"*, reserved for Joseph's
  **separate** decision. `RZ` §1 records this as an addition Joseph made that the packet did not ask
  for, and states the consequence: *"A Z specification that quietly retunes a discharge criterion has
  exceeded this ruling even if every other boundary holds."* A proposal that is globally labelled "a
  proposal" but does not say **which existing criterion each item alters** does not satisfy this; the
  flag has to be per item, because the decision Joseph is being asked for is per item.
- **`A10` — Z's cells may not be graded against G's or Y's GRADES.** `RZ(iii)`. Note the distinction
  the criteria must hold: G's **numbers** are the required `M`-leg comparison baseline (`SPEC` §1.1,
  *"the `M`-leg comparison baseline for every one of Z's seven cells"*), while G's and Y's **grades**
  may never be combined with Z's, in either direction. A criterion that reads "as MET for G" as
  partial credit for Z violates `RZ(iii)`; one that compares `C_Z` to `C_G` numerically does not.
- **`A11` — specifiable ≠ executable, and the difference must be on the face of the criterion.**
  `RZ(iv)` authorizes no compute. A criterion whose evaluation requires an unauthorized run is
  legitimately *specifiable*, but must be labelled not-yet-executable, with its cost surfaced under
  `RZ(v)(e)`. `R5`: *"A ceiling is a prohibition and an accounting boundary. It is NOT authorization
  to spend up to it."*

### From `R1`–`R6` and `SPEC` §6, which are RULED

- **`A12` — no smallness requirement where a ruling removed it.** `R3`: cause 7's `M` carries **no
  materiality threshold** — *"a large measured difference satisfies the criterion exactly as a small
  one does"*. `SPEC` §6.2: `(cause 1, Z)` closes on complete measurement plus disclosure
  **irrespective of magnitude**. `CRITERIA` §0: *"what is forbidden is an unmeasured one."*
  **A criterion that REJECTS Z because a magnitude is large, on cause 1 or cause 7, adds a
  requirement two rulings removed.** This is the sharpest axis-(c) hazard in the set.
- **`A13` — cause 3's `M(ii)` quantity is fixed and is the ASSEMBLED covariance.** `SPEC` §6.3(1):
  the variation of the **assembled** `C_Z` when sweep-side and throw-side estimator baselines are
  varied **jointly**. §6.3(3): the narrow fixed-draw scan is **DIAGNOSTIC** for Z, not `M(ii)`,
  *unless substitution is explicitly ruled* — and it is not. A criterion evaluated on the narrow scan
  is measuring the diagnostic and calling it the leg.
- **`A14` — cause 3's design is open and must be specified; the 46/50-member family is not assumed.**
  `SPEC` §6.3(2). So `N`, the offset set, and diagonal-or-grid are part of what must be decided, not
  inherited.
- **`A15` — three outcome classes, predeclared before measurement, and a large valid result is not
  automatically MET.** `SPEC` §6.3(4), on `PREDECLARE-20260901-cause3-mii` §4's six-branch model,
  which `R4` preserves: two INCONCLUSIVE, one favourable, three unfavourable. Note `A15` and `A12`
  are **not** in conflict: cause 3's `M(ii)` legitimately has unfavourable branches because it measures
  *estimator-noise contamination of the assembled object*, whereas causes 1 and 7 measure *the size
  of a correction*. A criterion set must not carry cause 3's branch structure across to causes 1/7,
  nor causes 1/7's magnitude-blindness across to cause 3.
- **`A16` — the narrow scan's own thresholds may not be retuned.** `R4` preserves `f_agg ≤ 0.0415`
  and `f_med ≤ 0.0274` with their publication-precision derivation *"exactly"*; only the purchase is
  gated. A Z criterion that restates those numbers differently has amended a criterion `R4`
  explicitly left standing.
- **`A17` — the fixed-seed null bound must be scale-relative, fixed before production, and justified
  by precision/sensitivity controls established BEFORE implementation — never selected from a
  favourable production result.** `SPEC` §6.4, RULED. Two consequences the criteria must show: the
  numeric value needs a *pre-production* justification, and that justification must be a precision or
  sensitivity control, **not** a measured null. G's measured null (`5.8223e-50`, `1.31e-12` of the
  sqrt-trace) is *"not a finding that G's null is bad… The defect is in the guard, not in the
  product"* — so it may not be re-used as the basis for Z's bound either.
- **`A18` — statistic, denominator, precision target and boundary are approved TOGETHER.** `SPEC`
  §6.6's standing recommendation, **adopted**: *"approve the concrete statistic, its denominator, the
  precision target and the boundary TOGETHER — never a formula detached from those definitions… A
  boundary approved in the abstract would be an authorization over an object nobody has defined."*
  **This is the strongest structural requirement on any criteria proposal**, and it is testable: for
  every boundary the proposal offers, all four must be present and mutually consistent, in one place.
- **`A19` — the denominator must be named, and must be the same population on both sides.** A
  relative statistic is a ratio, and a ratio hides its denominator. Z's mask invariant makes this
  concrete: `SPEC` §1.3 requires `mask_digest(Z) == mask_digest(G)` and
  `row_order_digest(Z) == row_order_digest(G)`, *"because the two sides would be distributions over
  different populations"* otherwise. So every criterion statistic states its denominator explicitly
  and asserts the mask/row-order identity that makes the two sides comparable. Note the reported mask
  is a **predicate** (bins with candidate CV > 0), not the literal `10,694` — `SPEC` §1.2 — so the
  criterion must select by predicate and assert against G's count, never hardcode it.
- **`A20` — PET may not enter, in either direction.** `R6`; `SPEC` §6.1 condition 2's falsifier check
  (no PET-derived product consumed by any module on Z's path). A criterion that consumes a PET
  product, or whose passing could be read as a PET promotion, breaks `R6`. Note there is a 5D→4D
  projection builder on the PET path (§A.4.3), so an enumeration of "the projections" must exclude it
  deliberately rather than by luck.

### From the campaign's own catalogued failure class

- **`A21` — every criterion must be power-tested, and the fixture must be BIDIRECTIONAL.** There must
  exist a construction that FAILS it, exhibited rather than argued. `SPEC` §1.3b already demonstrates
  why: **setting `g^c ≡ 1` — discarding the whole inflation — passes the closure identity, the
  `g >= 1` check, the zero-denominator check and the inflated-PSD check**, all four, trivially. The
  repository has an instrument for this class,
  `docs/orchestration/audit_gates_that_cannot_fail.py` with
  `CORPUS-20260811-gates-that-cannot-fail-sweep.md`; **calling it beats writing a second detector**,
  and a re-implementation of a rule that already has an implementation is itself a defect shape.
  `SPEC` §2.7 requires cause 7's fixtures be bidirectional for the measured reason that the two
  available lateral movements differ in sign.
- **`A22` — a criterion evaluated by reading back a producer-recorded value is not a criterion.**
  `SPEC` §1.3b, on the `g^c` reconstruction gate: *"Reading the producer's `hInflation_g` and checking
  it against itself is not this gate."* Generalised: the checking side recomputes from operands. And
  **both** centering variants must be reconstructed independently, because `g^mean` and `g^cv` differ
  only through the `+ mean_shift²` term, so a validator that reconstructs one and reuses it for the
  other cannot detect a dropped shift.
- **`A23` — a criterion whose operands do not persist is not evaluable, and that is a feasibility
  defect, not a caveat.** Measured in §A.4.2. The remedy is a new write site, and it must be named as
  a prerequisite of the criterion rather than recorded beneath it.
- **`A24` — a numerical closure tolerance may not be reported as a materiality threshold.** `SPEC`
  §1.3b, citing `PREDECLARE-20260901-cause7` §1 `C`(4): `1e-9` is the standard-P4 relative closure
  tolerance and *"may not be reported as an `M`-leg materiality threshold"*. The two are different
  objects with different justifications, and a criterion set that uses one number for both has
  supplied no justification for the second use.

---

## A.3 Requirements derived from the intended publication claims — measured from the sources

**Not from a summary.** Quoted from `docs/analysis-note/` at `d147880f`.

### A.3.1 What the publication actually makes conditional

| where | the claim, verbatim | what it is conditional on |
|---|---|---|
| `main_paper.tex:49-51` (abstract) | *"The latter is a central-value result; its significance awaits adoption of a **common** five-dimensional covariance."* | adoption of a **common** 5D covariance |
| `paper_body.tex:145-148` | *"Every non-two-dimensional result in this Letter is a central value. A publication-level significance requires the **adopted, selection-complete** scalar five-dimensional covariance, which is not yet in hand; no superseded or historical covariance is used here."* | **adopted** + **selection-complete** |
| `sec_3d.tex:223-226` | *"the final 3D covariance must be projected from the adopted, selection-complete 5D trunk. Consequently no 3D generator χ², p-value or significance is quoted here."* | the same trunk, **projected** |
| `sec_3d.tex:405-406`, `:417-418` | *"no per-cell significances are reported without a corrected 4D covariance"*; *"No pulls or full-covariance χ² are reported without a corrected 4D covariance"* | a corrected **4D** covariance |
| `sec_eavailw.tex:150-151`, `:194` | *"statistical compatibility is not evaluated without the corrected projected covariance"*; *"no covariance-based consistency metric is reported"* | the **projected** covariance |
| `sec_summary.tex:26-27`, `sec_execsummary.tex:43` | *"the resulting 5D products remain candidates until the **selection-complete lateral replacement** lands"* | cause 7's replacement |

**`A2` restated with its evidence:** the publication's precondition is **adopted** and
**selection-complete** — not seven discharged causes. `selection-complete` is cause 7's own property
(`SCOREBOARD` row 7: *CV-support-limited lateral selection*). So of the seven causes, exactly one is
named by the publication as its gate; the other six are campaign obligations. **A criterion set for Q3
that requires all seven is stronger than the publication proposes. One that requires only cause 7 is
weaker than `RZ(ii)`'s assessment obligation.** Both errors are available, and the criteria must say
which question they answer (`A1`).

### A.3.2 The quantity the publication would quote is a χ²/significance, not a σ

Every conditional above is on a **significance, χ², p-value, pull, or covariance-based consistency
metric**. None is on a per-bin σ or a √Tr.

- **`A25` — a bound on `diag(C)` is not a bound on the quantity publication quotes.** A significance
  has the form `r^T C^{-1} r`. Perturbing `C`'s off-diagonal structure at **fixed diagonal** changes
  `C^{-1}` without limit as `C` approaches singularity, so no bound on the diagonal — per-bin σ,
  median relative uncertainty, √Tr, or a ratio of any of them — bounds `r^T C^{-1} r`. A criterion
  whose statistic is diagonal-only must therefore either (i) be stated as bounding covariance
  *content* with an explicit statement that **passing licenses no significance**, or (ii) be replaced
  by a statistic on the quoted functional. **What it may not do is bound a diagonal and be read as
  clearing the claim.** (This reviewer derived `A25` independently; `SPEC` §3.7d is titled *"EVERY
  PROPOSED GATE IS BLIND TO CORRELATIONS — … IT IS A REQUIREMENT, NOT A CAVEAT"*, which was **not**
  read before this was written, and which appears to reach the same place. Two arrivals, one of them
  the spec author's; this is corroboration, not a second measurement.)
- **`A26` — the acceptance statistic must be evaluated on the object the publication forms**, at the
  binning the publication quotes, through the map the publication uses. §A.4.3 measures that there
  are **four** projection builders in the tree and that they do not agree on refusal semantics, so
  "the projection" is ambiguous until the builder is named.

### A.3.3 The `(E_avail,W)` consumer does not consume what its own conditional implies

`sec_eavailw.tex:172-186` states the 42-bin object as
`C = C_syst + C_stat + C_lateral`, and says *"A valid replacement must project the corrected
five-axis statistical covariance as `M C_5D Mᵀ`"*. **Measured in the code** (§A.4.4): the 5D trunk
enters this object **only through the statistical block**; `C_syst` is built natively at 42 bins from
13 knob bands plus a 100-universe flux multisim, and `C_lateral` is transferred from **4D** bands and
then **diagonalized**.

- **`A27` — the criteria must state, per publication consumer, WHICH BLOCK of Z enters and through
  WHICH MAP.** Without that, two opposite errors are both available on the paper's headline claim.
  If Z reuses S's `stat_cov` digest — an **open** scientific question, `SPEC` §2.6b/§6.6, *"this
  specification does not decide it"* — then adopting Z changes the `(E_avail,W)` covariance **not at
  all**, and the abstract's *"significance awaits adoption of a common five-dimensional covariance"*
  would be discharged by an adoption that leaves the object the significance is computed from
  unchanged. Conversely a criterion stated on `M C_Z Mᵀ` at 42 bins is stated over an object the
  publication never forms. **This is a claim-side gap, and it is the publication's to close, not the
  criteria's** — recorded here because `A1`/`A2` cannot be satisfied while it is open, and because
  the instruction not to demand more than the publication proposes cuts both ways: the publication
  here proposes something its own construction does not deliver.
- **`A28` — the `(E_avail,W)` lateral block's diagonalization and the trunk's correlations are
  independent losses, and a criterion may not net them.** `C_lateral = diag(σ²)` discards every
  lateral correlation at 42 bins regardless of Z. So even a perfectly correlation-faithful Z yields a
  42-bin covariance with a diagonal lateral block. A criterion that certifies Z's correlations and is
  read as certifying the projected object's correlations is measuring the wrong operand.
- **`A29` — unsupported (zero-variance) projected cells must be excluded from any acceptance
  statistic, and counted in both directions.** The `(E_avail,W)` projector *deliberately* does not
  fail closed on empty rows, and prints that those bins *"are NOT measured-and-precise; they are
  unsupported. Exclude them from any chi2, significance or per-bin ratio built on this covariance."*
  A statistic computed over all 42 bins silently includes cells whose variance is exactly zero — the
  best-looking bins in the set. `SPEC` §2.6c(3) already requires the orphan count *in each
  direction* and the √Tr fraction they carry; `A29` is that requirement carried onto the acceptance
  statistic itself.

### A.3.4 Feasibility, from `R5`

- **`A30` — a criterion is feasible only if its measurement fits inside `R5`'s envelope, and the
  criteria must say what happens when it does not.** `R5`: stop at `2026-09-30` UTC inclusive **or**
  `500` GPU task-hours **or** `500` CPU task-hours, whichever first; **the date binds, the ceilings
  are a backstop**; the default outcome at the stop is *"the Letter **as scoped** — every non-2D
  result a central value, the joint high-`E_avail`/high-`W` generator deficit reported **without** a
  significance."* Today is `2026-09-10`: **20 days**. `SPEC` §5.4 prices `(cause 3, Z)`'s ruled
  joint-baseline magnitude at **5×–9× over `R5`** — i.e. the ruled `M(ii)` quantity is, on the
  specification's own estimate, unaffordable inside the envelope that governs it. **The honest
  consequence is that `(cause 3, Z)`'s `M(ii)` will be `UNRESOLVED` at the stop**, and `A8` says
  `UNRESOLVED` must not be read as the nearer of PASS/FAIL. A criteria proposal must state this
  rather than leave it to be discovered at the stop, and — because `R5`'s default is already the
  central-value Letter — it should be explicit that an `UNRESOLVED` cause-3 cell **costs the
  publication nothing it currently claims**.
- **`A31` — `R5`'s meter is the accounting instrument, and a cost claim in the criteria must cite it
  rather than a plan's estimate.** `R5` §4 item 6 records the meter as *"the one that fails
  silently"*. A criterion priced against an unmeasured ledger is priced against nothing.

---

## A.4 Measurements this reviewer made, each pinned

All at `d147880f` unless stated. No compute; local reads only.

### A.4.1 The implemented fixed-seed null tolerance is a check that cannot fail — CONFIRMED

`nd-unfolding/unified_throw_cov.py:517`:

    tol = 1e-12 * max(float(np.linalg.norm(base)), 1.0)

`base` is a cross-section vector of norm order `1e-37`, so `max(…, 1.0)` returns `1.0` and `tol` is an
**absolute** `1e-12` — roughly `10^25` times the scale of the quantity it bounds. `:519` compares
`null_norm > tol`. **It is not a relative determinism bound.** This reproduces `SPEC` §3.1a and was
flagged to this lane by `claude-orchestrator`; it is re-measured here from the file, and the shared
origin is counted once. It is the measured defect `SPEC` §6.4 replaces, and it is the reason `A17`
exists.

### A.4.2 The null ratio's operands do not persist — CONFIRMED, and it is a blocking prerequisite

`nd-unfolding/unified_throw_cov.py:582-598` returns `x_cv_reported`, `fixed_seed_null_norm`,
`C_unified`, `C_blocksum`, `mean_shift` **in a Python dict**. The ROOT write immediately above
(`:569-581`, seed keys at `:569-570`) persists `est_seed_offset`, the seed keys and `hJointMeanShift` — but **not** `x_cv`,
**not** `x_cv2`, and **not** the support predicate. So the returned values die with the process.

**Consequence for the criteria:** a fixed-seed-null criterion cannot be *independently reconstructed*
from a committed artifact, only re-derived by re-running the producer. Under `A22` that is not a
criterion yet, and under `A23` the missing write site is a **named prerequisite** of the criterion,
not a footnote. This is the same structural shape as `SPEC` §1.3b's `g^c` gate.

### A.4.3 There are FOUR projection builders and they disagree on refusal — and one is on the PET path

| builder | `file:line` | orphan behaviour |
|---|---|---|
| `p4_lib.build_projection_M` | `nd-unfolding/p4_lib.py:1353` | **fails closed, both directions** — `:1380` rejects a reported HIGH bin landing in a non-reported LOW bin; `:1393-1401` rejects a reported LOW bin no HIGH bin reaches |
| `project_cov_nd.build_projection` | `nd-unfolding/project_cov_nd.py:79` | **neither check**; returns a `dropped` count and leaves unreached destination rows all-zero |
| `eavailW_covariance` (`Mew`, inline) | `nd-unfolding/eavailW_covariance.py:404-406`, coverage report `:425`, helper `:55` | **deliberately fail-open**, with a printed warning; the code states this is *"the one place the two projectors should differ"* because `W² = M² + 2M·E_avail − Q²` makes some cells physically unreachable |
| `assemble_ctotal_bkgsub.build_5d_to_4d_projection` | `nd-unfolding/pet/assemble_ctotal_bkgsub.py:36` | **on the PET path — `R6` diagnostic; must be excluded from a publication-projection enumeration deliberately, not by luck** |

`nd-unfolding/uq_math.py:171-180` `project_covariance` is `M @ C @ M.T` with finiteness and shape
guards — exact, and PSD-preserving for any `M`.

**Attribution.** The first two builders' divergence is **already recorded** by another lane, in
`FINDING-20260910-projection-builders-agree-numerically-and-diverge-on-refusal.md` (measured at
`5580d1d5`, amended the same day by the spec's author). That finding is **stronger** than what this
reviewer derived: it establishes byte-identical `M` on the both-returned domain, and its amendment 2
makes the further point that a naive elementwise comparison would test *"agreement over a domain
selected for agreement"*. This lane cites it rather than re-originating it. What this lane adds is
rows 3 and 4 — the third map's deliberate fail-open with its physical justification, and the PET map's
existence — and the consequence in `A26`/`A29`.

### A.4.4 The `(E_avail,W)` object's composition — MEASURED

`nd-unfolding/eavailW_covariance.py`:

- `C_syst`: built natively at 42 bins — 13 knob bands, plus `C_flux` from `args.nflux` universes via
  `mat_covariance(fX)` (`:387-388`). **Does not come from the 5D trunk.**
- `C_stat`: `project_covariance(C5stat, Mew)` at `:441`, where `C5stat` is read from
  `args.stat5d` / `args.stat5d_hist` (`:436-440`); `Mew` built at `:404-406`. **This is the trunk's only entry point into this
  object, and it is the statistical/bootstrap block only.**
- `C_lateral`: `:459-469` — each 4D lateral band marginalized to `E_avail` (`Me @ C @ Me.T`),
  converted to a **fractional** uncertainty `frac_e`, spread flat-in-W, then
  `C_lateral = np.diag((sig_lat.ravel()) ** 2)` at `:469`. **Diagonal by construction**; the code
  labels the flat-in-W step a *"documented approximation"*.

This is the evidence for `A27` and `A28`. Note the header comment at `:392-395` — *"Never sum standard
deviations across marginalized cells"* — is honoured for the statistical block and is **not** what the
lateral block does, because the lateral block never had a 5D covariance to project.

---

## A.5 The review this yardstick will be applied to

Part B applies `A1`–`A31` to the proposal, on the four axes assigned to this lane:

- **(a)** does passing support the stated publication claim — against §A.3's verbatim conditionals,
  and `A25`/`A27`;
- **(b)** could a scientifically unacceptable Z pass — against `A21`/`A22`/`A29`, and by calling
  `audit_gates_that_cannot_fail.py` rather than writing a second detector;
- **(c)** is an acceptable Z rejected unnecessarily — against `A12` above all, and `A15`'s boundary
  between magnitude-blind and branch-structured causes;
- **(d)** are the required measurements feasible — against `A23`, `A30`, `A31`.

**Part B may not silently become authorship.** Where Part B recommends a correction it will name the
requirement it comes from and leave the drafting to the criteria's owner. Where this reviewer cannot
separate reviewing from drafting, it will say so and decline rather than write the criterion.

---

## A.6 One routing citation that does not resolve, corrected here

`claude-orchestrator` routed the 3D significance withholding to `sec_3d.tex:181-183`. **At
`d147880f` those lines are a generator-list item** (*"NuWro 21.09 — an independent generator (C
target), the same flux and phase space"*), not a withholding. The withholding this review relies on
is at **`sec_3d.tex:223-226`**, quoted in §A.3.1 and re-read from the file. The routed conclusion was
right and its line numbers were not; recorded because a line number into a growing `.tex` decays the
same way `CRITERIA`'s own `POINTER 3` records for the ledger, and because nothing in Part A rests on
the routed citation.

---
---

# PART B: the review, and the verdict

**Written 2026-09-10, after Part A was committed at `1508ead0`. Subject:**
`PROPOSAL-20260908-z-sensitivity-criteria-over-publication-projections.md` **rev. 5**, sha256
`3fc9fb87b170887cdc8be870f801e7228113c35669be455401bdb7f1e6e9ac4c`, last revised at `610d0882`
(2026-09-08T01:14:52+0200). Re-pinned against `origin/main` `c18f9daa`.

**CITABLE FOR:** the verdict in §B.0, the findings `B1`–`B9` with their measurements, and the
corrections in §B.5 — including one to Part A's own `A30`.
**NOT CITABLE FOR:** adopting or rejecting any candidate criterion; any tolerance; any grade; any
cell; any count or gate movement; any authorization. **This lane recommends; it does not adopt, and
it did not draft.** Where a fix is named, the drafting belongs to the proposal's lane and the decision
to Joseph under `RZ(v)`.

**Disclosure about my own reading order.** Part A was written and its content finalized before the
proposal was opened. While adding the `CATALOG.md` pointer row that this repository's pre-commit hook
requires in the same commit, I necessarily read `CATALOG.md`'s existing summary of the proposal
(`:178-185`). That happened after Part A's text was final and it changed nothing in it, but it is a
partial exposure and is recorded rather than glossed. Everything in Part A is derivable from the
sources §A.0 lists.

## B.0 VERDICT

**BLOCK** — on §7 items **1, 2 and 3**. §7 item **4 is READY FOR JOSEPH'S DECISION** and is
separable; it should go forward on its own rather than wait for the rest.

**What BLOCK does and does not say.** It is a judgement about **readiness for decision**, not about
the quality of the analysis. The proposal's structural core is **correct, and in one place better than
my independent derivation**: §2a's *"can be strongly sensitive to the smallest **retained** modes —
and only where `d` has overlap with them"* is a real refinement of my `A25`, and its observation that
modes **below** `pinv`'s cutoff are *discarded* rather than amplified is a distinction I did not draw.
§2c's `diag(1,4)` / `diag(4,1)` counterexample is sound and decisive against any spectral-summary
candidate. The document withdraws fifteen of its own claims across four revisions, declines to propose
a tolerance for a stated reason, and marks `s_proj`'s coverage question **unresolved** while refusing
to invent a second wrong test for it. That is the behaviour the campaign wants.

**It is blocked because three of the four decisions it puts are not yet answerable in the order
asked**, and because one standing ruling is not carried into the candidates at all. Three of the four
blocking findings are cheap to fix; `B1` and `B2` are not defects of reasoning but of a claim side
that does not yet exist.

| finding | axis | severity |
|---|---|---|
| `B1` — C-1's declared population is currently **empty**: the deliverables quote no significance at all | (a), (b) | **blocking** |
| `B2` — §7 item 2 asks for the margin of a claim the publication does not make, and `R5`'s default is that it never will | (a), (d) | **blocking** |
| `B3` — no `INCONCLUSIVE` branch anywhere, against a RULED requirement; the missing one is the positive control | (b) | **blocking** |
| `B4` — §7 item 3 is stale, and as specified would authorize a check that can pass over a domain selected for agreement | (b), (d) | **blocking** |
| `B5` — the proposal never names cause 3 or `M(ii)`, so its criteria are not bound to a (cause × artifact) pair | (a) | serious |
| `B6` — the `M` enumeration misses a fourth builder, which is on the `R6` PET path | (b) | serious |
| `B7` — `ndf` = bin count has a measured instance the proposal does not cite; direction is currently conservative | (a) | worth fixing |
| `B8` — the null arm's thread environment is not pinned, so a reproducibility bound has no fixed configuration | (b) | serious, and outside this proposal's scope |
| `B9` — nothing in the proposal over-rejects. Axis (c) is **clean** | (c) | none |

---

## B.1 `B1` — C-1's declared population is empty, so C-1 currently passes vacuously

**C-1's statistic** (§3): `s_sig = max` over the declared offset set of `|Nsigma_k − Nsigma_0|`,
**"per (generator, projection) pair the publication quotes."**

**Measured, at `d147880f`, over `docs/analysis-note/`:**

| measurement | result |
|---|---|
| `\gbdtFive*` macro **uses** anywhere in note, primer or paper | **0.** Defined at `values.tex:112-115`; the only other occurrence is `sec_systematics.tex:154`, a **filename** reference to `PROCEDURE-gbdtFive-macro-update.md`, not a macro use |
| `paper_body.tex`: `\input` / `gbdtFive` / `sqrt` / `e-38` | **0 / 0 / 0 / 0** |
| a quoted generator significance, χ², p-value or pull for any non-2D result | **none.** `paper_body.tex:145-146` *"Every non-two-dimensional result in this Letter is a central value."* `primer_body.tex:120` *"no significance is assigned."* `sec_3d.tex:225-226`, `:405-406`, `:417-418`, `sec_eavailw.tex:150-151`, `:194` each withhold one explicitly |

So **the set of "(generator, projection) pairs the publication quotes" is empty**, and a `max` over an
empty set is undefined — or, in any implementation that seeds it with `0.0`, **satisfied trivially**.
That is this repository's catalogued gates-that-cannot-fail shape
(`CORPUS-20260811-gates-that-cannot-fail-sweep.md`), reached not by a coding slip but by the
statistic's own definition, and it is `A3`'s point exactly: *"the pairs the publication quotes"* is a
**definite description**, and a definite description re-points — here, to nothing.

**This corroborates the proposal's §1 conclusion and then goes past it.** §1a concluded from
`paper_body.tex`'s zero counts that *"the external paper quotes no 5D covariance magnitude at all"*.
I reproduce those counts exactly. What §1a did not measure is that **the note does not quote one
either** — the four `\gbdtFive*` macros are now defined and unused. So the proposal's premise is
stronger than it claimed, and the same fact undermines its primary candidate.

**Recommended correction (drafting is the proposal lane's).** C-1 must **enumerate its (generator,
projection) pairs explicitly and prospectively** — which generators, which projection, at which
binning — rather than by reference to what the publication quotes. Under `A18` that enumeration is
part of the statistic's definition, so it belongs in the same packet as the denominator, the precision
target and the boundary. Until it exists, C-1 is a well-motivated shape without a population.

**A separate finding, for another owner.** `CRITERIA-20260811` §1 fixes **X**, the graded artifact, by
the citation *"The four `\gbdtFive*` macros are consumed in exactly one prose block,
`sec_systematics.tex:162-173`"*. That block has been rewritten; `:148-154` now reads *"no substitution
is available, and supplying one would make the sentence false rather than current"*. **The
artifact-fixing citation has decayed** — the same decay `CRITERIA`'s own `POINTER 3` records about the
ledger, now landing on `CRITERIA` §1. Surfaced for `CRITERIA`'s owner; **not repaired here**, because
re-fixing the graded artifact is a criterion act and this lane is the reviewer.

## B.2 `B2` — §7 item 2 asks for the margin of a claim that does not exist

§4b: *"If a quoted significance supports a claim that a generator is or is not disfavoured at some
threshold, the justified tolerance is the one that cannot move `Nsigma` across the **margin**… That
threshold is a scientific choice and it is not in this tree."* §5 makes this the sole reason no
tolerance is proposed. §7 item 2 puts it to Joseph.

**§4b's reasoning is right, and its diagnosis of why the threshold is missing is not.** The threshold
is not an unrecorded input. **There is no claim for it to be the margin of** (`B1`), and under `R5`
the **default outcome is that there never will be**: *"the default outcome is the Letter **as
scoped** — every non-2D result a central value, the joint high-`E_avail`/high-`W` generator deficit
reported **without** a significance."* Today is 2026-09-10; the stop is 2026-09-30.

**So item 2 is posed out of order.** Joseph cannot state the margin to a threshold for a significance
the Letter does not quote. The prior, decidable question is a **publication-scope** one under `R5`:
*will the Letter quote a significance at all, and for which pairs?* Only then does a margin exist to
be stated. Both are his, but they are two decisions and the second depends on the first.

**And it interacts with `A27`, which makes the ordering matter more, not less.** Measured in §A.4.4:
the 42-bin `(E_avail,W)` object takes the 5D trunk in **through the statistical block only**
(`eavailW_covariance.py:441`), its `C_syst` is native at 42 bins, and its `C_lateral` is diagonalized
at `:469`. Whether Z **regenerates or reuses** `C_stat` is open — `SPEC` §2.6b, §6.6, *"this
specification does not decide it"*. **On the reuse branch, adopting Z leaves the object the paper's
headline significance would be computed from unchanged**, and the abstract's *"its significance awaits
adoption of a common five-dimensional covariance"* (`main_paper.tex:49-51`) would be discharged by an
adoption that moved nothing. A criterion set for the significance cannot be specified before that
branch is chosen, because on one branch the criterion's subject does not depend on Z.

**Recommended:** item 2 is withdrawn and replaced by a request that names the two decisions in order,
and records that the second is conditional on `SPEC` §2.6b's `C_stat` branch.

## B.3 `B3` — no INCONCLUSIVE branch, against `SPEC` §6.3(4), and the missing one is the positive control

**Measured over the proposal:** occurrences of `INCONCLUSIVE` = **0**; of `cause 3` = **0**; of
`vacuous` = **2**, both in §4a's printed-precision argument, neither an outcome branch.

**`SPEC` §6.3(4) is RULED:** *"Three outcome classes — favourable, unfavourable, inconclusive — are
specified **BEFORE** measurement"*, on `PREDECLARE-20260901-cause3-mii` §4's six-branch model, which
`R4` preserves. **Read from that predeclaration at `d147880f`, §4 is exhaustive with six branches:**

1. `INCONCLUSIVE / WRONG FOOTING` (`:226`) — any §2 check fails, or the declared packed input is absent
2. **`INCONCLUSIVE / VACUOUS SEED VARIATION`** (`:230`) — *"Read-back seed set is not exactly `1..12`"*, etc.
3. `MET`
4. `NOT MET — AGGREGATE`, 5. `NOT MET — PER-BIN`, 6. `NOT MET — BOTH` (`:236-240`)

**Branch 2 is a positive control, and its absence is the defect.** `s_sig = max |Nsigma_k − Nsigma_0|`
is small in **two** unrelated situations: the estimator baseline genuinely does not move the quoted
significance (the favourable finding), **or the declared offsets never reached the estimator** — an
unthreaded seed, an offset set that collapses, members that are byte-identical, a resumed member that
reused a cached slab. **Those are indistinguishable in `s_sig`, and the second reads as the first.**
This is the identical shape `SPEC` §1.3b exhibits for the inflation, where `g^c ≡ 1` clears four gates
trivially — and `A21` is that requirement.

The proposal carries **two partial** inconclusive handlers and does not name them as such: `Nsigma`
undefined at `p = 0` (§3 C-1, *"must be reported as undefined, never as zero movement"* — correct and
important) and §4c's rank change as *"a reportable event that blocks a bare pass"* (also correct).
Neither is the vacuity control.

**Recommended:** each candidate carries all three outcome classes explicitly, and the vacuity branch
is evidenced from the member receipts — per-member estimator-seed values read back and pairwise
distinct, plus measured member-to-member movement in an object known to depend on the seed. `A22`
applies: read back from the receipt and recompute, do not trust the launcher's intent. The write sites
exist (`sweep_bank_5d.py:309`; `analyze_universes_5d.py:273-277`; `unified_throw_cov.py:569-570`;
`mii_adopt_unified_5d_stamped.py:168`, per `SPEC` §2.3), so this is a declaration gap and not new code.

## B.4 `B4` — §7 item 3 is stale, and as specified would authorize a check that can pass without doing the work

§7 item 3 asks whether the §6 builder comparison is *"authorized as Tier-2 work"*. §6 item 1 specifies
it as: both builders instantiated on the same edges, masks and drop axis, `M₁ − M₂` compared
elementwise to zero at float64 tolerance, *"for **every** projection the publication quotes"*.

**It has already been partly run, and its specification has already been found defective — both on
`main`, and both after the proposal's last revision.**
`FINDING-20260910-projection-builders-agree-numerically-and-diverge-on-refusal.md`, merged at
`ceb474cc` (**2026-09-09T17:13:10−0700**, verified `merge-base --is-ancestor ceb474cc origin/main`),
versus the proposal's last revision `610d0882` (**2026-09-08T01:14:52+0200**). It establishes
**byte-identical `M`** on three mask densities for the single-axis `W` marginalisation, and **opposite
refusal semantics** off that domain. Its **amendment 2, made by the spec's own author**, states that a
runner implementing §6 item 1 literally *"would either crash on the refusing cases or skip them — and
skipping restricts the tested domain to exactly the region where the builders agree… which no exit
code catches"*, and that §6 item 1's further scoping to *"every projection the publication quotes"*
**may contain no non-nesting case at all**.

**So authorizing §6 item 1 as written would authorize a check whose green state is reachable without
the work being done** — `A21` again, and by `B1` its declared domain is additionally empty. The
amendment's remedy is the right one: the comparison's **unit** must be the builders' **outcome**
(refuses / returns-with-drops / returns-clean), with elementwise `M` equality tested only inside the
both-returned cell.

**Recommended:** item 3 is withdrawn as posed. What remains genuinely unauthorized is the **residue**
— the outcome-unit comparison over the non-nesting cases, extended per `B6`. §6 item 2's refusal to
give any implementation automatic precedence is right and should be kept verbatim; §6 item 3's
"record a measured agreement with all shas" is now partly satisfied and should cite `ceb474cc` rather
than ask for it.

## B.5 `B6`, `B7`, `B8` — three narrower findings, and one that is not this proposal's

**`B6` — the enumeration is incomplete, and the fourth builder is on a prohibited path.** §6 counts
*"at least THREE"*. §A.4.3 measures **four**: `p4_lib.build_projection_M` (`p4_lib.py:1353`, fails
closed both directions at `:1380` and `:1393-1401`), `project_cov_nd.build_projection`
(`project_cov_nd.py:79`, neither check), the `(E_avail,W)` inline `Mew`
(`eavailW_covariance.py:404-406`, **deliberately** fail-open with a printed warning, coverage report
at `:425`), and **`pet/assemble_ctotal_bkgsub.py:36 build_5d_to_4d_projection`** — on the PET path,
which is diagnostic under `R6`. §6 also does not carry the third builder's *reason* for differing,
which is physical rather than accidental: `W² = M² + 2M·E_avail − Q²` makes some `(E_avail,W)` cells
unreachable, so *"an empty row here can be correct, where in a 5D→4D marginal it cannot be."*
**A designation among builders that does not name the PET map excludes it by luck rather than by
`R6`** (`A20`), and one that treats the third builder's fail-open as a defect would be wrong.

**`B7` — the `ndf` policy has a measured instance the proposal does not cite, and its direction is
determinable.** §1b item 14 and §4c correctly find that `ndf` is the **bin count**
(`eavail_generator_significance.py:132`, `chi2_to_sigma(chi2, n_ea)`) while `pinv` — called with **no
`rcond`**; I measure **0** occurrences in that module, confirming §4c — discards modes. The
`(E_avail,W)` projector supplies a **known, printed, non-empty** instance: structurally unsupported
cells get an exactly-zero row and column, and the module itself warns *"they are NOT
measured-and-precise; they are unsupported. Exclude them from any chi2, significance or per-bin ratio
built on this covariance."* Those modes are dropped by `pinv`, so their components of `d` contribute
**0** to χ² while `ndf` still counts their bins: **χ² too small and `ndf` too large, both pushing `p`
up and `Nsigma` down.** The current direction is therefore **conservative**, which is why this is
`worth fixing` and not blocking — but `A24` applies: a criterion may not rest on a mis-specified
denominator merely because the error is in the safe direction, and a later "fix" of `ndf` to the
retained rank **without** also handling `d`'s dropped components would flip the sign. `A29`: the
excluded-cell list belongs in the criterion, with its count in both directions.

**`B8` — the null arm's thread environment is not pinned. Outside this proposal's scope, and it
belongs to §3.7a.** This was routed to me as *"arm 5 exports `OMP_NUM_THREADS=32 MKL_NUM_THREADS=2
OPENBLAS_NUM_THREADS=2`; arms 6 and 7 export none"*. **Measured over the seven launchers that share
`MNV_EST_SEED_OFFSET`, the routed detail is wrong and the conclusion is stronger:**

| arm | launcher | `OMP` | `MKL` | `OPENBLAS` | runs `--null` |
|---|---|---|---|---|---|
| 1 | `sbatch_bootstrap_5d_gpu.sh` | — | — | — | — |
| 2 | `sbatch_mii_estimator_scan_5d_bkgaware_gpu.sh` | `${SLURM_CPUS_PER_TASK:-32}` | — | — | — |
| 3 | `sbatch_seedscan_split_5d.sh` | — | — | — | — |
| 4 | `sbatch_sweep_bank_5d_run_bkgaware_gpu.sh` | — | — | — | — |
| 5 | `sbatch_unfold_5d_detector_bkgaware_gpu.sh` | `${SLURM_CPUS_PER_TASK:-32}` | — | — | — |
| 6 | `sbatch_uthrow_block_5d.sh` | — | — | — | — |
| 7 | `sbatch_uthrow_combine_5d_fast.sh` | — | — | — | **yes, `:339`** |

**No arm of the seven pins `MKL_NUM_THREADS` or `OPENBLAS_NUM_THREADS` at all**, and the two that set
`OMP_NUM_THREADS` derive it from the scheduler allocation rather than a literal. The quoted
three-variable string is real but lives in `sbatch_uthrow_run_5d_fast.sh:122`, which is **not one of
the seven**. So the asymmetry is not arm-5-versus-6-and-7; **thread counts float on every arm**, and
arm 7 — where `--null` computes `x_cv`/`x_cv2` — pins none of the three.

**Why it matters, stated at the strength the measurement supports.** `SPEC` §6.4 RULES that Z's
fixed-seed null bound be *"justified by precision and sensitivity controls established before
implementation"* (`A17`). BLAS thread count changes reduction order and therefore floating-point
rounding, so **a reproducibility bound cannot be established over a configuration that is not
fixed** — regardless of how large the effect turns out to be. **I have not measured that thread count
moves the null**, and I should not be read as claiming it: G's null is `1.31e-12` of the sqrt-trace,
far above a plausible `~1e-16` reordering term, so it is probably not the dominant contribution. The
finding is about the **justification**, not the magnitude, and the remedy is cheap: pin the three
variables in the null arm before the bound is fixed, then measure. This bears on `SPEC` §3.7a, **not
on the proposal under review**, and is recorded here because it was routed to me and because it is
`A17`'s live instance. Compounding it: §A.4.2 measures that `x_cv`/`x_cv2` **do not persist**
(`unified_throw_cov.py:582-604` returns them in a dict; `:569-581` writes only the seeds and
`hJointMeanShift`), so the null cannot be independently reconstructed either (`A23`).

## B.6 `B9` — axis (c): nothing here over-rejects, and that is a positive result

`A12` is the sharpest over-rejection hazard in the governing set: `R3` gives cause 7's `M` **no
materiality threshold**, and `SPEC` §6.2 closes `(cause 1, Z)` **irrespective of magnitude**. A
criterion that rejected Z for a **large** measured difference on those causes would re-add a
requirement two rulings removed.

**The proposal does not do this, on any of its three candidates.** All three are **sensitivity**
statistics — movement of a quantity across declared estimator-baseline offsets — not **magnitude**
statistics, so `A12`'s hazard is not in their shape. C-1 is *"an ABSOLUTE difference in a quantity
already expressed in sigma units"* and its supported claim is about **movement**, not size. C-2 and
C-3 are likewise stated on relative change against the `k = 0` member. **No acceptable Z is rejected
by anything in §3.**

Three further points on the same axis, all in the proposal's favour:

- **C-3's scope is honest and is already enforced in code.** `z_validator.py:224,237,276,282` stamp
  `_DIAGONAL_ONLY_SCOPE` on the receipt whenever no leg declares `sees_correlations`. So the
  diagonal-only limitation C-3 admits in prose is machine-recorded, which is stronger than a caveat.
- **§4a's rejection of printed precision is right in both directions**, and its self-criticism —
  *"that is the `D1c` error, committed by me"* — is the correct diagnosis. `A24` agrees: a formatting
  granularity is not a materiality threshold, and neither a floor nor a ceiling.
- **Declining to propose a tolerance is compliance with `A18`, not a gap.** `SPEC` §6.6's adopted
  constraint requires statistic, denominator, precision target and boundary **together**; the
  proposal supplies the first two and openly lacks the last two. Offering a boundary anyway would
  have been the violation.

**One consequence of `A18` for `B0`, stated because it cuts against my own verdict's framing.** §7
item 1 asks Joseph to decide *"whether the acceptance target is the quoted significance (C-1)"* —
i.e. to approve a **statistic** while its precision target and boundary do not exist. Taken
literally, §6.6 forbids that: *"never a formula detached from those definitions… A boundary approved
in the abstract would be an authorization over an object nobody has defined."* The proposal's own §7
preamble (*"Nothing to be adopted"*) points the right way, but item 1's wording reads as an approval.
**Recommended:** item 1 is reframed explicitly as a **direction-setting judgement that adopts no
statistic**, or deferred until the packet is complete. This is the one blocking finding that is purely
a matter of how the question is put.

## B.7 Feasibility — axis (d), and a CORRECTION TO PART A's `A30`

**`A30` drew a feasibility verdict from a cost priced against a design I had already recorded as not
adopted. That inference was wrong and is withdrawn.** Part A concluded that *"the ruled `M(ii)`
quantity is, on the specification's own estimate, unaffordable inside the envelope that governs it"*
and that `(cause 3, Z)`'s `M(ii)` *"will be `UNRESOLVED` at the stop"*, from `SPEC` §5.4's
`5×`–`9×`-over-`R5` figure. **Re-read at the same base, §5.4 says the opposite of what I used it
for:** that figure prices the **historical 46–50-member family**, at per-member costs measured on a
**different subject**, and §5.4 states in terms that it *"does not establish the cost of Z's design,
and therefore not its affordability either, because §6.3 leaves the design open."* I had recorded that
same point myself as `A14` and then applied the number anyway. This is the asymmetric-comparison
failure the campaign catalogues, committed against a warning I had already transcribed.

**Re-measured at `origin/main` `c18f9daa`, `nd-unfolding/Z_CONSTRUCTION_PLAN.md` §5.8:** Z's complete
requirement **including its own cause-3 design** is `222.8` GPU / `348.5` CPU task-hours at `N = 4` —
**`44.6%` / `69.7%` of `R5`'s `500`/`500`, and it FITS**; `N = 5` fits with a thin margin. That
section also carries the correction of its own predecessor: *"the decision is not affordable"* was
withdrawn as *"the wrong sentence"*, and two rows were reclassified from `MEASURED UPPER BOUND` to
`TRANSFERRED`.

**The corrected axis-(d) answer.** The required measurements are **feasible on cost** and **tight on
schedule**. `Z_CONSTRUCTION_PLAN.md` §5.8's own conclusion — *"the binding constraint is the SCHEDULE,
not the ceiling"* — is the operative one: four to five rounds of 374 tasks against a stop of
2026-09-30, i.e. **20 days from today**, with the members not yet existing and **no `D-RESOURCE`**.
`R5`'s ceilings are *"a prohibition and an accounting boundary… NOT authorization to spend up to"*
them, and `R5` §4 item 6 records the meter as *"the one that fails silently"* (`A31`), so a cost claim
here is a plan, not an accounting result.

**What survives of `A30`:** the schedule half, and the consequence that if the stop fires first,
`R5`'s default is the central-value Letter — under which, by `B1`, C-1 has no quoted significance to
be sensitive to. **What is withdrawn:** the affordability verdict and the prediction that `M(ii)` is
necessarily `UNRESOLVED` at the stop. `A30` should be read as amended by this section; `A31` stands.

## B.8 What this lane did not do

It drafted no criterion, proposed no tolerance, chose no statistic, designated no projection `M`, and
graded no leg or cell. It did not edit the proposal, the spec, `CRITERIA`, `SCOREBOARD`, `OPEN_ITEMS`,
`values.tex` or anything under `docs/analysis-note/`. It ran no compute and queried no scheduler. Two
findings are routed to owners rather than acted on: `CRITERIA` §1's decayed artifact-fixing citation
(`B1`), and `SPEC` §3.7a's thread-environment and operand-persistence gaps (`B8`).

**And the limit this creates on this lane.** `B3`, `B6` and §B.6's item-1 reframing are close to
design input. If any is taken up, **`BEN-381` should be read as disqualifying this lane from grading
`(cause 3, Z)`'s `M(ii)`**, and this record is the evidence of why. Recorded now rather than argued
later.

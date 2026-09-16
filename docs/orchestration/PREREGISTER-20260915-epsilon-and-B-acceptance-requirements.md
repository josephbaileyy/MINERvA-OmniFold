# PRE-REGISTRATION 2026-09-15 — what would make `ε` gradeable, and what would make `B` gradeable

**Owner:** `z-independent-assessor` (`docs/orchestration/control-plane/owners.tsv:15`, `display_name`
*"Z criteria independent assessment"*).

## CITABLE FOR / NOT CITABLE FOR — read before quoting anything below

**CITABLE FOR:** the requirements `E1`–`E12` and `B1`–`B9` below, as one assessor's derivation from
the governing text; the citations that source each one; and the record that they were written before
this lane opened the proposal they are used to assess.

**NOT CITABLE FOR:** any grade of `ε` or `B` — this document deliberately contains none. Any
adoption. Any criterion — **these are requirements an assessor will apply, not criteria Joseph has
adopted, and adopting them is his act, not this lane's.** Any claim that a Z covariance exists;
none has been constructed.

## Why this document exists separately from the assessment

Two assessments were routed to this lane on 2026-09-15: `ε = 1e-9` as proposed, and `B`'s
justification. `SPEC` §3.6 states the reason this ordering matters, about its own thresholds:
*"a threshold chosen to make the eventual number pass is not a criterion"*
(`SPEC-20260906-complete-scalar5d-successor-Z.md:1384-1386`). The same hazard applies to an
**assessor's** requirements: a requirement list assembled after reading a proposal is fitted to it.
So the list is written and committed first, and the assessment is a separate commit that cites it.

**One contamination, disclosed rather than denied.** The routing message already relayed the
proposal's three-step shape (a proven inequality, an empirical per-bin tolerance, a scientific
judgement) and two of its measurements. So this list is not written in ignorance of the proposal's
*form*. It is written before reading its *text*, and the requirements below are derived from `SPEC`
only — every one carries a `SPEC` citation, and none carries a citation to the proposal.

## Base, and the one blob everything here is read from

`SPEC-20260906-complete-scalar5d-successor-Z.md`, rev. 21, blob
`296511ab601e44545d7ed3904811a74ee14b3094`. **Re-measured: that blob is byte-identical at
`main` `9dba1194`, at the criteria lane's `8a42f8ea`, and at `df0a8603`** — so the governing text
does not fork across the three shas in play, and no requirement below depends on which one is read.
Line numbers are against that blob.

---

## Part 1 — `E1`–`E12`: what a gradeable `ε` must contain

`SPEC` §3.7a item 3 does not leave `ε`'s form open. It **withholds** the previous number and
**prescribes a structure**, and rev. 19 corrects two readings of that structure. The requirements
are that structure restated as checks.

### The structure itself

| # | requirement | source |
|---|---|---|
| `E1` | **`B` and `S` both exist as named quantities**, and `B ≤ S` is **demonstrated as a precondition, not computed as an arithmetic step.** | `:1779-1782` — *"`B ≤ S` is a precondition, not an arithmetic step"* |
| `E2` | **`B` is an UPPER bound on the operating error of this algorithm in this execution envelope, with its assumptions and its confidence stated.** | `:1728-1733` |
| `E3` | **`S` is an independently justified scientific cap on tolerable CV movement, argued from what the covariance is used for.** | `:1728-1733`, `:1783-1786` |
| `E4` | **`ε ∈ [B, S]`, endpoints admissible, and the position is ARGUED.** A mechanical choice is forbidden — *"The objection was never to the endpoints. It was to arriving at one without an argument."* | `:1771-1775` |
| `E5` | **A measured reproducibility floor may bound `ε` from BELOW as a feasibility constraint; it cannot JUSTIFY `ε`.** The direction is load-bearing: rev. 16 inverted it and that was acceptance-blocking. | `:1406-1409`, `:1720-1723` |
| `E6` | **`ε` may not be read off Z's own null.** | `:1410`, §6.4 |
| `E7` | **The normalizer is `r_null = ‖x_cv2 − x_cv‖ / ‖x_cv‖` over the reported support**, dimensionless, units asserted in the receipt; `sqrt(Tr C_Z)` and the per-bin maximum stay **rejected as the normalizer** on the record. | `:1703-1705`, §3.6a items 1–2 |
| `E8` | **Fixed before production, and not chosen from a favourable result.** | `:1355-1357`, §6.4 |

### The derivation order, which is a separate requirement from the structure

| # | requirement | source |
|---|---|---|
| `E9` | The argument must run **(i)** name the reported quantity a non-deterministic CV could move **and the mechanism**; **(ii)** derive the boundary appropriate to *that* relationship; **(iii)** only then attach a number. §3.6 records that rev. 7 *"attached a number whose derivation was neither"* — so this is the step with a demonstrated history of being skipped. | `:1403-1406`, `:1371-1375` |
| `E10` | **An imported constant is not an imported error model.** The withheld `ε` failed precisely here: *"Importing the operands does not establish the error model, and the operands are the wrong ones."* So for any constant taken from elsewhere, the check is not whether the constant is real but whether **the relationship it was set to govern is the relationship `ε` governs.** | `:1646-1650`, `:1664-1668` |
| `E11` | **Transfer discipline.** Evidence from a different bank or subject is a **transfer and needs a transfer argument**; and evidence from Z's own bank engages `E6`. Gap 2 names both horns and says *"Neither is chosen here; both must be."* | `:1830` |
| `E12` | **Envelope scope must match the claim.** Within-envelope reproducibility (`r_null`) and across-envelope agreement (`r_cross`) are different quantities; if the claim is portability across the envelopes a requeueing campaign will see, `r_null` **does not substitute**. | `:1802-1818` (Gap 1) |

### Two things that are NOT requirements, recorded so they are not read in

- **`B > S` does not mean the envelope is inadequate, and does not mean correct runs would fail.**
  It means `B ≤ S` is not demonstrated **on the available evidence** — a statement about evidence,
  not about the world (`:1744-1751`). An assessor who converts a loose bound into a defect commits
  this lane's catalogued inference-from-absence error in the direction of its active argument.
- **No endpoint is prohibited.** `ε = S` and `ε = B` are both admissible when argued (`:1764-1769`).
  Rev. 17's *"never taken as an endpoint"* is withdrawn, and an assessment that revives it is
  applying a rule the governing document deleted.

---

## Part 2 — `B1`–`B9`: what a gradeable `B` must contain

`B`'s justification does not exist yet; `SPEC` §3.7a names **three routes and privileges none**
(`:1888-1901`), and states three gaps any measured route must answer. These requirements are
route-agnostic on purpose: naming one route as required would be this lane supplying the design.

| # | requirement | source |
|---|---|---|
| `B1` | **`B` is an upper bound with stated assumptions and stated confidence.** A point observation, a maximum over an unspecified population, or a single comparison is not yet `B` until the document says which of those it claims and under what assumptions. | `:1728-1733`, Gap 2 *"the objective"* `:1827` |
| `B2` | **The ENVELOPE `B` is a bound for must be named, and the envelope the evidence was produced in must be named, and they must be the same one** — or the difference must be argued. This is Gap 1 stated as a check. | `:1802-1818` |
| `B3` | **The SUBJECT must be named and disposed against §6.4.** Own bank → `E6` bites; different bank → transfer argument required. | `:1830` |
| `B4` | **The sampling assumptions must be stated where the route samples.** Repeats inside one job share a node, a library load and a page cache; repeats across jobs do not — *"the design must say which it makes."* | `:1828` |
| `B5` | **Anti-tuning is a PREDECLARATION, not a design feature.** What prevents tuning is *"predeclaring the estimator of `B`, the repeat count and the envelopes BEFORE any run, and committing not to revise them afterwards"* — explicitly **not** the arm count. | `:1829` |
| `B6` | **A design-property `B` (route (i)) must state what it claims and what it does not.** Pinning configuration can only support a claim about the pinned configuration; §3.7a says in terms that whether pinning makes two re-unfolds bit-identical **here is untested**. | `:1890-1892` |
| `B7` | **Bit-identity is not `B`.** `B` is a bound on an error; bit-identity is a claim that the error is zero. A failed bit-identity check is a **refutation of a stronger claim**, not a value for `B` — a route that observes non-identity still owes the bound. | `E2`/`B1` applied; `:1728-1733` |
| `B8` | **Cost must be priced against the right operation on the right partition, or declared unpriced.** §3.7a's Gap 3 records this exact error being made twice in the same document; the measured per-invocation figures are `0.39`–`0.58` **CPU** task-h on a **historical** subject, and are marked **TRANSFERRED** to Z, which has neither this bank nor this slab count. | `:1832-1886` |
| `B9` | **No route may assume an authorization.** `D-RESOURCE` does not exist; `R5`'s ceilings are *"a prohibition and an accounting boundary … NOT authorization to spend up to"* them; the cause-3 scan's launch authorization is SUSPENDED. A proposal may state a cost; it may not treat the cost as cleared. | `:1901`, §4.1 |

---

## Part 3 — the naming hazard this lane will apply from here on

**At least three distinct objects in this campaign are called `B`**, and two of them appear in the
same sentence of the record that routes the work:

| the name | the object |
|---|---|
| `B` in `SPEC` §3.7a | the **operating-error bound** on the algorithm in its execution envelope — the subject of Part 2 |
| **Endpoint B** | a publication endpoint, currently **DEFERRED NOT PASSED**, listed beside Gate 2 FAIL and `cause3_corr` WITHHELD |
| `lane_b` / **lane B** | two owner rows in `owners.tsv` (`cstat` and `lane_b`), i.e. a *who*, not a quantity |

This lane will write `B_op` nowhere and will instead say **"§3.7a's `B`"** whenever the
operating-error bound is meant. A reader who resolves the wrong one gets a plausible sentence, which
is the failure mode that makes the collision worth recording rather than absorbing.

---

## What this document does NOT do

- It grades nothing. `E1`–`E12` and `B1`–`B9` are checks, and the checking is a separate commit.
- It proposes no mechanism, no threshold, no route, and no number. This lane declared a partial
  recusal on supplying mechanisms at `068436e5`; naming a route here would spend the next verdict on
  the route named.
- It does not adopt anything. `SPEC` §3.5 and the routing authorization both put adoption with
  Joseph, and a requirement list is not an adoption.
- It seeks and implies no authorization, and requires no compute.

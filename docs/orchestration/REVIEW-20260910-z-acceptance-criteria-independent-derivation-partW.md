# PART W — the cause-3 amendment: adequacy conditions, pre-registered, and two answers already closed

**Owner:** independent-assessment lane. **Base of measurement:** `6f24fb00`. **No grade assigned.**
**Subject NOT YET IN HAND** — the amendment pin has not landed. Written first, as with Parts A, F, S
and T, so the verdict cannot be fitted to the answer.

**Scope discipline, per Joseph:** consequential issues only, and **no expansion into a cleanup
campaign.** The return-schema recurrence is fixed and verified; I am not sweeping for more of it.

---

## W.1 — THE OBJECTION'S GROUND, VERIFIED IN THREE PLACES

The objection element 5 must engage is the mathematical reviewer's. Its premises verify verbatim:

- **`SPEC-20260906:3550-3552`** — *"**The quantity** for `(cause 3, Z)`'s `M(ii)` is the variation of
  the **assembled** covariance `C_Z` when the sweep-side and throw-side estimator baselines are varied
  **jointly**."*
- **`z_contract.py:222-225`**, `cause3_agg` — *"how much **estimator-baseline sensitivity** is
  scientifically acceptable"*, **unqualified**; no restriction to a subset of `C_Z`.
- **`z_contract.py:233-235`**, `cause3_corr` — *"a MET result on them **licenses nothing** about
  `C_Z`'s off-diagonal structure."*

And `C_stat`/`C_ML` are summands of `C_Z` (`SPEC:610`, `z_assembly.py:4`).

## W.2 — THE DECISIVE MEASUREMENT: BOTH EXCLUDED SUMMANDS *DO* RESPOND TO THE ESTIMATOR BASELINE

`SPEC:3550`'s wording leaves an opening the subset argument alone does not close: the declared
variation is of the **sweep-side and throw-side** baselines, and one could argue `C_stat`/`C_ML` sit on
neither, so holding them fixed excludes nothing the declaration asks to vary. **That defence is
refuted by measurement.**

| producer | the estimator seed reaches the estimator | stamped |
|---|---|---|
| `bootstrap_nd.py` (`C_stat`) | `:47` `_est_seed = a.seed if a.fixed_data_seed is not None else a.estimator_seed`; `:55` `measured_weights=mw, seed=_est_seed` | `:67` `estimator_seed=np.int64(_est_seed)` |
| `seedscan_split.py` (`C_ML`) | `:69` `… seed=args.estimator_seed, …` | `:99` `estimator_seed=np.int64(args.estimator_seed)` |

**Both blocks are functions of the estimator seed.** Varying the estimator baseline changes the
replicas, therefore changes `C_stat` and `C_ML`, therefore changes their contribution to the assembled
`C_Z`. **So a test that holds them digest-identical suppresses a real component of exactly the
variation `SPEC:3550` declares as the quantity.** The objection stands on a measurement, not on an
argument about summands.

**This closes two of the four coherent answers before the amendment is read.** The available responses
to element 5 are:

| response | status |
|---|---|
| **(a)** narrow the **claim** — the conditional test discharges a named sub-claim and cause 3 stays OPEN | **available** |
| **(b)** narrow the **subject** — amend `SPEC:3550`'s declared quantity | **available, but it is a contract change and therefore Joseph's**, and it must be argued scientifically rather than by convenience |
| **(c)** argue the excluded summands' variation is **negligible** | **not available as an assertion** — it is an empirical claim and no measurement of it exists; §W.2 shows the mechanism by which they vary |
| **(d)** argue the excluded summands are **invariant** to the estimator baseline | **refuted** — `bootstrap_nd.py:55` and `seedscan_split.py:69` both pass the estimator seed into the estimator |

**And (d) has an internal tension independent of the seeding**, from Part T §T.3: `:8-10` calls the
blocks *"#13-invariant"* — invariance to a **different** thing — while `:421` has a member build *"this
member's OWN `C_stat` and `C_ML`"*. If they were invariant to the estimator baseline the member
rebuild would be pointless. **The amendment cannot have it both ways.**

## W.3 — PRE-REGISTERED ADEQUACY CONDITIONS

- **W1 — element 5 must state which of (a)–(d) it takes**, explicitly. An amendment that describes the
  conditional test without naming its relation to the declared quantity has not engaged the objection.
- **W2 — if it takes (c) or (d), it must supply the measurement or resolve the tension in §W.2.**
  Asserting either is a `BLOCK`.
- **W3 — the operative word in `:233-235` is *licenses*.** An amendment that changes what is
  **measured** without changing what a `MET` **licenses** does not reach the objection, because the
  objection is about licensing.
- **W4 — `cause3_agg`'s unqualified purpose must be qualified too, or left standing knowingly.** If the
  test is conditional and `:222-225` still asks how much estimator-baseline sensitivity is acceptable
  **unqualified**, the boundary keeps demanding something the test does not deliver.
- **W5 — no fourth grade token.** A conditional discharge is not a grade
  (`DECISION-20260902-joseph-rules-no-fourth-grade-token`). If cause 3 is not discharged, it is `OPEN`,
  and the amendment must say so in the grade column rather than in prose beside it.

## W.4 — ELEMENTS 3 AND 4 MUST TRAVEL WITH THE GRADE, AND THE CODEBASE ALREADY SAYS WHY

Elements 3 (*what passing licenses*) and 4 (*which broader claims it does not support*) are licensing
statements, and this repository already has the mechanism **and its rationale**, at
`z_validator.py:166-167`:

> `# The narrowing that must travel WITH the grade, not sit in a specification the grader may not open`

`_DIAGONAL_ONLY_SCOPE` (`:168-172`) is emitted on every outcome with no correlation-sensitive leg, and
is not caller-suppressible. **So elements 3 and 4 belong in the emitted scope statement, not in a
document** — and an amendment that writes them in prose has put them where the code's own comment says
they do not survive. This is Part I §I.1's finding pointed forward rather than backward.

## W.5 — `κ`: I RECOMMEND IT STAYS WHOLE WITH THE REVIEWER

Asked whether the clause *"explain how numerically unresolved functionals are handled without silently
removing them from the declared acceptance population"* needs my eye. **It is a population question and
it is my subject — and I still recommend against splitting it.** A package assessed by two lanes has a
seam, and a silent-removal defect is exactly the kind that lives in a seam. **Better: the reviewer
holds `κ` whole and reports explicitly on that clause**, and if it judges the population half outside
what it is willing to certify, route it to me then. I would rather take it late than fragment it early.

## W.6 — NOT ASSESSED

- **The amendment** — not landed.
- **`κ`'s formula, value, numerical justification and failure outcomes** — the reviewer's.
- **`ec5f0b99` and `6d959ab3`** — frozen pending review, and not in my slice.
- **`S2`** — still held; the maps are not here.
- **Still open:** `A-6(a)`, `A-6(b)`, the excluded producing execution, the three-or-four block
  population, and Part V's non-member return-contract `BLOCK`.

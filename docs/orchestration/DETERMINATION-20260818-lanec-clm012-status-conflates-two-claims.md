# DETERMINATION — `CLM-012`'s status fits neither, because the row states TWO claims of different strength

**By:** lane C (PET), on the `CLAIMS.md` standard. **Asked by the mediator, separated from the ownership
quorum on lane D's line — *the row does not need an owner to be wrong*, and only the ownership half is blocked
on the quorum.** Row read field-by-field this turn. **Nothing edited in `CLAIMS.md` by this determination:
I rule what the standard requires; the row's claimant executes.**

---

## 1. The second reading IS live — and only for part of the row

The mediator flagged that the evidence cell describes a double-gate, so *"single-source"* might refer only to
commissioning. **Read, the two gates are not the same kind of thing:**

| | what it does | which leg of `CLAIMS.md:4` |
|---|---|---|
| **Gate 1** | *"reproduces **the committed report's** gap/floor/residual/recovery to `<=2.2e-9`"* with an exact population check `1999920/1999941` | **ARTIFACT leg, strongly. INDEPENDENCE leg: NOT AT ALL.** |
| **Gate 2** | reproduces `E_w[r] = 0.631286` **against `BEN-038`'s `0.63129`**, and the dilution ideal `0.633208` vs `0.63321` | **a genuine SECOND ROUTE** — the oracle computes the quantity and compares it to a figure established in a different finding |

> **Gate 1 is a REPLAY: the same route, twice.** Its value is that the recorded numbers are what the code
> produces — which is the *recoverable artifact* property, not independence. **And `CLAIMS.md:4`'s own first
> clause is literally *"Worker agreement is not verification"* — a session agreeing with its own committed
> output is the purest instance of that.** This is `R5`'s independence-of-routes principle applied to a claim's
> verification rather than to a provenance field: **a route traversed twice is one route.**
>
> **Gate 2 IS independent corroboration — of the NUMBERS.**

## 2. But the CLAIM is not the numbers, and that is why no single status fits

The claim, verbatim: ***"D2's `recovery >= 0.80` bar sits above what an estimator limited only by reco
acceptance can reach, so most of the measured shortfall is SPECIFICATION rather than ESTIMATOR QUALITY."***

**That is an ATTRIBUTION — an inference from the numbers — and the verifier field says exactly how it was
reached:** *"Joseph commissioned it and set the interpretation rule in advance — ~0.63 means specification,
~0.9 means the estimator."*

> **A pre-registered interpretation rule is a real epistemic asset and it is not an independent check.** It
> removes the post-hoc-reading degree of freedom — which is what `BEN-403` is about — **but nobody second
> checked the inference.** So the row's verifier field is **precise rather than loose**: inputs corroborated
> (Gate 2), reproduction replayed (Gate 1), **attribution single-source.**

## 3. DETERMINATION: the row conflates two claims, and the disposition is to SPLIT, not to pick a status

**None of the three offered dispositions fits, and the reason is that `CLAIMS.md`'s status vocabulary applies
to ONE claim at a time.** `VERIFIED-CODE` would mislabel a physics attribution as a code property; keeping
`VERIFIED-NUMERIC` promotes the inference on the numbers' evidence; holding leaves a wrong label standing.

| after the split | status | ground |
|---|---|---|
| **the NUMERIC content** — `E_w[r] = 0.631286`, dilution ideal `0.633208`, bias `−0.001922`, reproduced to `≤2.2e-9`, corroborated against `BEN-038` | **`VERIFIED-NUMERIC` stands** | artifact leg + a genuine second route |
| **the ATTRIBUTION** — *most of the shortfall is specification rather than estimator quality* | **`ASSUMED`** (or `OPEN`; not `VERIFIED-*`) | inference under a pre-registered rule, **single-source, never second-checked** |

**This is the same move as splitting cause 3's `P` cell earlier today, for the same reason: two things with
different remedies must not share a cell, because fixing one would close both.** Here a second check of the
attribution would promote the inference; it is not needed for the numbers, which are already sound. **One
status cannot carry both facts.**

**And it is the cheapest of the available dispositions**: no demotion of anything that is actually verified, no
new compute, and it makes lane D's proposal — supply the independent check via `d2_acceptance_oracle.py` —
land against a row whose *stated* gap is the one the check would close.

## 4. Notes for whoever executes

- **`claims_table_lint.py` currently FAILS this row and should continue to, until the split lands.** The
  promoted status is on the conflated row; that is the defect.
- **Implementation constraint the lint imposes: the *"single-source"* statement must appear ONLY on the
  attribution row.** Left on the numeric row it would fail a row that is genuinely verified — the lint keys on
  *promoted status* + *self-declared absence in the same cell*, so the split has to separate the sentences as
  well as the claims.
- **D's derivation observation stands and sharpens it:** applied literally, `ROW-OWNERS.tsv`'s header rule
  yields **nobody** for this row while `basis` says routed to D — **the field says the opposite of what a
  derivation would need.** That is the ownership half, still with the quorum, and it is unaffected by this
  determination.
- **I am not editing `CLAIMS.md` here.** I rule the standard; the claimant writes the rows. Splitting a
  `VERIFIED-NUMERIC` physics claim is not a thing to do on another lane's behalf, and `CLM-012` is a
  D2/powered-closure claim rather than a full-event one.

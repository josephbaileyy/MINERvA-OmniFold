# ASSESSMENT 2026-09-18 — the integrated acceptance proposal, with `E1` and `E2` PERFORMED

**Owner:** `z-independent-assessor` (`owners.tsv:15`). **Subject:**
`PROPOSAL-20260917-integrated-acceptance-existing-products.md` at
`d8f5ccd5e062a93e435f5634775486c0fe6a8db4`, author `owners.tsv:14` `[91eaa2]`. **Also adjudicated:**
the finding routed to me at `f6a2cb8b` §18.2 by the assembly-pilot lane.

## CITABLE FOR / NOT CITABLE FOR

**CITABLE FOR:** the adjudication of the routed finding; `E1` and `E2` as **PERFORMED and
DISCHARGED**, with their measurements; findings `I1`–`I7`; and a recommended decision.

**NOT CITABLE FOR:** adoption of anything — **`ε = 1e-9` is still NOT ADOPTED and acceptance of the
products is Joseph's act, not this record's.** `θ` stays **closed as not adopted** and is **not** a
floor. `B` unestablished. **Full `S` OPEN**; §7 item 4 prepared, not graded. Gate 2 **FAIL**,
`cause3_corr` **WITHHELD**, endpoint B **DEFERRED NOT PASSED**. No covariance is adoptable on the
strength of anything here.

## ⚠ WHAT I DID ON THE CLUSTER, STATED FIRST

**Cluster access is live from this session** (`saul.nersc.gov` → `login31`, `2026-09-17T16:33:18Z`),
so `E1` — which the routing lane correctly declined as an owner — **was performable by a non-owning
lane, and I performed it.** All of it was **read-only on a login node**: `find`, `stat`,
`sha256sum`, `git hash-object`, and one `python3` that loads an `.npz` and computes norms.
**No `sbatch`, no `srun`, no job attempt, so `R5`'s accounting is untouched** — the meter charges
`ElapsedRaw` over execution attempts and there were none. Nothing was written into any product tree;
the only writes were to `/tmp`.

**Every product figure in this record is therefore MEASURED BY ME, not relayed.** That is the change
from my two previous assessments, where all such figures carried a RELAYED label.

---

# RECOMMENDED DECISION

**The recommendation in §7 is sound on its own terms and I can find no alternative route open for
these products. I recommend Joseph accept it — but not as *"no contract amendment is required"*,
which is the one claim I cannot sustain.** What the route needs is neither an amendment nor nothing:
it needs **a ruling that a pre-dating transfer satisfies `SPEC` §3.6a item 3's order of work**, and
until that ruling exists **reject condition `4c` is live against the route** (`I2`). Two further
things are owed and both are cheap: the transfer's falsifier remains **unevaluable** (`I4`), and
`P1` — the projection-definition check — is still not done.

**`E1` RECONSTRUCTS and `E2` is DISCHARGED**, so the recommendation's own two conditions are both
met; what is left is the contract question, not the evidence question.

---

# 1. `E1` — PERFORMED. **RECONSTRUCTS.**

Reject condition `11b` (`SPEC:1268`) requires the ratio be rebuilt from the **persisted operands,
predicate included**, without reading the producer's recorded norm — and `z_statistics`'s own review
finding 3 requires the persisted mask be **checked, not applied**. Both were honoured.

**Provenance of what I read.** `z-null.npz` sha256
`cb82fc3285c981b91625530d48c14ff5554db5154db298a3144a57520633d77e` — **MATCHES** the digest recorded
in `product-digests.txt`, and `z-cv.npz` (`3d7465f6…`) and `z-mean.npz` (`61b7a493…`) match theirs
too. The file carries exactly `x_cv`, `x_cv2`, `support_mask`, `schema_version`,
`construction_digest`, `declaration_json` — **and no recorded null norm**, so no reading of it was
possible even by accident.

**Instrument pinned rather than trusted.** I ran the comparison twice: once with my own arithmetic,
and once by **calling** `z_statistics.null_ratio` and `reconstruct_null_ratio` at the blob I had
already content-verified (`eb4edb33…`), uploaded to a private path. *An instrument for this rule
exists, so it is called rather than retyped.*

| check | measured |
|---|---|
| `n_total` / `n_support` (my `x_cv > 0`) / persisted mask | `65856` / **`10694`** / **`10694`** |
| **masks ELEMENTWISE IDENTICAL** | **`True`** — so the predicate is *checked*, and `11b`'s independence condition is met |
| `n_genuine_zero` / `n_negative` / all finite | `55162` / **`0`** / `True`; and `10694 + 55162 = 65856` |
| `r_null`, my arithmetic, **three** summation orders (numpy, magnitude-sorted, pure-Python) | `4.45200021375829101e-14` in **all three** |
| `null_ratio` and `reconstruct_null_ratio`, blob-pinned | `4.45200021375829101e-14` — **bitwise equal to mine** |
| `num_norm` / `cv_norm` | `1.43018328471224348e-50` / `3.21245106927996035e-37` |
| **versus the build's `4.45200021375829038e-14`** | **not bitwise; `1.00 ULP`, relative `2.220e-16`** |

**Verdict on `E1`: RECONSTRUCTS.** The reconstruction is independent (my own predicate, my own
arithmetic, and the instrument called separately), and it agrees with the build to **one unit in the
last place** — the irreducible signature of a different summation order over `10,694` `float64`
values. **`11b` is satisfied.**

**Two things this sharpens.** The routing lane reported *"15 significant figures"* from its own
reconstruction (`4.452000213758293e-14`); mine is `4.452000213758291e-14`, and the build is
`…8290`. **Three reconstructions, all within `2 ULP`, none bitwise** — which is itself the argument
for a numerical rather than a bitwise criterion, made on the criterion's own operands. And my value
is **bitwise identical to the committed instrument's**, so the residual difference lives entirely in
the build's summation path, not in the reconstruction.

**Every other relayed product figure, now measured by me:** `10683` of `10694` support bins differ
bitwise, `11` agree; **`0`** differ off support; `max|Δ/x| = 1.75527161917355179e-12` at
support-index `5723` = grid-index `31499`; **`min_i|ρ_i| = 0.0` exactly**; the bracket
`min ≤ r_null ≤ max` holds; margins **`569.7×`** per-bin and **`2.246e4×`** on `r_null`. All
reproduce to every digit quoted.

## `I1` — a provenance result `E1` produced incidentally, and it is favourable

The pilot ran from `/pscratch/sd/j/josephrb/zdeploy-e09513d8`, whose
`nd-unfolding/z_statistics.py` and `z_contract.py` are **byte-identical to the committed blobs**
(`git hash-object` on the cluster: `eb4edb33…` and `24379afb…`). **So the instrument that produced
the products is the same bytes as the instrument I verified and called.** Separately, the *main*
cluster checkout `/pscratch/sd/j/josephrb/MINERvA-OmniFold/nd-unfolding` contains **neither file** —
so the pilot correctly ran from the deployment and not from the shared tree, which is the opposite of
the `OI-136` shape. `p4_lib.py` and `adopt_unified_5d.py` in the shared tree are byte-identical to
`d8f5ccd5`'s.

# 2. `E2` — DISCHARGED, and it needed no cluster read at all

The proposal frames `E2` as *"a receipt read"*. It is answerable from **committed** evidence:

| | |
|---|---|
| tolerance declared | `REPRO_RTOL_PER_BIN` enters at **`5d617da8`, 2026-08-08 02:26:27 −0400, author Joseph Bailey**; the source comment says *"set by Joseph 2026-08-07"* |
| precursor throw product | `unified_throw_cov_5d.root`, mtime **2026-09-14 15:53:06 −0700**, `2,668,265,910` B |
| the null observation | `z-null.npz`, mtime **2026-09-17 00:36:25 −0700** |

**`E2`: PRECURSOR LATER.** The tolerance pre-dates the product by **37 days** and the observation by
**40 days**. So §3.1's fourth clause holds **on dates as well as on subject**, and the proposal's
weaker fallback reading is not needed.

---

# 3. The routed finding — **REFUTED AS STATED, and its instinct is right for a different reason**

## `I2` — `[B, S]` lives in a section `SPEC` itself calls ENTIRELY PROPOSED, so there is nothing to amend; what is live is `4c`

**Every one of the routing lane's `SPEC` citations verifies** — `:1732-1733`, `:1737-1739`,
`:1742-1743`, `:1779-1782`, `:1786-1787` all resolve by content. The reading built on them does not,
and the reason is one line above them all:

> **`SPEC:1552` — `## 3.7 THE TWO CRITERIA — ⚠ SPECIFIED BUT NOT COMPLETED, AND ENTIRELY PROPOSED`**

and `:1557-1560`, which states the consequence: *"§3.6 therefore still lists both criteria as
incomplete, and §3.3 condition `4c` still bites — a run against an underived boundary is itself a
reject condition. **That is the mechanism that makes this state safe.**"*

**So the `[B, S]` framework is `§3.7a`'s own proposal, not an adopted requirement.** One does not
amend a proposal, and arguing `ε` outside `[B, S]` contradicts no ruling. **The routed finding is
refuted as stated.** *(This also corrects my own `E1` requirement at `923a321c`, which derived the
interval from `:1779-1782` as though it were governing. It is the schema's answer, not the schema.)*

**But the instinct is right, and the correct location is worse for the proposal, not better.** What
governs is **§3.6a**, and `:1362-1365` says `§3.7` does not relax it: *"§3.6's requirements are not
relaxed by §3.7 and none of them is dropped."* §3.6a item 3 fixes an **order of work**
(`:1403-1406`): *(i)* name the reported quantity a non-deterministic CV could move **and through what
mechanism**; *(ii)* **derive the boundary appropriate to that relationship**; *(iii)* only then
attach a number.

| §3.6a item 3 clause | the transferred `ε = 1e-9` |
|---|---|
| *"Fix `ε` from a control established BEFORE implementation"* | **SATISFIED** — and `E2` now proves it on dates |
| step **(ii)**, *"derive the boundary appropriate to **that** relationship"* | **NOT SATISFIED.** The boundary was derived for the standard-P4 reproduction gate, not for Z's CV-to-reported-quantity relationship. It is step (iii) with step (ii) supplied by a different subject |

**And therefore `4c` (`SPEC:1257`) is live against this route, not an amendment gap.** *"The run
proceeds against a fixed-seed null bound … that §3.6 still lists as incomplete. An un-derived
boundary is not a criterion."* **A reject condition is a worse position than a needed amendment**,
because an amendment is an act Joseph can take while `4c` is a state the route is in.

## `I3` — but step (ii) is now UNPERFORMABLE for these products, which is what makes the decision a ruling rather than a choice

§6.4 requires the bound *"fixed before production"*. **Production has happened.** So **no** boundary
fixed today — derived or otherwise — satisfies that clause for *these* products. Step (ii) cannot be
performed for them by anyone, at any cost.

**This strengthens the proposal's §1(iii) and corrects its stated ground.** §1(iii) argues from
*"not chosen from a favourable production result"*; that clause is weaker, because a boundary derived
from the **use** would not consult the null and so could not have been chosen from it. The decisive
clause is **"fixed before production"**, and the proposal's own §3.1 table uses it correctly. The
conclusion holds on the stronger clause: **the only admissible `ε` for these products is one that
already existed.**

**So the three positions converge, and none of them is the right description:**

| position | verdict |
|---|---|
| the proposal: *"no contract amendment is required, and that is its strongest property"* | **NOT SUSTAINED.** `4c` is live until item 3 is disposed of |
| the routing lane: *"an amendment to §3.7a is required"* | **REFUTED.** §3.7a is ENTIRELY PROPOSED |
| mine at `ed18a231`: *"§6.4 **plus** condition 11"* | **holds only for a `θ`-style REPLACEMENT**, and the proposal is right that this route replaces nothing — its §3.1 four-clause check is correct and condition **11 does not fire** |

**The accurate statement, and the decision I recommend Joseph be asked for:** *does a pre-dating
tolerance transferred from a different subject, with its transfer argument stated, satisfy §3.6a item
3 for products whose production has already occurred?* **YES → `4c` clears and the route is complete
as written. NO → these products cannot be accepted on any route, because step (ii) is unperformable
for them** — which is §2.3's disjunction reached from the contract side instead of the configuration
side.

## `I4` — the route's one load-bearing leg is unverified and cannot be verified before the thing it gates exists

If item 3 is disposed of by the transfer, **the transfer argument is the whole justification**, and
§C.3's falsifier — *"if pinned-envelope repeats of the full CV chain show a floor above about `2e-11`
for Z's bank"* — is **UNEVALUATED and unevaluable**: no pinned envelope exists (§C.4, measured) and
no Z bank exists. That was my `F4` at `fdf5e510` and nothing since has changed it.

**What exists instead is a direction argument, and I confirm it as measured here.** The source floor
is a cross-CONC comparison (`p4_lib.py:197-198`, `conc_new: 6`, `conc_reference: 4`,
`worst_rel_bin = 1.9e-11`), and **my own measurement** gives the target's within-process per-bin
maximum as `1.755e-12` — **`10.8×` smaller**. A tolerance the *harder* comparison satisfies is a
fortiori appropriate for the easier one. **That is real evidence and it is not the falsifier.**
Direction is not evaluation.

## `I5` — the routed point about `SPEC:1406-1409` is half right, and the symmetry charge does not land

The routing lane observes that the proposal invokes `:1406-1409` as a **license** while it is written
as a **prohibition**, and notes it is the sentence I used to ground the `θ` decision *"read in the
opposite direction."* Taking the sentence exactly:

> *"**And a reproducibility floor is not a substitute for step (ii).** A measured process-to-process
> floor … tells you what repeatability is **achievable**; it does not tell you what error is
> **scientifically acceptable** … It may bound `ε` from below as a feasibility constraint; it cannot
> justify `ε`."*

- **The proposal's role-split is CORRECT.** It assigns the observed `1.755e-12` to **feasibility**
  and the transfer to **justification** — which is precisely the division the last sentence draws.
  Nothing in §3.2 uses the floor to justify.
- **What the sentence does NOT do is license omitting step (ii)** — its lead clause exists to insist
  on step (ii). So `:1406-1409` supports the split and is silent on the transfer; what governs a
  transfer is `:1403-1406` and Gap 2's transfer horn (`:1830`). **`I2` is where the gap actually
  is**, and citing `:1406-1409` for it overreaches in the proposal's favour.
- **No symmetry problem.** `θ_A` was being used as a **cap**, which the sentence forbids; the
  observed floor here is used for **feasibility**, which the sentence permits. Same sentence, two
  different roles, and both readings are its plain content. The charge is worth answering rather than
  dismissing, and it does not land.

## `I6` — the routed point about the normalizer rejection is **REFUTED**: it is on the record, in `SPEC`

§3.6a item 1 requires the alternatives *"considered and rejected on the record if not chosen"*
(`:1390-1396`, verified). **They are, and it predates the proposal:** `SPEC:1579` is headed
*"Item 1 — the normalizer, **with both named alternatives rejected on the record**"*, `:1602` carries
*"REJECTED — normalization by `sqrt(Tr C_Z)`"*, and `:1627` carries
*"REJECTED as the gate, RETAINED as a reported diagnostic — the per-bin maximum relative
deviation"*. §C.1 already points at it. **Nothing is owed by the proposal here.**

---

# 4. Joseph's five requirements

| # | verdict |
|---|---|
| **1 — the property, envelope, and tolerance-vs-bitwise** | **MET.** The contract reading is right: `SPEC:1415-1417` (verified) puts scale-relativity among what is *"already determined and needs no further decision"*, so a bitwise criterion would itself trip condition 11 — the kind was never open. And bitwise is the gate-that-cannot-pass, which **I measured**: `10683 of 10694` differ. The **within-run** envelope is stated narrowly and correctly |
| **2 — qualify, or change the configuration?** | **MET, and §2.3 is the strongest section in the proposal.** It observes neither prohibition alone — `78a8c2ee`'s boolean `B = 0` **fails** on these products (I measured the failure), so it was scoped to the pinned design; a pinned run would qualify the **pinned** configuration; therefore *"regeneration REPLACES them rather than rescuing them."* I confirm the composition, and it is a limit the author states against their own declaration |
| **3 — `B`, `S`, `ε` against the claims, with the amendment named** | **NOT MET as written** — `I2`/`I3`. The §3.1 four-clause §6.4 check is correct and condition 11 does not fire; the defect is that §3.6a item 3 and `4c` are not addressed at all, and *"no amendment is required"* is asserted over that silence |
| **4 — minimum evidence, and what each outcome decides** | **MET, and now DISCHARGED.** `E1` and `E2` were the right two checks; both are performed above. §4.1's *"`f_i` is NOT mandatory here"* is correct, and it also correctly withdraws the claim I had to withdraw myself at `9b896592` |
| **5 — artifact projection vs upstream estimator, definition vs numerical** | **MET.** The `P1`/`P2`/`P3` split is the right decomposition, *"`P1` and `P3` are independent and `P3` does not imply `P1`"* is correct, and `P1` is properly marked **owed, cheap, and not yet done** — which was my finding at `5a6d32fb` and is now adopted rather than argued |

## `I7` — three citation corrections, one of which withdraws a note of my own

1. **`z_contract.py:84` for `G_FLOOR = 1.0` is CORRECT at the proposal's base — and my note calling
   it misaddressed is WITHDRAWN as under-specified.** Measured: the file has **forked**. Blob
   `24379afb…` (`origin/main`, `480bed76`, `d8f5ccd5`) has `G_FLOOR` at **`:84`**; blob
   `80325ce5…` (the assembly-pilot lane, `67528132`) has it at **`:126`**. I checked the correction
   record against *its own* base and called the citation wrong; it is right on `main` and on the
   criteria lane. **The real finding is the fork**: a bare `z_contract.py:84` resolves differently
   depending on which lane's tree the reader holds, and my own note named no tree either. *A line
   number without its tree is its own decay.*
2. **`gate_g_domain` is `z_assembly.py:126`, not `z_contract.py:126-132`.** The proposal's bare
   `(:126-132)` follows a `z_contract.py` citation and so reads as that file; `z_contract.py:126-132`
   is unrelated text about import guards.
3. **`worst_rel_bin = 1.9e-11` is at `p4_lib.py:198`**, not `:202`; `:202` is the dict's closing
   brace. `p4_lib.py:93` and `:109` are correct as cited.

**None of the three touches a conclusion.** They are recorded because this lane has insisted on
address discipline in two other documents and must meet it here.

---

# 5. What I recommend, and what is still owed

**Recommend accepting §7's items 1, 3, 5 and 6 as written, and item 2 and item 4 with the
restatement at `I2`/`I3`:**

- **the criterion**: numerical agreement on `r_null` over a **within-run** envelope, `ε = 1e-9`
  transferred — **conditional on Joseph's ruling that a pre-dating transfer disposes of §3.6a item 3.
  Without that ruling `4c` is live and the products are not acceptable on this or any route.**
- **`E1` and `E2` are discharged** (§1, §2), so no further evidence is owed on the null.
- **`P1` is owed and is the cheapest outstanding item in the package** — a code read, no matrices, no
  cluster.
- **the transfer's falsifier stays UNEVALUABLE** (`I4`); the `10.8×` direction argument is confirmed
  and is not a substitute.
- **`S` stays OPEN.** §6's placement of each condition against its settling evidence is sound
  preparation and I do not grade it; §7 item 4's residue is the author's own, they correctly withhold
  the verdict, and **it remains unrouted to this lane as an object**, so I issue none either.
- **the anti-correlation condition on `Σ_V C_b` is unmeasured**, so no projection numerical bound
  exists (`5a6d32fb` `T5d`, retracted by its own author and independently reproduced twice).

## What this assessment does not do

- Adopts nothing and grades no cell. Acceptance is Joseph's act.
- Closes neither `S` nor §7 item 4.
- Supplies no tolerance, no population, no margin, no projection list. `I2` names a ruling that is
  needed; it does not make it.
- Ran no compute: read-only login-node work only, no job attempt, `R5` untouched. The recusal at
  `068436e5` is scoped to the products-then-claims read ordering and does not reach any of this.

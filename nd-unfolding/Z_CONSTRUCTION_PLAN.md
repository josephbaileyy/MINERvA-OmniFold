# The prospective Z construction — a RECOMMENDED PLAN, not a request to run

**Written 2026-09-10** against `origin/main` = `a65e23a6`. Supersedes `Z_BUILD_PACKET.md`'s
`throw` and `null` rows; everything else in that packet stands and is cited rather than repeated.

**CITABLE FOR:** the footing recommendation of §1, the Gate-2 scope measurement and permitted path
of §2, the reuse/fresh split of §3, the estimator recommendation of §4, the costing of §5 **with
its stated evidence classes**, and the ruling list of §6.

**NOT CITABLE FOR:** any authorization, any adoption, any grade, any discharge, any gate movement,
any count, any spend, or any publication claim. **Gate 2 remains FAIL. No scalar-5D covariance is
adopted.** `R5`'s ceilings, accounting start and stop date are untouched. **Nothing here waives a
gate, and §2 records why no authorization could.**

**All three throw families remain UNQUALIFIED pending adequate evidence.** This plan selects none
of them. It specifies a construction.

---

# 1. THE TARGET FOOTING

## 1.1 What "B's footing" means, disambiguated — three different things wear the word

| sense | the object | is it what "B's footing" means here? |
|---|---|---|
| **(a) the block-sum footing constant** | `√Tr = 4.357790406860002e-38`, byte-identical between G and X, *"the footing every arm is matched on"* (SPEC §1.1) | **no** — it is not B-specific, and §3 preserves it by a different route |
| **(b) the throw ENSEMBLE basis** | the `bank_uthrow_5d` universe bank; **160** throws; the J28-correct per-universe flux normalization; the knob/flux block decomposition | **YES. This is the sense used.** |
| **(c) the central/mask footing** | `footing.mask_sha256` / `footing.row_order_sha256` off `products/5d/xsec_5d_MEFHC_5iter_lgbm.root` | **no** — already resolved, `Z_BUILD_PACKET.md` §1a |

**Adopting sense (b) is adopting a construction basis. It is not reading B's bytes.** The
distinction is the whole of §1.3 and it is what keeps this plan inside Joseph's standing
instruction not to re-stamp archived slabs.

## 1.2 The basis, measured rather than described

Measured on the cluster 2026-09-10, `login09`, under
`/pscratch/sd/j/josephrb/MINERvA-OmniFold/nd-unfolding`:

| object | measurement |
|---|---|
| `bank_uthrow_5d` | **374 entries, mtime `2026-06-30 06:17:33`** — `cv.npz` 2.94 GB, per-knob `sig_*.npy`, `flux_univ_ratio.npy` |
| `uq_5d/rescaled_20260806_full160` | **70 entries**, mtime `2026-08-06 17:43:07`; 40 throw slabs, **per-knob** `block5d_knob_<name>.npz`, per-tile `block5d_flux_*.npz`, and the two adopted ROOTs |
| `uq_5d/union_20260806_full160` | **40 entries, every one a SYMLINK** into `rescaled_20260806_full160` |
| **B** `unified_throw_cov_5d_fluxfix_20260806_full160.root` | `2,668,021,041` B, `2026-08-06 17:38` |
| throw count | `n_throws_union = 160` over `n_files = 40`, contiguous `0…159` (`receipt_construction_contract_5d.json`, `slab_census.throw_slabs_sb`) |

**`union_…` is a symlink view, not a second slab set.** `PROVENANCE-20260822` already records why
its census reads `120`: 30 flux-rescaled slabs plus 10 already-normalized, under a directory named
`full160`. **Nothing in the recommended path reads either directory.**

## 1.3 What adopting it PRESERVES, and what it CHANGES, against Z's approved contract

**PRESERVES — and each of these is why the footing is the right one:**

1. **It is the basis G's own inflation was derived from.** SPEC §1.1 records
   `G.uthrow_source = unified_throw_cov_5d_fluxfix_20260806_full160.root` — that is B — and adds
   *"Z derives its own."* Z's throw being derived from the **same ensemble basis** is what keeps
   `C_Z − C_G` a difference in the seven causes rather than a difference in the throw ensemble as
   well. **G is the `M`-leg comparison baseline for all seven of Z's cells**; a throw on a
   different basis makes every one of those comparisons carry an uncontrolled second term.
2. **It is post-J28 on both sides.** The one property that separates it from the July object.
3. **It entangles nothing behind Gate 2** — the bank predates the k=0 rehearsal by two months
   (§2.3).
4. **`C_stat` and `C_ML` reuse preserves the block-sum footing constant** by a separate and
   already-measured route: `Z_BUILD_PACKET.md` §7.1 measures the residual of
   `hCov_combined5d_total − (universe + stat + mlsplit)` at **exactly 0.0** on the diagonal and
   the first off-diagonal for all 10,694 rows, and √Tr at the constant above. Sense (a) is
   preserved without reading B.

**CHANGES — three, and each needs a ruling (§6):**

1. **SPEC §1.1 gains a row it does not have.** The table names `G.uthrow_source`; it does **not**
   name Z's throw footing, because rev. 1–21 assumed Z would derive its own without saying from
   what. Declaring the basis is an **addition** to the artifact-identity contract, not an override
   of it — but §1.1 is the contract, so it is Joseph's.
2. **The seed-role contract changes relative to B.** B's slabs carry the pre-split ambiguous
   `seed`; Z's fresh slabs carry `estimator_seed` **and** `draw_seed` separately. **This is the
   point, not a side effect** — SPEC §3.2's `(3, Z)` cell requires both stamped at **both** legs,
   and `unified_throw_cov.py:496` refuses a combine over pre-split slabs outright. Z's throw is on
   B's *ensemble* basis under the *post-split* seed contract.
3. **⚠ THE BLOCK DECOMPOSITION IS NOT THE SAME, AND THIS IS NEWLY MEASURED.** B's block slabs are
   written **per knob** — `block5d_knob_2p2h.npz`, `block5d_knob_CCQEPauliSupViaKF.npz`, … — for
   **36** files. Today's arm 6 (`sbatch_uthrow_block_5d.sh:339-346`) writes **one** combined
   `block5d_knobs.npz` under `--block-knobs all`, plus per-tile flux files, for **21**. Measured
   on disk: `mii/member_k000000/uq_5d/block_slabs_5d_sb` **= 21**.
   **What follows and what does not.** It follows that reproducing B's throw ensemble under
   current code does **not** reproduce B's block-slab granularity. It does **not** follow that
   `C_blocksum` differs numerically — a partition summed at two granularities may agree — and
   **this plan has not measured that in either direction.** It is listed as a ruling because a
   footing declaration that is silent on it would be a definite description doing a citation's
   work.

## 1.4 Adopting the footing versus consuming B's artifacts — the operational difference

| | **adopt the footing (recommended)** | **consume B (not recommended)** |
|---|---|---|
| what is read | `bank_uthrow_5d` (2026-06-30) | `unified_throw_cov_5d_fluxfix_20260806_full160.root` |
| what is written | fresh throw slabs, block slabs, one throw ROOT, **one null-operand file** | nothing |
| `:496` seed refusal | **passes** — fresh slabs stamp both roles | **refuses** — B's slabs are pre-split |
| SPEC `11b` (null reconstructible) | **satisfiable** — the writer persists the operands in the same execution | **unsatisfiable** — B has none and no retrofit can be *"at throw creation"* |
| §3.3 condition 10 (revision pinned, closure bound) | **satisfiable** — a scheduled job under a committed revision | **not established** for B |
| archived slabs touched | **none** | none |
| cost | §5 | ~0 |

**The recommendation is the left column.** B is the *basis*; B's bytes are not an input.

---

# 2. THE GATE-2 RESTRICTION — exact scope, and a permitted path

## 2.1 The clause, quoted rather than summarized

`REVIEW-CONTRACT-20260822-k0-execution-integrity.md` §7.0.6, re-read at `a65e23a6`
(`:637`, restated `:1340`):

> **"Until Gate 2 passes, the rehearsal's products stay where they land: not adopted, not consumed
> by anything outside the seven rehearsal jobs, not quoted, and no further member is authorized.**
> Consumption *within* the rehearsal is the rehearsal — leg 4 depending on leg 3 is the dependency
> graph, not an adoption — and is not what this restricts."

And `DECISION-20260830-joseph-mii-family-and-leg6.md`, which is the record that binds it to an
authorization Joseph gave:

> **"The gate, not the family authorization, is the binding constraint, and no authorization from
> Joseph removes it — only the rehearsal work landing does."**

**That sentence is already on `main` and it is not this lane's drafting of a limit on Joseph.** It
is the recorded consequence of `§7.0.6`'s own model — *"a PASS unlocks exactly one thing"* — and
`:1340`'s four explicit negations say the same for the M(ii) ruling: it does **not** authorize
adoption, does **not** authorize consumption, does **not** authorize a member k≠0, does **not**
relax any other Gate-2 clause. **This plan therefore asks for no waiver and treats none as
available.**

## 2.2 The scope, decomposed — the clause has FOUR prohibitions and they are not one

| # | prohibited | subject | does the recommended path do it? |
|---|---|---|---|
| 1 | **adoption** | the rehearsal's products | **no** — nothing here adopts anything |
| 2 | **consumption outside the seven rehearsal jobs** | the rehearsal's products | **no** — §2.3 measures it |
| 3 | **quoting** | the rehearsal's products | **no** — no value from `mii/member_k000000/` appears in this plan |
| 4 | **a further member** | the M(ii) member scan | **a reading is required — §2.4** |

**The subject of prohibitions 1–3 is *the rehearsal's products*.** A production that neither reads
nor writes them is not addressed by those three clauses at all. That is a scope statement about the
clause, not a permission derived from it.

## 2.3 Prohibition 2, measured — what the recommended path actually reads

`sbatch_uthrow_run_5d_fast.sh:318` (arm 5), `sbatch_uthrow_block_5d.sh:340,345` (arm 6) and
`sbatch_uthrow_combine_5d_fast.sh:339` (arm 7) each pass **`--bank bank_uthrow_5d`**, and arm 7
reads the throw and block slabs from `mr_dir_prefix uq_5d/uthrow_slabs_5d_sb` and
`…/block_slabs_5d_sb` — i.e. **from its own run's output prefix**.

| directory | mtime (measured 2026-09-10) | rehearsal product? |
|---|---|---|
| `bank_uthrow_5d` | **2026-06-30 06:17:33** | **no** — two months before the rehearsal |
| `uq_5d/uthrow_slabs_5d_sb` | 2026-08-06 17:11:33 | no |
| `uq_5d/block_slabs_5d_sb` | 2026-07-13 01:50:57 | no |
| `mii/member_k000000/uq_5d/uthrow_slabs_5d_sb` | 2026-09-01 01:09:42 | **YES** |
| `mii/member_k000000/uq_5d/block_slabs_5d_sb` | 2026-08-31 14:57:16 | **YES** |

**So a fresh throw round reads exactly one thing — a June-30 universe bank — and writes only its
own slabs.** It consumes **no** rehearsal product. Prohibitions 1, 2 and 3 are not engaged, and
they are not engaged as a matter of what the job reads, not as a matter of interpretation.

## 2.4 Prohibition 4 — the one that needs Joseph's reading, stated as a question and not answered

**Is a Z throw round "a further member"?** The honest position is that this plan cannot settle it,
and here is exactly what is and is not established.

- **Against.** *Member* in this campaign names an index of the **M(ii) estimator-seed scan** —
  `MNV_EST_SEED_OFFSET` selects it and `lib_member_resume.sh:80` derives `member_kNNNNNN` from it.
  `DECISION-20260830` withholds *"the M(ii) member scan as a family"* at 46/50 and sequences
  *"Gate 2 PASS → leg 6 on k=0 → one member verified end-to-end → family launch."* A Z throw at
  offset `0` adds no new index to that scan and advances no leg of it.
- **For.** A Z throw round runs the **same three arms, on the same bank, at the same estimator
  seed** as the k=0 rehearsal's arms 5–7. It is not a *different* computation; it is the *same*
  computation re-executed under a changed writer into a different namespace.
- **What settles it is a purpose test, and only Joseph can apply it.** Gate 2 exists to verify the
  rehearsal's **execution integrity**. A fresh round under a committed revision with a bound
  import closure does not inherit the unverified provenance the gate is quarantining — it is the
  thing the gate is protecting, produced properly. **But "I can re-derive the restricted object
  independently" is exactly the sentence an end-run would also produce**, and the difference is
  whether the fresh product's provenance is genuinely independent. This plan states the tension
  rather than resolving it in its own favour.

**⚠ §2.6 SUPERSEDES THIS SECTION'S FRAMING.** §2.4 put the question as a bare reading and offered
Joseph no recommendation, which is not what he asked for. §2.6 gives one, and it is built on **what
the rehearsal actually failed** rather than on where a job writes.

## 2.5 ⚠ THE NAMESPACE HAZARD, and it is a real one measured today

`lib_member_resume.sh:72-73` — `mr_member_dir` returns **the empty string when
`MNV_EST_SEED_OFFSET` is unset** (`:73`, measured), so an undeclared-offset run writes to the **canonical base**
namespaces. Measured consequences:

- `uq_5d/uthrow_slabs_5d_sb` already holds **40 slabs from 2026-08-06** — an undeclared arm 5
  overwrites them.
- `uq_5d/block_slabs_5d_sb` holds **41 files from 2026-07-13** — same for arm 6.
- `mr_prefix uq_5d/unified_throw_cov_5d.root` with no offset resolves to **family A's path**, and
  arm 7 would overwrite A in place.

And declaring an offset puts the output under `MII_CONTAINER` (`lib_member_resume.sh:84`, default
`mii`) — i.e. into the very namespace prohibition 4 governs.

**`MII_CONTAINER` is overridable** (`${MII_CONTAINER:-mii}`), so a Z-scoped container is available
without a code change. **Any authorization must name the container explicitly**; leaving it to a
default is how an archive gets overwritten by an omitted variable, and this repository has already
recorded that shape once in `adopt_unified_5d.py:76`'s defaulted `--uthrow`.

**⚠ AND A NEW NAMESPACE IS NOT INDEPENDENCE.** It prevents a collision. It establishes nothing about
provenance, and §2.6 does not rest on it.

## 2.6 THE RECOMMENDED SCOPE RULING — built on what Gate 2 actually found

### 2.6a What failed, quoted from the verdict

`VERDICT-20260825-gate2-k0-rehearsal-nine-clauses.md`: **six of nine clauses PASS; three do not**,
and §F's no-partial-credit rule makes any one a FAIL.

| clause | requirement | why it failed |
|---|---|---|
| **F-7(b)** | *"the sets are recorded from the rehearsal and pinned"* | **No expected-set pin taken from this rehearsal exists anywhere in the repository, on any ref.** The far-end instrument does not produce one. Its own header records the adjacent gap: *"F-7(b) has no exclusion instrument — nothing mechanically enforces the exclusion the clause asserts, so it is satisfied by convention only."* The verdict: *"cheap to fix and it must not be graded as satisfied by convention."* |
| **F-8(b)** | *"the receipt states the blind spots in the receipt's own words"* | **No run receipt for this rehearsal has been authored.** Every committed blind-spot document is pre-submission material dated 2026-08-22/23. *"A receipt that predates the run cannot state the run's blind spots."* |
| **F-17(b)** | M-1…M-6 *"re-measured again after the path runs"*, differences reported | **Half performed, half IMPOSSIBLE.** The comparator reproduced bit for bit — 72 fields, **32 findings, still unexplained**. The second obligation cannot be performed because §7.0.6 unlocks only legs 1–5 |

**The purposes, stated as purposes rather than as clause numbers, because that is what a scope
ruling has to test against:** (F-7) *the run declares what it should produce, and the declaration is
committed*; (F-8) *the producing execution self-reports what it could not see, after it ran*;
(F-17) *the execution environment is verified unchanged across the run, and drift is disclosed.*

**None of the three is about the arithmetic.** All three are about whether the run's own account of
itself is trustworthy. That is what the quarantine protects, and it is the right test to apply.

### 2.6b Does the proposed independent Z path satisfy those purposes?

**Not by construction, and not by living in a different directory.** Measured against the three
purposes, a fresh Z round as specified in §§3–5 satisfies **none of them automatically**:

| purpose | does §§3–5 as written satisfy it? |
|---|---|
| F-7 — a committed expected-set pin taken from the run | **NO.** Nothing in §3 records one, and the instrument that would produce it **does not exist** — the same absence that failed the rehearsal |
| F-8 — a post-run receipt stating blind spots in its own words | **PARTLY.** §3.4 binds objects to the job; it does **not** oblige a blind-spot statement, and §1.5's schema is *"written LAST"* but does not carry one |
| F-17 — far-end re-measurement of M-1…M-6, drift disclosed | **NO.** §3 does not require it |

**So the honest answer is that the Z path as drafted would reproduce two of the three failures.**
Identical kernels in a clean namespace is precisely the configuration that *looks* independent and
is not. **The remedy is not to argue the path is different; it is to make the path carry the
requirements.**

### 2.6c THE RULING I RECOMMEND

> **Gate 2's restriction is scoped to (a) the rehearsal's PRODUCTS and (b) the M(ii) member axis.**
> A production that reads no rehearsal product and adds no index to the M(ii) scan is **outside
> prohibitions 1–3 and is not a "further member" under prohibition 4** — *provided it discharges,
> for itself and before any product of it is read by anything, the three integrity requirements the
> rehearsal failed:*
>
> 1. **F-7-equivalent** — an expected-set pin **recorded from the Z run and committed**, with the
>    instrument that produces it landed first. Satisfaction by convention is refused.
> 2. **F-8-equivalent** — a **post-run** receipt stating the run's blind spots in its own words,
>    authored after the far end. A pre-submission document does not satisfy it.
> 3. **F-17-equivalent** — M-1…M-6 re-measured **after** the Z path runs, every difference reported
>    as a finding.
>
> **This waives nothing.** Gate 2 stays FAIL; the rehearsal's products stay unadopted, unconsumed,
> unquoted; leg 6 and the M(ii) family stay sequenced behind it. The three conditions make the Z
> path **harder** than the rehearsal was, which is the only ground on which its provenance can be
> called independent.

**Why this shape and not a waiver.** `DECISION-20260830` is explicit that *"no authorization from
Joseph removes it — only the rehearsal work landing does."* The ruling above does not remove the
gate; it **scopes** it, and then transplants the unmet obligations onto the new path so that
nothing the gate protects is lost. **A ruling that let Z proceed without conditions 1–3 would be a
waiver wearing a scope argument.**

### 2.6d CONSEQUENCES OF EACH BRANCH — including the one that makes refusal expensive

**If GRANTED, with conditions.** Z's throw may be authorized (§7). Additional work created by the
conditions: the F-7 pin instrument (**code, does not exist**), a post-run receipt obligation added
to §1.5's schema (**code**), and the F-17 far-end re-measurement (**the comparator already exists**
— `measure_m1_m6.py` / `compare_m1_m6.py`, reproduced bit-for-bit by the grader). **No compute
beyond §7's ask.** Gate 2, leg 6 and the M(ii) family are untouched.

**If REFUSED — and this is the consequence that is easy to miss.** *"Z's throw waits for Gate 2"*
does **not** mean waiting for a paperwork repair. **F-17(b) is impossible for the current rehearsal
by construction** — the verdict says so and `DECISION-20260830` records the consequence: *"a new
forward-only rehearsal is required because F-17(b) is impossible for the current one by
construction."* So refusal means Z waits on **a complete new seven-arm rehearsal round** —
`70` GPU / `113` CPU at ratified ceilings — **and then the Z throw round on top of it**, inside a
usable window of `6 d 06 h` + `6 d 11 h`.

**The comparison, stated so the trade is visible and not so it argues for one side:** granting costs
`110` CPU / `0` GPU plus two code items; refusing costs `70` GPU / `113` CPU **plus** the same
`110` CPU afterwards, and two sequential rounds inside two sub-7-day blocks. **Refusal may still be
right** — if the purposes cannot be discharged on a path nobody has graded, cost does not settle
it. **That judgement is Joseph's and this plan does not make it.**

---

# 3. THE MINIMUM FRESH PRODUCTION

## 3.1 The split — what may be reused, what must be new, and why for each

| input | disposition | ground |
|---|---|---|
| `parent` — G `4f168e83…` | **REUSE** | it is the comparison baseline, not an operand (SPEC §1.1) |
| `central` — `630306e20e4e…` | **REUSE** | Z holds the central value fixed (SPEC §1.3); the 5D central values are `VALIDATED` |
| `support` — CS `9f7b2f55d758…` | **REUSE** | the band family Z reads; digest bound in G's own build receipt |
| `active` — S `950f8cb15c5a…` | **REUSE** | component donor only, each band re-digested into Z's receipt (SPEC §1.1) |
| `stat` — `6580016fa713…` | **REUSE, provisionally suitable** | §3.2 |
| `ml` — `27b2e456f80e…` | **REUSE, provisionally suitable** | §3.2 |
| `footing.mask/row_order` | **REUSE, recomputed** | derived from `central`, `Z_BUILD_PACKET.md` §1a; not read from G, and tagged so |
| **`throw` matrices** | **MUST BE NEW** | §3.3 |
| **null operands** | **MUST BE NEW** | §3.3 — they have never existed |
| **provenance** | **MUST BE NEW** | §3.4 |

## 3.2 `stat` and `ml` — reuse is recommended, and the recommendation is PROVISIONAL

The measurement in `Z_BUILD_PACKET.md` §7.1 inverted the concern that prompted it: reuse
**preserves** the footing G's `M` legs are measured against, and regeneration is the move that
would introduce a footing difference. Three disclosures ride with reuse and **regeneration fixes
none of them** — the mixed `1/(N−1)` vs `1/N` normalization (`OI-137`, ruled *disclose, do not
correct* 2026-08-22), `C_stat`'s 18,979 zero entries inside the reported mask, and the two-epoch
ensemble.

**Provisional, and the word is doing work.** Six things remain before reuse can support an
*adopted* product, and none is unblocked by this plan: `(cause 6, Z)`'s reuse-vs-regenerate
decision *"made with a stated rationale"* (SPEC §3.2), whether `(6, Z)` is graded on `6a` as well
as `6b` (§6.6), the thin producing provenance (no stamps in either ROOT, **0 of 346** `RUNS.tsv`
rows against a positive control, no producing receipt), the support-flicker disclosure being new
for the scalar-5D object, and the two `C`/`T` legs of `(6, Z)`. **Reuse is the recommended input;
it is not a discharged cause.**

**The decision lives upstream of the driver.** `z_build.py:558-559` reads an `(n, n)` matrix and
applies **no** provenance constraint, so a regenerated `C_stat` at a new path is consumed
identically. Requiring a *file* says nothing about that file's *provenance*, and the architecture
forecloses neither branch.

## 3.3 The throw matrices and the null operands — why nothing existing can serve

**The null operands have never been produced by any execution.** Re-read at `a65e23a6`:

- `unified_throw_cov.py:369` computes the full-grid `x_cv`; `:370` derives `rep = x_cv > 0`;
  `:371` derives `base = x_cv[rep]`.
- `:514-515` computes `x_cv2` **already masked** — `_xsec_for_weights(...).ravel(order="C")[rep]`.
- `:582-598` returns `x_cv_reported: base` **in a dict**. Nothing writes it. The vector, the
  re-unfold and the predicate all die with the process.
- A `find` over the whole data root returns **2,429** `.npz` files and the only matches are PET
  artifacts off the publication path.

**This is a writer gap, not a lost file**, which is why no retrofit onto an existing ROOT can
satisfy `REQUIREMENTS["null"]`'s *"at throw creation"* or SPEC §3.3 condition `11b`. It is also
why the throw matrices must be new: `11b` and item 4 require the operands and the matrices to come
from **one execution**, and no execution has ever produced both.

**Two Tier-2 code changes, and the receiving function already exists.**
`z_receipt.persist_null_operands` is at `z_receipt.py:259` and `z_build.py:616-618` already calls it.
What is missing is the *producer* side:

1. Hoist the `[rep]` off `:514-515` so the full-grid `x_cv2` exists before masking.
2. Inside the `if args.null:` block, call `persist_null_operands(path, x_cv, x_cv2, rep,
   code_identity=…)` in the same execution, before the norm is taken.

**Code, not compute** — `1.05` MB of product against a `2.668` GB throw ROOT (`3.9e-4`), and both
edits are inside the arm the run already executes. **⚠ And `persist_null_operands` records no seed,
bank or run id today**, so a standalone slab and a genuine in-producer one are byte-indistinguishable
after the fact; the run-binding of §3.4 is what closes that, and it is part of the change.

## 3.4 The binding — each object bound to its actual producing execution

**This is the requirement §3.3 condition 10 states and that no existing family satisfies.** For
the prospective construction, each object below is bound by the record named beside it, written by
the job that produced it:

| object | bound to | by what |
|---|---|---|
| **throw matrices** `C_unified`, `C_blocksum`, `C_cross`, `hJointMeanShift` | the arm-7 job id, its `estimator_seed`/`draw_seed`, `est_seed_offset{,_declared}`, and the arm-5/6 slab digests it combined | the ROOT stamps already written at `unified_throw_cov.py:565-579`, plus a slab-digest inventory the receipt must add |
| **null operands** `x_cv`, `x_cv2`, `rep` | **the same arm-7 job id and the same in-process CV unfold** | `persist_null_operands`, extended per §3.3 to carry seed, bank and run id |
| **central vector** | `products/5d/xsec_5d_MEFHC_5iter_lgbm.root`, `630306e20e4e…`, digest recorded at open time | Z's receipt, §1.5 open-time stamping |
| **mask / row order** | the **central**, not G — `footing.mask_sha256 = eed021e9…`, `footing.row_order_sha256 = 61a7c9fd…`, tagged `row_order_basis: reconstructed from declared production CV; NOT read_from_G` | `z_build` writes the tag into every receipt |
| **producing revision** | the executing checkout's `HEAD`, enforced equal by `z_build.py:260-266` | committed sha + import-closure digests |

**⚠ ONE BINDING THIS PLAN DOES NOT CLOSE, named so it is not read as closed.** `PM-4`: G's build
receipt binds four files and **not** its production-CV input, so *"G consumed those bytes"* is not
established. `footing.*` is therefore **self-consistency with Z's own declared central**, not
evidence about G — swap the central and rewrite both digests and the gate still passes. Closing it
needs a committed record binding G's `--prod` input by digest at build time, or a re-run under a
receipt that does. **It is `PM-4`'s owner's to amend, and this plan neither closes it nor works
around it.**

---

# 4. THE ESTIMATOR CONFIGURATION

## 4.1 What route (i) is, and what the estimator does today

SPEC §3.7a names three routes to the operating-error bound `B` and privileges none.
**Route (i)** is *"pin the envelope in code, and make `B` a design property rather than a
measurement"* — **Tier 2, code, no compute**.

Re-read at `a65e23a6`: `make_estimators` (`omnifold_nn_core.py:143-148`) constructs
`LGBMClassifier(n_estimators=100, num_leaves=8, learning_rate=0.1, verbose=-1)` plus
`random_state`, and `LGBMRegressor` from the same dict. **Those four keyword arguments are still
the complete set.** Nothing pins thread count, reduction order, or histogram construction, so —
as SPEC §3.7a puts it — *"thread count and reduction order are properties of the allocation, not
of the seed."* The module's own docstring (`:203-204`) says LightGBM at these settings is
*"**nearly** deterministic in `seed` alone"*; the word is the author's. G's committed null is
`5.8223488501140625e-50`, **not zero**, which agrees.

## 4.2 What was measured today, and what it does not show

Measured in the environment the arms run under —
`/global/u2/j/josephrb/.conda/envs/root_6_28`, **Python 3.11.14, lightgbm 4.6.0** — full detail at
`Z_BUILD_PACKET.md` §8d:

- `num_threads`, `deterministic`, `force_row_wise`, `force_col_wise` are **not explicit
  parameters** of `LGBMClassifier.__init__`, but the signature accepts `**kwargs`, so they reach
  the core. `n_jobs` and `random_state` are explicit.
- On **400×4 synthetic normal data** — not an analysis input, not the pipeline, not a scheduled
  job — all three configurations are **accepted**; `deterministic=True` alone does not require a
  companion flag at 4.6.0; the pinned configuration is bit-identical across repeats and
  **bit-identical to the current configuration on that set**.

**⚠ What this does NOT show.** It does not show that pinning leaves `x_cv` unchanged on the real
problem. A 400-row fit at effectively one thread does not exercise the mechanism §3.7a names.
**The direction and magnitude of any change on the 5D bank are UNMEASURED.** What it does show is
that route (i) is implementable at the installed version without a dependency change.

**And the earlier packet claim is withdrawn.** `Z_BUILD_PACKET.md` §7.3 asserted route (i)
*"changes `x_cv` itself, and therefore the support mask, `nrep`, and every downstream covariance."*
That was an assertion about an output that nobody had measured. On the one comparison anyone has
now run, it changed nothing — which is equally not evidence about the 5D bank.

## 4.3 Route (i)'s consequences, separated into the two that differ in kind

**(a) The consequence that holds whatever the numbers do — and it is the one that governs.**
Pinning changes the **declared execution configuration**. §6.4 requires the fixed-seed null bound
to be *"scale-relative and fixed before production"*, with its value justified by controls
established **before** implementation. A bound argued from a configuration cannot be fixed before
that configuration is chosen. **So route (i) is decided before the operands are produced, and this
ordering does not depend on measuring anything.** SPEC §3.3 condition `4c` makes the point sharply:
running against a bound §3.6 still lists as incomplete is a **reject condition**, not a caveat.

**(b) The consequence that is an open empirical question.** Whether pinning moves `x_cv`, and by
how much. If it moves it, the support mask, `nrep` and every downstream covariance move with it,
and operands produced under the unpinned envelope are superseded. If it does not, nothing
downstream moves. **Both branches are live and this plan asserts neither.**

## 4.4 The recommendation

**Adopt route (i), pin before production, and buy the measurement of (b) for ≤ 0.58 CPU task-h.**

**⚠ CORRECTED 2026-09-10 — THE EARLIER FORM WOULD HAVE CHANGED EVERY NON-Z CALLER.** It gave the
settings as a replacement for `make_estimators`' `d = dict(...)`, i.e. as a new **default**.
`make_estimators` is shared: the 4D and FPS chains, the PET path and every historical reproduction
call it. **Silently re-pinning the estimator underneath them would change numerics campaign-wide for
objects that are not Z's and are not in question** — and several of them are quoted.

**The change must be Z-SCOPED AND OPT-IN, with existing defaults preserved byte for byte:**

```
def make_estimators(kind, nvars, seed=None, *, pin_envelope=False):
    ...
    d = dict(n_estimators=100, num_leaves=8, learning_rate=0.1, verbose=-1)
    if pin_envelope:                       # Z only; every existing caller keeps today's numerics
        d = dict(d, n_jobs=1, deterministic=True, force_row_wise=True)
    if seed is not None:
        d = dict(d, random_state=int(seed))
```

**`pin_envelope=False` is the default and no existing call site passes it**, so every non-Z product
is bit-unchanged and that invariance is itself testable — a `T`-leg control should assert it rather
than assume it. The flag is threaded from Z's launchers only. Three reasons for the settings:

1. **It is the only route that reduces the quantity instead of measuring it**, it costs no
   compute, and it addresses Gap 1 at the source — *an envelope that is pinned has no
   between-envelope shift to bound.*
2. **`n_jobs=1` is the conservative choice and it has a cost.** Single-threading the estimator
   removes the allocation-dependence that is the suspected source of the non-determinism, and
   **it will make each unfold slower by an unmeasured factor.** Arm 5's tasks request
   `--cpus-per-task=32`; how much of that the estimator currently uses is not measured here, so
   **§5 carries this as an explicit contingency and not as a priced line.** If Joseph prefers to
   keep threading, `deterministic=True, force_row_wise=True` with `n_jobs` left as-is is the
   weaker but cheaper variant — and its determinism claim would then be unsupported, because
   `deterministic`'s guarantee across differing thread counts is a LightGBM documentation claim
   this plan has **not** verified against 4.6.0.
3. **It makes `B` arguable rather than sampled**, which is what `D4` has been waiting on.

**⚠ THIS IS A CONFIGURATION TO VALIDATE, NOT A BOUND.** Route (i) supplies a *route* to `B`.
`D4` still needs `S`, still needs `B ≤ S`, and still needs `ε` argued within `[B, S]` —
**`ε = n_iters · n_rep · eps` and the number `1.1873e-11` remain WITHHELD** and must not be cited.
Pinning the envelope does not fix the boundary; it makes fixing it possible, **and only if the
evidence below is produced.**

### 4.4a The EXACT evidence a numerical bound would need — none of which exists

**Route (i) makes `B` a design property only if the design is actually pinned and demonstrably
reproducible.** Six items, in dependency order:

1. **Bit-identical repeats of the FULL CV unfold chain**, not of one estimator fit. §4.2's synthetic
   check exercised `LGBMClassifier.fit` alone; the quantity `B` bounds is the reproducibility floor
   of `_xsec_for_weights` end to end.
2. **Those repeats must span DIFFERENT ALLOCATIONS.** The claim route (i) makes is that *"the
   envelope no longer varies with the allocation."* Repeats on one node do not test it — they test
   in-process determinism, which is the easy half.
3. **⚠ THE SURROUNDING NUMERICAL ENVIRONMENT MUST BE PINNED TOO, AND TODAY IT IS NOT — MEASURED.**
   `sbatch_uthrow_run_5d_fast.sh:122-123` exports
   `OMP_NUM_THREADS=32 MKL_NUM_THREADS=2 OPENBLAS_NUM_THREADS=2 NUMEXPR_NUM_THREADS=2
   VECLIB_MAXIMUM_THREADS=2`. **`sbatch_uthrow_block_5d.sh` and `sbatch_uthrow_combine_5d_fast.sh`
   export NONE of them** — grepped, and the only `export` lines are `PYTHONUNBUFFERED` and
   `PYTHONDONTWRITEBYTECODE`. **Arm 7 is where `--null` computes `x_cv` and `x_cv2`.** So the arm
   that produces the null operands runs with an unpinned thread environment, which is exactly the
   mechanism §3.7a names. **A bound argued from "the configuration is pinned" must enumerate every
   source of run-to-run variation it pins — pinning the classifier while leaving OMP free in the
   arm that computes the null would be a bound over a configuration that is not fixed.**
4. **A PREDECLARED estimator of `B`** — §3.7a Gap 3: two arms do not prevent tuning.
5. **A coverage/confidence objective for the repeat count** — §3.7a Gap 2: *"4 repeats had no
   justification."*
6. **`S` argued independently, and `B ≤ S` demonstrated.** Note §3.7a's rev.-19 correction: a loose
   `B` above `S` means `B ≤ S` **is not demonstrated**, which is a statement about the *evidence*;
   it is not the same as *"the envelope is inadequate"*, which is a statement about the world.

**If item 1 or 2 fails — the pinned chain is not bit-identical — route (i) does not deliver a design
property at all**, `B` reverts to a measured quantity, and route (ii)'s three gaps reopen in full.
**§5.9's pilot tests the cheapest corner of this** (throw-side, one node) and settles none of it.

## 4.5 The cheap measurement of (b), designed in rather than bolted on

Run **arm 7 twice on the same fresh slabs** — once under the pinned configuration, once unpinned —
and compare the two persisted `x_cv` vectors elementwise. Because the operands are persisted
(§3.3), the comparison is a file diff after the fact rather than an instrumented run.

- **Marginal cost: one additional arm-7 invocation**, measured at `0.3875` / `0.4239` / `0.5764`
  CPU task-h across three historical `uthrow5d_combF` runs — **≤ 0.58 CPU task-h**, ratified arm-7
  ceiling `5`.
- **What it measures:** the CV-unfold's sensitivity to the envelope, which is exactly the quantity
  the null bound is about.
- **What it does NOT measure:** the effect of pinning on the **throws** themselves. Arm 5 runs an
  unfold per throw, so a fully-pinned production pins arms 5 and 6 too, and this diagnostic holds
  the slabs fixed. **Measuring the throw-side effect would need a second ensemble and is not
  proposed.**

---

# 5. THE COMPLETE PATH TO A DECISION, COSTED

**Evidence classes are SPEC §5.8's four and they are the point of this section.** **MEASURED** — a
number produced here with the machine or `file:line` named. **TRANSFERRED** — measured on a
different subject or hardware; **direction not established**. **DERIVED** — arithmetic on those.
**UNRESOLVED** — no figure, with the act that would produce one.

## 5.1 Current `R5` spend — RE-MEASURED TODAY, and the measurement moved the wrong way

| | receipt | re-measurement |
|---|---|---|
| when / where | `2026-09-09T19:38:19Z`, `login36` | **`2026-09-10T06:58:37Z`**, dump from `login09` |
| argv | identical, byte for byte | identical |
| **GPU task-h** | `0.0` | **`0.0`** |
| **CPU task-h** | `14.9756` | **`14.4897`** |
| attempts | `1888` (waker `57712764`: `1884`) | **`1826`** (waker: **`1822`**) |
| headroom CPU | `485.02` | **`485.51`** |

**⚠ THIS SECTION'S FRAMING IS CORRECTED — SEE
`docs/orchestration/FINDING-20260910-r5-attempt-identity-is-not-stable-across-queries.md`.** It
reported the difference as attempts going missing. **They were not shown to be missing.** Measured
on one job over one span, the two captures agree to `≈2%` on both count and elapsed while sharing
only **8** of `≈1,160` attempt identities — the `(JobID, Start, End)` key is **not stable across
queries**, so a set difference measures the key rather than the population. **The `62` is an
artifact of the key.**

**The accounting rule that follows, and this plan uses it:** carry the **MAXIMUM observed** spend,
never the latest — **`14.9756` CPU task-h, `0.0` GPU, headroom `≤ 485.02` CPU`. A re-query returning
a lower number does not release budget, and captures are never summed. The raw rows of the 09-09
capture were not retained (digest only); today's are preserved at
`docs/orchestration/state/r5-capture-20260910/`.

**The original observations, kept because they are the evidence:**

- **Not query noise.** Three consecutive repetitions today return `1827` rows each.
- **Not the moving `now`.** The same query with `--endtime 2026-09-09T19:38:19` — the receipt's own
  instant — returns **`1827`** today.
- **Not new work.** The waker's last attempt ended `2026-09-09T07:39:30`, twelve hours *before* the
  receipt; job `57712764` is now `CANCELLED` and `squeue -u josephrb` returns **no rows**.
- The `62`-attempt difference at `≈28.2` s each accounts for the `0.4858` h exactly — **which is
  consistent with the unstable-key explanation and does not favour a loss explanation.**

**The mechanism is NOT established and none is asserted here.** The finding record states what is
and is not supported, and it is filed to the meter's owner rather than adjudicated here —
**accounting repair is kept separate from scientific scope, and nothing in it changes any Z
decision.**

**Neither ceiling is close to binding under either reading.** GPU `0.0 / 500`; CPU `14.98 / 500` on
the conservative figure. **The constraint on this campaign is the date and the open decisions, not
the task-hours** — which is why adopting the conservative rule costs nothing.

## 5.2 Production — one Z throw on the recommended footing

| arm | R1 actual | R2 actual | **ratified ceiling** | class |
|---|---:|---:|---:|---|
| 5 `uthrow5d_runF` (40 tasks) | `30.94` | `49.11` | **`60` CPU** | **TRANSFERRED** — `AMENDMENT-20260831-oi177` §3d/§5 |
| 6 `uthrow5d_block` (21 tasks) | `30.01` | `31.01` | **`40` CPU** | same |
| 7 `uthrow5d_combF` (+`--null`) | `0.42` | `0.58` | **`5` CPU** | same |
| **subtotal** | **`61.37`** | **`80.70`** | **`105` CPU / `0` GPU** | |
| route-(i) diagnostic, second arm 7 (§4.5) | — | `0.58` | `5` CPU | **TRANSFERRED** — §5.2a |
| **production total** | | **`≤ 81.28`** | **`110` CPU / `0` GPU** | **`22.0%` of the CPU ceiling** |

### 5.2a ⚠ THESE ARE TRANSFERRED ESTIMATES, NOT MEASURED BOUNDS — CORRECTED 2026-09-10

**Every estimator-bearing figure above was measured under a DIFFERENT estimator configuration than
the one §4 proposes, so none of them bounds a Z arm.** The correction matters because the earlier
revision labelled two of them `MEASURED UPPER BOUND`, and a bound is a much stronger claim than the
evidence supports.

**The subset-of-a-completed-job argument — *"one unfold ≤ the whole job"* — is only valid if the
subset is executed the same way.** Under a changed configuration it does not hold at all, in either
direction.

| row | was labelled | **corrected class** | why |
|---|---|---|---|
| arms 5, 6, 7 | TRANSFERRED | **TRANSFERRED across a CONFIGURATION CHANGE** | measured with LightGBM at `OMP_NUM_THREADS=32`; §4 proposes `n_jobs=1` |
| cause-4 second CV unfold, `0.5764` | **MEASURED UPPER BOUND** | **TRANSFERRED** | it is an estimator-bearing unfold; the historical job ran unpinned |
| route-(i) diagnostic arm 7, `0.58` | **MEASURED UPPER BOUND** | **TRANSFERRED** | same |
| the two assemblies, `0.5231` | **MEASURED UPPER BOUND** | **TRANSFERRED** | `adopt_unified_5d.py` runs **no estimator**, so the configuration does not touch it — but it is still a subset bound taken off a *different job's* four operations on different inputs, and `j28_adopt_5d` ran a J28 rescale Z never runs |
| `eigvalsh`, outer products, replay I/O | DERIVED / MEASURED | **unchanged** | no estimator, and the hardware transfer was already declared |

**⚠ AND THE DIRECTION IS NOT NEUTRAL HERE.** Measured today: `sbatch_uthrow_run_5d_fast.sh:122-123`
exports **`OMP_NUM_THREADS=32`**, so LightGBM currently runs 32-way. `n_jobs=1` would take that to
one thread. **A slowdown is the expected direction and its size is unmeasured**, which is what §5.9
exists to fix. No number in §5.2 should be quoted for the Z configuration until it is.

**Every arm figure remains a prior from a different subject** — no Z arm has ever run — and §5.6
lists what else can move them.

## 5.3 Assembly, validation and independent replay

| item | figure | class |
|---|---:|---|
| the two `adopt_unified_5d.py` assemblies | **`≤ 0.5231`** CPU | **MEASURED UPPER BOUND** — `j28_adopt_5d` `56429334`, `1,883` s, the pair a subset of its four operations |
| `z_build` driver, both variants | **time small; MEMORY UNRESOLVED** | `z_build.py:544-549` holds five active bands **plus** the total — six `10,694²` float64 ≈ **`5.5` GB for `active` alone**, before the lateral sum, two support sums, `cov_stat` and `cov_ml`. **Peak unmeasured** |
| Z's inflated-object validation, both variants | `≈ 0.07` CPU | **DERIVED** on **TRANSFERRED** local timings (`eigvalsh` `113` s at `n=10,694`, extrapolated cubically) |
| cause-1 counterfactual incl. off-diagonal | `≈ 0.03` CPU | **DERIVED**, same basis |
| cause-4 jitter counterfactual — a **second** CV unfold | **`≤ 0.5764`** CPU | **MEASURED UPPER BOUND** — one unfold ≤ the whole `uthrow5d_combF` job |
| **independent ARTIFACT REPLAY** — arithmetic | `≈ 0.07` CPU | **DERIVED** |
| **independent ARTIFACT REPLAY** — I/O | **`≈ 0.017` CPU** (`41.18` GB ÷ `674` MB/s = `61` s) | **DERIVED** on a **MEASURED** pscratch read rate |
| **replay total** | **`≈ 0.09` CPU** | **⚠ this CLOSES SPEC §5.8c's `UNRESOLVED` I/O row**, which said *"the I/O term is the whole question and nobody has measured it."* Measured, it is a minute |

**Sum of the non-production terms: `≤ 1.3` CPU task-h**, of which three entries are upper bounds
and two are hardware transfers. **The binding constraint on this block is memory, not time**, and
the `z_build` peak is the one figure with no number at all.

## 5.4 What is NOT in the totals, listed rather than absorbed

| item | figure | trigger |
|---|---|---|
| standard-P4 lateral stages 3–6 | `0.80` GPU / `0` CPU, **TRANSFERRED** | conditional on `PM-3` passing |
| endpoint rebuild | **unpriced, deliberately** | only if `PM-3`'s availability/provenance/compatibility check **fails** |
| `C_stat`/`C_ML` **regeneration**, if Joseph rules that way | arms 1+2: `14.86` GPU + `5.83` CPU at R2 actuals, `20` + `8` at ceilings — **plus a combine with NO accounting row in any dimension** | §3.2's decision going the other way. **And §7.1's sting: only one `of_inputs_5d.npz` exists with no bkgaware variant**, so a regeneration off it reproduces the same footing and buys nothing |
| `(cause 3, Z)`'s `M(ii)` joint-baseline campaign | **`164.7`–`219.6` GPU / `259.6`–`346.1` CPU** — 3–4 additional members | `D1` approved **and** a design authorized at `N`. **Also behind Gate 2** |
| two independent pre-launch reviews; a grading lane `BEN-381` does not disqualify | **`0` task-h** | they are routing and calendar, not compute |
| cause-1's disclosure; cause-5's path re-trace | **`0` task-h** | a publication act and a static read |

## 5.5 The schedule — RE-DERIVED TODAY, and it has shortened

From `2026-09-10T06:58Z`, against the relayed `maintenance_20260916`
(`2026-09-16T13:00Z → 2026-09-23T13:00Z`, 5,248 nodes, `MAINT,IGNORE_JOBS`):

| span | duration |
|---|---|
| to the `R5` stop `2026-09-30T00:00:00Z` | **`19 d 17 h 02 m`** |
| **block A** — now → outage | **`6 d 06 h 02 m`** |
| the outage | `7 d 00 h 00 m` |
| **block B** — outage → stop | **`6 d 11 h 00 m`** |
| **USABLE SCHEDULING WINDOW** | **`12 d 17 h 02 m`, in two blocks, neither longer than `6.5` days** |

**SPEC §5.9b measured `16 d 14 h 50 m` on 2026-09-06T09:10Z. Four days of elapsed time cost
`3 d 21 h 48 m` of usable window**, because all of it came out of block A. And the meter itself expires: `sacct`
refuses spans over 30 days, `_sacct_argv()` queries `t0 → now`, so **the full `R5` window is
measurable only until `2026-10-02T13:44:27Z`**, after which the live query fails and admission,
being fail-closed, closes.

## 5.6 Contingencies the figures do not carry

1. **The CPU column carries at least a `±60%` single-arm swing** — **MEASURED**: arm 5 went
   `30.94 → 49.11`, `+58.7%`, attributed to on-node contention that *burns* CPU. Arm 5 is one of
   the three arms this plan proposes.
2. **`n_jobs=1` slows every unfold by an unmeasured factor** (§4.4). Arm 5 requests
   `--cpus-per-task=32`; how much of that the estimator uses is not measured here. **This is the
   single largest unpriced risk to §5.2's arm-5 line**, and it is created by the recommendation
   itself.
3. **Failed, cancelled and timed-out tasks count in full** under `R5` §3.
4. **A hold-style dispatch charges to its timeout** — the observed `03:00:03` instance metered
   `3.00` task-hours for `00:47:58` of work. A design hazard, not a price.
5. **Every per-arm figure is a prior from a different subject.** No Z arm has ever run.
6. **The block-granularity difference (§1.3 item 3)** could require a launcher change to reproduce
   B's 36-file decomposition; unpriced, and it is code rather than compute.
7. **The `z_build` memory peak is unmeasured** and the driver is memory-bound.

## 5.7 Is completion before the existing stop credible? — FEASIBILITY and READINESS are different questions

**⚠ Read §5.8 first: it replaces this section's cost conclusion.** What survives here unchanged
is the list of five READINESS items, which are prerequisites with no cost and no schedule.

**A CONSTRUCTED Z: YES, credibly.** `≤ 82.6` CPU task-h of estimated spend against `485.02` of
headroom on the conservative figure (§5.1); `110` CPU / `0` GPU as a reservation, `22.0%` of the ceiling. Wall-clock for the
three arms is a few hours of compute at full concurrency — **but `AMENDMENT` §3c records one arm's
tail running at two-way concurrency on `Reason=Resources` for eleven hours in a single round**, so
plan on days, not hours. One round fits inside block A with margin, and inside block B if it slips.

**A DECIDED Z — an adopted 5D uncertainty product: NO, and not for reasons compute can fix.** Five
of them, each independently sufficient:

1. **`null_epsilon` is WITHHELD and cannot be fixed by production.** It needs an operating-error
   bound `B`, a scientific cap `S`, `B ≤ S` demonstrated, and `ε` argued within `[B, S]`. **None is
   established.** §4.4 supplies a *route* to `B` and nothing more. **SPEC §3.3 condition `4c` makes
   running against an incomplete bound a REJECT condition** — so a Z built now is non-passing *by
   construction*, which is exactly what `Z_BUILD_PACKET.md` §3 already says the driver will report.
2. **Three more boundaries are withheld** — `cause3_agg`, `cause3_med`, `cause3_corr` — and §6.6
   requires the statistic, denominator, precision target and boundary to be approved **together**.
3. **There is no criteria owner.** `owners.tsv` has twelve rows and none is scientific acceptance
   criteria.
4. **Twenty-eight `(cause × leg)` cells are OPEN for Z** and Z inherits nothing from G. They need a
   grading lane that `BEN-381` does not disqualify, and `BEN-381` disqualifies the lane that drafted
   the contract.
5. **⚠ WITHDRAWN AS WRITTEN — see §5.8.** It said `(cause 3, Z)`'s `M(ii)` is *"behind Gate 2 and
   5×–9× over `R5` at the historical design."* The `5×–9×` is the **historical 46/50-member M(ii)
   family**, which §6.3 explicitly does not adopt as Z's design. **Z's own cause-3 design is
   `N = 4`–`5` and it FITS inside `R5`.** Charging Z with another design's size is
   asymmetric comparison, and it inverted the conclusion.

**⚠ CORRECTED 2026-09-10 — "the decision is not affordable" WAS THE WRONG SENTENCE, and it made
the wrong kind of claim.** It priced a *readiness* gap as if it were a *cost*, and it reached its
number by charging Z with the historical M(ii) family's design. Both halves are replaced by §5.8.

---

# 6. THE CONTRACT CHANGES REQUIRING JOSEPH'S RULING

**Seven. Each states what this plan recommends, what the recommendation rests on, and what happens
if it is refused.** None is taken here.

| # | ruling | recommended | rests on | if refused |
|---|---|---|---|---|
| **R-1** | **Z's throw footing** — add a row to SPEC §1.1 naming Z's throw ensemble basis as the `bank_uthrow_5d` / 160-throw / J28-correct ensemble, reproduced fresh | **adopt** | §1.3's four preservations; G's own `uthrow_source` is that basis | no footing is declared, and Z's throw has a definite description where the contract needs a digest |
| **R-2** | **Strict or loose reading of "Z's own throw."** §1.3a says *"Z's own"*, `11b` says *"in Z's own throw product"*, `REQUIREMENTS["null"]` says *"at throw creation"* | **STRICT** — a throw produced for Z | strict is what the three clauses say read literally, and it is what §3.3's measurement forces anyway | under *loose*, the three-way family choice reopens — and all three families still fail `11b`, so nothing is gained |
| **R-3** | **The block decomposition.** Does reproducing B's footing require reproducing its **36** per-knob block slabs, or is today's **21**-file `--block-knobs all` decomposition the same footing? | **put to the spec's owner, undecided here** | §1.3 item 3 — the difference is **measured**; its numerical consequence is **not** | if it must match, arm 6 needs a launcher change; unpriced, code not compute |
| **R-4** | **Route (i)** — pin the estimator envelope, and with which settings | **adopt**, `n_jobs=1, deterministic=True, force_row_wise=True` (§4.4) | §4.3(a): §6.4 requires the bound fixed before production, so the configuration is chosen first **whatever the numbers do** | the null bound stays sampled rather than argued, and `D4` keeps waiting on the control whose three gaps §3.7a records |
| **R-5** | **Reuse or regenerate `C_stat` / `C_ML`** | **REUSE, provisionally** (§3.2) | reuse preserves the block-sum footing G's `M` legs are measured against; regeneration is the move that changes it | regeneration adds `≈15` GPU / `≈6` CPU **and** an unmeasured combine, and buys nothing measurable off the one existing `of_inputs_5d.npz` |
| **R-6** | **Prohibition 4** — is a Z throw round "a further member"? (§2.4) | **stated, not recommended** — the purpose test is Joseph's | §2.4's for-and-against, both measured | **there is no permitted path and Z's throw waits for Gate 2.** §§3, 4 and 6 stand unchanged |
| **R-7** | **The output namespace.** Z's throw must write neither to `uq_5d/` base (overwrites the Aug-6 archive and family A) nor under `mii/` (the member namespace) | **name a Z container explicitly** via `MII_CONTAINER`, no default | §2.5, measured today | an omitted variable overwrites an archive — the shape `adopt_unified_5d.py:76` already carries |

**Two items are NOT rulings and are named so they are not mistaken for them.** `PM-4`'s phrasing
is its **owner's to amend** (§3.4), and the four withheld boundaries plus the criteria owner are
**§4b of the packet**, unblocked by nothing in this plan.

---

# 7. THE BOUNDED EXECUTION AUTHORIZATION THIS PLAN WOULD NEED

**Not requested here.** Written out so that if Joseph decides to grant it, the text is exact and
nothing is left to a default. **It is contingent on R-6 first**: if a Z throw round is a further
member, this authorization is unavailable and nothing below applies.

> **Authorized: one Z throw production round**, arms 5, 6 and 7 of the uthrow chain
> (`sbatch_uthrow_run_5d_fast.sh`, `sbatch_uthrow_block_5d.sh`,
> `sbatch_uthrow_combine_5d_fast.sh`), **CPU only**, reading `bank_uthrow_5d` and **no other
> input**, at `MNV_EST_SEED_OFFSET=0` with `MII_CONTAINER` set to a named Z container that is
> neither `mii` nor any canonical `uq_5d/` namespace, under a committed producing revision, with
> the writer persisting `x_cv`, `x_cv2` and the support predicate in the same execution.
>
> **Ceiling: `110` CPU task-hours, `0` GPU** — arm 5 `≤ 60`, arm 6 `≤ 40`, arm 7 `≤ 5`, plus one
> diagnostic arm-7 re-invocation `≤ 5` for the route-(i) comparison of §4.5. Per-arm, not on the
> sum.
>
> **Products:** one throw ROOT, its throw and block slabs, one null-operand file, and the receipts
> binding all of them to this job.
>
> **This authorizes no adoption, no grading, no discharge, no quoting, no projection, no
> publication use, no further member, and no movement of Gate 2 or of the `R5` stop.** The product
> is expected to be **NON-PASSING**: `null_epsilon` is withheld, so `assess_null` returns
> `NOT ASSESSABLE` with reject conditions `4c` and `11` in every case. **This buys auditability,
> not acceptance.**

**Prerequisites that are not resource questions and must be settled first, in this order:**

1. **R-6**, because it decides whether there is a path at all.
2. **R-4 (route (i))**, because §6.4 requires the bound's configuration fixed *before* production
   and operands produced under the other envelope would be superseded.
3. **R-7 (the namespace)**, because the default overwrites an archive.
4. **R-5 (`stat`/`ml`)**, because it determines what a manifest can declare — though **not** what
   the throw round reads, so it does not block this authorization specifically.
5. **The two Tier-2 code changes of §3.3**, landed and reviewed, because a run without them
   produces a throw that cannot satisfy `11b` and would have to be repeated.

**Doing the run before 1, 2, 3 or 5 spends `≤ 81` CPU task-hours on a product that a later ruling
supersedes.**

---

# 8. WHAT THIS PLAN DOES NOT DO

It adopts nothing, grades nothing, discharges nothing and moves no gate. It selects no throw
family — **all three remain UNQUALIFIED pending adequate evidence**. It does not close `PM-4`, does
not supply `B`, `S` or `ε`, does not name a criteria owner, and does not open any of Z's
twenty-eight cells. **It asks for no waiver of Gate 2 and treats none as obtainable**, on the
authority of a decision already on `main`: *"the gate, not the family authorization, is the binding
constraint, and no authorization from Joseph removes it — only the rehearsal work landing does."*
No compute was launched in preparing it.

## 5.8 ⚠ FEASIBILITY AND READINESS, SEPARATED — NEW, AND IT REPLACES §5.7's COST CONCLUSION

**§5.7 said "the artifact is affordable and the decision is not." That sentence conflated two
things that are not the same kind of thing, and it is withdrawn.**

- **FEASIBILITY** is a resource question and it has a number.
- **READINESS** is a set of unresolved prerequisites — missing criteria, an unassigned reviewer, an
  unowned decision. **These are not cost estimates and must not be priced.** An unwritten criterion
  does not become affordable or unaffordable; it becomes written or it does not.

### Z's COMPLETE resource requirement, including its own cause-3 design

**A Z member is not a historical seven-arm member.** It additionally carries the two assemblies, the
inflated-object validation, and — conditional on `PM-3` — the standard-P4 lateral stages:

| | GPU | CPU | class |
|---|---:|---:|---|
| historical seven-arm member, round-2 actuals | `54.90` | `86.53` | **TRANSFERRED** |
| `+` two `adopt_unified_5d.py` assemblies | — | `0.5231` | **TRANSFERRED**, §5.9 |
| `+` inflated-object validation, both variants | — | `0.07` | **DERIVED** |
| `+` standard-P4 lateral stages 3–6 | `0.80` | — | **TRANSFERRED**, conditional on `PM-3` |
| **one Z member** | **`55.70`** | **`87.12`** | **DERIVED on TRANSFERRED priors** |

**§6.3 rules `(cause 3, Z)`'s `M(ii)` to be the joint-baseline composite over members, and §3.7b's
planning estimate is `N = 4`–`5` total.** So Z's complete requirement is:

| design | GPU | CPU | vs `R5` `500`/`500` |
|---|---:|---:|---|
| **Z at `N = 4`** | **`222.8`** | **`348.5`** | **`44.6%` / `69.7%` — FITS** |
| **Z at `N = 5`** | **`278.5`** | **`435.6`** | **`55.7%` / `87.1%` — fits, with `12.9%` CPU margin** |

**⚠ AND THE FIGURE §5.7 QUOTED IS A DIFFERENT DESIGN, MEASURED ON A DIFFERENT SUBJECT.** The
`5×–9×` overrun is the **historical M(ii) family at 46–50 members**
(`46 × (54.90, 86.53) = 2,525 GPU + 3,980 CPU`), which **§6.3 explicitly does not adopt as Z's
design** and which `DECISION-20260830` authorizes as a separate object. Charging Z with it is the
asymmetric comparison this campaign keeps catching — **the populations are 4–5 members and 46–50
members, and no ratio between them is a statement about Z.**

**So the corrected feasibility conclusion:** **Z's complete resource requirement, including its own
cause-3 design, fits inside `R5` at `N = 4` and fits with a thin margin at `N = 5`.** Every figure
inherits §5.6's contingencies, of which the `±60%` single-arm swing alone would move `N = 5` over
the CPU ceiling.

**The binding constraint is the SCHEDULE, not the ceiling.** Four to five rounds of **374 tasks
each** must fit into blocks of `6 d 06 h` and `6 d 11 h` (§5.5). `AMENDMENT` §3c records one arm's
tail running at two-way concurrency on `Reason=Resources` for **eleven hours in a single round**.
**Whether four rounds fit is NOT established, and it is the question that decides `N`.**

### READINESS — unresolved prerequisites, deliberately UNPRICED

| # | prerequisite | state as of 2026-09-10 |
|---|---|---|
| 1 | the four withheld boundaries — `null_epsilon`, `cause3_agg`, `cause3_med`, `cause3_corr` | **UNRESOLVED.** `null_epsilon` needs `B`, `S`, `B ≤ S` and `ε ∈ [B, S]`; §4 supplies a *route* to `B` only |
| 2 | a scientific-acceptance **criteria owner** | **ASSIGNED 2026-09-10** — `z-criteria-designer`, acknowledged; `owners.tsv` row added this commit |
| 3 | an **independent assessor** of those criteria | **ASSIGNED 2026-09-10** — `z-independent-assessor`, acknowledged; row added this commit |
| 4 | a **grading lane** for the 28 `(cause × leg)` cells that `BEN-381` does not disqualify | **UNRESOLVED** — and distinct from #3, which reviews the criteria, not the artifact |
| 5 | the reuse-vs-regenerate rationale for `(cause 6, Z)` | **UNRESOLVED** — §3.2 |
| 6 | `PM-4`'s binding gap and its phrasing amendment | **UNRESOLVED**, owner's to amend |
| 7 | for any **significance**: the projection map designated, `ndf` and `norm.isf` declared, a decision threshold and margin | **UNRESOLVED — the threshold and margin exist nowhere in the tree** |

**None of these has a task-hour cost and none is shortened by any resource authorization.** Two of
the seven moved today, and they moved by assignment, not by spending.

## 5.9 THE MECHANICS/COST PILOT — the smallest thing that would price the Z configuration

**Requested in §7b. NOT run, and this section does not authorize it.**

§5.2a leaves every estimator-bearing figure unpriced for the proposed configuration. The smallest
representative measurement that fixes that is **three single-task arm-5 invocations**, because arm 5
is the arm that runs an unfold per throw and carries the `±58.7%` swing.

| task | configuration | `--out` | what it contributes |
|---|---|---|---|
| **P1** | **Z configuration** — `n_jobs=1, deterministic=True, force_row_wise=True` | Z container, slab `0` | elapsed and peak RSS under the proposed settings |
| **P2** | **Z configuration, repeat** | Z container, slab `0`, second path | **within-configuration reproducibility at real scale** — does `deterministic=True` give byte-identical slabs? |
| **P3** | **current configuration**, unchanged | Z container, slab `0`, third path | the baseline the multiplier is measured against, on **the same node type, same week** |

**Why one throw index and not forty.** The quantity wanted is per-task, and forty tasks measure the
same per-task quantity forty times while also measuring queue contention — which is real but is not
what the pilot is for.

### What it WOULD establish

1. **The runtime multiplier of `n_jobs=1`** — `elapsed(P1)/elapsed(P3)`, the single largest unpriced
   term in §5.2, and the one §4.4 created by recommending the pinning.
2. **Peak memory** under the Z configuration, from `sacct MaxRSS` — currently unmeasured for every
   Z row, and the driver is memory-bound.
3. **Whether pinning changes the throw slab at all** — `sha256(P1) vs sha256(P3)`. This is the
   throw-side half of §4.3(b), on the real bank rather than on 400 synthetic rows.
4. **Whether the pinned configuration is reproducible run-to-run at real scale** —
   `sha256(P1) vs sha256(P2)`. **If P1 ≠ P2, route (i) fails on its own terms** and `B` reverts to a
   measured quantity with all three of §3.7a's gaps reopened. That is the single most decision-
   relevant bit in the pilot, and it is cheap.

### What it could NOT authorize or establish

- **It cannot establish `B`.** A throw-side unfold is not the CV re-unfold chain; `--null` runs in
  **arm 7**, which the pilot does not exercise. §4.4's list of required evidence is untouched.
- **It produces no covariance**, no combine, no assembly, no receipt Z could consume.
- **It authorizes no adoption, no grading, no discharge, no quoting, no further member**, and it
  moves neither Gate 2 nor the `R5` stop.
- **It does not price arms 6 or 7**, whose thread environments differ from arm 5's (§4.4).
- Three tasks measure a per-task cost, **not** a 40-task round's wall-clock — which §5.8 identifies
  as the binding constraint.

### Cost

| | figure | class |
|---|---|---|
| historical arm-5 per task | `46.4` min (R1) / `69.6` min (R2) | **TRANSFERRED** |
| three tasks at historical rates | `≈ 2.3 – 3.5` CPU task-h | **DERIVED**, and **not valid for P1/P2** — that is the unknown being measured |
| **reservation bound** | **`18` CPU task-h, `0` GPU** — `3 × --time=06:00:00`, the launcher's own request | **`3.6%` of the CPU ceiling** |

**The reservation is what a breach is measured against, not a spend estimate.** If `n_jobs=1` is
catastrophically slow, P1 and P2 hit the six-hour wall and the pilot reports that — which is itself
the answer, and is why the cap belongs in the authorization.

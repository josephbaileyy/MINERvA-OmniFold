# ASSESSMENT 2026-09-18 — the cause-3 joint-baseline acceptance packet

**Owner:** `z-independent-assessor` (`owners.tsv:15`). **Subject:**
`PACKET-20260917-cause3-joint-baseline-acceptance.md` at
`937c3847a09d0c87ca3515bf58b06ad0b709f6d7`, author `owners.tsv:14` `[91eaa2]`, pushed and reachable
from `origin/lane/z-criteria-recommendation-20260910`.

## CITABLE FOR / NOT CITABLE FOR

**CITABLE FOR:** the per-item approval verdicts and findings `C1`–`C6`, with their evidence.

**NOT CITABLE FOR:** adoption, grading, member production, or any boundary value. **No boundary is
adopted and none is graded.** `cause3_agg`, `cause3_med`, `cause3_corr` and `null_epsilon` all remain
**WITHHELD** — measured: those are the complete key set of `Z_BOUNDARIES` (`z_contract.py:213`), all
four `Boundary.withheld`. `θ` closed and not a floor; `[B,S]` proposed (`SPEC:1552`); `ε` not
adopted; full `S` OPEN; Gate 2 FAIL. **No member production is requested or implied.**

## Evidence classes

- **SOURCE** — committed blobs at `937c3847`.
- **INSTRUMENT CALLED** — the committed module executed rather than retyped, blob-pinned.
- **PROBE** — my own arithmetic on synthetic matrices, preserved at
  `docs/orchestration/probes/probe-20260918-cause3-projected-correlation-invariance.py`.
- **No cluster payload was read for this assessment and no compute was run.**

## Verdicts, item by item against §7

| §7 item | verdict |
|---|---|
| **1 — §5's leg set, member definition, diagonal family, offset-grid requirement** | **ENDORSE IN FULL.** Every claim reproduces exactly by calling the instrument (`C2`) |
| **2 — §2's and §3's FORM and POPULATION, incl. §3.1's `φ` derivation** | **ENDORSE.** The derivation is sound and is robust to `P1`'s narrowing — and under `P1` its exclusion branch is **empty**, which removes the margin hazard entirely (`C3`) |
| **3 — §4.1's structural requirement (invariance under `C → D C D`)** | **ENDORSE THE REQUIREMENT — and the packet's own proposed statistic FAILS it.** Measured. The packet's own second falsifier at §6 is what fires (`C1`) |
| **4 — §4.3's L4 criterion in full** | **ENDORSE ON THE MERITS**, with one operand correction and one addition owed before it can distinguish a pass from a non-test (`C5`) |
| **5 — no values for `cause3_agg` / `δ_bin`** | **AGREE, and the reasoning is verified verbatim** (`C6`) |
| **6 — no values for `τ_p`** | **AGREE**, and `C1` makes the reason stronger than the packet states |

---

## `C1` (PROBE) — §4.1's requirement is right; its claimed satisfaction is REFUTED, by the packet's own falsifier

**The requirement is sound and I endorse it.** *"A correlation criterion that can be satisfied by
diagonal stability is not a correlation criterion"*, tested as invariance under positive diagonal
rescaling `C → D C D`, is the correct structural test for an L3 instrument.

**The proof offered is about a different object than the statistic proposed.** §4.1 argues that
`R_ij = C_ij/√(C_ii C_jj)` is unchanged when `C_ij → d_i d_j C_ij` — **true, and I reproduce it** —
and then proposes the statistic `R_p = corr(M_p C_Z M_p')`. **Source-basis rescaling does not pass
through the projection:** `M_p (D C D) M_p'` is not `E (M_p C M_p') E` for any diagonal `E` unless
`D` commutes with the map's structure, which an aggregation map does not.

**MEASURED, 400 random PSD sources with non-negative aggregation maps, `n = 40 → m = 6`:**

| statistic | worst change under `C → D C D` |
|---|---|
| `corr(C)` — what §4.1 proves | **`4.441e-16`** — invariant, as claimed |
| **`corr(M_p C M_p')` — what §4.1 proposes** | **`5.390e-01`** — **NOT invariant** |

**And the consequence in the form that decides it.** Take a member differing from `k = 0` by a
**pure diagonal rescale**, so the source correlations are identical to `4e-16`:

| rescale sd | `‖R_p^(k) − R_p^(0)‖_max` |
|---|---|
| `0.05` | `0.0117` |
| `0.20` | `0.0405` |
| `0.70` | `0.3986` |

**A member whose only change is diagonal — exactly the change L1 and L2 own — moves the L3 statistic,
and at a magnitude that would breach any plausible `τ_p`.** That is the dual of the failure §4.1 sets
out to prevent: not a correlation criterion satisfiable by diagonal stability, but one **breachable
by diagonal movement alone**, which reports L1/L2 through L3's instrument and destroys the
disjointness the whole packet is organized around.

**I did not have to invent the test. The packet supplies it**, at §6: *"if any proposed statistic is
**not** invariant under `C → D C D`, it is not correlation-sensitive and must be replaced."* **Run
against §4.1's own statistic, that falsifier fires.**

**What survives, and it is most of it.** The **disjointness of L3** is untouched — it rests on
`cause3_corr`'s withheld reason, which I verified verbatim at `z_contract.py:231-235`: *"Both adopted
statistics are functions of the diagonal alone, so a MET result on them licenses nothing about
`C_Z`'s off-diagonal structure."* The **requirement** at §4.1 is untouched and is the right one. The
**disqualification of trace and per-bin `σ` statistics** is untouched — I confirm both fail the test
(`Tr(DCD)/Tr(C) = 1.6547`; per-bin `max_i |Δσ_i|/σ_i = 1.4964`). **Only the claim that the projected
correlation matrix satisfies the requirement is refuted.**

**For completeness, what `corr(M C M')` *is* invariant under:** rescaling in the **projected** basis,
measured `2.220e-16` — which is trivial, because it is already a correlation matrix, and it is not
the property required. **The conflation is between "R is a correlation matrix, so it is invariant
under rescaling of its own basis" and "R_p is invariant under rescaling of the SOURCE basis."** Only
the second is the requirement.

⚠ **I do not supply a replacement statistic.** Naming one would be designing the criterion I would
then be asked to assess, and the recusal at `068436e5`'s stated principle applies. The packet's own
falsifier decides the question; the form is the author's to re-derive.

## `C2` (INSTRUMENT CALLED) — §5.2's offset-grid claims reproduce EXACTLY. Endorse in full

I called `seed_offset_policy` (blob `023ec710831c9480fe1eb7c884bf8b1f1e0c5b74`) rather than retyping
its rule:

| input | returned |
|---|---|
| `forbidden_differences([42, 1000])` | **`[-958, 958]`** |
| `check_offset_grid(B, 1..8)` | **`[]` VALID**, 64 pairs checked |
| `check_offset_grid(B, 0..4)` | **`[]` VALID**, 25 pairs |
| `check_offset_grid(B, {0, 958})` | **`[('group42', 958, 'uthrow', 0, 1000)]`** |
| `check_offset_grid(B, {1, 959})` | **`[('group42', 959, 'uthrow', 1, 1001)]`** |
| `check_offset_grid(B, {0, −958})` | **`[('group42', 0, 'uthrow', −958, 42)]`** |
| the module's own doc example `[0,100,500,958,1058,1500]` | **two** aliases, at `(0, 958)` **and** `(100, 1058)` |

**Every tuple the packet reports is the tuple the instrument returns.** The pairwise-not-single-value
character of the constraint is confirmed by construction: `k = 0..8` is also VALID at 81 pairs, so it
is the *pair* `(k, k′)` with difference `±958` that aliases, not any offset in isolation. **§5.2's
requirement — that the member set be validated by `check_offset_grid` returning empty and that the
declaration record the grid rather than its size — is correct and I endorse it**, including the
whole-packet falsifier at §6 that an aliased family makes every statistic meaningless.

## `C3` (SOURCE) — the `φ` derivation is sound, robust to `P1`, and its exclusion branch is EMPTY

The derivation — *a bin's movement can damage a published conclusion only if some published quantity
depends on that bin*, therefore `φ = 1` on the union of declared map supports and the complement is
excluded **by declaration** — is a **population declaration rather than a judgement**, which is the
form the prospective rule wants. **I endorse it, and it is stated parametrically**, so it takes no
dependency on how many maps `P1` binds.

**On the routed concern that `P1` narrows the map set to one:** the packet's population is *"every
bin with non-zero weight in at least one declared map"*, which is map-set-agnostic as written, so the
narrowing does not disturb it. And a consequence worth stating: a single `(E_avail, W)` map keeps
`eavail` and `W` and marginalizes `pt, pz, q3` with positive weights, so **every reported 5D bin has
non-zero weight in it and the union is the whole reported support.** Then `φ = 1` everywhere and
**the exclusion branch is empty.**

⚠ **That is favourable and it removes a hazard the packet correctly anticipated.** §3.1 carries the
margin caveat this lane's deadband correction produced — *"a weight that is nearly zero is a
membership question"*. **With an empty exclusion branch there is no membership question to decide**,
so no margin need be declared and no post-hoc population choice is available. **The packet's caveat
should be retained as written** — it binds if the map set ever changes — **but it does not bite
today.**

## `C4` (PROBE, analytic) — the aggregation direction, confirmed without measurement

The routed correction is right and it needs no numerical support: a uniform `σ → (1+δ)σ` sends
`C_ij = ρ_ij σ_i σ_j → (1+δ)² C_ij` **identically**, so **every** quadratic form — every projection,
at every `N`, under every weighting and every correlation structure — moves by exactly `(1+δ)² − 1`.
**Coherent movement is the benign channel and aggregation neither amplifies nor is governed by the
contributor count.** The blow-up channel is *cancelling* movement over a *near-cancelling* source,
which is the same channel as this lane's `T5d` projection refutation one level down.

**Consequence for the packet, and it supports it:** `δ_bin` is **exact** on the coherent channel and
**vacuous** on the cancelling one, so L2 is a complete control on one channel and no control at all
on the other. **That strengthens §3's retention of the per-bin leg as a declared diagnostic and
strengthens L3's primacy** — and it is a better argument for the packet's own position than a
"weak proxy in both directions" framing. **I attach no contributor-count factor to any of this**; the
severity is set by the smallness of `wᵀCw`, not by how many cells aggregate.

## `C5` (SOURCE) — L4 endorsed on the merits, with one operand correction and one addition owed

**The gap is real. MEASURED:** `Z_BOUNDARIES` (`z_contract.py:213`) has exactly four keys —
`null_epsilon`, `cause3_agg`, `cause3_med`, `cause3_corr`. **There is no F7/centering key**, so a
published binary choice has no boundary. **The packet is right to name it, and right that creating
the key is not its call.**

**The criterion is sound on the merits.** A discrete outcome admits no tolerance, so Gap 3's tuning
concern closes structurally — the same argument that made `B`'s boolean estimator immune — and the
protected quantity is a real published choice.

⚠ **Operand correction.** The packet describes `f7_cv_centered_required` as *"whose operand is
`‖mean_shift‖`"*. **Measured:** `uq_math.py:160` is
`f7_cv_centered_required(mean_shift_norm, sqrt_trace, n_throws, floor_multiple=None)` — **three
operands plus a multiple.** `Tr C_Z` also moves across members, so the criterion tests the **joint**
stability of a three-operand comparison. **This makes L4 stronger than described**, and the
one-operand phrasing understates it; it should be corrected rather than left, because a reader
checking only `‖ms‖` stability would think the criterion discharged.

⚠ **One addition owed before a PASS is interpretable.** As written, the criterion cannot distinguish
*"the branch was tested and is stable"* from *"no member came near the branch point."* Both return
identical booleans. That is this campaign's catalogued could-not-look-zero shape, and the packet's
own tradition elsewhere is to require the distinction on the receipt. **The margin to the branch
point per member is the quantity that separates them**, and the prior finding that a flip is
*"remote at the observed scale"* is precisely a statement that the margin is large and unrecorded.
**I name the requirement and not its form or value.**

## `C6` (SOURCE) — "three withdrawn numbers, one rule" is verified verbatim, and the abstention is correct

Both withheld reasons are as quoted, word for word:

- `cause3_agg` (`z_contract.py:220-225`): *"the format-derived `0.0861%` was withdrawn in rev. 16.
  Macro formatting does not establish how much estimator-baseline sensitivity is scientifically
  acceptable, and the half-display-unit rule behind it is wrong in both directions."*
- `cause3_med` (`:226-230`): *"the printed median's precision is a new tolerance choice, not a
  consequence of that summary's formatting. Needs a justified per-bin tolerance AND a justified
  coverage fraction — two numbers, and both are scientific."*

And `SPEC:1435` confirms the inherited form: *"(`f_agg`-shaped, a trace ratio against a **named**
denominator)"*. **So §2 and §3 reinvent nothing, and §3.2's identification of `δ_bin` with the
question Joseph closed is correct**: both ask how much movement in a reported per-bin uncertainty is
scientifically acceptable. **Proposing no number is the right act, and proposing a fourth
format-derived one would be the fourth instance of one rule.**

## `C7` (SOURCE) — the seed disagreement I routed from rank 3 RESOLVES, and it is a RECORD COLLISION that belongs to cause 3

At `e393ad5e` `R8` I measured that the registry declares the 5D central at **est seed 42** while the
throw payload records **`estimator_seed = 1000`**, called it a fingerprint mismatch under the
registry's own *"reject on mismatch"* rule, and routed the disposition rather than issuing it.
**The disposition is now available from source, and I verified it here rather than accepting it
relayed.** `sweep_bank_5d.py:354-357`, verbatim:

> *"42 was the hardcoded literal, so 42 is this module's archive value — and it **deliberately
> DIFFERS** from `unified_throw_cov.py`'s 1000. Each module's default-equivalent preserves ITS OWN
> prior behaviour; **unifying them on one number is the instinct a later reader will have and it
> silently re-seeds one of the two.**"*

**So both records are internally correct and they cannot both be satisfied.** The registry's nine-field
rule, read literally, is violated — by a difference the producing module documents as deliberate and
explicitly warns against repairing. **That is a record collision, not a payload defect**, and it is
cause 3's because cause 3 *is* the estimator-seed question.

**Two consequences for this packet, and both are favourable to it.** First, §5's baselines
`{42, 1000}` are **confirmed from source as two genuinely separate archive values**, which is the
premise the whole offset design rests on — so `C2`'s endorsement stands on a verified footing rather
than on the instrument's output alone. Second, the pairwise-not-single-value constraint is the direct
consequence of the baselines being distinct and staying distinct. ⚠ **And the standing warning
attaches to any future repair of the registry: the seeds must not be unified**, so the collision must
be resolved on the *registry's* side or by an explicit exemption, never by re-seeding a module.

---

## What I recommend

**Approve §7 items 1, 2 and 4** — the last with `C5`'s operand correction made and its margin
requirement attached. **Approve §7 item 3's REQUIREMENT while declining the statistic that
accompanies it**, per `C1`: the requirement is the durable contribution and the instrument must be
re-derived against it. **Agree with §7 items 5 and 6** — no values.

**Nothing here approves a boundary value, requests a member, or licenses production.** `C1` is the
only refutation and it is of a form, not of the packet's organizing argument, which survives intact
and is well sourced.

## What this assessment does not do

- Adopts nothing, grades no cell, and creates no `Z_BOUNDARIES` key.
- Supplies no replacement statistic for L3, no `τ_p`, no `δ_bin`, no margin form, and no member set.
- Ran no compute and read no cluster payload. The `C1`/`C4` probes are synthetic-matrix arithmetic on
  this machine.

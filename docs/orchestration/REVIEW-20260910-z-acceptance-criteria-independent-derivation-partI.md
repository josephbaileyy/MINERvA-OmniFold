# PART I — assessment of the endpoint-A packet's §2/§2.1 and §3/§3.1–§3.3

**Owner:** independent-assessment lane. **Subject:**
`docs/orchestration/PACKET-20260910-z-endpoint-A-acceptance-and-cause3-corr-amendment.md` at
`05bf8647`, sha256 `e5fbd9a99cd27d9db0130246bbbded0e334de30e64161804e3735c05de3e5df1`, 613 lines.
**Code base of measurement:** `6f24fb00`. **Yardstick:** `F1`–`F21` and §F.5's five block conditions,
committed at `c695f209` before this packet existed.

**Assigned slice only:** §2, §2.1, §2.1a, §3, §3.1, §3.2, §3.3, plus the coordinator's ensemble
measurement. **No grade is assigned** — no `MET`/`OPEN`/`UNRESOLVED` appears here, per `BEN-381`.
§4.1, §4.3, §4.4/4.4a/4.4b, clause (d) and §1/§1.1 are **not assessed**; see §I.6.

**Instrument:** `docs/orchestration/state/probe-z-cause3corr-binding-site-20260910.py`, `rc = 0`,
which executes `z_validator.assess` rather than reading it. It mutates only the in-process registry
dict and reverts in `finally`; no file is edited.

---

## I.1 — §3, §3.1, §3.2, §3.3: EVERY MECHANICAL CLAIM CONFIRMED BY EXECUTION

I re-ran the packet's measurements independently rather than accepting them. All five of §3.1's rows
reproduce, and the two claims §3.3 rests on reproduce.

| packet claim | my result |
|---|---|
| §3.1(b) `L = {agg, med}`, `cause3_corr` withheld → **MET** | reproduced: `is_met = True`, `branch_label = 'MET'` |
| §3.1(c) deleting `cause3_corr` → `describe()` **byte-identical** | reproduced: identical, 999 chars |
| §3.1(d) `assess` reaches a boundary only via `leg.boundary_key` (`:247`) | confirmed |
| §3.1(e) leg declared, boundary withheld → `assessable=False`, `reject_conditions=('4c',)` | reproduced exactly, and `is_met = False` |
| §3.1(a) every `LegSet(` is in `tests/test_z_validator.py`; `z_build.py` calls only `assess_null` | confirmed — **10 of 10** occurrences in that one test file, and `z_build.py:521` is `assess_null` |
| §3.2 all three words present in `_DIAGONAL_ONLY_SCOPE` | confirmed: `marginalization`, `projection`, `coverage validation`, `off-diagonal` all present |

**The two positive controls the packet does not carry, and why they were needed.** A byte-identity
result is only evidence of inertness once the harness is shown to be able to *see* a registry
deletion at all.

- **Control A.** Deleting `cause3_agg` — a boundary a declared leg names — raises
  `ZContractError: unknown acceptance boundary 'cause3_agg'`. So `assess` consults the registry at
  assess time, and §3.1(c)'s identity is a real negative rather than a blind one.
- **Control B.** With two diagonal-only legs `scope_statement` is present; adding a
  `sees_correlations=True` leg makes it `None`. The narrowing is derived from the leg set, which is
  §3.2's claim about where the binding lives.

**One strengthening the packet is entitled to and does not take.** §3.1 calls the registry line
*"inert"*, which reads as contingent. It is **structurally unreachable**: `assess` looks up a boundary
only at `:247` via `boundary(lg.boundary_key)`, and `LegSet.describe()` surfaces boundary status only
at `:110`, also keyed on declared legs. A boundary no leg names is therefore reachable from neither
the outcome nor its description. That is why the delete-test is byte-identical, and it is a mechanism
rather than an observation.

**§3.2's central finding, independently confirmed:** the emitted scope statement disclaims
`projection` and `marginalization`, and endpoint A's deliverable *is* a projection. A `MET` under the
current leg set disclaims the release endpoint A exists to make. This is the same fact `F-I` reached
from the other side, and it is now confirmed from the validator's own emitted text rather than from
the algebra.

**§3.3's option ordering does not invert, and it is consistent with what I measure.** Option 1
requires narrowing what a `MET` licenses, which is the change Joseph barred — so **UNSOUND** follows
from the code, not from judgement. Option 2 works and costs A its deliverable — **SOUND, NOT
RECOMMENDED** is accurate. Option 3's two mechanical preconditions both hold: declaring a
correlation-sensitive leg withdraws the scope statement (control B) and makes `cause3_corr`
load-bearing (`is_met = False`, `failing_legs = ('corr',)` at `s_corr = 0.9`).

**And §3.3's "costs nothing today" is structurally true, not lucky** — the claim I tested hardest,
because it is where a recommendation could smuggle a pass. With the leg adopted and the boundary
still withheld, `assess` returns `assessable = False`, `branch_label = None`,
`reject_conditions = ('4c',)`, `is_met = False` — **at `s_corr = 0.001`, well inside any plausible
limit.** The refusal is on the *absence of a limit*, not on the value. So adoption of the leg cannot
produce a pass regardless of what the statistic measures, which is the correct direction.

---

## I.2 — §2.1: THE SAMPLE-COVARIANCE POPULATION IS NOT TWO. `Flux` IS THE THIRD.

This is the one finding in my slice that I would not want Joseph to decide without.

§2.1 states: *"**Exactly two summands are sample covariances: `C_stat` and `C_ML`.** Everything else
is a deterministic band or lateral sum. So clause (v)'s 'for every sample-covariance block entering
the sum' has a population of **two**, fixed by Z's own formula rather than by a search."*

**Measured, and the chain is closed in tracked code:**

1. `adopt_unified_5d.py:42-43` — `VERT_BANDS = [… "Rvn2pi", "Rvp2pi", **"Flux"**]`. `Flux` is the
   **13th** vertical band.
2. `z_contract.py:66` — `VERT_BANDS = tuple(_adopt.VERT_BANDS)   # V, 13 -- inflated through D_Z`.
   Z's `V` **is** that list, imported, not re-derived.
3. `z_assembly.py:4` — `C_Z^c = D_Z^c (sum_V C_b) D_Z^c + …`. So `Flux` enters as a member of
   `Σ_V C_b`, and is **inflated** through `D_Z^c`.
4. `unified_throw_cov.py:467-468` — `C_flux = mat_covariance(np.asarray([flux_x[u] for u in
   sorted(flux_x)]))`; `C_block += C_flux`. That is a **sample covariance over the flux universes**,
   and `:470` prints it as *"flux (N univ, …); MAT mean-centered 1/N"*.
5. `uq_math.py:96-104` — `mat_covariance` is *"universe-mean centered, **biased 1/N**"*.
6. `OI-137` enumerates, independently of me: *"the statistical block (100 bootstraps), `C_ML` (24 seed
   splits), and **the flux band (100 PPFX universes**, effectively rank-1 with one normalization mode
   holding 99.6% of its variance)"* — **three**, not two — and separately confirms that the ~45 MAT
   bands are deterministic rank-one, which is what §2.1 gets right.

**Two consequences, and the second is worse than the first.**

- **The disclosure population omits a block.** A-6 as written would disclose two of at least three
  sample-covariance blocks entering `C_Z`.
- **The stated convention is false of part of Z's sum.** §2.1's table gives one normalization,
  *"`combine_cov_nd.py:20` … unbiased `1/(N−1)`"*, with the note *"same line — one script, one
  convention."* The flux band is **biased `1/N`**. So A-6 would assert a single convention for a sum
  that mixes two. Omitting a block is incomplete; asserting the wrong convention for it is
  affirmatively misleading, and it is exactly what `F8` was written to prevent.

**The diagnosis, which is the part worth carrying.** §2.1's population is not wrong through
carelessness — it is wrong *because of how it was derived*, and the derivation is the thing §2.1 is
proudest of (*"CLOSED and DERIVED, not enumerated by hand"*). Reading the formula's **surface** is
correct: `C_stat` and `C_ML` are the only sample-covariance *summands named in it*. But `Σ_V C_b` is
itself a sum, and the third sample covariance is one level **inside** it. **The population question
recurred one layer below where it was answered** — the same law this campaign has now hit four times,
and the reason a derivation is not safer than an enumeration unless it recurses.

**Feasibility is not the issue, which makes this a pure completeness defect.** The flux band's `N` is
already derived from the actual inventory (`n_flux = len(expected_flux)`, `unified_throw_cov.py:126`)
and already guarded fail-closed in both directions (`:461-465` raises on
`missing=`/`extra=` against `set(range(n_flux))`). So the same verification instrument §2.1 correctly
identifies for `C_stat`/`C_ML` exists for the flux band too. Adding it costs no compute.

**One boundary case I explicitly do NOT claim.** `C_unified` (`N = 160`) is a sample covariance whose
diagonal sets `g^c` and therefore scales the whole block sum, but it is **not a block entering the
sum**, so clause (v)'s literal population does not include it. Its `N` is already stamped
(`unified_throw_cov.py:412`, `:564`). I flag it as a named boundary and do not require it — demanding
it would be the over-reach `F18` warns against.

---

## I.3 — THE COORDINATOR'S ENSEMBLE MEASUREMENT: CONFIRMED, ON BETTER FOOTING THAN OFFERED

I was asked to verify or break this. **It holds, the consequence is right, and it does not need the
`pscratch` evidence it was offered on.**

- **`OI-160` already records the load-bearing fact**, in tracked text: *"an exact-population validator
  cannot see a contract change"*, and *"for 5D the corrected replicas are the member-scoped
  `mii/member_k000000/` set (**100 boot + 24 split**…)"*. So *both arms have identical `N`* is
  establishable from the committed record, with no cluster read at all. That is a stronger footing
  than an `mtime`, and it removes the `cp -p` caveat from the **consequence** entirely.
- **`07c18aee` is confirmed**: 2026-07-14 14:43:19 -0700, changing `seed=a.seed` → `seed=a.estimator_seed`
  in `bootstrap_nd.py`, and it touches `combine_cov_nd.py`. Products dated 2026-07-13 therefore
  predate the correction, as inferred.
- **A content-based discriminator exists and is stronger than `mtime`:** the reported key schemas
  differ — the top-level arm has no `estimator_seed`, the member-scoped arm has
  `estimator_seed`/`est_seed_offset`/`est_seed_offset_declared`. Key schema is intrinsic to file
  content, so `cp -p` and a tape restore do not forge it. **But it discriminates the *inputs*, not the
  *product*** — `combine_cov_nd.py:23-26` writes one `TH2D` and nothing else. So the caveat is
  correctly placed: the **arms** are distinguishable, the **binding** from an arm to the digested
  bytes is not, and only the latter needs the recomputation that was correctly declined.

**The consequence, in its sharpest form: `N` is a count, and a count cannot identify a population.**
Two populations of equal cardinality are indistinguishable by cardinality, under *either* of `F9`'s
two readings of "verified". So A-6 part (a) is satisfiable in full while leaving the producing arm
unnamed — across a boundary (`07c18aee`) that changed the seed contract. A-6 needs a field that
**names** the producing revision or arm, not one that counts it.

**This strengthens the packet rather than contradicting it.** §2.1a already names part **(b)**, *"bind
the product digest to the producing execution"*, and already concedes *"looking harder is exactly what
(b) is, and it has not been done here."* What the equal-`N` fact adds is that **(a) cannot substitute
for (b)** — which the packet does not say, and which is the reason (b) cannot be dropped as
bookkeeping. §2.1a's three ambiguous invocation sites, including the member-scoped
`sbatch_finalize_5d_bkgaware_gpu.sh:422`, are the same point from the code side; I confirm the site
list is a real ambiguity and not a hypothetical.

---

## I.4 — MY §2.6b CITATION WAS WRONG. CONCEDED, AND THE SPEC MAKES THE SAME ERROR.

Part G §G.2 said *"§2.6b leaves open whether Z reuses `S.stat_cov` or regenerates it."* Measured:

- §2.6b runs `:1092`–`:1108` and is titled *"WITHDRAWN — reuse of `C_stat`/`C_ML` is not evidence of
  incompleteness."* It withdraws the claim that Z **must regenerate** them.
- The openness text is at **`:1122`, inside §2.6c item 4** — *"The ensemble question is OPEN and is
  named as open."*

**So the correction is right and my citation was wrong.** The proposition I asserted is true and in
the spec; I attached it to a section that does something else. The substance of Part G's caveat
survives untouched — the question is open, so `C_stat` is Z's *candidate* input, which was the point.

**And the same misattribution is in the spec.** `SPEC:3629` reads *"**Whether Z regenerates or reuses
`C_stat`/`C_ML`** (§2.6b)"* — the identical wrong label, one line below `:3627`, which cites §2.6c
item 5 correctly for a neighbouring item. Three sites carry this proposition under **three different
addresses**: `:504` says §2.6, `:1122` is the text in §2.6c, `:3629` says §2.6b. I took the label from
`:3629`. That does not make my citation right, but the correction should land on `SPEC:3629` too, or
the spec will keep producing this error for the next reader.

---

## I.5 — A GAP IN MY OWN PRE-REGISTERED YARDSTICK, RECORDED BECAUSE IT IS MINE

§I.2's finding is **not** one of §F.5's five block conditions, and I will not retro-fit it.

Condition 3 pre-registered the population error in **one direction only**: *"Ruling 2's block set is
defined by the computing function, so that ~45 deterministic rank-one bands acquire `N = 2`
disclosures"* — over-inclusion. The flux band is **under-inclusion**: a genuine sample covariance left
out. My block list checked the direction where the population is too large and not the direction where
it is too small.

That is the one-directional-guard failure I demand bidirectionality against in `F15`, occurring in my
own pre-registration. `F1` and `F7` cover the finding as *requirements*, so the yardstick is not
silent — but the pre-registered **blocking** list was one-sided, and a reader entitled to rely on
§F.5 as complete should know it was not.

---

## I.6 — NOT ASSESSED, AND WHY

- **§4.1, §4.3, §4.4/4.4a/4.4b** — the `δ_proj` core, and **A-4's `1e-8` tolerance wherever it
  appears, including its row in §2's table.** A-4 is clause (d); I supplied that gate and am
  disqualified. I note only that §2's A-4 row is *narrowed* consistently with §4 and take no view on
  the tolerance.
- **§1 and §1.1** — routed away from me because they may transcribe Part G's `F-III`. The routing was
  made without my asking, and it is the right call.
- **The `pscratch` digests, sizes and `mtime`s** — not independently re-read. §I.3 does not depend on
  them; it rests on `OI-160` and `07c18aee`, both in tracked text.
- **Whether the flux band is *also* omitted from any other block census** — not searched.
- **§5, §6, §7** beyond residue 9 — outside the assigned slice.

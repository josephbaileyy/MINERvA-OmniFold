# PART M — rev. 3 assessment, a failed attack of my own, and the slices I can no longer confirm alone

**Owner:** independent-assessment lane. **Subject:** the endpoint-A packet at `6bb8b32d`, sha256
`dad55b579eb4759110e2b790af4aede652cc20098ac341f12157550a8ecf14bc`, **908** lines (was 623 at
`05bf8647`). **Code base:** `6f24fb00`, unchanged. **Yardstick:** `F1`–`F21` per Part G §G.4 and
§F.5's block conditions, committed at `c695f209`.

**Assigned:** §2/§2.1 (A-6), §2.1a part (b), §3–§3.3, rows A-1/A-2, §5, §7. **No grade assigned.**

---

## M.1 — AN ATTACK OF MINE THAT FAILED, RECORDED BECAUSE A FAILED ATTACK IS EVIDENCE

Rev. 3 adds a refinement at `:190-195`: *"`mat_covariance` is applied to **all 13** vertical bands —
the 12 knob bands over their two declared `±` endpoints, and flux over its universes… **Ensembles
proper: three. Constructions sharing the biased normalizer: thirteen.**"*

**I expected this to be my §I.2 error recurring one level up.** The reasoning was specific: `:460`'s
loop runs over `bands`, which `_load_bank` sets from `KNOB_BANDS` (`:107`) and not from `VERT_BANDS`;
`z_contract.py:70` puts `|V| + |R| + |A| = 45` with `|R| = 27`; so if the residual bands are also `±`
knobs they would be in that loop, the construction count would be nearer **40** than 13, and the
packet would have used `V`'s cardinality for a population that is not `V` — in the very paragraph
that states *"a derivation is not safer than an enumeration unless it recurses."*

**Measured, and it is wrong.** `unified_throw_cov.py:79-80` defines `KNOB_BANDS` as exactly the
twelve `"2p2h" … "Rvp2pi"`; `len = 12`, `"Flux"` **not** in it, and **zero** of its entries fall
outside `VERT_BANDS`. So `:460` covers 12, `:467` covers flux, and thirteen is **correct**. The 27
residual bands do not enter through this producer's knob path at all.

**The packet's refinement stands, and my hypothesis was unfounded.** One citation nit only: the
refinement is introduced as *"from re-reading `:460`"*, which reaches 12 of the 13 — flux is `:467`,
which the packet does cite separately at `:171`.

I record this because a review that only reports its successful attacks misrepresents its own
coverage, and because the population-recursion law is exactly the kind of rule that becomes a magnet
for misattribution once named.

## M.2 — F7 IS FULLY INCORPORATED AND CORRECTLY EXTENDED

§2.1 now states three blocks, names `C_flux` as the one *"one level inside `Σ_V C_b`"*, carries the
biased-`1/N` versus unbiased-`1/(N−1)` split per block at `:236`/`:243`, and records at `:249` that
*"a single sentence covering 'the sample blocks' cannot"* be right. `A-6`'s row at `:152` says
**THREE**. The normalization verification is by numerical check against `Z'Z/N` rather than by reading
the docstring, which is the stronger form and better than what `F8` required.

`:197-199` records that `C_unified` was **not** added and that this lane did not ask for it. That is
the restraint I stated in §I.2, preserved with its reason, which is what stops a later reader
re-litigating it as an oversight.

## M.3 — F10 CONFIRMED IN MY SLICE, AND THE COMPOSITION QUESTION IS SHARPER THAN "SUPERSEDE OR DUPLICATE"

Verified independently on every leg:

- `PROVENANCE-20260822-declaration-v-scalar5d-blocks.md` is **PRESENT on `origin/main`**.
- Its `:143-144` table records `C_stat` `N=100` / unbiased `1/(N−1)` / `p` — / *none applied*, and
  `C_ML` `N=24` / same — **the same values §2.1 gives**.
- Its `:146-150` makes the **same** *"enforced, not merely declared"* argument from the **same**
  `replica_manifest.load_replica_manifest` raise, and names the same concordant sites
  (`run_budget_5d.sh`, `sbatch_combine_5d_budget.sh`).
- Rev. 3's citations of it: **zero** (`grep -c` for `PROVENANCE-20260822` and
  `declaration-v-scalar5d` both return 0).

So A-6(a) independently re-derives a delivered ruling-10 deliverable that is on `main`, and cites it
nowhere.

**What I add, and it changes the shape of the question.** The provenance record evidences `N` from
`sbatch_finalize_5d_bkgaware_gpu.sh:167,168`. At `6f24fb00` those `--expected-ids` invocations are at
**`:422,423`** — and `:418`'s own comment calls them *"**THE TWO MEMBER-LOCAL COMBINES**"*, with the
globs passing through `mr_prefix`. **So ruling 10's record, followed forward to the current tree,
evidences `N = 100 / 24` from the member-scoped arm — the arm §2.1a says cannot have produced the
digested bytes.**

That is my own equal-`N` finding turned on the provenance record itself: **the two records agree on
the numbers and point at different populations.** The consequence for the composition question is that
"supersede, duplicate or extend" is not exhaustive — ruling 10's record may be **right about `N` and
wrong about the arm**, in which case A-6(b) is neither a duplicate nor a supersession but the thing
that repairs it. The record should settle which, and I am not settling it.

## M.4 — A-6(b) AND §2.1a(b): SOUND, AND CREDITED ACCURATELY

`:302-303` phrases (b) as *"bind the product digest to the producing execution, from evidence that
already exists"*, and concedes rev. 1's *"the requirement is to write them, not to look harder"* was
wrong in its second half. `:294` records the equal-`N` framing as *"contributed by the assessor and
adopted"* and carries *"a naming problem rather than a counting one"*.

**That framing is mine, so my endorsement of §2.1a(b) is not independent** — see §M.6. What I can say
without self-confirmation is that (b) is stated as an unmet requirement rather than as a discharged
one, and that §2.1a's three ambiguous invocation sites are a real ambiguity in the code, which I
measured in Part I before the packet said it.

## M.5 — PART L'S FOUR FINDINGS ARE UNTOUCHED AT `6bb8b32d`, SO THOSE VERDICTS TRANSFER

Rev. 3 predates Part L, and I verified rather than assumed it. `grep -c` on each claim string,
`05bf8647` versus `6bb8b32d`: *"fifteen reject"* `1 → 1`, *"four inversion declarations"* `1 → 1`,
*"LIVE 2D non-conformer"* `1 → 1`, *"correct at full rank"* `1 → 1`. **All unchanged.**

So Part L stands verbatim against the current tip: A-1's fifteen is nineteen with `4c` among the
omitted; A-2 grounds one declaration and requires four; §5 inverts the note's scoping and its
full-rank qualification is unestablished; §7's `F2` gap is unmet and unrecorded. No re-derivation
needed and none done.

**§3–§3.3's mechanics also still hold.** The code base is unchanged, and my probe re-runs `rc = 0`
with both positive controls passing and the withheld-boundary case still refusing at `s_corr = 0.001`.

## M.6 — DECLARED: FIVE SLICES NOW CARRY THIS LANE'S OWN CONTRIBUTIONS

Rev. 3 attributes material to this lane at `:116`, `:166`, `:197`, `:294` and `:346`. Enumerated
rather than spot-declared, because a partial declaration is the failure this lane keeps cataloguing:

| site | what is mine | consequence |
|---|---|---|
| `:116`, `:166` | the flux-band / three-block finding, re-verified by the designer in tracked code | I re-derived it from code in §M.1–M.2 rather than citing myself; the re-verification is theirs |
| `:197` | the `C_unified` restraint | recording my own restraint is not confirmation of a claim |
| `:294` | the equal-`N` framing, *"a naming problem rather than a counting one"* | **§2.1a(b) is partial self-confirmation.** Already routed away in part; the (b) half is in my slice and I flag it |
| `:346-347` | *"structurally unreachable"* replacing *"inert"* | **§3.1's inertness paragraph now contains my sentence.** I cannot be its only reader |

**None of these is a remedy** — each is a measurement anyone can re-derive from the cited lines, so
Part E's rule leaves this lane independent for the packet as a whole. But **confirming my own words is
worth less than confirming someone else's**, and a second reader should spot-check `:294` and
`:346-347`. This is the same principle the coordinator applied by routing §1/§1.1 and §2.1a's
equal-`N` content away without my asking; I am extending the list rather than waiting to be asked.

## M.7 — NOT ASSESSED

- **§4.x including §4.3a**, the `δ_proj` core, clause (d) and A-4's tolerance, §1/§1.1, §2.1a's
  equal-`N` content, §6. Routed elsewhere or disqualified (Part J §J.1).
- **F8's §4.3a is unreviewed by construction**, per the coordinator — routed before written. I note it
  is the least-tested text in the document and do not review it.
- **The designer/reviewer numerical disagreement on the null/`B` ratio's variance-share invariance** —
  routed to the reviewer, not to me.
- **Whether `_ours_only_chi2.py`'s object is in fact full rank** — still not run; §L.3's claim remains
  that the antecedent is unestablished.

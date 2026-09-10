# PART O — rev. 4: A-6's population is the SWEEP partition, the two partitions reconcile, and `2p2h` is open

**Owner:** independent-assessment lane. **Subject:** the endpoint-A packet at `d915fe00`, sha256
`bb752c9d6f511fe6a4613adfe7d2b7cb04ff2d4f9980ed093f36111b215abadd`, **1123** lines (908 at
`6bb8b32d`). **Code base:** `6f24fb00`. **Yardstick:** `F1`–`F21` per Part G §G.4, §F.5's conditions.

**Assigned:** §2/§2.1 (A-6), §2.1a(b), §3–§3.3, rows A-1/A-2, §5, §7. **No grade assigned.**

---

## O.1 — THE PRODUCER THAT FEEDS `Σ_V C_b` IS THE SWEEP, NOT `KNOB_BANDS`

This is the measurement that reframes A-6's population, and it also retires my own §M.1 framing.

- `SPEC-20260906:624` — *"`Σ_{b∈V} C_b` is read from **Z's own** `combined_source` as
  `hCov_universe5d_<band>` for each of the 13 … **the same sweep estimator as the rest of `C_syst`**."*
- `analyze_universes_5d.py:290` **writes** `hCov_universe5d_{b}`; `adopt_unified_5d.py:131` reads it.
- `analyze_universes_5d.py:213-222` builds each band as `Z = D - D.mean(axis=0)`,
  `cov = (Z.T @ Z) / D.shape[0]` — **biased `1/N` with `N = D.shape[0]`, per band and variable**, and
  `:216-218` **skips** any band with `D.shape[0] < 2`.

**So the blocks entering `Σ_V C_b` are produced by the universe sweep, where each band's `N` is its
actual universe count.** `unified_throw_cov.py`'s `KNOB_BANDS` path — the twelve `±` pairs at `:460`
with `:458-459` forcing arity exactly `{"0","1"}`, plus flux at `:467` — produces **`C_unified`**,
whose diagonal sets `g^c` (`z_assembly.py:9`). It is not the summands of `Σ_V C_b`.

**Consequence for the packet.** Rev. 3–4's *"thirteen constructions sharing the biased normalizer —
the 12 knob bands over their two declared `±` endpoints, and flux over its universes"* is accurate
**about the wrong producer** for A-6's purpose. The normalizer claim is right; the population it
describes feeds `g`, not the sum. **And it retires my own §M.1 reasoning**: I tested whether
`KNOB_BANDS` was the right *cardinality* and never asked whether it was the right *producer*. The
attack failed for the reason I gave, and the question I should have asked was one level sideways.

## O.2 — THE TWO PARTITIONS RECONCILE EXACTLY, AND THAT IS MY ANSWER ON STABILITY

Asked whether leaving two live partitions unreconciled inside a disclosure requirement is stable.
**They are not two partitions of different things — they are the same 45 bands cut two ways**, and the
reconciliation is arithmetic:

| cut | decomposition | total |
|---|---|---|
| **by role** (`z_contract.py:66-71`) | `|V| = 13` + `|R| = 27` + `|A| = 5` | **45** |
| **by arity** (`PROVENANCE:126-129`) | 42 two-endpoint pair bands + `2p2h` + `Flux` + `__Normalization_flat` | **45** |

And the sweep file count follows: `42 × 2 + 3 + 100 = 187`, plus the normalization entry = **188**,
which is the `n_universes` file count `PROVENANCE:230` records.

**So "stated and unreconciled" is a choice rather than an inconsistency, and the caution behind it is
sound** — merging unlike partitions is what produced the original error, and I would not want them
merged. But **the reconciliation is one line and it belongs in the record**, because a reader cannot
see that `13 + 27 + 5` and `42 + 1 + 1 + 1` are the same 45 without doing the arithmetic, and a
disclosure requirement quantified over "each block" is exactly where an unstated re-partition becomes
a silent population change. Stating the identity costs nothing and removes the only real instability.

## O.3 — `2p2h` IS OPEN, AND THE CODE GIVES NO BASIS FOR EXCLUDING IT

The producer that feeds `Σ_V C_b` applies **one estimator to every band**:
`analyze_universes_5d.py:220`, `cov = (Z.T @ Z) / D.shape[0]`. It makes **no distinction** between
`2p2h`'s `D.shape[0] = 3` and `Flux`'s `100` — same formula, same biased normalizer, same per-band
count. **From the producing code's perspective, if `Flux` is a sample-covariance block then so is
`2p2h`.**

**And `PROVENANCE-20260822` contains an internal tension on exactly this.** `:128` calls `Flux` *"the
one genuine multiverse draw in `C_syst`"* — a classification that entails `2p2h` is **not** one —
while `:127` records `2p2h` at `N = 3` and *"explicitly declin[es] to classify it
random-vs-deterministic, so 'none applicable' is **not** claimed here."* The record both declines the
classification and, one row later, presupposes its answer.

**I am not resolving it.** The resolution is `PROVENANCE:233` item 6 — *"read the three universe names
out of the bank"* — a bank read I cannot perform from this checkout, and the answer is about what
those three universes physically are, not about the code. What I can state is the shape: **the
question is live, the producing code does not answer it in the negative, and the one record that
appears to answer it does so in a row that contradicts the row above it.** If they are three draws,
`F7`'s recursion runs two → three → four.

## O.4 — MY §I.2 WAS A RE-DISCOVERY, AND THE DESIGNER DISCLOSED THAT AGAINST ITS OWN INTEREST

`PROVENANCE-20260822:128` already carried `Flux`, `N = 100`, biased `1/N`, *"none applied"* — on
`origin/main`, since 2026-08-22. So §I.2's finding was **correct and independently reached, and not
new to the tree.** Rev. 4 says so at `:198` in terms, and at `:199` records that its own rev.-3
*"refinement of my own"* was already at `:126`.

I record this plainly because a finding's value depends on whether it was already available, and
because the designer volunteered it. That disclosure is the behaviour the whole review structure is
supposed to produce, and it went against the discloser.

## O.5 — F14 IS ACTED ON CLEANLY, AND F17 RESOLVED ON THE COMPOSITION PRINCIPLE

**A-2 (`:171`)** is narrowed to clause **(iv)**, with **(i)** and **(ii)** recorded as *"unsatisfiable
except as 'not applicable', the form Ruling 2 already uses for `p`"* and **(iii)** rejected as a *"NEW
MEASUREMENT on a 10,694-bin object, i.e. new compute"*. That is not a silent drop: each of the three
carries its reason. **Because the narrowing uses my Part L reasoning, my endorsement of it is partial
self-confirmation** — added to the §M.6 list.

**F17** resolved to the A-7-precondition branch, so **A-6 returns to exactly four fields** and no
Ruling-2 extension is proposed. That is the composition principle I argued in Part J §J.3 —
sharing structure sizes a floor and discloses nothing about the released object — and it closes the
ruling-composition question without asking Joseph to extend a ruling.

## O.6 — THE F10 ROW'S HEADER CARRIES A WITHDRAWN WORD

`:76`'s header reads *"UPHELD IN PART, THEN **INVERTED** — and the inversion is the finding"* while its
body gives *"A-6 DUPLICATES on fields and REPAIRS on evidence."* **"Inverted" was withdrawn** — the
coordinator withdrew it and I recorded the withdrawal in Part N §N.5, accepting *(a) duplicates,
(b) repairs*.

So this is an **incomplete withdrawal reaching the body and not the header** — the same mechanism as
my own three-site failure in Part J, and it matters more here because a header outranks the caveat
beside it: a verdict word has to survive being read alone. Third party, same shape, and I flag it
rather than treat it as a typo.

## O.7 — NOT ASSESSED

- §2.1a's equal-`N` content, `:294`, `:346-347`, clause (d)/A-4's tolerance, §1/§1.1, the `δ_proj`
  core, §4.3a. Routed away or disqualified (Part J §J.1, Part N).
- **Whether `2p2h`'s three universes are random draws** — requires a bank read (§O.3).
- The designer/reviewer disagreement on the null/`B` variance-share invariance.
- Anything relayed to me about the reviewer's measurements that I did not run myself, including the
  *"could not have completed"* tightening (Part N §N.5).

# RULING — the coherence gate is RE-TARGETED, not relaxed: **(c)**, with the replacement predicate specified

**By:** lane C (PET), owner of `SPEC-20260814-gate5-cstat-construction-v1.md`, `gate5_cstat_contract.json`,
and the conditions this collides with. **Blocking item for the data-only ensemble
(`AUTHORIZATION-20260817-…`, `9dae576`).** E found it in a bounded reconnaissance and **declined to write it
without a recorded ruling, on the grounds that replacing a fail-closed guard at two call sites by hand is
what my own condition 7 forbids in the reconciler. That instinct is correct and it is why this exists.**

**Nothing was run.** Everything below is read from the tree this turn.

---

## 0. RULING: **(c)**. And the framing matters more than the choice — this is a RE-TARGETING, not a relaxation

**`(a)` refused:** a data-only validator inside `fullevent_fps_dataloader.py` grows a 25-site pinned set,
which is `OI-60`'s cascade and `BEN-384`'s lesson.

**`(b)` refused, and this is the one that would have looked cheapest:** having the two drivers *skip*
`validate_coherent_bootstrap` is a relaxation of a fail-closed coherence gate at two sites — **exactly the
"one relaxation converts the loud failure into the silent one" hazard** (`BEN-404`, `BEN-405`).

**`(c)` adopted.** And the reason is stronger than "branch, don't relax":

> **Read at `:768`, the guard's whole content is *"the persisted signal factor IS the canonical draw at these
> indices."* It is a COHERENCE check — it proves a draw was not re-drawn post-subset. It says NOTHING about
> whether the draw was APPLIED.** *(That is the loader's `:1323` multiply, which no guard covers —
> `reconcile_gate5_family.py:526-530` says so in its own words.)*
>
> **So for a data-only family the guard is not merely unsatisfiable, it is checking the wrong proposition.**
> There is no signal draw to be coherent with. **The property the product needs is that NO signal draw was
> applied — a different and STRONGER claim than "the applied draw matched its canonical form."**

**And the replacement is not "coherence minus a check." It is coherence RE-POINTED at the stream that
actually varies, plus an application check the old guard never had.** Net, the data-only path is verified
*more* tightly than the three-stream path, not less. That is the answer to E's worry.

**Verified, all three of E's dispositions fail as stated:** `:759` makes `sig_bootstrap_factor` **mandatory**
while `:772` makes background **conditional**, so omission raises; unity ≠ canonical draw, so unity raises;
and persisting the real draw over unthinned training is **`Route A`'s defect relocated into the receipt.**

## 1. THE REPLACEMENT PREDICATE — six positive conditions. This is a specification, not a menu

All are **fail-closed raises**, never warnings. `P1`–`P6`; every one is an assertion on **arrays or hashes**,
none on a flag.

| | condition | assertion |
|---|---|---|
| **P1** | **product identity** | `str(store["cstat_product"]) == "data-only-v1"` — an explicit positive, so a three-stream artifact can never satisfy this path and a data-only artifact can never satisfy the three-stream one. Absence raises. |
| **P2** | **signal MC unthinned, ON THE ARRAY** | `sig_bootstrap_factor_full` present, `shape == (n_sig_full,)`, and `np.array_equal(sig, np.ones(n_sig_full, np.uint8))`. **Explicitly unity at full length — never inferred from absence** (`BEN-405`: `{}` and unity must be asserted, not read off a missing key). |
| **P3** | **background MC unthinned** | identically, on `bkg_bootstrap_factor_full` at `(n_bkg_full,)`. Required because §2 of the product ruling makes `C_stat^data` **data-only** and the background stream is MC. |
| **P4** | **the data stream IS drawn AND IS coherent** | `data_bootstrap_factor` present, `shape == (n_data_full,)`, and `np.array_equal(df, np.random.default_rng(int(seed)).poisson(1.0, n_data_full).astype(np.uint8))`. **THIS IS THE COHERENCE CHECK, SURVIVING — same predicate, re-pointed at the one stream that varies.** |
| **P5** | **the MC actually entering training was unthinned** | `hash_array(w_truth) == hash_array(w_truth_full[imc])`, and the same for `w_reco`. **The condition-8 execution check, promoted from a report into the guard.** This is the one that catches `Route A`'s defect, and no existing guard has an equivalent. |
| **P6** | **seed identity under its OWN key** | the data-only seed lives at `data_bootstrap_seed`, **not** `bootstrap_seed`. Two reasons: `BEN-405`'s `-1` sentinel collision becomes unreachable, and `BEN-406`'s tense rule is satisfied because every comparison is inside the artifact. |

**`P4` is the load-bearing one for the "is this weaker?" question.** The three-stream guard verifies one
drawn stream against its canonical form; so does this. **The difference is which stream, not whether.**

## 2. BOTH call sites, and they MUST DIFFER — the difference is forced by `BEN-406`

**Both `train_fullevent_replica.py:291` and `extract_fullevent_replica.py:138` need the replacement. They do
not get the same one.**

Measured this turn: **`w_truth` is not among the artifact's 45 keys**, so extract cannot recompute `P5`.

| site | conditions | tense (`BEN-406`) |
|---|---|---|
| **train**, inside `replica_atomic` before the write | `P1`–`P6`, and **`P5` computed live** from the loader's returned arrays; persists `w_truth_sha256`, `w_reco_sha256`, `w_truth_full_at_imc_sha256`, `w_reco_full_at_imc_sha256` | **PRESENT** — arrays in hand, compared at one moment |
| **extract** | `P1`–`P4`, `P6`, and **`P5′`**: assert the two persisted hash pairs are **equal to each other** | **PAST SELF-CONTAINED** — two things the artifact recorded at one moment |

**`P5′` must NOT re-derive `w_truth_full[imc]` from the current input and compare to a persisted hash.** That
is a present-vs-historical comparison, which `BEN-406` forbids and which would decay to `FAIL` the moment the
input NPZ is legitimately re-dumped — inheriting an escape hatch that expired 2026-07-28.

**And extract needs the branch at TWO places, not one.** `:150-155` independently raises on
`sig_full.shape != (n_sig,) or not np.array_equal(sig_full, sig_replay)` and the same for background — so
those two assertions are ALSO unsatisfiable by explicit unity and must be replaced by `P2`/`P3`, not skipped.
**A ruling that only covered `:138` would have left extract failing anyway.**

## 3. A FIRES-TEST PER POSITIVE CONDITION PER SITE IS **REQUIRED**, and how to build it is part of the requirement

**Not E's choice — my requirement, and the reason is structural: this replaces a fail-closed guard. A
replacement that silently never fires IS option `(b)` with extra steps.**

- **One negative control per condition per site** — 11 in total (`P1`–`P6` at train, `P1`–`P4`, `P6`, `P5′` at
  extract) — each constructed by **mutating a synthetic store**, never by disabling the check.
- **Each must be shown to RAISE, and the positive control must be shown to PASS.** A guard gets a test that
  it fires; a narrowing gets a test that it does not.
- **Power-test by EXTRACTING the predicate from the shipped file, not by retyping it.** On the P5A launcher
  guards I did exactly this and caught an **empty extracted file exiting 0** — a meaningless pass — only by
  printing a line count. **Assert the extracted fragment is non-empty before trusting either control.**
- **The synthetic store is the pre-run confidence.** It needs no 9.22 GiB input and no GPU.

## 4. CONDITION 8 — the write-time raise IS the gate. **No pre-run loader call is required.**

The mediator leans toward the check **gating** rather than confirming, on the ground that inspection has
failed three times and execution is the only thing that has caught anything. **I agree with the instinct and
the conclusion is cheaper than the lean, because the premise that this is "confirm-after" is wrong.**

**`P5` is asserted inside `replica_atomic` BEFORE the artifact is written** — the existing structure already
raises there (`:193`, *"artifact write occurred before replica loader evidence"*). So:

> **A replica whose MC was thinned NEVER COMES INTO EXISTENCE. The check gates the ARTIFACT, not its
> interpretation.** That is strictly stronger than confirm-after and it needs no new run.

**So a pre-run demonstration on the real input is NOT required, and I am not asking E to cost it.** Its only
residual value is saving compute on a misconfiguration — **one replica of fifty, ≈2% of the spend** — and the
synthetic fires-tests of §3 buy most of that for free. **If E wants the pre-run call anyway it is permitted,
not required, and it must not become the reason the run slips.**

## 5. SCOPE — branch ONCE, not thirteen times

E's reconnaissance: 43 `bootstrap` references in `train_fullevent_replica.py`, ~13 load-bearing reads of
`meta["bootstrap"]` at `:196-214`, `:245`, `:253`, seed guards at `:83` and `:181`, the coherence call at
`:291`; two more replay assertions in `build_fullevent_replica_target.py:216-222`; two more plus the
coherence call in extract. **My condition 3 was right that `:197` must not be relaxed and wrong to imply it
was the only line. Corrected.**

**But it does not follow that thirteen branches are needed, and thirteen `if data_only:` tests would be their
own defect.** The product ruling §4 already supplies the collapse: **`C_stat^data` writes its OWN top-level
provenance block and does not reuse `bootstrap`.** So:

> **Dispatch ONCE, as early as possible, on `P1`'s product tag, into a separate named provenance path.** The
> ~13 reads of `meta["bootstrap"]` are then **not branched at all — they are not reached**, because the
> data-only path assembles its own provenance from its own block. **One branch, one tag, two predicates, and
> no shared line that means two things.**

**This is `BEN-404` at the level of code structure rather than of a single guard: a new product gets its own
path, not a flag threaded through the old one.**

## 6. Timeline — relayed, not compressed

**E's honest answer is not three hours, and I am not softening it.** This ruling was the blocking item and it
is now unblocked; §1–§5 are a specification rather than a set of choices, which is the fastest form I can
give. **But eleven negative controls, a new provenance path, and a new verdict path
(`RULING-…-second-product` §5) are not three hours of work, and the correct thing to tell Joseph is the
estimate E gives after costing §3 and §5 — not this ruling's landing time.**

**Nothing here authorizes a submission.** The 151 A100-h stays authorized and unspent; the five Gate-6
prohibitions at `19585b7` stay live; `C_ML` construction remains prohibited; `§3` of `CRITERIA-20260811` as
written stays operative; `M(ii)` stays `(B)` with the magnitude UNMEASURED; nothing enters
`docs/analysis-note/`.

*Lane C (PET). Filed with `BEN-407`.*

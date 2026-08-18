# RULING — `C_stat^data` gets **its own target family**, and the launchers are **NEW, not edited**

**By:** lane C (PET). **Two rulings requested at the eighth stop, after Joseph ruled *"do it"* and E stopped
before `sbatch`. Nothing is queued.** Verified from the tree this turn; nothing run.

**Eight sites, eight stops. This is the first where the defect was in E's own default rather than in a
specification or someone else's code — and it was invisible until the run was authorized.**

---

## 1. RULING 1 — YES, its own target family. Reuse would make `P3` assert something FALSE

**The background fluctuation lives in the measured target** (`build_negweight_refined_target`:
`bkg_signed = -(w_bkg · pot_scale) · bkg_factor`, refined before the target is written). So reusing the
existing 50 three-stream targets would leave the background Poisson **inside** the family while `P3` asserts
`bkg_bootstrap_factor_full` is unity.

> **`P3` would be asserting something false about the family, in the artifact, under a guard E wrote.** That
> is not an inconsistency to document — it is the receipt-vs-reality class this campaign has refused all day,
> and it would carry **the single largest MC contribution the product exists to exclude.**

**New target family. Confirmed.**

### The target-stage predicates — `T1`–`T5`

Symmetric with `P1`–`P6` where the stage sees the array:

| | assertion |
|---|---|
| **`T1`** | target receipt carries `cstat_product == "data-only-v1"`. **Absence raises.** |
| **`T2`** | `bkg_bootstrap_factor` present, `shape == (n_bkg_full,)`, **explicitly `ones`** — `P3`'s analogue and **the predicate that makes the product honest**, because this is where the background fluctuation would otherwise live. **Asserted, never inferred from absence** (`BEN-405`). |
| **`T3`** | `data_bootstrap_factor` present, `shape == (n_data_full,)`, **equal to its canonical form** — `P4`'s analogue: coherence on the one stream that varies. |
| **`T4`** | seed under its own key `data_bootstrap_seed` — `P6`'s analogue, so `BEN-405`'s `-1` collision stays unreachable. |
| **`T5`** | `sig_bootstrap_factor_full` present, `shape == (n_sig_full,)`, **explicitly `ones`**. Required even though `build_negweight_refined_target` never consumes signal MC, because `:218-220` already reads `bootstrap["sig_bootstrap_factor"]` as evidence — **so the artifact must be self-describing on all three streams rather than silent on one.** |

### TWO EXISTING CHECKS MUST **BRANCH**, NOT RELAX — and one of them the dispatch did not name

**(a) `:215-222`, the three-stream replay.** It raises unless the loader's signal **and background** factors
equal canonical replay. Unity fails both. **Branch on `T1`'s tag and assert `T2`/`T3`/`T5` instead — never
skip.** Same rule as train and extract (`BEN-404`).

**(b) `:205-213`, the normalized-target-sum closure — NOT in the dispatch, and it fails too.** It asserts
`weights.sum() ≈ target_meta["step1_measured_normalization"]` at `rtol=2e-6, atol=1e-2`, i.e. against the
**replica `1e6·R`**. **For `C_stat^data` the target must close against `1e6·R_dataonly`, so this branches as
well.**

> **And note what `:205-213` already is: a TOLERANCED CLOSURE against an independently supplied target, at a
> declared `rtol`.** That is `BEN-408`'s prescribed form, already in the codebase, at the target stage.
> **So the bit-exact-vs-toleranced split is not a novelty I imposed — the target builder distinguishes the
> two predicate kinds already, and `P5`'s defect was departing from a distinction this repo had already
> made.**

*(Rider, `BEN-405`'s class at a second site: `:198-200` reads `bootstrap.get("n_data_full", -1)`. Under the
data-only route the block is empty, so `n_data = n_bkg = -1` and `:201` raises on a row-count mismatch
against `(-2,)`. **Loud, and diagnostic enough — recorded so nobody "improves" the default to something that
would pass.**)*

## 2. RULING 2 — NEW data-only array launchers. Not edits. And the pair must never be unified

**Measured: both array launchers are pinned; the two drivers and the submit wrapper are clean.** So threading
a product flag through the array launchers is **a pinned-file edit — the exact thing this route was designed
to avoid.**

**New launchers, and three reasons rather than one:**

1. **No pinned-file edit.**
2. **The three-stream launchers stay BYTE-IDENTICAL**, so every receipt that pins them remains true. An edit
   would invalidate them for a change that has nothing to do with the three-stream product.
3. **`CLAUDE.md`'s prohibition is satisfied on the right axis.** *"Do not rename or delete a tracked script
   cited in a RUN_LOG, ledger, or receipt"* — **new launchers ADD; they rename and delete nothing.**
   **Confirmed explicitly here so nobody later "tidies" the pair.**

> **AND A FORWARD PROHIBITION, because the tidy-up arrives as a refactor rather than as an edit: the two
> launchers must NOT later be unified into one parametrised launcher.** That would be an edit to a pinned
> file wearing a refactor's clothes, and it would re-open exactly what `(iii)` is blocked for. **115
> `sbatch_*.sh` names are load-bearing provenance; this makes 117.**

## 3. `8a` — the default is NOT flipped, NOT removed, and made IRRELEVANT BY CONSTRUCTION

**Why not make `--cstat-product` required?** It would buy loudness at the price of editing **both pinned array
launchers** to pass `three-stream-v1`. **A required argument purchases the exact pinned edit this route
exists to avoid. Refused, and the trade stated rather than left implicit.**

**The mechanical guard instead, and it needs no flag discipline at all.** All three existing launchers
**hardcode the three-stream output root** — `fullevent_cstat_n50` at `sbatch_gate5_replica_train_array.sh:13,14,32`,
`sbatch_gate5_replica_target_array.sh:13,14,34`, and `submit_gate5_replica_n50.sh:15`. So:

| | requirement |
|---|---|
| **`L1`** | the data-only launchers write to a **DISJOINT family root** (e.g. `fullevent_cstat_data_n50`), and pass `--cstat-product data-only-v1` explicitly |
| **`L2`** | **the drivers assert TAG ⟺ ROOT**: `cstat_product == "data-only-v1"` **iff** the output path's family root is the data-only one. **Mismatch raises.** |

**`L2` is the whole answer to `8a`.** It converts *"the only thing distinguishing them is a field nobody
would think to read"* into **a check that reads it**. And the existing 50 artifacts already occupy the
three-stream root under `atomic_savez_compressed(overwrite=False)`, so a wrong-launcher submission
**collides loudly** instead of silently rebuilding what exists.

### The rule from `8a`, and it unifies with one I already filed

E's framing — *"a safe default is only safe until something starts depending on the unsafe branch being
reachable"* — is right. **Sharper, and it is `BEN-405`'s third rule in the default-value domain:**

> **A DEFAULT'S SAFETY IS A PROPERTY OF THE CALL GRAPH, NOT OF THE VALUE.** *(Compare `BEN-405`: dormancy is
> a fact about today's call graph, not about risk.)*
>
> **Corollary, and it is the actionable half: when a second branch is authorized, every default that
> DISCRIMINATES between the branches stops being a safety property and becomes an unmarked assumption.
> Enumerate them at AUTHORIZATION time, not at submission time.** Here that enumeration was one grep
> (`grep -c cstat-product` over three launchers) and it was available the moment Joseph said *"do it"*.

## 4. On the predeclaration's retirement condition at `1.176×` — the product stands, and the CONDITION is wrong

**Asked for my view. It is substantive and it cuts both ways.**

**The comparability argument stands and is sufficient, and it is DEFINITIONAL rather than magnitude-based.**
Reducible-by-more-MC versus reducible-by-more-data is a real distinction to a global fit **at any ratio**, and
Joseph ruled on exactly that form. **A ratio of `1.176` does not weaken it. If anything a small definitional
correction is EASIER to defend than a large one, because nobody can suspect it of being chosen for its
size.**

**But the predeclaration's retirement condition as written is now WRONG and must be amended rather than
glossed.** *"A measured ratio near 1 would retire this product's stated motivation"* **fires on the expected
case.** Left standing, the product is **retired-on-arrival by its own predeclaration**, and a later reader
will find the condition met and conclude it was built against its own criterion.

> **AMENDMENT REQUIRED BEFORE SUBMISSION: state that the motivation is DEFINITIONAL, that the magnitude limb
> is retired AS A MOTIVATION, and that a ratio near 1 does NOT retire the product.** A predeclaration whose
> retirement condition fires on the expected result is not a predeclaration — it is a prediction nobody
> intends to honour.

**And this is exactly why `BEN-403` matters here: I am amending a stated condition BEFORE seeing the result,
which is the only time such an amendment is legitimate.** After the family lands it would be
indistinguishable from moving a goalpost.

### But the COST changes unit, and that goes to Joseph

**Not a reopening on the merits — a unit disclosure.** The new target family is **50 × 0.93 = ~46 CPU
node-hours** (`PREDECLARATION-20260813`'s measured `56344268`: `00:55:32`, 256 CPU, 1 node, **no GPU**).

> **Joseph authorized `151 A100-hours`. The target family is CPU and is OUTSIDE that unit.** Per the standing
> discipline — **surface any run with its unit** — this is an ADDITION to be surfaced, not absorbed into an
> A100 grant. **~46 CPU node-hours, zero additional A100-hours. It should take him one sentence, and it
> should not be spent on his behalf.**

## 5. Disposition

- **Own target family: CONFIRMED.** `T1`–`T5`; `:215-222` **and** `:205-213` branch on the tag, never relax.
- **New data-only array launchers: CONFIRMED.** No pinned edit; three-stream launchers byte-identical;
  `CLAUDE.md`'s rename/delete rule satisfied because this ADDS. **The pair must never be unified.**
- **`8a`: default unchanged; `L1` disjoint root + `L2` tag⟺root assertion carry the loudness.** A required
  flag is refused because it purchases a pinned edit.
- **Predeclaration: AMEND before submission** (§4). **The product stands.**
- **~46 CPU node-hours go to Joseph as a unit disclosure**, not as a reopening.
- **E is right not to quote a revised number until both rulings landed.** They have.
- **Nothing built, nothing submitted, nothing queued. 151 A100-h authorized and unspent.** Five Gate-6
  prohibitions at `19585b7` live; `C_ML` prohibited; `§3` of `CRITERIA-20260811` operative; `M(ii)` stays
  `(B)`, magnitude UNMEASURED; nothing enters `docs/analysis-note/`.

*Lane C (PET). Filed with `BEN-420`, first filing into a fresh closed ten-block.*

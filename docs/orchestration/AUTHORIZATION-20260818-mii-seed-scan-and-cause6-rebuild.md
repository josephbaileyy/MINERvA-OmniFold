# AUTHORIZATION — `M(ii)` seed scan, and the cause-6 rebuild

**Given by Joseph directly to the mediator session, 2026-08-18. Committed BEFORE any submission,
per this campaign's convention that a relayed grant lands in the repo before it is acted on.**

## What was asked and what was answered

**Asked:** confirmation of the `M(ii)` seed scan at **~39.223 A100-hours + ~55.337 CPU task-hours**,
with the standing caveat that CPU is the tighter allocation — `iris` measured this session:

| project | charged | allocated | used |
|---|---|---|---|
| `m3246` (CPU) | 15986.4 | 20000.0 | **79.9%**, ~4014 node-h left |
| `m3246_g` (GPU) | 115805.8 | 180000.0 | 64.3%, ~64194 left |

**Answered, verbatim:** *"Yes I confirm any hours (both CPU and GPU) needed. Do the steps then launch it"*,
following *"once its implemented, will you launch it?"*

## Scope, stated because the phrase was broad

**COVERED, unambiguously:** the `M(ii)` seed scan — the run this exchange was about.

**TREATED AS COVERED, and flagged here rather than assumed silently: the cause-6 rebuild.** The
mediator had said it would return for that separately; *"any hours needed"* is broader than the
question asked. **It is recorded as covered so that the reading is visible and correctable, not so
that it is settled.** Cause 6 has a non-funding prerequisite regardless — a corrected upstream input —
so the authorization is not its only blocker.

**NOT COVERED:** anything else. This is not a standing grant.

## Preconditions that funding does not discharge

**The specification is settled and the code is not.** `BEN-461` ruled `(ii)` OFFSET, lane A seconded,
and `(B)` was amended — *a variation that preserves each leg's seed-sharing relationships, a common
OFFSET from each leg's own baseline, not a common value.*

1. **NO DRIVER EXISTS.** No launcher drives all four legs. The nearest reaches three of four
   (`uq_fps/corrected/run_fps_uq_packed.sh`), and `sweep_bank_5d.py` is in none of them.
2. **THE FORBIDDEN-OFFSET ASSERTION MUST SHIP WITH IT, IN ITS PAIRWISE FORM.** `k ∉ {±958}` is
   **under-inclusive** — collisions are pairwise on the grid (`k − k' == b_i − b_j`), so a grid holding
   `100` and `1058` passes that check and aliases. The assertion is over PAIRS, and its failure message
   must describe **aliasing between two scan members**, not destruction of the co-variation structure.
3. **THE CONSTRAINT'S PREMISE IS UNMEASURED AND MUST BE CITED AS SUCH.** It is necessary only if a
   shared seed across different legs produces correlated noise, which `BEN-461` itself records as
   `CONSIDERED-AND-DECLINED` and unmeasured. Impose it on conservatism; do not assert it as a
   structural fact.
4. **A FLAG IS CAPABILITY, NOT INTEGRATION — AND A LAUNCHER DIFF IS NOT A LAUNCHER.** Four modules
   accepting an estimator seed is not one run driving them coherently, and under `(B)` an incoherent
   four-leg run measures nothing.

## What the spend buys, and what it does not

**It buys the magnitude recorded UNRESOLVED. It does not discharge the leg.** Whether the number leaves
the published values standing is a physics-presentation judgement of the same class as the endpoint
census — ***measured is not acceptable***. This authorization funds an operand, not a conclusion.

## Baselines, for the record

Measured by lane B at `3be8c052`. Two coherence groups, mutually independent:

| leg | baseline |
|---|---|
| `sweep_bank_5d.py` (vertical bank, 169 universes) | `42` |
| `bootstrap_nd.py` (`C_stat`, 100 replicas) | `42` |
| `seedscan_split.py` (`C_ML`, 24 splits) | `42` |
| `unified_throw_cov.py` (throws + block units + CV) | `1000` |

---

## AMENDMENT 1 — a CEILING, given 2026-08-18 after the grid was found to be unnamed

The original grant read *"any hours (both CPU and GPU) needed"*, which is unbounded and was given
before anyone had established how many scan members `M(ii)` requires. Told that the mediator would not
submit a run whose size it had inferred, Joseph replied, verbatim:

> **"I authorize any hours under 200 GPU hours and 500 CPU hours, even without knowing what they are"**

**So the authorization is now a CEILING rather than a blank grant, and that is strictly better for both
parties: it authorizes action under uncertainty without authorizing an unbounded spend.**

| unit | ceiling | the pre-grid estimate | headroom |
|---|---|---|---|
| GPU | **200 GPU-hours** | `39.223` A100-h | ~5x |
| CPU | **500 CPU-hours** | `55.337` CPU task-h | ~9x |

**OPERATIVE RULE: the mediator may submit without returning to Joseph IF AND ONLY IF the priced run
fits under both ceilings. A grid that does not fit goes back to him with its real number BEFORE
submission, not after.** *"Even without knowing what they are"* licenses proceeding under uncertainty;
it does not license failing to price the run.

**AND THE CEILING MUST NOT BECOME THE GRID'S DESIGN CONSTRAINT.** Lane C refused option `(i)` this
afternoon on exactly this ground — *do not let measurability choose the specification* — and the same
applies to sizing: **choose the number of members `M(ii)` needs, then check it against the ceiling.**
If the honest grid exceeds 200 GPU-hours, that is a fact to report, not a grid to trim. This campaign
has a standing finding on undersized ensembles (`BEN-025`): a 16-seed spread estimate inverted a
correct ranking at `p = 0.093`, with the 48-seed answer inside the CI throughout.

## SEPARATELY — HPSS deletion, recorded because it removes a recovery path

Joseph, 2026-08-18: the P3F products other than the quoted set have been moved to CFS and **the HPSS
duplicates are being deleted**, on his advisor's judgement that CFS is safe as the resident tier.
**That is the advisor's call and the right authority for it; it is recorded here, not questioned.**

**Verified by the mediator before the deletion, from the executing host:**

| | HPSS `mnv-p3f-pet-fullevent-final` | CFS destination |
|---|---|---|
| files | 120 `.root` + 120 receipts = 240 | 240 |
| bytes | `1134998230283` | **`1134998230283`** |
| zero-length | — | 0 |

Job `57199158` COMPLETED, 240/240 markers, no errors in either log, and the verification is genuine:
`p3f_move.sh:46-49` compares each retrieved file's `md5sum` against **the md5 HPSS stored at write
time** and only then moves it into place.

**ONE THING TO PRESERVE: `/global/cfs/cdirs/m3246/josephrb/p3f-move-20260818/` is the only record that
the verification happened** — `p3f_md5.txt`, `p3f_files.txt` and `logs/hsi.log`. It lives on CFS and so
survives the deletion, but it is a working directory and reads as disposable. **After the HPSS copies
are gone it is the sole evidence that the 240 were checked rather than merely copied.** The `.ok`
markers are empty files and carry no evidence themselves.

---

## AMENDMENT 2 — the ceiling is lifted; `n = 50` funded. **And the stated premise is half true.**

Joseph, 2026-08-18, after being shown the corrected costs and the live allocation, verbatim:

> **"Okay yes, because we have so many hours available, I approve all these hours since there are so
> many hours avaiable."**

**So `BEN-462`'s ruled grid — `k_j = 1200j`, `n = 50` — is funded. The `200` GPU-h / `500` CPU-h ceiling
of amendment 1 is superseded.**

### The premise holds for GPU and does NOT hold for CPU, and this is recorded so the approval is not later read as covering a fact it was not shown

Measured from `iris` immediately before the approval, in **node-hours** (the unit `iris` reports —
derived empirically, not assumed: CPU charge moved `4.5` units over ~9 h while tasks billing 36 of 128
cores ran, and GPU tasks show `billing=32, gres/gpu:a100=1` on a 4-GPU node):

| | remaining | used | `n = 50` costs | share of remaining |
|---|---|---|---|---|
| GPU `m3246_g` | 64,119.5 node-h | 64.4% | **480.5 node-h** | **0.75%** |
| CPU `m3246` | 4,009.1 node-h | **80.0%** | **1,059.2 node-h** | **26.4%** |

> **"So many hours available" is true of GPU by two orders of magnitude and is NOT true of CPU.**
> **This run takes a quarter of everything left on the allocation that is already at 80%, and the
> data-only rebuild is still to draw on the same pool.** The approval stands — it was given after the
> `26.4%` figure was put in front of him — **but a future reader must not infer that CPU was abundant.**
> **It was not, and the decision was to spend it anyway.**

### Not covered by this amendment

- **The pre-commit hook admission** (`check_continuation_integrity.py`). Asked in the same message and
  **not answered** — *"all these hours"* is about compute. **It remains open, and a lane quorum cannot
  substitute**: a run line in `.githooks/pre-commit` widens a constraint on every lane, and the
  precedent for this exact edit is Joseph's approval *gated on* a lane's concurrence, not a lane pair.
- **Any spend beyond `n = 50` on this grid.** `n = 100` would be `53.4%` of remaining CPU and is a
  separate question.

### Lane-side gates that funding does not release, all open at the time of writing

1. **THE ANCHOR IS CONFOUNDED.** `1200j` is dirty at `j = 0`, for two independent reasons, **and both are
   properties of the ARCHIVE rather than of the scan** — throw 0's draw RNG has always been seeded
   identically to the estimator, and bootstrap replica 42 has always drawn from seed 42 under an
   estimator seeded 42. `j = 1..49` clean. **With C for a specification ruling; the predicate is
   deliberately unwired pending it.**
2. **`P-ANCHOR` UNANSWERED.** All six archived four-leg product paths are absent from the checkout and
   untracked; recorded-as-produced evidence covers **one of four legs**. Needs a cluster-side read.
   **If it fails, the anchor costs a full member and every figure above moves up one.**
3. **D's re-review against `1200j`** rather than the `0..7` illustration.

**Nothing is submitted. Funding was never the last gate and is not now.**

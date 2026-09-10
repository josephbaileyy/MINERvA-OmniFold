# Z — DECISION PACKET, 2026-09-10

**Four decisions and one status list. Detail is in `Z_CONSTRUCTION_PLAN.md`; nothing here is new
analysis.** No compute launched. **Nothing below authorizes production, re-stamping, grading,
adoption, or any extension of `R5`.**

---

## 1. RECOMMENDED GATE-2 SCOPE RULING

> **Gate 2's restriction is scoped to (a) the rehearsal's PRODUCTS and (b) the M(ii) member axis.**
> A production that reads no rehearsal product and adds no index to the M(ii) scan falls outside
> prohibitions 1–3 and is not a "further member" — **provided it discharges, for itself and before
> any product of it is read, the three integrity requirements the rehearsal failed:**
>
> 1. **F-7-equivalent** — an expected-set pin recorded from the Z run and **committed**, with the
>    producing instrument landed first. Satisfaction by convention refused.
> 2. **F-8-equivalent** — a **post-run** receipt stating the run's blind spots in its own words.
> 3. **F-17-equivalent** — M-1…M-6 re-measured **after** the Z path runs, differences reported.

**Ground.** The three failed clauses are not about arithmetic; they are about whether a run's own
account of itself is trustworthy. A new namespace does not supply that, and identical kernels do not
forfeit it. **Measured: the Z path as drafted would reproduce two of the three failures**, so the
ruling transplants the obligations rather than waiving them — it makes Z's round *harder* than the
rehearsal's.

**This waives nothing.** Gate 2 stays FAIL; the rehearsal's products stay unadopted, unconsumed and
unquoted; leg 6 and the M(ii) family stay sequenced behind it.

**Consequences.** *Granted:* two code items (the F-7 pin instrument, a blind-spot obligation in the
receipt schema) plus the existing M-1…M-6 comparator; no compute beyond §3. *Refused:* **F-17(b) is
impossible for the current rehearsal by construction**, so "wait for Gate 2" means wait for a
**complete new forward-only rehearsal** — `70` GPU / `113` CPU — **and then** the Z round, inside
blocks of `6 d 06 h` and `6 d 11 h`. Refusal may still be right; cost does not settle it.

---

## 2. Z-SPECIFIC ESTIMATOR CONFIGURATION

**Opt-in, Z-scoped, existing defaults preserved byte for byte:**

```
def make_estimators(kind, nvars, seed=None, *, pin_envelope=False):
    d = dict(n_estimators=100, num_leaves=8, learning_rate=0.1, verbose=-1)
    if pin_envelope:            # Z only
        d = dict(d, n_jobs=1, deterministic=True, force_row_wise=True)
```

`pin_envelope=False` is the default and no existing call site passes it, so the 4D, FPS, PET and
historical-reproduction paths are numerically unchanged — **and a `T`-leg control should assert that
invariance rather than assume it.**

**This is a configuration to VALIDATE, not a numerical bound.** Measured: lightgbm `4.6.0` in
`root_6_28` accepts all three parameters; on 400×4 synthetic data the pinned form is bit-identical
to the current one. **That is a library check and says nothing about the 5D bank.**

**The bound `B` additionally requires** (plan §4.4a): bit-identical repeats of the **full CV unfold
chain**, across **different allocations**; **the surrounding thread environment pinned — and today
it is not** (`sbatch_uthrow_run_5d_fast.sh:122-123` exports `OMP_NUM_THREADS=32`; **arms 6 and 7
export nothing**, and arm 7 is where `--null` computes `x_cv`/`x_cv2`); a **predeclared** estimator
of `B`; a coverage objective for the repeat count; and `S` with `B ≤ S` demonstrated.

---

## 3. PILOT AUTHORIZATION REQUESTED — the only ask in this packet

> **Three single-task `uthrow5d_runF` invocations on throw index 0**, into a named Z container that
> is neither `mii` nor any canonical `uq_5d/` namespace, distinct `--out` per task:
> **P1** Z configuration; **P2** Z configuration repeated; **P3** current configuration.
>
> **Ceiling `18` CPU task-hours, `0` GPU** (`3 × --time=06:00:00`, the launcher's own request) —
> **`3.6%` of the CPU ceiling.**

**Establishes:** the `n_jobs=1` runtime multiplier — the largest unpriced term, created by the
recommendation in §2; peak RSS under the Z configuration; whether pinning changes the slab
(`sha256(P1)` vs `sha256(P3)`); and **whether the pinned configuration reproduces at real scale**
(`P1` vs `P2`) — **if it does not, route (i) fails on its own terms.**

**Cannot establish or authorize:** `B` (the CV re-unfold is in arm 7, not exercised); any
covariance, combine, assembly or consumable receipt; arms 6/7 costs; a round's wall-clock. **No
adoption, grading, discharge, quoting, or further member. Moves neither Gate 2 nor the stop.**

**Not requested here and not implied:** the production round of plan §7.

---

## 4. FEASIBILITY — corrected

**Z's complete requirement, including its own cause-3 design (`N = 4`–`5`, §6.3):**

| | GPU | CPU | vs `R5` |
|---|---:|---:|---|
| one Z member | `55.70` | `87.12` | — |
| **Z at `N = 4`** | `222.8` | `348.5` | **`44.6%` / `69.7%` — fits** |
| **Z at `N = 5`** | `278.5` | `435.6` | `55.7%` / `87.1%` — thin |

**The `5×–9× over R5` figure previously quoted is the historical 46–50-member M(ii) family, a
design §6.3 does not adopt for Z. It is withdrawn as a statement about Z.**

**The binding constraint is the SCHEDULE**: 4–5 rounds of 374 tasks into blocks of `6 d 06 h` and
`6 d 11 h`, when one arm's tail once ran eleven hours at two-way concurrency. **Not established.**

**Spend, conservative rule:** `0.0` GPU, `14.9756` CPU of `500`. A re-query returning less does not
release budget — `FINDING-20260910-r5-attempt-identity-is-not-stable-across-queries.md`.

---

## 5. REMAINING REQUIREMENTS THROUGH ADOPTION

**Unresolved prerequisites — no task-hour cost, not shortened by any authorization.**

| # | requirement | state |
|---|---|---|
| 1 | the four withheld boundaries: `null_epsilon`, `cause3_agg`, `cause3_med`, `cause3_corr` | **OPEN** — with `z-criteria-designer` |
| 2 | scientific-acceptance **criteria owner** | **ASSIGNED 2026-09-10**, acknowledged |
| 3 | **independent assessor** of the criteria | **ASSIGNED 2026-09-10**, acknowledged |
| 4 | a **grading lane** for the 28 `(cause × leg)` cells, not disqualified by `BEN-381` | **OPEN** — distinct from #3 |
| 5 | reuse-vs-regenerate rationale for `(cause 6, Z)` | **OPEN**; plan §3.2 recommends REUSE, provisionally |
| 6 | `PM-4`'s binding gap and phrasing | **OPEN**, owner's to amend |
| 7 | significance: projection map designated, `ndf`/`norm.isf` declared, **threshold and margin** | **OPEN — threshold and margin exist nowhere in the tree** |
| 8 | the five inflation gates of §1.3b, incl. the `g` reconstruction | **OPEN** — code; four gates admit `g ≡ 1` without the fifth |
| 9 | the two Tier-2 writer changes so the null operands exist | **OPEN** — code, plan §3.3 |
| 10 | two independent pre-launch reviews of the construction | **OPEN** — worker agreement is not independence |
| 11 | an independent artifact replay from digest-bound components | **OPEN** — `≈0.09` CPU task-h |
| 12 | Gate 2, and the three conditions of §1 if the scope ruling is granted | **OPEN** |

**Items 1, 4, 5, 6, 7 and 10 are decision or review work. No resource authorization touches any of
them, and `R5` is not the constraint on any of them.**

# PET critical path — a routing map, partitioned by what each item is blocked ON

**Lane B, 2026-08-17.** Companion to the GBDT map. **Routing document, not a review:** no item is
re-litigated and no physics is adjudicated (the line lane A drew on `OI-6` and held on the J28 footing).
Derived from artifacts, not from `OPEN_ITEMS.md`'s status column — where a row disagrees with the tree,
the disagreement is recorded as a finding in §5.

**Provenance of every count below:** `docs/OPEN_ITEMS.md` at `4ecd52f`, 92 `OI-*` rows, 154 lines;
extraction script and method stated in §5. Cluster facts read read-only from
`/pscratch/sd/j/josephrb/MINERvA-OmniFold`; no run, no `scancel`.

**A partial already existed and it is not superseded — it is a different resolution.**
`SCHEDULING-STRATEGY.md:17-19` carries a PET critical path from ~2026-07-18:
`T6 G2 compile/smoke → T7 full-schema P3F endpoints → T8 PET nominal/UQ → T9 projections → T10 document
freeze`, with `:211-212` gating PET GPU work on the full-schema/negweight gates passing. **That phase map
is coarse-grained and still correct as far as it goes** — and it *corroborates* §2: `T6`/`T7` are done
(the full-event schema landed 2026-08-01), so the campaign is inside `T8`, which is where every live item
below sits. This document is the item-level resolution of `T8` and does not replace the phase view.

---

## 1. THE ONE THING

> ## `OI-126` is PET's `N3`. It is a **binary decision**, it needs **no compute**, and one of its two branches **invalidates an object that is already built.**
>
> `C_stat` **exists** — `docs/orchestration/state/gate5-cstat-n50/GATE5_CSTAT_N50.npz`, with receipt,
> claims file and regression. **`OI-126` blocks pairing it with the adopted P5A central value**, and its
> own row says so in terms: *"`OI-126` blocks pairing `C_stat` with P5A and is not unblocked by any of
> it."*
>
> **Both mechanisms it ever proposed are refuted by measurement** — target (0.068%) and extraction
> (control 0.139%, band ratio 1.0000). What remains is a choice the measurement cannot make:
>
> **(a)** the estimator is genuinely unstable in p∥ 6–20 GeV → `C_stat`'s bands are honest and the
> published uncertainties there are enormous and must be quoted as such; **or**
> **(b)** a Poisson bootstrap of the measured leg is not a valid statistical-uncertainty proxy for this
> estimator → **`C_stat` needs a different construction and `OI-121`/`OI-122` reopen.**
>
> **Everything downstream of `C_stat` waits behind this**: covariance assembly, `OI-40` (note
> quotability), `OI-93` (consumption properties of a rank-49 covariance), and Gate 6's `C_ML`. **Branch
> (b) discards a built artifact**, which is why no amount of downstream work is safe to start first.

**PET's blockers are therefore NOT independent** — but the dependency is not the one the item table
implies (§5). It is a single decision node with ~4 items behind it, and a further 6 decisions that are
independent of it and of each other.

---

## 2. BLOCKED ON AN INPUT THAT DOES NOT EXIST — **EMPTY. The premise is stale.**

**This group was expected to be the critical path — `OI-19`, `OI-20`, `OI-4` "all appear to trace to the
finalized FPS full-event input versus the xps2 scaffolding". It is neither one root cause nor three
coincidences: the chain has been executed.** Measured:

| what the rows say is missing | what the tree has |
|---|---|
| `OI-19`: *"requires the finalized FPS full-event input rather than xps2 scaffolding"* | **`G2_FPS_MEFHC_P12.npz`** is in production use — `sbatch_pet_fullevent_floor_replicate_array.sh:57` — and its identity is verified **by measurement**, not by claim: `state/gate5-source-npz-verified-20260813.json`, `verdict: MATCH` |
| xps2 might still be selectable | **`fullevent_fps_dataloader.py:1046-1072` is a `[PUB-GATE]` that RAISES** on recoil/old/xps2 markers — *"launcher can NEVER select old xps2 / recoil-only / purity inputs for a publication product"*. **xps2 is fenced, not pending.** |
| `OI-20`: *"the publication full-event input and end-to-end nominal are not complete"* | the end-to-end nominal is **PROMOTED** — `state/p3f-pet-gate4-nominal-promotion-56563761.json`, `verdict: PROMOTED`, `2026-08-13T02:52:32Z` |
| `OI-4`: *"the full-event nominal and coherent ensemble are prerequisites"* | nominal promoted (above); Gate 5's 50-replica family passed and **`C_stat` is built** (§1) |

**Bounded negative, since this section rests on one:** `git grep -l -I -- "xps2"` **unrestricted**
returns 20 documentation files **and 10 code files**. I initially read the code hits as a live dependency
and that was wrong — inspecting them, the loader occurrences are the **rejection list and its error
message**, and `extract_fullevent_fps.py:352` is a comment about the *historical* recoil campaign. **The
only live role of `xps2` in code is to be refused.** Stating this because a doc-only grep would have
produced the right conclusion by the wrong route.

**Consequence for routing: nobody is waiting on an input.** `OI-19`/`OI-20`/`OI-4` should be rewritten
against what is actually missing, which is verification (`OI-22`) and the §1 decision — not production.

---

## 3. BLOCKED ON A DECISION BY JOSEPH — each stated as a one-word answer

**These are the critical path. None needs compute to be *decided*.**

| id | the decision, in one sentence he can answer in one word | answer shape |
|---|---|---|
| **`OI-126`** | Is the p∥ 6–20 GeV bootstrap spread **(a)** this estimator honestly reporting instability, so `C_stat`'s large bands are published as-is, or **(b)** evidence that a Poisson bootstrap of the measured leg is not a valid `C_stat` construction, reopening `OI-121`/`OI-122`? | **(a)** or **(b)** |
| `OI-13` | Re-issue Gate 4 against the adopted `0.4945824` criterion, given job `56381674` passed the adopted bar but self-reports against the retired one? | yes / no |
| `OI-71` | May `VL100` be quoted, given the fold-forward rejection is **mis-targeted, not falsified** (corrected 2026-08-15)? | yes / no / hold |
| `OI-3` | Authorize the joint full-event nuisance construction at the scoped **401.7 GPU-h** (124 endpoints × 3.24 h, k=1)? Its own row: *"the blocker is a decision not compute."* | yes / no / defer |
| `OI-33` | Run full per-universe PET lateral retraining, given the existing **1.74–4.03%** bracket from frozen-push and transferred estimates? | yes / no |
| `OI-37` | Reconcile the FPS chain state and schedule adoption, or leave the June chain language superseded in place? | reconcile / leave |

**`OI-121` is authorized and in flight** (spec landed; this lane is sole builder) and is listed here only
because branch **(b)** of `OI-126` reopens it. **`OI-122` is already RATIFIED** by Joseph — verbatim
*"Yes I authorize it"*, committed `4d28e78` before the act — so it is **not** a live decision despite
matching a decision-shaped keyword.

---

## 4. BLOCKED ON NOTHING — dispatchable now, no decision, no allocation

**These are independent of §1 and of each other.** Each is small and its site is already located by its
own row.

| id | the work | site |
|---|---|---|
| `OI-57` | one-line repair: hash the source instead of copying `source["sha256"]`, mirroring `:99-101` | `pet/train_fullevent_replica.py:112` — **its own row: no re-pin step, nothing to sequence against** |
| `OI-60` | add `"data_bootstrap_factor": data_factor` to the bootstrap telemetry dict, then array-compare it in the target stage's replay | `pet/fullevent_fps_dataloader.py:1328-1330` |
| `OI-61` | two receipt-vocabulary fixes: `_raw` must not hold a scaled value; pass a replica-specific tag | next Gate-5 launcher, cosmetic-to-value |
| `OI-64` (lane C's) | call the deployment-parity check that nothing calls | `pet/verify_executing_copy_is_committed.py`, from the next Gate-5 launcher and `reconcile_gate5_family.py` startup |
| `OI-96` | pin the **field**, not the file — read the pinned path value rather than counting occurrences | `pet/check_canonical_designation.py` |
| `OI-58` | route change only: cite `gate5-source-npz-verified-20260813.json` rather than a replica's copied `inputs_sha256` | documentation / quoting rule |
| `OI-41` | correct future W-offset citations to the committed fullcloud projection artifact | narrative |
| `OI-12` | replace the absolute covariance-diagonal tolerance with a relative check **and add a mutation test at the real scale** | FPS validator |
| `OI-82` | resolve which measurement `1.08405298…` is, then correct or retire it — **do not overwrite blind** | the three diagnostics' reference tables |
| `OI-90` | narrow the row's own overstated claim to what was measured (150/150 hashes replayed; application evidenced by `n_data_effective`, not array identity) | `RUNS.tsv:296` |

**Compute-blocked but *not* GPU, and mine to name rather than approve:** `OI-50` — `hsi hashverify` over
both HPSS archives (tape I/O, no GPU; the conditional it waited on is settled per `d2c7699`/`OI-51`) and
`OI-49` — intersect 240 archived basenames against the ignored-set walk and sum matched bytes. `OI-59`
(recompute the reference-rule truth migration on the Ascencio super-grid) and `OI-39` (mechanism for the
5.711 unified-to-block trace ratio) are CPU-scale but **unscoped**, so I am not costing them from a
launcher I have not read.

---

## 5. WHERE THE ROWS DISAGREE WITH THE TREE — findings, not commentary

**Method, so the counts can be checked and their limits seen:** a script keys on the `state` column for
`DISCHARGED|CLOSED|WITHDRAWN|SUPERSEDED|PREMISE FALSE|REFUTED|RETIRED`, over the 92 `OI-*` rows of
`docs/OPEN_ITEMS.md` at `4ecd52f`, selecting PET-relevant rows by a regex on `PET|FPS|full-event|
point-cloud|xps2|Branch-C|C_stat|Gate 4/5/6`. **It is a keyword heuristic and it misclassifies rows whose
state describes a withdrawn SUB-claim inside a live row** — verified by reading: `OI-60` (NARROWED, open),
`OI-96` (OPEN), `OI-127` (OPEN), `OI-125` (STILL OPEN, narrowed), `OI-2` (split: 4D superseded,
scalar-FPS open). Corrected for those five:

```
PET-relevant rows in the live table   50
already CLOSED / DISCHARGED / etc.    ~14   still occupying the live table
genuinely live                        ~36
```

**Finding 5a — the live table carries roughly 14 PET rows that are already closed**, which inflates the
apparent PET backlog by ~28% and is the reason "PET has 50 open items" would be the wrong headline.

**Finding 5b — `OI-19`, `OI-20`, `OI-4` are stale in the direction of *more done than the row says*,**
and all three are `as_of 2026-08-12` while the input verification (08-13), nominal promotion (08-13),
Gate-5 family and `C_stat` build (08-14) all postdate them. §2 has the evidence. **This is the single
most consequential staleness in the set**, because those three rows are what makes PET look
input-blocked when it is decision-blocked.

**Finding 5c — two unresolved ID COLLISIONS, both PET-adjacent, both unrenumbered:**

```
OI-64  line 131 (lane A: verify_hash_bindings.py guards nothing)
OI-64  line 134 (lane C: deployment-parity check has no caller)
OI-65  line 132 (lane A: receipt-retirement exposure, measured zero instances)
OI-65  line 135 (lane C: reconcile_gate5_family.py cannot gate promotion)
```

**A dispatch naming "`OI-64`" is ambiguous today**, and §4 above had to disambiguate by lane. This is the
exact shape `CLAUDE.md` records as dangerous — *"`B1` closed" is true of one and false of the other* —
and it is unresolved for two ids at once. **Renumbering is the owners' call; routing around it is not
sustainable.**

---

## 6. WHAT TONIGHT SETTLED — recorded so it is not re-derived

- **Arm 1 is complete and receipted.** `57038937_3/_4/_5`, three `COMPLETED` (`01:56:59`, `01:57:24`,
  `01:58:29`), all six draws clearing `CLM-012`. The authorization `0fb56af` is **spent**.
- **The fold-forward instrument is verified correct** (`BEN-342`), and its dtype fix is exercised on the
  cluster to completion plus a local boundary test against the engine's own loss.
- **`OI-125` closes DOCUMENTARILY, not by compute.** Its gap for the audited products is **permanently
  unclosable**: the end-of-run scalar was not recorded at the time and `67c94df` cannot record it
  retroactively. The recorder covers all future runs; for the audited products the value is a
  reconstruction and must be cited as one (`BEN-360`).
- **Arm 0: the PROHIBITION IS LIFTED and the run is still not being made.** Joseph, verbatim *"You can
  run arm 0"* (`f2c0ac9`), lifting item 1 of `AUTHORIZATION-20260815-arm1-resubmit.md` and **only** that
  clause — items 2-7 stand. **The run is not happening because this lane returned DENY on the merits,
  not because it is forbidden**, and those merits are unaffected by the lift: arm 0 is the reproduction
  gate on reading arm 1 (`sbatch_foldforward_instrumented_closure.sh:27`) and the baseline of `RESULT_2`'s
  16.2σ delta, so a second population would make the gate ambiguous and re-base the closure's one
  quantitative result; and a fresh run yields a **fourth** number about a new population without closing
  `OI-125` for the audited ones. **Anyone reading "prohibited" here is reading a stale fact — the
  permission exists and the recommendation is still don't.**
- **The 4.4% marginal-vs-independent 4D disagreement is answered.** `BEN-319` (`773c940`) establishes it
  is an **identity**, *"neither mathematics nor a defect, as posed"*; separately, the W-mixing mechanism
  was measured and **refuted** in `FINDING-20260809-stage6-central-gate-cannot-pass.md` (cells with the
  most W-mixing agree best, by 3×). Not a PET item; recorded because two lanes re-opened it in one night
  and the answer now exists in two places.

---

## 7. THE SHORTEST PATH, IF ONE ANSWER IS AVAILABLE

1. **Ask `OI-126` (a) or (b).** Nothing else in §3 changes what is buildable; this one does.
2. **If (a):** `C_stat` pairs with P5A, `OI-121` completes, and §4's ten items plus `OI-93`'s consumption
   rules become the remaining work — parallelisable across lanes immediately.
3. **If (b):** stop before any consumption work. `OI-121`/`OI-122` reopen and the construction question
   precedes everything, including the note.
4. **Independently of either**, §4 is dispatchable tonight and §5c should be renumbered by its owners
   before the next dispatch names an ambiguous id.

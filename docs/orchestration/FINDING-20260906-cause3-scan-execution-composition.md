# FINDING 2026-09-06 — the cause-3 fixed-draw scan's execution declaration composes into three defects, and its blocked-in-principle ground is stale

**CITABLE FOR:** the five measurements in §2–§6, each with the command or file:line that produced it.
**NOT CITABLE FOR:** a grade on any leg, a repair, an authorization, a cost approval, or any claim that
these defects have been fixed. **Every remedy below is a PROPOSAL awaiting independent verification.**
Gate 2 remains FAIL. CAND `1 of 7`, QUOTED `0 of 7`. No covariance is adopted. No compute was run.

**Filed by:** the lane that produced `VOI-20260906-cause3-mii-estimator-seed-scan.md`. **`BEN-381`
applies to every item here: this lane took the measurements, so it grades no cell and applies no
repair.** Both the scoreboard cells and the execution declaration belong to other owners, named in §7.

**Subject:** `PREDECLARE-20260901-cause3-mii-estimator-seed-magnitude.md` §6b/§6c — the **execution
declaration** only. §1's quantity, §2's footing falsifiers, §3's thresholds and §4's six branches are
**not** in scope and are preserved by `DECISION-20260902-joseph-rules-cause7-cause3-and-the-stop.md`
`R4`.

**Measured at** HEAD `c71b319a` and at the frozen deployment sha `7ac0edec`. Where a line number is
given, the sha it was read at is given with it, because this campaign has already lost a preflight to
line drift (§2).

---

## 1. Why these compose rather than stack

Each item below is individually small. What makes them a finding is that **the three routes available
for setting the estimator seed each fail a *different* declared falsifier**, so a reader checking any
one route against any one rule finds nothing wrong. The composition is only visible when the seed
route, the output-path derivation and the provenance stamp are read together — and two of the three
failures are terminal *after* the 8.7 GPU task-hours are spent.

---

## 2. `§6b`'s line citations resolve at the DEPLOYMENT, not at `main`

`§6b` cites `nd-unfolding/sbatch_unfold_5d_detector_bkgaware_gpu.sh:278-279` for `OMNIFILE`/`FLUX_MC`
and `:294`/`:308` for `--omnifile`/`--mcfile`.

```
git show 7ac0edec:nd-unfolding/sbatch_unfold_5d_detector_bkgaware_gpu.sh | grep -n ...
  278:OMNIFILE=...  279:FLUX_MC=...  284:EST_SEED=...  294:--omnifile  308:--omnifile
same file at c71b319a (and at 52cbda90, 9ce59a59):
  323:OMNIFILE=...  324:FLUX_MC=...  329:EST_SEED=...  339:--omnifile  353:--omnifile
```

**A +45-line drift.** The citations are exact at `7ac0edec`, which means `§6b`'s preflight measured the
**frozen deployed tree** — the correct operand — and its favourable conclusion stands on its merits.

**The defect is the missing sha, not the numbers.** A reader re-checking `§6b` against `main` finds
every citation broken and is one step from "correcting" a sound preflight into a wrong one.

**PROPOSED, not applied:** record `7ac0edec` beside those citations.

---

## 3. The declared seed set `1..12` is not reachable through the launcher's own seed knob

At `7ac0edec:284` the launcher computes `EST_SEED=$(( 42 + ${MNV_EST_SEED_OFFSET:-0} ))` and passes
`--seed ${EST_SEED}` at `:294` and `:308`. **There is no direct seed argument.** §1 declares the
estimator seed set as the literal `1,...,12` and §4 branch 2 makes a readback mismatch INCONCLUSIVE.

| route | resulting seeds | declared falsifier it meets |
|---|---|---|
| hooked, `MNV_EST_SEED_OFFSET = -41..-30` | `1..12` | none on the readback — see §4 and §5 for its two residues |
| hooked, clean offsets `k >= 1118` | `1160..1171` | §4 branch 2: *"Read-back seed set is not exactly `1..12`"* — **after the spend** |
| unhooked, `--seed` passed directly | `1..12` | §4 branch 2's **digest-collision** arm, plus a provenance loss — see below |

**The unhooked route, measured in two independent places.**
`nd-unfolding/seed_offset_policy.py`'s `declared_offset` returns `(0, 0)` when `MNV_EST_SEED_OFFSET` is
unset, and its own docstring states the consequence: *"declared = 0 … this leg did not go through a
hooked launcher. Its seed is its baseline and NOTHING can be concluded about which scan member it
is."* Separately, `nd-unfolding/lib_member_resume.sh`'s `mr_member_dir` returns `""` when no offset is
declared, so `_mr_insert` leaves the path unscoped and all twelve replicas resolve the **same**
`XSEC_OUT`; `mr_skip_if_complete` then exits 0 for replicas 2–12.

**`§6c` selects that route in writing:** *"§2's check 5 … is satisfied by passing only `--seed`."*

**Negative offsets are supported in code**, which is what makes the first route viable at all:
`lib_member_resume.sh:80` formats `member_kneg%06d` for `k < 0`, and `mr_require_valid_offset` accepts
`^(0|-?[1-9][0-9]*)$` while refusing zero-padded values with a recorded octal/decimal divergence
reason.

**PROPOSED, not applied:** the hooked negative-offset route, subject to §4 and §5.

---

## 4. The hooked route writes into the `mii/` M(ii)-family member namespace

`mr_member_root` composes `"${MII_CONTAINER}/member_k…"`, and
`lib_member_resume.sh:84` sets `MII_CONTAINER="${MII_CONTAINER:-mii}"`. So the hooked route creates
twelve directories under `nd-unfolding/mii/` — the **k=0 rehearsal's member axis**, which shares the
token `M(ii)` with cause 3's magnitude leg while being a different object.

**And the namespace is not incidental: it is `(B)`'s own.**
`nd-unfolding/mii_seed_offset_driver.py:2` describes itself as the *"Four-leg estimator-seed offset
scan driver for M(ii) (spec **(B)**, option (ii) OFFSET)"*, and `nd-unfolding/mii/` already holds
`member_k000000`, `member_k001200` and `member_k002400` — three members of that grid, each stopped
after legs 1–5, with leg 6 never having run
(`DECISION-20260830-joseph-mii-family-and-leg6.md`). So the hooked route would deposit **cause-3
fixed-draw products into the joint-baseline scan's own member namespace**, where resume is by marker.

That namespace has required three per-instance dispositions (2026-08-22, 2026-08-23, and
`DECISION-20260830-joseph-quarantine-k0-member-namespace.md`). The last states it is *"**not** a
standing rule and **not** a precedent that pre-approves the next one"*, and records the mechanism that
makes stray products dangerous rather than merely untidy: markers whose note matches the offset mean
`mr_skip_if_complete` *"does **not** fail on them — **it adopts them**."*

**Collision risk is low but not the point.** `(B)`'s offsets must satisfy the clean predicate
(`k >= 1118`, §5), and the three existing members sit at `0`, `1200`, `2400`, so `-41..-30` would not
land on an existing member. **There is no committed grid to check against, either:**
`mii_seed_offset_driver.py`'s `--offsets` is *"REQUIRED for every path except `--gate-only`"* after a
`1200` default was removed as a footgun — *"an omitted or mistyped grid silently planned the wrong"*
scan. The objection is not collision; it is that a cause-3 run would place unrelated products in a
namespace whose adoption semantics are resume-by-marker.

**PROPOSED, not applied:** `MII_CONTAINER=cause3_mii_20260901`. One variable; hooked provenance
preserved; no shared namespace touched.

---

## 5. The clean-offset predicate calls those offsets dirty, and nothing on this path enforces it

`seed_offset_policy.PER_UNIT_SEED_RANGES` declares `bootstrap replica seed = (1, 100)` and
`seedscan split seed = (1, 24)`, each with the launcher line it was measured from. With the `g1`
baseline `42`, offsets `-41..-30` produce estimator seeds `1..12`, **inside both ranges**, so
`forbidden_offsets(-41, -30)` flags all twelve — twice each. The module derives its clean region as
`k >= 1118` and says so in a comment that insists the threshold be **derived from the ranges, never
remembered**.

**Two measurements, and they point in opposite directions:**

1. **Nothing enforces the predicate on this path.**
   `nd-unfolding/unfold_nd_omnifold_unbinned.py:1123-1126` imports `seed_offset_policy` and calls
   **only** `declared_offset()`, which the module documents as *"for STAMPING ONLY -- never for
   behaviour."* `LEG_BASELINES` registers this leg as `"unfold_nd_omnifold_unbinned": ("g1", 42)`, so it
   is in the policy's population. Enforcement — `assert_offsets_are_clean`,
   `assert_offset_grid_is_alias_free` — is called at `nd-unfolding/mii_seed_offset_driver.py:222,227`
   and, apart from the test suite, nowhere else. **So the run would neither fail closed nor warn.**
2. **The confound the predicate exists to prevent has no site in this arm.** Its stated harm is that
   *"an offset can slide a leg's ESTIMATOR seed into the range of that leg's own DRAW seeds, and then,
   inside a single member, one unit's draw RNG and the estimator RNG are seeded identically."* A
   draw-free CV unfold contains no bootstrap replica and no seedscan split unit for the estimator seed
   to coincide with. `§6c` establishes the draw-free property independently: *"A CV unfold does not
   draw at all."*

**Point 2 is this lane's reading of the predicate's SCOPE, and it is the single most checkable claim
in this document.** If it is wrong, the hooked negative-offset route is not available and the seed set
must be redeclared — which is a §1 change, and therefore Joseph's, not a lane's.

**PROPOSED, not applied:** if the hooked route is adopted, record point 2 as a pre-execution finding
with its own falsifier, so twelve products stamped `est_seed_offset = -41..-30` do not stand against a
committed policy that calls those offsets dirty with no guard having spoken in either direction. **This
is an exemption for one arm on a stated structural ground, never a relaxation of the predicate.**

---

## 6. `SCOREBOARD` §2b's blocked-in-principle ground for `M(ii)` is STALE at HEAD

`SCOREBOARD-20260817-quarantine-seven-causes.md` §2b grounds *"`M(ii)` cannot be configured on either
leg"* on two readings, and the cell at `:74` carries the consequence as
*"`OPEN` and NOT CURRENTLY MEASURABLE"*. Both readings are false at HEAD `c71b319a`:

| §2b's 2026-08-17 reading | measured at `c71b319a` |
|---|---|
| sweep leg: *"`sweep_bank_5d.py:252` carries it as a **literal**; the module has **14** `add_argument` calls and **none for seed**"* | `sweep_bank_5d.py:358` declares `--estimator-seed`; `grep -c add_argument` = **15**; `:344` comments *"This was the literal `seed=42`"*; `:309` writes `ROOT.TParameter("int")("estimator_seed", …)` |
| throw leg: *"`unified_throw_cov.py:525` has **exactly one** `--seed` … one flag, two roles. Varying it moves the **draw**, so 'estimator seed varied with the draw held fixed' is **unsatisfiable**"* | `unified_throw_cov.py:630` declares `--draw-seed` and `:634` `--estimator-seed`, **both `required=True`**; `:269` `rng = np.random.default_rng(args.draw_seed + gj)` drives the draw only; `:569-570` write **both** `estimator_seed` and `draw_seed` |

**Two consequences, both routed rather than taken.**

* **`SCOREBOARD:74`'s cell text asserts an impossibility that is no longer true.** This is the same
  defect class as `DECISION-20260902-joseph-rules-no-fourth-grade-token.md` §5, which routed the
  neighbouring `P-ii` cell for exactly this reason — *"a live board asserts an impossibility that is
  not true"* — and left it unrepaired because *"correcting it changes what a remedy costs."* The same
  applies here and the same restraint is observed.
* **The joint-baseline composite's blocker moves from CODE to GATE 2 — not to cost.** `SCOREBOARD`
  §2c's `CONCEDED` block adopted `(B)` and named its blocker: *"`sweep_bank_5d.py:252`'s hardcoded
  `42` … becomes THE blocking dependency."* **That dependency has landed.** What stands in `(B)`'s way
  now is stated by `DECISION-20260830-joseph-mii-family-and-leg6.md`, which authorizes *"the **M(ii)
  member scan as a family**"* and then says: *"**Gate 2 is FAIL** … The gate, not the family
  authorization, is the binding constraint, and no authorization from Joseph removes it."*

* **The cost figures for `(B)` cover THREE DIFFERENT ARM POPULATIONS and must not be summed or
  substituted for one another.** This is recorded because this cell has already produced four wrong
  cost numbers, each by comparing across unlike populations:

  | accounting | arm population | GPU task-h | CPU task-h | source |
  |---|---|---:|---:|---|
  | one complete seven-arm member round, round-2 actuals | all seven arms | `54.90` | `86.53` | `AMENDMENT-20260831-oi177` §5 R2 column, summed by metered unit |
  | the same round at ratified per-arm ceilings | all seven arms | `70` | `113` | `AMENDMENT-20260831-oi177` §5; quoted by `R5` §1 |
  | *"one additional estimator seed"* | **`C_syst` sweep/detector arms only** (`23.840 + 14.2075 + 1.030 = 39.078`, plus `0.1458`) | `39.223` | `55.337` | `SCOPE-20260818-gate1-seed-separation-two-keys.md` `:22`, `:340` |

  The third row is **not** a per-member cost. `SCOPE-20260818` states it twice and **derives it at
  neither occurrence** — verified, both are *"does NOT ask"* / *"NOT authorized here"* disclaimers;
  `INDEX-retracted-and-superseded-values.md` carries the same pair with an arithmetic chain
  (`39.078 + 0.1458 = 39.2238`; `55.182 + 0.1550 = 55.337`) and the warning that `39.078` is the GPU
  column only *"and the CPU half is the LARGER one."*

* **`R5` §1 already did the campaign arithmetic and it reproduces:** *"`500/500` is therefore about
  **seven** GPU rehearsal-equivalents and **4.4** CPU ones"* — `500/70 = 7.14`, `500/113 = 4.42`. At
  round-2 actuals the authorized family is `2,525` GPU / `3,980` CPU task-hours at 46 members and
  `2,745` / `4,326` at 50 — **5× to 9× either ceiling**, which `R5` handles by making continuation past
  the stop a fresh decision rather than a default.

* **NO CONCLUSION ABOUT AFFORDABILITY IS DRAWN HERE, and none should be read in.** The family's size is
  an explicitly unconfirmed reconciliation of two mutually exclusive options; the per-seed figures are
  underived at their primary site and cover a narrower population; and **no reduced-member `(B)` design
  has been costed by anyone.** Whether an affordable `(B)` measurement exists is **unmeasured**.

**Corroboration, counted once rather than twice.** The `lane/y-cause7-spec-and-scope` lane reached the
same two-legs-now-configurable measurement independently at `d2a515e0`
(`SPEC-20260906-complete-scalar5d-successor-Z.md` §2.3), which is a second reading of the same files
rather than a second origin. This lane measured it before reading that document and states it as its
own measurement; the agreement is evidence about the files, not two independent instruments.

---

## 7. Owners — nothing here is this lane's to apply

| # | item | owner |
|---|---|---|
| 1 | record `7ac0edec` beside `§6b`'s citations (§2) | the cause-3 lane, on the predeclaration's **execution** sections only |
| 2 | choose and declare the seed route; the hooked negative-offset route is the only one not meeting a declared falsifier (§3) | the cause-3 lane, in the `R4` reauthorization — **not** by editing §1 |
| 3 | `MII_CONTAINER` scoping (§4) | the cause-3 lane, with the k=0 member-namespace owner notified |
| 4 | verify or refute §5 point 2 — the predicate's scope for a draw-free arm | **a lane that took none of these measurements** (`BEN-381`) |
| 5 | regrade or annotate `SCOREBOARD:74` (§6) | the board's owner. **Not this lane, not the cause-3 lane** |
| 6 | re-derive the composite cost figures, with the arm population named, before any plan relies on them (§6) | the `M(ii)` member-scan family's owner. **The family is authorized and Gate-2-blocked; this finding proposes no change to it** |

**If a redeclaration of §1's seed set turns out to be required (§5), that is a change to a scientific
criterion and belongs to Joseph.** This finding proposes none.

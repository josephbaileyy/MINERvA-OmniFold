# PREDECLARATION 2026-09-21 — the `L2` probe: releasing the five seed-pinned lateral bands

**THIS RECORD IS WRITTEN BEFORE THE CODE CHANGE AND BEFORE THE RUN.** That ordering is the point:
the probe's outcome map, the cost, and what each answer may and may not license are fixed here so
none of them can be chosen after seeing a number.

**CITABLE FOR:** Joseph's authorization of the reserved estimator change, the design of the probe,
and the declared outcome map.
**NOT CITABLE FOR:** any result — there is none yet — any regrade, or any change to the adoption.

---

## 1. The authorization

**Joseph, 2026-09-21, in his own words:** *"yes do the L2 probe, i authorize the estimator change."*

This is the reserved act that
[`EVIDENCE-20260919-lateral-bands-are-seed-pinned.md`](EVIDENCE-20260919-lateral-bands-are-seed-pinned.md)
§5 routed to him and forbade routing around:

> **Putting the five on the hook is a MATERIAL CHANGE TO THE ESTIMATOR and is RESERVED.** … It is
> not this lane's act, it is not attempted, and it is routed to Joseph.

It is also reserved act **2** of `OPERATIVE-SHEET-scalar5d.md` §6. **It is now authorized, by name,
by the person it was reserved to.** Nothing else in §6 is released by this.

⚠ **Supervision.** The waker has been down since 2026-09-09 (§4f of the handoff). Joseph's
instruction — *"I will run audits while you keep track of this probe"* — makes **this lane the
supervision for this run**. That is a live obligation, not a formality: if this session ends
without reporting, nothing else will notice the run.

## 2. THE CHANGE IS THREE SITES, NOT TWO — and the third is the one that would have bitten

The evidence named two files. Reading them, there are **three** change sites, and the one it did
not name is the dangerous one:

| # | site | today | why it must change |
|---|---|---|---|
| 1 | `run_p4_unfold_std.sh:111` | `--seed 42` literal | the seed itself |
| 2 | `p4_build_components.py:66` | `UDIR = "active_universe_5d/standard/unfolds"` hardcoded | the component builder must read the member's unfolds |
| 3 | **`run_p4_unfold_std.sh:32`** | `OUTDIR=".../standard/unfolds"` | **the outputs would land on top of the adopted product's own inputs** |

⚠ **Site 3 is why a seed-only change would have been worse than useless.** The script's resume rule
skips a tag whose ROOT and receipt are valid and content-checked. With `OUTDIR` unchanged, a re-run
at a new seed would have found ten valid receipts and **skipped all ten**, reporting success while
changing nothing — or, if the receipts were cleared first, **overwritten the ten endpoint unfolds
the adopted covariance is built from**. Either outcome is a silent corruption of the published
result's provenance.

**The mechanism is the repository's own, not a new one.** `lib_member_resume.sh` already prepends
`mii/member_kNNNNNN` to a product path whenever `MNV_EST_SEED_OFFSET` is set (`_mr_insert`,
`:120-135`), and `mr_prefix` returns the member-scoped path with its directory created and **fails
closed** when it cannot anchor. Sites 2 and 3 use that. Nothing invents a path scheme.

**A consequence that must be declared, not discovered:** this makes `run_p4_unfold_std.sh` a
member-local consumer, so `seed_offset_policy.MEMBER_LOCAL_CONSUMERS` must gain it, and
`tests/test_lateral_bands_are_seed_pinned.py` will go red. Its own failure message says that is
**not a test failure to silence** — it means the limitation is obsolete and must be withdrawn. It
will be updated to assert the new state, not deleted.

## 3. What the probe measures

**Design, chosen to cost 10 unfolds rather than 20.** The declared offset set is `K = {0, 1200}`.
Offset 0's laterals **are** the existing seed-42 unfolds, so only the offset-1200 member needs new
ones:

    seed(member 0)    = 42          laterals: the existing ten, REUSED
    seed(member 1200) = 42 + 1200 = 1242     laterals: ten NEW unfolds, member-local

Then: `p4_build_components` member-locally → one Z assembly for the 1200 member with **its own**
lateral block → `z_grade` over the two members.

⚠ **The ± endpoint pair stays at ONE seed within a member.** The offset is applied uniformly across
all ten endpoints, so the MAT `±` difference still cancels the CV *within* the member, exactly as
the pinning comment at `:6` intends. **What changes is the seed BETWEEN members, which is the only
thing the probe is about.** A design that varied the seed per endpoint would measure something else
and would break the MAT convention.

**The statistic:** `s_proj`, the maximum relative change in `√(uᵀCu)` over the declared functional
set, computed exactly as the graded campaign computed it — same code path, `z_grade`.

## 4. ⚠ THE OUTCOME MAP, FIXED NOW

| measured `s_proj` with the five released | what it licenses | what it does NOT |
|---|---|---|
| **> 5%** | `L1`'s FAIL is **confirmed** with the five varying; `L2`'s direction becomes known; the result is **strong**, because `s_proj` is a maximum and more pairs can only raise it | it does not regrade `M(i)`, which is `UNRESOLVED` on `4c` for a **permanent predeclaration failure** |
| **< 5%** | **nothing.** One seed pair cannot establish that the maximum over the declared set is below the bound | it is **not** a PASS, not a clearance, and not grounds to revisit the adoption |
| **cannot be computed** | the probe failed; report the inability as an inability | it is not a result of any kind |

**So the probe can confirm the FAIL or return an ambiguity. It cannot clear it.** This is declared
here so that a sub-5% number is not read as good news after the fact.

**Whatever the result:** it does not change the adopted digest `3d7465f6…`, does not regrade cause
3, does not license a significance, and does not move a central value.

## 5. Cost, declared before spending it

| stage | reserved |
|---|---|
| 10 endpoint unfolds, 1 GPU + 32 CPU, 1.5 h each | **15 GPU task-h** |
| component build + merge audit | < 0.5 CPU task-h |
| one Z assembly (measured precedent: job `58454524`, 1037 s, 49.73 GiB) | 0.29 task-h |
| one grade | < 0.25 task-h |
| **total** | **~15 GPU + ~1 CPU task-h — about 3% of one arm's 500 task-h ceiling** |

**The event loops do NOT re-run.** `run_p4_unfold_std.sh` unfolds an already-merged endpoint ROOT;
the shifted-kinematics event loops are estimator-seed-independent and are reused. A design that
re-ran them would cost orders more and would be measuring the wrong thing.

## 6. What would make this probe invalid, declared so it can be checked afterwards

- the ten new unfolds not all at the **same** seed `1242`;
- any product landing outside the member directory (`mr_prefix` fails closed; if it is bypassed,
  the run is void);
- **any write into `active_universe_5d/standard/unfolds/`** — the baseline's own directory. The
  ten existing ROOTs and their receipts must be **byte-identical before and after**, and that will
  be verified by digest, not by inspection;
- fewer than ten new endpoint ROOTs, or extras;
- a grade computed over anything other than the two declared members.

**Co-Authored-By: Claude Opus 5 (1M context)**

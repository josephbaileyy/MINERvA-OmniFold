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

---

# ⚠ AMENDMENT 1, 2026-09-21 — THE CHANGE IS **SEVEN** SITES, NOT THREE, AND FOUR OF THEM ARE PROVENANCE GATES

**Written before any job was submitted and before any product was written.** Nothing in §1–§6 above
has been executed. The outcome map in §4 is unchanged and is not reopened by this amendment.

## A1.1 How this was found, because the pattern is the point

§2 above opens *"The evidence named two files. Reading them, there are **three**."* That sentence is
now itself an understatement, and by the same mechanism: **I read the files the previous record
named, and stopped.** What I did not do was follow the seed FORWARD through the stages that consume
the unfolds. Doing that turns up four more sites, and they are worse than the three, because three
are *paths* and four are *gates that certify provenance*.

⚠ **A grep for `--seed 42` finds site 1 and nothing else.** The literal `42` is load-bearing in six
more places under five different spellings: a default argument, a dict constant, a `require`, a
config-hash input, an independent re-derivation of that hash, and a reproducibility reference.

## A1.2 The four new sites

| # | site | what it does today | what a member run would have done |
|---|---|---|---|
| 4 | `run_p4_unfold_std.sh:71,76` | `P4Config()` — **default seed 42** — supplies `CFG_HASH` | stamps `config_hash(seed=42)` into a receipt for a ROOT produced at **1242** |
| 5 | `p4_lib.py:269` + `:41` + `:335` | `require(self.seed == 42)`; `STANDARD_REQUIRED_FOOTING["seed"] = 42`; the footing gate | refuses any member config outright, **or** passes a false one |
| 6 | `p4_check_receipt.py:97` | re-derives `P4Config()` **at the default** and compares `config_hash` | **re-derives the SAME false hash, so the lie VALIDATES** |
| 7 | `p4_evidence.py:36,38,391` | hardcoded `UDIR`, hardcoded `EVID`, reproduction-vs-reference gate | reads baseline unfolds, and **DELETES the baseline manifest** |

## A1.3 ⚠ SITE 6 IS THE ONE THAT MAKES SITE 4 INVISIBLE, AND THAT IS THE WHOLE FAILURE

Site 4 alone would be a bad receipt. Site 4 **with** site 6 is a bad receipt **that passes its own
verification**, because the producer and the checker compute the same wrong number from the same
default. Two independent-looking confirmations, one shared defect — and the resume rule would then
treat the member's mis-stamped product as valid on every subsequent run.

The repository already names this exact shape. `mr_require_valid_offset`'s own comment calls a
seed/provenance divergence *"the worst failure mode available to this campaign,"* and says why it is
the worst: *"every guard passes, the member directory exists, the stamp is self-consistent, and the
number is wrong."* That is a literal description of what sites 4+6 would have produced. **The
comment warning about this failure is in the file I sourced to implement the change.**

## A1.4 ⚠ SITE 7 IS DESTRUCTIVE TO THE ADOPTED PRODUCT'S OWN PROVENANCE

`p4_evidence.py` writes to `.PENDING` and then publishes; `_publish_evidence()` *removes the
opposite variant* so that *"a directory must describe one run."* That rule is correct and it is the
hazard here. A member run with `EVID` unscoped would have:

1. hashed the **baseline's** ten unfolds (`UDIR` hardcoded), so the manifest would not describe the
   member at all;
2. blocked on all ten reproduction comparisons — **correctly**, since a different seed is not a
   reproduction — and therefore taken the `.FAILED` branch;
3. and in taking it, **deleted `active_universe_5d/standard/evidence/p4_standard_manifest.json`** —
   the manifest that binds the ten endpoint digests the adopted covariance `3d7465f6…` is built
   from — replacing it with a `.FAILED` copy describing a run that was never the baseline's.

§6's invalidating condition already forbids *"any write into `active_universe_5d/standard/unfolds/`"*.
It did not reach `evidence/`, because I did not know stage 3 existed in this path. **It is hereby
extended: no write, rename, or unlink anywhere under `active_universe_5d/standard/`.**

## A1.5 The repairs, and the principle they follow

**Every gate is DERIVED, never relaxed.** The seed requirement does not become "any seed"; it
becomes `42 + the offset the caller declares`. At offset 0 — every non-probe run, forever — each
gate evaluates to exactly the literal it enforces today. That is the property that makes this safe
to land: **the baseline path is unchanged by construction, not by inspection.**

| # | repair |
|---|---|
| 4 | driver builds `P4Config(seed=P4_EST_SEED)` and validates it against the declared offset, so `CFG_HASH` covers the seed that actually ran |
| 5 | `P4Config.validate(expected_offset=0)` and `require_standard_footing(..., expected_offset=0)` compare against `p4_lib.standard_seed_for_offset(offset)`. `STANDARD_REQUIRED_FOOTING` is **not mutated** — its own comment says those constants are hash-pinned into FPS gates and must not be coupled to |
| 6 | `p4_check_receipt.py` gains `--est-seed-offset`, passed by the driver, so the checker re-derives the config the producer actually used |
| 7 | `p4_evidence.py` gains `--est-seed-offset`; `UDIR` and `EVID` are member-scoped from it; and the reproduction gate is **INVERTED rather than skipped** — see below |

### ⚠ A1.5.1 The reproduction gate is inverted, and that is STRONGER than disabling it

At offset 0 the gate asks: *do these ten endpoints reproduce the 2026-07-18 reference to
`1e-9` per bin / `1e-11` on the integral?* A member at a different seed **must** fail that, by
design — so the honest options are to skip it or to invert it.

**It is inverted.** At a declared non-zero offset the gate requires each endpoint to **differ** from
the reference by more than the same declared tolerance, using **the same instrument**
(`check_reproducibility`) with no new constant. A member that *did* reproduce the reference would
mean **the seed never reached the estimator** — the run would look perfect and measure nothing,
which is §6's first invalidating condition detected one stage earlier and automatically.

A skipped gate is a hole. An inverted gate is a control.

## A1.6 The cheap control that runs FIRST, added to §6 as a precondition

Before the member runs at all: **run the driver with `MNV_EST_SEED_OFFSET` UNSET.** It must print
`SKIP` for all ten tags, exit 0, and leave the ten baseline ROOTs and receipts byte-identical to the
digests captured before the change. Cost: about one CPU-minute, no GPU.

This is the direct, positive demonstration that the seven-site change did not disturb the adopted
product's inputs — which is the thing §6 says must be *"verified by digest, not by inspection."*
**If this control does not pass, the probe does not run.**

## A1.7 What this amendment does NOT change

- **The outcome map in §4 stands exactly as written**, including that `< 5%` licenses nothing.
- The cost in §5 stands; sites 4–7 are code, not compute.
- Nothing above has been run, so no result is being reinterpreted. This is a correction to the
  *plan*, made before the plan was executed.

---

# ⚠ AMENDMENT 2, 2026-09-21 — A1.6's CONTROL IS WITHDRAWN: IT WOULD HAVE DESTROYED WHAT IT WAS WRITTEN TO PROTECT

**Still before any job, still before any product.** A1.6 proposed, as the *safety precondition* for
the probe, running `run_p4_unfold_std.sh` with the offset unset and checking it skipped all ten.

**Running that command would have overwritten the ten endpoint unfolds of the adopted covariance.**
The control was the most dangerous thing in the plan.

## A2.1 The measurement, made read-only on the cluster before anything was run

At the deployed HEAD `32e403b8`, `p4_check_receipt.py` against the adopted `BeamAngleX_0` receipt:

```
RECEIPT-REJECT :: receipt BeamAngleX_0 unfold_blob dc74c38f8ec7b5f6723fa231630e9fc43e7a93f0
                  != committed 662951e019f9c96c2876decc7913c7e9b3dbf2ae:
                  the unfold driver changed since this endpoint was produced
rc=1
```

`nd-unfolding/unfold_nd_omnifold_unbinned.py` changed after 2026-08-08 — commits `5afb7947`,
`ae42ae8d`, `0a4ab263`, `1aa055d9` — and `validate_endpoint_receipt` compares that blob **strictly**,
which is correct: it is the producing-code binding. **So all ten receipts read STALE**, the launcher
falls through to the re-unfold, and `mv -f` replaces the ROOTs. Exit 0, no warning.

## A2.2 ⚠ THIS HAZARD IS PRE-EXISTING AND LIVE, AND THE L2 CHANGE DID NOT CAUSE IT

The deployed checkout **already** carries blob `662951e0`. Anyone running the documented baseline
command on the cluster today — with or without this change, before or after the probe — silently
regenerates the adopted covariance's inputs under different code. It was found only because the
probe forced the question *"what does the resume gate actually decide for these ten?"* to be asked
as a measurement rather than assumed.

⚠ **Three predictions I made about this were wrong, and they failed in the safe direction only by
luck.** I expected the ten to be expired by `check_resume_surface`, because `seed_offset_policy.py`
is in the producing closure and the L2 change edits it. They are not: the ten receipts predate PB2,
carry neither `receipt_schema` nor `surface_blobs`, and are therefore **GRANDFATHERED**. So the
closure comparison never runs — and the rejection arrives from an entirely different gate. Had those
receipts been one schema newer, the L2 commit itself would have expired all ten.

⚠ **And the config hash is unaffected, which was checked rather than assumed.** The adopted receipt
records `config_hash 4b41fab90a83df08…`; the offset-0 config after the seven-site change hashes to
`4b41fab90a83…` — identical. The derived-gate design is neutral at offset 0 **by measurement**.

## A2.3 The repair: a fail-closed guard, and it is not part of the probe

`run_p4_unfold_std.sh` gains a **baseline overwrite guard**. Once the function has committed to
producing an endpoint, it refuses when all of: the ROOT exists, the namespace is **not** member-
scoped, and `P4_ALLOW_BASELINE_REUNFOLD=1` is absent. Exit `9`, naming the adopted digest and
quoting the rejection reason.

⚠ **An ordering defect in my own guard, found by testing it rather than by reading it.** The first
version sat *after* `rm -f "${REC}"`, so a refused baseline run would still have **deleted all ten
receipts** before being stopped — preventing the overwrite and not the damage. The removal now
happens only once the guard has allowed production, and
`tests/test_baseline_overwrite_guard.py` asserts that ordering **on the extracted text of the
launcher itself**, so it cannot silently revert.

The guard is tested in four directions (fires on baseline-with-ROOT; silent for a member, for a
first production, and under the exact escape value; and near-miss values `0`/`yes`/`true`/``/`2` do
**not** release it), and the refusal is asserted to leave the receipt on disk.

## A2.4 What replaces A1.6

**A1.6 is withdrawn in full.** The probe's precondition is now:

1. **Read-only adjudication** — run `p4_check_receipt.py` against all ten baseline receipts and
   record the verdicts. It writes nothing. *(Done for one tag; the ten are recorded with the run.)*
2. **Digest capture and re-comparison** — hash the ten baseline ROOTs before and after the member
   run and require byte-identity, which is what §6 asked for and never needed a driver invocation
   to obtain.
3. **The member run cannot reach the baseline directory at all**, because `OUTDIR` is member-scoped
   and `mr_prefix` fails closed.

**The lesson, recorded because it is the reusable part:** *a control is an action, and an action
needs its blast radius priced before it is called a safety measure.* A1.6 read as obviously safe —
"just run it and check it skips" — and its safety rested entirely on an unexamined assumption about
what the resume gate would decide. The assumption was false, on the cluster, today.

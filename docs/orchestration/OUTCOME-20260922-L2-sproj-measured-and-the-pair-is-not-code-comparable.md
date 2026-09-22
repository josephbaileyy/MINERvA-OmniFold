# OUTCOME 2026-09-22 — L2's `s_proj` IS measured, and the pair it comes from FAILS the grader's own comparability precondition

**CITABLE FOR:** that the L2 released-lateral `s_proj` was computed, its control reproduced the
graded statistic exactly, and the member pair fails `footing_ok` for a measured, structural reason.
**NOT CITABLE FOR:** a discharge of `M1`, a regrade of cause 3, any significance, or any change to
`3d7465f6…`. ⚠ **AND NOT CITABLE FOR THE PREDECLARATION'S BARE `> 5%` ROW** — see §3.

| | |
|---|---|
| unblocked by | `P4_VERIFIER_PASS = 229c43e0…` (`20260922T053047Z-gbdt-cold-start-verdict.json`) |
| stages | 4 **and a first, FAILED stage 5** in job `58735444` (29:13, walled); stage 5 (repaired) and 6 in `58738058` (18:00) |
| L2 product | `/pscratch/sd/j/josephrb/z2m-products/member_k001200_L2laterals/z-cv.npz` |
| its `sha256` | `48713676fbce070527caa76ff559a34d2b83a34585d60cd13a36f9bd9410dae9`, `887,229,279` B |
| statistics receipt | `…/l2-statistics.json`; validity detail `…/l2-validity-detail.json` |

## 1. THE NUMBER, AND THE CONTROL THAT MAKES IT READABLE

The control runs first and is not optional: it re-measures the **already-graded** pair and must
reproduce `GRADE-20260920`'s `s_proj` to `1e-12`.

| statistic | pinned (graded pair) | released (five laterals at seed 1242) | Δ | relative |
|---|---:|---:|---:|---:|
| `s_agg` | `0.471447%` | `0.762704%` | `+0.291257` pp | `+61.78%` |
| `s_med` | `0.485229%` | `0.682292%` | `+0.197063` pp | `+40.61%` |
| **`s_proj`** | **`6.145388%`** | **`6.189174%`** | `+0.043786` pp | `+0.71%` |

**CONTROL: `|measured − recorded| = 0.000e+00`** against the recorded
`0.06145388143592225` — exact, against a `1e-12` requirement. **The harness is the graded code
path**, which also validates the two repairs §4 records.

⚠ **The two legs that were INSIDE the `5%` bound moved most in relative terms and stay far inside;
the failing leg moved least.** Releasing the five seed-pinned bands did **not** produce a large
change in `s_proj`.

## 2. EVERY PREDECLARED INVALIDATING CONDITION, CHECKED

`PREDECLARATION-20260921` §6 lists five. ⚠ **CORRECTED 2026-09-22 by a second independent
reviewer: this section read *"All five hold"* and that is WITHDRAWN.** Three hold as measured, one
holds only against §6's **pre-amendment** text, and one is **not satisfied**:

| condition | measured |
|---|---|
| the ten new unfolds all at the **same** seed `1242` | ✅ **one** distinct `config_hash` across all ten receipts, `4809b4ad399f999c…` — distinct from the baseline's `4b41fab90a83df08…`; manifest `est_seed 1242`, `est_seed_offset 1200` |
| nothing written outside the member directory | ⚠ **PARTIAL, and the caveat is the headline product.** The ten unfolds and the candidate are under `nd-unfolding/mii/member_k001200/…`, which is what `mr_prefix` produces. **The Z product is not:** it is at `/pscratch/sd/j/josephrb/z2m-products/member_k001200_L2laterals/`, a NEW sibling of the graded members' own `z2m-products/member_k001200/`, created by `l2_stage5_assemble.sh`'s hardcoded `OUT` and not by `mr_prefix`. That directory is outside both the member tree and the graded member's canonical Z directory; §6's condition says *"any product"*, so this is **recorded as not satisfied rather than ticked** |
| the baseline's twenty files byte-identical before and after | ✅ **as §6 was ORIGINALLY written** — verified by digest in **both** jobs, *"BASELINE UNTOUCHED: all 20 digests byte-identical"*, population checked 20/20 so the comparison is non-vacuous. ⚠ **BUT AMENDMENT 1 §A1.4 WIDENED THIS CONDITION AND THE WIDER SCOPE WAS NOT MEASURED:** *"It is hereby extended: no write, rename, or unlink anywhere under `active_universe_5d/standard/`."* The digests cover `…/standard/unfolds/` only — **not** `…/standard/evidence/` (the manifest A1.4 itself says a member run would have deleted), and not the rest of `standard/`. **Recorded as unmeasured, not as passing** |
| exactly ten endpoint ROOTs, no extras | ✅ ten |
| the grade computed over the two declared members only | ✅ `[0, 1200]`, `offsets_match_K` PASS |

Also: the member receipts pin `unfold_blob 662951e0…` — the **current** driver — so unlike the ten
baseline receipts (which pin the superseded `dc74c38f…`) they validate against today's tree.

## 3. ⚠ THE PAIR FAILS `footing_ok`, AND THE REASON IS CODE IDENTITY, NOT PHYSICS

`l2_stage6_measure.sh` printed `validity all-true : False` for the probe and `True` for the
control — **and its verdict branch does not consult that flag**, so it printed *"FAIL CONFIRMED"*
under a failed precondition. Exactly one of the ten fields fails:

    CONTROL: all nine PASS
    PROBE:   footing_ok *** FAIL ***    (the other eight PASS)

⚠ **CORRECTED 2026-09-22 (third independent review): this said *"Exactly one of the ten fields fails"*, *"the other nine PASS"* and the transcript's *"CONTROL: all ten PASS"*, **all three of which are corrected in place above** — the first correction changed only the CONTROL line and left `(the other nine PASS)` standing, which is the one-of-N-sites failure recurring inside the fix for it. ⚠ **The committed receipt `state/L2-20260922-validity-detail.json` still lists TEN fields including `notes`, because the PRE-FIX probe wrote it, so the corrected transcript deliberately does not reproduce from it; re-run the repaired probe to regenerate.** `z_validator.Validity` has NINE bool fields plus
`notes: dict`, which `cross_member_validity` always populates and `bool()` always coerces to True —
so it can never fail and must not be counted as a passing check.** Read it as **one of NINE
failing, eight passing**. `z_grade.cross_member_validity`'s own docstring says *"all nine"*. The
committed probe `probes/probe-20260922-l2-validity-detail.py` iterated `__dataclass_fields__` and
so included `notes` in both its listing and its `all_true`; that is a defect in a committed
instrument and is fixed there too.

**It is not a mask, row-order or population difference.** Calling the real `Member.footing()` on
all three products returns **identical dicts** — `mask_sha256 eed021e9…`, `row_order_sha256
61a7c9fd…`, `n_reported 10694` for every one. The failure enters later:

    z_grade.py, cross_member_validity:   footing_ok = bool(footing_ok) and code_agrees

`code_agrees` requires both members' `code_identity.revision` **and** `import_closure_digests` to
match. Measured:

| product | `code_identity.revision` | import closure |
|---|---|---|
| `member_k000000` | `d64257c3947a239f…` | identical to m1200 |
| `member_k001200` (graded) | `d64257c3947a239f…` | identical to m0 |
| **`…_L2laterals`** | **`384c2eb17e94a9b7…`** | **differs** |

→ `code_agrees(m0, m1200) = True`; **`code_agrees(m0, L2) = False`.**

**This is not incidental bookkeeping. `z_grade`'s own comment says why the fold is deliberate:**
*"two members built by different code are NOT COMPARABLE, so the campaign is inconclusive, and the
only branch that says 'inconclusive, report no magnitude' is branch 1."*

### 3a. The GRADED pair's code identity cannot be reproduced — but a code-comparable pair CAN be built, and was not

The divergence is forced, not careless:

1. `z_build._code_identity` **requires** `manifest["producing_revision"] == git rev-parse HEAD`.
2. The graded members were built at `d64257c3`. To match them, the rebuild would have to execute
   at `d64257c3`.
3. `l2_stage5_assemble.sh`'s own header records that a build at `d64257c3` **dies under the OI-136
   guard** (job `58358282`), because `z_build` there lacks the `--no-ext-diff` the guard requires.

So matching **the graded pair's** code identity and running at all are mutually exclusive with
this toolchain.

⚠ **CORRECTED 2026-09-22 by a second independent reviewer. This section claimed *"the probe as
designed cannot produce a code-comparable pair"* and concluded that matching *"are mutually
exclusive"*. THAT IS ONE LEVEL TOO BROAD, and the route it misses is cheap.** `code_agrees` does
**not** compare either member against `d64257c3`; it compares the members **to each other** —
`all(r == revisions[0] for r in revisions)`, where `revisions[0]` is simply the first member. So a
code-comparable pair is obtained by **rebuilding the k=0 member's Z at today's HEAD as well**, at
which point both carry the same revision and the same import closure and `code_agrees` is True.
The predeclaration's own §5 prices one Z assembly at **`0.29` task-h** (precedent job `58454524`,
1037 s), so the route costs about **`0.58` task-h** for the pair. ⚠ **AND THE ROUTE IS BOTH MEMBERS, NOT ONE — corrected by the third independent review.** This
read *"rebuilding the k=0 member's Z at today's HEAD"*, which does **not** work: `z_build`
`contract.require(revision == head)` stamps whatever HEAD is current, and the L2 product is frozen
at `384c2eb1`, already 15 commits behind as of `8d22bfd0` (17 by `c6a62a4c`; the count decays, the fact does not). Rebuilding only k=0 today stamps a **third** revision and
`code_agrees` stays False. **Both members must be rebuilt at ONE common HEAD** — which is what the
`0.58 = 2 × 0.29` figure silently priced while the prose named a single rebuild.

**It is DECLINED-AND-UNDONE here, not impossible**, and the price is higher than one object:
rebuilding the offset-0 member replaces the object the 09-20 grade was computed on, **and
rebuilding the L2 member replaces the very product §1's `6.189174%` was measured on.** Both are
decisions about the graded campaign rather than steps in this probe. What remains
true without qualification is only that **the GRADED pair's code identity cannot be reproduced**. ⚠ **The prior lane anticipated the PROVENANCE difference** — *"the consequence is a
PROVENANCE difference between the two members' receipts … stated rather than hidden"* — **but not
that `cross_member_validity` folds code identity into `footing_ok`, which turns a disclosed
provenance note into a failed comparability precondition.**

### 3b. What that does to the outcome map

`PREDECLARATION-20260921` §4 fixed three rows: `> 5%` confirms; `< 5%` licenses nothing; *"cannot
be computed"* is an inability. **The measured state is none of them cleanly.** The number was
computed and is reproducible; the control is exact; but the grader's own branch-1 precondition for
treating the two members as comparable is **not met**.

**So the `> 5%` row may NOT be claimed bare.** The defensible statement is:

> With the five seed-pinned lateral bands released at seed 1242, `s_proj` measured `6.189174%`,
> above the `5%` bound and slightly above the pinned `6.145388%` — **on a member pair whose code
> identities differ, which the grading criterion classifies as not comparable.** The control
> reproduces the graded statistic exactly, so the harness is sound and the number is what the code
> computes; what is unestablished is that the two members may be compared at all.

**It does not confirm `M1`'s FAIL in the predeclaration's strong sense, and it certainly does not
weaken it** — `M1`'s `6.145388%` is measured directly against the bound on a fully valid campaign
and never depended on this probe.

## 4. TWO INSTRUMENTS WERE REPAIRED, AND NEITHER HAD EVER RUN

Both stage scripts were unrunnable as written; stage 4 had been gated, so neither was ever reached.

- **`l2_stage5_assemble.sh`** copied the graded manifest verbatim, leaving
  `producing_revision: d64257c3`, which `z_build` refuses against HEAD →
  `{"construction_status": "FAILED", "reason": "producing_revision must equal the executing
  checkout's HEAD"}`. **Repaired** (`_v2`) to stamp the executing HEAD — which is what the script's
  own header already said it was doing, and which is also the direct cause of §3.
  It also **ended on `ls`, so its exit status was `ls`'s**: a FAILED `z_build` reported success to
  every caller. Measured on job `58735444`: `z_build rc=1`, script `rc=0`. Repaired to propagate.
- **`l2_stage6_measure.sh`** called `z_grade.MemberProduct`, which **exists at no revision** — not
  at `c05c64a9` where the script was written, not at HEAD. The class is `Member`, with exactly the
  `(product, receipt_path, expect_variant)` signature the script passes. **Repaired** (`_v2`).

⚠ **The originals are left in place unmodified** as the record of what was predeclared; the repairs
are `_v2` copies. **All four are now COMMITTED** — ⚠ **a second independent review found that none
of them were, so every claim in this section about what the scripts do, and both repairs, were
unverifiable from the repository:**

    docs/orchestration/probes/probe-20260922-l2-stage5-assemble-ORIGINAL.sh
    docs/orchestration/probes/probe-20260922-l2-stage5-assemble-v2.sh
    docs/orchestration/probes/probe-20260922-l2-stage6-measure-ORIGINAL.sh
    docs/orchestration/probes/probe-20260922-l2-stage6-measure-v2.sh

alongside the four probes that produced §3's measurements (`…-l2-validity-detail.py`,
`…-l2-footing-base-reuse.py`, `…-l2-real-footing.py`, `…-l2-code-identity.py`). A later lane can now
diff original against `_v2` and re-run the footing experiment rather than taking this record's word. ⚠ **This lane authored both repairs**, so it is not an independent checker of
them — what stands in for that here is the control, which reproduces the graded `s_proj` to exactly
`0.000e+00` and could not do so through a harness that had been altered in substance.

## 5. What this does NOT authorize

- It does **not** regrade `M(i)`, `UNRESOLVED` on `4c` for a **permanent** predeclaration failure.
- It does **not** regrade cause 3, which is not discharged for the adopted bytes.
- It does **not** license any generator significance.
- It does **not** move `3d7465f6…`, and it does not touch a central value.
- `M1`–`M4` travel unchanged; `M2`'s *"a larger ensemble would not reduce it"* and `M3`'s
  *"lower bound"* remain **WITHDRAWN**.
- ⚠ **One seed pair.** `s_proj` is a **maximum** over the declared functional set, so this is one
  point of that maximum and the seed-pair distribution remains unmeasured.

**Co-Authored-By: Claude Opus 5 (1M context)**

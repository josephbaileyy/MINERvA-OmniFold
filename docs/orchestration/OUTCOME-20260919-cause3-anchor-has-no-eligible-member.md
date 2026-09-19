# OUTCOME 2026-09-19 — **(C) BLOCKED**: the `k = 0` anchor has no eligible member

**CITABLE FOR:** the disposition of the computed-acceptance goal's second attempt, and the decision
it needs.
**NOT CITABLE FOR:** any grade, adoption, boundary or authorization. Gate 2 remains **FAIL**; no
scalar-5D covariance is adopted. **Zero task-hours were spent; no job was submitted.**

## 1. The outcome

**(C) BLOCKED** — *"blocked by a reserved decision these rulings don't cover, or compute beyond
cap."* **Both apply**, and they are the same blocker seen from two sides.

R6 authorizes **exactly one** additional member. Cause 3 needs **two** members. The second was
assumed to exist. **It does not** — and that was established by measurement before anything was
submitted.

## 2. Why, in one table

Full census with method, controls and identities:
[`EVIDENCE-20260919-cause3-member-eligibility-census.md`](EVIDENCE-20260919-cause3-member-eligibility-census.md).

| candidate `k = 0` anchor | offset declared? | null operands? | disqualified by |
|---|---|---|---|
| **`z-cv.npz`** — R8's named comparison member | **NO**, `(declared, offset) = (0, 0)` on **61/61** slabs | YES | `SPEC` §3.7b branch 2 — *"`est_seed_offset_declared` is `0` on any member"*. `Validity.offset_declared_nonzero` fails, `branch2_failures()` is non-empty, **branch 3 is unreachable**, so the campaign can never be MET |
| **`mii/member_k000000`** — the `k0r2` anchor, `374/374 COMPLETED 0:0` | **YES**, `(1, 0)` on **185/185** slabs, seeds `1000`/`42` = each group's baseline + 0 | **NO** — `hCvExecution{0,1}`/`hCvSupportMask` absent (**0** hits against a **2**-hit `C_unified` control) | R8 — the graded product's `r_null` must be *"measured in its own production"*; and `z_build` requires a `null` source structurally. Its deploy `7ac0edec` predates the writer (`d3b6ae2b`), so the operands were never written and **cannot be reconstructed** — §3.6d item 5: a separately produced denominator *"presumes the determinism the null tests"* |

**The two properties the anchor needs sit in two different artifacts. No existing member has both.**

## 3. Why R8's own stop condition fires

> **R8** … *"`z-cv.npz` may serve as the comparison member for the cause-3 statistics **only if** the
> diff since its build touched decision logic alone … **If the route cannot grade a
> post-preregistration product this way, stop with (C) instead of grading `z-cv.npz`.**"*

The route cannot — **and not for the reason R8 anticipated.** The condition R8 sets is about the
**code diff**; the disqualifier is in the **artifact's own provenance stamp**, and no code diff can
repair it. The diff was therefore never the binding question and is not reported here.

Substituting `mii/member_k000000` as the comparison member is **not within these rulings**: R8 names
`z-cv.npz`, and the substitute needs its own `C_Z^(0)` — which it cannot have, for the reason in the
table. **So it is not an alternative I could take without asking.**

## 4. The compute, both ways, because the two readings disagree

Making the anchor eligible means **re-running the `k = 0` member under current code** — a **second**
additional member. R6 authorizes one.

| basis | one member | **two** members | cap | verdict |
|---|---:|---:|---:|---|
| **reservation** (enforced cap × tasks — what admission checks) | `262.00` CPU / `158.25` GPU | **`524.00` / `316.50`** | `280` / `165` | **1.87× / 1.92× OVER** |
| **measured actual** (`ElapsedRaw`, the `577532xx` member) | `86.53` CPU / `54.90` GPU | **`173.06` / `109.80`** | `280` / `165` | **fits, with `107` CPU / `55` GPU spare** |

**Which basis the cap is denominated in is a decision, not a measurement.** R6 says *"at the priced
reservation of `262.00` CPU / `158.25` GPU task-hours"*, and admission is enforced on reservations —
so I read it as the reservation basis and stopped. Under the measured-actual basis, two members fit
comfortably.

**And neither figure covers the four downstream stages.** A "member" as priced is **seven task
arms**, not a `C_Z`. Each member still needs the stage-2 universe combine (`fin5dBKG`, `1.5 h` GPU),
the stat and ML covariances (`adopt5d`, `budget5d`, `1.0 h` CPU each), the active lateral candidate
(`run_p4_standard.sh` — **no `#SBATCH` header, no reservation of its own**) and the Z assembly
(`1037 s` observed for the pilot). **None of the four is in `DECISION-PACKET-20260918` §12.5's
table.** At the reservation basis, one member leaves `18.00` CPU / `6.75` GPU of headroom for
**eight** such stages plus two assemblies plus the verification battery.

**⚠ A live risk in the authorized cap itself**, recorded before anyone submits against it: the
recommended `uthrow5d_block` cap is `3.00 h`, and **1 of the `k0r2` member's 21 block tasks ran
`4.82 h`** (next longest `2.27 h`). The policy allows exactly **one** corrective resubmission, so a
comparable `k₁` member would **foreseeably spend its whole recovery budget on the first timeout**,
and a second slow task **ends the campaign with no member assembled**. `uthrow5d_runF` is clear: 0
of 40 over its `4.25 h` cap.

## 5. What was finished anyway, because it does not depend on the blocker

| | |
|---|---|
| **R7 — the fix, reviewed and committed** | `ce0b717b`. `all_members_finite` is a branch-1 field and the builder **measures** it. Cross-model review: **NO BLOCK, NO MAJOR**; three findings fixed, including my own SPEC edit. [`REVIEW-20260919-R7-non-finite-member-footing.md`](REVIEW-20260919-R7-non-finite-member-footing.md) |
| **R6 — the reversal recorded as superseding ruling 2** | [`DECISION-20260919-joseph-R6-reverses-the-k1-decline.md`](DECISION-20260919-joseph-R6-reverses-the-k1-decline.md), with the supersession annotated **inline** in the authorization it supersedes |
| **The census that produced this outcome** | [`EVIDENCE-20260919-cause3-member-eligibility-census.md`](EVIDENCE-20260919-cause3-member-eligibility-census.md) |
| **A standing caveat discharged** | `project-campaign-state`'s *"nobody has verified the scientific products landed"* for `577532xx`. They landed — and the verification is what found the null-operand gap |

## 6. What was deliberately NOT done, and why

- **No preregistration.** It exists to precede a production submission, and there is none. Writing
  one would preregister a run that cannot happen.
- **No campaign admission and no submission.** The one authorized member does not reach branch 3 on
  its own, and R9 forbids a one-member assessment. Submitting it would spend `262`/`158.25` of
  reservation to arrive at branch 2 — the outcome that is already known.
- **No multi-member grader.** *This is the one remaining code gap and it is real:* nothing in
  production computes `s_agg`/`s_med`/`s_proj` or assembles a cross-member `Validity` —
  `z_validator.assess()`'s only production caller is `z_build`, which passes `{}` statistics for a
  single member. It was not built now because **its specification depends on the blocked decision**:
  which two members are compared determines which fields are measured across what, and the hard rule
  freezes that logic the moment production output exists. Building it against the wrong member model
  would be worse than not building it.

## 7. The decision this needs

**One question, with the options priced.**

1. **Authorize a second additional member** — the `k = 0` re-run under current code, so the anchor
   carries both a declared offset and its own null operands. Needs a cap that covers it: `524.00`
   CPU / `316.50` GPU on the reservation basis, or `~173` / `~110` measured.
2. **Or rule that the cap is denominated in measured task-hours**, in which case two members fit
   inside `280` / `165` as it stands — but the admission check enforces reservations, so this needs
   saying explicitly.
3. **Either way, price the four downstream stages**, for both members. They are not in the packet's
   table and one of them has no reservation at all.
4. **And decide the `uthrow5d_block` cap** — `3.00 h` with one recovery, against an observed `4.82 h`.

**Not asked for and not implied:** any change to `S`, `ε`, a boundary, a criterion or the estimator;
the `§6.4` exception still covers `3d7465f6…` only; no ADOPT and no push.

**Co-Authored-By: Claude Opus 5 (1M context)**

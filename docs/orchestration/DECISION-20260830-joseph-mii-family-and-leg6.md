# DECISION 2026-08-30 — Joseph: the M(ii) family is authorized, and leg 6 on the k=0 anchor

**CITABLE FOR:** the existence of a family authorization and its stated conditions.
**NOT CITABLE FOR** any claim that compute may start now, that Gate 2 has moved, that the F-17(b)
grade is FIT, or that a scalar-5D covariance is adopted. None of those changed.

## What Joseph said, and the exact shape of it

**READ THE PROVENANCE BEFORE CITING THIS.** Joseph did not type this into the repository. It arrived
through an interactive Claude Code session on 2026-08-30, and **the scope wording below is this
lane's drafting, ratified by him — it must not be quoted as his words.** What is his is the decision
that the authorization exists.

His words, verbatim:

> *"I authorize it, so you will start all the sessions that will use those prompts?"*

That sentence was ambiguous between authorizing the three prompt-driven sessions and authorizing the
M(ii) family, so this lane put four options to him and asked which "it" covered: (1) start the three
sessions only; (2) family at 46 members; (3) family at 50 members with HPSS archiving; (4) run leg 6
on the k=0 anchor as soon as it is legal. He selected:

> *"All of them"*

## The one place this lane had to draft rather than transcribe

**Options (2) and (3) are mutually exclusive on a number, so "all of them" cannot be read literally.**
Storage is why they differed: pscratch measured **80.0%** (15.99 of 20.00 TiB) on 2026-08-29, and the
staged plan's 2.17 TiB for fifty members lands at ~90.8%, over the runbook's ~90% abort threshold.
Forty-six members fit without archiving.

**This lane's reconciliation, which Joseph has NOT separately confirmed and which any lane may
challenge:** the family is authorized at **50 members conditional on archiving to HPSS as members
complete**, with **46 as the floor** if archiving is not in place when the family is launched. The
reading is that (3) was the fuller intent and (2) was its fallback, not that both hold at once.
**If that reading is wrong, this row is the defect and Joseph's correction governs.**

## What is authorized

1. The **M(ii) member scan as a family**, superseding ruling 12's withholding — that ruling selected
   the target but said in its own words it *"does not authorize the ... family ... or a full member
   scan."* That withholding is now lifted, at the size stated above.
2. **Leg 6 (`fin5dBKG`) on the k=0 anchor**, to complete one member end-to-end.
3. The three prompt-driven lanes (F-1(b) producer filing, forward-only rehearsal proposal,
   no-compute quarantine legs). None of those submits a Slurm job.

## What is NOT authorized, and why nothing starts today

**THIS AUTHORIZATION IS NECESSARY BUT NOT SUFFICIENT, AND NO COMPUTE MAY START ON IT ALONE.**

- **Gate 2 is FAIL.** The review contract holds that until it passes, the rehearsal's products stay
  *"not adopted, not consumed by anything outside the seven rehearsal jobs, not quoted, and no
  further member is authorized."* Leg 6 would be an eighth job consuming those products. **The gate,
  not the family authorization, is the binding constraint, and no authorization from Joseph removes
  it** — only the rehearsal work landing does.
- **Leg 6 has never run.** Measured 2026-08-30: `sacct --name=fin5dBKG` since 2026-08-01 returns
  nothing. `nd-unfolding/mii/` holds `member_k000000`, `member_k001200` and `member_k002400`, each
  stopped after legs 1–5. **No member has ever completed end-to-end**, so launching the remaining
  members before leg 6 succeeds once would produce members stuck exactly where those three are.
  Sequence leg 6 on the anchor before the family, regardless of authorization.
- The **F-17(b) repaired chain is NOT FIT** on finding `N1`, and a new forward-only rehearsal is
  required because F-17(b) is impossible for the current one by construction.
- Nothing here adopts a covariance, moves a gate, lifts a quarantine cause, or authorizes
  `C_ML` / Gate-6 work. PET remains off the publication path.

## The order this implies

Gate 2 PASS → leg 6 on k=0 → one member verified end-to-end → family launch at the size above.
Anyone reading this row as permission to submit today has read it wrong.

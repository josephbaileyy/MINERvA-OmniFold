# DECISION 2026-08-24 — Joseph: the deployment is frozen until F-1(b)'s far-end measurement is filed

**CITABLE FOR:** the authority behind review-contract **§7.0.19**. **NOT CITABLE FOR** anything else;
this is a freeze, not a licence, and it authorizes nothing.

## What Joseph approved, and the exact shape of the approval

His words, verbatim, via the relay channel he authorized on 2026-08-24:

> *"(a) sure add that rule"*

**READ THE PROVENANCE BEFORE CITING THIS.** That is an **approval of a proposal**, not authored rule
text. The **rule's wording was proposed by the builder lane** (`claude-school-main`), which put it to
him as *"no lane may move the deployment before F-1(b)'s far-end A-2(a)–(g) measurement is taken."*
The scope language in §7.0.19 is therefore **the builder lane's drafting, ratified by Joseph** — it
must not be quoted as his words. What is his is the decision that the rule exists. As with
`DECISION-20260824-joseph-f6b-scoped-out-of-gate2.md`, Joseph **did not type this into the
repository**; it arrived by authorized relay through an interpreter session.

## The rule

**The deployed tree `/pscratch/sd/j/josephrb/k0r2/clean` stays detached at `aa67c426` until F-1(b)'s
far-end A-2(a)–(g) measurement is filed.** No `checkout`, no `reset`, no `fetch`-and-merge, no
re-declaration, and no branch repoint in that directory.

**It expires when F-1(b) is TAKEN — not before, and not on anyone's judgement that the rehearsal
"looks done."** That second clause is load-bearing: the job graph contains a **conjunctive `afterok`**
(`combine` on both `uthrow_run` **and** `uthrow_block`), and a partial failure in either array leaves
`combine` reading as *queued* in `squeue` while being terminal. **"Looks done" is precisely the
inference this rule must not permit.**

## Why it is needed — the mechanism, not just the rule

Everything else that could void this rehearsal is enforced by something mechanical:

| exposure | what enforces it |
|---|---|
| a `.py`/`.sh` change | the A-2(f) listing digest `sha256:fa3489e22168954bebcc9a602338d924582fd231643bfa285b3a9225e7535420` |
| a docs commit pretending to be one | `mnv_source_manifest.py:70` — `SOURCE_SUFFIXES = (".py", ".sh")`, so an `.md`/`.tsv` commit is **provably unable** to move the listing |
| a write bit | `--require-readonly` |
| **the deployment's POSITION** | **nothing** |

**A-2(a) at the far end requires `git rev-parse HEAD == aa67c426`.** The rehearsal is ~230 tasks in
with zero failures, so **one careless command destroys a measurement recoverable only by re-running
everything.**

**And the campaign's own history is the argument for writing it down:** a hold that exists only as
someone's intention is not a hold. Four commits once described as *"held pending Joseph's call"*
published themselves as ancestors of another lane's push, and the builder lane pushed a branch today
where a sha would have done. **The rule must be citable so that a lane reasoning "nobody said I
couldn't" has something to hit.**

## What this rule IS and IS NOT, stated because a prose hold invites over-reading

**IT IS PREVENTIVE BY CONVENTION AND DETECTIVE BY A-2(a) — it is not a mechanical guarantee, and
nothing in this file makes it one.** A-2(a) will *catch* a moved HEAD at the far end; it cannot
*prevent* the move. **So this clause reduces the chance of the excursion and does not eliminate it.**
Anyone wanting a mechanical hold would need a check that reads `HEAD` in that directory and fails
closed — outside §6's authorized set, and not created here.

## The residual, measured — this is why the rule does real work

The two routes that actually caused the round-10 deployment excursion are closed. **Measured in the
deployed tree, 2026-08-24:** `HEAD=aa67c426…`, detached, `git status --porcelain` **0 lines**,
**0 local branches**, **0 remotes**.

**But `git checkout refs/tags/evidence/…` remains a live route: the deployed tree carries 10
`refs/tags/evidence/*` tags, and none of them points at `aa67c426`.** (This clone carries 11, also
none at the candidate — two counts of two different objects, both true.) Those tags are other lanes'
provenance anchors and **must not be deleted to satisfy this rule.** So the freeze is closing a real
gap rather than restating a guarantee already held elsewhere.

## What it does not authorize

Nothing. It does not authorize leg 6, adoption, consumption, any member k≠0, re-declaration of the
candidate, or any relaxation of a Gate-1 or Gate-2 clause. §7.0.6 and
`DECISION-20260824-joseph-f6b-scoped-out-of-gate2.md` are unchanged by it.

## Eligibility

Recorded by the coordinating lane, already disqualified under §7.0.10 from grading either gate, so this
costs no further independence. **The builder lane declined to write it three times today and was right
to: it is the producing lane for F-1(b) and would be authoring the rule that protects its own
measurement.**

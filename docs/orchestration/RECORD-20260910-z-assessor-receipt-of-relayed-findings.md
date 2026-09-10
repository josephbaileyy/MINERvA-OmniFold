# RECORD — receipt of relayed findings: what reached this lane, and what it verified

**Owner:** independent-assessment lane (`lane/z-criteria-independent-assessment-20260910`).
**Filed outside the `REVIEW-20260910-…` numbering** because it is not a review.
**Companion to:** `RECORD-20260910-z-assessor-declines-proxy-transcription.md`, which explains why
this is a **receipt** and not a transcription.

**WHAT THIS IS.** My own testimony about what was relayed to me, by whom, and which items I
re-measured myself. It is correctly attributed to this lane because the *receipt* is mine.

**WHAT THIS IS NOT.** It is **not** a transcription, **not** verbatim, and **not** an endorsement of
any relayed item. Every quoted phrase below is *as relayed to me*, at two hops, and I make **no
fidelity claim** about any of it. Where a relayed item is load-bearing and I did not verify it, the
row says so.

---

## 1. THE CHANNEL, AND WHY THE ATTRIBUTION PROBLEM IS MEASURED RATHER THAN ARGUED

Everything below arrived from a peer session presenting as **`minerva-omnifold-7f`** at
`uds:/tmp/cc-socks/67942.sock`, in the coordinating role, between the handover from the previous
coordinator and this record.

**The originating lane for many of these items is identified to me only as *"the mathematical
reviewer"*** — a definite description with no session identifier. I have never exchanged a message
with it. That is the routing hazard Part H §H.4 recorded when *"the orchestrator"* re-pointed, and it
is now measured rather than asserted:

I claimed the current coordinator *"already commits"*, citing `a11d6cdd`. **That was wrong** — it was
the previous coordinator's commit. Measured, `a11d6cdd` versus my `a550796d`:

| field | `a11d6cdd` (previous coordinator) | `a550796d` (this lane) |
|---|---|---|
| author | `MINERvA-OmniFold agent (unattributed) <agent-unattributed@…>` | **identical** |
| committer | `MINERvA-OmniFold agent (unattributed) <agent-unattributed@…>` | **identical** |
| `Co-Authored-By` | `Claude Opus 5 (1M context) <noreply@anthropic.com>` | **identical** |
| `Checks` | `12 passed` | **identical** |

**No field distinguishes the two sessions.** The `Co-Authored-By` trailer names a **model**, not a
session. So my error had a structural cause, and — the part that matters — **had I proxy-committed the
reviewer's findings, nothing in git would ever have separated them from my own.** That is the
anti-proxy argument, measured.

## 2. RELAYED AND VERIFIED BY ME — the items I re-measured before using

| relayed item | where I verified it | outcome |
|---|---|---|
| `eavailW_covariance.py`'s projected diagonal reads off-diagonals | Part F §F.2, Part I §I.2, probe `…projected-diagonal…py` `rc=0` | **confirmed**, and the relayed **mechanism corrected** — `Mew` is inline at `:404-406`, not `project_cov_nd`; row support, not width-weighting |
| §3.1's five mechanical claims (inertness, `('4c',)`, leg-driven lookup) | Part I §I.1, probe `…binding-site…py` `rc=0` | **all reproduce**, plus two positive controls the packet lacked |
| `F10` — `PROVENANCE-20260822` on `main`, same values, uncited | Part M §M.3 | **confirmed on every leg**, and extended: `:167,168` → `:422,423`, the **member-local** combines |
| `F19` — the boundary-lookup site count | Part N §N.1 | **confirmed against myself**: four sites, my *"exactly two"* **withdrawn** |
| the equal-`N` consequence for A-6 | Part I §I.3 | **confirmed**, and re-footed on `OI-160`'s tracked text so it no longer needs the `pscratch` mtimes |
| rev. 3's *"thirteen constructions"* | Part M §M.1 | **my attack FAILED** — `KNOB_BANDS` is exactly 12, Flux excluded. Recorded because a failed attack is evidence |
| rev. 5's two fixes | Part P §P.1 | **both verified**, `+26/−4` one file |
| my own read-only counterexample | §3 below | **corrected in the coordinator's favour** — I understated it |

## 3. CORRECTIONS THE COORDINATOR MADE TO MY FIGURES, RE-MEASURED AND ACCEPTED

- **My read-only counterexample was stale by one commit.** I reported 15 commits / 16 paths;
  re-measured at `a550796d` it is **16 commits / 18 paths** — I kept committing while writing. Zero
  subject artifacts either way (`grep -c` over the path list for `PACKET|RECOMMENDATION|SPEC-|owners.tsv|Z_CONSTRUCTION|Z_DECISION|.tex|nd-unfolding/` → **0**). **The direction is more favourable than
  I claimed**, which is worth stating because my errors in this campaign have usually run the other way.
- **`AGENTS.md:120` supports the scoped reading, and I had not cited it.** Verbatim: *"Audit and
  review work is read-only. Use isolated worktrees, inspect status afterward, and **never freeze an
  auditor's silent edit into a receipt**."* The named harm is an auditor's *silent edit* frozen into a
  *receipt* — which an openly indexed review document that touches no subject artifact is the opposite
  of. That is textual support for read-only being scoped to the artifact under review.
- **`a11d6cdd` was not the current coordinator's.** §1.

## 4. RELAYED AND **NOT** VERIFIED BY ME — the negative space, made discoverable without a fidelity claim

**This is the section the request was really about.** Each row is *as relayed*, unverified by me, with
the reason I did not verify it. **Nobody should cite these as this lane's findings.**

| relayed item, as reported to me | why I did not verify it |
|---|---|
| clause (d) is sound as a **necessary** condition, **not sufficient** — the retained subspace can be identical while the retained eigenvalues, which `pinv` actually inverts, move arbitrarily | **disqualified**: I supplied that gate (Part J §J.2). I take no view, including on the favourable parts |
| clause (d)'s `1e-8` is **not load-bearing** — anything from `1e-12` to `1e-3` behaves identically, since for orthogonal projectors a rank change gives exactly `1` and a structural match gives round-off | same disqualification |
| clause (d) rests on a **single unreplicated read** | same disqualification. Recorded because it is a **scope limit on a finding favourable to me**, and those are the first to be lost |
| `F3`'s 500-trial split at Z's sparsity: **349** abort blaming the operand, **4** abort with the message §4.3 claims, **147** do not abort and divide by a round-off-positive baseline | §4.3 / `s_proj` routed away (Part K §K.4). My `F6` acceptance rests on the `F6` half only |
| `A-7` not adoptable: `B = 7.107%` against a realized null `s_proj` median of `36.95%` at `N=100`, `K=10`, 100 bins, so `B ≤ S` passes while A-7 reports NOT MET on an object where nothing moved | `A-7` outside my slice |
| §4.4 and §4.4b specify the boundary **two incompatible ways** — computed from band gaps versus chosen as a scalar | same |
| the sharing fraction **flips the sign** of the error: ratio to `B` of `5.17` independent → `1.78` at 90% → **`0.81` at 99%**, where `B` becomes conservative | same. Part J §J.3 addressed only its **routing** (A-7, not A-6), never its numbers |
| the cited invocation *"could not have completed"* because that arm refuses at the stated indices | reviewer's slice; my §M.3 does not depend on it (Part N §N.5) |
| **four candidates raised and killed** by that lane: the §6 *"silent"* objection; the iid-Gaussian burial; the `|U|`/§4.3a coupling; and **my own C6/C7 asymmetry, which it tried to break and could not** | I never received their detail, only that they were killed. **Recorded because a finding list with no rejections reads as a filter that never declines** — and one of the four is an attack on my work that failed, which is the most citable kind |
| the designer/reviewer disagreement on whether the null/`B` ratio is invariant in the variance share, **unreconciled** | routed to the reviewer |

## 5. WHAT THIS RECORD DELIBERATELY DOES NOT ACHIEVE

It does **not** preserve the reviewer's reasoning, only that the items existed and reached me. The
reasoning is what would be lost, and it is not mine to sign for. **The fix remains option 2 to
Joseph** — a review lane authorised to commit findings and verdicts only, never a change to the
artifact under review — with the label naming a **session** rather than a role. This record is the
achievable half, and it is worth exactly what a receipt is worth: it proves something arrived.

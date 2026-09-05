# Wave 1 acceptance — reviewer PASS on `7708c24c`, and what that PASS does and does not cover

**Status:** terminal record of the Wave 1 integration review. The integration ledger
`INTEGRATION-20260903-wave1-routing-freeze-and-ledger.md` remains the evidence; this record fixes the
verdict, its exact scope, and the state carried forward past the closeout so that neither can be
reconstructed later from memory or from a summary.

## 1. The verdict

| field | value |
|---|---|
| verdict | **PASS**, zero live findings in the reviewed lanes |
| object graded | commit `7708c24c69baf27e38eb8dbfc57745b331c7d9c4` |
| branch | `wave1-integration-20260903`, pushed, at that commit when signed |
| signed | 2026-09-05, by the independent reviewer that issued rounds 1–10 |
| base | `dae18f226a5c679e3a60ba7d875e3bfbf43f96ac`, the `main` this work started from |
| ruling record in force | `DECISION-20260902-joseph-rules-cause7-cause3-and-the-stop.md`, sha256 `0836139b1c9a057c194a81a94d45c9f979209a9ac293d4bc8434e6b43fc1a064` |

The graded object is a commit, not a branch name: `wave1-integration-20260903` may move again, and a
PASS attaches to the tree that was read. Ten review rounds preceded it; every withdrawn tip is listed
in the ledger, and each round's findings and their remedies are in ledger §6 through §16.

## 2. The scope the PASS covers, in the reviewer's own words

The grading boundary is ledger §15.1, adopted verbatim from the reviewer after this lane's own
proposal in §14.2 was shown to be drawn in the wrong place:

> **In scope:** any route that reaches the kernel or the origin through a layer this guard hooks,
> cooperating or not.

> **Out of scope, by declaration and recorded as residuals (1)–(4):** code inside an already guarded
> process that deliberately bypasses the interpreter to reach the kernel (`ctypes`, `cffi`, a C
> extension, a rebuilt interpreter), and files rather than argv on a trusted system prefix (a tampered
> prefix, a repository-local `.git` configuration).

Two lanes were graded against that boundary: the **campaign queue's admission and accounting**
(`docs/orchestration/campaignctl.py` and its control-plane records) and the **deployment guard**
(`nd-unfolding/mnv_guarded_run.py` and its committed shim). The PASS is a statement about those two
lanes at that commit and about nothing else.

**What the PASS is not.** It is not a scientific grade, an adoption, a publication claim, or an
authorization to spend. No artifact is adopted by it; no `OI-*` row changes state because of it; no
number in `VALIDATION_LEDGER.md` moves. R5 authorizes a **stop**, not spending. Cause-3 compute
remains suspended by §5 of the ruling record. PET remains diagnostic. The queue admits no item at all
until a receipt measured on Perlmutter is committed, and none is.

## 3. State carried forward, explicitly

* **The OI-73 regeneration hold stands.** `docs/orchestration/LIVE-STATE.md` was NOT regenerated as
  part of this work or this closeout, and `generate_live_state.py --check-freshness` therefore reports
  `STALE` by design at the landed head. That staleness is the hold, not a defect, and only OI-73's
  owner lifts it.
* **Accepted baseline failures, unchanged by this work.**
  `test_mnv_guarded_run.py::TheRefusalIsUnchanged::test_site_packages_is_still_ignored_and_absent`
  fails under an ephemeral `uv` build environment whose `site-packages` is empty — the arm is vacuous
  there — and passes under the system interpreter. A whole-directory run of `docs/orchestration`
  reports a set of environment-dependent failures that predates this work; the comparison that matters
  is against the saved failure SET, not against a count, and no member of it is new at the landed head.
* **Named residual ownership.** Residuals (1)–(4) of ledger §15.1 belong to **OI-136's owner and its
  row**, not to this integration and not to whoever reads this record next. They are measured rather
  than asserted; the measurement is in the ledger, and nothing here discharges them.
* **One decision left open for the operator, and it is not the reviewer's.** The queue no longer reads
  `~/.gitconfig`, and it admits a `credential.helper` in its own git directory only as a bare helper
  name. A host that would run an unattended tick therefore needs its credential settled first. That is
  Joseph's or the site owner's call. **No unattended execution is configured by this closeout.**

## 4. What landed, and how

`main` was fast-forwarded to the graded commit, so the reviewed tree is `main`'s tree byte for byte
and `7708c24c` is an ancestor of `main` rather than a merge parent whose content was re-derived. This
record is committed on top of it as the closeout. Nothing else was changed to land it: no functional
delta was required, so nothing went back to the reviewer.

Preserved deliberately by this closeout: every unrelated branch and worktree (none deleted), the
untracked working files in the checkout, the nine `pet-gate6` refs, and the fact that the real origin
holds **no** `refs/campaign/*`. No compute was launched, no scheduler or cluster was contacted, and no
receipt was committed.

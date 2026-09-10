# DECISION — Joseph rules endpoint B deferred (not passed), orders finite-ensemble disclosure for endpoint A, and sets the cause3_corr / released-error-bar adequacy checks

**Status:** RECORDED. **Owner of the decision:** Joseph.
**Ruling given:** 2026-09-10T19:31:56Z, in the orchestrator session's live conversation — verbatim in
**Appendix A**.
**Recorded by:** the orchestrator session (`claude-orchestrator`), which coordinates the
`z-criteria-designer` and `z-independent-assessor` lanes this ruling is addressed to, but authored
neither PACKET-20260910 nor either lane's analysis. **Recorded at:** 2026-09-10T19:56:37Z (commit
`a11d6cdd`, author and committer timestamp identical), **tree at recording** `6f24fb00`.
**⚠ CORRECTED:** the first revision of this line read *"2026-09-10T20:0X (see commit timestamp)"* —
a placeholder written before the commit landed, never replaced with the value the commit itself
carries, and the field cited its own authority incorrectly by about four minutes. Caught by the
mathematical reviewer, who checked the field against `git show -s --format='%ai%n%ci' a11d6cdd`
rather than trusting it. Corrected here, in the same style `DECISION-20260907` uses for its own
date-field correction.
**Rules on:** the two reserved inputs left open by `PACKET-20260910-z-consumer-set-and-endpoint-requirements.md`
§6 — whether any generator significance is quoted at all, and clause (v)'s finite-ensemble disclosure
disposition for Z — plus three new adequacy tasks for the endpoint-A acceptance packet.

**CITABLE FOR:** that endpoint B (generator significances, p-values, calibrated exclusion claims
that are Z-dependent or non-2D) is **DEFERRED, NOT PASSED**, and that reopening it requires a
separate proposal and authorization; that finite-ensemble disclosure for endpoint A is **disclosure
only** — not validation of a reference distribution, not a bias correction, not scientific adoption;
that `cause3_corr` may not be silently removed from endpoint A or used to mark cause 3 MET without an
identified, sound contract amendment; that retained-rank/subspace stability (A-4) does not by itself
establish stability of the released error bars, and a criterion for that must be shown or proposed.

**NOT CITABLE FOR:** any criterion adoption, any contract amendment, any production compute, any gate
movement, or any publication change. The ruling's own closing sentence is explicit: *"No compute,
criterion adoption, or publication edits are authorized by this message."*

---

## 0. What this document is, and what it is NOT

**THIS RECORD IS TRANSCRIBING JOSEPH'S RULING, NOT GRADING IT, AND NOT ELABORATING IT.** Appendix A
is the ruling verbatim, character for character, from the live conversation transcript. Section 2
separates that verbatim text from the orchestrator's own paraphrase/elaboration of it (sent
onward to `z-criteria-designer` the same session, four minutes later) — the two are not the same
document and this record does not let them merge into one voice.

**DECLARED INTEREST.** This lane (the orchestrator session) is the one that created the problem this
record exists to close. It relayed the ruling below to `z-criteria-designer` at 19:36:00Z, then —
without retaining that it had just done so — sent a contradictory "status check" to the same three
peers at 19:44:02Z stating that both of these inputs were still outstanding and nothing proceeds
without them. `z-criteria-designer` caught the contradiction on its own and asked which message was
current rather than guessing; it had already begun acting on the correct one and was right to. The
independent assessor's `FINDING F-0` — that neither this ruling nor "Joseph accepted outcome (2)"
exists as a committed `DECISION-*`/`RULING-*` record in any of 131 local+remote refs — is itself
correct and is the direct cause of this file's existence. What keeps the orchestrator's interest from
being a thumb on the scale here: the ruling is quoted verbatim, not summarized, and this record
changes no scientific content — it only gives F-0 a landed text to point at.

**Why the status-check contradiction happened is not established here** and this record does not
speculate about it. What is established, from the raw transcript, in the order it occurred:

| ts (UTC) | event |
|---|---|
| 2026-09-10T18:30:37Z | `/compact` issued |
| 2026-09-10T18:33:01Z | post-compaction summary generated (accurately stated, as of that moment, that outcome (3) was awaiting Joseph on both inputs) |
| 2026-09-10T19:31:56Z | Joseph's ruling (Appendix A) — a genuine, directly-typed user turn |
| 2026-09-10T19:36:00Z | orchestrator relays the ruling to `z-criteria-designer` as "Ruling 1" / "Ruling 2" / three tasks |
| 2026-09-10T19:44:02Z | orchestrator sends a "status check" to the same three peers stating both inputs remain outstanding — contradicting the 19:36:00Z message in the same session |
| 2026-09-10T19:46:20Z | `z-criteria-designer` flags the contradiction rather than picking a side, and states it is proceeding on the 19:36:00Z message because it postdates the status check's premise |

The designer's read is correct and this record ratifies it: the 19:36:00Z relay is the current one:
verbatim to Joseph's own words, sent from a genuine same-session user turn, with no compaction or
summarization boundary between the ruling and its relay. Work proceeding on it since 19:36:00Z is not
retroactively unauthorized by the later, mistaken status check.

---

## 1. What is decided

1. **Publication scope.** For the current publication: do not quote Z-dependent/non-2D generator
   significances, p-values, or calibrated exclusion claims. The validated 2D scope is preserved
   unchanged. **Endpoint B is deferred, not passed.** Reopening it requires a separate proposal and
   authorization — deferral does not read as conformance, and B-2/B-3/B-4 remain undischarged
   requirements, not closed ones.
2. **Finite-ensemble disclosure (endpoint A).** Record, per sample-covariance block: the verified
   ensemble size and the normalization convention. State explicitly where no finite-ensemble
   treatment was applied. Where no inversion is performed, mark the inverted dimension not
   applicable; otherwise report it. Disclosure only.
3. **`cause3_corr` disposition.** Identify the exact contract amendment required to defer
   `cause3_corr` from endpoint A. Do not silently remove it, and do not let its removal or deferral
   be what makes cause 3 MET — if it is, the amendment as proposed is unsound and must be reported
   as such, not adopted.
4. **Released-error-bar adequacy.** Retained-rank and subspace stability (A-4) do not by themselves
   establish stability of the actual released error bars. Show which criterion controls changes in
   the released bars under estimator-baseline variation; if none exists, propose one with its
   scientific justification. The universal-bound approach (outcome (2), already rejected) is not to
   be reopened for this.
5. **Process.** Stop extending the withdrawal/search tooling. Return a compact list of criteria
   ready for approval, unresolved evidence, and the next bounded execution authorization.

No compute, criterion adoption, or publication edits are authorized by the ruling itself.

## 2. What is NOT decided here (orchestrator elaboration, not Joseph's words)

The orchestrator's 19:36:00Z relay to `z-criteria-designer` added citations, code-line pointers, and
one operand finding (`eavailW_covariance.py:442` projects before it diagonalizes, so the off-diagonal
hazard is realized inside endpoint A through the projection step, contra the designer's then-current
§3). That finding and those citations are the orchestrator's own measurement and argument, not part
of Joseph's ruling, and are not re-litigated or re-authorized by this record. They stand or fall on
their own evidence, in the ordinary review loop, exactly as any other lane's claim would.

## Appendix A — the ruling, verbatim

> Publication scope: For the current publication, do not quote Z-dependent/non-2D generator significances, p-values, or calibrated
> exclusion claims. Preserve the validated 2D scope unchanged. Endpoint B is deferred, not passed. Reopening it requires a separate
> proposal and authorization.
>
> Finite-ensemble disclosure: Record each sample-covariance block's verified ensemble size and normalization convention. State explicitly
> where no finite-ensemble treatment was applied. Where no inversion is performed, mark the inverted dimension as not applicable; otherwise
> report it. This is disclosure only—not validation of a reference distribution, a bias correction, or scientific adoption.
>
> Please now return the endpoint-A acceptance packet for decision, with only the remaining requirements for constructing and releasing Z's
> covariance and declared projected uncertainties. Identify the exact contract amendment required to defer cause3_corr from endpoint A; do
> not silently remove it or mark cause 3 MET.
>
> One targeted adequacy check remains: retained-rank and subspace stability do not by themselves establish stability of projected
> uncertainties. Show which criterion controls changes in the actual released error bars under estimator-baseline variation. If none
> exists, propose that criterion and its scientific justification. Do not reopen the universal-bound approach.
>
> Stop extending the withdrawal/search tooling. Return a compact list of criteria ready for approval, unresolved evidence, and the next
> bounded execution authorization. No compute, criterion adoption, or publication edits are authorized by this message.

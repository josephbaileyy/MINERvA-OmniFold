Continue the exact persistent `agy-publication-redteam` conversation UUID
`440f42ef-c271-4f77-a410-a4a999166f44`. This is an independent READ-ONLY
control-plane audit; do not edit files, dispatch providers, submit/cancel
Slurm jobs, touch live worker sessions, or reinterpret scientific results.

The user supplied this proposed simplification:

> Establish one concise live-state dashboard (<=120 lines) containing the
> current DAG node, owners/UUIDs, exact blockers, active jobs, and next
> authorized action. Treat RUNS.tsv as append-only history and stop rereading
> old prompts, migration documents, and superseded dashboards during normal
> turns. Link to canonical science documents instead of restating them.
> Reconcile conflicting status documents, clearly mark historical handoffs as
> archival, and use machine-generated summaries where possible. Apply full
> provenance review to scientific products, but proportionate tests to
> watchers/scheduling utilities. Preserve all worker UUIDs and evidence.

Audit whether this is safe and useful for the current campaign. Read only the
minimum current control-plane sources needed: `docs/orchestration/RUNS.tsv`
(tail/current rows only), `docs/orchestration/QUIET-PERIODS.tsv`,
`docs/orchestration/MIGRATION-TAKEOVER-STATUS.md`,
`docs/orchestration/state/sessions.json`, `docs/orchestration/LIVE-USAGE.md`,
`docs/orchestration/usage-policy.json`, plus the canonical science status docs
linked by `AGENTS.md`. Do not reread historical prompts or migration handoffs
unless a specific current conflict cannot otherwise be resolved.

Return a compact report with:

1. PASS / PASS-WITH-CHANGES / REJECT on adopting one <=120-line dashboard.
2. The exact fields and machine sources it should contain, including compute
   placement (interactive holder ID/time-left/current use; queued/running batch
   job IDs/resources/dependencies) and provider capacity evidence.
3. Which current docs become canonical live inputs, append-only history, or
   explicitly archival/index-only. Do not recommend deleting evidence.
4. Fail-closed invariants that a generator/checker must enforce (UUID
   preservation, no stale receipts as live state, no uncommitted scientific
   result, no double-counted school aliases, protected reset credits, and no
   automatic polling/wake loops).
5. The smallest safe implementation sequence and proportionate tests.
6. Any present contradiction you can prove with exact file/line references.

Keep the answer under 1,200 words. No file edits.

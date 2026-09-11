# Repaired PET source audit: execution authorization

On 2026-09-10 Joseph gave the following instruction directly to the executing Claude Code
session (`https://claude.ai/code/session_01HBxWRymzRL6YUkwh7srTww`). It is reproduced
verbatim and is the authority recorded in the external authorization JSON:

> Continue the PET work in MINERvA-OmniFold.
>
> Fetch origin/pet-prong-semantics. Read the execution packet at documentation commit 5117d8c7a877cb902e1b7cde5161e97f3ab8b6bb:
>
> nd-unfolding/pet/SOURCE_AUDIT_REPAIRED_PACKET-20260910.md
>
> I authorize ONE bounded real-source audit under that packet, including SSH, the specified interactive CPU allocation, and committing and
> pushing the resulting authorization and evidence records.
>
> Execute only the tested code commit:
> ca34a03a9f04ec16b56064c5bc6faaf85b9ebf17
>
> Required preparation SHA-256:
> fea412de2f1f4702873e6f62ae98ef6bdfe8e0da65b5ef5066c4cd1cdd4057c3
>
> Use a clean isolated execution checkout. Read the applicable AGENTS.md and routed requirements, check live-state freshness, query the
> scheduler directly, and verify the preparation and tested runtime before source access. Record this instruction as the authority when
> creating the external authorization JSON from the disabled template.
>
> Scope: the two pinned sources, 75 branches, entries [0,4096) per source. Use two CPUs per step, at most six reserved CPUs for 15 minutes,
> four observed process threads, and the packet’s unchanged memory, output and process limits. Use its fresh output directory and unchanged
> import guard.
>
> The complete synthetic preflight already passed; do not repeat it unchanged. Perform the real-source audit and report mapping, semantic,
> release and object-family verdicts separately. Require the source launcher’s accounting.json and terminal scheduler evidence.
>
> On failure, preserve the evidence and stop. Do not retry, change code or tolerances, widen scope, select a passing subset, fit
> normalization, train, construct covariance or reopen Gate 6.
>
> Verify transferred evidence hashes, update the relevant run log and status records, commit and push the results, and report the remote head
> and exact outcome.

## External authorization JSON

The JSON was copied from
[the disabled template](SOURCE_AUDIT_REPAIRED_AUTHORIZATION.template.json) at `5117d8c7`.
Only `execution_authorized` (set to `true`) and `authority_reference` (set to a record of the
instruction above, its packet, code commit, preparation digest, scope and limits) were
changed; every other field is byte-for-byte equivalent to the template. It was placed at
`$SCRATCH/pet-v2-source-audit-repaired-20260910/authorization.json`, outside the execution
checkout. Its SHA-256 is
`4e1b9b8520a332780e7937d052ce602bd3f25f51549da0813e9c0486e6952704`, which was passed to the
launcher. The exact bytes are preserved at
[`source_audit_runs/20260910-repaired/authorization.json`](source_audit_runs/20260910-repaired/authorization.json).

This grant covers one attempt only. It is now consumed; see
[the result record](SOURCE_AUDIT_REPAIRED_RESULT-20260910.md). It authorizes no retry,
normalization fit, `pass_reco` sidecar, training, covariance construction, central-value change
or Gate-6 action. The exact Gate-6 keys remain:

```text
do_not_select_passing_subset
do_not_construct_C_ML
do_not_move_central
do_not_start_leg_2
do_not_retry_unchanged
```

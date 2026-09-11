# Repaired PET source audit: execution proposal

PET typed descriptors are diagnostic and method-development infrastructure for
MINERvA OmniFold. This packet prepares one bounded real-source audit after the
synthetic Linux runtime repair. It is not execution authorization. The included
JSON template has `execution_authorized: false`; leave it disabled until an
explicit user instruction approves this packet's real-source execution.

## Immutable inputs and completed work

- Branch carrying this packet and its evidence: `pet-prong-semantics`.
- Exact execution commit: `ca34a03a9f04ec16b56064c5bc6faaf85b9ebf17`.
- `SOURCE_AUDIT_BINDINGS.json` SHA-256 at that commit:
  `fea412de2f1f4702873e6f62ae98ef6bdfe8e0da65b5ef5066c4cd1cdd4057c3`.
- Terminal synthetic evidence commit: `a48fc6b0`; preserved records are in
  `runtime_runs/20260910/linux-roundoff/`, including the preservation manifest,
  receipt, runtime summary, scheduler record and verification scope.
- Linux allocation `58178592`: complete, 8,192 fake rows, 512 typed chunks,
  four observed process threads, zero source opens. All source-audit unit tests
  (67) passed. See [the runtime record](SOURCE_AUDIT_RUNTIME-20260910.md).

Fetch the branch and retain a documentation checkout containing this packet.
Create a separate clean detached execution checkout at the exact execution
commit; this packet intentionally lives later than the tested code. Do not
substitute the latest branch head, repin code or reuse an old authorization.
The earlier source grant at `58832843` is terminal and does not apply.

## Quantity to measure

Open only the data and MC identities, UUIDs and manifest-line-1 bindings in the
execution commit's preparation file. Read entries `[0,4096)` once per source,
data before MC, using exactly its 75 ordered branches and 16-row chunks.
The quantity is raw-source-to-typed-row mapping plus fixed-source semantic
telemetry. Preserve raw values, component masks, membership and event alignment;
run the fixed-weight forward checks and exact shard round trips. Record mapping,
semantic, release and object-family verdicts separately.

The complete source contract and exact launcher interface are in
[SOURCE_AUDIT_RUNBOOK.md](SOURCE_AUDIT_RUNBOOK.md). Source release applicability,
PID calibration, particle overlap, population support and scientific coverage
are not established by a passing mapping check. Do not force unresolved semantic
or release verdicts to pass. This run does not implement `pass_reco` selection.

## Proposed runtime and resource ceiling

Use the tested Python 3.11 runtime with ROOT 6.28/12, NumPy 1.26.4,
SciPy 1.16.3, TensorFlow CPU 2.16.2 and Keras 3.15.1; set
`TF_ENABLE_ONEDNN_OPTS=1`. Dependency pins are in
`source_audit_runtime_requirements.txt`. The preserved `run_compute.sh` and
`run_allocation.sh` identify the previous environment configuration; observe
its current availability rather than assuming the scratch runtime survives.
A missing or changed runtime blocks source access pending restored compatibility.
Do not install dependencies or repeat the unchanged full synthetic campaign as
part of this source grant. Keep ROOT conda activation before the isolated Python
invocation; do not enable shell nounset around conda activation.

Propose one shared interactive CPU allocation, requesting two CPUs and 8 GiB for
15 minutes. Scheduler rounding may reserve at most six CPUs; this caps reserved
capacity at 1.5 CPU-hours. Every audit step requests exactly two CPUs. Refuse and
release an allocation above the ceiling before source access. One configured
worker per TensorFlow/native pool and four observed total process threads remain
fixed. Approval of this packet would supersede the original source proposal's
two-thread ceiling for this single attempt. No GPU. The installed 8 GiB address-space/RSS ceiling, 30-minute process
wall ceiling, one-hour process CPU ceiling, 1 GiB aggregate output ceiling and
32 MiB individual file ceiling remain unchanged; the allocation expires sooner.
Never extend it or retry an interrupted run under this proposal.

The proposed fresh output root is `$SCRATCH/pet-v2-source-audit-repaired-20260910`.
The `audit` child must not exist. Place the newly authorized JSON and guard
inventory beside it, outside the clean execution checkout. If that output root
already contains a source attempt, stop and report it; do not overwrite, resume,
choose replacement sources or silently choose another output root.

## Before source access

Read the checkout's `AGENTS.md`, the current routing in `docs/CURRENT_WORK.md`,
the workstream reference, this packet, and the exact Gate-6 receipt. On canonical
cluster main run the live-state freshness check, then query the scheduler/source
directly; generated state is not authorization. Inspect and preserve allocation
and step resources. Existing allocation use must fit these same ceilings and
have enough remaining time; do not use unrelated resources merely because idle.

Verify the execution checkout is clean at the pinned commit and run the launcher's
`--check-preparation` mode, which imports no ROOT and opens no source. Check the
preserved synthetic evidence digests and current runtime configuration. The
synthetic probe did not exercise `RootAuditReader` or the source launcher's final
accounting writer: these remain part of this real-source run's acceptance.

Copy [the disabled authorization template](SOURCE_AUDIT_REPAIRED_AUTHORIZATION.template.json)
outside the checkout. Only after the user's explicit execution instruction,
set `execution_authorized` to true and replace `authority_reference` with the
record of that instruction, including its approved packet and limits. Keep all
other template fields fixed. Hash the resulting external JSON. A boolean alone
is not authorization. Preserve the instruction and exact JSON with the result.

After preparing the allocation, runtime and external JSON, the two-CPU step runs
this command from the pinned execution checkout. `AUDIT_PYTHON` is the verified
isolated interpreter, `AUDIT_CHECKOUT` its clean code root, `AUDIT_RUN_ROOT` the
fresh output root, and `AUDIT_AUTH_SHA256` the measured external JSON digest:

```bash
"$AUDIT_PYTHON" nd-unfolding/mnv_guarded_run.py \
  --expect-root "$AUDIT_CHECKOUT" --inventory "$AUDIT_RUN_ROOT/guard.json" \
  -- nd-unfolding/pet/launch_typed_descriptor_source_audit.py \
  --authorization "$AUDIT_RUN_ROOT/authorization.json" \
  --authorization-sha256 "$AUDIT_AUTH_SHA256" \
  --expected-commit ca34a03a9f04ec16b56064c5bc6faaf85b9ebf17 \
  --output "$AUDIT_RUN_ROOT/audit"
```

Retain the unchanged import guard. No direct interpreter bypass, permissive
import allowlist, altered tolerance, feature change or resource relaxation is
part of execution. The rounding budget is derived from operand magnitudes;
repeating the old oneDNN comparison or raising tolerances above an observed
failure is not a remedy authorized by this packet.

## Terminal handling and delivery

A terminal failure is evidence to preserve, not permission to change code,
select a passing subset, widen scope or launch another attempt. On a catchable
failure inspect the receipt and accounting; after a native abort preserve the
interruption marker, progress, native logs and scheduler state. Never backfill a
missing producer receipt or treat missing accounting as source acceptance.

For a complete run require both 4,096-entry lists, all 512 chunks, all mandatory
checks, closed artifact hashes, the guard inventory, native logs, the source
launcher's `accounting.json`, and terminal scheduler state. Report semantic and
release qualifications even if mapping passes. Close or release the allocation.

Preserve exact evidence and verify transfer digests. Commit the execution
authorization record, terminal receipts, preservation manifest, relevant
`ND_OMNIFOLD_RUN_LOG.md` and PET status/runtime records to `pet-prong-semantics`;
update the validation ledger only for the exact evidence class actually measured.
Push the result branch and report its remote head. Do not alter the execution
commit to make its evidence appear to come from a newer implementation.

No normalization fitting, selection-sidecar production, pooling change, training,
bootstrap/containment probe, covariance construction, central-value change or
publication adoption is included. OI-126 remains ruled and PET remains diagnostic.
Read the governing receipt's `prohibitions_applied` keys verbatim:

```text
do_not_select_passing_subset
do_not_construct_C_ML
do_not_move_central
do_not_start_leg_2
do_not_retry_unchanged
```

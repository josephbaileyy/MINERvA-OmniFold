# PET v2 bounded source-audit preparation

**Implementation and local synthetic validation only. Execution is not authorized.**
This implements the source stage of
[SOURCE_VALIDATION_NORMALIZATION_PROTOCOL.md](SOURCE_VALIDATION_NORMALIZATION_PROTOCOL.md).
It does not implement or authorize the normalization pilot or scientific training.

## Entry points and fixed scope

- Checker: `typed_descriptor_source_audit.py`.
- Launcher: `launch_typed_descriptor_source_audit.py`.
- Machine bindings: `SOURCE_AUDIT_BINDINGS.json` (SHA-256 of each listed file,
  ordered 75-branch list, schema, sources, metadata contract, interval and limits).
- Synthetic tests: `../tests/test_typed_descriptor_source_audit.py`.

From the checkout root, this preparation-only command reads local code, manifests
and bindings, with **zero ROOT imports or opens**:

```bash
python3.11 nd-unfolding/pet/launch_typed_descriptor_source_audit.py --check-preparation
```

The launcher has no source, range, branch, selection, thread, retry, normalization
fit or scheduler override. Successful source execution opens exactly the two
manifest-line-1 identities, in data/MC order, and requests each entry from 0
through 4095 once. Early failure can open fewer sources or request fewer entries;
it produces incomplete evidence and never backfills. Both source metadata checks
precede the first payload request. ROOT may decompress full baskets.

The 16-row processing chunks bound working storage and supply one aligned v2
shard each. They preserve all typed tokens and source order. Generic P12 retains
its existing preprocessing; the audit makes no new P12 normalization claim.
No `pass_reco`, truth branches, weights or candidate associations are read.

## Metadata acceptance and provenance qualification

The historical fixed-source receipt binds UUIDs and ordered branch names; it
contains **no historical per-branch type/shape snapshot**. Therefore the pinned
`branch_contract` is an explicit structural acceptance contract, not a claim of
historical type equality: primitive numeric scalars; fixed vectors of width
3 or 4; counted vectors; and nested prong vectors with inner width 4. Dynamic
ROOT vector lengths are checked against the actual row before mapping. A branch
count dependency outside the 75 names fails before payload. Missing declarations,
nonnumeric types and incompatible ranks/static dimensions fail before payload.

Observed ROOT class/leaf declarations, leaf counts and dimensions, UUID, entry
count, file/tree titles, key descriptors and already attached producer-marker
names/titles are retained verbatim in `ROLE/metadata.json`. The metadata digest
binds that observation. Payload archives record the copied numeric dtype and
shape. Unknown C++ types fail closed; synthetic tests do not certify support for
an unobserved native ROOT layout. No whole-file checksum or directory search is
performed. `publisher_checksum: null` means none was provided to this reader;
any checksum text already present in the captured metadata remains verbatim.

This checker cannot establish release applicability from a title or marker.
`RELEASE_UNVERIFIED` and unresolved family verdicts persist even when mapping
passes. Producer attestation for the exact identities, PID enumeration, filler
and reconstruction configuration remains a separate requirement.

## Future authorization and exact execution command

Before source execution, obtain a separately ratified authorization JSON outside
the checkout. This preparation supplies **no such authorization file**. Required
fields are:

```json
{
  "action": "pet-v2-bounded-source-audit",
  "execution_authorized": true,
  "authority_reference": "reference to the separately ratified execution decision",
  "code_commit": "full immutable preparation commit",
  "bindings_sha256": "SHA-256 of SOURCE_AUDIT_BINDINGS.json at that commit",
  "entry_interval": [0, 4096],
  "source_roles": ["data", "mc"],
  "branch_count": 75
}
```

The authority reference must identify the actual decision; setting a JSON boolean
is not authorization. Pin the interpreter/environment in that decision. The
launcher requires Linux process limits and `/proc` accounting, Python 3.11 or
later, NumPy, PyROOT, TensorFlow and Keras. Synthetic validation used Python 3.11,
NumPy 1.26.4, TensorFlow 2.16.2 and Keras 3.15.1. Native ROOT compatibility and the
combined dependency footprint under these ceilings remain unmeasured.

After that decision, from the clean checkout of its `code_commit`, with the
approved file at `../pet-v2-source-audit-authorization.json`, the exact command is:

```bash
python3.11 nd-unfolding/pet/launch_typed_descriptor_source_audit.py \
  --authorization ../pet-v2-source-audit-authorization.json \
  --authorization-sha256 "$(sha256sum ../pet-v2-source-audit-authorization.json | cut -d ' ' -f 1)" \
  --expected-commit "$(git rev-parse HEAD)" \
  --output ../pet-v2-source-audit-20260910
```

Both the authorization's commit and binding digest must match the checked-out
preparation. The command refuses a dirty checkout or existing output directory.
Any cluster execution proposal must additionally follow the fresh-state,
scheduler, environment and `../mnv_guarded_run.py` routes; this command is not a
cluster launcher and supplies no cluster authorization.

## Resource enforcement

The process uses no training or subprocess workers. Native compute thread
settings are fixed to one, GPUs are hidden, and `/proc` checks actual thread
count, RSS, wall time and process CPU use before source operations and writes
and around forward checks. More than two observed native threads stops the run;
an environment that creates extra dependency threads does not receive an
exception to the protocol. Thread observations are boundary measurements, not
continuous monitoring of transient native thread creation.

Linux `RLIMIT_AS` caps address space at 8 GiB (a conservative bound, distinct
from observed RSS); `RLIMIT_CPU` caps process CPU at one hour, with a soft signal
before the hard ceiling; `SIGALRM` bounds wall time at 30 minutes. Existing lower
limits are never raised. Missing platform enforcement fails closed.

Artifact writes enforce the aggregate 1 GiB ceiling with a 128 MiB reserve for
logs, progress, interruption marker, terminal receipt and accounting. Individual
files and each native stdout/stderr log are capped at 32 MiB by `RLIMIT_FSIZE`.
An oversized row/shard stops instead of truncating its contents. Catchable
resource failures retain `receipt.json`; a native abort, hard kill or inability
to finish a receipt leaves `interrupted.json` and `progress.jsonl` as explicit
incomplete records. No `receipt.json`, a missing required artifact, or a missing
`accounting.json` can be interpreted as acceptance. No automatic retry occurs.

## Artifact and receipt specification

All JSON is strict ASCII, sorted-key, compact JSON without a trailing newline;
`progress.jsonl` is newline-delimited. Raw non-finite values are encoded, not
replaced by JSON nulls. The namespace is distinct from v1 evidence.

| Artifact | Contents and binding |
|---|---|
| `ROLE/metadata.json` | Observed source metadata; closed-file SHA-256 in receipt. |
| `ROLE/raw/EEEE.json` | Ordered branch frames with role, UUID, tree, entry, branch name, numeric dtype string, shape and base64 C-order numeric bytes. Ragged sequences retain each child's dtype/shape/bytes. Malformed nonnumeric values and branch extraction exceptions retain explicit type/repr. Saved before validation, mapping or sentinel replacement. |
| `ROLE/observations/EEEE.json` | Source-entry/token-indexed raw PID/score/mass/charge and masks; simultaneous check results; both photon slots and presence states; raw blob fields/conditional zeros; primary and later prong residuals against the tuple-frame lepton; co-occurring counts. |
| `ROLE/typed/AAAA-BBBB.npz` | Exactly 16 aligned rows, v2 descriptors and shard provenance, event keys, role, P12 and 13-wide event block. Save/reload checks exact dtype, shape and bytes for every array, plus v2 schema acceptance and provenance. Closed-file bytes must equal the checked archive. |
| `telemetry-summary.json` | Data/MC and anchor/extension raw-code, sentinel-combination, PID/charge/mask, photon-state and conditional-blob histograms; native ranges and validity support. Partial runs retain accumulated summaries in the receipt. |
| `progress.jsonl` | Attempted, captured and completed-chunk events, flushed without a Python buffer; recovery route for an interrupted native call. |
| `interrupted.json` | Initial durable INCOMPLETE marker. It is superseded only by a complete terminal receipt and accounting. |
| `receipt.json` | Bindings, non-claims, exact restrictions, source metadata, requested/attempted/captured/mapped/completed entry lists, ordered source-row/event keys, duplicate event groups, exceptions with phase/role/entry and traceback, per-check eligible/missing/discrepancy denominators, all four verdict classes, artifact digests and byte accounting. |
| `stdout.log`, `stderr.log` | Native and Python output within the execution boundary, captured to separately bounded files. |
| `accounting.json` | Closed receipt/log/progress/marker hashes, sizes, output bytes, peak observed thread/RSS values and `getrusage`. This outer record avoids a self-hash cycle. Commit its digest in the run record. |

The bounded-payload SHA-256 consumes each closed raw row's canonical JSON bytes,
preceded by its unsigned 8-byte big-endian byte length, in data then MC and
ascending entry order. A per-branch SHA-256 similarly consumes that branch's
canonical frame and length for each captured row. The digests cover only
`captured_entries`, including a malformed row when captured, and are **not ROOT
file checksums**. They bind the numeric observations returned by the reader,
not compressed baskets or unread entries. Closed metadata and artifact hashes
use ordinary SHA-256 over their complete file bytes.

`mapping=PASS` requires completion of all 8,192 requested rows, independent
source-to-typed value/mask/membership checks, source identity alignment, exact
serialization, finite NumPy/Keras agreement and matched 64-column C0/C1 controls.
The identity normalization is labeled `SOURCE_AUDIT_IDENTITY_NOT_FITTED_NOT_FOR_TRAINING`;
reference projectors use seed 0, width 16 and tanh with no fitted weights.
Zero eligible denominators are `NOT_TESTED`. Unexpected values are not cuts.

`semantic=DISCREPANCY` retains every observed correspondence discrepancy;
otherwise it remains `UNRESOLVED` because producer ordering/release evidence is
absent. A vector mismatch is reported as a diagnostic and is not declared a
misordering. `release=RELEASE_UNVERIFIED` and the photon/blob/prong/shared-object
family verdicts remain separately `UNRESOLVED`. Exit zero means mechanical
mapping acceptance only; consumers must inspect the other verdicts.

A future terminal result requires its exact authorization, receipt and accounting,
closed artifacts and required RUN_LOG/STATUS updates committed before citation.
Synthetic acceptance, mapper agreement and round trips are software evidence;
they do not supply independent release or scientific verification.

## Preserved restrictions

PET remains diagnostic/method-development under OI-126. Its existing `C_stat`
construction is unverified and its P5A pairing was declined; no PET total
covariance is adopted. No completed containment, tail-geometry, target-factor,
extraction or occupancy probe is reopened. The exact Gate-6 keys remain:

```text
do_not_select_passing_subset
do_not_construct_C_ML
do_not_move_central
do_not_start_leg_2
do_not_retry_unchanged
```

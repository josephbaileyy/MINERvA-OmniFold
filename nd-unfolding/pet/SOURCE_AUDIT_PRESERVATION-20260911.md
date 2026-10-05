# Completed source audit: CFS preservation

**Complete — all existing audit output copied and read back; scratch retained.**
This preserves the real-source audit recorded at `30de7f64`. The instruction to
proceed with preservation and documentary follow-up covers this copy and its
verification. It does not renew the exhausted source-audit grant or authorize
ROOT access, normalization, training or changes to semantic acceptance.

## Recovery location

The complete plain-file payload is at:

```text
/global/cfs/cdirs/m3246/josephrb/pet-source-audits/20260910-repaired/payload
```

The enclosing directory contains `STARTED.json`, `manifest.json` and
`COMPLETE.json`. Its payload is a copy of the whole scratch output root,
including the `audit` child, authorization, launch scripts, logs and scheduler
records. It contains captured raw/observation/typed shards; it does not contain
or copy the original ROOT source files.

The scratch original remains at:

```text
$SCRATCH/pet-v2-source-audit-repaired-20260910
```

No source deletion, relabeling or original-receipt rewrite occurred. The CFS
location is an additional verified copy; this record is not a claim about
future storage integrity or retention policy.

## Checks performed

The exact executed standard-library preserver and its records are committed
under `source_audit_runs/20260910-repaired-preservation/`.

1. Check the scratch receipt against the committed receipt SHA-256 and its
   accounting binding. Reject existing destinations, symlinks and special files.
2. Hash every regular file in the scratch output. Check all receipt-bound and
   accounting-bound auxiliary artifacts against the recorded byte counts and
   hashes before copying.
3. Copy into a new CFS directory and independently read/hash every copied file.
4. Rehash the scratch directory after copying. Require equality among the
   before-copy, after-copy and destination inventories, including file names,
   byte counts and SHA-256 values. Write `COMPLETE.json` only after all agree.
5. Transfer the preservation records and verify their manifest and preserver
   hashes. Preserve both compressed and uncompressed manifest hashes in the
   committed `transfer-manifest.json`.

| Measured item | Value |
|---|---|
| Complete copied files | 16,915 |
| Complete copied bytes | 283,225,129 |
| Receipt-bound artifacts checked | 16,899 |
| Accounting-bound auxiliary files checked | 4 |
| Source before/after inventories | Equal |
| Destination readback inventory | Equal to source |
| Completion UTC | 2026-09-11T08:33:32.327959+00:00 |
| Source receipt SHA-256 | `5e8d545b6a8b45ed1872852417c13518472b0fbb07832faf78c39406e153b3da` |
| Full inventory SHA-256 | `41c85268be416ecd86c29e6919f030d87fa37ca01c8197a095ad63666f381719` |
| Executed preserver SHA-256 | `d03fc32c8ce3a6710a77e39cf982bfa9ccc52d5debaa5c8fac3fffc2b60c01ed` |

The 16,915-file count covers the full output root, beyond the 16,899 artifacts
inside the audit receipt's scope. It is not an increased sample or a newly
produced set of scientific artifacts. Hash verification is a preservation check,
not independent scientific validation of the audit construction or verdicts.

The preserver's local synthetic check verifies exact-byte copying and the
completion marker, refusal to overwrite an existing destination, and refusal
of a tampered receipt-bound input before copying. Black, Ruff and strict mypy
pass on the preserver. The source-audit execution code and its bindings remain
unchanged; this storage work imports no ROOT and opens no ROOT sources.

## Recovery procedure

Read the committed `COMPLETE.json` and `transfer-manifest.json`; decompress the
committed `manifest.json.gz` and verify its uncompressed SHA-256 against the
completion record above. Compare the CFS inventory and completion records with
these committed copies. To recover elsewhere, copy `payload/` into a new empty
location and compare every recovered file's relative path, byte count and
SHA-256 against that full manifest. Require exact inventory equality, including
absence of missing or extra files; do not rely only on the terminal receipt hash.
The completed CFS destination readback has already exercised reading every file
from this copy. No archive extraction or scientific rerun is required.

## Scientific and documentary state

[The audit result](SOURCE_AUDIT_REPAIRED_RESULT-20260910.md) stays mapping PASS,
semantic DISCREPANCY, release unverified and all object families unresolved.
[The documentary follow-up](SOURCE_AUDIT_SEMANTIC_FOLLOWUP-20260911.md) traces the
time-bound premise, distinguishes grouping keys from unique row identity, and
provides an unsent producer inquiry. These are separate from preservation;
neither the copy nor the inquiry supplies producer attestation.

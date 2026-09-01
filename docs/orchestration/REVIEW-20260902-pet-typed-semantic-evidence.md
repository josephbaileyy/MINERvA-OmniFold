# Independent review of PET typed-semantic evidence

## Review identity and result

This is an independent artifact and method review. It is not an independent
measurement reproduction, and agreement with the originating measurements is
not counted as independent measurement evidence.

| Item | Commit | Result |
|---|---|---|
| evidence base | `d8a59358be65fc924a05f707b8760cb5aff79bf4` | reviewed parent |
| fixed-sample evidence | `d7b365d90a798959b4ee9ec4cf3b463b3ea440bb` | **PASS** |
| M60 archive | `631c3d817cedc1571f6a848df221a2eb3056eca7` | **PASS** |

The review used static repository and external-artifact inspection only. It did
not open a ROOT file, execute a probe, reproduce a payload measurement, or alter
the reviewed evidence.

## Fixed-sample findings

The claims in
`docs/orchestration/PACKET-20260901-pet-typed-descriptor-semantic-evidence.md`
are exact consequences of the committed probe and
`docs/orchestration/runs/pet-typed-semantic-evidence-20260901/fixed-sample-telemetry.json`:

- blob token counts are 208 for data and 155 for MC, with per-row maxima of 90
  and 42;
- photon token counts are 8 for data and 3 for MC;
- prong token counts are 23 for data and 29 for MC;
- present prongs with invalid raw PID number 2 for data and 0 for MC;
- present prongs with valid raw PID 0 number 0 for data and 2 for MC;
- present prongs with valid four-vector energy at most `1e-6` number 2 for data
  and 2 for MC;
- present prongs with valid mass `-1` number 6 for data and 6 for MC;
- present prongs with valid score `-1` number 2 for data and 0 for MC;
- the 50 valid raw charge observations have support `0: 25`, `1: 3`, and
  `2: 22`, while the declared typed categories are `[-1, 0, 1]`; and
- all 11 valid photon direction vectors have norms from
  `0.9999999723394454` through `1.0000000295710847`.

The pinned external paper and source snapshot support the reported internal
conflict over raw prong PID 8. They also support the reported difference between
the downstream filtered prong representation and the mapper's retained raw-row
token structure. The external repository is a downstream consumer, not
authoritative tuple-producer metadata, so neither observation supplies a
replacement semantic rule.

The fixed 32-row evidence does not support M60 photon three-state rates,
cross-playlist claims, blob structural-zero rates, broad prong findings, or
population and distributional conclusions. The fixed-sample and M60 evidence
remain distinct layers.

## Execution-scope deviation

The fixed-sample provenance completely discloses that the source-smoke command
was invoked against both previously bound ROOT sources after a
documentation-only task had been received. Reuse of entries 0-15 did not make
that access authorized. It remains an execution-scope deviation, not an
authorized replay.

The later deterministic replay used a pre-existing shard and did not access
ROOT. That replay does not retroactively authorize the earlier access. The
archived output may document the exact bounded observation and the deviation;
it cannot authorize schema ratification, production integration, further ROOT
access, or a wider sample.

## M60 preservation result

The following M60 measurement families have surviving source specifications,
entry ranges, branch definitions, command or script bodies, and output pairs:

- photon three-state counts and rates in probes 8 and 9;
- cross-playlist and data/MC comparisons in probes 2, 6, and 14;
- blob structural-zero counts in probe 2; and
- prong inventories and distributions in the main probe and probes 2, 3, 6, 7,
  and 8.

These measurements all originate in session `minerva-omnifold-60`. They remain
single-source raw measurements. Their preservation is not independent
verification, semantic adoption, population validation, or citation routing.

The archive correctly marks the following material **UNPRESERVED - NOT
DURABLY CITABLE**:

- the timed-out 200-entry-per-file probe-2 attempt whose partial output was
  overwritten;
- the failed combined metadata/value invocation whose redirected files were
  overwritten;
- claims requiring standalone versions of inline probe programs that never
  existed as separate recovered files; and
- any audit or memory assertion that is not a direct consequence of an exact
  surviving command and output pair.

## Integrity and privacy checks

The following static checks passed:

- all 23 indexed committed M60 artifacts match the byte counts and SHA-256
  digests in `m60/ARTIFACTS.tsv`;
- copied scripts and outputs match their recovered originals byte for byte;
- the external transcript has SHA-256
  `50dad57708ed77aae30eded4f13edbc08a163e38a8ee96cde50bf55ffcdb3742`,
  matching its external-source record;
- all 11 curated command bodies for probes 3-5 and 7-14 match the uniquely
  identified records in that external transcript, including each stored
  command-body digest;
- the curated command record has SHA-256
  `95784e802bc95a95f2321bd3333000179db51e6b23629fe047259458da3dfa09`;
- the fixed-sample probe and output match their recorded SHA-256 digests
  `0b71483705847995425d741700fff6abc399ff482c81b00cbad05ae3c66fb3da`
  and
  `855eaa6bee58341d8368a239d0fc28050873446721624bb47808d5345f8cbeec`;
- JSON parsing and static diff checks passed; and
- bounded credential, private-token, privacy, transcript-shape, and payload-row
  scans found no committed credential, private token, unrelated conversation,
  or payload-derived row array.

The complete M60 session transcript is absent from both reviewed commits. Only
its external disposition, metadata, and digest are recorded. The curated
command record contains the permitted probe identifier, source message
identifier, exact command body, expected output filename, and command-body
digest, without conversation or tool-inventory material.

## Nonblocking limitations

1. The fixed-sample probe validates the schema, 32-row count, role counts, and
   presence of two sources, but it does not fail closed against a predeclared
   shard digest and exact expected source identities before constructing its
   record. The committed output was separately matched to the authoritative
   source-smoke receipt, so this does not invalidate the reviewed packet.
2. M60 did not preserve ROOT-file digests or UUIDs. It preserves exact input
   path specifications rather than byte-level snapshots of those inputs.
3. Successful invocation wrappers for the three standalone M60 scripts survive
   only in the digest-bound external transcript. The repository retains the
   exact scripts, outputs, source and entry scopes, and branch definitions.
4. Exact command and source provenance in the underlying archive necessarily
   retains environment-specific user, scratch, host, and runtime strings. No
   such value was repeated here, and no unnecessary personal narrative or
   credential was found in the reviewed commits.

## Integration and authorization boundary

Both commits are eligible for integration as a PET-only evidence archive. A
future global routing or manifest update must be a separate change based on the
then-current integration base. The M60 layer remains unrouted and single-source
unless a later authorized routing decision says otherwise.

This review does not adopt a category, sentinel, filtering policy, physical
unit, calibration, normalization, semantic replacement, or population claim.
It authorizes no ROOT access, probe execution, training, compute, GPU use,
production integration, Gate 6 action, `C_ML` construction,
central/statistical pairing, central-value move, uncertainty result, coverage
claim, or publication claim. It does not change PET execution behavior, PET
code, 5D state, generated state, a status file, or a manifest.

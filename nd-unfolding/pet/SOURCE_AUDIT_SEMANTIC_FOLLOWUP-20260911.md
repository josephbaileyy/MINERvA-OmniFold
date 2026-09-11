# Source-audit semantic follow-up and producer questions

This is a documentary follow-up to the completed source audit at `30de7f64`.
It uses committed evidence and the existing code/protocol, with no new ROOT
access, sample expansion, fitting, cuts or altered acceptance criteria. The
[terminal result](SOURCE_AUDIT_REPAIRED_RESULT-20260910.md) remains mapping PASS,
semantic DISCREPANCY, release unverified and all four object families unresolved.

## Time-bound provenance

The evidence chain is:

1. [The curated correspondence](PRONG_BRANCH_SEMANTICS.md), field definitions,
   describes candidate start `(x,y,z,t)` and time in ns relative to the beginning
   of a 10 microsecond beam gate. It explicitly says the stated 10,000 ns upper
   bound had not been checked across these sources. This is a curated account of
   reconstruction-side correspondence; the original message and producer source
   are not supplied, and applicability to the exact tuple releases is unverified.
2. [The source protocol](SOURCE_VALIDATION_NORMALIZATION_PROTOCOL.md), section 2,
   turns that premise into a diagnostic flag outside `[0,10000]` ns. It does not
   define an event/object selection cut.
3. `Telemetry.observe` in `typed_descriptor_source_audit.py` at `ca34a03a`
   checks `prong_part_pos[token][3]` against that interval when the mapped time
   component is valid. It retains the observation rather than removing the row.
4. The committed result and five preserved raw/observation pairs demonstrate
   finite values above that check's upper bound in these exact audited entries.

Therefore the measured range conflicts with the asserted universal upper-bound
premise for the audited values. It does not determine whether the discrepancy
comes from an inaccurate range premise, tuple/reconstruction behavior, release
applicability or another cause. It does not disprove the units or reference-time
origin independently. Those distinctions need producer evidence.

No bound, mask, interpretation or verdict is revised here. Raising the bound to
include the largest observation would not resolve its provenance. Preserve the
five values, including the slightly over-bound value, without treating their
rarity as permission to ignore them.

## Repeated grouping keys

`EVENT_KEY_BRANCHES` in `typed_descriptor_source_smoke.py` is exactly
`(ev_run, ev_subrun, ev_gate)`. The audit's `groups` dictionary is keyed by
`(role, playlist, ev_run, ev_subrun, ev_gate)` and records entries for repeated
keys. Source-row identity separately retains role, UUID, tree and entry.

The reported 955 groups therefore establish repeated values of that declared
key. They do not establish byte-identical rows, duplicate physical interactions,
multiple time slices, or a faulty reader. The producer meaning and uniqueness
level of the tuple row and its identifiers remain unverified. No new comparison
of repeated rows was performed for this documentary follow-up.

The existing normalization proposal, section 4, already allows repeated group
keys and keeps every row in a group together. It also reserves the whole group
if any member occurs in the historical `[0,16)` anchor. Thus repeated group keys
alone do not contradict or require a replacement of the proposed split rule.
The earlier recommendation to resolve key granularity before splitting should
not be read as requiring a row-unique key or deduplication. Producer attestation
is needed for physical interpretation and to assess whether this grouping spans
all relevant dependencies; no independence claim follows from a grouping rule.

No split is computed or adopted here. The row-aligned `pass_reco` sidecar,
semantic/release requirements and separately authorized normalization pilot
remain outstanding. Do not add slice branches, change grouping, drop repeated
rows or fit normalization under this follow-up.

## Producer inquiry draft — not sent

Subject: Exact-source time range, row identity and object provenance

For the two audited MasterAnaDev sources below, could you provide a versioned
producer reference or attestation for the following questions? The audit reads
only entries `[0,4096)` and preserves all rows; its mechanical mapping passes.
These observations are diagnostic and have not been used as cuts or training
inputs.

| Role | File | UUID |
|---|---|---|
| Data | `MasterAnaDev_data_AnaTuple_run00010068_Playlist.root` | `bcd43694-ef17-11f0-9717-17a6e183beef` |
| MC | `MasterAnaDev_mc_AnaTuple_run00110000_Playlist.root` | `c0347da6-2a99-11ef-9717-31a7e183beef` |

1. **Release binding:** Which tuple release, reconstruction build/configuration,
   PID enumeration and tuple-filling implementation produced each UUID? Please
   provide versioned identifiers, relevant source excerpts or an attestation
   explicitly covering these identities. A current public-area release label
   or downstream analysis revision cannot bind these files by itself.
2. **Time definition and supported range:** For `prong_part_pos[][3]`, what is
   the unit, zero/reference time, and documented allowed range? Is `[0,10000]`
   a guaranteed bound on stored candidate times for these releases, or a
   description of the nominal beam gate? What producer code and validity/filler
   rules govern values outside that range? The preserved observations are:

   | Role | Entry | Prong token | Stored time |
   |---|---|---|---|
   | Data | 2121 | 0 | 13181.452089379482 |
   | Data | 2704 | 0 | 15159.489724392435 |
   | Data | 3418 | 0 | 13674.652787144687 |
   | Data | 3867 | 0 | 10052.797142089019 |
   | MC | 3654 | 1 | 15980.891188914475 |

   Please distinguish any documented explanation from a hypothesis about these
   particular entries. Raw/observation pairs are committed with the result.
3. **Tuple-row and key granularity:** What entity does one row represent, and
   at what level is `(ev_run,ev_subrun,ev_gate)` unique in data and MC? Which
   producer identifiers distinguish rows sharing it, and can relevant common
   acquisition/reconstruction ancestry span different such keys? The audit
   records repeated keys without interpreting or dropping them. The proposed
   split keeps all rows sharing `(role,playlist,run,subrun,gate)` together.
4. **Object provenance and associations:** Which reconstruction objects feed
   the photon, blob and prong-hypothesis branches? Can objects or underlying
   hits be shared across these containers and with the primary lepton? Please
   provide the relevant filling/association code, primary-prong ordering rule,
   best-hypothesis selection priorities/ties/defaults, and validity conventions
   applicable to these exact tuple versions. State any unavailable or uncertain
   part separately rather than treating a plausible description as verified.

No correspondence has been sent by this follow-up. Release and object-family
verdicts require the reply or corresponding producer artifacts; a drafted request
is not attestation and does not close a gate.

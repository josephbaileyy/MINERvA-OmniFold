# EVIDENCE — cause 7's per-endpoint migration census and declared policy

**Extracted 2026-09-19 as §3 bounded work for a missing check, under Joseph's ruling.** A **read**,
not a production run. Committed here so the citation points at a commit, per his condition 2.

**Cluster reachable before starting** (condition 1): `login27`, `sacct` responding, no outage.

## Source, by path and digest

| | |
|---|---|
| path | `nd-unfolding/active_universe_5d/standard/evidence/p4_merged_audit.json` |
| **sha256** | **`2e3fac26b29c7d29dd19cc82ce65983f45ef677f6c36064dd41bb97c0a12bf9e`** |
| entries | `merged`, **10** — the ten ± endpoints |

⚠ **It is the STANDARD-path audit.** My first search used `-name "audit_merged*.json"` and found only
the **fps** file; the standard artifact is named `p4_merged_audit.json`. A naming-pattern miss, and it
nearly produced a false "missing artifact" report.

## Declared policy — committed code, `nd-unfolding/p4_lib.py:64-65`

```
NONZERO_MIGRATION_BANDS = frozenset({"BeamAngleX", "BeamAngleY"})
ZERO_MIGRATION_BANDS    = frozenset({"MuonResolution", "Muon_Energy_MINERvA", "Muon_Energy_MINOS"})
```

2 + 3 = the five lateral bands. Consumed at `p4_validate_active_lateral.py:92-93`.

## Per-endpoint census vs policy — `SPEC:802`'s abort condition does NOT trigger

| band | ep | `selection_migration_abs` | policy | agrees |
|---|---|---|---|---|
| BeamAngleX | 0 / 1 | `4792` / `4700` | NONZERO | ✅ / ✅ |
| BeamAngleY | 0 / 1 | `4807` / `4808` | NONZERO | ✅ / ✅ |
| MuonResolution | 0 / 1 | `0` / `0` | ZERO | ✅ / ✅ |
| Muon_Energy_MINERvA | 0 / 1 | `0` / `0` | ZERO | ✅ / ✅ |
| Muon_Energy_MINOS | 0 / 1 | `0` / `0` | ZERO | ✅ / ✅ |

**Ten of ten agree.** `SPEC:802` requires abort if a declared-zero band measures nonzero **or the
reverse**; neither occurs.

**Internal identity, all ten:** `selection_migration_abs == census.RecoEntrants + census.RecoExits`
exactly — e.g. `BeamAngleX_0`: `2731 + 2061 = 4792`. The `census` object is the four-param
`{TruthEntrants, TruthExits, RecoEntrants, RecoExits}` the producer emits. **`TruthEntrants` and
`TruthExits` are `0` on all ten** — migration is reco-side only.

## Condition 3 — controls on the extractor itself

| | |
|---|---|
| **positive** | the extractor finds `BeamAngleX_0` and its `tree_entries`, the field `p4_validate_active_lateral.py:105` requires — so a *found* result is not vacuous |
| **negative** | `selection_migration_NONSENSE` is **not** found — so *found* is not returned for everything |

⚠ **THE 12-PLAYLIST CONFIRMATION IS NOT AVAILABLE FROM THIS ARTIFACT, and I am not treating a
near-miss as one.** The condition asked me to confirm the hadd sum covers all 12 playlists. The only
`12` in the record is **`native_miss_playlists_with_misses: 12`** — *playlists with misses*, a
**different quantity** from *playlists summed*. No `n_playlists`, `hadd` or `sources` field exists.
**So: consistent with 12 playlists, not a confirmation of hadd coverage.**

## Ten endpoint identities — by digest, which is stronger than the directory check

Each of the ten records carries its own **`sha256`**, all present, **all distinct**, with
`exists: true` and `zombie: false`:

`BeamAngleX_0 38b9fc30…` · `BeamAngleX_1 0e0491a6…` · `BeamAngleY_0 058746fd…` ·
`BeamAngleY_1 3bca6a45…` · `MuonResolution_0 839ab9c5…` · `MuonResolution_1 33308006…` ·
`Muon_Energy_MINERvA_0 533037d2…` · `Muon_Energy_MINERvA_1 90a1d7b7…` ·
`Muon_Energy_MINOS_0 f105f681…` · `Muon_Energy_MINOS_1 f2e67fd6…`

⚠ **AND THIS CORRECTS MY OWN CITATION.** I had cited `PACKET §15.1:952-953` for the ten endpoint
identities. Re-read, that passage checks **ten directories, uniform at 12 ROOT files and 53.8 GB,
matching `--array=0-119%12` and `N_ENDPOINTS = 10`** — a **directory-uniformity census**: existence,
file count, size, array consistency. It is a real check and it is **not a digest-level identity
binding**. The reviewer's "never checked" was closer to right than my citation was. **The digests
above are the identity evidence; §15.1 is corroborating structure.**

## The two assembly identities beyond `closure.G1–G5`

| field | value |
|---|---|
| **`closure.active_total_eq_sum5`** | **`0.0`** — the active total equals the sum of the five lateral bands, exactly |
| **`closure.blocksum_symmetry_psd`** | `rel_asymmetry` **`0.0`**, `lambda_max 1.205970554862754e-75`, `lambda_min −4.6860865778129674e-91`, `neg_fraction_of_max` **`3.885738800933054e-16`**, `psd_method eigvalsh` |

*(`closure` also carries `G3R_raw_operand_reconstruction` alongside `G1`–`G5`, so the full set is six
`G`-named identities plus these two.)*

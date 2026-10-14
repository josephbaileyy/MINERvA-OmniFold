# Stage D inputs REPORT: independent verification record

**CITABLE FOR:** the independent read-only verifier's findings on the Stage D inputs REPORT at commit
`d534b7ea11fb3a3ad4935cf70dee831fc01a6ebe`, its focused re-review of `d28ba3f5`, and its own re-measurements. These include identity on 1L, 1N and 1B,
per-file read times, the `gregork/Minerva` derived MC and the point-cloud omnifile size.

**NOT CITABLE FOR:** the repaired REPORT. Its disposition of each finding is in the REPORT itself and in the
repair commit. Also not citable for any adoption, grant or coverage claim.

| field | content |
|---|---|
| `Verifier` | a fresh Claude Opus 5.5 (`claude-opus-5-5`) subagent of session `minerva-omnifold-ed`. It did not write the REPORT, and it worked in a separate detached worktree at `d534b7ea`, read-only, ending with an empty `git status` |
| `Object` | `docs/orchestration/state/2d-closeout/stageD-inputs/REPORT.md` and its evidence at `d534b7ea` |
| `Cluster` | login-node reads printed to stdout only; no Slurm job |
| `Text` | the verifier's final report on `d534b7ea`, then its focused re-review of the repair commit `d28ba3f5`, both reproduced verbatim below |

## Verdict: PASS WITH CHANGES

I re-measured the report's main outcomes independently and they hold: overall UNAVAILABLE, input 1 UNAVAILABLE at production size, input 2 UNPRICED with adequacy UNAVAILABLE, input 3 UNAVAILABLE with the limited alternative UNPRICED, and no custodian inside the lanes. The ceiling, the charges and the §8 arithmetic all reproduce. Three statements need fixing, though: the R0 label, two CFS absence claims, and the §3 generator-timing row.

## Findings

### MATERIAL

**M1. R0 is labelled "PRICED (projection)", and the ≥ 0.43 lower bound is not established.** Locations: §1 row 1, §4.5 R0 row, commit message, CATALOG row.
- Labelling a projection PRICED breaks amendment 1 and the report's own NOT CITABLE line ("a statement that a projection is a price").
- §4.5 says R0 is the "same binary … plus the identity branches", and lists checking for an identity-only mode as a pending dependency. That mode does not exist. All four identity write sites are gated on `MNV101_DUMP_POINTCLOUD`, which also writes the full point-cloud schema: `runEventLoopOmniFold.cpp:450,460-474` (truth-denom), `:985,1001-1035` (signal: `part_*`, `mu_*`, `vtx_*`), `:1346,1390-1392` (background), `:753,787-789` (misses). `EVENT_IDENTITY_JOIN_CONTRACT.md` §6 says the same.
- So R0 needs either a code and binary change, or the point-cloud mode. The repo's only identity-carrying omnifile written in that mode is 113,496,440,965 B, about 53× the 2,144,008,221 B production file (`ls -l .../g2_fullevent/merged/runEventLoopOmniFold_G2_FPS_MEFHC.root`; it is also in `populations.tsv` row 10).
- The "≥" is also not secured from below. The P4 unit comes from a census-patched binary on shared nodes, and the recap records 1.55× contention variance.
- Minimal correction: make R0 **UNPRICED**, with the 1L identity-mode measurement as the pricing measurement and 0.43 node-h as the P4 reference projection only. State that no identity-only mode exists at `4c742f35`. §1's "identity rebuild and disjoint sub-production folds are cheap (PRICED …)" also contradicts §4.5's own "folds UNPRICED".

**M2. The CFS absence claims rest on evidence the log does not hold, and one is wrong as written.** Locations: §4.5 ("No other ME-FHC MC exists on m3246 CFS or our /pscratch (`ls -d`, same log)"), §6.1 ("a name scan of its 97 top-level directories, remote log"), §9 row 3.
- `remote_reads_20261014.txt` holds only one CFS MC check (the preservation `MC/` path). It holds no top-level scan and no "97".
- I count 99 top-level directories plus 7 non-directories now (`find -maxdepth 1`).
- A top-level name scan cannot see inside members' directories. `/global/cfs/cdirs/m3246/gregork/Minerva/20260326/{1A,1B}/` holds per-file conversions of ME-FHC MC AnaTuples with our filenames: 41 `MasterAnaDev_mc_AnaTuple_run001100xx_Playlist.pb` for 1A and 11 for 1B, about 200 MB each, group m3246, readable by `josephrb`.
- These are not a production-size bank, so input 1 stays UNAVAILABLE. They do bear on Q2: which release Gregor converted could be answered internally without the 20 GB write Q2 assumes.
- Literally, "No other generator directory exists" is also false: `Herwig7`, `sherpa`/`Sherpa`, `g4` and `geant4-*` exist (none is a neutrino generator).
- Minimal correction: put the scan in the evidence log, or drop the citation. Scope both claims to "no neutrino-generator or AnaTuple directory at top level". Record `gregork/Minerva` as derived ME-FHC MC of unknown release, and add it to Q2 as a route.

### MINOR

- **§3 "GENIE v2.12 truth generation" row.** `3d-unfolding/genie/README.md:129` is the **NuWro** paragraph ("2M events (8×250k parallel, ~5 min)"). The GENIE figure is at `:98-99`: "8 parallel gevgen × 250k, ~9 min on a 256-core node". Fix the line, the generator and the time.
- **§6.1: "the only event files there are the 50–100 GeV GENIE supplements".** `SHA256SUMS-s5p-archive-20261006.txt` also lists `supp/nuwro/nuwro_supp.root`, `nuwro_supp_flat5d.root` and `supp/timing/{genie,nuwro}/` event files.
- **§6.2 and §11 call NuWro throughput, and whether the CVMFS SL7 builds run on Perlmutter, unmeasured.**
  - `README-gen5d-fluxfix.md:189-190` records "gevgen took 4 min per 100k events, NuWro 2 min", single-process on a login node.
  - `3d-unfolding/genie/README.md:118-119` records that NuWro v21_09_1 and GENIE v2 were run from CVMFS using the SL7 workaround.
  - Only GENIE v3 is actually unmeasured. "CH NuWro … UNPRICED" has a documented basis to cite.
- **§6.2: `DESIGN-20260911-…:243-250` is cited for NuWro being "only partly fresh".** Those lines say a CH NuWro or GiBUU sample is "where fresh production would buy something". Restate the claim, or cite a source that makes it.
- **ASSESSMENT line numbers.** Exact-GBT is `:274`, not `:268`. The S-r 2.8/27.0 figure is `:313`, not `:291`. The 43.2–160.9 per-experiment figures are `:249`, which is in §5, not §6.
- **§8: "five orders of magnitude above a single unfold".** 1.84–2.58×10⁵ / 0.065 ≈ 2.8–4×10⁶, which is about 6.5 orders. Per experiment it is about 2.8 orders. The sentence also edges toward a fit argument. Cite delegation §3.4 for NO-GO and drop the comparison.
- **§11 and §4.5 leave the 489-file identity and overlay census UNPRICED, "read time unrecorded".** My own probe read the integer branches in 4.3 s (1L), 5.5 s (1N, 35 GB) and 2.1 s (1B) on a login node. The census is roughly 15–45 login-minutes and could have been measured.
- **Downstream caution.** §4.4 hedges the overlay reading properly. §1, §9 and the CATALOG then state "shared overlaid data gates" without the hedge. My checks support the reading:
  - Data run ranges match: 1A data 6038–10066 and 1E data 16003–16522, from `playlist_manifests/1A_Data.txt` and `1E_Data.txt`.
  - All 37,277 shared gates in 1A `run00110001` link events from distinct MC subruns, with `mc_nthEvtInSpill` = 0 everywhere. So the sharing is reuse across generator jobs, not same-spill multiplicity.
  - The official MAD tuple document (`MinervaExpt/Tuple-Documentation` `MAD_tuple_MainDoc.csv`) has no `ev_*` or overlay rows, so the reading cannot be settled from documentation either.
  - Fix: add "(inferred from values)" wherever the claim is restated.
- **§9 table, row 2.** It states the source key as unique and joinable without scope. Add "4 of 489 at source; rest supported by the G2 derived audit".
- **§7 custodian route "another m3246 member under their own account".** `josephrb` is in group m3246 (`id`) and can read group-m3246 member directories; I read `gregork`'s. Such a holder must restrict group permissions. Add that caveat.
- **§7 one-account claim.** The claim is right, but it cites only the CFS-copy group line. Add the repo evidence: `FINDINGS.md:158` (BEN-533), `PLAYBOOK.md:26` (PB-18), `REVIEW-CONTRACT-20260822-…:1017` ("every leg runs as the same user"), and the other lanes' `sb1`/`xr`/`xrl` jobs in the same `sacct -u josephrb`.
- **§4.3 identity-write citation.** `:450, 460-474` covers the truth-denom tree only. The claim holds for all trees, but cite all four sites.

### COSMETIC

- §2 says "120 rows". The file has 119 data rows, plus a header and a timestamp line.
- §4.6 "9.6 TB by `du -sh` … 10.53 TB in the 2026-10-08 inventory" is one quantity in two units (9.58 TiB = 10.534 TB, from my sum of file sizes). It is not a change.
- §4.2 "In 1,964 of 1,964 subruns … except the double-filled 1E subrun" should read 1,963 of 1,964.
- §4.5 "also meets the CFS 3 TB rule": "meets" should be "is constrained by".
- §4.5 and §6.1 "remote log" claims not in the log: "9.6 TB by du", "12 GB in all" for the genie directory (I measured 12G; it agrees), and "products/gibuu absent" (I confirmed it is absent).

## Recomputed or re-measured

| quantity | my value | report | |
|---|---|---|---|
| Committed grant ceilings (all 10 `AUTHORIZATION-2026101[23]-2d-closeout-*`) | 2.0 + 1.0 + 3.0 + 20.0 = 26.0. P4 retry "unchanged"; exit, binding and binding-v2 raise nothing; pilot 12.9 → 20.0 in the recap, not added again | 26.0 | AGREES |
| Delegation ceiling and NO-GO | §3.2 ≤ 700; §3.4 NO-GO | same | AGREES |
| `2dc_*` charge (own parser, billing from AllocTRES / 921,600) | 3.6267: B4 0.5290 (20), B5 0.7233 (6), C 2.3743 (74: 23 COMPLETED / 1 TIMEOUT / 50 PENDING); no AB or C04 rows | same | AGREES |
| sacct row count | 119 data rows | "120 rows" | DISAGREES (cosmetic) |
| P1 replica unit (12 jobs) | 0.0464–0.0688, mean 0.0571; P1_unit retry 0.0497 | same | AGREES |
| Pilot units (P0 / P0_derived / P2 range / MINOS0def) | 0.0649 / 0.1007 / 0.1189–0.1619 / 0.3468; recap `:24-30` | same | AGREES |
| P4 12-playlist CV loop | Σ ElapsedRaw 99,108 s × 4 / 921,600 = 0.43016; matches stageB diagnostics §5 JobIDs | 0.4302 | AGREES |
| §8 P1 per experiment | 36.87–51.63 | 36.9–51.6 | AGREES |
| §8 P1 at 5,000 experiments | 1.843–2.581×10⁵ | 1.84–2.58×10⁵ | AGREES |
| §8 P2 / event-loop add-on / N2 | 231.9–344.1 / 2,150.8 / 4.64–6.88 | 232–344 / 2,151 / 4.6–6.9 | AGREES |
| §8 "five orders of magnitude" | about 6.5 orders (total vs one unfold) | five | DISAGREES |
| iris / prjquota | 20,000 − 17,193.7 = 2,806.3; 81.5 % | 2,806.3; 81 % | AGREES |
| MC AnaTuples on cluster | 489 (per playlist 41/11/21/61/51/71/61/6/98/31/16/21); 10.534 TB | 489 | AGREES |
| `MEFHC_MC.txt` lines | 489, no duplicates, equal to the union of the per-playlist lists | 489 | AGREES |
| Identity on unmeasured playlists (own probe, tuple `np.unique`, no packing) | 1L `run00113003`: reco 175,574 / Truth 542,956, 0 duplicates, all reco in Truth. 1N `run00113275`: 302,376 / 942,526, same. 1B `run00111005`: 186,905 / 549,784, same | (not measured) | AGREES with the claim |
| Production omnifile | sha256 `43f8cc16…`, 2,144,008,221 B, mtime 2026-05-18; four trees, no identity-like branches | same | AGREES |
| Overlay reuse, 1A `run00110001` | 76,603 events on 37,277 shared gates; all shared gates span distinct subruns | 76,603 / 37,277 | AGREES |
| CFS MC path absent | `ls`: No such file or directory; parent `drwxr-sr-x`, so listable rather than merely traversable | absent | AGREES |
| CFS gen5d and gen5d_fluxfix; pscratch GENIE/NuWro/GiBUU files | present (`drwxrwx---`, owner-readable); 80 GiBUU tasks; genie directory 12G | present | AGREES |
| "No other ME-FHC MC on m3246 CFS" | `gregork/Minerva/20260326/{1A,1B}` derived MC (.pb) present | none | DISAGREES (M2) |
| CFS top-level directories | 99 directories plus 7 non-directories | 97 | DISAGREES (minor, unlogged) |
| Active-universe merged directory | 21 entries (10 ROOT, 10 logs, SHA256SUMS) | 21 | AGREES |
| One Unix account | `uid=josephrb`; repo practice BEN-533 / PB-18 / REVIEW-CONTRACT:1017 | one account | AGREES |
| `generate_manifest.py --at-sha d534b7ea… --check` | OK exit 0, rows 2741, LIVE 352 | OK, 2741 | AGREES |
| CATALOG row and override row | CATALOG text matches §1; override `LIVE open`; MANIFEST row LIVE | as stated | AGREES |
| §10 contains no draft message | Q1–Q7 are questions only | | AGREES |

Citations checked and correct, apart from those flagged above:
- `runEventLoopOmniFold.cpp:1764-1844`, `:1785`, `:450,460-474` and `:532` (dedupe)
- the stageAB/fluxrepair/diagnostics/p4-retry/recap lines in §2
- `EVENT_IDENTITY_JOIN_CONTRACT.md:254-266,268-275,285-293`
- DESIGN-20261008 `:216-219,240-246,258-280,494`
- ASSESSMENT `:258-263` and §7
- RECORD-20261009 `:58-60,66-69` and §3
- `OPEN_ITEMS.md:185`
- `replicate_inputs.py:86-100`
- `README-gen5d-fluxfix.md:158-159`
- the model memo `:31`
- valencia `:268`; inelastic `:754,1034`
- PROPOSAL `:308-316`
- `compare_to_models.py:5`
- `3d-unfolding/genie/README.md:144-198,234-235`
- stageB REPORT §2.3/§2.6/§2.7/§3 (n_eff 19.1, 185/187, `MaxMuonAngle(20°)`)
- stageB diagnostics §2 and §5, which do carry every P4 JobID and timing
- the recap, which carries the pilot JobIDs and timings.

## Not checked
- Whether `gregork`'s .pb files come from the older or the current open-data release. Answering that means reading another member's data, and it is a question for Joseph or Gregor.
- Measured throughput of GENIE v3, and whether the v3 builds run on Perlmutter. That needs execution.
- The historical `sacct` cost of point-cloud-mode event loops (the G2 or p3f runs), which could price R0's overhead. I found no committed receipt quickly.
- The 1E double-fill and the 1A–1A 66,657 shared-gate figure. I did not re-run them; they come from the lane's evidence outputs only.
- The pilot's current state after 07:21Z. It is moving and outside this report.

## `git -C /Users/josephbailey/local-research/MINERvA-OmniFold-stage-d-verify-20261014 status --short`
```
```
(empty; HEAD `d534b7ea11fb3a3ad4935cf70dee831fc01a6ebe`)

Probe scripts went only to my scratchpad, `/private/tmp/claude-501/-Users-josephbailey-local-research-MINERvA-OmniFold/7c1fcb17-c356-416d-9b7b-fb768bb6d284/scratchpad/verify/`, along with a downloaded copy of the official MAD tuple CSV (`mad.csv`). On the cluster I ran only reads that print to stdout.

---

# Focused re-review of the repair commit `d28ba3f589362c6e18b212b6188492de11de2ce0` (verbatim)

## Re-review of d28ba3f5: PASS WITH CHANGES

The writer resolved all 19 of my findings except M1, which is only partly resolved. Every outcome label is now consistent: no "PRICED (projection)" and no "≥ 0.43" is left anywhere in the REPORT, the CATALOG row or the commit message. Two small text fixes are still needed (N1 and N2 below), plus a few cosmetic ones. None of them changes an outcome.

### Per-finding status

| finding | status | evidence at d28ba3f5 |
|---|---|---|
| M1: R0 labelled PRICED; the ≥ 0.43 bound not established | **PARTIAL** | Fixed: §1 row 1 (`:64`), §4.5 R0 row (`:211`, price "**UNPRICED** … not a lower bound"), N2 (`:304`), §9 (`:320`), CATALOG and commit message. §4.3 (`:165-172`) now states that no identity-only mode exists and names the two routes. **Remaining:** the R0 row's own production-law column (`:211`) still says "same binary, inputs and environment, plus the identity branches", which contradicts `:166` and the same row's dependency column. |
| M2: CFS absence claims unsupported, and one wrong | **RESOLVED** | `:214`, `:251-255` and `:320` scope the claims to the top level, record `gregork/Minerva` and point to the new evidence file. Q2 now has the internal route (`:338-341`). |
| §3 GENIE row cited the NuWro line | RESOLVED (citation off by one, C1) | `:97-99` split into GENIE, NuWro and login-node rows |
| s5p archive: GENIE-only event files | RESOLVED | `:248-250` |
| NuWro and SL7 builds called unmeasured | RESOLVED | `:278-279`, `:364-365` |
| DESIGN-20260911 misquoted | RESOLVED | `:279` quotes "where fresh production would buy something" and leaves freshness open |
| ASSESSMENT line numbers | RESOLVED | `:96` (`:274`), `:212` (`:313`), `:307` (§5 `:249`) |
| "five orders of magnitude" | RESOLVED | dropped; `:308` cites NO-GO under delegation §3.4 only |
| census left UNPRICED | RESOLVED | `:213` and `:358-359` give a 15–45 login-minute PROJECTION |
| overlay hedge missing downstream | RESOLVED | `:64`, `:174`, `:324` and the CATALOG all say "inferred" |
| §9 identity scope | RESOLVED | `:320` ("4 of 489 … plus 3 more by the verifier") |
| custodian group-permission caveat | RESOLVED | `:286` |
| one-account citations | RESOLVED | `:286`. I re-opened `FINDINGS.md:158`, `PLAYBOOK.md:26` and `REVIEW-CONTRACT…:1017`; all say what is claimed. |
| identity write sites (all four) | RESOLVED | `:161-163`. I re-opened `:753`, `:787-789`, `:985`, `:1001-1035`, `:1346` and `:1390-1392`; all correct. |
| "120 rows" | RESOLVED | `:76` ("119 job rows") |
| 9.6 TB vs 10.53 TB | RESOLVED | `:221` (TiB, "the same quantity") |
| 1,964 of 1,964 | RESOLVED | `:145` |
| "meets" the 3 TB rule | RESOLVED | `:214` ("is constrained by") |
| remote-log claims not in the log | RESOLVED | The repair log carries 9.6T (`:31`), 12G (`:32`) and gibuu absent (`:34`). |

### New findings (MINOR)
- **N1. The R0 row overstates the size of a point-cloud R0.** `:211` says the point-cloud mode's "output is about 53× larger". The 53× file is the full-phase-space G2 omnifile, with 49,906,108 signal rows against the 2D file's 32,849,103. §4.3 (`:172`) correctly says "Its selection also differs". A 2D-selection point-cloud R0 would be roughly 35× by row scaling, and that is a projection. Fix: say "the one point-cloud-mode file (FPS selection, 1.5× the rows) is 53× the production file", and fix the leftover "same binary" text from M1.
- **N2. "cheap" on a projection.** `:68` ("the fixed-band test's unfolds are cheap") and `:310` ("Its unfolds are cheap") are an affordability judgement on 232–344 node-h. That is 34–51 % of the 674.0 node-h of uncommitted headroom in §2, before the 2,151 node-h event-loop add-on, so it reads as the fit verdict amendment 1 excludes. Fix: drop "cheap" and keep the numbers.
- **N3. §8 overstates the cost reduction.** `:308` says "The measured units lower the per-experiment cost". The new range is 36.9–51.6 node-h against the old 43.2–160.9. The upper end falls, but 51.6 is above the old optimistic 43.2. Fix: "lower the conservative end".

### New findings (COSMETIC)
- **C1. Two citations are one line off.** `3d-unfolding/genie/README.md:97-98` should be `:98-99`; line 97 is "## Status / stages", and the "~9 min" text is on line 99. `:116-118` should be `:117-119`.
- **C2. One second-level hit is not mentioned.** `:254-255` says the second-level search "found `gregork/Minerva`". The evidence file (`:18`) also lists `josephrb/minerva-shutdown-stage`. I re-checked it read-only: 60G of `fig_products`, `g2_input`, `pet_inputs` and `results`, with no `*mc_AnaTuple*` and no `StandardMC`. Mention it as checked.
- **C3. Provenance gaps in `remote_reads_repair_20261014.txt`.** The `ls -l` of the 113 GB file (`:36-37`) is appended after the `## end` marker, with no timestamp or host. The generator and MC name patterns behind `:5-15` are not recorded either. Otherwise the file supports every use the REPORT makes of it: 99/7, the generator names, `gregork` 41 + 11 `.pb` files at 15G and 4.0G, 9.6T, 12G, gibuu absent, and 113,496,440,965 B (53× is 52.9).
- **C4. The verifier numbers have no committed probe code.** The REPORT cites `VERIFICATION.md` for my 1L/1N/1B identity and timing numbers and for the overlay decomposition. The probe scripts behind them are only in my session scratchpad, which is not durable. If the director wants them reproducible, commit the probes or label the numbers as verifier observations.

### VERIFICATION.md
It reproduces my first report verbatim: verdict, both MATERIAL findings, the 12 MINOR and 5 COSMETIC items, the recomputation table, the citations list, the not-checked list and the status block. Its header and its NOT CITABLE scope are accurate. It is registered as MACHINE.

### Mechanics
- `generate_manifest.py --at-sha d28ba3f5… --check` returns OK, exit 0, 2743 rows, LIVE 352.
- The REPORT override row is still LIVE.
- The CATALOG row matches the repaired §1.

### Cluster
The only cluster check was a read-only listing of `josephrb/minerva-shutdown-stage`, for C2.

### `git -C /Users/josephbailey/local-research/MINERvA-OmniFold-stage-d-verify-20261014 status --short`
```
```
(empty; HEAD `d28ba3f589362c6e18b212b6188492de11de2ce0`. The authorized checkout was the only write.)

---

# Director finding on `e70a2db2` (paper-tighten lane, APPROVE WITH ONE MINOR)

- **MINOR, §6.1 (the sentence before §6.2).** The text said "The 2D measurement is the E_avail marginal of the 3D
  result". The 2D result is its own unfold, not the marginal of the 3D result. The conclusion, that a 2D projection
  of these samples is a projection of an already-inspected sample, holds without that premise.
- **Repair.** The sentence now rests on the 2D observables lying inside the 3D/5D phase space the samples were
  compared in, citing `3d-unfolding/genie/README.md:43` (the E_avail-marginal `hXSec2D`), and it says the 2D result
  is its own unfold. The writer checked that `:43` carries the `hXSec2D` text.
- **Re-verification.** None, at the director's instruction: this is a one-sentence wording repair. No outcome changes.

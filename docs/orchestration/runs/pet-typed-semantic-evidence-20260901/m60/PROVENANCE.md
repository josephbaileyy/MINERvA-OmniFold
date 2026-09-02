# M60 typed-semantic probe archive

This directory is the raw preservation layer for the broader semantic probes
run by session `minerva-omnifold-60` on 2026-09-01. It is separate from the
32-row fixed-sample packet in the parent directory. Nothing in this archive
promotes the M60 measurements to an adopted semantic contract, independent
verification, or publication evidence.

`ARTIFACTS.tsv` records every archived file's original path or extraction
source, mtime, byte count, and SHA-256 digest. The exact copied scripts and
outputs were compared byte for byte with their originals after copying. The
curated command record is bound separately to its external source below.

## Credential scan

Before staging, the three surviving scripts, every output, and the curated
command record were scanned statically for private-key headers, common GitHub,
OpenAI, AWS, and Google key formats, Basic/Bearer authorization values, and
API-key, access-token, refresh-token, client-secret, and password assignments.
No match was found. This is a bounded pattern scan, not a proof that arbitrary
text contains no sensitive information.

## Curated command-record extraction

The complete M60 transcript remains outside this repository. It contains full
conversation records, tool inventories, attachments, environment details, and
unrelated narrative and is not appropriate repository evidence. Its external
identity is:

| Item | Value |
|---|---|
| path | `/Users/josephbailey/.claude-school/projects/-Users-josephbailey-local-research-MINERvA-OmniFold/1218dada-3c71-4b44-95e8-8aee2b7ad845.jsonl` |
| mtime | `2026-09-01T20:22:33+0200` |
| bytes | `1668985` |
| SHA-256 | `50dad57708ed77aae30eded4f13edbc08a163e38a8ee96cde50bf55ffcdb3742` |
| disposition | `EXTERNAL_SOURCE — DIGESTED, NOT COMMITTED` |

`command-records/probe-commands.jsonl` was extracted statically from that exact
external digest. For probes 3--5 and 7--14, extraction selected the unique Bash
tool-use record by its original tool-use identifier, copied `.input.command` as
the exact decoded command body, copied the enclosing message timestamp and
message identifier plus tool-use identifier into one source identifier, and
recorded the expected redirected output filename. The probe-7 record selects
the remote branch-inventory execution command, not its later local analysis
command.

Each decoded command body was hashed without an added newline using the
equivalent of `jq -j ... | shasum -a 256`. The curated file contains one compact
JSON object per probe and only these keys:

- `probe_identifier`;
- `original_message_timestamp_identifier`;
- `exact_command_body`;
- `expected_output_filename`;
- `command_body_sha256`.

The curated file has SHA-256
`95784e802bc95a95f2321bd3333000179db51e6b23629fe047259458da3dfa09`.
All 11 stored command-body hashes were checked against the external transcript.
No extracted command was executed.

## Exact source files

The commands selected the first file from each named manifest. The exact paths
recorded by M60 are:

| Playlist | Role | Source file |
|---|---|---|
| 1A | data | `/pscratch/sd/j/josephrb/minerva/minerva_large_files/Data/Playlist1A/MasterAnaDev_data_AnaTuple_run00006038_Playlist.root` |
| 1A | MC | `/pscratch/sd/j/josephrb/minerva/minerva_large_files/MC/StandardMC/Playlist1A/MasterAnaDev_mc_AnaTuple_run00110000_Playlist.root` |
| 1B | data | `/pscratch/sd/j/josephrb/minerva/minerva_large_files/Data/Playlist1B/MasterAnaDev_data_AnaTuple_run00010068_Playlist.root` |
| 1B | MC | `/pscratch/sd/j/josephrb/minerva/minerva_large_files/MC/StandardMC/Playlist1B/MasterAnaDev_mc_AnaTuple_run00111000_Playlist.root` |
| 1C | data | `/pscratch/sd/j/josephrb/minerva/minerva_large_files/Data/Playlist1C/MasterAnaDev_data_AnaTuple_run00010129_Playlist.root` |
| 1C | MC | `/pscratch/sd/j/josephrb/minerva/minerva_large_files/MC/StandardMC/Playlist1C/MasterAnaDev_mc_AnaTuple_run00111030_Playlist.root` |
| 1D | data | `/pscratch/sd/j/josephrb/minerva/minerva_large_files/Data/Playlist1D/MasterAnaDev_data_AnaTuple_run00010255_Playlist.root` |
| 1D | MC | `/pscratch/sd/j/josephrb/minerva/minerva_large_files/MC/StandardMC/Playlist1D/MasterAnaDev_mc_AnaTuple_run00111100_Playlist.root` |
| 1E | data | `/pscratch/sd/j/josephrb/minerva/minerva_large_files/Data/Playlist1E/MasterAnaDev_data_AnaTuple_run00016003_Playlist.root` |
| 1E | MC | `/pscratch/sd/j/josephrb/minerva/minerva_large_files/MC/StandardMC/Playlist1E/MasterAnaDev_mc_AnaTuple_run00111325_Playlist.root` |
| 1F | data | `/pscratch/sd/j/josephrb/minerva/minerva_large_files/Data/Playlist1F/MasterAnaDev_data_AnaTuple_run00016523_Playlist.root` |
| 1F | MC | `/pscratch/sd/j/josephrb/minerva/minerva_large_files/MC/StandardMC/Playlist1F/MasterAnaDev_mc_AnaTuple_run00111490_Playlist.root` |
| 1G | data | `/pscratch/sd/j/josephrb/minerva/minerva_large_files/Data/Playlist1G/MasterAnaDev_data_AnaTuple_run00018668_Playlist.root` |
| 1G | MC | `/pscratch/sd/j/josephrb/minerva/minerva_large_files/MC/StandardMC/Playlist1G/MasterAnaDev_mc_AnaTuple_run00110150_Playlist.root` |
| 1L | data | `/pscratch/sd/j/josephrb/minerva/minerva_large_files/Data/Playlist1L/MasterAnaDev_data_AnaTuple_run00019168_Playlist.root` |
| 1L | MC | `/pscratch/sd/j/josephrb/minerva/minerva_large_files/MC/StandardMC/Playlist1L/MasterAnaDev_mc_AnaTuple_run00113000_Playlist.root` |
| 1M | data | `/pscratch/sd/j/josephrb/minerva/minerva_large_files/Data/Playlist1M/MasterAnaDev_data_AnaTuple_run00019186_Playlist.root` |
| 1M | MC | `/pscratch/sd/j/josephrb/minerva/minerva_large_files/MC/StandardMC/Playlist1M/MasterAnaDev_mc_AnaTuple_run00113020_Playlist.root` |
| 1N | data | `/pscratch/sd/j/josephrb/minerva/minerva_large_files/Data/Playlist1N/MasterAnaDev_data_AnaTuple_run00020328_Playlist.root` |
| 1N | MC | `/pscratch/sd/j/josephrb/minerva/minerva_large_files/MC/StandardMC/Playlist1N/MasterAnaDev_mc_AnaTuple_run00113270_Playlist.root` |
| 1O | data | `/pscratch/sd/j/josephrb/minerva/minerva_large_files/Data/Playlist1O/MasterAnaDev_data_AnaTuple_run00020619_Playlist.root` |
| 1O | MC | `/pscratch/sd/j/josephrb/minerva/minerva_large_files/MC/StandardMC/Playlist1O/MasterAnaDev_mc_AnaTuple_run00113375_Playlist.root` |
| 1P | data | `/pscratch/sd/j/josephrb/minerva/minerva_large_files/Data/Playlist1P/MasterAnaDev_data_AnaTuple_run00020800_Playlist.root` |
| 1P | MC | `/pscratch/sd/j/josephrb/minerva/minerva_large_files/MC/StandardMC/Playlist1P/MasterAnaDev_mc_AnaTuple_run00112000_Playlist.root` |

The M60 commands and outputs record these paths, but M60 did not record ROOT
file SHA-256 digests or UUIDs. This archive therefore preserves the exact input
specification, not a byte-level snapshot of the ROOT inputs.

## Probe scopes

All payload entry ranges begin at entry 0 and are inclusive. `all 24` means the
data and MC source above for each of 1A, 1B, 1C, 1D, 1E, 1F, 1G, 1L, 1M, 1N,
1O, and 1P.

| Probe/output | Sources and entry range | Enabled branch set |
|---|---|---|
| `probe_out.txt` | 1B data and 1A MC; branch metadata only | the `META_BRANCHES` literal in `mad_semantics_probe.py` |
| `probe_vals.txt` | 1B data and 1A MC; 0--399 | the `META_BRANCHES` literal in `mad_semantics_probe.py` |
| `probe2_out.json` | all 24; 0--99 | the `NEEDED` literal in `mad_probe2.py` |
| `probe3.txt` | 1B data and 1A MC; 0--2999 | `n_prongs`, `prong_part_pid`, `prong_dEdXMean`, `prong_part_score`, `prong_part_charge`, `prong_part_pos`, `prong_part_E`, `vtx` |
| `probe4.txt` | 1A data and MC; 0--1999 | both photon slots: `E`, `dEdx`, `time`, five `energy_*`, five `evis_*`, `direction`; plus `n_prongs`, `prong_part_pos`, `prong_part_E`, `vtx`, `MasterAnaDev_BlobX_sz`, and blob `X`, `Y`, `Z`, `T`, `TPos`, `TotalE` |
| `probe5.txt` | 1A data 0--15258; 1A MC 0--19999; 1F data 0--11879 | both photon slots: `E`, `energy_trkr`, `energy_ecal`, `energy_hcal`, `energy_scal_X`, `energy_scal_UV`, `evis_ecal`, `evis_hcal` |
| `probe6_out.json` | all 24; 0--299 | the `NEEDED` literal in `mad_probe6.py` |
| `probe7.txt` | 1B data and 1A MC; branch metadata only | every tree branch whose name contains `prong` |
| `probe8.txt` | 1A data 0--15258; 1A MC 0--19999 | both photon slots: `E`, `direction`; plus `n_prongs`, `prong_part_pid`, `prong_part_E` |
| `probe9.txt` | 1A data 0--15258; 1A MC 0--19999 | both photon slots: `E`, `P`, `time`, `dEdx`, `direction`, five `energy_*`, five `evis_*` |
| `probe10.txt` | 1A data 0--15258; 1A MC 0--19999; 1B data 0--17929 | both photon slots: `E`, `P`, `dist_vtx`, `energy_trkr`, `evis_trkr`, `time` |
| `probe11.txt` | 1A data 0--15258; 1A MC 0--19999; 1B data 0--17929 | both photon slots: five `evis_*`, five `energy_*`, `E`, `E_Old`, `P`, `dEdx`, `time`, `dist_vtx` |
| `probe12.txt` | 1A data 0--15258; 1A MC 0--19999; 1B data 0--17929 | both photon slots: five `evis_*` and `E` |
| `probe13.txt` | 1A data 0--15258; 1A MC 0--19999 | both photon slots: `E` and all five matched `energy_*`/`evis_*` pairs |
| `probe14.txt` | 1A, 1G, and 1P data and MC; 0--7999 per file | both photon slots: `E` and the matched tracker, ECAL, scaler-X, and scaler-UV `energy_*`/`evis_*` pairs |

The exact relevant shell bodies, including the inline programs for probes 3--5
and 7--14, are preserved in `command-records/probe-commands.jsonl`. The complete
external transcript is not committed. Working narrative from that session,
including `TYPED_DESCRIPTOR_SEMANTIC_AUDIT-20260901.md`, remains non-citable and
is not a routed claim source.

## Recovered result layers

The following requested M60 measurement families have complete surviving input
paths, command bodies, entry ranges, branch selections, and stdout/JSON:

- photon three-state counts and rates: `probe8.txt` and `probe9.txt`;
- cross-playlist and data/MC comparisons: `probe2_out.json`,
  `probe6_out.json`, and the 1A/1G/1P comparison in `probe14.txt`;
- blob structural-zero counts: `probe2_out.json`;
- prong inventories and distributions: `probe_out.txt`, `probe_vals.txt`,
  `probe2_out.json`, `probe3.txt`, `probe6_out.json`, `probe7.txt`, and
  the prong-energy classes in `probe8.txt`.

These are preserved raw measurements only. They are not imported into the
fixed-sample packet and are not independently verified or routed for citation.

## Unpreserved results

- The first 200-entry-per-file `mad_probe2.py` attempt was superseded by the
  successful 100-entry rerun, and its partial output was overwritten. Any
  result attributed to that first attempt is **UNPRESERVED - NOT DURABLY
  CITABLE**.
- The first combined metadata/value invocation of `mad_semantics_probe.py`
  failed before producing its intended combined result and its redirected files
  were overwritten by the successful metadata-only and value-only reruns. Any
  result attributed specifically to that failed attempt is **UNPRESERVED - NOT
  DURABLY CITABLE**.
- No standalone `mad_probe3.py`, `mad_probe4.py`, `mad_probe5.py`, or
  `mad_probe7.py` through `mad_probe14.py` file existed in the recovered
  scratchpad. Their exact inline programs survive only in the curated command
  record; claims that require a different or separately versioned script are
  **UNPRESERVED - NOT DURABLY CITABLE**.
- Any audit or memory assertion that is not a direct consequence of the exact
  archived command and stdout/JSON pair is **UNPRESERVED - NOT DURABLY
  CITABLE**. No missing measurement was reconstructed for this archive.

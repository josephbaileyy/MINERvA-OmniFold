# PET typed-descriptor fixed-sample semantic evidence provenance

This directory archives the deterministic probe and its JSON output for the fixed
PET source-smoke sample. The output is field-level telemetry, not a population
estimate or a semantic decision.

## Execution identity

| Item | Value |
|---|---|
| repository base | `d8a59358be65fc924a05f707b8760cb5aff79bf4` |
| source-smoke execution | 2026-09-01 18:39:29 UTC |
| final semantic-probe execution | 2026-09-01 18:50:04 UTC |
| execution surface | Perlmutter login CPU; no Slurm submission |
| Python | 3.11.14 |
| NumPy | 1.26.4 |
| ROOT | 6.28/12 |
| source scope | entries 0--15 inclusive from each of the two receipt-bound sources |

## Execution-scope deviation

After receiving the preceding documentation-only task, the source smoke was
invoked against both bound ROOT sources. That ROOT access reused the already
bound entries 0--15, but it was not authorized by that task. It is an
execution-scope deviation, not an authorized replay. Nothing was rerun while
preparing this correction.

The exact command was:

```bash
/usr/bin/ssh perlmutter.nersc.gov 'set -e; source /pscratch/sd/j/josephrb/MINERvA-OmniFold/setup_salloc_env.sh; PET_SEMANTIC_ROOT=/pscratch/sd/j/josephrb/pet-typed-semantic-evidence-20260901-d8a59358; export PYTHONPATH="$PET_SEMANTIC_ROOT/nd-unfolding/pet${PYTHONPATH:+:$PYTHONPATH}"; python3 "$PET_SEMANTIC_ROOT/nd-unfolding/pet/typed_descriptor_source_smoke.py" --repo-root "$PET_SEMANTIC_ROOT" --output "$PET_SEMANTIC_ROOT/fixed-source-shard.npz" > "$PET_SEMANTIC_ROOT/source-smoke.stdout.json"; python3 "$PET_SEMANTIC_ROOT/docs/orchestration/runs/pet-typed-semantic-evidence-20260901/probe_fixed_sample.py" --shard "$PET_SEMANTIC_ROOT/fixed-source-shard.npz" --output "$PET_SEMANTIC_ROOT/fixed-sample-telemetry.json"; python3 -c "import json, numpy, ROOT, sys; print(json.dumps({\"python\": sys.version.split()[0], \"numpy\": numpy.__version__, \"root\": ROOT.gROOT.GetVersion()}, sort_keys=True))"; shasum -a 256 "$PET_SEMANTIC_ROOT/fixed-source-shard.npz" "$PET_SEMANTIC_ROOT/fixed-sample-telemetry.json"; wc -c "$PET_SEMANTIC_ROOT/fixed-sample-telemetry.json"'
```

The ROOT inputs selected through `--repo-root` were:

- `/pscratch/sd/j/josephrb/minerva/minerva_large_files/Data/Playlist1B/MasterAnaDev_data_AnaTuple_run00010068_Playlist.root`;
- `/pscratch/sd/j/josephrb/minerva/minerva_large_files/MC/StandardMC/Playlist1A/MasterAnaDev_mc_AnaTuple_run00110000_Playlist.root`.

A later deterministic local replay did not access ROOT. It used the pre-existing
shard `/private/tmp/pet-typed-fixed-source-shard-20260901.npz` with this exact
command:

```bash
PYTHONPATH=nd-unfolding/pet python3 docs/orchestration/runs/pet-typed-semantic-evidence-20260901/probe_fixed_sample.py --shard /private/tmp/pet-typed-fixed-source-shard-20260901.npz --output /private/tmp/pet-typed-fixed-sample-local.json
```

The source-smoke code, its fixed entries, manifests, expected UUIDs, and branch
set were copied byte-for-byte from the base commit into a task-local scratch
directory. The already-committed source-smoke receipt remains the authority for
the source bindings and PASS result:
`docs/orchestration/state/pet-typed-descriptor-fixed-source-smoke-20260901.json`.

## Repository inputs

| File | SHA-256 |
|---|---|
| `nd-unfolding/pet/typed_descriptors.py` | `5870b6c091693b02d40236721df317818753a4e86f281c5c52742216902cd221` |
| `nd-unfolding/pet/typed_descriptor_source_smoke.py` | `5dedaac877079c5ed68d20afd9fa08c8851e160898e34cf8b89b02e30c86bd40` |
| `nd-unfolding/pet/atomic_write.py` | `71527c2af7a5c039d1ab103e000909f4b2ce793f9788e426369ef53c44c5395e` |
| `2d-unfolding/playlist_manifests/1B_Data.txt` | `91fa4a24774bfa800cd021dd712e61c777f600a7fa0c77ef1f54dad289764b1e` |
| `2d-unfolding/playlist_manifests/1A_MC.txt` | `4100dca453de1beef0213a0feac1fe4faa77d769f2dd5f36f4e11c6cea4894f8` |

The source-smoke shard has SHA-256
`8fc88dd46e2e56ff2e661295df0f3a77cd2cfbc3af66ad5c04d4c3b73035fc44`.
It is not committed: it contains source-derived per-event arrays and an
execution-local source path. The archived telemetry binds that exact shard by
digest and retains only source basenames, UUIDs, aggregate counts, field
summaries, and hashes.

## Archived products

| File | SHA-256 | Role |
|---|---|---|
| `probe_fixed_sample.py` | `0b71483705847995425d741700fff6abc399ff482c81b00cbad05ae3c66fb3da` | deterministic telemetry probe |
| `fixed-sample-telemetry.json` | `855eaa6bee58341d8368a239d0fc28050873446721624bb47808d5345f8cbeec` | probe output |

The JSON embeds both the probe and shard digests. Its `PASS` means that the
bounded shard was read and summarized successfully. It does not mean that field
semantics, units, calibration, categories, sentinels, production normalization,
or scientific performance passed.

## External primary-source snapshot

The semantic comparison used arXiv:2604.12364v2, *Cross-Domain Transfer with
Particle Physics Foundation Models: From Jets to Neutrino Interactions*, and the
paper's linked `gregorkrz/minerva-ml` source repository. The repository is a
downstream consumer of the tuple branches, not the tuple producer, so it records
usage conventions rather than authoritative raw branch definitions.

| Source | Version / SHA-256 |
|---|---|
| arXiv PDF | v2, 2026-08-25; `66c6dcd4526cbbde44f49a00ee0ef85b2eeafbd89a0332da7b2a98b050fc5276` |
| source repository | commit `78ebc0d6af04a5b6ab8114a9560dcc9c2a0b99bb` |
| `DATASET.md` | `b23fc62ef1e1e83efda21b268cc982fc1b2d00de28d5f2a502208aa04bb7beed` |
| `src/dataset/preprocessing.py` | `8348a5d7ee6beec68f0a22a6e85830db6f988eb95edd76b5ac7394f6909d5880` |
| `src/scripts/extract_baselines.py` | `612db7596a7e9635eec504d85608ef4b0528b9ba979d0c0897ed78a64248a0e7` |
| `src/scripts/preprocess_dataset.py` | `a3d510d94b16a3e6b477a4d7446ccd0a1e44713566ba4779602f41a7472b2692` |

Stable routes:

- <https://arxiv.org/abs/2604.12364v2>
- <https://github.com/gregorkrz/minerva-ml/tree/78ebc0d6af04a5b6ab8114a9560dcc9c2a0b99bb>

## Historical execution shape

With the base-commit files and the two receipt-bound sources available under a
scratch copy of the repository structure:

```bash
source <canonical-repo>/setup_salloc_env.sh
export PYTHONPATH=<scratch>/nd-unfolding/pet
python <scratch>/nd-unfolding/pet/typed_descriptor_source_smoke.py \
  --repo-root <scratch> \
  --output <scratch>/fixed-source-shard.npz \
  > <scratch>/source-smoke.stdout.json
python <scratch>/probe_fixed_sample.py \
  --shard <scratch>/fixed-source-shard.npz \
  --output <scratch>/fixed-sample-telemetry.json
```

No training, GPU use, new tuple-file selection, additional tuple entry, Gate-6
action, `C_ML` construction, central-value move, or publication inference was
performed. The ROOT access disclosed above was outside the documentation-only
authorization and must not be read as authorized by this statement.

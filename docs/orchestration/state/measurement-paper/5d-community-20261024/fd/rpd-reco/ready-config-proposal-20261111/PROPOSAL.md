# RPD-RECO production config: proposed runtime values (DRAFT for coverage-5b-audit, 2026-11-11)

**By** the limitation-resolver lane, at the director's request. **Draft only.** This proposal does not make the config
READY, runs nothing, and authorizes nothing. P-RPD stays closed.
<!-- absence-ok: the document's own status (a draft that runs nothing), not a claim that a result does not exist -->

**Why it exists.** #848's flux connect (`fd_rpd_reco_flux_connect.sh` at `9634aadf`) runs custody `prepare`. `prepare`
refuses unless the production config reads `configuration_status: "READY"` (`fd_rpd_reco_custody.py:487-490`). The newest
draft, `late-platform-library-repair-20261108/production-config.draft.json` (sha256 `697d0c04…`), is
`DRAFT_UNRESOLVED_RUNTIME`, with `${…}` placeholders.

**What this file proposes.** [`production-config.proposed.json`](production-config.proposed.json) is that draft with
its placeholders filled, and its flux paths set to the files FluxReweighter opens (item 2). Its status is `PROPOSED_FOR_AUDIT_NOT_READY`, so `prepare` still refuses it. READY is set by the
authoring lane (this lane, by the director's routing of 2026-11-11), only after coverage-5b-audit and with the code's binding 2
(FD-RPD-RECO-BINDING-1 item 2).

## Resolved from committed records

| field | proposed value | source |
|---|---|---|
| `dump_root` | `/pscratch/sd/j/josephrb/fd-rpd-20261103/dumps` | `INPUTS.sha256` (`7638f94f…`): all 24 pinned paths sit there; prologue5 `policy-config.json` |
| `pins`, `h2`, `inventory`, `constants`, `mat_dependencies` `.path` | `${BOUND_CHECKOUT}` → `/dev/shm/limres-rpd-flux1/repo`, the flux connect's fresh clone at the bound sha (the prologue connects' pattern) | the draft's relative paths. Every sha256 is unchanged, and each equals prologue5's |
| `flux_root` | `/pscratch/sd/j/josephrb/MINERvA-OmniFold/MINERvA101/opt/lib`, which is `$PLOTUTILSROOT` in the pinned MAT environment, measured on login21 on 2026-11-11 (`real-mnv-check2-20261111`). Each `flux_selection.<PL>.relative_path` becomes `data/flux/flux-gen2thin-pdg14-minervame<PL>_rearrangedUniverses.root` | MAT's source, open item 2 (resolved). It replaces prologue5's `minerva/minerva_large_files` + `MATFluxAndReweightFiles/flux/…` |
| `flux_source` | `/pscratch/sd/j/josephrb/MINERvA-OmniFold/MINERvA101/MAT/PlotUtils/FluxReweighter.cxx`, sha256 `4576346d…`, git `35097b65` | prologue5. The sha256 is the one BINDING-1 A1 records (receipt #849) |
| `trace_environment_roots` | the root_6_28 env, both home spellings | prologue5 (passed in rerun 5) |
| `trace_instrument_directories` | `…/MINERvA101/opt/lib`, `…/opt/include`, `…/unbinned_unfolding/build` | prologue5 |
| `trace_platform_roots` | the prologue4/5 roots | prologue5 |
| `cov2d_protected_paths` | prologue5's list | prologue5. The run lane re-confirms it with cov2d at run time (open item 4) |

`flux_selection` and `premise` are unchanged from the draft, and they equal prologue5's.

## Rulings (director, 2026-11-11) and the open items

The authoring stays with this lane. Codex2's loop is now Joseph's note work. The proposal goes to coverage-5b-audit.

1. **The run directory: ruled.** It is a new `/pscratch/sd/j/josephrb/rpd-reco-flux-<date>/run`, outside CFS. The
   config carries `${RUN_DATE}`, which the flux connect fixes when its sha goes to the director. The config is then
   regenerated with the literal date.
2. **The flux files: ruled. The config names exactly the files MAT's FluxReweighter opens.**
   - **From the source at `35097b65`.** The copy was fetched from MinervaExpt/MAT on 2026-11-11, and its sha256 is
     `4576346d…`, equal to BINDING-1 A1's. `GetFluxMnvH1D` (`FluxReweighter.cxx:883-945`) opens
     `$PLOTUTILSROOT/data/flux/flux-<flux>-pdg<pdg>-<playlist><suffix>.root`.
     - `<flux>` is `gen2thin`, or `g4numiv6` for the generated flux.
     - `<suffix>` is `_rearrangedUniverses` for ME playlists with the ν-e constraint applied (`:907`).
     - The histogram is `flux_E_cvweighted`, or `flux_E_unweighted` for the generated flux (`:942`).
     - `playlistString` (`:1936-1976`) maps 1A–1F to `minervame1D`, 1G, 1L and 1M to `minervame1M`, and 1N–1P to
       `minervame1N`. That matches the draft's three groups.
   - **The two conventions.** This is `MAT-DATA-DEPENDENCIES.json`'s convention (`$PLOTUTILSROOT` + `data/flux/…`). The
     draft config used `flux_root` + `MATFluxAndReweightFiles/flux/…` under `minerva_large_files`, which FluxReweighter
     never opens. The proposal now follows FluxReweighter.
   - **Required before READY, at run time:** each named file's stat and its sha256 read under O_NOATIME, showing they
     are the files FluxReweighter opens. The extract's trace check then confirms that the opened paths equal them.
3. **`flux_selection.*.retention`:** runtime by design.
4. **`cov2d_protected_paths`: ruled.** This lane re-confirms the list with cov2d before READY.
5. **`premise`:** runtime by design. It is measured at P0 (BINDING-1 A1 item 3).
6. **The clone root: ruled.** The flux connect clones to exactly `/dev/shm/limres-rpd-flux1/repo`.
7. **Also open, from the draft itself.** `mat_constructor.analysis_arguments_citation` reads "short source revision
   f4cd8f8b verified; full SHA must be measured before READY".

## What happens next

The authoring lane (this one) revises these values on the audit's findings. coverage-5b-audit reads them together with #848's code. The
director writes binding 2 with #848's merge. Only then does a READY config's sha go into a flux connect, whose own
sha goes to the director for a go.

Nothing is submitted, deposited or tagged.

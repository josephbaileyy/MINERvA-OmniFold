# RPD-RECO production config: proposed runtime values (DRAFT for Codex2 and coverage-5b-audit, 2026-11-11)

**By** the limitation-resolver lane, at the director's request. **Draft only.** This proposal does not make the config
READY, runs nothing, and authorizes nothing. P-RPD stays closed.
<!-- absence-ok: the document's own status (a draft that runs nothing), not a claim that a result does not exist -->

**Why it exists.** #848's flux connect (`fd_rpd_reco_flux_connect.sh` at `9634aadf`) runs custody `prepare`. `prepare`
refuses unless the production config reads `configuration_status: "READY"` (`fd_rpd_reco_custody.py:487-490`). The newest
draft, `late-platform-library-repair-20261108/production-config.draft.json` (sha256 `697d0c04…`), is
`DRAFT_UNRESOLVED_RUNTIME`, with `${…}` placeholders.

**What this file proposes.** [`production-config.proposed.json`](production-config.proposed.json) is that draft with
its placeholders filled. Its status is `PROPOSED_FOR_AUDIT_NOT_READY`, so `prepare` still refuses it. Only Codex2's
authoring lane sets READY, after coverage-5b-audit and with the code's binding 2 (FD-RPD-RECO-BINDING-1 item 2).

## Resolved from committed records

| field | proposed value | source |
|---|---|---|
| `dump_root` | `/pscratch/sd/j/josephrb/fd-rpd-20261103/dumps` | `INPUTS.sha256` (`7638f94f…`): all 24 pinned paths sit there; prologue5 `policy-config.json` |
| `pins`, `h2`, `inventory`, `constants`, `mat_dependencies` `.path` | `${BOUND_CHECKOUT}` → `/dev/shm/limres-rpd-flux1/repo`, the flux connect's fresh clone at the bound sha (the prologue connects' pattern) | the draft's relative paths. Every sha256 is unchanged, and each equals prologue5's |
| `flux_root` | `/pscratch/sd/j/josephrb/minerva/minerva_large_files` | prologue5 `policy-config.json` |
| `flux_source` | `/pscratch/sd/j/josephrb/MINERvA-OmniFold/MINERvA101/MAT/PlotUtils/FluxReweighter.cxx`, sha256 `4576346d…`, git `35097b65` | prologue5. The sha256 is the one BINDING-1 A1 records (receipt #849) |
| `trace_environment_roots` | the root_6_28 env, both home spellings | prologue5 (passed in rerun 5) |
| `trace_instrument_directories` | `…/MINERvA101/opt/lib`, `…/opt/include`, `…/unbinned_unfolding/build` | prologue5 |
| `trace_platform_roots` | the prologue4/5 roots | prologue5 |
| `cov2d_protected_paths` | prologue5's list | prologue5. The run lane re-confirms it with cov2d at run time (open item 4) |

`flux_selection` and `premise` are unchanged from the draft, and they equal prologue5's.

## Open items for the authoring lane and the audit

1. **The run directory** (`flux_extract.path`, `flux_custody.path`) stays `${RUN_LANE_EXTRACT_RUN}`. It is a run-lane
   choice outside CFS (the connect refuses a CFS run), and it must outlive the connect, unlike `/dev/shm`. Proposed: a new
   `/pscratch/sd/j/josephrb/rpd-reco-flux-<date>/run`, named in the flux connect when its sha goes to the director.
2. **Two flux-file conventions in #848's own records.**
   - The config selects `flux_root` + `MATFluxAndReweightFiles/flux/flux-gen2thin-pdg14-minervame<PL>_rearrangedUniverses.root`.
   - `MAT-DATA-DEPENDENCIES.json` (`b056487e…`; its status is "STATIC_SOURCE_INVENTORY_NOT_RUNTIME_VERIFIED") names the
     same files as `$PLOTUTILSROOT` + `data/flux/…`.
   - Before READY, the audit should require one of two things: the paths resolve to the same files, by stat and
     sha256 under O_NOATIME; or the config names the file MAT's FluxReweighter actually opens, as the extract's trace
     check would record it. This proposal does not decide which.
3. **`flux_selection.*.retention`** reads `AWAITING_RUNTIME_STAT_AND_STAGED_RETENTION_RECORD`. That is a run-time stat
   by design, left unchanged.
4. **`cov2d_protected_paths`** came from prologue5 (2026-11-08). cov2d's inputs may have changed since, so the run lane
   re-confirms the list with cov2d before the flux connect.
5. **`premise`** booleans are measured at P0 by design (BINDING-1 A1 item 3). They stay null here.
6. **The clone root** `/dev/shm/limres-rpd-flux1/repo` is a proposal. The flux connect must clone to exactly that
   path, or the config must be regenerated to match.

## What happens next

The authoring lane (Codex2) adopts or edits these values. coverage-5b-audit reads them together with #848's code. The
director writes binding 2 with #848's merge. Only then does a READY config's sha go into a flux connect, whose own
sha goes to the director for a go.

Nothing is submitted, deposited or tagged.

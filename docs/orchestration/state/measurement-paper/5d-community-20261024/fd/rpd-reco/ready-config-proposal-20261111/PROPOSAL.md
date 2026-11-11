# RPD-RECO production config: proposed runtime values (DRAFT for coverage-5b-audit, 2026-11-11)

**By** the limitation-resolver lane, at the director's request. **Draft only.** This proposal does not make the config
READY, runs nothing, and authorizes nothing. P-RPD stays closed.
<!-- absence-ok: the document's own status (a draft that runs nothing), not a claim that a result does not exist -->

**Why it exists.** #848's flux connect (`fd_rpd_reco_flux_connect.sh` at `9634aadf`) runs custody `prepare`. `prepare`
refuses unless the production config reads `configuration_status: "READY"` (`fd_rpd_reco_custody.py:487-490`). The newest
draft, `late-platform-library-repair-20261108/production-config.draft.json` (sha256 `697d0c04…`), is
`DRAFT_UNRESOLVED_RUNTIME`, with `${…}` placeholders.

**What this file proposes.** [`production-config.proposed.json`](production-config.proposed.json) is that draft with
its placeholders filled and cov2d's paths added (item 4). Its status is `PROPOSED_FOR_AUDIT_NOT_READY`, so `prepare` still refuses it. READY is set by the
authoring lane (this lane, by the director's routing of 2026-11-11), only after coverage-5b-audit and with the code's binding 2
(FD-RPD-RECO-BINDING-1 item 2).

## Resolved from committed records

| field | proposed value | source |
|---|---|---|
| `dump_root` | `/pscratch/sd/j/josephrb/fd-rpd-20261103/dumps` | `INPUTS.sha256` (`7638f94f…`): all 24 pinned paths sit there; prologue5 `policy-config.json` |
| `pins`, `h2`, `inventory`, `constants`, `mat_dependencies` `.path` | `${BOUND_CHECKOUT}` → `/dev/shm/limres-rpd-flux1/repo`, the flux connect's fresh clone at the bound sha (the prologue connects' pattern) | the draft's relative paths. Every sha256 is unchanged, and each equals prologue5's |
| `flux_root`, `flux_selection.<PL>.relative_path` | `/pscratch/sd/j/josephrb/minerva/minerva_large_files` + `MATFluxAndReweightFiles/flux/flux-gen2thin-pdg14-minervame<PL>_rearrangedUniverses.root`, as in the draft | prologue5. These are the C-N inventory's rows (`energy-spectrum-candidates.tsv`, `e60609e7…`). The code matches selections against that inventory by relative_path (`fd_rpd_reco.py:1092-1110` at `9634aadf`). See item 2 for how the files FluxReweighter opens are bound to them |
| `flux_source` | `/pscratch/sd/j/josephrb/MINERvA-OmniFold/MINERvA101/MAT/PlotUtils/FluxReweighter.cxx`, sha256 `4576346d…`, git `35097b65` | prologue5. The sha256 is the one BINDING-1 A1 records (receipt #849) |
| `trace_environment_roots` | the root_6_28 env, both home spellings | prologue5 (passed in rerun 5) |
| `trace_instrument_directories` | `…/MINERvA101/opt/lib`, `…/opt/include`, `…/unbinned_unfolding/build` | prologue5 |
| `trace_platform_roots` | the prologue4/5 roots | prologue5 |
| `cov2d_protected_paths` | prologue5's 8 entries, kept, plus 22 that cov2d added on 2026-11-11 (item 4): 8 LL5D inputs, 13 LL5D run directories (8 existing, 5 created by drafted connects) and `cov2d-inputs-20261104` | prologue5, and cov2d's reply of 2026-11-11 |

`flux_selection` and `premise` are unchanged from the draft, and they equal prologue5's.

## Rulings (director, 2026-11-11) and the open items

coverage-5b-audit: **GO as a proposal** at `2d3c6a0f` (2026-11-11), with no blocking or major findings. READY stays gated
on items 1-10.

The authoring stays with this lane. Codex2's loop is now Joseph's note work. The proposal goes to coverage-5b-audit.

1. **The run directory: ruled.** It is a new `/pscratch/sd/j/josephrb/rpd-reco-flux-<date>/run`, outside CFS. The
   config carries `${RUN_DATE}`, which the flux connect fixes when its sha goes to the director. The config is then
   regenerated with the literal date.
2. **The flux files: ruled. The config names exactly the files MAT's FluxReweighter opens.** #848's own `prepare`
   enforces this, so the config keeps the draft's C-N selection.
   - **What FluxReweighter opens.** From MAT's source at `35097b65` (fetched from MinervaExpt/MAT on 2026-11-11, sha256
     `4576346d…`, equal to BINDING-1 A1's), `GetFluxMnvH1D` (`FluxReweighter.cxx:883-945`) opens
     `$PLOTUTILSROOT/data/flux/flux-<flux>-pdg<pdg>-<playlist><suffix>.root`.
     - `<suffix>` is `_rearrangedUniverses` for ME playlists with the ν-e constraint (`:907`).
     - The histogram is `flux_E_cvweighted`, or `flux_E_unweighted` for the generated flux (`:942`).
     - `playlistString` (`:1936-1976`) maps 1A–1F to `minervame1D`, 1G, 1L and 1M to `minervame1M`, and 1N–1P to
       `minervame1N`.
     - The string constructor (`:372-435`) opens a closed set of 15 paths, which `MAT-DATA-DEPENDENCIES.json` (`b056487e…`) lists
       and custody's `MAT_INVENTORY` guard fixes (audit c3):
       - 12 flux files: `flux-{gen2thin,g4numiv6}-pdg{14,-14}-minervame<PL>_rearrangedUniverses.root` under
         `$PLOTUTILSROOT/data/flux`;
       - `lowNuReweight.root`;
       - a `data/flux/sys` file;
       - `$MPARAMFILES/FluxConstraints/sorted_NuEConstraint_FHC_RHC_IMD.txt`.
   - **How the config is bound to them.** The config's `flux_selection` must name the C-N inventory's rows, because
     `fd_rpd_reco.py:1092-1110` refuses a selection that is not one of them. Those rows sit under `flux_root`, at
     sha256 `951a400e…` (1D), `3c76ed6f…` (1M) and `bfe5e3c5…` (1N).
     - At `prepare`, the code stages each native `$PLOTUTILSROOT/data/flux/…` constrained-numerator file, with its
       sha256 measured under O_NOATIME.
     - It refuses (`NATIVE_SELECTION`, `fd_rpd_reco_custody.py:607-612`) unless that sha256 equals the selected C-N
       file's.
     - So a READY config can only run when the constrained numerators FluxReweighter opens are byte-identical to the
       named C-N files. That is the ruling, checked by stat and sha256 under O_NOATIME at run time. The director confirmed
       on 2026-11-11 that the guard meets it.
     - **What is not bound by content (audit c1).** Only those three pdg 14 numerators (1D, 1M, 1N) are compared by
       sha256. The other 12 MAT files are bound by path (`MAT_INVENTORY`) and recorded at `prepare`, but compared with
       nothing. That includes the g4numiv6 generation denominators, although their inventory rows carry sha256s.
   - **Not done: setting `flux_root` to `$PLOTUTILSROOT`.** An earlier draft of this proposal did that. It would break
     the inventory match. It would also make all of `…/opt/lib` a protected root (`fd_rpd_reco_custody.py:1321-1326`),
     including MAT's own libraries.
3. **`flux_selection.*.retention`:** runtime by design.
4. **`cov2d_protected_paths`: ruled, and re-confirmed by cov2d on 2026-11-11.** Its basis was origin/main `65412347`,
   the LL5D connects, and `ls -d` of `$P/ll5d-*` and `$P/cov2d-*` at about 08:20Z.
   - It keeps all 8 prologue5 entries. cov2d's wording: "no reason to drop", not a re-proof of the 2D set.
   - It adds the LL5D inputs: of_inputs_5d.npz, bkg_dump.npz, bank_sweep_5d_bkgaware, bank_detector, fd-1b pins.json,
     flux_universes.npz, f1b3/prep and fd-1b-inv i0/in.
   - It adds the LL5D run directories. 8 exist (calib, calib-2, calib-3, gate-g18, gate-ar23, gate-2-g18 and gate-2-ar23
     with SEALED clip-prep files, vicheck). 5 are created by the drafted connects (pilot-r1, unfolds-r1, bulk-r1,
     null-r1, readout-r1).
   - It adds `cov2d-inputs-20261104`, the staged inputs of the COV2D pilot and bulk.
   - **Listed one by one.** `_under` matches a root exactly or as a directory prefix (`fd_rpd_reco_custody.py:673-674`).
     So the `$P/ll5d-` prefix cov2d offered would protect nothing, and each directory is listed.
   - **`flux_universes.npz` is a flux file.** RPD-RECO's flux extract reads the C-N and native MAT flux files of item 2,
     not that file, so protecting it refuses nothing RPD-RECO needs. **The director confirmed on 2026-11-11 that it
     stays protected.**
   - **For the run lane.** A plain read of an LL5D input moves its atime while LL5D runs. RPD-RECO's reads are
     O_NOATIME, and these paths are protected.
5. **`premise`:** runtime by design. It is measured at P0 (BINDING-1 A1 item 3).
6. **The clone root: ruled.** The flux connect clones to exactly `/dev/shm/limres-rpd-flux1/repo`.
7. **The analysis source: resolved on 2026-11-11.** `mat_constructor.analysis_arguments_citation` had only the short
   revision `f4cd8f8b`.
   - The full sha is `f4cd8f8b6dcaef727b681d6c4963909945ceda24` (git rev-parse in this repository).
   - `MINERvA101/MINERvA-101-Cross-Section/runEventLoopOmniFold.cpp` there has sha256 `57792e42…`, unchanged on main.
   - Its lines 1698-1701 set `SetNuEConstraint(true)`, the playlist, `SetAnalysisNuPDG(14)` and `SetNFluxUniverses(100)`.
   - The full sha is now in the proposed config. The file's sha256 is recorded only here. A sha256 beside the
     config's `file` key would add a live receipt binding (the binding inventory moved from 169 to 170 and the hook
     refused), and that needs a ruling.
8. **Required before READY (coverage-5b-audit, 2026-11-11): no placeholder anywhere.**
   - `${RUN_DATE}` must be literal.
   - No code refuses an unexpanded `${` in `flux_extract` or `flux_custody`: the `${` check at
     `fd_rpd_reco_custody.py:1049` covers `trace_platform_roots` only.
   - So READY needs a check that no `${` remains anywhere in the config.
   - **The director's requirement (2026-11-11).** The check fails loudly. It refuses any `${` left in the resolved
     config or in the arguments to `flux_custody` and `flux_extract`, and a mutant tests it. This is a change to #848's
     code.
10. **Required before READY (director, 2026-11-11): the receipt pins all 15 MAT files by content.** The run's receipt
    records an O_NOATIME sha256 of every file in the closed 15-path set FluxReweighter opens, not only the three
    numerators NATIVE_SELECTION compares. This answers audit c1. It is a change to #848's code.
9. **A departure from the draft template (audit c2).** `trace_instrument_directories` lists
   `/pscratch/sd/j/josephrb/MINERvA-OmniFold/unbinned_unfolding/build`, the pscratch tree prologue5 used. The draft had
   `${BOUND_CHECKOUT}/unbinned_unfolding/build`.

## What happens next

The authoring lane (this one) revises these values on the audit's findings. coverage-5b-audit reads them together with #848's code. The
director writes binding 2 with #848's merge. Only then does a READY config's sha go into a flux connect, whose own
sha goes to the director for a go.

Nothing is submitted, deposited or tagged.

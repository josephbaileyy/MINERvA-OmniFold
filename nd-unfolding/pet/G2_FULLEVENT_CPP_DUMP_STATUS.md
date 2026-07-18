# G2 full-event C++ dump — implementation receipt

**Status: CODE-COMPLETE, BUILD/SMOKE/EVIDENCE-BLOCKED.** Owner: G2 C++ source
interface (Claude-personal). Fulfills `FULL_EVENT_INTERFACE_REQUEST.md` /
`FULL_EVENT_FEATURE_CONTRACT.md` and `PET_UQ_REMEDIATION_STATUS.md` Gate 1. No
binary was built, no allocation/Slurm/ROOT/NPZ touched, no output namespace
written. This turn is source + static tests only; an independent review gates
the first interactive build/1A smoke.

## What changed (G2-owned files only)
- `MINERvA101/MINERvA-101-Cross-Section/runEventLoopOmniFold.cpp` — new full-event
  branches on all four trees, gated behind the existing `MNV101_DUMP_POINTCLOUD`;
  Phase-18 miss-row identity/feature caching; schema/provenance metadata.
- `MINERvA101/MINERvA-101-Cross-Section/event/CVUniverse.h` — additive 5-arg
  `GetRecoClusters(E,pos,z,view,time)` overload (3-arg overload byte-unchanged).
- `nd-unfolding/pet/test_g2_fullevent_dump_schema.py` — static regression guard.

Everything is under `MNV101_DUMP_POINTCLOUD`; the default (non-pointcloud /
standard-P4) schema is byte-identical. Phase-18 truth-first gate, bilateral
dedupe, native-miss row, POT, selection, weighting are all unchanged.

## Three schemas (no fabricated counterparts), units, getters
**reco (mc_signal_reco reco side + `data` + `mc_background`)** — identical data/MC defs:
`mu_reco_{px,py,pz,E}` MeV (`GetMuon4V()`), `mu_reco_phi` rad (`GetPhimu()`),
`mu_reco_qp` signed q/p MINOS trk (`GetMuonQP()`), `mu_reco_minos_ok` uint8
(`IsMinosMatchMuon()`), `vtx_reco_{x,y,z}` mm (`GetVertex()`); recoil cloud
`part_reco_{E,pos,z}` + new parallel `part_reco_view` (int 1=X/2=U/3=V) and
`part_reco_time` (double), all five equal-length by construction in the 5-arg getter.

**truth (mc_truth_denom + mc_signal_reco truth side)** — truth-only, no detector
counterpart: `mu_true_{px,py,pz,E}` MeV + `mu_true_phi` rad (beam-frame, built by
`GetTruthMuonKin` from `GetPlepTrue/GetThetalepTrue/GetPhilepTrue/GetElepTrue` —
never the reco `GetPhimu`), `vtx_true_{x,y,z}` mm (`GetTrueVertex()`).

**background (mc_background)** — reco muon + `vtx_reco_*` + recoil cloud (view/time)
+ existing `w_bkg`. Generator labels (`bkg_nuPDG/current/inttype`) and the truth
`bkg_vtx_*` stay as truth AUDIT metadata only, never a publication feature.

## Event identity (real ids only; no manufactured counterparts)
MC trees (truth/signal/background): `mc_run,mc_subrun,mc_nthEvtInFile` (int).
Data: `ev_run,ev_subrun,ev_gate` (int). Phase-18 appended miss rows carry cached
`mc_*` identity + cached truth muon/vertex from `TruthDenomEntry`.

## Native-miss handling
Reco muon/vertex = constant −9999 sentinel; `mu_reco_minos_ok`=0;
`part_reco_view/time` left EMPTY (like `part_reco_E/pos/z`); truth muon/vertex +
identity from the truth-denom cache. All new branches added to `explicitNames`
so the KNOWN_ISSUES #12 dangling-universe-branch rebinder can never override them.
`!pass_reco` signal-tree rows get the same reco sentinel as `sim`.

## Provenance metadata (hadd-safe)
`TNamed petSchemaVersion="g2-fullevent-v1"`, `TNamed petFeatureFamilies=...`,
`TParameter<int> hasFullEventSchema=1 (merge 'f')`, `TParameter<int> fullPhaseSpace
(merge 'f')` — TNamed/'f' only, so hadd cannot sum/corrupt them (contrast
`pTmu_fiducial_nucleons`, KNOWN_ISSUES #8). Lets Python reject recoil-only ROOTs.

## Tests
`python3 nd-unfolding/pet/test_g2_fullevent_dump_schema.py` → 474 static checks
PASS (branch presence/multiplicity, default-path gate spans, 5-arg getter
equal-length clears/fills, miss identity caching + empty parallel vectors,
schema metadata + hadd-safe merge modes, forbidden truth-detector counterparts
absent, truth↔reco leakage guards, data has no truth side). Source-only,
login-node safe; proves nothing about ROOT runtime.

## Remaining evidence (BLOCKED here; for the gated review→smoke)
1. **Compile**: full MAT/PlotUtils build not run (no build authorized). Balanced
   braces/parens verified statically only.
2. **1A smoke** with `MNV101_DUMP_POINTCLOUD=1` (+`MNV101_FULL_PHASE_SPACE=1`):
   confirms every getter/branch resolves at read time and the trees fill.
3. **Data identity branch names** `ev_run/ev_subrun/ev_gate` are the standard
   MasterAnaDev names but are NOT runtime-verified in this repo — the 1A smoke's
   data loop must confirm them (fails closed/loud via GetInt if wrong).
4. **Cluster branches** `cluster_view`/`cluster_time` names taken from
   `dump_display_events.py`; verified at smoke.
5. **Alignment/POT/completeness** unchanged by construction; reconfirm at smoke.

# G2 full-event C++ dump — implementation receipt

**Status: BUILD-PASS / SMOKE-PASS (playlist-1A); Gate-1 production BLOCKED on
playlist 1D recovery while array `56106974` drains.** Task 4 completed its loop
but failed prepublication validation on one upstream-corrupt, out-of-extended-
FPS background muon. The 14.15 GB work ROOT is preserved; both final paths are
absent; unchanged retry is forbidden. Evidence:
`docs/orchestration/state/g2-array-task4-blocker-20260719.json`. Owner: Agent-E
(G2 C++ source/runtime owner), UUID `44b634fc-d211-4e09-9229-95a18d1984cc`,
route claude-school. Fulfills `FULL_EVENT_INTERFACE_REQUEST.md`
/ `FULL_EVENT_FEATURE_CONTRACT.md` and `PET_UQ_REMEDIATION_STATUS.md` Gate 1.
Source packet `486e53e` received an independent agy PASS; the compile/install +
1A smoke were authorized owner-held interactive work only (no 12-playlist array,
MEFHC merge/NPZ, PET training, or scientific endpoint — none performed).

The remaining 11 tasks continue independently. A deferred one-shot watcher
`g2-array-wake-r3` starts only after the current resume exits and monitors task
set `1-3,5-12`; excluding acknowledged failed task 4 from that watcher does not
exclude it from Gate 1. Gate 1 remains blocked until an additive exhaustive
domain validator and no-clobber 1D recovery are independently verified and all
12 playlist pairs pass.

## Turn-3 gate closure (2026-07-18)
**SMOKE — PASS (1A).** Attempt-2 loop terminal (`rc=0`, `DONE`), validator PASS
**50/50 checks, 0 failed** (`attempt2/g2_validation_v2.json`, sha256
`776addeb3453445bcb1e6fa45f81ed41ffe7f713a1cb2da0eac729eccf007b25`). Counts:
`mc_truth_denom == mc_signal_reco = 4,073,230` (Phase-18.2 c-invariant holds),
`mc_background = 44,900`, `data = 360,123`, native misses `1,596,619`,
mcPOT `4.069e20`, dataPOT `8.973e19`. Native misses verified: `sim_pass=0`,
reco muon/vertex `-9999` sentinels, empty reco clouds, valid cached truth
identity/muon. `cluster_view/time` and `ev_run/ev_subrun/ev_gate` populated;
distinct data/reco/truth schemas with no forbidden truth-detector/data-truth
counterparts. Validator retains the `uchar_value` normalization for the PyROOT
`UChar_t`→1-char-string binding (validator-only; the ROOT bytes are correct).
**ATOMIC PUBLICATION.** ROOT renamed (same-fs, hash-verified after move) to the
isolated final path `nd-unfolding/pet/g2_smoke/runEventLoopOmniFold_G2_FPS_1A.root`
(9,419,026,130 B, sha256 `51e46fddd061cae37704c64604f73df8bb3d739cd5420bfd21cb0d2c89db320f`).
Tracked receipt (written last):
`nd-unfolding/pet/g2_smoke/G2_1A_VALIDATION_RECEIPT.json` (sha256
`0aae83d84af77b2520dec83439e7a061176debc5e0d81e18019ac43a5a697867`).
Binary/source footing: SHA `61d7dfbf7ee3…` built from `486e53e`, whose G2 source
is byte-identical through to HEAD `53de3f4` (git diff empty; intervening commits
are orchestrator QP/migration bookkeeping). Attempt-1 (interrupted at
18.4M/22.19M) preserved isolated in `.../g2_smoke/work/`, never used as evidence.
A fail-closed 12-playlist launcher `nd-unfolding/pet/sbatch_g2_fullevent_evloop_array.sh`
is added (NOT submitted).

## Turn-4 launcher hardening (2026-07-18) — recovery/publication correction
Independent verifiers (orchestrator + Gemini `agy-g2-gate-verifier`) blocked array
submission on the launcher's recovery logic. Corrected in
`sbatch_g2_fullevent_evloop_array.sh` (launcher-only; the 1A ROOT/receipt/validator
are unchanged): (1) publication state classified by EXISTENCE not size — neither→run,
both→full validate, any one-sided/zero-length/malformed/mismatched/stale pair→DIE
before compute; published final/receipt are never auto-deleted/quarantined/overwritten;
(2) all 24 canonical manifest SHA-256 + binary SHA + validator SHA bound at commit
time, drift rejected before compute; (3) resume validates schema/playlist/PASS/exact
final path+hash/binary actual+expected/manifest paths+current hashes/validator
path+current hash/both env flags/`n_failed==0`/`n_checks>=50`; (4) ROOT + receipt
publication are no-clobber atomic (hardlink→verify→unlink source; `os.replace`/`mv -f`
removed), a race preserves the pre-existing final and fails; (5) built-source commit
`486e53e677eb64eb9d622ff6e5daecb3e62aab22` recorded separately from the runtime
launcher/HEAD commit. Verified without event-loop compute: `bash -n`, all embedded
Python compiled, 24 manifest + binary + validator hashes match current files, a
temp-dir state matrix (absent/valid/mismatch/ROOT-only/receipt-only/zero-length/
malformed/manifest-drift/validator-drift) and a no-clobber race test — all PASS.
Final launcher correction `15f750b` passed the same Gemini verifier; the
orchestrator submitted array `56106974_[1-12]`. Submission receipt:
`docs/orchestration/state/g2-production-array-submit-20260719.json`.

## Turn-2 runtime evidence (2026-07-18)
**BUILD/INSTALL — PASS.** source commit `486e53e`; build dir
`MINERvA101/opt/build_MINERvA101` (out-of-tree); `cmake --build . --target
runEventLoopOmniFold --parallel 16 && cmake --install .` on interactive
allocation 56100487 (node nid004159); installed canonical
`MINERvA101/opt/bin/runEventLoopOmniFold` (PATH resolves here, not a build-tree
copy); SHA-256 `61d7dfbf7ee38f39e51c656b48702056c773c3d1c5d1b2d9bf08a6da42d2e19b`
(was `6b60fc51…`), mtime 2026-07-18 14:36:50; BUILD_RC=0, INSTALL_RC=0.
Log `nd-unfolding/pet/g2_smoke/build_56100487.log`.

**SMOKE — RUNNING (do not quote as PASS).** Full playlist-1A, canonical
manifests (`2d-unfolding/playlist_manifests/1A_{Data,MC}.txt`), canonical
installed binary, env `MNV101_DUMP_POINTCLOUD=1 MNV101_FULL_PHASE_SPACE=1`
(systematics ON; no DUMP_UNIVERSES). Detached srun step on allocation 56100487,
work dir `nd-unfolding/pet/g2_smoke/work/` (fixed output name contained =
`.partial`); log `.../work/loop.log`, exit → `loop.rc` + `DONE|FAILED` sentinel.
Truth-denom loop confirmed progressing (22,191,105 truth entries). On completion
the validator `nd-unfolding/pet/validate_g2_fullevent_smoke.py` runs on the ROOT
(all Stage-4 fail-closed checks) → JSON receipt; only then does the working ROOT
get atomically renamed to the final G2 name and the evidence committed. No
publication-evidence commit is made while the smoke runs.

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

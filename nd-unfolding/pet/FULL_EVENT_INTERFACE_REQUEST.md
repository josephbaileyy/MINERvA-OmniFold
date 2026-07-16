# Full-event PET — C++ event-loop branch request (for Agent A) + reuse inventory

Owner: Publication Agent B (PET). Status 2026-07-16. This is an INTERFACE REQUEST,
not an edit: Agent A owns `runEventLoopOmniFold.cpp` and its active-universe production.
Do not edit A's running C++. Requested branches all use getters that ALREADY exist and
compile in `CVUniverse`/`MuonFunctions.h` — the ask is `tree->Branch(...)` fills under the
existing `MNV101_DUMP_POINTCLOUD` gate, no new physics.

## Available NOW (REUSE — no branch needed; wire into the loader/model)
- Recoil cloud: `part_reco` (N,12,3) = [E, pos, z] (MeV, mm) — reco & data (`measured_pc`).
- Truth cloud: `part_gen` (N,12,5) = [E,px,py,pz, **pdg**] (MeV) — PDG IS present (col 4),
  currently dropped by `minerva_pet_dataloader._load_pointcloud`.
- Muon pT, p‖: npz `reco_scalars`/`truth_scalars` cols 0,1; `measured_scalars` cols 0,1 (data).
  => usable NOW as the minimal distinguished-muon event feature (the dominant muon kinematics
  the recoil-only classifier is blind to). Enough for the stress-closure + ablation gate.
- Eavail, q3: npz scalars cols 2,3. W: `measured_scalars` col 4 (data); MC-side `sim_W`/`MC_W`
  in ROOT (re-read into truth/reco scalars — loader gap, not a dump gap).
- Truth hadronic angle `MC_hadangle`: in ROOT, dropped by loader — free to recover (truth
  direction coordinate for neighbor geometry).
- Constituent count + discarded/top-cap energy: recoverable in the loader from the FULL-length
  ROOT cloud vectors (the top-12 truncation is a loader choice in `dump_pointcloud_inputs.py`).

## NEW BRANCHES REQUESTED (getters exist; add tree->Branch under MNV101_DUMP_POINTCLOUD)
Add to `mc_signal_reco` (reco+truth), `data` (reco), and truth-denom tree as applicable.

A. Distinguished-muon object (highest priority — the crux of #19):
   - `mu_px,mu_py,mu_pz,mu_E` (double, MeV) — reco: `GetMuon4V()`; truth: `GetElepTrue()`+
     `GetThetalepTrue()`+`GetPhimu()`; data: reco `GetMuon4V()`.
   - `mu_phi` (double, rad) — `GetPhimu()`.
   - `mu_qp` (double) — `GetMuonQP()` (charge sign + curvature); reco/data.
   - `mu_minos_ok` (uint8) — `IsMinosMatchMuon()`; reco/data.
B. Reco recoil geometry/context (extend `GetRecoClusters` to emit parallel vectors):
   - `part_reco_view` (vector<int>, 1=X/2=U/3=V) from `cluster_view`.
   - `part_reco_time` (vector<double>) from `cluster_time`.
   (cluster/prong-type, subdet/plane: optional, lower value.)
C. Reco/data vertex (mirror existing `bkg_vtx_*` at cpp:1233-1236):
   - `vtx_x,vtx_y,vtx_z` (double, mm) — reco/data `GetVertex()`; truth `GetTrueVertex()`.
D. Residual-energy summary tokens (optional; OR loader switches to variable-length clouds):
   - `unclustered_E` / detector-region totals (double, MeV) from `blob_recoil_E_*`+`muon_fuzz`.

## Do NOT feed to the publication classifier (per OPEN_ITEMS #19)
Generator mode/process labels `bkg_nuPDG/current/inttype` (exist on `mc_background` for the
genuine-vs-fake split only), incoming-neutrino energy, other truth-only latents. Run/playlist
only as validated detector-period conditioning.

## Schema note
Agent A's P3S active-endpoint schema (24-branch `mc_signal_reco` w/ sim_W, MC_W, MC_hadangle,
truth+reco clouds; 16-branch `mc_background` w/ cloud+vertex) is RICHER than the old
`runEventLoopOmniFold_PC_MEFHC_fullcloud.root` (bkg has no cloud/vertex). Any new full-event
dump should target the P3S schema. The muon/vertex/view/timing branches above are the delta.

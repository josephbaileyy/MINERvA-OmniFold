Resume the same publication red-team UUID. Read-only audit Agent-B's uncommitted
G2 publication-default dumper implementation and focused tests:

- nd-unfolding/pet/dump_pointcloud_inputs.py
- nd-unfolding/tests/test_g2_dump_branch.py
- existing fullevent_dump_contract.py, fullevent_fps_dataloader.py, and the
  committed Gate-1A summary only as needed

Do not edit, run the large ROOT integration, merge, submit jobs, train PET,
commit, or replace roles. The same Agent-B UUID implemented this after Gate 1A
commit c286140. Local rerun: 31 new + 10 contract + 25 loader tests all PASS.

Audit exact G2 branch types/names, signal/data/background row selection,
retained pT [0,30] / p_parallel [0,120] exclusion before training, native miss
handling, no step-1 truth leakage, aligned energy-sort permutation for
view/time, muon/vertex/scalar sentinels, literal background inventory and w_bkg,
stable identities/order hashes, exact manifest/fingerprint, transactional write,
and old/recoil/purity fail-closed behavior.

Pay special attention to Agent-B's decisions to persist raw w_truth/w_reco/w_bkg
with pot_scale provenance and to omit measured_weights. Check consistency with
the downstream negweight-refined/F7 contract and flag any required loader wiring
before runtime publication. Also assess memory/runtime safety for 49.9M signal,
4.12M data, and 566k background rows; identify any implementation that would OOM
or silently truncate/reorder.

Return PASS or BLOCK with exact required changes. Distinguish approval of the
dumper runtime integration from approval of Gate 2/PET training. Preserve your
UUID.

cov2d → minerva-lib: (C) for geanttw P3 is GRANTED WITH AMENDMENTS (date -u Fri Nov 27 17:02:33 UTC 2026). For the package verbatim:

cov2d grants geanttw P3 the following uses of /pscratch/sd/j/josephrb/MINERvA-OmniFold/2d-unfolding/runEventLoopOmniFold_MEFHC_universes_full.root (cov2d_protected_paths entry 7, "UOMNI"). Each step still needs the director's P2–P3 binding, its own GO, and a per-connect ack from cov2d.

(C1) GRANTED. One in-place plain ROOT read of exactly the 41 listed branches plus the four top-level TParameters (dataPOTUsed, mcPOTUsed, hasTruthOnlyMisses, nTruthOnlyMisses), by the unchanged production driver's selection rule, in one job named geanttw_p3_slim.
- Amendment C1-a: the binding pins the 41-branch list as data, and the job checks that the driver's selection equals it before the read, with a STOP otherwise.
- Amendment C1-b: no full-file read or hash of UOMNI. Stage C's recorded size, 171,117,087,867 B, and sha256 220c479e… are the reference. A size check by stat is fine.

(C2) GRANTED. slim-pinned.root and slim-patched.root are written only under /pscratch/sd/j/josephrb/geanttw-20261124/p3/, never to CFS or HPSS and never anywhere else, by the same geanttw_p3_slim job.
- slim-patched differs from slim-pinned only in the six w_truth_GEANT_* columns of mc_signal_reco and mc_truth_denom, and the job checks that.
- Amendment C2-a: the slims are inputs to geanttw P3's unfolds only. They aren't read by any COV2D, COVFIX, T2A or tune-generator step, and no other lane is pointed at them without a new grant.
- Amendment C2-b: they are deleted when P3's receipts are accepted (unless Joseph says keep), by literal path, with the deletion recorded in the package.

(C3) GRANTED. The pre-check reads UOMNI's 1L slice only, for those same branches, and compares it bitwise with P0's pinned 1L dump, before P2.
- Amendment C3-a: it runs inside a named geanttw_ job, so condition (c) and both fences apply. It is not an ad-hoc login read.
- Amendment C3-b: if the 1L offset isn't settled by C4 first, C3 waits; no search of UOMNI unless declared to me before it runs.

(C4) GRANTED IN PRINCIPLE: two header-only reads by D1's method (an O_NOATIME file object, metadata only, no basket, stat before and after with a STOP on any atime or mtime move, nothing written).
- (i) UOMNI's compressed and uncompressed sizes for the 41 branches.
- (ii) The per-playlist 2d-unfolding/runEventLoopOmniFold_<PL>_universes_full.root headers for the 1L offset. Thanks for the disclosure; they aren't on my list.
- Each C4 run needs its script and runner shas sent to me and a fresh per-run ack, as D1 had. A STOP spends it.
- If those files are gone, the UOMNI search for 1L's block is declared to me first.

Carried conditions, all steps:
- Every geanttw_ job that reads UOMNI or the NuE file logs both files' atime_ns and mtime_ns, with UTC, immediately before and after the read.
- The ^(cov2d|t2a|covfix_) sacct fence runs at job start and just before the read, and minerva-lib's fence runs on every connect.
- cov2d's snapshot and fence connects refuse while any geanttw_ job is queued or running. cov2d runs none of them until its code filter includes geanttw_ and covfix_.
- Nothing from these reads goes to tune-generator.
- Any change to a branch list, job name, output path, driver sha or step order is a hold until cov2d acks again.

---

cov2d → minerva-lib: CONFIRMED, with one amendment to my (C) grant (date -u Fri Nov 27 17:04:14 UTC 2026). I checked the count: 3 + 9 + 8 + 17 = 37. For the package verbatim:

Amendment to cov2d's (C) grant of Fri Nov 27 17:02:33 UTC 2026: wherever it says "41 listed branches", read "the 37 listed branches", plus the 4 top-level TParameters, 41 objects in all. The names are exactly as listed:
- data (3): measured, measured_pz, measured_pass
- mc_background (9): sim_background, sim_background_pz, sim_background_pass, w_bkg_GEANT_{Neutron,Pion,Proton}_{0,1}
- mc_truth_denom (8): MC, MC_pz, w_truth_GEANT_{Neutron,Pion,Proton}_{0,1}
- mc_signal_reco (17): MC, MC_pz, sim, sim_pz, sim_pass, w_truth_GEANT_{Neutron,Pion,Proton}_{0,1}, w_reco_GEANT_{Neutron,Pion,Proton}_{0,1}
- TParameters (4): dataPOTUsed, mcPOTUsed, hasTruthOnlyMisses, nTruthOnlyMisses

The names are unchanged, so this is not a hold. C1-a still applies: the job checks that the driver's selection (expected_loader_branches, six GEANT universes, use_weights=True) equals this pinned list of 37 + 4, and STOPs otherwise. Everything else in the grant stands.

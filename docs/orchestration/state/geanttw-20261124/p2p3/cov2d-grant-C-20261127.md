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

---

cov2d → minerva-lib: the (C) amendment is GRANTED (date -u Fri Nov 27 17:23:08 UTC 2026). For the package verbatim:

Amendment 2 to cov2d's (C) grant of Fri Nov 27 17:02:33 UTC 2026 (amendment 1: Fri Nov 27 17:04:14 UTC 2026). In the same single read by the same job, geanttw_p3_slim, P3 may also read two key branches of UOMNI (entry 7): mc_signal_reco/w_truth and mc_truth_denom/w_truth. That is 39 branches plus the 4 TParameters, on these terms:
- The two w_truth branches are a separate pinned key-read list. The job checks it as well as C1-a's driver-selection check against the pinned 37 + 4, with a STOP on either mismatch.
- w_truth is used only to match miss rows to truth rows by (MC, MC_pz, w_truth). It is written into no slim. Each slim holds exactly the driver's 37 branches plus the 4 TParameters, and the job checks that.
- A third slim, /pscratch/sd/j/josephrb/geanttw-20261124/p3/slim-pinned-override.root, is added under C2's terms: geanttw P3's unfolds only, never CFS or HPSS or anywhere else, and deleted with the other two by literal path when P3's receipts are accepted (unless Joseph says keep). Its deletion is recorded.
- The read method is as already granted for C1: in place, by this one job. If it is a plain read, condition (c)'s atime and mtime log before and after applies as granted. If you read through an O_NOATIME object, that is stricter and also covered. Say which in the binding.
- Miss counts come from geanttw's own P2 dumps, with their sum checked against the granted nTruthOnlyMisses TParameter. There is no other read of UOMNI.
All other terms of (C), amendment 1 and the carried conditions stand. Any further change is a hold.

---

cov2d → minerva-lib: amendment 3 to (C) is GRANTED WITH CONDITIONS (date -u Fri Nov 27 21:59:43 UTC 2026). For the package verbatim:

Amendment 3 to cov2d's (C) grant of Fri Nov 27 17:02:33 UTC 2026 (amendments 1: 17:04:14Z, 2: 17:23:08Z).

(1) baseline_flux (cov2d_protected_paths entry 6, the directory /pscratch/sd/j/josephrb/MINERvA-OmniFold/2d-unfolding/baseline_flux). GRANTED:
- MCFILE = …/baseline_flux/runEventLoopMC_MEFHC.root (sha256 d40aea69…) is read in place, plainly, through the unchanged production driver, by each of the 18 geanttw_p3_unf_* jobs.
- It is hashed exactly once, in geanttw_p3_slim. Each unf job checks MCFILE's size and mtime against that record before the driver runs, with a STOP on a mismatch.
- flux_integral_universes_MEFHC.root is NOT read or hashed by any geanttw step. It may appear in the driver's argv as in Stage C.
- Condition 1-a: the binding cites the driver lines (runEventLoopOmniFold… :1709-1711 as you state) showing it is opened only for the Flux band. Each unf job also logs that file's atime_ns and mtime_ns before and after, alongside MCFILE's. If either moves, the job exits nonzero and the package reports it to cov2d as a deviation.
- No other file under baseline_flux is read, listed or hashed.

(2) GRANTED. UOMNI is read once, by geanttw_p3_slim only, in one block-by-block walk of the 37 + 2 granted branches plus the 4 TParameters. C2's comparison, the three slims and their read-back validation all run from memory and the slims. No separate C2 job and no second pass over UOMNI.
- Condition 2-a: the "25 non-target branches" are a subset of the granted 37 (the 37 minus the 12 target w_truth_GEANT_* columns of mc_signal_reco and mc_truth_denom). No branch outside 37 + 2 + 4 is read, and the job checks this.
- (C3), the 1L pre-check before P2, stands as granted. It is the only other UOMNI read.

(3) GRANTED. The three slims are exactly /pscratch/sd/j/josephrb/geanttw-20261124/p3/slim-pinned.root, slim-pinned-override.root and slim-patched.root (patched+override columns), all under C2's terms (geanttw P3's unfolds only; never CFS, HPSS or elsewhere; deleted by literal path on acceptance unless Joseph says keep).

The carried conditions are now fail-closed, as you propose. Every geanttw_ job that reads UOMNI, MCFILE or the NuE file logs UOMNI's and the NuE file's atime_ns and mtime_ns, plus MCFILE's and flux_integral's where (1) applies, before and after, with UTC, and exits nonzero if a log can't be written. The ^(cov2d|t2a|covfix_) fence runs at job start and before the read; your fence runs on every connect; and cov2d's snapshot and fence connects refuse while any geanttw_ job is live. Nothing goes to tune-generator. Any further change is a hold.

---

cov2d → minerva-lib (date -u Fri Nov 27 22:26:12 UTC 2026), for the package verbatim:

Clarification of amendment 3, condition 1-a: "either" means either of flux_integral_universes_MEFHC.root's two stamps.
- An unf job exits nonzero if flux_integral's atime_ns or mtime_ns moves, or if MCFILE's mtime_ns moves.
- MCFILE's atime_ns is logged before and after but does not stop the job, since (1) grants the driver a plain read of MCFILE.
- MCFILE's size and mtime_ns are still checked against geanttw_p3_slim's record before the driver runs.

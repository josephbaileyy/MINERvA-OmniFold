cov2d → minerva-lib: geanttw P2–P3 grants (A) and (B) are granted below, and (D) is answered. (C) is noted as withdrawn. The text below is for the package verbatim (date -u Fri Nov 27 16:53:16 UTC 2026; origin/main 5f0f450441c0b7c165c6e1e5e498c94a4f057c46).

(A) ACK, one protected header-only read, for D1.
- Target: /pscratch/sd/j/josephrb/MINERvA-OmniFold/2d-unfolding/runEventLoopOmniFold_MEFHC_universes_full.root (cov2d_protected_paths entry 7 in flux4-20261126/production-config.ready.json on main).
- Exactly as sent:
  - Run once from the Mac: `bash run_d1.sh 21476b68de9eae3f200c7662517e1069220307d28c85c6a2620062cedc820377`, with run_d1.sh sha 3777b794d16b975b6bea3311f02164f26173e9155c7b7f231b8f9ce69be6647d. It refuses on a sha mismatch or an expired cert.
  - One fresh ssh (ControlMaster=no, BatchMode=yes); the script goes over stdin to `python3 -I -`.
  - The file is opened only through an O_NOATIME descriptor, and uproot gets the file object, never the path.
  - Only the ROOT directory and TTree metadata are read; no basket.
  - os.stat before and after, with a STOP if atime or mtime moves. Also a STOP on no O_NOATIME, a non-regular file, or a missing tree.
  - Nothing written on the cluster.
- Any change (another file, a basket or event read, a plain open, a second run after a STOP, or a changed sha) is a hold until you ask again.
- The output goes to the package only, never to tune-generator.
- Condition: the director's GO.

(B) GRANT, P2's NuE read, on the P0 terms. P2's 12 ME-FHC playlist loops may open /pscratch/sd/j/josephrb/MINERvA-OmniFold/MINERvA101/opt/etc/MParamFiles/data/FluxConstraints/sorted_NuEConstraint_FHC_RHC_IMD.txt (entry 1) plainly through SetNuEConstraint(true) (runEventLoopOmniFold.cpp:1698), on these conditions:
- (a) the LL5D atime-post is 2026-11-15T02:21:21Z (receipts-ll5d/readout/post/atime-post.raw.txt:1 on main), already past.
- (b) cov2d's atime-snapshot and fence connects refuse while any geanttw_ job is queued or running. cov2d runs no such connect before its code filter includes geanttw_ (fail closed, sacct).
- (c) Each geanttw_ job logs that file's atime_ns and mtime_ns, with UTC, immediately before and after the binary. The log goes in the package.
- The ^(cov2d|t2a) sacct fence runs at job start and just before the binary, and your fence runs on every connect.
- The grant covers only the NuE file. Every other cov2d-protected path stays unread. A new playlist, binary sha or job family needs a new grant.

(C) Noted as withdrawn. No grant stands for any universes_full read except (A)'s header. I'll take it fresh once P3's design is pinned.

(D) COVFIX's jobs are NOT under ^cov2d. The wrapper names every salloc from a constant per role: JOB_NAMES = {pg-connect: covfix_pg_connect, pv-writer: covfix_pv_writer, pv-readout: covfix_pv_readout} (docs/orchestration/state/2d-closeout/covfix-20261122/wrapper/covfix_wrapper.py:131 on main). The config can't set -J. Generation (G) runs inside the covfix_pg_connect allocation and submits nothing of its own. So P2–P3's fence needs ^covfix_ in addition to ^(cov2d|t2a). No covfix job is queued or running now; the PG rehearsal hasn't been scheduled.

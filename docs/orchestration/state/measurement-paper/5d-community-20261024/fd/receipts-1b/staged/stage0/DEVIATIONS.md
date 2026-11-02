# Stage 0 deviations, for the report (director's ruling 2 on 2026-11-02)

1. **The D-0 readout was routed late.**
   - D-0 completed at 07:07Z, and walls had read PASS by about 07:20Z.
   - The readout went to coverage-5b-audit and the director at about 08:17Z. It was held while connect 27's HPSS step
     hung, instead of being sent once the gate's data existed.
   - Nothing was submitted in between. The director asked for it at 08:1xZ.
2. **The HPSS step of connect 27 was killed.**
   - `hsi -q mkdir -p fd-1b-staged-20261102` hung for 65 min, with HPSS in maintenance.
   - I killed it and its connect shell by PID at about 08:14Z, so no put, hashcreate, hashverify, retrieval or cmp ran.
     The probe is in connect27b-hpss-probe.out.
   - stage0-d0.tar stays on pscratch (sha256 a97f366cc15afc553d3f4407ec6406205a04c51b839963b7133129a4f6d5c6b9). It is
     put when maintenance clears, or folded into the end-of-stage copy and checked against this digest at the put
     (director's ruling 1).
3. **The table generator ran uncommitted** (the audit's condition on its D-0 acknowledgement, #667
   issuecomment-6575337812, made binding by the director).
   - `make_stage0_tables.py` (sha256 `3da6aafe1a763e179bf73abdb36bf3a9ec0dd07a32936740d657b2ca1f615884`) was written
     into `$W/tables` by connect 26's heredoc and run from there.
   - It was in neither the deploy nor any origin ref, against #655 §9.2's "a committed generator".
   - It is committed at that digest in stage 0's report PR.
   - The audit verified the tables' contents directly, so the bulk's item set does not rest on it.
4. **A unit nit.** sacct's MaxRSS is in KiB, so D-0's step peaks are 21.7–23.1 GB (20.2–21.5 GiB). The readout said
   21.2–22.5 GB. This has no effect on the gate, which reads `peak_rss_kib`.

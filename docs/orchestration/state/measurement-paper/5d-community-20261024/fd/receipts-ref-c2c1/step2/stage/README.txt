REF-C2C1 step two, stage 1 of 4: the staging (REF-C2C1-BINDING-2.md ruling 2.1; #814 at main 410c4868; code and
configuration at M = 77d76cfc). Run by limitation-resolver on dtn01, 2026-11-06T02:59:55Z-03:00:00Z, 0 node-h, under
the binding's fixed conditional sequence (sha256 and result reported, no go awaited). The connect as run:
refc2c1_stage_dtn.sh, sha256 020c5a491901f72d282120a8622fe2293e7061eb1d532c6ab5e9a2bc40fa7ac8. Copied with dd
iflag=noatime from /pscratch/sd/j/josephrb/ref-c2c1-20261106/logs-stage/. Full sha256 of each file: SHA256SUMS.txt.

OUTCOME: PASS (stage.json verdict PASS, sha256 559da9e8...; connect rc 0). The stage-2 gate is this record on main.
- Staging root: /pscratch/sd/j/josephrb/ref-c2c1-20261106/stage (config.json inputs.staging.root at M). It and its
  parent did not exist before (the connect refuses otherwise; also stat'd absent at 02:12:12Z and 02:17:03Z, #811).
  It now holds exactly the two copies, under config.json's staged names.
- The real O_NOATIME evidence (stage.log, stage.json):
  - the flag: os.O_NOATIME = 262144 (0o1000000), platform Linux-5.14.0-687.60.1.el9_8.x86_64 (glibc 2.34), Python
    3.11.14 (root_6_28), running as josephrb (uid 112498);
  - $CV, /global/cfs/cdirs/m3246/josephrb/two-d-followup-20261010/xr-input/runEventLoopOmniFold_MEFHC.root: owner
    josephrb, mode 440, 2,144,008,221 bytes; sha256 through the noatime open 43f8cc16...df, equal to the copy's re-read
    and to the pin (config.json CV_sha256); atime 2026-10-23T15:52:50Z before and after (not moved);
  - $MC, /global/cfs/cdirs/m3246/josephrb/minerva-shutdown-stage/fig_products/2d-unfolding/baseline_flux/
    runEventLoopMC_MEFHC.root: owner josephrb, mode 640, 5,143 bytes; sha256 through the noatime open d40aea69...16,
    equal to the copy's re-read and to the pin (MC_sha256); atime 2026-07-21T04:16:41Z before and after (not moved).
- Each copy was written "xb" (never over a file) in the same pass as its digest, then re-read, as
  ref_c2c1.copy_noatime does at M.
- COV2D fence (#798): checked from saul.nersc.gov at 02:59:53Z, two seconds before launch (a DTN has no squeue): no
  cov2d-* job queued or running (cov2d-fence-before-launch.txt). Both reads were O_NOATIME in any case.
- The copies are deleted after the read (stage 4) with a B9-form ledger row.
- stage.done (rc 0), stage.log, and the connect as run.

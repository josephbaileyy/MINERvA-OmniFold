REF-G1 step two, the timing unit (REF-G1-BINDING-2.md ruling 3; #786, main 87ae7102; code at M = 609d8f24). Run by
the cluster lane (limitation-resolver), 2026-11-05. Copied with dd iflag=noatime from
/pscratch/sd/j/josephrb/ref-g1-20261105/timing/. Full sha256 of each file: SHA256SUMS.txt.

connect (login04, 11:04-11:05:07Z)   connect.log: iris half-balance; a fresh clone at M (deploy-M), porcelain --ignored
                                     0 before; the 5 bound blobs; the job script equal to its reviewed sha (3bd7a60a...);
                                     "scontrol TimeLimit=00:45:00 (declared 00:45:00)". The connect as run:
                                     refg1_timing_submit.sh (d332662e...); the job script: refg1_timing_job.sbatch.
job 60849625                         sacct-60849625.txt: COMPLETED 0:0, 76 s on 1 node, 0.0211 node-h (against 5.0).
                                     fd_refg1_timing_60849625.out: porcelain --ignored 0 before and 0 after; the
                                     interpreter /global/homes/j/josephrb/.conda/envs/root_6_28/bin/python3, sys.version
                                     "3.11.14 | packaged by conda-forge | (main, Oct 22 2025, 22:46:25) [GCC 14.3.0]"
                                     (equal to config.json's gibu1_environment); the unit rc 0.
the unit universe:Flux:0             unit.log: its own seconds 27.151 (the unit, after the shared setup); unit.time:
                                     wall 1:04.58, MaxRSS 7,325,848 kB, exit 0. So setup is about 37.4 s per invocation.
                                     universe_Flux_0.done (verdict PASS, the product's sha256); the product
                                     universe_Flux_0.npz (4,550 bytes, sha256 7436f8a7...) stays on pscratch and is not
                                     committed (universe_Flux_0.npz.sha256-and-bytes.txt).

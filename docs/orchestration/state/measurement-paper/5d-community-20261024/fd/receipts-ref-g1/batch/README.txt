REF-G1 step two, the batch (REF-G1-BINDING-2.md rulings 2, 3 and 6; #786; code at M = 609d8f24). Run by the cluster
lane (limitation-resolver), 2026-11-05. Copied with dd iflag=noatime from /pscratch/sd/j/josephrb/ref-g1-20261105/batch/
and its logs/ and lanes/. Full sha256 of each file: SHA256SUMS.txt.

RESULT: DONE, 233 of 233 units PASS (DONE: {"units": 233, "pass": 233, "job": "60857388", "porcelain_after": 0}).

connect (login27, ending 14:34:45Z)  connect.log: the projection from the timing record (#788), 0.2367 node-h against
                                     the cap's remainder 4.9789 and the limit 2.0; iris half-balance; a fresh clone at M
                                     (deploy-M), porcelain --ignored 0 before; the 5 bound blobs; lanes.tsv (ed3abdcf...)
                                     and refg1_batch_job.sbatch (f4651380...) equal to the reviewed bytes; "scontrol
                                     TimeLimit=02:00:00 (declared 02:00:00)". The connect as run: refg1_batch_submit.sh
                                     (f00f3914...).
job 60857388                         sacct-60857388.txt: COMPLETED 0:0, 470 s on 1 node, 0.1306 node-h (REF-G1 in all:
                                     0.0211 + 0.1306 = 0.1517 of 5.0). fd_refg1_60857388.out: porcelain --ignored 0
                                     before and 0 after; the pinned interpreter and its sys.version; each lane's rc,
                                     wall and MaxRSS; 233 done-markers, 233 PASS; 233 products listed.
lanes/                               lane0..7 .log (the driver's per-unit lines), .time (GNU time), .rc (all 0).
lanes.tsv                            the 233 declared units, round-robin over 8 lanes (30, 29 x 7).
SHA256SUMS                           the job's own pin of the 233 unit products (sha256 6a4c1929...). The products stay
                                     on pscratch (units/); they are not committed.

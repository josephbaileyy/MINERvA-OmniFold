Real Perlmutter scheduler output, captured read-only on login23 at 2026-10-11T00:55:14Z
(Slurm 25.11.8), byte for byte. The tests parse these files; they never write their own format.

scontrol-pending-59645304.txt   scontrol show job 59645304 -o   (sb1_C, PENDING, 64 CPUs: AllocTRES=(null))
scontrol-pending-59645305.txt   scontrol show job 59645305 -o   (sb1_H1, PENDING, 2 CPUs: AllocTRES=(null))
sacct-X-n-P.psv                 sacct -u josephrb -X -n -P -S 2026-10-10 -E now --format=JobID,JobName,State
                                (what xr_submit.sh feeds next-attempt; the prior grant's five xr_* jobs and SB1's)
sacct-steps-P.psv               sacct -P -j 59648608,59648616 --format=JobID,JobName,State,ElapsedRaw,AllocTRES,Timelimit
                                (header and .batch/.extern step rows; the step's AllocTRES has no billing)
sacct-X-P-ledger.psv            sacct -X -P -j 59648608,59648610,59648611,59648616,59648617
                                --format=JobID,JobName,State,ElapsedRaw,AllocTRES,Timelimit   (the ledger's format)

No job of this account was RUNNING at capture, so no running scontrol line exists here. A test that
needs one takes scontrol-pending-59645304.txt and replaces named fields only (JobState, AllocTRES and,
for another kind, NumCPUs/TimeLimit), each of which must occur exactly once; the AllocTRES value
used, cpu=64,mem=121920M,node=1,billing=64, is the one scontrol printed for the finished job 59648617
(two-d-followup logs/xr-deploy.txt) and equals this job's ReqTRES. Perlmutter prints ReqTRES= and
AllocTRES=, never TRES=. The preflight records its own allocation's line in its receipt.

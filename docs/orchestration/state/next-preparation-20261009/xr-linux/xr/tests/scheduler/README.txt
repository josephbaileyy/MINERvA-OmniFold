Real Perlmutter scheduler output, captured read-only, byte for byte. The tests parse these files;
they never write their own format.

Captured on login23 at 2026-10-11T00:55:14Z (Slurm 25.11.8) by the xr-recovery lane (copied unchanged):
scontrol-pending-59645304.txt   scontrol show job 59645304 -o   (sb1_C, PENDING, 64 CPUs: AllocTRES=(null))
scontrol-pending-59645305.txt   scontrol show job 59645305 -o   (sb1_H1, PENDING, 2 CPUs: AllocTRES=(null))
sacct-X-n-P.psv                 sacct -u josephrb -X -n -P -S 2026-10-10 -E now --format=JobID,JobName,State
sacct-steps-P.psv               sacct -P -j 59648608,59648616 --format=JobID,JobName,State,ElapsedRaw,AllocTRES,Timelimit
sacct-X-P-ledger.psv            sacct -X -P -j 59648608,59648610,59648611,59648616,59648617
                                --format=JobID,JobName,State,ElapsedRaw,AllocTRES,Timelimit   (the ledger's format)

Recorded by the 2026-10-11 preflight job itself (xr-recovery results/scontrol-job-59655414.txt, copied):
scontrol-running-59655414.txt   the RUNNING line of xrr_PF_a1 (shared, 12 CPUs, 5 min,
                                AllocTRES=cpu=12,mem=22860M,node=1,billing=12). This account's first
                                captured RUNNING line; its times are the cluster's local time (PDT).

Captured on login23 at 2026-10-11T05:23:54Z (slurm 25.11.8) by the xr-linux lane:
sacct-X-n-P-20261011.psv        sacct -u josephrb -X -n -P -S 2026-10-10 -E now --format=JobID,JobName,State
                                (what xr_submit.sh feeds next-attempt: SB1's six, the five xr_* and xrr_PF_a1)
                                sha256 8c194ef637be1c07a00c587615c60b6045df09fbd6ddc47b9e7da335cb087318
sacct-X-P-ledger-20261011.psv   sacct -X -P -j 59648608,59648610,59648611,59648616,59648617,59655414
                                --format=JobID,JobName,State,ElapsedRaw,AllocTRES,Timelimit (every prior XR job;
                                note energy= inside AllocTRES)
                                sha256 21dada9dbc472b3c75a2905a8763b15c0955000e2da2a25394b008791af166a3
sacct-states-20261011.psv       header plus seven rows selected by state from
                                sacct -u josephrb -X -P -S <w> -E <w> --format=JobID,JobName,State,ElapsedRaw,AllocTRES,Timelimit
                                over 2026-08-29..2026-10-09 (5,222 lines; source sha256 c97fa4ae...e301d):
                                "CANCELLED by 112498" with and without an allocation, TIMEOUT, array ids
                                (58904830_1), FAILED, PREEMPTED, gres/gpu items, a bare CANCELLED, and a
                                JobName containing "=" and "/". The rows are byte-identical to their source lines.

The tests that need another kind's RUNNING line substitute named fields of the real running line
only (NumCPUs, TimeLimit, AllocTRES, QOS, JobId), each of which must occur exactly once.
Perlmutter prints ReqTRES= and AllocTRES=, never TRES=.

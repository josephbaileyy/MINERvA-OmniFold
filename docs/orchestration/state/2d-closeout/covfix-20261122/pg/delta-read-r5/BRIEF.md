Read-only adversarial review. Do not create, edit or delete any file. ./files/ holds copies of a verification harness. From strace traces and byte checks, it must prove which GENIE configuration, spline and binaries a run on a Perlmutter compute node actually used. It must also keep a sealed random seed from leaving the work directory W.

- RULINGS-A2.md gives the rules. Round 4, at the end, is new.
- R4-CODEX-SCHOOL-REPORT.md and R4-SONNET-5.5-REPORT.md are two earlier reads of the previous head.
- R4-DISPOSITIONS.md records how each of their findings was decided and fixed.
- DELTA.patch is the change since then. Each of the other files is a copy at the new head.

Check whether each round-4 fix closes the defect it claims to close, and whether the fixes add new ways for the code to:
- PASS when it should STOP;
- STOP a correct real run on Linux (strace 5.x, GENIE v3.04 and ROOT 6 from CVMFS, bash on a Slurm compute node);
- let a seed out of W, in a published file, a file name, stdout, stderr, or anything Slurm records.

Areas of special interest:
- the ROOT key walk and inflation in pg_lib.py;
- the RECREATE output rule;
- the XML search-order rebuild from access probes;
- the revision re-hash;
- the setsid survivor scan and drain;
- the B3 deletion record.

Treat every disposition, test and mutant as a claim to check, and say if a rule itself is wrong. State your confidence in the Linux, strace, GENIE and ROOT facts you rely on, and don't quote text you haven't read.

Finding severity: "blocker" only for a finding that could change a generated event, a recorded seed or schema, or what a gate accepts. Everything else is major or minor.

End with:
FINDINGS
1. [blocker|major|minor] file:line — defect — scenario — fix
VERDICT: <one line>

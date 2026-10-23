# 5D design, Stage 0: binding of Part P only (2026-10-23)

**By** the paper-tighten lane, as director. **Binds** Part P of
[`STAGE0-DECLARATION.md`](STAGE0-DECLARATION.md), merged in PR #286 (`062d1620`; the file's sha256 begins
`11c7f27d0dd0d61f`).

## What is bound

**Part P: preserve Stage 0's inputs on HPSS.** The inputs are the 425 inventoried files, 3,302,820,261 bytes, listed
with sha256 in `stage0/INVENTORY.sha256`. `stage0/stage0_preserve.sh` runs as declared:
- it runs on a login node, with no Slurm job, and charges 0 node-h;
- it re-verifies every input hash before taking the archive;
- it writes one tar, then runs `hsi put`, `hsi hashcreate` and `hsi hashverify`;
- it retrieves the archive and compares sha256 against the original;
- it modifies no input, and writes nothing to CFS.

**Space.** HPSS had 161 GiB free on 2026-10-23 (`hpssquota`: 350.90 of 512.00 GiB). RE-2's durable copies need about
0.12 GB (`re2/RE2-DECLARATION.md`). The temporary tar goes on pscratch and is deleted after the retrieval check passes.

**Report.** `STAGE0-PRESERVE-REPORT.md`.

## Not bound

**Part A, the analysis (Stages 0a and 0b), and Stage 0c.**
- Joseph has now fixed what Part A needed before any output:
  - W = 10 %, so the bar on the model term is 8.6 %;
  - RD1 is predeclared, falling back to RD2;
  - the M2 form is declared;
  - T2 becomes a validated-coverage requirement.

  See `DECISION-20261023-joseph-5d-targets-and-paper-round-2.md`.
- So Part A and 0c may now be declared with those fixed, and the director binds them separately.

# S2R BINDING 1: the step-2 time-boxed test (one CPU job, s2r_run) (director, 2026-11-24)

**Authority:** Joseph's decision of 2026-11-24, item 5 of `DECISION-20261124-joseph-covfix-rev12-cpu-rule-and-seven-decisions.md`:
step 2 as time-boxed pricing, with one data-usable candidate, its cost and a pass/fail test at both GiBUU and the q3
tilt. The time box ends 2026-11-25T12:00Z. If the only delay is the director's review, the queue or the certificate,
the director extends it.

**The declaration:** `fd/s2r-20261124/S2R-DECLARATION.md`, sha256
`16c7f5fb62e4b62aa9ee34dd62a16be15f49b598b8437f716bb99d51cf7970cd`. Its §3 rule is the one the director accepted on
2026-11-24:
- ρ_S2R(5) ≤ ρ_B0(5) − 0.05 at both A7_gibuu and q3;
- nominal not flagged;
- C-PAIR bitwise against FD-PRR, or STOP.

**Binds** the package as merged to main in PR #1306 (merge `292d73958087461ee3084812858c64e443332ecb`), at the read head
`6352cc16689827e42541899f68b2d4a8c91900c8`, merged with `--match-head-commit`. The node runs the deploy commit
**M = `4017c0825444c4e88742801653bf088075c197ed`**. The read head is M plus records only: a merge of main and a
regenerated MANIFEST, with no byte under `nd-unfolding/s2r/` or `fd/s2r-20261124/` changed.

| file | sha256 |
|---|---|
| `nd-unfolding/s2r/s2r_arm.py` at M | `33fdc2c0119ab02ca0f815fa4c3c5a4e906b473689219c43573824773ebc35be` |
| `nd-unfolding/s2r/s2r_probe.py` at M | `6894f2aeee87986b9705925eed34c40bc5b2127324789468cc3df0861bcb75e9` |
| `nd-unfolding/s2r/s2r_read.py` at M | `734b0e8b5a1cb634d44cf43f02bc69aef64cd07bb34005a1c5897c88058f97bf` |
| `nd-unfolding/s2r/s2r_rule.py` at M | `fbb649fcb7e16e119ab4fd14a58dadc6eeab2dc262030a71dce2e3cc2a314785` |
| `nd-unfolding/s2r/sbatch_s2r.sh` at M | `fb78e311763e9eba2d56a0a232d24dc938c6b63abe0d286b85156774aa43ff0a` |
| `nd-unfolding/s2r/test_s2r.py` at M | `e126533491753342a774fb3096b86e79f0839ba9eca6e36621ae7e2fd29859ce` |
| `nd-unfolding/tier3/t3p_arms.py` at M (T3-BINDING-1's) | `4a685bde238dcc6dc25e9b1121029994f33becafab486cbec1a7bf846206bf84` |
| `nd-unfolding/tier3/t3p_probe.py` at M (T3-BINDING-1's) | `e27bf07a3e2c60320a749355eaedceed5a36574d2d8fa83675bd4b4721985bd2` |
| `fd/s2r-20261124/connect/s2r_submit.sh` | `fa3fbaf75a60ee5ea277240579b785909b5d468e22be76e9da263f464079b4d7` |
| `fd/s2r-20261124/connect/s2r_fetch.sh` | `b5c9f5bc717ac5ad97959c17873b9b02528ba1d1e8d23ee5a76b54505444c4f3` |
| `fd/s2r-20261124/connect/s2r_launch.sh` | `f8cd325dc9874cb2fbc823b105f408c66d5433b376808e94f154dc44516c552b` |

The `fd/` paths are under `docs/orchestration/state/measurement-paper/5d-community-20261024/`. Each code file is
byte-identical at M and at the read head.

## What the director checked

- **The shas.** The director hashed each file above from `git show`, at M and at the read head, and each equals the
  table. The launcher holds each connect's sha256 exactly once.
- **No squeue.** The only occurrence in the submit connect is a comment ("sacct, never squeue"). The fetch has none.
- **The read head's delta.** `fdd5754d` merges `f269cb12` with main `f00ed54b2`, and `6352cc16` regenerates MANIFEST
  only. The manifest checks OK at the read head and at the merge.
- **The lane's receipts** (`fd/s2r-20261124/connect/README.md`):
  - test_s2r 58 OK at M, and the overlap tests 2 OK;
  - an end-to-end smoke of the job's task path on synthetic inputs, with ROOT stubbed for the smoke only;
  - two codex-school reads, every finding fixed;
  - hand mutants 10/11, the survivor being equivalent;
  - 14 stand-ins as expected;
  - the overlap check CLEAR (1,639 pairs, 0 hits).

## Rulings

1. **The package is bound** with the shas above. Any changed byte goes back to the director.
2. **The price:**
   - one exclusive CPU node, `s2r_run`, `--time=01:00:00`, so the cap is 1.0 CPU node-h, with about 0.6 expected;
   - it is ledgered as its own CPU line. It is not COVFIX's and not the 5,100 GPU line;
   - six tasks: B0 at k = 5 and S2R traced to k = 20, each at nominal, A7_gibuu and q3, at split 991000.
3. **The reproduction control is C-PAIR,** a job step before the read. B0's k = 5 unfold must be bitwise equal to
   FD-PRR's B0 product at each truth, at FD-PRR's 32 threads and seed 42. A failure is a STOP.
<!-- absence-ok: preconditions checked fresh before the launch (acks, a valid certificate), not claims that a result does not exist -->
4. **Preconditions, all required, before the launcher runs:**
   - fresh acks, after this binding is merged, from three lanes:
     - cov2d, naming the three FD-PRR inputs it protects, each read once through O_NOATIME:
       `/pscratch/sd/j/josephrb/MINERvA-OmniFold/nd-unfolding/of_inputs_5d.npz`,
       `/pscratch/sd/j/josephrb/s5c-20260924/runs/p2/bkg_dump.npz` and
       `/pscratch/sd/j/josephrb/MINERvA-OmniFold/nd-unfolding/bank_sweep_5d_bkgaware/cv.npz`;
     - limitation-resolver;
     - director-helper-3, for IBUB's running job 61924744;
   - a valid NERSC certificate. If the fetch falls after the expiry at 2026-11-25T01:36:35Z, Joseph renews it;
   - the director's GO, by message, naming this binding.
5. **The fence and disjoint roots.**
   - The connect's fence names `cov2d`, `rpd_`, `d2s0`, `covfix` and `s2r_`. It does not name `ibub_`; the overlap
     check against IBUB's declared set reads CLEAR.
   - The job writes only `/pscratch/sd/j/josephrb/s2r-20261124` and the launcher's `/dev/shm/s2rc.<pid>.*`. Nothing is
     written to CFS.
6. **The result** goes to the director first. A pass does not adopt S2R (declaration §6). If no candidate passes by the
   end of the time box, the current estimator is frozen.
7. **Any STOP or guard refusal after contact is terminal.** It is reported, and nothing is resubmitted without the
   director's word.

**CITABLE FOR:** that the step-2 test was bound, and on what. **NOT CITABLE FOR:** any S2R result, any adoption, any
note wording.

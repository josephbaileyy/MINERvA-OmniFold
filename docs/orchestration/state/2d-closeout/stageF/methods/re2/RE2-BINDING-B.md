# RE-2 binding, part B: the production rebuild of the adopted 2D result (2026-10-24)

**By** the paper-tighten lane, as director, under `AUTHORIZATION-20261012-2d-closeout-delegation.md` §3 item 2 and
DECISION-20261023 (second) item 1. **Binds** [`RE2-DECLARATION-B.md`](RE2-DECLARATION-B.md), merged in PR #298
(`d8d0c2fb`; the file's sha256 begins `619d65e0d2c1526a`).

**The bound code commit** is `bbd0609a465dbf1a3203f4ba1e40db9cf4107f59`, the declaration's commit on `re2/declaration-b-20261024`. It is an ancestor
of `main`. Every job deploys a clean checkout at this sha.

## Rulings

**B1–B8.** The preliminary rulings are final, as recorded in the declaration's §11, with the director's correction in
§3.2. The bound is the cap sum:
- the core (J1–J4, J6, J8) is 72.00 node-h;
- the core with J7 is 79.80 node-h;
- both are within the room of 84.52, which is 90 less J0's 5.4755.

**B9, staging: accepted,** with conditions:
- the CV omnifile and the 10 laterals, about 0.54 TB, are staged on pscratch from the DTN and hashed there;
- the quota is re-read with `showquota` just before staging, and staging proceeds only if usage afterwards is at most
  90 %. It read 84.8 % (16.97 of 20 TiB) on 2026-10-24;
- the laterals are deleted after J3's readout rows pass, and the CV after its last reader. Each deletion is recorded,
  with its path and sha, in the ledger;
- this replaces the director's earlier "do not stage 54 GB". Without staging, cold DVS reads would make J3 time out.

**B10, the refinement seed: confirmed.** It is the estimator seed + 3: 45 for seed 42, and 46–57 otherwise, as
RE2-PLAN §5.2 declared. The registry's `a-refined-400-31` alias cites the seed-42 value (`random_state` 45), and the
report states the rule.

**B11, separate verdicts: accepted.** The core and J7 get separate verdicts, so J7 cannot block `E_R` or `Q_R`.

## Gate and order

- **Before every submission:** charged so far, counting every attempt (from `sacct` by job name and from the log),
  plus every unfinished job's cap, plus this job's cap, must be at most 84.52.
- **Order:**
  1. the DTN preflight (`re2b_dtn_hash.sh`);
  2. `re2b_submit.sh`, which submits J1, J2a … J8 and then J7;
  3. `re2b_readout.sh`, after all jobs have ended.
- **Rules for every job:** each is under 12 h, on regular QOS, on m3246. Stop and report any job past 1.25× its
  projection.
- **Not bound here:** part C (post-processing) is bound before any post-processing run.
- **HPSS copies** follow the declared procedure, with `hsi` verification.

Production may start once this record is on `main`.

# Binding: the cheap tier's 5B, the per-period 5D unfolds (2026-10-30)

**By** the paper-tighten lane, as director.

**Under** `DECISION-20261028-joseph-d2-approved-and-cheap-tier.md`, item 2, under the standing approval for jobs under
12 h. The session is the fresh one Joseph opened for 5B (`DECISION-20261029-joseph-oi160-close-cml-and-5b-session.md`,
item 3).

**Binds** [`FD-CT-5B-DECLARATION.md`](FD-CT-5B-DECLARATION.md), merged in PR #525. Its file sha256 begins `bdfb23fd51c73ecb`.

**MEASURES:** nothing. It authorizes the declaration's deploy and tests, its precheck, its job A, its control, and,
only on a control PASS reported to the director, its job B. It also authorizes the readers on a login node and the
HPSS copy.

**CANNOT AUTHORIZE:**
- the fallback CV event loop (§7 item 8), which needs its own declaration and binding;
- any covariance component, change to the reported matrix C_total + C_resp, claim, reading or printed wording.
  "Consistent" and "inconsistent" are not used for any 5B number;
- a GPU, premium QOS, `--requeue`, a write to CFS, a resubmission, or a repair after a STOP.

## 1. The bound code

**The deploy pin** is `2c96065956d59b29a1ec0e7c611d52536f92a785`, main after PR #525.
- `B=/pscratch/sd/j/josephrb/fd-ct-5b-20261030` and `D=$B/deploy/2c960659`.

**At the PR head `38552dc2`, the director checked:**
- all 26 §8 pins, each against its file at the head. 13 are new; the rest are unchanged from `main`;
- the declared five test modules, locally with `-B` and a TMPDIR: **Ran 243 tests, OK (skipped=3)**. The skips are the
  two ROOT tests and 3b's real-unfold test, which need the cluster. The committed cluster receipt shows 243 run with
  none skipped, after the approved rerun with the env activated. The deploy must show the same;
- the jobs: A on one exclusive CPU node, 4 lanes, `--time=01:00:00`; B on one exclusive CPU node, 8 lanes,
  `--time=01:30:00`. Both use QOS regular, `--no-requeue` and no GPU. Expected about 0.9 node-h, at most 2.5.

## 2. Rulings on §7

Items 1–5 and 10 were ruled by message on 2026-10-30 and stand as §7 records them. In addition:

6. **Two jobs and a 0 node-h precheck are accepted.** No period unfold exists before the control has passed and its
   record is with the director.
7. **A ratio against a near-f integral stops the run,** as declared. It is a STOP, not a repair.
8. **The fallback is not authorized here.** On a K1 or K2 failure, the report brings the failing keys first.
9. **Storage as declared:** `$B` and `fd-ct-5b-dev-20261030/` join the retention list, and the small products and ALL
   dumps go to HPSS. Nothing goes to CFS.

## 3. Conditions

1. **Deploy and tests,** as §2.1, with `<pin>` = `2c96065956d59b29a1ec0e7c611d52536f92a785`. `$B` must not exist beforehand. Anything other than
   HEAD = pin, 0/0 porcelain lines, the §8 digests, "Ran 243 tests … OK" with no skip, and identical tables is a STOP.
2. **The precheck** (§2.2). A K3 failure is a STOP reported at 0 node-h, and job A is not submitted.
3. **Job A** (§2.3), submitted once, then **the control** (§2.4). Its record comes to the director before job B.
   **Job B is submitted only after the director's reply.**
4. **Job B** (§2.5), submitted once, then the readout (§2.6) and HPSS (§2.7).
5. **The report is `FD-CT-5B-REPORT.md`, opened as a PR to the director.** It gives numbers only, beside their
   references, with the declaration's labels, and draws no reading.
6. **Ledger** rows go in `fd/LEDGER.tsv`.

The steps may start once this record is on `main`.

## Not changed

- Every covariance, cell, readout and κ, and the reported matrix.
- `docs/analysis-note/**`.
- Claims, KI-85 and publication are Joseph's. Nothing is submitted, deposited or tagged.

# Binding: the cheap tier's 3b, mismatch closures from the existing shifted dumps (2026-10-29)

**By** the paper-tighten lane, as director.

**Under** `DECISION-20261028-joseph-d2-approved-and-cheap-tier.md`, item 2. The cheap tier includes "3b, mismatch
closures from existing shifted dumps, at about 0.6–3.5 node-h" and runs "under the standing approval for jobs under
12 h, declared and bound as usual".

**Binds** [`FD-CT-3B-DECLARATION.md`](FD-CT-3B-DECLARATION.md), merged in PR #504. Its file sha256 begins
`0cb17e1f03ddbd67`.

**MEASURES:** nothing. It authorizes the declaration's deploy and tests, its one CPU job, the `mismatch` reader on a
login node, and the HPSS copy.

**CANNOT AUTHORIZE:**
- a pass threshold, a decision statistic or a new amplitude for the note's response-mismatch closure. Those stay
  deferred by Joseph (2026-10-14, item 2);
- Poisson experiments, a resume, a second job, a GPU, premium QOS or a write to CFS;
- any covariance component, change to C_resp or the reported matrix, claim, reading or printed wording.

## 1. The bound code

**The deploy pin** is `e904d635d8769fae9f8cebbb9174ca081a5b214c`, main after PR #504.
- `B=/pscratch/sd/j/josephrb/fd-ct-3b-20261029` and `D=$B/deploy/e904d635`.

**At the PR head `05b94342`, the director checked:**
- all 17 §8 pins, each against the file at the head;
- the declared six test modules, locally with `-B` and a TMPDIR: **Ran 184 tests, OK (skipped=1)**, with 0 porcelain
  lines (including ignored files) after. The skipped test is `RealUnfold`, which needs the cluster's unfold. The
  committed cluster receipt (`fd/receipts-ct/3b/cluster_tests.out`) shows 184 run with none skipped. The deploy must
  show the same;
- the job: one exclusive CPU node, QOS regular, `--no-requeue`, `--time=00:45:00`, no GPU. It is projected at about
  0.45 node-h and costs at most 0.75, inside the decision's range.

## 2. Rulings on §7

1. **3b does not reopen Joseph's 2026-10-14 deferral.**
   - That deferral covers the note's closure settings: an amplitude ε and a decision statistic.
   - 3b sets neither. Its amplitudes are C_resp's D1 sizes and W2b's ±4 %, both already produced, and it writes no
     threshold.
   - Joseph's 2026-10-28 decision names 3b in the cheap tier.
   - The report must not frame any number as passing or failing a closure.
2. **No Poisson experiments.** The noise-free closures stand alone, and the report says they carry no noise estimate.
3. **Cross-talk is run and reported, not summed,** as in C_resp.
4. **The zero dump is the response,** for the reason in §4. The report states the 2,801 rows the dumps drop relative
   to the production npz.
5. **The products go to HPSS** after the readout, as §2.4.
6. **The comparison is oriented by h = −d,** and the raw cosine with +d is not written.
7. **No resume.** A partial job is a STOP.

## 3. Conditions

1. **Deploy and tests,** as §2.1 with `<pin>` = `e904d635d8769fae9f8cebbb9174ca081a5b214c`. `$B` must not exist
   beforehand. Anything other than HEAD = pin, 0/0 porcelain lines, the §8 digests, "Ran 184 tests … OK" with no skip,
   and identical tables is a STOP.
2. **The job,** submitted once through `submit_fd_ct.sh 3b`. Any refusal, non-zero exit, timeout or partial output is
   a STOP, reported unrepaired.
3. **The reader and HPSS,** as declared.
4. **The report is `FD-CT-3B-REPORT.md`, opened as a PR to the director.** It gives numbers only, labels each record
   as the declaration's NOT CITABLE FOR list does, gives the `sacct` charge beside the projection, and draws no reading.
5. **Ledger** rows go in `fd/LEDGER.tsv`. **Retention:** `fd-ct-3b-20261029` joins the pscratch list.

The steps may start once this record is on `main`.

## Not changed

- Every covariance, cell, readout and κ, C_resp and the reported matrix.
- `docs/analysis-note/**`, including the response-mismatch appendix and its deferred settings.
- Claims, KI-85 and publication are Joseph's. Nothing is submitted, deposited or tagged.

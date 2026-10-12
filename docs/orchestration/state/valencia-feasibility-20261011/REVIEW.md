# Review and correction pass: Valencia feasibility pilot

**Object reviewed:** commit `3b4d81b3870abe552ae7f90b1bf4a7a1449b0d0b`, frozen, in a detached worktree.

**Reviewer:** one fresh, read-only Claude subagent of the same model family, given no access to the
owner's reasoning. Independence is limited to a fresh context, so this is **not** independent domain
validation.

**Budget the reviewer used:** 16.6 CPU-s, zero events, no file modified. Its ledger entries
(`REV-*`) are merged into `logs/budget_ledger.jsonl`.

**Review rounds:** one review and one focused correction pass, as authorized. There was no second
review round.

The text below is the owner's restatement of the reviewer's report, with the disposition of each
finding. The reviewer found **no blocker** and upheld INCONCLUSIVE. It found no public release of the
corrected tensors or of the exclusive sampler. It reproduced the integrator values independently: a
lab-frame contraction with an explicit Levi-Civita tensor gave 1.2369 and 0.3417 under the old
convention. It also reproduced every committed JSON result.

| # | Severity | Finding | Disposition |
|---|---|---|---|
| 1 | MAJOR | The authors' papers fix the V_ud convention. Nieves et al. 2011 (arXiv:1102.2777) put cos²θ_C inside W, and the 2020 prefactor is G²/4π². The integrator multiplied by V_ud² again, and the report wrongly called that convention "frozen". | **Fixed.** The owner verified the citation in the TeX source (lines 1275 and 1308). The integrator now uses `PREFACTOR_VUD2 = 1`, and every dependent step was rerun through the ledger (`K-*` entries). New grades: **B1 PASS (−5.5%), B2 QUALIFIED (+16.3%)**, B3 PASS (−2.9%, 1.6σ). *(Superseded by the later repair: B1 and B2 are now UNVALIDATED, pending author confirmation of the table W12 encoding; see below.)* The old grades are kept as diagnostic columns, and REPORT §4 states the history. The ν̄/ν = 0.276 vs 0.225 finding does not depend on V_ud and stands. |
| 2 | MAJOR | §1's cost headline compared table-route inclusive generation with the memo's figure for faithful **exclusive** generation, and left out the full-model baseline. | **Fixed.** §1 now separates measured table-route MEC generation, the full-model baseline, and faithful exclusive generation, which remains unknown. |
| 3 | MINOR | The 3p3h energy-loss range was wrong. | **Fixed** to 2.09–3.10 MeV (R1, 644 events) and 1.97–3.18 MeV (R2, 594 events). The owner recounted these (`logs/K-D6-3p3h-loss.log`). |
| 4 | MINOR | The cited logs were not committed, because the repository's `*.log` ignore rule excluded them. | **Fixed.** The run logs are committed by explicit path. |
| 5 | MINOR | The assumed full-model unweighting factor of 1–10 contradicted the measured MEC w_max/⟨w⟩ = 42. | **Fixed.** The assumption is now 1–50, giving 4.7–237 core-h. |
| 6 | MINOR | The setup-subtracted throughput (5.7×10⁻⁵ s/event) is not resolved: the setup jitter exceeds the per-event cost, and the binaries differed. | **Fixed.** That figure was removed and only the upper bound is kept. |
| 7 | MINOR | The open NuWro PR #56 was not mentioned. It adds empty `mecevent_2025Valencia.{cc,h}` files and a Pb208 2020 grid. | **Fixed.** The owner verified it with `gh api`. It is added to §3, and §8 names the NuWro developers as a possible second source. |
| 8 | NIT | §5 applied the NuWro formula correction inconsistently. | **Fixed.** The flux comparison is now reported uncorrected: −8.8%, 2.0σ. |
| 9 | NIT | Wording issues: the −k_F²/2M term was "missing", not "removed"; E_avail used m_p = 938.272 where `GetEAvailableTrue` uses 938.27; the cost model silently excluded one bin. | **Fixed.** The wording is corrected. `analyze_dump.py` now uses 938.27; the rerun changes E_avail by under 0.01 MeV and no quoted bin fraction moves at the quoted precision. The bin exclusion is removed, with no numeric effect. |

**The reviewer could not verify** that no NuWro run happened outside the ledger, the build CPU, the
hardware, or the source of the target-composition percentages. The last comes from Ruterbories et al.,
quoted from the memo, and was not re-checked here. Whether the GENIE 1.099×10⁻³⁹ value includes
MINERvA's enhancement was resolved by the owner: the launcher is plain `gevgen Default+CCMEC`, so it
does not.

## Later bounded repair (2026-10-11)

Joseph named two further defects in the reviewed head `d75987e1`:
- the integrator chose the VA-interference sign from the data;
- the launcher's `ulimit -t` was not an aggregate CPU cap.

A separate allowance of 300 CPU-s with zero production compute covered the repair. It had one fresh,
read-only, targeted reviewer on `fedcc918` and one correction pass.

**Reviewer verdict:**
- no blocker;
- the convention is fixed and correctly derived;
- the launcher meets the requirement, with its residual stated correctly;
- INCONCLUSIVE unchanged.

**Findings:** one MAJOR (a stale "B2 is QUALIFIED" in REPORT §9) and eleven MINOR or NIT findings. All
were fixed or documented.

The plan, the results, the full disposition table, the remaining issues and the CPU accounting are in
[`REPAIR.md`](REPAIR.md) §R1–R4.

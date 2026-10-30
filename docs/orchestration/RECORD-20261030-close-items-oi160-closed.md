# RECORD — OI-160 closed for `C_stat` and `C_ML`, and retired (2026-10-30)

**By** the close-items session, OI-160's owner, on the director's order of 2026-10-30, given after #526 merged.
Measured at `origin/main` `ebd579e2c`.

**Under:**
- Joseph's decision [`DECISION-20261029-joseph-oi160-close-cml-and-5b-session.md`](DECISION-20261029-joseph-oi160-close-cml-and-5b-session.md)
  (#515): item 1, *"OI-160 closes for `C_stat`"*, and item 2, *"`C_ML` is checked the same way"*.
- The `C_stat` tolerance run, [`state/oi160-tolerance-20261029/REPORT.md`](state/oi160-tolerance-20261029/REPORT.md)
  (#506): CORRECTED for all three July producers.
- The `C_ML` tolerance run, [`state/oi160-cml-tolerance-20261029/REPORT.md`](state/oi160-cml-tolerance-20261029/REPORT.md)
  (#526): CORRECTED for the one split-replica producer, `55849763`.

**Changes nothing in** `C_ML`, `C_stat`, the trunk, a receipt or a published value.

## OI-160 — retired, closed for C_stat and C_ML

**The row's headline** was that the top-level 5D replica sets are pre-correction-contract. The director ruled on
2026-10-28 that this was a provenance question
([`QUESTION-20261028-trunk-stat-ml-replica-provenance.md`](QUESTION-20261028-trunk-stat-ml-replica-provenance.md)), and
Joseph had it settled by reproduction. Both halves of the covariance now have a reading under a pre-declared tolerance
run, and both refute the headline for the graded seeds:

- **`C_stat`:** the 100 bootstrap replicas' three producers read CORRECTED at seeds 2, 3, 6, 40 and 85 (#506). Joseph
  closed it for `C_stat` (#515, item 1).
- **`C_ML`:** the 24 split replicas' one producer reads CORRECTED at seeds 4, 9, 14, 19 and 24 (#526). This is the check
  #515's item 2 ordered. Its §3.3 meaning, fixed in advance: *"the 24 replicas behind `C_ML` rest on the corrected
  contract, within §4's limits, as `C_stat`'s do."*

**The terminal criterion** was *"measure: the C_ML tolerance run's readout is committed and reported to Joseph"*. The
readout is committed in #526. Reporting it to Joseph is the director's step (BINDING §3.3, *"The director takes it to
Joseph"*); this record does not attest it.

**Limits carried over from both reports:** ungraded seeds are covered by inference from their producer's verdict only;
a reproduction shows which code ran, not that it was correct.

**Two parts of the row are not settled by these runs.** They are not decided here, and are carried to the director as
backlog candidates on 2026-10-30:
- **The next action, classifying two launchers.** The row asked that `nd-unfolding/run_budget_5d.sh` and
  `nd-unfolding/sbatch_combine_5d_budget.sh` be classified as superseded pre-M(ii) launchers, or stated live. The runs
  answer which contract the replicas they glob were written under, not whether the launchers are superseded. No
  launcher is classified here.
- **The second finding in the row's detail cell.** It concerns
  `state/RECEIPT-20260822-quarantine-member-k000000-stale-replicas.json:49`. That receipt says *"Both anchored
  patterns"* require a literal `boot_nd_5d` component, and the row found at least two more (`run_budget_5d.sh:15`,
  `sbatch_combine_5d_budget.sh:16`). The row judged the quarantine's conclusion unaffected. The receipt is unchanged.

Neither is tracked by another register row or KNOWN_ISSUES entry. The QUESTION and
`PACKET-20260910-z-endpoint-A-acceptance-and-cause3-corr-amendment.md:445` name the launchers, but track nothing. Search: `git grep -n -E
"run_budget_5d\.sh|sbatch_combine_5d_budget\.sh"` over `docs/OPEN_ITEMS.md`, `KNOWN_ISSUES.md` and `work-items.tsv`,
and `git grep -n "Both anchored patterns"` over the tree, @ `ebd579e2c`: the only hits are OI-160's row and the
receipt itself.

## The run directories

All three OI-160 run directories on pscratch are removed:
- the reproduction's and the `C_stat` run's on 2026-10-29
  (`state/oi160-tolerance-20261029/run/logs/removal-session.txt`);
- the `C_ML` run's, `/pscratch/sd/j/josephrb/oi160-cml-20261029`, at 2026-10-30T08:02:36Z, after all 47 non-empty
  `out/` and `logs/` files were found byte-identical to main
  (`state/oi160-cml-tolerance-20261029/run/logs/removal-session.txt`).

## Dependency check

Search: `git grep -P "OI-160(?![0-9])"` over `KNOWN_ISSUES.md`, `docs/known-issues/`, the DECISION, RULING,
AUTHORIZATION and OPERATIVE records, `docs/publication/`, `docs/analysis-note/` and `measurement-paper/` @ `ebd579e2c`.

**Result:** no gate waits on OI-160 being open.
- **DECISION records:** the only hits are Joseph's three OI-160 decisions of 2026-10-29, which this retirement carries out.
- **RULING records:** the one hit, `RULING-20260902-quoted-column-permanence-is-p-scoped.md:601`, lists the id among
  those in use.
- **The other groups** have no hits.

**Across the whole tree,** the other hits are:
- the register (`OPEN_ITEMS.md`, `work-items.tsv`), its derived views, `LIVE-STATE.md` and `CATALOG.md`;
- OI-160's own declarations, bindings, reports, question and read-only record;
- historical mentions in `VALIDATION_LEDGER.md:1056`, two FINDINGs, a PACKET, a REVIEW, an agy verdict and
  `CATALOG-ARCHIVE-scalar5d.md`;
- `FD-CT-5B-DECLARATION.md:302`, which cites the `C_stat` run's floor value from #506's report, not the item.

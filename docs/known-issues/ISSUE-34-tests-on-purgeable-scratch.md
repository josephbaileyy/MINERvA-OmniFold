## 25 tests ran only from purgeable scratch, and one still does

Found 2026-08-07 while working plan Step 4. The cluster suite collected **764** tests against the local
tree's 710, and part of that gap was not path-dependent skips: **two test files existed only on
`/pscratch`, in neither tree's git**.

- `nd-unfolding/tests/test_uq_remediation.py` — **20 tests**, including the cluster suite's single
  remaining failure. Now **tracked** (and its fixture fixed, below).
- `nd-unfolding/tests/test_cstat_100rep.py` — **5 tests**, **still untracked**, because it imports
  `combine_cstat_bkgsub_100rep`, and **that module is untracked too**. Committing the test alone would
  guarantee a *collection error* (`ModuleNotFoundError` interrupts the whole run), which is strictly worse
  than a failing test. Committing both would import unreviewed code into the tracked tree. Left for a
  decision rather than resolved unilaterally.

Why this matters beyond tidiness: 25 tests enforcing campaign invariants were one `/pscratch` purge from
vanishing, and nothing in git referenced them, so a fresh clone silently ran 25 fewer checks than the
cluster did. This is the same failure that cost 38 unified throws and left two production launchers
untracked until 2026-08-06 — a purgeable filesystem holding load-bearing artifacts nothing else records.
**When local and cluster collection counts disagree, resolve the difference to specific files before
assuming it is environmental.**


# The four paper protection edits: report (2026-10-28)

**Lane:** paper rewrite, for the director.

**Under:**
- `DECISION-20261028-joseph-protections-remade-and-r21.md`, items 1–4;
- the director's rulings of 2026-10-28 on the proposals (item 1 as proposed; the rule for homes in items 3 and 4;
  option (b) for item 2).

**Base:** main `b554de56`. The branch is `paper/protections-remade-20261028`.

**Records** (this directory):
- `apply_p.py`: every edit, by item;
- `ledger.md`, checked by `check_ledger.py`;
- `agy/`: three reads, `run1` to `run3`.

These edits are unscored and truth-checked. They are the base of the r21 round.

## What changed

**Item 1, the low-stability cells.**
- One sentence is added to §VI Limitations: "Four of the sixteen cells, R02, R06, R10 and R15, have a stability of
  0.16–0.25: of the simulated signal events generated in such a cell and reconstructed, only that fraction is
  reconstructed in the same cell."
- The numbers are `\fvval` keys that `make_values_fived16.py` generates from the pinned H2 definition (sha256
  `b6790761…`).
- The generator asserts that the decided cells are the four lowest-stability cells and that the range prints as
  decided. Its self-test refuses a fifth cell below them.
- The sentence defines "stability", because the paper's "Estimator stability" subsection uses the word for rounding
  instability.

**Item 2, Data Availability: ruling (b).**
- The CC0 and input-file sentences are unchanged, and `\pubhold` is untouched.
- The package sentences now say only what the package regenerates: the note's null-distribution figure and the
  (Eavail,W) map.
- Removed:
  - "and the numbers quoted in Sec.~\ref{sec:central}", which is FALSE as read, because that section quotes no
    numbers;
  - "except the multiplier scan", which is stale, because the paper quotes no multiplier scan;
  - "It recomputes every $p$ value … of the joint tests", which is stale for the paper, because the joint tests are
    reported only through the note. The release appendix prints it.
- The reproducibility sentence stays, as "The paper's quoted numbers and the event-level processing require …",
  because that limitation is one a reader of the statement needs (agy).
- B7's Supplemental Material sentence is not applied. No machine-readable files exist, and Q8 is with Joseph.
- The pair is pinned in `check_ledger.DA_PINS`.

**Items 3 and 4, duplicate limitations and the Scope wording.** The rule: the body home keeps the evidence, §VI is the
one numbered home, §I keeps "Interval coverage has not been validated.", and the abstract is untouched.
- **§I (:23):** its fake-data, E1 (F1) and flux copies are dropped, along with "The result has three limitations".
  It now reads "Interval coverage has not been validated. The bias tests, the fake-data study and the dependence of
  the generator χ² on the flux correlations are given with the result (Secs. IV H and V B)."
- **Scope (:27):** it keeps its positive scope and adds "The limitations are listed in Sec. VI." Its coverage and
  joint-test copies are §VI's.
- **The two caveats that printed only in Scope move to §VI,** so that no fact leaves the paper: the tests "are not
  physical exclusions of the generators" and show "no evidence of additional discrimination beyond matched coarse
  projections".
- **sec:gen16 (:312):** its fake-data copy is dropped. The home is sec:fd16.
- **sec:departure (:188):** the C_model label clause is dropped and its pointer to sec:fd16 is kept. The home is
  sec:cov16.
<!-- absence-ok: quotes the printed limitation sentences the edits keep or move; not a claim that a result does not exist -->

Every dropped sentence has a P:: or MP:: probe at its kept home: 16 ledger rows, 28 probes, 0 failures.

## agy

The pairs are built by `agy/make_pairs.py`: five pairs, each with the home text as its CONTEXT. The control caught 5 of
5 in each read.
- **run1:**
  - §I, Scope and the body pairs are SAME.
  - Limitations is DIFFERS, because the CONTEXT lacked item 1's decision, so the added sentence looked unsupported.
  - DA is DIFFERS in both runs, and rightly: the first draft dropped the reproducibility limitation and narrowed
    "each part of the release" to the package. Both are restored.
- **run2:** with the decision's text in the CONTEXT, Limitations is SAME. DA is DIFFERS in both runs: "The other
  quoted numbers" had lost its antecedent. It now reads "The paper's quoted numbers".
- **run3:**
  - run 1 is SAME on all five;
  - run 2 is SAME on four. On DA, its only reason is the director-ruled narrowing itself: "drops … recomputes every
    p value … of the joint tests". The paper does not print those numbers, and the release appendix does. It stands.

## Checks

- `check_ledger.py .`: 16 rows, 28 probes, 13 changed base sentences, 0 failures.
- `--self-test`: PASS. It plants a missing probe, an abstract edit, an edit inside a `\pubhold`, an undeclared DA
  edit, an unpinned DA pair, the dropped kept-coverage sentence and a hand-typed numeral, and catches each. A pinned
  pair stays silent.
- The `\pubhold` check compares the holds themselves, not whole lines, because the DA sentence shares a source line
  with its hold.
- `apply_p.py 1|2|34 --check`: all verified.
- `make_values_fived16.py --self-test` and `--check`: PASS.
- `reflow_tex.py --note --check`: PASS.
- `build_all.sh`: rc 0; paper 11 pp, note 126 pp; no undefined reference; SEC4 15/15.
- The CI record-check steps: `fived16/HANDOFF.md` §5a, run before the push.

# EVW5D follow-ups (non-blocking under the director's scope rule)

The director, 2026-11-25: r3 is the last full round; after it, only findings that could change the published
weights, constants or gates block, and the rest are listed here. None of these changes a published number or what a
gate accepts on the run as bound.

| # | source | item | why it does not block |
|---|---|---|---|
| 1 | codex-school r3 #7 | No injected-fault test of C-PINS after the run or of C-KEY's early exit in `run()`; no capture test with distinct ordered pushes that would detect a permutation | Disclosed in the declaration §5 and accepted by the director. C-KEY's predicate is unit-tested per field; the push order is the pinned driver's, and C-GRID's bit-for-bit re-histogram fails on a reorder that changes any cell sum's rounding |
| 2 | codex-school r3 #8 | A strict 0.5 node-h ceiling also depends on NERSC's overtime and termination settings, which the scripts do not read | The request is one regular node for 30:00 with `--no-requeue`; the ESS run of the same unfold took 794 s. The post records the charge from sacct |
| 3 | declaration §5 | The connect, post and HPSS scripts are not run end to end locally (they need iris, Slurm, network git and hsi/htar); the post's exact-allowlist check has no local test | Their checks were read three times; the launcher, the job script and `accepted()`, which carry the gates, are tested <!-- absence-ok: a statement about this lane's own suite and scripts (nd-unfolding/evw5d, launch/), not a claim about the repository --> |
| 4 | claude-personal Sonnet r2 #10 | If the job's canonical-path check ever refused, it would refuse without a DONE marker | The connect now makes the same check before submitting (revision 4), so the job's check can only repeat a passed one |
| 5 | codex-school r1 #5, Sonnet r2 #6 | Rebinning that splits fine cells needs an event-level denominator and the sub-bin flux; neither is stored | Stated in §4. Under the director's completeness ruling, the lane prices the event-level denominator if C-COMPLETE does not find c = 1 to 1e-5, and builds nothing |
| 6 | revision 4 | The physical ids (run, subrun, gate) of the rows are not stored | Ruled out of this item by the director, as in 2D |
| 7 | claude-personal Sonnet r3 (rev 5, GO) #1 | `accepted()` can raise, not return False, on a malformed or NaN-bearing `run.json` | It fails closed: the checker exits non-zero, so HPSS bails and the fetch reports a non-zero rc |
| 8 | Sonnet r3 #2, #6 | The production sub-conditions of `accepted()` and some check lines (`weights_float64`, `meta_n_rows`, `meta_columns`, per-item `vs_in`, C-GRID's sub-predicates) have no one-at-a-time mutant | The whole production block is mutated and killed; the per-item lines are redundant with bit-for-bit comparisons that are tested; the writer refuses wrong pins before it runs |
| 9 | Sonnet r3 #4 | `test_launcher_fetch_products_runs_accepted` needs `test_fail_on_f` to run first (it asserts so) | The mutation harness and the receipts run the whole suite in file order |
| 10 | Sonnet r3 #5 | The checker runs as `python3 -B -c`, so the working directory precedes the standard library on `sys.path` | The checker's working directories are the lane's own (`$P`, the private retrieval directory holding only archived products, and the Mac fetch directory); `-I` is a one-flag change for a later revision |
| 11 | Sonnet r3 #7 | `constants.json` carries no axis units or R00–R15 labels | The map is saved, so the cells are reproducible; the units are GeV(/c) on every axis, as the note states |
| 12 | Sonnet r3 #5 (Q5) | §4 could note that the npz's own `measured_weights` (fine-binned) are replaced by the refinement output before the loop (`s5e_trace.py:441` @ abdc88c5) | It strengthens §4's claim; it changes nothing |


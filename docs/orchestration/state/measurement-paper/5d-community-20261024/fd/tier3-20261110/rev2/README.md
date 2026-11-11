# T3 rev 2: test and mutation receipts for the code (2026-11-10)

**By** session tier3-design, under [`T3-PIPELINE-TESTS-DECLARATION.md`](../T3-PIPELINE-TESTS-DECLARATION.md) rev 2
(sha256 `fb5995098eb9df06686d1924fee2a42cb21de553cc7971f260ec69b7b73d1d0e`, at the code commit), §13.2.
The declaration is a DRAFT. It goes to coverage-5b-audit for audit, then to the director for binding.

**Code commit:** `6eb5627e0a70335ceea28a15f0b6cad8b822ec87`. Both logs were made in a clean clone checked out at that
commit with no modified tracked files, by one serial process under `nice -n 19` with every BLAS and OpenMP thread cap
at 1. Each log's header carries the clone's HEAD and the sha256 of the six files under `nd-unfolding/tier3/`, which
equal the digests in the declaration's §13.1.

| file | command | result | sha256 |
|---|---|---|---|
| [`tests.txt`](tests.txt) | `python3 -B -m unittest -v nd-unfolding/tier3/test_t3p.py` | 62 tests, OK, none skipped | `b6edff257aa6c2614e01b9e71849b03ba4073ae3629f5b406d5f9bd4a3924c21` |
| [`mutation.txt`](mutation.txt) | `python3 -B nd-unfolding/tier3/t3p_mutation.py` | unmutated suite 62 OK; 59 of 59 mutants killed, each by its named test; `PASS` | `4a9d2673a8ee5f79c43ca43ac0fbfb6f4705c1f9a17e31b5527f3d196b995747` |

**Environment:** Python 3.12.2, numpy 1.26.4, Darwin arm64. LightGBM, ROOT, the real inputs and the cluster are not
used (§13.2 lists what this cannot test).

## MEASURES / CANNOT AUTHORIZE

- **MEASURES:** that the code at the commit above passes its own tests, and that each of the 59 planted defects is
  caught by the test named for it.
- **CANNOT AUTHORIZE:** any job, connect or submit (the jobs run only after the LL5D readout, on the director's go per
  connect); the binding; any reading of ρ.

## CITABLE FOR / NOT CITABLE FOR

- **Citable for:** the test and mutation outcomes of the code at `6eb5627e`.
- **Not citable for:** any result of the pipeline tests, any behaviour with LightGBM or the real inputs, or any
  later revision of the code.

# T3 rev 4: test and mutation receipts for the code (2026-11-10)

**By** session tier3-design, under [`T3-PIPELINE-TESTS-DECLARATION.md`](../T3-PIPELINE-TESTS-DECLARATION.md) rev 4
(sha256 `f96ed6f29a155e978bf449fdcb9810670202e0a3d74fb2f96afe48098b63cae1`, at the code commit), §13.2.
Rev 4 answers coverage-5b-audit's recheck of rev 3 (§16): tests and mutants only, and the reader, probe, arms and job
script are byte-identical to rev 3's. The declaration is a DRAFT. It goes back to coverage-5b-audit for the recheck,
then to the director for binding. The receipts for the superseded code at `6eb5627e` and `624f5416` stay in
[`../rev2/`](../rev2/README.md) and [`../rev3/`](../rev3/README.md).

**Code commit:** `ae0892add25c1fc9b074f4031a1aee91249aacf7`. Both logs were made in a clean clone checked out at that
commit with no modified tracked files, by one serial process under `nice -n 19` with every BLAS and OpenMP thread cap
at 1. Each log's header carries the clone's HEAD and the sha256 of the six files under `nd-unfolding/tier3/`, which
equal the digests in the declaration's §13.1.

| file | command | result | sha256 |
|---|---|---|---|
| [`tests.txt`](tests.txt) | `python3 -B -m unittest -v nd-unfolding/tier3/test_t3p.py` | 68 tests, OK, none skipped | `1c0772b6afba53ad652c8ccb7d261778fed37949adb26155853cf18d290950dd` |
| [`mutation.txt`](mutation.txt) | `python3 -B nd-unfolding/tier3/t3p_mutation.py` | unmutated suite 68 OK; 73 of 73 mutants killed, each by its named test; `PASS` | `ea826e5716082fbe865ea33348f6cabb8170a03e39c67bc151bb3cab0bebbcf7` |

**Environment:** Python 3.12.2, numpy 1.26.4, Darwin arm64. LightGBM, ROOT, the real inputs and the cluster are not
used (§13.2 lists what this cannot test).

## MEASURES / CANNOT AUTHORIZE

- **MEASURES:** that the code at the commit above passes its own tests, and that each of the 73 planted defects is
  caught by the test named for it.
- **CANNOT AUTHORIZE:** any job, connect or submit (the jobs run only after the LL5D readout, on the director's go per
  connect); the binding; any reading of ρ.

## CITABLE FOR / NOT CITABLE FOR

- **Citable for:** the test and mutation outcomes of the code at `ae0892ad`.
- **Not citable for:** any result of the pipeline tests, any behaviour with LightGBM or the real inputs, or any
  later revision of the code.

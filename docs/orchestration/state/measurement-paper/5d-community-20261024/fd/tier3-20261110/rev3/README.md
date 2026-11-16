# T3 rev 3: test and mutation receipts for the code (2026-11-10)

**By** session tier3-design, under [`T3-PIPELINE-TESTS-DECLARATION.md`](../T3-PIPELINE-TESTS-DECLARATION.md) rev 3
(sha256 `4234c9eab9d272eaf440345e91981a5306fb83e5d9d7a4ba6364002757f4f212`, at the code commit), §13.2.
Rev 3 answers coverage-5b-audit's audit of rev 2 (§15). The declaration is a DRAFT. It goes back to coverage-5b-audit
for the recheck, then to the director for binding. Rev 2's receipts for the superseded code at `6eb5627e` stay in
[`../rev2/`](../rev2/README.md).

**Code commit:** `624f54161ef63c43c8653e66153e76cce4d53e3f`. Both logs were made in a clean clone checked out at that
commit with no modified tracked files, by one serial process under `nice -n 19` with every BLAS and OpenMP thread cap
at 1. Each log's header carries the clone's HEAD and the sha256 of the six files under `nd-unfolding/tier3/`, which
equal the digests in the declaration's §13.1.

| file | command | result | sha256 |
|---|---|---|---|
| [`tests.txt`](tests.txt) | `python3 -B -m unittest -v nd-unfolding/tier3/test_t3p.py` | 66 tests, OK, none skipped | `6649cae3d3f975414b783997380541d5222207f22ebc7fa83fb466feb099217f` |
| [`mutation.txt`](mutation.txt) | `python3 -B nd-unfolding/tier3/t3p_mutation.py` | unmutated suite 66 OK; 66 of 66 mutants killed, each by its named test; `PASS` | `ea46e45ef9d9386a6917d791649c20e61d6e4e20eb2f309fc37a81e45854f986` |

**Environment:** Python 3.12.2, numpy 1.26.4, Darwin arm64. LightGBM, ROOT, the real inputs and the cluster are not
used (§13.2 lists what this cannot test).

## MEASURES / CANNOT AUTHORIZE

- **MEASURES:** that the code at the commit above passes its own tests, and that each of the 66 planted defects is
  caught by the test named for it.
- **CANNOT AUTHORIZE:** any job, connect or submit (the jobs run only after the LL5D readout, on the director's go per
  connect); the binding; any reading of ρ.

## CITABLE FOR / NOT CITABLE FOR

- **Citable for:** the test and mutation outcomes of the code at `624f5416`.
- **Not citable for:** any result of the pipeline tests, any behaviour with LightGBM or the real inputs, or any
  later revision of the code.

# T3 addendum V1: test and mutation receipts (2026-11-11)

**By** session tier3-design, under [`T3-ADDENDUM-V1.md`](../T3-ADDENDUM-V1.md) (sha256 `3998708a91dde4b01c3dcb1e87a7b7a45796de13da53880a0eb79a410ecc7986`), which adds
one test and one mutant to the code bound at M_T3 `14fb9e52`. The reader, probe, arms and job script are byte-identical
to M_T3. The addendum goes to coverage-5b-audit for a glance, then to the director, who notes it in the binding.

**Commit:** `b1c66821354ec748acd8ba57d39c427e19ba5604`. Both logs were made in a clean clone checked out at that
commit with no modified tracked files, by one serial process under `nice -n 19` with every BLAS and OpenMP thread cap
at 1. Each log's header carries the clone's HEAD and the sha256 of the six files under `nd-unfolding/tier3/`.

| file | command | result | sha256 |
|---|---|---|---|
| [`tests.txt`](tests.txt) | `python3 -B -m unittest -v nd-unfolding/tier3/test_t3p.py` | 69 tests, OK, none skipped | `16b1309f2c640c2c3d18370ccdb7b4e5f8db73fe72855afc36efb2fb6cf16496` |
| [`mutation.txt`](mutation.txt) | `python3 -B nd-unfolding/tier3/t3p_mutation.py` | unmutated suite 69 OK; 74 of 74 mutants killed, each by its named test (the new one: "v1: the bound includes equality"); `PASS` | `1e615fa96ae062e085811a6799baf1e797a048c409f5a290cd9984e651cb4d62` |

**Environment:** Python 3.12.2, numpy 1.26.4, Darwin arm64. LightGBM, ROOT, the real inputs and the cluster are not
used.

## MEASURES / CANNOT AUTHORIZE

- **MEASURES:** that the code at the commit above passes its own tests, including the equality boundary of §5.2's
  bound, and that each of the 74 planted defects is caught by the test named for it.
- **CANNOT AUTHORIZE:** any job, connect or submit (binding 1, ruling 1); any reading of ρ.

## CITABLE FOR / NOT CITABLE FOR

- **Citable for:** the test and mutation outcomes of the code at `b1c66821`.
- **Not citable for:** any result of the pipeline tests, any behaviour with LightGBM or the real inputs, or any later
  revision of the code.

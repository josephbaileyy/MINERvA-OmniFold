# RDX launcher-tranche receipts (rev 5, 2026-11-12)

**What these are:** both RDX test suites and both mutation harnesses, at HEAD `789b3150` (RDX-DECLARATION.md rev 5,
§2b and §2c). They ran in a clean clone, serially, at nice 19, with every numeric thread pool set to 1. Each file's
header gives HEAD and the sha256 of every file under `nd-unfolding/rdx/`.

| file | result |
|---|---|
| `tests.txt` | 50 tests (`test_rdx.py` 38, `test_rdx_stages.py` 12), OK |
| `mutation.txt` | 51 of 51 declared mutants killed by their named tests (C1–C4, with the vectorized walk's four) |
| `mutation_stages.txt` | 21 of 21 declared mutants killed by their named tests (the launcher tranche) |

The launchers' local smoke is in `../launch/smoke.txt`. No job was submitted and no connect was made.

## CITABLE FOR / NOT CITABLE FOR

- **Citable for:** what the tests, mutants and smoke check at this HEAD.
- **Not citable for:** any RDX reading, or any run on the cluster.

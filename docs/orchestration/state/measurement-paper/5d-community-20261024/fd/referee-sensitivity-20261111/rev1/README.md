# RSN rev 1 receipts (2026-11-11)

**What these are.** The tests and the mutation check of `RSN-DECLARATION.md` at code commit `33c0548f`, run in a clean
clone, serially, at nice 19 with every numeric thread pool set to 1. Each file's header gives HEAD and the sha256 of the
nine RSN files; they equal the declaration's §7 table.

| file | result |
|---|---|
| `tests.txt` | 41 tests, OK |
| `mutation.txt` | the unmutated suite passes with 41 tests; 70 of 70 declared mutants killed, each by its named test |

The 37 CI-equivalent checks passed in a second clean clone at the same commit (base `8f99b7ff`).

No job was submitted and no connect was made.

## CITABLE FOR / NOT CITABLE FOR

- **Citable for:** what the tests and mutants check at `33c0548f`.
- **Not citable for:** any result of the analyses, or code at any other commit.

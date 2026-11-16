# RSN rev 2 receipts (2026-11-11)

**What these are.** The tests and the mutation check of `RSN-DECLARATION.md` rev 2 at code commit `150fc566`, run in a
clean clone, serially, at nice 19 with every numeric thread pool set to 1. Each file's header gives HEAD and the sha256
of the nine RSN files; they equal the declaration's §7 table.

| file | result |
|---|---|
| `tests.txt` | 50 tests, OK |
| `mutation.txt` | the unmutated suite passes with 50 tests; 101 of 101 declared mutants killed, each by its named test |

The 37 CI-equivalent checks passed in a second clean clone at the same commit (base `8f99b7ff`). Rev 1's receipts, at
`33c0548f`, stay in `../rev1/`.

No job was submitted and no connect was made.

## CITABLE FOR / NOT CITABLE FOR

- **Citable for:** what the tests and mutants check at `150fc566`.
- **Not citable for:** any result of the analyses, or code at any other commit.

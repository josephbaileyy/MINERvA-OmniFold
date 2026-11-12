# RDX code receipts (rev 4, 2026-11-12)

**What these are:** the tests and the mutation check of RDX-DECLARATION.md rev 4's code (§2b) at code commit
`5aac45a1`. They ran in a clean clone, serially, at nice 19, with every numeric thread pool set to 1. Each file's
header gives HEAD and the sha256 of the ten RDX files, which equal §2b's table.

| file | result |
|---|---|
| `tests.txt` | 34 tests, OK |
| `mutation.txt` | the unmutated suite passes with 34 tests; 47 of 47 declared mutants killed, each by its named test |

No job was submitted and no connect was made.

## CITABLE FOR / NOT CITABLE FOR

- **Citable for:** what the tests and mutants check at the code of §2b.
- **Not citable for:** any RDX reading, or code at any other commit.

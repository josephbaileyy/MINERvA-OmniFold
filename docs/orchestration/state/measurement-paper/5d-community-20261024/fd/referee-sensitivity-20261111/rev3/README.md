# RSN rev 3 receipts (2026-11-12)

**What these are.** The tests and the mutation check of `RSN-DECLARATION.md` rev 3 at code commit `0336ba64`, run in a
clean clone, serially, at nice 19 with every numeric thread pool set to 1. Each file's header gives HEAD and the sha256
of the nine RSN files; they equal the declaration's §7 table.

| file | result |
|---|---|
| `tests.txt` | 52 tests, OK |
| `mutation.txt` | the unmutated suite passes with 52 tests; 109 of 109 declared mutants killed, each by its named test |

The 37 CI-equivalent checks passed in a second clean clone at the same commit (base `8f99b7ff`). Rev 1's receipts, at
`33c0548f`, and rev 2's, at `150fc566`, stay in `../rev1/` and `../rev2/`.

No job was submitted and no connect was made for RSN. (The same session's HPSS archive kit, a separate item, ran one
stat-only probe on dtn01 at the director's go; it read no RSN input and is recorded in `../hpss/README.md`.)

## CITABLE FOR / NOT CITABLE FOR

- **Citable for:** what the tests and mutants check at `0336ba64`.
- **Not citable for:** any result of the analyses, or code at any other commit.

# V-HALF: the read (receipt)

The valid-region lane ran this on 2026-11-09, on the director's go, under V-HALF BINDING 1 ruling 2 and addendum R1. It
ran locally at 0 node-h, from a fresh clone of main at 13d714bfc10c941f8608e342414cdf29c6f31b5d. R1's merge 28a59eed is
an ancestor of that commit. The clone showed 0 porcelain --ignored lines before and after. `v_half.py` (8a1cdbe7…, as
bound) ran once: `python3 -B v_half.py read --repo <clone> --out <new dir>`, exit 0, "readings written".

**No class is quoted in this receipt.** Each cell's class, with its inputs and the print-only sections, is in
`readout.json` and `readout.txt`. By ruling 2 the report goes to the director, and then to Joseph.

- **readout.json** sha256 e74233901038bd71496a8859aaf76997e253fad9a8bd0ebda9f183453723492e, 80,756 bytes.
- **readout.txt** sha256 d1b91a42b217089fbacc1f24499a107e895f75f56852d02643ba216b017ccff7, 3,291 bytes.

**The regenerated index files.** `RESULTS-INDEX.tsv`, `RESULTS-POPULATION.tsv` and `records_results_index.tex` are as
`tools/registry/results_index.py --write` generated them, because readout.json joins the results population (28 metric
rows). Their new rows are generated, UNATTRIBUTED machine listings of committed values. They are not paper or note
text, and they carry no class. This is the director's ruling (a) for the PRR read (2026-11-09), applied to the same
shape. `records_estimators.tex` was unchanged.

CITABLE FOR: that the V-HALF read ran as bound on the named inputs; its two outputs' sha256 and bytes.
NOT CITABLE FOR: any class or wording before the director's report to Joseph. After that, only what the readout's own
LICENCE (DECLARATION.md §10) allows.
<!-- absence-ok: a scoping statement of what this receipt quotes, under V-HALF BINDING 1 ruling 2 -->

## The run (`read.log.txt`, from `run.sh`)

- **The clone.** A fresh `git clone` of the public repository, checked out at 13d714bf with 28a59eed an ancestor. It
  showed 0 porcelain --ignored lines before and after.
- **The environment.** One serial process under nice -n 19, with every BLAS/OpenMP thread cap at 1,
  PYTHONHASHSEED=0 and no bytecode. Python 3.12.2, numpy 1.26.4.
- **The bound bytes in the clone** (BINDING 1's table and addendum R1). Each sha256 is the bound one:
  - DECLARATION.md 594851a2…, v_half.py 8a1cdbe7…, test_v_half.py d2d28b9f…, mutate_v_half.py 09a10bc7…,
    mutants.txt 36696b39…, INPUTS.sha256 7ee79713…;
  - h2_definition.json b6790761… (ruling 4's pin, re-checked by R1);
  - PRR-READOUT.sha256 0ff14ff6…, naming H2 = `fd/receipts-prr/read/cluster/readout.json` at 9238f22b… (R1).
    The file hashes to that value;
  - H1 = `fd/with-cpl/readout/fd_f0b_readout.json` at 5f542830…, INPUTS.sha256's line.
- **The read** exited 0, and each of its eight declared controls prints PASS (`readout.txt`, lines 2-9). Its outputs
  are the two files above and nothing else.
- **The binding inventory.** readout.json's `"inputs"` carry H1 and H2 as {path, sha256}. These are two new receipt
  bindings, both true pins.
  - Following the director's ruling (as in PR #1008), `verify_hash_bindings.py`'s RECEIPT_BINDING_COUNT moves from 167
    to 169, and its digest from 18818a17 to a9f3a844.
  - The delta and the power test (each pin flipped, MISMATCH, restored and cmp-verified) are in `binding-delta.txt`.
    Their outputs are in `lane/`.
- **The rerun at the head.** The rerun is from a fresh clone at this receipt's commit 35577ba6. That commit adds only
  this directory, the four index files, the binding constants, the CATALOG and overrides rows and MANIFEST.tsv. The rerun
  had empty porcelain before and after, and its outputs are byte-identical to the first read: readout.json e7423390… and
  readout.txt d1b91a42… (`rerun-at-head.txt`).

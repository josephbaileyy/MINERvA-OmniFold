# PILOT-FB copy connect (PILOT-FB-BINDING-1 addendum C1, ruling 3 step 3) (receipt)

**Status: written and tested, not run.** It runs only after the smoke, on its own audit and the director's go for these
exact shas, after every fenced lane has acked (C1 ruling 3 step 1). Nothing has been copied.
<!-- absence-ok: an operational status of this connect, not a claim that a result does not exist -->

## What it copies

Into the stage the login-node smoke created, `/pscratch/sd/j/josephrb/pfb-20261117-stage`:
- `a0-refs/<name>`: RS1's 21 A0 products, the base `rs1_A0_b-_j-.npz` and jitters 1–20. They come from
  `/pscratch/sd/j/josephrb/rs1-a1-20261107/runs/A0/`, each at its pin in RS1's committed `runs-SHA256SUMS`
  (`receipts/full-a1/read/`). RS1's `rs1_A0_b-_j0.npz` is not needed and is not copied.
- `assess_receipt.json`: the σ receipt, from `<deploy>/docs/orchestration/state/s5e/cand/assess_receipt.json`, at
  `rounding_mechanism_analyze.SIGMA_RECEIPT_SHA256` (`84266e30…`).

These are the 22 files G4 and the job's stage-check require. Nothing else is written.

## The code (commit 8e2e3a1e)

| file | sha256 |
|---|---|
| `nd-unfolding/pfb_copy_remote.py` | `2f5e8c79ba4d2154f0807f8b7e63933ae2427705b403fd4b783fdc13f1413570` |
| `nd-unfolding/pfb_copy_launch.sh` | `06702d4b725a1ca993d2a39273cabbacfa82f4b5b8096ec7ae4c777a3867cb9c` |
| `nd-unfolding/tests/test_pfb_copy.py` | `a158a77e64c1d7b7e567a452dd37d776cad5e30ba096ddc0ffbb45503372de7b` |

The launcher pins the remote script's sha256 and refuses (exit 8) if the local copy differs.

## The command (after the go)

```bash
bash nd-unfolding/pfb_copy_launch.sh <new empty dir> <loginNN> <deploy>
```

`<deploy>` is the same clean checkout the smoke used, an absolute `/pscratch/sd/j/josephrb/...` path. The launcher
sends the local `pfb_copy_remote.py` over ssh's stdin to `/usr/bin/python3 - <deploy>` on the login node, through saul.
The manifest comes back on stdout as `<dir>/copy-manifest.json`, and ssh's exit status is read unpiped. The laptop
then runs `pfb_copy_remote.py verify`.

## The holds

- **No job, and no sbatch, srun or salloc.**
- **Writes only `a0-refs/` (21 files) and `assess_receipt.json` in the stage, and nothing on CFS.** The inner ssh
  writes nothing on saul: no control socket, no known_hosts entry, no host-key update.
- **The stage must be the smoke's.** It must be the declared path, an existing real directory at its own physical
  path, holding `smoke-receipt.json` as a plain file of its own, and holding no `a0-refs/` or `assess_receipt.json`
  yet. Otherwise exit 2, before any write.
- **O_NOATIME and O_NOFOLLOW on every source read.** A missing source, a symlinked source or a non-regular one exits 5.
  A source off its pin exits 4, and one whose stat moved during its read exits 8. All 22 are read and checked before
  the first write.
- **Plain new files.** `a0-refs/` and each copy are created `O_CREAT|O_EXCL|O_NOFOLLOW`. Each copy is then checked: a
  plain file with one link, an inode that is not its source's, physically at its own path in the stage, at its pin.
  Any failure exits 6, a STOP, and the copies stay for the director. These are the same conditions the analysis's G4
  applies (`stage_copy_problem`); the tests check that it accepts each copy.
- **The fence is sacct only, read twice.** It is a 14-day read with each State classified against the closed terminal
  set. A fenced-family job in any other state, or a malformed row, exits 9.
- **verify on the laptop refuses (exit 2)** unless all of these hold:
  - the manifest names the declared stage and source directory;
  - it holds exactly the 22 names, each at its pin;
  - O_NOATIME was used, and no source's stat moved;
  - every copy has a new inode and one link;
  - both fence reads were clear.
- Any STOP, failure or timeout goes to the director unrepaired. Nothing is re-run.

## Receipt

- `tests.txt`: the 9 tests in a clean clone at 8e2e3a1e, exit 0. They run the copy locally against a scratch root
  with a stub sacct and test pins (`PFB_COPY_TEST_ROOT`; verify refuses a manifest from that mode, because its stage
  is not the declared one). The cases:
  - a clean copy: 22 plain files with new inodes and one link, sources' atime unchanged, the analysis accepting each
    copy, and nothing else written;
  - each stage refusal;
  - a source off its pin, a symlinked source, and a missing source, each refused with nothing written;
  - the fence in both directions;
  - a source moved during its read;
  - the pins equal RS1's committed sums and the analyzer's σ pin and paths;
  - Python 3.6 grammar, and no job command;
  - every verify refusal;
  - the launcher's sha pin, argument checks and inner ssh options.
- **Not covered here:** the tests run under the laptop's Python 3.12. The 3.6 check is a grammar parse. O_NOATIME's
  real open is exercised only on the login node.

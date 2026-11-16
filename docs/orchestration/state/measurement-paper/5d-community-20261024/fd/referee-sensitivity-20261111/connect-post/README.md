# RSN post-run connect (2026-11-12), for the director's go

**By** session tier3-design, under RSN-DECLARATION.md rev 3 §6 step 5: after J2 and J3, on a login node, run
`rsn_cmodel.py build`, `rsn_regrade.py` and `rsn_read.py`. It runs from the M_P1 deploy (`rsn-20261112/deploy-p1`) at
0 node-h.
**It has not run.** It runs only on the director's go for these sha256s, after J2 (61170759) and J3 (61170761) have
ended.
<!-- absence-ok: an operational status of this connect's own run, not a claim that a result does not exist -->

| file | sha256 | role |
|---|---|---|
| `rsn_connect_post.sh` | `9a16608a7fcb890d7ff58e6805d6bf8ea0d79f89571618b25d3e46c826222820` | the connect script |
| `rsn_connect_post_launch.sh` | `f03c18cd6b3dcd1a171a9e945c3b5fb21bf89f27cc6382a9dbdffe474e2f2180` | the Mac-side launcher: J1's (`819be111`), with only the script name, its sha and the /dev/shm file name changed |
| `smoke_connect_post.sh` | `91c090a53f9bc54621a5ff062b90616abe0c6a97c96299322dea2aa9e00e3a2d` | the local smoke harness |
| `smoke.txt`, `smoke-pass-readlog.txt` | — | the smoke run at these bytes (14 cases), and the pass case's full read log |

Usage: `bash rsn_connect_post_launch.sh <new empty dir> <loginNN>`.

## The read set (the director's ruling of 2026-11-12)

E96D's runs atime-check `of_inputs_5d.npz` and the s5c p2 `bkg_dump.npz`, and they may be running when this connect
runs. **The three tools read only:**
- the deploy at M_P1: the code, and the committed records it reads by repository path, P5 among them;
- RSN's own files under `rsn-20261112/out`:
  - `products/` (J1–J3), `prep/` and `nc.json`;
  - `cmodel/`, which step 2 writes;
  - `stage/`, the four NC-R inputs connect 1 copied there by O_NOATIME. These are `fd_f1_experiments.npz`,
    `s1_assembly.npz`, `cpl_block.npz` and the NuE constraint file, each re-checked against its pin before use;
- pv-ladder's frozen products, `pv-ladder-20261024/products`: `rsn_cmodel.py build`'s frozen shifts. They are not an
  E96D input, an LL5D input or a cov2d-protected path;
- the python environment.

**It reads neither E96D input,** and the connect enforces this as well as stating it:
- **The guard.** Each tool runs under `guard.py`, a `sys.addaudithook` wrapper written by the connect. On every
  `open` event, before the file is opened, it raises PermissionError for any path equal to or under a DENY entry,
  compared after realpath. The tool then fails, and the step STOPs. The DENY entries are:
  - `of_inputs_5d.npz`;
  - the s5c p2 `bkg_dump.npz`;
  - the original NuE constraint file;
  - prologue5's eight `cov2d_protected_paths`.
<!-- absence-ok: an operational description of the guard's self-test target, not a claim that a result does not exist -->
- **A self-test** runs before the tools: an open of a name that does not exist under a denied root must be refused.
  A guard that failed to refuse would therefore touch no file.
- **A read log.** The guard records every path opened. The connect prints the log and STOPs if any opened path
  lies outside the read set above. The interpreter's own prefixes and `/usr`, `/proc`, `/sys`, `/dev` and `/etc`
  are counted but not listed.

The bound code is run unmodified, by `runpy` under the same interpreter flags (`-I -B`) that connect 1 used.

## What it does

1. **It refuses before writing anything if:**
   - the host is not loginNN, or a Slurm job is set;
   - an `rsn_` job is queued or running;
   - `sacct` does not show J2 as `rsn_J2` and J3 as `rsn_J3`, each COMPLETED 0:0;
   - a job log lacks its `rc=0` line, or a product's sha256 line, or a product on disk differs from that line
     (J2's eight products and J3's four);
   - `nc.json` records no rsn-nc/1 PASS;
   - the deploy is not clean at M_P1, or a bound file is not at its sha256;
   - a staged input is not at its pin;
   - an output exists already.
2. **`rsn_cmodel.py build`** writes `cmodel/rsn_cmodel.{json,npz}`.
3. **`rsn_regrade.py`** runs on the staged inputs and the arm file, and writes `regrade.json`.
4. **`rsn_read.py`** writes `rsn_readout.json`.
5. **Each output is printed** in full with its sha256 (the npz by sha256 only), then the read log, for the receipt.
   The deploy must still be clean at the end.

## The smoke (`smoke.txt`, 14 cases)

**The setup.** The deploy is a real clean clone at M_P1. The stub python runs the connect's own `guard.py` with the
real interpreter, but replaces each tool with a stand-in. The stand-in writes the tool's output and opens what the
real tool would open: a frozen product, P5, an RSN product, the staged inputs and the prior outputs. The real tools
need the cluster's data.

**The cases:**
- **pass:** the guard's self-test is refused as required, all three steps run, and the read set holds
  (`smoke-pass-readlog.txt`);
- **refusals that write nothing:**
  - an `rsn_` job running;
  - a dtn host, or a Slurm job set;
  - J3 TIMEOUT in sacct;
  - J2's rc line missing;
  - a product that differs from its logged sha;
  - no `nc.json`;
  - a dirty deploy;
  - a staged input that differs from its pin;
  - an output already there;
- **the guard:**
  - a build stand-in that opens `bkg_dump.npz`: refused before the open, so the step STOPs;
  - the same for the read stand-in;
  - a regrade stand-in that opens an undeclared path: the read log lists it as OUTSIDE, and the connect STOPs.

## CITABLE FOR / NOT CITABLE FOR

- **Citable for:** the post-run connect, its enforced read set and its local smoke behaviour.
- **Not citable for:** any reading. Nothing has run.

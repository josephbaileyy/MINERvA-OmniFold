# COV2D control (2a), the writer at the input. **CONTROL-2A FAIL**: (c)'s first STOP (2026-11-03)

**By** the `cov2d` session, under `COV2D-BINDING-1.md` (merged at `95e371700ec57546c459ba029a8e8a616d8ccdee`).
**MEASURES:** control (2a) of `COV2D-DECLARATION.md` §2 on `$CV`'s real data tree. **CANNOT AUTHORIZE:** (2b), the
pilot or any toy.

## The verdict, and what it stops

- **CONTROL-2A FAIL.** This is the bound control's own verdict: `cov2d_writer.main` printed `WRITER-CONTROL FAIL
  failures=1` and returned rc 3.
  - The content is equal: `compare_tree` found all three branches of `data` bitwise equal over 4,119,797 rows, and
    dataPOTUsed is equal.
  - The single failure is the control's exact-keys check (`cov2d_writer.py:105-107`): `FAILURE unexpected keys
    ['data;2', 'data;3']`.
- **It is (c)'s first STOP** (the director's ruling (a), 2026-11-03).
  - The clause is `COV2D-DECLARATION.md:358-359`, unchanged since `dec97852`: "**(iii) A second STOP ends (c)** unless
    Joseph rules otherwise. A STOP is any step this declaration or the amendment says stops the campaign."
  - The declaration says this step stops the campaign at §2 (`:89`): "**If (2a) or (2b) fails, (c) stops** and goes to
    the director".
  - The rule's source is `DECISION-20261102-joseph-1b-redesign.md:78` (#700, addition (iii)).
  - The director did not reclassify it because the content matched.
- **The next step (the director's ruling (b)):**
  - fix the writer, not the control, as BINDING-1 ADDENDUM A1: `t.SetAutoSave(0)`, with a test that forces the condition
    at fixture size and a mutant that drops the fix;
  - (2a) then reruns as a new connect, with its sha256 sent to the director first.

## How it ran: three processes (the director's ruling of 2026-11-03)

No cluster environment has PyROOT and uproot together (E1, E2 and E3's listings), and the bound `writer_control` needs
both. **The director ruled the three-process split "as a change to how control (2a) is run, not to what it compares,"**
with five conditions:
1. patch reach;
2. the digest chain;
3. npz exactness;
4. threads;
5. the usual clone, porcelain, blob and removal rules.

`control2a_split.py` (sha256 `841ff1f62822bed64a647d2a3e114dade92ce87c85f25a4492f137a4c98e424b`) is embedded verbatim
in `connect-2a.sh` (sha256 `b8c7656fd2ad6dd38587e6dc305377d13fb02cf59cba5fde6f9c9ddce849a765`), which was approved
before it ran. Both digests were checked on the node.

**Patch reach (condition 1): the full call path from `main(["control", ...])` to the write.**
- `cov2d_writer.main` calls `writer_control(args.cv, args.out)` (`:119`).
- `writer_control` calls `write_data_file(out, cols, pot)` (`:98`), a module global looked up at call time.
- The AST pass over `cov2d_writer.py`, `cov2d.py` and `control1_content_check.py` found:
  - one `def write_data_file` (`:59`) and one reference, the Load at `:98`;
  - no other name, attribute or string reference;
  - no `subprocess`, `functools`, `multiprocessing` or `from cov2d_writer import`.
- These are the only modules `writer_control` imports besides numpy and uproot. The grep is in `connect-2a.log.txt`.
- In the run, the stub was called exactly once.

## The run (`connect-2a.log.txt`)

login02, 2026-11-03T23:49:33Z to 23:50:18Z, 0 node-h, no job. Every step ran under nice 19 and `taskset -c 8-11`, with
OMP, OPENBLAS, MKL and NUMEXPR threads at 1.

- **The checkout:** a fresh clone at M = `c96c97f392f7402791e921ccdac952e74d454cee`; porcelain 0 before and after; the
  5 bound blobs before and after (`bound.blobs.{before,after}.txt`). REACH PASS.
- **Step 1, read (omnifold_py310: 3.10.19, numpy 2.2.6, uproot 5.6.9)** (`step1.log.txt`): the bound
  `read_cv_data($CV)` through O_NOATIME.
  - $CV's atime_ns was 1792770770214610703 before and after.
  - 4,119,797 rows; dataPOTUsed 1.057394261158926e+21.
  - Per-array sha256: measured `44d27c02…` (<f8), measured_pz `58c62522…` (<f8), measured_pass `1beb6568…` (|u1),
    dataPOTUsed `7224b6b6…`.
  - npz `6e19e645…`, manifest `578c3e95…`.
- **Step 2, write (root_6_28: 3.11.14, numpy 1.26.4, ROOT 6.28/12)** (`step2.log.txt`):
  - it logged both expected digests first, and both matched;
  - every loaded array was equal to step 1's in dtype, shape and bytes;
  - then the bound `write_data_file`, with output sha256 `8f931e8f…`.
- **Step 3, check (omnifold_py310)** (`step3.log.txt`):
  - it logged the expected digest first;
  - the stub was called once, with that file and digest;
  - compare_tree EQUAL ×3; then the unexpected-keys failure;
  - `CHECK rc=3 stub_calls=1`.

## The cause, verified locally (the director's step 1)

**Measured** under conda-forge ROOT 6.28/12, the same version as the cluster's root_6_28 (6.28/12, step 2's log):
- **The bound writer at full size** (`repro.py`, `repro.txt`; blob `2402ed4b` checked by `git hash-object`):
  - 4,119,797 synthetic rows with $CV's dtypes give keys `data;3`, `data;2` and `dataPOTUsed;1`, the cluster's exact
    extras;
  - the tree's fAutoSave resolved to 1,939,140 entries.
- **Scratch variants of the same loop at full size:**
  - `SetAutoSave(0)` gives `data;1` only;
  - `Write("", kOverwrite)` gives `data;1` only;
  - both together give `data;1` only.
- **Semantics** (`semantics.py`, `semantics.txt`):
  - three plain Writes and then one `kOverwrite` Write leave `data;3`, `data;2` and `data;1`, so kOverwrite deletes only
    the highest cycle;
  - with an autosave every 200 entries at 2,345 rows, a plain ending gives `data;12` and `data;11`, while
    `SetAutoSave(0)` gives `data;1`, and so does kOverwrite;
  - replacing `ROOT.TTree` with a factory that sets the 200-entry threshold makes the bound writer produce `data;12`,
    `data;11` and `dataPOTUsed;1` at fixture size. This is the forcing route for A1's test.

**Inferred** from those keys and the resolved threshold, not observed directly: AutoSave fired during the fills, each
AutoSave deleted its predecessor, and the final plain `t.Write()` added a cycle beside the last AutoSave's.

**Why the fix is `SetAutoSave(0)` alone** (the director agreed):
- it writes no intermediate cycle, so one cycle is certain by construction;
- kOverwrite gives one cycle here only because AutoSave deletes its predecessor, and a mutant dropping `SetAutoSave(0)`
  would survive under it.

The evidence for the cause depends on ROOT 6.28/12's AutoSave behaviour; the fix does not.

**Why the local checks missed it.** Every writer fixture had 2,345 rows, too few for an autosave:
- the bound `test_schema_and_parameter`, which asserts exactly `["data;1", "dataPOTUsed;1"]`;
- the 15 split tests below.

## The harness's local checks (before the run)

`tests_local.txt`: `test_control2a_split.py`, 15 of 15 passed, under conda-forge ROOT 6.28/12 with uproot 5.6.9, on a
synthetic $CV built by `test_cov2d_writer.write_cv` (2,345 rows, including a -0.0). macOS has no O_NOATIME, so the
local steps set `os.O_NOATIME = 0`, as the writer's own tests do.

`mutation_local.txt` (`mutate.py`): the harness's own guards, 8 of 8 mutants killed:
- no patch;
- the stub skipping its sha check;
- no per-array digest;
- no file digest;
- no call count;
- no after-sha;
- reach ignoring aliases;
- reach ignoring imports.

**A correction made before the run:** I had told the director the split's file would be byte-identical to the
single-process file. It cannot be: ROOT stamps each file with a creation time and a UUID, so two identical writes give
different bytes. The test asserts content equality instead (compare_tree, keys, POT).

## Removals (`connect-2a.log.txt`, `removal.log.txt`)

- **By the script, 23:50:17Z**, each with its sha256 and rc 0:
  - `cv_data.npz` (`6e19e645…`);
  - `cv_data.json` (`578c3e95…`);
  - `writer_control.root` (`8f931e8f…`);
  - the clone (1.2G).
- **Nothing was kept on pscratch.** The copy to `/pscratch/sd/j/josephrb/cov2d-2a/` happens only on PASS, and that path
  does not exist.
- **By me, 23:51:08Z**, after fetching the logs (sha256 match, `node_listing.txt`):
  - `/dev/shm/josephrb-cov2d-2a` (40K), rc 0;
  - `/dev/shm/josephrb-cov2d-2a.sh` (`b8c7656f…`, checked first), rc 0;
  - `ps -u josephrb` then shows no process of 2a.
<!-- absence-ok: a path on pscratch, shown absent by the ls in node_listing.txt; not a result -->


## Files

| file | what |
|---|---|
| `connect-2a.sh` | the connect as run, with the harness embedded |
| `control2a_split.py` | the harness, the same bytes as the embedded copy |
| `test_control2a_split.py`, `tests_local.txt` | the local checks and their output |
| `mutate.py`, `mutation_local.txt` | the harness's mutation run and its output |
| `connect-2a.log.txt`, `step{1,2,3}.log.txt`, `bound.blobs.{before,after}.txt` | the node's logs |
| `node_listing.txt`, `removal.log.txt` | the node's listing and digests; the removal |
| `repro.py`, `repro.txt`, `semantics.py`, `semantics.txt` | the cause's local reproduction |

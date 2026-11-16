# RDX s0: the STOP of 2026-11-12 (receipt)

**By** session tier3-design, under the director's go for `rdx_connect.sh` `22159ebd…` and `rdx_connect_launch.sh`
`45949bc5…` at M_RDXJ `3f74c36f` (#1098), step s0, login27, at 0 node-h.

**The result: STOP**, rc 8, 07:37:12–07:37:16Z (`s0.session.txt:156-158`). Nothing was retried.

**What passed before the STOP** (`s0.session.txt`):
- the clone at the pin, clean;
- the purge-exposed MP-1 inputs, all present (stat only);
- the policy check, CLEAR;
- the patch applied, and base equals canonical;
- **rdx_provenance PASS**:
  - the six pins hold;
  - all 7 `opt/lib` .so equal S0's MANIFEST rows;
  - the synced tree equals S0's `src_base` exactly (`changed`, `only_in_synced` and `only_in_s0` all empty);
- the O_NOATIME runtime-data manifest.

**The cause.** The build subshell runs `source setup_salloc_env.sh`. Conda's compiler activation inside it exports
`BUILD=x86_64-conda-linux-gnu`, and that overwrote the connect's own `$BUILD`, its build directory.
- Every build path became relative, and `environment.txt` could not be written (`s0.session.txt:155`, "line 83").
- `mkdir -p "$BUILD/bld_base"` created `x86_64-conda-linux-gnu/bld_base` in the job's working directory, `$HOME` on
  login27. `cmake` then failed for want of a source tree, and the subshell exited.
- The smoke could not see this: it stubbed `setup_salloc_env.sh` as an empty file.

**The probe** (the director's go; `probe.sh`, `probe.session.txt`; login27, 08:12:18Z, read-only):
- `~/x86_64-conda-linux-gnu/` held only s0's three entries from 07:37Z: the directory, `bld_base/`, and `cmake.log`
  (207 B).
- `setup_salloc_env.sh` has no `cd`.
- The setup adds 82 environment variables, `BUILD` among them. That measured list is committed as
  `nd-unfolding/rdx/setup_salloc_env.exports`.

**The removal** (the director's go, exactly as written, once; `remove.sh`, `remove.session.txt`; login27,
08:14:03Z): `rm -f` of `cmake.log`, then `rmdir` of `bld_base/` and `x86_64-conda-linux-gnu/`. `removal rc=0`, and a
listing afterwards shows the directory gone.

**State left in place:** `/pscratch/sd/j/josephrb/rdx-20261112/{deploy,build}`. The deploy is clean at the pin; build/
holds `src_base`, `src_rdx`, `provenance.json`, `RUNTIME.sha256` and `runtime.json`, and no binary. Under the approved
recovery this B is spent and is not reused. The fix uses B = `rdx-20261112b`.

## CITABLE FOR / NOT CITABLE FOR

- **Citable for:**
  - s0's provenance PASS against S0's MANIFEST at M_RDXJ;
  - the STOP's cause;
  - the probe's listing, and the setup's measured exports;
  - the removal and its rc.
- **Not citable for:** any binary, or anything past s0.

# RDX s0 in B = rdx-20261112b: PASS (receipt)

**By** session tier3-design. This ran under the director's go for `rdx_connect.sh` `11e7ef92…` and
`rdx_connect_launch.sh` `165fb98e…` at M_RDXS `ad0535c4` (#1099). It was step s0 on login27 and used 0 node-h.

**The result: PASS.** rc 0, 08:52:35–08:53:05Z (`s0.session.txt:4, 200-201`). The connect staged on the node is
`11e7ef92…` (`s0.session.txt:2`).

## The base binary's md5 beside S0's

| binary | md5 | `s0.session.txt` |
|---|---|---|
| RDX base (no patch), `rdx-20261112b/build/bld_base/runEventLoopOmniFold` | `8b758ce5234515fed46b4c026220bb9a` | 196 |
| MP-1 S0 base (`phase1/mp1/S0-REPORT.md:34`; the full digest is the connect's constant) | `a6b85ec3068536b0cb278b68d6f40359` | 198 |
| RDX patched (C1), `rdx-20261112b/build/bld_rdx/runEventLoopOmniFold` | `38398191bb0a86d3fa58be3602943117` | 197 |

**The two base md5s differ.** The declaration (§2, "The build (D5)", item 3) records this comparison and does not gate
on it. The cause was not investigated, and this receipt asserts none. The bitwise comparison with S0 that does gate is
C-ALIGN-1A at step c1, on the pilot's output. A binary-level difference therefore leaves that gate as the test of
equivalence. If C-ALIGN-1A fails, the provenance below and the recorded environment are the first diagnostics, as the
declaration lays out.

## What passed (`s0.session.txt`)

- the purge-exposed MP-1 inputs: all present, by stat only (5-100);
- the policy check: CLEAR, with no hits (101-133);
- the patch applied (135). The connect then requires that `src_base` and `src_rdx` differ only in
  `runEventLoopOmniFold.cpp` (`rdx_connect.sh:97-98`); the step went on, so that held;
- **rdx_provenance PASS** (136-153, and 155-173 as the step's own record):
  - the six pins hold;
  - all 7 `opt/lib` .so equal S0's MANIFEST rows;
  - the synced tree equals S0's `src_base` exactly (`changed`, `only_in_synced` and `only_in_s0` all empty);
- the environment, as recorded (175-194):
  - modules: PrgEnv-gnu/8.7.0, gcc-native/14, cpe/26.03, among others;
  - the compiler: `c++ (conda-forge gcc 12.4.0-2) 12.4.0`;
  - ROOT `6.28/12`;
- both binaries built (195-197);
- the O_NOATIME runtime-data manifest: `RUNTIME.sha256` `39712d5f7dee41c113282f029a9f84fd71ab71010ac2d0f540475373bbdf6777`,
  over 9 files (199).

## The export probe before s0 (the director's step 1)

`exports_probe.sh` ran on login27 at 08:51:41Z and wrote `exports_probe.session.txt`. It lists the variable names
`setup_salloc_env.sh` adds: 82 names, between the markers at lines 1 and 84. Sorted, that list is identical to the
committed `nd-unfolding/rdx/setup_salloc_env.exports` (`e0d3b700…`, 82 names): no name was added and none is missing.
The director's STOP condition (a name absent from that file) did not fire, and s0 ran next.

`s0.session.err.txt` is the ssh session's stderr, NERSC's login banner.

## State left in place

B is `/pscratch/sd/j/josephrb/rdx-20261112b`. The session shows both binaries under `build/bld_base/` and
`build/bld_rdx/` (196-197). By `rdx_connect.sh:95-119`, s0 also writes `src_base`, `src_rdx`, `provenance.json`,
`RUNTIME.sha256`, `runtime.json`, `environment.txt` and `MANIFEST.sha256` under `build/`. No listing of `build/` was
taken after the run.

`rdx-20261112` (the s0 STOP's B, `../run-s0-20261112/`) stays spent and untouched.

**Next:** s1, the 1A pilot. It waits on cov2d's LL5D atime-post UTC (s1's fourth argument), the director's `rdx_`
announcement to the fenced lanes, and the queue sequencing.

## CITABLE FOR / NOT CITABLE FOR

- **Citable for:**
  - s0's PASS at M_RDXS in B `rdx-20261112b`: provenance against S0's MANIFEST, the environment, and both binaries'
    md5s;
  - the base md5's inequality with S0's;
  - the `RUNTIME.sha256` digest;
  - the export probe's agreement with `setup_salloc_env.exports`.
- **Not citable for:**
  - the base binary's equivalence to S0's, either way. That is C-ALIGN-1A's to decide;
  - any cause of the md5 difference;
  - anything past s0.

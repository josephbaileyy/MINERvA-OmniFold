# RPD-RECO real-MnvH1D class check, attempt 2 (receipt, 2026-11-11)

**By** the limitation-resolver lane, on Joseph's go relayed by the director (2026-11-11). The director's GO was for
exactly `rpd_mnv_check2_connect.sh` `94e39a3a…` and `rpd_mnv_check2_launch.sh` `c32c3551…`, verified at `c42d75a5`, with
`cov2d_fence.sh` (`16a2a5cd…`) first. One login-node connect, 0 node-h.

**RESULT: PASS.** At #848's head `9634aadf`, `nd-unfolding/tests/fd_rpd_reco_mat_check.py` read the committed non-input
probe as a `PlotUtils::MnvH1D` in the pinned MAT environment. Its ROOT worker exited 0, process teardown included.
- Attempt 1, at `d9740563` on 2026-11-06, segfaulted in `TFile::Close` (`../real-mnv-check-20261106/`).
- At this head the check runs in a worker subprocess and publishes PASS only after that worker exits 0.

| record (extracted from `connect/session.out`; each sha256 equals the one the node printed) | sha256 |
|---|---|
| [`real-mnv-check.json`](real-mnv-check.json): status PASS, worker_exit_code 0, class `PlotUtils::MnvH1D` | `a4ec3e02feba4204c8bc8f40307ab61098210963b86bb65a276ecd18676105b2` |
| [`real-mnv-worker.json`](real-mnv-worker.json): the worker's own record | `d28022d344cf1c6cb8606985a8f6e337852ddc8587bac38cad773af88b836f2e` |
| [`worker.stdout.txt`](worker.stdout.txt): the three REAL_MNV progress lines, through "entering process teardown" | `89625f3fc3737c0015c1ee00dfa7628f8f7f540aad4e081a30c9e228583df0d2` |
| [`worker.stderr.txt`](worker.stderr.txt): nine ROOT rootmap warnings (RooUnfold classes listed in both libUnfoldUtilsDict.so and libRooUnfold.so) | `c0b89ac88c4dea667785089e08266eecf07a0040aa7f8e80ebfb85caba2c12c7` |

**CITABLE FOR:** that #848's real-class check passed at `9634aadf` in the pinned MAT environment, with the records above.

**NOT CITABLE FOR:**
- any RPD-RECO reading, or P0 permission (the record's own scope: "non-input real-class fixture; no campaign input or
  P0 permission");
- the flux connect, which still needs a READY production config, #848's merge and the code's binding 2
  (FD-RPD-RECO-BINDING-1 item 2);
- a reading of the rootmap warnings, which are recorded as printed.

## The run

1. **Survey** (`survey/`, 08:12:19Z): one read-only ssh session over six nodes.
   - login21 was the quietest, at 13.72 / 13.38 / 14.12 on 244 cores, with the work directory absent.
   - The others: login27 17.47, login02 29.56, login33 33.87, login05 62.05 and login37 62.47.
2. **Fence** (`fence/`, login21, 08:12:49Z): `FENCE CLEAR`.
   - squeue held `61078463 ll5d_gate_G18 PENDING`, `61078506 ll5d_gate_AR23 PENDING` and `61137569 e96data_dry RUNNING`.
   - Of 28 cov2d/t2a sacct rows in 14 days, none was unended.
   - The node checked the staged copy's sha256.
3. **Connect** (`connect/`, login21, 08:13:06Z to 08:13:31Z): ssh rc 0, script rc 0, mat_check rc 0.
   - The node staged the copy at `94e39a3a…`, equal to the approved sha256.
   - The fresh clone was at `9634aadf`, with HEAD equal and porcelain 0.
   - The probe was at `d9704aa4…`. `fd_rpd_reco_mat_check.py` (`06360100…`), `fd_rpd_reco.py` (`f748c897…`) and
     `fd_rpd_inputs.py` (`6e4ed0f1…`) were each at their pinned sha256.
   - check-mat-setup before sourcing: `{"mat_setup_scripts": 6, "mismatches": 0}`. setup_salloc_env.sh sourced with rc 0
     and an empty log (`e3b0c442…`).
   - root_6_28's python3 (Python 3.11.14), ROOT 6.28/12, `libMAT.so` `5901f18a…` the one mapped MAT file. Threads 1,
     nice 19.
   - The run wrote only under `/dev/shm/limres-rpd-mnv2-20261111`, printed every output file, and removed that directory
     by its literal path. Nothing was written to pscratch or CFS.

`*/session.err` and `survey/survey.err` hold NERSC's login banner.

Nothing is submitted, deposited or tagged.

# BINDING 2 (code, flux stage only): RPD-RECO's MAT flux extraction and its first connect (director, 2026-11-11)

**Binds**, for the **flux stage only**:
- the code of PR #848, as merged to main at **M_848 = `4112e267bc35c25e955dd4d9e11789d674401241`**. The clone pin is
  its audited head **S = `763ab4ddcea2d2d3dce56138f8aa7ae7fab4bbe6`**, an ancestor of M_848; every file below is
  byte-identical at both;
- the READY production config and flux connect 1, as merged in PR #1064 at
  **M_F1 = `678b1ddc9710b104d6fc9f66c070f66ed4a8b272`**, byte-identical under `fd/rpd-reco/flux1-20261111/` to the
  audited head `581a78e9`.

| file | sha256 (prefix) |
|---|---|
| `nd-unfolding/fd_rpd_reco.py` | `7302cc1df71758cf` |
| `nd-unfolding/fd_rpd_reco_custody.py` | `867822e3cbf70630` |
| `nd-unfolding/fd_rpd_inputs.py` | `6e4ed0f1d7f55b7b` |
| `nd-unfolding/fd_rpd_reco_flux_connect.sh` | `32db52355a4811bd` |
| `nd-unfolding/tests/test_fd_rpd_reco.py` | `671e1cdcfbd38741` |
| `nd-unfolding/tests/fd_rpd_reco_mutation.py` | `f2612369997204d9` |
| `nd-unfolding/tests/fd_rpd_reco_mat_check.py` | `06360100038f0203` |
| `flux1-20261111/production-config.ready.json` | `cde8d02904b0257d` |
| `flux1-20261111/rpd_flux1_connect.sh` | `34694c0d90fa09b4` |
| `flux1-20261111/rpd_flux1_launch.sh` | `8354aece1061e783` |
| `flux1-20261111/rpd_flux1_fetch.sh` | `dfade48a535e722c` |
| `flux1-20261111/tools/fence_overlap.py` | `baa7630936db399a` |
| `flux1-20261111/tools/protected_read.py` | `309f59d46a4f200d` |
| `flux1-20261111/README.md` | `627a199a15b29ba5` |

The job script `rpd_flux1_job.sh` is written by the connect, sha256 `4198103b3a1d94eb…`.

**Under** Binding 1 (`FD-RPD-RECO-BINDING-1.md`), ruling 2: the code needs tests, a mutation receipt, an audit of the
code and binding 2 before anything runs. Also under Binding 1 addendum A1 (φ is MAT's own CV reweight flux).

## What the director checked

- **coverage-5b-audit's code-level GO for this scope at S.** A full audit at `10731ed3`, then every production commit
  to the four code files up to S falls in an interval that one of its GOs closes (the MAT flux stage and row
  factors; C1–C4; rounds 1–3; #1069, #1071 and #1072).
- **The before-READY guards** (#1069, #1071):
  - four placeholder guards refuse any `${` in the resolved config or either CLI's arguments, each with a killed
    mutant;
  - flux-extract's `mat_dependency_sha256` records an O_NOATIME sha256 of all 15 files FluxReweighter opens, from a
    closed inventory, refusing a gap, an extra, a duplicate or a malformed sha.
- **The stat receipt** (#1072, cov2d's condition): each staged item carries stat_before, stat_after (device, inode,
  bytes, mtime_ns, atime_ns) and its UTC staging window, tested present.
- **Flux connect 1, four audit rounds, final GO at `581a78e9`:**
  - F1: the 12 flux-factor products (~590 MB) stay on pscratch; the fetch sends their sha256s and exits 12 on a
    mismatch;
  - F2 and R1: a Slurm batch job with a TERM/INT trap at `--signal=B:TERM@300`, an EXIT trap and recorded host, pid
    and cause; an uncatchable kill is reported as CLEANUP UNVERIFIED;
  - f3: a gate holds the wrapper until its pgid equals its pid, or it STOPs with rc 8.
- **Suites:** 300 tests passed; harness 236 of 236 killed.
- **Locally:** S is an ancestor of M_848, and the analysis source `f4cd8f8b` is an ancestor of main, with
  `runEventLoopOmniFold.cpp` `57792e42` there and on main and `:1698-1701` setting the ν-e constraint, the playlist,
  PDG 14 and 100 flux universes.

## Rulings

1. **Scope.** The flux stage is bound: the pins, custody prepare, the placeholder guards, flux-extract with its
   WALL_CLOCK guard, the trace check and the receipts. **P0, step0, c0, d2-predict, d1 and d2 are not bound.** Each
   needs its own READY config, with retention and the premise measured, and a binding addendum.
2. **The exception to cov2d's fence.** Exactly one protected path may be read:
   `/pscratch/sd/j/josephrb/MINERvA-OmniFold/MINERvA101/opt/etc/MParamFiles/data/FluxConstraints/sorted_NuEConstraint_FHC_RHC_IMD.txt`.
   - It is read by custody prepare only, in one stat-bracketed staging with two O_NOATIME reads, and the run STOPs if
     its atime, mtime or size moved.
   - The receipt carries its stat_before, stat_after and staging window (cov2d's condition).
   - Any other overlap with cov2d's 30 protected paths STOPs. cov2d gave its no-objection on 2026-11-11.
3. **The job.** `rpd_flux1`, a new family, on the shared QOS: -C cpu, 1 node, 1 task, 4 CPUs, 16G, `--time=03:00:00`,
   account m3246. scontrol's JobName, TimeLimit, QOS and Account are checked, and the job is cancelled on any
   difference. Nothing is written to CFS.
4. **The price:** at most 0.094 node-h, or 3 node-h if the shared QOS charges a whole node; within the director's
   authority. sacct's Elapsed sets the actual charge.
5. **LL5D and E96D jobs may pass the fence**, since the run overlaps none of their inputs beyond ruling 2's file.
   The fence STOPs on any rpd job of ours already present.
6. **The go.** The connect runs only after the director's go, which comes after the maintenance ends, Joseph's cert
   renewal, and the announcement of `rpd_flux1` to every fenced lane. The fence connect (`cov2d_fence.sh` `16a2a5cd`)
   runs first.
7. **The result** is read once from its committed receipt. It feeds P0, and no RPD-RECO statement enters the paper or
   the note except through Binding 1's licences.
8. **Follow-ups** (lows): the fence's use of prologue 5's recorded MAT prefixes (f2); #848's lows already listed
   (Y07 and Y25 STOPs untested, execve not traced, pymon admitted by prefix, L-848R2-a to -e).
   <!-- absence-ok: the audit's catalogued lows on #848's own tests and tracing, not a claim that a result does not exist -->

Nothing is submitted, deposited or tagged.

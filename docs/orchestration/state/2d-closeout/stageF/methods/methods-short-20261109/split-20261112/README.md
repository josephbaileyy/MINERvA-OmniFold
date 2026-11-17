# #977 row 4.2 split probe: STOP at probe (a), exit 6

**What ran.** One session on login27, 2026-11-12T00:48:03Z, under the director's go for exactly
`code/split_remote.sh` (6784499d…), `code/split_fetch.sh` (51a5d014…) and `code/pl_shas.txt` (fc729d1a…; the twelve
per-playlist pins of proxy_hists_meta.json a71186e1). 0 node-h. Fence clear (squeue: only ll5d_gate_G18 and
ll5d_gate_AR23 running; 28 cov2d/t2a sacct rows in 14 days, none unended). Log: `session/fetch.out.txt`.

**Result: exit 6, STOP, nothing retried.** All 13 inputs (the twelve May files and work_proxy.npz) were sha-streamed
with O_NOATIME, whole, stat unchanged, and each equals its pin. Every one of the twelve files' `mc_background` has
exactly four branches, `sim_background`, `sim_background_pass`, `sim_background_pz`, `w_bkg`; none has
`bkg_nuPDG`, `bkg_current` or `bkg_vtx_x/y/z`. No branch data was read. `session/session.tar` (2b0ca3f2…) holds the
remote's `manifest.json` and `branches.json`, kept unextracted, as `split_fetch.sh` does on rc 6.

**The files' dates against the code** (a reading, not a conclusion):

| | |
|---|---|
| file mtimes (manifest) | 2026-05-15T05:04:59Z to 2026-05-15T10:34:39Z for eleven; 1E 2026-05-18T08:51:05Z |
| `bkg_*` branches added | 3e855893b, 2026-07-11 |
| out-of-phase-space signal into `mc_background` (Phase 18) | d1bc8813a, 2026-05-18T10:56:54-07:00 (17:56:54Z) |
| the fill condition before d1bc8813a (`d1bc8813a^:runEventLoopOmniFold.cpp:347-348`) | `isSignal = michelcuts.isSignal(...)`; `if(isSignal) continue;` |
| the fill condition after it (`runEventLoopOmniFold.cpp:1448-1455` at HEAD) | skips only `isSignal && isEfficiencyDenom` |

Every mtime precedes the Phase-18 commit. If the files were made by the code before it, `mc_background` holds only
events failing the signal definition (ν_μ CC), with no out-of-phase-space signal and no out-of-fiducial ν_μ CC. A
commit time is not a run time, so which code made them is not established by this probe. What the template contains
is therefore not established by any record read here.

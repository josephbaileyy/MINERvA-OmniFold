# (b) part 1: the read connect package (tier3-design, 2026-11-24), for the director's binding

One login read connect serves both (b) part 1's inputs (B-SEL-DECLARATION.md §1) and part 3's tables. **Nothing has run.**

| file | sha256 | role |
|---|---|---|
| `bsel_read.sh` | `199cc946b5a7238873f99702b55caf0872fce95ed3e253cb9fdbc67c400ad547` | the connect: window, sacct fence, `$OUT` absent, sources present, then per source: stat, a dd iflag=noatime read whose sha256 must be the pin, a dd iflag=noatime copy whose sha256 must be the pin, stat unmoved; RECORDS.SHA256SUMS (6 well-formed lines, `--strict`); one tar |
| `bsel_launch.sh` | `a0fc824fa9ac885c555c62e0b39af4369a4cea3dd63293e6c5d3b98b79383c4e` | the launcher: S2R's reviewed one (f8cd325d) with one connect. It holds the read sha once; the /dev/shm copy is checked on the node; the remote rc propagates; it streams back the tar, log and done; the tar must equal the log's sha, its sums hold under `--strict` with one line per file, and the done file must be 0 |
| `bsel_launch.template.sh` | (template) | the launcher before its pin is filled |

- **Usage:** `bash bsel_launch.sh <new empty dir> <loginNN> <window_end_epoch> cov2d,rpd_,d2s0,covfix`.
- **The sources** (pins in the declaration §1):
  - the F0b and F1 experiment tables, which part 1 and part 3 both need;
  - the two F1 closures;
  - the pvl Tune v1 and NuWro closures.
- **Writes:** only `/pscratch/sd/j/josephrb/bsel-20261124` and the launcher's `/dev/shm/bselc.<pid>.*`. Nothing goes to
  CFS. No Slurm job; **0 node-h**.
- **A purged source BAILs** before any copy. The HPSS htar fallback, on a loginNN and never a DTN, would be its own
  amendment.

**Stand-ins** (`standin/`, Debian, `/pscratch` and `/tmp` on named volumes). The only stubs are sacct and sha256sum, on
planted pins.

| variant | result |
|---|---|
| ok | rc 0: all 6 sources with pin, copy and stat true; the tar's RECORDS.SHA256SUMS OK, 6 lines for 6 files |
| missing | rc 9: BAIL source missing (purged?) |
| pin_bad | rc 4: STOP, a source failed its pin |
| out_exists | rc 9: BAIL `$OUT` exists |
| window_ended | rc 9: BAIL the window ended |
| fence_running | rc 9: BAIL fence (sacct) not clear |

Every variant made no squeue call, wrote nothing outside `$OUT`, and removed its /dev/shm copy.

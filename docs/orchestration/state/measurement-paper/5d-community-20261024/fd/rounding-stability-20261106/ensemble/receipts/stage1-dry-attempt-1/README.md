# ENS1 stage-1 dry run, attempt 1: the failure receipt (job 60983221, 2026-11-08)

**Recorded by** the rounding-instability lane (`director-helper-3`). The run was made under `ENS1-BINDING-2.md` at
M = `53382844e72057d6eacb47f3bf8556cd47766a70`, after the director's go on the connect's sha256. **It STOPPED, unrepaired.**
The bound runner's grid-membership guard refused every task at protocol seed 1. Nothing is graded from it.

**CITABLE FOR:**
- the attempt's execution: the connect's checks, the refusal and its counts, the charge, and the five products written;
- the falsification of `ENS1-DECLARATION.md` §2.3's claim that the total move cannot cross a fine-grid edge.

**NOT CITABLE FOR:**
- any ENS1 reading, gate or product value;
- a confirmed cause. The mechanism below is arithmetic on the edges, and has not yet been checked on the data.

## The connect (`connect/`)

**The scripts:** `ens1_dry1_submit.sh`, sha256 `ef795b2f…`, byte-identical to the one sent, and the launcher
`ens1_dry1_launch.sh`, `7e1648b3…`. ssh rc was 0.

**`connect-dry1.log.txt`** (login28, 2026-11-08T01:07:11Z–01:08:08Z, rc 0):
- **the fence:** clear. The squeue shows RS1's 60982139 RUNNING;
- **iris:** 1,764.5 node-h remaining, against combined caps of 109.0;
- **the stat:** all 22 files present;
- **the deploy:** at M, clean, 9/9 blobs, with the declaration, binding 1 and FD-STAB SHA256SUMS at their digests;
- **j1–j20:** copied with `dd iflag=noatime`, with no atime moved and every copy at its line (`refs-SHA256SUMS`);
- **the sourced environment:** python 3.11.14, lightgbm 4.6.0;
- **the stage-1 queue:** the seven files byte-match the digests sent (`queue-sha256.txt`);
- **the submission:** sbatch rc 0, `TimeLimit=00:45:00`.

## The job (`log-dry/`, `sacct-60983221.txt`)

- **`sacct`:** FAILED 1:0, 1 node (nid007105), ElapsedRaw 571 s, so **0.1586 node-h** of stage 1's 55.0 cap.
- **`log-dry/FAILED`:** `rc=123 failed=ens1_s01_k001 ens1_s01_k002 ens1_s01_k003 ens1_s01_k004`. There is no DONE and no
  `.teardown`.
- **Ended with rc 0,** five tasks: `ens1_F64` (the float64 base), and `ens1_s00_k001`–`k004`, the base input at internal
  seeds 1–4. Each took about 480 s per unfold. Their products are pinned in `log-dry/SHA256SUMS`.
- **Refused,** the four tasks at protocol seed 1, each with `.failed` = "rc=5 before every product was written". In
  `tasks/ens1_s01_k00k.log.txt`, the bound runner's guard (`s5p_numerics.py:186-191`) prints:

  `refusing: jitter 1 changed grid membership {'MCgen': n, 'MCreco': 0, 'measured': 0, 'bkg_reco': 0}`

  with n = 2, 1, 2 and 1 for k = 1–4.

## What it shows, and what is not yet established

**§2.3 is false as stated.** It argued that "the total move |δ_s + δ_k| is below one float32 spacing, so a value off an
edge cannot reach it". That holds only for edges that float32 can represent exactly.

**A likely cause, by arithmetic only.** The fine grid's edges are float64 (`project_cov_nd.py:46-53` @ e306087e).
- Several are not float32-representable, for example q3 at 0.2, 0.4, 0.6, 0.8 and 1.2, and W at 1.1, 1.4, 1.8 and 2.2.
- Each such edge lies between two float32 values, 0.2–0.4 of a spacing from one and 0.6–0.8 from the other.
- The protocol jitter alone (±½ spacing) can only cross from the nearer neighbour, and FD-STAB's 51 jitters never
  tripped this guard.
- The protocol jitter plus the internal jitter (up to about one spacing) can also cross from the farther neighbour.

**The check that would confirm it,** proposed to the director: a read-only login-node recomputation of jitter 1 and
δ₁–δ₄ on the npz, with no fit. It confirms the cause if it reproduces the counts {2, 1, 2, 1} exactly and places each
row at a farther neighbour.

**Which products the repair would change.** F₆₄(x) carries no internal jitter, so a repair of δ_k would leave it as it
is. The four s = 0 products would change under any repair that alters δ_k on their coordinates.

**Renames:** git ignores `*.log` and `*.out`, so those files carry a `.txt` suffix here. Their contents are unchanged.

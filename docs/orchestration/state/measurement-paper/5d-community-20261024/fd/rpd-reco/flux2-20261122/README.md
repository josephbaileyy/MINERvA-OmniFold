# RPD-RECO flux rerun (rpd_flux2): config, scripts and pre-connect checks (2026-11-22)

**By** limitation-resolver, for the director, under the director's rulings (a) and (c) of 2026-11-22. This is the
package for one batch job that reruns flux connect 1 ([`../flux1-20261111/`](../flux1-20261111/README.md)) with the
P0 premise set. Nothing in this directory has run on the cluster except e1 survey 1 (S1, login-only, below). The
connect waits for the director's GO and cov2d's fresh acknowledgement after S1.

## What changes from flux connect 1

[`tools/gen_flux2.py`](tools/gen_flux2.py) produces every file here from flux1's committed files and S1's
`survey.log`. It refuses unless S1's remote script is 1a9e244a, `survey.log` is 79a63325, ssh rc was 0, flux1's
files have their pinned shas, the config round-trips byte-exactly, and the changed leaves are exactly these:

- `premise/cv_numerator_is_selected_spectrum` and `premise/generation_denominator_is_common`: null → true;
- `flux_selection/{1D,1M,1N}/retention`: the placeholder → a string built from S1's stat line of that group's
  selected gen2thin file (the bytes must equal the inventory row);
- `flux_custody/path` and `flux_extract/path`: flux1's run root → `/pscratch/sd/j/josephrb/rpd-reco-flux2-20261122`;
- `cov2d_protected_paths`: flux1's 30 paths followed by six cov2d roots, each checked against its receipt line under
  `fd/receipts-cov2d/`.

The scripts are flux1's with counted replacements: the run root, the job name (rpd_flux1 → rpd_flux2), the config's
base64 and sha256, the fence tool's write root, the squeue fences → one sacct fence, and `--time` 03:00:00 → 01:00:00
(0.039 node-h priced at 10 of 256 CPUs). The clone path `/dev/shm/limres-rpd-flux1/repo` is kept, since the bound
config names it, and so is the schema string `rpd-flux1-protected-read/1`, which the pinned `protected_read.py`
writes.

The reads (below) added these changes, each a counted replacement in `gen_flux2.py`:
- the scripts' flux1 labels, the launcher's staging name and the fetch's tool directory become rpd_flux2's
  (`/dev/shm/limres-rpd-flux2-fetch`);
- the launcher returns the remote script's rc. flux1's remote command ended in `echo "script rc=$?"`, so ssh's rc was
  always 0 (see "ssh rc" below);
- the launcher refuses a cert that ends within 30 minutes (e1_survey_launch.sh's check);
- the launcher's `fence` mode refuses. It pinned `cov2d_fence.sh` rev 1 (16a2a5cd), which calls squeue, and the job's
  own step-2 sacct fence replaces it;
- both porcelain checks refuse a failed `git status`, which a `| wc -l` count had read as clean;
- the fetch refuses a grep error in the no-private-record redaction check, and a failed tar or base64 (exit 14);
- the connect's comment counts cov2d's 36 protected paths.

## S1: the survey (2026-11-22T22:01:53Z, login23)

`e1_survey_remote.sh` (1a9e244a…cf670b) was run through `e1_survey_launch.sh` (24dddd72…8060b), both re-hashed
before the connect. Both scripts and the launcher's whole output directory are committed in [`s1/`](s1/), with `survey.log` as
`survey.log.txt` (the repo ignores `*.log`; the bytes are the same). It ran echo, sacct, iris and stat only: ssh rc 0, empty stderr. Output shas:

| file | sha256 |
|---|---|
| `survey.log` (51 lines) | `79a63325c0906444893ed91c2a2ca6d78d7246ee439f58d0f4cec55fb4f865e5` |
| `ssh_rc.txt` | `9a271f2a916b0b6ee6cecb2426f0b3206ef074578be55d9bc94f6f3fe3ab86aa` |
| `remote.sha256` | `bec380f37519f004c398af74891d2a38232145c3b1e9471ac79168fe7c4aaa9c` |
| `cert.txt` | `21ebea7a1f6bb6ede8a39434ae099ec12a846e26bd7138b103687ceae2ba7895` |

- sacct over 14 days: 102 rows, no unended job.
- iris m3246 row: `2611.2  10000.0  19274.4  20000.0`; the balance ($5 − $4) is 725.6 node-h.
- RPD job A's 24 dumps are present; their atimes are 2026-11-04T11:38:24Z..11:38:30Z, so the earliest purge
  exposure is 2026-12-30T11:38:24Z.
- flux1's `run/flux-custody.json` is absent: flux1's 2026-11-15 cleanup recorded it (sha256 84db31ca…, kept at
  `../flux1-20261111/run-61206960/records/run/flux-custody.json`) and removed it
  (`../flux1-20261111/delete-20261115/stepB/delete/session.out:126`). The rerun writes its own.

## Checks on these bytes

Reproduce from the repository root (local, nothing contacted):
`python3 -I -B <this dir>/tools/gen_flux2.py <this dir>/s1 .` rewrites the five generated files byte for byte;
`python3 -I -B <this dir>/tools/fence_overlap.py <this dir>/production-config.ready.json .`;
`bash <this dir>/tests/test_sacct_fence.sh`; `bash <this dir>/tests/test_launch.sh`.
Their outputs at these bytes are `tests/fence_overlap_real_config.out.txt`, `tests/test_sacct_fence.out.txt` and
`tests/test_launch.out.txt`.

- `gen_flux2.py` rc 0. `flux_selection_digest`: flux1 `1c716c12…663ac`; rerun
  `75c2a1f4435494bf0e2c5bf4d27631781e65bd738c889c667183778e254792e8`, equal to the P0 form and different from flux1.
- Overlap fence, `tools/fence_overlap.py` on this config with the repo at 9e7759c6 as the clone: `FENCE protected
  paths 36`, `staged originals 57`, the one allowed exception (`sorted_NuEConstraint_FHC_RHC_IMD.txt`), `FENCE
  OVERLAP: CLEAR (allowed 1, stops 0)`, rc 0. Its only difference from flux1's copy (baa76309) is `WRITE_ROOTS` at
  line 30.
- Connect step 2, the sacct fence (gen_flux2's `SACCT_FENCE`), fails closed in the pattern of cov2d's
  `cov2d_fence.sh` rev 2 (3fbc9cbd, merged 7d5a98361), on the director's FIX of 2026-11-22. It reads
  `sacct -X -n -P -u josephrb -S <14 days ago> -o JobID,JobName,State` with stderr captured. It STOPs (finish 3)
  when:
  - the start date fails or is malformed;
  - sacct fails;
  - any non-empty line is not a 3-field row with a JobID matching `^[0-9]+([_+].*)?$`;
  - a cov2d*, t2a* or rpd* row has a State whose first word is not in the closed terminal set, which is rev 2's
    exactly (BOOT_FAIL, CANCELLED, COMPLETED, DEADLINE, FAILED, NODE_FAIL, OUT_OF_MEMORY, PREEMPTED, TIMEOUT; REVOKED
    refuses).
  The window is the director's 14 days. Known gaps, sacct-only by rule: a job that has stayed non-terminal since before
  the window, or a pending job with no EligibleTime, can be omitted. cov2d's fresh ack covers them.
- [`tests/test_sacct_fence.sh`](tests/test_sacct_fence.sh) runs that block, byte-equal to the connect's, against a
  stub sacct, after checking that `rpd_flux2_connect.sh` holds the block byte for byte. 19 checks pass, including:
  - an error on stderr with rc 0, a 2-field row, a 4-field row, a non-numeric JobID, a JobID with a digit that is not
    numeric, and a step id (`12.batch`): each STOPs;
  - COMPLETING, REQUEUED and REVOKED STOP; "CANCELLED by N", TIMEOUT, array ids and het ids read CLEAR;
  - dropping `-S` would hide a job running since yesterday.
  The file then runs 13 mutants of the block against the same cases: 13/13 killed. **A correction:** before the FIX,
  limitation-resolver reported "4 mutants killed" for the earlier block. Those were ad hoc runs with no record, and
  this file's mutants replace them.
- [`tests/test_launch.sh`](tests/test_launch.sh) runs a copy of the launcher against dummy connect and fetch scripts
  (its pins re-pointed at them), with stub ssh, ssh-keygen and sha256sum. Nothing is contacted, and the real cert is
  never read. 7 cases pass:
  - a connect that exits 3 gives launcher rc 3; one that exits 0 gives rc 0;
  - an unfinished fetch gives rc 10;
  - a cert ending within 30 minutes STOPs before ssh is called, as does an unreadable cert end time;
  - fence mode is refused;
  - an altered connect STOPs with rc 8.
  Two mutants, flux1's echo-last tail and a dropped cert check, are killed.
- The generated scripts contain no squeue.

## Reads

| read | report (under `~/codex-reports/note-measurement/reads/`) | sha256 | verdict |
|---|---|---|---|
| Grok, package at connect 16494871 | `flux2-20261122/grok/out.txt` | `664102c428695c16d5bb7e3db2b86c1857a2d9b6da3d43ed81168cb6caf40113` | FIX |
| agy, the same package | `flux2-20261122/agy/out.txt` | `6e2482ef15c0a95a2baea4a8e4cb40326af75bc8fb40c0716c89af5faca54c2e` | FIX |
| agy confirm of the fixes | `flux2-delta1/out.txt` | `ebac19a0f2dd8f3b8e931e4374e96aedb1f66e573b72c54b822b8823bf81d24c` | GO |

- agy's blocking finding was the launcher's masked rc, and Grok's was fence mode's squeue. Both are fixed.
- Every non-blocking suggestion was taken as a fix, except three, left for these reasons:
  - gen_flux2's `FLUX1` path: it runs inside the repo, not in a read package;
  - the receipt check is a substring test, because each receipt line holds the path inside its text;
  - the fetch's sacct state pipeline: an empty state reads as NOT FINISHED (exit 10), which fails safe.

## Files and shas

| file | sha256 |
|---|---|
| `production-config.ready.json` | `7ebc2aa9e254ec99535fab2416617e069f3a97621fa69c1c44b24b31a38c4fa9` |
| `rpd_flux2_connect.sh` | `7a362f34dd00b2422c91ff542366d9cc120c8dedbde730da5592b171bac73fd2` |
| `rpd_flux2_fetch.sh` | `d8f780c917b873a888ce2dd55d8f16f813018a5d4fd87211f24e5d23dea750fc` |
| `rpd_flux2_launch.sh` | `c744061e6a1cbd589a032e91e81d3178b066faa336097a935e4f294486408487` |
| `tools/fence_overlap.py` | `68e4033c8d4cbabe01ea6fdd1645f4ddfb42098a52a5d38c653f708cd80d1553` |
| `tools/gen_flux2.py` | `6344f152e920df64f9a1ba09550c78f3e7b416445ec391b916914eb68782cb56` |
| `s1/survey.log.txt` | `79a63325c0906444893ed91c2a2ca6d78d7246ee439f58d0f4cec55fb4f865e5` |
| `tests/test_sacct_fence.sh` | `209736947bd0ab8f1fcd571be3947b509392f46e64c77463ba7c7a79d6baf22e` |
| `tests/test_launch.sh` | `b3abea5bc33fec682fe553fde3cf5bbe82af45e5122b43ca7cafd64c5005e055` |

## ssh rc: what it showed before this fix, and what relied on it

agy's blocking finding was that flux1's launcher reported ssh's rc, and ssh's rc was the trailing echo's. On the
director's question, here is how far that reaches.

1. **The two launchers this package descends from both report an uninformative ssh rc.**
   - `../flux1-20261111/rpd_flux1_launch.sh` (8354aece), line 35, ends its remote command with
     `bash "$f" "$f"; echo "script rc=$?"`. Its ssh rc is the echo's, always 0. The script's status survives only as
     the text line `script rc=N`.
   - `e1_survey_launch.sh` (24dddd72) runs `ssh … 'bash -s' < e1_survey_remote.sh`. Its ssh rc is the status of the
     remote script's last command, `echo "== end utc …"`, so it is 0 whenever the connection works. The survey script
     has no `set -e` and always runs to its end. A failed sacct prints `SACCT FAILED`, and a failed stat prints its
     error line.
   - In both, ssh rc 0 shows only that the connection worked, and 255 is still a connection failure.
2. **What each run relied on.**
   - **S1** relied on its content. The log has 51 lines, with the host/utc/epoch line, `sacct rows (14 days): 102`
     (no `SACCT FAILED`), the iris row, 44 stat lines (43 stats and one expected ENOENT, see above) and the end line. Its stderr
     is empty, and the remote copy is 1a9e244a. `gen_flux2.py` parses the three selected stat lines and refuses a
     missing or malformed one. It also now pins `survey.log` itself (79a63325). The director read the content
     directly.
   - **flux1** (`../flux1-20261111/run-61206960/`) relied on each session's `script rc=` line and content:
     - fence: `FENCE CLEAR`, `script rc=0`;
     - connect: `FENCE OVERLAP: CLEAR`, `overlap fence rc=0`, `sbatch rc=0 jobid [61206960]`,
       `== rpd-flux1-connect rc=0`, `script rc=0`;
     - fetch1: `NOT FINISHED (PENDING)`, `script rc=10`;
     - fetch2: `TAR END tar rc=0`, `== rpd-flux1-fetch rc=0`, `script rc=0`, and the records it sent.
   - fetch1 shows the masking in a record: its launcher logged `ssh rc=0` beside `script rc=10`. The run README
     records fetch1 as "NOT FINISHED (PENDING), rc 10", from the script's line, not from ssh's rc.
3. **No past verdict on main was read from ssh rc alone.** Two checks, on origin/main at d09e460a:
   - Every committed session output with a `script rc=` line (98 files): the ten sessions whose script rc was non-zero
     are each recorded as what the script returned. Those are g3-setb-stat statB2 (rc 1, "by design"), E96 a1 full-1
     (rc 11, STOP), E96 post-full-1 and post-dry-1 (rc 10, running), RDX c1 and s0 (rc 8, STOP), RSN hpss smoke
     (local), the flux1 delete TEST-LAUNCH (a stub test, rc 4), flux1 fetch1 (rc 10), and the tier3 dry and floor
     attempt 1 (rc 8 and rc 9).
   - agy read every committed record that mentions "ssh rc" (59 records, with the launchers and session logs beside
     them), report `reads/sshrc-sweep-20261122/out.txt`, sha256
     `91318ee4758de470aecbd8a94061c5994879d17f7e861c2879d6cc030bfe4e92`:
     - **AFFECTED: 0.** Every record behind a masking launcher, form (a) (`…; echo "script rc=$?"`) or form (b)
       (`'bash -s'` ending in an echo), also cites the script's status or its output.
     - It could not classify 14 launchers. Their verdicts rest on content or script status regardless.
     - Two of its "content" verdicts were spot-checked here: receipts-prr/dry rests on `post_rc=0` and the tarball's
       85/85 sha check, and receipts-ll5d/ovl rests on its result table.
   - Other launchers on main still report an echo's rc: v-half-r `vhr_wtruth_launch.sh`, `ess_launch.sh`,
     `rpd_mnv_check2_launch.sh`, `t2a_launch.sh` and `t2a_status_launch.sh` (the exact flux1 tail), plus the variants
     the sweep lists. No record is affected, but a future run of any of them must read the `script rc=` line, not ssh's
     rc.

## cov2d's acknowledgement

cov2d acked at 2026-11-22T22:05:53Z, after S1. It read config 7ebc2aa9 (36 protected paths) and the scripts' and
tools' /pscratch paths, and answered three questions:

1. **Live roots outside the 36: none.** cov2d disclosed 12 more cov2d/t2a-named roots on main:
   cov2d-deploy-cb31611c, cov2d-deploy-a6054769, cov2d-deploy-cf533377, cov2d-crossterms-20261107, cov2d-e3, cov2d-2a,
   cov2d-mumax-20261116, cov2d-clip-20261103, cov2d-clip2-20261103, cov2d-receipt-20261102, cov2d-stage-20261104.sh
   and t2a-20261110. In cov2d's words, these are "deploys or outputs of finished, committed runs", none appears in any
   flux2 path, and "You don't need to add any of these to the protected list for flux2."
   The director ruled that they stay out of the config: adding them is outside the ruling, and flux2 writes only to
   its own root and the /dev/shm clone, both of which the fence checks.
2. **Jobs before flux2 ends:** cov2d has none planned or queued, and will tell limitation-resolver before any submit.
3. **Reads:** reading the three gen2thin flux files and the MINERvA101/opt MParamFiles set is fine. The only file in
   that set that cov2d custody names is the allowed exception.

After the sacct FIX, cov2d re-hashed connect 16494871 and launcher 8b22dd8c and confirmed that the ack stands. The
director accepted it. The read fixes since then changed the connect, fetch and launcher, but not the config, the
fence copy or any path cov2d acked. If the connect starts more than 6 h after 22:05:53Z, a fresh ack is taken first.

## Before the connect

1. The director's binding addendum and GO at these shas.
2. cov2d's ack no older than 6 h at the connect.
3. A cert valid for the job's hour. The connect then runs `bash rpd_flux2_launch.sh connect <new dir> <login node>`.

# RSN connect 1 (2026-11-12), for the director's go

**By** session tier3-design, under RSN-BINDING-1 (#1087) rulings 3 and 4 and RSN-DECLARATION.md rev 3 §6 step 3.
**Connect 1 has not run.** It runs only on the director's go for these exact sha256s, on one login node, at 0 node-h.
It writes neither `fence.txt` nor any job: the director first announces the `rsn_` family to every fenced lane, and
`fence.txt` and J1 belong to a later connect.
<!-- absence-ok: an operational status of this connect's own run, not a claim that a result does not exist -->

| file | sha256 | role |
|---|---|---|
| `rsn_connect1.sh` | `4fbb8f29384eeccb3f5b914ce1b76a47aa84ae89ca5c68095b3b51e0d592caac` | the connect script (what runs on the login node) |
| `rsn_connect1_launch.sh` | `f7cc3c8040c2cd7261c566c71fb17ba1108146a074f971156a4bc6f14f54ae4d` | the Mac-side launcher: the audited HPSS launcher's hop (saul, then a loginNN, accept-new) |
| `smoke_connect1.sh` | `ab00c5bb9abb1fd31096a68dddcc5e337bc07373583f8f3e58ff960af4bbb7f4` | the local smoke harness, committed so the smoke can be rerun (audit low k8) |
| `smoke.txt` | — | the smoke run at these bytes |

**What it does, in order. Any failure is a STOP, and nothing is retried.**
1. **Refusals before anything is written:** the host is not loginNN; a Slurm job is set; `$B` exists; an input is
   missing; an `rsn_` job is queued or running.
2. **The deploy:** a fresh clone at M_RSN `af711298` into `$B/deploy`. HEAD must equal M_RSN, with no modified or
   untracked file, and the nine §7 files must be at their bound sha256s. Every RSN job will name this deploy.
3. **Staging:** the four NC-R inputs are copied into `$OUT/stage` by `os.open(O_RDONLY | O_NOATIME)`. Each copy's
   sha256 must equal its pin:
   - the F1 table `997c7dae…`;
   - S1 `db000707…`;
   - the cpl block `d9aa32fd…`;
   - the flux constraint file `e38ad7d2…`.

   Each source's size, mtime and atime must be unchanged.
   - **Why:** the flux file is an input of the running LL5D gates (cov2d's list of 2026-11-12). Their atime-post
     check STOPped cov2d's AR23 attempt 1 when that file's atime moved (`receipts-cov2d/pseudo/AR23-attempt1/`).
   - The other three are staged the same way, so that no shared input is read plainly.
   - The bound code reads only the copies. Their bytes are identical, so its own sha256 pins hold. Its argument
     values differ from a direct read; its code does not.
4. **rsn_prep**, as declared: `rsn_prep.py --ratios $PVL_PREP/ratios/L-5D-PV --out $OUT/prep`.
   - pv-ladder's frozen prep is not a gate input, and it is archived (#1085).
   - Its sums lines become `$OUT/rsn-prep-SHA256SUMS`. Every listed file must match, and every file but `prep.json`
     must be listed.
5. **The NC-R gate:** `rsn_regrade.py --nominal-only` on the staged inputs writes `$OUT/nc_r.json`. It must record
   `rsn-nc-r/1` and `PASS`.
6. **Ruling 4 (audit low r1):** nc_r.json's recorded code sha256 of `rsn_regrade.py` is printed beside the deployed
   file's and the bound `661608d8…`. All three must be equal.
7. **Printing:** the sums, `prep.json` and `nc_r.json` are printed in full for the receipt PR. The deploy must still
   be clean.

**Paths.**
- `B=/pscratch/sd/j/josephrb/rsn-20261112`, with `$B/deploy` and `OUT=$B/out`.
- The environment is `root_6_28`'s python3, run as `-I -B` with `PYTHONPATH` unset: the environment of the CT-5B
  addition chain that wrote the F1 readout NC-R reproduces. rsn_prep needs only numpy.
- Threads 1, nice 19.

**The smoke** (`smoke.txt`, 11 cases) used stubs for `squeue`, `hostname` and `timeout`. A wrapper stands in for the
bound code, which needs the cluster's inputs. It covers:
- the pass path, with r1 EQUAL and no `fence.txt`;
- STOPs: a read that moves atime, a wrong pin, an r1 mismatch, an unlisted prep file;
- an extra rsn_prep stdout line, which is reported and tolerated;
- refusals that write nothing: a dtn host, a Slurm job set, an `rsn_` job queued, `$B` existing, a missing input.

The launcher stages the script at its pinned sha256 and refuses a dtn node name and a non-empty session directory.
**The real rsn_prep and NC-R run only on the cluster.**

**After connect 1:**
- the receipt PR: the sums, `prep.json`, `nc_r.json` and the session;
- §6's "new pin": J2 and J2n read the committed `nd-unfolding/rsn/rsn-prep-SHA256SUMS` from their deploy, so they
  need a deploy at a commit that adds it. J1 does not.

## CITABLE FOR / NOT CITABLE FOR

- **Citable for:** the connect script, its launcher and their local smoke behaviour.
- **Not citable for:** any prep, NC-R or reading. Nothing has run.

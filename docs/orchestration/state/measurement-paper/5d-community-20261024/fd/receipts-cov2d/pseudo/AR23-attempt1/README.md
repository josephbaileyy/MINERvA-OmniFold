# COV2D: AR23's first pseudo-data job (60860645) STOPPED on step A's atime guard. This is STOP #2, ruled externally caused

**By** the `cov2d` session, 2026-11-05. This is the failed run's receipt, committed as is. Joseph's ruling is in
[`DECISION-20261105-joseph-ar23-stop-external-and-765-phrases.md`](../../../../../../../DECISION-20261105-joseph-ar23-stop-external-and-765-phrases.md)
(#798), with the independent read in `../../../consult-cov2d-ar23-stop-20261105/`.

**MEASURES:** the run's record. **CANNOT AUTHORIZE:** a rerun. The rerun goes under COV2D addendum A2, once the director
has bound it.

This is not `order()`'s record. `PSEUDO_RECORD` (`pseudo/AR23/pseudo_b.json`) stays absent, so `order()` admits no
universe job.

## The STOP count is two

| # | what | date | ruling |
|---|---|---|---|
| 1 | CONTROL-2A FAIL, a writer defect fixed in A1 | 2026-11-03 | under COV2D-BINDING-1 |
| 2 | **this firing**: step A's atime guard on the shared flux constraint | 2026-11-05 | counted, and ruled externally caused by Joseph for this event only |

**Joseph's ruling** (verbatim: "Count it, rule external, continue (Recommended)"). A third STOP of any kind, or any guard
firing on a private (staged) file, ends (c), with no further reclassification. Under the literal rule, ending (c)
here, the paper would have kept "the coverage has not been validated" for the 2D result.
<!-- absence-ok: quotes the paper's existing limitation sentence as the counterfactual the decision requires, not an absence claim -->

## The run

- **The connect** (`connect-ar23-pseudo.sh`, sha256 `f1c712e7…`; log `connect-ar23.log.txt`): run with the director's GO.
  - The deploy was clean at **M = `cb31611ca8b96ed2d1eeb809fda7236e56645863`**, porcelain 0/0 before and after.
  - origin/main was at `e3f76a9c`, and its pilot record is sha256 `b59ffa2d…`.
  - gate: `{"spent": 3.16, "held": 0.0, "want": "pseudo_AR23", "want_node_h": 3.0, "total": 6.16, "cap": 165.8, "pass": true}`.
  - order: `[]`.
  - Submitted at 16:02:44Z as 60860645, TimeLimit 03:00:00, QOS regular_1.
- **sacct** (`end_state.txt`): `FAILED 5:0`, Elapsed 01:12:03 (4,323 s), so **1.20 node-h**.
  - It ran 16:13:57Z to 17:26:00Z on nid005007 (sacct prints node-local time, UTC−8).
  - Exit 5 is `cov2d_pseudo.sbatch`'s step A path: step A returned 3 (STOP), so step B never ran.
- **The job log** (`cov2d-pseudo_AR23-60860645.out.txt`; ROOT's rootmap warnings, printed under MAT, are left in):
  - `UNI-STAT PASS`;
  - `COV2D-PSEUDO-A AR23 STOP natures=301 stops=1`;
  - `STOP atime moved on ['/pscratch/sd/j/josephrb/MINERvA-OmniFold/MINERvA101/opt/etc/MParamFiles/data/FluxConstraints/sorted_NuEConstraint_FHC_RHC_IMD.txt']`.
- **`pseudo_a.json`** (sha256 `9e58194934d79982d9116b988e5abf88c81637f488763ca490e9f91463f3ffa4`, the node's digest in
  `remote_sha256.txt`):
  - verdict STOP. The only stop is that atime move.
  - `atime_moved` lists only the constraint. `$UNI`, `$CV` and AR23's ratio file did not move.
  - Otherwise clean: 301 natures (300 toys and the realization); the director's R1 counts all zero; 36 non-finite reco
    weights zeroed and counted, as for G18; pins checked.
- **Left in place on pscratch:** `$O/pseudo/AR23/a` (305 files). The rerun goes to a new directory, and the sbatch's
  refusal of an existing `$O/pseudo/AR23` stays. There is no `$O/pseudo/AR23/b`. The deploy is unchanged.

## The guard, and what it did not record

`cov2d_pseudo.py` at M:
- **:198–199:** stat the atime of `[$UNI, $CV, constraint, ratio]` at step A's start, 16:14:09Z, before any read.
- **:203:** read the constraint once, through O_NOATIME (`rc.read_noatime`).
- **:332–335:** stat again at step A's end, about 17:26Z. Stop if any value differs.

It compares two stats taken in the same process, against no earlier baseline. **It kept only the list of moved files,
not the values.** `before` and `after` are local, so no record holds the two atimes. A2 makes both guards record them.

## The inferred cause

All of this evidence is stat-only and comes from other lanes' records.
- REF-G1's reader plain-read the file with `read_text()` (`ref_g1_read.py:477-478`; `s1_assemble.py:133-144`), at about
  15:01:52Z (its bars connect) and at 15:18:14Z (its read connect). That's before this job started.
- coverage-5b's login-node stat snapshots show atime 15:01:52Z (1793890912) both at 15:33:38Z and at 16:08:53Z.
- limitation-resolver's stat at 19:34:06Z shows **15:18:14Z** (1793891894), the time of REF-G1's second read.
- No lane's record shows an access in 16:14–17:26Z. A read in that window would stamp a later atime than 15:18:14Z.

**Inferred explanation:** REF-G1's 15:18:14Z read became visible to `stat` only after 16:08, through lazy atime
propagation on Lustre. Step A's start stat then saw 15:01:52Z and its end stat saw 15:18:14Z. The guard reported an
earlier external read surfacing mid-job, not a read during the job.

This is inferred, not measured, for three reasons:
- the guard kept no values;
- the 16:08:53Z → 19:34:06Z sequence comes from other lanes;
- Lustre's atime settings were not measured at the time.
<!-- absence-ok: scopes the inference's evidence (no guard values, no Lustre measurement at the time), as the decision requires the record to state -->

A2's probes (2026-11-05, login02; receipts in A2) found two things:
- `/pscratch`'s mount options carry no noatime, relatime, strictatime or lazytime option.
- The Lustre client (lctl 2.15.7.1) exposes no atime parameter in `llite` or `mdc`. The server-side atime policy (for
  example the MDT's `atime_diff`) cannot be read from a client.

So lazy propagation is consistent with what can be measured, but it was not measured.
<!-- absence-ok: scopes what the record lacks (guard values, Lustre settings), as the decision requires, not a claim a result is absent -->

**What would falsify it:**
- an access to the file in 16:14–17:26Z by anything other than REF-G1's earlier reads; or
- Lustre atime settings that rule out lazy propagation. That is, a stat on another node would see a read immediately.

## Files

- `pseudo_a.json`: step A's record, verbatim.
- `cov2d-pseudo_AR23-60860645.out.txt`: the job log. `*.out` is gitignored, so it has a `.txt` suffix; the bytes are
  unchanged.
- `connect-ar23-pseudo.sh`, `connect-ar23.log.txt`: the connect and its log.
- `end_state.txt`: sacct, the deploy's porcelain and `$O/pseudo/AR23`'s listing, fetched at about 19:40Z.
- `remote_sha256.txt`: the record's and the log's digests, taken on the node. Each equals its file here.
- `removal.log.txt`: `/dev/shm/josephrb-cov2d-ar23.{log,sh}` removed, rc 0 each.

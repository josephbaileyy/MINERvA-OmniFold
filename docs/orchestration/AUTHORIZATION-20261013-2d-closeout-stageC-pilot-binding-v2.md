# AUTHORIZATION 2026-10-13 — 2D closeout: v2 binding addendum to the Stage C pilot grant

**Issued by** the paper-tighten lane, as director. This is the v2 binding that
[`AUTHORIZATION-20261013-2d-closeout-stageC-pilot-recap.md`](AUTHORIZATION-20261013-2d-closeout-stageC-pilot-recap.md)
§4 requires before any job runs under the v2 caps. It supersedes the package row of
[`AUTHORIZATION-20261013-2d-closeout-stageC-pilot-binding.md`](AUTHORIZATION-20261013-2d-closeout-stageC-pilot-binding.md)
§1 for every job launched after v2 deployment. Everything else in that addendum, including §3's naming reuse and §4's
operating conditions, still applies.

**CITABLE FOR:**
- the v2 package, manifest and digests that bind the rest of the pilot;
- the director's acceptance of the coupled `JOBS_SHA` pin change.

**NOT CITABLE FOR:**
- anything the pilot grant and the recap record exclude. It changes no check, threshold, terminal outcome, window or
  namespace, and does not raise the 20.0 node-h ceiling.

## 1. Binding

| item | value |
|---|---|
| package commit | `a2ea0d6a50cc644f5898a2983f953172b2b3904b` on `closeout/stagec-pilot-20261013`: one commit on top of `92b0b466…` (ancestor verified; `origin` ref equals it) |
| manifest | `manifest.json` at that commit, sha256 `bd67d23a90a068e140c9cfa8d21796189415ed0abb73e50dc2b5b37862b57a46` |
| job table | `jobs.tsv`, sha256 `1c30a50b5bf0fd8a8fec25d226113a130cd197847ed2347568f5ac2aefca0182` |
| gate | `launch.py`, sha256 `fa0b01675e2e99aa047b713dc6fdae99c5acce7a841027a5cbd6187ce4d858cf` (`CEILING = 20.0`) |
| dispatcher | `sbatch_pilot.sh`, sha256 `507ff6a114458a58cebf09aceb540ea6e0ac23e2d5c286548f8f05a40e4c93fb` |
| unchanged | producer `74a4ed69…`, `driver_p1.py` `3056e625…`, `driver_g2.py` `eb258cad…`, `omnifold.py` `e9623412…` |

## 2. Director's review of `92b0b466..a2ea0d6a`

The director re-measured each item from `git show` and `git diff`:
- **All four digests** match the closer's report.
- **Diff scope:** six files, all expected:
  - `DESIGN.md`, `jobs.tsv`, `launch.py` and `manifest.json`;
  - the generated `MANIFEST.tsv` row;
  - `sbatch_pilot.sh`, discussed below.
- **`jobs.tsv`** has the same 73 names in the same order. 63 rows differ, only in columns `time` and `enforced_nh`:
  - 60 P1 replicas at 00:58:00 / 0.2417;
  - `G2_on` and `G2_on_s43` at 01:15:00 / 0.6250;
  - `G2_off_s43` at 00:40:00 / 0.3333.

  Each `enforced_nh` equals billing × time / 256 to 4 decimal places. The gate recomputes from `billing` and
  `time`, not from that column (`launch.py` `enforced()`).
- **`launch.py`:** only `CEILING` and its docstring changed, 12.9 → 20.0.
- **`sbatch_pilot.sh`:** only line 21 changed, the `JOBS_SHA` pin, from `54b0abca…` to `1c30a50b…`. The recap
  record's list did not name this file. Accepted: the pin is coupled to `jobs.tsv`, and without it every v2 job
  would refuse at start. This is not a logic change.
- **DESIGN §4** recomputes both walks at the v2 caps and gives the measured upper edge, 18.2901 ≤ 20.0. That agrees
  with the recap record.
  - The median walk still uses the pre-pilot medians, and says it is a floor.
  - The enforced total of all 73 rows is 18.7583.
- **DESIGN §9** cites today's `sacct` rows for each v2 basis and states both launch conditions.

The `P1_unit` retry, job `59740518`, was submitted under the v1 deployment as the recap record §3(a) allows, and
runs there.

## 3. Deployment

Deploy v2 only when both of these hold:
- this addendum is on `origin/main`;
- `squeue -u josephrb` lists no pilot job, pending or running.

Then run `git archive a2ea0d6a50cc644f5898a2983f953172b2b3904b` → `$NS/repo/`, keeping `retries/`, `gatelog/`, `out/`
and `results/`. Verify the four digests in §1 on the deployed copy. After that:
- B4 is subject to the recap record's condition: the `P1_unit` retry passes, and its elapsed × 1.3 ≤ 3,480 s;
- the order is B2 → B3 (conditional) → B4–B7 → B8.

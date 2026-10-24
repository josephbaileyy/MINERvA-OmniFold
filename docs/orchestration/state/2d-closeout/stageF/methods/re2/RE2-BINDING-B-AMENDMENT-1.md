# RE-2 part B binding, amendment 1: deploy the sacct-date fix (2026-10-24)

**By** the paper-tighten lane, as director. **Amends** [`RE2-BINDING-B.md`](RE2-BINDING-B.md) (PR #299).

**What happened.** The bound `re2b_submit.sh` (code `bbd0609a`) stopped at its first gate, before any `sbatch`.
- `sacct -S 2026-10-24` is parsed in local time (PDT). At 06:38Z that start was still in the future, and `sacct`
  refused it.
- No job was submitted and nothing was charged. The queue, `sacct` and `submissions.log` were empty.
- `re2b_readout.sh` had the same line.

**What ran before the stop**, all valid:
- the quota was re-read: 84.8 % before staging, 87.3 % after, within the ≤ 90 % condition;
- the DTN preflight: 12 of 12 inputs matched their declared digests. The record is `partb/preflight/inputs.stat`,
  sha256 `89595b3e6c4ee3dddc77841ef53ef78b7f71aa488bdf8dfb2ca02254173da0fc`.

**The fix**, PR #302, commit `dbdad2f93a255f1bd4bf357951aaa5689aaac512`:
- both scripts use `-S 2026-10-23`, in local time;
- the `re2b-*` job names exist only for part B, so no attempt is missed;
- the director checked the diff: the date and its comments only.

**Amendment.** The bound code commit becomes `dbdad2f93a255f1bd4bf357951aaa5689aaac512` (an ancestor of `main`).
- Jobs deploy a clean checkout at that sha.
- Everything else in RE2-BINDING-B stands: the cap sum, the gate, the order, B9's conditions, B10, B11, and part C.
- The preflight record stays valid, because it does not depend on the code sha.

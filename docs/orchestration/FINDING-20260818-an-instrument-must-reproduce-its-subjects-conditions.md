# An instrument must reproduce its subject's conditions — stricter is a false alarm, looser is a false pass, and neither shows in its output

**Lane E, 2026-08-18. `BEN-474`.** Two verification scripts, written hours apart for different purposes,
failed the same way: **they ran under conditions the thing they were checking does not have.** One was looser
than its subject and passed vacuously. The other was stricter and failed three times on a healthy system. Both
printed exactly what a correct run prints.

## The false pass — a check that could not fail

`gen_manifest_run_bound_addendum.py` exists to satisfy one condition: *the run-bound predictions must be
recorded before any artifact they predict exists.* Its refusal is what turns that from a promise into a check.

I ran it **from the local checkout against a family root on `/pscratch`** — a path that does not exist on that
filesystem. `existing_artifacts()` walks replica directories and skips any that are not directories, so an
absent root yields zero artifacts and **the refusal cannot fire.**

The cluster-side state happened to be clean — verified separately: root present, zero products, array still
PENDING — **so the claim was true. It was true by timing, not because the check established it.** The whole
purpose of the check is to tell those two apart, and from the wrong host it cannot.

**Repair:** refuse if the family root is not a directory *from here*, plus a `--repo` argument so the script
can execute where the root is visible without living inside the repository it reads. Deriving the repo from
`__file__` alone had *forced* the two to be co-located, which is what put the first run on the wrong host.

## The false alarms — a check stricter than its subject, three times

`check_activator_paths.sh` began as a full activation smoke: source the job's environment in a clean shell and
assert it comes up. It failed on a healthy environment three times, each time because **I imposed a condition
the job does not have**:

1. **`set -u` inside the check.** The launcher uses `set -eo pipefail` and *not* `-u` (line 15), and conda's
   own `activate-binutils_linux-64.sh` references unbound variables. My check was stricter than the job.
2. **`env -i`.** The controller submits `--export=ALL,…`, so tasks inherit the submitting shell. A bare
   environment is not what the job has.
3. **Even corrected**, `ADDR2LINE: unbound variable` kills a fresh non-interactive shell — and is
   demonstrably **not** fatal in the real tasks: **2 of generation one's 50 emitted it and COMPLETED.**

That third fact is the decisive one, and it exists only because I looked at the **historical population**
rather than at my own shell. Without it I would have concluded the environment was broken and spent hours on
a non-defect.

**Repair:** the pass/fail condition became the deterministic, encodable property — *does every path the
activator resolves against its own directory exist from this data root* — and activation is attempted and
reported as INFO. **A gate that fails on a healthy system is worse than no gate**, because an over-reporting
check gets switched off exactly as fast as an under-reporting one gets trusted.

## The symmetry, which is the finding

|  | instrument vs subject | symptom | how it hides |
|---|---|---|---|
| addendum | **looser** (no filesystem to check) | PASS | indistinguishable from a real pass |
| activation smoke | **stricter** (`-u`, `env -i`) | FAIL | looks like a real defect in the subject |

> **An instrument's conditions are part of the measurement. If they differ from the subject's, the output is
> about the instrument.**

And the two directions are not equally dangerous but they *are* equally invisible: nothing in either output
names the discrepancy. The looser one is worse — it licenses action — but the stricter one is more likely to
get the check deleted, which then licenses the same action later with no check at all.

## Why "run it where it runs" is the operative rule

Both repairs reduce to the same instruction, and it is cheap:

- **Run the check on the host, in the shell, and with the environment the subject will have.** Not `env -i`
  unless the subject has `env -i`; not from a laptop against a cluster path; not with stricter shell options
  than the launcher sets.
- **When you cannot reproduce the conditions, narrow the claim rather than widening the check.** The
  activation gate could not be made faithful, so it stopped being a gate and became an INFO line beside a
  property that *can* be checked faithfully. Naming the scope beats shipping a flaky gate.
- **Prefer the historical population to your own shell** when asking whether something is fatal. Two of fifty
  tasks answered a question my login shell answered wrongly.

## The check to steal

Before trusting any verification script's verdict, ask: **could this have failed, here, today?** If the answer
needs the subject's host, environment, or shell options, and this run did not have them, the verdict is about
the run.

**Cross-references.** `BEN-470` (the first end-to-end run refutes your model of the system — same session, the
composition rather than the conditions), `BEN-418` (checks that matched their own explanatory prose),
`BEN-415`/`BEN-417` (a green verdict over a population smaller than it appears), `BEN-258` amendment 1 (a live
guard that has never fired is unverified — the addendum's refusal was exactly that until it was run somewhere
it could fire).

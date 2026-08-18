# A relay is not a neutral pipe: it launders a hypothesis into a campaign fact

**Mediator, 2026-08-18. `BEN-305`.** Twice in about an hour I took a claim from lane B, restated it in my own
words, and forwarded it to Joseph as fact. Both times I had the means to check it and did not. Both times the
claim was materially wrong. This is a finding about the **relay**, not about the lane — B's origination error is
its own row, and B offered to absorb both, which I declined.

## Instance 1 — a safety claim, refuted by a six-line file

B wrote to me: *"IT WRITES NOTHING. Read-only by construction, not by intention"*, and its module docstring said
`python3`/`sbatch` were stubbed so there was no real work and no submission. I forwarded this to Joseph as
*"CPU-only, seconds, writes nothing"*.

On the cluster it was false. The stubs were installed as **PATH shims**, and every launcher's first executable
line is `REPO=...; source "${REPO}/setup_salloc_env.sh"`, whose `conda activate` **prepends** the environment's
`bin` and displaces them. Demonstrated directly rather than inferred:

```
before: /tmp/tmp.u8DMim0Bcy/python3                 <- the probe's shim
after:  ~/.conda/envs/root_6_28/bin/python3         <- after sourcing the activator
```

Consequences, in order of severity:

- A **real unfold ran on a login node**, across two runs; an orphan from the first survived my initial kill and
  had been running ~15 minutes.
- **`sbatch` was equally unstubbed.** Nothing was submitted only because these seven launchers happen not to
  invoke it. The read-only property rested on that accident, not on the stub.
- **Nothing was written only because `mkdir` was a shell *function***, which survives the activation where a PATH
  shim does not. The stub that protected the canonical tree is the one that happened to use the surviving
  mechanism. Had B been consistent and used PATH throughout, a real product would have landed in the canonical
  tree under a member path, from a run everyone was calling read-only.

**The refuting evidence was `pre.sh` — six lines, one command.** I read it only after the second hang, at which
point the missing `python3` stub was visible immediately.

## Instance 2 — a synthesis, refuted by measurement

B wrote: *"the campaign's hard rules are enforced in the libraries and bypassed in the Python."* I relayed it to
Joseph as the day's most useful generalisation and endorsed it as the headline for a repo finding.

An audit lane measured it by AST over all **467** tracked `.py` at `origin/main`, 0 parse errors: **exactly two
instances** of the full shape (`sweep_bank_5d.py:216` and its character-identical 4D sibling `sweep_bank.py:204`),
out of 77 candidates. Not a language-wide bypass. And the remedy already exists in-repo —
`nd-unfolding/pet/atomic_write.py`, written for this defect class, whose `completion_marker_path` docstring says
it writes *"the marker `lib/resume_guard.sh` looks for"* — with **zero callers in the `nd-unfolding/` root
covariance chain**.

B's account of the origin is the better half and belongs to its row, not this one: *"I had n=2 and reached for the
widest sentence covering both."*

## The two errors are independent

Originating a claim too wide from real data, and amplifying a claim without checking it, are **different acts by
different parties**. B's error came first and mine could only have caught it. That ordering does not merge them:
a relay that forwards without checking is a second, independent failure, and it is the one that determines whether
the claim reaches the person making decisions.

## Why the relay is the dangerous step

A lane's claim arrives carrying its context — the hedges, the sample size, the environment it was tested in, the
phrase *"by construction"* that should prompt *"in which environments has the construction been exercised?"*.
**Restating it in the orchestrator's own voice strips exactly that.** What reaches the reader is a clean sentence
with no attached doubt, and the reader has no way to reconstruct what was removed.

And the compounding is **social, not only inferential**: the more law-like a sentence sounds, the less likely
anyone is to ask for its evidence. So the sentences most in need of testing are the ones least likely to get it.
Instance 2 is exactly this — it sounded like a repo invariant, which is why it was relayed as a headline and why
nobody asked for its `n`.

## The rule

Before forwarding a lane's claim as fact, do one of:

- **(a)** run the *one command* that checks it; or
- **(b)** forward it **attributed and unverified**, naming what would check it.

**Never (c): restate it in your own voice.** (c) is the step that converts a hypothesis into a fact, and it is the
only one of the three that feels like ordinary summarising — which is why it is the default and why it needs a
named prohibition rather than a reminder to be careful.

Both instances here were (c). Both were cheap to make (a): six lines of `pre.sh`; one AST scan an audit lane ran
in a single dispatch.

## How each was caught

Neither was caught by an instrument.

- Instance 1: by reading `ps` during what looked like a hang. B's probe printed one flushed line per case
  (`START` before `DONE`) because of the quiet-log finding `BEN-028`, and that is the only reason I looked at the
  process table instead of waiting. The payout came in a direction `BEN-028` did not anticipate — a quiet stream
  that was neither a dead job nor a healthy one, but **a job doing something nobody had authorised**.
- Instance 2: by commissioning a lane to **test** the synthesis rather than apply it. The dispatch said so
  explicitly, and the answer came back refuting it.

The second is the generalisable one: when a claim is about to become a headline, the cheap move is to commission
its test, not its application.

## Related

`BEN-452` (a probe that forces a guard false cannot test that guard — instance 1 is its structure one level up:
locally the stubs fire, so every local run confirms them, and the one environment where they are defeated is the
only environment the probe is for). `BEN-464` (independent non-Claude reviewers found what five Claude lanes
missed). `BEN-481` (the detector whose walk covers two languages and whose matcher and power fixture cover one).
`BEN-300`, `BEN-304` (this lane's earlier rows, both about dispatching on unverified state).

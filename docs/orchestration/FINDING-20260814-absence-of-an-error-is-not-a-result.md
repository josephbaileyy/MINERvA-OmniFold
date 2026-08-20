# FINDING 2026-08-14 — an operation that reports nothing has told you nothing

**BEN-251.** Lane D (verifier). **Three instances in one evening, on three different tools.** Filed
at this level of generality rather than as a Slurm note because the general form would have caught
the `git` one too, and a per-tool caution would not have.

> **An operation that returns silently has not told you it succeeded. The absence of an error is
> not a result.** Read the resulting state, field by field, against what you asked for.

## The three

**1. `git push` — a `fatal` immediately followed by a success line.**

```
error: RPC failed; HTTP 400 curl 22 The requested URL returned error: 400
send-pack: unexpected disconnect while reading sideband packet
fatal: the remote end hung up unexpectedly
Everything up-to-date
```

`Everything up-to-date` is the **last** line and reads as the outcome. The push had not landed;
`origin/main` was two commits behind. Caught by `git rev-parse origin/main`, not by the output. The
cause was a 1 MB binary against the default `http.postBuffer`; the fix was one flag. **The danger
was never the failure — it was the green tail on it.**

**2. `scontrol update` — three commands, zero output, three different outcomes.**

| command | printed | did |
|---|---|---|
| `MinMemoryNode=196608` | nothing | **applied** |
| `QOS=shared` | nothing | **silently misfired** → landed in `QOS=debug` |
| `Partition=shared_milan_ss11` | nothing | **silently refused**, twice |

One applied, one ignored, one actively harmful, and **no way to tell them apart from the return.**

**3. The QOS downgrade, which is the dangerous one and is directional.**

Changing `QOS` while the job is still in an incompatible partition does not error. It resolves to
`debug`:

```
QOS=debug   Reason=QOSMaxWallDurationPerJobLimit   TimeLimit=06:00:00
```

A 6-hour job in `debug` QOS **can never start.** The job went from "queued behind everything" to
"permanently ineligible" with nothing printed at all.

> **Ordering rule: move the partition first, then the QOS.** The reverse silently strands the job.

## Two facts worth separating from the caution

- **QOS changes reset priority accrual; memory changes do not.** Measured: `68119 → 66679` (the
  submit-time base) across the QOS churn, while `MinMemoryNode` landed clean and cost nothing. This
  is the useful version — a blanket "`scontrol update` loses your queue age" would be false.
- **A user can raise their own nice and cannot lower it.** So a nice set for a reason that later
  expires can only be removed by resubmitting. Nothing in Slurm retires a nice value when its
  justification dies.

## Why the general form is the one to keep

Each instance has an obvious per-tool lesson — pass `--porcelain`, check `scontrol show job`, read
the Slurm QOS table. **None of those three lessons generalises to the other two.** What does
generalise is the shape: a mutating operation whose success and failure are indistinguishable from
its output, where the natural reading of silence is "fine."

This is the same family as the campaign's verification findings, one layer down. `BEN-250` is a
*check* that could not fail; these are *operations* that could not report. In both cases the
artifact everyone reads — a green line, an empty return — is disconnected from the property it
appears to attest.

**The habit that caught all three was the same one:** after any mutating operation, read the state
back from the system rather than from the command's own account of itself.

## Attribution

The `scontrol update` route was the mediator's recommendation, made to preserve nine hours of queue
age — and **the QOS churn is what destroyed the age it was written to protect**, as well as
stranding the job in `debug` for an interval. The mediator has recorded that as theirs. It is noted
here only because the finding is *about* silent operations, and an instruction that backfires
silently is the same shape one level up.

## Environment note

The lane sessions are being killed by host memory pressure (16 GB, swap 93% full; all four lanes
died and respawned within the same second at 18:20:24). **Assume a session can vanish between any
two tool calls.** That makes commit-then-verify not merely good practice here but the only way work
survives, and it is why the `git push` instance above mattered: an unverified push is
indistinguishable from a lost session.

## AMENDMENT 2026-08-20 — a fourth instance, and the silence was CONFIGURED SOMEWHERE ELSE

The three instances above are tools that *say nothing by nature*. This one is worse, because the tool
had plenty to say and a **config setting made for an unrelated purpose suppressed it.**

`ssh saul.nersc.gov` had been recorded as *"exits 255"* since `2026-08-19T13:00Z`, in `OI-135`, in
`LIVE-STATE.md`, and by three separate parties. Every one of those probes returned an exit status and
**no text at all**, so the cause was attributed — reasonably, and as it happens correctly — to
`maintenance_20260819`. Nobody had the server's own statement, because `~/.ssh/config:40` sets
`LogLevel QUIET` for `Host dtn*.nersc.gov perlmutter*.nersc.gov *.nersc.gov`, which is there for
**connection-noise reduction** and has nothing to do with diagnostics.

Re-probed at `2026-08-20T04:5xZ` with `-o LogLevel=DEBUG1`, the same command prints the answer:

    Perlmutter is currently down for maintenance.
    Received disconnect from 128.55.126.2 port 22:2: Too many authentication failures

**So an empty 255 was never evidence about the cluster; it was evidence about the log level.** The
attribution happened to be right, which is exactly why this survived a day — a silent instrument that
agrees with your hypothesis is indistinguishable from a working one.

### The near-miss that makes the point

The mediator, probing at `2026-08-20T04:51Z`, found `~/.ssh/nersc-cert.pub` **expired**
(`Valid: from 2026-08-18T19:50:00 to 2026-08-19T19:51:37`) and was one step from telling Joseph to
re-run `sshproxy.sh` — a wrong instruction that would have burned a round-trip with an away user and
left the real blocker in place. What stopped it was **reading the config file rather than reasoning
about it**: `~/.ssh/config:19-22` already records, from a prior verification, that

> this account authenticates to Perlmutter with the PLAIN key `~/.ssh/nersc` (verified: no cert
> offered, no `~/.ssh/authorized_keys` on the cluster, so the key is registered centrally), which
> does not expire -- so cert lifetime is not the usual failure mode here **despite appearances**.

Confirmed by measurement rather than by trusting the comment: with `CertificateFile=none`,
`IdentityAgent=none`, `IdentitiesOnly=yes` and the plain key alone, ssh **still** exits 255. The
expired cert is real, is present, and is **not the cause** — recorded here so nobody re-raises it.

*The phrase "despite appearances" was written by whoever verified it, for precisely this reader. A
prior session's warning was worth more than the fresh, true, irrelevant measurement.*

### The executable remedy

**An `ssh` exit status quoted as evidence must come from a probe the server can speak through.**
`LogLevel QUIET` is correct for the multiplexed working connections and wrong for any probe whose
output becomes a record. Probe with `-o LogLevel=DEBUG1` (or `ERROR`) and quote the server's line, or
write `255, reason not captured` — never `255` bare, which reads as an attributed finding and is not one.

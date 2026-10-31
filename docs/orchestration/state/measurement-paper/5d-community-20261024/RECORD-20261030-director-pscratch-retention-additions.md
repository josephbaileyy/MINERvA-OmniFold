# RECORD: pscratch retention-list additions (2026-10-30)

**By** the paper-tighten lane, as director. It adds the run directories created since
[`FD-PSCRATCH-RETENTION-PROPOSAL.md`](FD-PSCRATCH-RETENTION-PROPOSAL.md) to the pscratch retention list. Their bindings
already named each one for the list. **It deletes nothing.** Retention decisions stay as
`DECISION-20261029-joseph-retention-archive-a1.md` set them: nothing on the list is removed without a recorded decision.

**Measured** with `du -sh` on `saul.nersc.gov`, read-only, on 2026-10-30, under `/pscratch/sd/j/josephrb/`:

| directory | size | what it holds | named by |
|---|---:|---|---|
| `fd-ct-3b-20261029` | 1.1G | the 3b deploy and run; closures also on HPSS (`mnv-5d-ct-3b-closures-20261029`) | FD-CT-3B-BINDING §3.5 |
| `fd-ct-5b-20261030` | 18G | the 5B deploy, period merges, dumps and 34 unfolds; small products on HPSS (`mnv-5d-ct-5b-20261030`) | FD-CT-5B-BINDING §2.9 |
| `fd-ct-5b-dev-20261030` | 1.1G | 5B's pre-binding test clone | FD-CT-5B-DECLARATION §7 item 9 |
| `fd-ct-5b-audit-20261030` | 1.1G | the 5B audit's deploy and readout | FD-CT-5B-AUDIT-BINDING |
| `oi74-ff-20261030` | 188K | the canonical checkout's set-aside files (two live-state files, four untracked files), with SHA256SUMS | state/oi74-canonical-ff-20261030/BINDING-2.md |
| `fd-ct-readers-20261028` | 1.1G | the 3a/4C/5A deploy and readouts | FD-CT-READERS-BINDING §3.5 |
| `fd-ct-readers-am1-20261029` | 1.1G | the 5A rerun at amendment 1 | FD-CT-READERS-BINDING-AMENDMENT-1 §3.4 |
| `fd-f1-20261027` | 9.0G | F1's deploy and products; HPSS copy per FD-F1-REPORT | FD-F1-BINDING §4.9 |
| `fd-flux-boot-20261027` | 1009M | the 3D flux-bootstrap run | FD-FLUX-BOOT-BINDING §3.5 |

**Purge exposure:** NERSC's 8-week rule makes these exposed from about 2026-12-22 at the earliest, by last access. That
is an estimate from today's date. Access times were not read.

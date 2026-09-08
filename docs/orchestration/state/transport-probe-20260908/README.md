# Transport probe — authenticated read under campaignctl's sanitised environment

**Evidence only. This arms nothing, admits nothing, and writes nothing to any remote.**

## The bounded claim

**Established:** on Perlmutter, under `campaignctl.git_environment()`, `git ls-remote` over the
**scp SSH spelling** `git@github.com:josephbaileyy/MINERvA-OmniFold` returns `rc=0` and the
correct ref. GitHub offers **no anonymous SSH**, so `rc=0` on that spelling means the existing
key authenticated *inside the sanitised environment* — which is the thing an ordinary-shell
`ssh -T` does not establish and which an earlier claim of mine rested on by mistake.

**NOT established: write capability.** No push was attempted, by decision: a real push to the
campaign namespace is an admission write. Whether the admission compare-and-swap would succeed
over SSH is **unverified**, and this receipt must not be read as evidence that it would.

**The `https` row proves less than it looks.** `rc=0` there is anonymous read on a public
repository. Under the same sanitised environment a `--dry-run` push over HTTPS fails with
`could not read Username for 'https://github.com'`, because the only credentials on the
available hosts live in scopes campaignctl disables — `GIT_CONFIG_NOSYSTEM=1` for the system
file and `GIT_CONFIG_GLOBAL=/dev/null` for `~/.gitconfig`.

## What was measured

| file | sha256 |
|---|---|
| `ls-remote-under-git-environment.log` | `0a9a80d86389946cbe637c104ae6040e44bb03de25080e869a78fe2432665d70` |
| `probe.sh` | `bd2a98c2ed373c3382e5ba725f0ada8fc840d424cd6846e09f295fdf59c5dae2` |

`probe.sh` is the exact source as run. The log's first line records
`campaignctl.git_environment present: True`, so the environment is the module's **own**
function, not a reconstruction from its constants — the probe carries a fallback that
reconstructs from `GIT_INJECTING_ENVIRONMENT` and `GIT_ISOLATED_CONFIGURATION_ENVIRONMENT`,
and that fallback did not fire.

Environment as observed: `HOME` present, `SSH_AUTH_SOCK` present, `GIT_CONFIG_GLOBAL=/dev/null`,
`GIT_CONFIG_NOSYSTEM=1`. That combination is why SSH works and a global credential helper does
not: `ssh` reads `~/.ssh/*`, which campaignctl does not touch, while both git config file
scopes are pointed at nothing.

## Pin the capture, not the repository

Taken `2026-09-07T23:05:08Z`, with `refs/heads/main` at
`8c939996cab973dc0ea84296c11ab5aa244d3acd`. `main` has moved since. The ref value here is part
of the observation, not a current fact about the repository.

## No credentials

Neither file contains a token, key, or secret. The log records return codes, ref shas, and
environment-variable **presence** — never values.


## ⚠ NARROWING, 2026-09-08 — "this proves authenticated read" was the integration lane's overreach

**Added by the integration lane, correcting its own wording, on Joseph's ruling of 2026-09-08.** The
overstatement is in that lane's pin merge commit body, which is history and is not rewritten; this is
the correction, placed where the evidence is rather than where the claim was.

**What is established.** Two things, and they are narrower than the sentence they were reported as:

1. **Reachability.** `ls-remote` returned `rc=0` with the correct ref.
2. **A LOCAL precondition.** The refusal this pin cleared —
   *"a clone whose origin is a different repository is a different repository"* — is raised by
   `campaignctl.py:1583`, a **string comparison** between `checkout_origin_urls()` (which reads `git
   config`) and the pin. **No transport is reached before it raises.** So clearing that refusal proves
   a local precondition now passes. That is strictly narrower than proving a read authenticated.

**Why `rc=0` is not by itself a credential proof.** Measured on the integration host: an HTTPS
`ls-remote` against this origin with `credential.helper=` emptied and `GIT_TERMINAL_PROMPT=0` returns
`rc=0` and the correct ref. This repository is public, so **that read path is anonymous** and its exit
code exercises no credential. (The cluster read used the **scp SSH** spelling, for which GitHub offers
no anonymous access — that is the preflight lane's measurement and is recorded as theirs, not
re-derived here.)

**The gap that remains, and it is a gap by construction.** Every read taken so far has been against
`refs/campaign/*`, which was **observed empty at every reading taken so far**. (An earlier version of
this sentence said the namespace *cannot* be non-empty because nothing has ever staged an item. That
asserted more than any observation here supports — never-created and created-then-emptied are
indistinguishable from these reads, and it is the same unevidenced form struck from the section
below. Corrected here rather than left for the correction below to carry alone.) A zero row count
therefore has **no positive control**: it cannot distinguish *"the namespace is
empty"* from *"the probe did not look."* Partial credit where it is due: `campaignctl.remote_head()`
(`:1965-1983`) **raises** on a nonzero `ls-remote` exit, for the reason its module docstring gives at
`:92` — *"a queue that cannot read them cannot tell an empty campaign from a full one"* — so the code
already closes the blind-read half of this hazard. What is missing is the other half.

**The fix, and it costs nothing.** Perform one read **against a ref that EXISTS on that origin**,
through the queue gitdir's own config and credential helper. **A nonzero row count is the positive
control for authenticated read.** Owner: the lane with cluster access. Until that exists, this
directory proves reachability and a local precondition, and should not be cited for more.

**The positive control that section asks for was taken, and it is the section below.** One
correction carries across both: "cannot be non-empty yet" and "nothing has ever staged an
item" are not established by an `ls-remote`, which shows current state only. The evidenced
form is observed absence at a recorded time; that supersedes the earlier phrasing wherever it
appears above, and the wording above is left as its author wrote it.

## Positive control — 2026-09-07T23:48:05Z

Every campaign read taken until now was against `refs/campaign/*`, and every one returned zero
rows. A zero row count on its own cannot separate *"the namespace is empty"* from *"the probe
did not look"*. Review named that, having written the same rule to me earlier the same day
about presence censuses — pair every "found nothing" with a control whose absence would be
impossible.

**Two `ls-remote` invocations**, one per namespace, under the same
`campaignctl.git_environment()` and the same pinned SSH URL, driven by one Python parent as two
Git subprocesses. The source loops `subprocess.run`; an earlier revision of this section called
it a single invocation, which its own `positive-control-probe.sh` contradicts.

```
url (the pin): git@github.com:josephbaileyy/MINERvA-OmniFold
refs/heads/*     rc=0  rows=20
refs/campaign/*  rc=0  rows=0
```

**Twenty rows is the control.** Same environment, same URL, **same Python parent driving two
Git subprocesses**, seconds apart: the
read demonstrably returns data when data exists, so the zero on `refs/campaign/*` is a measured
absence rather than a blind read. Two invocations rather than one is a real weakening — control
and subject are not literally the same call — but they share the configured environment and
URL; these observations establish authenticated reads at the recorded time, not write
capability. And because the URL is the scp SSH spelling, against which
GitHub offers no anonymous access, `rc=0` with rows here does carry the credential proof that
an `rc=0` over public HTTPS does not.

**Two limits on this, stated rather than left to be found.**

1. **It did not route through the queue's own git directory.** `~/.campaignctl/queue-git` was
   **observed absent at `2026-09-07T23:48:05Z`**. Why it is absent is not evidenced here:
   never created, or created and removed, are indistinguishable from this observation. So this
   measures the environment and the URL, not that gitdir's own config and credential helper,
   and that routing stays untestable while no queue directory exists.
2. **It still says nothing about writes.** A push to `refs/campaign/<KEY>/queue` *is* the
   admission write; probing it would perform the act the gate exists to control. Write
   capability remains **NOT ESTABLISHED and DELIBERATELY UNPROBED**, and the first real write
   will be an authorized staging.

Raw output in `positive-control.log`, source in `positive-control-probe.sh`.

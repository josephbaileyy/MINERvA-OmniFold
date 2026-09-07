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

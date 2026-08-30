# RUNBOOK — campaign status dashboard (collector, scrontab, local viewer)

**What this is.** A glanceable status page for the MINERvA-OmniFold campaign: what is queued or
running on Perlmutter, what the tmux/LLM-orchestration sessions are doing, and what may honestly be
said about when things finish. Three files:

| File | Role |
|---|---|
| [`dashboard_collector.py`](dashboard_collector.py) | Runs on a login node under `scrontab`; writes one self-describing `status.json`. |
| [`dashboard.html`](dashboard.html) | One static file, no build step, renders `status.json` and auto-refreshes. |
| [`dashboard_serve.py`](dashboard_serve.py) | Serves the page on your laptop, reading `status.json` over SSH. Nothing is published. |
| [`test_dashboard_serve.py`](test_dashboard_serve.py) | 12 tests for the viewer and the tailnet binding. |
| [`test_dashboard_collector.py`](test_dashboard_collector.py) | 57 tests; `/usr/bin/python3.11 -m unittest test_dashboard_collector`. |

**What it deliberately cannot tell you.** It does not predict completion times, it does not claim a
job is running because a job exists, and it never reports a login node as session-free when that node
could not be reached. Each of those is a measured failure mode, recorded below.

---

## 1. Setup you have to run yourself

### 1a. Delivery — the science gateway is DECLINED

**Decision, Joseph, 2026-08-30: do not create `/global/cfs/cdirs/m3246/www`.** The reason is that
the project web space is a group resource, and standing it up for a personal dashboard is not this
lane's call to make. The stronger form of the objection, which the measurements support: creating
`www` does not merely occupy a directory, it **switches on public web serving for the whole
project** — every probe below returned `200` to a laptop with no credential, no VPN and no NERSC
login, and the portal generates directory listings, so afterwards anything any group member drops
under `www` is world-readable whether or not they realise it. That is a posture change for
everyone in m3246, and it needs the PI, not a dashboard.

The investigation is kept because it answers the question if the group ever *does* want a gateway:

| Probe | Result | Meaning |
|---|---|---|
| `curl https://portal.nersc.gov/cfs/act/` (`www` is `drwxrwxr-x`) | `200` | Serving is automatic; no ticket, no NERSC action. 338 projects have a `www`. |
| `curl https://portal.nersc.gov/cfs/callat/` (`www` is `drwxr-s---`) | `403` | World read+execute is required. |
| `curl https://portal.nersc.gov/cfs/m3246/` (no `www`) | `403` | Only the directory is missing. |
| `curl https://portal.nersc.gov/cfs/act/dr6_data/` (no `index.html`) | `200`, `<title>Index of…` | **The portal lists directories**, so an "unguessable" subdirectory is not secret unless every parent has an `index.html`. |
| `curl https://portal.nersc.gov/~josephrb/` | `404` | There is no per-user NERSC web space to use instead. |

**What is used instead.** The collector writes to a private path on the cluster and nothing is
published:

```
/pscratch/sd/j/josephrb/MINERvA-OmniFold/docs/orchestration/state/dashboard/status.json
```

That path is gitignored (regenerated every 5 minutes) and is outside `state/waker/`, which the
collector refuses to write into because it holds `notification-secrets.json`.

[`dashboard_serve.py`](dashboard_serve.py) then serves the page **on your laptop**, reading the
snapshot over SSH on each refresh:

```bash
cd docs/orchestration      # a local checkout; dashboard.html must sit beside the script
python3 dashboard_serve.py            # http://127.0.0.1:8899
```

It fails loudly at startup if the snapshot cannot be read, rather than serving a page that 502s
forever. There is no local cache and no polling loop: the only copy is the one on the cluster, so
the page cannot show a file that outlived the thing that produced it. With the `ControlMaster` in
`~/.ssh/config` each refresh costs well under a second.

**Phone — Tailscale (set up 2026-08-30).** Alerts already work with no further setup (§1c); this is
the *glancing* path. Run the viewer with `--tailscale`:

```bash
cd docs/orchestration
python3 dashboard_serve.py --tailscale
```

It prints the URL to open on the phone:

```
tailnet tail29db9c.ts.net:
  iphone-14 (iOS): online
snapshot OK (20582 bytes) from saul.nersc.gov
serving on the tailnet only (not on any other network):
  http://josephs-macbook-pro-2.tail29db9c.ts.net:8899/       <- open this on the phone
  http://100.69.110.31:8899/
```

`--tailscale` binds to the tailnet IPv4 **specifically**, not to `0.0.0.0`. That is the whole point
of preferring it: this server has no authentication, so the interface it listens on *is* the access
control. Verified by measurement, both directions:

| Probe | Result |
|---|---|
| `curl http://100.69.110.31:8899/` (tailnet IP) | `200` |
| `curl http://josephs-macbook-pro-2.tail29db9c.ts.net:8899/` (MagicDNS) | `200` |
| `curl http://127.0.0.1:8899/` | **refused** |
| `curl http://10.119.0.38:8899/` (laptop LAN address) | **refused** |

So joining an untrusted network does not expose the page. Tailscale carries it over WireGuard, so
plain HTTP is encrypted in transit — which is *not* true of `--bind 0.0.0.0` on an ordinary LAN.
HTTPS via `tailscale serve` is not used: this tailnet reports `CertDomains: None`, i.e. HTTPS
certificates are not enabled, and enabling them is a tailnet-wide admin change that buys nothing
here because the transport is already encrypted.

Two things that look broken and are not:

- **`tailscale ping iphone-14` times out, and the phone can show as offline.** iOS suspends the
  Tailscale client when the app is backgrounded; it stops answering pings but still brings the
  tunnel up the moment the phone initiates a connection. Measured within one minute: the same phone
  reported `Online: true`, then `0 devices online`, then online again. The startup banner says this
  in words rather than printing a bare count, so a sleeping phone does not read as a broken tailnet.
- **The laptop must be awake and running the viewer.** This is the cost of not publishing: there is
  no cluster-side web endpoint, so if the laptop is asleep the phone gets nothing. Alerts still
  arrive, because those are pushed from the cluster by `notifyctl`.

The page costs one `ssh <host> cat` per refresh, measured at ~1.3 s with the `ControlMaster` warm.

### 1b. Install the scrontab entry

Print the block rather than letting a tool rewrite your table:

```bash
cd /pscratch/sd/j/josephrb/MINERvA-OmniFold/docs/orchestration
/usr/bin/python3.11 dashboard_collector.py --print-scrontab \
    --state-dir /pscratch/sd/j/josephrb/MINERvA-OmniFold/docs/orchestration/state/waker \
    --out .../state/dashboard/status.json      # this is already the default
```

It emits, with its own markers so that `wakerctl install-cron` — which strips only
`# BEGIN/END wakerctl managed block` — leaves it alone (there is a test for this):

```
# BEGIN mnv-dashboard managed block
#SCRON -q cron
#SCRON -t 00:20:00
#SCRON -o .../state/waker/logs/dashboard-collector.log
#SCRON --open-mode=append
*/5 * * * * /usr/bin/python3.11 .../dashboard_collector.py --state-dir ... --out ... --alert
# END mnv-dashboard managed block
```

**Follow the [`ISSUE-42`](../known-issues/ISSUE-42-wakerctl-install-cron-fail-open.md) procedure —
it is not optional.** `scrontab <file>` replaces the *entire* table, so a mistake deletes the waker's
block and any other lane's entries:

```bash
scrontab -l > ~/scrontab.$(date +%Y%m%dT%H%M%S).bak; echo "rc=$?"   # rc MUST be 0
scrontab -e                                                        # paste the block, keep everything else
scrontab -l | diff ~/scrontab.*.bak -                              # ONLY the new block may differ
```

**On the walltime.** The `cron` *partition* allows `MaxTime=90-00:00:00`, but the `cron` *QOS* caps
`MaxWall` at `1-00:00:00`, so a 90-day request is rejected. A collection takes ~8–12 s; `00:20:00`
means a wedged ssh sweep is killed rather than holding the slot. (`wakerctl` asks for `12:00:00`
because one of its ticks can dispatch a whole LLM turn. This collector never does.)

### 1c. Alerts (optional)

The collector reuses `notifyctl.py` — it does not talk to ntfy itself, so the topic secret, the
`0600` mode check, the channel config and the sent-marker de-duplication stay in one place.

```bash
/usr/bin/python3.11 dashboard_collector.py --state-dir state/waker \
    --out /tmp/status.json --alert-dry-run      # prints subjects and keys, sends nothing
```

It alerts on: an unreadable tick receipt, a ticker stale beyond 30 min, any job in `ERROR`, any
failed source, and coverage below 60 % of login nodes. It does **not** alert on the routine 31/40
sweep — an alert that fires every time is one you learn to ignore. Keys are bucketed into a 6 h
window (`--alert-window-seconds`), so a condition re-alerts at most every 6 h instead of once ever
(a fixed key) or every 5 min (a per-tick key). Subjects are self-contained and path-free because
`notification-config.json` sets `include_body: false` — only the subject crosses the public ntfy
topic.

---

## 2. Verifying it works

```bash
cd /pscratch/sd/j/josephrb/MINERvA-OmniFold/docs/orchestration
/usr/bin/python3.11 -m unittest test_dashboard_collector      # 57 tests
/usr/bin/python3.11 dashboard_collector.py --state-dir state/waker --out /tmp/status.json
```

A healthy run prints e.g. `wrote /tmp/status.json (4 jobs, 31/40 nodes)`. Then confirm the page shows
a **non-happy** path too, which is the only way to know the honesty machinery is wired: point the
page at a snapshot with `sources[].ok = false` and confirm the affected panels read
**"not measured"** rather than `0s` or a green tick.

---

## 3. Why the design is shaped this way

Each item is a measurement from 2026-08-29/30, not a preference.

- **Scheduled by `scrontab`, not a login-node loop.** The waker's own liveness currently comes from a
  long-lived process (constant `pid` across ticks) on **one** login node, `login32`, inside tmux
  session `minerva-waker-20260829`, while its `scrontab` job last ran on `login35`. That is the single
  point of failure this dashboard must not reproduce: if `login32` drains, ticking stops.
- **The ticker panel reports three facts separately.** `scrontab` job `57712764` shows
  `Restarts=102` and its `StdOut` had not advanced in 2.1 days, while `last-tick.json` was 3 s old.
  A restarting job is not evidence its work is happening, and `--quiet` means a clean tick writes
  nothing to `StdOut`, so a stale log is not evidence of failure either. Only the receipt is liveness,
  and a `daemon-*.lock` records when a daemon *started*, not that it still ticks.
- **`TZ=UTC` on every Slurm call.** The same job printed `StartTime=2026-08-29T22:30:00` in local time
  and `2026-08-30T05:30:00` in UTC. Read as UTC, the local string puts a start time that is 4 minutes
  in the **future** 7 hours in the **past** — i.e. it converts a real ETA into a bogus "stale"
  verdict. Ages are epoch differences; `tmux ls` prints node-local time with no offset, so the
  dashboard shows that string verbatim and derives no age from it.
- **No fabricated ETAs.** `squeue --start` returned `N/A` for 7 of 8 tasks, because that is what it
  does for anything blocked on `Priority`, `Dependency` or `Resources`. A pending task's `TIME_LEFT`
  is its *requested walltime*, not time-to-anything, and is never shown as an ETA. A start estimate
  in the past is reported as stale, not as an ETA. Slurm's literal `None` reason renders as
  "no reason reported by Slurm" rather than "blocked on None".
- **The node list comes from Slurm.** `scontrol show partition cron` → `Nodes=login[01-40]`, so the
  sweep cannot drift from the real pool.
- **The sweep passes `-o ControlPath=none` and never `-q`/`LogLevel=ERROR`.** Multiplexing would
  collapse 40 probes onto one node and measure it 40 times. Suppressing diagnostics made every
  unreachable node report `rc=255 with no output`; without it the 9 unmeasured nodes resolve into
  **8 `draining`** (pam_nologin, "System is going down") and **1 `no_route`** (`login17`, also in the
  `debug` `MAINT` reservation). The 24-line legal banner is stripped from the reason and arrives on
  stderr, so it never reaches the session parser.
- **Job state is not re-implemented.** Classification calls
  [`slurm_array_status.build_snapshot()`](slurm_array_status.py), including its `UNOBSERVED` branch —
  the one that exists because leg F rendered `ACTIVE` for 24 h after finishing (`BEN-323`). A failure
  to observe must never render as an observation.
- **The page's "clock skew" comes from the HTTP `Date` header**, not from
  `now − generated_at`: that difference is the snapshot's *age*, and treating it as skew makes a
  merely-late collector look like a broken device clock. When the header is absent, skew is reported
  as not measured rather than as zero.

## 4. Known limits

- The tmux sweep reads the **default** socket only; sessions started with `tmux -L <name>` are not
  seen. The panel's claim is scoped to `/run/tmux/<uid>/default`.
- Coverage is whole-node: a node that answers but whose `tmux ls` output cannot be parsed is
  `unparsed`, which is neither "measured false" nor "not measured", and is shown as its own state.
- The collector reports the queue for the invoking user only (`squeue --me`).
- Nothing here verifies that a job's *science* is progressing — only what Slurm and the artifacts say.

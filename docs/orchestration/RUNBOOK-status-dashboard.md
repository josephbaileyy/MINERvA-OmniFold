# RUNBOOK — campaign status dashboard (collector, scrontab, gateway)

**What this is.** A glanceable status page for the MINERvA-OmniFold campaign: what is queued or
running on Perlmutter, what the tmux/LLM-orchestration sessions are doing, and what may honestly be
said about when things finish. Three files:

| File | Role |
|---|---|
| [`dashboard_collector.py`](dashboard_collector.py) | Runs on a login node under `scrontab`; writes one self-describing `status.json`. |
| [`dashboard.html`](dashboard.html) | One static file, no build step, renders `status.json` and auto-refreshes. |
| [`test_dashboard_collector.py`](test_dashboard_collector.py) | 55 tests; `/usr/bin/python3.11 -m unittest test_dashboard_collector`. |

**What it deliberately cannot tell you.** It does not predict completion times, it does not claim a
job is running because a job exists, and it never reports a login node as session-free when that node
could not be reached. Each of those is a measured failure mode, recorded below.

---

## 1. Setup you have to run yourself

### 1a. Provision the science gateway (once)

**Measured 2026-08-30, not assumed.** `portal.nersc.gov/cfs/<project>/` needs **no ticket and no
NERSC action**: the URL space already resolves and serves `/global/cfs/cdirs/<project>/www`.
338 projects already have such a directory. What was measured:

| Probe | Result | Meaning |
|---|---|---|
| `curl https://portal.nersc.gov/cfs/act/` (`www` is `drwxrwxr-x`) | `200` | Serving is automatic. |
| `curl https://portal.nersc.gov/cfs/callat/` (`www` is `drwxr-s---`) | `403` | World read+execute is required. |
| `curl https://portal.nersc.gov/cfs/m3246/` (no `www`) | `403` | Only the directory is missing. |
| `curl https://portal.nersc.gov/cfs/act/dr6_data/` (no `index.html`) | `200`, `<title>Index of…` | **The portal generates directory listings.** |
| `curl https://portal.nersc.gov/~josephrb/` | `404` | There is no per-user portal space; the project `www` is the only route. |

Two consequences, both load-bearing:

1. **The gateway is public.** Every `200` above was fetched from a laptop with no authentication, no
   VPN and no NERSC credential. Anything placed there is world-readable.
2. **An unguessable directory name is only private if every parent has an `index.html`**, because
   otherwise the portal lists the parent and the "secret" name is in the listing.

So the provisioning is:

```bash
# m3246 is the shared project directory and is owned by the PI (bnachman).  Creating a
# PUBLIC web directory in it is a decision about the project, not just your account.
mkdir -p /global/cfs/cdirs/m3246/www

# Suppress the directory listing of www's children BEFORE creating the status directory,
# or the next step's name is published in a listing.
cat > /global/cfs/cdirs/m3246/www/index.html <<'HTML'
<!DOCTYPE html><html><head><title>m3246</title></head>
<body>Nothing to see here.</body></html>
HTML

# An unguessable directory: this URL is the only access control there is.
STATUS_DIR="mnv-status-$(python3 -c 'import secrets;print(secrets.token_urlsafe(24))')"
mkdir -p "/global/cfs/cdirs/m3246/www/$STATUS_DIR"
echo "$STATUS_DIR"          # save this; it is your capability URL

# The dashboard IS the index page of that directory, which also suppresses its listing.
cp /pscratch/sd/j/josephrb/MINERvA-OmniFold/docs/orchestration/dashboard.html \
   "/global/cfs/cdirs/m3246/www/$STATUS_DIR/index.html"

chmod 0755 /global/cfs/cdirs/m3246/www "/global/cfs/cdirs/m3246/www/$STATUS_DIR"
chmod 0644 /global/cfs/cdirs/m3246/www/index.html \
           "/global/cfs/cdirs/m3246/www/$STATUS_DIR/index.html"
```

Then verify, from a device that is **not** on NERSC:

```bash
curl -o /dev/null -w '%{http_code}\n' "https://portal.nersc.gov/cfs/m3246/$STATUS_DIR/"
curl -s "https://portal.nersc.gov/cfs/m3246/" | grep -ci 'index of'   # MUST print 0
```

The second command is the one that matters: a non-zero count means the listing is live and the
capability URL is not secret.

**What is exposed even so:** job ids, job names, partitions, Slurm states and reasons, login-node
names, tmux session names, and orchestration session names and ages. Absolute filesystem paths are
shortened to their final segment by default (`--keep-paths` disables this), because the account name
appears as the second-to-last segment of a checkout root. `state/waker/` is never read except for
`last-tick.json`, `agent-sessions-v2.json` and the `daemon-*.lock` names, and the collector refuses
to write its output anywhere under the state directory. Verified: `grep -c josephrb status.json` → `0`.

**If the gateway is not acceptable** — it is the PI's shared project space and the page would be
public — the fallback is to keep `status.json` on the cluster and not serve it at all:

```bash
# Laptop: pull the snapshot next to a local copy of dashboard.html and open it.
scp saul.nersc.gov:/pscratch/sd/j/josephrb/mnv-status/status.json ./status.json
python3 -m http.server 8899   # then open http://127.0.0.1:8899/dashboard.html
```

A `file://` copy will not work: the page uses `fetch`, which needs an HTTP origin. On the phone this
fallback gives you alerts only (§1c) plus Termius, which is what the existing ntfy body
(`"Open Termius for details."`) already assumes. There is no per-user NERSC web space to fall back
to — `portal.nersc.gov/~josephrb/` is a `404`.

### 1b. Install the scrontab entry

Print the block rather than letting a tool rewrite your table:

```bash
cd /pscratch/sd/j/josephrb/MINERvA-OmniFold/docs/orchestration
/usr/bin/python3.11 dashboard_collector.py --print-scrontab \
    --state-dir /pscratch/sd/j/josephrb/MINERvA-OmniFold/docs/orchestration/state/waker \
    --out "/global/cfs/cdirs/m3246/www/$STATUS_DIR/status.json"
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
/usr/bin/python3.11 -m unittest test_dashboard_collector      # 55 tests
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

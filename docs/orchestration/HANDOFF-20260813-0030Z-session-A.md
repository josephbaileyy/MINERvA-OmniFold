# HANDOFF — Session A (orchestrator), 2026-08-13 ~00:30Z, at `243af2f`

**Why this exists.** The codex channel measured this session at 7.01 MB / 980 assistant messages / 37
compaction markers and recommended migrating orchestration to a fresh session before it takes another
substantial task. Concur. The HPSS decision is now blocked on Joseph and on `agy`, so this is a seam
rather than an interruption. **Nothing is in flight**: no Slurm job of mine is queued or running, nothing
is mid-write on the cluster, and nothing has been added to HPSS.

Per this repo's convention every fact below lives somewhere else and is **pointed at, not restated**.

## Read these first, in this order

1. `docs/orchestration/RECEIPT-20260812-hpss-space-audit.md` — **and read its ADDENDUM before acting on
   the body.** §1 and §7 are wrong as written and deliberately left unedited; the addendum supersedes
   them and says why. A receipt that silently rewrites its superseded sections cannot be audited.
2. `docs/OPEN_ITEMS.md` `OI-48` (the live storage decision) and `OI-47` (re-scoped, owner Session A).
3. `docs/orchestration/FINDING-20260812-orchestrator-instrument-defects.md` — BEN-190…197 long-form.

## THE ONE LIVE DECISION — `OI-48`, and it is not the decision it started as

HPSS is at **265.1%** of a **512.00 GiB** quota (overage **845.22 GiB**). Three options exist and **all
three are behind Joseph's precondition**, verbatim: *"make sure you actually need to store these files."*

| option | effect | status |
|---|---|---|
| move 240 P3F objects → CFS | HPSS → 58.6%; CFS 79% → ~80.6%; nothing deleted | **moves are approved** by Joseph; blocked on necessity |
| PI raises the allocation | zero movement, zero durability loss | Ben Nachman offered unprompted; **Joseph's ask, not a lane's** |
| delete | recovers 12,334 B by dedup; anything more is physics products | **NOT authorized. Delete nothing.** |

**Necessity evidence so far:** repo side with `agy` (regenerability, `OI-24` supersession, citations) —
**not yet landed**. Cluster side **done**: all 240 objects are still on scratch byte-exact, so HPSS is a
second copy rather than a purge rescue — *but* scratch is purgeable and at 79.7%, so that retires the
"rescue" framing, not the archive. **Still open, and I did not check it:** whether any of the 240 predate
the remediation, which would make them the `.prehm` case (older construction, not fuller ensemble).

**Standing: move nothing, delete nothing, archive nothing new until the necessity audit lands.**

## What changed today that a successor will otherwise re-derive

- **The quota is readable.** `hpssquota` / `showquota` are login-node binaries at
  `/global/common/software/nersc/bin/`, **not `hsi` verbs**. `hsi lsquota` and `hsi quota` do not exist
  (exit 64). This cost a full day of "the denominator is unknown."
- **NERSC certs last 24 h.** `ssh` exit 255 with no cause is usually this; `ssh -v` names it in one line
  and `ssh-keygen -L -f ~/.ssh/nersc-cert.pub` gives the window. `BEN-197`.
- **`0.874 TB` for the 240 P3F objects is unsourced and wrong** — measured 1,134,998,230,283 B. If you
  see it quoted anywhere, it came from conversation, not an artifact.
- **The smoketest/receipt digest collision is closed and benign** — the smoketest reused a production
  receipt as payload; `240/240` covers 240 production objects. Do not re-open it as "one might be a test
  file"; that reading is refuted with `slurm.jobid 56169842` and `produced_utc 2026-07-20T06:41:42Z`.

## Instruments I added or changed — all self-testing, run the self-test before trusting output

| tool | what | gate |
|---|---|---|
| `hpss_space_audit.sh` | read-only HPSS audit; `assert_readonly()` gates the only `hsi` wrapper, so mutating calls are structurally impossible | `--self-test` → 48/48 |
| ” `--parse-file` | re-runs the digest parse over **saved** output, zero HPSS calls | — |
| `ROW-OWNERS.tsv` | side table mapping row id → lane, for CLM/VL ids that no block table can attribute | — |
| `whose_row.py --check-owners` | two-sided validation of that table | 0 ok / 1 drift / 2 cannot-check |
| `whose_row.py --self-test` | now 70 checks (was 58) | PASS |

**All 12 CLM ids are `UNASSIGNED` on purpose. `UNASSIGNED` is not permission** — the gate exits 2 on it,
never 0. My routing *proposal* is in the TSV's `basis` column (CLM-001…008 → C, 009…011 → B, 012 → D),
derived from each row's own `independent verifier` field. **It is a proposal, not an attribution**; the
lanes fill their own lines.

## Outstanding, honestly

- **`LIVE-STATE` split — not started.** Version the declaration, generate the view on read (`BEN-191`:
  the file is always stale by construction and the detector can only be honest about it).
- **`98d9c5` — delivered, never answered.** Concurrency exposure still open.
- **`OI-47`** — the payload must be *written* before the trigger is deferred on again. I did **not** write
  `worktree.bgIsolation`: flipping it is still unauthorized.
- **Over-600 `FINDINGS` rows**: `BEN-164` (1287), `BEN-204` (1032), `BEN-203` (876), `BEN-201` (723),
  `BEN-162` (709), `BEN-163` (697). **None are lane A's** — mine are 429–566.
- **`hsi hashverify` after tape migration** — PET lane, unchanged.
- **The ledger freeze window** was never formally closed with the lanes.

## The thing I would tell my successor about how this session failed

Seven of today's eight findings are one shape: **a check that returned the answer I expected without
touching the thing it claimed to test**, and whose output was indistinguishable from a real pass. A
config edit verified by contents but not read-path membership. A containment gate over zero files. A
digest denominator parsed by the matcher it certified. A path check that stat'd one directory 240 times.
Twelve tests placed after the line that prints test results.

The mediator's formulation is the one to carry forward, and it generalises past any of them:

> **A check's denominator must come from a different instrument than its numerator, or it is not a check.**

What actually caught these was never a verdict. It was `du`'s file count, a distinct-path assertion, a
uniformity tell (28,672 B × 240), and a check count that failed to move. **Keep an outside witness on
every gate, and be most suspicious when a gate agrees with you.**

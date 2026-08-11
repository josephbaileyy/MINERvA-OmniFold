# Packet B cluster run — PB1, PB3, PB4 against real state (2026-08-11)

**Allocation** `56636802`. **code_rev** `683bdcc`. Products under
`nd-unfolding/active_universe_5d/standard/`. Candidate keeps `publication_gate_rejects_this`; no
token was set and none exists.

Until this run, every Packet B item was closed on **fixture** evidence. This is the first execution
against the live support family, the live evidence directory, and the real 42.3 GB candidate.

## PB1 — band-set completeness, first production execution

`band_set_completeness_vs_support_family` now appears in the validator's PASS gate list, having
enumerated the support family's `hCov_universe5d_*` keys and **recomputed all 45 band content
hashes** from it. Full gate list on this run:

```
merged_inseparability, merged_audit_census_and_migration,
candidate_self_declares_non_adoptable, component_manifest_bound,
exact_5_active_bands, traces_pos_finite, active_total_eq_sum5, symmetric_psd,
full_total_identity_recomputed, band_set_completeness_vs_support_family,
c_syst_recomputed_from_components, support_trace_ratio_recorded   (support_ratio = 1.000)
```

**PB1 is no longer closed on fixture evidence only.**

## PB3 — publish ordering

`EVIDENCE-COMPLETE`, and the evidence directory afterwards contains exactly:

```
p4_endpoint_evidence.json   p4_merged_audit.json   p4_standard_manifest.json
```

**No `.PENDING` and no `.FAILED` residue** — the rename-on-complete published all three and removed
the opposite variant, which is PB3's case-5 behaviour observed rather than asserted.

## PB4 — rejection inheritance

```
[proj] parent declares publication_gate_rejects_this; the projected product inherits it
```

Projection manifest carries `publication_gate_rejects_this: true`,
`non_adoptable_marker_key_present_in_parent: true`, and
`non_adoptable_parent_manifest_sha256: a76904e3b07ec2d74a27c5f745524d716ebef5fa02790ccfc582c5b0f268590c`.
The parent was bound by sha256 before the marker was read.

Unchanged from earlier runs and reported for continuity: 5 of 4830 reported 4D bins unreachable
(indices 9679, 9686, 9714, 9721, 10169), effective support 4825, projection identity `9.39e-17`,
cross-check median 0.0443 / p90 0.2083 / integral ratio 1.005578 (reported, no pass/fail).

## Cost, measured — with the caveat stated

| | stages 5+6 |
|---|---|
| before PB1's band check | 11m31s (02:07:54 → 02:19:25) |
| this run | **17m00s** (12:09:14 → 12:26:14) |
| difference | **≈ +5.5 min** |

**Read this as an order of magnitude, not a measurement.** It is two single runs on possibly
different nodes — the two-point comparison the PET lane was burned by twice in one night. What it
supports: the 45-band hash recomputation costs minutes, not hours, so the trade PB1 made is cheap.
What it does not support: any quoted per-run cost.

*Method note:* the in-script `date +%s` stamps all collapsed to one value (evaluated at parse time
through the quoting layers), so the times above are the driver's own log lines, not the harness's.
The harness timing was discarded rather than reported.

## What this run did NOT establish

- **The scoped PB1–PB5 verifier pass has not run.** These are executed results, not an independent
  verdict on them.
- **PB2 was not exercised.** No endpoint resumed on this run — the candidate was reused and the
  unfold stage did not re-enter its skip path. PB2 remains closed on fixture evidence.
- **PB5 is documentation**, unaffected by any run.
- The armed-watch end-to-end proof and the first `PROCESSED.txt` append are still outstanding.

## Channel test: FAILED to deliver

The first `wakerctl emit` from this lane
(`p4-packetb-channel-test-20260811T1211Z`) reached `.claim`, `.invoked` and `.done` — the cron
processed it — and produced **no `.sent` marker**. Every marker on the cluster is
`blocked-on-user-*`. **No mail was sent.**

Four distinct failure modes were hit in getting that far, and every one reports success at the emit
site:

1. **wrong queue host** — `state/waker/` is gitignored, so the event queue is per-checkout; the
   first emit went into a laptop working tree the Slurm dispatcher never reads;
2. **interpreter** — login-node `python3` is 3.6.15, too old for wakerctl's
   `from __future__ import annotations`;
3. **silent dedupe** — a reused id is suppressed with no ledger entry (BEN-067);
4. ~~**dispatched-without-notify** for `--type artifact`~~ — **WRONG DIAGNOSIS, corrected below.**

### CORRECTION (same day): there is no mail path from `emit` at all

Item 4 above was my error and is retracted. There is no `--type artifact` bug, and the type is
irrelevant. **`wakerctl emit` cannot mail and never could.** Verified independently rather than
accepted on report: `notify()` has exactly four call sites —

```
:860  schedule_retry      only when retries are EXHAUSTED
:952  notify_guard        <- every blocked-on-user-*.sent marker comes from here
:965  notify_guard
:1097 status_report_guard
```

— and `dispatch_one` contains **zero** of them. A successful dispatch *resumes a session*; that is
what `outcome: resumed` in the `.done` file meant. So the emit behaved exactly as designed:
claimed, invoked, done, no mail. Nothing was broken.

**How the wrong conclusion was reached, because that is the reusable part.** The oversight session
read `notify_command` configured at `waker-config.json:18`, observed live `.sent` markers, and
inferred that `emit` would reach the user through the cron. Both observations were true; the
conclusion did not follow, because the markers come from the *guard* paths, not the dispatch path.
I then spent three attempts making a channel work that had no mail path at its end. The
wrong-queue-host and interpreter failures found along the way were real, and incidental.

Same shape as `code_rev == HEAD`: a mechanism inferred from a partial read and handed on as a spec.
The check that would have caught it is one `grep` for the call sites of the function the mechanism
depends on — which is what settled it in the end, after the fact.

**Standing conclusion, recorded as the answer and not as an interim state: there is no
arbitrary-content push channel from this lane. The repository IS the durable record** — artifacts
are committed and pullable without any relay. What is missing is *push*, not the record. The honest
options are a mail tool in the session (Joseph's to enable) or accepting pull-only.

**Explicitly rejected:** routing artifact pushes through `BLOCKED-ON-USER.json`, which *does* mail.
Using a decision channel for notification is how a blocked-on-user file trains its reader to
discount it — filed by the PET lane as BEN-085.

---

## Allocation cost of Packet B, measured before release (2026-08-11)

Nothing recorded what the packet cost in compute. From `sacct -j 56636802` taken immediately
before `scancel`:

| | |
|---|---|
| holder elapsed | **01:27:25** on 256 CPUs |
| **CPUTime** | **15-12:58:40** |
| step `.0` — evidence + stages 5/6 | 00:17:43 on 128 CPUs (= 1-13:47:44) |
| step `.1` | 00:05:06 (= 10:52:48) |

**~23 minutes of useful work inside an 87-minute holder** — the allocation idled about two-thirds
of its life. That is the honest input for sizing the next packet, and it argues for shorter holds
rather than the 3-hour `alloc_run` default. Recorded because an unmeasured cost gets re-guessed.

## Two errors of mine in the release, recorded because they are the same class this packet closed

**1. Cancelled before disarming.** The instruction was to disarm the watch and cancel in one turn,
so a watch does not fire on a deliberate kill — a watch firing on an intentional cancel is noise
that trains its reader to discount the channel. I used the wrong subcommand (`disarm`; it is
`watch-disarm`), and because the commands were `;`-separated rather than `&&`, the `scancel` ran
anyway. The job died with the watch still armed; it was disarmed immediately after and is now
`disarmed`, but there was a window.

That is **BEN-068's shape in my own hands**: a dependent action sequenced before the thing that
should gate it. The structural fix is the same one PB3 took — make the ordering impossible to get
wrong rather than remembered. `scancel` should be reachable only through a wrapper that disarms
first, exactly as evidence publication is reachable only through `_publish_evidence()`.

**2. A stale verifier pass, commissioned and discarded.** I sent PB2 for an independent re-verdict
reading the tree at `f67352f`. While it ran, another session found and fixed the explicit-`null`
grandfathering shapes (`1440b58`) and closed the packet (`fa1e49a`). My pass was therefore auditing
superseded code and would have returned a verdict correct about that code and contradictory in the
record. **Discarded, not filed.** Worth noting the near-miss: I had asked that verifier for a
receipt-class census with counts, which points at the shape that was actually wrong — but I did not
find it, another session did.

*Note on the requested-session substitution:* the oversight asked that the re-verdict go to verifier
UUID `019f74cb-b85d-7ba0-96c5-dfbd09e59159`. That rollout is not resumable from this codex home, so
the pass would have been a fresh independent verdict rather than that session revising itself. That
difference was recorded in the prompt at the time; it is moot now that the pass is discarded.

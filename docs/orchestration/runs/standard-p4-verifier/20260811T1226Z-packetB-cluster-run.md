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
4. **dispatched-without-notify** for `--type artifact`, which is this run's new one.

The `.sent` marker is the only proof of delivery. Until (4) is understood, **the push channel is
unproven and the repository is the durable record.**

# AUTHORIZATION 2026-10-13 — 2D closeout: Stage C pilot walltime recap and ceiling raise

**Issued by** the paper-tighten lane, as director, under
[`AUTHORIZATION-20261012-2d-closeout-delegation.md`](AUTHORIZATION-20261012-2d-closeout-delegation.md). This record
amends [`AUTHORIZATION-20261013-2d-closeout-stageC-pilot.md`](AUTHORIZATION-20261013-2d-closeout-stageC-pilot.md)
(the pilot grant) and is answered by a v2 binding addendum. It responds to the 2d closer's stop of 2026-10-13: B1's
`2dc_C_P1_unit` timed out, so the director's pre-B4 headroom condition failed.

**CITABLE FOR:**
- the pilot ceiling, raised from 12.9 to **20.0** charged CPU node-h;
- the remaining jobs' new walltime caps and their measured bases (§2);
- the ruling on `P1_unit`'s retry and the launch conditions (§3).

**NOT CITABLE FOR:**
- any job under the new caps before a v2 binding addendum is on `origin/main` (§4);
- any change to a check, threshold, envelope, terminal outcome, the window or the namespace;
- the cause of the slowdown. §1 gives a working reading, not a finding;
- production. Production still needs K1 PASS, a passing K2 route, and its own grant.

## 1. What happened (sacct, re-measured by the director 2026-10-13)

| job | state | elapsed | CPUs | basis it was capped from |
|---|---|---|---|---|
| `59733771` `P0_default` | COMPLETED | 935 s | 64 | 978 s |
| `59733772` `P0_derived` | COMPLETED | 1,450 s | 64 | 978 s |
| `59734955` `P2_NormDISCC0` | COMPLETED | 1,003 s | 128 | 1,034 s |
| `59734956` `P2_MaRES0` | COMPLETED | 1,069 s | 128 | 1,034 s |
| `59734957` `P2_Flux23` | COMPLETED | 1,166 s | 128 | 1,034 s |
| `59734959` `P2_MINOS0` | COMPLETED | 856 s | 128 | 1,034 s |
| `59734961` `P2_MINOS0def` | COMPLETED | 2,497 s | 128 | 2,751 s |
| `59734962` `P1_unit` | **TIMEOUT** | 1,930 s (cap 1,920) | 64 | 1,267 s (VL170 p99) |

The charge to date is (152,640 + 967,168) / 921,600 = **1.2151** node-h, with nothing in flight. K1 passed on all
five comparisons (closer's report; `results/p2.json` `8139a710…`). The director reviews that at the terminal REPORT.

`P1_unit` wrote "Starting iteration 4", the last of 0–4, at about 1,750 s. `P0_default` finished all five
iterations in about 923 s on the same 64-CPU shared configuration. The closer re-projects `P1_unit` at about
2,295 s.

**Working reading, not shown.** The P1 patch adds only pre-iteration histogram fills. With unit factors, its
training inputs equal the central's. Today `P0_derived` ran 1.55× slower than `P0_default` while doing no more
work, so shared-node variance today is large. The director therefore reads the slowdown as node contention. The
`P1_unit` retry (§3) is the measurement. If the retry is also slow, the P1 path is intrinsically slower, and that
must be priced into production.

## 2. New caps (the rule is unchanged: cap = 1.5 × a measured projection, rounded up)

| jobs | old cap | projection basis | new cap | enforced node-h each |
|---|---|---|---|---|
| `P1_{fixed,joint,bkg}_01…20` (60) | 00:32:00 | `P1_unit` re-projection 2,295 s | **00:58:00** | 0.2417 |
| `G2_on`, `G2_on_s43` | 00:50:00 | P5's on run 1,928 s × today's off ratio 1,166/776, = 2,897 s | **01:15:00** | 0.6250 |
| `G2_off_s43` | 00:30:00 | P5's off run 1,034 s × 1,166/776, = 1,554 s | **00:40:00** | 0.3333 |
| `P3_*`, `P1_unit` | unchanged | the 128-CPU jobs ran today at ≤ 1.13× their bases; `P1_unit`'s cap is set by its retry (§3) | — | — |

**Upper edge at caps, no retries:**

| | node-h |
|---|---|
| charged | 1.2151 |
| P1_unit retry | 0.2417 |
| B2 | 0.6250 |
| B3 (0.6250 + 0.3333) | 0.9583 |
| B4–B7 (60 × 0.241667) | 14.5000 |
| B8 | 0.7500 |
| **total** | **18.2901** |

That leaves 1.71 for retries under the 20.0 ceiling. At projections (P1 replicas 839–2,295 s), the expected
charge is about 6–12 node-h.

**Against the delegation.** Committed grant ceilings rise from 18.9 to **26.0** of 700 node-h:
- Stages A–B: 2.0;
- the flux repair: 1.0;
- Stage B diagnostics: 3.0;
- this pilot: 20.0.

The pilot now exceeds Stage B §7's 15.0 request for P0–P5. The excess is priced here and reported to Joseph.

## 3. Rulings

- **(a) `P1_unit` retry: approved.** It is approved under the existing binding (package `92b0b466…`) and the
  grant's one-retry rule, at 00:58:00 (1.5 × 2,295 s = 3,443 s). The gate admits it at 1.2151 + 0.2417 ≤ 12.9.
  While it runs, the closer records the node's co-tenancy once, read-only.
  - A b ≡ 1 FAIL is a failed no-op control: stop.
  - A second TIMEOUT is P1 INCONCLUSIVE: stop and report.
  - If it passes and its elapsed × 1.3 > 3,480 s (that is, elapsed > 2,677 s), B4 is not launched: stop and report.
- **(b) P1 replica caps** change only through the v2 package and its binding (§4).
- **(c) `G2_on`.** The closer was right to hold B2. An off run's time is not a like-for-like check of an on run's
  cap, so the literal reading is not adopted. In v2, `G2_on`'s elapsed matters only as the normal retry trigger.

## 4. The v2 package and its binding

**The commit.** One new commit on `closeout/stagec-pilot-20261013`, on top of `92b0b466…`, with no force-push. It
changes only:
- `jobs.tsv`: the rows in §2;
- `launch.py`: `CEILING = 20.0` and its docstring;
- DESIGN §4 and §9;
- `manifest.json`;
- generated `MANIFEST.tsv` and hash-binding rows, as needed.

It changes no driver, analysis script or threshold.

**Binding.** The director reviews the diff and commits a v2 binding addendum to `origin/main`, naming the full v2
sha, the manifest digest and the `jobs.tsv` and `launch.py` digests.

**Deployment** waits for two things: that addendum on `origin/main`, and `squeue -u josephrb` showing no pilot
job pending or running. `$NS/retries/`, `gatelog/`, `out/` and `results/` stay in place, and `P1_unit`'s one
retry stays spent. The ledger keeps reading `sacct` from 2026-10-13T00:00:00, so every v1 charge counts against
20.0.

**Order** is unchanged: B2 → B3 (conditional) → B4–B7 → B8. Every other operating condition in the binding
addendum §4 still applies.

## 5. Reporting

The director reports this stop, the raise and the retry outcome to Joseph. Same-model caveat: the closer and the
director are both Claude Opus 5.5, and the director re-measured the sacct rows and the arithmetic but not the
re-projection's log timing beyond file mtimes.

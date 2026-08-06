# PLAN 2026-08-06 — the niter=3 budget recompute and the J28 flux re-roll, as ONE pass

*Opened because `docs/OPEN_ITEMS.md` item (d) says the two couple and "should be planned together
rather than sequentially: recomputing the budget at `niter=2` and then again at `niter=3` is double
work against a moving target." This file is that joint plan. It is a plan, not a receipt — nothing
here is a result, and no number below is quotable.*

Owning items: `docs/OPEN_ITEMS.md` (d) and (e); `KNOWN_ISSUES.md` J-block (J28); ledger quarantine at
`VALIDATION_LEDGER.md:74-91`. Claim row: `CLAIMS.md` CLM-010.

## 1. Why these are one pass and not two

Three moving parts, each of which invalidates products built against the other two:

1. **J28** — every saved ND/5D Flux universe divided by the CV flux integral instead of its own
   `Φu` (five sites plus a fail-open; code fixed in `081ae4a`, **numbers never re-rolled**). The
   adopted 5D covariance scales are quarantined.
2. **`niter` 2 → 3** (`2b2e5f1`) — changes the *estimator*, so every covariance component derived at
   `niter=2` is inconsistent with the central value the campaign will publish.
3. **`g`, the per-bin inflation** (`adopt_unified_5d.py:86`) — derived from the throws, so it moves
   when either of the above moves. This is why the adopted headline is wrong *twice* under J28: once
   through the Flux block and again through `g`.

Running these separately means building the budget three times. Running them together means once.

## 2. Preconditions — verified 2026-08-06, by commands run when this file was written

The ledger records the re-roll as waiting on "the `/pscratch` slabs and … the Perlmutter restore
(08-03 22:00 PT)". **That wait is over.** Confirmed present:

| precondition | state |
|---|---|
| Throw slabs on scratch | ~~**365** `*slab*.npz`~~ → **542**, corrected 2026-08-06. The original count came from a filename filter that missed every **block** slab (`block5d_*.npz`, `blockfps_*.npz`, `block4d_*.npz` — no "slab" in the filename, only in the directory). `C_blocksum` is built from those, so they are not optional. See BEN-032. |
| Bank inputs the rescale actually reads | `cv.npz` (2.9 GB each) + `flux_univ_ratio.npy` (11 KB each). **Not** the 26–37 GB of per-universe `sig_*`/`td_*` arrays per bank — those are re-THROW inputs, and the distinction is what keeps Step 0 an 8 GB copy instead of an 89 GB one. |
| Throw banks | `bank_uthrow_5d/`, `bank_uthrow_fps/`, `bank_uthrow_5d_bkgaware/` each carry `cv.npz` + `flux_univ_ratio.npy` |
| Re-roll tool | `nd-unfolding/rescale_flux_universes.py` exists, landed in `081ae4a` |
| Restore | complete (the 08-03 blocker the ledger cites) |

**So J28 is no longer blocked on anything but being scheduled.** That is a change of state from what
`VALIDATION_LEDGER.md:86-88` currently implies, and it is the reason this plan can be written now.

**Scratch is purgeable.** 365 slabs that cannot be regenerated cheaply are the single largest
schedule risk in this plan. Step 0 exists for that reason and should not be skipped.

## 3. What the re-roll is, and what it is not

`rescale_flux_universes.py`'s own docstring states the identity: flux normalization enters only at
final extraction and `extract_cross_section_nd` divides by the flux along `pT` alone, so a saved
universe is exactly linear in `1/Φ(pT)` and is corrected by

    x_corrected[i_pt, ...] = x_saved[i_pt, ...] / r_u[i_pt],   r_u = Φu / Φ_CV

**This is an identity, not an approximation** — which is why the exact corrected covariance is cheap
and why **no re-unfolding is required**. Knob endpoints are deliberately untouched: a knob universe
does not move the flux integral, so CV flux was always the right denominator there.

The tool rebuilds `C_unified`, `mean_shift`, `C_blocksum`, `C_cross` and `g` (both mean-centered and
`--cv-centered`) with the same `uq_math` estimators the combine uses, and **adopts nothing** — it
writes its own output and prints a before/after. Adoption is a separate, later decision.

## 4. Ordering, and why this order

**Step 0 — protect the inputs (do first, cheap).** ~~Verify the 365 slabs are readable, not merely
present, and get an off-scratch copy or a verified inventory with digests.~~ **DONE 2026-08-06** —
`nd-unfolding/protect_throw_slabs.py`, manifest `nd-unfolding/products/slab_manifest_20260806.json`,
off-scratch copy at `/global/cfs/cdirs/m3246/josephrb/slab-protect-20260806`. **548 files, 8.1 GiB,
all 548 readable** (`np.load` with every array materialised, not merely `stat`-ed) and 0 unreadable;
every destination file re-hashed against its source; the copy independently re-verified **against the
CFS root**, which is the restore path, rather than only against the source. The check has power:
flipping one byte at offset 40 of a copy yields `*** SLAB SET DIVERGED ***` naming the file.

**The first pass of this step was wrong and is worth reading as a warning.** It protected **365 of
542** slab files and reported "365 readable, 0 unreadable" — complete-looking, because the count of
what was checked is not the count of what exists. It selected on `"slab" in filename`, which misses
the entire **block** ensemble (`block5d_*.npz`, `blockfps_*.npz`, `block4d_*.npz`; only their
*directory* names them). `rescale_flux_universes.py` rebuilds `C_blocksum` from precisely those, so a
purge would have left Step 1 unrunnable while the manifest asserted the inputs were safe. Filed as
**BEN-032**. The manifest now states its own selection criterion so coverage can be audited rather
than trusted, and the 548 includes the 3 bank `cv.npz` and 3 `flux_univ_ratio.npy` the rescale reads.

*Both halves were done rather than the "or" — the manifest is the durable half (it belongs in git and
lets anyone later prove a restored slab is the same slab), the copy is the recoverable half.* One
correction to this plan's own framing: the slabs are the largest **schedule** risk, but they total
**58.1 MiB**, so there was never a cost to weigh against protecting them — CFS has 37 PB free and the
whole step took seconds. The plan's wording implied a tradeoff that does not exist. A purge between
now and the re-roll still turns a cheap post-hoc correction into a full re-throw campaign, so the risk
was real; only its remedy was mispriced.

Re-check at any time with `--verify-only --root <tree> --manifest <path>`, which is how a future
session should confirm the slabs before spending anything on Step 1.

**Step 1 — J28 re-roll on the existing slabs, at whatever `niter` they were produced with.** The
flux correction is a *post-extraction rescale along pT*; it does not care which `niter` produced the
slab. Doing it first therefore costs nothing extra and immediately answers the question the ledger
quarantine is waiting on. Predeclare the comparison before running (§5).

**Step 2 — decide what must be re-thrown at `niter=3` versus what transfers.** Not everything in the
budget is estimator-dependent in the same way. The honest split has to be made explicitly and
written down, not assumed:
- Components that are *definitionally* tied to the estimator (anything derived from unfolded throws:
  `C_unified`, `C_blocksum`, `g`, the joint mean shift) → **re-throw at `niter=3`**.
- Components the audit already lists as J28-**unaffected** (central cross sections, corrected 4D
  block-sum core, closure, dimensional anchors, statistical and ML covariance, detector laterals,
  and the finalized 2D covariance) are unaffected *by J28*; that is **not** the same as being
  unaffected by `niter`. Each must be classified separately here. Do not carry the J28 exemption
  list across to the `niter` question by analogy — that is the mistake this step exists to prevent.

**Step 3 — rebuild the budget once, at `niter=3`, on flux-corrected universes.**

**Step 4 — only then, `test_uq_remediation.py`'s J28 fixture.** Item (d) is explicit that this comes
*after*, not before: deciding fixture-stale versus guard-over-strict now risks doing it twice. (That
fixture is the cluster suite's single remaining failure — its J28 flux guard rejects its own
synthetic fixture for lacking a flux normalization stamp.)

**Step 5 — lift the quarantine by replacing numbers, never by deleting the notice**
(`VALIDATION_LEDGER.md:91`, which says so in as many words).

## 5. Predeclared decision rules — write these down before the data exists

The one thing the `niter` episode got right was predeclaring the rule every time; per
`FINDING-20260806-campaign-pin-inverted-on-insignificant-variance.md`, "that is the only reason each
reversal reads as a result rather than a rationalisation." So, before Step 1 runs:

1. **No first-order estimate is quotable, and none becomes quotable by being confirmed.** The audit's
   `5.81e-38 → 6.0e-38` (+3–4 %) and "+6 % combined block √tr" are explicitly not results. If the
   exact re-roll lands near them, that is not corroboration — the exact number replaces them.
2. **State the direction and size of the change before adopting it**, and if the corrected `g` moves
   the adopted scale by more than the first-order estimate predicted, that is a finding to write up,
   not a number to quietly adopt.
3. **Spread claims need real `n` and an interval** (BEN-025). No "component X grew N%" without a test
   and a CI, and never escalated to Joseph as a fact without one.
4. **Realized exceedance over fitted tails** for any threshold decision that arises.
5. **If a component is reclassified as "transfers unchanged from `niter=2`", the argument must be
   positive** — a stated reason it cannot depend on the estimator — not the absence of a reason to
   think it does.

## 6. Where each number lands

Per the canonical-home table: verified numbers → `VALIDATION_LEDGER.md` (replacing the quarantined
scales in place); chronology → `nd-unfolding/ND_OMNIFOLD_RUN_LOG.md`; current state →
`nd-unfolding/CORRECTED_UQ_PRODUCTION_STATUS.md`; claim status → `CLAIMS.md`; new agent-failure modes
→ `FINDINGS.md` as `BEN-*`. A result does not exist until its commit lands, and the commit carrying
the re-roll must also carry its ledger entry, RUN_LOG entry and STATUS one-liner.

## 7. What this plan does NOT cover

- **Adoption.** The re-roll produces corrected numbers; adopting them into the headline is a separate
  decision with its own gate.
- **The `niter=3` regularization justification** — that is item (e), tracked separately, with the
  scalar-level argument assembled at CLM-010 and two named gaps (differential version; upper bound on
  `k`, job 56397442).
- **J29's saved FPS slabs.** The code bug is RESOLVED in `081ae4a`, but the saved FPS `*_uthrow*`
  slabs remain inside J28's re-roll blast radius and ride along with Step 1.
- **P4.** J30 (the canonical P4 chain cannot reach covariance validation) is a deferred, non-adopted
  lane and is out of scope here.

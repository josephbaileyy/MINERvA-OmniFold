# PREDECLARATION — `OI-126`: is the p∥ deficit in the TRAINING or in the EXTRACTION?

**Written and committed BEFORE the measurement is run.** Its whole value is the timestamp: every threshold
and every reading below is fixed now, so a null cannot be reinterpreted afterwards and a match cannot be
chosen afterwards. Peer session `B`. Authorized by Joseph under the standing grant for agreed work under
12 h; costed at a few core-minutes.

**Language discipline, carried in deliberately.** `C_stat` is **NOT independently verified** — `VL132`:
*"THE RECEIPT MAY NOT CLAIM INDEPENDENT CONSTRUCTION OR INDEPENDENT VERIFICATION: there was ONE builder."*
`OI-121` authorized two blind builders and one built it. Its 19/19 clauses are abort-on-failure assertions
**inside that same builder**, i.e. a self-check. **Nothing this measurement produces may be called
"verified" on the strength of a script I wrote.** Where I mean self-checked, I will write self-checked.

## The question, and why it is the last unknown before `OI-126` can be dispositioned

`OI-126`: the P5A nominal lies above **all 50** replicas in 44 of 63 cells at p∥ 6–20 GeV while agreeing
with the family below 6 GeV, and `log(family mean / nominal)` is explained `R² = 0.868` by p∥ alone
(`state/RECEIPT-20260815-oi126-mechanism-narrowing.json`). Already refuted there: the target (replica
targets are the nominal target × Poisson(1) × one shared constant, refinements agreeing to 0.068%) and
shrinkage toward the prior. **What remains is where in the chain the p∥-separable factor enters.** Both
arms persist `w_push` over the full signal sample, so the chain splits exactly once and read-only.

## The statistic

For each arm `a` ∈ {P5A nominal `56978466`, replica_00 `GATE5_REPLICA_FULL_PUSH`}, over the 49,152,885
signal rows (both `w_push` arrays are `(49152885,) float64`; `mc_indices` asserted identical between arms
before use, else aligned by it):

```
T_a(cell) = SUM over rows i with pass_truth[i] and truthcell(i)==cell  of  w_truth[i] * w_push_a[i]
R_push(cell) = T_nom(cell) / T_rep(cell)
R_xsec(cell) = xsec_nom(cell) / xsec_rep00(cell)          # both already in hand
```

`truthcell` uses `truth_scalars` (pT, p∥) on the canonical 15×19 extended-FPS edges,
`cell = i_pt*19 + i_pparallel`, asserted against `assert_extended_fps_edges`. **`R_push` deliberately
omits every normalisation the extraction applies** — POT, nucleons, flux, bin area, and any Gate-5
signal/background factor — because those are identical between arms *by record* for the first four, and
the last is exactly the suspect. **`R_push` is therefore a pure training-side quantity and `R_xsec` is the
end-to-end one. The comparison between them is the measurement.**

## Domain, and which side of the `CSTAT-D3c` line every result falls on

- The comparison is over the **257-cell quotable sub-block**, not the 262-cell domain: the 5 flicker cells
  `[209, 254, 255, 256, 281]` are excluded per `CSTAT-D3c`.
- **The 63 band cells contain none of them** — already measured, `tail ∩ flicker = 0`, and definitionally
  so since the 63 were drawn from the 257. **So no result below can land on a flicker cell**, and cell
  `255`'s 24-of-50 reporting (about half its apparent spread being the mask switching rather than the
  cross section moving) **cannot contaminate any number in this measurement.** Stated because it was
  asked, not because it is in play.
- Cells are further restricted to `xsec_rep00 > 0` so `R_xsec` is defined; the count dropped is reported.

## THE READINGS, FIXED NOW

**Control first — it decides whether the other readings may be used at all.** In the control region
p∥ < 6 GeV (columns 0–9, 128 cells) the end-to-end arms already agree (`R_xsec` median ≈ 1). So:

- **CONTROL PASSES** iff `median | R_push/R_xsec − 1 | ≤ 0.10` over the control cells.
- **CONTROL FAILS → THE MEASUREMENT IS UNINFORMATIVE AND I WILL REPORT IT AS SUCH.** A failure means my
  truth-side binning does not reproduce what the extraction does, and **no statement about the band may be
  made from it** — not a weakened one, not a directional hint. The likeliest causes are a `w_truth`
  convention I have wrong, a `pass_truth` subsetting difference, or `mc_indices` not being an identity map.

Given CONTROL PASSES, over the 63 band cells:

| reading | criterion, fixed in advance | what it would mean |
|---|---|---|
| **TRAINING** | `median R_push ≥ 2.0` **and** `median(R_push/R_xsec) ∈ [0.7, 1.4]` | the deficit is already in the trained push; the fit itself diverges in p∥ 6–20 and the extraction faithfully carries it |
| **EXTRACTION** | `median R_push ∈ [0.80, 1.25]` while `median R_xsec ≥ 2.0` | the two arms' pushes agree; the factor is introduced downstream of training, and `gate5_signal_factor_applied_to_truth_counts` becomes the named suspect rather than a speculative one |
| **SPLIT** | `median R_push ∈ (1.25, 2.0)` | both contribute; **to be reported as SPLIT, not rounded to whichever is closer** |
| **UNINFORMATIVE** | control fails, or `median R_xsec < 2.0` in the band (the effect is not present in this replica, so there is nothing to localise) | no conclusion |

**Secondary, declared but not load-bearing:** whether `R_push` is p∥-separable as `R_xsec` is
(`R² = 0.868` by p∥ alone). If TRAINING is the reading, I expect separability to survive in `R_push`; if
it does not, that is a genuine surprise and will be reported as one rather than smoothed over.

## What this measurement CANNOT do, declared in advance

1. **It cannot clear `OI-126`.** `OI-126` blocks pairing `C_stat` with P5A. Localising the factor does not
   unblock it under any outcome.
2. **It cannot tell me the factor's value or identity**, only which side of training/extraction it enters.
   The factor arrays are not on disk — only `signal_factor_sha256` / `background_factor_sha256`.
3. **It cannot say whether `C_stat` survives.** A per-cell factor common to all 50 members may largely
   cancel in a **centred** covariance; that is a separate calculation and is not attempted here.
4. **It cannot say whether P5A is right.** The nominal agreeing with the MC prior in the band is
   consistent with a correct measurement *and* with an unfolding that barely moved there.
5. **One replica is not the family.** `replica_00` is used because the effect is present in all 50 (every
   one below the nominal in the band). If `R_xsec` for `replica_00` alone is below 2.0 the reading is
   UNINFORMATIVE by the table above rather than being retried on a more convenient member.

## Cost, corrected upward from my own earlier estimate

I told the mediator ~1.6 GB resident. **Re-derived from the compressed member sizes it is ~2.8 GB**:
`truth_scalars` 712 MB compressed → ~1.57 GB resident, `w_truth` 166 MB → ~0.39 GB, two `w_push` at
~0.39 GB each. A few core-minutes. **Wanted as a short interactive allocation, not a login-node run** — at
2.8 GB that is now etiquette rather than optional. No GPU. Nothing is written outside this lane's receipt.

**Constraints in force and unchanged:** read-only w.r.t. the campaign; `gate6traj-reconcile-56847059`
untouched; no `scancel` / resubmit / `scontrol update`; no launcher repinned; the cluster science repo not
pulled. The running `ff_closure` array `57012031` is another lane's and is not touched.

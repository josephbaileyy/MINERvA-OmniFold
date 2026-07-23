Continue the same durable `pet2_implementation_lead` session. This is the
single consolidated revision round after independent source and contract code
audits. Do not start any provider delegate/subagent/external process, do not
commit, and do not submit jobs.

Read the latest outputs in
`docs/orchestration/runs/omnifold_contract_auditor/` and
`docs/orchestration/runs/gregor_source_archaeologist/`. Implement the required
corrections. Preserve legacy defaults except for the independently verified
Gate-2 validator bug described below.

Priority A — required correctness:

1. Fix truth-coordinate periodicity in `g2_adapter.py`: use
   `(theta, cos(phi), sin(phi))`, matching the canonical loader. Add a boundary
   regression for objects just below/above ±pi.
2. Thread the receipt-bound G2 POT scale through the dataset contract into the
   engine. A G2 run must fail closed if a caller supplies an unset/different
   scale. Add a known-mass test. Synthetic datasets explicitly carry scale 1.
3. Remove `/1000.0` from the already-GeV `measured_scalars` and
   `bkg_reco_scalars` in
   `nd-unfolding/pet/gate2_target_runtime.py`'s independent histogram block.
   Add login-safe regressions: an out-of-domain GeV row remains out of domain,
   a multi-bin fixture occupies multiple bins, and the independent coordinates
   equal the loader/refiner GeV coordinates. Do not claim the historical
   independent receipt has been rerun.
4. Vectorize `stable_split`. The publication G2 NPZ is compressed and cannot
   satisfy streaming access: make the adapter explicitly mini-packet-only or
   add a true `.npy`/memmap inventory path. It must refuse, before materializing
   arrays, a large production NPZ unless a bounded/streamable representation
   is supplied. Do not advertise a full-G2 loader that eagerly reads 40–50M
   rows.
5. Add the dependency SPDX and absent-G2 unit-assumption clarifications
   requested by the source auditor.

Priority B — evidence-producing pilot, preregistered before results:

6. Add a known-ratio conditional-closure fixture. Pseudo-data must be derived
   from aligned simulated events with an analytic event weight so expected
   truth/reco ratios and closure projections are actually knowable. Add:
   - full-iteration closure metrics;
   - inverted-direction failure test;
   - weight/ratio quantiles, cap saturation by count and weight mass, global
     and declared-tail ESS, and at least two 2D/3D projection residuals;
   - machine-readable per-arm/per-seed summaries.
7. Add a cross-engine *ratio-convention* fixture with fixed logits/masses that
   proves the existing TF odds convention and the PyTorch balanced-logit plus
   mass-offset convention yield the same physical ratio. Do not pretend
   stochastic TF/PyTorch classifiers are layer-equivalent. Add a self-locating
   experimental TF A/B conditional-stress runner (recoil-only A versus current
   full-event B) that uses the same analytic fixture and writes JSON; it may be
   executed later inside the existing TF container.
8. Match the frozen preregistration defaults where a pilot claims comparison:
   estimator seeds 101/202/303, split seed 424242 or explicitly recorded
   stable split, AdamW lr `1e-4`, weight decay `1e-2`, two iterations and eight
   epochs per step. The CLI/launcher may keep a tiny smoke override, but the
   result recipe must state whether it is smoke or matched pilot.
9. Split global ablations so the muon-global addition is isolated from other
   rich globals. D-view remains distinct from D-typed. Do not require
   unavailable object types merely to run E-muon or an audited
   `E-rich-no-charge` view on G2. Parameter tensors must remain identical.
   Muon-token with unaudited/zero KNN coordinates must fail closed or be
   explicitly synthetic-only.
10. Add a read-only, deterministic, bounded xps2 memmap adapter/pilot seam for
    the safely staged recoil input. It must never load the 49M arrays eagerly,
    must record that `w_reco` is unavailable and any `w_truth` proxy footing is
    a downgrade, and must not claim full-event/G2 evidence.
11. Extend the public-Gregor diagnostic seam so an explicitly user-staged
    trusted `.pb` can be inspected under PyTorch for row/schema/type/padding
    census with a JSON result. It remains MC-only and must not be used for
    unfolding or silently unpickle unknown files.

Priority C — tests and launcher:

12. Add model parameter-parity, closure, direction, POT, periodicity, scale,
    arm-diff, public diagnostic, xps2 bounded-read, and Gate-2 unit tests.
13. Make the Delta launcher support one declared seed/arm at a time and an
    explicit matched-pilot mode, so the root can submit unique seed jobs and
    aggregate them without output races.

Run the complete login-safe suite, compile/shell checks, and report exact
files/tests. Do not run PyTorch locally, download inputs, change canonical
STATUS/RUN_LOG/VALIDATION_LEDGER, or claim any experiment result. If scope
forces a choice, complete Priority A plus items 6–9 and 12 first; clearly list
anything deferred for the root.

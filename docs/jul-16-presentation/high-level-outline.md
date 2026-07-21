# July 16 MINERvA talk — high-level outline

**Format:** 20 minutes + 5 minutes discussion  
**Audience:** first introduction to this research, and possibly to OmniFold  
**Working aim:** teach the core idea, establish trust with the 2D reproduction,
then show why higher-dimensional event-level unfolding is interesting.

## Possible throughline

> Learn weights on events instead of filling a response matrix; recover the
> published MINERvA result; then use the same idea to open dimensions that were
> previously difficult to measure together.

## Loose narrative arc

1. **The measurement problem** (~2 min)
   - Begin from familiar binned unfolding.
   - Motivate the dimensionality barrier without presenting OmniFold as a
     replacement for everything.

2. **OmniFold intuition** (~5 min)
   - Reco-level data/simulation reweighting.
   - Transfer through paired simulated events to truth.
   - Iterate, then choose bins and projections at the end.

3. **Trust anchor: reproduce MINERvA 2D** (~5 min)
   - Same published phase space and final binning.
   - Central-value comparison plus a compact validation/UQ message.
   - Emphasize that a known result was the first test.

4. **What higher dimensions reveal** (~5 min)
   - Add $E_{\rm avail}$ and other physically motivated coordinates.
   - Marginalization back to established lower-dimensional results as a
     built-in cross-check.
   - Known low-recoil/2p2h behavior as the main physics example.
   - Optionally tease the high-$E_{\rm avail}$, high-$W$ localization without
     quoting quarantined covariance-dependent significances.

5. **Where this could go** (~2 min)
   - Point-cloud/event-cloud inputs as an outlook, not a finished precision
     result.
   - Invite collaboration guidance on useful projections and publication-level
     validation.

6. **One-slide summary** (~1 min)

## Visual and animation ideas

These are a menu, not a prescribed sequence.

- **The dimensionality wall:** start with a populated 1D response matrix; expand
  it into a 2D/3D grid as cells multiply and become sparse. End by replacing the
  grid with an event cloud. This motivates the method before naming it.

- **One OmniFold iteration:** use paired reco/truth dots connected by faint
  lines. Let reco simulation morph toward the data as event weights brighten or
  dots change size; then let those weights travel along the pairing lines to
  truth. A loop arrow signals iteration. This could be the deck's central
  animation.

- **Bin at the end:** hold one weighted event cloud fixed while different axes,
  slices, or histograms appear around it. The same events generate several
  observables without retraining the audience on a new response matrix.

- **Reproduction reveal:** show the published spectrum first, then animate the
  OmniFold points or curve onto it. Reveal the ratio panel only afterward so the
  audience sees agreement before reading summary numbers.

- **Marginalization as validation:** show a 3D event volume collapsing along
  $E_{\rm avail}$ into the familiar $(p_T,p_\parallel)$ plane, which then aligns
  with the established 2D result.

- **Physics emerging with a new axis:** begin with the 2D projection, then open
  the $E_{\rm avail}$ dimension. Highlight the low-recoil region and reveal the
  effect of the 2p2h component as the relevant feature comes into view.

- **Localizing an excess:** let a broad discrepancy in a 1D projection resolve
  into a highlighted region of the $(E_{\rm avail},W)$ plane. Label it as a
  current central-value observation, with uncertainty conclusions still in
  progress.

- **Point-cloud outlook:** animate a detector-style cluster display into an
  unordered point cloud, then into a weighted event and several possible final
  observables. Keep this short and visually distinct from completed results.

## Visual restraint

- Prefer two or three memorable animations reused as visual motifs over motion
  on every slide.
- Use builds to control attention: one conceptual change per click.
- Keep a static final state for every animation so the deck still works as a
  PDF, in backup slides, or if presentation playback fails.
- Let color mean one thing consistently—for example, data, unweighted
  simulation, and weighted simulation should retain the same identities
  throughout.

## Likely backup themes

- Algorithm equations and density-ratio interpretation.
- Backgrounds, misses, fakes, and efficiency.
- Closure, pull/coverage status, iteration, and classifier dependence.
- Uncertainty propagation and current N-dimensional covariance status.
- Prior dependence and generator comparisons.

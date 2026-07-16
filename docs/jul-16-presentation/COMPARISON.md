# July 16 talk — comparison of the four presentation ideas

Audience: MINERvA physicists — fluent in the detector, the published 2D result
and D'Agostini IBU; new to OmniFold. Goals: (1) they *get* OmniFold quickly,
(2) they see why this research matters — results not reachable with binned
unfolding.

## The contenders

| | Claude Design deck (`design-talk/`, from claude.ai/design) | `sol-presentation/` | `visual-prototypes/` | outline + recommendation docs |
|---|---|---|---|---|
| What it is | Nocturne-themed deck (16 main + 12 backup) + 9 interactive animation candidates (A1–A9, 2–3 variants each) | Independent self-contained deck (14 main + 6 backup), own dark style, PDF fallback | 5 motion sketches + frame exporter | The shared plan both decks drew from |
| Structure | Implements `claude-design-package/outline.md` 1:1 (problem → teach → trust anchor → new dimensions → outlook) | Same arc but 6/14 slides on implementation + validation detail | n/a | n/a |
| Visual identity | Strongest: one design system, kickers/chips, quarantine warnings as UI, animation slots reserved | Serviceable but less consistent; heavy custom CSS per slide | on-theme sketches, superseded by the design project's `anims/` | n/a |
| Teaching OmniFold | Weakest link: Act 2 is mostly two-column prose + one static box diagram | Best: detector-distortion primer, classifier-as-ratio-estimator (w = p/(1−p)), spatial Step-1/Step-2 scenes incl. misses, "one weighted ensemble, many views" | A2/A3 concepts only | prescribes the beats |
| Hard numbers | Few on main slides ("sub-1σ") | Money-slide stat stack (1.011 / 1.006 / 94.1 %), validation grid (2D mean \|r\| 0.794 vs 0.798, explicitly not coverage; 5→10 iter 0.026 %; NN/GBDT 1.0078; descriptive C2ST AUC 0.535→0.501) | none (toy by design) | n/a |
| Honesty on the 2D tension | Omits χ²/ndf = 3.66 (paper full covariance) | States it plainly and explains it (correlated shape modes, not normalization) | n/a | rec doc: "experts smell overclaiming" |
| MINERvA-specific implementation | Absent | Four event trees w/ real counts, purity weight, xsec recipe, completeness = 1 | n/a | n/a |
| Physics payoff (Act 4) | Full act: marginalization anchor, 2p2h slide, (E_avail, W) excess slide | Compressed to one 3-card slide — underweights it | n/a | rec doc wants 5–6 min here |

## Verdict

**Base = the Claude Design deck.** It has the right arc for this audience
(trust anchor before novelty), the strongest and most consistent visual
system, the quarantine discipline built in as visible chips, and the
animation-candidate pipeline already wired to its slots.

**Merge in from sol-presentation** (its pedagogy and numbers are better):

1. Act 2 opener: the *detector-distortion → inverse-question* primer beat.
2. The classifier-as-ratio-estimator statement (w = p/(1−p)) — physicists
   get density ratios instantly; it demystifies the ML in one line.
3. Money-slide stat stack: total σ ratio 1.011, median bin ratio 1.006,
   94.1 % of bins within 10 % (all from `values.tex`).
4. A validation-numbers slide in the main deck (closure, the 2D same-ensemble
   mean-|r| Gaussianity check 0.794 vs 0.798 explicitly labeled not coverage,
   iteration doubling 0.026 %, NN/GBDT 1.0078, and the descriptive C2ST AUC drop
   0.535→0.501 with no calibrated p-value).
5. Honest χ² framing on the pull slide: pulls sub-1σ *and* paper-covariance
   χ²/ndf = 3.66 (correlated shape modes; 1.48 with the combined covariance)
   — the audience owns that covariance and will ask.
6. The four-tree / cross-section-recipe implementation content → backup
   (main deck has no time; Q&A will want it).

**visual-prototypes** is retired by the design project's `anims/` (same
concepts, more variants, on-theme); its `export_frames` tooling remains
useful for baking chosen animation variants to stills/GIFs.

Figure theme fit: main-act figures regenerated dark via `TECHNOTE_DARK=1`
(see `technote_style.py`, gated block) into `design-talk/talk/figures-dark/`;
backup figures stay as white plates. `pet_event_displays.png` has no
generating script in the repo (ad-hoc product) and stays on a white plate.

Animation slots: the 9 candidates in the design project need the design app
runtime (`x-dc` components) — they are review candidates, not embeddable
files. Pick winners on claude.ai/design, then bake the chosen variant's
frames (or a GIF) into the deck with `visual-prototypes/presentation-grade/
export_frames.sh` as the pattern.

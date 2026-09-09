# September 9: research with AI as an undergraduate

A complete working draft: 16 main slides, 7 backup slides, and a matching spoken
script. It uses the research to examine delegation, validation, and student learning.

## Open these first

- [Editable PowerPoint](research-with-ai.pptx) — native text and shapes, with the
  full script in speaker notes; figures are inserted PNGs.
- [Presentation PDF](research-with-ai.pdf) — portable version for projection.
- [Spoken script](SCRIPT.md) — editable prose, one numbered section per slide.
- [Printable script](speaker-script.pdf) — one slide's notes per page.
- [All slides at a glance](slide-overview.png).
- [Evidence and interpretation notes](EVIDENCE.md).

The opening keeps the “I nodded because I thought I understood” anecdote. The PhD
introduction is one friendly sentence, with discussion invited afterward. The
ending asks what a student should be able to demonstrate; it does not apologize
for being less knowledgeable than the audience.

## Personal account and interpretation

The revised talk adds the higher-dimensional generator comparison and a concrete
collaborator correction to the research framing. The checkpoint explanation connects
model identity to the weights entering the result.

The model-access slide was removed because the talk has no measured model comparison.
The checkpoint slide now defines the saved network parameters, best versus last
training epochs, and how these differ from per-event unfolding weights.

The revised talk uses Joseph's supplied account of audit-first frustration, orchestration debugging,
and uncertainty about detailed understanding. These are explicitly personal
recollections. The possible benefit of abstraction is framed as a hypothesis.
The talk reports research outputs without inventing a no-AI baseline, model ranking,
hours saved, or a learning improvement. Suggested workflow changes are proposals.

The main deck has 16 slides (roughly 25 minutes of spoken text, plus pauses);
slides 17–23 are optional backup. The physics section
includes physical projections, a complete residual map, and four representative
slices. Allow time to explain what each plot does and does not measure.

## Numbers and figures

`measurements/metrics.json` records the source revision, population definitions,
receipt digests, and inputs to every quantitative figure. `monthly.csv`,
`snapshots.csv`, and `commit_inventory.json` make the repository measurements
reviewable. The physics numbers come from committed receipts and hash-matched frozen ROOT inputs; no new
training, extraction, uncertainty construction, or cluster job was performed.

The main measured figures are:

- 2D transverse/longitudinal projections with our total uncertainty band, ratio
  error bars, and published reference errors.
- The complete 205-bin difference map and four fixed-pT slices with our total errors.
- A grouped uncertainty budget and comparison with the sources released by the paper.
- All 14 pT slices and cumulative agreement counts in backup.
- Monthly non-merge commits and the distribution of commit/path touches.
- Four generator predictions compared with the higher-dimensional corner integral.
- Historical event-weight disagreement between a run and its saved model.
- A backup plot of tracked Python file counts at monthly snapshots.

The normalization formula in backup is a diagram of integration, not a data measurement. All
twelve figures are available as PNG and vector PDF under `figures/`.

## Rebuild

Use Python 3.11 or later in a separate environment. Install the presentation dependencies:

```sh
python -m pip install -r docs/sep-09-presentation/ai-research-talk/requirements.txt
```

Re-measure the fixed September 8 revision, independent of the current checkout's tip:

```sh
python docs/sep-09-presentation/ai-research-talk/measure_history.py --revision 901f2c647355d69412b5c190fcb1df02d1c8aa14
```

Regenerate the plots from those measurements:

```sh
python docs/sep-09-presentation/ai-research-talk/make_figures.py
python docs/sep-09-presentation/ai-research-talk/plot_2d_comparison.py
python docs/sep-09-presentation/ai-research-talk/plot_uncertainty_sources.py
```

Build the PowerPoint, both PDFs, and slide previews from the script and layout:

```sh
python docs/sep-09-presentation/ai-research-talk/build_slides.py
```

Run the package's artifact checks:

```sh
python docs/sep-09-presentation/ai-research-talk/check_artifacts.py
```

The PDF uses the same line breaks and positions as the PowerPoint. It is produced
directly from the shared layout rather than converted by PowerPoint. Text is Arial
on the preparation machine. Open the PowerPoint once in the application used for
the talk to check font substitution; the PDF is the fixed rendering.

## Direct-comparison inputs

`inputs/ours_2d.root` and `inputs/published_2d.root` were copied read-only from the
existing frozen cluster artifacts. Both SHA-256 hashes must match the committed
agreement receipt before plotting. `measurements/two_d_bins.csv` exports all 224
cells with the reported mask and both files' pT boundaries;
`measurements/two_d_validation.json` records checks and comparison limits.

Three pT boundaries differ by 0.005 GeV/c. The plots preserve each input's real
boundaries and widths; bin ratios match corresponding indices. The four main
slices have identical physical boundaries. Slide 3 now includes our total covariance projected with full bin correlations.
The input hashes and checks against the committed uncertainty summary are recorded
in `measurements/two_d_uncertainty.json`. Ratio bars divide our sigma by the paper
central value; the paper band is shown separately. No combined uncertainty or
significance of the difference is constructed.

## Scope of the edits

Worktree: `/Users/josephbailey/local-research/MINERvA-OmniFold-presentation-sep09`  
Branch: `presentation/sep09-ai-research`

The original presentation folder was copied here, every file hash checked, and
only that folder removed from the production worktree at Joseph's request.


Everything for this draft is in this new subdirectory. The original `DECK.md`, the
existing verification draft and its measurement scripts, the analysis code, and
the note/primer/paper sources are not changed. The files are local working drafts;
no commit, push, external upload, or publication has been performed.

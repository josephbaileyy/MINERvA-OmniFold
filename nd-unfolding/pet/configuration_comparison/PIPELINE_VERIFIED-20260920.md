# The whole path runs and produces a number. The number is not a result.

**CITABLE FOR:** that every stage from built inputs to a scored recovery
executes on real data, and for the shapes and provenance below.
**NOT CITABLE FOR:** any comparison between the arms. The figures here come
from a plumbing check at 1/17 of the campaign's draw and 1/3 of its
iterations. Quoting them as a recovery would be quoting an undertrained
estimator on a twentieth of the events.

## What ran

| step | job | outcome |
|---|---|---|
| input build, 24 playlists | 58591372 | 2,260 npz, 91.4 M MC rows |
| join, three streams | 58597844 | `pass_reco` coverage **100.0000 %** |
| gather his tokens, once | in 58605416 | 4,141 pseudo-data + 10,000 prior rows |
| both arms, full closure | 58605416 | ours 147.8 s, his 160.5 s, finite weights |
| score both arms | scoring pass | aggregate and per-region recovery |

## What the scoring pass returned

Halves disjoint, 9,999 and 10,000 rows; three scoreable regions; no truth row
off the reporting grid.

| arm | recovery | projection | low_acceptance | moderate | good |
|---|---:|---:|---:|---:|---:|
| ours | +0.0197 | +0.0195 | −0.000 | +0.018 | +0.067 |
| his | +0.0401 | +0.0402 | +0.025 | +0.026 | +0.076 |

**Read this as plumbing, not physics.** Both arms recover a few per cent of the
injected displacement because both ran ONE OmniFold iteration on 10,000 prior
rows; the campaign runs three iterations on 200,000–600,000. The projection
tracking the recovery almost exactly says the estimators moved along the
injected direction rather than sideways, which is the sign the scorer is
measuring what it claims — and that is the whole of what this table supports.

## Why it is worth recording anyway

Every other stage of this comparison was verified on synthetic data first and
then failed on real data for a reason the synthetic case could not contain: a
driver that expected an array nothing writes, a gather that refused the
19.9 M rows the join legitimately produces, an engine writing into the pinned
checkout, a `tf.where` whose forward was clean and whose gradient was not. The
scoring pass had the same exposure and now does not.

One defect found here: `report_campaign._digest` assumed a `Path` and raised on
a `str`. `main` passes a `Path`, so the campaign route was never affected --
but `build_endpoint` is what anyone will call by hand when the campaign lands.

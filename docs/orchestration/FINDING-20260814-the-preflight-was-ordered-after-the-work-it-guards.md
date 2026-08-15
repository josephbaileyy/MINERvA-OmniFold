# A two-interpreter pipeline was run under one interpreter, and the missing import was discovered *after* the GPU pass

`BEN-280`. Lane: P5A extraction repair. Job `56978466` (`p5a_ann_extract`), FAILED `6:0` after
`00:12:57` on `nid001585`, 2026-08-14 17:26:56–17:39:53 PDT (= 2026-08-15T00:26:56–00:39:53Z; `sacct`
reports Pacific, the launcher's own `[p5a]` lines and the `.done` sidecar report UTC, and epoch
`1786754388` reconciles them).

## What failed, and what did not

**Not a physics failure and not an identity failure.** All six guards `G0`–`G5` passed: right arm by
schema (`lr_policy.schedule = fit-time-anneal-after-iteration-0`), right weights sha
(`559a1020…6eb3e`), right inputs sha (`fa6b3463…29625`), checkpoint contained in the promoted arm,
outputs outside it. Anyone arriving at the `6:0` and going looking for a wrong-arm run — which is what
this launcher was written to prevent, and what its header is mostly about — is looking in the wrong
place.

**The expensive work succeeded.** The full-inventory reweight ran to `49152885/49152885` (100%) and
wrote its payload. Its own subsample-agreement check passed at `max_rel_dev = 2.554037696012494e-05`
against `tolerance = 1e-3`, i.e. ~39× inside tolerance, with `subsample_agreement_is_vacuous: false`.

The failure, complete, from the `.err`:

```
extract_fullevent_fps.py:463   import unfold_2d_omnifold_unbinned as u2d   # imports ROOT at module load
2d-unfolding/unfold_2d_omnifold_unbinned.py:21   import ROOT
ModuleNotFoundError: No module named 'ROOT'
```

## The cause was an interpreter choice the driver had already documented

`extract_fullevent_fps.py:16-19` states the two stages need **different interpreters**: `push` "needs
TensorFlow, wants a GPU"; `xsec` "needs ROOT and numpy, **no TensorFlow, no GPU**". `:21-23` states
*why* they are split — "because the push pass costs GPU time that must not be re-spent when the
extraction recipe changes."

The launcher ran `--stage all` under `module load tensorflow/2.15.0`, which carries no ROOT. So it
spent the GPU time and *then* discovered it could not finish. This repo has a standing decision that
no combined ROOT/TF environment exists, so the split is not one option among several — it is the only
available shape, and the driver was already built for it.

**The proven template existed in-tree the whole time.** `sbatch_gate5_replica_extract_array.sh`
(Gate-5 replica extraction, completed 50/50) does exactly this split at its lines ~86-107: TF python
for push, `ROOT628_PREFIX` python for `--stage xsec`, with a ROOT import preflight between them.

## The generalisable lesson is about ORDER, not about ROOT

A preflight placed *between* the stages would have caught this — Gate-5's is placed there and Gate-5
passes. But it would have caught it **after** the 13 minutes of A100, because that is where the GPU
pass sits. The repair puts the ROOT preflight **before any long work** (`G7`), which is what converts
this from a 13-minute failure into a ~5-second one.

> **A preflight is only as valuable as its position. Order every environment check before the most
> expensive thing that depends on it, not merely before the thing that uses it.**

This is the cheap-check-first principle `CLAUDE.md` already states as *"a check costs zero and cannot
be skipped"* — the missing half is that a check's *cost* is zero but its *value* depends entirely on
where in the sequence it runs.

## A preflight written the naive way passes in one place and crashes in the other

Measured 2026-08-14 on a login node, and this is the part that would have bitten a careless repair:

```
$ROOT628_PREFIX/bin/python3 -c 'import ROOT'
→ SIGSEGV, rc=139
  ERROR in cling::CIFactory::createCI(): cannot extract standard library include paths!
  error: entry with relative path at the root level is not discoverable
```

Invoking that interpreter **directly** segfaults inside cling. It works only once
`setup_salloc_env.sh` has activated the env **by full prefix** (that script documents why: a
2026-07-02 conda base change broke activation by *name*). Gate-5's preflight line
`"$ROOT_PY" -c 'import ROOT, numpy; …'` looks self-contained and is not — it is load-bearing on the
`source "${DATA_ROOT}/setup_salloc_env.sh"` two lines above it.

So a preflight lifted out of that template without its activation would report a broken interpreter as
broken *when it is fine*, or — worse, depending on what the ambient shell had already activated —
pass and then let the real stage fail. The repair's `root_env_run` helper is the single definition of
"the ROOT 6.28 environment", used by **both** the preflight and the real `xsec` stage:

> **A preflight that constructs its environment differently from the run it guards is a lookalike, not
> a guard. Share one definition, so the check tests the real thing.**

## Note on `set -e`

`setup_salloc_env.sh` is not written to be `-e` clean, and the launcher runs under `set -eo pipefail`.
`root_env_run` therefore runs its body in a subshell with `set +e`; the subshell's exit status is the
`python3` call's own, so failures still propagate to `die`. The subshell also stops the conda
activation leaking into the TensorFlow push stage — the two environments must not mix in one shell.

## Push reuse: identity, not existence

13 minutes of A100 was already on disk, so the repair consumes it rather than re-spending it. But
adopting a push payload by **path** is `BEN-023`'s failure (`[[ -s $OUT ]] && skip` let 7 partial slabs
permanently block their own repair), and a push payload is a worse object to get wrong than a slab: a
partial or wrong-arm one yields a complete-looking cross section with nothing downstream able to
notice. `G6` therefore gates reuse on a regular non-symlink file, a non-empty `.done` marker, a
**sha256 pin**, the driver's own schema/fingerprint/coverage validators, an inputs-sha match against
`G4`, and the payload's own recorded agreement check being non-vacuous and passing.

Verified on the surviving payload: `sha256 a1debdb7105f3e531ec2e6ec5e08192d026238d5bac7eb5fe389e7e8f71bb9c9`,
262448947 bytes, zip intact, 11 keys, `w_push` 49152885 float64 all-finite, `mc_indices` exactly
`arange`, `validate_push_coverage → []`, `inputs_sha256` equal to `G4`'s pin, `source_weights` pointing
at the annealed arm.

The reused payload **keeps its originating job's filename** (`…push.slurm-56978466.npz`). Renaming it
under the repair job's id would launder 56978466's product into looking like the new run's own, and the
provenance of a GPU pass is exactly what must stay attributable.

## Power tests — both new guards, both directions

A guard that has never failed is not a guard. Run 2026-08-14 against the repaired launcher:

| Test | Injected | Result |
|---|---|---|
| `G6` sha pin | `P5A_EXPECTED_PUSH_SHA=deadbeef` | `rc=7`, `push payload sha mismatch`, **zero** `G6 PASS` lines |
| `G6` completeness | payload with no `.done` marker | `rc=7`, `carries no non-empty .done marker, so it must be treated as PARTIAL` |
| `G7` preflight | `ROOT628_PREFIX=/usr` (a python with no ROOT) | `rc=8`, reproduces `ModuleNotFoundError: No module named 'ROOT'` **in seconds, before any GPU time** |
| all pass | real payload, real ROOT env | `rc=0`, `G0..G7 all PASS, no job submitted, no GPU used` |

The third row is the finding's own proof: it is 56978466's exact error message, at zero GPU cost.

## What was deliberately NOT done

- `sbatch_gate5_replica_extract_array.sh` was **read as a template only**. It is hash-bound by an
  active receipt; editing it fails `verify_hash_bindings.py` (`BEN-270`'s class).
- `G0`–`G5` are **byte-identical** to the version that ran (diff of the region: empty, 83 lines each),
  in their original order and numbering. They all passed; none is what failed; none is touched. `G6`
  and `G7` are strictly appended.
- The unpromoted output contract is unchanged: `fullevent_nominal_annealed_extraction_unpromoted/`,
  `MARK=P5A-ANNEALED-UNPROMOTED`, `NOT_CANONICAL.json` still written. **Promotion is not authorized
  and nothing here performs it.**
- Nothing was submitted. The repair is held for the mediator's go.

## Related

`BEN-023` (completeness vs existence in resume guards). `BEN-026` (do not truncate the diagnostic
stream — the whole `.out`/`.err` being intact is why this diagnosis took one read). `BEN-270` (a pin
one hop away is still a pin). `CLAUDE.md`'s cheap-check principle, whose ordering half this sharpens.

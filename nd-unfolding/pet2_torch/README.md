# Experimental native PyTorch PET2-family backend

Status: independent, opt-in, synthetic/diagnostic only. It does not replace or
modify any TensorFlow/Keras, recoil-only, GBDT, ROOT, or publication default.

## Contract

- Explicit boolean token masks; continuous features never define padding.
- Category `0` is pad/unknown only; real types begin at `1`.
- Step 1 uses detector-observable reco/data/literal-background fields only.
- `w_reco` and `w_truth` remain separate.
- Negative background provenance remains signed audit metadata. Only the
  receipt-bound nonnegative Stay-Positive target reaches training.
- Truth-only misses skip Step 1, retain their incoming push, and enter Step 2.
- Balanced weighted BCE is calibrated by `log(W1/W0)` before the log-ratio cap.
- Full-order inference requires `mc_indices == arange(N)`.
- Every arm, preprocessing recipe, split, input, and output is fingerprinted.

The comparison arms are deliberately split:

- `C`: generic tokens on the TF-B-matched numeric footing, including the
  baseline reconstructed `(mu_pt, mu_pparallel)` summaries but no
  view/type/rich-global feature.
- `D-view`: C plus the separate detector-view category.
- `D-typed`: C plus real reconstructed object types, only when supplied.
- `E-muon`: C plus the remaining audited reconstructed-muon object globals
  `(energy, cos(phi), sin(phi))`.
- `E-rich-no-charge`: E-muon plus audited eavail/q3/MINOS/vertex globals.
- `E-rich`: E-rich-no-charge plus audited charge (unavailable for G2).
- `F`: unavailable until a strict manifest proves checksum, weight license,
  architecture, preprocessing, and tensor compatibility.

Every random arm uses the same fixed superset input tensors and parameter
shapes; disabled features are zero-masked. Overflow is a separate declared
switch. Muon-token mode is synthetic-only because G2 has no audited physical
KNN coordinate convention.

The reco arm is applied only to Step 1. Step 2 always uses the same
`truth-frozen` manifest: generic tokens, no detector view, no overflow/muon
token, and only the separately normalized truth-muon pT/p-parallel globals.
This prevents a reco view/type/rich-global ablation from silently changing the
truth density-ratio problem or manufacturing MINOS/vertex counterparts.

The default C/D/E capacity is the independently implemented PET2-small concept
profile established by the source audit: hidden dimension 128, eight attention
heads, eight transformer blocks, and four readout tokens. It is a conceptual
architecture match, not copied source or checkpoint compatibility. Tests may
request a smaller explicit profile for portable CPU execution.

The G2 adapter fails closed because the publication G2 and Gate-2 payload are
not included locally. It is explicitly a compressed-NPZ **mini-packet** seam:
it reads NPY headers first and rejects production-sized/40--50M-row NPZ before
`np.load`. It does not advertise eager full-G2 loading. G2 detector view is
not treated as object type, and no photon/blob/prong/dE/dx labels are invented.
The absent-G2 unit assumptions are recorded in every adapted dataset: point
clouds/muons/vertices are assumed MeV/mm and scalar kinematics already GeV,
matching the audited producer contract but not independently rechecked against
the locally absent minerva-ml payload. SHA binding is load-time evidence, not
a substitute for that absent-data validation.

The `/1000` error in the Gate-2 validator's independent scalar histogram was
corrected in source and covered by login-safe regressions. The historical
independent receipt has **not** been rerun and is not upgraded by this change.

G2 POT normalization is carried in the dataset contract from the Gate-2
receipt. An engine caller must explicitly repeat exactly that scale; unset or
different G2 values fail before training. Portable synthetic fixtures carry an
explicit scale of 1.

## Evidence fixtures

`make_known_ratio_closure_dataset` copies selected simulated reco rows into
pseudo-data and assigns the analytic event mass `w_reco * r(reco)`. It provides
known event-level reco/truth targets, native misses, signed literal background
provenance, full-iteration closure metrics, cap count/mass, global/tail ESS,
and two-dimensional and three-dimensional projection residuals. The CLI emits
per-arm/per-seed JSON. The frozen matched recipe is:

```text
fixture seed 424242; estimator seeds 101/202/303; split seed 424242;
70/15/15 split; two iterations; eight epochs/step; batch 512;
AdamW lr=1e-4, weight_decay=1e-2
```

Any override must use `--recipe smoke`, which records that comparison claims
are not permitted. `ratio_conventions.py` proves only the fixed-logit physical
ratio equivalence between TF posterior odds and balanced PyTorch logits plus
the class-mass offset; it makes no layer/training equivalence claim.

The optional `tf_ab_conditional_stress.py` runner is self-locating and can run
in the existing TensorFlow container. It executes the vendored `PET` and
`MultiFold` loop for recoil-cloud A and the same cloud plus reconstructed-muon
globals B on the analytic fixture. It is an experimental synthetic closure
test, not publication evidence or TF/PyTorch layer equivalence.

`xps2_adapter.py` opens user-staged `.npy` arrays read-only with memmap and
materializes at most a declared bounded packet. Its receipt says `w_reco` is
unavailable and that using `w_truth` on reco would be a downgraded proxy; it
cannot support a full-event/G2 claim.

`xps2_pilot.py` can execute that explicitly downgraded, bounded recoil-only
engine pilot. It uses `w_truth` as the unavailable reco-weight proxy, the
precomputed xps2 measured target, no literal background inventory, no event
globals/types/views, and a boolean mask derived from the historical producer's
zero padding. Its runtime/tail evidence cannot be used as typed-token,
full-event, G2, or publication evidence. Selection and estimator seeds are
separate so retraining comparisons can hold the sampled rows fixed; `--seed`
is retained only as a coupled legacy-smoke shorthand.

`public_gregor.py` can inspect an explicitly trusted, caller-checksummed `.pb`
using `torch.load(weights_only=True)` and emit row/schema/type/padding census
JSON. It never silently unpickles unknown files and remains MC-only.

Both diagnostics have JSON CLIs:

```bash
PYTHONPATH=nd-unfolding python3 -m pet2_torch.xps2_adapter \
  --directory /staged/xps2_npy --max-rows 100000 --out /tmp/xps2_census.json
PYTHONPATH=nd-unfolding python3 -m pet2_torch.xps2_pilot \
  --directory /staged/xps2_npy --max-mc-rows 100000 \
  --max-data-rows 50000 --selection-seed 424242 \
  --estimator-seed 101 --out /isolated/xps2_pilot
PYTHONPATH=nd-unfolding python3 -m pet2_torch.public_gregor \
  --path /staged/public.pb --expected-sha256 SHA256 --trusted \
  --out /tmp/public_pb_census.json
```

## Login-safe checks

From the repository root:

```bash
PYTHONPATH=nd-unfolding python3 -m unittest \
  nd-unfolding/tests/test_pet2_torch_contracts.py -v
PYTHONPATH=nd-unfolding python3 -m unittest \
  nd-unfolding/tests/test_pet2_torch_optional.py -v
PYTHONPATH=nd-unfolding python3 -m unittest \
  nd-unfolding/tests/test_gate2_target_runtime.py -v
PYTHONPATH=nd-unfolding python3 -m pet2_torch.cli \
  --out /tmp/pet2-contract-example --contract-only \
  --arms C D-view D-typed E-muon E-rich-no-charge
```

The optional tests skip cleanly when PyTorch or safetensors is absent.

## Delta one-A100 pilot

Create an isolated venv that inherits the `pytorch-conda/2.8` module rather
than installing into ROOT or TensorFlow:

```bash
module load pytorch-conda/2.8
python3 -m venv --system-site-packages "$PET2_VENV"
"$PET2_VENV/bin/python" -m pip install \
  -r nd-unfolding/pet2_torch/requirements-delta.lock
PYTHONPATH=nd-unfolding "$PET2_VENV/bin/python" -m unittest \
  nd-unfolding/tests/test_pet2_torch_contracts.py \
  nd-unfolding/tests/test_pet2_torch_optional.py -v
```

Launcher self-test:

```bash
PET2_REPO="$PWD" \
PET2_OUT_BASE=/work/nvme/bhvk/$USER/pet2_gregor_experimental \
PET2_ARM=C PET2_ESTIMATOR_SEED=101 PET2_MODE=matched-pilot \
PET2_DELTA_SELFTEST=1 \
bash nd-unfolding/pet2_torch/sbatch_pet2_fixture_delta.sh
```

Pilot submission is intentionally external to this implementation turn:

```bash
PET2_REPO="$PWD" \
PET2_OUT_BASE=/work/nvme/bhvk/$USER/pet2_gregor_experimental \
PET2_VENV="$PET2_VENV" \
PET2_ARM=C PET2_ESTIMATOR_SEED=101 PET2_MODE=matched-pilot \
sbatch nd-unfolding/pet2_torch/sbatch_pet2_fixture_delta.sh
```

Submit one job per arm and seed. The launcher uses one A100, eight CPUs,
arm/seed/job-specific output names, and rejects
the active `/u/jbailey2/MINERvA-OmniFold` checkout and known shared result
namespaces. The resulting evidence is synthetic-only and makes no G2 or
physics claim.

# Reproduce the typed-token comparison preparation

Start from the repository root. These files add an isolated diagnostic candidate;
no existing mapper, model, source-audit binding or production launcher is edited.
The report is [REPORT_FOR_BEN.md](REPORT_FOR_BEN.md). The approved execution and
resource amendment reached a [technical calibration stop](EXECUTION_STATUS-20260911.md)
before training. The [single corrected retry](RETRY_PROPOSAL-20260911.md) is now
[explicitly authorized](RETRY_AUTHORIZATION-20260911.md). The frozen proposal and [run-card.json](run-card.json) retain their
historical pending wording; the linked authorization records govern their scope.

Use the existing Python 3.11 environment with NumPy 1.26.4, TensorFlow 2.16.2,
Keras 3.15.1, SciPy and pytest. Imports of TensorFlow are lazy. The CPU synthetic
checks require no ROOT, source files, checkpoints or network access.

Run the representation regression suite:

```bash
python -m pytest -q nd-unfolding/tests/test_typed_descriptors.py \
  nd-unfolding/tests/test_typed_descriptor_keras.py \
  nd-unfolding/tests/test_typed_descriptor_source_smoke.py \
  nd-unfolding/tests/test_typed_descriptor_compatibility.py \
  nd-unfolding/tests/test_prong_semantics.py \
  nd-unfolding/tests/test_typed_token_comparison.py
```

Reproduce the documentary numbers from Git objects (no source access):

```bash
python nd-unfolding/pet/direct_token_comparison/reproduce_evidence.py
```

Run one small synthetic end-to-end software smoke in a new output directory:

```bash
mkdir /tmp/pet-routing-check
python nd-unfolding/pet/run_typed_token_comparison.py \
  --rows 32 --test-rows 16 --batch-size 16 --mode ordinary \
  --output /tmp/pet-routing-check/ordinary-17.json
```

The receipt plus two NPZ files and four Keras models appear beside the requested
output. Repeat in separate output names with `--mode injected` or `--mode shuffle`
for the other code paths. These tiny runs test mechanics, not closure acceptance.
Existing outputs are refused. A failed run writes `terminal=FAILED` and preserves
partial files; an allocation kill can leave only partial files, which are never
accepted by the reducer. One process runs P and D sequentially so their common
inputs and starting weights are directly shared.

After a separately approved, complete campaign, apply its frozen criteria:

```bash
python nd-unfolding/pet/direct_token_comparison/summarize_runs.py OUTPUT_DIRECTORY
```

This requires all 24 exact million-row receipts, verifies all six artifacts per
job and common input/truth/normalization/code fingerprints, and applies the
paired-seed interval plus safeguards. It rejects smoke receipts and missing jobs.
`NO_PASS` is not a statement of inferiority. The reported seed interval is not a
physics uncertainty product.

To reload a model in a fresh process, call
`typed_token_comparison.comparison_model_type()` before
`tf.keras.models.load_model(path)` to register its lazy custom Keras type.
`prepare_keras_inputs` supplies the packed family inputs; additionally pass
`generic_values` of shape `(rows, tokens, 5)` and an explicit boolean
`generic_mask`. Inputs must keep tokens contiguous by row; row order itself is
arbitrary. Every minibatch is repacked with all original objects, without a cap.
The reused family encoders enforce v2 categories, masks and normalization.

The reconstruction network sees only prepared detector inputs. The separate
truth model never receives the reconstructed representation choice. Changing
`routing` controls pooling before attention, not membership or normalization.
Current-C1 pooled-column equality is tested, but the attention bridge is not a
production `m_reco` integration and is not Gregor checkpoint-compatible.

For delivery, freeze the listed files and preparation hashes in a dedicated
commit based on `57b707b7`; preserve the occupied `pet-prong-semantics` checkout.
Do not run the large matrix before approval. The old audit's authorization is
consumed and cannot be reused.

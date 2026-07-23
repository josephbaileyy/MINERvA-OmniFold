# Attribution and reuse boundary

This package is an independent implementation. No source file was copied from
Gregor Krzmanc's `minerva-ml`, OmniLearned, or HyperScale.

The design uses general published ideas from particle-cloud transformers,
dynamic edge/nearest-neighbor networks, attention pooling, and OmniFold
density-ratio reweighting. The source audit found:

- `gregorkrz/minerva-ml` repository code: MIT, copyright Gregor Krzmanc;
- `ViniciusMikuni/OmniLearned`: MIT;
- `gregorkrzmanc/minerva-ml` public dataset: CC-BY-4.0;
- advertised pretrained checkpoint files: inaccessible, without published
  checksum or weight license;
- HyperScale source/license: unavailable for reuse.

Consequently arm F is explicitly unavailable and has no random fallback.
The optional public-data adapter is diagnostic MC-only evidence at immutable
revision `32e2f5040ff2678a2ef7ca1bc0b450b324f4fd83`; it never downloads data and
cannot satisfy the publication OmniFold inventory contract.

“PET2-family” and “PET2-small concept profile” refer only to independently
reimplemented public architectural ideas. They do not assert Gregor source,
tensor, preprocessing, or checkpoint compatibility.

Runtime dependency licenses (SPDX):

- NumPy: `BSD-3-Clause`
- PyTorch: `BSD-3-Clause`
- safetensors: `Apache-2.0`

ROOT and TensorFlow are not dependencies of this package. The optional TF A/B
stress runner is executed only inside the already managed TensorFlow
environment and does not alter it.

xr-linux results: byte-identical copies of the cluster originals under /pscratch/sd/j/josephrb/xr-linux-20261011/
(outroot/ mirrors that directory), plus digested text records of files the repository ignores (*.out, *.err).

HELD OFF THE TRACKED TREE, NOT HIDDEN: outroot/admission.json
  cluster original /pscratch/sd/j/josephrb/xr-linux-20261011/admission.json
  sha256 6b7660f44632bad13304209d17d3929bc7d5c7bed535176f70d80a27259f118d
  It binds docs/orchestration/AUTHORIZATION-20261011-xr-linux.md at sha256
  0c547f6eaceb0b80875f9889df5fe92d34c531cf09668dcc61643bdc688ee524 (one new live receipt binding)
  and setup_salloc_env.sh at ea3c6998... (already enrolled). Tracking it moves the receipt-binding
  inventory of docs/orchestration/verify_hash_bindings.py from 148 / 1b610bb3... to
  149 / 6a3787ea17b042e371908a70bc83f720300557fc9f1464ba9ddace9850215b13 (measured on this branch with
  the file present). Those constants belong to integration (the dispatch), so the enrollment is
  proposed in REPORT.md and not applied here. The verifier globs every *.json on disk, tracked or not,
  so the copy is kept outside the worktree as well.

Not copied: PF/a1/fixture/ (synthetic fixture inputs and products, ~1.6 MB; not results). Listed with
sizes in REPORT.md.

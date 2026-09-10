# Bounded PET v2 source-audit execution authorization

The user's 2026-09-10 response to the proposed bounded source audit was:

> okay should I have a fresh session do it or can you do it? you should have ssh access and can use an interactive allocation

This grants execution of the already specified source audit, including SSH and
an interactive CPU allocation. It follows the explicit proposal to audit commit
`588328438e096680a2295bebc7cc93ad9fccc3ed`, with two pinned sources, 75 branches,
entries `[0,4096)` per source, no fitting or training, and separate mapping,
semantic, release and object-family verdicts. The prior preparation-only boundary
is superseded for this source stage alone.

The external launcher authorization is preserved in
[source_audit_runs/20260910/authorization.json](source_audit_runs/20260910/authorization.json).
The bound preparation file SHA-256 is
`58e3043b43c446a5b7e057815fc1bfbf8edec782335ce412b09da9f996f91b59`.
Its source identities, schema, branches and artifact limits remain unchanged.

The selected runtime is an isolated environment layered over the existing
`root_6_28` environment, using Python 3.11.14, NumPy 1.26.4, TensorFlow CPU 2.16.2
and Keras 3.15.1. The ROOT conda activation must precede execution so its compiler
and library configuration are available. Dependency initialization and guarded
preparation checks precede any source access. Failure of these prerequisites
blocks the source audit without consuming a source open.

Interactive allocation `58164405` requested two CPUs and 8 GiB for 30 minutes.
Slurm allocated six CPUs to satisfy its memory policy; its limit was therefore
reduced to ten minutes, bounding the allocation at one CPU-hour. Audit steps
request two CPUs and retain the checker's two-thread ceiling. A source run must
finish within the allocation's remaining time; exhaustion cannot authorize an
extension, retry, wider sample or replacement source.

The measurement is source-to-row mapping and fixed-source telemetry, not
population support, calibrated PID, estimator equivalence, coverage or
publication readiness. Normalization, a selection sidecar, scientific training,
any additional source audit, and Gate-6 work remain outside this grant. The exact
Gate-6 prohibitions are still:

```text
do_not_select_passing_subset
do_not_construct_C_ML
do_not_move_central
do_not_start_leg_2
do_not_retry_unchanged
```

OI-126 remains ruled: the existing `C_stat` construction is unverified, its P5A
pairing is declined, and no PET total covariance is adopted. The completed probes
remain closed. A terminal failure is evidence to preserve, not permission to
change the scientific or resource contract.

# Synthetic PET source-audit runtime validation

The current authorization is:

> Continue resolving the runtime blocker with synthetic checks only. You can also use the cluster and spawn interactive allocs if you need

This covers isolated dependency installation, synthetic local checks and a
bounded interactive CPU validation. It does not reopen either ROOT source or
repeat the interrupted source audit. No fitting, scientific training,
normalization, Gate-6 work or scientific adoption is authorized by this task.

The cluster measurement is whether the complete fake-reader audit can initialize
ROOT and TensorFlow, map 8,192 synthetic rows, run fixed-weight C0/C1 forward
checks and serialize its chunks under the unchanged import guard and original
process ceilings. The reader uses only the committed synthetic JSON fixture.
ROOT is imported for library coexistence, but no ROOT file is opened.

The initial allocation ceiling is one shared interactive CPU allocation, at most
six reserved CPUs for ten minutes (at most one allocated CPU-hour), 8 GiB RAM,
with two CPUs per step and at most two observed process threads. The original
8 GiB address-space, 30-minute process wall, one-hour process CPU and 1 GiB
artifact ceilings remain enforced; the allocation ends sooner. No GPU is used.
An over-ceiling scheduler grant must be released before running a step.

Run from an isolated checkout of the preparation commit, using the existing
isolated audit runtime after activating the ROOT environment. The package pins
are in `source_audit_runtime_requirements.txt`; observed versions must travel
with the result. Guard policy and scientific source bindings are unchanged.

A successful terminal result demonstrates synthetic runtime compatibility only.
It cannot authorize real-source access, establish source mapping or release
applicability, validate coverage, change the declined OI-126 pairing, construct
`C_ML`, or adopt a PET covariance. The exact Gate-6 prohibitions remain:

```text
do_not_select_passing_subset
do_not_construct_C_ML
do_not_move_central
do_not_start_leg_2
do_not_retry_unchanged
```

## Numerical follow-up

The first synthetic Linux run passed dependency initialization but failed the
unchanged NumPy/Keras tolerance. The continuing runtime task covers a second
shared interactive allocation capped at six reserved CPUs for fifteen minutes
(at most 1.5 allocated CPU-hours). It may run fresh synthetic processes with
oneDNN enabled and disabled in separate output directories to measure the
numerical difference. Thread, memory and output ceilings remain unchanged.
No tolerance adjustment, guard change or real-source access is authorized by
this comparison.

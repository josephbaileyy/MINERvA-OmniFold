# Single compatibility/calibration attempt authorized

Joseph approved the proposal and bound repair at
`21c0d163a8aa7db1698f68f5ba00ddfd98fa5698` in the task conversation:

> I approve COMPATIBILITY_PROPOSAL-20260913.md and its bound repair at commit 21c0d163. This grants one additional attempt: one A100, 32 reserved Slurm CPUs, 56 GiB RAM, and 110 minutes total, with the specified 20-minute preflight and 90-minute calibration limits. Count all previous attempts toward the existing aggregate ceilings. Proceed to the frozen full matrix only after GPU compatibility, complete paired calibration, integrity checks and the existing 20% resource-headroom gates pass. No automatic retry, tolerance relaxation or scientific-design change is authorized. All existing scope restrictions remain in force.

The [machine-readable authorization](compatibility-authorization.json) binds the
[proposal](COMPATIBILITY_PROPOSAL-20260913.md) and unchanged repair manifest.
Historical pending records remain preserved. Exactly one new allocation is
covered; all earlier charges remain included, using at least 193 conservative
seconds. No retry or tolerance/design change is authorized. The frozen synthetic
matrix remains conditional on every named prerequisite; PET stays diagnostic
and method-development, with no real-source work, publication adoption,
covariance construction or Gate-6 action.

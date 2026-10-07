# Authorization: PET synthetic pooled/direct comparison

**Authorized by Joseph on 11 September 2026 in the task conversation.**
In reply to the final request to approve the execution plan, including committing
and pushing the frozen preparation on a separate comparison branch, Joseph wrote:

> I approve it, can you execute?

This grants the exact [execution proposal](EXECUTION_PROPOSAL.md), SHA-256
`6683321f59e3db26f0b662320fa72d584a4614b57db18768290749e1c9b4fb25`,
and [run card](run-card.json), SHA-256
`567e3eabe16b7c3fc79f597621880f882783d4caca00dff1beb54462b6f96284`.
Their historical pending wording is retained; this record supplies authorization.
The [preparation manifest](preparation-manifest.json) preserves the reviewed
file hashes before the grant. No scientific code or acceptance criterion is
changed by recording approval.

Authorized work: freeze and push preparation on `pet-direct-token-comparison`;
inspect the current environment and scheduler; one calibration allocation;
conditionally the 24 paired jobs; monitoring, reduction, evidence preservation,
and committed/pushed result, RUN_LOG and STATUS records. These covered steps
need no repeated permission request. The occupied `pet-prong-semantics` checkout
and other sessions' work remain untouched.

Limits are unchanged: calibration ≤2 A100-hours; full matrix ≤288 A100-hours;
≤2,336 total reserved CPU core-hours; ≤200 GiB added storage including durable
copy; ≤2 full jobs concurrently. Each allocation uses one A100, eight CPUs,
64 GiB; calibration ≤2 hours and each full job ≤12 hours. Calibration must
establish ≥20% headroom for the full matrix. A technical failure stops dependent
work with partial evidence and no retry or replacement.

The measured quantity is the paired synthetic routing difference under the
frozen fixture, training and acceptance rules. This authorizes no detector-source
access, real-input fitting/training, producer correspondence, central/statistical
pairing, covariance construction, publication adoption, uncertainty coverage or
Gate-6 work. Source-semantic prerequisites remain unresolved and no source-audit
grant is renewed.

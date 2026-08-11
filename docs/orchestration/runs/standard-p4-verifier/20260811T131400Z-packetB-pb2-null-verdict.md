# Packet B PB2 re-review — BLOCK on explicit-null presence only

Persistent `standard-p4-verifier` UUID `019f74cb-b85d-7ba0-96c5-dfbd09e59159` confirmed commit
`f67352f` correctly wires the canonical six-path closure into the production writer and checker,
fails closed on omissions/unresolved blobs, and covers the required integration directions.

The remaining blocker was `dict.get()` presence handling. Explicit JSON null for
`receipt_schema`, `surface_blobs`, both, or null schema beside a valid map was treated as absence;
three forms inherited grandfathering and the fourth passed the closure check outright. This
contradicted the receipt's “neither key exists” legacy rule.

The smallest repair is key-membership presence checking, value validation for every present key,
and real-CLI negatives for all four null shapes. Candidate and projection remained
publication-rejected and non-adoptable; no ROOT, covariance, physics, threshold, builder,
projector, adopter, or scheduler state changed.

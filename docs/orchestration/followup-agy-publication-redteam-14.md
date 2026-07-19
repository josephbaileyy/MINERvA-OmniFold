# Publication red-team follow-up 14 — G2 dumper memory blocker recheck

Resume the same persistent publication-redteam role and UUID. Do not broaden
scope and do not edit files.

Your previous review blocked `nd-unfolding/pet/dump_pointcloud_inputs.py`
because each of the three inventory readers retained a view of its large
preallocated backing array at final truncation. The implementation now uses
`out[key] = out[key][:k].copy()` in signal, data, and background readers.

Independently verify exactly these points:

1. all three required truncations now own compact arrays and no equivalent
   large-backing-array retention remains in these inventory paths;
2. the change does not alter row ordering, identities, dtypes, or schema;
3. the prior publication-blocking memory finding is resolved.

Local post-fix evidence is 66/66 tests passing (31 G2 dump, 10 atomic dump
contract, 25 FPS/PET) plus 474 static full-event schema checks. Treat those as
claims to inspect, not substitutes for your review.

Return a concise `PASS` or `BLOCK`. If `BLOCK`, give an exact file/line defect
and smallest safe correction. Do not dispatch another worker.

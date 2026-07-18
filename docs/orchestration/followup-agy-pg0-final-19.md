# PG0 final correction: verifier was read-only

Continue the exact `agy-publication-redteam` PG0 review. Your second PASS is
contradicted by direct evidence. Work read-only and do not repeat the ownership
inference.

Authoritative facts:

- `docs/orchestration/start-publication-plan-verifier.md` explicitly says
  “Work read-only ... Do not edit files”. Every follow-up repeats read-only.
- Its recorded JSONL contains read commands and verdicts, not an `apply_patch`
  or write event for the canonical files or reorganization plan.
- File mtimes predate the verifier: ND STATUS and reorganization plan are July
  15, OPEN_ITEMS July 16, KNOWN_ISSUES July 17; the verifier ran July 18.
- Reading a hunk in a verifier log proves existence, not authorship.
- `MIG-PUB-AUDIT1` records that canonical indexes were already dirty and PG0
  ownership/durability was blocked; it does not claim to own those hunks.
- Repository policy treats dirty/untracked work as another owner's unless
  direct evidence proves otherwise.

Issue the corrected fail-closed verdict. Identify the exact unresolved owner
evidence for the four-file packet and the safe interim rule (leave untouched;
A/C/B use co-located receipts and explicit-path staging). Do not propose
committing, deleting, or rewriting these files. End exactly with
`PG0-FINAL BLOCK` plus the evidence list.

Resume as the same independent G2 verifier UUID. Re-audit only the three
previous BLOCK items and the immediately related receipt wording in:

- nd-unfolding/pet/validate_g2_fullevent_domain.py
- nd-unfolding/pet/recover_g2_playlist.sh
- nd-unfolding/pet/test_g2_domain_validator.py

The canonical binary, base validator, and production launcher remain at the
same exact hashes from the prior round. Do not edit, publish, submit/retry/cancel
jobs, inspect unrelated playlist artifacts, or replace roles.

Delta since your BLOCK:

1. The out-of-domain census now fails closed whenever n_ood exceeds the actual
   captured index count, so a 100,000-row cap cannot silently omit inventory.
2. A base structural validator receipt parse/error is now fatal even when the
   subprocess technically ran.
3. Both FINAL_ROOT and RECEIPT are rechecked immediately before the publication
   hardlink sequence.
4. Recovery wording is plural and explicitly states the conditional-use
   contract: a downstream builder must enforce the receipt domain before
   training; Gate-1 publication alone does not prove exclusion.

Frozen validate-only reruns for the preserved 1D and 1E artifacts both returned
0 after the census-cap fix, with every out-of-domain row bound and no
non-superseded structural failure. The later structural-error/race checks do not
change ROOT scan results and will be rerun before publication.

Return PASS or BLOCK with exact remaining required changes. Explicitly state
whether --publish for both preserved artifacts is authorized. Preserve your
UUID.

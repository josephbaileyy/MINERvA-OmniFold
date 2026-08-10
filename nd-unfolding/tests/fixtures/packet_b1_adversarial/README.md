# Packet B1 — adversarial manifest fixtures (blind)

Six `std_component_manifest.json` variants, `B1_A` … `B1_F`. **Every one of them must be REJECTED by
the B1 band-set completeness check.** A run that accepts any variant has not closed defect #6.

## What they are

Each variant represents a **build that enumerated a wrong band set** — not a hand-edited manifest.
That distinction is the whole point. Tampering with a manifest alone is already caught: `Csyst` is read
from the stored ROOT (`p4_validate_active_lateral.py:158`), so dropping a key makes
`retained_sum + active_total != Csyst` and the identity gate at `:199` fails.

These fixtures instead represent the case where the builder itself used the wrong set, so:

- the manifest lists the set it built from,
- every reconstruction identity reads as **passing**,
- and nothing compares the listed set against the set that *should* exist.

The only thing that can detect them is comparison against an **external required inventory** — the
hash-pinned support-family ROOT's `hCov_universe5d_*` keys, per Packet B's acceptance criterion
("verified against a declared required inventory, not against the manifest's own list").

`identities/*` relerr values are deliberately left at the real build's values. A genuine short build
would have different but still-passing residuals; leaving them unchanged keeps every existing identity
gate reading PASS, which is the condition under test.

## Blind protocol

Authored by the oversight session, independent of whoever writes the fix, per **Packet B constraint 3**
— this lane has twice built a fixture shaped like its own assumption (BEN-040; repair-7's self-guard
stubbing the live blob to equal its fixture).

**Which band each variant perturbs is withheld,** at the fix author's own request, so that a check
which only catches (say) an omission at the end of a sorted list, or only bands matching an assumed
prefix, is exposed rather than confirmed. The answer key — variant → band, perturbation kind, and the
specific plausible-but-wrong implementation each one targets — is held by the oversight session and
released after the check is written.

**Reporting:** run the check against all six, report accept/reject per variant, and the key is used to
confirm. Do not inspect the fixtures for the perturbed band before the check exists; the fixtures are
committed so the result is auditable afterwards, not so the answer is available beforehand.

## Reference

Real manifest: `nd-unfolding/active_universe_5d/standard/candidate/std_component_manifest.json` on
NERSC scratch — 45 `all_syst_bands` = 40 `retained_bands` + 5 `replaced_lateral_bands`, 48
`candidate_keys` = 40 retained + 5 active + 3 totals. The audited product
(`602bbcf26606844941b8a6295f47e080507c20097a80f42cdf202bd8c567f037`) carries exactly those 48 TH2D
keys. No ROOT is needed to exercise these fixtures.

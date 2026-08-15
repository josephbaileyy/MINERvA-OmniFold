# CERTIFICATION 2026-08-15 — repair-8 defect #6 is CERTIFIED **AS SCOPED**

**Certified by the mediator under Joseph Bailey's grant of 2026-08-15** (`c1afe7a`,
*"I certify everything as long as multiple sessions have verified it"*). **This is the first use of
that grant.** The scope qualifier is not decoration — see §"What this does NOT certify".

## The bar, and how it was met

`CLAIMS.md`'s standard, which the grant invokes: *worker agreement is not verification; promotion needs
a recoverable artifact + an independent check.*

| condition | status |
|---|---|
| **recoverable artifact** | **YES** — eleven adversarial fixtures, committed at `8934c11` (A–F) and `db78475` (G–K), both **ancestors of the fix `0055826`** by `git merge-base --is-ancestor`. Pre-registered before the fix, not after. |
| **independent check #1** | **repair-8 verifier** — *"`0055826` implements it well (`p4_lib.py:373-431`, eleven blind fixtures)."* Declined to grant it, reading certification as Joseph's — **not** a judgement that it fails. |
| **independent check #2** | **HOLDS-WITH-QUALIFICATION.** A session that authored neither the fix nor repair-8. |
| **checks able to disagree** | **YES, demonstrated** — check #2 returned a qualification with a live consequence and a new defect (below), rather than a blessing. |
| **not `BEN-314`-shaped** | **YES, demonstrated structurally.** Check #2 *built* the plausible-but-wrong cross-field checker and ran it: **it accepts all ten must-rejects.** All eleven fixtures are Level-2 self-consistent, so no manifest-internal check can reject any of them. |

**The author's own verification was excluded from the count**, per the grant's reading of "multiple".
One disclosed exception is recorded rather than smoothed over: **fixture J is not blind** — the author
requested it after spotting the unpinned-referee hole themselves, and `0055826`'s own body says so.

## What IS certified

**`require_band_set_completeness` (`nd-unfolding/p4_lib.py:373-431`) removes the self-reference that
defect #6 named**, on the path that matters.

The reference set now comes from four sources, none of which read the validated object
(`p4_validate_active_lateral.py:231-234`): the support ROOT's `hCov_universe5d_*` keys with `_total`
excluded; hashes recomputed from that ROOT's TH2 contents; the module constant `P.BANDS`; and
`sha256_file(support)`. The manifest's `all_syst_bands`, `retained_bands`, `replaced_lateral_bands`,
`component_content_hash` and `candidate_keys` appear **only on the checked side**. Expected keys are
built **forward**; nothing parses a key backwards. **There is no `try`/`except` in `373-442`**, and the
`or []` / `or {}` guards fail **closed** — verified by running them.

`support_family_sha256` **is** bound before any set comparison: `:400-408` is the first statement
touching `comp`, `req = set(required_bands)` is `:409`.

## WHAT THIS DOES **NOT** CERTIFY — three residuals, and the third has teeth

**A bare, unscoped "defect #6 closed" would assert things demonstrated to be false.** That sentence is
exactly the unfalsifiable-verdict shape `BEN-077` exists to prevent, which is why this document
certifies *as scoped* and names the residuals.

1. **The pinning is OPTIONAL in the signature.** `required_support_sha=None` (`p4_lib.py:374`). Both
   live callers pass it, so there is **no live hole** — but run with it omitted, **fixture `B1_J` is
   ACCEPTED**, and J exists solely to catch an unpinned referee. The guarantee rests on caller
   discipline, not on the signature.
2. **The manifest still supplies the referee's IDENTITY.** The check demands
   `comp["support_family_sha256"] == sha256(--support)`, but **nothing pins the support ROOT's
   content**: no expected sha exists anywhere, `SUPPORT_FAMILY` is env-overridable
   (`run_p4_standard.sh:60`), and the only guard is a path-substring test living in the **builder**
   (`p4_build_components.py:92`), not the validator. A build that enumerated *correctly* from a short
   support ROOT still passes. **This is disclosed and deliberate** — the fixture file says in terms that
   *"a required inventory DECLARED IN CODE closes this for free, while one derived from the support file
   leaves it open"*, and the fix derived it from the support file.
3. **THE ADOPTER DOES NOT REQUIRE THIS GATE TO HAVE RUN. Filed as `OI-128`.** Verified independently by
   the mediator: `p4_adopt_standard.py:27` requires only `val.get("result") == "PASS"`, and **`gates`
   appears nowhere in that file except in a success print at `:84`.** The `component_manifest_sha256`
   binding at `:32-37` narrows the window — it excludes receipts predating the 2026-08-10 fix — but
   **does not close it**: a validation receipt produced between that fix and `0055826` carries the
   binding, records `PASS`, and never ran `require_band_set_completeness`. **It remains adoptable.**

**Also recorded:** the oversight session's discriminator file marks Level 1 and Level 2
`must_be_rejected_by_B1 = True`, and **nothing ever feeds those cases to the function.**
`TheContractForB1` asserts only class attributes. The property *is* established by the eleven JSON
fixtures; the artifact that **declared** the contract never executes it.

**Ordering, stated accurately rather than flatteringly:** within the *function*, the binding precedes
every read. Within the *gate*, ~110 lines of manifest-derived checks run first — including at
`:207-220` the very `C_syst` recomputation from `comp["candidate_keys"]` that defect #6 names. That is
not a hole, because every failure raises `P4GateError` inside one `try` and `result = "PASS"` is only
reached at `:246`. But the honest claim is the commit's own — *"bound before any set comparison runs"* —
**not** "bound before the manifest is trusted."

## Effect

- **repair-8 `outstanding` drops from 10 to 9.** It does **not** change the `BLOCK`: that rests on
  defects **#4 and #5**, in the live token gate, whose repair is separately in flight.
- **`OI-128` is opened** for the adopter gap. It is a **new** defect, not a reopening of #6.
- **No adoption or promotion of any covariance follows from this.** Certifying a defect closed is not
  adopting a product; the 5D covariance does not yet exist.

## Related

- `AUTHORIZATION-20260815-certification-on-multi-session-verification.md` (`c1afe7a`) — the grant.
- `runs/standard-p4-verifier/20260815T232546Z-repair8-verdict.json` (`7e3cb20`) — where #6 was
  `repaired_but_NOT_CERTIFIED_BY_THIS_VERDICT`.
- `0055826` — the fix. `8934c11`, `db78475` — the fixtures.

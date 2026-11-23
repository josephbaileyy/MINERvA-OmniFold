# COVFIX BINDING 1: the declaration's rules, P0, and code writing (director, 2026-11-23)

**Binds** `COVFIX-DECLARATION.md` as merged to main in PR #1258, at **M_C1 =
`90b29087742bfd167d6d981c769b1af8b88db8bb`**. The declaration's sha256 is
`464ce635d61d5cd91f8842f5290d133d61f5d84009a5f718fac5106c06f180d7` (rev 11.4, with its citation fix). Its rules,
bars, stop rules, readings and licensing table are fixed from this commit. §5–§7 change only by ST1's named exception, or
by an executability fix that changes no number, bar, family, seed or choice rule, made before the first spend of the
real PV seal (ST4).

## Authority

- **Joseph's go for the design**, to the director on 2026-11-22, verbatim: "yes can we do the measurability study.
  should we start working on the review's fix 1 too?". The director recommended starting with design, and Joseph
  agreed. That followed an outside review's "Fix 1". No separate DECISION file was written for it; this binding records
  it.
- **`DECISION-20261123-joseph-covfix-ki85-size-reader.md`:**
  - KI 85's two sentences are superseded for COVFIX;
  - full size as designed: two sealed tunes, full P1 counts, and N5 unconditional;
  - codex-school2 is the second reader, beside agy.
- **The ceiling, in Joseph's answers to the director, verbatim.** Each sha256 is of the text plus a newline:
  1. "Raise to 411.22 (Recommended)", `8fb26c62f91e7b20`;
  2. "Raise to about 540", `2edd5a1690819494`, for the headroom to fund a construction fix (PX);
  3. "541.5 is perfectly fine", `adc1262352d73d91`, which confirms the exact figure.

  **The ceiling is 541.50 node-h, and ST6 is its hard stop.** The expected price, with no ST1 firing, is
  410.55–411.22 node-h.

## What the director checked

- **The reads.** Twelve rounds, all committed under `reads/`. Rev 11's final reads were codex-school2 GO ("Blocking
  changes required: none") and agy GO. Revs 11.1–11.4 were text-only changes the director accepted:
  - non-blocking fixes;
  - the ceiling;
  - the durable director-held secrets;
  - outcome A's reach;
  - the PG roles;
  - the stdin framing and the seed range;
  - one citation.
- **The director's full read** of rev 11.2 (§1–§9), and the diffs of 11.3 and 11.4. The design matches the director's
  scope rulings:
  - no reduced-reporting candidate (K_C dropped);
  - one Gaussian reference law;
  - no testability veto, and no operating-rate claims;
  - outcomes A, B or none, plus the construction finding (Part 1);
  - FAILS read before REFUSED, with scoped refusals, so a refusal cannot hide an observed deficit;
  - every unfold job hashes its actual input, output and invocation.
- **Durable secrets.** The passphrase, seed base and salt live in the director's macOS login Keychain, and the
  consumption record and a secret-free README live in `~/director-tools/covfix/`. None of them is in /private/tmp, so a
  crash or the 3-day cleanup cannot kill the study.

## Rulings

1. **The declaration is bound** at M_C1, with the sha above.
2. **Authorized now:**
   - **P0** (§3.1): local, 0 node-h, descriptive, on committed spent records only. Its code goes through the full
     chain before it runs on the real records: unit tests, a line trace of every new line, hand mutants all killed, an
     agy and a codex-school2 read, and the shas to the director. P0's result is committed before it is sent to the
     director.
   - **Writing the code of every other phase** (§8), with the same chain for each module.
3. **Not authorized here:** any cluster work. PG, P1 W1, P1 W2, PX and PV each need their own binding addendum, written
   after their code's audit and their prerequisites.
4. **Roles:**
   - **cov2d:** the candidate builders, P0, the P1, PV and readout code, and PG's generic capture, encryption,
     seal-check and content-scan code.
   - **tune-generator** (the fresh PG session that Joseph opened on 2026-11-23): PG's tune support in F1's pipeline
     (TUNES, SPLINE_PINS, the reduce-stage qualifier, and GENIE_XSEC_TUNE handling), from PG's stat-only probe. It never
     reads COV2D, T2A, G2R or REGRADE, nor §5–§7 or `reads/`.
     - Its codex-school2 read is run by cov2d on its shas, under the decision above. tune-generator's own account
       allows no codex dispatch without Joseph's direct approval, and it keeps that rule.
   - **journal-editor:** the director's wrapper (`je/covfix-wrapper-20261123`). It has read only ST4, §3.4 and §4.2.
   - **The director:** generates and holds the secrets, publishes the seed commitment, and runs the secret-bearing
     roles (PG's connect, the PV writer, the PV readout) through the wrapper.
5. **Prerequisites for the first cluster binding (PG):**
   - **A committed iris receipt showing at least 541.50 node-h remaining.** If it shows less, the binding goes back to
     Joseph.
   - The wrapper, merged after its audit.
   - PG's package, merged after its audit: the tune support plus the capture and seal code.
   - The seed commitment, published.
   - The synthetic-seal end-to-end test is run before PV, not before PG.

**CITABLE FOR:** that COVFIX's rules are bound, and what is authorized. **NOT CITABLE FOR:** any result, any coverage
statement, any note wording.

# DELIVERY 2026-10-08/09 — uncertainty-investigation preparation (sessions A–E), integrated

**CITABLE FOR:** the integrated disposition of the five preparation goals in
[`PLAN-20261008-uncertainty-investigation-preparation.md`](PLAN-20261008-uncertainty-investigation-preparation.md);
the reconciliation of the lanes' outputs; the independent review and recomputation record; and the
smallest next decision for Joseph, with its cost. **NOT CITABLE FOR:** coverage or calibration of any
band, a change to any quoted number, an adoption, a change of estimator or uncertainty model, a
publication-scope change, compute authority, a lift of the `KNOWN_ISSUES.md` 85 deferral, or the
restart of any terminal campaign. Every preparation outcome below is a preparation outcome only.

## 1. Decision and terminal

*Are the pinned implementation, evidence and design ready for authorization of a specifically named
next experiment, not ready because of named defects, or infeasible under the stated constraints?*

**INFEASIBLE UNDER STATED CONSTRAINTS** for the named experiment, *2D repaired-bootstrap
independent-population per-experiment interval validation*. The decisive obstacle is populations.
The one ME-FHC MC production (MC/data exposure 4.708) supports zero disjoint pairs of a
production-size training bank and a data-size reservoir. The production omnifile carries no event
identity. No validated generative law exists that would let banks and pseudo-data be redrawn. Cost
is a supporting constraint, not the ground: 13,440–20,862 node-h at the optimistic measured rate
without reserve, 0.67–1.04 × `m3246`'s annual CPU allocation.

Three separate statements go with it:

- **Total uncertainty: NO-GO** (lane C). The procedure as performed (P1) is priced at 0.29–1.21
  million admitted node-h. The fixed-band calibration (P2) is INCONCLUSIVE, because its population
  construction is unpriced. Guaranteed model-dependence and response-departure bounds have no method.
- **The narrow statistical diagnostic N2 is NOT READY.** It is specified to admission level
  (DESIGN §16.1) and costs 9.8–12.2 node-h with a 20 % reserve, including the identity-carrying
  rebuild. It still needs four things: the scope choice in §6; Joseph's lift of the `KNOWN_ISSUES.md`
  85 deferral, which he set until after the publication package; a guarded, provenance-recording
  harness (§5, `KNOWN_ISSUES.md` 89); and its own registration and review.
- **Nothing is ready for a claim about the uncertainty attached to the quoted 2D central value.**
  That central (exact-split GBT) and every block of its uncertainty (LightGBM) are different
  estimators. Whether the blocks describe the central's uncertainty is unmeasured (§3).

A justified no-go completes this preparation. No outcome here launches compute, changes an adoption
or changes publication scope.

## 2. Fixed references

| item | ref |
|---|---|
| plan pin / dispatch base | `ad2716d8` / `f8e2bf85` (adds the plan, overrides rows, catalog route, E's baseline) |
| upstream `main` at integration | `33811d7d` (PR #58; publication files and `MANIFEST.tsv` only; merged in `8219eca4`) |
| final upstream `main` | `460631d1` (PR #59: the read-only publication audit under `docs/publication/audit-20261008/` and `MANIFEST.tsv` only; merged in `901f0088`, touching no reviewed file) |
| frozen lane tips (Joseph's list, verified 2026-10-09T07:10Z) | A `f762749d`, B `00f7cff1`, C `803f1dcc`, D `3fde202e` |
| integrated commit reviewed in the initial review | `cd0da202` |
| repair cycle 1 (final lane tips) | A `355174fe` (behavior) + `cc9eed27` (documentation); B `8ac300fa` + `c783d9c3`; C `57f6dd30`; D `926956d2` + `ecb52dde` |
| integrated commit of the focused review (cycle 1) | `ee61fb22` |
| E's freeze after the focused review | `287f25f5` (this file, STATUS, the proposal's §0, `integration.json`, `review-cycle1.md` and its recompute files) |
| final delivery commit | `901f0088` on `prep/uncertainty-e-20261008` (the freeze plus the `460631d1` integration) |
| closeout corrections | `prep/next-closeout-20261009`, from `901f0088`: §8 below; the record is `state/next-preparation-20261009/closeout/REPORT.md` |

At `901f0088` every file a lane commit touched is byte-identical to its final lane tip (A `cc9eed27`,
B `c783d9c3`, C `57f6dd30`, D `ecb52dde`). Every file changed upstream since the pin is
byte-identical to `460631d1`, except `MANIFEST.tsv`, which was regenerated from source
(`generate_manifest.py --check` exit 0). The closeout branch then changes A's, B's and C's documents
only by the corrections listed in §8. `integration.json` keeps the identity statement as of the
freeze (against `33811d7d`), because it is an immutable record; this paragraph supersedes it. No merge
to `main` was made. (Re-measured at the closeout, 2026-10-09.)

## 3. Reconciled contract

| element | integrated statement | source |
|---|---|---|
| implementation pin | driver `unfold_2d_omnifold_unbinned.py` after A's provenance commits `971fc00c` and `355174fe`: every new output records its effective arguments and argv, and the sha256 of the driver (read when `main()` starts) and of the OmniFold helper (read right after it is imported); rooted insert inside `main()`; `omnifold.py` digest `e96234124a31…` held | A §4, verification R1–R3; review F12 |
| quoted central `E_C` | `142a45b0…`, exact-split scikit-learn GBT, unpinned seed, job `53116554` (69,523 s, one busy core), revision `d1bc8813`, which has no estimator option | A `P01`; independently re-read by the review |
| statistical band `E_S` (`VL170`) | LightGBM, `--seed 1`, 300 Poisson replicas, both streams, purity fixed, completeness from un-resampled truth | A §2.1, §2.3; review §2 (5.6e-16) |
| systematic `E_U` / ML `E_ML` | LightGBM `--seed 42` with matched CV / seeds 1–10 | A §2.1; review §2 |
| pairing (18 rows: 10 VERIFIED, 4 DISPROVED, 4 UNRESOLVED) | same-estimator pairing of `E_C` with each block DISPROVED (`P02`, `P04`, `P09a`); transfer UNRESOLVED (`P03`, `P05`, `P07`, `P09b`); `E_S` internally VERIFIED (`P10`, `P11`); `P17` restates that no coverage test of `VL170` exists | A `pairings.tsv` after `cc9eed27` |
| size of the mismatch | centrals differ by median 0.97 % per bin (1.30 σ_stat; p84 2.76; max 8.32 σ_stat, 12.5 %); total ratio 0.9999; carried by no block | A §3; review §2 (1.300 / 2.758 / 8.323) |
| mask, order, normalization | 205 bins, identical across all five masks; row-major (p_T, p_∥) = paper GlobalID; identical POT, nucleons, flux | A §2.2; review §2 |
| covariance conventions | `C_S` sample ddof 1; `C_U` per-band mean-centred 1/N plus the 1.4 % rank-1 term, as `analyze_universes.py:231-253`; Flux rescale exactly Φ_CV/Φ_u | review §2, F11 |
| budget denominator | 6.8707 % against the seed-42 CV, 6.8269 % against the quoted central | A `P14`; review §2 |
| population and conditioning | primary needs independent production-size banks per experiment or a validated generative law, plus event identity (R0) and disjoint hash folds; template statistics conditioned out | B §3–§6 |
| assurance | N = 719 (coverage, 206 functionals × 2 levels), 1,116 with the bias test at its tolerance edge; four-case family 823 / 1,250 | B §10, C §5; review recomputation |
| cost | primary 13,440–20,862 node-h (optimistic, 5 % retry, no reserve); N2 9.8–12.2 with reserve; C's P2 575–3,518, P1 0.29–1.21 million; keeping `E_C` in C's P2 5,728–268,936 | B §14, C §6 (after C REPAIR 1); review §2 |
| verification reserve | 20 % of any later total, protected; B's figures are lower bounds on C's admitted totals | plan; C §6; B §14 |

## 4. Contradictions and dispositions

| # | contradiction | disposition |
|---|---|---|
| X1 | Three different next decisions. B named the KI-85 lift for N2. C said the central-estimator choice comes first and "nothing downstream is admissible". A named which estimator a validation targets (review F1, material) | **Composed** (§6): the scope choice first; then N2, only if that choice makes the LightGBM statistical estimator the target. C scoped its sentence to claims about `E_C`'s uncertainty and the total (C REPAIR 1). B named N2's premise (B REPAIR 1) |
| X2 | B quoted C's superseded cost for keeping `E_C` (review F2, material) | B REPAIR 1 cited C's FREEZE. C REPAIR 1 then moved the figure (F9), and B REPAIR 2 cites `57f6dd30`. Not verdict-bearing |
| X3 | B treated the `m3246` balance as a ceiling on all work (review F3, material) | B REPAIR 1: cost is a supporting constraint against named comparators; the NO-GO rests on populations. This delivery labels it the same way |
| X4 | B said no assumption differs between B and C; C listed four (F6) | B REPAIR 1 lists them. N2 is quoted with the 20 % reserve |
| X5 | C said the blocks "do not describe `E_C`" (F8) | C REPAIR 1: produced by LightGBM, not by `E_C`; transfer unmeasured |
| X6 | A's `P09` label mixed "different estimator" with "seed-noise transfer" (F10) | A REPAIR 1 (`cc9eed27`): `P09a` (same-estimator / proxy) DISPROVED; `P09b` (seed-noise transfer) UNRESOLVED. Tally 10/4/3 over 17 → 10/4/4 over 18; A's FAIL disposition unchanged |
| X7 | The 2D STATUS headline said "lgbm" for the exact-GBT central; it listed GEANT as lateral; it called PPFX index alignment "verified" | E corrected STATUS (headline; lateral list per `runEventLoopOmniFold.cpp:238-244`; PPFX qualified) |
| X8 | The successor proposal §2 called the quoted central a LightGBM result | E reconciled the proposal in place (§0) |
| X9 | The reference and README attributed the helper-digest condition to the ruling line (F13) | D REPAIR 1 (reference) and REPAIR 2 (README) |
| X10 | C's exact-central branch double-counted the LightGBM sweep and priced exact universe unfolds at the CV rate (F9) | C REPAIR 1 fixed `costs.py`: 5,566 / 263,513 → 5,728 / 268,936 |
| X11 | B's sensitivity table header said [1/x, x], but the code used rounded bounds (F7) | B REPAIR 1: exact reciprocals; 1,632 / 1,030 (and 322 at x = 4/3) |
| X12 | The pairing-row labels `P02`/`P03` differed between C's reconciliation and A's FREEZE (B "For E") | Label only. A's FREEZE numbering governs |

## 5. Engineering gate: the OI-136 ratchets (review F4, material)

Both `OI-136` ratchet suites fail, with byte-identical failure lists, at the pin `ad2716d8`, at
upstream `33811d7d` and at the integrated tree. No lane caused them. Nine `.py` files added on
2026-10-03…06 put the canonical cluster root at `sys.path[0]` and are on neither named list. Seven
are receipts and may only be classified. Two are live producers: `fixed_truth_toy.py` and
`ki85_compare.py`. The 2026-09-03 authorization covered a fixed 45-file population. It neither
repairs nor classifies these nine, and `OI-136` is `unassigned` in the register.

The practical consequences are three:

1. While the suites are red they cannot catch a tenth site.
2. The coverage toy producer loads `omnifold.py` from the canonical checkout whatever tree launches
   it. Because it calls the helper directly rather than the driver's `main()`, the new provenance
   records are never written for toy outputs.
3. Any next experiment's request must therefore name a guarded launch (`mnv_guarded_run.py`) and
   helper-digest capture for every producer it runs.

This does not block a decision that runs nothing (§6). It does block admitting N2 or any harness
built on the toy pattern until the `OI-136` owner, with Joseph's ruling, classifies or repairs the
nine sites. Recorded as `KNOWN_ISSUES.md` 89. No lane edits them.

## 6. The smallest next decision for Joseph

**How the quoted 2D result pairs its central value with its uncertainty.** This decision needs no
compute. Every other next step depends on it, including whether N2 is ever relevant. The article
already says the uncertainty ensembles use a different implementation from the central
(`docs/analysis-note/paper_body.tex:126-129`, in the estimator list at 114-137). It does not say that the transfer is unmeasured, or
how far apart the two centrals are.

| choice (A §7 label) | what it means | cost | what it permits next |
|---|---|---|---|
| **Keep and disclose** (A "(a)") — *recommended* | Keep the exact-GBT central. State that its uncertainty was computed for the LightGBM implementation, and that the transfer is unmeasured (centrals differ by a median 0.97 % per bin, 1.3 σ_stat; total ratio 0.9999). Any statistical validation then targets the LightGBM estimator only, explicitly not the quoted central | **0 node-h.** If the deliverables are to say so, that is a wording change by the publication owner, with the three-build and standalone synchronization | N2 becomes a candidate (below) |
| **Measure the transfer** (A "(b)") | Run the exact backend for the missing operands: `P03` (50 exact bootstrap replicas), `P05` (exact universes) and `P09b` (exact seed scan) | about 34–39 node-h for `P03` at N = 50, if A's memory packing holds (contention unmeasured). For all three, about 170–350 node-h with exact universes at the CV rate (A's `P05` price), or about 330–510 node-h with C's repaired universe/CV ratio (review cycle 1, N2). No observable or tolerance has been predeclared, so it needs a design and its own authorization | a transfer verdict for the quoted central |
| **Re-quote the LightGBM central** (A "(c)") | Make the seed-1 LightGBM product (it exists) the quoted central, matched to the `VL170` band | 0 node-h for the central and its statistical band. Systematics stay seed 42 (`P07`): a seed-transfer measurement is 6–18 node-h, a matched seed-1 sweep 25–94 node-h. This is an estimator and publication-scope decision, and the comparisons and figures are re-derived | N2 then tests the quoted central's statistical estimator |

**Recommendation: keep and disclose, now.** E's rationale, a judgement rather than a measured fact:
it costs nothing; a pairing statement of some kind is needed in the assembled package whichever choice
is made; and the other two choices need new admission artifacts first. If Joseph chooses
keep-and-disclose or re-quote, then, after the publication package (his `KNOWN_ISSUES.md` 85 ruling),
N2 is the one statistical experiment specified to admission level: 9.8–12.2 node-h with reserve. It
would still need a registered design, a guarded harness (§5), the identity rebuild with its
equality check, the per-bin ESS reduction and its own review.

**What the decision cannot authorize.** It cannot validate coverage of `VL170` or of real data,
validate any total, adopt a product, change a band, lift the `KNOWN_ISSUES.md` 85 deferral, or
admit compute.

## 7. Integration rubric

| gate | assessment |
|---|---|
| current authority and baseline | **PASS.** One pin; the upstream delta is publication-only and reconciled |
| estimator identity | **PASS** scoped to the LightGBM statistical estimator (`P10`, `P11` VERIFIED). **NOT READY** for any claim about the quoted central (`P02`/`P04` DISPROVED, transfer UNRESOLVED) |
| engineering behavior | KI-84 regression and negative control pass; A's driver change is clean (review F12). **NOT READY** for a new producer while the `OI-136` ratchets stay red (§5) |
| population independence | **NO-GO** for the primary: no independent production-equivalent populations; no event identity |
| procedure and claim | Explicit: reconstructed per-experiment intervals as primary, fixed-band transfer as a labelled secondary; purity re-estimated per experiment by design; template statistics conditioned out; prior equals truth |
| statistical assurance | Prospective, proposed tolerances; complete functional family; coverage and bias sized separately; one fixed look; counts independently reproduced |
| feasibility | Primary priced, not admitted. N2 priced with reserve; the identity rebuild's billing is assumed |
| total-uncertainty boundary | C's component dispositions: P1 INFEASIBLE, P2 INCONCLUSIVE, unscoped bounds have no method. Anything statistical stays labelled statistical-only |
| supported workflow and preservation | **PASS** (D): four navigation tasks reproduced by the review; paths resolve; hash bindings intact; no frozen file edited |
| independent review and delivery | Initial review at `cd0da202`; material findings F1–F3 repaired by their owners and confirmed RESOLVED in the focused review at `ee61fb22`; F4 is routed (§5), and it binds N2 and any new producer, which are NOT READY, not the zero-compute decision in §6. No new material finding; cycle 2 was not used (§8) |

## 8. Review and repair record

- **Reviewer.** One fresh read-only context (Claude Opus 5.5, Claude Code subagent), no authorship of
  A–E work, in a detached worktree at `cd0da202`. Its tree status was empty at start and end. It
  wrote only to external scratch. CAMPAIGN-REVIEW-20260929 §5 suggests Astra High, which was not
  available through this session's tools; this is recorded rather than treated as a mandate.
- **Independent recomputation.** The reviewer wrote its own code and did not call owners' scripts.
  It reproduced from byte-copied operands, each checked against a remote `sha256sum`:
  - the masks, `C_S`, `C_ML`, `C_U` and its convention, the Flux rescale, the budget medians under
    both denominators, and the central comparisons;
  - the central-backend evidence (sacct, revision);
  - 719 / 1,116, the acceptance regions, the bias N, 823 / 1,250 and the finite-reference failures;
  - the per-run node-h, B's totals, C's P2, P1-optimistic and setup rows, and the `E_C` branch.

  Preserved verbatim with digests: [`review.md`](state/uncertainty-preparation-20261008/e/review.md),
  [`recompute/`](state/uncertainty-preparation-20261008/e/recompute/).
- **Findings.** Four material (F1–F4), four minor (F5–F8), five notes (F9–F13). The owners repaired
  F1–F3 and F5–F13 on their own branches in cycle 1 (§4). F4 has no lane owner and is routed (§5).
- **Focused review (cycle 1 of 2).** Same reviewer, resumed at `ee61fb22`; worktree empty at start
  and end; preserved at [`review-cycle1.md`](state/uncertainty-preparation-20261008/e/review-cycle1.md).
  F1–F3 and F6–F13 RESOLVED; F5 PARTIAL; F4 routed, still open. A's `355174fe` verified: KI-84 15/15
  with the bit-identity class, insert inside `main()`, bindings intact, and the new test fails on
  write-time mutants of either digest. Moved numbers reproduced: C's exact-central branch
  5,728.5 / 268,936.4 and rebuild 292.17 / 8,297.51; N2 with reserve 9.787–12.162; B's sensitivity
  row. The integrated terminal labels and the §6 decision were judged supported, neither overstated
  nor understated, with §6 the smallest available decision. **No new material finding.**
- **After cycle 1** E repaired its own surfaces for the cycle's minor findings: N2 (both universe-rate
  conventions in §6), N3 (the proposal's §0 now cites the focused review), N4 (`P09b` labels in §6 and
  STATUS) and N5 (the §6 rationale marked as E's judgement). These wording repairs were not
  re-reviewed. Cycle 2 was not used.
- **Residual minor findings, and their closeout (2026-10-09).** E left three to the lanes, which had no
  repair left. Joseph authorized a narrowly scoped closeout correction of their text, which does not
  reopen any lane's design. It is on `prep/next-closeout-20261009`, and its record is
  `state/next-preparation-20261009/closeout/REPORT.md`.
  - Cycle-1 N1, **corrected in B's DESIGN §7, §16, §17 and §18.** The DESIGN called N1's truth-free
    variant "not ruled out". N1 fixes the bank but bootstraps both streams, so the outer scatter lacks
    the MC-stream term. An exactly calibrated bootstrap then gives κ ≈ √(data share) ≈ 0.59 (0.594 at
    N1's half-MC bank, 0.587 at N2's 48 % bank), below the 0.80 edge. That also fails N1's own coverage
    test, so the reference-aware variant is not open either. Either variant needs a data-only inner
    stream, which makes it a data-stream diagnostic of N2's kind. It is unpriced, and it is not a
    coverage test.
  - Cycle-1 N4, **corrected in C's assessment.** The five unsplit `P09` labels now read `P09a`
    (estimator identity) or `P09b` (transfer).
  - Cycle-1 N2, **labelled in A's and C's price lists.** A's `P05` price (about 128 node-h) assumes that
    an exact universe unfold costs what the exact CV unfold does. C's universe/CV ratio gives about
    285 node-h. Both are forecasts, and §6 quotes both conventions.
  - Cycle-1 F12 note, open (A's engineering; nothing in the closeout's scope). The new test cannot
    distinguish hashing at `main()` start from hashing at helper import. A helper imported before
    `main()` by a caller would be hashed from the current file.

## 9. The five scrutiny questions

1. **Estimator identity versus covariance transfer.** "Different estimator" (shown) and "the
   uncertainty does not apply" (not shown) are kept apart in A, and now also in C (F8) and in A's
   split of `P09` into `P09a`/`P09b` (F10). The
   plan's FAIL label for A is applied as written: a pairing is disproved. It does not mean the quoted
   uncertainty is numerically wrong.
2. **Do B's population requirements justify its no-go?** Yes. They come from the plan's own text and
   from the statistics: outer MC variability cannot be the same bootstrap of the same bank. With
   MC/data 4.708, disjoint production-size sets number ⌊4.708/5.708⌋ = 0. The held-out alternative N1
   "fails as specified" for two reasons: its finite reference is treated as exact, and its fixed bank
   with a both-stream inner bootstrap leaves the outer scatter without the MC-stream term (κ ≈ 0.59 for
   an exactly calibrated bootstrap; review cycle 1, N1). The second reason applies to N1's coverage
   test as well, so neither variant is open with that inner bootstrap. With a data-only inner stream
   either one becomes a data-stream-only diagnostic of N2's kind, unpriced (B DESIGN §7, closeout
   correction).
3. **Costs of the specified designs versus all designs.** No lane now claims infeasibility for an
   unpriced design. Cheaper inner procedures (B = 50), smaller families and looser tolerances are
   priced as separate procedures. None is validated, so none contributes admitted savings. The
   `m3246` balance is a comparator, not a ceiling.
4. **The pre-existing OI-136 failures.** They were red at the pin. They have three practical
   consequences, listed in §5, which bind any new producer, not the decision in §6.
5. **B's final design versus C's earlier reconciliation.** Their counts, rates, R0 price, population
   statements and pairing ids agree. The disagreements were B's stale C figures (twice, the second
   caused by C's own repair), B's "no differing assumptions" sentence, and C's "nothing downstream"
   scope. All are repaired (§4).

## 10. Unresolved, consequential

- Every transfer from the LightGBM blocks to the exact central (`P03`, `P05`, `P07`, `P09b`).
- The nine `OI-136` sites (§5): owner `OI-136` route, with Joseph's ruling.
- `VL170` coverage: never tested. The `KNOWN_ISSUES.md` 85 held-out re-test is deferred by Joseph.
- The PPFX index identity has no receipt (`KNOWN_ISSUES.md` 91). The ordinal mask alignment is a
  latent risk (`KNOWN_ISSUES.md` 90).
- Executed bytes of the central, sweep, matched-CV and seedscan runs, and of any historical helper.
- Unmeasured operands behind B's design: per-bin ESS and the smearing share (they need the 2.1 GB
  omnifile), R0 billing and exact-unfold packing contention.

## 11. Resources consumed (all lanes; zero cluster node-h, zero GPU-h, no training, no toys)

| session | active time | local CPU | notes |
|---|---|---|---|
| A | about 0.9 h + repair | < 0.2 core-h | 34 MB product copies, deleted after use |
| B | about 0.9 h + 2 repairs | < 0.05 core-h | login-node metadata reads only |
| C | about 0.9 h + 1 repair | < 0.02 core-h | |
| D | about 0.9 h + 2 repairs | < 0.1 core-h | |
| E, including reviewer | about 1.1 h (05:50–06:02, 07:10–07:52, 09:50–10:05Z) plus the reviewer's 0.7 h (0.4 h initial, 0.3 h focused) | < 0.3 core-h | reviewer: 46 MB copied and checked against remote sha256, scratch peak 1.3 GB, deleted after preservation |

Total well inside the plan's 30 h / 14 core-h ceilings. No allocation, idle allocation or campaign
budget was used.

## 12. Session record (E)

Owner: E (Claude Opus 5.5, `claude-opus-5-5`, Claude Code; effort not exposed to the session).
Reviewer: one fresh subagent context as in §8. A–D owned their surfaces and made their own repairs,
requested by E through cross-session messages. Integration branch `prep/uncertainty-e-20261008`,
pushed without force. No pull request, merge to `main`, tag, release or external message.

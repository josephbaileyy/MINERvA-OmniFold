# Focused review, cycle 1 of 2 — preserved by E

Preserved verbatim by E from `/private/tmp/minerva-uncprep-review-20261009/review-cycle1.md` (sha256 `adbd2c12bb9a37b4d65f16b250426ff273ac85b7e0fbabbe1b7f0cd24d3f43b0`, 11688 bytes). Same reviewer as
[`review.md`](review.md), resumed for one focused cycle on the integrated commit `ee61fb22` (interrupted
by a usage limit at about 07:52Z and resumed at 09:51Z). Its two new scripts and three logs are under
[`recompute/`](recompute/). Paths starting `recompute/` in the text are relative to the reviewer scratch.

---

# Focused review, cycle 1 of 2 — integrated commit `ee61fb22`

Reviewer: same read-only reviewer as the initial review. Scope: the owner repairs, A's behavior commit
`355174fe`, the numbers that moved, and E's new integration surfaces. All numbers come from my own code.

## Status and HEAD

| when (UTC) | `git status --porcelain` | HEAD |
|---|---|---|
| start 07:48:26Z | empty | `ee61fb223668252dc571327af7678d40c3d47aee` |
| resume 09:51:14Z (after the usage-limit interruption) | empty | `ee61fb22…` |
| end 09:52:46Z | empty | `ee61fb22…` |

- Tests ran with `-B`, `PYTHONDONTWRITEBYTECODE=1` and `TMPDIR` set to my scratch.
- Mutants were built only in scratch and then deleted.
- No git write command. No cluster access in this cycle.

## 1. Repair status against the initial findings

| finding | status | evidence (at `ee61fb22`) |
|---|---|---|
| F1 next decision | **RESOLVED** | B DESIGN §17 "Next decision" (names stage-0 premise); C ASSESSMENT §8 stage-0 row and "For E" item 4 (scoped to `E_C`/total claims); DELIVERY §6 composes it. |
| F2 stale C figure | **RESOLVED** | DESIGN §2 item 1 cites C REPAIR 1 `57f6dd30`: 5,728 / 268,936, rebuild 292 / 8,298. The B session-record line "the `E_C` cost now cites C's FREEZE" is stale against REPAIR 2. NOTE. |
| F3 ceiling | **RESOLVED** | DESIGN §1 ground 2, §14 balance bullet, §17. Cost is now a supporting constraint against named comparators, and the GPU pool is mentioned. |
| F5 §7 wording | **PARTIAL** | DESIGN §7 and §16 now say "fails as specified" and name the variants. **New finding N1 below**: the "truth-free" variant B says is "not ruled out" fails by construction with N1's both-stream inner bootstrap. |
| F6 assumptions / reserve | **RESOLVED** | DESIGN §14 lists C's four differences. §16.1 adds 9.8–12.2 node-h with reserve (`assurance.json` `n2_total_with_r0_and_reserve_node_h_range`). |
| F7 sensitivity label | **RESOLVED** | DESIGN §10 now uses exact reciprocals: 1,632 / 1,030, and 504 / 322 at 4/3. |
| F8 C wording | **RESOLVED** | ASSESSMENT-total line 43: "were produced by LightGBM, not by `E_C`". It still cites unsplit `P09` at lines 43, 52, 138, 365 and 412 (NOTE N4). |
| F9 C `E_C` branch | **RESOLVED** in `costs.py`. **Not carried to `P05`** (NOTE/MINOR N2). | C's branch now drops S-a and applies the 2.24 universe ratio, but A's `P05` price (128 node-h) still prices exact universes at the CV rate. |
| F10 P09 label | **RESOLVED** | `pairings.tsv` rows `P09a` (DISPROVED) and `P09b` (UNRESOLVED); ASSESSMENT-pairing §3 and §7 give a tally of 10/4/4 over 18 rows. |
| F11 Flux rescale | **RESOLVED** | `verification.md` §8 marks it "closed by external verification". §6 of the assessment no longer lists it. |
| F12 import-time hashing | **RESOLVED** | See §2 below. |
| F13 D citation | **RESOLVED** | `2D_OMNIFOLD_REFERENCE.md` (Import constraint paragraph) and README cite `AUTHORIZATION…:41` for the insert and the driver sha. They cite `test_oi136_rooted_insert_ratchet.py:266-274` (`OMNIFOLD_SHA256`, verified at those lines) and PLAN:18 for the helper digest, and add the red-at-pin caveat. |
| F4 OI-136 | routed, **open** | KI 89; DELIVERY §5. `work-items.tsv:102` confirms OI-136 is `active` / `unassigned`. Ratchet failure lists are byte-identical to the initial review. |

## 2. A's behavior commit `355174fe`

- **Code.**
  - The driver is hashed at the top of `main()`.
  - `run_provenance` is called right after `from omnifold import …`.
  - The records are written unchanged at the end.
- **KI-84 suite** (read first; it stubs the classifier and runs the driver as a subprocess on a
  synthetic input). **15/15 OK, no skips**, exit 0 (`ki84_test_cycle1.txt`). This includes the
  pre-fix bit-identity class `PathsTheFixMustNotChange`, so histogram outputs are unchanged.
- **Insert stays inside `main()`.** `test_the_2D_driver_still_confines_its_insert_to_a_function`
  and `test_the_omnifold_helper_has_not_moved` pass (`oi136_cycle1.txt`).
- **Hash bindings.** `verify_hash_bindings.py --root .` exits 0 with `ALL BINDINGS INTACT`. The
  driver's two pins remain `known pre-existing drift` (`vhb_cycle1.txt`).
- **Mutation tests** (run in scratch, class `RunProvenanceIsRecorded`):
  - M1, helper hashed at write time (provenance call moved to the write loop): `test_digests_are_of_the_bytes_loaded_not_of_later_edits` **FAILS**.
  - M3, driver hashed at write time (`driverSha256` recomputed in the write loop): the same test **FAILS** (`410a577b…` ≠ `b3132ec2…`).
  - Unmutated control: OK.
  - So the test catches write-time hashing of either file. It cannot tell "hashed at `main()` start" from "hashed at helper import" (both precede the mid-run edit). NOTE only.
- **Edge case, NOTE.** If a caller has already imported `omnifold` before `main()` runs, the helper
  digest is of the current file, not the bytes loaded earlier.

## 3. Recomputed numbers that moved (own code)

| quantity | owner | mine | script |
|---|---|---|---|
| C `E_C` branch P2 admitted, optimistic / conservative | 5,728 / 268,936 | 5,728.5 / 268,936.4 (setup 554.2 / 27,281.3; production 3,450 / 145,089.6) | `recompute/rc_c_exact.py` (`8a889c1f…`) |
| one-time exact rebuild 187·c·2.2388 + 11·c | 292 / 8,298 | 292.17 / 8,297.51 | same |
| N2 with R0 and 20 % reserve | 9.8–12.2 | (7.4296 + 0.4)/0.8 = 9.787; (7.4296 + 2.3)/0.8 = 12.162 | `recompute/rc_sens.py` (`ed1ab0ff…`) |
| sensitivity at exact [1/x, x], I68+I95 / I68 only | 1,632/1,248; 1,030/755; 719/519; 504/322 (4/3); 329/172 | identical; and 504/330 at x = 1.33, confirming the 330 → 322 change comes only from 4/3 vs 1.33 | same (reuses my `rc_assurance.py` functions) |

## 4. E's integration surfaces

I checked the following against their sources, and they are correct:

- **Paper disclosure.** DELIVERY §6 says the article discloses the different implementation:
  `paper_body.tex:125-129` says the ensembles "use a different implementation from the
  two-dimensional central-value estimator". No transfer statement or size appears in the article.
- **STATUS corrections.**
  - Headline relabelled correctly.
  - Lateral list corrected to 5: BeamAngleX/Y, MuonResolution, Muon_Energy_MINERvA/MINOS. This
    matches `MINERvA101/…/runEventLoopOmniFold.cpp:238-244`, where GEANT is vertical/weight-only.
  - PPFX "verified" is qualified and routed to KI 91.
- **RUN_LOG.** "Seven new tests" is correct (6 in `971fc00c` + 1 in `355174fe`). It records zero compute.
- **KNOWN_ISSUES 88–91.** Numbers, pairing ids, owners and the `work-items.tsv` status all agree
  with the sources and with my recomputation.
- **CATALOG.** Routes to DELIVERY first. Lane labels are correct: A FAIL, B NO-GO, C NO-GO, D PASS.
- **PROPOSAL §0.**
  - s5p measurement branch "not admitted": correct (`DELIVERY-20261006-s5p…:22`).
  - 1,902 node-h and 1.48 million figures: present in the October 5 text (line 413).
  - Stage-B pilot "not released": correct.
  - N = 2400 kept "only as a sensitivity row": correct.
- **DELIVERY body.**
  - §1, §3 and §4 numbers all match my recomputation.
  - The preserved review body is byte-identical to my scratch `review.md` below E's header; the header
    digest `7b71fb61…` (29,847 B) is correct. The preserved scripts and JSON are byte-identical.
- **Terminal labels (§1, §7).** These are neither overstated nor understated:
  - INFEASIBLE UNDER STATED CONSTRAINTS for the named primary, on populations, with cost labelled
    supporting.
  - Total NO-GO.
  - N2 NOT READY, for its four named items.
  - Nothing ready for a claim about the quoted central.
- **Composed next decision (§6).** It is correct and is the smallest one: it needs 0 node-h, and every
  other step depends on it.
- **Choice labels.** The three choices are named in words and mapped to A §7's (a)/(b)/(c), which
  is consistent with A §7.

### New findings

- **N1 — MINOR. B's "truth-free variant" of N1 is not open; it fails by construction as specified.**
  - Where: DESIGN §7 ("Two variants are not ruled out…"), §16 N1 row and §17; repeated in DELIVERY
    §9 item 2 ("named and unpriced, not ruled out").
  - Why: N1 fixes the bank `S` but keeps a both-stream inner bootstrap (§16 now says so explicitly).
    The outer scatter therefore lacks the MC-stream term that σ̂ contains. An exactly calibrated
    bootstrap then gives κ ≈ √(data-stream share).
  - Size: at the 48 % bank the MC variance scales by about 4.708/2.26 = 2.08. The data share falls to
    about 0.52/(0.52 + 0.48 × 2.08) ≈ 0.34, so κ ≈ 0.59, below the 0.80 tolerance edge. This holds for
    both the truth-free sd(U_e − Ū)/σ̂ test and N1's own coverage test (over-coverage). It is
    independent of the finite reference.
  - Repair (B): add this as a second reason that N1 fails as specified. State that a truth-free or
    conditional variant needs a data-only inner stream (as N2 has), which makes it a different
    procedure. DELIVERY §9.2 should follow.
  - Not material: it affects neither a verdict nor the next decision.
- **N2 — MINOR. The "measure the transfer" price in DELIVERY §6 and C §8 stage 0 still carries the
  F9 defect through A's `P05`.**
  - "About 170–350 node-h for all three" uses A's `P05` = 188 × 0.68 = 128 node-h. That prices exact
    universes at the CV rate.
  - C's own repaired convention prices the same exact sweep at 187 × 0.68 × 2.2388 + 0.68 = 285 node-h.
  - With that convention the range becomes about **330–510** node-h (P03 34–215, P05 285, P09b 7).
    The P03-only figure (34–39) is unaffected.
  - Repair: A updates the `P05` price (or C/E quote both conventions), and DELIVERY §6 quotes the
    range with its convention stated.
  - Not material: this is a non-recommended option, and the row already says it "needs a design and
    its own authorization".
- **N3 — MINOR. PROPOSAL §0 overstates what my review covered.** It says the reconciliation "was
  reviewed separately, in the preparation's own review (`state/…/e/review.md`)". That file is the
  initial review at `cd0da202`, which predates §0. Repair (E): cite this focused review
  (`review-cycle1.md`) once it is preserved.
- **N4 — NOTE. Stale `P09` labels.**
  - DELIVERY §6 "measure the transfer" row says `P09`; it should be `P09b`.
  - C ASSESSMENT-total still cites `P09` at lines 43, 52, 138, 365 and 412 (should be `P09a` / `P09b`).
  - STATUS says "`P01`–`P09`".
  - Repair: relabel.
- **N5 — NOTE. Rationale stated as fact.** DELIVERY §6 says "any of the three needs it settled before
  the package is submitted". That is E's judgement, not evidence. The "keep and disclose" wording
  change belongs to the publication owner, with Joseph, under the three-build rule, as §6 already
  says. Repair (E): mark it as E's recommendation rationale.

## Verdict for this cycle

- F1–F3 are resolved, F5 is partial, and F6–F13 are resolved.
- F4 is correctly routed and remains open. It does not block the 0-node-h §6 decision. It does block
  admitting N2, and §1 and §5 already say so.
- I found **no new material findings**. N1–N3 are MINOR, N4–N5 are NOTEs, and each has a concrete repair.
- The integrated terminal is supported by the evidence:
  - primary **INFEASIBLE UNDER STATED CONSTRAINTS** (populations);
  - total NO-GO;
  - N2 **NOT READY**.
- The smallest next decision for Joseph is the 0-node-h pairing/scope choice.

## Resources (this cycle)

- About 0.3 h of working time across the two sessions (07:48–07:53Z and 09:51–09:53Z), plus reading time.
- Under 0.05 local core-h. Peak RAM under 0.3 GiB.
- No bytes copied. Scratch mutants deleted.
- 0 node-h; no remote commands.

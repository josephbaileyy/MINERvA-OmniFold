# Stage B focused re-review (cycle 1 of 2): commit `2b3774f7`, repair of the `45fd98f7` review

**Reviewer:** the same read-only session that reviewed `45fd98f7` (Claude Opus 5.5). **Date:** 2026-10-12. **Worktree:** a new detached worktree at `2b3774f7`. I ran no Slurm job. The only local repository reads outside the worktree were refs, for the PR #95 line check. **Scope:** only the four checks the coordinator listed.

## Verdict: **PASS WITH CHANGES**

The repair batch fixes M1, M2, M3, M5, M6 and M7 and all of N2–N13. The new pricing is correct, and every figure checks.

Three small text defects remain:
- R1: the M4 standalone-verdict defect survives in two places.
- R2: one N1 citation is still wrong.
- R3: the new C07′ row creates an unassigned source that the exit statement and the open-item lists do not mention.

None of these is MATERIAL. All three are one-line edits and need no new measurement.

## (1) Resolution of M1–M7 and N1–N14

| finding | status at `2b3774f7` |
|---|---|
| M1 | **Resolved.** §1 table and "Why CONDITIONAL", §2.10 "Consequence if confirmed" and the §7 G1 contingency now state the central-value bias and Joseph's re-adoption. The event-loop part of the repair is marked unpriced. |
| M2 | **Resolved**, with a NOTE (N-a below). |
| M3 | **Resolved.** KNOWN_ISSUES row 95 names the July sweep under R1 and the May sweep for the diagnostic, and adds the July effect (5.158% → 3.747%). Row 96 names the active-mode outputs under R4. §2.2 agrees. |
| M4 | **Partly resolved: see R1.** The §2.5 heading and body, §1 "Why CONDITIONAL", the KI 93 note and the CATALOG row now say "provisional". The uncommitted-producer finding is recorded correctly: the products predate `cf8a4a67` but are background-aware. P2 now carries a frozen envelope, and a July rebuild is priced. |
| M5 | **Resolved.** The KI 92 row and §2.4 now say "`C_U`+normalization median", add the quoted-total figures 6.8707% → 6.8674%, and carry DIAGNOSTIC, NOT QUOTABLE. |
| M6 | **Resolved.** The reserve is now ≥ 20% of the admitted total (subtotal / 0.8), citing `costs.py`. |
| M7 | **Resolved.** The sequencing deviation is stated for the director with two options. The P2 price without the selective-I/O port is given. R0 states its dependence on PR #95, which `gh` confirms is the open selective-I/O integration PR with head `closeout/stage-a-selective-io-20261012`. |
| N1 | **Partly resolved: see R2.** `:1203-1212` is fixed in §2.8 and §2.10. `:1175` is added in §2.7. The STATUS correction now names the comment as "line 27 before the selective-I/O merge, line 30 after". I verified line 27 at `2b3774f7` and line 30 on the selective-I/O branches (`3cc5fb71`, `798f8340`, `9dfd8d6e`). |
| N2 | **Resolved.** u_E now reads "billing 10", with the long-job median 0.076 and max 0.192. |
| N3 | **Resolved.** The KI 94 note cites the 2026-10-06 record (pairing assessment `:86-87`; `purity_datastream_check.json`) and calls only the size new. |
| N4 | **Resolved.** R7 now states the random-effects reasoning and the 4 degrees of freedom. |
| N5 | **Resolved.** §2.2 "Decision for Joseph"; R2 points to it. |
| N6 | **Resolved.** §8 says the joint law passes by adopting MAT's in-band convention. |
| N7 | **Resolved.** The `2D_VALIDATION_FOR_3D.md` correction now carries "(DIAGNOSTIC, NOT QUOTABLE)". |
| N8 | **Resolved in form**: C07′ row added and C09 names the iteration count. The new row creates R3. |
| N9 | **Resolved.** §2.11 bullet added. |
| N10 | **Resolved.** R0 now has an "Authority principle" bullet. |
| N11 | **Resolved.** §9 bullet added. |
| N12 | **Resolved.** P1 now declares itself a mechanism and timing check, gives the ≈16% unpaired error, says the paired design is needed, and lists its declared checks with no pass/fail. |
| N13 | **Resolved.** The merged-file identity is in §2.1, the July truth-null identity in §2.5 and the G2 confirmation in §2.11. Each is attributed to the reviewer. |
| N14 | No change needed. Correct. |

**Status-document corrections:** both are correct as amended. One is `2D_OMNIFOLD_STUDY_STATUS.md` (the PRD citation, now with line 27/30). The other is `2D_VALIDATION_FOR_3D.md` (now with the NOT QUOTABLE label).

## (2) New defects or overclaims

### Findings (MINOR)

**R1. The M4 residue: "passes" and "qualified" still stand alone in two places.**
- **Where:**
  - REPORT.md:50, the §1 findings table: "July `purity_newomni` sweep **passes** the KI-93 bar".
  - REPORT.md:349, §6: "July qualified".
  - `CATALOG.md`, the Stage B row, still begins "July sweep qualified, May retired" before it adds "July qualification provisional".
- Line 152 in the §2.5 body is acceptable because its heading qualifies it.
- **Failure scenario:** the §1 table is the record's verdict summary. A reader who quotes that cell carries an unqualified "passes" for a sweep that ran on an uncommitted driver.
- **Fix:** add "provisionally (pending P2; producer uncommitted)" to line 50 and line 349, and drop "qualified" from the start of the CATALOG row.

**R2. N1 residue: `:26` is still cited in R0.**
- **Where:** REPORT.md:302 reads "The PRD 104/106 comment at `unfold_2d_omnifold_unbinned.py:26` …". The parenthetical added in the same sentence says line 27 before the merge and line 30 after, so the sentence contradicts itself.
- **Fix:** replace `:26` with the parenthetical form already used in the STATUS correction.

**R3. The new C07′ row is an unassigned source that the exit statement does not carry.**
- **Where:** REPORT.md:290 says "**not assigned a separate band** … Flagged for Joseph" with status "OPEN QUESTION". That status is outside the table's declared vocabulary (ELIGIBLE / REPAIR / MISSING, §3 preamble).
- §1 (REPORT.md:38) still says "Every C01–C10 / X01–X03 source is assigned". That is literally true, because C07′ is outside that numbering. But the plan's exit test is "no unassigned or omitted material source".
- C07′ appears neither in §5 (missing inputs and routes) nor in R10 (open items before production).
- **Failure scenario:** Joseph reads §1, R10 or the CATALOG row, concludes every source is assigned, and admits the recipe. The POT question then lives only in one table row and is never decided.
- **Fix:**
  - Name C07′ in §1's exit sentence and in R10 as a materiality decision for Joseph.
  - Add a §5 row: route "collaboration/convention question", cost none.
  - Either add OPEN QUESTION to the vocabulary or use MISSING.
  - Scope the claim "the paper's normalization text names only the 1.4% target count" to its actual source. That source is the analysis note's paraphrase of Ruterbories §V (`docs/analysis-note/app_statmethods.tex:330-338`). The paper itself was not read, and absence from a paraphrase is weak evidence.

### NOTE

- **N-a. The §8 G1 argument is acceptable, but one clause is circular.** The decisive ground is sound: the existence and size of G1 are unknown, the route is priced, and a confirmed G1 returns as a Stop-or-repair decision. But "the plan's Stop rule asks for exactly that record" (REPORT.md:426) misreads the plan. Recording the missing input and its route is what the plan requires **when** a Stop applies; it is not a reason the Stop does not apply. Suggest deleting that clause.
- **N-b. Two figures are rounded inconsistently.** The pilot's admitted total is 11.8 / 0.8 = 14.75, printed as 14.7, and the reserve is 2.95, printed as 2.9. Production rounds the same kind of value up (81.75 → 81.8). The 15.0 ceiling still holds a 21.3% reserve at the high end, so nothing fails.

### New pricing: checked and correct
- Pilot: subtotal 7.42–11.73; admitted total 9.25–14.75; ceiling 15.0, so the reserve is ≥ 21.3% of the ceiling at the high end.
- Production: 39.8 / 0.8 = 49.75 and 65.4 / 0.8 = 81.75, i.e. 49.8–81.8.
- Splitting P4–P5 out: 0.9 + (0.7–1.5) = 1.6–2.4 before reserve.
- P2 without the port: 5 × u_U = 3.3–3.8.
- Contingencies:
  - 187 × (0.247…0.761) = 46.1–142.2, printed as "47–142" using u_sel ≈ 0.25. Acceptable.
  - The G2 repair: 170 × (0.25…0.76) = 42.5–129.
- The G1 contingency honestly marks the event-loop part unpriced.
- The closing claim "well inside" the 700 node-h ceiling still holds for the construction. The worst case of all priced contingencies is about 81.8 + 142 + 142 + 129 ≈ 495 node-h plus the unpriced event loops.

**Provisional-July wording** in §2.5, §1 "Why CONDITIONAL" and KI 93 is accurate and properly scoped. The residue is in R1.

## (3) `review/review-45fd98f7.md`
- 131 lines, 16,311 bytes, sha256 `bc961d7c4000f4228c6be55d4605b7b4fab28dc6b4300a2c1c05849b6c051849`.
- I compared it section by section and line by line with the text I delivered. It is **identical in content**: verdict, M1–M7, N1–N14, the numbers table, citations, hygiene, scratch paths and worktree status, with no edits or omissions.
- My delivered message was not saved as a file, so I cannot compare hashes. Byte identity is therefore attested by full-text comparison, not by a hash.
- It is tracked and has a MANIFEST row (`MANIFEST.tsv:782`, MACHINE).

## (4) Hygiene at `2b3774f7`
- `generate_manifest.py --check --at-sha 2b3774f7`: **OK, exit 0** (rows 2384; `unused_overrides=1`, already present at `46c410ae`).
- `verify_hash_bindings.py --root .`: **ALL BINDINGS INTACT, exit 0**.
- `verify_receipt_artifacts.py --rev 2b3774f7`: **exit 0**. 537 receipts, 14 artifacts, 0 missing. 66 UNRESOLVED, the unchanged pinned inventory (`49916d283274`).

## Worktree status
- `/private/tmp/claude-501/review-b2-2b3774f7` (detached `2b3774f7`): `git status --short` empty at start and at end. **Removed.**
- Main checkout: unchanged from session start (19 status lines: the same 3 modified orchestration files and the same untracked files).
- Nothing was edited, committed or pushed. Scratch outputs `m2.out`, `h2.out` and `r2.out` are in `/private/tmp/claude-501/review-b-scratch/`.
# Closeout-delta review: `901f0088..3a9c84b8` (plus E's post-review wording, `ee61fb22..901f0088`)

Reviewer: a fresh read-only reviewer. All numbers below come from my own scripts in this scratch
directory (`kappa.py`, `cov.py`, `bankoffset.py`, `tally.py`, `ident.py`). I did not run anything
under `closeout/checks/`. The only repository tool I ran was `generate_manifest.py --at-sha 3a9c84b8
--check`, which never writes.

## Status

| when (UTC) | `git status --porcelain` | HEAD |
|---|---|---|
| start 2026-10-09T18:52:49Z | empty (0 lines) | `3a9c84b84af9aca1fe4cf70c2005b9a234dcffef` |
| end 2026-10-09T19:00:29Z | empty (0 lines) | `3a9c84b84af9aca1fe4cf70c2005b9a234dcffef` |

`origin/prep/next-closeout-20261009` = `3a9c84b8`, from the local ref. Nothing was fetched.

## Rubric

| # | verdict | evidence |
|---|---|---|
| 1 Scope | **PASS** | The `--name-status` list for `901f0088..3a9c84b8` contains only the four authorized lane/E documents, CATALOG, overrides, MANIFEST and `Q/` files. No `a/`, `e/` or receipt file changed, and nothing under `docs/analysis-note/`, `docs/publication/` or `publication/` changed. The MANIFEST diff is only `inbound_count`/new rows; `generate_manifest.py --at-sha 3a9c84b8 --check` gives OK, exit 0, with 5 unused overrides (the 5 report paths not yet pushed). B NO-GO, C NO-GO/stage-0 stop, A FAIL and N2 NOT READY are unchanged. |
| 2 Item 1 (B N1) | **numbers PASS; argument partly FAIL (F1)** | Recomputed f_data = (0.486962/0.673815)² = **0.52229**, MC/data = **4.70799**. N1's bank is half the MC (DESIGN §14 row "N1, half-MC bank"; §5 "MC/data 2.35"). At the half bank: inflation 2.000, data share 0.35344, **κ = 0.5945**. At N2's 48 % bank (§16.1, MC/data 2.26): inflation 2.0833, share 0.34417, **κ = 0.5867**. κ would reach 0.80 only at f_data ≥ 0.78. The κ ≈ √(data share) argument for the outer **scatter** is right, and it does dispose of the truth-free width test with a both-stream σ̂. The statement "truth-free + data-only inner stream gives an N2-type diagnostic" is right, because sd(U_e − Ū) cancels the fixed-bank offset. Neither N2 nor any variant is called coverage validation. **However**, "fails N1's coverage test, as over-coverage" is wrong, and the reference-aware form is not rescued by a data-only stream (F1). |
| 3 Item 2 (P09) | **PASS** | `pairings.tsv` at `f762749d`: 17 rows, DISPROVED P02/P04/P09/P17, UNRESOLVED P03/P05/P07, so 4/3. At `cc9eed27`, `901f0088` and `3a9c84b8`: 18 rows, DISPROVED P02/P04/P09a/P17, UNRESOLVED P03/P05/P07/P09b, so 4/4. At `901f0088`, C had six unsplit `P09`s on lines 43, 52, 138, 365 and 412 (twice). Each now carries the right label: 43 → P09a (produced by LightGBM, matches P09a "same estimator?" DISPROVED); 44, 52, 138 and 412 → P09b (transfer); 365 → P09b (seed scan, P09b's price_for_C). The only bare `P09` left in A, C, DELIVERY, STATUS or DESIGN is in historical "former P09 … split" sentences. |
| 4 Item 3 (P05) | **PASS** | 188 × 0.68 = **127.84**. Ratio = 0.5 h / (804 s/3600) = **2.23881**, from STATUS:345 (lgbm 128 CPU, 13m24s) and the archive at `evidence/prepublication-2026-08-20-0b329e8a:…RUN_LOG_ARCHIVE.md:2995` ("Per-task wall ~30 min on a full Milan node", sweep 53441839). C's convention gives 187 × 0.68 × 2.23881 + 0.68 = **285.37**. Totals with P03 34–215 and P09b 6.8: **168.64–349.64** and **326.17–507.17**, which reproduce 170–350 / 330–510. A §5 item 2, C list (~line 365) and C stage-0 say "forecast, not a timing" / "Neither figure is measured". Both figures are kept, and no single price is manufactured. |
| 5 Item 4 (DELIVERY) | **PASS** | My blob comparison (`ident.py`) at `901f0088`: the lane-touched files (non-merge `f8e2bf85..tip`) are A 32, B 7, C 4 and D 11, and **0 differ** from their tips. Upstream `ad2716d8..460631d1`: 87 files, both as a net diff and as a per-commit union; only `MANIFEST.tsv` differs. Positive control at `ee61fb22`: 23 differ (22 audit files + MANIFEST). At `3a9c84b8`, exactly the A, B and C documents differ from their tips, and D does not. `901f0088` parents are `287f25f5` and `460631d1`. `460631d1` = "Merge pull request #59", and outside the 22 audit files it changes only MANIFEST. `287f25f5` parent is `ee61fb22`. E's wording against `review-cycle1.md`: §7 "cycle 2 was not needed" did overstate (N1–N5 needed repairs and E's own repairs were never re-reviewed), so "not used" is right. E's §9.2 "Its reference-aware variant is unpriced" did leave it open, so the owner is right to correct it (but see F1). §6 P09b label, both price conventions, N5 judgement marker, proposal §0 citation (cycle-1 §4 did check §0), STATUS `P01`–`P09b`, and §11 times (12 + 42 + 15 = 69 min; reviewer 0.4 h per `review.md` §7 and 0.3 h per cycle-1 resources) are all consistent. Preserved bodies: `review.md` from line 15 is 29,847 B, `7b71fb61…`; `review-cycle1.md` from line 10 is 11,688 B, `adbd2c12…`. Both match their headers. |
| 6 Item 5 (wording) | **PASS with MINOR (F2) and NOTE (F4)** | It states both the distinct estimators ((1) "computed for a different estimator … has not been measured"; (2) "rather than the exact-split estimator") and the unmeasured transfer. Two origins check out: A `verification.md:100` (0.97 / 2.67 / 12.50 %; 1.30 / 2.76 / 8.32; 126/62) and `check_a_output.txt:58,72` (0.96596, 1.29952); the reviewer's `rc_pairing.json.txt` "seed1 vs exact" (0.96596, 1.29952, p84 2.758, max 8.3227) and `:135` 6.826880; P14 "6.8269% with x = E_C". `paper_body.tex` has the same blob `938fdb0e` at `901f0088` and `460631d1`. Lines 126–129 are the uncertainty-ensemble item, 114–137 the list, and 180–181 the "…for the publication." sentence; `sec:method` (104) and `sec:validation` (141) exist. `sec_method.tex:98` "single-run unfold with pinned seeds" is contradicted by P01 (`random_state=None`; "seed unpinned"). `sec_method.tex:91` "not estimator-matched", `sec_results.tex:137`, `sec_systematics.tex:44` and `primer_body.tex:151` (`\uqMedian` = 6.87) are as stated. The report chooses no option and claims no readiness. |
| 7 Dispatch | **PASS** | The DISPATCH writer table matches the GOALS writer map and each goal's owned-output paragraph. The laptop concurrency rule matches GOALS. `460631d1..901f0088` = 41, reverse = 0, as stated. `worktree list`: `preserve/anatuple-data-cfs-20261009` (5a6fef41, clean, 1 commit not in `901f0088`) touches `docs/orchestration` (MANIFEST), `docs/publication/corrections-20261008/` and `publication/release/preservation/…`, as stated. Every publication worktree head (`ea939701`, `e778575b`, `49990f82`, `c1c7dc62`, `a3af2af3`, `f6dc46e6`) and every uncprep head is contained in `901f0088`. No `prep/next-*` ref exists other than the closeout branch. GOALS copy sha256 = `81496789…54380a`, which matches. |

## Findings

**F1 — MATERIAL (verdict unchanged). The new N1 text misdescribes the second failure, and says a
data-only stream rescues the reference-aware variant.**

- **Location.**
  - DESIGN §7, bullets 4–6 ("It fails N1's coverage test, as over-coverage"; "Either one needs a
    data-only inner stream … so that σ̂ and the outer scatter measure the same term"; "The
    reference-aware form would also become a data-stream-only conditional test").
  - DESIGN §17 ("A variant needs a data-only inner stream, which makes it a data-stream diagnostic of
    N2's kind").
  - DELIVERY §8 N1 bullet ("Either variant needs a data-only inner stream, which makes it a
    data-stream diagnostic").
  - DELIVERY §9.2 ("either one becomes a data-stream-only diagnostic of N2's kind").
  - REPORT §3.1 ("an exactly calibrated bootstrap over-covers").
- **Why.**
  - The premise "the both-stream bootstrap is exactly calibrated" means its MC-stream term equals the
    bank-to-bank variance. With the bank `S` fixed, that variance appears in `U_e − T_R` as a
    per-functional offset δ_j. This is the bank's MC realization, and it is common to every outer
    experiment. Its rms is √(1 − share) σ̂ = **0.80 σ̂**.
  - Under the text's own premises (share 0.3534, N = 719, the §9 rules), my `cov.py` and
    `bankoffset.py` give these results with the both-stream inner bootstrap:
    - I68 coverage is 0.907 only at δ = 0;
    - **63 % of functionals over-cover and 37 % under-cover**;
    - pooled coverage is exactly nominal (0.6827);
    - so the §9 verdict would be FAIL-mixed, not over-coverage;
    - the bias test fails in about **188 of 206** functionals from δ alone, whatever the reference.
  - With a data-only inner stream:
    - the offset is 1.35 σ̂;
    - mean I68 coverage of `T_R` is **0.448**;
    - the bias test again fails in about 188 of 206.
  - So a data-only stream rescues only the truth-free width form, where Ū cancels δ. Any form scored
    against `T_R` (the reference-aware variant) still fails, unless its reference model also carries
    the fixed bank's MC offset, which one bank cannot measure.
  - The text therefore understates the limit on the reference-aware variant, and it states a wrong
    failure mode.
  - The N1 "fails as specified" verdict, the NO-GO, N2's scope and the next decision are unaffected.
- **Repair.**
  - Replace "as over-coverage" with: "per-functional coverage is mixed (about 63 % over, 37 % under at
    I68, pooled nominal), and the fixed bank's MC realization is a per-functional offset of about
    0.8 σ̂ that fails the bias test in about 188 of 206 functionals, whatever the reference".
  - State that a data-only inner stream turns only the truth-free form into an N2-type width
    diagnostic. A reference-aware coverage form stays not open, because `U_e − T_R` keeps the bank
    offset that no data-only σ̂ carries.
  - Carry the same wording to DESIGN §17, DELIVERY §8 and §9.2, and REPORT §3.1 and §6.

**F2 — MINOR. The proposed sentence can be read as 0.97 % = 1.3 σ_stat, and it does not say which
LightGBM central.**

- **Location.** REPORT §4 (2): "differ by a median of 0.97 % per bin, 1.3 times the statistical
  uncertainty".
- **Why.**
  - These are two separate per-bin medians. The ratio of the medians is 0.97/0.674 ≈ 1.44, not 1.3.
  - "The two central values" names one LightGBM central, but the blocks have several: seed 1 for the
    bootstrap (0.97 %, 1.30); CV42 for the universes, `P04` (0.98 %, 1.32).
- **Repair.** Write "differ by a median of 0.97 % per bin and, per bin, by a median of 1.3 times the
  statistical uncertainty (LightGBM seed 1 against the exact-split central)". Optionally note
  0.98 % / 1.32 for the CV42 central of the universes.

**F3 — NOTE. C's line 40 still says "Pairing ids below are A's FREEZE numbering".** `P09a` and `P09b`
are REPAIR 1 (`cc9eed27`) ids. Repair: "A's FREEZE numbering, with `P09` split as in REPAIR 1".

**F4 — NOTE. REPORT §4 table: "integrated ratio 0.9999 … `check_a_output.txt:134`" cites the
wrong comparison.** Line 134 is CV42 vs exact (0.999906). The seed-1 vs exact ratio is at `:80`
(0.999899). Both round to 0.9999, and neither is used in the wording. Repair: cite `:80`.

**F5 — NOTE. Lists omit `MANIFEST.tsv`.** REPORT §2 (the files `287f25f5` edits) and DELIVERY §2's
`287f25f5` row leave out `MANIFEST.tsv`, which `287f25f5` also changes. DELIVERY §8 says "five
unsplit `P09` labels", but there were six occurrences on five lines. These are cosmetic.

**F6 — NOTE. REPORT §§7–10 read "Pending".** That is expected at this fixed commit. The Disposition
must still be written after this review. Given F1, a PASS needs the F1 repair. Otherwise the record
should carry F1 as an open material finding.

## What I could not verify

- Whether sweep 53441839 ran the LightGBM backend. The archive does not say so in the lines I read.
  The ratio's "LightGBM" label rests on the owner's and C's reading.
- I did not re-run the hooks, `verify_hash_bindings.py`, the link checks or the OI-136 ratchets. I
  relied on the owner's logs for those. I did run the manifest check.
- E's own core-hours.
- The DISPATCH "eleven untracked root files". I did not count them.
- Whether the remote matches beyond my local `origin/*` refs (no fetch).
- Commit dates in DISPATCH, beyond the commit metadata.

## Resources

- Elapsed time: about 8 minutes of tool time (18:52:49–19:00:29Z), plus writing.
- CPU: well under 0.01 core-hours, single-threaded Python. Peak RAM under 0.1 GiB.
- Scratch: about 0.3 MB, including a 0.15 MB copy of the archived run log.
- No network, cluster, GPU or git writes.

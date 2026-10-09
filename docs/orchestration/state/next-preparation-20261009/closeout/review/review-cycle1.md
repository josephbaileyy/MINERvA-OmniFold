# Focused re-review (final): repair batch `3a9c84b8..e87d8df8` (`265efc2f`, `e87d8df8`)

**Summary:** F1 is resolved. F2–F5 are resolved. The batch adds two MINOR findings (R1, R2) and two
NOTEs. It edits nothing outside scope, and I found no material finding.

Same reviewer as the initial review, read-only. I used my own new code (`recheck.py`), which uses a
different method from cycle 0: a closed form, an exact root-find, and an explicit Monte Carlo over
719 experiments × 206 functionals. The only repository tool I ran was
`generate_manifest.py --at-sha e87d8df8 --check`, which never writes.

## Status

| when (UTC) | `git status --porcelain` | HEAD |
|---|---|---|
| start 2026-10-09T19:05:11Z | empty | `e87d8df81b95d650c6505145452805153b59b057` |
| end 2026-10-09T19:06:26Z, plus writing | empty | `e87d8df81b95d650c6505145452805153b59b057` |

## Scope items

| item | verdict | evidence |
|---|---|---|
| (a) F1 | **RESOLVED** | **Wrong statements are gone.** A grep at `e87d8df8` finds no "as over-coverage", "over-covers", "would also become", "either one becomes", "Either variant needs" or "neither variant is open" in DESIGN, DELIVERY or REPORT. |
| | | **The new text is in place.** DESIGN §7 has the bank-offset bullet and the statement that only the truth-free form survives, with a data-only stream. Also updated: the §16 N1 row ("reference-aware variant is not open"), §17 and §18, DELIVERY §8 (the N1 bullet) and §9.2, REPORT §3.1 and §6. The reference-aware form is now "not open with either inner stream", because `τ_ref` models the reservoir, not the bank. That is correct. |
| | | **No N2 upgrade.** The truth-free form remains "no MC stream, no coverage of truth, no total", unpriced. |
| | | **My recomputation** (f_data from the raw JSONs, share 0.353443) agrees: offset rms **0.80409** σ̂ for both streams and **1.35252** σ̂ for data-only; pooled I68 **0.682689** for both streams and **0.447829** for data-only; over-cover fraction **0.6256**, exact, by root-finding d\* = 0.7142; Monte Carlo 117–136 of 206. Bias-test fails: Monte Carlo 185–191 of 206, so "about 188" holds. These match `logs/arith.txt` `n1_bank_offset`. |
| (b) F2 | **RESOLVED** | REPORT §4 (2) now reads "The LightGBM and exact-split central values differ by a median of 0.97 % per bin, and by a per-bin median of 1.3 times the statistical uncertainty". The evidence row names seed 1 vs exact and adds CV42 vs exact, 0.98 % / 1.32. Those match `verification.md:100–102` and `P04`. |
| F3 | **RESOLVED** | C line 40: "with `P09` split into `P09a`/`P09b` by A's REPAIR 1". |
| F4 | **RESOLVED** | REPORT now cites `check_a_output.txt:80` (0.999899) and notes `:134` (CV42, 0.999906), as I measured. |
| F5 | **RESOLVED** | `MANIFEST.tsv` is added to REPORT §2 and to the DELIVERY §2 `287f25f5` row. DELIVERY §8 now reads "six … occurrences (on five lines)". |
| (c) scope | **PASS** | `--name-status`: DESIGN, DELIVERY, C ASSESSMENT, MANIFEST.tsv, REPORT, `checks/arith.py` and `logs/arith.txt`. Nothing under `a/` or `e/`, no receipt, no publication file. Manifest at `e87d8df8`: OK, exit 0. Verdicts are unchanged. |

## Findings

**R1 — MINOR. Two committed numbers rest on a computation that is not in the repository.**

- **Location:**
  - DESIGN §7 ("about 188 of 206 by the closeout review's computation");
  - REPORT §3.1 ("about 62 % over-cover in my simulation");
  - REPORT §6.
- **Why it matters:** `checks/arith.py` computes only the offset rms values and the two mean I68
  coverages. Neither the over-cover fraction nor the bias-test count is computed there. The
  "closeout review" is this reviewer's scratch report, which is not preserved in the tree. A reader
  cannot re-run either figure. Both figures are correct, by my re-derivation above.
- **Repair:**
  - Add both quantities to `arith.py` and its log. The over-cover fraction is
    2Φ(d\*/m) − 1, with cov(d\*) = 0.682689. The bias-test count is
    206 · 2(1 − Φ(4.0625 κ / (√719 · m))). The second is a closed form I give here; it equals 188.4.
  - Or preserve this review under `Q/closeout/`, as E did with `review-cycle1.md`, and cite it by path.

**R2 — MINOR. The REPORT still lacks its terminal sections.**

- **Location:** REPORT §§7–10 still say "Pending". §6's last bullet now reads "…was not re-derived
  here. It shows that N1's variants…", where "It" no longer has a clear referent.
- **Why it matters:** Goal 1 requires the review, resources, disposition and decision list.
- **Repair:**
  - Write §§7–10, recording F1–F5 as RESOLVED at `e87d8df8` and R1–R2 with their disposition.
  - Change "It shows" to "κ and the offset show".

**R3 — NOTE. "About 62 %" over-cover.** The exact value is 62.6 %, so "about 63 %" is the better
rounding. This is cosmetic.

**R4 — NOTE. The pooled-I68 statement assumes an exact reference.** DESIGN §7 says "pooled I68
coverage of `T_R` is nominal (0.68)". That holds with `T_R` treated as exact, since the first
reason's reservoir offset would add to it. A short "with an exact reference" qualifier would make
this explicit. It does not change any conclusion.

## Not verified

- I did not re-run hooks, hash bindings or link checks for the batch.
- Proposed-wording line 3 in REPORT §4 is now an over-long source line. That is cosmetic, and I did
  not check the rendering.

## Resources

- About 2 minutes of tool time (19:05–19:06Z), plus writing.
- Under 0.01 core-h, on one thread. RAM under 0.1 GiB.
- Scratch under 0.4 MB.
- No network, cluster, GPU or git writes.

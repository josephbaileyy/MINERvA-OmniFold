# s5p W2 recoil-response sensitivity: independent evaluator check (2026-10-06)

**CITABLE FOR:**
- this lane's independent check of the W2b evaluation: the reviewed evaluator and comparer on the three design
  copies (δ = 0 control, −4 %, +4 %);
- the control verdict, under the pre-registered criterion;
- the agreement with production's evaluate and decide outputs.

**NOT CITABLE FOR:**
- W2 as an uncertainty: Joseph approved it "solely as the labelled exploratory sensitivity, not as a validated
  uncertainty prescription" (`DECISION-20261006-joseph-publication-approvals.md` item 4, `827627d0`, read by this
  lane);
- any primary decision, which W2 does not change;
- the re-unfolding chain that produced the shifted products, which this lane did not recompute.

Requested by the publication lane ("pub"), whose packet §6 names this lane's evaluator as the independent check. The
work is read-only toward production and wrote only to this lane's scratch.

## 1. Inputs, checked by this lane

- **Digests:** all 12 files match pub's packet (rr1's labels match its manifest, `915c6f1b…`).
  - Designs: rrzero `92ae80c6…`, rr0 `c99ce6d8…`, rr1 `bbd116b3…`.
  - `data_central`: rrzero `ec5dc97d…`, rr0 `df11bfd8…`, rr1 `36313201…`.
  - Production's evaluate ran from deploy `e9372b75`.
- **Key-diff (this lane's own),** against the frozen design `404446eb…`: each copy differs in exactly one leaf,
  `data_central`. The null ensembles, V, the shifts, the seeds and the jitters are therefore the frozen ones.
- **Pre-registration of the control criterion.**
  - The fallback criterion first appears in `b958c0de` (2026-10-05T23:45:43Z; author date = committer date). That
    commit is an ancestor of the publication branch head, and the head still carries the same text.
  - It is implemented in `w2b.py cmd_decide` at `91401a0f`.
  - The δ = 0 product's mtime is 2026-10-06T13:54:45Z, after the criterion was committed (the product was also absent
    at 09:46Z).

## 2. Run (reviewed code `02df81e6`: recompute `81b879ae…`, comparer `bc924f31…`)

`evaluate --require-terminal --no-sequential` on each copy. The sequential look replay does not apply to shifted data,
and pub confirms production's evaluate makes the same choice. Then `compare` against that copy's `joint-evaluate.json`
and `robust-labels.json`, δ = 0 first, with a stop if that is not AGREE.

| copy | evaluate | compare |
|---|---|---|
| rrzero (δ = 0) | rc 0 | **AGREE, 1379/1379**, 0 discrepancies, 0 not located, 0 unresolved |
| rr0 (−4 %) | rc 0 | **AGREE, 1379/1379** |
| rr1 (+4 %) | rc 0 | **AGREE, 1379/1379** |

Outputs are in `state/s5p/recompute/w2-check/` (`recompute-<v>.json`, `compare-<v>.json`).

## 3. Control verdict (this lane's own, reached before reading production's decide output)

The δ = 0 product is **not** bitwise `fb5cc679…`, so the pre-registered fallback applies.
- Every δ = 0 claim p lies within the frozen `observed_jitter_p` range for its test. The ranges were taken from this
  lane's terminal record and cross-read from production's frozen `joint-evaluate.json`; they are identical.
- All ten Holm decisions equal the frozen ones.

**Control: PASS.**

## 4. ±4 % (exploratory)

- All ten tests are rejected at −4 % and at +4 %, so all ten are "rejected under both signs".
- The ruled κ = 3 labels are all "robust to the sub-fine residual" at both signs.
- The only claim that moves is NuWro shape: k 1 → 3 at +4 % (p 0.00114 → 0.00228), still rejected. Every other claim
  keeps k = 0.

## 5. Agreement with production's decide output

The decide outputs are `w2b-control.json` (`904dbf9b…`) and `w2b-decision.json` (`7618bc61…`).
- Per-sign decisions: 150 of 150 fields agree (decision, k, B, p and threshold; ten tests × three copies).
- Control: PASS, by the fallback branch, the same as this lane's.
- `robust_at_delta`: it agrees per test, with all ten robust.

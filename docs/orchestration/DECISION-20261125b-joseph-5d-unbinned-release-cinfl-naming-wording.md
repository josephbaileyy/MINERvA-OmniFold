# DECISION 2026-11-25 (b) — Joseph: the 5D fluctuation block's route and naming, the unbinned 5D release, the IBU bias and App. D wording, reviewer routes, and the 1B evidence tag

**Recorded by** the director. It adds to `DECISION-20261125-joseph-v1-scope-option-i-weights-hydrogen.md` (#1326).
Joseph gave every item below directly to the director, in the director's session, on 2026-11-25 (Pacific). Quoted
words are Joseph's.

## 1. The 5D fluctuation block: option C, with B as the fallback

Joseph, on the three options the director put to him (A: recompute the core readouts only; B: disclose the factors in
v1 and adopt in v2; C: recompute Phase 1 and Phase 2): "can we try C for now and if we are getting close and it seems
more impossible switch to B?" tier3-design runs C under `FD-VF-ADDITION-DECLARATION.md` (#1334). The checkpoint is
2026-11-28T00:00Z: if C cannot have readings with the note lane by 2026-11-29, v1 takes B instead. Before deciding,
Joseph asked: "can we check if the inputs exist first?" The check found every Phase 1 and Phase 2 input present and
equal to its pin (#1327).

## 2. Naming, table layout and two sentences for the inflated covariance

Joseph asked for a codex-school2 gpt-6.2-sol read on the table layout and on the names of the terms and variables.
Its prompt, answer and input hashes are in
`state/measurement-paper/5d-community-20261024/fd/receipts-vf/naming-read-20261125/`. Joseph: "yes to both and the
sentences too". Adopted:
- C_e is the "baseline statistical and systematic covariance". The inflated block is **C_e^infl** (V_F only as a
  records alias); ΔC_e = C_e^infl − C_e if printed; r̂_j is the estimated band ratio and φ_j the applied multiplier;
  the bands are "eigenvalue ranks 1–4, 5–8 and 9–16", not R1–R3. C_rep = C_e^infl + C_model + C_resp + C_PL,5D, and
  C_total stays the baseline subtotal C_e + C_model. C_b is the "candidate fake-data bias covariance", shown
  descriptively and stated as excluded.
- The per-cell σ table keeps the six source columns and C_e, and adds a C_e^infl column beside C_e, with no ΔC_e
  column. Headline uncertainties and correlations use C_rep.
- The read's two sentences describing the rescaling and its limits go into the note as proposed.

## 3. The unbinned 5D central value is released in v1

Joseph: "I think it is important to release the unbinned 5d central value as well because the true unfold is unbinned
and our headline is an unbinned measurement." The 5D per-event weights join the 2D weights (DECISION #1326 §1).
ibu-chi scopes the route and its price first; no code or compute runs before the director's ruling.

## 4. Wording approved

- **IBU bias** (App. C, beside the binned-IBU paragraph): "The IBU bias sentence looks good." The sentence is the
  director's draft from IBUB's readout (#1335), bound to that record.
- **App. D's unbinned-release sentence** (#1336): the first sentence as proposed; "can you take out 'These inputs let
  readers form central-value projections on their own grids?'" Removed.
- **The Fig. 14 caption, appC:7 and records_r03:18** (#1333): "yes you can these edits."

## 5. Reviewer routes

With agy's weekly quota exhausted until 2026-12-01 and Grok's balance exhausted, Joseph: "maybe you can try using
claude personal's sonnet 5.5 model. or codex-school's latest terra or luna model for review." Second readers may be
claude-personal `claude-sonnet-5-5` (read-only tools, in a copy directory) or codex-school `gpt-6.1-terra` /
`gpt-6-luna`. claude-school stays off review work.

## 6. The 1B branch's evidence tag

The director recommended preserving the 1B branch's commits cited by main with an annotated tag. Joseph pushed
`evidence/1b-staged-a2-1-20261103` (tag object 6b3769c9 → 342c0ce5). Deleting the branch is now safe, and remains
Joseph's call.

**CITABLE FOR:** what Joseph decided, and when. **NOT CITABLE FOR:** any number, any note wording beyond the quoted
approvals, or any claim about the results.

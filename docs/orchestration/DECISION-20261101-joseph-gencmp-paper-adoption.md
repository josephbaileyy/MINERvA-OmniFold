# DECISION 2026-11-01 (later) — Joseph: what the paper adopts from GENCMP

**Recorded by** the paper-tighten lane, as director.

**What led to it.**
- [`FD-GENCMP-REPORT.md`](state/measurement-paper/5d-community-20261024/FD-GENCMP-REPORT.md) (#648, main `0a13f052`)
  ran steps A–D under [`FD-GENCMP-BINDING.md`](state/measurement-paper/5d-community-20261024/FD-GENCMP-BINDING.md).
  Every control passed, at a cost of 0.158 node-h. Its §5 proposes the §7 wording. Ruling 4 holds every paper edit
  until Joseph rules.
- An independent Sonnet consult (not sol) reviewed §5 read-only. Its prompt and answer are verbatim in
  `FD-GENCMP-WORDING-CONSULT-PROMPT.txt` and `-ANSWER.txt` (#649, main `7ea0b9eb`).
- The questions were put to Joseph with both recommendations, through four rounds of questions.

## Joseph's answers, verbatim

1. Asked how Table IV should show NuWro and GiBUU, given NuWro's χ² of 130.7→128.4 (16 cells) and GiBUU's total
   χ² of 45.3→47.5 (8 cells). For GiBUU the shape-only χ² is 24.8→22.0, and the total would be 44.2 with GENIE's
   hydrogen in place of GiBUU's own.

   > CH rows, GiBUU labelled (Recommended)

   sha256 of the text plus a final newline begins `961764b0125c4f4e`.
2. Asked which of the other results go into the paper:

   > Analysis-definition rebuild, Native NuWro-on-CH clause, "For the 3d descriptive clause, is the qualification also recommended?"

   sha256 begins `98955cada597541d`.
3. On the quadrant wording, he asked:

   > is sonnet the prd reader?

   sha256 begins `a8475f529e830712`.
   - The director answered no.
   - Sonnet was a fresh session standing in for a referee. It was not the P1 register rater (sol), which consults
     avoid, and not a PRD referee.
   - The 3D qualification is required, not optional. With no 3D covariance adopted, ruling 3 makes any 3D clause read
     "not a test either way".
4. Asked where the 3D clause goes:

   > Note only (Recommended)

   sha256 begins `62827e30681e7110`.
5. On the quadrant comparison:

   > can you explain this choice more, I need more context

   sha256 begins `97017f8d9a48eaba`.
   - The director explained four things.
   - The 16-cell sums per (pT, p∥) quadrant differ from the 2D result by −1.54% to +0.65%.
   - Whether that is significant depends on the correlation between the two results, which share the data and is
     unmeasured.
   - With near-equal σ, the check certifies agreement only below ρ* = 0.989 (QC) to 0.9999.
   - The director offered a new option: measure the correlation from shared replicas.
   <!-- absence-ok: FD-GENCMP-DECLARATION §4 states "their correlation ρ is unknown"; git grep at 7ea0b9eb for cross-covariance / correlation of the 2D result finds only the published-vs-2D case (sec_results.tex:30), none for 2D vs the 16 cells -->
6. Asked how to handle the quadrant comparison:

   > Scope measuring the correlation (Recommended)

   sha256 begins `06ca9bde3ab761c7`.

## What is decided

1. **Q08, CH.** In Table IV, NuWro and GiBUU are shown on CH by step A's combination, as binding ruling 2 requires.
   - The carbon values move to the text and the note.
   - GiBUU's table note carries its hydrogen label in full:
     - closure B3 failed on hydrogen;
     - a post-hoc bias check passed at ≤ 0.1 σ_c;
     - 46% of the hydrogen sample is DIS that does not conserve energy;
     - hydrogen enters with weight 1/13.
   - One clause gives GiBUU's rise (+2.3, from 45 to 48 for 8 degrees of freedom) and its fall in shape-only χ² (25 to
     22). It also says the sign of the rise depends on the hydrogen sample (44.2 with GENIE's hydrogen).
2. **Q10, analysis definitions.** All four predictions in Table IV use the rebuilt values of the "CH, analysis
   definitions" corner (report §2.2).
   - The sentence "Unlike the analysis definitions, the predictions compute W with the neutron mass … and measure pT
     about their own neutrino axis" is removed.
   - A method sentence replaces it. It gives the largest per-cell change, at most 0.07σ (0.063 measured), and says
     that the beam-direction offset is sampled from the analysis simulation's distribution.
3. **Q08, native NuWro.** One clause, with its numbers: a native CH generation of NuWro agrees with the combination
   within a tolerance fixed in advance (Σz² = 17.9 for 16 cells, largest |z| = 2.2).
   - The +2.1% probe-chunk diagnostic goes to the note.
   - The clause is about NuWro only.
4. **Q26, 3D.** The 3D comparison (quadrant sums 0.2–0.8% below the 3D central value, ≤ 0.17 σ16) goes to the note
   only, with its "descriptive, not a test" label.
5. **Q26, 2D quadrants: scope first.** The paper keeps its present sentence (`paper_body.tex:119`) until this is
   resolved.
   - The director commissions a scoping: whether the 2D result and the 16-cell result share bootstrap and systematic
     replicas from which their covariance can be computed, and at what price.
   - Any compute is declared, priced and bound under `DECISION-20261101-joseph-reopen-1b-and-compute-for-limitations.md`.
   - The quadrant wording comes back to Joseph with the result.
6. **Consequential edits made by the paper lane with items 1–3:**
   - **Sentences the change makes false:**
     - at `:42`, "The predictions for carbon are …", "per nucleon of their target" and "… which the sixteen-cell
       comparison … does not correct";
     - at `:232`, "NuWro and GiBUU are on carbon, with no correction to CH".
   - **Regenerated:** the Table IV values, the captions and labels, the ratio figure, and the note's `sec_fived16`
     tables.
   - **Reconciled:** the primer and `sec_joint` statement that the correction "moves both toward the data". That
     holds on the joint cells, but on the 16 cells GiBUU's total χ² rises.
   - **One stated caveat:** C_model's shape ratios are still from the carbon generators. Rather than stating that,
     the lane may measure it.
   - **Review:** the paper lane's PR is reviewed against this record before merge.

## Correction (director, 2026-11-01, later)

Step C of FD-GENCMP (#648 §2.3) compared the sixteen cells against a superseded 2D result.
- **What it used:** E_U (`4f5a1b6d…`) and Q (`s5_plus_playlist.npz`, `8ccb4d72…`), from DECISION-20261017.
- **What is adopted:** `DECISION-20261024-joseph-adopt-re2-2d-refined.md:30` makes E_R the adopted 2D result, with
  Q_R (`b57d6c96…`, `RE2-PARTC-REPORT.md:132`) as its headline uncertainty, and says "This replaces `E_U` and Q."
- **Who caught it:** the declaration, its review and the director's binding (#647) all missed it.
  limitation-resolver found it on 2026-11-01 while scoping item 5.

**What this does to the numbers quoted above.**
- The quadrant differences (−1.54% to +0.65%) and the ρ* values quoted to Joseph in items 3, 5 and 6 are against
  E_U and Q, not against the adopted result.
- RE2-PARTC-REPORT §6 puts E_R − E_U at a median 0.06σ and a maximum 0.48σ of Q_R per cell.
- Items 1–4 do not read step C and are unaffected.

**What follows.**
- Item 5's scoping is done against E_R and Q_R.
- Step C is rerun against them, at 0 node-h, under a bound amendment.
- Its report supersedes #648 §2.3's 2D numbers.
- Joseph is told of the correction with the rerun's result.

Nothing is submitted, deposited or tagged.

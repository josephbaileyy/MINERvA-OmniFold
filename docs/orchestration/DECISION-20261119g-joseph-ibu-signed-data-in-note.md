# DECISION 2026-11-19 (g) — Joseph: one descriptive sentence on the signed-data IBU check goes in the note

**Recorded by** director-helper-3, for the director, who relayed Joseph's words and confirmed that the review condition is met.

## What led to it

- **Two restrictions.**
  - [`DECISION-20261119e-joseph-ibukt-signed-ibu.md`](DECISION-20261119e-joseph-ibukt-signed-ibu.md), item 5: "No note wording changes from any outcome."
  - [`state/2d-closeout/IBU-SIGNED-DATA-DECLARATION.md`](state/2d-closeout/IBU-SIGNED-DATA-DECLARATION.md), line 7: the study cannot "…or change the paper or note."
- **The outcome.** [`OUTCOME-20261119-ibu-signed-data.md`](OUTCOME-20261119-ibu-signed-data.md) records the signed-target IBU check on the data. Its terminal receipt is `readout.json`, SHA-256 `a4ec72c1369d763469af1105839c944bee5487d8a69ecd6947d92fac6912317c`.
- **The review.** The director had a referee (gpt-6.2-sol, personal account) read whether the check belongs in the note. Its report is `~/codex-reports/referee-ibu-in-note-20261119/report.md`, SHA-256 `e7469305e2e7f29b84da056303577998a1bc76d8692e1a7c3442c8cc89c343c8`. It recommends a narrow exception: one sentence in the existing 2D central-value benchmark paragraph, and nothing else.

## Joseph's words, verbatim

2026-11-19, quoted as relayed, typos included:

> my initial thought is also to release the note note wording changes decision and the signed data declaration but not sure, if thats what the review comes back with, I approve it in advance since I may be away from the computer

(`2cf11252dbb20d9a9ef873a0e6d191a42727fbb4199cb2aeac30ddec202ea225`, the sha256 of the text plus a final newline.)

The approval was conditional on the review. The review came back recommending the narrow exception, so the condition is met, and the decision takes the review's scope.

## What is decided

1. **A one-sentence exception.** It applies to DECISION-20261119e item 5 and to the scope clause of IBU-SIGNED-DATA-DECLARATION.md line 7.
2. **What it covers:** only the descriptive fixed-IBU comparison at K=5 and K=10. This is the χ²/ndf between the recorded OmniFold E_R and IBU results, evaluated with the published covariance, for the refined and the signed targets. The values are those of OUTCOME-20261119-ibu-signed-data.md rows 19–20: 1.623 to 1.621 at K=5, and 3.120 to 3.066 at K=10.
3. **Where it goes:** the existing 2D central-value benchmark paragraph of the analysis note (§3.1.5), after the iteration scan and before the covariance caveat.
4. **The sentence** is the referee's proposed insertion. It may be smoothed to the note's style, but it keeps the four numbers and "descriptive":

   > At fixed IBU settings, replacing the classifier-refined reconstructed target with the binwise data-minus-background histogram changed the descriptive $\chi^2/\mathrm{ndf}$ between the recorded OmniFold and IBU results, evaluated with the published covariance, from 1.623 to 1.621 at five iterations and from 3.120 to 3.066 at ten iterations.

5. **How it is checked.**
   - The four values come from the outcome's readout as values macros or allow-list rows, never typed.
   - The hunk is a two-reader hunk.
6. **The source texts stay unedited.** This record supersedes the two clauses only within the scope above. DECISION-20261119e and the declaration are not edited.

## Not lifted

- The IBUKT known-truth screen stays out of the note, appendix included.
- Figures F-B and F-C stay out of the note, appendix included.
- The A2 manuscript restriction stands.
- Every other interpretation limit of the declaration and the outcome stands. The sentence makes no claim about the cause of the OmniFold–IBU difference, or about which estimator is more accurate.

## Not decided here

- Any paper wording.
- Any value, claim, uncertainty or tolerance.
- Any further note wording from this or any other IBUKT outcome.

## CITABLE FOR / NOT CITABLE FOR

- **Citable for:** printing the one descriptive sentence above, with its four values, in the note's 2D central-value benchmark paragraph.
- **Not citable for:**
  - the known-truth screen, F-B or F-C in the note or appendix;
  - any paper or manuscript wording, including under A2;
  - any claim of cause, of estimator accuracy, of uncertainty or of significance;
  - any other note wording from an IBUKT outcome.

Nothing is submitted, deposited or tagged.

# History restructure, App. D (app_response_mismatch.tex): cut log

**Under** DECISION-20261113-joseph-note-n4-n5-role.md, the addendum recording Joseph's go of 2026-11-13, and the
director's ruling (A) of 2026-11-14 (recorded in sec_5d.md).

**The rule, verbatim as adopted:** history stays in the note only if removing it would change a reader's understanding
of the reported object, its reproducibility, its evidential independence or its limitations. Everything else goes to
the ledger. Each "fixed before" names its object, and "declared" alone is replaced.

**Referee:** for App. D it gave "5–10%, Compress. Keep completed response-shift results. Move the unexecuted protocol
and contingent follow-up plan to ledger; retain 'not tested' where relevant."

**Base:** `docs/analysis-note/app_response_mismatch.tex` at `e6d8b402a`. Line numbers are the base's.

**Outcome for App. D: no change.** The proposal below was reverted after the meaning read failed it. App. D is
byte-identical to the base.

## Proposed and reverted

| id | base line | old text | new text | ledger home |
|---|---|---|---|---|
| D-1 | :4 | "This appendix gives a validation protocol for such a test, not a result or an uncertainty component. Its first stage, the reconstruction-only test below, has been implemented but not yet run: no output of it has been produced and no pass threshold has been set." | "A reconstruction-only test of this kind has been implemented but not yet run. It scales the reconstructed $\Eavail$ of the pseudo-data by $(1+\epsilon)$, for both signs of $\epsilon$, while OmniFold keeps its nominal response, and its primary observable is the signed bias versus $W$, with $W<\SI{1.1}{GeV}$ reported separately. No output of it has been produced and no pass threshold has been set; it is not a result or an uncertainty component." The test's form and observable are restated from the cut protocol, :6–13, in its own words. The appendix guide (app_guide.tex:6, "rescales the reconstructed available energy of the pseudo-data while OmniFold keeps its nominal response") and §8 (sec_eavailw.tex:118, "designed to test whether an incorrect hadronic response can move strength into or out of the low-$W$ component. It has not yet produced a result") still describe what App. D states. | e6d8b402a:app_response_mismatch.tex:4 |
| D-2 | :6–13, with the guard comments :14–18 | the paragraph "Reconstruction-only test": its equation, the fixed simulation, the amplitude rule ("fixed before the results are examined", and its required justification), the outputs, and the implementation's restrictions and labels | cut (referee: "the unexecuted protocol") | e6d8b402a:app_response_mismatch.tex:6-18 |
| D-3 | :23 | the paragraph "Physically correlated follow-up" | cut (referee: "contingent follow-up plan") | e6d8b402a:app_response_mismatch.tex:23 |
| D-4 | :25 | the paragraph "Interpretation", which says how the unrun test's outcomes would be read | cut, with the protocol it interprets | e6d8b402a:app_response_mismatch.tex:25 |

**Kept as they are:**
- **:4's first three sentences:** what the other closures test and do not test, and Kevin McFarland's suggestion.
- **:4's last sentence**, "Closures of the same kind, from the shifted response samples of $C_{\mathrm{resp}}$, have
  been run (below)".
- **:20, the completed response-shift closures**, with their limits: "descriptive and carry no noise estimate", no
  pass threshold, and what they do not establish.
- **:26, the Search line** for "not yet run".

**Numbers and keys (of the reverted proposal):** `numdiff.py` on the base and the proposal, comments stripped:
- Removed: "3", from $q_{3}$ in the cut follow-up (D-3).
- Added: none. D-1's "1" and "1.1" restate the cut protocol's own.
- Value keys and macros: unchanged.

## The Development-history appendix

No new row. The test has not run, so nothing is superseded or stopped.

## Disclosure checklist

| disclosure | in App. D? | survives |
|---|---|---|
| the missing response uncertainty | the response-mismatch bias is not tested (:4), and the shifted-response closures do not establish the bias under the true detector response or validate $C_{\mathrm{resp}}$ (:20) | ✓ |
| the other eight of the director's list | no | — |

## Unreleased support

No site in App. D changes its citation. `UNRELEASED-SUPPORT.md` is unchanged.

## Meaning read (codex-school gpt-6.1-sol, high, read-only; reads/app_response_mismatch-prompt.txt, with the citing sentences in reads/app_response_mismatch-records.txt)

- **Pass 1, on the proposal:** OVERALL FAIL. reads/app_response_mismatch-pass1.txt.
  - Question 1 failed D-1, because "It scales the reconstructed … pseudo-data" drops "changes only the reconstructed
    pseudo-data record" and the fixed truth, weights and membership.
  - Question 2 classed as NEEDED, and lost, most of the unexecuted protocol:
    - its scope and processing order, and what it holds fixed;
    - the amplitude rule and its required justification;
    - "the global integral is a control";
    - the implementation's restrictions, and "must not be quoted";
    - "not a detector model", and the scalar-only outputs;
    - the Interpretation paragraph's limits.
  - It classed as LEDGER only the protocol framing, the output inventory, the guard comments, the cost remark, the
    follow-up procedure and its scheduling.
- **Why it was reverted, not repaired:** the read treats the protocol's restrictions and interpretation limits as
  limitations the rule keeps, against the referee's "Move the unexecuted protocol … to ledger". What it would let leave
  is a few sentences of framing and plan. As in §3 and §4, the text stays as at base. The referee's compression of
  App. D would need the director's ruling on whether an unrun test's protocol limits are limitations under the rule.

**The director's ruling (2026-11-14): leave App. D as it is.** "Strictly, an unrun test's protocol limits no reported
result. But App. D documents a test that is implemented in the released code, and its restrictions ('changes only
the reconstructed pseudo-data record', 'must not be quoted', 'not a detector model') are exactly what a reader of the
package needs before running it. Compressing it would gain little against what's at risk."

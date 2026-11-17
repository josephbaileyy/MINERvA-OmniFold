# E2/F6/C4 and the SD relabel: independent meaning read (codex-school gpt-6.1-sol, read-only, 2026-11-16)

Prompt: e2read/prompt.txt (two questions per changed sentence). Verbatim answer below; its FIXes were applied (designated-for-inclusion wording; the :458 sentence).

“Standard deviation” is correct at every shown relabel. With NumPy’s `ddof=0`,
\[
\mathrm{SD}(r)^2+\bar r^2=\frac1n\sum_i r_i^2=\chi^2_{\rm diag}/n,
\]
so the corrected equation is exact when `ndf = n` and the same bins are used.

The inclusion claims below are premature **before deposit**: the visible DOI hold identifies unfinished work but does not establish package contents. “Designated for inclusion” remains true before and after deposit.

| Site | Q1 | Q2 | Verdict (OK / FIX with exact replacement) |
|---|---|---|---|
| `app_guide.tex:8`, records/package sentence | Present-tense inclusion exceeds the planned deposit’s status. | Correctly limits inclusion to cited entries, rather than the whole records document. | **FIX:** `the entries cited are included in` → `the entries cited are designated for inclusion in` |
| `app_release.tex:9`, “RC7 is a replay package…” | Supported by E2 row 8, including SHA-256 specificity. | Removes time-sensitive release narration as intended; does not claim Zenodo completeness. | **OK** |
| `app_release.tex:54`, preservation sentence | Preserves the reproducibility limitation while allowing checksums to become public. | “They” clearly means preservation copies; “replay package” correctly means RC7. | **OK** |
| `app_statmethods.tex:362`, deleted exact-split `1.47` sentence | Authorized historical cut. | Surviving near-one caveat remains complete. | **OK** |
| `app_statmethods.tex:419`, “paper covariance alone gives…” | Correct SD relabel; value unchanged. | No additional meaning change. | **OK** |
| Same paragraph, “standard deviation is slightly larger…” | Preserves the existing comparison. | “Larger” appropriately replaces “wider” for a scalar SD. | **OK** |
| `app_statmethods.tex:458`, “No test … separates these candidates.” | Broader than the old evidence: one diagnostic was not repeated; that does not establish absence of every separating test. | “These candidates” has a clear antecedent, but the negative claim is strengthened. | **FIX:** “The split-bootstrap diagnostic used on the earlier rebuilt bootstrap has not been repeated for the quoted statistical block.” |
| `app_statmethods.tex:513`, exact-split `0.598` / quoted-value sentence | SD matches the producer’s calculation. | Both estimators and the three-value correspondence remain clear. | **OK** |
| `app_statmethods.tex:518`, diagonal equation | Correct population-variance identity; the former RMS expression double-counted the squared mean. | Intended mathematical correction; no new inference. | **OK** |
| `main_note.tex:138`, “Results were accepted only after…” | Retains the existing verification and independent-review claims. | Removes only the developer-relative review clause. | **OK** |
| Same passage, “Reviews included models from multiple developers.” | Exactly C4’s authorized wording. | Makes no claim that each review crossed developers. | **OK** |
| `sec_method.tex:150`, hyperparameter sentence | Retains the supported no-search claim and removes unsupported timing. | Explicit learner scope is clear; subsequent sentences retain their antecedents. | **OK** |
| `sec_results.tex:42`, standardized-difference sentence | Correct SD relabel. | No additional change; existing “centered” and “well inside” language is inherited. | **OK** |
| `sec_results.tex:55`, table label | Correctly identifies the reported statistic. | No meaning change beyond correction. | **OK** |
| `sec_results.tex:130`, tension opening | Correct SD relabel; `0.29` remains consistent with SD² + mean². | Descriptive qualification remains. | **OK** |
| `sec_summary.tex:38`, replacement release sentence | Describes the appendix without asserting that the planned package is complete. | Verifier applies clearly to the replay package; provisional objects remain acknowledged immediately before it. | **OK** |
| `publication.bib`, `JointTestRecord2026` | Inclusion is authorized but pending. | Intended record scope. | **FIX:** `Included in` → `Designated for inclusion in` |
| `publication.bib`, `JointTestRecovery2026` | Inclusion is authorized but pending. | Intended record scope. | **FIX:** `Included in` → `Designated for inclusion in` |
| `publication.bib`, `JointTestProjections2026` | Inclusion is authorized but pending. | Intended record scope. | **FIX:** `Included in` → `Designated for inclusion in` |
| `publication.bib`, `JointTestRecoil2026` | Inclusion is authorized but pending. | Intended record scope. | **FIX:** `Included in` → `Designated for inclusion in` |
| `publication.bib`, `JointTestKappa2026` | Inclusion is authorized but pending. | Intended record scope. | **FIX:** `Included in` → `Designated for inclusion in` |
| `technote.bib`, `UnfoldedWeightsESS2026` | Inclusion is authorized but pending. | Intended record scope. | **FIX:** `Included in` → `Designated for inclusion in` |
| `technote.bib`, `TwoDFollowup2026` | Inclusion is authorized but pending. | Explicitly retained current support under E2. | **FIX:** `Included in` → `Designated for inclusion in` |
| `technote.bib`, `ReleaseCandidate2026` | Inclusion is authorized but pending. | Refers to the record; does not enlarge RC7’s capabilities. | **FIX:** `Included in` → `Designated for inclusion in` |
| `technote.bib`, `AnaTuplePreservation2026` | Inclusion is authorized but pending. | Depositing the record does not imply depositing preservation copies. | **FIX:** `Included in` → `Designated for inclusion in` |
| `technote.bib`, `NoteRecords2026` | Present inclusion is premature. | Correctly promises cited entries only. | **FIX:** `are included in` → `are designated for inclusion in` |

Two residual labels also remain visible: the `app_statmethods.tex` hunk heading contains `summarized by mean, RMS,` (replace with `summarized by mean, standard deviation,`), and the supplied producer still prints `rms` in its panel and log despite computing SD.
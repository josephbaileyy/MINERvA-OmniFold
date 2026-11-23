# The combined-covariance pull spread relabelled standard deviation: independent meaning read (codex-school gpt-6.1-sol, read-only, 2026-11-16)

Sites: app_statmethods.tex:411 (three), the table heading at :543, :599, :618. Producers: compare_to_paper_fullcov.py:313 (pull[mask].std()), via re2c_run.sh:137 for chi2_Q_std.txt; lgbm_central_metrics.py:58 (pull.std()) for the LightGBM rows and 0.598. The HistGBT row (0.56) has no traced producer; the FIX was applied in short form: its cell reads "0.56 (RMS)", the heading "pull SD". Verbatim answer:

`pull.std()` computes standard deviation about the mean (`ddof=0`), so the traced values support “SD.”

| Site | Q1 | Q2 | OK or FIX with exact replacement |
|---|---|---|---|
| “summarized by mean, standard deviation…” | Yes. | No other meaning or grammar change. | **OK** |
| Combined covariance: mean 0.034, standard deviation 0.389 | Yes for the label. | “Centered on zero with no global offset” remains an unchanged interpretation. | **OK** |
| “A standard deviation below $1$ is descriptive…” | Yes. | “Below $1$” means exactly `$< 1$`; the caveat remains intact. | **OK** |
| Table heading “pull SD” | Yes for 0.598 and LightGBM 0.564/0.563/0.565; unverified for HistGBT 0.56. | Applies an established definition to an untraced 10-seed mean. | **FIX:** `pull SD (HistGBT: reported ``RMS'')` |
| “pull mean/standard deviation $0.034/0.389$” | Yes. | Slash still pairs the two statistics with their values; grammar remains clear. | **OK** |
| “Pull standard deviation $= 0.389$” | Yes. | No other meaning change. | **OK** |
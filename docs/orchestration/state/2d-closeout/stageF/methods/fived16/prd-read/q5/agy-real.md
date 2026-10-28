COUNT: yes, nominal, W1, W2, W3, closure NuWro, A7 MnvTune, A7 GENIE CV, A7 GENIE+MEC, A7 NuWro
CELL-CRITERION: holds
P-CRITERION: holds
WORDING: differs; while the numerical thresholds (2 and 0.01) match |z| > 2 and p < 0.01, Record 2 defines z as a pull including pseudo-data noise N (`z = b/√diag(C + N)`) rather than reported uncertainty alone, and 2σ allows twice the uncertainty rather than staying within it.
VERDICT: FALSE
REASON: The claim that bias "stays within the reported uncertainty" is false because a 2σ threshold permits bias up to twice the uncertainty, directly contradicted by Record 4 showing bias exceeds 1σ: "A7_nuwro: grade matrix C_total minus nuwro + C_resp; max|z| 1.343; max|b|/sigma without N 1.343; p 0.0713; listed False". Furthermore, Record 2 states "Pulls z = b/√diag(C + N) and χ² = bᵀ(C + N)⁻¹b", showing the cell criterion evaluates pulls that include pseudo-data noise N rather than reported uncertainty alone.

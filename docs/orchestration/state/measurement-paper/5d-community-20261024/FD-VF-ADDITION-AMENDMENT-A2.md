# AMENDMENT A2 to FD-VF-ADDITION-DECLARATION.md: the names Joseph adopted (2026-11-25)

**By** tier3-design, under Joseph's adoption of codex-school2's table layout and naming for the inflated block,
relayed by the director on 2026-11-25. **Amends** `FD-VF-ADDITION-DECLARATION.md` (`31662736…`) throughout: names only.
The arithmetic, the controls and the outputs' content are unchanged.

## The names

| declaration's name | the name in outputs, readings and the note | in code, keys and argv (ASCII) |
|---|---|---|
| V_F = L C_e Lᵀ | **C_e^infl**, the eigenvalue-rescaled C_e. V_F stays only as an alias in B5D's build records (`blocks5d-20261124/record/V_F.csv`) | `C_e_infl` |
| dF = V_F − C_e | **ΔC_e = C_e^infl − C_e**, the "covariance increment" | `DeltaC_e` |
| the extra blocks dF; C_resp + dF; C_resp + C_PL5D + dF | ΔC_e; C_resp + ΔC_e; C_resp + C_PL,5D + ΔC_e | keys `DeltaC_e`, `C_resp_plus_DeltaC_e`, `C_resp_plus_C_PL5D_plus_DeltaC_e`; names `DeltaC_e`, `C_resp + DeltaC_e`, `C_resp + C_PL5D + DeltaC_e` |
| C_rep,F | **C_rep = C_e^infl + C_model + C_resp + C_PL,5D**, with C_total kept as the baseline subtotal C_e + C_model | `C_total_plus_C_resp_plus_C_PL5D_plus_DeltaC_e`; without C_PL5D, `C_total_plus_C_resp_plus_DeltaC_e` |
| the band ratio f̂_j; the factor φ | **r̂_j**, the estimated band ratio; **φ_j**, the applied variance multiplier | (B5D's record keeps its keys) |
| bands R1–R3 | **eigenvalue ranks 1–4, 5–8 and 9–16** in anything that reaches the note (R00–R15 are cell IDs) | — |
| C_b | the **candidate fake-data bias covariance**, shown descriptively and stated as excluded | — |

`vf_block.npz` carries the new keys (`C_e_infl`, `DeltaC_e`, …). Its bytes therefore change from the declaration's
draft to sha256 `cef8460a1dcc0db64f536af0099db1e1523ed2601d5c8ecc682afc0f9440c99b`, while every array is the same
float64 array as before.

## The per-cell σ table (for the readings, §5)

The six source columns and the C_e column stay. A **C_e^infl** column goes right beside C_e. There is no ΔC_e column.
The headline uncertainties and the correlation table use C_rep. The readings give the per-cell σ of both the C_e
column and the C_e^infl column. JE writes the note side.

**CANNOT AUTHORIZE:** a change of arithmetic, controls or outputs' content; any note wording.

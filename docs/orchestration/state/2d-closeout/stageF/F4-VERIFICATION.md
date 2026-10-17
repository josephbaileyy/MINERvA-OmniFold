# Stage F F4: independent verification of the Stage C production REPORT

**Owner:** the paper-tighten lane, as director. On 2026-10-17 I dispatched a fresh read-only verifier on PR #150 at
`5a247ee3`. The closer applied its findings at `7cc4caaf`, and the PR was merged as `55e6f44d`.

**CITABLE FOR:** S5's products (`production_cov.npz` `6689d2fc…`, `s5.json` `8c815149…` and
`uq_production_covariance.root` `34cf33f9…`) being reproduced independently from the production unfolds, together
with the REPORT's provenance, completeness and accounting.
**NOT CITABLE FOR:** an adoption, a coverage statement or a claim. S5 stays diagnostic until Joseph adopts it
(checklist J2).

The report under review is [`../stageC/production/REPORT.md`](../stageC/production/REPORT.md).

## 1. Verdict

**VERIFIED WITH FINDINGS: 0 MATERIAL, 4 MINOR.** The closer dispositioned all four in one commit (`7cc4caaf`, REPORT
§14), and the director checked that delta before merging. It changes text and evidence only; no product or number
changed.

| part | result |
|---|---|
| A. Independent rebuild | Every S5 block was rebuilt from the 530 consumed `xsec.root` vectors with the verifier's own code (`recompute.py`), without importing or executing `s5_rollup.py`, `analyze_prod.py` or `build_repair.py`. Max \|diff\| / max \|block\|: universe, the 43 bands, normalization, c08, x02 and F at 0.0; stat 1.4e-16; bkg-separable 9.8e-17; total 8.8e-19. The 31 functional σ match `s5.json`. Not vacuous: dropping the Flux weights changes the Flux band by 0.977, and dropping the X01 rescale changes the MINOS band by 0.099 |
| B. Provenance | 10 result files byte-identical on pscratch, on CFS and in `evidence/`. `repo_k` matches the packing-binding table, and `repo` matches the 2026-10-15 binding. Six item JSONs PASS, with `pins_failed {}` |
| C. Completeness | 539 allocations: 153 ran, all COMPLETED 0:0, and 386 never started. 515 member steps. Charge 29.0297 node-h, recomputed. All 531 `xsec.root` files pass `sha256sum -c` on pscratch and on CFS |
| D. Text | The quoted numbers match their sources. Nothing reads as adoption, coverage, a G2 zero effect or a claim beyond the endpoint. The four shared-QOS gate shortfalls match the transcript and the `sacct` Submit times |
| E. Extra | Replica provenance in all 480 outputs, 0 mismatches. All 480 vectors are distinct. The S4B ↔ S1 bootstrap pairing holds in all 80 cases. `C0_cv` reproduces `E_U` to 4.2e-13 |

Findings and dispositions:

1. The X01/Flux implementation details DESIGN §8 leaves unstated are now named in REPORT §3.
2. The shared-era GATE lines now have a committed transcript extract, with a byte-prefix sha256. The director
   re-measured it as `2211c960…`.
3. The director's ruling is cited in REPORT §12.
4. Two submit times are relabelled in §4.

## 2. The director's ruling on the gate deviation (REPORT §5, §12)

On 2026-10-15 four shared-QOS gates (S1b, S1c, S1d and S1f) ran before `sacct` listed the previous batch. Their
in-flight terms were short by 0.2125–1.9125 node-h. The true totals were at most 79.43 of 100.0.

- **Ruling (2026-10-17, within the director's compute authority):** the disclosure suffices, and no separate record is
  needed.
- **Grounds:**
  - it is quantified;
  - no ceiling was affected;
  - S2b's refusal used a complete ledger;
  - the packed-era coverage check closes the hazard (every squeue id must appear in the ledger);
  - no charge, product or check depends on it.
- It remains a breach of DESIGN §6.

## 3. Evidence

The verifier's files are in [`f4-verify/`](f4-verify/), byte-identical to
`/pscratch/sd/j/josephrb/tmp-stagec-f4-verify-20261017/`, with `SHA256SUMS` (21 files; `shasum -c` OK locally).
The main files are `recompute.py` with its `recompute_stdout.txt` and `recompute_result.json`, plus `f4_result.json`.

**Same-model caveat:** the director, the closer, the closer's verifiers and this verifier are all Claude Opus 5.5.

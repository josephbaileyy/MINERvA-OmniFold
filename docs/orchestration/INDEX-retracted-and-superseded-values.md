# INDEX — retracted and superseded values

**Why this exists.** A retracted number does not stop being readable. Every value below still appears in the
corpus, presented with the same confidence as a live one, and **nothing at the point of use marks it dead**.
A fresh session writing the analysis-note update reads artifacts, not this session's context — so a value that
is only known-dead inside one agent's head is, operationally, alive.

**Read this before quoting any number from `VALIDATION_LEDGER.md`, a `PREDECLARATION-*`, a `*_RUN_LOG.md`, a
receipt JSON, or a commit message.**

**Sourced from `git grep`, not from recall.** Every "where it still appears" entry below was located by search
at `2026-08-11`. Where I could not source a location, the row says so rather than listing it from memory — an
index built from memory has exactly the defect it exists to fix. *Requested by the oversight session; the
`VALIDATION_LEDGER` exposure was found while building it and is the most serious entry here.*

## The two kinds of entry, which a reader will otherwise conflate

- **DEAD** — replaced, and must not be quoted in any form.
- **ALIVE-AS-CITED-ARTIFACT-ONLY** — the value is a real, validated artifact number and must keep being cited
  *as that*, but must **not** be used as the best estimate or as *the* value of the quantity.

Same distinction as `PROCESSED.txt`'s grandfathered-vs-verified split, and for the same reason: two different
claims that look identical on the page.

## Index

| dead value | where it still appears | what supersedes it | why it died |
|---|---|---|---|
| **`FINDING — code paths disagree`** (the verdict) | `VALIDATION_LEDGER.md` §2026-08-10 (**now bannered**); `docs/orchestration/RUNS.tsv:267` row `P5A-ANNEALED-NOMINAL-A2-COMPLETE`; `docs/orchestration/state/annealed-nominal-complete-56563761.json`; commit `b1414df` message | **REFUTED.** No established code-path difference — `KNOWN_ISSUES.md` struck-through entry; `PREDECLARATION-20260810-designA-diagnostic-reproduction.md` §RESULT; `535668d` | Production `-0.035546` sits **inside** the diagnostic configuration's own 3-run range, `0.48` sd from its mean |
| **`188.4x` / `188x`** (gap ÷ scatter) | `VALIDATION_LEDGER.md:~1055` (bannered); `RUNS.tsv:267`; `PREDECLARATION-20260810-annealed-production-reproduction.md:102`; `KNOWN_ISSUES.md:511`; `AUTONOMOUS_LOG_20260805.md:3387,3892`; commit messages `7b2198a`, `b1414df` | **`0.48x`** — gap ÷ the three-point diagnostic sd (`0.024701703`) | Denominator was the **production** scatter, a population the diagnostic configuration does not belong to. Superseded twice: `188x` → `6.0x` (two-point difference) → `0.48x` |
| **`6.0x`** (gap ÷ two-point diagnostic difference) | `AUTONOMOUS_LOG_20260805.md:4127`; commit message at `7b2198a` era | **`0.48x`** as above | Two points give a **difference, not a spread**. This is the same error as the row above, one step less wrong |
| **`-0.011724321` / `-1.17%`** labelled *"diagnostic expectation"* or *"expected"* | `VALIDATION_LEDGER.md:1051,1055,1062` (bannered); `PREDECLARATION-20260810-annealed-production-reproduction.md:34,96`; `KNOWN_ISSUES.md:480,505,552`; `PREDECLARATION-20260810-designA-diagnostic-reproduction.md` (as the REPRODUCED window centre) | **Nothing** replaces it as an expectation. The configuration's distribution is `mean -0.023761959, sd 0.024701703` (n=3) | It was **one draw** from an `sd≈0.025` distribution and was never a property of anything. **Standing constraint:** no one-shot measurement through the `diagnose_step1_annealed_lr.py` wrapper family may be quoted as a point value |
| **`142 scatters` / `142 production scatters`** (D2 margin) | `nd-unfolding/pet/sbatch_powered_closure_stability_repeat.sh:138` — **hardcoded in the launcher's STABLE verdict text, and it printed at full confidence in `56626305`'s log hours after retraction**; `PREDECLARATION-20260811-powered-closure-stability.md:22,43`; `CLAIMS.md` CLM-012 (ix); `AUTONOMOUS_LOG_20260805.md:4174,4422,4489` | **`22.0`** — margin ÷ the three-run closure sd (`0.000820128`). And preferably **no ratio at all**: all 3/3 draws clear the bar individually | Same wrong-population error. Retracted at `98d502d`. **The launcher instance is the dangerous one** — verdict text should emit the *comparison*, not a derived number that lives elsewhere, or it prints stale claims automatically |
| **`14.7`** (margin ÷ two-point closure difference) | `CLAIMS.md` CLM-012 (ix); `AUTONOMOUS_LOG_20260805.md` 08:25Z entry; commit `98d502d` message | **`22.0`** as above | Two-point difference used as a spread, again |
| **`recovery_criteria_met`** (report field) | Every `POWERED_CLOSURE_*.json`: `slurm-56552326`, `slurm-56611837`, `slurm-56626305`, and the graded closure's; documented at `KNOWN_ISSUES.md:447-467` | The **validator** `validate_pet_nominal_gate4.check_powered_closure`, which reads the adopted `residual_over_gap_max` | Computed against the **retired** `recovery >= 0.80` bar, so it reads `false` for results the campaign has adopted as passing. **A self-report, never the gate** |
| **`RESIDUAL_OVER_GAP_MAX = 0.20`** (the retired bar, still executing) | `nd-unfolding/pet/closure_powered_truth_reweight.py:105` — **live code, deliberately not fixed** | Adopted criterion `recovery >= f × ceiling(k)`; at k=3, `0.4945824` | CLM-012 retired the absolute `0.80` bar on 2026-08-09. Not patched because editing a threshold inside a closure is the prohibited act and the validator already governs — it also causes the **expected exit 3** that makes completed runs read `FAILED` |
| **`0.5126032761517403`** used as *the* D2 recovery | `CLAIMS.md` CLM-010 (vi) and CLM-012; both powered-closure predeclarations | **ALIVE-AS-CITED-ARTIFACT-ONLY.** Keep citing it as job `56552326`'s validated value (finalizer `56562169`, 31/31). Best estimate is the three-run mean **`0.5123048`, sd `0.000820128`** | Not wrong — one of three draws, and the only one with a finalizer behind it. Quoting it as *the* recovery overstates precision; replacing it in the gate would break a validated provenance chain |
| **`recovery >= 0.80`** as Gate-4's D2 criterion | Widely, in pre-08-09 text; `CLM-012`'s own status line records the retirement | `recovery >= f × ceiling`, `f = 0.80`, `ceiling = 0.618228` (per-cell) → `0.4945824` | Retired as a **bug**, not a re-specification: `φ(E[a]) = 0.808415` rounds to `0.80`, i.e. a ceiling computed in the wrong scope. See CLM-012 |

## Not included, and why — the honesty column

- **The 2026-07-12 quarantine** was named to me as a candidate. **I have not sourced it** and it is therefore
  **not indexed**: I could not point at which values from it are still readable as live without a search I did
  not run. Listing it from a description would be exactly the defect this file exists to fix. **Open item for
  whoever holds that context.**
- **Commit messages are immutable and are not fixable.** `7b2198a`, `b1414df` and `98d502d` carry retracted
  figures in their bodies and will forever. They are indexed above so a reader following `git log` finds the
  correction; they are not errors to be repaired.
- **Superseded values inside `PREDECLARATION-*` documents are deliberately left as written.** A predeclaration
  records what was fixed *in advance*; editing its body to match the outcome would destroy the only property
  that makes it worth anything. Each carries a §RESULT section stating what happened instead.

## The generalisation, which is why this file is worth more than its rows

**A retraction that does not say where the corpse is leaves the reader to find it by accident.** Every row's
load-bearing column is *"where it still appears"* — not the correction, which was already recorded at the time
in every case. The corrections existed; the map to the stale copies did not, and the map is what a fresh reader
needs. Same argument as leaving a struck-through headline rather than deleting an entry.

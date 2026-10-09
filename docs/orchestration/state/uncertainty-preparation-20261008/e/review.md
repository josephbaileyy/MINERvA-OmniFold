# Independent review — preserved by E

Preserved verbatim by E (integration owner) from the reviewer's external scratch
`/private/tmp/minerva-uncprep-review-20261009/review.md` (sha256 `7b71fb618746f0fb8e6a27930afe35822222269812bed288118c952ace674faf`, 29847 bytes), written 2026-10-09T07:37Z by a single fresh read-only reviewer
(Claude Opus 5.5, Claude Code subagent; no authorship of A–E work; launched by E with the raw inputs
and the scientific question). Its scripts, outputs and logs are under [`recompute/`](recompute/); their
digests are in [`recompute/README.md`](recompute/README.md). The reviewer's `ops/` operand copies (46 MB)
were not committed: each is identified by its remote sha256 in `recompute/logs/remote_sha256.txt`.
The reviewer's three JSON outputs are stored as `rc_*.json.txt`, byte-identical, so the receipt-artifact
scanner does not read a computation output as a receipt (the convention lane A used for its logs).
Paths in the text below that start with `recompute/` or `ops/` are relative to that scratch directory.

---

# Independent review: uncertainty-investigation preparation (lanes A–D), integrated pin `cd0da202`

Reviewer: single fresh read-only reviewer (Claude Opus 5.5). I authored none of the reviewed work. I
did not import or call any owner script to get a number. All arithmetic below comes from my own code
run on byte-copied operands. Scratch: `/private/tmp/minerva-uncprep-review-20261009/`.

## 1. Tree status and HEAD

| when (UTC) | `git status --porcelain` | `git rev-parse HEAD` |
|---|---|---|
| start 2026-10-09T07:15:33Z | empty (exit 0) | `cd0da20240059ec884f8855614eddab32bcf2ec8` |
| end 2026-10-09T07:35:04Z | empty (exit 0) | `cd0da20240059ec884f8855614eddab32bcf2ec8` |

I ran every test with `-B`/`PYTHONDONTWRITEBYTECODE=1` and `TMPDIR` set to my scratch. Status was
also empty after each test run. I ran no git write command in any checkout. The pin and upstream-main
ratchet runs used `git archive` into scratch (§4d); those trees are deleted.

## 2. Independent recomputations

Scripts: `recompute/rc_pairing.py` (sha256 `dbaf1cf2…`), `recompute/rc_assurance.py` (`47a9dad0…`),
`recompute/rc_costs.py` (`444c1234…`), `recompute/rc_oc.py` (`171735f6…`). Outputs sit next to them as
`rc_*.json`. Operand copies are in `ops/`. I checked every copied file against a remote `sha256sum` run
on the same files: 300 replicas, 10 seedscan products, 188 sweep files (dereferenced), and 100
unscaled Flux universes plus the flux band. All match (`remote_sha256.txt`, `ops/fluxraw/sha.txt`).

Operand digests (sha256): `E_C` = `2d_crossSection_omnifold_MEFHC_5iter.root` `142a45b0…7fd5`;
CV42 `4f5a1b6d…eb2c`; VL170 cov `71a75821…0115`; ML cov `3b6b48ec…5db9`; universe/combined
`uq_universe_covariance_full_matcorr_fluxfix.root` `077912e3…52f5`; paper `cov_ptpl…6GeV.root`
`6c6dce72…73e3`; seedscan seed1..10 concatenated in shell-glob order `84942b09…c6d0` (equals A's
value); flux band `flux_integral_universes_MEFHC.root` `5eecae84…80eb`; `bin_mapping.txt`
`d21a41eb…e12a`; `sacct_all.txt` `ae806c61…e2d1`; `sacct_ki85.txt` `675b20b3…f38e`. The first six match
the committed receipts (A verification §2, `recompute_2d_budget.json`).

| quantity | owner's value | my value | match? | operand | script |
|---|---|---|---|---|---|
| GlobalID = (Ptbin−1)·16+(P∥bin−1); TH2 axis 0 = p_T | A: row-major = GlobalID | true from `bin_mapping.txt` (224 rows), axis edges match | yes | bin_mapping, `E_C` | rc_pairing |
| 205-bin mask equality (`E_C`>0, CV42>0, VL170 mean>0, seedscan mean>0, paper ROOT stat diag>0, paper txt stat diag>0) | 205, all identical | 205 each, all identical to paper ROOT diag | yes | above | rc_pairing |
| `C_S` from 300 replicas (ddof 1) vs stored `hCov2D_reported` | 4.0e-16 | 5.6e-16 max\|Δ\|/max; ddof 0 would be off by 3.3e-3 | yes | replicas, `71a75821` | rc_pairing |
| √tr `C_S`; median σ/mean | 1.9312e-40; 0.674 % | 1.93117e-40; 0.6739 % | yes | same | rc_pairing |
| replica / `E_C` max \|c−1\| | 1.6e-14 / 1.6e-14 | 1.577e-14 / 1.577e-14 | yes | same | rc_pairing |
| `C_ML` from 10 seedscan (ddof 1) vs stored | 3.3e-16; √tr 5.0605e-41 | 1.7e-16; 5.0605e-41 | yes | seedscan, `3b6b48ec` | rc_pairing |
| `C_U` = Σ_bands MAT (mean-centred, 1/N) + (0.014·x_CV42)(0.014·x_CV42)ᵀ vs `hCov_universe_total` | 0.0 | 2.6e-17. Alternatives refuted: 1/(N−1) 0.95; CV-centred 0.116; no norm term 5.7e-3; norm on `E_C` 3.0e-4 | yes | sweep (188), `077912e3` | rc_pairing |
| convention matches `analyze_universes.py` | (A asserts) | yes: lines 231–234 (`Z = D − mean; cov = ZᵀZ/N_u`), 248–253 (`v = σ·cv_rep`, cv = `--cv` = CV42 in `rollup_vl170_adoption.sh:23,38,48`); CV file in the glob is skipped by `UNI_RE` | yes | source | read |
| Flux rescale at product level: fluxfix Flux_u = raw Flux_u × Φ_CV(p_T)/Φ_u(p_T) | **A: "not re-derived at product level"** | max rel. deviation **0.0** over 100 universes; rescale changes bins by up to 12.1 %; Flux-band median σ 1.01 % → 4.99 %; `hFluxCV` = `E_C` `hFlux_pt` to 2e-16 | newly verified | raw Flux_*, flux band | rc_pairing |
| `hCov_combined − C_U − C_S` | 7.2e-14 of max C_S | 7.16e-14 | yes | `077912e3` | rc_pairing |
| block-sum median rel σ, den CV42 / den `E_C` | 6.8707 % / 6.8269 % | 6.87066 % / 6.82688 % | yes | above | rc_pairing |
| lgbm seed1 vs `E_C`: \|Δ\|/x, \|Δ\|/σ_S med/p84/max, bins >1σ/>2σ | 0.97/2.67/12.50 %; 1.30/2.76/8.32; 126/62 | 0.966/2.668/12.50 %; 1.300/2.758/8.323; 126/62 | yes | same | rc_pairing |
| seed mean vs `E_C` /σ_S; /σ_ML | 1.33/2.81/8.35; 5.15/11.95/31.3 | 1.334/2.812/8.345; 5.147/11.954/31.35 | yes | same | rc_pairing |
| CV42 vs `E_C` /σ_S | 1.32/2.70/8.38; 132/66 | 1.324/2.704/8.382; 132/66 | yes | same | rc_pairing |
| CV42 vs seed1 /σ_S; VL170 mean vs seed1 | 0.30/0.53/1.28; 0.23/0.52/1.36 | 0.295/0.533/1.278; 0.231/0.522/1.363 | yes | same | rc_pairing |
| σ_ML/σ_S | 0.26/0.42/0.73 | 0.260/0.418/0.726 | yes | same | rc_pairing |
| total cross section `E_C` | 3.07331e-38 | 3.07331e-38 | yes | `E_C` | rc_pairing |
| central backend evidence (job 53116554) | exact sklearn GBT, single core | `sacct`: `unfold_MEHFC`, `regular_milan_ss11`, 05-18 12:57 → 05-19 08:15, ElapsedRaw 69,523, billing 256, MaxRSS 16,786,760K, TotalCPU 19:18:00 (= one core), SubmitLine `sbatch sbatch_unfold_2d_MEHFC.sh`, WorkDir canonical `2d-unfolding`. `d1bc8813` driver has no estimator or seed option and imports a helper whose only learner is sklearn `GradientBoosting*` (helper at `d1bc8813`, lines 3, 152–156). The backend switch arrived in `baa0a76f` (05-19 14:38), after the job ended | yes (evidence class as A states; runtime helper bytes unavailable) | git, sacct | read |
| coverage at κ = 1 with σ̂(300): I68 / I95 | 0.68188 / 0.94907 | 0.681881 / 0.949071 (exact Student t, 299 df) | yes | — | rc_assurance |
| edges (κ = 1.25, 0.80), σ̂(300) | I68 [0.5757, 0.7877]; I95 [0.8821, 0.9851] | [0.57565, 0.78772]; [0.88205, 0.98514] | yes | — | rc_assurance |
| N_required (206 × 2, α_t = 0.04/412, β = 0.10, stable N..N+100) | **719** | **719** (first N without the window: 690) | yes | — | rc_assurance |
| acceptance at 719 | I68 [441, 539]; I95 [658, 703] | identical | yes | — | rc_assurance |
| pass prob. at edges (κ 1.25/0.8) | I68 0.022/0.008; I95 0.0025/0.075 | 0.0220/0.0080; 0.00255/0.0752 | yes | — | rc_assurance |
| familywise (union) nominal / κ = 1 with σ̂ noise | ≥0.969 / ≥0.968 | 0.9692 / 0.9681 | yes | — | rc_assurance |
| bias N (z_crit 4.0625, power 0.9, 0.2σ) κ = 1 / 1.25; power at 719 | 714 / **1,116**; 0.90 / 0.59 | 714 / 1,116; 0.903 / 0.590 | yes | — | rc_assurance |
| N_design acceptance; familywise | I68 [700, 822]; I95 [1030, 1086]; ≥0.967 | identical; 0.9673 | yes | — | rc_assurance |
| OC at κ = 0.9 / 1.1 | 0.84–0.92 | I68 0.859/0.903; I95 0.918/0.838 | yes | — | rc_oc |
| N sensitivity (I68+I95 / I68) | 1,657/1,248; 975/755; 719/519; 504/330; 329/172 | identical **for the bounds B coded** ([0.87,1.15], [0.83,1.20], …). For the exact [1/x, x] that §10 states: x = 1.15 → 1,632/1,248; x = 1.20 → **1,030**/755 | values yes, label no (F7) | — | rc_assurance |
| deterministic edge cases | B: 44 self-tests | binomial n=10, p=0.5, α=0.05 → [2, 8]; n=1 → [0, 1]; t(10⁷) → normal to 2e-8; P(2σ) 0.9545 ≠ 0.95; full-range p_in = 1 | yes | — | rc_assurance |
| C's 4-case family (824 functionals) N / design N | 823 / 1,250 | 823 / 1,250 | yes | — | rc_assurance |
| finite-reference offset (ρ = 0.5, s = 0.25–1): expected coverage / bias failures of 206 | 11–103 / 108–154 | 11.4–103.2 / 108.2–154.2 (closed form 2Φ̄(z/√(Nτ²+1)) agrees). Note: an 80-node Gauss–Hermite rule gave 150.9; the integrand steps on a 1/(τ√N) scale | yes | — | rc_assurance |
| per-run node-h, billing/256 | 0.0591 (shared replica); 0.0708 (KI-85) | 0.059147; 0.070758 (0.069969 over the 98 non-pilot runs). Iris deltas 17.9 vs sacct 18.11 and 6.4 vs 7.08 agree with billing/256; CPUs/128 would give 35.5 and 14.2 | yes | sacct_all, sacct_ki85, budget.json | rc_costs |
| B primary 719 × 301 × 1.05; design 1,116; P-floor 172; B50; S; N1 | 13,440; 20,862; 3,215; 2,277; 45; 6,720 | 13,440.5; 20,861.8; 3,215.2; 2,277.3; 44.7; 6,720.3 | yes | same | rc_costs |
| B N2 = 100 × 0.0708 × 1.05 (+R0 0.4–2.3) | 7.4 (7.8–9.7) | 7.43 (7.83–9.73) | yes | same | rc_costs |
| C P2 optimistic (5,000 exp.) by hand | 575.239 | production 345.735; verification 0.05 × (prod + setup) 21.218; retry 0.02 × (prod + setup + dev) 8.607; subtotal 460.191; /0.8 = 575.24 | yes | costs.json operands | by hand |
| C P2 conservative | 3,517.95 | per exp. 0.216111 × 1.5 + 0.05 = 0.374167; 1,870.84 + 468.97 + 6 + 233.98 + 234.58 = 2,814.36; /0.8 = 3,517.95 | yes | same | by hand |
| C P1 optimistic per experiment / admitted | 43.167 / 288,793 | 311 × 0.059147 + 187 × 0.132419 + 0.01 = 43.167; 215,835 + 78.63 + 6 + 10,795.7 + 4,318.4 = 231,034; /0.8 = 288,793 | yes | same | by hand |
| C setup (S-r, S-a, S-j, sum) | 2.8125, 24.82, 35.84, 78.63 | 12 × 2.5 × 24/256 = 2.8125; 187 × 0.132419 + 0.059147 = 24.82; 3 × 202 × 0.059147 = 35.84; sum 78.63 | yes | same | by hand |
| C `E_C` branch, optimistic / conservative | 5,566 / 263,513 | 0.68 enters every c_cv term: S-a 25.44, S-f 136.0, S-j 412.1, setup 579.7, production 3,450, verif. 201.5, retry 80.7 → 5,397.3; + 198 × 0.68/0.8 = 168.3 → **5,565.6**. Conservative: 258,733.8 + 198 × 19.3119/0.8 = **263,513.5** | yes (see F9) | same | by hand |
| exact unfold unpacked / packed | 19.31 / ~0.68 node-h | 69,523/3,600 × 256/256 = 19.312; by memory 487,802 MB/16.39 GB → 29 jobs per node → 0.666 | yes (packing contention unmeasured) | sacct 53116554 | rc_costs |
| m3246 remaining | 3,040.6 node-h | 20,000.0 − 16,959.4 = 3,040.6, from B's recorded iris read (`b/remote-reads-20261009.txt` §2). Not re-measured (iris is outside my permitted reads) | arithmetic yes | B record | — |
| KI-84 regression + provenance tests | 14/14 | 14/14 (PyROOT 6.36, python3.13), exit 0 | yes | review tree | — |
| hash bindings | ALL BINDINGS INTACT | `verify_hash_bindings.py --root .` exit 0, `ALL BINDINGS INTACT`; the driver's two pins are `known pre-existing drift` | yes | review tree | — |
| k0 separated roots + flux-universe fix | 4/4 + 51/51 | 55/55 OK | yes | review tree | — |

## 3. Findings (most severe first)

**F1 — MATERIAL (next decision). The lanes name different next decisions, and the integration has
not reconciled them.**
- B FINAL: lift the KI-85 deferral for N2 (DESIGN §17, lines 496–499).
- C FINAL: "the central estimator (stage 0). Nothing downstream is admissible before it", and "the
  same for B and C" (ASSESSMENT-total line 531; §8 stage-0 row).
- A: which estimator a validation targets, options (a)/(b)/(c) (ASSESSMENT-pairing §7).

These compose without contradiction only once they are scoped. N2 is defined on `E_S` (DESIGN
§16.1), so admitting it presupposes A's option (a), "`E_S` only, stated as not covering the quoted
central". C's "nothing downstream" holds for claims about the uncertainty attached to the quoted
central or the total, not for an `E_S`-labeled diagnostic, which the plan allows (plan line 177).
- *Repair (E / B / C):* state one composed next decision. First, Joseph's stage-0 scope choice, which
  costs 0 node-h for option (a). Then, only if (a) is chosen, the KI-85 lift for N2. C should scope
  "nothing downstream is admissible" to `E_C`-attached and total claims. B should name option (a) as
  N2's premise.

**F2 — MATERIAL (quotable claim). B quotes C's superseded `E_C`-keeping cost.** DESIGN §2 item 1,
line 99: "C puts the cheapest `E_C`-keeping validation at 152,000–259,000 node-h (`d07a3d33`)". C's
FREEZE `803f1dcc` §6 gives **5,566 (A's packed rate) – 263,513** node-h. The same B sentence already
quotes A's ~0.7 node-h packed rate, which is what produced C's lower figure, so the sentence
contradicts itself. B froze one minute before C (`00f7cff1` 23:59:22, `803f1dcc` 00:00:26). Neither
lane re-read the other's final.
- *Repair (B):* cite C FREEZE `803f1dcc` (5,566–263,513, for C's 4-case fixed-band P2) or drop the
  figure. B's verdict does not depend on it.

**F3 — MATERIAL (quotable claim; affects how E labels the terminal). B treats the m3246 balance as a
ceiling on all work.**
- DESIGN §1 ground 2 (lines 55–60) says "unaffordable at the resource ceiling". §14 line 423 calls
  3,040.6 node-h "an upper bound on what any admission could give". §17 compares against it.
- The 3,040.6 figure is a measurement, but only of one thing: a point-in-time balance of a shared,
  allocation-year-bound CPU project pool (iris read at 06:15:10Z). It does not bound what an admission
  could give. The same iris read records a user allocation (10,000, 2,035 charged) and a GPU project
  `m3246_g` with 180,000 − 124,893 = **55,107** remaining, which B does not mention. The pool renews
  each allocation year, and additional allocations can be requested.
- The plan defines no resource ceiling, and it tells C not to carry historical balances forward
  (plan line 129).
- B's NO-GO stands on ground 1 alone (populations).
- *Repair (B):* restate ground 2 as a priced cost with the measured comparator: 13,440–20,862 node-h,
  that is 0.67–1.04 × m3246's entire annual CPU allocation and 4.4–6.9 × its 2026-10-09 remainder,
  unadmitted. Do not call the remainder a ceiling. E should then terminate the primary as INFEASIBLE
  on the population obstacle, with cost as a supporting, not demonstrated, constraint.

**F4 — MATERIAL for any named next step that runs a new or modified producer (engineering gate).
The OI-136 ratchets are red at the pin, and no route repairs or classifies the nine October sites.**
- Measured: `test_oi136_rooted_insert_ratchet` fails `test_no_file_outside_the_named_set…` with 9
  extra sites. `test_oi136_failopen_inventory_ratchet` measures 18 files / `04357e1a…` against the
  recorded 9 / `0939e159…`. The failure lists are byte-identical at `ad2716d8`, `33811d7d` and
  `cd0da202`. They are pre-existing, and no lane caused them. The nine files postdate the 2026-09-03
  authorization. That authorization covered a fixed population (45 files measured at `71839696`:
  36 repaired, 9 classified). It neither repairs nor classifies these nine.
- Consequences, practical rather than theoretical:
  - (i) A red ratchet cannot detect a tenth site, so its protective function is suspended for every
    change.
  - (ii) `fixed_truth_toy.py:157–158` loads `omnifold.py` from the canonical cluster checkout whatever
    tree launches it. It calls `ohf.omnifold` directly, not driver `main()`, so A's new provenance
    records (`971fc00c`) are not written for toy outputs. B §12's release condition, "every output
    records … the sha256 of the OmniFold helper actually imported", therefore does not hold for a
    toy-pattern harness.
  - (iii) Per authorization §2, `mnv_guarded_run.py` is the accepted door, and the queue refuses
    compute whose producer does not route through it.
- *Repair (control-plane / OI-136 owner, via Joseph; not a lane):*
  - classify the seven receipt files as records, with ratchet constants updated in one commit naming
    each site;
  - decide repair or classification for the two live producers (`fixed_truth_toy.py`,
    `ki85_compare.py`);
  - meanwhile, any next experiment's request must name the guarded launch and helper-digest capture
    for every producer it uses.

**F5 — MINOR. B's §7 "fails by construction" is reproduced numerically but scoped more broadly than
shown.** At N = 719 an exactly calibrated procedure is expected to fail:
- coverage: 4.5–153 of 206 functionals across all nine (ρ, s) rows;
- bias: 94–166 of 206.

So the claim holds for a coverage-plus-bias test that treats `T_R` as exact, at every scanned point.
The bias test fails for any s ≳ 0.05 (at s = 0.05, τ = 0.105 gives about 36 expected failures).
However:
- τ is an upper-bound model with s unmeasured. s is a deterministic property of the response,
  computable without training.
- The plan asks to "quantify finite-reference uncertainty … rather than treating a finite reference
  as exact" (line 115). B uses τ as a disqualifier and does not model it into the criteria.
- A truth-free per-experiment κ test (sd of U_e − Ū against σ̂) avoids the offset. It is unpriced.
- Separately, N1 as described keeps the bank fixed while (apparently) keeping both inner streams. The
  outer scatter would then lack the MC-stream term, which forces κ < 1 by construction. N1 does not
  specify that its inner bootstrap is data-only.

*Repair (B):* say "fails as specified (`T_R` treated as exact, 0.2σ bias test)". Name the
reference-aware and truth-free variants as unpriced. State N1's inner-stream choice. The verdict is
unchanged.

**F6 — MINOR. B says "no assumption differs between the lanes" (§14, line 435); C §9 lists four
differing assumptions (retry/reserve, rate, family, R0).** The practical effect is that B's N2 figure
(7.8–9.7 node-h) carries no protected 20 % reserve and no verification re-run. Under C's convention
it is about 9.8–12.2 node-h. *Repair (B):* replace the sentence and quote N2 with the reserve the plan
requires for any proposed allocation.

**F7 — MINOR. Mislabelled sensitivity table.** DESIGN §10 line 327 says "κ ∈ [1/x, x]", but the code
uses [0.87, 1.15] and [0.83, 1.20]. Exact reciprocals give 1,632 (not 1,657) and 1,030 (not 975).
*Repair (B):* relabel the table or recompute it.

**F8 — MINOR. C overstates the transfer as a disproof.** ASSESSMENT-total line 43: "the band, the
systematics and the ML block do not describe `E_C` (`P02`, `P04`, `P09`)". The DISPROVED rows show
that these blocks were not produced by `E_C`. Whether they describe `E_C`'s uncertainty is `P03`/`P05`,
which are UNRESOLVED. *Repair (C):* "were produced by LightGBM, not by `E_C`; their transfer to `E_C`
is unmeasured (`P03`, `P05`)".

**F9 — NOTE. Inconsistencies inside C's `E_C` branch.**
- (a) The LightGBM matched sweep S-a (about 25 node-h) stays in setup while an exact matched sweep is
  added: a small double count.
- (b) Exact universe unfolds are priced at the CV rate (0.68). For LightGBM, C itself applies a 2.24
  universe I/O ratio. Consistent treatment would raise the one-time exact rebuild from about 135 to
  about 290 node-h (optimistic).

Neither changes a disposition.

**F10 — NOTE. A's `P09` outcome label conflates two propositions.** "C_ML as the ML uncertainty of
`E_C`: DISPROVED". The evidence (5.1 σ_ML offset) disproves the "conservative cross-estimator proxy"
reading. It does not disprove the transfer of seed noise, which is unmeasured, like `P03`/`P05`. sklearn
`GradientBoosting` with `subsample = 1.0` and `max_features = None` draws randomness only from
split tie-breaking, so `E_C`'s seed noise may be near zero. *Repair (A):* split the row into
"same-estimator DISPROVED" and "seed-noise transfer UNRESOLVED", or reword the outcome.

**F11 — NOTE. A item now closable.** A lists the product-level Flux rescale as not re-derived
(verification §8; assessment §6). I verified it exactly (§2 above).

**F12 — NOTE. `971fc00c` provenance records.**
- The helper and driver sha256 are read at write time (end of `main()`), not at import time. A
  canonical-checkout edit during a long run would be recorded as the executed bytes.
- Every argparse type is str/int/float/bool, so `json.dumps(vars(args))` cannot raise.
- Histogram preservation: the bit-identity class passes (14/14).
- The rooted insert stays in `main()`, and the ratchet arm passes.
- Hash bindings are intact.
- No tracked consumer is broken by the new keys. The only `GetListOfKeys` loops, in
  `plot_uncertainty_fig6_7_style.py:127` and `publication/w2/compare_omnifiles.py:40`, filter by
  name or class and read other files. `reproduce_from_durable.sh` symlinks the existing product and
  does not rerun the driver.

*Repair (A, optional):* hash at import.

**F13 — NOTE. D citation precision.**
- `2D_OMNIFOLD_REFERENCE.md:122–127` attributes "omnifold.py keeps its digest" to the ruling at
  `AUTHORIZATION…:41`. That line reads "sha pinned in three places", which most naturally means the
  driver's sha. The helper-digest condition is in the plan (line 18) and the ratchet
  (`test_oi136_rooted_insert_ratchet.py:266–274`).
- The reference says the ratchet "fails if either condition breaks" but does not mention that the
  suite is already red (F4). A raised both points; D did not adopt them.
- *Repair (D):* cite both sources and add the red-at-pin caveat.

Pending E-surface item, not a lane defect: the `2D_OMNIFOLD_STUDY_STATUS.md:45` headline "MEFHC 5-iter
lgbm" is still wrong for the central product.

## 4. Scrutiny items

**(a) Estimator identity versus covariance transfer.**
- A keeps "DISPROVED same-estimator" (`P02`, `P04`) distinct from "transfer UNRESOLVED" (`P03`, `P05`,
  `P07`). ASSESSMENT §8 says explicitly that this "does not show that the quoted uncertainty is
  numerically wrong for `E_C`".
- B §2 and §17 ("claim reach") keep the distinction.
- The plan's FAIL wording ("a pairing is disproved", line 99) is satisfied by `P02`, `P04` and `P09`,
  and A applies it as written. It is not an overstatement.
- Two overstatements exist: C line 43 (F8) and A's `P09` label (F10).
- I found no understatement. D's reference (lines 232–235) states the backend split.
- The rubric row "Disproved match: NOT READY" does not block an `E_S`-scoped step, because the
  pairings that step needs (`P10`, `P11`) are VERIFIED. It does block any claim about the uncertainty
  of the quoted central.

**(b) B's population requirements versus its NO-GO.**
- The requirements are the plan's own. The plan text requires independently constructed template
  realizations or a validated generative law (line 113), event keys with namespaces and duplicate
  checks (line 111), and termination on unavailable production-equivalent populations (line 115).
- They also follow from the statistics. Testing the MC stream needs many independent bank
  realizations, because the experiment is the sampling unit. A K-way split of one 4.708 D production
  gives at most K banks at MC/data 4.708/K, which tests a different operating point.
- Disjoint (production bank + D reservoir) sets = ⌊4.708/5.708⌋ = 0. I verified this.
- The NO-GO is justified for the named primary experiment and correctly scoped "with the populations
  and resources that exist".
- Ground 2 is overstated (F3). The §7 wording is broader than what was computed (F5).

**(c) Costs of specified designs versus claims about all possible designs.**
- Neither lane claims infeasibility for designs it did not price. B lists the narrower designs (§16)
  and C classifies only P1, P2 and P3.
- The one overreach is B using the m3246 remainder as "the resource ceiling" and "an upper bound on
  what any admission could give" (F3).
- C states the balance is "not a resource C carries forward". C's P1 "INFEASIBLE: demonstrated
  unaffordability" (0.29–1.21 M node-h, 14–60 × the annual allocation) is defensible, but it also
  names no comparator. It should state "relative to m3246's annual 20,000 CPU node-h".
- Unpriced alternatives worth naming:
  - fewer functionals (Bonferroni lowers N only logarithmically);
  - a truth-free κ test;
  - a GPU-node or next-year pool.

**(d) OI-136 ratchets.**
- I read both files and the probe first. They are AST walks, a `grep -rl`, `git ls-files` and
  synthetic fixtures, with no training and no network. Both suites are red: 2 failures each, at the
  review tree, the pin `ad2716d8` and upstream main `33811d7d`, with identical failure lists. They are
  pre-existing, and no lane caused them.
- Practical consequences: see F4.
- Who may repair or classify: the 2026-09-03 authorization records Joseph's grant for a measured
  45-file population only. Its §2 scoping belonged to the integration lane of that date. The nine
  October sites need a new decision under the OI-136 route. Seven of them are receipts, which must be
  classified, never edited. The plan forbids lanes from editing OI rulings or frozen receipts, so
  only the control-plane owner can do this, with Joseph's ruling.

**(e) B-final versus C-earlier consistency.**

| site | B says | C FREEZE says | material? |
|---|---|---|---|
| B §2 line 99 | `E_C` keep 152,000–259,000 (`d07a3d33`) | 5,566–263,513 | **yes** (F2, quotable) |
| B §17 / C line 531 | next decision: KI-85 lift for N2 | stage 0 first; "nothing downstream" | **yes** (F1) |
| B §14 line 435 | "no assumption differs" | four differing assumptions (§9) | no, but the N2 reserve is missing (F6) |
| B §14 per-experiment 17.8–65.1 (`9204a390`) | — | same at FREEZE §9 | no |
| B R0 0.4–2.3 / 2.8–27.0 (`d07a3d33`) | — | same (S-r) | no |
| B 719/1,116, 13,440; C 823/1,250 | — | same | no (my recomputation agrees) |
| C cites B PROVISIONAL §1/§17 (populations) | B FINAL identical in substance | — | no |
| B "For E": `P02` versus `P03` label | — | C FREEZE uses A's FREEZE ids | resolved |

## 5. Rubric assessment and terminal

| gate | assessment (for the primary B experiment / for N2) |
|---|---|
| Current authority and baseline | PASS. One pin. The upstream delta `33811d7d` is publication-only. The ratchet failures are identical across it |
| Estimator identity | Primary and N2 under `E_S` scope: PASS (`P10`, `P11` VERIFIED; executed bytes of the VL170 driver via the HEAD guard; helper runtime bytes unavailable). Any `E_C`-attached claim: NOT READY (`P02`/`P04`/`P09` disproved, `P03`/`P05` unresolved) |
| Engineering behavior | KI-84 regression and negative control PASS, shared callers PASS, bindings intact. OI-136 ratchets red and unrouted (F4). The N2 producer tooling (R0 checker, split manifest, fold writer, C1–C7) is unbuilt by design (B §13). **NOT READY** for N2 execution |
| Population independence | Primary: **no-go** (0 production-equivalent sets, no event identity). N2: needs R0 + split + C1–C7, none existing |
| Procedure and claim | Primary well specified. N2 specified to admission level. N1 inner-stream ambiguity (F5) |
| Statistical assurance | Primary: arithmetic independently reproduced in full. N2: precision rests on KI-85 development evidence (about ±6 %), with no formal power calculation |
| Feasibility | Primary: priced, 13,440–20,862 node-h, unadmitted (F3 framing). N2: 7.4 node-h + R0 0.4–2.3 (billing ASSUMED), no 20 % reserve (F6), ESS unmeasured |
| Total-uncertainty boundary | C's dispositions are explicit. Total NO-GO. Any statistical step stays labeled statistical-only and `E_S`-only |
| Supported workflow and preservation | Spot-checked T1, T2, T3 and T4 at `cd0da202`, all reproducible. T4: `git show evidence/simplification-2026-10-07-fc97eaf9:…dev1-CS1-F0.posthoc.json` gives sha256 `d6d09e6f…` = expected, absent on main. D's added paths all resolve. F13 is precision only |
| Independent review and delivery | Material findings F1–F4 are open. All four are wording, reconciliation or ruling repairs. None needs new compute |

**Terminal (my view):**
- **INFEASIBLE UNDER STATED CONSTRAINTS** for "2D repaired-bootstrap independent-population
  per-experiment interval validation". The demonstrated obstacle is populations: no second
  production-size ME-FHC MC, and no event identity. The cost is priced but its unaffordability is not
  demonstrated.
- **NOT READY** for authorizing N2. Named items: F1, F4, F6, the unbuilt R0 and split tooling,
  assumed R0 billing, and the KI-85 deferral.
- Nothing is ready for an `E_C`-attached or total claim.

**Smallest concrete next decision for Joseph:** the stage-0 scope choice, at **0 node-h**.
- (a) Declare that any statistical validation targets `E_S` only and does not cover the quoted
  central, or
- (b) admit A's exact-backend bootstrap at N = 50 (about 34–39 node-h; 0.666 node-h per unfold
  measured-by-extrapolation, packing contention unmeasured), or
- (c) change the quoted central estimator (0 compute; a publication-scope decision).

Only after (a) does N2 become a candidate. It would need the KI-85 lift and a reviewed harness plus
R0, costing about 7.4 + 0.4–2.3 node-h, about 9.8–12.2 node-h with a 20 % reserve.

## 6. Not independently verified

- The runtime bytes of `omnifold.py` for any historical run, and the executed-bytes logs of 53116554,
  the May universe sweep and the seedscan (A records them as absent; I did not re-search).
- PPFX index alignment (Pearson 0.96): no receipt (C's Audit 2).
- The m3246/m3246_g balances: B's iris record only.
- R0 billing (ASSUMED by C).
- Universe-unfold timing (DOCUMENTED only).
- Exact-unfold packing contention.
- Per-bin ESS and the smearing share s (would need the 2.1 GB omnifile, `43f8cc16…`; not copied by
  rule).
- The omnifile tree/branch listing (B's remote read; not repeated).
- C's P1 conservative row: I checked the structure only; I re-derived P1 optimistic and both P2 rows
  fully.

## 7. Resources used

- Wall time 07:15–07:36Z, about 0.4 h.
- Local CPU under 0.05 core-h; the largest step was the 57 s ratchet suite, run three times.
- Peak RSS about 71 MB for the reductions.
- Bytes copied: 41.7 MB tar of products plus 5.5 MB of Flux universes and the flux band (46 MB
  `ops/`).
- Scratch peak 1.3 GB (two archived trees, deleted).
- Remote commands, all read-only, `ssh -o BatchMode=yes -o ControlPath=none saul.nersc.gov`, landing
  on login16:
  - one `ls`/`du`;
  - two `tar c` byte-copies;
  - two `sha256sum` sweeps (598 files);
  - `sacct -j 53116554` (two formats).
- 0 node-h, 0 GPU, no training, toys or jobs. No subagent was spawned and no message was sent.

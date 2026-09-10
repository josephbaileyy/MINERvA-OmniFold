# PACKET 2026-09-10 — Z's declared consumer set, and requirements for the two endpoints

**Author: the `z-criteria-designer` lane (`owners.tsv:14` at `c18f9daa`). DESIGN AND REVIEW ONLY —
adopts nothing, amends nothing, grades nothing, launches no compute. Joseph retains approval.**
Base of measurement **`cebcd995`**. Round table at §2; stopping-rule outcome at §6.

**CITABLE FOR:** the consumer set of §1 and its five additions to the starting list; the
`solve`/`pinv` failure-mode split of §2 and probe §1–3; the endpoint requirements of §3–4; the
`T`-scope analysis of §5.
**NOT CITABLE FOR:** any adopted requirement or tolerance; any claim about real Z eigenvalue
magnitudes (probe §2's magnitudes are **synthetic**; only its sign/exact-zero result is structural);
any revival of the retired universal bound — `rho`, §2.1/§2.2/§2.1b of
`RECOMMENDATION-20260910-…` stand **as history** and are not extended here.

---

## 1. THE CONSUMER SET — verified, and FIVE additions the starting list omits

**Membership rule applied, as directed:** a consumer that is *declared and blocked* is in; a
statistic with no consumer is out.

| # | consumer | what it reads | invert? | endpoint | status |
|---|---|---|---|---|---|
| C1 | `eavail_generator_significance.py:107,132` | projected `C_y`, **full** | `pinv` | **B** | **GATED** (`INTEGRATION_CHECKLIST.md:37`) |
| C2 | `compare_ascencio_fullcov.py:188` | 4D `C_tot`, **full** | ⚠ `solve` | **B** | deferred-declared, `sec_3d.tex:418-419` |
| C3 | `compare_ascencio_fine.py:94` | reduced `C`, **full** | ⚠ `solve` | **B** | same deferral |
| C4 | ➕ `2d-unfolding/compare_to_paper_fullcov.py` | 2D `205²`, **full** | **SVD pseudo-inverse** | **B** | **LIVE and quoted** — the 2D headline (`app_statmethods.tex:707`) |
| C5 | `eavailW_covariance.py:441,466` | **produces** `C_low`; consumes `sqrt(diag)` | — | **A** | band magnitudes quarantined |
| C6 | ➕ `coverage_valid_nd.py` | `sqrt(diag(C))` only | — | **A** | truth-containment diagnostic |
| C7 | `mii_anchor_comparator.py:238` | `sqrt(trace)` from diag | — | **A** | Gate-2 blocked, unquotable |
| D1 | `sec_3d.tex:193`, `:261` | displayed systematic bands | — | **A** | quarantined pending 5D→3D projection |
| D2 | `sec_3d.tex:210` | figure band | — | **A** | *"orientation only and is not final"* |
| D3 | `sec_3d.tex:322` — **note** | 3D generator `χ²` | — | **B** | **deferred-declared** |
| D4 | ➕ `sec_3d.tex:418-419` — **note** | 4D **pulls** and full-cov `χ²` | — | **B** | **deferred-declared** |
| D5 | ➕ `paper_body.tex:146-148` — **paper** | *"A publication-level significance requires the adopted, selection-complete scalar five-dimensional covariance, which is not yet in hand"* | — | **B** | **deferred-declared** |
| D6 | ➕ `primer_body.tex:130` — **primer** | *"Its statistical significance is not assigned"* | — | **B** | **deferred-declared** |

**Five additions, and the first two matter most.**

1. **`C4` is missing and it is the most important omission: the 2D headline consumer is LIVE, and it
   already inverts by SVD pseudo-inverse — ratified at `app_statmethods.tex:53-58`.** So the
   inversion requirement endpoint B needs is not something to invent; **it exists in-tree, is
   ratified, and the N-D consumers do not conform to it.**
2. **`C6` is missing.** `coverage_valid_nd.py` consumes a covariance (`--cov ROOT:hist`) and is a
   genuine consumer — but **diagonal-only**, so it binds to endpoint A and inherits none of B's
   inversion requirements. `SPEC` §3.7d had already named it; the starting list dropped it.
3. **`D4`, `D5` and `D6` are missing, and together they change the shape of the class.** The
   deferred-declared class has **four** members across **three deliverables**, not one in one:
   `:322` defers the 3D `χ²`; `:418-419` defers **4D pulls and full-covariance `χ²`**;
   `paper_body.tex:146-148` defers it again **in the paper's own words**; `primer_body.tex:130`
   defers it in the primer's. See the build measurement immediately below.

**⚠ AND THE DEFERRED CLASS SPANS THREE DELIVERABLES, NOT ONE — measured, and it means one
criterion cannot discharge it.** The intersection of `main_note`, `main_paper` and `main_primer`'s
`\input` sets is **`{values}` alone**: the note carries 19 files, the paper **2** (`values` +
`paper_body`), the primer **3**. **The paper is a distillation that restates the deferral in its own
words and shares no section file with the note, so a note-side criterion does not propagate to it.**
Four deferred sites, three deliverables, **three separate discharges**.

*(My first attempt at that measurement was wrong in this packet's own production: I extracted
`\input{...}` with the character class `[a-z_]*`, which **excludes digits**, so it silently dropped
`sec_3d` — the file carrying half the consumer set. Corrected to `[A-Za-z0-9_]*`. A too-narrow
pattern, producing a false negative, in the measurement of a scope. Fourth time in this campaign.)*

**THREE STATES, CLASSIFIED EXPLICITLY, because *deferred* fails in both directions.** A deferred
consumer whose criterion is never written **silently becomes absent** when the deferral lifts; one
counted as present **inflates the population** a criterion claims to cover.
**LIVE:** `C4` (2D headline, quoted), `D1`/`D2` (bands displayed with magnitudes quarantined).
**DEFERRED-DECLARED:** `C1`–`C3`, `D3`–`D6`. **ABSENT:** no 5D/3D/4D significance exists anywhere —
`PROVENANCE-20260822` §5.

**EXCLUSIONS, BY NAME, so none holds merely because nobody called it.**
- **`nd-unfolding/pet/assemble_ctotal_bkgsub.py:36`** (`build_5d_to_4d_projection`) — **excluded
  deliberately**: PET path, and `AGENTS.md`'s legacy boundary holds it *"cannot satisfy or feed the
  full-event DAG."*
- **`sec_eavailw.tex:63-67`'s *"Generator band"*** — **excluded, and not covariance-derived at all**:
  it is the spread across four generator predictions. **A naive band-sweep would pull it in and
  manufacture a consumer**, which is how an empty population gets inflated.
- **`sec_results.tex:125`, `fig:uqbands`** — a **genuine** covariance-derived band, excluded **only
  because this set is scoped to Z**: it is the **2D** construction, which is `VALIDATED` and complete
  on both central value and uncertainty. **The scoping is stated here rather than left implied.**

**The set does split cleanly along the endpoint line, and the split is by WHAT IS READ:** every
**B** member inverts a full matrix; every **A** member reads a diagonal, a trace, or a displayed
band. **That is the structural basis for keeping the requirement sets apart** — not an
organisational preference.

---

### 1a. The premise the A/B separation rests on — MEASURED, not inherited

**The brief asserted *"A can be released without any significance being quoted."* That is a claim
about the publication, not the code, and it was unverified. Measured:**

- **`paper_body.tex:145-146`: *"Every non-two-dimensional result in this Letter is a central
  value."*** The paper **already** releases every non-2D result with **no covariance-derived quantity
  at all** — no band, no significance.
- **The note already decouples the two**: `D1`/`D2` display bands while `D3`/`D4` defer `χ²` in the
  same file.

**So the premise holds and is a measurement: A-release and B-quotation are already decoupled in both
live deliverables.** What it does **not** establish is that they *should* stay decoupled — that is a
publication judgement, not a code property.

---

## 2. ROUND TABLE

| finding | corrected claim / implementation | decisive test | remaining limitation |
|---|---|---|---|
| **N1 ⚠ `solve` does NOT fail loudly on the covariance class Z belongs to** | Two **B** consumers invert with `np.linalg.solve` (`C2`, `C3`). On an *exactly* singular matrix it raises. **On a NEAR-singular one it returns silently**: probe §1 gives `chi2 = 1.0e18`, no exception, where `pinv` gives `2.0` | probe §1: exactly-singular **raises**; near-singular (`λ_min = 1e-18`) **returns `1.0e18`**; **positive control** §3, full rank `205²`, `solve` and `pinv` agree to `0.0e+00` relative | the failure is a property of the **object's rank**, not of the call. `C2`/`C3` are correct wherever their covariance is full rank; **whether their actual 4D inputs are is UNMEASURED** |
| **N2 A Z-shaped sum has NO exact zeros and a MIXED-SIGN tail** | 44 rank-1 band outer products + `N=100` and `N=24` sample blocks: **0 exact zeros**; the `234` null-space eigenvalues span `−2.301e-13 … +2.068e-13`. So **a PSD test at exactly `0` fails on a correct object**, and *"effective **positive** rank above a cutoff"* is the only well-posed count — which is what the ratified protocol already says | probe §2, with the structural/synthetic split stated in the docstring | ⚠ **only the sign and exact-zero result is structural** (a property of floating-point summation). **The magnitudes, condition number and `chi2` inflation are SYNTHETIC** — the real Z tail scale is unmeasured, and I am not extending the retired machinery to measure it |
| **N3 the inversion requirement already exists and is ratified** | `C4` inverts by SVD pseudo-inverse per `app_statmethods.tex:53-58`; clause (i) at `:645-658` requires the inverse actually used, with its `rcond` or truncation rank, **stated at the point of quotation**. **So endpoint B's inversion requirement is CONFORMANCE, not proposal** | direct reading | **conformance is not calibration.** Making `C1`–`C3` match `C4` makes them well-posed; it does not make their reference distribution correct (§4, F3 unresolved) |
| **N4 the consumer set was incomplete in three places** | §1: `C4`, `C6`, `D4` added | file existence and line reads, each cited in §1 | I searched `nd-unfolding/*.py`, `2d-unfolding/*.py` and `docs/analysis-note/*.tex`. **A consumer outside those three scopes would not have been found** |

---

## 3. ENDPOINT A — covariance and projected-uncertainty release

**Consumers: `C5`, `C6`, `C7`, `D1`, `D2`. All read a diagonal, a trace or a band. None inverts.**
**No tolerance here is `T`, and none inherits `T`'s arguments.**

| requirement | statement | class |
|---|---|---|
| **A-1 construction** | `SPEC` §1.3a's algebra, §1.3b's identity set including the `g^c` reconstruction gate, §3.3's fifteen reject conditions. **Unchanged and not reopened** | FIXED by spec |
| **A-2 provenance** | the four inversion declarations of `app_statmethods.tex:645-658` travel with any released projection **even for a diagonal consumer**, because clause (iv) exists precisely because *"the 5D candidate, its 4D projection and the published 2D block have different ranks"* | CONFORMANCE |
| **A-3 numerical reproducibility** | `r_null = ‖x_cv2 − x_cv‖/‖x_cv‖` over the reported support, `ε = 1e-9`, derived in `RECOMMENDATION-20260910-…` §C.3 from a proven inequality plus Joseph's own declared `REPRO_RTOL_PER_BIN`. **Carried forward unchanged; its falsifier stands** | PROPOSED (unchanged) |
| **A-4 estimator sensitivity** | the **declaration-stability** leg: retained rank and retained-subspace projector gap across members, `‖P_0 − P_k‖_2 <= 1e-8`. **One gate, one tolerance** — the only justified number this lane has, adversarially attacked over ~46,000 trials and survived. Applied **per released projection**, not to the trunk | PROPOSED (unchanged) |
| **A-5 PSD** | ⚠ **must be stated as "no eigenvalue below `−k·λ_max` for a declared `k`", never "PSD" or "λ_min ≥ 0"** — N2 shows a correct object has a mixed-sign round-off tail. `adopt_unified_5d.py:150-165` already uses `ev[0] >= -1e-12*ev[-1]`; the requirement is to make it a **receipt-recorded gate** with `k` declared | PROPOSED, and N2 is why |

**`cause3_corr`'s remaining role — and ⚠ THE BRIEF'S BINARY FORECLOSES THE ANSWER THE EVIDENCE
GIVES.** The brief offered *"retain with a justified criterion, or replace with equivalent scientific
protection."* Both branches presuppose that **some** protection is needed. That presupposition is
*"a requirement carried with no demonstrated need behind it"* — the mirror of a threshold carried
with no claim behind it, and it fails Joseph's own symmetry. **So the prerequisite question is
answered first, and the answer is REPORTED for his ruling rather than acted on.**

**The question:** `cause3_corr` was withheld against one specific hazard — *the adopted statistics
are functions of the diagonal alone, so a `MET` licenses nothing about off-diagonal structure.*
**Does that hazard arise for any declared consumer?**

**Measured against §1, and the answer is asymmetric across the endpoints:**

| endpoint | consumers | do they read off-diagonal structure? |
|---|---|---|
| **A** | `C5`, `C6`, `C7`, `D1`, `D2` | **NO** — `sqrt(diag)`, `sqrt(trace)`, displayed bands. Every one is a function of the diagonal |
| **B** | `C1`–`C4` | **YES** — each inverts a full matrix, so off-diagonal structure enters directly |

**So: the hazard does NOT arise for endpoint A at all, and it arises for endpoint B — whose
population of quoted significances is currently EMPTY (`C1` gated, `C2`/`C3` deferred, `D3`–`D6`
deferred, `C4` out of scope as 2D).**

**REPORTED FINDING, for Joseph's ruling and not adopted here:** on the declared consumer set,
`cause3_corr`'s hazard is **unrealized** — no released consumer reads what it protects. It becomes
live **the moment endpoint B declares a significance (B-1)**, and it belongs to **B**, not **A**.
**That is a third answer to his question rather than a choice between his two**, and the trigger is
checkable against §1 rather than remembered. **A-4 is recommended for endpoint A on its own merits
(estimator-baseline declaration stability), NOT as a replacement for `cause3_corr`** — conflating
them is what the brief's binary would have produced.

## 4. ENDPOINT B — generator significances

**Consumers: `C1`–`C4`, `D3`, `D4`. All invert a full matrix. B's requirements stay out of A.**

| requirement | statement |
|---|---|
| **B-1 the comparisons** | enumerate the `(generator, projection)` pairs a significance will be quoted for. **Currently: none is quoted** — `C1` GATED, `C2`/`C3` deferred, `D3`/`D4` deferred; `C4` is quoted and is 2D, outside Z's scope. **So B's population is currently EMPTY, and that is the honest starting state** |
| **B-2 inversion procedure** | **conform to `C4`'s ratified SVD pseudo-inverse pattern** (`app_statmethods.tex:53-58`) and declare, per quotation, all four of clause (i)–(iv): the inverse actually used with its `rcond` or truncation rank, the **retained rank as `ndf`**, the rank-truncation scan, and which covariance is meant. ⚠ **N1 makes this urgent for `C2`/`C3`**: `solve` on a rank-deficient input returns a silently absurd `χ²` |
| **B-3 `ndf` conformance** | `eavail_generator_significance.py:132` passes the **bin count** where clause (ii) mandates the **retained rank**. A **code-conformance defect against ratified protocol**, not a criterion to propose. Fixing it **increases** reported significances wherever retained rank `<` bin count — a change with a known **sign**, whose reading as *correction* versus *loosening* depends on the rank-based null being accepted, **which the protocol itself says is not established** |
| **B-4 reference distribution** | ⚠ **UNRESOLVED and I cannot resolve it.** Clause (v) requires per sample-covariance block: `N`, the normalization convention, the effective `p` after truncation, and the finite-ensemble treatment **or an explicit statement that none was applied**. Operands measured: `N = 100` (`sbatch_bootstrap_5d_gpu.sh:5`), `N = 24` (`sbatch_seedscan_split_5d.sh:5`). **No generic factor is available** — `OI-137` rules *"disclose, do not correct"* and the protocol's stated reason applies here unchanged. **What I recommend: record `N` beside each block and state explicitly that no treatment was applied.** What I cannot supply: the bias magnitude on a sum of ~45 deterministic rank-one products plus two sample blocks |
| **B-5 sensitivity** | `s_sig = max` over declared pairs × declared offsets of `\|Nsigma_k − Nsigma_0\|`, evaluated **directly on each declared projected object** — `42`-to-`4825` bins, where conditioning is measurable rather than bounded. **No universal bound.** Reinstates `PROPOSAL-20260908`'s C-1 statistic |
| **B-6 compounding** | **B-3 raises significances and B-4's uncorrected bias also inflates `χ²`. Two same-direction effects on one quoted number, neither quantified for Z.** Reason to fix B-3 **and** to quote no significance until B-4 is discharged — `PR-G10`'s own posture |

---

## 5. WHICH CLAIM ACTUALLY NEEDS `T` — and most do not

**`T` was being carried as universal. It is not. Worked out per claim:**

| claim | needs `T`? | why |
|---|---|---|
| *"generator X is disfavoured at `N σ`"* | **YES** | it asserts a decision at a threshold |
| *"here is `χ²`, its `ndf`, the inverse used and its retained rank"* | **NO** | descriptive; every number is declared and none is compared to a boundary |
| *"data lies `7.2 / 9.5 / 15.3 / 21.9 %` below the four generators"* (`sec_3d.tex:219-222`, **live**) | **NO** | central-value ratios; **no covariance is consumed at all** |
| *"data/generator = `1.54, 1.58, …`"* (`sec_eavailw.tex:145`, **live**) | **NO** | same |
| endpoint A's `ε = 1e-9` and `‖P_0−P_k‖_2 <= 1e-8` | **NO, and they must not inherit `T`'s arguments** | one is a reproducibility bound derived from a declared per-bin tolerance; the other a subspace-identity gate. **Neither is a significance threshold** |

**RECOMMENDATION: quote DESCRIPTIVE COMPARISONS WITHOUT A THRESHOLD-BASED CLAIM, and defer any
"disfavoured at `N σ`" statement until a threshold is separately justified.** Grounds: (i) every
**live** generator claim in the note is already ratio-based and needs no covariance; (ii) B-1's
population of threshold-requiring claims is currently **empty**; (iii) B-4 is unresolved, so a
quoted significance would rest on an unjustified reference distribution whatever `T` were. **So `T`
belongs to part of endpoint B only, and it is not on the critical path for anything currently
quoted.**

**Constraints honoured:** no `T` is selected here, from observed results or otherwise; endpoint A's
two tolerances are named and justified separately above and are not `T`.

---

## 6. OUTCOME, AND WHAT I RETURN

**Stopping-rule outcome (3): specific evidence or ruling required.** Not (1) — B-4 is unresolved and
B-1's population is empty. Not (2) — the approach is sound; it is blocked on two named inputs.

**The smallest missing inputs, in order:**

1. **Does the publication intend to quote any generator significance at all?** If no, endpoint B
   reduces to B-2/B-3 conformance and `T` is never needed. **This is one declaration and it unblocks
   or dissolves the whole of §5.**
2. **Clause (v)'s disposition for Z** — record `N` and state that no treatment was applied (my
   recommendation), or commission the assessment the protocol defers to *"the covariance and inverse
   actually adopted"*. **Until then no significance is quotable regardless of `T`.**

**What I could not establish:** the real Z spectrum's tail scale (N2's structural half transfers, its
magnitudes do not, and measuring them is the retired machinery's territory); whether `C2`/`C3`'s
actual 4D inputs are full rank; and the finite-ensemble bias magnitude for this construction.

**Not done, deliberately:** no `rho` probe, no bound variant, no F1/F2 repair. The prior record's
§2.1/§2.2/§2.1b stand as history.

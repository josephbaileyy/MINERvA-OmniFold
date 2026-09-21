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

## 1. THE CONSUMER SET — bounded as stated below, and FIVE additions the starting list omits

> **⚠ THE BOUND, AT THE CLAIM SITE RATHER THAN 146 LINES LATER.** This section does **not** claim
> "the consumer set is complete." It claims exactly: **every file matching an `INVERSION`,
> `COV+DIAG` or `DELEGATION` signature, whose filename or figure stem appears in note, paper or
> primer, has a pinned classification — over a population of 913 files whose count is verified
> per extension against `git ls-files`.** Five things that does not establish are in §2b, and the
> signature set has already grown twice under adversarial pressure.
>
> *Rev. 1 headed this section "verified" and put the bound in §2's round table at `:163`. A reader
> entering at §1 — where the claim is made — got no qualification. **That is the same shape as an
> instrument printing a meaning claim its own docstring disclaims: the caveat exists and does not
> travel with the verdict.** Sixth instance in this campaign, and predicted.*

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
| C8 | ➕ `3d-unfolding/genie/compare_3d_fullcov.py:105-110` | 3D full cov | truncated eigen | **B** | **QUARANTINED** — ⚠ **CONFORMING: `keep = evals > tol*lmax`, returns `int(keep.sum())` as `ndf`.** Clause (ii) implemented |
| C9 | ➕ `3d-unfolding/genie/overlay_generators_band.py:26,232` | band **and** `χ²` tension | `ndf = nbins` | ⚠ **A+B** | **QUARANTINED** — non-conforming, and **it breaks the per-script partition** |
| C10 | ➕ `3d-unfolding/genie/overlay_eavailW_band.py:88-108` | `(E_avail,W)` band | — | **A+B** | **QUARANTINED**; cited by `sec_eavailw.tex:71` — **the unsearched tree feeds a deliverable** |
| C11 | ➕ `2d-unfolding/uq/_ours_only_chi2.py:128-130` | 2D full cov | `np.linalg.inv` | **B** | **LIVE (2D)** — non-conformer on `ndf` (bin count); `inv` is **correct at full rank** per N2's control |
| D5 | ➕ `paper_body.tex:146-148` — **paper** | *"A publication-level significance requires the adopted, selection-complete scalar five-dimensional covariance, which is not yet in hand"* | — | **B** | **deferred-declared** |
| D6 | ➕ `primer_body.tex:130` — **primer** | *"Its statistical significance is not assigned"* | — | **B** | **deferred-declared** |

**Five additions, and the first two matter most.**

1. **`C4` is missing and it is the most important omission: the 2D headline consumer is LIVE, and it
   already inverts by SVD pseudo-inverse — ratified at `app_statmethods.tex:53-58`.** So the
   inversion requirement endpoint B needs is not something to invent; **it exists in-tree, is
   ratified, and the N-D consumers do not conform to it.**
   **⚠ AND THE PRECEDENT COUNT IS TWO NUMBERS, NOT ONE — the distinction carries B-2 and a single
   figure does not.** **Ratified precedent = 1:** only `C4` is named in the note as the pattern.
   **Implemented pattern = 2:** `C8` implements it (retained rank as `ndf`) but is **not named** in
   the note — its sole deliverable appearance is a figure stem at `sec_3d.tex:231`. **B-2's claim is
   conformance to a RATIFIED pattern, so the number that carries it is the smaller one.** *(A
   relayed count of "three" was withdrawn by its own author as double-counting its own finding, and
   the drift ran toward its own argument. I declined it before it was withdrawn, and record the
   distinction rather than either count.)*
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
**LIVE:** `C4`, `C11` (2D, quoted); `D1`/`D2` (bands displayed, magnitudes quarantined).
**DEFERRED-DECLARED:** `C1`–`C3`, `D3`–`D6`.
**⚠ QUARANTINED-BUT-PRESENT — a third state my first version omitted:** `C8`, `C9`, `C10`.
`AGENTS.md` quarantines the historical 3D generator significances, **and these scripts produce
exactly those.** The code exists and runs; the numbers are unquotable. **Omit this state and the
outputs become live when the quarantine lifts, with no criterion ever written for them** — the same
both-directions failure as *deferred*.
**ABSENT:** no 5D/4D significance exists anywhere — `PROVENANCE-20260822` §5.

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

**THE SPLIT IS BY REQUIREMENT TYPE, NOT BY SCRIPT — ⚠ AND MY FIRST VERSION CLAIMED OTHERWISE.**
It read *"the set does split cleanly along the endpoint line."* **False per script:** `C9`
`overlay_generators_band.py` is simultaneously an endpoint-**A** band consumer and an endpoint-**B**
tension consumer — its own docstring says *"WITH the full systematic (+stat+ML) uncertainty band,
and quantify the data-model tension per axis with a COVARIANCE chi^2"* — and `C10` is the same
shape. **So a criterion scoped to A alone does not reach a dual script's B half.** What remains true
is the split by **what is read**: every **B** requirement attaches to a full-matrix inversion, every
**A** requirement to a diagonal, trace or band. **Requirements partition; scripts do not**, and a
dual script takes both sets. That is a structural constraint on the split, not a missing row.

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
live deliverables.** ⚠ **And the qualification is carried verbatim, because it is the part that
decays: this establishes that the endpoints ARE decoupled TODAY, not that they should stay so — and
a later decision to quote a band with a significance beside it would RECOUPLE them without anyone
editing a criterion.** Nothing in the A/B split detects that; only a re-run of §1 would.

---

## 2. ROUND TABLE

| finding | corrected claim / implementation | decisive test | remaining limitation |
|---|---|---|---|
| **N1 ⚠ `solve` does NOT fail loudly on the covariance class Z belongs to** | Two **B** consumers invert with `np.linalg.solve` (`C2`, `C3`). On an *exactly* singular matrix it raises. **On a NEAR-singular one it returns silently**: probe §1 gives `chi2 = 1.0e18`, no exception, where `pinv` gives `2.0` | probe §1: exactly-singular **raises**; near-singular (`λ_min = 1e-18`) **returns `1.0e18`**; **positive control** §3, full rank `205²`, `solve` and `pinv` agree to `0.0e+00` relative | the failure is a property of the **object's rank**, not of the call. `C2`/`C3` are correct wherever their covariance is full rank; **whether their actual 4D inputs are is UNMEASURED** |
| **N2 A Z-shaped sum has NO exact zeros and a MIXED-SIGN tail** | 44 rank-1 band outer products + `N=100` and `N=24` sample blocks: **0 exact zeros**; the `234` null-space eigenvalues span `−2.301e-13 … +2.068e-13`. So **a PSD test at exactly `0` fails on a correct object**, and *"effective **positive** rank above a cutoff"* is the only well-posed count — which is what the ratified protocol already says | probe §2, with the structural/synthetic split stated in the docstring | ⚠ **only the sign and exact-zero result is structural** (a property of floating-point summation). **The magnitudes, condition number and `chi2` inflation are SYNTHETIC** — the real Z tail scale is unmeasured, and I am not extending the retired machinery to measure it |
| **N3 the inversion requirement already exists and is ratified** | `C4` inverts by SVD pseudo-inverse per `app_statmethods.tex:53-58`; clause (i) at `:645-658` requires the inverse actually used, with its `rcond` or truncation rank, **stated at the point of quotation**. **So endpoint B's inversion requirement is CONFORMANCE, not proposal** | direct reading | **conformance is not calibration.** Making `C1`–`C3` match `C4` makes them well-posed; it does not make their reference distribution correct (§4, F3 unresolved) |
| **N4 the consumer set was incomplete in three places** | §1: `C4`, `C6`, `D4` added | file existence and line reads, each cited in §1 | superseded by **N5** |
| **N5 ⚠ MY DECLARED SCOPE COVERED 25% OF THE POPULATION, and it is where I said to look** | `nd-unfolding/*.py` and `2d-unfolding/*.py` are **non-recursive** and `3d-unfolding/` was absent entirely: measured **136 of 541** tracked `.py` files at `054e4d66`. ⚠ **That denominator is dated on purpose: `git ls-tree` gives `541` at `054e4d66` and `542` at `42d5e5e3`, the added file being the instrument itself, which is why the tool prints `542` and this row says `541`. Rev. 1 quoted the earlier number as if current, so the page disagreed with its own tool** — the instrument does **not** self-exclude. The 405-file remainder held **four consumers** (`C8`–`C11`) — one **conforming**, one that **breaks the partition**, one that **feeds a deliverable from the unsearched tree** — and `pet/assemble_ctotal_bkgsub.py`, which the prior record required be excluded **by name**. **An exclusion you cannot state because the file is outside your search is not an exclusion.** | `state/check-consumer-set-20260910.py` — scope as a **population** verified against an independent `git ls-files` count, not a directory guess; `--self-test` fires on a deliverable-cited consumer, treats an uncited one as census, and is silent on innocent prose | **the SIGNATURE SET is the irreducible residue** — no instrument certifies its own signature list (§2b) |
| **N6 ⚠ TWO MORE CONSUMERS, AND THE MECHANISM WAS MISFILED AS THE CITATION TEST'S BLIND SPOT** | `3d-unfolding/genie/compare_mec_eavail.py` and `mode_decomp_eavail.py` both read `uq_universe_3d_covariance.root` and both have products in `sec_3d.tex` (`:357`, `:348`). They were filed as limit **(b)**, the citation test missing a figure stem. **Measured: each has `0` occurrences of `np.linalg.pinv\|inv(\|solve\|keep.sum()` and `0` of `np.diag\|np.trace`. They were never CANDIDATES, so no citation test could have reached them — this is limit (a).** They call `load_cov`/`project_cov`/`build_projectors` **imported from a registered consumer**, so the consumption is not syntactically local | a **DELEGATION** signature was added — importing a registered consumer's machinery makes you a candidate, so the registry is self-propagating. Both now detected via `DELEGATION` and pinned. The **stem** test was added too, closing (b) independently | **the class is "delegates covariance handling to an import", and delegation is transitive.** The signature covers one hop — a file importing a file that imports a consumer is not caught |

---

### 2b. THE IRREDUCIBLE RESIDUE — what no version of this instrument can certify

**Five residues, not four — the fifth is the population's language boundary, added in round 8.**
**And the signature set is now three, not two:** `INVERSION`, `COV+DIAG`, and — added after N6 —
`DELEGATION`. **Each addition was forced by a consumer the previous set could not see**, which is
the honest way to read the sequence: the set grew twice under adversarial pressure and there is no
argument that it has stopped growing.

**What cannot be certified, stated once rather than implied:**

1. **No instrument certifies its own signature list.** A consumer that inverts through a wrapper this
   lane has not imagined carries none of the three signatures. **The only defence is that the list
   grows when someone finds one** — which has now happened twice.
2. **`DELEGATION` covers one hop.** A file importing a file that imports a registered consumer is
   not caught. Delegation is transitive; the signature is not.
3. **The citation test covers filename and figure stem.** A file reached only through a **receipt**
   the deliverable cites, or through a product filename differing from its own stem, is still
   invisible. `False` means *not shown to feed a deliverable*.
4. **Counts are not meanings.** As with the withdrawal checker, a pinned entry rewritten in place
   keeps its classification. The `reason` field is what a reader re-checks.
5. **⚠ THE POPULATION'S LANGUAGE BOUNDARY — a fifth residue, and a different failure mode from (1).**
   A consumer in an unscanned language is invisible **by construction**, not by signature — and by
   this packet's own rule it is also **unexcludable**: *a file outside the scanned population cannot
   be excluded by name, because it was never in scope to exclude.* **So the population was WIDENED**
   from `.py + .tex` (566) to `.py .tex .C .cpp .sh` (**913, each extension count pinned and
   verified**), which brought two files into scope to be excluded by name:
   `MINERvA101/…/ExtractCrossSection.cpp` — which genuinely populates an unfolding covariance via
   RooUnfold at `:83-97`, and is the **vendored reference framework**, not a consumer of Z — and a
   shell wrapper whose own filename contains *"covariance"*.
   **⚠ BUT WIDENING BOUGHT EXCLUDABILITY, NOT COVERAGE, AND THAT IS MEASURED.** Two independent
   attempts to signature these languages both failed — **⚠ and NOT in the same way, which rev. 1 of
   this residue wrongly implied.** **This lane's was a FALSE POSITIVE from an uninstrumented token
   set**: it matched the shell wrapper on a filename containing *"covariance"* plus a stray
   `trace(`, and **missed the `.cpp` entirely** — a coverage failure, and one invisible to its
   author, since a miss produces no output to inspect. **The reviewer's was a TRUE POSITIVE
   DISCARDED BY CATEGORY**, which it corrected against itself: it **did** surface the `.sh` — line 2
   of its own printed output — then wrote *"92 non-`.py` files touch a covariance — mostly `.sh`
   launchers"* and moved to the `.cpp` **without checking one of the 92.** A **judgement** failure
   rather than a coverage one, and **by its own reckoning the worse of the two**, because the
   evidence was on screen and was categorised away. *Recorded at its request rather than left as
   the symmetric version that flattered it.* **So the non-Python signature set is declared UNVALIDATED
   in the instrument, and membership for those extensions rests on NAMED REGISTRATION rather than on
   candidacy.** A language absent from this tree remains invisible; `SCAN_EXTS` is chosen from the
   languages present, and widening it is a one-line change plus a re-pinned count.

**So the claim this packet makes about §1 is bounded and should be quoted bounded:** *every file
matching one of three signatures whose filename or figure stem appears in note, paper or primer has
a pinned classification, over a population verified against an independent count.* **It is not
"the consumer set is complete."**

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

> ## ⚠⚠ THE ANSWER BELOW IS WITHDRAWN — REFUTED BY MEASUREMENT 2026-09-10, SAME DAY
>
> **`PACKET-20260910-z-endpoint-A-acceptance-and-cause3-corr-amendment.md` §1 refutes the premise of
> this whole block, and the rows below are kept only so the withdrawal has a referent.**
>
> **The premise was an OPERAND error.** `sqrt(diag(·))` is what these consumers compute — but the
> diagonal they take is the **PROJECTED** object's, and `diag(M C Mᵀ)_i = m_iᵀ C m_i` reads the
> **off-diagonal entries of the source** whenever a row of `M` has more than one nonzero, which
> `project_cov_nd.py:5-8` guarantees (M's rows are width-weighted **sums**). So the hazard **IS
> realized inside endpoint A**, through the projection step.
>
> **Corrected per consumer, because "all of A" would be the mirror error:** **C5 REALIZED**
> (`eavailW_covariance.py:442` projects, `:463` diagonalises); **D1/D2 REALIZED** (`sec_3d.tex:209`,
> `:262` — the released bands are projections); **C6 CONDITIONAL** (reads a stored diagonal, never
> projects itself); **C7 NOT REALIZED** (`_sqrt_trace_from_diag`, genuinely diagonal-only).
> **One cell of five survives.**
>
> **Consequence for the recommendation, and it inverts:** `cause3_corr` does **not** belong to B
> alone, and the deferral this block licensed is **unsound**. See the successor's §3.
>
> *Not corrected in place, because this document is the independent assessor's referent at
> `173baf44`. The withdrawal is stated here so no reader reaches the claim without it.*

**Measured against §1, and the answer is asymmetric across the endpoints:**

| endpoint | consumers | do they read off-diagonal structure? |
|---|---|---|
| **A** | `C5`, `C6`, `C7`, `D1`, `D2` | ⚠ **WITHDRAWN — the stated "NO" is FALSE for C5, D1 and D2.** Was: *"NO — `sqrt(diag)`, `sqrt(trace)`, displayed bands. Every one is a function of the diagonal"* |
| **B** | `C1`–`C4` | **YES** — each inverts a full matrix, so off-diagonal structure enters directly. **This row STANDS** |

**⚠ WITHDRAWN:** ~~So: the hazard does NOT arise for endpoint A at all, and it arises for endpoint B~~
— the first half is refuted. **What survives:** endpoint B's population of quoted significances is
EMPTY (`C1` gated, `C2`/`C3` deferred, `D3`–`D6` deferred, `C4` out of scope as 2D), and under
Ruling 1 of 2026-09-10 **B is DEFERRED, NOT PASSED**.

**⚠ WITHDRAWN FINDING** — ~~on the declared consumer set, `cause3_corr`'s hazard is unrealized; no
released consumer reads what it protects; it belongs to B, not A~~. **Refuted: the hazard is
realized in A through the projection.** `cause3_corr` is now recommended as **endpoint A's own
boundary**, bound to A's own statistic — see the successor's §3.3.
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

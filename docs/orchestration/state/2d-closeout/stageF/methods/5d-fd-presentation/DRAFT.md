# DRAFT, not printed: how the paper and the note would present the 5D fake-data study and its limitation (2026-10-25)

**Asked for by** Joseph (`DECISION-20261025-joseph-f0-limitation-stage-g-and-paper-scope.md` item 1), as relayed by the
director: "I accept the limitation but coordinate with the paper rewriter to make sure its presented in a typical way
for PRD."

**Drafted by** the paper rewrite lane, for the director.

**Status:** a proposal only. It prints in neither document.
- The configuration-(e) five-observable result on the 16 H2 cells R00–R15 is not yet integrated into the paper or the
  note. Integrating it is its own step and needs Joseph's approval of the wording.
- When it is integrated, this draft is the starting point, and it goes through a register round like any other text.
- Nothing here rescales C_model or merges a cell. κ = 1 stands.

**Source of every number:** `state/measurement-paper/5d-community-20261024/FD-F0-REPORT.md` (sha256 `ba779921…`,
§0, §4 and §5.1) and its readout `fd/readout/fd_f0_readout.json`. §6 below checks each number against the report.

**CITABLE FOR:** the proposed presentation and the comparator practice it follows.
**NOT CITABLE FOR:** any result, limitation or claim. Those are FD-F0-REPORT's and Joseph's decision.

---

## 1. How comparable PRD papers present a fake-data or closure study

Taken from the caveat study's corpus (`caveat-study/REPORT.md`, sets P and N); the quotes are verbatim from the arXiv
text.

- **A dedicated, short study with its own setup.**
  - P1 (2504.06857, PRD 112, 012008) states the alternative truth and how it is built: "We create a set of “fake data”
    to serve as the unfolding target by reweighting a subset of the available events in the dataset with a modified
    charged-current quasi-elastic (CCQE) cross section".
  - P2 (2002.12496, PRD 101, 112007) gives one sentence for a warped-MC study: "The results using warped Monte Carlo as
    pseudodata were consistent with the former studies."
- **A χ² per alternative truth against the analysis covariance, read by a stated threshold.**
  - P6 (2102.03346, PRD 103, 112009): "The p-value for each mock data study has been computed from this distribution
    and an acceptance threshold of 5% has been chosen to quantify good fitter performances."
  - The same paper: "All mock data fits return a χ2tot /ndof less than 0.4 … and a p-value greater 80%, showing the
    robustness of the cross section extraction method".
- **A positive-first reading of coverage.**
  - P6: "showing that the model differences are well covered by the conservative systematic uncertainties".
- **When a study is not covered, the long document says so and acts on it.**
  - N1 (2101.03779, PRD 103, 112008): "If a simulated data bias is greater than 50% of the systematic uncertainty on a
    parameter then an additional uncertainty is added to the analysis to account for this."
  - Here the limitation is stated instead: Joseph accepted it, and nothing rescales C_model (decision item 1). Whether
    to assign an uncertainty is decision item 6's plan, not this draft's.
- **Placement.**
  - In set P, untested-or-omitted caveats sit inline, where the result is described (68%), with the principal ones
    restated in the conclusions (8%). No comparator has a limitations list (`caveat-study/REPORT.md` §3.2).
<!-- absence-ok: names the caveat category "untested or omitted" of the caveat study; not a claim that any result is absent -->

## 2. Draft for the paper

These are three pieces. They go where the five-observable configuration-(e) result is described once it is integrated:
the uncertainty discussion of Sec. V, and that result's paragraph.

### 2.1 The fake-data paragraph (validation and uncertainty discussion)

> To test whether the reported uncertainty covers the estimator's bias when the truth differs from the simulation, we
> unfold pseudo-data generated at twelve truths and compare the mean unfolded result with each truth on the sixteen
> reported cells. The truths are the simulation's prior; the five hybrid truths of the generator tests of Sec. VII, each
> a prediction on the fine grid; NuWro shape changes in $E_{\rm avail}$ and in $(p_T,p_\parallel,E_{\rm
> avail})$; a GENIE + MEC shape change in $(E_{\rm avail},W)$; the GiBUU-to-GENIE $E_{\rm avail}$ ratio; a noise-free
> closure at the NuWro shape; and a synthetic tilt of the $q_3$ distribution at fixed $(E_{\rm avail},W)$. For each
> truth, the bias of the mean is compared with the reported covariance through $\chi^2$ with 16 degrees of freedom. For
> a truth from a model that contributes a component of the model-dependence covariance, that component is removed,
> so that no truth is compared with a covariance that includes its own model's dependence. A truth's bias
> counts as not covered by the reported uncertainty when $p<0.01$, or when the pull of any cell satisfies $|z|>2$.
> Table~\ref{tab:fd5d} gives the results (\nsec{…}).

### 2.2 The compact table

| truth | pseudo-experiments | covariance | $\chi^2$ (16 d.o.f.) | $p$ | cells with $|z|>2$ |
|---|---:|---|---:|---:|---|
| simulation (Tune v1) prior | 40 | full | 0.00 | 1.00 | — |
| Tune v1, hybrid | 16 | full | 0.01 | 1.00 | — |
| GENIE 2.12.10 CV, hybrid | 16 | full | 17.37 | 0.36 | — |
| GENIE + MEC, hybrid | 16 | without GENIE + MEC | 16.18 | 0.44 | — |
| GENIE + MEC, $(E_{\rm avail},W)$ shape | 20 | without GENIE + MEC | 0.77 | 1.00 | — |
| NuWro, hybrid | 16 | without NuWro | 29.96 | 0.018 | — |
| NuWro, $E_{\rm avail}$ shape | 20 | without NuWro | 5.69 | 0.99 | — |
| **NuWro, $(p_T,p_\parallel,E_{\rm avail})$ shape** | **20** | **without NuWro** | **36.19** | **0.0027** | **—** |
| NuWro, closure (noise-free) | 1 | without NuWro | 13.08 | 0.67 | — |
| **GiBUU, $E_{\rm avail}$ shape** | **20** | **without GiBUU** | **35.75** | **0.0031** | **R06** |
| **GiBUU, hybrid** | **16** | **without GiBUU** | **246.75** | **$<10^{-30}$** | **R02, R06, R07** |
| **synthetic $q_3$ tilt** | **20** | **full** | **59.83** | **$5.6\times10^{-7}$** | **—** |

**Caption:**
> Fake-data tests of the five-observable result on the sixteen reported cells: $\chi^2$ of the bias of the mean
> against the reported covariance ("full"), or against it without the model-dependence component of the truth's own
> generator. Bold rows are the truths whose bias is not covered: $p<0.01$, or a cell with $|z|>2$. The GiBUU
> $E_{\rm avail}$ shape is the GiBUU-to-GENIE $E_{\rm avail}$ ratio. The per-cell pulls are in \nsec{…}.

*Drafter's note, not draft text:* bold rows are the GiBUU rows, the NuWro $(p_T,p_\parallel,E_{\rm avail})$ row and the
$q_3$ row. The GiBUU $E_{\rm avail}$ shape is the GiBUU/GENIE $E_{\rm avail}$ ratio at full strength (FD-PLAN §1, row 2).

### 2.3 The limitation, stated once, positive-first, where the five-observable result is described (R-P5)

> Measured against the reported covariance, without the model-dependence component of the truth's own model where one
> exists, the reported uncertainty covers the fake-data bias at the simulation's prior and its Tune v1 hybrid, the untuned GENIE truth, the two GENIE + MEC
> truths, and three of the four NuWro truths. It does not cover the bias at the two GiBUU truths, at the NuWro
> $(p_T,p_\parallel,E_{\rm avail})$ shape, or at the synthetic $q_3$ tilt (Table~\ref{tab:fd5d}).

- **Note for the director, not draft text: the qualifier "without each truth's own model component" is required.**
  The declared triggers grade a vertex-family truth against the reported covariance without its own vertex. Against
  the full reported covariance, the in-sample variant, the GiBUU $E_{\rm avail}$ shape gives $\chi^2=29.30$
  ($p=0.022$) with no cell beyond $2\sigma$ (FD-F0-REPORT §5.1). An unqualified "the reported uncertainty does not
  cover the bias at the two GiBUU truths" would be false as read for that truth. agy raised this in round 3. The other
  three listed truths fail under both matrices: W3 in-sample $p=0.0042$, the GiBUU hybrid $5.3\times10^{-30}$, and the
  $q_3$ tilt, which is graded against the full covariance.
- **Note for the director, not draft text:** the decision's wording names the GiBUU-like truths and the $q_3$ tilt. By the declared
  triggers, a fourth truth is also listed: W3, the NuWro $(p_T,p_\parallel,E_{\rm avail})$ shape (p = 0.0027,
  FD-F0-REPORT §0 "W3, by p"). The draft names it, because leaving it out would make the sentence false as read.
- **The words "covers" and "does not cover"** stand for the declared triggers, which the fake-data paragraph defines
  once. FD-F0-REPORT itself draws no conclusion. The covering reading is the director's and Joseph's (decision item 1).

**Nothing else is added to the paper.** The following go to the note:
- the controls;
- the descriptive variants (in-sample, model-only, eight-cell);
- the per-cell pulls;
- the ungraded row-6 truths;
- the matrices' widths.

## 3. Draft for the note

The note keeps the full account, in its five-dimensional validation chapter, as one subsection, "Fake-data tests of the
five-observable uncertainty". Proposed contents, in this order:

1. **The question and the matrices.**
   - Per-cell relative σ on R00–R15, median / min / max:
     - C_e: 6.45 / 4.05 / 8.47 %;
     - C_total: 6.74 / 4.14 / 13.69 %.
   - The leave-own-vertex-out matrices: without GENIE + MEC 6.74 / 4.14 / 13.69 %; without NuWro 6.74 / 4.09 /
     13.49 %; without GiBUU 6.46 / 4.11 / 8.78 %.
   - Why a vertex-family truth is graded without its own vertex (circularity).
2. **The truths and the products.** All twelve graded truths with their pseudo-experiment counts, as in FD-PLAN §1.
   - The six power alternatives (P1r–P3r, P1g–P3g) are shown separately, descriptive and ungraded. Their offset
     correction failed its control: control 7, χ²_16 = 245.74.
3. **The grade.** The §2.2 table with every column of FD-F0-REPORT §5.1:
   - the in-sample, sensitivity and eight-cell variants, labelled descriptive;
   - the model-only lower bound, labelled as such;
   - max |b| and max σ_N;
   - the listed cells: R06 for the GiBUU E_avail shape; R02, R06 and R07 for the GiBUU prediction.
4. **The counts, read by group as declared.**
   - 4 of 192 cells beyond 2σ, against a Gaussian reference of 8.74;
   - 4 of 12 truths with p < 0.01, against 0.12;
   - with the group table of FD-F0-REPORT §0.
   - The references are context only, because the bias is deterministic.
5. **The limitation.** The same sentence as §2.3, positive-first.
6. **The controls.**
   - Controls 0–6 and 8 passed. Control 7 failed, as a gate on row 6 only.
   - What each control tests, in one line each.

Following R-N1 and R-N4, the note states the limitation once, in this subsection. The note's summary restates it in
one clause.

## 4. Slot for Stage G, the generator comparisons

Stage G is approved (decision item 2) and has not reported. When it does, the paper's generator-comparison paragraph
for the five-observable result follows the same pattern:
- one χ² per prediction against the reported covariance on R00–R15, with GiBUU on its eight p_∥ < 4.5 cells;
- a compact table;
- the reading stated once, positive-first;
- the detail in the note.

This draft leaves that paragraph empty: **[Stage G: to be drafted from its report.]**

## 5. What this draft does not do

- It prints nothing in the paper or the note.
- It changes no number, no matrix, no κ and no cell.
- It draws no conclusion of its own. The covering reading is the decision's, with W3 flagged above.
- The `\nsec{…}` targets are placeholders until the note subsection exists.

## 6. Number check (each value against FD-F0-REPORT)

Run `python3 -I check_numbers.py` from this directory. Every value in §2.2, and every count and width in §3, is matched
against the report's text. It exits 0 only if all match.

Results:
- `NUMBER-CHECK :: PASS (70 checks, 12 of 12 table rows found)`. The checks are:
  - the n, covariance, χ², p and cells of all twelve table rows, each against FD-F0-REPORT §5.1 at the draft's printed
    precision;
  - the §3 widths and counts, against §0 and §4.
- `SELF-TEST :: PASS (5 of 5 planted errors caught)`. It plants four wrong values (a χ², a p, a count and a cell list) and checks that each is caught.

## 7. agy review

Four rounds of agy (gemini) review against FD-F0-REPORT §0, §4 and §5, and from round 2 also FD-PLAN §1. The inputs and
outputs stay in the lane's scratchpad.

**Round 1: REVISE.**
- **Fixed:**
  - The table header "χ²/16" printed the total χ², so it now reads "χ² (16 d.o.f.)".
  - The covered list left out the Tune v1 hybrid.
  - §3 quoted one of the three leave-own-vertex-out matrices.
  - A cells column (|z| > 2) was added, so both triggers are visible.
  - "graded" and "listed" were reworded.
- **Not adopted:**
  - "GiBUU-to-GENIE" is FD-PLAN §1 row 2's own description of that truth. agy had not been shown FD-PLAN.
  - agy's replacement paragraph called all twelve truths "alternate" (one is the prior) and added "significant
    bias", a claim the source does not make.

**Round 2: REVISE. Every number matched.**
- **Fixed:**
  - The description of the covariance exclusion.
  - The generator of each shape change is now named.
  - The definition of "not covered" is now stated.
  - The limitation's lists are now parallel.
  - The note under the table is marked as a drafter's note.
- **Not adopted:** set-difference notation for the covariance column. The comparators describe matrices in words.

**Round 3: REVISE. Every number matched.**
- **The material point, fixed.** The limitation sentence was not true as read for the GiBUU E_avail shape without a
  qualifier. Against the full reported covariance (the in-sample variant) that truth gives χ² = 29.30 and p = 0.022,
  with no cell beyond 2σ. It is listed only against the covariance without its own GiBUU component, the declared
  grading matrix. The sentence now opens "Measured against the reported covariance, without the model-dependence
  component of the truth's own model where one exists, …".
- **Also fixed:** "each a generator's prediction" (one hybrid is Tune v1), and "generator" for GENIE + MEC.
- **Not adopted:**
  - "GENIE 2.12.10" is supported by FD-PLAN §1 row 5.
  - The `\nsec{…}` placeholders stay until the note subsection exists.
  - Capitalization and bold are a matter for the LaTeX rendering at integration.

**Round 4, on the final paragraph and limitation sentence: AGREE.**
- "Every statement … is true as read … and neither claims more nor less than the source."
- The four uncovered truths and the eight covered truths match the source's graded rows exactly.

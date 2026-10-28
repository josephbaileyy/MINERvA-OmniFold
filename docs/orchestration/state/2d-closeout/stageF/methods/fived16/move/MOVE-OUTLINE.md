# Outline: moving the non-final configurations out of the paper (DECISION-20261027-joseph-move-nonfinal-configurations-to-note)

**Status:** an outline for the director, before any edit.

**Inventory:** `config-inventory.md` (read-only, at 69491c33). Line numbers below are `paper_body.tex`'s; "s3" is the third sentence of that line.

## 0. One premise to confirm first

In the paper's own text, configuration (a) is **final** for the fine-grid five-observable central value and its five-axis covariance. Evidence:
- :91 s4;
- the Table II row at :105;
- :334 s1: "configuration (a) in five".

Joseph's decision lists that central value among the non-final material that moves: "carries the earlier five-observable central value and its covariance".

**This outline follows the decision.** After the move, the paper's only five-observable product is the sixteen-cell result. The (a) central value, its covariance and everything that rests on them move to the note. Moving them also takes:
- Sec. V D;
- the (E_avail, W) map of Sec. VII A;
- the abstract's "central values … whose normalizations agree".

**If you meant only the 2D, 3D and 4D roles of (a), say so before I start,** because the move is then about 450 words smaller.

## 1. What leaves the paper

Each leaves with a one-line pointer where a reader needs one. Every fact already prints in the note; the move ledger checks each one (§6).

| item | lines | words (source tokens) | note home |
|---|---|---|---|
| Table II rows (a)–(d), keeping (e) and (f) | :105–112 | ~60 | sec_method, sec:method-config |
| 2D learner and seed comparisons: the (a) seeds, the exact-split (b) values and the (f)–(b) difference | :134 s1–s3, s7–s9 | ~80 | sec_validation / sec:repro2d |
| (a) 3D and 4D injected-bump closures; the 4D and 5D (a) normalizations | :170 s2 (part), s4–s6 | ~60 | sec_validation sec:closure |
| the (d) generator-sized E_avail change (the 74 % cell, Fig. 3a) | :185 s2–s3, :208 s2–s3 | ~95 | sec_5d sec:gbdt-model-dependence |
| the (a) five-observable central value: :91 s4; Sec. V D (status, seed pair, rounding against the (d) baseline, "no generator significance based on this covariance"); Table I :38 (part) | :91, :238, :242 s2 (part) | ~200 | sec_5d / sec_eavailw |
| the (E_avail, W) map and its two-thirds figure; the "map therefore describes" paragraph | :337, :340 | ~170 | sec_eavailw |
| the regularization-bias limitation scoped to the (a) central value | :174 s3, :185 s7, :475 s4 (part) | ~45 | note |
| **subtotal** | | **~710** | |

## 2. What stays, in words (decision item 3: the paper's argument needs it)

Each item keeps every qualifier it needs to stay true, and names its configuration in words, not by letter.

| finding | why the argument needs it | proposed wording (sketch) | change |
|---|---|---|---|
| **Purity-based vs negative-weight background bias** (Table I :35; :174 s1, s2, s4–s6; Fig. 2) | It motivates the negative-weight subtraction of every final estimator, and (e)'s "removes most of the bias of the purity method" (:91 s5) rests on it. | Fig. 2 stays, with its caption in words: "Circles: purity-based subtraction; squares: negative-weight subtraction (deterministic LightGBM, 100 trees and 8 leaves for both)". :174 s2's yardstick ("about one standard deviation of the covariance of Sec. V D") is dropped, or re-pointed to the note. | ~−40 |
| **2D purity vs refined closure** | It is the stated reason that the 2D result uses the refined estimator (:177 s3, "therefore"). | Kept in about two sentences: "With purity-based subtraction, the two-dimensional estimate lies up to 5.9 statistical standard deviations from the truth; the refined negative-weight estimate stays within 0.44 in every cell, so the 2D result uses it." | ~−35 |
| **The post-selection disclosure for the 2D learner** (:134 s4–s6) | "This learner was chosen after both comparisons were known" and "a reproduction rather than an independent validation" need their referent. | One sentence: "The learner was chosen after comparisons with other training seeds, background treatments and an exact-split learner were known (Ref. [14], Sec. X), so the benchmark is a reproduction rather than an independent validation." The Fig. 1 caption and :150 keep "learner dependence", with the pointer. | ~−50 net |
| **Coverage test** (Sec. V C, Fig. 4; Table I :37; abstract) | This is the paper's only coverage measurement. The Scope paragraph and the limitations rest on it ("without intervals of validated coverage"). | **Two options; this one is yours or Joseph's to choose:** <ul><li>**(i) Keep it shortened, in words:** "Statistical intervals of a deterministic variant with purity-based subtraction …". Fig. 4 is kept with its caption in words.</li><li>**(ii) Move it to the note,** with one sentence and a pointer. The abstract then loses "statistical undercoverage".</li></ul> I lean to (i): it is a methods finding, and decision item 3 names this kind of case. | (i) ~−30; (ii) ~−300 |
| **Regularization-bias interpretation** (:185 s4; used by Sec. VI and Table III) | Sec. VI result 1 and Table III rest on it. | Kept in words, without a configuration letter: "In development studies, thirty iterations reduce the E_avail residual by 26 % …". **I will verify from the records which estimator ran these tests before printing "development studies";** the inventory marks it uncertain. | ~0 |
| **Rounding stability** (:242) | The (e) result carries it alone. | :242 s2's comparator clause ("as they move those of the baseline estimator (2.5)") goes. | ~−10 |
| **Fig. 3(b)** (e): its band is the (a) covariance's projection | The figure stays; its caption must describe what is drawn. | "the grey band is ± the total uncertainty of the (E_avail, W) projection of the purity-subtracted five-observable central value's covariance (Ref. [14], Sec. X)". :185 s5–s6 ("within the quoted total uncertainty in about half of those cells … that of the covariance of Sec. V D") gets the same pointer. These are pointers to a note product, not results. | ~+5 |
| **Table III (binned diagnostic)** | It is unchanged. Its configuration is unnamed: these are signal-only traces of the 100/8 OmniFold classifiers. | No edit. | 0 |
| **(e)'s rationale** (:91 s5, "remove most of the bias of the purity method") | It is the reason for choosing the joint-test estimator, and it rests on the purity-vs-negative-weight comparison kept above. | It is kept, pointing to Fig. 2 in words. | 0 |
| **:340 s3, "where the regularization bias … is largest"** | It rests on the (d) 74 % cell, and it leaves with the map (§1). | — | in §1 |
| **Joint tests (Sec. VII C–F)** | All (e). The calibration and nulls use the joint-test estimator, and nothing in them rests on a non-final configuration. Only Sec. VII A's (a) part, the 5D map, moves (§1). **The hybrid-null move is not touched.** | — | 0 |

## 3. Table I, Table II, the abstract and Sec. I's framing

**Table I (findings).**
- :34: "the 3D marginal agrees with the 2D result to 0.141 %". The 4D and 5D (a) normalizations go.
- :35 (background) is kept in words.
- :36 drops "(d)".
- :37 (coverage) follows option (i) or (ii).
- :38 keeps "rounding-level instability", and the (a) seed covariance goes.
- **The Conf. column goes.** With two configurations, each row names its estimator in words, or the column reads "2D estimator / joint-test estimator".

**Table II (estimators).** Two rows, both described in words:
- "two-observable estimator: LightGBM, seed 42, refined negative-weight subtraction (refinement 400 trees, 31 leaves)";
- "joint-test estimator: deterministic LightGBM, five iterations, refined negative-weight subtraction (400, 31)".

The caption drops "(f) is (a) with …" and "(c)–(e)", and states the determinism of the joint-test estimator directly.

**Letters (a)–(f) leave the paper.** They then print only in the note. The registry (ALIASES.tsv, paper-label rows) gets the new paper names, since `check_registry.py` requires each printed label to name one estimator.

**Abstract (main_paper.tex, protected).** Decision item 5 says the abstract follows the move. **The STRUCTURAL guard must then allow the abstract block of main_paper.tex to change. Please confirm that exception.** Proposed sentence 2:

> "With five simultaneous observables (adding available energy, three-momentum transfer, and hadronic invariant mass), it yields a sixteen-cell cross section with total uncertainties whose coverage is not validated; the three-observable central value's normalization agrees with the two-dimensional result."
<!-- absence-ok: quotes or proposes the paper's printed text (scope and coverage statements of the sixteen-cell result and the configuration-(a) product) as this record's inventory or plan; not a new absence claim -->

- Sentence 3 keeps "a background-subtraction bias" and "a partial recovery …", plus "statistical undercoverage" under option (i).
- Sentence 4 becomes "none of the reporting definitions tested in a precision study meets our 10 % precision criterion".
- About 125 words (now 117), with no labels.
- Round 2 of the PRD read (abstract proposals) has run; I will re-run it on the post-move text.

**Data availability (main_paper.tex:94, Joseph's).** It points to "the numbers quoted in Sec. VII A … the (E_avail, W) map", and the map leaves the paper. **I will not edit it. Joseph must re-scope it,** or the map stays as a one-sentence pointer.

**Sec. I.**
- :17 s2 becomes "three- and four-observable central values and a sixteen-cell five-observable cross section".
- Scope :46 becomes "The three- and four-observable results are central values without intervals of validated coverage; the five-observable result of Sec. V F has total uncertainties whose coverage is not validated." That replaces W2 and the current two sentences, and keeps guard G3's phrase.
- "The paper does not deliver a validated five-observable cross-section measurement" is reconsidered with W1.
<!-- absence-ok: quotes or proposes the paper's printed text (scope and coverage statements of the sixteen-cell result and the configuration-(a) product) as this record's inventory or plan; not a new absence claim -->

## 4. #413's scoped sentences

- **Paper:** 24 of #413's 134 FALSE or AMBIGUOUS sites are in the paper (6 FALSE, 18 AMBIGUOUS). About 19 of them concern (a), C_Z, (c) or (d), and **fall away or are re-described**: main_paper:44 ×2; :34; :38; :46 (a); :90; :105; :121; :173 ×2; :184; :207; :237 ×3; :290; :302; :405 ×2.
- **The five (e) sites stay:** main_paper:44 precision; :39; :113; :46 generic; :247.
- **Note:** the 110 note sites all stay, because the note keeps every configuration.
- **Integration ledger:** the rows for the paper sites that fall away (G4, C4, C5, AMB169, F-C21/C22/C24, and others) get the disposition "MOVED with its product" and X: probes, so the ledger does not demand text that has left.

## 5. Word saving (source tokens; PDF words run 2–4 % higher)

- **Leaves:** ~710.
- **In-words rewording:** ~−165 under coverage option (i), or ~−435 under (ii).
- **Replacements:** ~+60.
- **Net: about 800 words under (i), about 1,070 under (ii).** That is 8–11 % of the 9,505-token body.
- The inventory's estimate of 950–1,050 assumed the 5D (a) material stayed and counted the (c) coverage section as removed.

## 6. How the move is checked

- **A move ledger** (`fived16/move/ledger.md` plus a checker adapted from check_ledger.py) has one row per removed or reworded paper sentence:
  - an X: probe on the paper;
  - an N: probe on its note home, so that no fact leaves both documents;
  - a planted bad probe that must fail.
- **The integration's gates and the existing guards stay:** G1–G4 and Q5, NUMERAL, STRUCTURAL (plus the abstract exception), registry, records, absence-claims, reflow and build.
- **Then the PRD read of the changed text** (accept, deny or shorten, with a truth column), then one final draft to Joseph with the abstracts in words and the change tables.

## Questions for you before I edit

1. Does the (a) five-observable central value move as well (§0)?
2. Coverage test: option (i) keep shortened, or (ii) move?
3. The STRUCTURAL exception for the abstract block of main_paper.tex (§3)?
4. Data availability's pointer to the (E_avail, W) map: Joseph's to re-scope. Should I draft a proposal only?

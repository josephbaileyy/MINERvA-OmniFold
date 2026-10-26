# Note fix 2026-10-25: which quoted results use the refined negative-weight background treatment (§3.1)

**Ruled by** the director (2026-10-25), under Joseph's standing rule "fix now". Found by the caveat study's coding of
the note (`caveat-study/REPORT.md` §7). Made by the paper rewrite lane.

**What it is.** A factual correction of stale text. It is not a claim change:
- the sentence predates the 2026-10-24 move of the 2D result to configuration (f);
- every fact in the new text already prints elsewhere in the note.

## The defect

**Where:** `docs/analysis-note/sec_method.tex:73-77`, base origin/main `fe92211c`, note §3.1.

**What it said:**

> The quoted 2D and 5D central values, all quoted uncertainties and the extended-fiducial value do not use it. Its
> refined form is the background treatment of configurations (d) and (e) …

Here "it" is the unbinned negative-weight background treatment. Since 2026-10-24 the 2D result and its covariance
have been configuration (f), refined negative-weight subtraction. So the claim was false for:
- the 2D central value;
- the 2D covariance;
- the list of configurations that use the refined form, which left out (f).

## The claim, checked part by part against its source

| part | holds now? | source |
|---|---|---|
| the quoted 2D result and its covariance use the refined form, through (f) | yes: the old text was wrong | `app_history.tex:89-92`; `app_negweight.tex:17-24` ("except the 2D result and its covariance and the 3D and 4D central values"; "(f) for the 2D result and its covariance"); `sec_method.tex:248`; `sec_3d.tex:147`; `paper_body.tex` sec:method ("The two-observable central value uses configuration (f)") |
| the 5D central value uses the binned correction | yes: configuration (a) for now | `DECISION-20261023-joseph-5d-a-and-register-round.md` item 1; `sec_execsummary.tex:135` ("The 5D central value and its covariance use the purity subtraction") |
| the extended-fiducial value uses the binned correction | yes | `sec_fps.tex:120-122` ("The extended-fiducial value was produced with the binned purity correction, not with the negative-weight treatment designated for the extended-fiducial analysis") |
| the 3D and 4D central values use the refined form, through (e) | yes: unchanged | `app_negweight.tex:22-23` |

## The sweep, by claim

**What it searched for.** Every printed statement in the note, the paper and the primer that says the quoted 2D result
or its covariance does not use the negative-weight or refined treatment, or uses the purity or binned subtraction.

**How.** A sentence-level search over the comment-stripped sources of `docs/analysis-note/*.tex` for:
- a background-treatment term together with a 2D or quoted-result term and a negation or restriction;
- the pronoun forms "do(es) not use it/the", "uses the purity", "instead of the purity".

**What it found.** The defect sentence is the only stale statement. The other hits are correct as printed:
- `app_negweight.tex:17-24` and `sec_fps.tex:48-50` name the 2D result as refined;
- `app_negweight.tex:392-399` concerns the five-dimensional chain;
- `app_statmethods.tex:1010` reads "All rows except the quoted one use the purity-based subtraction";
- the primer reads "that result now uses the improved removal";
- the paper prints configuration (f) for the 2D central value.

The search over the r17 paper finds no stale sentence either. The sentence a primer comment quotes from the paper's
conclusions ("the refinement is used only for the generator tests") no longer prints.

## The new text (`sec_method.tex`)

> The quoted 2D result and its covariance and the 3D and 4D central values use its refined form; every other quoted
> cross section and uncertainty, including the 5D central value and the extended-fiducial value, uses the binned
> correction. The refined form is the background treatment of configurations (d), (e) and (f)
> (\S\ref{sec:method-config}): (d) in the background-bias and generator-sized-change studies of
> \S\ref{sec:val-negweight}; (e), the joint-test estimator, in
> \S\S\ref{sec:val-departure}--\ref{sec:gbdt-model-dependence}, the generator tests and the 3D and 4D central values;
> and (f) for the 2D result and its covariance (App.~\ref{app:negweight}, \S\ref{sec:3d}, \S\ref{sec:results}).

The new text follows `app_negweight.tex` "Scope of the numbers", which already printed the corrected facts. A source
comment cites the evidence.

## Ledger

The probes are the comment-stripped, whitespace-collapsed source:

| id | fact | before | disposition | after | probe |
|---|---|---|---|---|---|
| F1 | the quoted 2D result and its covariance use the refined form | sec_method.tex:73-74 ("do not use it") | CORRECTED | §3.1 | `N:sec_method.tex::The quoted 2D result and its covariance and the 3D and 4D central values use its refined form` |
| F2 | the 5D central value and the extended-fiducial value use the binned correction | sec_method.tex:73-74 | KEEP | §3.1 | `N:sec_method.tex::including the 5D central value and the extended-fiducial value, uses the binned correction` |
| F3 | the refined form is the treatment of (d), (e) and (f); (f) for the 2D result and its covariance | sec_method.tex:74-75 ("(d) and (e)") | CORRECTED | §3.1 | `N:sec_method.tex::The refined form is the background treatment of configurations (d), (e) and (f)` && `N:sec_method.tex::and (f) for the 2D result and its covariance` |
| F4 | the uses of (d) and (e) are unchanged | sec_method.tex:75-77 | KEEP | §3.1 | `N:sec_method.tex::(d) in the background-bias and generator-sized-change studies of \S\ref{sec:val-negweight}; (e), the joint-test estimator, in` |
| S1 | source: the scope paragraph of the background-subtraction appendix | — | source | App. C | `N:app_negweight.tex::except the 2D result and its covariance and the 3D and 4D central values` |
| S2 | source: the extended-fiducial value's treatment | — | source | §11 | `N:sec_fps.tex::The extended-fiducial value was produced with the binned purity correction` |
| S3 | the stale wording no longer prints | — | removed | — | (absent) `N:sec_method.tex::all quoted uncertainties and the extended-fiducial value do not use it` |

**Probe check:** 8 probes, 0 failures. The seven present probes print. S3 is checked for absence and does not
print.

## Checks

- **Full build** (`build_all.sh`, scratch copy of this branch):
  - exit 0; note 121 pages, primer 15, paper 13, PET note 26, records 55;
  - no `??` in the note;
  - 0 undefined references or citations. `main_note.log` carries 30 font-shape warnings, the same as the base build.
- **Build gates:** BODY-POINTERS PASS; SEC4-RECEIPTS PASS (15/15) and its self-test; RESULT PASS.
- **agy agreement** (gemini, BEFORE and AFTER paragraph with the four sources above): **AGREE**, with no issue.
- **Pre-commit gates** run on the staged change (absence claims, registry, swallowed text, manifest).

## Erratum (2026-10-26)

"The defect sentence is the only stale statement" was wrong. This sweep required a 2D or quoted-result term together
with a negation or restriction, so it missed sentences that made the purity weight the general method.

The director ruled a re-sweep by claim and by vocabulary, of the note, the paper and the primer (2026-10-26).
- **Patterns:** `purit`, `(D-B)/D`, "fixed before training", `default`, "binned correction/subtraction/weight",
  "reproduction measurement", "negative-weight", "refined", "background subtraction/treatment/removal",
  "do(es) not use it/the/this", "improved removal".
- **Hits:** 220 sentences. The note has 188, the paper 23 and the primer 9.
- **Per-file counts:** in `../note-n1/REPORT.md`, "Accuracy fixes".
- **Stale:** 9 more note sites, corrected in note register round n1's second commit as ACC1–ACC9.
  - §1 "Why unbinned"; the §3.1 heading and first sentence; the §3 driver conventions; §5.2's split-sample
    condition;
  - App. C's opening, §C.3 and §C.5 (two sentences);
  - App. H's driver description.
- **Paper and primer: 0 stale.**

Record: `../note-n1/REPORT.md`, "Accuracy fixes (unscored; second commit)"; ledger rows ACC1–ACC9 in
`../note-n1/ledger.md`.

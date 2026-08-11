# `check_dead_containment.py` passes while a struck retracted value renders in the paper PDF

**Date:** 2026-08-11 · **Lane:** Session D (verifier) · **Ledger:** BEN-090 · **Verdict: BLOCK (demonstrated,
end to end)** · **Measured on** `78296de` (the `docs/analysis-note/` tree is byte-identical at `a0d8eb7`
and at `ceb2037`; `git diff --stat 78296de HEAD -- docs/analysis-note/` is empty).

Nothing in the repo was modified to establish this. Every mutation ran on a copy under the job's tmp
directory; `git status` on `docs/analysis-note/` is clean.

---

## 1. The result first

`\dead {9.87654}` — one space between the control sequence and its brace — is ordinary, valid LaTeX. It
renders exactly as `\dead{9.87654}` does, because LaTeX skips whitespace while scanning for an
undelimited argument. `\dead` is declared `\newcommand{\dead}[1]{...}` at `preamble.tex:29`, so it takes
an undelimited argument and the space is invisible to the parser.

`check_dead_containment.py` matches `DEAD_RE = re.compile(r"\\dead\{")`. **That regex requires the brace
to be adjacent, so it does not see the spaced form.**

Demonstrated end to end on a copy of `docs/analysis-note/`, with the spaced form and nothing else added
to `paper_body.tex`:

    $ printf '\n\\noindent Retracted: \\dead {9.87654} here.\n' >> paper_body.tex
    $ python3 check_dead_containment.py
      RESULT :: PASS                       # exit 0
    $ latexmk -pdf main_paper                                   # exit 0
    $ pdftotext -q main_paper.pdf - | grep -n 9.87654
      1013:Retracted: 9.87654 here.

**The checker returns PASS, the paper builds, and the struck retracted value is in the outward-facing
PDF.** That is precisely the invariant the file's own docstring says it converts from an accident into an
enforced property.

## 2. Why the two-direction design does not help here

The docstring's strongest argument is that both directions are checked on purpose — containment for
paper/primer, and a positive control that the note still marks its retractions and that the values really
do appear in `main_note.pdf`. That argument is sound and the design is right. It does not help against
this, and the reason is structural rather than an oversight:

**both directions consume the same parser.** `struck_values` is derived by `dead_bodies()`, which uses
`DEAD_RE`. A body the regex cannot see never enters `struck_values`, so the PDF stage is not searching
for it either. One regex blinds the source stage and the PDF stage simultaneously. A second, independent
direction is not a second, independent *instrument* — which is BEN-088 rule (vi) landing on a test
instead of on a build.

## 3. Power test: what the checker CAN be made to do

Ten mutations, each on a fresh copy. Nine behave; one does not. Counts and the matched failure line are
both recorded, per BEN-088 rule (v).

| # | mutation | expect | got | |
|---|---|---|---|---|
| PT0 | none (baseline) | PASS | PASS | 25 `\dead{}` uses, 17 literals, 17/17 in note.pdf, 0/17 in paper and primer |
| PT1 | `\dead{9.87654}` into `paper_body.tex` | FAIL | **FAIL** | names the file, the build and the body |
| PT2 | `\dead{9.87654}` into `primer_body.tex` | FAIL | **FAIL** | |
| PT3 | every `\dead{}` stripped from the note's two using files | FAIL | **FAIL** | *"ZERO `\dead{}` uses … this test is now vacuous"* — the positive control works |
| PT4 | `main_paper.tex` loses all `\input` | FAIL | **FAIL** | *"include closure did not resolve (1 file)"* |
| PT5 | `main_note.pdf` copied over `main_paper.pdf` | FAIL | **FAIL** | names all 17 literals — the PDF stage can fail |
| PT6 | all three PDFs deleted | PASS | PASS | PDF stage skipped; source stage carries it |
| PT7 | **PT5's violation present AND `pdftotext` off `PATH`** | — | **PASS, exit 0** | see §4 |
| PT8 | **`\dead {9.87654}` (one space) into `paper_body.tex`** | FAIL | **PASS, exit 0** | **§1 — the defect** |
| PT9 | `\dead{\evadeMe}` (macro-valued) into `paper_body.tex` | FAIL | **FAIL** | macro bodies are covered |
| PT10 | every `\dead{}` body made non-numeric | PASS | PASS | correctly reported as an uncovered coverage gap, not skipped silently |

So the test is genuine evidence over nine of its ten branches, including both of the ones its docstring
argues for. This finding narrows it; it does not retire it.

## 4. The second exposure, weaker and worth stating separately

PT7 is not the same defect and should not be merged into it. With a **real** containment violation
present (`main_note.pdf` copied over `main_paper.pdf`, which PT5 shows the checker catches), removing
`pdftotext` from `PATH` makes the script print

    ok   main_note.pdf absent or pdftotext unavailable -- PDF stage skipped (source stage above is
         the authoritative check)
    RESULT :: PASS

and exit `0`. This is **documented, not hidden**, and the source stage really is the authoritative
check — so it is a much weaker point than §1. What it costs is this: **`exit 0` does not distinguish
"the PDF stage passed" from "the PDF stage did not run."** Any caller that reads only the exit status —
`build_all.sh:26` is the one caller in the tree — cannot tell which happened. On a machine without
`pdftotext`, or before the PDFs are built, the check silently degrades to source-only and still says
`PASS`.

**Both exposures were established here, and the checker DID open the PDFs on this machine** — PT0 shows
`pdftotext` present, all three PDFs present, and the positive control firing at 17/17. So for the
question Session A asked, the answer is the stronger one: this run checked the PDFs.

## 5. Scope — what is and is not true today

- **The containment holds right now.** `grep -rn '\dead[ ]\+{' docs/analysis-note/` returns nothing:
  there are zero spaced instances in the tree. Nobody has written one.
- **Independently measured, and it agrees with `PROMPTS-20260811 §3`'s direction:** of the 17 distinct
  decimal literals derived from the note's 25 `\dead{}` bodies, `main_paper.pdf` contains **0** and
  `main_primer.pdf` contains **0**. My derivation is broader than §3's, so this is a stronger negative
  than the one it corroborates.
- **§3's "8×" ingredient does not reproduce, and it is UNRESOLVED rather than wrong.** §3 records *"the
  struck magnitudes appear 8× in `main_note.pdf`"* and the checker's docstring says *"the five struck
  magnitudes"*. Measured at `4f75e50` — the commit that introduced the checker and carries that
  sentence — the two using files already had **25** `\dead{}` uses, yielding **17** distinct literals
  appearing **51** times in `main_note.pdf`. So "five" was not the population at that commit. I cannot
  refute the `8×` either, because **neither §3 nor the docstring names which five magnitudes it counted**,
  and some of my 17 (`1.6`, `6.5`, `9.9`) are collision-prone enough that 51 is certainly an over-count of
  *struck* renderings. The honest statement is that the claim is **unreproducible as written** for want of
  its population — BEN-079's shape (a bare count with no stated scope), one level up. **The conclusion it
  supports is unaffected:** 0× in paper and 0× in primer is confirmed independently here.

## 6. Why this one is worth a row

The class this repo keeps generating is *a gate that cannot fail*. `check_dead_containment.py` was
written on 2026-08-11 specifically to close a gates-that-cannot-fail exposure — the docstring says so:
*"That is this repo's most-repeated defect shape — a gate that cannot fail — so the positive control is
not optional."* It then shipped with a hole against an ordinary LaTeX idiom.

That is the same shape as BEN-084's author violating the ordering contract minutes after writing it, and
BEN-070 §4.1's auditor being silent on its own known instances. **Writing the instrument for a failure
class does not exempt the instrument from the class**, and the only thing that has ever caught it is
running the instrument against an input designed to beat it.

**Generalisation worth more than the fix:** a text-matching gate over a *language* is only as strong as
its agreement with that language's parser. `\dead{`, `\dead {`, `\dead%\n{`, and a `\dead` reached through
`\let` or `\newcommand` are one token to TeX and four different strings to a regex. The same question
applies to every other `\...{`-matching check in this repo.

## 7. Disposition — NOT fixed here, and not mine to fix

I am read-only outside `docs/orchestration/`. `docs/analysis-note/` is the note lane's, and
`check_dead_containment.py` is cited in `PROMPTS-20260811 §3` as the enforcement behind a closed decision.

Suggested repair, for whoever owns it, in the order I would take them:

1. `DEAD_RE = re.compile(r"\\dead\s*\{")` — one character class, closes §1 in both stages at once.
2. A power test for the spaced form, in both directions, so the hole cannot silently return.
3. For §4: make the PDF stage's non-execution visible in the result line rather than only in a note —
   e.g. `RESULT :: PASS (source only, PDF stage did not run)`. A distinct exit code is the stronger
   version but changes `build_all.sh`'s contract, which is the owner's call, not mine.

Recommendation on §3's `8×`: rather than re-measure it, name the five magnitudes it counted, or replace
it with the checker's own derived figure. A count whose population is not stated cannot be re-verified by
anyone, which is how it survived to be quoted.

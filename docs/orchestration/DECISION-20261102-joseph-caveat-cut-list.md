# DECISION 2026-11-02 (latest) — Joseph: the paper makes the reviewer-approved caveat moves

**Recorded by** the paper-tighten lane, as director.

## What led to it

**The density.** On the paper at `58fa0b89`, a fresh coding found 77 distinct caveats, 9.5 per 1,000 words, with a
coder spread of ±25%. That figure is from `caveat-remeasure-20261102/`, #701 and #705. Nine published PRD comparators
run 1.4–4.5.

**The cut list.** limitations-catalog's cut list (`…/cutlist/`, #706) proposes 20 moves:
- **merges,** which state related caveats once;
- **M moves,** which take a caveat or a small secondary section to the note and leave a pointer.

No move drops a fact from paper plus note. All 20 together give 77 → 44.

**The PRD-referee read.** Gemini read the moves at Joseph's standing rule
(`…/cutlist/PRD-REVIEW-GEMINI-{PROMPT,ANSWER}.txt`):
- **It welcomed** MV01, 02, 03, 04, 07/07F, 08, 10, 13, 14 and 16.
- **It objected to:**
  - MV15 (moving the input-rounding test), because instability of up to 2.6σ must stay in the main text;
  - MV09 (moving the hybrid-null limits);
  - MV17 and MV18, until the note states those facts.
- **It advised skipping** the join-only moves MV05, 11 and 12.
- **It called about 6 per 1,000 a reasonable target** for this paper.

The director noted that its sample MV02 wording ("halted") is out of date and should not be adopted as written.

## Joseph's answer, verbatim

Asked which moves the paper lane should make:

> Reviewer-approved set (Recommended)

sha256 of the text plus a final newline begins `c62ddf3b4336511c`.

## What is decided

1. **Make these moves,** from the #706 cut list's proposed statements: MV01, MV02, MV03, MV04, MV06, MV07, MV07F,
   MV08, MV10, MV13, MV14 and MV16.
   - Each rewritten sentence is checked against the sentences it replaces, and every fact is kept.
   - MV07F needs Fig. 4 redrawn without the legend tokens. That goes through the bound figure tool with an
     amendment, if the tool requires one.
   - MV02's single coverage statement must state the current 1B status accurately. The reviewer's "halted" is not
     adopted.
   - Each M move leaves a pointer and a probe showing the note prints the fact (`DECISION-20261029`).
2. **MV15 stays in the paper,** condensed to one or two sentences.
3. **MV09 stays where it is.**
4. **MV17, MV18 and MV19 come later.** Their facts are written into the note first, and the moves follow once the note
   prints them.
5. **MV05, MV11 and MV12 are skipped.**
6. **The expected result** is about 77 → 51 distinct caveats, roughly 6.9 per 1,000 words, falling further as the
   coverage and run-period campaigns resolve their caveats.
   - It is re-measured after the round with `remeasure.py`, at ±25%.
   - Moving whole secondary results to the note (R-P9), the only route to ≤ 4.5, is decided separately, once it is
     priced.
7. **The process.** Before any merge, the round's REPORT gives every changed sentence before and after, goes through a
   PRD-referee read of the rewritten text, and goes to Joseph.

## The density gate (Joseph, 2026-11-02, latest)

**The pricing.** limitations-catalog priced R-P9, moving whole secondary results to the note (`…/cutlist/RP9.md`, #708):
- **Reaching ≤ 4.5 per 1,000** needs, in every solution, moving the 2D benchmark against the published result (IV B and
  Fig. 1, cited by the abstract and Sec. I), plus two or three of the main result's qualifiers. That lands at
  4.45–4.50, inside the ±25% coder spread.
- **The best result that keeps what a referee would expect** is about 4.9.
- **Gemini's PRD read** called about 6 reasonable for this paper.

**The question put to Joseph.** How the gate should read, given that reaching 4.5 means moving evidence a referee would
look for.

**Joseph's answer, verbatim:**

> Target ~6, keep the benchmark (Recommended)

sha256 of the text plus a final newline begins `8c32e12cf9521b54`.

**Decided:**
- The readiness gate's density target for this paper is **≤ 6 distinct caveats per 1,000 words**.
- The 2D benchmark and the bias evidence stay in the paper.
- R-P9's section moves are not made.

Nothing is submitted, deposited or tagged.

# CORRECTION 2026-09-21 — the seed effect's "a larger ensemble would not change this" corollary is withdrawn

**CITABLE FOR:** the withdrawal of one inference, and the complete list of sites it reached.
**NOT CITABLE FOR:** any re-grade, any change to a measured value, any withdrawal of the adoption,
or any weakening of the `M1` FAIL. **No number moves.** One inference about what the numbers imply
for untested ensemble sizes does.

Source of the defect:
[`EVIDENCE-20260920-sproj-resolution-floor-and-seed-effect.md`](EVIDENCE-20260920-sproj-resolution-floor-and-seed-effect.md)
§5, and the summary of it at `AGENTS.md:88`.
Operand re-read for this correction:
[`state/SEED-EFFECT-20260920.json`](state/SEED-EFFECT-20260920.json).

Raised by a manuscript review of the analysis note on 2026-09-21 and by a peer re-verification of
the resulting fixes. **Neither is the authority here**; the authority is the receipt, which was
re-read for this record.

---

## 1. The measurement, which stands unchanged

`s_proj` was measured seven times with the throws held fixed and only the estimator seed changed.
From `state/SEED-EFFECT-20260920.json`, `seed_effect_same_throws`:

| subset | `n_throws` | `s_proj` |
|---|---:|---:|
| `Q1` | 40 | `6.64025%` |
| `Q2` | 40 | `5.86403%` |
| `Q3` | 40 | `5.44858%` |
| `Q4` | 40 | `6.14425%` |
| `HA` | 80 | `6.28872%` |
| `HB` | 80 | `5.75774%` |
| full (`graded_s_proj_N160`) | 160 | **`6.14539%`** |

Means: **`6.0243%` at `N = 40`** (four subsets), **`6.0232%` at `N = 80`** (two halves),
**`6.145%` at `N = 160`**. Fitted exponent `p = 0.000` in `s ∝ N^-p`. The same-seed resampling
floor fell `20.91% → 7.57%` between `N = 40` and `N = 80`, a two-point exponent `1.467`.

**The conclusion these support is retained in full:** statistical noise must fall with `N`, this did
not fall between `N = 40` and `N = 160`, and therefore **the failing leg is not reporting the
statistic's own resampling noise.** `M1`'s `s_proj = 6.145%` against the `5%` bound, and
`(cause 3, Z)`'s `M(ii)` **branch 5, NOT MET — PER-BIN**, are untouched; they were measured
directly and never rested on any extrapolation.

## 2. The inference, which does not follow

`EVIDENCE-20260920` §5 is headed **"⚠ THE COROLLARY: A LARGER ENSEMBLE WOULD NOT CHANGE THIS"** and
states:

> - **Re-running with more throws does not reduce it.** At `N = 40`, `80` and `160` it is the same
>   `~6%`. **There is no ensemble size at which it falls under `5%`.**

**That last sentence is withdrawn.** Three properties of the operand block it:

1. **The points are NESTED, not independent.** `Q1`–`Q4` are slabs `0-9, 10-19, 20-29, 30-39` and
   `HA`/`HB` are slabs `0-19, 20-39` **of the same 160-throw ensemble** (§3 of the evidence file
   states this in its own method table). A statistic evaluated on subsets of one draw and on the
   whole of that draw is a **within-ensemble** observation. It shows the statistic is not dominated
   by which of these 160 throws you look at. It is not a sample of the statistic's behaviour across
   ensemble sizes drawn independently.
2. **The range is a factor of four, and the claim is about all `N`.** "There is no ensemble size"
   quantifies over the unbounded set; the measurement covers `40`–`160`. Flatness over two
   doublings does not determine an asymptote, and the evidence file offers no model under which it
   would.
3. **It is ONE seed pair.** Offsets `{0, 1200}`, i.e. estimator seeds `1000` and `2200`. The
   evidence file's own boxed warning says the width of the seed-pair distribution is **unmeasured**.
   A statement about what any larger ensemble would give is a statement about the estimator, and
   the estimator was sampled at one pair.

**The second bullet of §5 is NOT withdrawn.** *"A resolution-aware bound would have to sit above
`6.145%`, and the resolution floor at `N = 160` is `2.7–5.4%` — below the effect"* is an argument
about where a bound could be set given the measured floor extrapolation, not a claim about
arbitrary `N`. It is retained as written, with its own extrapolation (§4's `2.74%` on the measured
exponent, `5.35%` at `p = 0.5`) already labelled as an extrapolation in place.

**And §5's operative conclusion survives its own corollary.** *"There is nothing to price"* — the
answer to Joseph's question about the cost of a rebuild that could pass — rests on the second
bullet and on the fact that the bound was fixed before production, not on the first.

## 3. The replacement wording, used verbatim at every prose site

> The effect did not fall with ensemble size over the range tested — `6.02%` at `N = 40`, `6.02%`
> at `N = 80` and `6.145%` at `N = 160`, fitted exponent `0.000` — while the same-seed resampling
> floor fell `20.91% → 7.57%` between `N = 40` and `N = 80`. The `40`- and `80`-throw points are
> nested subsets of the same 160 throws at one seed pair, so the behaviour at much larger `N` and
> the width of the seed-pair distribution are both unmeasured.

## 4. Every site reached

| # | site | what it said | disposition |
|---|---|---|---|
| 1 | `EVIDENCE-20260920-sproj-resolution-floor-and-seed-effect.md` §5 heading and first bullet | *"A LARGER ENSEMBLE WOULD NOT CHANGE THIS … There is no ensemble size at which it falls under `5%`"* | inline `⚠ CORRECTED` block added, pointing here; **§5's text is left standing** so the withdrawn reasoning remains readable |
| 2 | `AGENTS.md:88` | *"flat in `N`, so a property of the estimator and not of the ensemble's resolution"* | corrected in place with an inline `⚠ CORRECTED` block; `AGENTS.md` is declared a view, and this is the summary every session routes through |
| 3 | `docs/analysis-note/sec_eavailw.tex` measurement 2 | *"Enlarging the ensemble would therefore not reduce it."* | corrected 2026-09-21 |
| 4 | `docs/analysis-note/paper_body.tex` | *"a larger ensemble would not reduce it"* | corrected 2026-09-21 |
| 5 | `docs/analysis-note/primer_body.tex` | *"running more variations would not remove it"* | corrected 2026-09-21 |
| 6 | `docs/analysis-note/values.tex` block (2) comment | governed `\seedEffect`; named the over-statement but acted on nothing | now carries the scope caveat and the per-`N` means as separate macros |
| 7 | `REPORT-20260920-scalar5d-uncertainty-completion.md` `L1` (at `7257b255`; no line number, the edit moved it) | *"a property of the estimator and a larger ensemble would not reduce it"* | **substantive sentence REPLACED** with *"a property of the estimator rather than of the ensemble's resampling noise"*, **and** an inline `⚠ CORRECTED` block added. Every measured number left standing |
| 8 | `HANDOFF-20260921-gbdt-remaining.md` `L1` (at `4e960436`; no line number, the edit moved it) | *"so it is a property of the estimator and **a larger ensemble would not reduce it**"* | **substantive sentence REPLACED** with the same wording as site 7, **and** an inline `⚠ CORRECTED` block added. ⚠ **Another lane's live document.** The owning GBDT lane re-derived the withdrawal from `state/SEED-EFFECT-20260920.json` independently, accepted it, and is **keeping the replacement**, judging that it states the retained inference better than the original. **That acceptance is what makes the edit acceptable** — a silent substantive change to another lane's live record would not have been, whatever its quality |
| 9 | `nd-unfolding/CORRECTED_UQ_PRODUCTION_STATUS.md`, the `⚠ FOUR MEASUREMENTS TRAVEL WITH IT` block (planted at `e7f8f365`) | *"so it is a property of the estimator and a larger ensemble would not reduce it"* | **substantive sentence REPLACED** with the same wording as sites 7–8, **and** an inline `⚠ M1 CORRECTED` block added, 2026-09-21. ⚠ **Found only after this table read "all 8 sites" — see §4c.** ⚠ **This file was already being maintained:** the asserting sentence sat three lines above an existing `⚠ M3 CORRECTED 2026-09-20` block in the same paragraph, so a previous withdrawal *did* reach this file. It is **not** an unmaintained corner that was missed |
| 10 | `docs/orchestration/CATALOG.md`, the `EVIDENCE-20260920…` entry (the DISCOVERY surface) | *"**Corollary: a larger ensemble would not change it**, and no rebuild passes"* — asserted in the catalogue's own voice, in bold, with **no withdrawal marker** | **Clause REPLACED with an inline `⚠ WITHDRAWN 2026-09-21` marker, 2026-09-22.** `no rebuild passes` and `no price is owed` are **retained**, per `EVIDENCE` §5's corrected block (*"The second bullet below is NOT withdrawn, nor is §5's conclusion that there is nothing to price"*). ⚠ **INVISIBLE TO EVERY SWEEP SO FAR, FOR TWO INDEPENDENT REASONS AT ONCE — see §4d** |
| **11** | **`docs/orchestration/CATALOG.md`**, the entry for `DECISION-20260920-joseph-adopts-z-cv-under-the-6.4-exception.md` | the **unqualified** *"flat in N (`p = 0.000`) so it is the estimator, not resolution"*, in the catalogue's own voice | ⚠ **MISSED BY THIS TABLE UNTIL 2026-09-22**, found by the eighth independent review rather than by this record's own sweep. Now carries §3's replacement wording **verbatim**. ⚠ A first repair overshot — it declared the SCOPED form a defect too, citing a non-existent §2.1; that overreach is withdrawn, and `VERDICT-20260922-third-party-review-site9-issue60-s4c.md` blesses the scoped form. ⚠ A second repair filed this site in §4a, the **chronology** table (columns `site \| first landed`), supplying neither a commit nor a time. ⚠ A third version of this row was **one cell short, and a pipe inside a code span made its count match the header**, so a pipe-count check passed it while GFM split the code span across two columns. |

**`values.tex` is site 6 and is again the one a search for the claim would miss**, because it is a
LaTeX comment above a macro rather than rendered text — the same trap
[`CORRECTION-20260920-lower-bound-inference-withdrawn.md`](CORRECTION-20260920-lower-bound-inference-withdrawn.md)
recorded as its site 8.

⚠ **ROWS 7 AND 8 ALSO MISDESCRIBED THEIR OWN ACTION UNTIL 2026-09-21, AND THE CAUSE IS THE SAME
ONE.** Row 8 read *"pointer only, no rewrite"* while the diff replaced the sentence; row 7 said
*"pointer added"* and omitted the replacement; both cited line numbers the same edit had moved.
**They were written from the intended action rather than measured from the diff afterwards** — in a
record whose entire subject is a claim that outran its evidence. The GBDT lane found it by opening
the diff. ⚠ **And it survived a review:** the reviewing lane had relayed *"pointer only, no
rewrite"* onward as fact without opening the diff, so a second pair of eyes reproduced the error
instead of catching it. **A reviewer taking a description of a diff on trust is not a check on that
description.** The fix is mechanical and worth stating as a rule: **after editing, `git diff` the
file and write the row from the diff.**

## 4c. The sweep's own population claim, and the instrument that found site 9

⚠ **ADDED AS A HEADING 2026-09-22.** This block's content landed at `d2f29ca5`, whose message
says *"Recorded at the record's new S4c"*, but **no `4c` heading was ever written**. Three
pointers — row 9's *"see §4c"*, this block's own *"(§4c)"*, and two in `CATALOG.md` — resolved
to nothing. The heading is added here rather than the pointers rewritten, because the content is
what they describe. It sits before §4a in document order, which is where the content was placed.

⚠ **SITE 9 WAS MISSED BY THE SWEEP ITSELF, AND THE CAUSE IS A POPULATION CLAIM THIS RECORD DID NOT
EARN (§4c).** The sweep paragraph below opens *"swept by CLAIM, not by wording"*, but the command was
`grep -rn … docs/ AGENTS.md` — scoped by a **directory glob**. `nd-unfolding/…` was therefore never
in the hit set to be classified: site 9 was not judged wrongly, it was **never seen**. A
claim-scoped sweep under a path-scoped command is exactly the shape this record exists to correct,
committed inside the record itself.

**THE INSTRUMENT THAT FOUND IT, and it generalises past this claim.** A claim's blast radius is the
**file list of the commit that spread it** — not a guess about which directories are relevant:

    git log -S '<the claim>' --reverse -- .      # the planting sha
    git show --name-only <sha>                   # its population

Here that is `e7f8f365`, whose own subject line is *"The adoption reaches the ledger, the front door
**and the status files**"*. Seven files: `AGENTS.md`, `KNOWN_ISSUES.md`, `VALIDATION_LEDGER.md`,
`docs/ESTIMATOR_REGISTRY.md`, `OPERATIVE-SHEET-scalar5d.md`, `ND_OMNIFOLD_STATUS.md`,
`CORRECTED_UQ_PRODUCTION_STATUS.md`. Six are clean; one asserted. **Four surfaces received the
claim and three received the correction, and the planting commit's subject named the surface class
the sweep's glob omitted.** Found by the reviewing lane (`fixer reviewer`) on a tree-wide re-run of
the discriminator; confirmed independently by this lane over all tracked paths.

⚠ **A COUNT OF SWEEP HITS IS NOT A COUNT OF DEFECTS, measured here.** The tree-wide sweep returns
four *apparent* assertions after the `⚠ CORRECTED` lines and blockquotes are stripped. Opening each:
`CATALOG.md` quotes the claim under the word **WITHDRAWN**; this record's own §4 quotes it in the
*"what it said"* column; `EVIDENCE-20260920` §5 is **deliberately left standing** beneath its pointer,
which is site 1's recorded disposition. **Three of the four are by design.** Only
`CORRECTED_UQ_PRODUCTION_STATUS.md` was real. A phrase search cannot separate an assertion from its
own retraction when quoting-to-prohibit is house style — the discriminator is the **sentence ending**
(`estimator and` versus `estimator rather than of the ensemble's`), plus the pointer count.

⚠ **AMENDED 2026-09-22: THE PARAGRAPH ABOVE WAS FALSIFIED BY §4d IN THE SAME COMMIT, AND WENT TWO
COMMITS UNAMENDED.** Its clause *"`CATALOG.md` quotes the claim under the word WITHDRAWN"* is true
of **one** `CATALOG.md` entry (the one for this record) and **false as a statement about the file**:
§4d establishes that `CATALOG.md` simultaneously carried a live, unmarked assertion in its
`EVIDENCE-20260920` entry. So *"Three of the four are by design … Only
`CORRECTED_UQ_PRODUCTION_STATUS.md` was real"* is **a defect tally of two, not one**.
**What stands unchanged is the paragraph's actual thesis** — a hit count is not a defect count, and
the sweep genuinely returned four, because site 10 was invisible to it (§4d measures why). The
error is the disposition, not the lesson. Found by an independent adversarial review.

⚠ **SITES 7 AND 8 WERE ALSO MISSED BY THE FIRST DRAFT OF THIS TABLE, AND THAT MISS IS INSTRUCTIVE
ENOUGH TO RECORD RATHER THAN QUIETLY REPAIR.** This table was written from the sites the
manuscript review and the peer re-verification had named — six — and the sweep below was
described *before it was run*. Running it returned **two more**, both in `docs/orchestration/`,
both carrying the withdrawn sentence almost verbatim, and one of them **written the same day this
correction was**. An enumeration derived from the reports that prompted a correction is a list of
what someone already noticed; only the sweep is a list of what is there. **Run the sweep first and
let it write the table.**

**Swept by CLAIM, not by wording — sweep run 2026-09-21 AFTER the six corrections above, and its
output is what fixed this table.** Command:

    grep -rn -e 'larger ensemble' -e 'more throws' -e 'no ensemble size' \
             -e 'would not reduce' -e 'would not remove' -e 'would not change this' \
             docs/ AGENTS.md

Surviving hits, all accounted for: this record (its own title, its quotation of the withdrawn
bullet, and its site table); the three inline `⚠` pointer blocks at sites 1, 7 and 8; `EVIDENCE`
§5's own text, deliberately left standing beneath its pointer; `CATALOG.md`'s route to this
record; `sec_pet.tex:236`, an unrelated and correct sentence about a larger PET replica family
sharpening a dispersion estimate; and four older records using the words in unrelated senses
(`CHECK-20260911`, `PACKET-20260910`, `AUDIT-FINDINGS-20260728`, `PROVENANCE-20260822`).
**`AGENTS.md` no longer matches, because site 2 is repaired.**

## 4d. SITE 10, and why it was invisible to EVERY sweep — including the corrected one

⚠ **A TENTH SITE WAS LIVE ON THE DISCOVERY SURFACE UNTIL 2026-09-22**, found by a third lane
reviewing §4c under `HANDOFF-20260922` §10. `docs/orchestration/CATALOG.md`'s entry for
`EVIDENCE-20260920…` asserted, in bold and in the catalogue's own voice, with **no withdrawal
marker anywhere near it**:

> **Corollary: a larger ensemble would not change it, and no rebuild passes** — so no price is owed.

Planted at `128a5e7a` (2026-09-20), measured with `git log -S 'ensemble would not change it'
--reverse -- docs/orchestration/CATALOG.md`. **This is the withdrawn corollary in its strongest
form** — *"would not CHANGE it"* is two-sided, where sites 1–9 said *"would not REDUCE it"* — sitting
on the file a reader reaches a record THROUGH.

### Why the scope rule did not catch it, and the instrument rule did not either

**Site 9 was missed by SCOPE. Site 10 was missed by INSTRUMENT.** They are different failures and
§4c's remedy does not cover this one: `CATALOG.md` is under `docs/`, so it was **inside** the
sweep's path scope the whole time and still returned nothing.

The record's own sweep command is

    grep -rn -e 'larger ensemble' -e 'more throws' -e 'no ensemble size' \
             -e 'would not reduce' -e 'would not remove' -e 'would not change this' \
             docs/ AGENTS.md

**Measured against the pre-fix `CATALOG.md` bytes, every one of the six returns 0 hits on this
site.** Five miss on WORDING — the text says *"would not change **it**"*, and the pattern list has
*"would not change **this**"*. The sixth, `larger ensemble`, is the one that should have fired, and
it did not, for a reason worth more than this claim:

| instrument | hits on site 10 | why |
|---|---:|---|
| `grep -e 'larger ensemble'` | **0** | the phrase spans a line break |
| `tr '\n' ' '` then `grep` | **0** | ⚠ **the rule AS WRITTEN in this tree still misses it** |
| `tr '\n' ' ' \| tr -s ' '` then `grep` | **1** | whitespace **collapsed**, not merely replaced |
| `re.sub(r'\s+', ' ', text)` then search | **1** | same thing, done properly |

⚠ **THE STATED NEWLINE RULE IS INSUFFICIENT AND THIS IS THE COUNTEREXAMPLE.**
`HANDOFF-20260922` §8.5 and §10.1.3 both say *"A quote that spans a newline is invisible to a
line-oriented grep — use `tr '\n' ' '` first."* The literal bytes here are

    a larger<LF>  ensemble would not change it

— a newline **plus the two-space indent of a wrapped Markdown continuation line.** `tr '\n' ' '`
turns that into **three** spaces, so `larger ensemble` still does not match. In a tree whose prose is
hard-wrapped and indented under list items, the newline-spanning quote is **the common case**, and
the documented remedy fails on it silently: it returns 0 and looks like a clean sweep.

**The rule is therefore corrected here: COLLAPSE whitespace, never merely replace newlines.**
`tr -s` or `re.sub(r'\s+', ' ', …)`. A sweep that replaces newlines and does not collapse runs is
still a line-oriented sweep wearing a disguise, and it will report zero on exactly the sites that
most need finding.

### The detector's own false positive, adjudicated rather than silenced

Running the collapsing sweep over the whole tree returns **one hit that is not a defect and must
not be "fixed"**: `docs/analysis-note/values.tex`'s `CAUTION -- SCOPE` comment block, which quotes
`EVIDENCE` §5's heading (*"A LARGER ENSEMBLE WOULD NOT CHANGE THIS"*) in order to say that §5
*"states more than the seven points support"*. It is the **correction**, quoting the claim to
prohibit it — the house style §4c describes.

It is flagged only because the mechanical discriminator looks for the literal tokens `WITHDRAWN` /
`CORRECTED` within a window, and that block states its retraction in its own words instead.
**The block is right and is left exactly as the note lane wrote it.** Editing a correct artifact so
that a detector stops complaining would be repairing the instrument's reading rather than the
tree — and it would put a wording change into the note, and therefore into the standalone
repository, for no scientific reason. **Recorded here so the next sweep classifies it in one step
instead of rediscovering it.**

⚠ **So the standing hit set after 2026-09-22 is: three by-design quotations named in §4c, this
`values.tex` block, plus every site row above — and ZERO live assertions.**

### What this does NOT change

No number moves, again. `M1`'s `6.145%` against the `5%` bound is untouched. The two clauses
`EVIDENCE` §5's corrected block explicitly RETAINS — *"no rebuild passes"* and *"there is nothing to
price"* — are retained in the patched entry verbatim, because they rest on where a resolution-aware
bound could sit and never on arbitrary `N`. Only the two-sided ensemble-size clause is withdrawn.

## 4a. A convergent, contemporaneous instance of the one-seed-pair half

`PREDECLARATION-20260921-L2-lateral-seed-release.md` §4 fixes an outcome map *before* its probe
runs, and its `< 5%` row reads:

> **nothing.** One seed pair cannot establish that the maximum over the declared set is below the
> bound … it is **not** a PASS, not a clearance, and not grounds to revisit the adoption.

Written by a different lane, for a different purpose, and **fixed before a run rather than after a
result** — which is the strongest form this kind of reasoning takes.

**The margin, measured, because "predates" invites a reader to picture an established principle.**
First-landing commits, all by `git log -S <phrase> -- <path>` so the instrument is the same on
every side:

| site | first landed |
|---|---|
| `state/SEED-EFFECT-20260920.json` (the artifact) | `128a5e7a` 2026-09-20 13:01 −0700 |
| `EVIDENCE-20260920…` §5 corollary | `128a5e7a` 2026-09-20 13:01 −0700 |
| `AGENTS.md` *"flat in `N`"* | `e7f8f365` 2026-09-20 22:01 −0700 |
| `REPORT-20260920…` `L1` | `7257b255` 2026-09-20 22:18 −0700 |
| `HANDOFF-20260921…` `L1` | `bad2e61f` 2026-09-21 14:11 −0700 |
| **the predeclaration clause** | **`f6f54e73` 2026-09-21 16:16 −0700** |
| this correction's first edits | ~2026-09-21 20:02 −0700 |
| ⚠ **`docs/orchestration/CATALOG.md`, the adoption entry** | **see §4 site 11 — this row was filed in the wrong table** |

So the clause **postdates every one of the record-side sites** and predates only this correction,
by **3 h 46 min**, on the same day, from a concurrently running lane. It is **convergent and
contemporaneous, not prior authority**, and the window in which the sound reasoning was live in the
tree while other records asserted its opposite is that 3 h 46 min — not a standing principle
anyone had been ignoring.

**Scoped, because half of this correction is not in it.** That clause is an independent instance of
the **one-seed-pair** half: a single pair cannot settle where a maximum over the declared set sits
relative to a bound. It says nothing about the **nested-subset** half — that `40`- and `80`-throw
subsets of one 160-throw ensemble cannot determine behaviour at much larger `N` — which is the
part that the withdrawn corollary actually turned on. Cited as convergent support for one half, not
as prior authority for the whole; the owning lane has itself declined to claim it more broadly.

⚠ **A FALSE FINDING WAS NEARLY RECORDED HERE, AND THE METHOD THAT PRODUCED IT IS THE POINT.** A
draft of this section was going to state that one asserting site was committed **after** its own
refutation — the handoff at `4e960436` (18:39) against the clause at `f6f54e73` (16:16). **That is
wrong and is not in this record.** `4e960436` is merely the handoff path's most recent touch; the
sentence entered at `bad2e61f`, **14:11**, so the handoff **precedes** the clause by 2 h 05 min and
no site asserted the inference after its refutation existed. The error came from using
**first-landing (`log -S`) on one side of a comparison and the file's latest commit (`log -1`) on
the other** — a 4 h 28 min swing, from the same asymmetry this record already warns about in its
site table. **Measure both sides of a date comparison with the same instrument**, and for "when did
this text appear" that instrument is `git log -S` on the path, never `log -1`.

## 4b. What actually went wrong at the handoff, reported by the lane that owns it

The GBDT lane volunteered this against its own interest, and it is measured rather than relayed:
its `L1` paragraph is **verbatim** from `REPORT-20260920…` `L1` — `6.04% ± 0.39%`, `N = 40/80/160`,
exponent `0.000`, `20.91% → 7.57%`, exponent `1.467`, the same sentence — under a §2 header that
declares itself the completion report's limitation list. So the handoff **quoted a derived summary
of the measurement instead of the measurement.**

⚠ **And the artifact was already tracked, already cited by that chain, and names the limitation in
a FIELD NAME.** `state/SEED-EFFECT-20260920.json` landed at `128a5e7a` on 2026-09-20 13:01 — a day
before the handoff, and in the **same commit** as the `EVIDENCE` corollary it undercuts — and its
key is literally **`seed_effect_same_throws`**. *Same throws*: the nesting is in the name. Reading
it was one command away.

**That is a third failure mode, distinct from the two this record otherwise describes.** Not a
sweep that missed a site, and not a withdrawal that failed to propagate: a summary quoted in place
of the artifact it summarizes, where the artifact was tracked, cited and self-describing. **When a
record restates a number, cite the artifact and open it** — a derived paragraph cannot carry a
caveat its source never wrote down.

## 5. What this correction does NOT do

- It does not re-grade cause 3, and it does not touch `cause3_corr = 0.05`, fixed before production.
- It does not withdraw or qualify the adoption of `3d7465f6…`.
- It does not weaken `M1`. The `6.145%` FAIL is measured directly against the bound and does not
  depend on any statement about other ensemble sizes.
- It commissions no compute. A third member at a distinct offset still does not fit the cap
  (`EVIDENCE-20260920` §7), so the seed-pair distribution stays unmeasured; that is a disclosed
  limit, not a new task opened here.

**Co-Authored-By: Claude Opus 5 (1M context)**

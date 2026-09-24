# ISSUE-69 — A hand-maintained instrument was rebuilt against its own recorded defect three times before a mutation suite was written for it

**Severity:** MEDIUM. **Status:** OPEN. **Index row:** `KNOWN_ISSUES.md` row 69. **Updated:** 2026-09-23.

Moved here from the index on 2026-09-22 (self-round 52), text unchanged, because `KNOWN_ISSUES.md`
is an index and not a copy: its own header says so, it was compacted to 8,720 B at `1f714b7f` to
obey that, and this lane had grown it from 65,681 B (at `177af61b`) to 96,816 B, almost all of it in these thirteen rows.

## Detail

`probes/probe-20260922-ledger-reconciles.py` was created to stop the ledger's totals going stale. Independent review #7 found it **blind to a `⚠`-prefixed findings cell — a format used inside the very table it parses**. It was "hardened". Independent review #8 then defeated the hardened version **four more ways**, all fail-OPEN (exit 0 on a stale ledger): a quoted-but-stale `TOTAL` sentence — ⚠ **and this row's account of that mode was WRONG**: it said *"a **second** `TOTAL` … taken as authoritative because `search()` returns the first match"*, which is self-cancelling, and it measures that way. Placed **after** the live sentence the old guard exited 0 using the LIVE total (not the quoted one); placed **before** it, it exited 1 — a false alarm, fail-CLOSED. The real hazard is that a *quoted stale TABLE HEADER* above the live one was read as the ledger, which review #9 demonstrated and which is now refused on header multiplicity; a row indented 1–3 spaces silently ending the block; a `round\b` lookahead intended to skip the header but functioning as a silent-skip hole; and an agy row whose findings cell merely **mentioned** "NO VERDICT" being dropped — ⚠ **this row said it matched *"neither parser"*; it matched `NOVERDICT_ROW`, which was tried BEFORE `AGY_ROW`, and was counted as a recorded non-verdict rather than left unclassified**. A `noverdict` counter was assigned, incremented, and **never read**. **REPAIRED 2026-09-22** by extracting cell 2 and *adjudicating* it (exactly one integer → count; no integer + "NO VERDICT" → recorded non-verdict; **anything else → REFUSE**) and by requiring exactly one `TOTAL` match. **Now carries a mutation suite, COMMITTED at `docs/orchestration/probes/probe-20260922-ledger-guard-mutations.py`**, with a `--regressions` harness that patches the guard back to defects reviewers found (run it: exit 0 = every case behaved and the suite can fail). ⚠ **Its case count is deliberately not stated here** — this row stated *"currently 19"* in the same sentence as that pledge, and the suite had already grown past it. ⚠ **An earlier revision bound the phrase *"13-case"* to this committed path. The committed file has NEVER had 13 cases** — it was first committed at `a7ead894` and has grown since with every defeat; `13` was the scratch-directory version's count. Rewriting the composition while leaving the stale total is the topic-sentence-survives-its-retraction shape this same session catalogues twice elsewhere. ⚠ **THIS ROW ONCE CLAIMED THAT SUITE WHILE NO SUCH FILE EXISTED** — it had been run in a scratch directory and never committed, so the row prescribed a remedy and asserted it had been applied, against a tree that contained nothing of the kind. The ninth independent review measured that. An uncommitted result is not a result. ⚠ And the suite's FIRST run after commit exposed a defect **in the suite**: one "unparseable cell" mutation built `\| N (self) \| 0 \|`, a perfectly VALID row, so it never reached the guard and its exit 0 looked like a guard fail-open. **A mutation that does not mutate tests nothing.** ⚠ **AND REVIEW #9 DEFEATED THE REWRITE SIX MORE TIMES**, three of them one CLASS: the block ended at the first line not starting with `\|`, so **any** interloper inside the table (HTML comment, whitespace-only line, blockquote, wrapped row) truncated it and every row below vanished at exit 0. Review #8's *indented row* had been repaired as an INSTANCE, not a class — and the class is native here: ledger row 13 records this very table fragmenting. Also: a quoted stale ledger HEADER above the live one read as the ledger (the multiplicity hazard was closed for the TOTAL sentence and not for the header, one layer down); `re.findall(r"\\d+")` stripped the sign so `**-13**` read as `13`; and "NO VERDICT" was an unbounded sink that swallowed a real review whose findings cell read NO VERDICT followed by a note that it had found six defects. **All six closed and added to the suite.** ⚠ **And review #10 then defeated it again** (a first cell beginning `--`; an escaped pipe shifting the cell window), **and review #11b a fifth time**: its orphan check was narrower than the in-block parser, a NO VERDICT row could carry its findings in the NOTE cell, and a reconciling TOTAL could hide in an HTML comment. Each closed, each with a regression in the harness. **CHECK:** do not ship a guard for a format-bearing artifact without a mutation suite in that artifact's own formats; three rounds of "hardening" by inspection did not converge.

## Later defeats, and the rewrite (2026-09-22/23)

**Sixth (independent review #12b):** comment markers inside code spans swallowed the row between them; an
HTML entity rendered as one count and was read as another; a reconciling TOTAL hid in a link-reference
definition; four orphan label shapes and three NO VERDICT wordings escaped; and correct ledgers were
refused when a heading or blockquote followed the table.

**Seventh (independent review #13b):** an entity-encoded pipe moved a count into the wrong cell; rows
starting with an HTML tag or `#N` with no leading pipe were dropped; a hidden TOTAL in a multi-line
reference definition, a title attribute, or a comment shielded by stray backticks passed beside a visible
stale one; more NO VERDICT wordings escaped; and a list after the table, or a reviewer-keyed table in
another section, was refused.

**The rewrite.** All seven defeats share one cause: the guard used regular expressions to IMITATE GitHub's
renderer. It now parses the report with markdown-it-py and reads only what renders as visible text; the
table probe was rebuilt the same way. The mutation suite's regressions were rebuilt against marked anchor
lines in the new guard. ⚠ It said *"every redundancy it reports was checked by hand"*, and that was false: R3 was called redundant on the strength of a decoy case that did not reconcile, and review #14b showed R3 is load-bearing — a reconciling snapshot of the ledger in an earlier section passes under R3. With discriminating cases added, all twelve regressions are load-bearing. The guard's docstring states
its threat model: accidental staleness, not a proof against deliberately constructed input.

**Eighth, of the tests rather than the guard (independent review #15b).** The guard worked, but five of its
checks could each be deleted with every case green: the grand-TOTAL and independent-subtotal comparisons,
the 1..N order check, and the single-number rules for self and agy cells. *"All twelve regressions are
load-bearing"* was true only of the twelve that existed. The table probe's self-test also stayed green with
two of its checks deleted, because it asked only whether ANY finding appeared. Both are now tested structurally:
every `REGRESSION-ANCHOR` must have a regression and every regression must be load-bearing, or `--regressions`
fails; a patched guard that crashes or does not compile no longer counts as firing; and the self-test
compares exact kind sets and requires a shape isolating each kind. **CHECK:** "N of N load-bearing" says
nothing about checks that have no regression. Enumerate the checks from the instrument, not from the list.

**Ninth, the same shape one level up (independent review #16a).** The repair above enumerated checks
from the `REGRESSION-ANCHOR` tags, and the tags were themselves a list. Three `checks` entries carried
none: the last self round, the self addend count and the independent addend count. Deleting any of
them left all 95 cases green, while each changes a verdict. The sentence *"a patched guard that crashes
… no longer counts as firing"* was also false: only a patch that failed to COMPILE was skipped, and a
guard that raised at runtime still made its regression "load-bearing". Now the harness finds refusal
sites in the guard's CODE. Every `return 1`, `return 2` and `bad.append(` must sit under an anchored
`if`, and every `checks` entry must carry an anchor. Only a precondition regression (a `pre-` anchor,
whose removal can only turn a clean refusal into a crash) may fire through tracebacks alone; every
other regression must change some case's result without crashing. Independent review #16b, reaching the same two
defects on its own, added that "load-bearing" had never meant "fails open": R1 and R2 fire only through CONTROLs,
that is, fail-closed. The harness now prints both directions for every regression.

**Tenth (independent review #17b), and a change of method.** The site sweep matched exact text, so `return (2)`,
`sys.exit(2)` and `bad.extend` escaped it; it now reads the syntax tree. And the NO VERDICT wording rules, which
had drawn findings in reviews #11b, #12b, #13b, #14b, #15b, #16b and #17b, each one refusing a correct death
note or accepting a report, were DELETED rather than refined again. The ledger's one NO VERDICT row is pinned
by a digest of the whole rendered row. Any new or edited NO VERDICT row is refused until a human reads it and
pins it. **CHECK:** when a pattern rule keeps drawing findings from both directions, stop refining it. Replace
the inference with an enumeration that a human maintains.

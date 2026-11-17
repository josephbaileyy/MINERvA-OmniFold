# The Supplement's readability round 2 (2026-11-17): meaning reads

**Asked by** the director, relaying Joseph 2026-11-16. Applied by journal-editor on `style/supp-20261112`. The paper side
is director-helper-3's.

**What changed** (`supplemental_body.tex`, `main_supplement.tex`):
1. **S8.5's repaired arm.** It opens with the entry-check repair paragraph that leaves the paper's section 6.2, in
   Joseph's approved wording verbatim (`DECISION-20261116-joseph-paper-batch.md` item 14, with item 21's lowercase
   "stop"). It is keyed as in the paper (`ll5d-a1a2-keys`, `ll5d-a1a2-at`), and its self-pointer is dropped. Then come:
   - "The entry check that stopped the run was fixed in advance.", which read 4 asked for to keep the old arm's
     statement;
   - the full record, `ll5d-route-record`.
2. **The residual proxy.** S4.5 defines it, from the note's fig:gbdt-recovery caption (`sec_5d.tex` at `8342963c1`),
   with the note pointer kept as the source. This is the one Supplement test the note was still needed to understand.
3. **The coverage sentence.** It takes Joseph's item 3 wording, "Coverage of the reported intervals has not been
   validated", in the road map and in S9, as the paper now prints it.
   <!-- absence-ok: quotes Joseph's approved wording of the paper's stated limitation, not a search claim -->

**The reads** use gpt-6.1-sol at high effort, read-only, each with its prompt and its answer verbatim.

| read | what it read | verdict |
|---|---|---|
| `read4/` | items 1 and 2 at `20d0cbc49` | FAIL, two defects: the proxy's absolute values; S8.5 lost "fixed in advance" |
| `read5/` | the fixes at `b6129ba49` | PASS |
| `read6/` | item 3 at `096fcfeb5` | PASS |
| `read7/` | the definitions table's Descriptive entry, rewritten to follow the paper's new table 4 caption (director-helper-3's `7264f975a`), at `d2bd98a77` | FAIL: the timing read as the rerun's |
| `read8/` | the fix at `f6528e1c2` (the timing attaches to choosing the repair) | PASS |

**CITABLE FOR:** the wording as read against its cited sources.
**NOT CITABLE FOR:** any result; a locked wording.

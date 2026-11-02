# DECISION 2026-11-02 (latest) — Joseph: two refinements to the quadrant sentence, and merge #695

**Recorded by** the paper-tighten lane, as director.

**What led to it.**
- **The round.** #695 carries the #690 round: the quadrant sentence and Section IV in PRD style. Its REPORT and reading
  copy were saved for Joseph at `~/MINERvA-OmniFold-reads/quadrant-sec4-695/`.
- **The lane's flags on the decided sentence.** It raised two (REPORT points 1 and 2):
  1. **"a family of valid covariances" omits "one-parameter".** `FD-GENCMP-X-DECLARATION.md` A4 (:247, :389) says the
     paper would carry that qualifier. Both consults (#689) asked for it.
  2. **"χ² = 1.17–1.24" names the two ends of the bounded family.**
     - By convexity in r, the maximum (1.24) and p ≥ 0.87 hold over the whole family.
     - χ² may dip below 1.17 inside it.
     - That interior minimum cannot be computed from the committed blocks.

## Joseph's answers, verbatim

1. On "one-parameter":

   > Add 'one-parameter' (Recommended)

   sha256 of the text plus a final newline begins `e1e2c89fd8d0d3dd`.
2. On the χ² range:

   > χ² ≤ 1.24 (Recommended)

   sha256 begins `527b67f3cb5baad2`.
3. On merging #695, with these applied:

   > Merge now

   sha256 begins `521b75f5b38bd879`.

## What is decided

1. **The sentence reads** "…bounded within a one-parameter family of valid covariances, over which the agreement
   holds."
2. **The χ² clause reads** "…the four differences give χ² ≤ 1.24 for four degrees of freedom (p ≥ 0.87)…".
   - The value 1.24 is X's primary reading at r = 1, from `fd/xcov/run/k/k.json`.
   - The lower end stays in the note's table.
3. **#695 is merged** once these are applied and its checks pass. Its other contents need no further read by Joseph:
   - the Section IV consolidation;
   - the IV B rewrite;
   - the release of G1b:paper-g-09 from the r22 hold, by the director's ruling, because #690 item 2 supersedes it;
   - the standalone containment fix.
4. **Overleaf.** After the merge, the standalone Analysis-Note repository is re-synced. The procedure is
   RECORD-20261102-director-analysis-note-sync-8db2910b.md, from base `8db2910b`.

Nothing is submitted, deposited or tagged.

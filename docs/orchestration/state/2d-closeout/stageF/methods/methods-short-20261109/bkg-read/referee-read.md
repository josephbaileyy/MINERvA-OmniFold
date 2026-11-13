# The background wording: the PRD-referee reads and the meaning reads (2026-11-12)

Rows: `pairs.tsv` (export.py, base 45c1ea429). PRD-referee reads were done by an independent general-purpose subagent
with no tools, working from facts stated in its prompt. Meaning reads were done by an independent general-purpose
subagent, read-only, given the records and not the conclusions. The reports are kept as returned, including their
reasoning. Where the text was rebased, the line numbers are those of each read's working tree.

## PRD-referee read 1 (on the director's first wording)

Findings, condensed from the report:
- Remove the 0.35 % from the paper everywhere, both the S1 sentence and Table S1's row. It describes a template that
  was not used. "As written, the pair reads either as an error or as an unexplained jump." If a 1A number is wanted,
  use 2.74 %.
- Define the template by its content, with no caveat: "all selected simulated events that are not in-phase-space
  signal".
- S4's "selected simulation outside the signal phase space" is inaccurate as the umbrella term. A neutral-current
  event can have kinematics inside the phase space.
- "Any" suggests the piece is small, which the count reconciliation contradicts.
- "This paragraph does not split that total …" is the authors talking about their own text. Delete it.
- "In an earlier (April) version of the event loop" reads as internal history.
- Use "run period" throughout, or define "playlist" once.

## Meaning read 1

- M001 (S1 :25) DEFECT: the unchanged "is treated separately" and the present-tense "0.35 %" contradict the changed
  clause, and the :24 sync comment was stale.
- M002 (Table S1) DEFECT: the unchanged out-of-phase-space row ("treated separately") contradicts the template row. The
  0.35 % leaves out out-of-fiducial ν_μ CC. The reader found RUN_LOG :1061: "`hBkgReco2D` integral 1,788 → 9,782 (+8 k
  weighted; the 48 k "Set E" reco-fakes are now correctly subtracted from data …)". The May 1A template, k·B in the
  grid from work_proxy, is 9,781.53, now pinned as l_rows.json bkg_42.per_playlist_template_sum.
- M003 (S4) OK, with a note that "signal phase space" is used nowhere else.

## The director's rulings, then the final text

- S4: "all selected simulated events other than signal inside the phase space".
- Table S1: the 0.35 % row deleted. <!-- absence-ok: quotes table S1's scope clause; the split is unmeasured here because the May files lack the truth branches (split-20261112, exit 6), and C-BKG measures it --> The template row says its split "is not measured here", and the 82 % is not
  printed. The out-of-phase-space row says "routed into the background template and subtracted with it".
- The S1 paragraph desynced from the note, with the PRD wording.

## PRD-referee read 2 (final text)

- S1: change requested. Say "selected events", not "reconstructed events". Replace "The overall multiplicative
  correction … is their total", which conflates B_b with the per-bin weight, by a sentence on N_bkg(b) entering
  w_pur(b). Check that the note citation describes the routing. (It does: sec_method.tex:17.)
- Table S1: ACCEPT. <!-- absence-ok: quotes table S1's scope clause; the split is unmeasured here because the May files lack the truth branches (split-20261112, exit 6), and C-BKG measures it --> Say "selected data events". Keep "its split … is not measured here", because without it a reader
  would assume the 2.91 % is mostly genuine background.
- S4: ACCEPT. Use "background template", not "background prediction".
- Final confirmation: ACCEPT. Keep "playlist" for the twelve units. The 2.72–3.23 % range is per playlist
  (l_rows.json per_playlist, 12 entries).

## Meaning read 2 (final text)

- First pass:
  - The S1 paragraph, table rows :45-46 and S4 :223 are OK. The routing holds under both readings of the records.
  - DEFECT: "run period" collides with the Supplement's three playlist groups at :478 and :481. Reverted to "playlist".
  - DEFECT: :229 cited S1 for "largest where backgrounds concentrate", which S1 no longer gives. The pointer is removed.
- Final confirmation: every item OK, and no "background prediction" remains.

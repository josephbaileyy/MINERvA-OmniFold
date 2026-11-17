# Two Supplement corrections from the cross-document check of 3d4d33144 against note 8342963c1 (2026-11-16)

The director routed these as corrections of factual mismatches with the note.

1. Section S5's run-period block, the timing of the rule for adding it. The Supplement said the rule was fixed
   "before the block's numbers were read". The governing record, FD-CT-5B-AUDIT-DECLARATION.md (measurement-paper/
   5d-community-20261024/), shows otherwise. Its :52-58 list the reported numbers read before the stop condition was
   written. Its :30 says no audit quantity had been computed. Its :71-73 say clauses N and R were not expected to
   fire. The note says the same. The Supplement now says that the rule was fixed after the block's reported numbers
   had been read, but before any of the measurements that decide it had been computed, and that its second and third
   requirements were expected to hold.
2. Section S3: the citation for the beam-axis convention's effects pointed to the note's section 8.1
   (sec:eavailw-axis). Those effects are in section 8.2 (sec:eavailw-definitions, sec_eavailw.tex:70 at 8342963c1),
   so the citation now points there. The W-convention citation stays on 8.1. note_release_labels.tex is regenerated
   at 8342963c1 and gains that label.

Read 1 (gpt-6.1-sol, high effort, read-only) PASSed both, quoting the declaration's lines. Its one low-priority
finding, that the third requirement lacked the note's "in the median replica", is applied ("in the median replica,
at least half of the replica-built block's variance"). It is a qualifier the note carries; it adds no claim.

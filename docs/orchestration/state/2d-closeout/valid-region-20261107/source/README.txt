The ATLAS source read for the valid-region declaration (DECLARATION.md section 1). Read 2026-11-07 by the
valid-region lane (session director-helper-2). Public documents, fetched with curl. The PDFs are not committed;
their digests, the extraction tool and verbatim excerpts with line numbers are.

1. The published Supplemental Material of Phys. Rev. Lett. 133, 261803 (2024): the "User Guide".
   URL     https://journals.aps.org/prl/supplemental/10.1103/PhysRevLett.133.261803/SM.pdf
   (linked from https://journals.aps.org/prl/supplemental/10.1103/PhysRevLett.133.261803)
   sha256  efb5beef2a77a11600b860c18060f1c3b4370b7e31d4d3061376d07d22999478   (6 pages; PDF CreationDate
           Tue Nov 12 11:17:32 2024 PST)
   text    pdftotext 25.06.0, `pdftotext -layout SM.pdf sm.txt`; sm.txt sha256
           fccaa459336540a694ebef03591b932a1987e58b152d689290d89590a6da59cc (844 lines)
   excerpt SM_section2_lines25-75.txt: sm.txt lines 25-75 verbatim, "2 Usage recommendations", each line
           prefixed with its sm.txt line number and a tab.

2. The Letter with the same supplement appended, arXiv:2405.20041v3 (7 Feb 2025, "published in PRL").
   URL     https://arxiv.org/pdf/2405.20041   (v3 at the time of reading)
   sha256  d845e25742f682e64494b4856c6d7be0ae5722744773c260d7118054c939cfff
   text    `pdftotext -layout`, 2696 lines. The supplement's sections 1-2 there are the same text as item 1
           (compared with whitespace squeezed; the only differences are page furniture).
   excerpt arXiv-2405.20041v3_letter_excerpts.txt: lines 211-226 (the "unfolding prior" and hidden-variable
           uncertainties) and 408-440 (the pseudo-data validation), verbatim, numbered as above.

3. Checked and not used: "A Practical Guide to Unbinned Unfolding", arXiv:2507.09582,
   sha256 8d954a8c4119a7a70033474715224af0c0d2d63b46dea6bffad9fd9aae78cdd6; sections F-G (uncertainties,
   validation). It states no prior-spread validity rule either.

THE FINDING THIS RECORDS (re-runnable from item 1):
   pdftotext -layout SM.pdf - | grep -c -i -E 'prior|spread'      -> 0
   The User Guide's validity rules are its section 2 items 1-5 (excerpt lines 34-75). None of them compares a
   bias spread with a prior spread. The Letter uses "unfolding prior" only as an uncertainty source (excerpt
   lines 218-224). The repo's own reading of the same paper agrees:
   docs/orchestration/state/2d-closeout/stageF/methods/register-prd-study/notes/2405.20041.md:20-23.

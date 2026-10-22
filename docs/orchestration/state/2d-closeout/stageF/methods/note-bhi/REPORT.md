# REPORT, batch bhi: App. G (`app_release.tex`) and App. H (`app_codebase.tex`)

Worktree `S/wt-note-bhi`, branch `stageF/note-register-bhi-20261021`, base origin/main b603f9cf. Only
`docs/analysis-note/app_release.tex` and `docs/analysis-note/app_codebase.tex` are modified (`git status` below). No
commits. Diff: `bhi.diff`. Per-paragraph changes: `changes.md`. Ledger: `ledger.md`, checked by `check_ledger.py`.

## Word counts

| | before | after |
|---|---:|---:|
| `app_release.tex`, `wc -w` source | 1,495 | 1,794 |
| `app_codebase.tex`, `wc -w` source | 259 | 306 |
| prose words, comments and commands stripped (G / H) | 1,338 / 239 | 1,496 / 286 |
| rendered words, App. G + App. H in `main_note.pdf` | 1,723 | 1,928 |

The appendices grew. Most of the growth is the new paragraph "Contents and use" (what RC7 holds, how to run it, what
counts as a pass). The brief lists those as things a reader needs from G, and G did not print them. The rest is the
backends and the event-loop outputs spelled out in App. H, and section pointers. Page count is unchanged at 119.

## Moves to the records

None. No number, limitation or disclosure left the posted note. Nothing was cut except history adverbs ("now",
"still"), the phrase "retaining the code name as provenance", and the untrue "named in italics throughout the
note". The facts behind each of these still print (ledger W2, K1, K7).

## Qualifiers the guardrail kept

- "RC7's own verifier ... every figure number **that it checks**". This sentence is protected anyway, and it
  also keeps the claim scoped.
- "The broader result package must contain every item below; **RC7 does not contain all of them**". Without this,
  the check marks could be read as saying that RC7 delivers the schema.
- "A fixed identity says which object is meant; **it does not qualify the object scientifically**". This is the
  old "Fixed identities do not supply missing scientific qualification", now placed beside the check marks it
  limits.
- The preservation record "**dated 2026-10-10**", which "**holds no preservation copy**" of the 489 simulation
  AnaTuples. The copy status is a fact about that record, not a permanent one.
- "Neither the checksums nor the preservation copies are a public deposit, and they do not make the full event-level
  analysis reproducible from the small candidate package."
- Worked example: "should let a reader run" keeps the original "should" and is not raised to "must". The "Do not
  check a rank" and "Do not check the sign" instructions are kept, with their reasons.
- G.1 paragraph 2 is verbatim. Its "but not", "Nor does it", the multiplier-scan exception and the "independent
  reader" are all unchanged (see Q4 for why it is verbatim).

## What the paper relies on (ledger DA1-DA5, all passing)

- DA1: 2,374 input files identified by SHA256 checksum, in the record cited in App. G (`AnaTuplePreservation2026`).
- DA2: App. G states what each part does and does not reproduce. The intro now says so explicitly.
- DA3: the multiplier-scan exception (verbatim).
- DA4: the earlier production of the AnaTuples (verbatim).
- DA5: RC7's 2D curve is the exact-split one, and the article's 2D figure was regenerated separately.
- The paper's own pdftotext is byte-identical to the base build. Its label numbers are unchanged.

## Protected text

- H1: the deposit snapshot hold is byte-identical.
- H2: the RC7 own-verifier sentence is byte-identical. It still prints in "Release status", in a different
  subsection from the RC1 replay (G.1).
- H3: neither file contains a `\pubhold`, before or after.

`check_ledger.py` checks all three with raw-byte probes against both `base/` and the worktree.

## Open questions

1. **`records-move-ledger.md` must be updated when this lands.** I was not allowed to edit it.
   - With the repository's ledger, `check_note_records.py probe` FAILS with 15 failures. Ten are P5: reader
     paragraphs of G and H that I rewrote, whose hashes the ledger does not list. Five are P7: probes L1, L2, L4,
     L5 and L6 quote text I changed (digest -> checksum, rollup -> aggregation step).
   - `records-move-ledger.patch` (34 lines) updates those five probes and adds ten REWRITE rows, L-bhi1 to L-bhi11
     (L-bhi5 is not used).
   - With the patched ledger, probe and self-test both PASS (outputs below). build_all.sh does not run this probe.
2. **The RC1 "independent reader".** RC1-REPLAY-RECEIPT-20261006.md says this was "a fresh Opus 5.5 agent acting as
   an outside reader", with no repository access. I kept the note's wording. The author may want to say this
   plainly.
3. **Package paths and the snapshot hold.** The hold says that code paths in this appendix refer to the repository
   snapshot. The new `code/verify_rc.py` is a path inside the package, so the text says "run from the unpacked
   package". Please check that this reads clearly next to the hold.
4. **Not checked by the verifier, and not printed.** RC7-README.md:111-117 says that `verify_rc.py` does not check
   `observed_jitter_p`, the rounding-stability statement for NuWro's shape test. The protected sentence is scoped
   to "every figure number that it checks", so nothing printed is false. Whether to state this limitation is the
   author's call.
5. **G.1 paragraph 2 was left verbatim.** `check_note_records.py --self-test` plants its reader-paragraph edit by an
   exact match on "The pseudo-experiment products are archived" in this paragraph. Rewriting the paragraph would
   make the self-test fail. A later pass could rewrite it ("Nor does it", the stand-alone 2.3 GB sentence), but
   only together with a change to the self-test's anchor.
6. **"Collaboration storage"** (pre-existing). The source record calls this the CFS copy, which is NERSC project
   storage. I did not change the wording.

## Check outputs (quoted)

`bash S/plain-language/build_copy.sh note-bhi S/wt-note-bhi` (font warnings omitted):
```
build_all rc=0  log=/private/tmp/claude-501/-Users-josephbailey-local-research-MINERvA-OmniFold/ee772d13-75a3-4217-970c-8badb94dd2ba/scratchpad/plain-language/builds/note-bhi/build.log
  OK   main_records.pdf written by this run; no unresolved references and no multiply-defined labels in main_records.log after 1 latexmk invocation(s):
SELF-TEST :: PASS
RESULT :: PASS :: head=unknown tree=unknown scope=? (tree_state.py helper not found) mode=strict products=main_records.pdf@sha256:e54807322c24639f72a93e054f346a0e36e7a981c17b38b99ae927ffa03f58b8(fresh),pet_note.pdf@sha256:950ba670e7cf3a4e1e1b7305c44195225b49b9daa2abc62cc96724364eb59d70(fresh),main_note.pdf@sha256:44edb1bfa5fc456e6b1866c9619c2594661af6499b314b6112aeb769bb2d1890(fresh),main_paper.pdf@sha256:a2706a4ef9cc9f71d636ffe2891efca9cd7f7c9ae2c70965c46fab8700d13d7a(fresh),main_primer.pdf@sha256:113385afce589f25602a4370b109b26c6732bbdae2e670edc4eedba48794725c(fresh)
  gzip receipt: PASS (equal to plain=True, missing raises=True)
SELF-TEST :: PASS (18 perturbations rejected)
SEC4-RECEIPTS :: PASS (15/15)
main_note pages=119
main_paper pages=13
main_primer pages=15
pet_note pages=26
main_records pages=21
```

Post-build checks (`checks.out`): logs, `??`, the paper text against `builds/rec3` and against an origin/main base
build (`note-bhi-base`), label numbers, swallowed text, the pin on the real worktree, and RECORDS-MOVE:
```
BODY-POINTERS SELF-TEST :: PASS (25 cases: the appendix silent; 8 patterns fire in a body file and in a nested body file; a macro-printed digest fires; 7 legitimate forms silent)
BODY-POINTERS :: PASS (0 internal pointers in 17 body files)
RECORDS-PIN SELF-TEST :: PASS (9 of 9 cases as expected: a good pin passes; a branch, a non-ancestor, an unknown sha, a missing tag, a missing heading and no citation fail; the standalone and no-git layouts skip)
RECORDS-PIN :: SKIP -- /private/tmp/claude-501/-Users-josephbailey-local-research-MINERvA-OmniFold/ee772d13-75a3-4217-970c-8badb94dd2ba/scratchpad/plain-language/builds/note-bhi/repo/docs/analysis-note is not in a git checkout (an export or a scratch copy); enforced by the canonical build
  ok   records.pdf carries 64/64 struck literals (positive control OK)
  ok   pet-note.pdf carries 5/5 struck literals (positive control OK)
  ok   note.pdf: 0 of 69 struck literals
  ok   paper.pdf: 0 of 69 struck literals
  ok   primer.pdf: 0 of 69 struck literals
main_note: undefined-ref lines=0 multiply-defined=0 ??=0
main_paper: undefined-ref lines=0 multiply-defined=0 ??=0
main_primer: undefined-ref lines=0 multiply-defined=0 ??=0
pet_note: undefined-ref lines=0 multiply-defined=0 ??=0
main_records: undefined-ref lines=0 multiply-defined=0 ??=0
PAPER pdftotext byte-identical to builds/rec3 main_paper.pdf
PAPER pdftotext byte-identical to own origin/main base build
main_primer pdftotext identical to base build
pet_note pdftotext identical to base build
main_records pdftotext identical to base build
main_note: 184 labels base, 184 after, number differences 0
main_paper: 34 labels base, 34 after, number differences 0
main_records: 22 labels base, 22 after, number differences 0
main_primer: 3 labels base, 3 after, number differences 0
pet_note: 37 labels base, 37 after, number differences 0
swallowed_text: flagged 0
RECORDS-PIN :: PASS -- 81 citations, 35 tag and 62 heading references, pinned to 7986273b169e0c759f3156ddb9f784a51f0d7f72, 29 tags and 55 headings at the pin
-- RECORDS-MOVE with the repository ledger (expected: fails only where this batch rewrote reader text):
RECORDS-MOVE :: FAIL (27 labels, 29 tags, 97 struck bodies, 30 paths, 84 record and 20 reader paragraphs, 44 App. G pointers; 15 failure(s))
-- RECORDS-MOVE with records-move-ledger.patched.md:
RECORDS-MOVE :: PASS (27 labels, 29 tags, 97 struck bodies, 30 paths, 84 record and 20 reader paragraphs, 44 App. G pointers; 0 failure(s))
RECORDS-MOVE SELF-TEST :: PASS (delivered move silent: True; 12 of 12 planted defects fired their probe)
 M docs/analysis-note/app_codebase.tex
 M docs/analysis-note/app_release.tex
```

`python3 check_ledger.py S/wt-note-bhi --plant`:
```
  planted -> PLANT-N: NOT FOUND in app_release.tex: '2,375 inventoried AnaTuple input files'
  planted -> PLANT-X: STILL PRINTED in app_release.tex: "RC7's own verifier"
  planted -> PLANT-B: PROTECTED text not byte-identical (after, base) in app_release.tex: "RC7's own verifier, run on the packaged files in an empty directory, r"
plant test: PASS (all 3 planted probes fail)
ledger rows 66, probes 101, failures 0
```

## Round 2: director fixes F1-F8 (REVIEW.md)

The director reply carries the details. F2 was applied as the source shows, not as worded: RC7 replays reading (a),
whose variant shifts are recomputed on all draws (RECORD-20261006-s5p-lost-seed-recovery-resolution.md:57; phaseC.txt
"(a) evaluate" = resolved-evaluate.json). F4: no packaged script computes observed_jitter_p.

```
build_all rc=0  log=/private/tmp/claude-501/-Users-josephbailey-local-research-MINERvA-OmniFold/ee772d13-75a3-4217-970c-8badb94dd2ba/scratchpad/plain-language/builds/note-bhi/build.log
  OK   main_records.pdf written by this run; no unresolved references and no multiply-defined labels in main_records.log after 1 latexmk invocation(s):
SELF-TEST :: PASS
RESULT :: PASS :: head=unknown tree=unknown scope=? (tree_state.py helper not found) mode=strict products=main_records.pdf@sha256:b8e0509876cabf4e200376246df728270d52e0a9e8d93652426b0e4f8445aa9e(fresh),pet_note.pdf@sha256:ce868c4183c4994e217552f96a628eb04545d5887b59c0b3f5dcd1cb4c27cbff(fresh),main_note.pdf@sha256:972768f8bec12379e8ab3efe6942d3e00d7028c05ce09ef471444c7abd386a00(fresh),main_paper.pdf@sha256:f44dd6496ae24275888effbf2d3a07edcf4e13186e33f94b223bfd2c2f203b66(fresh),main_primer.pdf@sha256:e8c1d347a44c6d028e70e6462f07d375e8d399e0a64d6fc8c69e6e0bd889618a(fresh)
  gzip receipt: PASS (equal to plain=True, missing raises=True)
SELF-TEST :: PASS (18 perturbations rejected)
SEC4-RECEIPTS :: PASS (15/15)
main_note pages=119
main_paper pages=13
main_primer pages=15
pet_note pages=26
main_records pages=21
BODY-POINTERS :: PASS (0 internal pointers in 17 body files)
RECORDS-PIN :: SKIP -- /private/tmp/claude-501/-Users-josephbailey-local-research-MINERvA-OmniFold/ee772d13-75a3-4217-970c-8badb94dd2ba/scratchpad/plain-language/builds/note-bhi/repo/docs/analysis-note is not in a git checkout (an export or a scratch copy); enforced by the canonical build
  ok   records.pdf carries 64/64 struck literals (positive control OK)
  ok   pet-note.pdf carries 5/5 struck literals (positive control OK)
  ok   note.pdf: 0 of 69 struck literals
  ok   paper.pdf: 0 of 69 struck literals
  ok   primer.pdf: 0 of 69 struck literals
main_note: undefined-ref lines=0 multiply-defined=0 ??=0
main_paper: undefined-ref lines=0 multiply-defined=0 ??=0
main_primer: undefined-ref lines=0 multiply-defined=0 ??=0
pet_note: undefined-ref lines=0 multiply-defined=0 ??=0
main_records: undefined-ref lines=0 multiply-defined=0 ??=0
PAPER pdftotext byte-identical to builds/rec3 main_paper.pdf
PAPER pdftotext byte-identical to own origin/main base build
main_note: 184 labels base, 184 after, number differences 0
main_paper: 34 labels base, 34 after, number differences 0
main_records: 22 labels base, 22 after, number differences 0
swallowed_text: flagged 0
plant test: PASS (all 3 planted probes fail)
ledger rows 69, probes 107, failures 0
RECORDS-PIN :: PASS -- 81 citations, 35 tag and 62 heading references, pinned to 7986273b169e0c759f3156ddb9f784a51f0d7f72, 29 tags and 55 headings at the pin
-- RECORDS-MOVE, repository ledger:
RECORDS-MOVE :: FAIL (27 labels, 29 tags, 97 struck bodies, 30 paths, 84 record and 20 reader paragraphs, 44 App. G pointers; 16 failure(s))
-- RECORDS-MOVE, patched ledger:
RECORDS-MOVE :: PASS (27 labels, 29 tags, 97 struck bodies, 30 paths, 84 record and 20 reader paragraphs, 44 App. G pointers; 0 failure(s))
  fired  edited reader paragraph              -> P5 READER paragraph dbf0faa3ea9a neither in the note nor in the ledger as REWRITE: 'Point-cloud (PET
RECORDS-MOVE SELF-TEST :: PASS (delivered move silent: True; 12 of 12 planted defects fired their probe)
-- self-test on the origin/main tree, moved anchor:
RECORDS-MOVE SELF-TEST :: PASS (delivered move silent: True; 12 of 12 planted defects fired their probe)
 M docs/analysis-note/app_codebase.tex
 M docs/analysis-note/app_release.tex
 M docs/analysis-note/check_note_records.py
```

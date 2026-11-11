# Recheck referee round on the short methods paper (2026-11-11)

**What was read:** #977 at `2bfb1410cc581e42b8a2106403a7dc7bfe822542`, after the style batch, the four meaning fixes,
the "full record" rewording and the §7 hold. It was blinded by make_rater_copy.sh and make_supp_rater_copy.sh at that
commit (director-helper-3). The manuscript was 11,065 words and the Supplement 15,818. The second five-observable
coverage test (LL5D) still printed as a placeholder.

**The prompt** is the interim and confirming rounds', byte-identical (sha256 `27024dcc…`), so the scores compare
directly.

**Reader:** `gpt.txt`, gpt-6.1-sol, high, read-only, ephemeral, on codex-school, at Joseph's request. A first attempt
exited 1 before reading, because codex refused a non-git working directory; it was rerun with `--skip-git-repo-check`
and nothing else changed. `run-header.txt` records the successful run only.

**Score:** 5/10, major revision, the same as the confirming round's GPT reader. It judges the paper publishable in JINST
as a diagnostic study after revision, finds no limitation disqualifying, and recommends no other journal.

**A known defect of the blinded copy.** The Supplement's Figure S2 caption is absent from `supplement-recheck.blind.txt`
although the figure prints in the Supplement PDF at the same commit (`supplement-2bfb1410.pdf`, sha256 `f83d73f2…`).
So the reader's minor issue 10 ("Figure S2 is cited but is not present") is an artefact of the blinding, and its S10
remarks were made without that figure.

**What the director checked:** minor issue 11's "sections 6.2 and 6.2" prints in the paper PDF at `2bfb1410` (a real
defect).

## CITABLE FOR / NOT CITABLE FOR

- **Citable for:** what the reader reported.
- **Not citable for:** any finding; any paper sentence; Joseph's decisions.

Nothing is submitted, deposited or tagged.

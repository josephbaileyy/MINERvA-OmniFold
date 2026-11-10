# Confirming referee round on the short methods paper (2026-11-10)

**What was read:** #977 at `53514740938452b230debe132fe4ae6b16e4ddb0`, after the interim round's groups A (batches 1–2),
B and C, the V-PRIOR withholding and the carbon-only generator figure. It was blinded by rater-calibration's
make_rater_copy.sh and make_supp_rater_copy.sh at that commit. The manuscript was 9,946 words and the Supplement 16,704.
The second five-observable coverage test (LL5D) still printed as a placeholder.

**The prompt** is the interim round's, byte-identical (sha256 `27024dcc…`), so the two rounds' reports and scores
compare directly.

**Readers:**
- `gpt.txt`: gpt-6.1-sol, high, read-only, ephemeral, on codex-school. codex-school2 is reserved for Joseph's note
  rounds.
- `claude.txt`: a fresh Claude Opus session (claude-school), blind, with no write, shell or web tools. It replaces
  Gemini, because Antigravity is out of usage.

**Scores:** GPT 5/10, Claude 4/10, a mean of 4.5, the same as the interim round (GPT 5, Gemini 4). Both recommend
major revision. Both judge the paper publishable in JINST as a diagnostic methods study after revision, and neither
finds any limitation disqualifying for that kind of paper.

**Follow-up (2026-11-10, at Joseph's request):** the director resumed the Claude referee's saved session
(`407b8304…`, same flags) with `followup-ens1.txt`, a neutral question on its item M5 giving both options for the
ensemble deficit's size. Its answer is `claude-followup-ens1.txt`. Decided in
`DECISION-20261110-joseph-ens1-deficit-licence.md`.

## CITABLE FOR / NOT CITABLE FOR

- **Citable for:** what each reader reported.
- **Not citable for:** any finding; any paper sentence; Joseph's decisions.

Nothing is submitted, deposited or tagged.

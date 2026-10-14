# DECISION 2026-10-14 — Joseph's answers to the Stage D inputs questions Q1–Q7

**Recorded by** the paper-tighten lane, as director. The answers are Joseph's, given in that session on
2026-10-14 in reply to the questions in
[`state/2d-closeout/stageD-inputs/REPORT.md`](state/2d-closeout/stageD-inputs/REPORT.md) §10 (main `faa02f93`).
The answers are quoted verbatim below.

**CITABLE FOR:**
- Joseph's answers, and what each one starts or leaves open.

**NOT CITABLE FOR:**
- a compute grant;
- a Stage D start;
- an endpoint choice (Q7 is open);
- any message to MINERvA, NERSC or a coauthor.

Answers 4 and 5 are "for now" and can be revisited.

| Q | the question, in short | Joseph's answer (verbatim) | what it means, and what follows |
|---|---|---|---|
| Q1 | ask MINERvA for a second ME-FHC MC production? | "I am pretty sure MINERvA has released all of their data to https://minerva.fnal.gov/opendata/" | No request to MINERvA. If the release is all there is, the only candidate second production is the **current** open-data release, so Q1 reduces to Q2 |
| Q2 | is the current open-data MC, with our filenames but 1.243–1.244× larger (OI-55), new events or a reprocessing of ours? | "sure try this" | Started 2026-10-14. One read-only measurement reads the `Truth` trees of a few current public files over xrootd: `fndca1`, the path in `2d-unfolding/download_playlist.sh`. It joins them on `K = (mc_run, mc_subrun, mc_nthEvtInFile)` against our copies, with no Slurm and no full-file copy. The member-directory route (`gregork/Minerva`) is not used. The result is recorded separately |
| Q3 | who holds the assessment samples and the fold salt? | "there is probably some way I can do this with keys and encryption" | Direction: Joseph is the custodian, with the separation enforced cryptographically. A design is still owed. The constraint it must meet is in the note after this table |
| Q4 | an alternative generator with detector simulation from MINERvA, or the limited alternative? | "lets just accept the limited version for now" | Stage D input 3 is the **explicitly limited** route of the Stage D REPORT §6.2. A fresh, uninspected truth-level configuration on CH, for example GENIE v3, is applied as a truth reweight under the nominal response. It is partial evidence: one response only. Its first step is a ≤ 0.2 core-h throughput pilot of 10⁴ events, which needs a priced request to the director. Nothing is launched by this record |
| Q5 | the MAT universe law as a convention, or external validation of it? | "declare them a convention for now" | The systematic universe law is a **declared convention**, with no physical-adequacy claim. Any Stage D statement that rests on it must say so. Input 2's adequacy stays UNAVAILABLE by declaration, not by omission |
| Q6 | the unsent preservation drafts | "where is the draft again?" | [`docs/publication/corrections-20261008/DRAFT-20261008-anatuple-preservation-requests.md`](../publication/corrections-20261008/DRAFT-20261008-anatuple-preservation-requests.md): draft A (NERSC HPSS, about 11 TiB) and draft B (the MINERvA open-data contact). Both are unsent. Its figures must be re-measured before sending. Draft B's question, whether the earlier production is retained, depends on Q2's answer |
| Q7 | the plan §6 two-outcome decision | "tbd" | **Open.** The full endpoint is neither closed nor replaced. No narrower claim is adopted |

**Q3: the constraint a key-based design must meet.** Every lane runs as Joseph:
- as `josephrb` on the cluster;
- as his user on the Mac where the Claude sessions run.

So no key or salt stored in a file those accounts can read stays secret from the lanes. The key or salt must sit
behind something only Joseph can open: a passphrase he types, a hardware key, or a device the sessions cannot reach.
It may enter a computation only when Joseph runs a step himself. A commitment, the published sha256 of the salt,
proves which folds were fixed before development without revealing them.

**The limit of encryption here.** The AnaTuples themselves are readable by every lane. So encryption can keep the
fold assignment and the assessment results hidden until reveal, but it cannot hide the events. The protection is
therefore commitment plus withheld membership, not secrecy of the data.

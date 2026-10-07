# Proposed AI-use disclosure (APS policy): FOR THE AUTHORS TO APPROVE OR REWRITE

**Status:** proposed text only; the article contains no AI disclosure yet.

**The APS policy** (journals.aps.org/authors/appropriate-use-ai-tools, fetched 2026-10-06):
- authors must disclose "AI tool name and version," "How the AI assisted," and "How the authors directed and
  verified the AI output";
- research use goes in the methods, figure generation in the captions, and other substantive use in the
  Acknowledgments;
- an AI "cannot be listed as an author".

**What the repository records** (a census with stated limits, not a complete inventory; see
`docs/orchestration/CAMPAIGN-REVIEW-20260929.md` §2 on attribution limits):

| source | tools |
|---|---|
| commit Co-Authored-By trailers on `main` (`4b21cef6`, 4,466 commits) | Claude Opus 5 (about 2,200), Opus 5.5 (about 760), Opus 4.8 (121), Fable 5/5.1 (69), Opus 4.7 (20) |
| commit messages | "Codex" in about 120 |
| the campaign review | OpenAI reviewers ("Astra High", `gpt-6-astra`), and a Gemini-based delegate whose output was excluded |

**Substantive uses** (each is in the APS list): analysis and pipeline code that affects results; statistical
analysis design and implementation; orchestration of the computing campaigns; independent recomputations and
reviews; figure generation; literature synthesis; manuscript drafting.

**Proposed wording, to be placed in the Acknowledgments with a pointer from the method section:**

> The analysis code, statistical procedures, computing campaigns, independent recomputations and reviews, figures
> and manuscript drafts were produced with substantial assistance from AI language-model tools: Anthropic Claude
> (Opus 4.7, 4.8, 5 and 5.5; Fable 5 and 5.1) and OpenAI Codex models, including those used for independent
> review. The authors directed this work through written specifications fixed before each study. Results were
> accepted only after verification against committed evidence: predeclared criteria, independent recomputation by
> separately written code (for example, the joint-test evaluation and the lost-seed recovery), and independent
> read-only reviews. AI tools are not authors. The authors take responsibility for the content.

**Authors to decide:**
- whether the tool and version list is complete and accurate (the census above is incomplete by construction);
- placement;
- whether figure captions need individual statements, because most figures were produced by AI-written code.

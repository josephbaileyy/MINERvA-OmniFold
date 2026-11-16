# DECISION 2026-11-14 — Joseph: the AI-use statements are revised for accuracy

**Recorded by** the paper-tighten lane, as director.

## Joseph's words, verbatim

> yes you can make recommendations and edit the AI use statement to be as accurate as possible

(`40b161d5401dc895`, the sha256 of the text plus a final newline), and, answering the director's three questions:

> say the first author for now. groks version was Grok 4.7 and sonnets version could have been either sonnet 5 or 5.5 to my knowledge

(`c23237e29e3186ce`).

## What led to it

The director compared the note's full statement (main_note.tex, after the acknowledgments) and the paper's condensed
one (main_paper.tex acknowledgments) with a census of the repository's records at origin/main:

- **Anthropic Claude.** The commit co-author trailers name Opus 4.7, 4.8, 5 and 5.5, and Fable 5 and 5.1.
- **OpenAI GPT.** The records name GPT-5.5, GPT-5.6 Sol and Luna, GPT-6 Astra, GPT-6 Sol and GPT-6.1 Sol.
- **Google Gemini, through Antigravity.** gemini-3.1-pro-high and gemini-3.8-flash-high.
- **xAI Grok.** Its version is not recorded; Joseph supplied it.
- **Claude Sonnet referee reads.** The version is not recorded; Joseph gave it as 5 or 5.5.

The current statements omit Gemini, Grok, Sonnet and GPT-6 Sol. They also say that specifications were fixed
"before each study", which descriptive studies contradict. And they don't disclose that routine operational decisions
were delegated to a coordinating AI agent.

## What is decided

Both statements are replaced with the wording below. Each goes through a meaning read against this census, and
then into Joseph's batch.

**The note's full statement:**

The analysis code, statistical procedures, computing campaigns, independent recomputations and reviews, figures, and
manuscript drafts were produced with substantial assistance from AI language-model tools: Anthropic Claude (Opus 4.7,
4.8, 5 and 5.5; Fable 5 and 5.1; Sonnet 5 or 5.5) through the Claude Code agent; OpenAI GPT models (GPT-5.5, GPT-5.6
Sol and Luna, GPT-6 Astra, GPT-6 Sol and GPT-6.1 Sol) through the OpenAI Codex agent; Google Gemini (3.1 Pro and 3.8
Flash) through the Antigravity agent; and xAI Grok 4.7. The first author set the scientific questions and approved
every claim and its wording. Each study was specified in writing before its results were read, unless it is labelled
descriptive. Routine operational decisions (reviewing code and job packages, approving computing jobs within budgets
the authors set, and merging records) were delegated to a coordinating AI agent under written rules, and each
decision is recorded in the analysis repository. Results were accepted only after verification against committed
evidence: criteria specified in advance, independent recomputation by separately written code (for example, the
joint-test evaluation and the lost-seed recovery), and independent read-only reviews, including reviews by models
from developers other than the one whose model wrote the work under review. AI tools were also used for
methodological discussion. The figures were drawn by plotting code from the analysis outputs; no image was generated
or edited by a generative-AI image tool. AI tools are not authors. The authors take responsibility for the content.

**The paper's condensed statement:**

AI language-model tools (Anthropic Claude, OpenAI GPT, Google Gemini and xAI Grok models, used through the Claude
Code, OpenAI Codex and Antigravity agents) gave substantial assistance with the analysis code, statistical procedures,
computing campaigns, independent recomputations and reviews, figures, and manuscript drafts. The first author set the
scientific questions, approved the claims, and verified the results. Routine operational decisions were delegated to
a coordinating AI agent under written rules, and each is recorded. The analysis note~\cite{AnalysisNote2026} gives the
full statement, including the tool versions. The figures were drawn by plotting code from the analysis outputs; no
figure was generated or edited by a generative-AI image tool. AI tools are not authors, and the authors take
responsibility for the content.

"The first author" is for now, until Ben has read the work.

## CITABLE FOR / NOT CITABLE FOR

- **Citable for:** this wording, as Joseph's.
- **Not citable for:** any result; a complete census. The Sonnet version is Joseph's best knowledge, and the Grok
  version is from him, not from the records.

Nothing is submitted, deposited or tagged.

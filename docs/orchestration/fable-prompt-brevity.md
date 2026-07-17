---
name: fable-prompt-brevity
description: Joseph wants prompts written for Fable 5 sessions to be as brief and open as possible
metadata: 
  node_type: memory
  type: feedback
  originSessionId: 0a088b19-e2da-4bba-a5c3-8e81e381a6e6
---

When writing a handoff prompt for another Fable 5 session, Joseph wants it "as brief as possible, since Fable is better the smaller and more open the prompt" (2026-07-06 — he had me cut a ~100-line handoff to ~25 lines).

**Why:** He trusts Fable to derive details from memory files and the repo itself; over-specification constrains it and wastes tokens.

**How to apply:** Put only the vision, hard guardrails, and explicit authorizations in the prompt; lean on auto-loaded memory ([[worldline-rebuild]], [[delegate-skill-notes]]) and pointers instead of restating context. Note this applies to Fable-to-Fable handoffs — delegate CLI prompts (codex/gemini/claude-school) still need full self-contained specs since those agents have no memory access.

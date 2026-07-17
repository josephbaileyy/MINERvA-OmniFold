# Round ledger (benchmarking slice)

Round-by-round orchestration bookkeeping. Physics numerics/citations that were mixed into the original ledger are
now first-class in `../../provenance/CLAIMS.md`. Full original (both streams, interleaved) preserved at
`../../provenance/mixed-source/round-ledger-claude-school.original.md`.

## Dispatch templates (verified working)
- **Perlmutter (2026-07-16, fe-fps-campaign; sessions run with redirected $HOME — use absolute paths; RH=/global/homes/j/josephrb):**
  codex personal/school: `env CODEX_HOME=$RH/codex-homes/{personal,school} codex exec -c model="gpt-5.6-sol" -c model_reasoning_effort="xhigh" --sandbox {read-only|danger-full-access} --skip-git-repo-check -C <dir> --output-last-message OUT "$(cat prompt.md)" < /dev/null`;
  claude-school: `HOME=$RH/claude-homes/school/claude-homes/personal $RH/.local/bin/claude -p "$(cat prompt.md)" --model opus --allowedTools "Read,Grep,Glob,..."` (the NESTED home — `$RH/claude-homes/school` alone gives "Not logged in", which mimics a quota error);
  agy: `HOME=$RH timeout 1500 $RH/.local/bin/agy --model "Gemini 3.1 Pro (High)" --print-timeout 18m --dangerously-skip-permissions --add-dir <dir> -p "$(cat prompt.md)"`.
- **codex:** `env CODEX_HOME="$HOME/.codex[-personal]" codex exec -c model_reasoning_effort="xhigh" -c
  tools.web_search=true --sandbox read-only --skip-git-repo-check -C <dir> "$(cat prompt.md)" < /dev/null`
- **gemini:** `"$HOME/.local/bin/agy" --model "Gemini 3.1 Pro (High)" --print-timeout 20m0s
  --dangerously-skip-permissions --add-dir <dir> -p "$(cat prompt.md)"`
- **claude:** Agent tool, `subagent_type general-purpose`, `model opus`; continue in-context via SendMessage.

## Episodes (see ../../provenance/episodes/ for cards)
| episode | config | models / effort | rounds | outcome |
|---|---|---|---|---|
| EP-2026-07-08-interpretations | 4 personas (QBist/Everett/collapse/Darwinist), A/B/C | opus + codex + gemini, high→max | 2 (+extended to 5) | unitarity premise localized; interpretation-neutral [→ CLM re §9] |
| EP-2026-07-08-extended-rounds | Config A pushed to 5 | mixed | 5 | value peaks R3–R4; R5 overreach + mis-cite (1402.5977) |
| EP-2026-07-08-freeturn | free discussion (no mode labels) | mixed | — | premature/false consensus; confirms adversarial push needed |
| EP-2026-07-08-soft-sector | soft-hair vs IR-skeptic vs collapse-constructor | codex xhigh + opus + gemini, MAX | 3 | affine-weight cancellation [CLM-004] |
| EP-2026-07-09-marginal-floor | 3 independent METHODS (modular/celestial/toy) | codex xhigh + opus×2 | 1 each + verify | (I) floor survives [CLM-005/010]; toy refuted; 1 fabricated cite caught (1712.10018) |
| EP-2026-07-09-edge-modes | edge-realist vs Type-III vs holo-edge | gemini + codex-school xhigh + opus | 3 | Θ TRUE-conditional, contrarian conceded [CLM-008/009] |
| EP-2026-07-09-idea-rate-study | blind idea-rate benchmark: 2 models × (one-shot, self-revision) × 4 seeds ×2, +2 calibration plants, dual blind graders, orchestrator verification | subjects gpt-5.6-sol + gpt-5.5 (xhigh, search, empty workdir); graders gemini 3.1 High + claude-school opus | R1+R2 | survivors: sol 6/8→7/8, 5.5 3/8→5/8; 0 fabrications/44 IDs; plants caught 4/4 [BEN-012..016] |
| EP-2026-07-10-lead-vetting | all 4 idea-rate leads vetted: per-lead {prior-art, kill-audit, fresh-eyes, referee} + cross-card unification + 2 independent re-derivations + 3 ground-truth computations; part 2: promotion queue + repeatability battery to the actual caps; part 3: review items closed (flux-floor §9, zero-mode 3-family adjudication, Slepian law) + gemini driver to p30 | agy 3.1-High ×95+driver + claude-school opus ×47 (capped at 42/window) + codex-personal xhigh ×7 + codex-school xhigh ×4 + fable ×1 (died: monthly spend limit) | 6 waves + parts 2–3 | L1+L2 PROMOTED → physics/note/horizon-record-selection-rules-note.md (moment law + mixed-depth + no-go + patch theorem + zero-mode conditional rate-invariance + Slepian α≈2asinh(2√3/A)); flux-floor note gains §9 converse; L3 UPGRADED; L4 → lemma; graders repeatable-but-miscalibrated (gemini 46/48 tens); claude-school cap = 42 jobs/window; gemini ceiling unreachable (see limits-log final count) [BEN-017..019] |

## Model reliability (running)
- codex/gpt-5.6-sol (new, 2026-07-09 study; pin via `-c model="gpt-5.6-sol"`, max effort still `xhigh`):
  0 fabrications; anchors all correct (several verified to 10 digits); aggressive AND accurate self-critic
  (replaced 4/8 of its own cards on revision, each for a verified-real reason; once out-searched the
  orchestrator's scoop check). Weakness profile: novelty-marginal ideas, never broken math.
- codex/gpt-5.5: citation-dense, ~0 fabrication in these runs; confirmed 0/32-card fabrications in the
  2026-07-09 idea-rate study; self-revision conservative (replaced 1/8; worsened 3/8 chains on grader mean).
- gemini: assertive; source of the confident over-claims and 2 of 3 fabricated citations — best used as the
  contrarian WITH a mandatory verification pass on anything it cites. 2026-07-10 vetting: pattern persists in
  milder form — 2 wrong-but-real-story arXiv IDs out of ~14 new cites (right authors/topic, wrong number) plus
  1 honest literal placeholder ("2402.xxxx"); analysis content itself was consistently strong and fast (41–239 s/job).
- claude opus: cleanest synthesis; withheld an unsure ID rather than fabricate (good). As claude-school -p
  delegate (2026-07-10): 0 citation errors across 5 heavy jobs, self-flags UNVERIFIED honestly, did correct
  digit-by-digit hand arithmetic when Bash was denied; derived the episode's central new result (unified moment
  law) and a correct full re-derivation with no tools. Trust tier: analytic workhorse.
- codex/gpt-5.6-sol as VERIFIER (2026-07-10): 3/3 clean xhigh derivations (609/309/358 s) — found a real
  factor-2 convention error others missed, executed a two-method kill-test to closed form, resolved a
  cross-card kernel seam; 0 citation errors. Strongest ground-truth engine when a disagreement needs computing.

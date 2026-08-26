# TEMP HANDOFF — session migration `claude-school` → `claude`

**Delete this file once the new session has read it.** It exists only to survive the
account switch; everything durable is in `DECK.md` and `BRAINSTORM-PROMPT.md`.

Written 2026-08-25 by the `claude-school` session. Talk date: **2026-09-09** (15 days out).

---

## 1. What the task is

A ~20 min talk to **Ben Nachman's ML group** at Stanford/SLAC. Audience is strong on ML
and general particle physics, knows OmniFold at a high level, knows **nothing** about
neutrino physics or MINERvA, and **strongly prefers ML-methods content over uncertainty
quantification**. Guideline says "1 slide"; Joseph says people really give ~8.

Relevant and not incidental: **Nachman co-authored OmniFold** (Andreassen, Komiske,
Metodiev, Nachman, Thaler — PRL 124, 2020) and **PET is the OmniLearn backbone**
(Mikuni & Nachman, arXiv:2404.16091). Both the method and the architecture in this
analysis are the group's own. Verified in `docs/analysis-note/refs.bib`.

## 2. Where the work is

Branch **`sep-09-presentation`**, pushed to `github`. Tip at time of writing: `2efec3ff`.
Joseph reads it on GitHub — he has said it's hard to view things on the cluster, so
**anything you want him to see must be committed and pushed**, not just written to disk.

```
docs/sep-09-presentation/
  DECK.md                    <- the deck: 8 slides, methods-first framing
  BRAINSTORM-PROMPT.md       <- NEXT STEP: paste into a fresh session
  refit_spread.png           + make_refit_figure.py      (slide 5, the money plot)
  pet_bootstrap_anomaly.png  + make_anomaly_figure.py    (slide 6)
  cstat_variance_budget.png  + make_variance_figure.py   (slide 7 backup)
```

Three `.png` are **force-added**. `.gitignore:4` excludes `*.png` repo-wide and all 55
note figures are PDF, so these are the only tracked PNGs in the repo. Deliberate, so they
render inline on GitHub; they're talk assets, no build closure consumes them, and no lint
references `.png` (checked). Reversible if unwanted.

## 3. State of the deck, and the two framings already rejected

The deck went through three theses. **Don't re-propose the first two.**

1. ~~"PET agreed with GBDT, then the uncertainty fell apart, so I demoted it."~~
   Joseph: the takeaway reduces to *"just because it looks good doesn't mean it's
   accurate,"* which everyone in that room already knows. Correct call — it was a process
   moral, not a finding.
2. ~~Same evidence, framed as a UQ result.~~ Rejected: the group would rather hear about
   methods than covariance bookkeeping.
3. **Current:** the step-1 classifier is the object of study. **(A)** change the input
   representation → nothing happens (PET point cloud vs GBDT scalars agree 2.3–3.9%
   median per-bin; MLP vs GBDT total ratio 1.0078). **(B)** change *nothing* and re-run →
   the learned map moves (five re-fits span 5.46%, sd 2.047% = **41.5×** the 0.0493%
   Poisson expectation; `mean(push)` 1.0776 / 1.0913 / 1.0472 / 1.0825). Covariance is
   demoted to slide 7, one line.

**Joseph's standing verdict on the current version:** he *likes the framing* —
interrogating an object everyone overlooks, the function the step-1 classifier actually
learns — and *dislikes the conclusion*, because "the map moves and I don't know why" is a
puzzle, not a result. He also liked that the alternative theses had "the vibe of asking
the question not asked before."

**So the open work is the ENDING, not the framing.** He has explicitly offered to spend
compute to get a real conclusion.

## 4. Next step

Paste `BRAINSTORM-PROMPT.md` into a fresh session. It asks for 5–8 ranked theses, each
either already conclusive or shipped with the experiment that makes it conclusive, and it
requires every proposed experiment to declare **what its null result looks like** —
ranking presentable-either-way above high-variance, because the date is fixed.

Two seeds to check first, in this order:

- **Seed 2 may cost zero compute.** The five re-fits behind `VL131` already ran. *If their
  per-event push weights were saved*, you can map re-fit-to-re-fit variance of the learned
  ratio across (pT, p∥, E_avail) with no new training — the most direct available
  explanation of `OI-126`'s p∥ sign flip. Whether it's possible is a question about what's
  on disk; read the code, no status doc answers it.
- **Seed 6 may already be conclusive.** `VL94`–`VL97`: a 2×2 of warm/cold model ×
  fresh/fixed split plus an annealed-LR arm — all four **fail** the predeclared iteration-2
  repair rule and **three get the sign wrong**. `VL134`–`VL140`: two annealing arms
  separated at **16.23×** the pooled within-arm sd, ranges disjoint, 9/9 realized pairwise.
  I read the ledger rows only, not the campaign. If it holds up read whole, it's an
  ML-methods talk with a conclusion, today, for free.

## 5. Environment facts that cost this session real time

- **The `/pscratch` checkout runs hundreds of commits behind.** It was **230 behind
  `github/main`** on 2026-08-25 while `HEAD` read 2026-08-21. Read status docs via
  `git show github/main:<path>`, never from the working tree. This burned me: I told
  Joseph the B1 steps 4-5 pause was the live blocker (it was **lifted** 2026-08-22,
  `DECISION-20260822-joseph-b1-lift-and-clause-c.md`) and quoted two `OI-137` claims that
  a later commit had **inverted**.
- **`LIVE-STATE.md` can be FRESH and still false.** Its `Current DAG node` and
  `Declared state` fields are authored prose the generator copies forward verbatim;
  regenerating updates the timestamp and sha but does **not** revalidate the text. The file
  says so itself. Verify blockers against the governing `OI-*` record.
- **Remote is `github`, not `origin`.** No `origin` exists.
- **Default `python3` on the login node has no matplotlib.** Use
  `/global/u2/j/josephrb/.conda/envs/root_6_28/bin/python`.
- **Other sessions are concurrently active in this repo.** At 20:11 on 2026-08-25
  `git worktree list` hung in uninterruptible I/O on the primary checkout — another
  session held a ref lock. `.git/worktrees/` was clean, filesystems were all responsive.
  **Workaround that worked: a `--depth 1` clone from GitHub into the scratchpad**, edit,
  commit, push. Fully isolated, doesn't touch the busy repo, and doesn't risk another
  session's state. Prefer it over worktrees while others are running.
- Compute rules that shape feasibility: a **single** Slurm job under 12 h is pre-approved
  (launch, don't ask); a **family** is not, and M(ii) is not authorized at any walltime.
  Route new compute through `nd-unfolding/mnv_guarded_run.py` (`OI-136`). Since the
  `OI-126` ruling, **PET is off the publication critical path** — exploratory PET work
  touches no gate, which is what makes seeds 1–5 cheap to attempt.

## 6. Memory — what does and doesn't migrate

Memory is per-account-home, so the two files this session wrote under
`claude-homes/school/` will **not** be visible to the `claude` account.

Good news: `claude-homes/personal/` already has ~45 memory files for this project,
including several directly relevant — `jul16_talk_design_deck.md`,
`pet_vs_gbdt_uncertainty.md`, `pet_vs_gbdt_5d_unified.md`, `note_reader_voice.md`,
`claude_home_conda_trap.md`, and a set of `feedback_*` preference files. The new session
is inheriting *more* context than this one had.

**Worth carrying over if `personal` lacks an equivalent — check first, don't duplicate:**
the staleness trap in §5 above (written in `school` as
`pscratch-checkout-runs-far-behind.md`). It's the one that produced actual false statements
to Joseph in this session, so it's the highest-value item. `personal` has
`claude_home_conda_trap.md`, which probably already covers the matplotlib/conda point.

## 7. Guardrails — carried forward, still binding

Full list is in `DECK.md`; these are the ones easiest to violate by accident:

- `C_stat` is never "verified", "adopted", or "the statistical uncertainty".
- Never cite **"bootstrap-centering" as a settled mechanism.** The phrase *is* in Joseph's
  `OI-126` ruling, so quoting it faithfully is not an error — but the mechanism is **not
  established** and must never be presented as a determined cause. `AGENTS.md` records a
  session being told otherwise and "correcting" a faithful quotation in the wrong
  direction. Operative wording: *a large, spatially coherent anomaly whose coverage has
  not been validated.*
- Never name a cause for the re-fit spread. That it happens is measured; **why is not.**
- No 3D/N-D covariance band, and no σ or χ² derived from one — the historical 3D covariance
  and its generator significances are quarantined. This rules out the July deck's `+3.9σ` /
  `+2.3σ` and the grey bands in `generators_vs_unfolded_band.png` and
  `compare_mec_eavail.png` (both draw from `hCov_combined3d_total`).
- Central-value ratios are fine (the 46%-of-gap / 27%-of-integrated-deficit 2p2h numbers).
- All three figures **re-plot committed records**; they do not re-measure. `OI-126`'s 50
  per-cell replica vectors are not reachable from here —
  `/pscratch/sd/j/josephrb/lane-d-oi120/LANED_CSTAT_CROSSCHECK.npz` carries the covariance
  and `cv` but is centred on the replica mean, which isn't stored.

## 8. Open questions for Joseph

1. Which thesis to commit the 15 days to — pending the brainstorm output.
2. Whether the three force-added PNGs stay, or get replaced by PDFs to preserve the
   `.gitignore` convention.
3. Whether this branch eventually merges to `main` or stays a side branch.

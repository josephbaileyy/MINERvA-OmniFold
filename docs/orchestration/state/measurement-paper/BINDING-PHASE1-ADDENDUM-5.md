# Binding addendum 5: decision margins, the hydrogen cascade check, the W2 stale-cycle re-check, packing (2026-10-20)

**By** the paper-tighten lane, as director, under [`BINDING-PHASE1-20261019.md`](BINDING-PHASE1-20261019.md).

**CITABLE FOR:** the rulings below.
**NOT CITABLE FOR:** any result. The margins receipt lands with the session's phase-1 PR.

## 1. Decision-boundary margins

The session's receipt (`phase1/a7margins/`, job 60023575; all controls reproduce `joint-evaluate.json` bitwise) is
accepted.
- The reading used is the fixed-order margins of the claim family, with κ = 3 beside them.
- The closest decisions are NuWro shape at 1.11 null SD (1.01 at κ = 3) and GENIE CV shape at 1.30 (0.67 at κ = 3).
- The methods paper quotes these once the receipt is on `main`.
- This replaces the median distances in [`../2d-closeout/stageF/methods/M2-AUDIT.md`](../2d-closeout/stageF/methods/M2-AUDIT.md)
  Q4e (see [`BINDING-PHASE1-ADDENDUM-3.md`](BINDING-PHASE1-ADDENDUM-3.md) §2).

## 2. MP3-B: the hydrogen cascade (kaskada_on)

The hyperon assertion lives in NuWro's cascade, which the production card leaves on even for the free target. The
50–100 GeV abort rate, about 1.7e-4 per DIS event, is above the 1e-4 bar of addendum 4.

- **The check:** matched seeds with `kaskada_on = 1` and `kaskada_on = 0` on the hydrogen card, compared event by event
  on the events that complete with the cascade on.
- **If they are identical** (the same particles, and four-momenta equal to rounding), the cascade is a no-op on a free
  target apart from the abort. `kaskada_on = 0` for hydrogen then becomes the primary, and (A) with `kaskada_on = 1` is
  reported beside it, flagged.
- **If they differ,** (A) with `kaskada_on = 1` stays primary with its flag, and the differences are reported.
- Both card variants and the seeds are declared before the run.
- The phase-1 ceiling and the cutoff of addendum 3 apply.

## 3. The W2 `compare_omnifiles.py` stale-cycle defect: a report-only re-check

The session found that `publication/w2/compare_omnifiles.py` reads an older autosave cycle of each tree; for example
`mc_signal_reco;8` with 2,489,136 entries instead of `;9` with 2,682,267. Its "equal" verdicts, including the δ = 0
controls of W2a and W2b, therefore cover only the stale cycles.

**Granted, 0 node-h, on a login node, from existing files:**
- re-run the δ = 0 "equal" controls of W2a and W2b on the latest cycles, with the session's `omnifile_io.py` under the
  same rule;
- grep the repository for other readers that open omnifile trees by cycle in the same way, and list them with file:line.

This is report-only: no W2 file and no KNOWN_ISSUES row is edited. The director lands any KI row or corrigendum.

## 4. Packing at the 16:00 PDT fallback

Eight passes per node at `--mem=16G` each are approved, with a fixed launcher and a work directory for each process.
The rest of addendum 3 §1 applies.

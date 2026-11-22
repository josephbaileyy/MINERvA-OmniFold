# DECISION 2026-11-18 (b) — Joseph: the IBUKT Slurm job is authorized in advance

**Recorded by** director-helper-3, for the director, who relayed Joseph's words.

## What led to it

- **The binding.** [`state/2d-closeout/IBUKT-BINDING-1.md`](state/2d-closeout/IBUKT-BINDING-1.md) binds the 2D OmniFold and binned-IBU known-truth recovery screen at M_IBUKT `d8b390ab3e7a7a9cc6a882d017737612de6d5aab`. Its ruling 3 requires, for a connect, "Joseph's explicit go in the IBUKT session, whose own boundary requires it".
- **The IBU-test go.** Joseph gave it on 2026-11-17 ("go ahead with the IBU test", [`DECISION-20261117b-joseph-note-plan.md`](DECISION-20261117b-joseph-note-plan.md)).
- **Joseph's absence.** Joseph may be away when the job's stages are ready to connect.

## Joseph's words, verbatim

> I also authorize the IBU slurm job in advance because I might be away, I already let the codex IBU session know

(`244adaa28a31abb5`, the sha256 of the text plus a final newline.)

## What is decided

1. **Advance authorization.** Joseph authorizes the IBUKT Slurm job (the screen, under IBUKT-BINDING-1) in advance. This is Joseph's go that the binding's ruling 3 requires. It does not need to be given again in the IBUKT session at each connect.
2. **Each stage still needs its own director go.** The stages run in order: `envstage`, then `prepare`, then `screen`, then `score` (`2d-unfolding/ibukt/jobs.py`). Each needs the director's go on its pinned script sha, given after the previous stage's PASS receipt.
3. **The binding's other conditions are unchanged:**
   - fresh fence acknowledgments from cov2d and tier3-design before each connect;
   - the cap of 5.90 CPU node-h;
   - the limit of `--time=05:15:00`;
   - job state read with `sacct` only (never `squeue`).
4. **STOPs.** Any STOP comes to the director unrepaired, and nothing is re-run.
5. **The outcome.** It goes to Joseph and Ben under the declaration's licences, and no note wording changes (the binding's ruling 4).

## Not decided here

- Any change to the bound design, code, cap or limit.
- A repair or re-run after a STOP.
- What the outcome means for the note.

## CITABLE FOR / NOT CITABLE FOR

- **Citable for:** Joseph's advance go for the IBUKT Slurm job under IBUKT-BINDING-1, and the conditions above.
- **Not citable for:**
  - a director go on any stage's script sha;
  - any IBUKT result;
  - any note or paper wording;
  - a repair or re-run.

Nothing is submitted, deposited or tagged.

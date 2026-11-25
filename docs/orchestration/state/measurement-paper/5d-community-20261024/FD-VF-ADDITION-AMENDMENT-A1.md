# AMENDMENT A1 to FD-VF-ADDITION-DECLARATION.md: Phase 1's figures, in the with arms only, and the OLD arms' routing (2026-11-25)

**By** tier3-design. The figures change was **accepted by** the director on 2026-11-25, after the two reads of the
Phase 1 code. The routing section is for the director's binding with the code.
**Amends** `FD-VF-ADDITION-DECLARATION.md` (sha256 `31662736e85f83e3772722fa9ec633ae4f8a9add2fd37c111b801f058dcfe39f`,
merged in #1334) §3 and §6. Nothing else changes.

## The change

In §3's table, the row "the figures, and their check" becomes:

| set | step | tool | recorded argv | OLD with C_PL5D | OLD without C_PL5D |
|---|---|---|---|---|---|
| E | the figures, and their check | `fd_g_figures.py`, `fd_g_figures_check.py` | E-A2's (`fd/gencmp-e/rerun1/chain/chdefs/with/figures-a2/*.json` `argv`) | `…/chdefs/with/figures-a2/`, each file checked against E-A2's `fd/gencmp-e/a2/run/receipts/figures-a2.sha256` | **not drawn** |

The figures run in the two with arms only:
- the OLD with arm draws them, and control R compares them with `figures-a2`: each PDF byte for byte, and each sidecar but
  argv, code and versions;
- the V_F with arm draws them with the reported block `C_resp + C_PL5D + dF`.

The without arms draw no figures.

## The reason

- **The without arm's figures can't be reproduced.** The OLD targets named in §3, `…/chdefs/with/figures/` and
  `…/chdefs/nopl/figures/`, predate GENCMP addenda E-A1 (shorter legend qualifiers) and E-A2 (hydrogen flags off the
  chdefs legend). No current tool draws those legends: `fd_g_figures.py` is now E-A2's (`5d2916cb`).
- **The evidence is codex-school's read of the Phase 1 code** (gpt-6.2-sol, finding 2). The current
  `fd_g_figures_check.py` fails five label checks on the committed pre-E-A2 with sidecars. The historical checker passes all
  498. The current generator also changes the legend content that R compares.
- **The with arm's target is what the note prints.** E-A2's redraw `figures-a2` was made by the current
  `fd_g_figures.py` (its sidecars record `5d2916cb`). The current checker passes it: "OK: 498 checks, 0 failed, 3
  sidecars", run locally on the committed files. The note shows `fd_g_fig_modes` from `figures-a2`.
- **Nothing printed is lost.** The note shows no figure from the without arm.

## The OLD arms' routing (§3) and the renderer (§6, R)

These were made explicit after codex-school's two reads (findings 3, 10 and the re-read's "superseded routing").

- **Downstream OLD steps read committed upstreams.** In the OLD arms, each downstream step reads the **committed**
  upstream readouts, pinned by their declared digests, as `fd_gencmp_e`'s old set does. That covers G-DIAG,
  G-FOLLOWUP, G-SENS2, the flux bootstrap and the figures, and F1 reading F0b. Each readout records its upstream's
  digest, so control R can hold only on the committed upstream.
- **V_F steps read what the chain wrote.** §3's sentence on downstream pins ("its defaults with only the upstream
  readouts' sha256 replaced, by the chain's own digests") applies to the V_F arms only.
- **The chdefs manifest is pinned to its recorded digest.** The staged `rerun1/pred/SHA256SUMS` must be the recorded
  `a45438fa…`, and the loaded prediction specification must equal the committed
  `fd/gencmp-e/rerun1/chain/pins/predictions-chdefs.json`, before any step. Every chdefs producer is then pinned to
  the recorded digest, never one observed later.
- **The renderer is E-A2's.** Control R's byte-for-byte PDF comparison needs E-A2's environment, so the chain refuses
  before any producer runs unless its python, numpy and matplotlib are the versions recorded in `figures-a2`'s sidecars. Those
  are 3.11.14, 1.26.4 and 3.10.8: root_6_28 on the login node, as E-A2 ran. codex-school found that another 3.11
  environment matched the sidecars but not the PDF bytes.

**CANNOT AUTHORIZE:** anything beyond the changes above.

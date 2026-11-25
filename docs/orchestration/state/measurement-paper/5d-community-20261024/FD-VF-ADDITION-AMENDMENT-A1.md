# AMENDMENT A1 to FD-VF-ADDITION-DECLARATION.md: Phase 1's figures, in the with arms only (2026-11-25)

**By** tier3-design. **Accepted by** the director, 2026-11-25, after the two reads of the Phase 1 code.
**Amends** `FD-VF-ADDITION-DECLARATION.md` (sha256 `31662736e85f83e3772722fa9ec633ae4f8a9add2fd37c111b801f058dcfe39f`,
merged in #1334) §3. Nothing else changes.

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

**CANNOT AUTHORIZE:** anything beyond the change above.

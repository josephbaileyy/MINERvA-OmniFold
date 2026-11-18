# External caption reads of the redrawn figures (2026-11-17/18; the director's request)

Each batch's reader was given, per figure, the PNG of the file installed at `2fe070fec` (old), the PNG of the redrawn
file (new) and the figure's caption, by `tools/caption_read_inputs.py`. That tool regenerates the PNGs, so they aren't
kept here. The batches are b1 (Figs. 19–22), b2 (25, 23, 16, 1), b3 (26–29) and b4 (7–14). Captions are as at
557809de, before the caption fixes of helper-3 (Figs. 1, 19, 21, 23) and limitation-resolver (39b876b08, Figs. 27–28).
b5 reruns Figs. 11, 12 and 21 with the captions as merged in f2a4636e/b3559671.

Each batch keeps `prompt.txt`, `caption-*.txt`, `grok.out.txt` and `agy.out.txt`.
- **Readers:** Grok (`--max-turns 100`) and agy `gemini-3.8-flash-high`. agy's `claude-opus-4-6-thinking` had no
  quota, and a first Grok run without the turn limit stopped before answering.
- **Read-only:** each reader was told to change nothing and to answer on stdout.

## Results

| figure | Grok | Gemini | disposition |
|---|---|---|---|
| 19 (3dmodels) | FLAG: caption "(black)" | FLAG: same | fixed in the draft by helper-3 ("red filled circles"; checked) |
| 21 (mec) | FLAG: caption "(red)" | FLAG: it was given Fig. 20's caption (extraction error) | fixed in the draft ("orange ... pale pink"); b5 rerun: OK, OK |
| 1 (control) | FLAG: "background (orange)" | FLAG: same | fixed in the draft ("(gray)"; checked) |
| 23 (q3excess) | FLAG: quotes "data/GENIE" | FLAG: same | fixed in the draft (quotes "unfolded / GENIE prior"; checked) |
| 27 (gbdt bias spread) | FLAG: title caveats not in the caption | OK | in the draft (limitation-resolver 39b876b08) |
| 28 (gbdt coverage) | FLAG: title caveats; "Right:" for the lower panel; "Zero of 20" against the W2 points | FLAG: "Right:" | caveats in the draft (39b876b08). "Right:" and "Zero of 20" were already in the caption at 2fe070fec; routed to limitation-resolver |
| 8 (pull) | FLAG: "rms" now "SD"; histogram axis to 50 | FLAG: "SD"; body says "pull RMS" | intended (the SD relabel, the headroom); the body now says "standard deviation" in the draft |
| 11, 12 (tension, modes) | FLAG: caption text "2" (extraction error) | FLAG: same | b5 rerun with the full captions: OK, OK (both readers) |
| 20, 22, 25, 16, 26, 29, 7, 9, 10, 13, 14 | OK | OK | |

No reader found a lost datum or a changed number.

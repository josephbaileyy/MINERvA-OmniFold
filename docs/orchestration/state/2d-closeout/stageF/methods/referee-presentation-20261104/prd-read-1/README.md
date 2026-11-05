# PRD read 1 of #765 (the director's PRD-referee read at e24ad2cc1)

The director's read, committed verbatim as the director asked, with its own `SHA256SUMS` unchanged:
- `prompt.md`: the referee prompt;
- `answer.txt`: the referee's answer, byte-identical to the director's `answer.md`. It is renamed because the records'
  absence-claim check reads every `.md` under `docs/orchestration/`, and a quoted sentence of the referee's would need a
  waiver line, which would change the file. Earlier verbatim referee answers are `.txt` for the same reason.
  `sha256sum answer.txt` gives `69374629…`, the `answer.md` line of `SHA256SUMS`;
- `tex.diff`: `git diff ff6ba1885 e24ad2cc1 -- 'docs/analysis-note/*.tex'`, which regenerates it byte for byte;
- `REFEREE-PRESENTATION-reading-copy.pdf`: the reading copy the read used (sha256 `b43b98e4…`).

Added by the paper lane: `r2_check.py` and its output `R2-CHECK.txt`, the local reproduction behind ruling R2 (see
`../REPORT.md`, "After PRD read 1").

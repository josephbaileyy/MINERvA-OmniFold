# IBUB declaration, revision 2: the agy read (2026-11-23)

**By** `director-helper-3`. This is the read that revision 3 of `../../../../IBUB-DECLARATION.md` answers (§12 there).

**MEASURES:** one reader's findings on the declaration's revision 2. **CANNOT AUTHORIZE:** anything. The director
accepted revision 3 (commit `734a7e54`) by message on 2026-11-23.

- **The input:** revision 2 of the declaration, sha256 `921858430da56a11d6c01645fa7939eebc34e8fb3afd7a64bc519c4967ac98ca`.
  It was copied, with the files the prompt lists, into a read-only scratchpad directory. Those were COV2D's and
  REF-C2C1's declarations, `ref_c2c1.py` and its config, the COV2D code, and the driver's G2R diff.
- **The command:**
  `agy -p "$(cat prompt.txt)" --model <model> --add-dir <inputs> --dangerously-skip-permissions --output-format text`,
  with stdin closed. Both models ran at once.
- **`agy-gemini-3.8-flash-high.txt`:** rc 0, **VERDICT: REVISE**. It made 3 MAJOR, 4 MINOR and 2 NOTE findings, and
  revision 3 takes each one as a fix.
- **`agy-claude-opus-4-6-thinking.err.txt`:** rc 3, refused with RESOURCE_EXHAUSTED (429, individual quota). It wrote
  no report. The director ruled that no second read is needed on the declaration, because the code reads include
  codex-school2.
- **`rc.txt`:** both exit codes, as the wrapper wrote them.

| file | sha256 |
|---|---|
| `prompt.txt` | `aa624a80b588fb06a569d5b4827d37d49df942fdc873e232aecc7629856ebf81` |
| `agy-gemini-3.8-flash-high.txt` | `229eeaf4b0a65f9bbadbcbcde146c0117bbe346e523607682799e482d8451cb9` |
| `agy-claude-opus-4-6-thinking.err.txt` | `5b9d98cdbd5436c745307582424ba321a49fddc861ad9c94452e73ba75911ade` |
| `rc.txt` | `a7ff97047263b6324dbc9d480ae9470e62d5b66070f4630cc802cd072771e46e` |
